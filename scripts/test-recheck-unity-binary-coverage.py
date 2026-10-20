"""Small extension-independent coverage fixtures; no real project is read."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


tool = load("binary_global_coverage", "recheck-unity-binary-coverage.py")
fixtures = load("binary_global_fixtures", "test-finalize-unity-asset-library.py")


class CoverageFixtures(unittest.TestCase):
    def test_headers_17_22_23_both_endians_and_reserved_bytes(self):
        for version in (17, 22, 23):
            for endian in ("<", ">"):
                data = fixtures.serialized_fixture(version, [], endian=endian)
                self.assertEqual(version, tool.serialized_header(data[:64], len(data))["formatVersion"])
                changed = bytearray(data); changed[17:20] = b"abc"
                self.assertIsNotNone(tool.serialized_header(bytes(changed[:64]), len(changed)))
        self.assertIsNone(tool.serialized_header(b"%YAML 1.1\n" * 8, 80))
        self.assertIsNone(tool.serialized_header(b"Kaydara FBX Binary\0" + b"\0" * 50, 500))
        self.assertIsNone(tool.serialized_header(data[:64], len(data) + 1))

    def test_unknown_extension_binary_is_audited_and_correct_nibble_hit_found(self):
        with tempfile.TemporaryDirectory(prefix="yamyam-global-binary-") as temporary:
            project = Path(temporary) / "Main"
            work = project / "Library/YamyamAssetLibrary"
            root = work / "headless-project/Assets/ThirdParty/YamyamAssetLibrary"
            root.mkdir(parents=True)
            old, new = "c0474c8c6e059a24882af631c769b71e", "172515602e62fb746b5d573b38a5fe58"
            raw = tool.F.guid_byte_forms(old)["unity-byte-nibbles"].hex()
            data = fixtures.serialized_fixture(22, [raw])
            path = root / "001-example/native.customextension"; path.parent.mkdir(); path.write_bytes(data)
            products = [{"id": f"{number:03d}", "status": "complete", "files": [], "guidRemaps": {}} for number in range(84)]
            products[1].update(guidRemaps={old: new}, files=[{"path": "001-example/native.customextension", "bytes": len(data), "sha256": tool.sha(data)}])
            manifest_path = work / "staging-manifest.json"
            manifest = {"stageRoot": str(root), "products": products}
            before = json.dumps(manifest).encode(); manifest_path.write_bytes(before)
            result = tool.audit(project)
            self.assertEqual("needs-extra-binary-reference-repair", result["status"])
            self.assertEqual(1, result["headersChecked"])
            self.assertEqual(1, result["additionalBinaryFiles"])
            self.assertEqual(1, result["additionalExactExternalHits"])
            self.assertEqual(0, result["staleReceiptFiles"])
            self.assertEqual(before, manifest_path.read_bytes())
            self.assertEqual(data, path.read_bytes())

    def test_historical_path_is_not_redecoded_and_malformed_native_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="yamyam-global-historical-") as temporary:
            project = Path(temporary) / "Main"; work = project / "Library/YamyamAssetLibrary"
            root = work / "headless-project/Assets/ThirdParty/YamyamAssetLibrary"; root.mkdir(parents=True)
            products = [{"id": f"{number:03d}", "status": "complete", "files": [], "guidRemaps": {}} for number in range(84)]
            products[1].update(guidRemaps={"a" * 32: "b" * 32}, binaryGuidRecoveryProofs=[{"path": "001/historical.asset"}], files=[
                {"path": "001/historical.asset", "bytes": 20, "sha256": "0" * 64},
                {"path": "001/unknown.asset", "bytes": 20, "sha256": tool.sha(b"x" * 20)}])
            (root / "001").mkdir(); (root / "001/unknown.asset").write_bytes(b"x" * 20)
            (work / "staging-manifest.json").write_text(json.dumps({"stageRoot": str(root), "products": products}))
            result = tool.audit(project)
            self.assertEqual(1, result["historicalProofPaths"])
            self.assertEqual("needs-review", result["status"])
            self.assertEqual(1, len(result["errors"]))
            self.assertIn("Native extension", result["errors"][0]["error"])


if __name__ == "__main__":
    unittest.main()
