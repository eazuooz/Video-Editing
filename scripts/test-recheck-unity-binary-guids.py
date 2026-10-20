"""Read-only binary recheck fixtures; all payloads live in disposable directories."""
import hashlib
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


recheck = load("recheck", "recheck-unity-binary-guids.py")
fixtures = load("finalizer_fixtures", "test-finalize-unity-asset-library.py")


class ReadOnlyRecheckFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="yamyam-guid-recheck-fixture-")
        self.project = Path(self.temp.name) / "Main"
        self.work = self.project / "Library/YamyamAssetLibrary"
        self.root = self.work / "headless-project/Assets/ThirdParty/YamyamAssetLibrary"
        self.root.mkdir(parents=True)
        self.path = self.root / "001-demo/Example.asset"
        self.path.parent.mkdir()
        self.canonical = "172515602e62fb746b5d573b38a5fe58"
        self.new_guid = "123456789abcdef00123456789abcdef"
        self.data = fixtures.serialized_fixture(externals=["71525106e226bf47b6d575b3835aef85"])
        self.path.write_bytes(self.data)
        self.manifest = {"stageRoot": str(self.root), "targetAssetRoot": "Assets/ThirdParty/YamyamAssetLibrary", "products": [
            {"id": "001", "guidRemaps": {self.canonical: self.new_guid}, "guidCollisions": [{"oldGuid": self.canonical,
                "path": "001-demo/Texture.meta", "previous": {"owner": "earlier-pack", "path": "old/Texture.meta"}}],
             "files": [{"path": "001-demo/Example.asset", "bytes": len(self.data), "sha256": hashlib.sha256(self.data).hexdigest()},
                       {"path": "001-demo/Texture.meta", "guid": self.new_guid}],
             "binaryGuidRecoveryProofs": [{"path": "001-demo/Example.asset", "collidedGuidsAbsent": True}]}]}
        self.manifest_path = self.work / "staging-manifest.json"
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.manifest_before = self.manifest_path.read_bytes()
        self.receipt = self.work / "receipt-sentinel.json"
        self.receipt.write_bytes(b"untouched provenance")

    def tearDown(self):
        self.temp.cleanup()

    def check_books(self):
        self.assertEqual(self.manifest_before, self.manifest_path.read_bytes())
        self.assertEqual(b"untouched provenance", self.receipt.read_bytes())

    def test_exact_unity_encoding_hit_is_reported_with_owners_and_bound_hashes(self):
        result = recheck.audit(self.project)
        self.assertEqual("needs-binary-reference-repair", result["status"])
        self.assertEqual(1, result["filesChecked"])
        self.assertEqual(1, result["exactCanonicalExternalReferenceHits"])
        product = result["products"][0]
        item = product["files"][0]
        self.assertEqual(str(self.path), item["actualPath"])
        self.assertEqual("001", item["productId"])
        self.assertEqual(2, item["proofVersion"])
        self.assertEqual(recheck.guid_map_sha(self.manifest["products"][0]["guidRemaps"]), item["guidMapSha256"])
        hit = item["exactCanonicalExternalHits"][0]
        self.assertEqual(self.canonical, hit["oldGuid"])
        self.assertEqual(self.new_guid, hit["desiredNewGuid"])
        self.assertEqual("001-demo/Texture.meta", hit["currentDesiredGuidOwners"][0]["path"])
        self.assertEqual(hit["rawGuidHex"], self.data[hit["guidOffset"]:hit["guidOffset"] + 16].hex())
        self.assertEqual(self.data, self.path.read_bytes())
        self.check_books()

    def test_stale_receipt_cannot_be_reported_as_pass(self):
        changed = self.data[:-1] + bytes([self.data[-1] ^ 1])
        self.path.write_bytes(changed)
        result = recheck.audit(self.project)
        self.assertEqual("needs-review", result["status"])
        self.assertEqual(1, result["staleReceiptFiles"])
        self.assertEqual(changed, self.path.read_bytes())
        self.check_books()

    def test_payload_only_hit_remains_explicit_outside_the_external_table(self):
        self.data = fixtures.serialized_fixture(payload=bytes.fromhex("71525106e226bf47b6d575b3835aef85"))
        self.path.write_bytes(self.data)
        record = self.manifest["products"][0]["files"][0]
        record.update(bytes=len(self.data), sha256=hashlib.sha256(self.data).hexdigest())
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.manifest_before = self.manifest_path.read_bytes()
        result = recheck.audit(self.project)
        self.assertEqual("needs-binary-reference-repair", result["status"])
        self.assertEqual(0, result["exactCanonicalExternalReferenceHits"])
        item = result["products"][0]["files"][0]
        self.assertTrue(item["collidingReferences"])
        self.assertTrue(all(hit["where"] == "whole-binary-byte-scan" for hit in item["collidingReferences"]))
        self.assertEqual(self.data, self.path.read_bytes())
        self.check_books()

    def converted(self, text):
        self.data = text.encode()
        self.path.write_bytes(self.data)
        record = self.manifest["products"][0]["files"][0]
        record.update(bytes=len(self.data), sha256=hashlib.sha256(self.data).hexdigest())
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.manifest_before = self.manifest_path.read_bytes()
        return recheck.audit(self.project)

    def test_clean_unity_converted_yaml_keeps_original_path_coverage_and_v2_binding(self):
        result = self.converted("%YAML 1.1\n--- !u!21 &1\nMaterial:\n  guid: " + self.new_guid + "\n")
        self.assertEqual("pass", result["status"])
        self.assertEqual(1, result["filesChecked"])
        self.assertEqual(0, result["serializedBinaryFiles"])
        self.assertEqual(1, result["convertedTextFiles"])
        item = result["products"][0]["files"][0]
        self.assertEqual("converted-yaml", item["binaryKind"])
        self.assertEqual("converted-yaml-collided-guids-absent", item["status"])
        proof = item["convertedTextProof"]
        self.assertEqual(item["actualSha256"], proof["sourceSha256"])
        self.assertEqual(item["guidMapSha256"], proof["guidMapSha256"])
        self.assertTrue(proof["allGuidSpellingsScanned"])
        self.assertEqual([], proof["collidingGuidOccurrences"])
        self.assertEqual(self.data, self.path.read_bytes())
        self.check_books()

    def test_unity_converted_yaml_with_mixed_case_old_guid_cannot_pass(self):
        mixed = "".join(char.upper() if index % 2 else char for index, char in enumerate(self.canonical))
        result = self.converted("%YAML 1.1\n--- !u!21 &1\nMaterial:\n  guid: " + mixed + "\n")
        self.assertEqual("needs-binary-reference-repair", result["status"])
        item = result["products"][0]["files"][0]
        self.assertTrue(item["convertedTextProof"]["collidingGuidOccurrences"])
        self.assertTrue(any(hit["representation"] == "case-insensitive-32hex-token" for hit in item["collidingReferences"]))
        self.assertEqual(self.data, self.path.read_bytes())
        self.check_books()

    def test_yaml_without_unity_document_marker_is_not_a_converted_source_proof(self):
        result = self.converted("%YAML 1.1\nplain: text\n")
        self.assertEqual("needs-review", result["status"])
        self.assertEqual(1, len(result["errors"]))
        self.assertEqual(0, result["filesChecked"])
        self.check_books()

    def preserve_as_source_only(self):
        product = self.manifest["products"][0]
        native = copy.deepcopy(product["files"][0])
        metadata_bytes = b"fileFormatVersion: 2\nguid: ffffffffffffffffffffffffffffffff\n"
        metadata = {"path": native["path"] + ".meta", "guid": "f" * 32, "bytes": len(metadata_bytes),
                    "sha256": hashlib.sha256(metadata_bytes).hexdigest()}
        product["files"].append(metadata)
        original = json.dumps(self.manifest).encode()
        run = "fixture-preserved-001"
        directory = self.work / "source-only-group-quarantine" / run
        directory.mkdir(parents=True)
        (directory / "manifest.json").write_bytes(original)
        report_path = directory / "report.json"
        history = {"run": run, "report": str(report_path)}
        report = {"schemaVersion": 2, "status": "complete", "apply": True, "run": run,
                  "completedUtc": "2026-10-19T00:00:01Z", "sourceManifestSha256": hashlib.sha256(original).hexdigest(),
                  "sourceRuntimeProofSha256": "1" * 64, "sourceMissingEvidenceSha256": "2" * 64, "files": []}
        product["files"] = [row for row in product["files"] if row["path"] not in {native["path"], metadata["path"]}]
        product["sourceOnlyFiles"] = []
        for row, data in ((native, self.data), (metadata, metadata_bytes)):
            destination = self.work / "SourceOnly" / row["path"]
            backup = directory / "backups" / row["path"]
            destination.parent.mkdir(parents=True, exist_ok=True); backup.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data); backup.write_bytes(data)
            record = {**copy.deepcopy(row), "preservedPath": str(destination), "sourceOnlyRun": run,
                      "sourceOnlyReason": "unused-provider-terrain-missing-original-references",
                      "runtimeProofSha256": report["sourceRuntimeProofSha256"], "missingEvidenceSha256": report["sourceMissingEvidenceSha256"]}
            product["sourceOnlyFiles"].append(record)
            report["files"].append({"productId": "001", "path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"],
                                    "destination": str(destination), "backupPath": str(backup), "originalRecord": copy.deepcopy(row)})
        self.path.unlink()
        product["sourceOnlyHistory"] = [history]
        self.manifest["sourceOnlyHistory"] = [history]
        report_path.write_text(json.dumps(report))
        self.manifest_path.write_text(json.dumps(self.manifest)); self.manifest_before = self.manifest_path.read_bytes()
        return report_path, report

    def test_preserved_native_is_still_parsed_with_original_scope_map_and_exact_guid_hits(self):
        report_path, _report = self.preserve_as_source_only()
        result = recheck.audit(self.project)
        self.assertEqual("needs-binary-reference-repair", result["status"])
        self.assertEqual(1, result["filesChecked"])
        self.assertEqual(1, result["sourceOnlyFilesChecked"])
        self.assertEqual(0, result["activeAssetFilesChecked"])
        self.assertEqual(1, result["exactCanonicalExternalReferenceHits"])
        row = result["products"][0]["files"][0]
        self.assertEqual("001-demo/Example.asset", row["path"])
        self.assertEqual("source-only", row["assetLocation"])
        self.assertEqual(str(self.work / "SourceOnly/001-demo/Example.asset"), row["actualPath"])
        self.assertEqual(str(report_path), row["sourceOnlyProof"]["reportPath"])
        self.assertEqual("f" * 32, row["sourceOnlyProof"]["metadataGuid"])
        self.assertEqual(self.data, Path(row["actualPath"]).read_bytes())
        self.check_books()

    def preserve_as_optional_demo(self):
        old_path, report = self.preserve_as_source_only(); run = report["run"]
        directory = self.work / "source-only-optional-demo-quarantine" / run
        directory.parent.mkdir(); old_path.parent.rename(directory); path = directory / "report.json"
        kind = "incomplete-optional-demo-script-group"
        report.update(kind=kind, sourceArchivesModified=False, actualMainAssetsModified=False)
        for row in report["files"]: row["backupPath"] = str(directory / "backups" / row["path"])
        for history in [*self.manifest["sourceOnlyHistory"], *self.manifest["products"][0]["sourceOnlyHistory"]]: history.update(kind=kind, report=str(path))
        for row in self.manifest["products"][0]["sourceOnlyFiles"]: row["sourceOnlyReason"] = kind
        path.write_text(json.dumps(report)); self.manifest_path.write_text(json.dumps(self.manifest)); self.manifest_before = self.manifest_path.read_bytes()
        return path, report

    def test_optional_demo_original_binary_scope_and_exact_references_are_retained(self):
        path, report = self.preserve_as_optional_demo(); result = recheck.audit(self.project)
        self.assertEqual("needs-binary-reference-repair", result["status"]); self.assertEqual(1, result["filesChecked"])
        self.assertEqual(1, result["sourceOnlyFilesChecked"]); self.assertEqual(1, result["exactCanonicalExternalReferenceHits"])
        row = result["products"][0]["files"][0]; self.assertEqual("001-demo/Example.asset", row["path"])
        self.assertEqual(str(path), row["sourceOnlyProof"]["reportPath"]); self.assertEqual("f" * 32, row["sourceOnlyProof"]["metadataGuid"])
        self.check_books()

    def test_optional_demo_history_kind_or_reason_cannot_be_relabelled(self):
        path, report = self.preserve_as_optional_demo(); report["kind"] = "unreviewed-kind"; path.write_text(json.dumps(report))
        result = recheck.audit(self.project); self.assertEqual("needs-review", result["status"]); self.assertTrue(any("wrong exact kind" in error.get("error", "") for error in result["errors"]))
        self.check_books()

    def test_preserved_backup_or_metadata_corruption_cannot_pass(self):
        report_path, report = self.preserve_as_source_only()
        backup = Path(report["files"][0]["backupPath"])
        backup.write_bytes(b"changed")
        result = recheck.audit(self.project)
        self.assertEqual("needs-review", result["status"])
        self.assertIn("backup bytes changed", result["errors"][0]["error"])
        backup.write_bytes(self.data)
        metadata = Path(report["files"][1]["destination"])
        metadata.write_bytes(metadata.read_bytes().replace(b"f" * 32, b"e" * 32))
        result = recheck.audit(self.project)
        self.assertEqual("needs-review", result["status"])
        self.assertIn("metadata SHA/bytes/GUID", result["errors"][0]["error"])
        self.check_books()

    def test_preserved_path_escape_active_duplicate_and_unfinished_history_refuse(self):
        report_path, original_report = self.preserve_as_source_only()
        product = self.manifest["products"][0]
        native = product["sourceOnlyFiles"][0]
        original_path = native["preservedPath"]
        native["preservedPath"] = str(self.project / "foreign.asset")
        self.manifest_path.write_text(json.dumps(self.manifest)); self.manifest_before = self.manifest_path.read_bytes()
        result = recheck.audit(self.project)
        self.assertEqual("needs-review", result["status"])
        native["preservedPath"] = original_path
        self.manifest_path.write_text(json.dumps(self.manifest)); self.manifest_before = self.manifest_path.read_bytes()
        self.path.write_bytes(self.data)
        result = recheck.audit(self.project)
        self.assertEqual("needs-review", result["status"])
        self.assertIn("active Assets", result["errors"][0]["error"])
        self.path.unlink()
        original_report["status"] = "failed"; report_path.write_text(json.dumps(original_report))
        result = recheck.audit(self.project)
        self.assertEqual("needs-review", result["status"])
        self.assertIn("not completed cleanly", result["errors"][0]["error"])
        self.check_books()


if __name__ == "__main__":
    unittest.main()
