"""Bounded Unity SerializedFile external-GUID repair; dry run by default.

Only exact, independently parsed 16-byte external-table GUID fields may change.
All other header/metadata/object bytes and every .meta GUID stay unchanged.
Original archives and the actual project's Assets/Packages/Settings are excluded.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import tempfile


SCRIPTS = Path(__file__).resolve().parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FINALIZER = load_module("yamyam_binary_parser", SCRIPTS / "finalize-unity-asset-library.py")
SHARED = load_module("yamyam_shared_reader", SCRIPTS / "unity-asset-library-code/extract_binary_scene_scripts.py")


def literal_path(path):
    """Reject links/junctions before resolving any explicitly owned boundary."""
    path = Path(os.path.abspath(path))
    for component in reversed((path, *path.parents)):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Symlink/reparse point is outside this tool's owned boundary: " + str(component))
    return path


def read_bytes(path):
    return SHARED.read_shared(literal_path(path))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")


def read_json(path):
    return json.loads(read_bytes(path).decode("utf-8-sig"))


def atomic_write(path, data):
    path = literal_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    literal_path(path.parent)
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".yamyam-binary-", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        literal_path(temporary)
        literal_path(path)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            literal_path(temporary).unlink()


def write_new(path, data):
    path = literal_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    literal_path(path.parent)
    with path.open("xb") as stream:
        stream.write(data)


def child(root, relative):
    root = literal_path(root)
    relative = str(relative).replace("\\", "/")
    if Path(relative).is_absolute() or ".." in Path(relative).parts or Path(relative).drive:
        raise ValueError("Absolute/traversing child path is forbidden: " + relative)
    path = literal_path(root / relative)
    if path == root or not path.is_relative_to(root):
        raise ValueError("Path escaped the explicitly owned root: " + str(relative))
    return path


def map_sha(remaps):
    normalized = {str(old).lower(): str(new).lower() for old, new in remaps.items()}
    for old, new in normalized.items():
        if not re.fullmatch("[a-f0-9]{32}", old) or not re.fullmatch("[a-f0-9]{32}", new) or old == new:
            raise ValueError("Invalid or identity GUID remapping")
    return sha(json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode())


def parse_data(data, scratch):
    atomic_write(scratch, data)  # Only the invocation's owned Library scratch file.
    return FINALIZER.parse_binary_externals(scratch)


def outside_guid_occurrences(data, remaps, allowed=()):
    """Locate every spelling/occurrence, including overlapping byte matches."""
    allowed = set(allowed)
    outside = []
    for old in remaps:
        patterns = {}
        for representation, pattern in FINALIZER.guid_byte_forms(old).items():
            patterns.setdefault(pattern, []).append(representation)
        for pattern, representations in patterns.items():
            cursor = 0
            while True:
                offset = data.find(pattern, cursor)
                if offset < 0:
                    break
                if (old, pattern, offset) not in allowed:
                    outside.append({"oldGuid": old, "offset": offset, "bytes": len(pattern), "representations": representations})
                cursor = offset + 1
    return outside


def verify_converted_text(data, row, remaps, digest):
    """Review a formerly binary path without widening binary patch semantics."""
    proof = row.get("convertedTextProof", {})
    if (row.get("binaryKind") != "converted-yaml"
            or row.get("status") != "converted-yaml-collided-guids-absent"
            or row.get("exactCanonicalExternalHits") != []
            or row.get("collidingReferences") != []
            or proof.get("format") != "unity-yaml"
            or proof.get("guidMapSha256") != digest
            or proof.get("sourceSha256") != sha(data)
            or proof.get("sourceBytes") != len(data)
            or proof.get("allGuidSpellingsScanned") is not True
            or proof.get("collidingGuidOccurrences") != []):
        raise ValueError("Converted YAML lacks the exact clean SHA/map-bound version2 proof")
    if not data.startswith(b"%YAML 1.1") or not re.search(rb"(?m)^--- !u![0-9]+ &[+-]?[0-9]+(?:\s|$)", data):
        raise ValueError("Converted text does not have an actual Unity YAML header/document")
    outside = outside_guid_occurrences(data, remaps)
    for match in re.finditer(rb"(?<![a-fA-F0-9])[a-fA-F0-9]{32}(?![a-fA-F0-9])", data):
        old = match.group().decode().lower()
        if old in remaps:
            outside.append({"oldGuid": old, "offset": match.start(), "bytes": 32, "representations": ["case-insensitive-32hex-token"]})
    return outside


def prepare_patch(data, table, remaps, audited_hits):
    """Independent bounded preflight, useful with real parser-based fixtures."""
    remaps = {old.lower(): new.lower() for old, new in remaps.items()}
    map_sha(remaps)
    actual = []
    for external in table["externals"]:
        old = FINALIZER.unity_guid_from_bytes(bytes.fromhex(external["rawGuidHex"]))
        if old in remaps:
            actual.append((external["guidOffset"], old, remaps[old], external["rawGuidHex"]))
    audited = [(int(hit["guidOffset"]), hit["oldGuid"].lower(), hit["desiredNewGuid"].lower(), hit["rawGuidHex"].lower()) for hit in audited_hits]
    if sorted(actual) != sorted(audited) or len(set(actual)) != len(actual):
        raise ValueError("Current parsed external fields differ from the final version2 audit")
    patches, allowed = [], {}
    after = bytearray(data)
    end = 0
    header_bytes = 48 if table["formatVersion"] >= 22 else 20
    for offset, old, new, raw_hex in sorted(actual):
        old_raw = FINALIZER.guid_byte_forms(old)["unity-byte-nibbles"]
        new_raw = FINALIZER.guid_byte_forms(new)["unity-byte-nibbles"]
        if offset < max(end, header_bytes) or offset + 16 > table["dataOffset"] or data[offset:offset + 16] != old_raw or old_raw.hex() != raw_hex:
            raise ValueError("External GUID field bounds/old bytes changed")
        after[offset:offset + 16] = new_raw
        patches.append({"offset": offset, "oldGuid": old, "newGuid": new, "originalRawHex": old_raw.hex(), "adaptedRawHex": new_raw.hex()})
        allowed[(old, old_raw, offset)] = True
        end = offset + 16
    # Audit presence alone cannot prove an occurrence was the external field.
    outside = outside_guid_occurrences(data, remaps, allowed)
    if outside:
        return None, patches, outside
    after = bytes(after)
    cursor = 0
    for patch in patches:
        offset = patch["offset"]
        if data[cursor:offset] != after[cursor:offset]:
            raise ValueError("A byte outside reviewed GUID fields changed")
        cursor = offset + 16
    if data[cursor:] != after[cursor:] or len(data) != len(after):
        raise ValueError("Serialized object body/file length changed")
    return after, patches, []


def verify_after(before_table, after_table, remaps):
    if {key: value for key, value in before_table.items() if key != "externals"} != {key: value for key, value in after_table.items() if key != "externals"}:
        raise ValueError("Parser observed a changed header/type/object layout")
    if len(before_table["externals"]) != len(after_table["externals"]):
        raise ValueError("External table length changed")
    for before, after in zip(before_table["externals"], after_table["externals"]):
        canonical = FINALIZER.unity_guid_from_bytes(bytes.fromhex(before["rawGuidHex"]))
        expected = remaps.get(canonical, canonical)
        if FINALIZER.unity_guid_from_bytes(bytes.fromhex(after["rawGuidHex"])) != expected:
            raise ValueError("Reparsed external GUID did not equal the intended owner GUID")
        if {key: value for key, value in before.items() if key not in {"rawGuidHex", "canonicalGuid"}} != {key: value for key, value in after.items() if key not in {"rawGuidHex", "canonicalGuid"}}:
            raise ValueError("External path/type/offset changed")


def editor_lock_guard(work):
    lock = literal_path(work / "headless-project/Temp/UnityLockfile")
    if not lock.exists():
        return
    if os.name != "nt":
        raise ValueError("Headless Unity lockfile remains; remove only after confirming that Editor exited")
    import ctypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    create.restype = ctypes.c_void_p
    handle = create(str(lock), 0x80000000, 0, None, 3, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ValueError("Headless Unity lockfile is held; active import must finish before repair")
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle(handle)


def repair(project, audit_path, apply=False, expected_manifest_sha=None, expected_audit_sha=None, editor_stopped=False):
    project = literal_path(project)
    work = child(project, "Library/YamyamAssetLibrary")
    manifest_path = child(work, "staging-manifest.json")
    original_manifest = read_bytes(manifest_path)
    manifest = json.loads(original_manifest.decode("utf-8-sig"))
    audit_path = literal_path(audit_path)
    if not audit_path.is_relative_to(work):
        raise ValueError("Audit must be the owned local Library evidence")
    audit_bytes = read_bytes(audit_path)
    audit = json.loads(audit_bytes.decode("utf-8-sig"))
    stage = literal_path(manifest["stageRoot"])
    allowed = {work / "staging/CreatorBundle", work / "headless-project/Assets/ThirdParty/YamyamAssetLibrary"}
    if stage not in allowed:
        raise ValueError("Only the explicit local stage/isolated headless Assets copy is repairable")
    if len(manifest["products"]) != 84 or any(product.get("status") != "complete" for product in manifest["products"]):
        raise ValueError("All84 products must be complete before bounded binary repair")
    if audit.get("proofVersion") != 2 or audit.get("errors") or audit.get("staleReceiptFiles") != 0 or not audit.get("completedUtc"):
        raise ValueError("A completed final version2 audit with no parse/stale-receipt errors is required")
    if audit["sourceManifestSha256"] != sha(original_manifest) or literal_path(audit["stageRoot"]) != stage:
        raise ValueError("Canonical manifest/stage changed after the final version2 audit")
    if apply:
        if not editor_stopped or expected_manifest_sha != sha(original_manifest) or expected_audit_sha != sha(audit_bytes):
            raise ValueError("Apply needs confirmed Editor exit and the exact reviewed manifest/audit SHA256 arguments")
        editor_lock_guard(work)
    products = {product["id"]: product for product in manifest["products"]}
    if len(products) != 84:
        raise ValueError("Product IDs are not unique")
    receipt_originals, all_records, owners = {}, {}, {}
    for product in products.values():
        receipt = child(work / "receipts", product["id"] + ".json")
        raw = read_bytes(receipt)
        if json.loads(raw.decode("utf-8-sig")) != product:
            raise ValueError("Canonical receipt differs from its manifest product: " + product["id"])
        receipt_originals[receipt] = raw
        for record in product["files"]:
            if record["path"] in all_records:
                raise ValueError("A canonical asset path has multiple owners")
            all_records[record["path"]] = (product, record)
            if record["path"].lower().endswith(".meta") and record.get("guid"):
                owners.setdefault(record["guid"].lower(), []).append((product["id"], record["path"]))
    expected_products = {product["id"] for product in products.values() if product.get("originalBinaryGuidCollisionBlockers")}
    if len(audit["products"]) != len(expected_products) or {product["id"] for product in audit["products"]} != expected_products:
        raise ValueError("Final version2 audit does not cover every original blocked binary product")
    run = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_root = child(work, "binary-reference-repair/" + run)
    run_root.mkdir(parents=True)
    scratch = run_root / "parser-scratch.bin"
    report_path = run_root / "report.json"
    report = {"schemaVersion": 1, "run": run, "status": "preflighting", "applyRequested": apply,
              "sourceManifestSha256": sha(original_manifest), "sourceAuditSha256": sha(audit_bytes), "sourceAudit": str(audit_path),
              "stageRoot": str(stage), "sourceArchivesModified": False, "actualMainProjectAssetsModified": False,
              "patchedFieldBytes": 16, "files": [], "convertedTextFiles": [], "errors": [], "outsideExternalFieldHits": [], "referencedOwnerProofs": []}
    protected, changes = {}, {}

    def protect(relative):
        if relative in protected:
            return protected[relative]
        if relative not in all_records:
            raise ValueError("Ownership proof path has no canonical file receipt: " + relative)
        owner, record = all_records[relative]
        path = child(stage, relative)
        raw = read_bytes(path)
        if sha(raw) != record["sha256"] or len(raw) != record["bytes"]:
            raise ValueError("Ownership/source asset differs from canonical SHA/bytes: " + relative)
        protected[relative] = {"sha256": sha(raw), "bytes": len(raw)}
        return protected[relative]

    def meta_identity(relative, expected):
        proof = protect(relative)
        raw = read_bytes(child(stage, relative))
        match = re.search(rb"(?m)^guid:[ \t]*([a-fA-F0-9]{32})", raw)
        if not match or match.group(1).decode().lower() != expected.lower():
            raise ValueError("Actual .meta GUID differs from the exact owner proof: " + relative)
        return proof

    for product_audit in audit["products"]:
        product = products[product_audit["id"]]
        remaps = {old.lower(): new.lower() for old, new in product["guidRemaps"].items()}
        digest = map_sha(remaps)
        if digest != product_audit["guidMapSha256"]:
            raise ValueError("Product GUID map changed after final audit: " + product["id"])
        if len(product_audit["files"]) != len(product["originalBinaryGuidCollisionBlockers"]) or {row["path"] for row in product_audit["files"]} != set(product["originalBinaryGuidCollisionBlockers"]):
            raise ValueError("Final audit omitted/added an original blocked binary path")
        for row in product_audit["files"]:
            relative = row["path"]
            try:
                if row.get("proofVersion") != 2 or row["guidMapSha256"] != digest or row["productId"] != product["id"]:
                    raise ValueError("Final audit row version/product/map binding changed")
                owner, record = all_records[relative]
                path = child(stage, relative)
                if owner["id"] != product["id"] or not relative.startswith(product["folder"] + "/") or literal_path(row["actualPath"]) != path:
                    raise ValueError("Binary source path is outside its exact product owner")
                before = read_bytes(path)
                if not row["receiptMatches"] or sha(before) != row["actualSha256"] or row["actualSha256"] != row["receiptSha256"] or record["sha256"] != row["receiptSha256"] or len(before) != row["receiptBytes"] or len(before) != record["bytes"]:
                    raise ValueError("Current binary SHA/bytes no longer match the final audit and canonical receipt")
                protected[relative] = {"sha256": sha(before), "bytes": len(before)}
                kind = row.get("binaryKind", "serialized-file")
                if kind == "converted-yaml":
                    outside = verify_converted_text(before, row, remaps, digest)
                    if outside:
                        report["outsideExternalFieldHits"].append({"path": relative, "hits": outside, "binaryKind": kind})
                        raise ValueError("A converted YAML path still contains a collided old GUID spelling/token")
                    own_meta = relative + ".meta"
                    meta_record = all_records[own_meta][1]
                    meta_identity(own_meta, meta_record["guid"])
                    report["convertedTextFiles"].append({"path": relative, "productId": product["id"], "bytes": len(before), "sha256": sha(before),
                                                         "allGuidSpellingsAndCaseInsensitiveTokensIndependentlyAbsent": True,
                                                         "rootMetaGuid": meta_record["guid"], "rootMetaSha256": protected[own_meta]["sha256"], "modified": False})
                    continue
                if kind != "serialized-file":
                    raise ValueError("Unknown binary audit classification")
                table = parse_data(before, scratch)
                after, patches, outside = prepare_patch(before, table, remaps, row["exactCanonicalExternalHits"])
                if outside:
                    report["outsideExternalFieldHits"].append({"path": relative, "hits": outside})
                    raise ValueError("Collided GUID spelling occurs outside the exact planned external GUID fields")
                if not patches:
                    continue
                after_table = parse_data(after, scratch)
                verify_after(table, after_table, remaps)
                own_meta = relative + ".meta"
                meta_record = all_records[own_meta][1]
                meta_identity(own_meta, meta_record["guid"])
                for hit in row["exactCanonicalExternalHits"]:
                    desired = hit["desiredNewGuid"].lower()
                    requested = [(item["productId"], item["path"]) for item in hit["currentDesiredGuidOwners"]]
                    if len(requested) != 1 or owners.get(desired) != requested or requested[0][0] != product["id"]:
                        raise ValueError("Desired GUID does not have exactly one current owned product path")
                    target_meta = requested[0][1]
                    target_record = all_records[target_meta][1]
                    old_guid = hit["oldGuid"].lower()
                    initial_intent = any(collision["oldGuid"].lower() == old_guid and collision["newGuid"].lower() == desired and collision["path"] == target_meta for collision in product.get("guidCollisions", []))
                    # Recovery added further remaps after initial extraction.
                    # Those receipts carry the original GUID twice, including
                    # immutable archive provenance, rather than appending the
                    # initial guidCollisions list. Require every binding.
                    source = target_record.get("source", {})
                    recovery_intent = (target_record.get("binaryGuidRecoveryRewrite") is True
                                       and target_record.get("originalGuid", "").lower() == old_guid
                                       and source.get("kind") == "unitypackage"
                                       and source.get("originalGuid", "").lower() == old_guid
                                       and bool(source.get("package")) and bool(source.get("originalPath"))
                                       and target_record.get("guid", "").lower() == desired)
                    if not initial_intent and not recovery_intent:
                        raise ValueError("Desired owner path is not the original recorded collision/remap intent")
                    meta_identity(target_meta, desired)
                    target_asset = target_meta[:-5]
                    if child(stage, target_asset).is_dir():
                        if not re.search(rb"(?m)^folderAsset:[ \t]*yes", read_bytes(child(stage, target_meta))):
                            raise ValueError("Folder GUID target lacks explicit folderAsset metadata")
                    else:
                        protect(target_asset)
                    proof = {"productId": product["id"], "oldGuid": hit["oldGuid"], "desiredNewGuid": desired, "metaPath": target_meta, "sourceAssetPath": target_asset,
                             "originalGuidIntent": "initial-collision-record" if initial_intent else "recovery-receipt-original-guid-and-archive-provenance"}
                    if proof not in report["referencedOwnerProofs"]:
                        report["referencedOwnerProofs"].append(proof)
                details = {"path": relative, "productId": product["id"], "bytes": len(before), "originalSha256": sha(before), "adaptedSha256": sha(after),
                           "formatVersion": table["formatVersion"], "patches": patches, "allOtherBytesIdentical": True, "reparsedExternalGUIDsVerified": True,
                           "rootMetaGuid": meta_record["guid"], "rootMetaSha256": protected[own_meta]["sha256"]}
                report["files"].append(details)
                changes[relative] = details
                if apply:
                    backup, candidate = child(run_root / "backups", relative), child(run_root / "candidates", relative)
                    write_new(backup, before)
                    write_new(candidate, after)
            except Exception as error:
                report["errors"].append({"path": relative, "error": str(error)})
    scratch.unlink(missing_ok=True)
    report["summary"] = {"files": len(report["files"]), "externalFields": sum(len(row["patches"]) for row in report["files"]),
                         "convertedTextFiles": len(report["convertedTextFiles"]),
                         "errors": len(report["errors"]), "outsideFieldFiles": len(report["outsideExternalFieldHits"])}
    report["protectedSourceFiles"] = protected
    report["status"] = "blocked" if report["errors"] else "prepared" if apply else "dry-run-ready"
    atomic_write(report_path, json_bytes(report))
    atomic_write(work / "binary-reference-repair-latest.json", json_bytes({"report": str(report_path), "status": report["status"], **report["summary"]}))
    if report["errors"] or not apply:
        return report, report_path
    # Recheck every owned input after preparation and before the first mutation.
    editor_lock_guard(work)
    if read_bytes(manifest_path) != original_manifest or read_bytes(audit_path) != audit_bytes:
        raise ValueError("Canonical manifest/audit changed during preflight")
    for relative, proof in protected.items():
        if sha(read_bytes(child(stage, relative))) != proof["sha256"]:
            raise ValueError("Referenced asset/meta changed during preflight: " + relative)
    for relative, details in changes.items():
        if sha(read_bytes(child(stage, relative))) != details["originalSha256"]:
            raise ValueError("Binary source changed during preflight: " + relative)
    updated = copy.deepcopy(manifest)
    metadata_writes = {}
    for product in updated["products"]:
        owned_changes = {path: change for path, change in changes.items() if change["productId"] == product["id"]}
        if not owned_changes:
            continue
        for record in product["files"]:
            if record["path"] in owned_changes:
                record["sha256"] = owned_changes[record["path"]]["adaptedSha256"]
        product.setdefault("binaryReferenceRepairHistory", []).append({"run": run, "report": str(report_path), "files": len(owned_changes)})
        receipt = child(work / "receipts", product["id"] + ".json")
        metadata_writes[receipt] = (receipt_originals[receipt], json_bytes(product))
    updated["updatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    updated.setdefault("binaryReferenceRepairHistory", []).append({"run": run, "report": str(report_path), **report["summary"]})
    metadata_writes[manifest_path] = (original_manifest, json_bytes(updated))
    for path, (original, _after) in metadata_writes.items():
        backup = child(run_root / "metadata-backups", path.relative_to(work).as_posix())
        write_new(backup, original)
    atomic_write(run_root / "source-audit.json", audit_bytes)
    written = []
    try:
        for relative, details in changes.items():
            path = child(stage, relative)
            candidate = read_bytes(child(run_root / "candidates", relative))
            if sha(read_bytes(path)) != details["originalSha256"] or sha(candidate) != details["adaptedSha256"]:
                raise ValueError("Binary/candidate changed before its atomic replacement")
            atomic_write(path, candidate)
            written.append((path, child(run_root / "backups", relative)))
            if sha(read_bytes(path)) != details["adaptedSha256"]:
                raise ValueError("Written binary SHA differs from verified candidate")
        # Referenced asset contents must remain identical, except other explicitly
        # planned binary external-field replacements in this same transaction.
        for relative, proof in protected.items():
            expected = changes.get(relative, {}).get("adaptedSha256", proof["sha256"])
            if sha(read_bytes(child(stage, relative))) != expected:
                raise ValueError("Protected source/meta changed after binary patch: " + relative)
        for path, (original, after) in metadata_writes.items():
            if read_bytes(path) != original:
                raise ValueError("Canonical receipt changed during binary application")
            atomic_write(path, after)
            written.append((path, child(run_root / "metadata-backups", path.relative_to(work).as_posix())))
        report["status"] = "complete"
        report["updatedManifestSha256"] = sha(metadata_writes[manifest_path][1])
        report["completedUtc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        atomic_write(report_path, json_bytes(report))
        atomic_write(work / "binary-reference-repair-latest.json", json_bytes({"report": str(report_path), "status": report["status"], **report["summary"]}))
    except BaseException as error:
        rollback_errors = []
        for path, backup in reversed(written):
            try:
                atomic_write(path, read_bytes(backup))
            except BaseException as rollback_error:
                rollback_errors.append({"path": str(path), "error": str(rollback_error)})
        report.update(status="failed", error=str(error), rollbackErrors=rollback_errors)
        atomic_write(report_path, json_bytes(report))
        atomic_write(work / "binary-reference-repair-latest.json", json_bytes({"report": str(report_path), "status": report["status"], **report["summary"]}))
        raise
    return report, report_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-manifest-sha256")
    parser.add_argument("--expected-audit-sha256")
    parser.add_argument("--editor-stopped", action="store_true")
    args = parser.parse_args()
    audit = args.audit or args.project / "Library/YamyamAssetLibrary/binary-guid-encoding-recheck.json"
    report, path = repair(args.project, audit, args.apply, args.expected_manifest_sha256, args.expected_audit_sha256, args.editor_stopped)
    print(json.dumps({"status": report["status"], "report": str(path), **report["summary"]}))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
