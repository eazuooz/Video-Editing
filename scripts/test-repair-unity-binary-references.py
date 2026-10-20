"""Synthetic SerializedFile transactions; never read actual vendor assets."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


repair = module("repair_binary_references", "repair-unity-binary-references.py")
fixtures = module("binary_fixture_builder", "test-finalize-unity-asset-library.py")
OLD = "172515602e62fb746b5d573b38a5fe58"
NEW = "89abcdef012345670123456789abcdef"
ROOT_GUID = "0123456789abcdef89abcdef01234567"


class RepairFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="yamyam-binary-repair-")
        self.project = Path(self.temp.name) / "Unity"
        self.work = self.project / "Library/YamyamAssetLibrary"
        self.stage = self.work / "staging/CreatorBundle"
        self.pack = self.stage / "000-fixture"
        self.pack.mkdir(parents=True)
        (self.work / "receipts").mkdir()
        (self.project / "Assets").mkdir()
        self.main_asset = self.project / "Assets/preserved.txt"
        self.main_asset.write_bytes(b"existing-main-asset")
        self.archive = Path(self.temp.name) / "source.unitypackage"
        self.archive.write_bytes(b"untouched-original-archive")
        self.product = {"id": "000", "folder": "000-fixture", "status": "complete", "files": [],
                        "guidRemaps": {OLD: NEW}, "guidCollisions": [{"oldGuid": OLD, "newGuid": NEW, "path": "000-fixture/Texture.png.meta"}],
                        "originalBinaryGuidCollisionBlockers": []}
        self.products = [self.product] + [{"id": f"{i:03d}", "folder": f"{i:03d}-empty", "status": "complete", "files": [], "guidRemaps": {}} for i in range(1, 84)]
        self.add("Texture.png", b"texture-source-bytes")
        self.add("Texture.png.meta", f"fileFormatVersion: 2\nguid: {NEW}\n".encode(), NEW)
        self.binaries = []

    def tearDown(self):
        self.temp.cleanup()

    def add(self, name, raw, guid=None):
        path = self.pack / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        record = {"path": "000-fixture/" + name, "bytes": len(raw), "sha256": repair.sha(raw)}
        if guid:
            record["guid"] = guid
        self.product["files"].append(record)
        return path

    def binary(self, name="Terrain.asset", version=22, endian="<", payload=b"native-object-payload"):
        raw_guid = repair.FINALIZER.guid_byte_forms(OLD)["unity-byte-nibbles"].hex()
        data = fixtures.serialized_fixture(version, [raw_guid, "e" * 32], endian=endian, payload=payload)
        path = self.add(name, data)
        self.add(name + ".meta", f"fileFormatVersion: 2\nguid: {ROOT_GUID}\n".encode(), ROOT_GUID)
        self.product["originalBinaryGuidCollisionBlockers"].append("000-fixture/" + name)
        self.binaries.append(path)
        return path

    def finish(self):
        self.manifest = {"stageRoot": str(self.stage), "products": self.products}
        self.manifest_path = self.work / "staging-manifest.json"
        self.manifest_path.write_bytes(repair.json_bytes(self.manifest))
        for product in self.products:
            (self.work / "receipts" / (product["id"] + ".json")).write_bytes(repair.json_bytes(product))
        rows = []
        digest = repair.map_sha(self.product["guidRemaps"])
        for path in self.binaries:
            data = path.read_bytes()
            table = repair.FINALIZER.parse_binary_externals(path)
            external = table["externals"][0]
            hit = {"guidOffset": external["guidOffset"], "oldGuid": OLD, "desiredNewGuid": NEW, "rawGuidHex": external["rawGuidHex"],
                   "currentDesiredGuidOwners": [{"productId": "000", "path": "000-fixture/Texture.png.meta"}]}
            rows.append({"path": "000-fixture/" + path.name, "actualPath": str(path), "productId": "000", "proofVersion": 2,
                         "guidMapSha256": digest, "actualSha256": repair.sha(data), "receiptSha256": repair.sha(data),
                         "receiptBytes": len(data), "receiptMatches": True, "exactCanonicalExternalHits": [hit]})
        self.audit = {"proofVersion": 2, "sourceManifestSha256": repair.sha(self.manifest_path.read_bytes()), "stageRoot": str(self.stage),
                      "completedUtc": "2026-10-19T00:00:00Z", "errors": [], "staleReceiptFiles": 0,
                      "products": [{"id": "000", "guidMapSha256": digest, "files": rows}]}
        self.audit_path = self.work / "audit.json"
        self.audit_path.write_bytes(repair.json_bytes(self.audit))

    def run_repair(self, apply=False):
        return repair.repair(self.project, self.audit_path, apply,
                             repair.sha(self.manifest_path.read_bytes()), repair.sha(self.audit_path.read_bytes()), apply)

    def test_versions_endianness_exact_fields_header_body_meta_preserved(self):
        for version in (17, 22, 23):
            for endian in ("<", ">"):
                with self.subTest(version=version, endian=endian):
                    raw = fixtures.serialized_fixture(version, [repair.FINALIZER.guid_byte_forms(OLD)["unity-byte-nibbles"].hex()], endian=endian)
                    path = self.work / "parser.bin"; path.write_bytes(raw)
                    before = repair.FINALIZER.parse_binary_externals(path)
                    external = before["externals"][0]
                    hit = {"guidOffset": external["guidOffset"], "oldGuid": OLD, "desiredNewGuid": NEW, "rawGuidHex": external["rawGuidHex"]}
                    after, patches, outside = repair.prepare_patch(raw, before, {OLD: NEW}, [hit])
                    self.assertEqual([], outside)
                    self.assertEqual(1, len(patches))
                    offset = external["guidOffset"]
                    self.assertEqual(raw[:offset], after[:offset]); self.assertEqual(raw[offset+16:], after[offset+16:])
                    self.assertEqual(len(raw), len(after)); self.assertEqual(repair.FINALIZER.guid_byte_forms(NEW)["unity-byte-nibbles"], after[offset:offset+16])
                    path.write_bytes(after); repair.verify_after(before, repair.FINALIZER.parse_binary_externals(path), {OLD: NEW})

    def test_dry_run_never_changes_source_metadata_archive_main(self):
        path = self.binary(); self.finish()
        targets = [path, path.with_suffix(".asset.meta"), self.archive, self.main_asset, self.manifest_path, self.work / "receipts/000.json"]
        originals = {p: p.read_bytes() for p in targets}
        report, report_path = self.run_repair()
        self.assertEqual("dry-run-ready", report["status"]); self.assertEqual(1, report["summary"]["externalFields"])
        self.assertTrue(report_path.is_file()); self.assertFalse((report_path.parent / "backups").exists())
        for path, data in originals.items(): self.assertEqual(data, path.read_bytes())

    def test_apply_updates_only_binary_and_canonical_hash_receipts_with_full_backup(self):
        path = self.binary(); self.finish(); before = path.read_bytes(); meta_before = Path(str(path)+".meta").read_bytes()
        report, report_path = self.run_repair(True)
        self.assertEqual("complete", report["status"])
        offset = report["files"][0]["patches"][0]["offset"]
        self.assertEqual(before[:offset], path.read_bytes()[:offset]); self.assertEqual(before[offset+16:], path.read_bytes()[offset+16:])
        self.assertEqual(meta_before, Path(str(path)+".meta").read_bytes())
        self.assertEqual(before, (report_path.parent / "backups/000-fixture/Terrain.asset").read_bytes())
        updated = json.loads(self.manifest_path.read_bytes()); receipt = json.loads((self.work / "receipts/000.json").read_bytes())
        self.assertEqual(updated["products"][0], receipt)
        self.assertEqual(repair.sha(path.read_bytes()), next(r for r in receipt["files"] if r["path"].endswith("Terrain.asset"))["sha256"])
        self.assertEqual(b"untouched-original-archive", self.archive.read_bytes()); self.assertEqual(b"existing-main-asset", self.main_asset.read_bytes())

    def test_whole_payload_and_ascii_occurrences_refuse_blind_patch(self):
        self.binary(payload=b"object" + repair.FINALIZER.guid_byte_forms(OLD)["unity-byte-nibbles"] + OLD.encode())
        self.finish(); before = self.binaries[0].read_bytes()
        report, _ = self.run_repair(True)
        self.assertEqual("blocked", report["status"]); self.assertEqual(1, report["summary"]["outsideFieldFiles"])
        self.assertEqual(2, len(report["outsideExternalFieldHits"][0]["hits"]))
        self.assertEqual(before, self.binaries[0].read_bytes())

    def test_stale_binary_sha_refuses(self):
        path = self.binary(); self.finish(); path.write_bytes(path.read_bytes()[:-1]+b"X")
        report, _ = self.run_repair(True)
        self.assertEqual("blocked", report["status"]); self.assertIn("SHA/bytes", report["errors"][0]["error"])

    def test_map_hash_changed_refuses_before_writes(self):
        self.binary(); self.finish(); self.audit["products"][0]["guidMapSha256"] = "0"*64
        self.audit_path.write_bytes(repair.json_bytes(self.audit))
        with self.assertRaisesRegex(ValueError, "map changed"): self.run_repair(True)

    def test_ambiguous_or_cross_product_target_owner_refuses(self):
        self.binary(); self.products[1]["files"] = [{"path": "001-empty/Duplicate.meta", "bytes": 0, "sha256": "0"*64, "guid": NEW}]
        self.finish(); report, _ = self.run_repair(True)
        self.assertEqual("blocked", report["status"]); self.assertIn("exactly one", report["errors"][0]["error"])

    def test_missing_original_collision_intent_refuses(self):
        self.binary(); self.product["guidCollisions"] = []; self.finish()
        report, _ = self.run_repair(True)
        self.assertEqual("blocked", report["status"]); self.assertIn("collision/remap intent", report["errors"][0]["error"])

    def test_recovery_original_guid_and_archive_provenance_intent(self):
        self.binary(); self.product["guidCollisions"] = []
        target = next(r for r in self.product["files"] if r["path"].endswith("Texture.png.meta"))
        target.update(originalGuid=OLD, binaryGuidRecoveryRewrite=True,
                      source={"kind": "unitypackage", "package": str(self.archive), "originalPath": "Assets/Vendor/Texture.png", "originalGuid": OLD})
        self.finish(); report, _ = self.run_repair()
        self.assertEqual("dry-run-ready", report["status"])
        self.assertEqual("recovery-receipt-original-guid-and-archive-provenance", report["referencedOwnerProofs"][0]["originalGuidIntent"])
        target["source"]["originalGuid"] = "f"*32
        self.finish(); report, _ = self.run_repair()
        self.assertEqual("blocked", report["status"])

    def test_unexpected_meta_or_target_asset_edit_refuses(self):
        self.binary(); self.finish(); (self.pack / "Texture.png").write_bytes(b"changed-texture")
        report, _ = self.run_repair(True)
        self.assertEqual("blocked", report["status"]); self.assertIn("Ownership/source asset", report["errors"][0]["error"])

    def test_metadata_write_failure_rolls_back_binaries_receipts_and_manifest(self):
        self.binary("First.asset"); self.binary("Second.asset"); self.finish()
        protected = self.binaries + [self.manifest_path, self.work / "receipts/000.json", self.archive, self.main_asset]
        originals = {p: p.read_bytes() for p in protected}; actual_write = repair.atomic_write; failed = False
        def injected(path, data):
            nonlocal failed
            if Path(path) == self.manifest_path and not failed:
                failed = True
                raise OSError("synthetic final manifest write failure")
            return actual_write(path, data)
        with mock.patch.object(repair, "atomic_write", side_effect=injected):
            with self.assertRaisesRegex(OSError, "synthetic"): self.run_repair(True)
        self.assertTrue(failed)
        for path, raw in originals.items(): self.assertEqual(raw, path.read_bytes())
        latest = json.loads((self.work / "binary-reference-repair-latest.json").read_bytes())
        report = json.loads(Path(latest["report"]).read_bytes()); self.assertEqual("failed", report["status"]); self.assertEqual([], report["rollbackErrors"])

    def test_reparse_component_and_traversal_refused(self):
        with self.assertRaisesRegex(ValueError, "traversing"): repair.child(self.work, "../outside")
        with mock.patch.object(Path, "lstat", return_value=type("Info", (), {"st_mode": 0, "st_file_attributes": 0x400})()):
            with self.assertRaisesRegex(ValueError, "reparse"): repair.literal_path(self.stage)

    def test_final_complete_report_failure_also_rolls_back(self):
        path = self.binary(); self.finish()
        originals = {p: p.read_bytes() for p in (path, self.manifest_path, self.work / "receipts/000.json")}
        actual_write = repair.atomic_write; failed = False
        def injected(path, data):
            nonlocal failed
            if Path(path).name == "report.json" and json.loads(data)["status"] == "complete" and not failed:
                failed = True
                raise OSError("synthetic completion report failure")
            return actual_write(path, data)
        with mock.patch.object(repair, "atomic_write", side_effect=injected):
            with self.assertRaisesRegex(OSError, "completion report"): self.run_repair(True)
        self.assertTrue(failed)
        for path, raw in originals.items(): self.assertEqual(raw, path.read_bytes())

    def test_apply_requires_exact_reviewed_hashes_and_editor_exit(self):
        self.binary(); self.finish()
        for stopped, manifest, audit in ((False, "", ""), (True, "wrong", repair.sha(self.audit_path.read_bytes()))):
            with self.assertRaisesRegex(ValueError, "confirmed Editor exit"):
                repair.repair(self.project, self.audit_path, True, manifest, audit, stopped)

    def test_all84_terminal_products_and_matching_receipts_required(self):
        self.binary(); self.products.pop(); self.finish()
        with self.assertRaisesRegex(ValueError, "All84"): self.run_repair()
        self.products.append({"id": "083", "folder": "083-empty", "status": "complete", "files": [], "guidRemaps": {}})
        self.finish(); receipt = self.work / "receipts/083.json"; receipt.write_bytes(b"{}")
        with self.assertRaisesRegex(ValueError, "receipt differs"): self.run_repair()

    def test_stale_manifest_or_false_audit_offset_refuses(self):
        self.binary(); self.finish(); self.audit["sourceManifestSha256"] = "0"*64
        self.audit_path.write_bytes(repair.json_bytes(self.audit))
        with self.assertRaisesRegex(ValueError, "manifest/stage changed"): self.run_repair()
        self.finish(); self.audit["products"][0]["files"][0]["exactCanonicalExternalHits"][0]["guidOffset"] += 1
        self.audit_path.write_bytes(repair.json_bytes(self.audit)); report, _ = self.run_repair(True)
        self.assertEqual("blocked", report["status"]); self.assertIn("external fields differ", report["errors"][0]["error"])

    def test_actual_main_assets_root_and_held_editor_lock_refused(self):
        path = self.binary(); self.finish(); before = path.read_bytes()
        with mock.patch.object(repair, "editor_lock_guard", side_effect=ValueError("held Editor lock")):
            with self.assertRaisesRegex(ValueError, "held Editor lock"): self.run_repair(True)
        self.assertEqual(before, path.read_bytes())
        self.manifest["stageRoot"] = str(self.project / "Assets")
        self.manifest_path.write_bytes(repair.json_bytes(self.manifest))
        with self.assertRaisesRegex(ValueError, "explicit local stage"): self.run_repair()

    def converted(self, data):
        path = self.binary()
        path.write_bytes(data)
        record = next(r for r in self.product["files"] if r["path"].endswith("Terrain.asset"))
        record.update(bytes=len(data), sha256=repair.sha(data))
        # Initial fixture finish uses binary parser, so briefly construct it
        # against original bytes then replace the exact current bindings.
        current = data
        raw_guid = repair.FINALIZER.guid_byte_forms(OLD)["unity-byte-nibbles"].hex()
        binary = fixtures.serialized_fixture(22, [raw_guid, "e" * 32])
        path.write_bytes(binary); self.finish(); path.write_bytes(current)
        row = self.audit["products"][0]["files"][0]
        row.update(binaryKind="converted-yaml", status="converted-yaml-collided-guids-absent", actualSha256=repair.sha(current),
                   receiptSha256=repair.sha(current), receiptBytes=len(current), exactCanonicalExternalHits=[], collidingReferences=[],
                   convertedTextProof={"format": "unity-yaml", "guidMapSha256": repair.map_sha(self.product["guidRemaps"]),
                                       "sourceSha256": repair.sha(current), "sourceBytes": len(current), "allGuidSpellingsScanned": True, "collidingGuidOccurrences": []})
        self.audit_path.write_bytes(repair.json_bytes(self.audit))
        return path, row

    def test_converted_unity_yaml_only_verified_zero_old_guids_is_skipped(self):
        current = (f"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n  m_Texture: {{fileID: 2800000, guid: {NEW}, type: 3}}\n").encode()
        path, row = self.converted(current)
        report, _ = self.run_repair(True)
        self.assertEqual("complete", report["status"]); self.assertEqual(0, report["summary"]["externalFields"])
        self.assertEqual(1, report["summary"]["convertedTextFiles"]); self.assertEqual(current, path.read_bytes())

    def test_converted_yaml_hidden_mixed_case_guid_or_wrong_proof_refuses(self):
        mixed = "".join(c.upper() if i % 2 else c for i, c in enumerate(OLD))
        current = (f"%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n  m_Texture: {{fileID: 2800000, guid: {mixed}, type: 3}}\n").encode()
        path, row = self.converted(current)
        report, _ = self.run_repair(True)
        self.assertEqual("blocked", report["status"]); self.assertEqual(current, path.read_bytes())
        self.assertEqual(1, report["summary"]["outsideFieldFiles"])
        row["convertedTextProof"]["sourceSha256"] = "0"*64
        self.audit_path.write_bytes(repair.json_bytes(self.audit)); report, _ = self.run_repair(True)
        self.assertEqual("blocked", report["status"]); self.assertIn("exact clean SHA/map", report["errors"][0]["error"])

    def test_unclassified_yaml_cannot_be_silently_skipped_as_binary(self):
        path, row = self.converted(b"%YAML 1.1\n--- !u!21 &2100000\nMaterial: {}\n")
        row.pop("binaryKind"); self.audit_path.write_bytes(repair.json_bytes(self.audit))
        report, _ = self.run_repair()
        self.assertEqual("blocked", report["status"]); self.assertEqual(0, report["summary"]["convertedTextFiles"])


if __name__ == "__main__":
    unittest.main()
