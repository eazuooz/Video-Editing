#!/usr/bin/env python3
"""Read-only recheck of every recovered binary's current GUID collision proof.

Reads the canonical manifest and only the recorded binary files. It never runs
Unity, vendor code or recovery, and never writes asset bytes, receipts or the
canonical manifest. The sole output is an owned audit report.
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat

spec = importlib.util.spec_from_file_location("unity_guid_finalizer", Path(__file__).with_name("finalize-unity-asset-library.py"))
finalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finalizer)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def guid_map_sha(remaps):
    return hashlib.sha256(json.dumps(remaps, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def bind_context(report, manifest, manifest_path):
    """Attach immutable audit inputs without re-reading any binary payload."""
    report["sourceManifestContext"] = {"path": str(manifest_path.absolute()), "stageRoot": manifest["stageRoot"],
                                       "targetAssetRoot": manifest.get("targetAssetRoot"), "products": len(manifest["products"])}
    products = {str(product["id"]): product for product in manifest["products"]}
    root = Path(manifest["stageRoot"]).absolute()
    for result in report["products"]:
        remaps = {key.lower(): value.lower() for key, value in products[str(result["id"])].get("guidRemaps", {}).items()}
        result["guidMapSha256"] = guid_map_sha(remaps)
        for item in result["files"]:
            item.update(productId=str(result["id"]), guidMapSha256=result["guidMapSha256"],
                        proofVersion=finalizer.BINARY_GUID_PROOF_VERSION)
            item.setdefault("actualPath", str(root.joinpath(*item["path"].split("/"))))
            item.setdefault("assetLocation", "assets")
    return report


def regular_owned(root, relative):
    resolved = finalizer.contained(root, relative)
    literal = root.joinpath(*str(relative).replace("\\", "/").split("/"))
    for path in (literal, *literal.parents):
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Symlink/reparse point refused: " + str(path))
        if path == root:
            break
    if not resolved.is_file():
        raise ValueError("Binary proof path is not a regular file")
    return resolved


def owned_literal(work, path):
    """Check literal ancestors before resolving local immutable evidence."""
    value = Path(path)
    if ".." in value.parts:
        raise ValueError("Traversing SourceOnly evidence path refused")
    value = Path(os.path.abspath(value))
    if value == work or not value.is_relative_to(work):
        raise ValueError("SourceOnly evidence escaped the owned workspace")
    for component in (value, *value.parents):
        if os.path.lexists(component):
            info = component.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("SourceOnly evidence traverses a symlink/reparse point")
        if component == work:
            break
    return value


def source_only_file(project, manifest, product, record, cache):
    """Resolve one preserved original through exact complete history+backups."""
    work = project / "Library/YamyamAssetLibrary"
    root = Path(manifest["stageRoot"]).absolute()
    relative, identifier = record["path"], str(product["id"])
    parts = Path(relative.replace("/", os.sep)).parts
    if not parts or Path(relative).is_absolute() or any(part in (".", "..") or ":" in part for part in parts):
        raise ValueError("Unsafe preserved original path")
    run = str(record.get("sourceOnlyRun", ""))
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run):
        raise ValueError("SourceOnly record lacks a safe exact run identity")
    destination = owned_literal(work, work / "SourceOnly" / Path(*parts))
    if owned_literal(work, record.get("preservedPath", "")) != destination:
        raise ValueError("Preserved original does not use its exact SourceOnly path")
    if os.path.lexists(root.joinpath(*parts)):
        raise ValueError("SourceOnly original still exists under active Assets")
    histories = [row for row in product.get("sourceOnlyHistory", []) if str(row.get("run")) == run]
    if len(histories) != 1:
        raise ValueError("Preserved original requires one matching product SourceOnly history")
    report_path = owned_literal(work, histories[0].get("report", ""))
    allowed = {work / kind / run / "report.json" for kind in ("source-only-quarantine", "source-only-group-quarantine", "source-only-optional-demo-quarantine")}
    if report_path not in allowed:
        raise ValueError("SourceOnly history report is not in its exact bounded run")
    top = [row for row in manifest.get("sourceOnlyHistory", []) if str(row.get("run")) == run]
    if len(top) != 1 or owned_literal(work, top[0].get("report", "")) != report_path:
        raise ValueError("Preserved original lacks matching top-level SourceOnly history")
    optional_demo = report_path.parent.parent.name == "source-only-optional-demo-quarantine"
    if optional_demo and (histories[0].get("kind") != "incomplete-optional-demo-script-group"
                          or top[0].get("kind") != "incomplete-optional-demo-script-group"
                          or record.get("sourceOnlyReason") != "incomplete-optional-demo-script-group"):
        raise ValueError("Optional-demo source record/history kind is not explicitly bound")
    key = str(report_path)
    if key not in cache:
        raw = report_path.read_bytes()
        report = json.loads(raw.decode("utf-8-sig"))
        if (report.get("status") != "complete" or report.get("apply") is not True or str(report.get("run")) != run
                or report.get("rollbackErrors") or report.get("error") or not report.get("completedUtc")):
            raise ValueError("SourceOnly preservation transaction was not completed cleanly")
        if optional_demo and (report.get("schemaVersion") != 2 or report.get("kind") != "incomplete-optional-demo-script-group"
                              or report.get("sourceArchivesModified") is not False or report.get("actualMainAssetsModified") is not False):
            raise ValueError("Optional-demo preservation report has the wrong exact kind or mutation scope")
        snapshot_path = owned_literal(work, report_path.parent / "manifest.json")
        snapshot_raw = snapshot_path.read_bytes()
        if hashlib.sha256(snapshot_raw).hexdigest() != report.get("sourceManifestSha256"):
            raise ValueError("SourceOnly original manifest snapshot SHA changed")
        cache[key] = (report, hashlib.sha256(raw).hexdigest(), json.loads(snapshot_raw.decode("utf-8-sig")))
    report, report_sha, original_manifest = cache[key]
    originals = [p for p in original_manifest["products"] if str(p["id"]) == identifier]
    if len(originals) != 1:
        raise ValueError("SourceOnly original manifest lacks one exact product")
    original_records = [row for row in originals[0]["files"] if row["path"] == relative]
    rows = [row for row in report["files"] if row.get("path") == relative and
            (str(row.get("productId")) == identifier or report.get("schemaVersion") == 1 and identifier == "033" and "productId" not in row)]
    if len(rows) != 1 or len(original_records) != 1:
        raise ValueError("SourceOnly report lacks one exact original product/path")
    row, original = rows[0], original_records[0]
    if (row.get("originalRecord") != original or any(record.get(field) != value for field, value in original.items())
            or row.get("sha256") != original["sha256"] or row.get("bytes") != original["bytes"]
            or owned_literal(work, row.get("destination", "")) != destination
            or record.get("runtimeProofSha256") != report.get("sourceRuntimeProofSha256")
            or record.get("missingEvidenceSha256") != report.get("sourceMissingEvidenceSha256")):
        raise ValueError("SourceOnly record/report differs from immutable original provenance")
    backup = owned_literal(work, report_path.parent / "backups" / Path(*parts))
    if "backupPath" in row and owned_literal(work, row["backupPath"]) != backup:
        raise ValueError("SourceOnly backup path does not match the exact owned run")
    if report.get("schemaVersion") == 2 and "backupPath" not in row:
        raise ValueError("Group SourceOnly report lacks explicit backup binding")
    data = backup.read_bytes()
    if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError("SourceOnly independent original backup bytes changed")
    info = destination.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_size != record["bytes"]:
        raise ValueError("SourceOnly preserved source is absent, nonregular or changed size")
    return destination, {"run": run, "reportPath": str(report_path), "reportSha256": report_sha,
                         "backupPath": str(backup), "backupSha256": hashlib.sha256(data).hexdigest(),
                         "sourceManifestSha256": report["sourceManifestSha256"], "sourceBytes": len(data)}


def converted_yaml_proof(path, remaps):
    """Prove a Unity-converted YAML source has no remaining old GUID spelling."""
    data = path.read_bytes()
    if not data.startswith(b"%YAML 1.1") or not re.search(rb"(?m)^--- !u![0-9]+ &[+-]?[0-9]+(?:\s|$)", data):
        raise ValueError("Converted text is not an explicit Unity YAML document")
    hits = []
    for guid in remaps:
        patterns = {}
        for name, pattern in finalizer.guid_byte_forms(guid).items():
            patterns.setdefault(pattern, []).append(name)
        for pattern, names in patterns.items():
            cursor = 0
            while True:
                offset = data.find(pattern, cursor)
                if offset < 0:
                    break
                hits.append({"guid": guid, "representation": "+".join(names), "where": "converted-yaml-byte-scan",
                             "offset": offset, "bytes": len(pattern)})
                cursor = offset + 1
    for match in finalizer.TOKEN.finditer(data):
        guid = match.group(1).decode().lower()
        if guid in remaps:
            hits.append({"guid": guid, "representation": "case-insensitive-32hex-token", "where": "converted-yaml-byte-scan",
                         "offset": match.start(1), "bytes": 32})
    digest = hashlib.sha256(data).hexdigest()
    return {"proofVersion": finalizer.BINARY_GUID_PROOF_VERSION, "fileBytes": len(data),
            "sha256Before": digest, "sha256After": digest, "binaryModified": False,
            "collidedGuidsAbsent": not hits, "collidingReferences": hits, "testedCollidedGuids": sorted(remaps),
            "formatVersion": None, "unityVersion": None, "externalCount": 0,
            "metadataBytes": None, "metadataBytesConsumed": None}


def audit(project, report_path=None):
    project = Path(project).resolve()
    work = project / "Library/YamyamAssetLibrary"
    manifest_path = work / "staging-manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    root = Path(manifest["stageRoot"]).absolute()
    if not root.resolve().is_relative_to(work.resolve()):
        raise ValueError("Read-only recheck is confined to the owned isolated library workspace")
    report_path = Path(report_path).absolute() if report_path else work / "binary-guid-encoding-recheck.json"
    if report_path == work or not report_path.resolve().is_relative_to(work.resolve()):
        raise ValueError("Audit output must remain inside the owned workspace")
    report = {"schemaVersion": 1, "startedUtc": utc(), "status": "checking", "stageRoot": str(root),
              "sourceManifestSha256": hashlib.sha256(manifest_bytes).hexdigest(),
              "proofVersion": finalizer.BINARY_GUID_PROOF_VERSION,
              "guidEncodingRecheckToolSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "finalizerToolSha256": hashlib.sha256(Path(spec.origin).read_bytes()).hexdigest(),
              "scope": "All original recovered binary-proof paths, including exact history/backup-verified SourceOnly originals; current complete per-product GUID remaps; full external-table parsing and full binary-byte scans including verified Unity per-byte nibble order.",
              "assetBytesModified": False, "receiptsModified": False, "manifestModified": False,
              "unityLaunched": False, "sourceArchivesRead": False, "products": [], "errors": []}
    owners = {}
    for product in manifest["products"]:
        for record in product.get("files", []) + product.get("sourceOnlyFiles", []):
            if record.get("guid"):
                owner = {"productId": product["id"], "path": record["path"]}
                if record in product.get("sourceOnlyFiles", []):
                    owner.update(assetLocation="source-only", actualPath=record["preservedPath"])
                owners.setdefault(record["guid"].lower(), []).append(owner)
    checked_files = checked_bytes = hit_files = external_hits = stale_files = 0
    source_only_checked = 0
    preservation_cache = {}
    for product in manifest["products"]:
        original_proofs = product.get("binaryGuidRecoveryProofs", [])
        if not original_proofs:
            continue
        identifier = str(product["id"])
        remaps = {key.lower(): value.lower() for key, value in product.get("guidRemaps", {}).items()}
        records = {record["path"]: record for record in product["files"]}
        source_only = {record["path"]: record for record in product.get("sourceOnlyFiles", [])}
        if len(records) != len(product["files"]) or len(source_only) != len(product.get("sourceOnlyFiles", [])) or set(records) & set(source_only):
            raise ValueError("Historical path has duplicate/ambiguous active or SourceOnly provenance")
        prior = {}
        for collision in product.get("guidCollisions", []):
            prior.setdefault(collision["oldGuid"].lower(), []).append({"path": collision.get("path"), "previous": collision.get("previous")})
        result = {"id": identifier, "guidRemapsTested": len(remaps), "originalProofFiles": len(original_proofs), "files": []}
        report["products"].append(result)
        for original_proof in original_proofs:
            relative = original_proof["path"]
            item = {"path": relative, "status": "checking"}
            result["files"].append(item)
            try:
                if relative in records:
                    record = records[relative]
                    path = regular_owned(root, relative)
                    item.update(assetLocation="assets", actualPath=str(path))
                else:
                    record = source_only[relative]
                    path, preservation = source_only_file(project, manifest, product, record, preservation_cache)
                    metadata = source_only.get(relative + ".meta")
                    if metadata is None or metadata.get("sourceOnlyRun") != record.get("sourceOnlyRun"):
                        raise ValueError("Preserved native original lacks metadata from the same exact run")
                    metadata_path, metadata_proof = source_only_file(project, manifest, product, metadata, preservation_cache)
                    metadata_bytes = metadata_path.read_bytes()
                    metadata_sha = hashlib.sha256(metadata_bytes).hexdigest()
                    metadata_guid = finalizer.GUID.search(metadata_bytes[:65536])
                    original_guid = metadata.get("source", {}).get("originalGuid")
                    expected_guid = metadata.get("guid") or remaps.get(original_guid, original_guid)
                    if (len(metadata_bytes) != metadata["bytes"] or metadata_sha != metadata["sha256"]
                            or not metadata_guid or expected_guid and metadata_guid.group(1).decode().lower() != expected_guid.lower()):
                        raise ValueError("Preserved native metadata SHA/bytes/GUID differs from its original")
                    preservation.update(metadataPath=str(metadata_path), metadataSha256=metadata_sha,
                                        metadataGuid=metadata_guid.group(1).decode().lower(), metadataBackup=metadata_proof)
                    item.update(assetLocation="source-only", actualPath=str(path), preservedPath=str(path), sourceOnlyProof=preservation)
                before = path.lstat()
                with path.open("rb") as source:
                    header = source.read(64)
                converted = header.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"%YAML")
                proof = converted_yaml_proof(path, remaps) if converted else finalizer.binary_absence_proof(path, remaps, None)
                after = path.lstat()
                if (before.st_size, before.st_mtime_ns, before.st_ctime_ns, before.st_ino, before.st_dev) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns, after.st_ino, after.st_dev):
                    raise ValueError("Binary changed while the read-only audit was in progress")
                checked_files += 1
                source_only_checked += item["assetLocation"] == "source-only"
                checked_bytes += proof["fileBytes"]
                exact = []
                enriched = []
                for hit in proof["collidingReferences"]:
                    guid = hit["guid"]
                    row = {**hit, "oldGuid": guid, "desiredNewGuid": remaps[guid],
                           "currentOldGuidOwners": owners.get(guid, []), "currentDesiredGuidOwners": owners.get(remaps[guid], []),
                           "originalCollisionRecords": prior.get(guid, [])}
                    enriched.append(row)
                    if hit["where"] == "external-table" and hit["representation"] == "unity-byte-nibbles" and hit["canonicalGuid"] == guid:
                        exact.append(row)
                if enriched:
                    hit_files += 1
                external_hits += len(exact)
                matches = proof["sha256After"] == record["sha256"] and proof["fileBytes"] == record["bytes"]
                stale_files += not matches
                status = ("converted-yaml-collisions-present" if enriched else "converted-yaml-collided-guids-absent") if converted else ("collision-reference-present" if enriched else "collided-guids-absent")
                item.update(status=status, binaryKind="converted-yaml" if converted else "serialized-file",
                            fileBytes=proof["fileBytes"], actualSha256=proof["sha256After"], receiptSha256=record["sha256"],
                            receiptBytes=record["bytes"], receiptMatches=matches, formatVersion=proof["formatVersion"],
                            unityVersion=proof["unityVersion"], externalCount=proof["externalCount"],
                            metadataBytes=proof["metadataBytes"], metadataBytesConsumed=proof["metadataBytesConsumed"],
                            originalProofVersion=original_proof.get("proofVersion", 1),
                            originalProofTestedGuids=len(original_proof.get("testedCollidedGuids", [])),
                            exactCanonicalExternalHits=exact, collidingReferences=enriched)
                if converted:
                    item["convertedTextProof"] = {"format": "unity-yaml", "guidMapSha256": guid_map_sha(remaps),
                        "sourceSha256": proof["sha256After"], "sourceBytes": proof["fileBytes"],
                        "allGuidSpellingsScanned": True, "collidingGuidOccurrences": enriched}
            except Exception as error:
                item.update(status="error", error=f"{type(error).__name__}: {error}")
                report["errors"].append({"productId": identifier, **item})
        hits = sum(bool(row.get("collidingReferences")) for row in result["files"])
        converted_count = sum(row.get("binaryKind") == "converted-yaml" for row in result["files"])
        print(f"Recheck {identifier}: {len(result['files'])} original binary paths ({converted_count} now YAML); {hits} files with collision spellings", flush=True)
    if manifest_path.read_bytes() != manifest_bytes:
        report["errors"].append({"kind": "canonical-manifest-changed-during-audit"})
    report.update(completedUtc=utc(), productsChecked=len(report["products"]), filesChecked=checked_files,
                  bytesChecked=checked_bytes, filesWithCollisionSpellings=hit_files,
                  exactCanonicalExternalReferenceHits=external_hits, staleReceiptFiles=stale_files,
                  sourceOnlyFilesChecked=source_only_checked, activeAssetFilesChecked=checked_files - source_only_checked,
                  serializedBinaryFiles=sum(row.get("binaryKind") == "serialized-file" for product in report["products"] for row in product["files"]),
                  convertedTextFiles=sum(row.get("binaryKind") == "converted-yaml" for product in report["products"] for row in product["files"]))
    report["status"] = "needs-binary-reference-repair" if hit_files else "pass"
    if report["errors"] or stale_files:
        report["status"] = "needs-review"
    bind_context(report, manifest, manifest_path)
    temporary = report_path.with_name(report_path.name + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, report_path)
    print(json.dumps({key: report[key] for key in ("status", "productsChecked", "filesChecked", "activeAssetFilesChecked", "sourceOnlyFilesChecked", "serializedBinaryFiles", "convertedTextFiles", "bytesChecked", "filesWithCollisionSpellings", "exactCanonicalExternalReferenceHits", "staleReceiptFiles")}), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.project, args.report)
    raise SystemExit(0 if result["status"] == "pass" else 1)
