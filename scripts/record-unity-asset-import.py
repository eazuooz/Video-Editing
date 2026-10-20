#!/usr/bin/env python3
"""Record the quiescent, actual Unity asset library after normal Editor exit.

The canonical manifest supplies the actual root (stageRoot), which can be the
owned headless project's Assets directory. Assets are read-only. The default
hashes every file once; optional fingerprints reuse unchanged payload hashes.
Metadata is always hashed. Bookkeeping writes follow complete validation.
No archive is opened, no vendor code executes, and no Git data is accessed.
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
import stat
import sys
import uuid

TARGET = "Assets/ThirdParty/YamyamAssetLibrary"
GUID = re.compile(rb"(?m)^guid:[ \t]*([a-fA-F0-9]{32})[ \t]*\r?$")
ARCHIVES = {".zip", ".7z", ".rar", ".unitypackage", ".tar", ".gz", ".tgz", ".bz2", ".xz"}
REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
CACHE_VERSION = 1
SHA = re.compile(r"^[a-f0-9]{64}$")


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def encoded_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")


def read_json_bytes(path):
    data = Path(path).read_bytes()
    return json.loads(data.decode("utf-8-sig")), data


def write_json_atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".record-" + uuid.uuid4().hex + ".tmp")
    with temporary.open("xb") as output:
        output.write(encoded_json(value))
    os.replace(temporary, path)


def is_link(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & REPARSE)


def relative_parts(value):
    value = str(value).replace("\\", "/")
    parts = PurePosixPath(value).parts
    if (not parts or value.startswith("/") or re.match(r"^[A-Za-z]:", value)
            or any(part in (".", "..", "") or "\0" in part or ":" in part for part in parts)):
        raise ValueError(f"Unsafe manifest-relative path: {value}")
    return parts


def owned_file(root, relative):
    parts = relative_parts(relative)
    path = root.joinpath(*parts)
    resolved = path.resolve()
    if resolved == root.resolve() or not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Path escaped its explicitly owned directory: {path}")
    return path


def no_links_below(path, boundary):
    """Check literal path components before resolving any ownership boundary."""
    path, boundary = Path(path).absolute(), Path(boundary).absolute()
    if path != boundary and not path.is_relative_to(boundary):
        raise ValueError(f"Path is outside its literal ownership boundary: {path}")
    for current in (path, *path.parents):
        if os.path.lexists(current) and is_link(current.lstat()):
            raise ValueError(f"Owned path traverses a symlink/reparse point: {current}")
        if current == boundary:
            return
    raise ValueError(f"Ownership boundary was not reached: {path}")


def root_allowed(project, root):
    literal = Path(root).absolute()
    work = (project / "Library/YamyamAssetLibrary").absolute()
    main_root = (project / TARGET).absolute()
    if literal != main_root and (literal == work or not literal.is_relative_to(work)):
        raise ValueError("Actual root must be this library's main Assets root or its owned Library workspace")
    no_links_below(literal, project)
    resolved = literal.resolve()
    if not resolved.is_dir():
        raise ValueError("Actual library root is not a directory")
    return resolved


def inventory(root, product_by_folder, errors):
    """List regular files without following any links; no asset contents read."""
    rows, spellings = {}, {}
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                key = relative.casefold()
                previous = spellings.get(key)
                if previous is not None:
                    errors.append({"kind": "casefold-collision", "path": relative, "otherPath": previous})
                    continue
                spellings[key] = relative
                # On Windows DirEntry.stat reports zero st_ino/st_dev while
                # Path.lstat reports the real identity. Use one API consistently
                # so the post-read identity comparison detects actual changes.
                info = path.lstat()
                if is_link(info):
                    errors.append({"kind": "symlink-or-reparse-point", "path": relative})
                    continue
                parts = relative_parts(relative)
                if any(part.casefold() == ".git" for part in parts):
                    errors.append({"kind": "unexpected-git-path", "path": relative})
                    continue
                first = parts[0]
                owner = product_by_folder.get(first.casefold())
                if stat.S_ISDIR(info.st_mode):
                    if owner is None:
                        errors.append({"kind": "unowned-directory", "path": relative})
                    else:
                        pending.append(path)
                    continue
                if not stat.S_ISREG(info.st_mode):
                    errors.append({"kind": "nonregular-file", "path": relative})
                    continue
                if path.suffix.lower() in ARCHIVES:
                    errors.append({"kind": "unexpected-archive-file-not-read", "path": relative})
                    continue
                if owner is None and len(parts) == 1 and first.lower().endswith(".meta"):
                    owner = product_by_folder.get(first[:-5].casefold())
                if owner is None:
                    errors.append({"kind": "unowned-file", "path": relative})
                    continue
                rows[key] = {"path": relative, "absolutePath": path, "statBefore": info,
                             "productId": str(owner["id"])}
    return rows


def hash_actual_file(path, before):
    """One complete read computes SHA and captures metadata's near-top GUID."""
    digest, prefix = hashlib.sha256(), bytearray()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(2 * 1024 * 1024), b""):
            digest.update(chunk)
            if len(prefix) < 65536:
                prefix.extend(chunk[:65536 - len(prefix)])
    after = path.lstat()
    identity = lambda info: (info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_ino, info.st_dev)
    if is_link(after) or not stat.S_ISREG(after.st_mode) or identity(before) != identity(after):
        raise ValueError("File changed identity/size/mtime during recording; normal Unity exit is required")
    record = {"bytes": after.st_size, "sha256": digest.hexdigest()}
    if path.suffix.lower() == ".meta":
        match = GUID.search(prefix)
        if not match:
            raise ValueError("Metadata has no canonical GUID near its header")
        record["guid"] = match.group(1).decode().lower()
    return record


def expected_guid(product, record):
    if record.get("guid"):
        return str(record["guid"]).lower()
    original = record.get("source", {}).get("originalGuid")
    return product.get("guidRemaps", {}).get(original, original) if original else None


def fingerprint(info):
    """Same literal lstat API at build/use time, including Windows file identity."""
    return {"size": info.st_size, "mtime_ns": info.st_mtime_ns,
            "ctime_ns": info.st_ctime_ns, "ino": info.st_ino, "dev": info.st_dev}


def cache_path_owned(project, path=None):
    work = project / "Library/YamyamAssetLibrary"
    path = Path(path).absolute() if path else work / "hash-reuse-cache.json"
    if path == work or not path.is_relative_to(work):
        raise ValueError("Hash cache must stay inside the owned library workspace")
    relative_parts(path.relative_to(work).as_posix())
    if path != work / "hash-reuse-cache.json" and not path.is_relative_to(work / "hash-caches"):
        raise ValueError("Custom sidecars must stay under the dedicated hash-caches directory")
    no_links_below(path, project)
    return path


def cache_layout(manifest):
    products = manifest.get("products", [])
    if not products or any(product.get("status") != "complete" for product in products):
        raise ValueError("Hash cache requires all complete products")
    folders, identifiers, expected = {}, set(), {}
    for product in products:
        identifier = str(product["id"])
        parts = relative_parts(product["folder"])
        if len(parts) != 1 or identifier in identifiers or parts[0].casefold() in folders:
            raise ValueError("Hash cache product IDs/folders must be unique")
        identifiers.add(identifier)
        folders[parts[0].casefold()] = product
        if not product.get("files"):
            raise ValueError("Complete cache product lacks provenance")
        for record in product["files"]:
            record_parts = relative_parts(record["path"])
            first = record_parts[0].casefold()
            if not (first == parts[0].casefold() or len(record_parts) == 1 and first == (parts[0] + ".meta").casefold()):
                raise ValueError("Hash cache record escapes its product")
            key = "/".join(record_parts).casefold()
            if key in expected:
                raise ValueError("Hash cache contains casefold-duplicate provenance")
            expected[key] = (product, record)
    return folders, expected


def cache_canonical_record(product, record):
    value = {"productId": str(product["id"]), "path": record["path"],
             "bytes": record["bytes"], "sha256": record["sha256"]}
    guid = expected_guid(product, record) if record["path"].lower().endswith(".meta") else record.get("guid")
    if guid:
        value["guid"] = str(guid).lower()
    if not isinstance(value["bytes"], int) or isinstance(value["bytes"], bool) or value["bytes"] < 0 or not SHA.fullmatch(str(value["sha256"])):
        raise ValueError("Invalid canonical hash/size for cache entry")
    return value


def validate_full_delta(delta, manifest_sha, root, expected_files):
    root_meta_count = 1 if delta.get("rootMeta") else 0
    covered = delta.get("hashedFiles", 0)
    if delta.get("hashMode") == "recovered-complete-scan":
        evidence = delta.get("recoveredCompleteScan", {})
        if (not SHA.fullmatch(str(evidence.get("scanSha256", "")))
                or not SHA.fullmatch(str(evidence.get("beforeManifestSha256", "")))
                or evidence.get("validatedFileCoverage") != expected_files + root_meta_count
                or evidence.get("priorHashedFiles") != expected_files + root_meta_count):
            raise ValueError("Recovered baseline lacks complete immutable FULL-scan coverage proof")
        covered += delta.get("recoveredScanFiles", 0)
    if (delta.get("status") != "complete" or delta.get("bookkeepingCommitted") is not True
            or delta.get("afterManifestSha256") != manifest_sha
            or str(Path(delta.get("actualRoot", "")).absolute()).casefold() != str(root).casefold()
            or delta.get("assetRootFiles") != expected_files
            or delta.get("reusedHashFiles", 0) != 0
            or covered != expected_files + root_meta_count):
        raise ValueError("Cache baseline requires a successful matching FULL recorder delta")


def immutable_snapshot(project, path, data):
    no_links_below(path, project)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Immutable recorder evidence snapshot conflict")
    else:
        with path.open("xb") as output:
            output.write(data)


def validate_recovery_source(project, delta):
    if delta.get("hashMode") != "recovered-complete-scan":
        return
    evidence = delta.get("recoveredCompleteScan", {})
    digest = str(evidence.get("scanSha256", ""))
    if not SHA.fullmatch(digest):
        raise ValueError("Invalid immutable recovered full-scan digest")
    directory = project / "Library/YamyamAssetLibrary/completed-scan-recovery" / digest
    values = []
    for field, filename, digest_field in (("scanPath", "failed-scan.json", "scanSha256"),
                                           ("beforeManifestPath", "before-manifest.json", "beforeManifestSha256")):
        path = directory / filename
        if Path(evidence.get(field, "")).absolute() != path:
            raise ValueError("Recovered full-scan evidence path differs from immutable owned location")
        no_links_below(path, project)
        value, data = read_json_bytes(path)
        if hashlib.sha256(data).hexdigest() != evidence.get(digest_field):
            raise ValueError("Recovered full-scan evidence snapshot digest changed")
        values.append(value)
    prior, original = values
    _folders, old = cache_layout(original)
    if (prior.get("status") != "validation-failed" or prior.get("bookkeepingCommitted") is not False
            or prior.get("beforeManifestSha256") != evidence.get("beforeManifestSha256")
            or prior.get("hashedFiles") != evidence.get("priorHashedFiles")
            or prior.get("hashedBytes") != evidence.get("priorHashedBytes")
            or prior.get("reusedHashFiles", 0) != 0
            or prior.get("hashMode", "full") != "full"
            or len(old) + (1 if prior.get("rootMetaChange") else 0) != evidence.get("validatedFileCoverage")):
        raise ValueError("Recovered immutable prior scan is not the proved complete FULL pass")


def load_completed_scan(project, path, manifest_path, manifest_bytes, root, expected, actual):
    """Adopt only a fully traversed scan refused for unchanged unknown-GUID meta.

    Payloads newer than that scan's start are freshly hashed instead. Every meta
    is freshly hashed by the caller; this function never substitutes GUID data.
    """
    work = project / "Library/YamyamAssetLibrary"
    path = Path(path).absolute()
    if path == work or not path.is_relative_to(work):
        raise ValueError("Completed scan evidence must stay in the owned workspace")
    relative_parts(path.relative_to(work).as_posix())
    no_links_below(path, project)
    prior, prior_bytes = read_json_bytes(path)
    scan_sha = hashlib.sha256(prior_bytes).hexdigest()
    directory = work / "completed-scan-recovery" / scan_sha
    # Preserve the input even if a later guard refuses adoption and replaces
    # final-import-delta.json with the new refusal report.
    immutable_snapshot(project, directory / "failed-scan.json", prior_bytes)
    before_sha = hashlib.sha256(manifest_bytes).hexdigest()
    if (prior.get("schemaVersion") != 1 or prior.get("status") != "validation-failed"
            or prior.get("failure") != "ValueError: Post-hash file/GUID validation failed"
            or prior.get("bookkeepingCommitted") is not False or prior.get("assetsModifiedByRecorder") is not False
            or prior.get("sourceArchivesRead") is not False or prior.get("gitDataAccessed") is not False
            or prior.get("beforeManifestSha256") != before_sha
            or Path(prior.get("manifest", "")).absolute() != manifest_path
            or Path(prior.get("actualRoot", "")).absolute() != root
            or prior.get("hashMode", "full") != "full" or prior.get("reusedHashFiles", 0) != 0
            or prior.get("newFiles") != [] or prior.get("pathSpellingChanges") != []
            or "uncommittedManifestSha256" in prior or "afterManifestSha256" in prior):
        raise ValueError("Evidence is not the exact unchanged-canonical completed FULL failed scan")
    started = dt.datetime.fromisoformat(prior["startedAt"])
    completed = dt.datetime.fromisoformat(prior["completedAt"])
    if started.tzinfo is None or completed.tzinfo is None or completed < started:
        raise ValueError("Completed scan timestamps are invalid")
    started_ns = int(started.timestamp() * 1_000_000_000)
    allowed_errors = prior.get("errors")
    if not isinstance(allowed_errors, list) or not allowed_errors:
        raise ValueError("Recovery requires explicit unchanged missing-stored-GUID errors")
    error_keys = set()
    for error in allowed_errors:
        key = "/".join(relative_parts(error.get("path", ""))).casefold()
        if error.get("kind") != "old-meta-guid-unavailable" or key not in expected or key in error_keys:
            raise ValueError("Completed scan has a nonrecoverable/duplicate error")
        product, record = expected[key]
        if str(error.get("productId")) != str(product["id"]) or not record["path"].lower().endswith(".meta") or expected_guid(product, record):
            raise ValueError("Recovery error does not identify unknown stored-GUID metadata")
        error_keys.add(key)
    derived = {}
    for key, (product, old) in expected.items():
        derived[key] = {"bytes": old["bytes"], "sha256": old["sha256"]}
    changes = prior.get("changedFiles")
    if not isinstance(changes, list):
        raise ValueError("Completed scan changed-file evidence missing")
    changed_keys = set()
    for change in changes:
        key = "/".join(relative_parts(change.get("path", ""))).casefold()
        if key not in expected or key in changed_keys or key in error_keys:
            raise ValueError("Completed scan delta is duplicate, unowned or changes unknown-GUID metadata")
        product, old = expected[key]
        if (str(change.get("productId")) != str(product["id"]) or change["path"] != old["path"]
                or change.get("beforeSha256") != old["sha256"] or change.get("beforeBytes") != old["bytes"]
                or change.get("source") != old.get("source")
                or change.get("kind") != ("importer-metadata" if old["path"].lower().endswith(".meta") else "post-import-content")
                or not SHA.fullmatch(str(change.get("afterSha256", "")))
                or type(change.get("afterBytes")) is not int or change["afterBytes"] < 0):
            raise ValueError("Completed scan delta conflicts with exact original provenance")
        derived[key] = {"bytes": change["afterBytes"], "sha256": change["afterSha256"]}
        changed_keys.add(key)
    meta_path = root.with_name(root.name + ".meta")
    root_change = prior.get("rootMetaChange")
    root_count = 1 if os.path.lexists(meta_path) else 0
    if bool(root_change) != bool(root_count):
        raise ValueError("Root metadata presence differs from completed full scan")
    if root_count:
        if (not isinstance(root_change, dict) or not SHA.fullmatch(str(root_change.get("afterSha256", "")))
                or type(root_change.get("afterBytes")) is not int or root_change["afterBytes"] < 0
                or not re.fullmatch(r"[a-f0-9]{32}", str(root_change.get("guid", "")))):
            raise ValueError("Completed scan root metadata evidence invalid")
    byte_coverage = sum(row["bytes"] for row in derived.values()) + (root_change["afterBytes"] if root_count else 0)
    if (set(actual) != set(expected) or prior.get("hashedFiles") != len(actual) + root_count
            or prior.get("hashedBytes") != byte_coverage):
        raise ValueError("Completed full scan lacks exact original/current file and byte coverage")
    for key, row in actual.items():
        if row["path"] != expected[key][1]["path"]:
            raise ValueError("Actual file spelling changed since original complete scan")
        # A changed stamp/size is not trusted; only that payload will be re-read.
        derived[key]["eligible"] = (row["statBefore"].st_size == derived[key]["bytes"]
            and max(row["statBefore"].st_mtime_ns, row["statBefore"].st_ctime_ns) <= started_ns)
    snapshots = ((directory / "failed-scan.json", prior_bytes), (directory / "before-manifest.json", manifest_bytes))
    for target, data in snapshots:
        immutable_snapshot(project, target, data)
    evidence = {"scanPath": str(snapshots[0][0]), "scanSha256": scan_sha,
                "beforeManifestPath": str(snapshots[1][0]), "beforeManifestSha256": before_sha,
                "startedAt": prior["startedAt"], "completedAt": prior["completedAt"],
                "priorHashedFiles": prior["hashedFiles"], "priorHashedBytes": prior["hashedBytes"],
                "validatedFileCoverage": len(actual) + root_count,
                "validatedByteCoverage": byte_coverage, "allowedMissingGuidErrors": allowed_errors,
                "policy": "Reconstructed canonical plus exact full-scan deltas; payloads newer than prior scan start rehashed; all metadata rehashed; final installer hashes all payloads."}
    return derived, evidence


def build_hash_cache(project, manifest_path=None, hash_cache=None):
    """Capture stamps after a full pass while writers stay stopped.

    This local hint is not an integrity proof. The installer hashes every
    payload independently. A timestamp later than the baseline is refused.
    """
    project = Path(project).resolve()
    if not (project / "ProjectSettings/ProjectVersion.txt").is_file():
        raise ValueError("--project must identify the original Unity project")
    work = project / "Library/YamyamAssetLibrary"
    manifest_path = Path(manifest_path).absolute() if manifest_path else work / "staging-manifest.json"
    if manifest_path == work or not manifest_path.is_relative_to(work):
        raise ValueError("Canonical manifest must stay in the owned workspace")
    relative_parts(manifest_path.relative_to(work).as_posix())
    no_links_below(manifest_path, project)
    manifest, manifest_bytes = read_json_bytes(manifest_path)
    if manifest.get("targetAssetRoot", TARGET) != TARGET:
        raise ValueError("Unexpected target asset root")
    root = root_allowed(project, manifest["stageRoot"])
    folders, expected = cache_layout(manifest)
    delta_path = work / "final-import-delta.json"
    no_links_below(delta_path, project)
    delta, delta_bytes = read_json_bytes(delta_path)
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    validate_full_delta(delta, manifest_sha, root, len(expected))
    validate_recovery_source(project, delta)
    completed_ns = int(dt.datetime.fromisoformat(delta["completedAt"]).timestamp() * 1_000_000_000)
    if completed_ns <= 0:
        raise ValueError("Invalid full recorder completion time")
    errors = []
    actual = inventory(root, folders, errors)
    if errors or set(actual) != set(expected):
        raise ValueError("Cache build requires exact fully owned baseline inventory")
    entries = []
    for key, row in sorted(actual.items()):
        product, record = expected[key]
        info = row["statBefore"]
        canonical = cache_canonical_record(product, record)
        if info.st_size != record["bytes"] or max(info.st_mtime_ns, info.st_ctime_ns) > completed_ns:
            raise ValueError("File changed after full recorder baseline: " + row["path"])
        entries.append({**canonical, "path": row["path"], "fingerprint": fingerprint(info)})
    root_meta = manifest.get("assetRootMeta")
    meta_path = root.with_name(root.name + ".meta")
    if bool(root_meta) != os.path.lexists(meta_path):
        raise ValueError("Root metadata presence changed after full recording")
    root_meta_entry = None
    if root_meta:
        no_links_below(meta_path, project)
        info = meta_path.lstat()
        if is_link(info) or not stat.S_ISREG(info.st_mode) or info.st_size != root_meta["bytes"] or max(info.st_mtime_ns, info.st_ctime_ns) > completed_ns:
            raise ValueError("Root metadata changed after full recording")
        root_meta_entry = {**root_meta, "fingerprint": fingerprint(info)}
    for product in manifest["products"]:
        receipt = owned_file(work / "receipts", str(product["id"]) + ".json")
        no_links_below(receipt, project)
        if read_json_bytes(receipt)[0] != product:
            raise ValueError("Receipt differs from baseline canonical product")
    cache_path = cache_path_owned(project, hash_cache)
    baseline = work / "hash-cache-baselines" / manifest_sha
    snapshots = ((baseline / "manifest.json", manifest_bytes), (baseline / "delta.json", delta_bytes))
    for path, data in snapshots:
        no_links_below(path, project)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if path.read_bytes() != data:
                raise ValueError("Immutable cache baseline snapshot conflict")
        else:
            with path.open("xb") as output:
                output.write(data)
    if manifest_path.read_bytes() != manifest_bytes or delta_path.read_bytes() != delta_bytes:
        raise ValueError("Bookkeeping changed during hash cache build")
    cache = {"schemaVersion": CACHE_VERSION, "status": "cache-built", "builtAt": utc(),
             "project": str(project), "actualRoot": str(root), "targetAssetRoot": TARGET,
             "sourceManifestSha256": manifest_sha, "sourceDeltaSha256": hashlib.sha256(delta_bytes).hexdigest(),
             "sourceManifestSnapshot": str(snapshots[0][0]), "sourceDeltaSnapshot": str(snapshots[1][0]),
             "baselineCompletedAt": delta["completedAt"], "entries": entries, "rootMeta": root_meta_entry,
             "policy": "Strict malformed/root/baseline rejection; mismatched current record/fingerprint hashes normally. Metadata always rehashed. Requires quiescent writers; final installer always fully hashes."}
    write_json_atomic(cache_path, cache)
    return {"status": "cache-built", "cachePath": str(cache_path), "entries": len(entries),
            "sourceManifestSha256": manifest_sha, "sourceDeltaSha256": cache["sourceDeltaSha256"],
            "assetBytesRead": 0, "actualRoot": str(root)}


def load_hash_cache(project, path, root):
    path = cache_path_owned(project, path)
    cache, cache_bytes = read_json_bytes(path)
    if (cache.get("schemaVersion") != CACHE_VERSION or cache.get("status") != "cache-built"
            or str(cache.get("project", "")).casefold() != str(project).casefold()
            or str(cache.get("actualRoot", "")).casefold() != str(root).casefold()
            or cache.get("targetAssetRoot") != TARGET):
        raise ValueError("Hash cache schema/project/actual root mismatch")
    baseline = project / "Library/YamyamAssetLibrary/hash-cache-baselines" / str(cache.get("sourceManifestSha256", ""))
    snapshots = []
    for field, name, sha_field in (("sourceManifestSnapshot", "manifest.json", "sourceManifestSha256"),
                                  ("sourceDeltaSnapshot", "delta.json", "sourceDeltaSha256")):
        if not SHA.fullmatch(str(cache.get(sha_field, ""))):
            raise ValueError("Invalid cache baseline digest")
        expected_path = baseline / name
        if Path(cache.get(field, "")).absolute() != expected_path:
            raise ValueError("Hash cache snapshot must be its immutable owned baseline")
        no_links_below(expected_path, project)
        value, data = read_json_bytes(expected_path)
        if hashlib.sha256(data).hexdigest() != cache[sha_field]:
            raise ValueError("Hash cache baseline snapshot digest mismatch")
        snapshots.append(value)
    manifest, delta = snapshots
    if str(manifest.get("stageRoot", "")).casefold() != str(root).casefold():
        raise ValueError("Hash cache baseline root mismatch")
    _folders, expected = cache_layout(manifest)
    validate_full_delta(delta, cache["sourceManifestSha256"], root, len(expected))
    validate_recovery_source(project, delta)
    rows = {}
    if not isinstance(cache.get("entries"), list):
        raise ValueError("Hash cache entries must be a list")
    for row in cache["entries"]:
        key = "/".join(relative_parts(row["path"])).casefold()
        if key in rows or key not in expected:
            raise ValueError("Hash cache has duplicate or unowned entry")
        product, record = expected[key]
        canonical = cache_canonical_record(product, record)
        if any(row.get(field) != canonical.get(field) for field in ("productId", "bytes", "sha256", "guid")):
            raise ValueError("Hash cache entry conflicts with immutable baseline provenance")
        stamps = row.get("fingerprint")
        if not isinstance(stamps, dict) or set(stamps) != {"size", "mtime_ns", "ctime_ns", "ino", "dev"} or any(type(value) is not int or value < 0 for value in stamps.values()) or stamps["size"] != row["bytes"]:
            raise ValueError("Malformed cache fingerprint")
        rows[key] = row
    if set(rows) != set(expected):
        raise ValueError("Hash cache baseline entry coverage differs")
    return rows, {"path": str(path), "sha256": hashlib.sha256(cache_bytes).hexdigest(),
                  "sourceManifestSha256": cache["sourceManifestSha256"], "sourceDeltaSha256": cache["sourceDeltaSha256"]}


def reused_hash(row, old, product, cache):
    """Return cached digest only for one unchanged, already-owned payload."""
    if row["absolutePath"].suffix.lower() == ".meta" or old is None or cache is None:
        return None
    canonical = cache_canonical_record(product, old)
    if any(cache.get(field) != canonical.get(field) for field in ("productId", "bytes", "sha256", "guid")):
        return None
    if fingerprint(row["statBefore"]) != cache["fingerprint"]:
        return None
    if not cache["fingerprint"]["ino"] or not cache["fingerprint"]["dev"]:
        return None  # No reusable identity if this filesystem reports placeholders.
    after = row["absolutePath"].lstat()
    if is_link(after) or not stat.S_ISREG(after.st_mode) or fingerprint(after) != cache["fingerprint"]:
        raise ValueError("Cached payload changed identity/stamps during recording")
    return {"bytes": canonical["bytes"], "sha256": canonical["sha256"]}


def transaction(outputs):
    """Atomic replacement per JSON with rollback if any later replacement fails."""
    prepared, replaced = [], []
    try:
        for path, value in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            old_bytes = path.read_bytes() if path.is_file() else None
            temporary = path.with_name(path.name + ".record-" + uuid.uuid4().hex + ".tmp")
            with temporary.open("xb") as output:
                output.write(encoded_json(value))
            prepared.append((path, temporary, old_bytes))
        for path, temporary, old_bytes in prepared:
            os.replace(temporary, path)
            replaced.append((path, old_bytes))
    except Exception:
        for path, old_bytes in reversed(replaced):
            if old_bytes is None:
                path.unlink()
            else:
                restore = path.with_name(path.name + ".restore-" + uuid.uuid4().hex + ".tmp")
                restore.write_bytes(old_bytes)
                os.replace(restore, path)
        raise
    finally:
        for _path, temporary, _old_bytes in prepared:
            if temporary.is_file():
                temporary.unlink()


def record_import(project, manifest_path=None, reuse_unchanged_cache=False, hash_cache=None, recover_completed_scan=None):
    project = Path(project).resolve()
    if not (project / "ProjectSettings/ProjectVersion.txt").is_file():
        raise ValueError("--project must point to the original Unity project")
    work = project / "Library/YamyamAssetLibrary"
    manifest_path = Path(manifest_path).absolute() if manifest_path else work / "staging-manifest.json"
    if manifest_path == work.resolve() or not manifest_path.is_relative_to(work.resolve()):
        raise ValueError("Canonical manifest must stay inside this library's owned workspace")
    no_links_below(manifest_path, project)
    no_links_below(work / "receipts", project)
    original, manifest_bytes = read_json_bytes(manifest_path)
    manifest = copy.deepcopy(original)
    errors = []
    report = {"schemaVersion": 1, "startedAt": utc(), "status": "validating", "manifest": str(manifest_path),
              "beforeManifestSha256": hashlib.sha256(manifest_bytes).hexdigest(), "assetsModifiedByRecorder": False,
              "bookkeepingCommitted": False,
              "sourceArchivesRead": False, "gitDataAccessed": False,
              "scope": "Actual-root inventory after Unity exit. Existing file presence/GUIDs and complete product ownership required before bookkeeping writes; optional fingerprint reuse is a local hint and final installer fully hashes.",
              "changedFiles": [], "newFiles": [], "pathSpellingChanges": [], "errors": errors,
              "hashedFiles": 0, "hashedBytes": 0, "reusedHashFiles": 0, "reusedHashBytes": 0,
              "hashMode": "recovered-complete-scan" if recover_completed_scan else "validated-fingerprint-reuse" if reuse_unchanged_cache else "full",
              "recoveredScanFiles": 0, "recoveredScanBytes": 0, "recoveryRehashedFiles": [], "adoptedUnknownMetaGuids": []}
    delta_path = work / "final-import-delta.json"
    try:
        if manifest.get("targetAssetRoot", TARGET) != TARGET:
            raise ValueError("Unexpected target asset root")
        root = root_allowed(project, manifest["stageRoot"])
        report["actualRoot"] = str(root)
        products = manifest.get("products", [])
        if not products or any(product.get("status") != "complete" for product in products):
            raise ValueError("Every manifest product must be complete before final recording")
        by_id, by_folder, expected = {}, {}, {}
        for product in products:
            identifier = str(product["id"])
            folder_parts = relative_parts(product["folder"])
            if len(folder_parts) != 1 or identifier in by_id or folder_parts[0].casefold() in by_folder:
                raise ValueError("Product IDs/folders must be unique single-component names")
            by_id[identifier], by_folder[folder_parts[0].casefold()] = product, product
            if not product.get("files"):
                raise ValueError(f"Complete product has no existing file provenance: {identifier}")
            receipt = owned_file(work / "receipts", identifier + ".json")
            no_links_below(receipt, project)
            for old in product.get("files", []):
                parts = relative_parts(old["path"])
                first = parts[0].casefold()
                if not (first == folder_parts[0].casefold() or len(parts) == 1 and first == (folder_parts[0] + ".meta").casefold()):
                    raise ValueError(f"Old record is not owned by its product: {old['path']}")
                key = "/".join(parts).casefold()
                if key in expected:
                    raise ValueError(f"Duplicate Windows-casefold record in canonical manifest: {old['path']}")
                expected[key] = (product, old)
        actual = inventory(root, by_folder, errors)
        for key, (product, old) in expected.items():
            if key not in actual:
                errors.append({"kind": "missing-old-file", "productId": str(product["id"]), "path": old["path"]})
        if errors:
            raise ValueError("Pre-hash inventory validation failed")
        cached_rows = {}
        recovered_rows = {}
        if reuse_unchanged_cache:
            cached_rows, report["hashReuseCache"] = load_hash_cache(project, hash_cache, root)
        if recover_completed_scan:
            if reuse_unchanged_cache:
                raise ValueError("Completed-scan recovery and fingerprint reuse are separate modes")
            recovered_rows, report["recoveredCompleteScan"] = load_completed_scan(
                project, recover_completed_scan, manifest_path, manifest_bytes, root, expected, actual)
        owners = {}
        actual_root_meta = None
        root_meta = root.with_name(root.name + ".meta")
        if os.path.lexists(root_meta):
            info = root_meta.lstat()
            if is_link(info) or not stat.S_ISREG(info.st_mode):
                errors.append({"kind": "invalid-library-root-meta", "path": str(root_meta)})
            else:
                actual_root_meta = {"absolutePath": str(root_meta), **hash_actual_file(root_meta, info)}
                report["hashedFiles"] += 1
                report["hashedBytes"] += actual_root_meta["bytes"]
                if recover_completed_scan:
                    evidence, _bytes = read_json_bytes(Path(report["recoveredCompleteScan"]["scanPath"]))
                    prior_root = evidence["rootMetaChange"]
                    if any(actual_root_meta.get(current) != prior_root.get(prior) for current, prior in
                           (("sha256", "afterSha256"), ("bytes", "afterBytes"), ("guid", "guid"))):
                        raise ValueError("Root metadata differs from the completed full-scan proof")
                    report["recoveryRehashedFiles"].append({"path": str(root_meta), "reason": "root-metadata-guid-verification"})
                prior_meta = original.get("assetRootMeta")
                if isinstance(prior_meta, dict) and prior_meta.get("guid") != actual_root_meta["guid"]:
                    errors.append({"kind": "changed-library-root-meta-guid", "beforeGuid": prior_meta.get("guid"),
                                   "afterGuid": actual_root_meta["guid"], "path": str(root_meta)})
                owners[actual_root_meta["guid"]] = str(root_meta)
                report["rootMetaChange"] = {"beforeSha256": prior_meta.get("sha256") if isinstance(prior_meta, dict) else None,
                    "afterSha256": actual_root_meta["sha256"], "beforeBytes": prior_meta.get("bytes") if isinstance(prior_meta, dict) else None,
                    "afterBytes": actual_root_meta["bytes"], "guid": actual_root_meta["guid"],
                    "kind": "existing-root-metadata" if isinstance(prior_meta, dict) else "new-root-metadata"}
        elif original.get("assetRootMeta"):
            errors.append({"kind": "missing-library-root-meta", "path": str(root_meta)})
        files_by_product = {identifier: [] for identifier in by_id}
        for key, row in sorted(actual.items()):
            path = row["absolutePath"]
            try:
                previous = expected.get(key)
                recovered = recovered_rows.get(key)
                current = None
                if recovered is not None and recovered["eligible"] and path.suffix.lower() != ".meta":
                    after = path.lstat()
                    if is_link(after) or not stat.S_ISREG(after.st_mode) or fingerprint(after) != fingerprint(row["statBefore"]):
                        raise ValueError("Completed-scan payload changed while validating inventory")
                    current = {"bytes": recovered["bytes"], "sha256": recovered["sha256"]}
                    report["recoveredScanFiles"] += 1
                    report["recoveredScanBytes"] += current["bytes"]
                elif not recover_completed_scan:
                    current = reused_hash(row, previous[1] if previous else None,
                                          previous[0] if previous else None, cached_rows.get(key))
                if current is None:
                    current = hash_actual_file(path, row["statBefore"])
                    report["hashedFiles"] += 1
                    report["hashedBytes"] += current["bytes"]
                    if recover_completed_scan:
                        report["recoveryRehashedFiles"].append({"path": row["path"],
                            "reason": "metadata-guid-verification" if path.suffix.lower() == ".meta" else "newer-than-prior-scan-start-or-size-changed"})
                elif not recover_completed_scan:
                    report["reusedHashFiles"] += 1
                    report["reusedHashBytes"] += current["bytes"]
                guid = current.get("guid")
                if guid:
                    if guid in owners:
                        errors.append({"kind": "duplicate-actual-guid", "path": row["path"], "otherPath": owners[guid], "guid": guid})
                    else:
                        owners[guid] = row["path"]
                if previous:
                    product, old = previous
                    record = copy.deepcopy(old)
                    if row["productId"] != str(product["id"]):
                        errors.append({"kind": "changed-product-ownership", "path": row["path"]})
                    if path.suffix.lower() == ".meta":
                        before_guid = expected_guid(product, old)
                        if not before_guid:
                            if old["sha256"] == current["sha256"] and old["bytes"] == current["bytes"]:
                                proof = {"kind": "unchanged-exact-canonical-bytes", "sha256": current["sha256"],
                                         "bytes": current["bytes"], "guid": guid}
                                record["guidPreservationEvidence"] = proof
                                report["adoptedUnknownMetaGuids"].append({"productId": row["productId"], "path": row["path"], **proof})
                            else:
                                errors.append({"kind": "old-meta-guid-unavailable", "productId": row["productId"], "path": old["path"]})
                        elif before_guid.lower() != guid:
                            errors.append({"kind": "changed-old-meta-guid", "productId": row["productId"], "path": old["path"],
                                           "beforeGuid": before_guid, "afterGuid": guid})
                    if old["path"] != row["path"]:
                        report["pathSpellingChanges"].append({"productId": row["productId"], "beforePath": old["path"], "afterPath": row["path"]})
                    if old["sha256"] != current["sha256"] or old["bytes"] != current["bytes"]:
                        change = {"productId": row["productId"], "path": row["path"], "beforeSha256": old["sha256"],
                                  "afterSha256": current["sha256"], "beforeBytes": old["bytes"], "afterBytes": current["bytes"],
                                  "kind": "importer-metadata" if path.suffix.lower() == ".meta" else "post-import-content",
                                  "source": old.get("source")}
                        report["changedFiles"].append(change)
                        record["postImportChange"] = {"recordedAt": utc(), "beforeSha256": old["sha256"], "beforeBytes": old["bytes"]}
                else:
                    record = {"source": {"kind": "observed-new-after-unity-import", "productId": row["productId"],
                        "productSourceUrl": by_id[row["productId"]].get("sourceUrl"),
                        "purpose": "New file present under this existing product after Unity import; no specific generator is inferred."}}
                    report["newFiles"].append({"productId": row["productId"], "path": row["path"], **current,
                                               "source": record["source"]})
                record.update(path=row["path"], **current)
                files_by_product[row["productId"]].append(record)
            except Exception as error:
                errors.append({"kind": "actual-file-read-error", "path": row["path"], "error": f"{type(error).__name__}: {error}"})
        if errors:
            raise ValueError("Post-hash file/GUID validation failed")
        stamp = utc()
        outputs = []
        for identifier, product in by_id.items():
            product["files"] = files_by_product[identifier]
            product["finalImportRecordedAt"] = stamp
            product["finalImportActualRoot"] = str(root)
            product["finalImportFileCount"] = len(product["files"])
            product["scripts"] = [record["path"] for record in product["files"]
                                  if PurePosixPath(record["path"]).suffix.lower() in {".cs", ".dll", ".asmdef", ".asmref"}]
            receipt = owned_file(work / "receipts", identifier + ".json")
            outputs.append((receipt, product))
        manifest["assetRootMeta"] = actual_root_meta
        manifest["updatedAt"] = stamp
        manifest["finalImportRecordedAt"] = stamp
        manifest["finalImportDeltaReport"] = str(delta_path)
        summary = manifest.setdefault("summary", {})
        summary.update(products=len(products), complete=len(products), blockedOrFailed=0,
                       files=len(actual), bytes=sum(record["bytes"] for records in files_by_product.values() for record in records),
                       scripts=sum(len(product["scripts"]) for product in products))
        report.update(status="complete", completedAt=stamp, products=len(products), assetRootFiles=len(actual),
                      changedFileCount=len(report["changedFiles"]), newFileCount=len(report["newFiles"]), rootMeta=actual_root_meta,
                      newMaterials=sum(Path(record["path"]).suffix.lower() == ".mat" for record in report["newFiles"]),
                      newPrefabs=sum(Path(record["path"]).suffix.lower() == ".prefab" for record in report["newFiles"]),
                      newMetaFiles=sum(Path(record["path"]).suffix.lower() == ".meta" for record in report["newFiles"]))
        report["afterManifestSha256"] = hashlib.sha256(encoded_json(manifest)).hexdigest()
        report["bookkeepingCommitted"] = True
        outputs.extend(((manifest_path, manifest), (delta_path, report)))
        transaction(outputs)
    except Exception as error:
        report.update(status="validation-failed", completedAt=utc(), failure=f"{type(error).__name__}: {error}", bookkeepingCommitted=False)
        if "afterManifestSha256" in report:
            report["uncommittedManifestSha256"] = report.pop("afterManifestSha256")
        write_json_atomic(delta_path, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--hash-cache", type=Path, help="Owned-workspace cache path (default: hash-reuse-cache.json)")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--build-cache", action="store_true", help="After a full successful recorder, capture stamps with all Unity writers stopped; read no payloads")
    modes.add_argument("--reuse-unchanged-cache", action="store_true", help="Reuse only canonical/fingerprint-matching payload SHA values; always hash metadata")
    modes.add_argument("--recover-completed-scan", type=Path, help="Adopt an immutable completed failed FULL scan refused solely for unchanged metadata lacking a stored GUID; rehash metadata and newer payloads")
    args = parser.parse_args(argv)
    if args.build_cache:
        try:
            report = build_hash_cache(args.project, args.manifest, args.hash_cache)
        except Exception as error:
            report = {"status": "cache-build-failed", "failure": f"{type(error).__name__}: {error}"}
        print(json.dumps(report, ensure_ascii=False), flush=True)
        return 0 if report["status"] == "cache-built" else 1
    report = record_import(args.project, args.manifest, args.reuse_unchanged_cache, args.hash_cache, args.recover_completed_scan)
    print(json.dumps({key: report.get(key) for key in ("status", "products", "assetRootFiles", "hashedFiles", "hashedBytes",
        "reusedHashFiles", "reusedHashBytes", "hashMode",
        "recoveredScanFiles", "recoveredScanBytes",
        "changedFileCount", "newFileCount", "newMaterials", "newPrefabs", "newMetaFiles", "failure")}, ensure_ascii=False), flush=True)
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    raise SystemExit(main())
