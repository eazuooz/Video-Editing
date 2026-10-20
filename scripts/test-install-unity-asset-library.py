"""Owned temporary fixtures only; never invokes Unity or the real asset library."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("installer", Path(__file__).with_name("install-unity-asset-library.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class InstallFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="yamyam-install-fixture-")
        self.base = Path(self.temp.name)
        self.project = self.base / "repo/unity/VideoEditing"
        self.work = self.project / "Library/YamyamAssetLibrary"
        self.headless = self.work / "headless-project"
        self.source = self.headless / m.TARGET
        self.destination = self.project / m.TARGET
        self.inner = self.headless / "Library/YamyamAssetLibrary"
        self.inner.mkdir(parents=True)
        self.source.mkdir(parents=True)
        self.destination.parent.mkdir(parents=True)
        (self.project / "ProjectSettings").mkdir()
        (self.project / "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.6.0f1\n")
        (self.project / "ProjectSettings/Keep.asset").write_text("existing scene/pipeline settings\n")
        self.original_archive = self.base / "original.unitypackage"
        self.original_archive.write_bytes(b"original archive is never opened or modified")
        self.packages = {"dependencies": {"com.unity.core": "1.0.0"}}
        self.lock = {"dependencies": {"com.unity.core": {"version": "1.0.0", "source": "registry", "depth": 0, "dependencies": {}}}}
        self.old_packages = {}
        baseline = []
        for name, value in (("manifest.json", self.packages), ("packages-lock.json", self.lock)):
            path = self.project / "Packages" / name
            path.parent.mkdir(exist_ok=True)
            data = m.encode(value)
            path.write_bytes(data)
            self.old_packages[name] = data
            baseline.append({"path": str(path), "bytes": len(data), "sha256": m.sha(data)})
        self.write(self.work / "preserved-project-baseline.json", baseline)
        isolated_manifest = copy.deepcopy(self.packages)
        self.required_dependencies = {m.ADDRESSABLES: m.ADDRESSABLES_VERSION,
                                      "com.unity.cinemachine": "6.6.0", "com.unity.splines": "2.9.1"}
        isolated_manifest["dependencies"].update(self.required_dependencies)
        isolated_lock = copy.deepcopy(self.lock)
        for name, version, source, dependencies in (
                (m.ADDRESSABLES, m.ADDRESSABLES_VERSION, "registry", {"com.unity.scriptablebuildpipeline": "3.0.3"}),
                ("com.unity.cinemachine", "6.6.0", "builtin", {"com.unity.splines": "2.8.4"}),
                ("com.unity.splines", "2.9.1", "registry", {"com.unity.settings-manager": "1.0.3"}),
                ("com.unity.settings-manager", "2.1.1", "registry", {}),
                ("com.unity.scriptablebuildpipeline", "3.0.3", "registry", {})):
            row = {"version": version, "depth": 0 if name in self.required_dependencies else 1,
                   "source": source, "dependencies": dependencies}
            if source == "registry":
                row["url"] = "https://packages.unity.com"
            isolated_lock["dependencies"][name] = row
        self.write(self.headless / "Packages/manifest.json", isolated_manifest)
        self.write(self.headless / "Packages/packages-lock.json", isolated_lock)
        self.products = []
        for index in range(84):
            folder = f"{index:03d}-fixture"
            pack = self.source / folder
            pack.mkdir()
            entries = [(pack / "asset.txt", f"payload {index:03d}".encode(), None),
                       (pack / "asset.txt.meta", f"fileFormatVersion: 2\nguid: {index * 2 + 1:032x}\n".encode(), f"{index * 2 + 1:032x}"),
                       (self.source / (folder + ".meta"), f"fileFormatVersion: 2\nguid: {index * 2 + 2:032x}\nfolderAsset: yes\n".encode(), f"{index * 2 + 2:032x}")]
            records = []
            for path, data, guid in entries:
                path.write_bytes(data)
                record = {"path": path.relative_to(self.source).as_posix(), "bytes": len(data), "sha256": m.sha(data), "source": {"kind": "fixture"}}
                if guid:
                    record["guid"] = guid
                records.append(record)
            product = {"id": f"{index:03d}", "index": index, "title": "Fixture", "folder": folder,
                       "status": "complete", "files": records, "finalImportRecordedAt": "2026-10-19T00:01:00+00:00", "finalImportActualRoot": str(self.source)}
            if index == 0:
                product["guidRemaps"] = {"a" * 32: "b" * 32}
                product["binaryGuidRecoveryProofs"] = [{"path": records[0]["path"], "proofVersion": 1, "status": "historical-scope-only"}]
            self.products.append(product)
            self.write(self.work / "receipts" / (product["id"] + ".json"), product)
        self.meta = self.source.with_name(self.source.name + ".meta")
        meta_bytes = ("fileFormatVersion: 2\nguid: " + "f" * 32 + "\nfolderAsset: yes\n").encode()
        self.meta.write_bytes(meta_bytes)
        self.manifest = {"stageRoot": str(self.source), "products": self.products,
                         "assetRootMeta": {"absolutePath": str(self.meta), "bytes": len(meta_bytes), "sha256": m.sha(meta_bytes), "guid": "f" * 32}}
        self.manifest_path = self.work / "staging-manifest.json"
        self.write(self.manifest_path, self.manifest)
        self.delta = {"status": "complete", "bookkeepingCommitted": True, "actualRoot": str(self.source),
                      "manifest": str(self.manifest_path), "afterManifestSha256": m.sha(self.manifest_path.read_bytes()),
                      "products": 84, "assetRootFiles": 252}
        self.write(self.work / "final-import-delta.json", self.delta)
        first = self.products[0]["files"][0]
        map_sha = m.sha(json.dumps(self.products[0]["guidRemaps"], sort_keys=True, separators=(",", ":")).encode())
        self.binary_proof = {
            "proofVersion": 2, "status": "pass", "errors": [], "productsChecked": 1, "filesChecked": 1,
            "filesWithCollisionSpellings": 0, "exactCanonicalExternalReferenceHits": 0, "staleReceiptFiles": 0,
            "sourceManifestContext": {"path": str(self.manifest_path), "stageRoot": str(self.source), "targetAssetRoot": m.TARGET, "products": 84},
            "products": [{"id": "000", "guidMapSha256": map_sha, "originalProofFiles": 1, "files": [{
                "productId": "000", "path": first["path"], "actualPath": str(self.source / first["path"]),
                "proofVersion": 2, "guidMapSha256": map_sha, "status": "collided-guids-absent", "binaryKind": "serialized-file",
                "actualSha256": first["sha256"], "receiptSha256": first["sha256"], "receiptBytes": first["bytes"],
                "fileBytes": first["bytes"], "receiptMatches": True, "exactCanonicalExternalHits": [], "collidingReferences": []}]}]}
        self.binary_path = self.work / "binary-guid-encoding-recheck.json"
        self.write(self.binary_path, self.binary_proof)
        self.validation = {"status": "pass", "nonce": "fixture-session", "unityVersion": "6000.6.0f1",
                           "completedUtc": "2026-10-19T00:00:00+00:00", "issues": []}
        self.fallback = {"status": "completed", "jobsTotal": 84, "jobsCompleted": 84, "issues": []}
        self.write(self.inner / "validation.json", self.validation)
        self.write(self.inner / "fallback-preparation-report.json", self.fallback)
        self.result = {"active": False, "status": "complete", "exitCode": 0, "nonce": "fixture-session", "error": None,
                       "projectPath": str(self.headless), "completedUtc": "2026-10-19T00:00:00+00:00",
                       "validationPath": str(self.inner / "validation.json"), "fallbackPath": str(self.inner / "fallback-preparation-report.json")}
        self.write_result()
        self.settings = m.settings_snapshot(self.project)
        self.liveness = mock.patch.object(m, "process_running", return_value=False)
        self.liveness.start()

    def tearDown(self):
        self.liveness.stop()
        self.temp.cleanup()

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(m.encode(value))

    def write_result(self):
        result_path = self.inner / "headless-result.json"
        self.write(result_path, self.result)
        self.proof = {"status": "exited", "exitCode": 0, "pid": 12345, "projectPath": str(self.headless),
                      "nonce": self.result["nonce"], "headlessResultSha256": m.sha(result_path.read_bytes())}
        self.write(self.work / "headless-process-exit.json", self.proof)

    def unchanged(self):
        self.assertTrue(self.source.is_dir())
        self.assertTrue(self.meta.is_file())
        self.assertFalse(self.destination.exists())
        self.assertFalse(self.destination.with_name(self.destination.name + ".meta").exists())
        for name, data in self.old_packages.items():
            self.assertEqual(data, (self.project / "Packages" / name).read_bytes())
        self.assertEqual(self.settings, m.settings_snapshot(self.project))
        self.assertEqual(b"original archive is never opened or modified", self.original_archive.read_bytes())

    def test_dry_run_is_structural_then_apply_moves_preserving_guid_and_settings(self):
        before = self.meta.read_bytes()
        manifest_bytes = self.manifest_path.read_bytes()
        dry = m.install(self.project)
        self.assertEqual("ready-dry-run", dry["status"], dry)
        self.assertFalse(dry["fullLibraryHashesVerified"])
        self.unchanged()
        result = m.install(self.project, apply=True)
        self.assertEqual("installed", result["status"], result)
        self.assertTrue(result["fullLibraryHashesVerified"])
        self.assertFalse(self.source.exists())
        self.assertEqual(before, self.destination.with_name(self.destination.name + ".meta").read_bytes())
        self.assertEqual(b"payload 000", (self.destination / "000-fixture/asset.txt").read_bytes())
        package, _ = m.read_json(self.project / "Packages/manifest.json")
        self.assertEqual({**self.packages["dependencies"], **self.required_dependencies}, package["dependencies"])
        self.assertEqual(self.settings, m.settings_snapshot(self.project))
        self.assertEqual(manifest_bytes, self.manifest_path.read_bytes())

    def test_same_size_mutation_is_not_rehashed_in_dry_run_but_blocks_apply(self):
        asset = self.source / "000-fixture/asset.txt"
        asset.write_bytes(b"X" * asset.stat().st_size)
        self.assertEqual("ready-dry-run", m.install(self.project)["status"])
        result = m.install(self.project, apply=True)
        self.assertEqual("failed", result["status"])
        self.assertIn("hash/identity mismatch", result["error"])
        self.unchanged()

    def test_running_exit_or_pending_capture_refuses_without_writes(self):
        with mock.patch.object(m, "process_running", return_value=True):
            self.assertEqual("failed", m.install(self.project, apply=True)["status"])
        pending = self.project / "Library/AiCraftProduction.request"
        pending.write_text("render")
        result = m.install(self.project, apply=True)
        self.assertEqual("failed", result["status"])
        self.assertIn("capture", result["error"])
        self.unchanged()

    def test_active_progress_capture_and_existing_destination_refused(self):
        output = self.project.parent.parent / "shared/output/ai-game-development-human-craft/unity-production/scene"
        output.mkdir(parents=True)
        (output / "progress.txt").write_text("60/1800")
        self.assertIn("capture progress", m.install(self.project)["error"])
        (output / "progress.txt").unlink()
        self.destination.mkdir()
        sentinel = self.destination / "existing.txt"
        sentinel.write_text("must stay")
        self.assertEqual("failed", m.install(self.project, apply=True)["status"])
        self.assertEqual("must stay", sentinel.read_text())

    def test_stale_receipt_or_delta_and_changed_package_baseline_refused(self):
        path = self.work / "receipts/000.json"
        original = path.read_bytes()
        changed = copy.deepcopy(self.products[0]); changed["files"][0]["bytes"] += 1
        self.write(path, changed)
        self.assertIn("receipt is stale", m.install(self.project)["error"])
        path.write_bytes(original)
        delta = dict(self.delta, afterManifestSha256="0" * 64)
        self.write(self.work / "final-import-delta.json", delta)
        self.assertIn("recorder delta is stale", m.install(self.project)["error"])
        self.write(self.work / "final-import-delta.json", self.delta)
        (self.project / "Packages/manifest.json").write_bytes(self.old_packages["manifest.json"] + b" ")
        self.assertIn("Packages changed", m.install(self.project)["error"])
        self.assertTrue(self.source.is_dir())

    def test_isolated_lock_cannot_change_existing_versions_or_add_unrelated(self):
        path = self.headless / "Packages/packages-lock.json"
        original = path.read_bytes()
        lock = json.loads(original)
        lock["dependencies"]["com.unity.core"]["version"] = "9.9.9"
        self.write(path, lock)
        self.assertIn("existing package", m.install(self.project)["error"])
        lock = json.loads(original)
        lock["dependencies"]["unrelated.package"] = {"version": "1.0.0", "dependencies": {}}
        self.write(path, lock)
        self.assertIn("unrelated packages", m.install(self.project)["error"])
        self.unchanged()

    def test_registry_cinemachine_cannot_masquerade_as_verified_builtin(self):
        path = self.headless / "Packages/packages-lock.json"
        lock, _ = m.read_json(path)
        lock["dependencies"]["com.unity.cinemachine"].update(version="3.1.7", source="registry", url="https://packages.unity.com")
        self.write(path, lock)
        self.assertIn("reviewed version", m.install(self.project)["error"])
        lock["dependencies"]["com.unity.cinemachine"]["version"] = "6.6.0"
        self.write(path, lock)
        self.assertIn("identity/source", m.install(self.project)["error"])
        self.unchanged()

    def test_reviewed_runtime_closure_refuses_foreign_registry_or_unreviewed_reachable_package(self):
        path = self.headless / "Packages/packages-lock.json"
        lock, original = m.read_json(path)
        lock["dependencies"]["com.unity.settings-manager"]["url"] = "https://unreviewed.invalid"
        self.write(path, lock)
        self.assertIn("official Unity registry", m.install(self.project)["error"])
        lock = json.loads(original)
        lock["dependencies"]["com.unity.splines"]["dependencies"]["com.unity.unreviewed"] = "1.0.0"
        lock["dependencies"]["com.unity.unreviewed"] = {"version": "1.0.0", "source": "registry", "dependencies": {}, "url": "https://packages.unity.com"}
        self.write(path, lock)
        self.assertIn("unrelated packages", m.install(self.project)["error"])
        self.unchanged()

    def test_missing_reviewed_transitive_package_refused(self):
        path = self.headless / "Packages/packages-lock.json"
        lock, _ = m.read_json(path)
        del lock["dependencies"]["com.unity.scriptablebuildpipeline"]
        self.write(path, lock)
        self.assertIn("absent from isolated lock", m.install(self.project)["error"])
        self.unchanged()

    def test_builtin_package_url_and_unreviewed_direct_dependency_refused(self):
        path = self.headless / "Packages/packages-lock.json"
        lock, original = m.read_json(path)
        lock["dependencies"]["com.unity.cinemachine"]["url"] = "https://packages.unity.com"
        self.write(path, lock)
        self.assertIn("editor-bundled identity", m.install(self.project)["error"])
        path.write_bytes(original)
        manifest, _ = m.read_json(self.headless / "Packages/manifest.json")
        manifest["dependencies"]["com.unity.unreviewed"] = "1.0.0"
        self.write(self.headless / "Packages/manifest.json", manifest)
        self.assertIn("three reviewed runtime", m.install(self.project)["error"])
        self.unchanged()

    def test_package_depth_can_change_without_changing_baseline_identity(self):
        path = self.headless / "Packages/packages-lock.json"
        lock, _ = m.read_json(path)
        lock["dependencies"]["com.unity.core"]["depth"] = 2
        self.write(path, lock)
        self.assertEqual("ready-dry-run", m.install(self.project)["status"])
        self.unchanged()

    def test_exact_owned_stage_root_and_current_main_guid_are_required(self):
        altered = copy.deepcopy(self.manifest)
        altered["stageRoot"] = str(self.source.parent)
        self.write(self.manifest_path, altered)
        delta = dict(self.delta, afterManifestSha256=m.sha(self.manifest_path.read_bytes()))
        self.write(self.work / "final-import-delta.json", delta)
        self.assertIn("exact isolated Assets root", m.install(self.project)["error"])
        self.write(self.manifest_path, self.manifest)
        self.write(self.work / "final-import-delta.json", self.delta)
        existing = self.project / "Assets/Existing.meta"
        existing.write_text("fileFormatVersion: 2\nguid: " + f"{1:032x}" + "\n")
        result = m.install(self.project, apply=True)
        self.assertEqual("failed", result["status"])
        self.assertIn("GUID collides", result["error"])
        self.unchanged()

    def test_rename_failure_rolls_back_metadata_and_packages(self):
        original_rename = m.rename_retry
        def fail_root(start, end, attempts=5):
            if Path(start) == self.source:
                raise PermissionError("fixture root rename failure")
            return original_rename(start, end, attempts)
        with mock.patch.object(m, "rename_retry", side_effect=fail_root):
            result = m.install(self.project, apply=True)
        self.assertEqual("failed", result["status"])
        self.assertTrue(result["rollbackAttempted"])
        self.assertTrue(result["rollbackComplete"], result)
        self.unchanged()

    def test_post_move_missing_metadata_restores_owned_backup(self):
        original_rename = m.rename_retry
        def remove_after_root(start, end, attempts=5):
            original_rename(start, end, attempts)
            if Path(start) == self.source:
                self.destination.with_name(self.destination.name + ".meta").unlink()
        with mock.patch.object(m, "rename_retry", side_effect=remove_after_root):
            result = m.install(self.project, apply=True)
        self.assertEqual("failed", result["status"])
        self.assertIn("metadata disappeared", result["error"])
        self.assertTrue(result["rootMetadataRestoredFromBackup"])
        self.assertTrue(result["rollbackComplete"], result)
        self.unchanged()

    def test_post_move_foreign_metadata_is_preserved_during_rollback(self):
        original_rename = m.rename_retry
        original_meta = self.meta.read_bytes()
        foreign = b"newer foreign metadata must not be overwritten"
        def change_after_root(start, end, attempts=5):
            original_rename(start, end, attempts)
            if Path(start) == self.source:
                self.destination.with_name(self.destination.name + ".meta").write_bytes(foreign)
        with mock.patch.object(m, "rename_retry", side_effect=change_after_root):
            result = m.install(self.project, apply=True)
        self.assertEqual("failed", result["status"])
        self.assertIn("metadata changed", result["error"])
        self.assertFalse(result["rollbackComplete"])
        self.assertTrue(self.source.is_dir())
        self.assertEqual(original_meta, self.meta.read_bytes())
        self.assertEqual(foreign, self.destination.with_name(self.destination.name + ".meta").read_bytes())
        self.assertEqual([str(self.destination.with_name(self.destination.name + ".meta"))], result["foreignWritesPreserved"])
        for name, data in self.old_packages.items():
            self.assertEqual(data, (self.project / "Packages" / name).read_bytes())

    def test_v2_binary_gate_rejects_historical_proofs_and_stale_maps_or_binary_hashes(self):
        for change in ("version", "map", "hash", "missing"):
            with self.subTest(change=change):
                proof = copy.deepcopy(self.binary_proof)
                if change == "version": proof["proofVersion"] = 1
                elif change == "map": proof["products"][0]["guidMapSha256"] = "0" * 64
                elif change == "hash": proof["products"][0]["files"][0]["actualSha256"] = "0" * 64
                else: proof["products"][0]["files"] = []
                self.write(self.binary_path, proof)
                with self.assertRaises(ValueError):
                    m.validate_binary_v2(self.project, self.source, self.manifest_path, self.manifest)
        self.write(self.binary_path, self.binary_proof)
        metadata_changed = copy.deepcopy(self.manifest)
        metadata_changed["products"][0]["files"][1]["sha256"] = "0" * 64
        self.assertEqual(1, m.validate_binary_v2(self.project, self.source, self.manifest_path, metadata_changed)["files"])
        self.unchanged()

    def test_exact_review_supports_provider_limits_but_not_missing_or_compilation(self):
        validation = dict(self.validation, status="completed-with-issues", issues=[{"path": "mesh", "kind": "unsupported-shader", "detail": "retained vendor shader", "count": 1}])
        fallback = dict(self.fallback, status="completed-with-issues", issues=[{"product": 46, "path": "optional", "code": "job-error", "detail": "NotSupportedException: fixture provider limitation"}])
        vb, fb = m.encode(validation), m.encode(fallback)
        with self.assertRaises(ValueError):
            m.validate_reports(validation, vb, fallback, fb, None)
        decisions = [{"report": name, "issueSha256": m.issue_identity(issue), "decision": "accept", "reason": "Reviewed this exact retained source/provider limitation."}
                     for name, report in (("validation", validation), ("fallback", fallback)) for issue in report["issues"]]
        review = {"validationSha256": m.sha(vb), "fallbackSha256": m.sha(fb), "decisions": decisions}
        self.assertEqual(2, len(m.validate_reports(validation, vb, fallback, fb, review)))
        for counter in ("missingMonoScripts", "missingShaders", "missingTextureReferences", "shaderCompileErrors"):
            with self.subTest(counter=counter), self.assertRaises(ValueError):
                m.validate_reports(dict(validation, **{counter: 1}), vb, fallback, fb, review)
        with self.assertRaises(ValueError):
            m.validate_reports(validation, vb + b" ", fallback, fb, review)

    def test_original_binary_proof_accepts_only_hash_bound_explicit_unity_yaml_conversion(self):
        manifest = copy.deepcopy(self.manifest)
        canonical = manifest["products"][0]["files"][0]
        path = self.source / canonical["path"]
        before = path.read_bytes()
        payload = b"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!156 &15600000\nTerrainData: {}\n"
        path.write_bytes(payload)
        canonical.update(sha256=m.sha(payload), bytes=len(payload))
        proof = copy.deepcopy(self.binary_proof)
        item = proof["products"][0]["files"][0]
        item.update(binaryKind="converted-yaml", status="converted-yaml-collided-guids-absent",
                    actualSha256=canonical["sha256"], receiptSha256=canonical["sha256"],
                    fileBytes=canonical["bytes"], receiptBytes=canonical["bytes"])
        self.write(self.binary_path, proof)
        self.assertEqual(1, m.validate_binary_v2(self.project, self.source, self.manifest_path, manifest)["files"])
        for kind, status in (("serialized-file", "collided-guids-absent"), ("converted-yaml", "collided-guids-absent"), ("unknown", "converted-yaml-collided-guids-absent")):
            with self.subTest(kind=kind, status=status):
                item.update(binaryKind=kind, status=status)
                self.write(self.binary_path, proof)
                with self.assertRaises(ValueError):
                    m.validate_binary_v2(self.project, self.source, self.manifest_path, manifest)
        path.write_bytes(before)
        self.write(self.binary_path, self.binary_proof)

    def test_v2_preserves_original_scope_for_independently_verified_source_only_binary(self):
        manifest = copy.deepcopy(self.manifest)
        product = manifest["products"][0]
        original = product["files"].pop(0)
        preserved = self.work / "SourceOnly" / original["path"]
        preserved.parent.mkdir(parents=True)
        (self.source / original["path"]).rename(preserved)
        product["sourceOnlyFiles"] = [dict(original, preservedPath=str(preserved))]
        proof = copy.deepcopy(self.binary_proof)
        row = proof["products"][0]["files"][0]
        descriptor = {"run": "reviewed-fixture-run", "sourceBytes": original["bytes"], "backupSha256": original["sha256"]}
        row.update(actualPath=str(preserved), assetLocation="source-only", sourceOnlyProof=descriptor)
        self.write(self.binary_path, proof)
        key = ("000", original["path"])
        with self.assertRaisesRegex(ValueError, "independently verified"):
            m.validate_binary_v2(self.project, self.source, self.manifest_path, manifest)
        result = m.validate_binary_v2(self.project, self.source, self.manifest_path, manifest, {key: descriptor})
        self.assertEqual((1, 1), (result["files"], result["sourceOnlyFiles"]))
        for field, value in (("assetLocation", "assets"), ("actualPath", str(self.source / original["path"]))):
            current = copy.deepcopy(proof)
            current["products"][0]["files"][0][field] = value
            self.write(self.binary_path, current)
            with self.assertRaises(ValueError):
                m.validate_binary_v2(self.project, self.source, self.manifest_path, manifest, {key: descriptor})
        self.unchanged()

    def test_validation_only_result_uses_preserved_fallback_evidence(self):
        self.result.update(command="validate", fallbackPath=None)
        self.write_result()
        result = m.install(self.project)
        self.assertEqual("ready-dry-run", result["status"], result)
        self.assertTrue(result["fallbackEvidenceReusedByValidationOnlySession"])

    def test_post_repair_validation_requires_fresh_final_session_and_exact_binary_scene_proof(self):
        relative = self.products[0]["folder"] + "/binary.unity"
        path = self.source / relative
        payload = b"\x00\x00fixture serialized scene"
        path.write_bytes(payload)
        manifest = copy.deepcopy(self.manifest)
        manifest["products"][0]["files"].append({"path": relative, "bytes": len(payload), "sha256": m.sha(payload)})
        repair_path = self.work / "repair-fixture/report.json"
        self.write(repair_path, {"run": "fixture-repair", "status": "complete", "errors": [],
                                 "completedUtc": "2026-10-19T00:01:00+00:00"})
        manifest["binaryReferenceRepairHistory"] = [{"run": "fixture-repair", "report": str(repair_path)}]
        validation = dict(self.validation, completedUtc="2026-10-19T00:02:00Z",
                          binarySceneSourcesVerified=1, binaryExplicitMonoBehaviours=2, binaryScriptReferencesResolved=2,
                          binaryScenes=[{"path": m.TARGET + "/" + relative, "status": "pass", "sourceSha256": m.sha(payload),
                                         "sourceBytes": len(payload), "explicitMonoBehaviours": 2,
                                         "resolvedScriptReferences": 2, "unresolvedScriptReferences": 0}])
        result = dict(self.result, completedUtc="2026-10-19T00:03:00Z", command="finalize")
        self.assertEqual(1, m.validate_post_repair(self.project, self.source, manifest, result, validation)["binaryScenes"])
        self.assertEqual(1, m.validate_post_repair(self.project, self.source, manifest, dict(result, command="validate"), validation)["binaryScenes"])
        for change in ("stale", "import-only", "scene-hash", "missing-scene", "unresolved", "totals"):
            with self.subTest(change=change):
                v, r = copy.deepcopy(validation), dict(result)
                if change == "stale": v["completedUtc"] = "2026-10-19T00:00:00Z"
                elif change == "import-only": r["command"] = "import-only"
                elif change == "scene-hash": v["binaryScenes"][0]["sourceSha256"] = "0" * 64
                elif change == "missing-scene": v["binaryScenes"] = []
                elif change == "unresolved": v["binaryScenes"][0]["unresolvedScriptReferences"] = 1
                else: v["binaryExplicitMonoBehaviours"] = 3
                with self.assertRaises(ValueError):
                    m.validate_post_repair(self.project, self.source, manifest, r, v)
        path.unlink()
        self.unchanged()

    def test_source_only_keeps_all84_products_and_requires_preserved_proof_chain(self):
        source_spec = importlib.util.spec_from_file_location("installer_source_only_fixture", Path(__file__).with_name("test-quarantine-unity-source-only-terrain.py"))
        source = importlib.util.module_from_spec(source_spec); source_spec.loader.exec_module(source)
        fixture = source.SourceOnlyFixtures(); fixture.setUp()
        try:
            report, _ = fixture.run_tool(True)
            manifest, _ = m.read_json(fixture.manifest_path)
            validation = {"completedUtc": m.utc()}
            accepted = m.validate_source_only(fixture.project, fixture.stage, manifest, validation)
            self.assertEqual((4, 84), (accepted["files"], accepted["productsPreserved"]))
            for kind in ("product-count", "coverage", "extra-exclusion", "stale-validation"):
                with self.subTest(kind=kind):
                    current, reviewed = copy.deepcopy(manifest), dict(validation)
                    if kind == "product-count": current["products"].pop()
                    elif kind == "coverage": current["products"][-1]["binaryGuidRecoveryProofs"] = [{"path": current["products"][-1]["files"][0]["path"]}]
                    elif kind == "extra-exclusion": current["products"][0]["sourceOnlyFiles"].append(dict(current["products"][0]["sourceOnlyFiles"][0], path="unapproved.asset"))
                    else: reviewed["completedUtc"] = "2020-01-01T00:00:00Z"
                    with self.assertRaises(ValueError):
                        m.validate_source_only(fixture.project, fixture.stage, current, reviewed)
            preserved = Path(report["files"][0]["destination"])
            original = preserved.read_bytes()
            preserved.write_bytes(b"X" * len(original))
            with self.assertRaises(ValueError):
                m.validate_source_only(fixture.project, fixture.stage, manifest, validation)
            preserved.write_bytes(original)
            self.assertEqual(4, m.validate_source_only(fixture.project, fixture.stage, manifest, validation)["files"])
        finally:
            fixture.tearDown()

    def test_two_source_only_transactions_preserve_all84_and_original_binary_scope(self):
        def load(name, filename):
            spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
            value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
        initial_module = load("install_initial_chain_fixture", "test-quarantine-unity-source-only-terrain.py")
        group_module = load("install_group_chain_fixture", "test-quarantine-unity-source-only-group.py")
        initial = initial_module.SourceOnlyFixtures(); initial.setUp()
        group = group_module.GroupFixtures(); group.setUp()
        try:
            # Both actual temporary transactions share one84-product project.
            # Match033's real canonical folder while keeping the group fixture's
            # separate usable assets and original package index evidence.
            folder = initial_module.tool.FOLDER
            def rewrite(value):
                if isinstance(value, str): return value.replace("033-fixture", folder)
                if isinstance(value, dict): return {key: rewrite(item) for key, item in value.items()}
                if isinstance(value, list): return [rewrite(item) for item in value]
                return value
            (group.stage / "033-fixture").rename(group.stage / folder)
            group.products["033"] = rewrite(group.products["033"])
            group.targets, group.terrains, group.evidence, group.graph = (rewrite(value) for value in (group.targets, group.terrains, group.evidence, group.graph))
            group.paths = {rewrite(path) for path in group.paths}
            group.empty, group.prefab, group.scene = (rewrite(path) for path in (group.empty, group.prefab, group.scene))
            template_rows = copy.deepcopy(initial.product["files"])
            template_bytes = {row["path"]: (initial.stage / row["path"]).read_bytes() for row in template_rows}
            initial.project, initial.work, initial.headless, initial.stage = group.project, group.work, group.headless, group.stage
            initial.product = group.products["033"]; initial.products = list(group.products.values())
            initial.archive = Path(initial.product["inputs"][0]["path"])
            initial.main = group.main
            initial.manifest = dict(group.manifest, products=initial.products)
            initial.manifest_path = group.manifest_path
            initial.runtime_path = group.headless / "Library/YamyamAssetLibrary/initial-proof/report.json"
            initial.runtime_path.parent.mkdir(parents=True)
            initial.missing_path = group.work / "initial-missing-evidence.json"
            initial.missing.update(package=str(initial.archive), packageBytes=initial.archive.stat().st_size)
            for row in template_rows:
                raw = template_bytes[row["path"]]
                initial.add(row["path"], raw, row.get("guid"))
            initial.finish(); initial_report, _ = initial.run_tool(True)
            group.manifest = json.loads(group.manifest_path.read_bytes())
            group.products = {product["id"]: product for product in group.manifest["products"]}
            group.finish(); group_report, group_report_path = group.run_tool(True)
            manifest, _ = m.read_json(group.manifest_path)
            validation = {"completedUtc": m.utc()}
            accepted = m.validate_source_only(group.project, group.stage, manifest, validation)
            self.assertEqual((32, 84, 2), (accepted["files"], accepted["productsPreserved"], len(accepted["runs"])))
            self.assertEqual(32, len(accepted["verifiedFiles"]))
            self.assertEqual(4, len(initial_report["files"]))
            self.assertEqual(28, len(group_report["files"]))
            preserved = {(row["productId"], row["path"]): row["proof"] for row in accepted["verifiedFiles"]}
            p84 = next(product for product in manifest["products"] if product["id"] == "084")
            binary_path = p84["binaryGuidRecoveryProofs"][0]["path"]
            canonical = next(row for row in p84["sourceOnlyFiles"] if row["path"] == binary_path)
            map_sha = m.sha(b"{}")
            proof = {"proofVersion": 2, "status": "pass", "errors": [], "productsChecked": 1, "filesChecked": 1,
                     "filesWithCollisionSpellings": 0, "exactCanonicalExternalReferenceHits": 0, "staleReceiptFiles": 0,
                     "sourceManifestContext": {"path": str(group.manifest_path), "stageRoot": str(group.stage), "targetAssetRoot": m.TARGET, "products": 84},
                     "products": [{"id": "084", "guidMapSha256": map_sha, "originalProofFiles": 1, "files": [{
                         "productId": "084", "path": binary_path, "actualPath": canonical["preservedPath"], "assetLocation": "source-only",
                         "sourceOnlyProof": preserved[("084", binary_path)], "proofVersion": 2, "guidMapSha256": map_sha,
                         "binaryKind": "serialized-file", "status": "collided-guids-absent", "receiptMatches": True,
                         "actualSha256": canonical["sha256"], "receiptSha256": canonical["sha256"], "fileBytes": canonical["bytes"], "receiptBytes": canonical["bytes"],
                         "exactCanonicalExternalHits": [], "collidingReferences": []}]}]}
            self.write(group.work / "binary-guid-encoding-recheck.json", proof)
            checked = m.validate_binary_v2(group.project, group.stage, group.manifest_path, manifest, preserved)
            self.assertEqual((1, 1), (checked["files"], checked["sourceOnlyFiles"]))
            for change in ("coverage", "product", "history", "extra", "stale-validation"):
                with self.subTest(change=change):
                    current, reviewed = copy.deepcopy(manifest), dict(validation)
                    if change == "coverage": next(product for product in current["products"] if product["id"] == "084")["binaryGuidRecoveryProofs"] = []
                    elif change == "product": current["products"].pop()
                    elif change == "history": current["sourceOnlyHistory"].reverse()
                    elif change == "extra": current["products"][0]["files"].pop()
                    else: reviewed["completedUtc"] = "2020-01-01T00:00:00Z"
                    with self.assertRaises(ValueError): m.validate_source_only(group.project, group.stage, current, reviewed)
            preserved_path = Path(group_report["files"][0]["destination"])
            original = preserved_path.read_bytes(); preserved_path.write_bytes(b"X" * len(original))
            with self.assertRaises(ValueError): m.validate_source_only(group.project, group.stage, manifest, validation)
            preserved_path.write_bytes(original)
            report_raw = group_report_path.read_bytes()
            changed = copy.deepcopy(group_report); changed["sourceRuntimeProofSha256"] = "0" * 64
            group_report_path.write_bytes(m.encode(changed))
            with self.assertRaises(ValueError): m.validate_source_only(group.project, group.stage, manifest, validation)
            group_report_path.write_bytes(report_raw)
            self.assertEqual(32, m.validate_source_only(group.project, group.stage, manifest, validation)["files"])
        finally:
            group.tearDown(); initial.tearDown()

    def test_rename_retry_is_bounded_to_five_windows_sharing_attempts(self):
        error = OSError(13, "fixture sharing violation"); error.winerror = 5
        with mock.patch.object(m.os, "rename", side_effect=[error, error, None]) as rename, mock.patch.object(m.time, "sleep"):
            m.rename_retry(self.base / "start", self.base / "absent")
            self.assertEqual(3, rename.call_count)
        with mock.patch.object(m.os, "rename", side_effect=error) as rename, mock.patch.object(m.time, "sleep"):
            with self.assertRaises(OSError):
                m.rename_retry(self.base / "start", self.base / "absent")
            self.assertEqual(5, rename.call_count)

    def test_reparse_point_is_rejected_without_following_it(self):
        asset = self.source / "000-fixture/asset.txt"
        inode = asset.lstat().st_ino
        actual = m.is_link
        with mock.patch.object(m, "is_link", side_effect=lambda info: info.st_ino == inode or actual(info)):
            result = m.install(self.project, apply=True)
        self.assertEqual("failed", result["status"])
        self.assertIn("reparse", result["error"])
        self.unchanged()


if __name__ == "__main__":
    unittest.main()
