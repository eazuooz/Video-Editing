"""Small archive/security fixtures; no real asset library or project is touched."""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest import mock
import zipfile

spec = importlib.util.spec_from_file_location("asset_import", Path(__file__).with_name("import-unity-asset-library.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ImportFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="yamyam-asset-fixture-")
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def package(self, binary=False):
        package = self.base / "fixture.unitypackage"
        guid = "a" * 32
        with tarfile.open(package, "w:gz") as archive:
            values = {
                f"{guid}/pathname": b"Assets/Vendor/Cube.prefab",
                f"{guid}/asset.meta": f"fileFormatVersion: 2\nguid: {guid}\n".encode(),
                f"{guid}/asset": b"\0binaryUnitySerialization" if binary else f"%YAML 1.1\n--- !u!1 &1\nGameObject:\n  m_Ref: {{guid: {guid}}}\n".encode(),
                f"{'b' * 32}/pathname": b"ProjectSettings/GraphicsSettings.asset",
                f"{'b' * 32}/asset.meta": f"fileFormatVersion: 2\nguid: {'b' * 32}\n".encode(),
                f"{'b' * 32}/asset": b"not installed",
            }
            for name, content in values.items():
                info = tarfile.TarInfo(name)
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))
        return package

    def product(self, package):
        return {"index": 1, "id": "001", "title": "Fixture Pack", "sourceDirectory": str(self.base),
                "sourceUrl": "https://example.invalid/fixture", "selectedSources": [
                    {"kind": "unitypackage", "path": str(package)}]}

    def collision_package(self, filename, paths, reverse=False):
        package = self.base / filename
        entries = []
        for index, (guid, path) in enumerate(zip(("a" * 32, "c" * 32), paths)):
            entries.extend([
                (f"{guid}/pathname", path.encode()),
                (f"{guid}/asset", b"identical texture bytes"),
                (f"{guid}/asset.meta", f"fileFormatVersion: 2\nguid: {guid}\nTextureImporter:\n  testSetting: {index}\n".encode()),
            ])
        guid = "d" * 32
        entries.extend([
            (f"{guid}/pathname", b"Assets/Vendor/References.asset"),
            (f"{guid}/asset", f"%YAML 1.1\n--- !u!1 &1\nrefs: [{{guid: {'a' * 32}}}, {{guid: {'c' * 32}}}]\n".encode()),
            (f"{guid}/asset.meta", f"fileFormatVersion: 2\nguid: {guid}\n".encode()),
        ])
        with tarfile.open(package, "w:gz") as archive:
            for name, content in reversed(entries) if reverse else entries:
                info = tarfile.TarInfo(name)
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))
        return package

    def test_guid_remapping_rewrites_text_and_keeps_meta(self):
        product = self.product(self.package())
        tree, result = module.build_product(product, self.base / "work", {"a" * 32: {"owner": "existing"}})
        self.assertEqual(1, len(result["guidRemaps"]))
        self.assertFalse(result["binaryGuidCollisionBlockers"])
        replacement = result["guidRemaps"]["a" * 32]
        prefab = tree / result["folder"] / "Vendor/Cube.prefab"
        self.assertIn(replacement, prefab.read_text())
        self.assertIn(replacement, prefab.with_name("Cube.prefab.meta").read_text())
        self.assertFalse((tree / result["folder"] / "ProjectSettings").exists())
        self.assertEqual(1, len(result["excluded"]))

    def test_binary_serialization_collision_is_blocked(self):
        product = self.product(self.package(binary=True))
        tree, result = module.build_product(product, self.base / "work", {"a" * 32: {"owner": "existing"}})
        self.assertEqual(1, len(result["binaryGuidCollisionBlockers"]))
        self.assertIn(b"\0binary", (tree / result["folder"] / "Vendor/Cube.prefab").read_bytes())

    def test_generated_raster_meta_declares_2d_without_replacing_vendor_cube_settings(self):
        writer = module.PackWriter("fixture", self.base / "raster-tree")
        names = ["Palette.PNG", "Surface.jpg", "Normal.tga", "Layers.tiff", "Image.bmp", "Art.psd", "Anim.gif", "Environment.hdr", "Cube.dds", "Mesh.fbx"]
        before = {}
        for name in names:
            source = self.base / name
            source.write_bytes(("fixture-only source bytes " + name).encode())
            before[source] = source.read_bytes()
            writer.put(name, source, {"kind": "archive-files"})
        vendor = self.base / "vendor-cube.png"
        vendor.write_bytes(b"provider environment image fixture")
        vendor_meta = self.base / "vendor-cube.png.meta"
        original_meta = b"fileFormatVersion: 2\nguid: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nTextureImporter:\n  serializedVersion: 13\n  textureShape: 2\n  textureType: 0\n"
        vendor_meta.write_bytes(original_meta)
        writer.put(vendor.name, vendor, {"kind": "archive-files"})
        writer.put(vendor_meta.name, vendor_meta, {"kind": "vendor-meta"})
        module.ensure_metadata(writer, "001")
        for name in names:
            meta = (writer.tree / writer.folder / (name + ".meta")).read_text()
            self.assertIn("guid: " + module.stable_guid("001", writer.folder + "/" + name), meta)
            if Path(name).suffix.lower() in module.RAW_RASTER_2D:
                self.assertIn("TextureImporter:\n", meta)
                self.assertIn("  serializedVersion: 13\n", meta)
                self.assertIn("  textureShape: 1\n", meta)
            else:
                self.assertNotIn("TextureImporter:", meta)
        self.assertEqual(original_meta, (writer.tree / writer.folder / vendor_meta.name).read_bytes())
        self.assertEqual("vendor-meta", writer.files[writer.folder + "/" + vendor_meta.name]["source"]["kind"])
        for source, raw in before.items(): self.assertEqual(raw, source.read_bytes())
        self.assertEqual(original_meta, vendor_meta.read_bytes())

    def test_archive_traversal_and_symlink_rejected(self):
        archive = self.base / "bad.zip"
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("../escaped.txt", "bad")
            link = zipfile.ZipInfo("link")
            link.create_system = 3
            link.external_attr = 0o120777 << 16
            output.writestr(link, "../escaped.txt")
        for name in ("../escaped.txt", "link"):
            with self.assertRaises(ValueError):
                module.extract_archive_members(archive, [name], self.base / "extracted")

    def test_no_case_insensitive_overwrite(self):
        writer = module.PackWriter("fixture", self.base / "tree")
        one, two = self.base / "one", self.base / "two"
        one.write_bytes(b"one")
        two.write_bytes(b"two")
        writer.put("Cube.txt", one, {})
        with self.assertRaises(ValueError):
            writer.put("cube.txt", two, {})
        self.assertEqual(b"one", (self.base / "tree/fixture/Cube.txt").read_bytes())

    def test_streamed_owned_move_matches_copy_receipt_and_preserves_archive(self):
        package = self.package()
        archive_bytes = package.read_bytes()
        work = self.base / "owned-work"
        groups = module.unpack_unitypackage(package, work / "unpacked")
        group = groups["a" * 32]
        # Routing names are retained in memory; they are not written to disk.
        self.assertEqual("Assets/Vendor/Cube.prefab", group["originalPath"])
        self.assertNotIn("path", group["pathname"])
        self.assertFalse(list((work / "unpacked").rglob("pathname")))
        origin = {"kind": "fixture", "package": str(package)}
        copied = module.PackWriter("fixture", self.base / "copied-tree")
        moved = module.PackWriter("fixture", work / "tree", owned_root=work)
        for kind, destination in (("asset", "Cube.prefab"), ("asset.meta", "Cube.prefab.meta")):
            payload = group[kind]
            copied.put(destination, payload["path"], origin)
            self.assertTrue(payload["path"].exists())  # public/default put copies
            with mock.patch.object(module, "sha_file", side_effect=AssertionError("streamed hash reread")), \
                    mock.patch.object(module.shutil, "copyfile", side_effect=AssertionError("owned payload recopied")):
                moved.put(destination, payload["path"], origin, owned_move=True,
                          known_digest=payload["sha256"], known_bytes=payload["bytes"])
            self.assertFalse(payload["path"].exists())
            self.assertEqual((copied.tree / "fixture" / destination).read_bytes(),
                             (moved.tree / "fixture" / destination).read_bytes())
        self.assertEqual(copied.files, moved.files)
        self.assertEqual(archive_bytes, package.read_bytes())

    def test_owned_move_rejects_outside_root_stale_sizes_and_destinations(self):
        work = self.base / "owned-work"
        work.mkdir()
        writer = module.PackWriter("fixture", work / "tree", owned_root=work)
        outside = self.base / "original.unitypackage"
        outside.write_bytes(b"original stays intact")
        digest = module.sha_file(outside)
        with self.assertRaises(ValueError):
            writer.put("original", outside, {}, owned_move=True,
                       known_digest=digest, known_bytes=outside.stat().st_size)
        self.assertEqual(b"original stays intact", outside.read_bytes())
        raw = work / "raw"
        raw.write_bytes(b"payload")
        with self.assertRaises(ValueError):
            writer.put("asset", raw, {}, owned_move=True,
                       known_digest=module.sha_file(raw), known_bytes=99)
        for relative in ("../escaped", "nested/../../escaped"):
            with self.assertRaises(ValueError):
                writer.put(relative, raw, {}, owned_move=True)
        self.assertEqual(b"payload", raw.read_bytes())

    def test_native_path_collisions_keep_both_guids_and_importers_deterministically(self):
        for case, names in enumerate([
            ("Assets/Vendor/Noise_Big.tga", "Assets/Vendor/Noise_Big.tga"),
            ("Assets/Vendor/Noise_Big.tga", "Assets/Vendor/noise_big.TGA"),
        ]):
            with self.subTest(paths=names):
                payloads = []
                for reverse in (False, True):
                    package = self.collision_package(f"collision-{case}-{reverse}.unitypackage", names, reverse)
                    original = package.read_bytes()
                    tree, result = module.build_product(self.product(package), self.base / f"work-{case}-{reverse}", {})
                    self.assertEqual({}, result["guidRemaps"])
                    self.assertEqual(2, len(result["pathChanges"]))
                    for index, guid in enumerate(("a" * 32, "c" * 32)):
                        change = next(c for c in result["pathChanges"] if c.get("guid") == guid)
                        self.assertEqual(names[index], change["original"])
                        self.assertIn("__guid_" + guid, change["destination"])
                        asset = tree / result["folder"] / change["destination"]
                        meta = asset.with_name(asset.name + ".meta")
                        self.assertEqual(b"identical texture bytes", asset.read_bytes())
                        self.assertIn("guid: " + guid, meta.read_text())
                        self.assertIn("testSetting: " + str(index), meta.read_text())
                    references = (tree / result["folder"] / "Vendor/References.asset").read_text()
                    self.assertIn("a" * 32, references)
                    self.assertIn("c" * 32, references)
                    self.assertEqual(original, package.read_bytes())
                    payloads.append({r["path"]: (r["bytes"], r["sha256"]) for r in result["files"]})
                self.assertEqual(payloads[0], payloads[1])

    def project(self):
        project = self.base / "Unity"
        (project / "Assets").mkdir(parents=True)
        (project / "ProjectSettings").mkdir()
        (project / "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.6.0f1")
        return project

    def test_staging_and_resume_never_touch_assets(self):
        project = self.project()
        plan = self.base / "plan.json"
        plan.write_text(json.dumps({"sets": [self.product(self.package())]}))
        arguments = ["--plan", str(plan), "--project", str(project)]
        source_bytes = (self.base / "fixture.unitypackage").read_bytes()
        self.assertEqual(0, module.main(arguments))
        with mock.patch.object(module, "build_product", side_effect=AssertionError("completed product re-extracted")):
            self.assertEqual(0, module.main(arguments))
        self.assertEqual([], list((project / "Assets").iterdir()))
        manifest = json.loads((project / "Library/YamyamAssetLibrary/staging-manifest.json").read_text())
        self.assertEqual("complete", manifest["products"][0]["status"])
        self.assertTrue(manifest["products"][0]["assetPath"].startswith(module.TARGET_ROOT))
        self.assertEqual(source_bytes, (self.base / "fixture.unitypackage").read_bytes())

    def test_blocked_resume_keeps_evidence_without_reextract_or_guid_registration(self):
        project = self.project()
        existing = project / "Assets/Existing.prefab.meta"
        existing.write_text("fileFormatVersion: 2\nguid: " + "a" * 32 + "\n")
        package = self.package(binary=True)
        archive_bytes, existing_bytes = package.read_bytes(), existing.read_bytes()
        product = self.product(package)
        plan = self.base / "plan.json"
        plan.write_text(json.dumps({"sets": [product]}))
        arguments = ["--plan", str(plan), "--project", str(project)]
        self.assertEqual(1, module.main(arguments))
        base = project / "Library/YamyamAssetLibrary"
        receipt_path = base / "receipts/001.json"
        previous_bytes = receipt_path.read_bytes()
        previous = json.loads(previous_bytes)
        self.assertEqual("blocked-binary-guid-collision", previous["status"])
        signature = module.source_signature(product)[0]
        self.assertTrue(module.resume_blocked_valid(previous, signature, base / "work"))
        self.assertTrue(previous["guidRemaps"])
        self.assertTrue(previous["guidCollisions"])
        owners = module.guid_registry(project / "Assets")
        with mock.patch.object(module, "build_product", side_effect=AssertionError("blocked product re-extracted")), \
                mock.patch.object(module, "unpack_unitypackage", side_effect=AssertionError("blocked archive decoded")), \
                mock.patch.object(module, "guid_registry", return_value=owners):
            self.assertEqual(1, module.main(arguments))
        self.assertEqual({"a" * 32}, set(owners))
        self.assertEqual(previous_bytes, receipt_path.read_bytes())
        manifest = json.loads((base / "staging-manifest.json").read_text())
        self.assertEqual([previous], manifest["products"])
        self.assertEqual(1, manifest["summary"]["blockedOrFailed"])
        self.assertEqual(archive_bytes, package.read_bytes())
        self.assertEqual(existing_bytes, existing.read_bytes())
        self.assertTrue(Path(previous["workDirectory"]).is_dir())
        self.assertFalse(module.resume_blocked_valid(previous, "different signature", base / "work"))
        escaped = dict(previous, workDirectory=str(self.base))
        self.assertFalse(module.resume_blocked_valid(escaped, signature, base / "work"))
        tree = Path(previous["workDirectory"]) / "tree"
        record = previous["files"][0]
        (tree / record["path"]).write_bytes(b"changed file size")
        self.assertFalse(module.resume_blocked_valid(previous, signature, base / "work"))

    def test_only_retry_keeps_all_other_terminal_receipts_and_reserves_complete_only(self):
        project = self.project()
        package = self.package()
        plan = self.base / "plan.json"
        plan.write_text(json.dumps({"sets": [self.product(package)]}))
        base = project / "Library/YamyamAssetLibrary"
        receipts = base / "receipts"
        receipts.mkdir(parents=True)
        others = {}
        for identifier, status, guid in [
            ("002", "complete", "e" * 32),
            ("003", "blocked-binary-guid-collision", "a" * 32),
            ("004", "failed", "a" * 32),
        ]:
            receipt = {"id": identifier, "index": int(identifier), "folder": identifier + "-other",
                       "status": status, "workDirectory": "preserved-other-work",
                       "guidCollisions": [{"oldGuid": guid, "evidence": "preserve verbatim"}],
                       "files": [{"path": identifier + "-other.meta", "guid": guid, "bytes": 0}]}
            module.save_json(receipts / (identifier + ".json"), receipt)
            others[identifier] = receipt
        original_build = module.build_product
        def checked_build(product, work, owners):
            self.assertEqual({"e" * 32}, set(owners))
            return original_build(product, work, owners)
        with mock.patch.object(module, "build_product", side_effect=checked_build):
            self.assertEqual(0, module.main(["--plan", str(plan), "--project", str(project), "--only", "001"]))
        manifest = module.read_json(base / "staging-manifest.json")
        by_id = {r["id"]: r for r in manifest["products"]}
        self.assertEqual({"001", "002", "003", "004"}, set(by_id))
        for identifier, receipt in others.items():
            self.assertEqual(receipt, by_id[identifier])
            self.assertEqual(receipt, module.read_json(receipts / (identifier + ".json")))
        self.assertEqual({}, by_id["001"]["guidRemaps"])


if __name__ == "__main__":
    unittest.main()
