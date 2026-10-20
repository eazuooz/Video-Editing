#!/usr/bin/env python3
"""Repair staged Unity YAML GUID references, then inventory vendor C# risks.

Run after import-unity-asset-library.py finishes, before the Editor install.
This tool never writes Assets, original downloads, or binary serialized assets.
Only changed staged text files have their receipt SHA256 recomputed.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import sys
import time
import uuid

TOKEN = re.compile(rb"(?<![a-fA-F0-9])([a-fA-F0-9]{32})(?![a-fA-F0-9])")
GUID = re.compile(rb"(?m)^guid:\s*([a-fA-F0-9]{32})\s*$")
SERIALIZED = {
    ".unity", ".prefab", ".asset", ".mat", ".anim", ".controller", ".overridecontroller",
    ".playable", ".mask", ".mixer", ".rendertexture", ".guiskin", ".lighting", ".flare",
    ".physicmaterial", ".physicsmaterial2d", ".terrainlayer", ".spriteatlas", ".spriteatlasv2",
    ".preset", ".shadervariants", ".giparams", ".brush", ".signal", ".spritelib", ".cubemap",
    ".lightingdata", ".flaredata", ".lensflaredata", ".scenetemplate", ".fontsettings", ".flare",
}
JSON_UNITY = {".shadergraph", ".shadersubgraph", ".vfx", ".vfxoperator", ".vfxblock",
              ".asmdef", ".asmref", ".inputactions"}
AUTO_MARKERS = ("InitializeOnLoad", "InitializeOnLoadMethod", "AssetPostprocessor",
                "ScriptedImporter", "ExecuteAlways", "ExecuteInEditMode", "OnWillSaveAssets",
                "OnPostprocessAllAssets", "DidReloadScripts")
SIDE_EFFECT_MARKERS = ("Process.Start", "Application.OpenURL", "EditorUtility.DisplayDialog",
                       "File.Delete", "Directory.Delete", "File.Write", "Directory.Move")
PATH_TEXT_EXT = {".cs", ".shader", ".cginc", ".hlsl", ".compute", ".uxml", ".uss", ".xml"}
CODE_AUDIT_EXT = {".cs", ".asmdef", ".asmref", ".dll", ".shader", ".cginc", ".hlsl", ".compute", ".shadergraph", ".shadersubgraph"}
BINARY_GUID_PROOF_VERSION = 2
PATH_LITERAL = re.compile(rb'''(?P<quote>["'])(?P<path>Assets(?:/|\\)[^"'\r\n]+)(?P=quote)''')
ANGLE_INCLUDE = re.compile(rb'(?m)(^\s*#\s*include(?:_with_pragmas)?\s*<)(Assets/[^>\r\n]+)(>)')
YAML_PATH = re.compile(rb'(?m)(:[ \t]*)(Assets/[^\r\n]+?)([ \t]*\r?$)')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


class MetadataReader:
    """Bounded reader for a SerializedFile's metadata, never its object payloads."""
    def __init__(self, data, endian):
        self.data, self.endian, self.position = data, endian, 0

    def take(self, size):
        if size < 0 or self.position + size > len(self.data):
            raise ValueError("Serialized metadata read exceeded declared bounds")
        start = self.position
        self.position += size
        return self.data[start:self.position]

    def number(self, format):
        return struct.unpack(self.endian + format, self.take(struct.calcsize(format)))[0]

    def count(self, maximum=1000000):
        value = self.number("i")
        if value < 0 or value > maximum:
            raise ValueError(f"Invalid serialized metadata count: {value}")
        return value

    def boolean(self):
        value = self.number("B")
        if value not in (0, 1):
            raise ValueError("Invalid serialized metadata boolean")
        return bool(value)

    def align4(self):
        self.take((-self.position) % 4)

    def string(self, maximum=1048576):
        end = self.data.find(b"\0", self.position, min(len(self.data), self.position + maximum + 1))
        if end < 0:
            raise ValueError("Missing bounded metadata string terminator")
        value = self.data[self.position:end].decode("utf-8")
        self.position = end + 1
        return value


def parse_binary_externals(path):
    """Read format17–23 tables with bounds/type/range checks; never write binary.

    Format facts checked against the primary parser implementations:
    https://github.com/K0lb3/UnityPy/blob/master/UnityPy/files/SerializedFile.py
    https://github.com/K0lb3/UnityPy/blob/master/UnityPy/files/ObjectReader.py
    https://github.com/K0lb3/UnityPy/blob/master/UnityPy/helpers/TypeTreeNode.py
    Format23 is pinned to its original definition, before shared-subtree changes:
    https://github.com/K0lb3/UnityPy/blob/d1edc71c0c32/UnityPy/helpers/TypeTreeNode.py
    https://github.com/K0lb3/UnityPy/blob/d1edc71c0c32/UnityPy/files/SerializedFile.py
    Later formats are deliberately rejected instead of guessing their tree layout.
    """
    path = Path(path)
    actual_size = path.stat().st_size
    with path.open("rb") as source:
        header = source.read(48)
        if len(header) < 20:
            raise ValueError("Truncated SerializedFile header")
        metadata_size, file_size, version, data_offset = struct.unpack(">4I", header[:16])
        if version not in range(17, 24):
            raise ValueError(f"Unsupported SerializedFile format {version}; binary left unchanged")
        if header[16] not in (0, 1) or header[17:20] != b"\0\0\0":
            raise ValueError("Unexpected SerializedFile endian/reserved header fields")
        endian = ">" if header[16] else "<"
        header_size = 20
        if version >= 22:
            if len(header) != 48:
                raise ValueError("Truncated 64-bit SerializedFile header")
            metadata_size, file_size, data_offset, _reserved64 = struct.unpack(">Iqqq", header[20:48])
            header_size = 48
        if file_size != actual_size or metadata_size < 16 or metadata_size > 256 * 1024 * 1024:
            raise ValueError("SerializedFile size/header mismatch or excessive metadata")
        if data_offset < header_size + metadata_size or data_offset > file_size:
            raise ValueError("SerializedFile metadata/data regions overlap or exceed file")
        source.seek(header_size)
        metadata = source.read(metadata_size)
        if len(metadata) != metadata_size:
            raise ValueError("Truncated SerializedFile metadata")
    reader = MetadataReader(metadata, endian)
    unity_version = reader.string(256)
    if not re.fullmatch(r"\d+\.\d+\.\d+[\w.\-]*", unity_version):
        raise ValueError("Unexpected serialized Unity version string")
    platform = reader.number("i")
    type_tree = reader.boolean()

    def read_type(reference=False):
        class_id = reader.number("i")
        reader.boolean()  # stripped type (format16+)
        script_index = reader.number("h")
        if script_index < -1:
            raise ValueError("Invalid serialized script type index")
        if (reference and script_index >= 0) or class_id == 114:
            reader.take(16)  # script identifier
        reader.take(16)  # old type hash
        if type_tree:
            tree_reader = reader
            if version == 23:
                reader.take(16)  # type-tree information hash
                info_bytes = reader.number("I")
                if info_bytes:
                    if info_bytes < 16 or info_bytes > 128 * 1024 * 1024:
                        raise ValueError("Invalid format23 type-tree information size")
                    tree_reader = MetadataReader(reader.take(info_bytes), endian)
                    if tree_reader.take(4) != b"mhtt":
                        raise ValueError("Invalid format23 type-tree information magic")
                    if tree_reader.number("i") != version:
                        raise ValueError("Format23 type-tree format version disagrees with file header")
                else:
                    tree_reader = None  # Hash-only shared/absent type-tree information.
            if tree_reader is not None:
                nodes, strings = tree_reader.count(2000000), tree_reader.count(128 * 1024 * 1024)
                tree_reader.take(nodes * (32 if version >= 19 else 24))
                tree_reader.take(strings)
                if version == 23:
                    if tree_reader.position != len(tree_reader.data):
                        raise ValueError("Format23 type-tree information was not completely consumed")
            if version >= 21:
                if reference:
                    reader.string(); reader.string(); reader.string()
                else:
                    reader.take(reader.count() * 4)
        return class_id

    type_count = reader.count(100000)
    classes = [read_type() for _ in range(type_count)]
    objects = reader.count(2000000)
    for _ in range(objects):
        reader.align4()
        reader.number("q")  # path identifier
        start = reader.number("q" if version >= 22 else "I")
        size, type_index = reader.number("I"), reader.number("i")
        if type_index < 0 or type_index >= len(classes) or start < 0 or data_offset + start + size > file_size:
            raise ValueError("Serialized object table has an invalid type/data range")
    scripts = reader.count()
    for _ in range(scripts):
        reader.number("i")
        reader.align4()
        reader.number("q")
    external_count = reader.count()
    externals = []
    for _ in range(external_count):
        reader.string()  # reserved empty string; retained variants are valid strings
        guid_offset = header_size + reader.position
        raw_guid = reader.take(16)
        kind = reader.number("i")
        if kind not in range(4):
            raise ValueError("Unknown external SerializedFile reference kind")
        externals.append({"rawGuidHex": raw_guid.hex(), "canonicalGuid": unity_guid_from_bytes(raw_guid),
                          "guidOffset": guid_offset, "type": kind, "path": reader.string()})
    reference_types = 0
    if version >= 20:
        reference_types = reader.count(100000)
        for _ in range(reference_types):
            read_type(reference=True)
    user_info = reader.string()
    trailing = metadata[reader.position:]
    if len(trailing) > 15 or any(trailing):
        raise ValueError("Serialized metadata was not completely consumed; no absence proof accepted")
    return {"formatVersion": version, "unityVersion": unity_version, "endian": endian,
            "metadataBytes": metadata_size, "metadataBytesConsumed": reader.position,
            "dataOffset": data_offset, "fileBytes": file_size, "platform": platform,
            "hasTypeTree": type_tree, "types": type_count, "objects": objects, "scripts": scripts,
            "referenceTypes": reference_types, "externalCount": len(externals), "externals": externals,
            "userInfo": user_info, "metadataPaddingBytes": len(trailing)}


def unity_guid_from_bytes(raw):
    """Canonical .meta spelling of Unity's 16 serialized GUID bytes.

    Unity's binary GUID uses the opposite nibble order within each byte. This
    is independent of the SerializedFile numeric endian flag. Both directions
    use the same involution. Confirmed against exact external-table byte ranges
    and official/package plus vendor MonoScript .meta GUIDs in actual scenes.
    """
    if len(raw) != 16:
        raise ValueError("A serialized Unity GUID must contain exactly 16 bytes")
    return bytes(((value & 15) << 4) | (value >> 4) for value in raw).hex()


def guid_byte_forms(guid):
    """Actual Unity nibble encoding plus conservative alternate spellings."""
    if not re.fullmatch(r"[a-fA-F0-9]{32}", guid):
        raise ValueError("Invalid recovery GUID")
    raw = bytes.fromhex(guid)
    forms = {"unity-byte-nibbles": bytes.fromhex(unity_guid_from_bytes(raw)),
             "raw128": raw, "uint32-little": b"".join(raw[i:i + 4][::-1] for i in range(0, 16, 4)),
             "dotnet-guid": uuid.UUID(hex=guid).bytes_le, "reverse128": raw[::-1],
             "word-nibbles": bytes.fromhex("".join(guid[i:i + 8][::-1] for i in range(0, 32, 8)))}
    forms.update({"ascii-lower": guid.lower().encode(), "ascii-upper": guid.upper().encode(),
                  "utf16-le": guid.lower().encode("utf-16le"), "utf16-be": guid.lower().encode("utf-16be")})
    return forms


def binary_absence_proof(path, remaps, expected_sha):
    table = parse_binary_externals(path)
    patterns = [(guid, name, value) for guid in remaps for name, value in guid_byte_forms(guid).items()]
    hits = []
    for entry in table["externals"]:
        raw = bytes.fromhex(entry["rawGuidHex"])
        for guid, form, pattern in patterns:
            if len(pattern) == 16 and raw == pattern:
                hits.append({"guid": guid, "representation": form, "where": "external-table", "externalPath": entry["path"],
                             "guidOffset": entry["guidOffset"], "rawGuidHex": entry["rawGuidHex"],
                             "canonicalGuid": entry["canonicalGuid"]})
    digest = hashlib.sha256()
    tail = b""
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(2 * 1024 * 1024), b""):
            digest.update(chunk)
            search = tail + chunk
            for guid, form, pattern in patterns:
                if pattern in search:
                    hit = {"guid": guid, "representation": form, "where": "whole-binary-byte-scan"}
                    if hit not in hits:
                        hits.append(hit)
            tail = search[-63:]
    actual_sha = digest.hexdigest()
    if expected_sha is not None and actual_sha != expected_sha:
        raise ValueError("Binary SHA differs from the extraction receipt")
    return {"proofVersion": BINARY_GUID_PROOF_VERSION, "sha256Before": actual_sha, "sha256After": actual_sha,
            "binaryModified": False, "collidedGuidsAbsent": not hits, "collidingReferences": hits,
            "testedCollidedGuids": sorted(remaps),
            "scope": "Fully parsed external GUID table plus conservative whole-file GUID spellings. Object payloads are never rewritten.",
            **table}


def hash_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(2 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def meta_guid(path):
    with Path(path).open("rb") as source:
        match = GUID.search(source.read(65536))
    if not match:
        raise ValueError(f"No GUID in metadata: {path}")
    return match.group(1).decode().lower()


def rename_owned_with_retry(source, destination, source_root, destination_root, attempts=8):
    """Retry only transient Windows access-denied failures, never replace a target.

    The default seven waits total15.75seconds. Ordinary errors propagate without
    retry. Callers retain their transactional text/move rollback on final failure.
    """
    if attempts < 1 or attempts > 8:
        raise ValueError("Owned rename permits1–8 bounded attempts")
    source_root, destination_root = Path(source_root).resolve(), Path(destination_root).resolve()
    source, destination = Path(source), Path(destination)
    for attempt in range(attempts):
        absolute_source, absolute_destination = source.resolve(), destination.resolve()
        if (absolute_source == source_root or not absolute_source.is_relative_to(source_root)
                or absolute_destination == destination_root or not absolute_destination.is_relative_to(destination_root)):
            raise ValueError("Rename escaped the explicitly owned source/destination roots")
        if source.is_symlink() or os.path.lexists(destination):
            raise FileExistsError(f"Refusing symlink source or existing rename destination: {destination}")
        try:
            os.rename(absolute_source, absolute_destination)
            return {"attempts": attempt + 1, "permissionRetries": attempt}
        except PermissionError:
            if os.path.lexists(destination):
                raise FileExistsError(f"Rename destination appeared; no overwrite attempted: {destination}")
            if attempt + 1 == attempts:
                raise
            time.sleep(min(.25 * (2 ** attempt), 4))


def recover_blocked(project, manifest_path=None, require_complete_plan=True):
    """Promote existing work trees only after binary absence and global GUID checks."""
    project = Path(project).resolve()
    work = project / "Library/YamyamAssetLibrary"
    manifest_path = Path(manifest_path).resolve() if manifest_path else work / "staging-manifest.json"
    if not manifest_path.is_relative_to(work.resolve()):
        raise ValueError("Recovery manifest escaped task-owned Library directory")
    manifest = read_json(manifest_path)
    if require_complete_plan:
        if not manifest.get("plan"):
            raise ValueError("Recovery requires the complete source plan to prove extraction finished")
        plan = read_json(manifest["plan"])
        expected = {str(product["id"]) for product in plan["sets"]}
        actual = [str(product["id"]) for product in manifest["products"]]
        terminal = {"complete", "blocked-binary-guid-collision", "failed"}
        if set(actual) != expected or len(actual) != len(expected) or any(product.get("status") not in terminal for product in manifest["products"]):
            raise ValueError("Extraction has not reached every planned terminal receipt; recovery refused while extraction is running")
    stage = Path(manifest["stageRoot"]).resolve()
    if not stage.is_relative_to(work.resolve()) or not stage.is_dir():
        raise ValueError("Recovery staging root is missing/outside task directory")
    owners = {}
    for meta in (project / "Assets").rglob("*.meta"):
        if meta.is_symlink():
            continue
        owners.setdefault(meta_guid(meta), {"owner": "existing-project", "path": str(meta)})
    for product in manifest["products"]:
        if product.get("status") != "complete":
            continue
        for record in product.get("files", []):
            if not record["path"].lower().endswith(".meta"):
                continue
            guid = meta_guid(contained(stage, record["path"]))
            if record.get("guid") and guid != record["guid"]:
                raise ValueError(f"Completed product metadata differs from receipt: {record['path']}")
            if guid in owners:
                raise ValueError(f"Existing completed products already have a GUID collision: {guid}")
            owners[guid] = {"owner": product["id"], "path": record["path"]}
    report = {"schemaVersion": 1, "startedAt": now(), "sourceArchivesRead": False,
              "scope": "Completed-plan ownership audit, bounded SerializedFile17–23 external-table/whole-byte absence proof, text/meta rewrite and work-tree promotion. Binary bytes unchanged.",
              "products": [], "recovered": 0, "stillBlocked": 0}
    text_extensions = PATH_TEXT_EXT | SERIALIZED | JSON_UNITY | {".meta", ".json", ".txt", ".md", ".yaml", ".yml", ".xml"}
    for index, original_product in enumerate(manifest["products"]):
        if original_product.get("status") != "blocked-binary-guid-collision":
            continue
        product = copy.deepcopy(original_product)
        identifier = str(product["id"])
        outcome = {"id": identifier, "status": "blocked", "binaryProofs": []}
        mutations = []
        moved_folder = moved_meta = False
        source_folder = source_meta = destination = destination_meta = None
        receipt_path = None
        journal = None
        try:
            source_work = Path(product["workDirectory"]).resolve()
            if not source_work.is_relative_to((work / "work").resolve()) or source_work == (work / "work").resolve():
                raise ValueError("Blocked work tree escaped task-owned extraction area")
            tree = source_work / "tree"
            source_folder = contained(tree, product["folder"])
            source_meta = contained(tree, product["folder"] + ".meta")
            destination = contained(stage, product["folder"])
            destination_meta = contained(stage, product["folder"] + ".meta")
            if not source_folder.is_dir() or not source_meta.is_file() or destination.exists() or destination_meta.exists():
                raise ValueError("Blocked source/staging paths are incomplete or destination exists; preserve for inspection")
            metadata, local_guids, binary_paths = [], {}, []
            for record in product["files"]:
                path = contained(tree, record["path"])
                if not path.is_file() or path.stat().st_size != record["bytes"] or hash_file(path) != record["sha256"]:
                    raise ValueError(f"Blocked work-tree bytes differ from receipt: {record['path']}")
                if path.suffix.lower() == ".meta":
                    guid = meta_guid(path)
                    if guid in local_guids:
                        raise ValueError(f"Ambiguous duplicate original GUID inside blocked product: {guid}")
                    local_guids[guid] = record["path"]
                    metadata.append((record, guid))
                else:
                    with path.open("rb") as source:
                        prefix = source.read(256)
                    if not text_kind(path, prefix):
                        looks_serialized = path.suffix.lower() in SERIALIZED
                        if len(prefix) >= 20:
                            candidate_version = struct.unpack(">I", prefix[8:12])[0]
                            declared_size = struct.unpack(">I", prefix[4:8])[0]
                            if candidate_version >= 22 and len(prefix) >= 48:
                                declared_size = struct.unpack(">q", prefix[24:32])[0]
                            looks_serialized = looks_serialized or (candidate_version in range(17, 24)
                                and declared_size == record["bytes"] and prefix[16] in (0, 1))
                        if looks_serialized:
                            binary_paths.append(record)
            remaps = dict(product.get("guidRemaps", {}))
            used = set(owners) | set(local_guids)
            assigned = set()
            for record, guid in metadata:
                desired = remaps.get(guid, guid)
                if desired in owners or desired in assigned or (desired != guid and desired in local_guids):
                    salt = 0
                    while True:
                        desired = hashlib.sha256(f"YamyamAssetLibrary/recovery/v1/{identifier}/{record['path']}/{guid}/{salt}".encode()).hexdigest()[:32]
                        if desired not in used:
                            break
                        salt += 1
                    remaps[guid] = desired
                if desired != guid:
                    used.add(desired)
                assigned.add(desired)
                if desired in owners:
                    raise ValueError(f"Recovery final GUID still collides: {desired}")
            for record in binary_paths:
                proof = binary_absence_proof(contained(tree, record["path"]), remaps, record["sha256"])
                outcome["binaryProofs"].append({"path": record["path"], **proof})
                if not proof["collidedGuidsAbsent"]:
                    raise ValueError(f"Actual collided GUID occurs in binary; retain blocked: {record['path']}")
            binary_names = {record["path"] for record in binary_paths}
            for record in product["files"]:
                if record["path"] in binary_names:
                    continue
                path = contained(tree, record["path"])
                with path.open("rb") as source:
                    header = source.read(4096)
                if not text_kind(path, header) and path.suffix.lower() not in text_extensions:
                    continue
                data = path.read_bytes()
                if b"\0" in data:
                    raise ValueError(f"Non-text bytes in a reference-bearing text asset; retain blocked: {record['path']}")
                changed = TOKEN.sub(lambda match: remaps.get(match.group(1).decode().lower(), match.group(1).decode()).encode(), data)
                if changed != data:
                    mutations.append({"path": path, "relative": record["path"], "before": data, "after": changed})
                    record.update(bytes=len(changed), sha256=hashlib.sha256(changed).hexdigest(),
                                  guidReferencesRewritten=True, binaryGuidRecoveryRewrite=True)
                if record.get("guid") in remaps:
                    record["originalGuid"], record["guid"] = record["guid"], remaps[record["guid"]]
            # Persist original changed text bytes before any mutation; no source re-decode needed.
            journal_root = work / "recovery-journals" / (identifier + "-" + uuid.uuid4().hex)
            journal_root.mkdir(parents=True)
            journal = journal_root / "journal.json"
            for change in mutations:
                backup = contained(journal_root, "before/" + change["relative"])
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup.write_bytes(change["before"])
            save_json(journal, {"id": identifier, "state": "prepared", "sourceTree": str(tree), "stage": str(stage),
                                "changedPaths": [change["relative"] for change in mutations], "binaryProofs": outcome["binaryProofs"]})
            for change in mutations:
                temporary = change["path"].with_name(change["path"].name + ".recovery-" + uuid.uuid4().hex + ".tmp")
                temporary.write_bytes(change["after"])
                os.replace(temporary, change["path"])
            # Both absolute source and destination were checked under the owned work/stage roots.
            folder_move = rename_owned_with_retry(source_folder, destination, tree, stage); moved_folder = True
            metadata_move = rename_owned_with_retry(source_meta, destination_meta, tree, stage); moved_meta = True
            product.update(status="complete", guidRemaps=remaps, binaryGuidRecoveryAt=now(),
                           originalBinaryGuidCollisionBlockers=product.get("binaryGuidCollisionBlockers", []),
                           binaryGuidCollisionBlockers=[], binaryGuidRecoveryProofs=outcome["binaryProofs"],
                           recoveredFromWorkTree=str(tree), binaryGuidRecoveryMoveAttempts={"folder": folder_move, "metadata": metadata_move})
            receipt_path = contained(work / "receipts", identifier + ".json")
            save_json(receipt_path, product)
            manifest["products"][index] = product
            manifest["updatedAt"], manifest["summary"] = now(), summarize(manifest["products"])
            save_json(manifest_path, manifest)
            for record, guid in metadata:
                owners[remaps.get(guid, guid)] = {"owner": identifier, "path": record["path"]}
            save_json(journal, {"id": identifier, "state": "complete", "sourceTree": str(tree), "stage": str(stage),
                                "changedPaths": [change["relative"] for change in mutations], "binaryProofs": outcome["binaryProofs"]})
            outcome.update(status="complete", textFilesChanged=len(mutations), guidRemaps=remaps,
                           moveAttempts={"folder": folder_move, "metadata": metadata_move})
            report["recovered"] += 1
        except Exception as error:
            # Ordinary failures roll back source text and both moves. Abrupt-process
            # failures retain a prepared journal with original text bytes for review.
            if moved_meta and destination_meta.exists() and not source_meta.exists():
                rename_owned_with_retry(destination_meta, source_meta, stage, tree)
            if moved_folder and destination.exists() and not source_folder.exists():
                rename_owned_with_retry(destination, source_folder, stage, tree)
            for change in mutations:
                if change["path"].is_file():
                    change["path"].write_bytes(change["before"])
            manifest["products"][index] = original_product
            if receipt_path is not None:
                save_json(receipt_path, original_product)
                manifest["updatedAt"], manifest["summary"] = now(), summarize(manifest["products"])
                save_json(manifest_path, manifest)
            outcome["error"] = f"{type(error).__name__}: {error}"
            if journal is not None:
                save_json(journal, {"id": identifier, "state": "rolled-back", "error": outcome["error"]})
            report["stillBlocked"] += 1
        report["products"].append(outcome)
        print(f"Recovery {identifier}: {outcome['status']}" + (": " + outcome["error"] if outcome.get("error") else ""), flush=True)
    report["completedAt"] = now()
    save_json(work / "binary-guid-recovery.json", report)
    return report


def contained(root, relative):
    relative = str(relative).replace("\\", "/")
    pieces = PurePosixPath(relative).parts
    if not pieces or any(piece in ("..", ".") for piece in pieces) or PurePosixPath(relative).is_absolute():
        raise ValueError(f"Unsafe staging-relative path: {relative}")
    path = root.joinpath(*pieces).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve() or path.is_symlink():
        raise ValueError(f"Path escaped staging: {path}")
    return path


def text_kind(path, header):
    trimmed = header.lstrip(b"\xef\xbb\xbf \t\r\n")
    if trimmed.startswith((b"%YAML", b"--- !u!")):
        return "Unity-YAML-header"
    if path.suffix.lower() == ".meta":
        return "Unity-meta"
    if path.suffix.lower() in JSON_UNITY and trimmed.startswith((b"{", b"[")):
        return "Unity-JSON"
    return None


def original_path(value):
    """Canonicalize a literal Assets path without guessing traversal/URL encoding."""
    value = str(value).replace("\\/", "/").replace("\\", "/")
    pieces = value.split("/")
    if not pieces or pieces[0] != "Assets" or any(piece in (".", "..") for piece in pieces):
        return None
    if any("\0" in piece or ":" in piece for piece in pieces):
        return None
    return "/".join(piece for piece in pieces if piece)


def product_path_map(product, stage, target_root):
    """Use recorded original package pathnames, never an inferred vendor-name swap."""
    mapping = {"exact": {}, "folded": {}, "entries": [], "ambiguities": []}
    checked_pairs, target_info = set(), {}

    def inspect_target(relative):
        relative = str(relative).replace("\\", "/")
        if relative not in target_info:
            target = contained(stage, relative)
            target_info[relative] = (target, target.exists(), target.is_dir())
        return target_info[relative]

    def register(before, relative):
        before = original_path(before)
        if before in (None, "Assets"):
            return
        relative = str(relative).replace("\\", "/")
        pair = (before, relative)
        if pair in checked_pairs:
            return
        checked_pairs.add(pair)
        # This cache is local to a read-only map-construction pass. No source
        # path, directory or asset is created/moved while these facts are reused.
        _target, exists, directory = inspect_target(relative)
        if not exists:
            return
        after = target_root.rstrip("/") + "/" + str(relative).replace("\\", "/")
        entry = {"before": before, "after": after, "stageRelative": str(relative).replace("\\", "/"),
                 "directory": directory}
        # Distinct native GUID groups can legitimately need different suffixed
        # Windows filenames. Retain every original spelling; never pick an
        # arbitrary casefold winner or abort/exclude a product's assets.
        exact = mapping["exact"].setdefault(before, [])
        if not any(previous["after"] == after for previous in exact):
            exact.append(entry)
            mapping["entries"].append(entry)
        folded = mapping["folded"].setdefault(before.casefold(), [])
        if not any(previous["before"] == before and previous["after"] == after for previous in folded):
            folded.append(entry)

    for record in product.get("files", []):
        origin = record.get("source", {})
        if origin.get("kind") not in {"unitypackage", "archive-unitypackage"}:
            continue
        before = original_path(origin.get("originalPath", ""))
        if before is None or before == "Assets":
            continue
        relative = record["path"]
        if relative.lower().endswith(".meta"):
            related = relative[:-5]
            _related_path, _exists, directory = inspect_target(related)
            if directory:
                register(before, related)
            else:
                register(before + ".meta", relative)
            continue
        register(before, relative)
        # Exporters can omit folder metadata. Derive parent correspondences only
        # from an actual asset's original pathname and existing staged parents.
        old_parts = before.split("/")
        new_parts = str(relative).replace("\\", "/").split("/")
        for depth in range(2, len(old_parts)):
            parent_before = "/".join(old_parts[:depth])
            remove = len(old_parts) - depth
            parent_after = "/".join(new_parts[:-remove])
            register(parent_before, parent_after)
    for original, entries in mapping["folded"].items():
        targets = sorted({entry["after"] for entry in entries})
        if len(targets) > 1:
            mapping["ambiguities"].append({"casefoldPath": original,
                "originalSpellings": sorted({entry["before"] for entry in entries}), "candidateTargets": targets})
    mapping["cacheStats"] = {"validatedTargets": len(target_info), "registeredPairs": len(checked_pairs)}
    return mapping


def repair_path_references(data, mapping, stage, target_root, yaml=False):
    changes, unresolved = [], []
    target_prefix = target_root.rstrip("/") + "/"

    def replacement(raw, quote=b'"'):
        try:
            decoded = raw.decode("utf-8")
            # JSON's escaped slash/unicode spelling can be decoded per literal,
            # without reparsing/reformatting an entire ShaderGraph file.
            if quote == b'"' and "\\" in decoded:
                try:
                    decoded = json.loads('"' + decoded + '"')
                except (json.JSONDecodeError, ValueError):
                    pass  # C# verbatim strings/shader paths use different escapes.
            before = original_path(decoded)
            if before is None:
                unresolved.append({"path": decoded, "reason": "Unsafe/traversing/noncanonical Assets pathname; left unchanged."})
                return raw
            if before == "Assets":
                return raw
            if before == target_root or before.startswith(target_prefix):
                return raw  # Already relocated: makes retries strictly idempotent.
            exact = mapping["exact"].get(before)
            candidates = exact if exact is not None else mapping["folded"].get(before.casefold(), [])
            targets = {candidate["after"] for candidate in candidates}
            if len(targets) > 1:
                unresolved.append({"path": decoded,
                    "reason": "Ambiguous original Assets pathname; exact spelling has multiple targets." if exact is not None else
                              "Ambiguous casefold Assets pathname; no unique exact-spelling target.",
                    "candidateTargets": sorted(targets)})
                return raw
            entry = candidates[0] if len(targets) == 1 else None
            if entry:
                after = entry["after"]
                if decoded.endswith(("/", "\\")):
                    if not entry["directory"]:
                        return raw
                    after += "/"
            else:
                # A valid directory prefix can support a whole path only when
                # that exact resulting file/directory already exists in staging.
                after = None
                directories = [candidate for candidate in mapping["entries"] if candidate["directory"] and
                               before.casefold().startswith((candidate["before"].rstrip("/") + "/").casefold())]
                if directories:
                    longest = max(len(candidate["before"]) for candidate in directories)
                    directories = [candidate for candidate in directories if len(candidate["before"]) == longest]
                    exact_directories = [candidate for candidate in directories if before.startswith(candidate["before"].rstrip("/") + "/")]
                    if exact_directories:
                        directories = exact_directories
                    targets = {candidate["after"] for candidate in directories}
                    if len(targets) > 1:
                        unresolved.append({"path": decoded, "reason": "Ambiguous original directory prefix; no unique target.",
                                           "candidateTargets": sorted(targets)})
                        return raw
                    candidate = directories[0]
                    prefix = candidate["before"].rstrip("/") + "/"
                    suffix = before[len(prefix):]
                    relative = candidate["stageRelative"].rstrip("/") + "/" + suffix
                    target = contained(stage, relative)
                    if target.exists():
                        after = candidate["after"].rstrip("/") + "/" + suffix
                        if decoded.endswith(("/", "\\")) and target.is_dir():
                            after += "/"
                if after is None:
                    unresolved.append({"path": decoded,
                                       "reason": "No unambiguous recorded original pathname or existing staged target; left unchanged."})
                    return raw
            if after == decoded:
                return raw
            changes.append({"before": decoded, "after": after})
            return after.encode("utf-8")
        except (UnicodeDecodeError, ValueError) as error:
            unresolved.append({"path": raw.decode("utf-8", errors="replace"), "reason": str(error)})
            return raw

    changed = PATH_LITERAL.sub(lambda match: match.group("quote") + replacement(match.group("path"), match.group("quote")) + match.group("quote"), data)
    changed = ANGLE_INCLUDE.sub(lambda match: match.group(1) + replacement(match.group(2)) + match.group(3), changed)
    if yaml:
        changed = YAML_PATH.sub(lambda match: match.group(1) + replacement(match.group(2)) + match.group(3), changed)
    unique_changes = list({(item["before"], item["after"]): item for item in changes}.values())
    unique_unresolved = list({(item["path"], item["reason"]): item for item in unresolved}.values())
    return changed, unique_changes, unique_unresolved


def scan_csharp(path, relative, product_id):
    data = path.read_bytes()
    encoding = "utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    try:
        source = data.decode(encoding)
    except UnicodeDecodeError:
        return {"path": relative, "productId": product_id, "error": "undecodable C# source"}
    namespaces = re.findall(r"^\s*namespace\s+([\w.]+)", source, re.M)
    types = re.findall(r"\b(?:class|struct|interface|enum|record)\s+([A-Za-z_]\w*)", source)
    usings = sorted(set(re.findall(r"^\s*using\s+(?:static\s+)?([\w.]+)\s*;", source, re.M)))
    markers = []
    asset_paths, resources_calls = [], []
    for number, line in enumerate(source.splitlines(), 1):
        for marker in AUTO_MARKERS + SIDE_EFFECT_MARKERS:
            if marker in line:
                markers.append({"line": number, "marker": marker, "text": line.strip()[:350]})
        for literal in re.findall(r'["\'](Assets/[^"\'\r\n]+)["\']', line):
            asset_paths.append({"line": number, "path": literal})
        if re.search(r"\bResources\s*\.\s*Load(?:All|Async)?\b", line):
            resources_calls.append({"line": number, "text": line.strip()[:350]})
    return {"path": relative, "productId": product_id, "namespaceDeclarations": namespaces,
            "declaredTypes": types, "usingNamespaces": usings,
            "isEditorPath": "editor" in [part.lower() for part in PurePosixPath(relative).parts[:-1]],
            "hasUnityEditorUsing": any(value == "UnityEditor" or value.startswith("UnityEditor.") for value in usings),
            "conditionalSymbols": sorted(set(re.findall(r"^\s*#(?:if|elif)\s+(.+)$", source, re.M))),
            "markers": markers,
            "assetPathLiterals": asset_paths, "resourcesLoadCalls": resources_calls,
            "typeScanLimit": "Lexical inventory includes nested/conditional declarations; candidate duplicates require compiler/context review."}


def summarize(products):
    return {"products": len(products), "complete": sum(p["status"] == "complete" for p in products),
            "blockedOrFailed": sum(p["status"] != "complete" for p in products),
            "files": sum(len(p.get("files", [])) for p in products),
            "bytes": sum(r["bytes"] for p in products for r in p.get("files", [])),
            "guidRemaps": sum(len(p.get("guidRemaps", {})) for p in products),
            "scripts": sum(len(p.get("scripts", [])) for p in products)}


def finalize(project, manifest_path=None, repair_only=None):
    project = Path(project).resolve()
    if not (project / "ProjectSettings/ProjectVersion.txt").is_file():
        raise ValueError("Expected an existing Unity project")
    work = project / "Library/YamyamAssetLibrary"
    manifest_path = Path(manifest_path).resolve() if manifest_path else work / "staging-manifest.json"
    if not manifest_path.is_relative_to(work.resolve()):
        raise ValueError("Manifest must be inside this project's Library/YamyamAssetLibrary")
    manifest = read_json(manifest_path)
    if repair_only is not None:
        repair_only = {value.strip() for value in repair_only.split(",")} if isinstance(repair_only, str) else {str(value).strip() for value in repair_only}
        repair_only.discard("")
        unknown = repair_only - {str(product["id"]) for product in manifest["products"]}
        if not repair_only or unknown:
            raise ValueError(f"--repair-only requires known nonempty product IDs; unknown: {sorted(unknown)}")
    target_root = manifest.get("targetAssetRoot", "Assets/ThirdParty/YamyamAssetLibrary").rstrip("/")
    if target_root != "Assets/ThirdParty/YamyamAssetLibrary":
        raise ValueError("Unexpected target asset root; refuse path rewriting outside the asset library")
    stage = Path(manifest["stageRoot"]).resolve()
    if not stage.is_relative_to(work.resolve()) or not stage.is_dir():
        raise ValueError("Staging root is missing or outside the task-owned Library directory")
    report = {"schemaVersion": 1, "startedAt": now(), "manifest": str(manifest_path),
              "scope": "Staged complete products only. No Assets/original/binary mutations. Header-based GUID repair and verified original-package-pathname relocation.",
              "changedFiles": [], "binaryReview": [], "skippedProducts": [], "errors": [],
              "assetPathChanges": [], "unresolvedAssetPaths": [],
              "scannedFiles": 0, "yamlFiles": 0, "metaFiles": 0, "jsonFiles": 0,
              "binaryAbsenceProofsReused": 0}
    report["repairOnly"] = sorted(repair_only) if repair_only is not None else None
    report["repairSkippedProducts"] = []
    code_report = {"schemaVersion": 1, "generatedAt": now(),
                   "scope": "Lexical C# dependency/type/automatic-Editor-execution inventory, not a compilation result.",
                   "scripts": [], "assemblies": [], "dlls": [], "duplicateTypeCandidates": [],
                   "shaderAssetPathLiterals": [], "existingProjectTypes": [],
                   "packageTypeCollisionCandidates": [], "ambiguousOriginalPaths": []}
    code_report["productsAudited"] = []
    code_report["auditScope"] = "C#/assembly/DLL and shader code inventory across every complete product, independent of --repair-only."
    type_owners = {}
    package_types = {}
    package_manifest = project / "Packages/manifest.json"
    if package_manifest.is_file():
        code_report["availableProjectPackages"] = read_json(package_manifest).get("dependencies", {})
    existing_inventory_path = work / "existing-code-inventory.json"
    if existing_inventory_path.is_file():
        existing_inventory = read_json(existing_inventory_path)
        code_report["existingProjectInventory"] = {"path": str(existing_inventory_path),
                                                    "method": existing_inventory.get("method"),
                                                    "generatedUtc": existing_inventory.get("generatedUtc")}
        for script in existing_inventory.get("scripts", []):
            relative = "existing-project/" + script["path"]
            for declaration in script.get("declarations", []):
                name = declaration["metadataFullName"]
                type_owners.setdefault(name, []).append(relative)
                code_report["existingProjectTypes"].append({"type": name, "path": relative})
        for assembly in existing_inventory.get("packageAssemblies", []):
            for name in assembly.get("types", []):
                package_types.setdefault(name, []).append(assembly["assembly"])
    else:
        # Small fallback for standalone fixture/reuse environments without Roslyn's inventory.
        for existing in (project / "Assets").rglob("*.cs"):
            if existing.is_symlink() or existing.is_relative_to(project / target_root):
                continue
            relative = "existing-project/" + existing.relative_to(project).as_posix()
            entry = scan_csharp(existing, relative, "existing-project")
            namespaces = entry.get("namespaceDeclarations", [])
            prefix = namespaces[0] + "." if len(namespaces) == 1 else ""
            for declared in entry.get("declaredTypes", []):
                name = prefix + declared
                type_owners.setdefault(name, []).append(relative)
                code_report["existingProjectTypes"].append({"type": name, "path": relative})
    for product in manifest["products"]:
        identifier = str(product["id"])
        if product.get("status") != "complete":
            report["skippedProducts"].append({"id": identifier, "status": product.get("status"),
                                              "binaryGuidCollisionBlockers": product.get("binaryGuidCollisionBlockers", []),
                                              "workDirectory": product.get("workDirectory")})
            continue
        remaps = {str(old).lower(): str(new).lower() for old, new in product.get("guidRemaps", {}).items()}
        repair_enabled = repair_only is None or identifier in repair_only
        path_map = None
        if repair_enabled:
            try:
                path_map = product_path_map(product, stage, target_root)
                code_report["ambiguousOriginalPaths"].extend({"productId": identifier, **entry} for entry in path_map["ambiguities"])
            except Exception as error:
                report["errors"].append({"productId": identifier, "error": f"Path-map construction: {error}"})
                continue
        else:
            report["repairSkippedProducts"].append(identifier)
        code_report["productsAudited"].append(identifier)
        changed_product = False
        binary_proofs = {proof["path"]: proof for proof in product.get("binaryGuidRecoveryProofs", [])}
        for record in product.get("files", []):
            relative = record["path"]
            if not repair_enabled and PurePosixPath(relative).suffix.lower() not in CODE_AUDIT_EXT:
                continue
            try:
                path = contained(stage, relative)
                if not path.is_file():
                    raise FileNotFoundError(path)
                if path.stat().st_size != record["bytes"]:
                    raise ValueError("File size differs from extraction receipt; preserve and inspect")
                report["scannedFiles"] += 1
                with path.open("rb") as source:
                    header = source.read(4096)
                kind = text_kind(path, header)
                if kind:
                    counter = {"Unity-YAML-header": "yamlFiles", "Unity-meta": "metaFiles", "Unity-JSON": "jsonFiles"}[kind]
                    report[counter] += 1
                guid_changed = False
                path_changes = []
                if repair_enabled and (kind or path.suffix.lower() in PATH_TEXT_EXT):
                    data = path.read_bytes()
                    if b"\0" in data:
                        if remaps and kind:
                            report["binaryReview"].append({"productId": identifier, "path": relative,
                                                           "reason": "Text/header file contains NUL; not modified", "blocking": True})
                        continue
                    changed = data
                    if remaps and kind:
                        # Replacement GUIDs come from the explicit product-local map.
                        changed = TOKEN.sub(lambda match: remaps.get(match.group(1).decode().lower(), match.group(1).decode()).encode(), data)
                        guid_changed = changed != data
                    changed, path_changes, unresolved = repair_path_references(
                        changed, path_map, stage, target_root, yaml=kind in {"Unity-YAML-header", "Unity-meta"})
                    for item in unresolved:
                        report["unresolvedAssetPaths"].append({"productId": identifier, "sourceFile": relative, **item})
                    if changed != data:
                        before_sha = hashlib.sha256(data).hexdigest()
                        if before_sha != record["sha256"]:
                            raise ValueError("File hash differs from extraction receipt; no overwrite")
                        temporary = path.with_name(path.name + ".guidrepair-" + uuid.uuid4().hex + ".tmp")
                        with temporary.open("xb") as output:
                            output.write(changed)
                        os.replace(temporary, path)
                        record["sha256"] = hashlib.sha256(changed).hexdigest()
                        record["bytes"] = len(changed)
                        if guid_changed:
                            record["guidReferencesRewritten"] = True
                            record["guidHeaderRepair"] = True
                        if path_changes:
                            record["assetPathReferencesRewritten"] = True
                            for item in path_changes:
                                report["assetPathChanges"].append({"productId": identifier, "path": relative, **item})
                        if path.suffix.lower() == ".meta":
                            match = GUID.search(changed[:65536])
                            if match:
                                record["guid"] = match.group(1).decode().lower()
                        report["changedFiles"].append({"productId": identifier, "path": relative, "kind": kind or "path-reference-text",
                                                        "guidRepair": guid_changed, "assetPathRepairs": len(path_changes),
                                                        "beforeSha256": before_sha, "afterSha256": record["sha256"]})
                        changed_product = True
                elif repair_enabled and remaps and path.suffix.lower() in SERIALIZED and not kind:
                    proof = binary_proofs.get(relative)
                    if (proof and proof.get("proofVersion") == BINARY_GUID_PROOF_VERSION
                            and proof.get("collidedGuidsAbsent") and not proof.get("binaryModified")
                            and proof.get("sha256After") == record["sha256"]
                            and proof.get("testedCollidedGuids") == sorted(remaps)
                            and hash_file(path) == record["sha256"]):
                        report["binaryAbsenceProofsReused"] += 1
                    else:
                        report["binaryReview"].append({"productId": identifier, "path": relative,
                            "reason": "Unity binary lacks a matching current GUID-absence proof; not modified", "blocking": True})
                if path.suffix.lower() == ".cs":
                    entry = scan_csharp(path, relative, identifier)
                    code_report["scripts"].append(entry)
                    namespaces = entry.get("namespaceDeclarations", [])
                    prefix = namespaces[0] + "." if len(namespaces) == 1 else ""
                    for declared in entry.get("declaredTypes", []):
                        name = prefix + declared
                        type_owners.setdefault(name, []).append(relative)
                        if name in package_types:
                            code_report["packageTypeCollisionCandidates"].append({"type": name, "path": relative,
                                                                                 "packageAssemblies": package_types[name]})
                elif path.suffix.lower() in {".asmdef", ".asmref"}:
                    try:
                        value = read_json(path)
                    except Exception as error:
                        value = {"parseError": str(error)}
                    code_report["assemblies"].append({"productId": identifier, "path": relative, "definition": value})
                elif path.suffix.lower() == ".dll":
                    code_report["dlls"].append({"productId": identifier, "path": relative, "sha256": record["sha256"]})
                elif path.suffix.lower() in {".shader", ".cginc", ".hlsl", ".compute", ".shadergraph", ".shadersubgraph"}:
                    data = path.read_bytes()
                    if b"\0" not in data[:8192]:
                        source = data.decode("utf-8-sig", errors="replace")
                        for number, line in enumerate(source.splitlines(), 1):
                            for literal in re.findall(r'["\'](Assets/[^"\'\r\n]+)["\']', line):
                                code_report["shaderAssetPathLiterals"].append({"productId": identifier,
                                    "path": relative, "line": number, "assetPath": literal,
                                    "existsAtOriginalProjectPath": (project / literal).exists(),
                                    "reason": "Product namespace relocation does not automatically rewrite shader include/path strings."})
            except Exception as error:
                report["errors"].append({"productId": identifier, "path": relative,
                                          "error": f"{type(error).__name__}: {error}"})
        if changed_product:
            product["guidHeaderRepairAt"] = now()
            product["assetPathRepairAt"] = now()
            receipt = work / "receipts" / (identifier + ".json")
            if not receipt.resolve().is_relative_to((work / "receipts").resolve()):
                raise ValueError("Unsafe product identifier for receipt")
            save_json(receipt, product)
            # Keep manifest in sync after each product, including partial interruption.
            manifest["updatedAt"] = now()
            manifest["summary"] = summarize(manifest["products"])
            save_json(manifest_path, manifest)
    code_report["duplicateTypeCandidates"] = [{"type": name, "paths": sorted(set(paths))}
                                               for name, paths in sorted(type_owners.items())
                                               if len(set(paths)) > 1 and any(not path.startswith("existing-project/") for path in paths)]
    code_report["automaticEditorExecutionScripts"] = [entry["path"] for entry in code_report["scripts"]
                                                      if any(marker["marker"] in AUTO_MARKERS for marker in entry.get("markers", []))]
    code_report["externalNamespaceCandidates"] = sorted({value for entry in code_report["scripts"]
                                                         for value in entry.get("usingNamespaces", [])
                                                         if not value.startswith(("System", "UnityEngine", "UnityEditor", "TMPro"))})
    code_report["summary"] = {"scripts": len(code_report["scripts"]), "assemblies": len(code_report["assemblies"]),
                              "dlls": len(code_report["dlls"]), "duplicateTypeCandidates": len(code_report["duplicateTypeCandidates"]),
                              "packageTypeCollisionCandidates": len(code_report["packageTypeCollisionCandidates"]),
                              "automaticEditorExecutionScripts": len(code_report["automaticEditorExecutionScripts"])}
    report["completedAt"] = now()
    report["status"] = "needs-review" if report["errors"] or report["binaryReview"] or report["skippedProducts"] or report["unresolvedAssetPaths"] else "complete"
    manifest["guidHeaderRepairReport"] = str(work / "guid-header-repair.json")
    manifest["codeAuditReport"] = str(work / "code-audit.json")
    manifest["updatedAt"] = now()
    manifest["summary"] = summarize(manifest["products"])
    save_json(manifest_path, manifest)
    save_json(work / "guid-header-repair.json", report)
    save_json(work / "code-audit.json", code_report)
    return report, code_report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--recover-blocked", action="store_true",
                        help="After every planned extraction receipt is terminal, recover binary-unrelated blocked work trees")
    parser.add_argument("--repair-only", help="Comma-separated product IDs for GUID/header/path repair; code/dependency audit still covers every complete product")
    args = parser.parse_args(argv)
    recovery = recover_blocked(args.project, args.manifest) if args.recover_blocked else None
    report, code = finalize(args.project, args.manifest, repair_only=args.repair_only)
    print(json.dumps({"status": report["status"], "scannedFiles": report["scannedFiles"],
                      "changedFiles": len(report["changedFiles"]), "binaryReview": len(report["binaryReview"]),
                      "assetPathChanges": len(report["assetPathChanges"]),
                      "unresolvedAssetPaths": len(report["unresolvedAssetPaths"]),
                      "skippedProducts": len(report["skippedProducts"]), "errors": len(report["errors"]),
                      "codeAudit": code["summary"], "recovery": {"recovered": recovery["recovered"],
                          "stillBlocked": recovery["stillBlocked"]} if recovery else None}), flush=True)
    return 1 if report["errors"] or report["binaryReview"] or (recovery and recovery["stillBlocked"]) else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    raise SystemExit(main())
