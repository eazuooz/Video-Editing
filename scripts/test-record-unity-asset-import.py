"""Post-import recording fixtures; no real project, archive or Unity is used."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("record_unity_import", Path(__file__).with_name("record-unity-asset-import.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RecordingFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="yamyam-import-record-fixture-")
        self.project = Path(self.temp.name) / "Main"
        (self.project / "ProjectSettings").mkdir(parents=True)
        (self.project / "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.6.0f1")
        (self.project / "Assets").mkdir()
        self.sentinel = self.project / "Assets/Preserved.cs"
        self.sentinel.write_bytes(b"unrelated project source")
        self.work = self.project / "Library/YamyamAssetLibrary"
        self.root = self.work / "headless-project/Assets/ThirdParty/YamyamAssetLibrary"
        self.root.mkdir(parents=True)
        (self.work / "receipts").mkdir()
        self.manifest_path = self.work / "staging-manifest.json"
        self.receipt = self.work / "receipts/001.json"
        self.product = {"id": "001", "folder": "001-demo", "status": "complete", "sourceUrl": "https://example.invalid/fixture",
                        "files": [], "guidRemaps": {}}
        self.add_old("001-demo/Example.prefab", b"original prefab", source={"kind": "unitypackage", "originalPath": "Assets/Demo/Example.prefab"})
        self.add_old("001-demo/Example.prefab.meta", self.meta("a" * 32), guid="a" * 32)
        self.add_old("001-demo.meta", self.meta("b" * 32, folder=True), guid="b" * 32)
        self.original_archive = Path(self.temp.name) / "source-original.zip"
        self.original_archive.write_bytes(b"not a real archive; recorder must never read it")
        self.save_baseline()

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def meta(guid, folder=False):
        return ("fileFormatVersion: 2\nguid: " + guid + ("\nfolderAsset: yes" if folder else "") + "\n").encode()

    def add_old(self, relative, data, guid=None, source=None):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        record = {"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        if guid:
            record["guid"] = guid
        if source:
            record["source"] = source
        self.product["files"].append(record)

    def save_baseline(self):
        manifest = {"schemaVersion": 1, "project": str(self.project), "stageRoot": str(self.root),
                    "targetAssetRoot": module.TARGET, "products": [self.product]}
        self.manifest_path.write_bytes(module.encoded_json(manifest))
        self.receipt.write_bytes(module.encoded_json(self.product))
        self.manifest_before, self.receipt_before = self.manifest_path.read_bytes(), self.receipt.read_bytes()

    def assert_books_unchanged(self):
        self.assertEqual(self.manifest_before, self.manifest_path.read_bytes())
        self.assertEqual(self.receipt_before, self.receipt.read_bytes())
        self.assertEqual(b"unrelated project source", self.sentinel.read_bytes())

    def test_single_hash_pass_updates_content_meta_generated_assets_and_root_meta(self):
        prefab = self.root / "001-demo/Example.prefab"
        prefab.write_bytes(b"prefab updated by the offline fixture importer")
        old_meta = self.root / "001-demo/Example.prefab.meta"
        old_meta.write_bytes(self.meta("a" * 32) + b"NativeFormatImporter:\n  userData: updated\n")
        generated = {"001-demo/Generated/Preview.mat": b"generated material", "001-demo/Generated/Preview.mat.meta": self.meta("c" * 32),
                     "001-demo/Generated/Preview.prefab": b"generated prefab", "001-demo/Generated/Preview.prefab.meta": self.meta("d" * 32)}
        for relative, data in generated.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        root_meta = self.root.with_name(self.root.name + ".meta")
        root_meta.write_bytes(self.meta("e" * 32, folder=True))
        original_hash = module.hash_actual_file
        with mock.patch.object(module, "hash_actual_file", wraps=original_hash) as hash_file:
            report = module.record_import(self.project)
        self.assertEqual("complete", report["status"])
        self.assertTrue(report["bookkeepingCommitted"])
        paths = [str(call.args[0]) for call in hash_file.call_args_list]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(8, len(paths))  # seven library files plus its outside root.meta
        self.assertNotIn(str(self.original_archive), paths)
        self.assertEqual(2, report["changedFileCount"])
        self.assertEqual(4, report["newFileCount"])
        self.assertEqual(1, report["newMaterials"])
        self.assertEqual(1, report["newPrefabs"])
        self.assertEqual(2, report["newMetaFiles"])
        manifest = json.loads(self.manifest_path.read_text())
        records = {record["path"]: record for record in manifest["products"][0]["files"]}
        self.assertEqual("a" * 32, records["001-demo/Example.prefab.meta"]["guid"])
        self.assertEqual("Assets/Demo/Example.prefab", records["001-demo/Example.prefab"]["source"]["originalPath"])
        for relative, record in records.items():
            self.assertEqual(record["sha256"], hashlib.sha256((self.root / relative).read_bytes()).hexdigest())
        self.assertEqual("e" * 32, manifest["assetRootMeta"]["guid"])
        self.assertEqual(report["afterManifestSha256"], hashlib.sha256(self.manifest_path.read_bytes()).hexdigest())
        self.assertEqual(manifest["products"][0], json.loads(self.receipt.read_text()))
        self.assertEqual(b"unrelated project source", self.sentinel.read_bytes())

    def test_missing_old_file_fails_before_hash_and_preserves_all_books(self):
        (self.root / "001-demo/Example.prefab").unlink()
        with mock.patch.object(module, "hash_actual_file") as hash_file:
            report = module.record_import(self.project)
        self.assertEqual("validation-failed", report["status"])
        self.assertIn("missing-old-file", {error["kind"] for error in report["errors"]})
        hash_file.assert_not_called()
        self.assert_books_unchanged()

    def test_unexpected_guid_change_fails_without_receipt_or_manifest_mutation(self):
        (self.root / "001-demo/Example.prefab.meta").write_bytes(self.meta("f" * 32))
        report = module.record_import(self.project)
        self.assertEqual("validation-failed", report["status"])
        self.assertIn("changed-old-meta-guid", {error["kind"] for error in report["errors"]})
        self.assert_books_unchanged()

    def test_original_guid_remap_is_used_when_old_meta_has_no_explicit_guid(self):
        record = self.product["files"][1]
        record.pop("guid")
        record["source"] = {"originalGuid": "f" * 32}
        self.product["guidRemaps"] = {"f" * 32: "a" * 32}
        self.save_baseline()
        report = module.record_import(self.project)
        self.assertEqual("complete", report["status"])
        records = {row["path"]: row for row in json.loads(self.receipt.read_text())["files"]}
        self.assertEqual("a" * 32, records["001-demo/Example.prefab.meta"]["guid"])

    def test_new_file_cannot_reuse_an_existing_guid(self):
        new = self.root / "001-demo/New.mat.meta"
        new.write_bytes(self.meta("a" * 32))
        report = module.record_import(self.project)
        self.assertEqual("validation-failed", report["status"])
        self.assertIn("duplicate-actual-guid", {error["kind"] for error in report["errors"]})
        self.assert_books_unchanged()

    def test_library_root_meta_cannot_change_its_previously_recorded_guid(self):
        root_meta = self.root.with_name(self.root.name + ".meta")
        root_meta.write_bytes(self.meta("f" * 32, folder=True))
        manifest = json.loads(self.manifest_path.read_text())
        manifest["assetRootMeta"] = {"guid": "e" * 32, "sha256": "0" * 64, "bytes": 10}
        self.manifest_path.write_bytes(module.encoded_json(manifest))
        self.manifest_before = self.manifest_path.read_bytes()
        report = module.record_import(self.project)
        self.assertEqual("validation-failed", report["status"])
        self.assertIn("changed-library-root-meta-guid", {error["kind"] for error in report["errors"]})
        self.assert_books_unchanged()

    def test_windows_casefold_manifest_spelling_matches_one_actual_file(self):
        self.product["files"][0]["path"] = "001-DEMO/example.PREFAB"
        self.save_baseline()
        report = module.record_import(self.project)
        self.assertEqual("complete", report["status"])
        self.assertEqual(1, len(report["pathSpellingChanges"]))
        paths = {record["path"] for record in json.loads(self.receipt.read_text())["files"]}
        self.assertIn("001-demo/Example.prefab", paths)
        self.assertNotIn("001-DEMO/example.PREFAB", paths)

    def test_duplicate_casefold_manifest_records_and_path_escape_are_rejected(self):
        original = copy.deepcopy(self.product)
        for bad_path in ("001-DEMO/example.PREFAB", "../outside"):
            self.product = copy.deepcopy(original)
            duplicate = copy.deepcopy(self.product["files"][0])
            duplicate["path"] = bad_path
            self.product["files"].append(duplicate)
            self.save_baseline()
            with mock.patch.object(module, "hash_actual_file") as hash_file:
                report = module.record_import(self.project)
            self.assertEqual("validation-failed", report["status"])
            hash_file.assert_not_called()
            self.assert_books_unchanged()

    def test_unowned_new_file_and_archive_are_not_read_or_committed(self):
        for relative in ("Unowned.mat", "001-demo/Source.zip"):
            extra = self.root / relative
            extra.write_bytes(b"must not be read")
            with mock.patch.object(module, "hash_actual_file") as hash_file:
                report = module.record_import(self.project)
            self.assertEqual("validation-failed", report["status"])
            hash_file.assert_not_called()
            self.assert_books_unchanged()
            extra.unlink()

    def test_symlink_is_not_followed(self):
        link = self.root / "001-demo/ArchiveAlias.txt"
        try:
            os.symlink(self.original_archive, link)
        except OSError as error:
            self.skipTest("Host does not permit unprivileged fixture symlinks: " + str(error))
        try:
            with mock.patch.object(module, "hash_actual_file") as hash_file:
                report = module.record_import(self.project)
            self.assertEqual("validation-failed", report["status"])
            self.assertIn("symlink-or-reparse-point", {error["kind"] for error in report["errors"]})
            hash_file.assert_not_called()
            self.assert_books_unchanged()
        finally:
            link.unlink()

    def test_windows_reparse_file_is_rejected_without_reading_contents(self):
        reparse_path = self.root / "001-demo/Example.prefab"
        actual_lstat = module.Path.lstat

        def reparse_info(path, *args, **kwargs):
            info = actual_lstat(path, *args, **kwargs)
            if path == reparse_path:
                return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=module.REPARSE)
            return info

        with mock.patch.object(module.Path, "lstat", new=reparse_info), mock.patch.object(module, "hash_actual_file") as hash_file:
            report = module.record_import(self.project)
        self.assertEqual("validation-failed", report["status"])
        self.assertIn("symlink-or-reparse-point", {error["kind"] for error in report["errors"]})
        hash_file.assert_not_called()
        self.assert_books_unchanged()

    def test_actual_root_outside_owned_workspace_is_rejected_before_hash(self):
        manifest = json.loads(self.manifest_path.read_text())
        manifest["stageRoot"] = str(self.project / "Assets")
        self.manifest_path.write_bytes(module.encoded_json(manifest))
        self.manifest_before = self.manifest_path.read_bytes()
        with mock.patch.object(module, "hash_actual_file") as hash_file:
            report = module.record_import(self.project)
        self.assertEqual("validation-failed", report["status"])
        hash_file.assert_not_called()
        self.assert_books_unchanged()

    def test_json_commit_failure_rolls_back_prior_receipt(self):
        (self.root / "001-demo/Example.prefab").write_bytes(b"changed content")
        actual_replace = module.os.replace
        calls = []

        def fail_manifest_once(source, target):
            calls.append(str(target))
            if Path(target) == self.manifest_path and calls.count(str(target)) == 1:
                raise PermissionError("fixture JSON commit failure")
            return actual_replace(source, target)

        with mock.patch.object(module.os, "replace", side_effect=fail_manifest_once):
            report = module.record_import(self.project)
        self.assertEqual("validation-failed", report["status"])
        self.assertFalse(report["bookkeepingCommitted"])
        self.assertNotIn("afterManifestSha256", report)
        self.assert_books_unchanged()

    def build_baseline_cache(self):
        report = module.record_import(self.project)
        self.assertEqual("complete", report["status"])
        self.manifest_before, self.receipt_before = self.manifest_path.read_bytes(), self.receipt.read_bytes()
        result = module.build_hash_cache(self.project)
        self.assertEqual("cache-built", result["status"])
        self.cache_path = self.work / "hash-reuse-cache.json"
        return json.loads(self.cache_path.read_text())

    def test_cache_build_reads_no_payload_and_binds_immutable_full_baseline(self):
        report = module.record_import(self.project)
        before_books = self.manifest_path.read_bytes(), self.receipt.read_bytes()
        with mock.patch.object(module, "hash_actual_file", side_effect=AssertionError("cache build must not hash")):
            result = module.build_hash_cache(self.project)
        self.assertEqual("cache-built", result["status"])
        self.assertEqual(0, result["assetBytesRead"])
        self.assertEqual(before_books, (self.manifest_path.read_bytes(), self.receipt.read_bytes()))
        cache = json.loads((self.work / "hash-reuse-cache.json").read_text())
        self.assertEqual(report["afterManifestSha256"], cache["sourceManifestSha256"])
        for name, digest in (("sourceManifestSnapshot", "sourceManifestSha256"), ("sourceDeltaSnapshot", "sourceDeltaSha256")):
            self.assertEqual(cache[digest], hashlib.sha256(Path(cache[name]).read_bytes()).hexdigest())
        self.assertEqual({"size", "mtime_ns", "ctime_ns", "ino", "dev"}, set(cache["entries"][0]["fingerprint"]))

    def test_optional_cache_reuses_unchanged_payload_but_always_hashes_metadata(self):
        self.build_baseline_cache()
        with mock.patch.object(module, "hash_actual_file", wraps=module.hash_actual_file) as hashed:
            report = module.record_import(self.project, reuse_unchanged_cache=True)
        self.assertEqual("complete", report["status"])
        self.assertEqual("validated-fingerprint-reuse", report["hashMode"])
        self.assertEqual(1, report["reusedHashFiles"])
        self.assertEqual(len(b"original prefab"), report["reusedHashBytes"])
        self.assertEqual(2, report["hashedFiles"])
        self.assertTrue(all(call.args[0].suffix == ".meta" for call in hashed.call_args_list))
        self.assertEqual(0, report["changedFileCount"])
        self.assertEqual(0, report["newFileCount"])

    def test_fingerprint_change_same_size_hashes_and_records_current_content(self):
        self.build_baseline_cache()
        path = self.root / "001-demo/Example.prefab"
        before = path.stat()
        path.write_bytes(b"modifiedprefab!")
        self.assertEqual(before.st_size, path.stat().st_size)
        os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns + 1_000_000_000))
        report = module.record_import(self.project, reuse_unchanged_cache=True)
        self.assertEqual("complete", report["status"])
        self.assertEqual(0, report["reusedHashFiles"])
        self.assertEqual(3, report["hashedFiles"])
        self.assertEqual(1, report["changedFileCount"])
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), report["changedFiles"][0]["afterSha256"])

    def test_changed_canonical_hash_never_reuses_cache_even_when_stamps_match(self):
        self.build_baseline_cache()
        manifest = json.loads(self.manifest_path.read_text())
        next(row for row in manifest["products"][0]["files"] if row["path"].endswith("Example.prefab"))["sha256"] = "f" * 64
        self.manifest_path.write_bytes(module.encoded_json(manifest))
        report = module.record_import(self.project, reuse_unchanged_cache=True)
        self.assertEqual("complete", report["status"])
        self.assertEqual(0, report["reusedHashFiles"])
        self.assertEqual(1, report["changedFileCount"])

    def test_metadata_guid_change_is_read_and_refused_despite_cached_fingerprint(self):
        cache = self.build_baseline_cache()
        path = self.root / "001-demo/Example.prefab.meta"
        path.write_bytes(self.meta("f" * 32))
        # Even an accidentally restamped hint must never stand in for reading metadata.
        row = next(row for row in cache["entries"] if row["path"].endswith("prefab.meta"))
        row["fingerprint"] = module.fingerprint(path.lstat())
        self.cache_path.write_bytes(module.encoded_json(cache))
        report = module.record_import(self.project, reuse_unchanged_cache=True)
        self.assertEqual("validation-failed", report["status"])
        self.assertIn("changed-old-meta-guid", {row["kind"] for row in report["errors"]})
        self.assert_books_unchanged()

    def test_new_generated_payload_always_hashed_with_cache(self):
        self.build_baseline_cache()
        new = self.root / "001-demo/Generated/New.mat"
        new.parent.mkdir()
        new.write_bytes(b"new material")
        report = module.record_import(self.project, reuse_unchanged_cache=True)
        self.assertEqual("complete", report["status"])
        self.assertEqual(1, report["reusedHashFiles"])
        self.assertEqual(3, report["hashedFiles"])
        self.assertEqual(1, report["newMaterials"])

    def test_malformed_root_duplicate_digest_or_fingerprint_cache_fails_closed(self):
        original = self.build_baseline_cache()
        variants = []
        bad = copy.deepcopy(original); bad["actualRoot"] = str(self.project / "Assets"); variants.append(bad)
        bad = copy.deepcopy(original); bad["entries"].append(copy.deepcopy(bad["entries"][0])); variants.append(bad)
        bad = copy.deepcopy(original); bad["entries"][0]["sha256"] = "0" * 64; variants.append(bad)
        bad = copy.deepcopy(original); bad["entries"][0]["fingerprint"]["ino"] = "invalid"; variants.append(bad)
        for cache in variants:
            self.cache_path.write_bytes(module.encoded_json(cache))
            with mock.patch.object(module, "hash_actual_file") as hashed:
                report = module.record_import(self.project, reuse_unchanged_cache=True)
            self.assertEqual("validation-failed", report["status"])
            hashed.assert_not_called()
            self.assert_books_unchanged()

    def test_cache_baseline_snapshot_tampering_fails_and_ownership_inventory_still_required(self):
        cache = self.build_baseline_cache()
        Path(cache["sourceManifestSnapshot"]).write_bytes(b"{}")
        report = module.record_import(self.project, reuse_unchanged_cache=True)
        self.assertEqual("validation-failed", report["status"])
        self.assert_books_unchanged()
        extra = self.root / "Unowned.mat"; extra.write_bytes(b"never read")
        with mock.patch.object(module, "load_hash_cache") as load:
            report = module.record_import(self.project, reuse_unchanged_cache=True)
        self.assertEqual("validation-failed", report["status"])
        load.assert_not_called()
        self.assert_books_unchanged()

    def test_cache_build_refuses_stale_delta_reuse_baseline_or_postbaseline_change(self):
        self.build_baseline_cache()
        delta_path = self.work / "final-import-delta.json"
        original = json.loads(delta_path.read_text())
        for key, value in (("afterManifestSha256", "0" * 64), ("reusedHashFiles", 1), ("bookkeepingCommitted", False)):
            delta = copy.deepcopy(original); delta[key] = value
            delta_path.write_bytes(module.encoded_json(delta))
            with self.assertRaisesRegex(ValueError, "FULL recorder"):
                module.build_hash_cache(self.project)
        delta_path.write_bytes(module.encoded_json(original))
        path = self.root / "001-demo/Example.prefab"
        info = path.stat()
        completed_ns = int(module.dt.datetime.fromisoformat(original["completedAt"]).timestamp() * 1e9)
        os.utime(path, ns=(info.st_atime_ns, completed_ns + 2_000_000_000))
        with self.assertRaisesRegex(ValueError, "changed after"):
            module.build_hash_cache(self.project)

    def test_cache_use_is_optional_default_still_fully_hashes(self):
        self.build_baseline_cache()
        report = module.record_import(self.project)
        self.assertEqual("complete", report["status"])
        self.assertEqual("full", report["hashMode"])
        self.assertEqual(0, report["reusedHashFiles"])
        self.assertEqual(3, report["hashedFiles"])

    def completed_failed_scan(self):
        self.product["files"][1].pop("guid", None)
        self.save_baseline()
        payload = self.root / "001-demo/Example.prefab"
        payload.write_bytes(b"native importer converted this prefab")
        info = payload.stat()
        os.utime(payload, ns=(info.st_atime_ns, info.st_mtime_ns - 1_000_000_000))
        started = module.utc()
        changes, total = [], 0
        for old in self.product["files"]:
            path = self.root / old["path"]
            current = module.hash_actual_file(path, path.lstat())
            total += current["bytes"]
            if (old["bytes"], old["sha256"]) != (current["bytes"], current["sha256"]):
                changes.append({"productId": "001", "path": old["path"], "beforeSha256": old["sha256"],
                    "beforeBytes": old["bytes"], "afterSha256": current["sha256"], "afterBytes": current["bytes"],
                    "kind": "importer-metadata" if path.suffix == ".meta" else "post-import-content", "source": old.get("source")})
        prior = {"schemaVersion": 1, "startedAt": started, "completedAt": module.utc(), "status": "validation-failed",
                 "manifest": str(self.manifest_path), "beforeManifestSha256": hashlib.sha256(self.manifest_before).hexdigest(),
                 "assetsModifiedByRecorder": False, "bookkeepingCommitted": False, "sourceArchivesRead": False, "gitDataAccessed": False,
                 "errors": [{"kind": "old-meta-guid-unavailable", "productId": "001", "path": "001-demo/Example.prefab.meta"}],
                 "hashedFiles": 3, "hashedBytes": total, "actualRoot": str(self.root), "changedFiles": changes,
                 "newFiles": [], "pathSpellingChanges": [], "failure": "ValueError: Post-hash file/GUID validation failed"}
        path = self.work / "final-import-delta.json"
        path.write_bytes(module.encoded_json(prior))
        return path, prior

    def test_unknown_guid_unchanged_full_metadata_bytes_prove_preservation(self):
        self.product["files"][1].pop("guid")
        self.save_baseline()
        report = module.record_import(self.project)
        self.assertEqual("complete", report["status"])
        self.assertEqual(1, len(report["adoptedUnknownMetaGuids"]))
        proof = report["adoptedUnknownMetaGuids"][0]
        self.assertEqual("unchanged-exact-canonical-bytes", proof["kind"])
        self.assertEqual("a" * 32, proof["guid"])

    def test_unknown_guid_changed_metadata_still_fails(self):
        self.product["files"][1].pop("guid")
        self.save_baseline()
        (self.root / "001-demo/Example.prefab.meta").write_bytes(self.meta("a" * 32) + b"changed settings\n")
        report = module.record_import(self.project)
        self.assertEqual("validation-failed", report["status"])
        self.assertIn("old-meta-guid-unavailable", {error["kind"] for error in report["errors"]})
        self.assert_books_unchanged()

    def test_recovery_adopts_completed_payload_scan_and_rehashes_every_meta(self):
        path, prior = self.completed_failed_scan()
        failed_bytes = path.read_bytes()
        with mock.patch.object(module, "hash_actual_file", wraps=module.hash_actual_file) as hashed:
            report = module.record_import(self.project, recover_completed_scan=path)
        self.assertEqual("complete", report["status"])
        self.assertEqual("recovered-complete-scan", report["hashMode"])
        self.assertEqual(1, report["recoveredScanFiles"])
        self.assertEqual(0, report["reusedHashFiles"])
        self.assertEqual(2, report["hashedFiles"])
        self.assertTrue(all(call.args[0].suffix == ".meta" for call in hashed.call_args_list))
        evidence = report["recoveredCompleteScan"]
        self.assertEqual(failed_bytes, Path(evidence["scanPath"]).read_bytes())
        self.assertEqual(prior["hashedFiles"], evidence["validatedFileCoverage"])
        self.assertEqual(1, len(report["adoptedUnknownMetaGuids"]))
        self.assertEqual(1, report["changedFileCount"])
        cache = module.build_hash_cache(self.project)
        self.assertEqual("cache-built", cache["status"])
        reused = module.record_import(self.project, reuse_unchanged_cache=True)
        self.assertEqual("complete", reused["status"])
        self.assertEqual(1, reused["reusedHashFiles"])

    def test_recovery_newer_payload_is_freshly_hashed_and_named(self):
        path, prior = self.completed_failed_scan()
        payload = self.root / "001-demo/Example.prefab"
        payload.write_bytes(b"subsequent actual content independently hashed")
        old = payload.stat()
        started_ns = int(module.dt.datetime.fromisoformat(prior["startedAt"]).timestamp() * 1e9)
        os.utime(payload, ns=(old.st_atime_ns, started_ns + 1_000_000_000))
        report = module.record_import(self.project, recover_completed_scan=path)
        self.assertEqual("complete", report["status"])
        self.assertEqual(0, report["recoveredScanFiles"])
        self.assertEqual(3, report["hashedFiles"])
        self.assertIn({"path": "001-demo/Example.prefab", "reason": "newer-than-prior-scan-start-or-size-changed"}, report["recoveryRehashedFiles"])
        self.assertEqual(hashlib.sha256(payload.read_bytes()).hexdigest(), report["changedFiles"][0]["afterSha256"])

    def test_recovery_incomplete_or_ambiguous_evidence_fails_without_bookkeeping(self):
        path, original = self.completed_failed_scan()
        mutations = []
        bad = copy.deepcopy(original); bad["hashedFiles"] -= 1; mutations.append(bad)
        bad = copy.deepcopy(original); bad["hashedBytes"] -= 1; mutations.append(bad)
        bad = copy.deepcopy(original); bad["beforeManifestSha256"] = "0" * 64; mutations.append(bad)
        bad = copy.deepcopy(original); bad["errors"].append({"kind": "actual-file-read-error", "path": "001-demo/Example.prefab"}); mutations.append(bad)
        bad = copy.deepcopy(original); bad["changedFiles"].append(copy.deepcopy(bad["changedFiles"][0])); mutations.append(bad)
        bad = copy.deepcopy(original); bad["changedFiles"][0]["beforeSha256"] = "0" * 64; mutations.append(bad)
        for bad in mutations:
            path.write_bytes(module.encoded_json(bad))
            with mock.patch.object(module, "hash_actual_file") as hashed:
                report = module.record_import(self.project, recover_completed_scan=path)
            self.assertEqual("validation-failed", report["status"])
            hashed.assert_not_called()
            self.assert_books_unchanged()

    def test_recovered_baseline_cache_refuses_changed_immutable_source_proof(self):
        path, _prior = self.completed_failed_scan()
        report = module.record_import(self.project, recover_completed_scan=path)
        self.assertEqual("complete", report["status"])
        Path(report["recoveredCompleteScan"]["scanPath"]).write_bytes(b"{}")
        with self.assertRaisesRegex(ValueError, "snapshot digest"):
            module.build_hash_cache(self.project)

    def test_recovery_includes_exact_outside_root_metadata_and_refuses_drift(self):
        path, prior = self.completed_failed_scan()
        root_meta = self.root.with_name(self.root.name + ".meta")
        root_meta.write_bytes(self.meta("e" * 32, folder=True))
        info = root_meta.lstat()
        value = module.hash_actual_file(root_meta, info)
        prior["rootMetaChange"] = {"afterSha256": value["sha256"], "afterBytes": value["bytes"], "guid": value["guid"],
                                   "beforeSha256": None, "beforeBytes": None, "kind": "new-root-metadata"}
        prior["hashedFiles"] += 1
        prior["hashedBytes"] += value["bytes"]
        path.write_bytes(module.encoded_json(prior))
        report = module.record_import(self.project, recover_completed_scan=path)
        self.assertEqual("complete", report["status"])
        self.assertEqual(3, report["hashedFiles"])
        self.assertEqual(1, report["recoveredScanFiles"])
        self.assertEqual("e" * 32, report["rootMeta"]["guid"])
        self.assertEqual(4, report["recoveredCompleteScan"]["validatedFileCoverage"])
        self.assertEqual("cache-built", module.build_hash_cache(self.project)["status"])

    def test_recovery_root_metadata_mismatch_keeps_books_and_original_failure(self):
        path, prior = self.completed_failed_scan()
        root_meta = self.root.with_name(self.root.name + ".meta")
        root_meta.write_bytes(self.meta("e" * 32, folder=True))
        value = module.hash_actual_file(root_meta, root_meta.lstat())
        prior["rootMetaChange"] = {"afterSha256": "0" * 64, "afterBytes": value["bytes"], "guid": value["guid"]}
        prior["hashedFiles"] += 1; prior["hashedBytes"] += value["bytes"]
        original = module.encoded_json(prior); path.write_bytes(original)
        report = module.record_import(self.project, recover_completed_scan=path)
        self.assertEqual("validation-failed", report["status"])
        self.assertIn("Root metadata differs", report["failure"])
        snapshot = self.work / "completed-scan-recovery" / hashlib.sha256(original).hexdigest() / "failed-scan.json"
        self.assertEqual(original, snapshot.read_bytes())
        self.assert_books_unchanged()

    def test_cache_cannot_be_written_inside_source_payload_or_canonical_bookkeeping(self):
        for target in (self.manifest_path, self.root / "001-demo/Cache.json", self.work / "hash-caches/../staging-manifest.json"):
            with self.assertRaises(ValueError):
                module.cache_path_owned(self.project, target)


if __name__ == "__main__":
    unittest.main()
