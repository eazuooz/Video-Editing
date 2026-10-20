"""Read-only, extension-independent native-binary census beyond historical proofs.

Read at most64 header bytes per non-metadata canonical file in remapped products.
Only additional SerializedFile candidates are fully hashed/parsed. Source assets,
receipts, archives and canonical bookkeeping are never modified.
"""
import argparse
import collections
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import stat
import struct
import uuid

spec = importlib.util.spec_from_file_location("coverage_finalizer", Path(__file__).with_name("finalize-unity-asset-library.py"))
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def map_sha(remaps):
    return sha(json.dumps(remaps, sort_keys=True, separators=(",", ":")).encode())


def serialized_header(header, file_bytes):
    """Strict standalone header discrimination, independent of file extension."""
    if len(header) < 16:
        return None
    metadata, stored_size, version, offset = struct.unpack_from(">4I", header)
    if not 1 <= version <= 50:
        return None
    if version >= 9 and (len(header) < 20 or header[16] not in (0, 1)):
        return None
    minimum = 20 if version >= 9 else 16
    if version >= 22:
        if len(header) < 48:
            return None
        metadata, stored_size, offset = struct.unpack_from(">IQQ", header, 20)
        minimum = 48
    if stored_size != file_bytes or not minimum <= offset <= stored_size or not 0 < metadata <= offset:
        return None
    return {"formatVersion": version, "headerBytes": minimum, "metadataBytes": metadata,
            "dataOffset": offset, "endian": ("little" if header[16] == 0 else "big") if version >= 9 else "stored-in-metadata"}


def regular_path(root, relative, checked_directories):
    parts = PurePosixPath(relative).parts
    if not parts or relative.startswith("/") or any(part in ("", ".", "..") or ":" in part or "\\" in part for part in parts):
        raise ValueError("Unsafe canonical relative path")
    path = root.joinpath(*parts)
    for current in (path, *path.parents):
        if current in checked_directories:
            break
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Symlink/reparse point refused")
        if current != path:
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError("Non-directory ancestor refused")
            checked_directories.add(current)
        if current == root:
            break
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Canonical source is not a regular file")
    return path, info


def stamp(info):
    return info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_ino, info.st_dev


def audit(project, report_path=None):
    project = Path(project).absolute()
    work = project / "Library/YamyamAssetLibrary"
    manifest_path = work / "staging-manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    root = Path(manifest["stageRoot"]).absolute()
    if root != work / "headless-project/Assets/ThirdParty/YamyamAssetLibrary":
        raise ValueError("Only the exact owned isolated native-asset root is readable")
    # Inspect all literal ancestors before caching any directory checks.
    for current in (root, *root.parents):
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Owned root traverses a symlink/reparse point")
    products = manifest["products"]
    if len(products) != 84 or len({str(p["id"]) for p in products}) != 84 or any(p.get("status") != "complete" for p in products):
        raise ValueError("All84 unique complete products are required")
    report_path = Path(report_path).absolute() if report_path else work / "binary-guid-global-coverage.json"
    if report_path.parent != work:
        raise ValueError("Coverage report must be a direct owned-workspace sidecar")
    owners = collections.defaultdict(list)
    historical = {(str(p["id"]), row["path"]) for p in products for row in p.get("binaryGuidRecoveryProofs", [])}
    for product in products:
        for record in product["files"]:
            if record.get("guid"):
                owners[record["guid"].lower()].append({"productId": str(product["id"]), "path": record["path"]})
    report = {"schemaVersion": 1, "proofVersion": 2, "status": "checking", "startedUtc": utc(),
              "sourceManifestSha256": sha(manifest_bytes), "manifestPath": str(manifest_path), "stageRoot": str(root),
              "scope": "Every current non-metadata canonical file in every product with explicit GUID remaps, excluding independently audited historical paths; header detection does not depend on extension.",
              "historicalProofPaths": len(historical), "assetBytesModified": False, "canonicalModified": False,
              "sourceArchivesRead": False, "unityLaunched": False, "headersChecked": 0, "headerBytesRead": 0,
              "additionalBinaryFiles": 0, "additionalBinaryBytes": 0, "additionalFilesWithCollisions": 0,
              "additionalExactExternalHits": 0, "staleReceiptFiles": 0, "products": [], "errors": []}
    checked_directories = set()
    for product in products:
        remaps = {str(old).lower(): str(new).lower() for old, new in product.get("guidRemaps", {}).items()}
        if not remaps:
            continue
        identifier = str(product["id"])
        row = {"id": identifier, "guidRemaps": len(remaps), "guidMapSha256": map_sha(remaps),
               "historicalProofPaths": sum(pid == identifier for pid, _path in historical), "headers": [], "additionalFiles": []}
        report["products"].append(row)
        for record in product["files"]:
            relative = record["path"]
            if relative.lower().endswith(".meta") or (identifier, relative) in historical:
                continue
            try:
                path, before = regular_path(root, relative, checked_directories)
                if before.st_size != record["bytes"]:
                    raise ValueError("Canonical source size changed before header census")
                with path.open("rb") as source:
                    header = source.read(64)
                if stamp(before) != stamp(path.lstat()):
                    raise ValueError("Source changed during header census")
                report["headersChecked"] += 1
                report["headerBytesRead"] += len(header)
                native = serialized_header(header, before.st_size)
                text = header.lstrip(b"\xef\xbb\xbf \t\r\n").startswith((b"%YAML", b"--- !u!"))
                header_row = {"path": relative, "fileBytes": before.st_size, "canonicalSha256": record["sha256"],
                              "headerSha256": sha(header), "format": "serialized-file" if native else "unity-yaml" if text else "other-source"}
                row["headers"].append(header_row)
                if native is None:
                    if not text and path.suffix.lower() in F.SERIALIZED:
                        raise ValueError("Native extension has neither recognized Unity text nor bounded SerializedFile header")
                    continue
                proof = F.binary_absence_proof(path, remaps, None)
                if stamp(before) != stamp(path.lstat()):
                    raise ValueError("Native binary changed during external-table audit")
                exact = []
                enriched = []
                for hit in proof["collidingReferences"]:
                    old = hit["guid"]
                    bound = {**hit, "oldGuid": old, "desiredNewGuid": remaps[old],
                             "currentOldGuidOwners": owners.get(old, []), "currentDesiredGuidOwners": owners.get(remaps[old], [])}
                    enriched.append(bound)
                    if hit["where"] == "external-table" and hit["representation"] == "unity-byte-nibbles" and hit["canonicalGuid"] == old:
                        exact.append(bound)
                item = {"productId": identifier, "path": relative, "actualPath": str(path), "proofVersion": 2,
                        "guidMapSha256": row["guidMapSha256"], "binaryKind": "serialized-file", **native,
                        "actualSha256": proof["sha256After"], "fileBytes": proof["fileBytes"], "receiptSha256": record["sha256"],
                        "receiptBytes": record["bytes"], "receiptMatches": proof["sha256After"] == record["sha256"],
                        "status": "collision-reference-present" if enriched else "collided-guids-absent",
                        "exactCanonicalExternalHits": exact, "collidingReferences": enriched,
                        "externalCount": proof["externalCount"], "metadataBytesConsumed": proof["metadataBytesConsumed"]}
                row["additionalFiles"].append(item)
                report["additionalBinaryFiles"] += 1
                report["additionalBinaryBytes"] += proof["fileBytes"]
                report["additionalFilesWithCollisions"] += bool(enriched)
                report["additionalExactExternalHits"] += len(exact)
                report["staleReceiptFiles"] += not item["receiptMatches"]
            except Exception as error:
                report["errors"].append({"productId": identifier, "path": relative, "error": f"{type(error).__name__}: {error}"})
        print(f"Coverage {identifier}: {len(row['headers'])} additional headers; {len(row['additionalFiles'])} additional SerializedFiles", flush=True)
    if manifest_path.read_bytes() != manifest_bytes:
        report["errors"].append({"error": "Canonical manifest changed during coverage census"})
    report["completedUtc"] = utc()
    report["productsWithRemaps"] = len(report["products"])
    report["status"] = "needs-review" if report["errors"] or report["staleReceiptFiles"] else "needs-extra-binary-reference-repair" if report["additionalFilesWithCollisions"] else "pass"
    temporary = report_path.with_name(report_path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, report_path)
    print(json.dumps({key: report[key] for key in ("status", "productsWithRemaps", "historicalProofPaths", "headersChecked", "headerBytesRead", "additionalBinaryFiles", "additionalBinaryBytes", "additionalFilesWithCollisions", "additionalExactExternalHits", "staleReceiptFiles")}), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    result = audit(arguments.project, arguments.report)
    raise SystemExit(0 if result["status"] == "pass" else 1)
