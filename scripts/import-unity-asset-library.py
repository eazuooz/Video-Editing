#!/usr/bin/env python3
"""Stage purchased asset downloads for a later, explicit Unity Editor import.

Only Library/YamyamAssetLibrary is written. Archives and Assets are read-only.
The original package GUIDs and importer metadata are retained unless a GUID
already belongs to another pack or to the existing project. No vendor code is
executed by this script.
"""
from __future__ import annotations

import argparse
import datetime as dt
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tarfile
import unicodedata
import uuid
import zipfile

VERSION = 1
TARGET_ROOT = "Assets/ThirdParty/YamyamAssetLibrary"
GUID = re.compile(rb"(?m)^guid:\s*([a-fA-F0-9]{32})\s*$")
TOKEN = re.compile(rb"(?<![a-fA-F0-9])([a-fA-F0-9]{32})(?![a-fA-F0-9])")
SERIALIZED = {".unity", ".prefab", ".asset", ".mat", ".anim", ".controller",
              ".overridecontroller", ".playable", ".mask", ".mixer",
              ".rendertexture", ".guiskin", ".lighting", ".flare", ".physicmaterial"}
# Raw raster sources have no vendor importer intent. Explicitly declare their
# ordinary2D shape: a GUID-only .meta was imported as Cubemap in Unity6000.6.
# DDS/HDR/EXR can be environment/array sources and retain their separate review.
RAW_RASTER_2D = {".png", ".jpg", ".jpeg", ".tga", ".tif", ".tiff", ".bmp", ".psd", ".gif"}
TEXT_EXT = SERIALIZED | {".meta", ".cs", ".shader", ".cginc", ".hlsl", ".compute",
                        ".json", ".asmdef", ".asmref", ".shadergraph", ".shadersubgraph",
                        ".vfx", ".vfxoperator", ".vfxblock", ".uss", ".uxml", ".txt",
                        ".md", ".yaml", ".yml", ".xml", ".inputactions"}
EXCLUDE_EXT = {".blend", ".blend1", ".blend2", ".godot", ".tscn", ".tres", ".gd",
               ".gdc", ".pck", ".csproj", ".sln", ".slnx", ".user", ".log",
               ".exe", ".msi", ".apk", ".aab", ".unitypackage", ".zip", ".7z",
               ".rar", ".tmp", ".ds_store"}
EXCLUDE_DIR = {"library", "temp", "obj", "logs", "usersettings", "projectsettings",
               "packages", ".git", ".godot", "build", "builds", "__macosx"}
RESERVED = re.compile(r"^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$", re.I)


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def sha_file(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(2 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def checked_child(root, path):
    root, path = Path(root).resolve(), Path(path).resolve()
    if path == root or not path.is_relative_to(root):
        raise ValueError(f"Path escaped task directory: {path}")
    return path


def remove_owned(root, path):
    # Validate the resolved absolute path before recursive deletion on Windows.
    target = checked_child(root, path)
    if target.exists():
        shutil.rmtree(target)


def parts_safe(value):
    value = str(value).replace("\\", "/")
    if value.startswith("/") or re.match(r"^[a-zA-Z]:", value):
        raise ValueError(f"Absolute archive pathname: {value}")
    parts = [p for p in value.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." or "\0" in p for p in parts):
        raise ValueError(f"Unsafe archive pathname: {value}")
    return parts


def win_segment(value):
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value).rstrip(" .") or "_"
    if RESERVED.match(value):
        value = "_" + value
    if len(value) > 135:
        suffix = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
        value = value[:120] + "_" + suffix
    return value


def folder_name(product):
    slug = unicodedata.normalize("NFKD", product["title"]).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug).strip("-").lower()[:78] or "asset-pack"
    return win_segment(str(product["id"])) + "-" + slug


def asset_relative(original, native=False):
    pieces = parts_safe(original)
    if native:
        if pieces[0].lower() != "assets":
            return None, "outside Assets (project/global settings excluded)"
        pieces = pieces[1:]
        if not pieces:
            return "", None
    if any(p.lower() in EXCLUDE_DIR for p in pieces[:-1]):
        return None, "project cache/build/other-engine directory"
    filename = pieces[-1].lower()
    effective_name = filename[:-5] if filename.endswith(".meta") else filename
    if Path(effective_name).suffix.lower() in EXCLUDE_EXT:
        return None, "non-Unity/authoring/archive/generated file"
    # Pipeline configuration is never installed into this project's global state.
    if ("globalsettings" in effective_name and effective_name.endswith(".asset")) or effective_name in {
        "urp.asset", "hdrp.asset", "graphicssettings.asset", "qualitysettings.asset",
        "universalrenderpipelineglobalsettings.asset", "hdrenderpipelineglobalsettings.asset"
    }:
        return None, "global render-pipeline configuration"
    return "/".join(win_segment(p) for p in pieces), None


def source_signature(product):
    inputs = []
    for source in product["selectedSources"]:
        source_path = Path(source.get("path") or source["archive"])
        info = source_path.stat()
        inputs.append({"path": str(source_path.resolve()), "bytes": info.st_size,
                       "mtimeNs": info.st_mtime_ns})
    payload = {"version": VERSION, "product": product, "inputs": inputs, "target": TARGET_ROOT}
    signature = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return signature, inputs


def stream_to_file(reader, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    count = 0
    with target.open("wb") as output:
        for chunk in iter(lambda: reader.read(2 * 1024 * 1024), b""):
            output.write(chunk)
            digest.update(chunk)
            count += len(chunk)
    return count, digest.hexdigest()


def extract_archive_members(archive, members, output):
    """Extract exactly the requested regular files; never trust archive paths."""
    archive, output = Path(archive), Path(output)
    requested = list(dict.fromkeys(members))
    for member in requested:
        parts_safe(member)
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as package:
            names = {}
            for info in package.infolist():
                names.setdefault(info.filename, []).append(info)
            for member in requested:
                matches = names.get(member, [])
                if len(matches) != 1:
                    raise ValueError(f"Missing/ambiguous archive member: {archive}: {member}")
                info = matches[0]
                mode = info.external_attr >> 16
                if info.is_dir() or stat.S_ISLNK(mode):
                    raise ValueError(f"Nonregular archive member: {member}")
                target = checked_child(output, output.joinpath(*parts_safe(member)))
                with package.open(info) as reader:
                    stream_to_file(reader, target)
    else:
        import py7zr
        with py7zr.SevenZipFile(archive, "r") as package:
            infos = {}
            for info in package.list():
                infos.setdefault(info.filename, []).append(info)
            for member in requested:
                matches = infos.get(member, [])
                if len(matches) != 1 or not matches[0].is_file or matches[0].is_symlink:
                    raise ValueError(f"Missing/ambiguous/nonregular 7z member: {member}")
            # py7zr also validates traversals; prevalidated selection contains no links.
            package.extract(path=output, targets=requested)
    result = {}
    for member in requested:
        path = checked_child(output, output.joinpath(*parts_safe(member)))
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Extraction did not produce a regular file: {member}")
        result[member] = path
    return result


def unpack_unitypackage(package, output):
    """Unity packages are streamed gzip/tar GUID directories, not filesystem paths."""
    groups = {}
    output.mkdir(parents=True, exist_ok=True)
    with tarfile.open(package, "r|*") as source:
        for member in source:
            if member.isdir():
                continue
            components = parts_safe(member.name)
            if len(components) != 2 or not re.fullmatch(r"[a-fA-F0-9]{32}", components[0]):
                continue  # package-level icons/metadata are not Unity assets
            guid, kind = components[0].lower(), components[1]
            if kind not in ("asset", "asset.meta", "pathname"):
                continue
            if not member.isfile():
                raise ValueError(f"Package contains a link/nonregular member: {member.name}")
            if kind == "pathname" and member.size > 65536:
                raise ValueError("Unreasonably large package pathname")
            group = groups.setdefault(guid, {})
            if kind in group:
                raise ValueError(f"Duplicate unitypackage member: {member.name}")
            reader = source.extractfile(member)
            if reader is None:
                raise ValueError(f"Cannot read unitypackage member: {member.name}")
            with reader:
                if kind == "pathname":
                    # At most 64 KiB, needed only for routing: avoid a temporary
                    # file and a second filesystem read for every Unity asset.
                    data = reader.read()
                    count, digest = len(data), hashlib.sha256(data).hexdigest()
                    group["originalPath"] = data.decode("utf-8-sig").rstrip("\0\r\n")
                    record = {"bytes": count, "sha256": digest}
                else:
                    target = checked_child(output, output / guid / kind)
                    if target.exists():
                        raise ValueError(f"Existing unitypackage member: {member.name}")
                    count, digest = stream_to_file(reader, target)
                    record = {"path": target, "bytes": count, "sha256": digest}
            if count != member.size:
                raise ValueError(f"Truncated unitypackage member: {member.name}")
            group[kind] = record
    for guid, group in groups.items():
        if "pathname" not in group:
            raise ValueError(f"Unity asset has no pathname: {guid}")
        group["archiveGuid"] = guid
    return groups


class PackWriter:
    def __init__(self, folder, tree, owned_root=None):
        if parts_safe(folder) != [folder]:
            raise ValueError(f"Unsafe product folder: {folder}")
        self.folder, self.tree = folder, Path(tree)
        self.owned_root = Path(owned_root).resolve() if owned_root is not None else None
        if self.owned_root is not None:
            checked_child(self.owned_root, self.tree)
        self.files, self.by_case, self.excluded, self.path_changes = {}, {}, [], []

    def exclude(self, original, reason, source):
        self.excluded.append({"originalPath": original, "reason": reason, "source": source})

    def put(self, relative, source_file, source, *, owned_move=False,
            known_digest=None, known_bytes=None):
        if relative:
            parts_safe(relative)
        target_rel = f"{self.folder}/{relative}" if relative else self.folder
        target = checked_child(self.tree, self.tree / PurePosixPath(target_rel))
        source_file = Path(source_file)
        if owned_move:
            if self.owned_root is None:
                raise ValueError("Moving a source requires an explicit owned product-work root")
            if source_file.is_symlink():
                raise ValueError(f"Cannot move a symlink: {source_file}")
            source_file = checked_child(self.owned_root, source_file)
            if source_file.is_relative_to(self.tree.resolve()):
                raise ValueError(f"Cannot move an already staged file: {source_file}")
        elif known_digest is not None or known_bytes is not None:
            raise ValueError("Known stream hashes are accepted only for owned extracted-file moves")
        count = source_file.stat().st_size
        if not source_file.is_file():
            raise ValueError(f"Not a regular source file: {source_file}")
        if known_digest is not None:
            if not re.fullmatch(r"[a-fA-F0-9]{64}", known_digest) or known_bytes != count:
                raise ValueError(f"Invalid/stale streamed hash or byte count: {source_file}")
            digest = known_digest.lower()
        else:
            if known_bytes is not None:
                raise ValueError("A known byte count requires its streamed SHA256")
            digest = sha_file(source_file)
        prior_key = self.by_case.get(target_rel.casefold())
        if prior_key:
            previous = self.files[prior_key]
            if previous["sha256"] != digest:
                raise ValueError(f"Conflicting duplicate destination (not overwritten): {target_rel}")
            previous.setdefault("duplicateSources", []).append(source)
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise ValueError(f"Unregistered destination exists (not overwritten): {target_rel}")
        if owned_move:
            # Source is an extracted regular file inside this product's work
            # directory, never a supplied archive or an existing project file.
            try:
                os.replace(source_file, target)
            except OSError as exc:
                if exc.errno != errno.EXDEV and getattr(exc, "winerror", None) != 17:
                    raise
                shutil.move(str(source_file), str(target))
        else:
            shutil.copyfile(source_file, target)
        self.files[target_rel] = {"path": target_rel, "bytes": count, "sha256": digest, "source": source}
        self.by_case[target_rel.casefold()] = target_rel

    def generated(self, relative, content):
        target_rel = f"{self.folder}/{relative}" if relative else self.folder + ".meta"
        if target_rel.casefold() in self.by_case:
            return
        target = self.tree / PurePosixPath(target_rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        data = content.encode()
        target.write_bytes(data)
        self.files[target_rel] = {"path": target_rel, "bytes": len(data),
                                  "sha256": hashlib.sha256(data).hexdigest(),
                                  "source": {"kind": "generated-stable-meta"}}
        self.by_case[target_rel.casefold()] = target_rel


def stable_guid(product_id, path, salt=""):
    return hashlib.sha256(f"YamyamAssetLibrary/v1/{product_id}/{path}/{salt}".encode()).hexdigest()[:32]


def ensure_metadata(writer, product_id):
    pack_root = writer.tree / writer.folder
    if not pack_root.exists():
        pack_root.mkdir(parents=True)
    # Add folder metadata before files so every copied asset has a stable identity.
    directories = [pack_root] + sorted((p for p in pack_root.rglob("*") if p.is_dir()), key=str)
    for directory in directories:
        relative = directory.relative_to(pack_root).as_posix()
        if relative == ".":
            relative = ""
            meta_rel = ""
        else:
            meta_rel = relative + ".meta"
        guid = stable_guid(product_id, relative + "/")
        writer.generated(meta_rel, f"fileFormatVersion: 2\nguid: {guid}\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n")
    originals = list(writer.files)
    for relative in originals:
        if relative.lower().endswith(".meta"):
            continue
        meta_path = relative + ".meta"
        if meta_path.casefold() not in writer.by_case:
            local = relative[len(writer.folder) + 1:] + ".meta"
            content = f"fileFormatVersion: 2\nguid: {stable_guid(product_id, relative)}\n"
            if PurePosixPath(relative).suffix.lower() in RAW_RASTER_2D:
                content += "TextureImporter:\n  externalObjects: {}\n  serializedVersion: 13\n  textureShape: 1\n"
            writer.generated(local, content)


def metadata_guid(path):
    # GUID is near the top even when sprite metadata is very large.
    with path.open("rb") as source:
        match = GUID.search(source.read(65536))
    return match.group(1).decode().lower() if match else None


def guid_registry(assets):
    owners = {}
    for meta in assets.rglob("*.meta"):
        if meta.is_symlink():
            continue
        guid = metadata_guid(meta)
        if guid:
            owners.setdefault(guid, {"owner": "existing-project", "path": str(meta)})
    return owners


def resolve_guids(writer, product_id, owners):
    pack_guids, remaps, collisions = {}, {}, []
    for relative, record in writer.files.items():
        if not relative.lower().endswith(".meta"):
            continue
        guid = metadata_guid(writer.tree / PurePosixPath(relative))
        if not guid:
            raise ValueError(f"Missing GUID in metadata: {relative}")
        if guid in pack_guids and pack_guids[guid] != relative:
            raise ValueError(f"Ambiguous repeated GUID within the same product: {guid}: {relative}")
        pack_guids[guid] = relative
        record["guid"] = guid
    for guid, relative in pack_guids.items():
        if guid in owners:
            replacement = stable_guid(product_id, relative, guid)
            salt = 0
            while replacement in owners or replacement in pack_guids or replacement in remaps.values():
                salt += 1
                replacement = stable_guid(product_id, relative, f"{guid}:{salt}")
            remaps[guid] = replacement
            collisions.append({"oldGuid": guid, "newGuid": replacement, "path": relative,
                               "previous": owners[guid]})
    binary_serialized = []
    for relative in writer.files:
        path = writer.tree / PurePosixPath(relative)
        if path.suffix.lower() in SERIALIZED:
            with path.open("rb") as stream:
                prefix = stream.read(256)
            if not prefix.lstrip(b"\xef\xbb\xbf \r\n\t").startswith((b"%YAML", b"--- !u!")):
                binary_serialized.append(relative)
    if remaps and binary_serialized:
        return remaps, collisions, binary_serialized
    if remaps:
        for relative, record in writer.files.items():
            path = writer.tree / PurePosixPath(relative)
            if path.suffix.lower() not in TEXT_EXT:
                continue
            data = path.read_bytes()
            # Never modify a binary blob just because it has a text-looking extension.
            if b"\0" in data[:8192]:
                raise ValueError(f"Binary file prevents safe GUID-reference rewriting: {relative}")
            changed = TOKEN.sub(lambda match: remaps.get(match.group(1).decode().lower(), match.group(1).decode()).encode(), data)
            if changed != data:
                path.write_bytes(changed)
                record["bytes"], record["sha256"] = len(changed), hashlib.sha256(changed).hexdigest()
                record["guidReferencesRewritten"] = True
            if record.get("guid") in remaps:
                record["originalGuid"], record["guid"] = record["guid"], remaps[record["guid"]]
    for guid, relative in pack_guids.items():
        owners[remaps.get(guid, guid)] = {"owner": product_id, "path": relative}
    return remaps, collisions, []


def allocate_native_paths(prepared):
    """Keep distinct Unity identities when exported paths collide on Windows.

    Decide asset and sidecar destinations together, before either is written.
    Equal pixels are insufficient grounds to merge different metadata GUIDs.
    """
    by_case, used, allocated = {}, set(), {}
    for selection, groups in prepared.items():
        for guid, group in groups.items():
            relative, reason = asset_relative(group["originalPath"], native=True)
            if reason or not relative:
                continue
            by_case.setdefault(relative.casefold(), []).append((selection, guid, relative, group))
            used.update((relative.casefold(), (relative + ".meta").casefold()))
    for key in sorted(by_case):
        entries = by_case[key]
        if len({entry[1] for entry in entries}) < 2:
            continue
        for _, _, _, group in entries:
            meta = group.get("asset.meta")
            if meta and b"folderAsset: yes" in meta["path"].read_bytes()[:8192]:
                raise ValueError("Distinct folder GUIDs share a Windows path; child ownership is ambiguous: " + group["originalPath"])
        for guid in sorted({entry[1] for entry in entries}):
            identities = [entry for entry in entries if entry[1] == guid]
            original = min(entry[2] for entry in identities)
            path = PurePosixPath(original)
            attempt = 0
            while True:
                marker = f"__guid_{guid}" + (f"_{attempt}" if attempt else "")
                budget = 135 - len(marker) - len(path.suffix)
                if budget < 1:
                    raise ValueError(f"Cannot safely suffix colliding asset filename: {original}")
                name = path.stem[:budget] + marker + path.suffix
                destination = path.with_name(name).as_posix()
                if destination.casefold() not in used and (destination + ".meta").casefold() not in used:
                    break
                attempt += 1
            used.update((destination.casefold(), (destination + ".meta").casefold()))
            for selection, _, _, _ in identities:
                allocated[(selection, guid)] = destination
    return allocated


def build_product(product, work, owners):
    folder = folder_name(product)
    tree = work / "tree"
    tree.mkdir(parents=True)
    writer = PackWriter(folder, tree, owned_root=work)
    prepared = {}
    # Preflight all native asset identities before moving any payload. This also
    # handles collisions spanning multiple selected Unity packages in one pack.
    for number, selection in enumerate(product["selectedSources"]):
        kind = selection["kind"]
        if kind in ("unitypackage", "archive-unitypackage"):
            area = work / f"source-{number:02d}"
            package = Path(selection["path"]) if kind == "unitypackage" else extract_archive_members(
                selection["archive"], [selection["member"]], area / "outer")[selection["member"]]
            prepared[number] = unpack_unitypackage(package, area / "unpacked")
    allocated = allocate_native_paths(prepared)
    for number, selection in enumerate(product["selectedSources"]):
        area = work / f"source-{number:02d}"
        kind = selection["kind"]
        if kind in ("unitypackage", "archive-unitypackage"):
            groups = prepared[number]
            for group in groups.values():
                original = group["originalPath"]
                origin = {"kind": kind, "package": str(selection.get("path") or selection["archive"]),
                          "packageMember": selection.get("member"), "originalPath": original,
                          "originalGuid": group["archiveGuid"]}
                relative, reason = asset_relative(original, native=True)
                if reason:
                    writer.exclude(original, reason, origin)
                    continue
                relocated = allocated.get((number, group["archiveGuid"]))
                if relocated is not None:
                    relative = relocated
                    writer.path_changes.append({"original": original, "destination": relative,
                                                "guid": group["archiveGuid"],
                                                "reason": "distinct-native-guids-share-windows-path"})
                elif relative != "/".join(parts_safe(original)[1:]):
                    writer.path_changes.append({"original": original, "destination": relative})
                meta = group.get("asset.meta")
                is_folder = bool(meta and b"folderAsset: yes" in meta["path"].read_bytes()[:8192])
                if is_folder:
                    (tree / folder / relative).mkdir(parents=True, exist_ok=True)
                elif "asset" in group:
                    payload = group["asset"]
                    writer.put(relative, payload["path"], origin, owned_move=True,
                               known_digest=payload["sha256"], known_bytes=payload["bytes"])
                else:
                    writer.exclude(original, "package entry has no asset and is not a folder", origin)
                    continue
                if meta:
                    if relative:
                        writer.put(relative + ".meta", meta["path"], origin, owned_move=True,
                                   known_digest=meta["sha256"], known_bytes=meta["bytes"])
                    else:
                        # Unity's Assets root GUID must not replace our product root.
                        writer.exclude(original, "package Assets-root metadata replaced by product folder metadata", origin)
        elif kind in ("archive-files", "nested-archive-files"):
            archive = Path(selection["archive"])
            if kind == "nested-archive-files":
                archive = extract_archive_members(archive, [selection["member"]], area / "outer")[selection["member"]]
            extracted = extract_archive_members(archive, selection["members"], area / "files")
            for original, source_file in extracted.items():
                origin = {"kind": kind, "archive": str(selection["archive"]),
                          "nestedMember": selection.get("member"), "originalPath": original}
                relative, reason = asset_relative(original)
                if reason:
                    writer.exclude(original, reason, origin)
                    continue
                writer.put(relative, source_file, origin, owned_move=True)
        else:
            raise ValueError(f"Unsupported source kind: {kind}")
    if not any(not path.lower().endswith(".meta") for path in writer.files):
        raise ValueError("Selected sources contain no usable Unity asset files")
    ensure_metadata(writer, str(product["id"]))
    remaps, collisions, binary_blockers = resolve_guids(writer, str(product["id"]), owners)
    scripts = [r["path"] for r in writer.files.values() if Path(r["path"]).suffix.lower() in {".cs", ".dll", ".asmdef", ".asmref"}]
    return tree, {"folder": folder, "files": list(writer.files.values()), "excluded": writer.excluded,
                  "guidRemaps": remaps, "guidCollisions": collisions, "scripts": scripts,
                  "pathChanges": writer.path_changes, "binaryGuidCollisionBlockers": binary_blockers}


def receipt_files_valid(receipt, root):
    """Reuse existing extraction evidence only for contained, size-matching files.

    Like completed-staging resume, this deliberately does not rehash unchanged
    payloads. The receipt already contains the hashes produced during extraction.
    """
    records, folder = receipt.get("files"), receipt.get("folder")
    if not records or not folder:
        return False
    try:
        if parts_safe(folder) != [folder]:
            return False
        for record in records:
            relative = record["path"]
            if relative != folder + ".meta" and not relative.startswith(folder + "/"):
                return False
            candidate = Path(root).joinpath(*parts_safe(relative))
            if candidate.is_symlink():
                return False
            path = checked_child(root, candidate)
            if not path.is_file() or path.stat().st_size != record["bytes"]:
                return False
        return True
    except (KeyError, TypeError, ValueError, OSError):
        return False


def resume_valid(receipt, signature, stage):
    return (receipt.get("status") == "complete" and receipt.get("inputSignature") == signature
            and receipt_files_valid(receipt, stage))


def resume_blocked_valid(receipt, signature, work_root):
    if (receipt.get("status") != "blocked-binary-guid-collision"
            or receipt.get("inputSignature") != signature or not receipt.get("workDirectory")):
        return False
    try:
        work = checked_child(work_root, receipt["workDirectory"])
        tree = checked_child(work, work / "tree")
        return work.is_dir() and tree.is_dir() and receipt_files_valid(receipt, tree)
    except (TypeError, ValueError, OSError):
        return False


def update_summary(manifest):
    products = manifest["products"]
    manifest["updatedAt"] = now()
    manifest["summary"] = {
        "products": len(products),
        "complete": sum(p["status"] == "complete" for p in products),
        "blockedOrFailed": sum(p["status"] != "complete" for p in products),
        "files": sum(len(p.get("files", [])) for p in products),
        "bytes": sum(r["bytes"] for p in products for r in p.get("files", [])),
        "guidRemaps": sum(len(p.get("guidRemaps", {})) for p in products),
        "scripts": sum(len(p.get("scripts", [])) for p in products)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--only", help="Comma-separated product IDs, for a small verification run")
    args = parser.parse_args(argv)
    project = args.project.resolve()
    if not (project / "Assets").is_dir() or not (project / "ProjectSettings/ProjectVersion.txt").is_file():
        parser.error("--project must point to the intended existing Unity project")
    plan = read_json(args.plan)
    base = project / "Library/YamyamAssetLibrary"
    stage = base / "staging/CreatorBundle"
    stage.mkdir(parents=True, exist_ok=True)
    receipts = base / "receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    work_root = base / "work"
    work_root.mkdir(parents=True, exist_ok=True)
    manifest_path = base / "staging-manifest.json"
    manifest = {"schemaVersion": VERSION, "generatedAt": now(), "plan": str(args.plan.resolve()),
                "project": str(project), "stageRoot": str(stage), "targetAssetRoot": TARGET_ROOT,
                "originalsPreserved": True, "actualAssetsModified": False, "products": []}
    owners = guid_registry(project / "Assets")
    only = set(args.only.split(",")) if args.only else None
    selected = [p for p in plan["sets"] if only is None or str(p["id"]) in only]
    # An --only retry updates one result without erasing other terminal evidence.
    # Blocked/failed products do not reserve GUID ownership until staged complete.
    for receipt_path in receipts.glob("*.json"):
        receipt = read_json(receipt_path)
        status = receipt.get("status", "")
        if (only and str(receipt.get("id")) not in only
                and (status in {"complete", "failed"} or status.startswith("blocked"))):
            manifest["products"].append(receipt)
            if receipt.get("status") == "complete":
                for record in receipt.get("files", []):
                    if record.get("guid"):
                        owners[record["guid"]] = {"owner": receipt["id"], "path": record["path"]}
    failed = 0
    for position, product in enumerate(selected, 1):
        identifier = str(product["id"])
        receipt_path = receipts / (win_segment(identifier) + ".json")
        result = {"id": identifier, "index": product["index"], "title": product["title"],
                  "sourceUrl": product.get("sourceUrl"), "sourceDirectory": product["sourceDirectory"],
                  "folder": folder_name(product), "startedAt": now(), "status": "failed"}
        result["assetPath"] = TARGET_ROOT + "/" + result["folder"]
        work = None
        try:
            signature, inputs = source_signature(product)
            if receipt_path.is_file():
                previous = read_json(receipt_path)
                if resume_valid(previous, signature, stage):
                    result = previous
                    for record in result["files"]:
                        if record.get("guid"):
                            owners[record["guid"]] = {"owner": identifier, "path": record["path"]}
                    print(f"[{position}/{len(selected)}] {identifier} resumed: {len(result['files'])} files", flush=True)
                    manifest["products"].append(result)
                    update_summary(manifest)
                    save_json(manifest_path, manifest)
                    continue
                if resume_blocked_valid(previous, signature, work_root):
                    # Keep the original blocker, collision evidence and work
                    # directory. Binary collisions are not resolved by retrying
                    # decompression, and their GUIDs were never registered by
                    # resolve_guids() on the original blocked return path.
                    result = previous
                    failed += 1
                    print(f"[{position}/{len(selected)}] {identifier} resumed blocked: {len(result['files'])} files", flush=True)
                    manifest["products"].append(result)
                    update_summary(manifest)
                    save_json(manifest_path, manifest)
                    continue
                if previous.get("status") == "complete":
                    raise ValueError("Existing completed staging differs from inputs/files; preserve it and review before replacement")
            result.update(inputSignature=signature, inputs=inputs)
            work = work_root / f"{identifier}-{uuid.uuid4().hex}"
            checked_child(work_root, work).mkdir()
            tree, details = build_product(product, work, owners)
            result.update(details)
            if details["binaryGuidCollisionBlockers"]:
                result["status"] = "blocked-binary-guid-collision"
                result["workDirectory"] = str(work)
                failed += 1
            else:
                destination = stage / details["folder"]
                if destination.exists() or destination.with_name(destination.name + ".meta").exists():
                    raise ValueError(f"Unreceipted staging already exists; no overwrite: {destination}")
                shutil.move(str(tree / details["folder"]), str(destination))
                root_meta = tree / (details["folder"] + ".meta")
                shutil.move(str(root_meta), str(stage / root_meta.name))
                result["status"] = "complete"
                remove_owned(work_root, work)
                work = None
            result["completedAt"] = now()
            save_json(receipt_path, result)
            print(f"[{position}/{len(selected)}] {identifier} {result['status']}: {len(details['files'])} files; {len(details['guidRemaps'])} GUID remaps", flush=True)
        except Exception as exc:
            failed += 1
            result.update(status="failed", error=f"{type(exc).__name__}: {exc}", completedAt=now())
            if work is not None:
                result["workDirectory"] = str(work)
            save_json(receipt_path, result)
            print(f"[{position}/{len(selected)}] {identifier} FAILED: {exc}", flush=True)
        manifest["products"].append(result)
        update_summary(manifest)
        save_json(manifest_path, manifest)
    print(json.dumps({"manifest": str(manifest_path), "summary": manifest.get("summary", {}), "failuresThisRun": failed}), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    raise SystemExit(main())
