"""Read seven enumerated binary scenes without Unity, vendor execution or saving.

UnityPy API reference: https://github.com/K0lb3/UnityPy
Pinned local dependency: UnityPy==1.25.4, installed only under task Library.
Only MonoBehaviour/MonoScript type trees are read; no images/audio are decoded,
PPtr.deref is never called, and no external dependency files are auto-loaded.
"""
import argparse
import ctypes
import datetime as dt
import gc
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys


def read_shared(path):
    """Allow Unity to rename/update its own files while this read-only tool runs."""
    if os.name != "nt":
        return Path(path).read_bytes()
    import msvcrt
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
                       ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    create.restype = ctypes.c_void_p
    handle = create(str(Path(path).resolve()), 0x80000000, 1 | 2 | 4, None, 3, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    with os.fdopen(descriptor, "rb") as stream:
        return stream.read()


def read_json(path):
    return json.loads(read_shared(path).decode("utf-8-sig"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--dependencies", type=Path)
    parser.add_argument("--census", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    work = args.project.resolve() / "Library/YamyamAssetLibrary"
    dependencies = args.dependencies or work / "tool-dependencies"
    sys.path.insert(0, str(dependencies.resolve()))
    import UnityPy
    from UnityPy.helpers import TypeTreeHelper
    if UnityPy.__version__ != "1.25.4":
        raise ValueError("This audited parser expects pinned UnityPy1.25.4")
    # The project's documentation warns that the C typetree accelerator can
    # crash without an exception. Pure Python is sufficient for seven scenes.
    TypeTreeHelper.read_typetree_boost = None
    manifest_path = work / "staging-manifest.json"
    manifest_bytes = read_shared(manifest_path)
    manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    stage = Path(manifest["stageRoot"]).resolve()
    if not stage.is_relative_to(work.resolve()):
        raise ValueError("Binary preparation accepts only the owned isolated Library copy")
    census = read_json(args.census or work / "scene-header-census.json")
    script_owners, script_owner_meta_paths = {}, {}
    for product in manifest["products"]:
        for record in product.get("files", []):
            if record["path"].lower().endswith((".cs.meta", ".dll.meta")) and record.get("guid"):
                script_owners[record["guid"].lower()] = "Assets/ThirdParty/YamyamAssetLibrary/" + record["path"][:-5]
                script_owner_meta_paths[record["guid"].lower()] = stage / record["path"]
    for package in (args.project.resolve() / "Library/PackageCache").glob("com.unity.render-pipelines.core@*"):
        meta = package / "Runtime/Volume/Volume.cs.meta"
        if meta.exists():
            match = re.search(rb"(?m)^guid:[ \t]*([a-f0-9]{32})", read_shared(meta))
            if match:
                script_owners[match.group(1).decode()] = "Packages/com.unity.render-pipelines.core/Runtime/Volume/Volume.cs"
                script_owner_meta_paths[match.group(1).decode()] = meta
            break
    report = {"schemaVersion": 1, "generatedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "sourceManifestSha256": hashlib.sha256(manifest_bytes).hexdigest(),
              "sourceCensus": str(args.census or work / "scene-header-census.json"), "stageRoot": str(stage),
              "parser": "UnityPy", "parserVersion": UnityPy.__version__, "purePythonTypeTreeReader": True,
              "unityLaunched": False, "vendorAssemblyExecuted": False, "sceneFilesModified": False,
              "externalPointersDereferenced": False, "imagesOrAudioDecoded": False, "scenes": []}
    guid_reader_source = dependencies / "UnityPy/files/SerializedFile.py"
    report["guidEncodingImplementation"] = {"source": str(guid_reader_source), "sha256": hashlib.sha256(read_shared(guid_reader_source)).hexdigest(),
        "operation": "FileIdentifier.__init__ directly assigns self.guid = reader.read_bytes(16); no integer/hex conversion.",
        "canonicalConversion": "Swap the high and low hexadecimal nibble of every source byte; verified against actual vendor and official package MonoScript metadata below.",
        "primarySource": "https://github.com/K0lb3/UnityPy/blob/master/UnityPy/files/SerializedFile.py"}
    report["guidEncodingProofs"] = []
    for scene in census["binaryScenes"]:
        relative = scene["path"]
        source = (stage / relative).resolve()
        if not source.is_relative_to(stage) or source.suffix.lower() != ".unity":
            raise ValueError("Census scene escaped its owned root")
        result = {"scenePath": "Assets/ThirdParty/YamyamAssetLibrary/" + relative, "relativePath": relative,
                  "status": "parsing", "monoBehaviourCount": 0, "references": [], "decodeFailures": []}
        try:
            raw = read_shared(source)
            result.update(fileBytes=len(raw), sourceBytes=len(raw), sourceSha256=hashlib.sha256(raw).hexdigest())
            environment = UnityPy.load(io.BytesIO(raw))
            serialized = environment.file
            result.update(formatVersion=serialized.header.version, unityVersion=serialized.unity_version,
                          objectCount=len(serialized.objects), hasTypeTree=serialized._enable_type_tree,
                          externalCount=len(serialized.externals))
            for obj in serialized.objects.values():
                if obj.type.name != "MonoBehaviour":
                    continue
                result["monoBehaviourCount"] += 1
                reference = {"objectPathId": str(obj.path_id), "decodeStatus": "decoded"}
                try:
                    data = obj.parse_as_dict(check_read=True)
                    pointer = data["m_Script"]
                    file_id, local_id = int(pointer["m_FileID"]), int(pointer["m_PathID"])
                    reference.update(scriptExternalFileId=file_id, scriptLocalFileId=str(local_id), scriptGuid="",
                                     scriptGuidCandidates=[], scriptReferenceKind="null" if local_id == 0 else "external" if file_id else "internal")
                    game = data.get("m_GameObject", {})
                    reference["gameObjectPathId"] = str(game.get("m_PathID", 0))
                    if local_id == 0:
                        reference["referenceStatus"] = "missing-script-reference"
                    elif file_id > 0:
                        if file_id > len(serialized.externals):
                            raise ValueError("m_Script external index exceeds parsed external table")
                        external = serialized.externals[file_id - 1]
                        guid_bytes = bytes(external.guid)
                        raw_guid = guid_bytes.hex()
                        canonical = bytes((value >> 4) | ((value & 15) << 4) for value in guid_bytes).hex()
                        byte_offset, occurrences = raw.find(guid_bytes), raw.count(guid_bytes)
                        reference.update(scriptGuid=canonical, scriptGuidRawBytes=raw_guid,
                                         scriptGuidCandidates=[canonical], externalPath=external.path,
                                         guidEncoding="canonical-per-byte-nibble-swap",
                                         scriptGuidSourceByteOffset=byte_offset, scriptGuidUniqueByteOccurrenceCount=occurrences,
                                         knownScriptAssetPath=script_owners.get(canonical, ""),
                                         referenceStatus="requires-unity-guid-localid-class-resolution")
                        if canonical in script_owners:
                            header_bytes = 48 if serialized.header.version >= 22 else 20
                            if occurrences != 1 or byte_offset < header_bytes or byte_offset + 16 > serialized.header.data_offset:
                                raise ValueError("Known GUID proof was not a unique source metadata byte range")
                            meta_path = script_owner_meta_paths[canonical]
                            meta_bytes = read_shared(meta_path)
                            meta_guid = re.search(rb"(?m)^guid:[ \t]*([a-f0-9]{32})", meta_bytes)
                            if not meta_guid or meta_guid.group(1).decode() != canonical:
                                raise ValueError("Known GUID proof no longer matches the actual source MonoScript.meta")
                            proof = {"scenePath": result["scenePath"], "sourceByteOffset": byte_offset,
                                     "sourceBytesHex": raw[byte_offset:byte_offset + 16].hex(), "canonicalMetaGuid": canonical,
                                     "matchingMonoScriptAsset": script_owners[canonical], "sourceByteOccurrences": occurrences,
                                     "matchingMetaFile": str(meta_path), "metaGuidRead": meta_guid.group(1).decode(),
                                     "metaSha256": hashlib.sha256(meta_bytes).hexdigest()}
                            if proof not in report["guidEncodingProofs"]:
                                report["guidEncodingProofs"].append(proof)
                    elif file_id == 0:
                        target = serialized.objects.get(local_id)
                        if target is None or target.type.name != "MonoScript":
                            reference["referenceStatus"] = "invalid-internal-monoscript-reference"
                        else:
                            script = target.parse_as_dict(check_read=True)
                            reference["internalMonoScript"] = {"assemblyName": script.get("m_AssemblyName", ""),
                                                               "namespaceName": script.get("m_Namespace", ""), "className": script.get("m_ClassName", "")}
                            reference["referenceStatus"] = "internal-type-requires-unity-class-resolution"
                    else:
                        raise ValueError("Negative m_Script external-file index")
                except Exception as error:
                    reference.update(decodeStatus="failed", error=str(error), referenceStatus="unavailable")
                    result["decodeFailures"].append({"objectPathId": str(obj.path_id), "error": str(error)})
                result["references"].append(reference)
            result["status"] = "decoded" if not result["decodeFailures"] else "decoded-with-failures"
            del environment, serialized, raw
            gc.collect()
        except Exception as error:
            result["status"] = "failed"
            result["decodeFailures"].append({"error": str(error)})
        report["scenes"].append(result)
        print(json.dumps({"scenePath": result["scenePath"], "status": result["status"], "components": result["monoBehaviourCount"],
                          "decodeFailures": len(result["decodeFailures"])}), flush=True)
    report["summary"] = {"scenes": len(report["scenes"]), "decodedScenes": sum(scene["status"] == "decoded" for scene in report["scenes"]),
                         "monoBehaviours": sum(scene["monoBehaviourCount"] for scene in report["scenes"]),
                         "decodeFailures": sum(len(scene["decodeFailures"]) for scene in report["scenes"]),
                         "nullOrInvalidReferences": sum(reference.get("referenceStatus") in {"missing-script-reference", "invalid-internal-monoscript-reference"}
                                                         for scene in report["scenes"] for reference in scene["references"])}
    output = args.out or work / "binary-scene-script-references.json"
    if not output.resolve().is_relative_to(work.resolve()):
        raise ValueError("Output must stay inside the owned Library evidence folder")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), **report["summary"]}))
    return 0 if not report["summary"]["decodeFailures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
