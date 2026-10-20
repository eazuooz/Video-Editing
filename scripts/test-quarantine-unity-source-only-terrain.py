"""Synthetic four-file preservation transactions; no real assets or Unity."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


tool = load("source_only_quarantine", "quarantine-unity-source-only-terrain.py")
binary = load("source_only_binary_fixture", "test-finalize-unity-asset-library.py")


class SourceOnlyFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="yamyam-source-only-")
        self.project = Path(self.temp.name) / "Unity"
        self.work = self.project / "Library/YamyamAssetLibrary"
        self.headless = self.work / "headless-project"
        self.stage = self.headless / tool.ROOT
        self.stage.mkdir(parents=True)
        (self.work / "receipts").mkdir()
        (self.project / "Assets").mkdir()
        self.main = self.project / "Assets/Preserved.txt"; self.main.write_bytes(b"main-project-preserved")
        self.archive = Path(self.temp.name) / "Original.unitypackage"; self.archive.write_bytes(b"original-source-archive")
        self.product = {"id": "033", "folder": tool.FOLDER, "status": "complete", "guidRemaps": {}, "files": [], "originalBinaryGuidCollisionBlockers": [],
                        "inputs": [{"path": str(self.archive), "bytes": self.archive.stat().st_size}]}
        self.products = [self.product]
        for i in range(84):
            if i == 33: continue
            folder = f"{i:03d}-fixture"; relative = folder + "/preserved.txt"; data = b"other-product-source"
            path = self.stage / relative; path.parent.mkdir(parents=True); path.write_bytes(data)
            self.products.append({"id": f"{i:03d}", "folder": folder, "status": "complete", "files": [{"path": relative, "bytes": len(data), "sha256": tool.sha(data)}], "originalBinaryGuidCollisionBlockers": []})
        self.add(tool.FOLDER + "/Kept.txt", b"033model-and-other-assets-preserved")
        for relative, target in tool.TARGETS.items():
            raw = [tool.SAFE.FINALIZER.guid_byte_forms(guid)["unity-byte-nibbles"].hex() for guid in target["missing"]]
            data = binary.serialized_fixture(22, raw)
            self.add(relative, data)
            self.add(relative + ".meta", f"fileFormatVersion: 2\nguid: {target['guid']}\n".encode(), target["guid"])
        self.manifest = {"stageRoot": str(self.stage), "targetAssetRoot": tool.ROOT, "products": self.products, "summary": {}}
        self.manifest_path = self.work / "staging-manifest.json"
        self.runtime_path = self.headless / "Library/YamyamAssetLibrary/terrain-normalization/report.json"
        self.runtime_path.parent.mkdir(parents=True)
        self.missing_path = self.work / "missing-source-proof.json"
        self.missing = {"sourceModified": False, "missingGuids": sorted(tool.MISSING), "packageMatches": [], "canonicalReceiptMatches": [],
                        "metadataFiles": 564, "guidFolders": 564, "pathnames": 564, "members": 2678,
                        "available033UnitypackageVariants": 1, "excluded033Files": [], "package": str(self.archive), "packageBytes": self.archive.stat().st_size,
                        "supplementalArchives": [{"unityMetadataFiles": 0, "nestedUnitypackages": [], "exactMissingGuidMatches": []} for _ in range(3)],
                        "sourceTerrainPaths": {target["guid"]: "Assets/EmaceArt/PlasticineWorld/Terrain/" + Path(path).name for path, target in tool.TARGETS.items()}}
        self.finish()

    def tearDown(self): self.temp.cleanup()

    def add(self, relative, data, guid=None):
        path = self.stage / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        record = {"path": relative, "bytes": len(data), "sha256": tool.sha(data), "source": {"kind": "unitypackage", "package": str(self.archive)}}
        if guid: record["guid"] = guid
        self.product["files"].append(record)
        return path

    def finish(self):
        self.manifest_path.write_bytes(tool.encoded(self.manifest))
        for p in self.products: (self.work / "receipts" / (p["id"] + ".json")).write_bytes(tool.encoded(p))
        roots = sorted((tool.ROOT + "/" + record["path"] for p in self.products for record in p["files"] if not record["path"].endswith(".meta") and record["path"] not in tool.TARGETS), key=tool.ordinal_key)
        records = {r["path"]: r for r in self.product["files"]}; targets = []
        for relative, target in tool.TARGETS.items():
            r, meta = records[relative], records[relative + ".meta"]
            targets.append({"path": tool.ROOT + "/" + relative, "guid": target["guid"], "canonicalSha256": r["sha256"], "actualSha256": r["sha256"], "sourceArtifactSha256": r["sha256"], "bytes": r["bytes"],
                            "referencedByOtherRootAssets": False, "checkedInboundReferences": 0, "metadataPath": tool.ROOT + "/" + relative + ".meta", "metadataBytes": meta["bytes"], "metadataSha256": meta["sha256"], "canonicalMetadataSha256": meta["sha256"]})
        self.runtime = {"schemaVersion": 1, "project": str(self.headless), "manifestPath": str(self.manifest_path), "manifestSha256": tool.sha(self.manifest_path.read_bytes()),
                        "apply": False, "originalArchivesModified": False, "scenesOpened": False, "completedUtc": "2026-10-19T00:00:01Z", "observedUnityErrors": 0,
                        "status": "dependency-proof-complete", "errors": [], "blockers": [],
                        "missingProviderTerrainDependencyProof": {"proofVersion": 1, "status": "unreferenced-by-other-root-assets", "startedUtc": "2026-10-19T00:00:00Z", "completedUtc": "2026-10-19T00:00:01Z",
                            "method": "AssetDatabase.GetDependencies(all current root asset paths except both targets, recursive:true)", "receiptSha256": tool.sha((self.work / "receipts/033.json").read_bytes()),
                            "rootAssetsChecked": len(roots), "rootPathsSha256": tool.sha("\n".join(roots).encode()), "dependencyClosurePaths": len(roots), "closurePathsSha256": tool.sha("\n".join(roots).encode()), "excludedTargets": targets}}
        self.save_proofs()

    def save_proofs(self):
        self.runtime_path.write_bytes(tool.encoded(self.runtime)); self.missing_path.write_bytes(tool.encoded(self.missing))

    def run_tool(self, apply=False):
        return tool.quarantine(self.project, self.runtime_path, self.missing_path, apply, apply,
                                tool.sha(self.manifest_path.read_bytes()), tool.sha(self.runtime_path.read_bytes()), tool.sha(self.missing_path.read_bytes()))

    def originals(self):
        paths = [self.stage / p for p in tool.TARGETS] + [self.stage / (p + ".meta") for p in tool.TARGETS]
        paths += [self.manifest_path, self.work / "receipts/033.json", self.archive, self.main, self.stage / (tool.FOLDER + "/Kept.txt")]
        return {path: path.read_bytes() for path in paths}

    def test_default_dry_run_preserves_all_assets_canonical_and_archives(self):
        before = self.originals(); report, _ = self.run_tool()
        self.assertEqual("dry-run-ready", report["status"]); self.assertEqual(4, len(report["files"]))
        self.assertFalse((self.work / "SourceOnly").exists())
        for path, data in before.items(): self.assertEqual(data, path.read_bytes())

    def test_apply_preserves_exact_four_bytes_guid_records_and_every_other_asset(self):
        before = self.originals(); report, path = self.run_tool(True)
        self.assertEqual("complete", report["status"])
        manifest = json.loads(self.manifest_path.read_bytes()); product = next(p for p in manifest["products"] if p["id"] == "033")
        self.assertEqual(4, len(product["sourceOnlyFiles"])); self.assertEqual(1, len(product["files"]))
        self.assertEqual(product, json.loads((self.work / "receipts/033.json").read_bytes()))
        for row in report["files"]:
            old = self.stage / row["path"]; self.assertFalse(old.exists())
            self.assertEqual(before[old], Path(row["destination"]).read_bytes())
            self.assertEqual(before[old], (path.parent / "backups" / row["path"]).read_bytes())
        for target in (self.main, self.archive, self.stage / (tool.FOLDER + "/Kept.txt")): self.assertEqual(before[target], target.read_bytes())

    def test_inbound_reference_or_incomplete_root_scope_refuses(self):
        proof = self.runtime["missingProviderTerrainDependencyProof"]
        proof["excludedTargets"][0]["referencedByOtherRootAssets"] = True; self.save_proofs()
        with self.assertRaisesRegex(ValueError, "inbound-reference"): self.run_tool(True)
        self.finish(); self.runtime["missingProviderTerrainDependencyProof"]["rootAssetsChecked"] -= 1; self.save_proofs()
        with self.assertRaisesRegex(ValueError, "every current"): self.run_tool(True)

    def test_stale_manifest_payload_meta_or_guid_refuses(self):
        self.runtime["manifestSha256"] = "0"*64; self.save_proofs()
        with self.assertRaisesRegex(ValueError, "stale"): self.run_tool(True)
        self.finish(); target = self.runtime["missingProviderTerrainDependencyProof"]["excludedTargets"][0]; target["metadataSha256"] = "0"*64; self.save_proofs()
        with self.assertRaisesRegex(ValueError, "payload/meta/GUID"): self.run_tool(True)
        self.finish(); relative = next(iter(tool.TARGETS)); source = self.stage / relative; source.write_bytes(source.read_bytes()[:-1] + b"X")
        with self.assertRaisesRegex(ValueError, "canonical SHA"): self.run_tool(True)

    def test_failed_runtime_job_cannot_authorize_quarantine(self):
        self.runtime.update(status="failed", errors=["Some other runtime failure"]); self.save_proofs()
        with self.assertRaisesRegex(ValueError, "clean completed"): self.run_tool(True)

    def test_missing_source_texture_recovery_candidate_refuses(self):
        self.missing["packageMatches"] = [{"member": "foundOriginalTexture"}]; self.save_proofs()
        with self.assertRaisesRegex(ValueError, "exact inspected"): self.run_tool(True)

    def test_current_terrain_must_still_have_original_missing_references(self):
        relative = next(iter(tool.TARGETS)); path = self.stage / relative
        raw = binary.serialized_fixture(22, ["e"*32]); path.write_bytes(raw)
        record = next(r for r in self.product["files"] if r["path"] == relative); record.update(bytes=len(raw), sha256=tool.sha(raw)); self.finish()
        with self.assertRaisesRegex(ValueError, "no longer contains"): self.run_tool(True)

    def test_destination_exists_or_main_root_redirect_refuses(self):
        relative = next(iter(tool.TARGETS)); destination = self.work / "SourceOnly" / relative; destination.parent.mkdir(parents=True); destination.write_bytes(b"preserved-previous-source")
        with self.assertRaisesRegex(ValueError, "destination already exists"): self.run_tool(True)
        self.manifest["stageRoot"] = str(self.project / tool.ROOT); self.finish()
        with self.assertRaisesRegex(ValueError, "isolated current library"): self.run_tool(True)

    def test_manifest_write_failure_rolls_back_all_moves_and_receipt(self):
        before = self.originals(); actual = tool.atomic_write; failed = False
        def injected(path, data):
            nonlocal failed
            if Path(path) == self.manifest_path and not failed:
                failed = True; raise OSError("synthetic canonical write failure")
            return actual(path, data)
        with mock.patch.object(tool, "atomic_write", side_effect=injected):
            with self.assertRaisesRegex(OSError, "canonical write"): self.run_tool(True)
        for path, data in before.items(): self.assertEqual(data, path.read_bytes())
        report = json.loads(Path(json.loads((self.work / "source-only-quarantine-latest.json").read_bytes())["report"]).read_bytes())
        self.assertEqual([], report["rollbackErrors"])

    def test_partial_move_failure_rolls_back_earlier_asset_meta_pair(self):
        before = self.originals(); actual = tool.os.rename; calls = 0
        def injected(source, target):
            nonlocal calls
            calls += 1
            if calls == 3: raise OSError("synthetic third move failure")
            return actual(source, target)
        with mock.patch.object(tool.os, "rename", side_effect=injected):
            with self.assertRaisesRegex(OSError, "third move"): self.run_tool(True)
        for path, data in before.items(): self.assertEqual(data, path.read_bytes())

    def test_completion_report_failure_rolls_back_sources_and_bookkeeping(self):
        before = self.originals(); actual = tool.atomic_write; failed = False
        def injected(path, data):
            nonlocal failed
            if Path(path).name == "report.json" and json.loads(data)["status"] == "complete" and not failed:
                failed = True; raise OSError("synthetic final report failure")
            return actual(path, data)
        with mock.patch.object(tool, "atomic_write", side_effect=injected):
            with self.assertRaisesRegex(OSError, "final report"): self.run_tool(True)
        for path, data in before.items(): self.assertEqual(data, path.read_bytes())

    def test_original_binary_coverage_unchanged_and_any_target_coverage_refused(self):
        # A plain text fixture entry in the original audit coverage stays exact;
        # quarantine does not recompute or shrink the historical896-path list.
        self.products[1]["originalBinaryGuidCollisionBlockers"] = [self.products[1]["files"][0]["path"]]
        self.finish(); expected = copy.deepcopy([p["originalBinaryGuidCollisionBlockers"] for p in self.products]); self.run_tool(True)
        after = json.loads(self.manifest_path.read_bytes())
        self.assertEqual(expected, [p["originalBinaryGuidCollisionBlockers"] for p in after["products"]])

    def test_target_cannot_be_removed_from_original_binary_coverage(self):
        self.product["originalBinaryGuidCollisionBlockers"] = [next(iter(tool.TARGETS))]; self.finish()
        with self.assertRaisesRegex(ValueError, "original896"): self.run_tool(True)

    def test_target_in_authoritative_recovery_proofs_alone_refuses(self):
        self.product["binaryGuidRecoveryProofs"] = [{"path": next(iter(tool.TARGETS))}]; self.finish()
        with self.assertRaisesRegex(ValueError, "original896"): self.run_tool(True)

    def test_current_exact_original_texture_recovery_candidate_refuses(self):
        self.products[1]["files"].append({"path": self.products[1]["folder"] + "/RecoveredTexture.meta", "bytes": 1, "sha256": "0"*64, "guid": next(iter(tool.MISSING))})
        self.finish()
        with self.assertRaisesRegex(ValueError, "recovery candidate exists"): self.run_tool(True)

    def test_target_metadata_guid_must_have_unique_current_owner(self):
        self.products[1]["files"].append({"path": self.products[1]["folder"] + "/Ambiguous.meta", "bytes": 1, "sha256": "0"*64, "guid": next(iter(tool.TARGETS.values()))["guid"]})
        self.finish()
        with self.assertRaisesRegex(ValueError, "exactly one canonical"): self.run_tool(True)

    def test_apply_requires_explicit_stopped_editor_and_all_reviewed_shas(self):
        with self.assertRaisesRegex(ValueError, "stopped Editor"):
            tool.quarantine(self.project, self.runtime_path, self.missing_path, True)

    def test_rollback_preserves_later_foreign_canonical_write(self):
        actual = tool.atomic_write; failed = False; receipt = self.work / "receipts/033.json"; foreign = b"foreign-canonical-edit-preserved"
        def injected(path, data):
            nonlocal failed
            if Path(path) == self.manifest_path and not failed:
                failed = True; receipt.write_bytes(foreign); raise OSError("injected after foreign receipt edit")
            return actual(path, data)
        with mock.patch.object(tool, "atomic_write", side_effect=injected):
            with self.assertRaisesRegex(OSError, "foreign receipt"): self.run_tool(True)
        self.assertEqual(foreign, receipt.read_bytes())
        report = json.loads(Path(json.loads((self.work / "source-only-quarantine-latest.json").read_bytes())["report"]).read_bytes())
        self.assertEqual(1, len(report["rollbackErrors"])); self.assertIn("foreign canonical", report["rollbackErrors"][0]["error"])

    def test_rollback_preserves_foreign_modified_quarantined_destination(self):
        actual = tool.os.rename; calls = 0; first = next(iter(tool.TARGETS)); destination = self.work / "SourceOnly" / first; foreign = b"foreign-source-only-edit-preserved"
        def injected(source, target):
            nonlocal calls
            calls += 1
            if calls == 3:
                destination.write_bytes(foreign); raise OSError("injected after foreign destination edit")
            return actual(source, target)
        with mock.patch.object(tool.os, "rename", side_effect=injected):
            with self.assertRaisesRegex(OSError, "foreign destination"): self.run_tool(True)
        self.assertEqual(foreign, destination.read_bytes()); self.assertFalse((self.stage / first).exists())
        report = json.loads(Path(json.loads((self.work / "source-only-quarantine-latest.json").read_bytes())["report"]).read_bytes())
        self.assertEqual(1, len(report["rollbackErrors"])); self.assertIn("foreign-modified", report["rollbackErrors"][0]["error"])

    def test_input_path_hash_uses_unity_utf16_ordinal_order(self):
        values = ["Assets/\ue000", "Assets/\U00010000"]
        self.assertEqual(list(reversed(values)), sorted(values, key=tool.ordinal_key))


if __name__ == "__main__": unittest.main()
