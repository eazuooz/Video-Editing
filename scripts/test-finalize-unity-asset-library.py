"""Fixtures for staged reference repair; no real assets or Editor are touched."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("finalize_asset_library", Path(__file__).with_name("finalize-unity-asset-library.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def serialized_fixture(version=22, externals=(), endian="<", type_tree=True, extra_metadata=b"", payload=b"native-object-payload"):
    """Construct table-format fixtures without executing/deserializing objects."""
    metadata = bytearray(b"6000.0.36f1\0")
    pack = lambda format, *values: struct.pack(endian + format, *values)
    metadata.extend(pack("iBi", 19, int(type_tree), 1))
    metadata.extend(pack("iBh", 1120, 0, -1) + bytes(16))
    if type_tree:
        nodes = bytearray(pack("ii", 1, 4))
        nodes.extend(pack("hBBIIiii", 1, 0, 0, 0, 0, -1, 0, 0))
        if version >= 19:
            nodes.extend(bytes(8))
        nodes.extend(b"Foo\0")
        if version == 23:
            info = b"mhtt" + pack("i", version) + nodes
            metadata.extend(bytes(16) + pack("I", len(info)) + info)
        else:
            metadata.extend(nodes)
        if version >= 21:
            metadata.extend(pack("i", 0))
    metadata.extend(pack("i", 1))
    metadata.extend(bytes((-len(metadata)) % 4))
    metadata.extend(pack("q", 1))
    metadata.extend(pack("q" if version >= 22 else "I", 0))
    metadata.extend(pack("Ii", len(payload), 0))
    metadata.extend(pack("ii", 0, len(externals)))
    for guid in externals:
        metadata.extend(b"\0" + bytes.fromhex(guid) + pack("i", 2) + b"Assets/External.asset\0")
    if version >= 20:
        metadata.extend(pack("i", 0))
    metadata.extend(b"\0" + extra_metadata)
    header_size = 48 if version >= 22 else 20
    data_offset = (header_size + len(metadata) + 15) // 16 * 16
    file_size = data_offset + len(payload)
    flags = bytes([int(endian == ">"), 0, 0, 0])
    if version >= 22:
        header = struct.pack(">4I", 0, 0, version, 0) + flags + struct.pack(">Iqqq", len(metadata), file_size, data_offset, 0)
    else:
        header = struct.pack(">4I", len(metadata), file_size, version, data_offset) + flags
    return header + metadata + bytes(data_offset - header_size - len(metadata)) + payload


class FinalizeFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="yamyam-finalizer-fixture-")
        self.project = Path(self.temp.name) / "Unity"
        (self.project / "Assets").mkdir(parents=True)
        (self.project / "Assets/preserved.txt").write_bytes(b"existing asset preserved")
        (self.project / "ProjectSettings").mkdir()
        (self.project / "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.6.0f1")
        self.work = self.project / "Library/YamyamAssetLibrary"
        self.stage = self.work / "staging/CreatorBundle"
        self.pack = self.stage / "001-fixture"
        self.pack.mkdir(parents=True)
        (self.work / "receipts").mkdir()
        self.source = Path(self.temp.name) / "original.unitypackage"
        self.source.write_bytes(b"original archive remains untouched")
        self.original_sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.product = {"id": "001", "status": "complete", "guidRemaps": {"a" * 32: "b" * 32},
                        "files": [], "scripts": []}

    def tearDown(self):
        self.temp.cleanup()

    def add(self, local, contents, original=None):
        if isinstance(contents, str):
            contents = contents.encode("utf-8")
        target = self.pack / local
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(contents)
        record = {"path": "001-fixture/" + local, "bytes": len(contents),
                  "sha256": hashlib.sha256(contents).hexdigest()}
        if original:
            record["source"] = {"kind": "unitypackage", "package": str(self.source), "originalPath": original}
        self.product["files"].append(record)
        return target

    def finish(self):
        manifest = {"stageRoot": str(self.stage), "targetAssetRoot": "Assets/ThirdParty/YamyamAssetLibrary", "products": [self.product]}
        (self.work / "staging-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (self.work / "receipts/001.json").write_text(json.dumps(self.product), encoding="utf-8")
        return module.finalize(self.project)

    def test_verified_shader_csharp_json_and_yaml_paths(self):
        new = "Assets/ThirdParty/YamyamAssetLibrary/001-fixture/Vendor/Common.hlsl"
        self.add("Vendor/Common.hlsl", "// common\n", "Assets/Vendor/Common.hlsl")
        shader = self.add("Vendor/Test.shader", '#include "Assets/Vendor/Common.hlsl"\n#include_with_pragmas <Assets/Vendor/Common.hlsl>\n', "Assets/Vendor/Test.shader")
        script = self.add("Vendor/Editor/Loader.cs", 'const string Root = "Assets/Vendor";\nconst string File = @"Assets\\Vendor\\Common.hlsl";\nconst string Global = "Assets";\n', "Assets/Vendor/Editor/Loader.cs")
        graph = self.add("Vendor/Test.shadergraph", '{"path":"Assets\\/Vendor\\/Common.hlsl"}', "Assets/Vendor/Test.shadergraph")
        yaml = self.add("Vendor/Layer.terrainlayer", "%YAML 1.1\n--- !u!195 &1\nref: " + "a" * 32 + "\nm_Path: Assets/Vendor/Common.hlsl\n", "Assets/Vendor/Layer.terrainlayer")
        report, _ = self.finish()
        self.assertEqual([], report["errors"])
        self.assertEqual(4, len(report["changedFiles"]))
        self.assertEqual(5, len(report["assetPathChanges"]))  # repeated same literal per file is deduplicated
        for path in (shader, script, graph, yaml):
            self.assertIn(new, path.read_text())
        self.assertEqual(2, shader.read_text().count(new))
        self.assertIn('Global = "Assets"', script.read_text())
        self.assertIn("b" * 32, yaml.read_text())
        receipt = json.loads((self.work / "receipts/001.json").read_text())
        for record in receipt["files"]:
            self.assertEqual(record["sha256"], hashlib.sha256((self.stage / record["path"]).read_bytes()).hexdigest())
        second, _ = module.finalize(self.project)
        self.assertEqual([], second["changedFiles"])
        self.assertEqual([], second["assetPathChanges"])
        self.assertEqual(b"existing asset preserved", (self.project / "Assets/preserved.txt").read_bytes())
        self.assertEqual(self.original_sha, hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_external_missing_and_generated_paths_are_not_guessed(self):
        self.add("Vendor/Common.hlsl", "// common\n", "Assets/Vendor/Common.hlsl")
        source = '#include "Assets/Other/Unknown.hlsl"\nstring future = "Assets/Vendor/NotCreated.asset";\nstring root = "Assets/";\n'
        path = self.add("Vendor/Loader.cs", source, "Assets/Vendor/Loader.cs")
        report, _ = self.finish()
        self.assertEqual(source, path.read_text())
        self.assertEqual([], report["changedFiles"])
        self.assertEqual(2, len(report["unresolvedAssetPaths"]))
        self.assertEqual("needs-review", report["status"])

    def test_binary_unmodified_and_unknown_yaml_extension_guid_repaired(self):
        binary = self.add("Vendor/Binary.spriteatlas", b"\0binary" + b"a" * 32, "Assets/Vendor/Binary.spriteatlas")
        custom = self.add("Vendor/custom.futureformat", "%YAML 1.1\n--- !u!114 &1\nref: " + "a" * 32, "Assets/Vendor/custom.futureformat")
        report, _ = self.finish()
        self.assertEqual(1, len(report["binaryReview"]))
        self.assertEqual(b"\0binary" + b"a" * 32, binary.read_bytes())
        self.assertIn("b" * 32, custom.read_text())

    def test_same_size_unreceipted_edit_is_preserved(self):
        self.add("Vendor/Common.hlsl", "// common\n", "Assets/Vendor/Common.hlsl")
        path = self.add("Vendor/Test.shader", '#include "Assets/Vendor/Common.hlsl"\n// one\n', "Assets/Vendor/Test.shader")
        path.write_bytes(path.read_bytes().replace(b"one", b"two"))
        edited = path.read_bytes()
        report, _ = self.finish()
        self.assertEqual(1, len(report["errors"]))
        self.assertEqual(edited, path.read_bytes())
        self.assertEqual([], report["assetPathChanges"])

    def test_auto_editor_code_inventory(self):
        self.add("Vendor/Editor/Auto.cs", "using UnityEditor;\nnamespace Fixture {\n[InitializeOnLoad]\nclass Auto { void Call() { UnityEngine.Application.OpenURL(\"https://example.invalid\"); } }\n}\n", "Assets/Vendor/Editor/Auto.cs")
        report, code = self.finish()
        self.assertEqual([], report["errors"])
        self.assertEqual(1, code["summary"]["automaticEditorExecutionScripts"])
        self.assertEqual({"InitializeOnLoad", "Application.OpenURL"}, {m["marker"] for m in code["scripts"][0]["markers"]})

    def test_existing_roslyn_and_package_metadata_inventory_is_reused(self):
        inventory = {"method": "fixture Roslyn+PE metadata", "scripts": [{"path": "Assets/Readme.cs",
            "declarations": [{"metadataFullName": "Readme"}]}], "packageAssemblies": [
            {"assembly": "Unity.TextMeshPro", "types": ["TMPro.TextMeshPro"]}]}
        (self.work / "existing-code-inventory.json").write_text(json.dumps(inventory))
        self.add("Vendor/Readme.cs", "public class Readme {}\n", "Assets/Vendor/Readme.cs")
        self.add("Vendor/TextMeshPro.cs", "namespace TMPro {\npublic class TextMeshPro {}\n}\n", "Assets/Vendor/TextMeshPro.cs")
        report, code = self.finish()
        self.assertEqual([], report["errors"])
        self.assertEqual("Readme", code["duplicateTypeCandidates"][0]["type"])
        self.assertEqual("TMPro.TextMeshPro", code["packageTypeCollisionCandidates"][0]["type"])

    def test_versioned_binary_tables_bounds_and_endian(self):
        path = self.pack / "binary.asset"
        for version in (17, 18, 19, 20, 21, 22, 23):
            for endian in ("<", ">"):
                for tree in (False, True):
                    path.write_bytes(serialized_fixture(version, ["d" * 32], endian, tree))
                    table = module.parse_binary_externals(path)
                    self.assertEqual(version, table["formatVersion"])
                    self.assertEqual(endian, table["endian"])
                    self.assertEqual("d" * 32, table["externals"][0]["rawGuidHex"])
                    self.assertEqual(table["metadataBytes"], table["metadataBytesConsumed"])
        for invalid in (serialized_fixture()[:-1], serialized_fixture(extra_metadata=b"not-consumed"),
                        serialized_fixture()[:8] + struct.pack(">I", 24) + serialized_fixture()[12:]):
            path.write_bytes(invalid)
            with self.assertRaises(ValueError):
                module.parse_binary_externals(path)
        version23 = serialized_fixture(23)
        magic = version23.index(b"mhtt")
        declared = struct.unpack("<I", version23[magic - 4:magic])[0]
        for invalid in (version23[:magic + 4] + struct.pack("<i", 22) + version23[magic + 8:],
                        version23[:magic - 4] + struct.pack("<I", declared + 4) + version23[magic:]):
            path.write_bytes(invalid)
            with self.assertRaises(ValueError):
                module.parse_binary_externals(path)

    def test_actual_unity_guid_nibble_encoding_is_detected_in_external_tables(self):
        # Distinct nibbles matter: repeated 'aaaa' fixture GUIDs cannot catch an
        # omitted Unity binary encoding. These pairs are independently observed
        # exact scene bytes and matching MonoScript .meta GUIDs.
        pairs = (("71525106e226bf47b6d575b3835aef85", "172515602e62fb746b5d573b38a5fe58"),
                 ("0c74c4c8e650a94288a26f137c967be1", "c0474c8c6e059a24882af631c769b71e"))
        path = self.pack / "binary.asset"
        for raw_hex, canonical in pairs:
            self.assertEqual(canonical, module.unity_guid_from_bytes(bytes.fromhex(raw_hex)))
            self.assertEqual(bytes.fromhex(raw_hex), module.guid_byte_forms(canonical)["unity-byte-nibbles"])
            for version in (17, 22, 23):
                for endian in ("<", ">"):
                    data = serialized_fixture(version, [raw_hex], endian)
                    path.write_bytes(data)
                    proof = module.binary_absence_proof(path, {canonical: "f" * 32}, hashlib.sha256(data).hexdigest())
                    self.assertEqual(module.BINARY_GUID_PROOF_VERSION, proof["proofVersion"])
                    self.assertFalse(proof["collidedGuidsAbsent"])
                    external = [hit for hit in proof["collidingReferences"] if hit["where"] == "external-table"]
                    self.assertTrue(external)
                    self.assertEqual("unity-byte-nibbles", external[0]["representation"])
                    self.assertEqual(canonical, external[0]["canonicalGuid"])
                    offset = external[0]["guidOffset"]
                    self.assertEqual(raw_hex, data[offset:offset + 16].hex())
                    self.assertEqual(data, path.read_bytes())

    def test_unity_encoded_guid_in_payload_across_chunk_boundary_is_detected(self):
        canonical = "172515602e62fb746b5d573b38a5fe58"
        encoded = bytes.fromhex("71525106e226bf47b6d575b3835aef85")
        empty = serialized_fixture(payload=b"")
        padding = 2 * 1024 * 1024 - len(empty) - 8
        data = serialized_fixture(payload=b"x" * padding + encoded + b"tail")
        path = self.pack / "binary.asset"
        path.write_bytes(data)
        proof = module.binary_absence_proof(path, {canonical: "f" * 32}, hashlib.sha256(data).hexdigest())
        self.assertFalse(proof["collidedGuidsAbsent"])
        self.assertTrue(any(hit["representation"] == "unity-byte-nibbles" and hit["where"] == "whole-binary-byte-scan"
                            for hit in proof["collidingReferences"]))
        self.assertEqual(data, path.read_bytes())

    def prepare_blocked(self, binary_guid="d" * 32):
        (self.project / "Assets/Scenes").mkdir()
        (self.project / "Assets/Scenes.meta").write_text("fileFormatVersion: 2\nguid: " + "a" * 32 + "\nfolderAsset: yes\n")
        self.add("Scenes/Scenes.meta", "fileFormatVersion: 2\nguid: " + "a" * 32 + "\nfolderAsset: yes\n")
        self.add("Scenes/Example.unity", "%YAML 1.1\n--- !u!1 &1\nref: " + "a" * 32)
        self.add("Scenes/Example.unity.meta", "fileFormatVersion: 2\nguid: " + "f" * 32 + "\n")
        binary = self.add("Scenes/LightingData.asset", serialized_fixture(externals=[binary_guid]))
        self.add("Scenes/LightingData.asset.meta", "fileFormatVersion: 2\nguid: " + "e" * 32 + "\n")
        source_work = self.work / "work/001-owned"
        tree = source_work / "tree"
        tree.mkdir(parents=True)
        self.pack.rename(tree / "001-fixture")
        root_content = ("fileFormatVersion: 2\nguid: " + "c" * 32 + "\nfolderAsset: yes\n").encode()
        (tree / "001-fixture.meta").write_bytes(root_content)
        self.product["files"].append({"path": "001-fixture.meta", "bytes": len(root_content),
            "sha256": hashlib.sha256(root_content).hexdigest(), "guid": "c" * 32})
        for record in self.product["files"]:
            if record["path"].endswith(".meta"):
                record["guid"] = module.meta_guid(tree / record["path"])
        self.product.update(status="blocked-binary-guid-collision", folder="001-fixture", workDirectory=str(source_work),
            binaryGuidCollisionBlockers=["001-fixture/Scenes/LightingData.asset"])
        plan = self.work / "fixture-plan.json"
        plan.write_text(json.dumps({"sets": [{"id": "001"}]}))
        manifest = {"stageRoot": str(self.stage), "plan": str(plan), "products": [self.product]}
        (self.work / "staging-manifest.json").write_text(json.dumps(manifest))
        (self.work / "receipts/001.json").write_text(json.dumps(self.product))
        return tree

    def test_recover_unrelated_binary_without_reextract_or_byte_change(self):
        tree = self.prepare_blocked()
        before = (tree / "001-fixture/Scenes/LightingData.asset").read_bytes()
        result = module.recover_blocked(self.project)
        self.assertEqual(1, result["recovered"])
        self.assertEqual(0, result["stillBlocked"])
        self.assertEqual(before, (self.pack / "Scenes/LightingData.asset").read_bytes())
        self.assertIn("b" * 32, (self.pack / "Scenes/Example.unity").read_text())
        self.assertIn("a" * 32, (self.project / "Assets/Scenes.meta").read_text())
        receipt = json.loads((self.work / "receipts/001.json").read_text())
        self.assertEqual("complete", receipt["status"])
        for record in receipt["files"]:
            self.assertEqual(record["sha256"], hashlib.sha256((self.stage / record["path"]).read_bytes()).hexdigest())
        self.assertEqual(self.original_sha, hashlib.sha256(self.source.read_bytes()).hexdigest())
        followup, _ = module.finalize(self.project)
        self.assertEqual([], followup["binaryReview"])
        self.assertEqual(1, followup["binaryAbsenceProofsReused"])

    def test_actual_binary_guid_reference_stays_blocked_without_any_text_edit(self):
        tree = self.prepare_blocked(binary_guid="a" * 32)
        text = tree / "001-fixture/Scenes/Example.unity"
        before = text.read_bytes()
        result = module.recover_blocked(self.project)
        self.assertEqual(0, result["recovered"])
        self.assertEqual(1, result["stillBlocked"])
        self.assertEqual(before, text.read_bytes())
        self.assertFalse(self.pack.exists())

    def test_pre_encoding_fix_binary_absence_proof_is_not_reused(self):
        self.prepare_blocked()
        result = module.recover_blocked(self.project)
        self.assertEqual(1, result["recovered"])
        manifest_path = self.work / "staging-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["products"][0]["binaryGuidRecoveryProofs"][0].pop("proofVersion")
        manifest_path.write_text(json.dumps(manifest))
        followup, _ = module.finalize(self.project)
        self.assertEqual(1, len(followup["binaryReview"]))
        self.assertEqual(0, followup["binaryAbsenceProofsReused"])

    def test_recovery_refuses_partial_extractor_manifest(self):
        self.prepare_blocked()
        (self.work / "fixture-plan.json").write_text(json.dumps({"sets": [{"id": "001"}, {"id": "002"}]}))
        with self.assertRaisesRegex(ValueError, "not reached every planned"):
            module.recover_blocked(self.project)

    def test_casefold_collisions_prefer_exact_case_and_report_ambiguous_fallback(self):
        self.add("Vendor/Noise_Big.tga", b"first texture", "Assets/Vendor/Noise_Big.tga")
        self.add("Vendor/noise_big__guid123.tga", b"second texture", "Assets/Vendor/noise_big.tga")
        self.add("Vendor/Only.tga", b"unique texture", "Assets/Vendor/Only.tga")
        script = self.add("Vendor/Loader.cs", 'string first = "Assets/Vendor/Noise_Big.tga";\n'
            'string second = "Assets/Vendor/noise_big.tga";\n'
            'string ambiguous = "Assets/Vendor/NOISE_BIG.TGA";\n'
            'string unique = "Assets/Vendor/only.TGA";\n', "Assets/Vendor/Loader.cs")
        report, code = self.finish()
        text = script.read_text()
        prefix = "Assets/ThirdParty/YamyamAssetLibrary/001-fixture/Vendor/"
        self.assertIn('first = "' + prefix + 'Noise_Big.tga"', text)
        self.assertIn('second = "' + prefix + 'noise_big__guid123.tga"', text)
        self.assertIn('unique = "' + prefix + 'Only.tga"', text)
        self.assertIn('ambiguous = "Assets/Vendor/NOISE_BIG.TGA"', text)
        self.assertEqual([], report["errors"])
        self.assertEqual(1, len(report["unresolvedAssetPaths"]))
        self.assertEqual(2, len(report["unresolvedAssetPaths"][0]["candidateTargets"]))
        self.assertEqual(1, len(code["ambiguousOriginalPaths"]))
        self.assertTrue((self.pack / "Vendor/Noise_Big.tga").is_file())
        self.assertTrue((self.pack / "Vendor/noise_big__guid123.tga").is_file())

    def test_duplicate_exact_original_paths_report_without_aborting_or_losing_assets(self):
        self.add("Vendor/Noise.tga", b"first texture", "Assets/Vendor/Noise.tga")
        self.add("Vendor/Noise__guid456.tga", b"other texture", "Assets/Vendor/Noise.tga")
        script = self.add("Vendor/Loader.cs", 'string path = "Assets/Vendor/Noise.tga";\n', "Assets/Vendor/Loader.cs")
        report, _ = self.finish()
        self.assertEqual('string path = "Assets/Vendor/Noise.tga";\n', script.read_text())
        self.assertEqual([], report["errors"])
        self.assertEqual(1, len(report["unresolvedAssetPaths"]))
        self.assertIn("exact spelling has multiple", report["unresolvedAssetPaths"][0]["reason"])
        self.assertTrue((self.pack / "Vendor/Noise.tga").is_file())
        self.assertTrue((self.pack / "Vendor/Noise__guid456.tga").is_file())

    def test_owned_rename_retries_two_permission_errors_then_promotes(self):
        tree = self.prepare_blocked()
        original_rename = module.os.rename
        source = tree / "001-fixture"
        failures = []

        def transient(before, after):
            if Path(before) == source and len(failures) < 2:
                failures.append(True)
                raise PermissionError(5, "fixture transient Windows file handle")
            return original_rename(before, after)

        with mock.patch.object(module.os, "rename", side_effect=transient), mock.patch.object(module.time, "sleep") as sleep:
            result = module.recover_blocked(self.project)
        self.assertEqual(1, result["recovered"])
        self.assertEqual(2, result["products"][0]["moveAttempts"]["folder"]["permissionRetries"])
        self.assertEqual([mock.call(.25), mock.call(.5)], sleep.call_args_list)
        self.assertTrue(self.pack.is_dir())
        self.assertFalse(source.exists())

    def test_permanent_metadata_move_permission_error_rolls_back_folder_and_text(self):
        tree = self.prepare_blocked()
        original_rename = module.os.rename
        source_meta = tree / "001-fixture.meta"
        text = tree / "001-fixture/Scenes/Example.unity"
        before = text.read_bytes()
        failures = []

        def permanent_metadata(before_path, after_path):
            if Path(before_path) == source_meta:
                failures.append(True)
                raise PermissionError(5, "fixture permanently denied metadata move")
            return original_rename(before_path, after_path)

        with mock.patch.object(module.os, "rename", side_effect=permanent_metadata), mock.patch.object(module.time, "sleep") as sleep:
            result = module.recover_blocked(self.project)
        self.assertEqual(0, result["recovered"])
        self.assertEqual(1, result["stillBlocked"])
        self.assertEqual(8, len(failures))
        self.assertEqual(7, sleep.call_count)
        self.assertEqual(15.75, sum(call.args[0] for call in sleep.call_args_list))
        self.assertEqual(before, text.read_bytes())
        self.assertTrue((tree / "001-fixture").is_dir())
        self.assertTrue(source_meta.is_file())
        self.assertFalse(self.pack.exists())
        self.assertEqual("blocked-binary-guid-collision", json.loads((self.work / "receipts/001.json").read_text())["status"])

    def test_owned_rename_never_retries_ordinary_errors_or_overwrites_destination(self):
        source_root, destination_root = self.work / "source", self.work / "destination"
        source_root.mkdir(); destination_root.mkdir()
        source, destination = source_root / "input", destination_root / "output"
        source.write_bytes(b"source")
        with mock.patch.object(module.os, "rename", side_effect=FileNotFoundError("fixture ordinary error")) as rename, mock.patch.object(module.time, "sleep") as sleep:
            with self.assertRaises(FileNotFoundError):
                module.rename_owned_with_retry(source, destination, source_root, destination_root)
            self.assertEqual(1, rename.call_count)
            self.assertEqual(0, sleep.call_count)
        destination.write_bytes(b"preserved")
        with mock.patch.object(module.os, "rename") as rename:
            with self.assertRaises(FileExistsError):
                module.rename_owned_with_retry(source, destination, source_root, destination_root)
            rename.assert_not_called()
        self.assertEqual(b"source", source.read_bytes())
        self.assertEqual(b"preserved", destination.read_bytes())

    def test_repair_only_keeps_other_product_bytes_and_receipt_but_audits_its_code(self):
        self.add("Vendor/Texture.png", b"selected texture", "Assets/Vendor/Texture.png")
        selected_yaml = self.add("Vendor/Layer.terrainlayer", "%YAML 1.1\n--- !u!195 &1\nref: " + "a" * 32 + "\nm_Path: Assets/Vendor/Texture.png\n", "Assets/Vendor/Layer.terrainlayer")
        selected_code = self.add("Vendor/Shared.cs", 'class Shared {}\nstring path = "Assets/Vendor/Texture.png";\n', "Assets/Vendor/Shared.cs")
        other = {"id": "002", "status": "complete", "guidRemaps": {"a" * 32: "b" * 32}, "files": [], "scripts": []}
        other_bytes = {
            "002-other/Other/Layer.terrainlayer": ("%YAML 1.1\n--- !u!195 &1\nref: " + "a" * 32).encode(),
            "002-other/Other/Binary.spriteatlas": b"\0unselected binary" + b"a" * 32,
            "002-other/Other/Shared.cs": b'class Shared {}\nstring old = "Assets/Other/Texture.png";\n',
            "002-other/Other/Other.asmdef": b'{"name":"Other.Assembly","references":[]}',
            "002-other/Other/Vendor.dll": b"fixture DLL is inventory-only and never executed",
        }
        for relative, contents in other_bytes.items():
            path = self.stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
            other["files"].append({"path": relative, "bytes": len(contents), "sha256": hashlib.sha256(contents).hexdigest(),
                "source": {"kind": "unitypackage", "originalPath": "Assets/Other/" + Path(relative).name}})
        manifest = {"stageRoot": str(self.stage), "products": [self.product, other]}
        (self.work / "staging-manifest.json").write_text(json.dumps(manifest))
        (self.work / "receipts/001.json").write_text(json.dumps(self.product))
        other_receipt = self.work / "receipts/002.json"
        other_receipt.write_text(json.dumps(other, separators=(",", ":")))
        receipt_before = other_receipt.read_bytes()
        report, code = module.finalize(self.project, repair_only={"001"})
        self.assertIn("b" * 32, selected_yaml.read_text())
        self.assertIn("Assets/ThirdParty/YamyamAssetLibrary/001-fixture/Vendor/Texture.png", selected_code.read_text())
        self.assertEqual([], report["errors"])
        self.assertEqual([], report["binaryReview"])
        self.assertEqual(["002"], report["repairSkippedProducts"])
        self.assertEqual({"001", "002"}, set(code["productsAudited"]))
        self.assertEqual(2, len(code["duplicateTypeCandidates"][0]["paths"]))
        self.assertEqual(1, len(code["assemblies"]))
        self.assertEqual(1, len(code["dlls"]))
        for relative, contents in other_bytes.items():
            self.assertEqual(contents, (self.stage / relative).read_bytes())
        self.assertEqual(receipt_before, other_receipt.read_bytes())

    def test_path_mapping_caches_repeated_validated_parent_pairs(self):
        for index in range(5):
            self.add(f"Vendor/Deep/File{index}.png", b"texture", f"Assets/Vendor/Deep/File{index}.png")
            self.add(f"Vendor/Deep/File{index}.png.meta", "fileFormatVersion: 2\nguid: " + f"{index + 1:032x}" + "\n", f"Assets/Vendor/Deep/File{index}.png")
        original_contained = module.contained
        with mock.patch.object(module, "contained", wraps=original_contained) as inspect:
            mapping = module.product_path_map(self.product, self.stage, "Assets/ThirdParty/YamyamAssetLibrary")
        relative_calls = [str(call.args[1]).replace("\\", "/") for call in inspect.call_args_list]
        self.assertEqual(1, relative_calls.count("001-fixture/Vendor"))
        self.assertEqual(1, relative_calls.count("001-fixture/Vendor/Deep"))
        self.assertEqual(1, relative_calls.count("001-fixture/Vendor/Deep/File0.png"))
        self.assertEqual(len(set(relative_calls)), mapping["cacheStats"]["validatedTargets"])


if __name__ == "__main__":
    unittest.main()
