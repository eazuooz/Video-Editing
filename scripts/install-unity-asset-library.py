#!/usr/bin/env python3
"""File-only final installation after isolated Unity exit and delta recording.

Default is a structural dry run. --apply hashes the complete library once, then
renames only its owned root/metadata and adds the verified runtime dependencies.
No Unity, desktop, vendor code, archive, Git, or process-control command is run.
"""
from __future__ import annotations

import argparse
import copy
import ctypes
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import time
import uuid

TARGET = "Assets/ThirdParty/YamyamAssetLibrary"
EXPECTED_PRODUCTS = 84
ADDRESSABLES = "com.unity.addressables"
ADDRESSABLES_VERSION = "2.11.2"
REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
GUID = re.compile(rb"(?m)^guid:[ \t]*([a-fA-F0-9]{32})[ \t]*\r?$")
HARD_COUNTERS = ("missingMonoScripts", "missingTextureReferences", "missingShaders",
                 "shaderCompileErrors", "unreadableAssets", "compilationErrors", "externalAssetDependencyCount")
HARD_KINDS = {"asset-inspection-error", "incomplete-pbr-set", "null-source-material"}


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_json(path):
    data = Path(path).read_bytes()
    return json.loads(data.decode("utf-8-sig")), data


def is_link(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & REPARSE)


def no_links(path, boundary):
    path, boundary = Path(path).absolute(), Path(boundary).absolute()
    if path != boundary and not path.is_relative_to(boundary):
        raise ValueError(f"Outside ownership boundary: {path}")
    if not path.resolve().is_relative_to(boundary.resolve()):
        raise ValueError(f"Resolved path escaped ownership boundary: {path}")
    for current in (path, *path.parents):
        if os.path.lexists(current) and is_link(current.lstat()):
            raise ValueError(f"Symlink/reparse point refused: {current}")
        if current == boundary:
            return
    raise ValueError("Ownership boundary not reached")


def relative_parts(relative):
    value = str(relative).replace("\\", "/")
    parts = PurePosixPath(value).parts
    if (not parts or value.startswith("/") or re.match(r"^[A-Za-z]:", value)
            or any(p in (".", "..", "") or ":" in p or "\0" in p for p in parts)):
        raise ValueError(f"Unsafe relative path: {relative}")
    return parts


def child(root, relative):
    parts = relative_parts(relative)
    path = Path(root).joinpath(*parts)
    no_links(path, root)
    if not path.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError(f"Escaped owned root: {path}")
    return path


def process_running(pid):
    """Read-only liveness check; permission uncertainty fails closed."""
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        raise ValueError("Exit proof needs a positive integer pid")
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.restype = ctypes.c_void_p
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() not in (87, 1168)
        try:
            code = ctypes.c_ulong()
            return not kernel.GetExitCodeProcess(ctypes.c_void_p(handle), ctypes.byref(code)) or code.value == 259
        finally:
            kernel.CloseHandle(ctypes.c_void_p(handle))
    if Path("/proc").is_dir():
        return Path("/proc", str(pid)).exists()
    raise ValueError("No supported read-only process liveness check on this host")


def issue_identity(issue):
    return sha(json.dumps(issue, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())


def validate_reports(validation, validation_bytes, fallback, fallback_bytes, review):
    if validation.get("status") not in {"pass", "completed-with-issues"}:
        raise ValueError("Isolated asset validation did not finish successfully")
    if any(validation.get(key, 0) for key in HARD_COUNTERS):
        raise ValueError("Missing/unreadable assets, references or compilation failures cannot be reviewed away")
    if fallback.get("status") not in {"completed", "completed-with-issues"} or fallback.get("lastError"):
        raise ValueError("Fallback preparation did not complete successfully")
    if (not isinstance(fallback.get("jobsTotal"), int) or fallback["jobsTotal"] < 0
            or fallback.get("jobsCompleted") != fallback["jobsTotal"]):
        raise ValueError("Fallback jobs are unfinished")
    required = []
    for source, data in (("validation", validation), ("fallback", fallback)):
        for issue in data.get("issues", []):
            kind = issue.get("kind", issue.get("code", ""))
            if (kind in HARD_KINDS or kind.startswith("missing") or "compile" in kind
                    or "guid" in kind.lower() or "hash" in kind.lower()
                    or kind == "job-error" and re.search(r"FileNotFound|DirectoryNotFound|hash mismatch|invalid GUID|compilation|corrupt", issue.get("detail", ""), re.I)):
                raise ValueError(f"Non-reviewable integrity/compilation issue: {source}: {kind}")
            required.append({"report": source, "issueSha256": issue_identity(issue), "issue": issue})
    if not required:
        if validation["status"] != "pass":
            raise ValueError("A non-pass validation has no exact issues to review")
        return []
    if not review or review.get("validationSha256") != sha(validation_bytes) or review.get("fallbackSha256") != sha(fallback_bytes):
        raise ValueError("Exact report-bound issue decisions are required: " + json.dumps(required, ensure_ascii=False))
    decisions = {}
    for decision in review.get("decisions", []):
        key = (decision.get("report"), decision.get("issueSha256"))
        if (key in decisions or decision.get("decision") != "accept"
                or not isinstance(decision.get("reason"), str) or len(decision["reason"].strip()) < 8):
            raise ValueError("Each reviewed issue needs one explicit, specific acceptance reason")
        decisions[key] = decision
    keys = {(r["report"], r["issueSha256"]) for r in required}
    if set(decisions) != keys:
        raise ValueError("Issue decisions do not match the exact current issue identities")
    return [decisions[key] for key in sorted(keys)]


def capture_guard(project):
    library = project / "Library"
    if list(library.glob("*.request")):
        raise ValueError("Pending existing Unity capture/sample request; installation deferred")
    for path in library.iterdir():
        if path.is_file() and "capture" in path.name.lower() and path.name.lower().endswith((".running", ".active")):
            raise ValueError(f"Running capture marker: {path}")
    output = project.parent.parent / "shared/output/ai-game-development-human-craft/unity-production"
    if output.is_dir():
        for progress in output.glob("*/progress.txt"):
            statuses = [progress.parent / (mode + "-status.txt") for mode in ("render", "preflight")]
            recent = [p for p in statuses if p.is_file() and p.stat().st_mtime_ns >= progress.stat().st_mtime_ns]
            if not recent or any(p.read_text("utf-8-sig").strip().lower() in {"running", "capturing", "recording", "in-progress"} for p in recent):
                raise ValueError(f"Existing capture progress has no newer terminal status: {progress}")


def settings_snapshot(project):
    root = project / "ProjectSettings"
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in [*dirs, *files]:
            no_links(Path(directory) / name, project)
        for name in files:
            path = Path(directory) / name
            result[path.relative_to(root).as_posix()] = sha(path.read_bytes())
    return result


def package_candidates(project, headless, baseline):
    """Preserve baseline packages; install only the reviewed official runtime closure."""
    required = {ADDRESSABLES: ADDRESSABLES_VERSION,
                "com.unity.cinemachine": "6.6.0", "com.unity.splines": "2.9.1"}
    # The15 required Cinemachine GUID/type pairs were verified against the
    # actual Unity6000.6 bundled package, rather than registry version3.1.7.
    approved_new = {ADDRESSABLES: (ADDRESSABLES_VERSION, "registry"),
                    "com.unity.cinemachine": ("6.6.0", "builtin"),
                    "com.unity.splines": ("2.9.1", "registry"),
                    "com.unity.settings-manager": ("2.1.1", "registry"),
                    "com.unity.scriptablebuildpipeline": ("3.0.3", "registry")}
    old = {}
    for name in ("manifest.json", "packages-lock.json"):
        path = project / "Packages" / name
        no_links(path, project)
        matching = [r for r in baseline if Path(r["path"]).resolve() == path.resolve()]
        if len(matching) != 1:
            raise ValueError(f"No unique recorded package baseline: {name}")
        data = path.read_bytes()
        if len(data) != matching[0]["bytes"] or sha(data) != matching[0]["sha256"]:
            raise ValueError(f"Main Packages changed since the recorded baseline: {name}")
        old[name] = data
    main = json.loads(old["manifest.json"].decode("utf-8-sig"))
    new = copy.deepcopy(main)
    for name, version in required.items():
        if new["dependencies"].get(name) not in (None, version):
            raise ValueError(f"An existing required dependency version must not be replaced: {name}")
        new["dependencies"][name] = version
    for name in ("manifest.json", "packages-lock.json"):
        no_links(headless / "Packages" / name, project)
    isolated_manifest, _ = read_json(headless / "Packages/manifest.json")
    isolated_lock, lock_bytes = read_json(headless / "Packages/packages-lock.json")
    if isolated_manifest != new:
        raise ValueError("Isolated manifest changes more than the three reviewed runtime dependencies")
    old_lock = json.loads(old["packages-lock.json"].decode("utf-8-sig"))["dependencies"]
    new_lock = isolated_lock["dependencies"]
    for name, version in required.items():
        if new_lock.get(name, {}).get("version") != version:
            raise ValueError(f"Isolated lock does not resolve the reviewed version: {name}")
    for name, record in old_lock.items():
        before = {k: v for k, v in record.items() if k != "depth"}
        after = {k: v for k, v in new_lock.get(name, {}).items() if k != "depth"}
        if before != after:
            raise ValueError(f"Isolated lock changes an existing package identity/version/dependencies: {name}")
    closure, pending = set(), list(required)
    while pending:
        name = pending.pop()
        if name in closure:
            continue
        if name not in new_lock:
            raise ValueError(f"Reviewed runtime dependency is absent from isolated lock: {name}")
        closure.add(name)
        pending.extend(new_lock[name].get("dependencies", {}))
    additions = set(new_lock) - set(old_lock)
    if additions - closure or additions - set(approved_new):
        raise ValueError("Isolated lock adds unrelated packages")
    for name in additions | set(required):
        record = new_lock[name]
        if (record.get("version"), record.get("source")) != approved_new[name]:
            raise ValueError(f"Reviewed official package identity/source differs: {name}")
        if record["source"] == "registry" and record.get("url") != "https://packages.unity.com":
            raise ValueError(f"Reviewed package does not use the official Unity registry: {name}")
        if record["source"] == "builtin" and "url" in record:
            raise ValueError("Builtin Cinemachine must retain the editor-bundled identity")
    return old, {"manifest.json": old["manifest.json"] if main == new else encode(new), "packages-lock.json": lock_bytes}


def rename_retry(source, target, attempts=5):
    for attempt in range(attempts):
        if os.path.lexists(target):
            raise ValueError(f"Rename destination already exists: {target}")
        try:
            os.rename(source, target)
            return
        except OSError as error:
            if getattr(error, "winerror", None) not in (5, 32) or attempt + 1 == attempts:
                raise
            time.sleep(min(.2 * 2 ** attempt, 1.0))


def replace_bytes(path, data):
    temporary = path.with_name(path.name + ".install-" + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as output:
            output.write(data)
        os.replace(temporary, path)
    finally:
        if temporary.is_file():
            temporary.unlink()


def verify_inventory(root, products, root_meta, full_hash):
    expected, guids, folders = {}, {}, set()
    for product in products:
        folder = product["folder"]
        if len(relative_parts(folder)) != 1 or folder.casefold() in folders:
            raise ValueError("Product folders are not unique single components")
        folders.add(folder.casefold())
        for record in product["files"]:
            relative = record["path"]
            if relative != folder + ".meta" and not relative.startswith(folder + "/"):
                raise ValueError("A file record is not owned by its product")
            # Components are checked here without per-record disk traversal.
            # The walk below inspects each actual directory/file with lstat once
            # before descent/read, so no link or reparse point is followed.
            relative_parts(relative)
            key = relative.casefold()
            if key in expected or not re.fullmatch(r"[a-f0-9]{64}", record.get("sha256", "")):
                raise ValueError("Duplicate path or invalid canonical SHA256")
            expected[key] = record
            if relative.lower().endswith(".meta"):
                guid = record.get("guid")
                if not re.fullmatch(r"[a-f0-9]{32}", guid or "") or guid in guids:
                    raise ValueError("Missing/duplicate canonical metadata GUID")
                guids[guid] = relative
    actual, actual_folders = set(), set()
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            if is_link((Path(directory) / name).lstat()):
                raise ValueError(f"Symlink/reparse point refused: {Path(directory) / name}")
            if name.casefold() == ".git":
                raise ValueError("Embedded Git directory/file is not an asset-library payload")
        if Path(directory) == root:
            actual_folders.update(d.casefold() for d in dirs)
        for name in files:
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            key = relative.casefold()
            record = expected.get(key)
            if key in actual or record is None or record["path"] != relative:
                raise ValueError(f"Unexpected/duplicate/path-spelling-changed actual file: {relative}")
            before = path.lstat()
            if is_link(before):
                raise ValueError(f"Symlink/reparse point refused: {path}")
            if name.casefold() == ".git":
                raise ValueError("Embedded Git file is not an asset-library payload")
            if not stat.S_ISREG(before.st_mode) or before.st_size != record["bytes"]:
                raise ValueError(f"Missing/nonregular/size-changed file: {relative}")
            if full_hash:
                digest = hashlib.sha256()
                with path.open("rb") as source:
                    for chunk in iter(lambda: source.read(2 * 1024 * 1024), b""):
                        digest.update(chunk)
                after = path.lstat()
                if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino) or digest.hexdigest() != record["sha256"]:
                    raise ValueError(f"Canonical hash/identity mismatch: {relative}")
            actual.add(key)
    if actual != set(expected) or actual_folders != folders:
        raise ValueError("Actual files/product directories differ from the complete canonical inventory")
    meta_path = root.with_name(root.name + ".meta")
    no_links(meta_path, root.parent)
    if not root_meta or Path(root_meta["absolutePath"]).resolve() != meta_path.resolve():
        raise ValueError("Canonical library-root metadata is missing or points elsewhere")
    data = meta_path.read_bytes()
    match = GUID.search(data[:65536])
    if (len(data) != root_meta["bytes"] or sha(data) != root_meta["sha256"] or not match
            or match.group(1).decode().lower() != root_meta.get("guid") or root_meta["guid"] in guids):
        raise ValueError("Library-root metadata hash/GUID mismatch")
    guids[root_meta["guid"]] = str(meta_path)
    return len(actual), guids


def validate_binary_v2(project, root, manifest_path, manifest, verified_source_only=None):
    """Bind every original binary-proof path to the current nibble-aware proof.

    Old v1 receipt proofs supply scope only, never acceptance. File/map hashes,
    rather than the whole manifest hash, survive unrelated metadata recording.
    """
    path = project / "Library/YamyamAssetLibrary/binary-guid-encoding-recheck.json"
    no_links(path, project)
    proof, data = read_json(path)
    products = {str(p["id"]): p for p in manifest["products"]}
    expected = {}
    verified_source_only = verified_source_only or {}
    preserved = set()
    maps = {}
    for identifier, product in products.items():
        originals = product.get("binaryGuidRecoveryProofs", [])
        if not originals:
            continue
        maps[identifier] = sha(json.dumps({k.lower(): v.lower() for k, v in product.get("guidRemaps", {}).items()}, sort_keys=True, separators=(",", ":")).encode())
        records = {r["path"]: r for r in product["files"]}
        for record in product.get("sourceOnlyFiles", []):
            key = (identifier, record["path"])
            if key not in verified_source_only or record["path"] in records:
                raise ValueError("Binary SourceOnly scope lacks independently verified preservation evidence")
            records[record["path"]] = record
            preserved.add(key)
        for original in originals:
            key = (identifier, original["path"])
            if key in expected or original["path"] not in records:
                raise ValueError("Duplicate/missing original binary-proof scope")
            expected[key] = records[original["path"]]
    context = proof.get("sourceManifestContext", {})
    if (not expected or proof.get("proofVersion") != 2 or proof.get("status") != "pass" or proof.get("errors") != []
            or any(proof.get(key) != 0 for key in ("filesWithCollisionSpellings", "exactCanonicalExternalReferenceHits", "staleReceiptFiles"))
            or proof.get("productsChecked") != len(maps) or proof.get("filesChecked") != len(expected)
            or context.get("products") != len(products) or context.get("targetAssetRoot") != TARGET
            or Path(context.get("path", "")).resolve() != manifest_path.resolve()
            or Path(context.get("stageRoot", "")).resolve() != root.resolve()):
        raise ValueError("Post-repair binary GUID v2 recheck is missing, stale, or not a complete pass")
    actual, seen_products = set(), set()
    for product_proof in proof.get("products", []):
        identifier = str(product_proof["id"])
        if (identifier in seen_products or identifier not in maps or product_proof.get("guidMapSha256") != maps[identifier]
                or product_proof.get("originalProofFiles") != sum(key[0] == identifier for key in expected)):
            raise ValueError("Binary v2 product proof does not bind the current complete GUID map/scope")
        seen_products.add(identifier)
        for record in product_proof.get("files", []):
            key = (str(record.get("productId")), record.get("path"))
            canonical = expected.get(key)
            valid_encoding = False
            actual_path = None
            if canonical is not None:
                is_preserved = key in preserved
                actual_path = child(project / "Library/YamyamAssetLibrary/SourceOnly", canonical["path"]) if is_preserved else child(root, canonical["path"])
                if ((is_preserved and (record.get("assetLocation") != "source-only" or Path(canonical.get("preservedPath", "")).resolve() != actual_path.resolve()))
                        or (not is_preserved and record.get("assetLocation", "assets") != "assets")):
                    raise ValueError("Binary v2 asset location does not match its verified canonical preservation location")
                if is_preserved and (record.get("sourceOnlyProof") != verified_source_only[key]
                                     or "preservedPath" in record and Path(record["preservedPath"]).resolve() != actual_path.resolve()):
                    raise ValueError("Binary v2 SourceOnly proof differs from independently verified transaction/backup evidence")
                with actual_path.open("rb") as stream:
                    converted = stream.read(64).lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"%YAML")
                valid_encoding = ((record.get("binaryKind") == "converted-yaml" and converted
                                   and record.get("status") == "converted-yaml-collided-guids-absent")
                                  or (record.get("binaryKind") == "serialized-file" and not converted
                                      and record.get("status") == "collided-guids-absent"))
            if (key in actual or canonical is None or key[0] != identifier or record.get("proofVersion") != 2
                    or record.get("guidMapSha256") != maps[identifier] or not valid_encoding
                    or record.get("receiptMatches") is not True or record.get("exactCanonicalExternalHits") != [] or record.get("collidingReferences") != []
                    or record.get("actualSha256") != canonical["sha256"] or record.get("receiptSha256") != canonical["sha256"]
                    or record.get("receiptBytes") != canonical["bytes"] or record.get("fileBytes") != canonical["bytes"]
                    or Path(record.get("actualPath", "")).resolve() != actual_path.resolve()):
                raise ValueError("Binary v2 file proof is stale/incomplete or still contains a collided GUID")
            actual.add(key)
    if actual != set(expected):
        raise ValueError("Binary v2 evidence is not a bijection over every original proof file")
    return {"path": str(path), "sha256": sha(data), "proofVersion": 2, "products": len(maps), "files": len(expected),
            "sourceOnlyFiles": len(set(expected) & preserved)}


def utc_time(value):
    if not isinstance(value, str):
        raise ValueError("Evidence needs an explicit UTC timestamp")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Evidence timestamp must include its timezone")
    return parsed.astimezone(dt.timezone.utc)


def validate_post_repair(project, root, manifest, result, validation):
    """Reject pre-repair validation and bind every binary scene to current bytes.

    A 64-byte read per canonical scene determines the scope independently of
    historic collision proofs, which cover only four of the seven binary scenes.
    Full payload hashes remain the single --apply verification pass.
    """
    validation_time = utc_time(validation.get("completedUtc"))
    if utc_time(result.get("completedUtc")) < validation_time:
        raise ValueError("Headless result predates its validation report")
    repairs = []
    history = manifest.get("binaryReferenceRepairHistory", [])
    for entry in history:
        path = Path(entry.get("report", "")).absolute()
        no_links(path, project / "Library/YamyamAssetLibrary")
        repair, data = read_json(path)
        if repair.get("status") != "complete" or repair.get("errors") or repair.get("run") != entry.get("run"):
            raise ValueError("Canonical binary-repair history lacks a successful exact run report")
        completed = utc_time(repair.get("completedUtc"))
        if validation_time < completed:
            raise ValueError("Unity validation predates the latest binary reference repair")
        repairs.append({"path": str(path), "sha256": sha(data), "completedUtc": repair["completedUtc"]})
    if history and result.get("command") not in {"finalize", "validate"}:
        raise ValueError("Repaired binaries require a subsequent complete finalize/validate session")
    expected = {}
    for product in manifest["products"]:
        for record in product["files"]:
            if not record["path"].lower().endswith(".unity"):
                continue
            with child(root, record["path"]).open("rb") as stream:
                prefix = stream.read(64).lstrip(b"\xef\xbb\xbf \r\n\t")
            if not prefix.startswith(b"%YAML"):
                expected[TARGET + "/" + record["path"]] = record
    checked, explicit, resolved = set(), 0, 0
    for scene in validation.get("binaryScenes", []):
        path = scene.get("path")
        record = expected.get(path)
        counts = (scene.get("explicitMonoBehaviours"), scene.get("resolvedScriptReferences"))
        if (path in checked or record is None or scene.get("status") != "pass"
                or scene.get("sourceSha256") != record["sha256"] or scene.get("sourceBytes") != record["bytes"]
                or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counts)
                or counts[0] != counts[1] or scene.get("unresolvedScriptReferences") != 0):
            raise ValueError("Binary scene validation is stale, incomplete or contains unresolved scripts")
        checked.add(path)
        explicit += counts[0]
        resolved += counts[1]
    if checked != set(expected):
        raise ValueError("Unity validation does not cover every current binary scene source")
    if expected and (validation.get("binarySceneSourcesVerified") != len(expected)
                     or validation.get("binaryExplicitMonoBehaviours") != explicit
                     or validation.get("binaryScriptReferencesResolved") != resolved):
        raise ValueError("Binary scene validation totals disagree with the exact source evidence")
    return {"repairRuns": repairs, "binaryScenes": len(checked), "explicitMonoBehaviours": explicit,
            "resolvedScriptReferences": resolved, "validationCompletedUtc": validation["completedUtc"]}


def source_only_descriptors(work, report_path, report, report_bytes):
    """Exact per-file transaction descriptors used by the binary v2 resolver."""
    rows = {row["path"]: row for row in report["files"]}
    def descriptor(row):
        return {"run": report["run"], "reportPath": str(report_path), "reportSha256": sha(report_bytes),
                "backupPath": str(child(report_path.parent / "backups", row["path"])),
                "backupSha256": row["sha256"], "sourceManifestSha256": report["sourceManifestSha256"], "sourceBytes": row["bytes"]}
    result = []
    for path, row in rows.items():
        value = descriptor(row)
        if not path.endswith(".meta"):
            meta = rows[path + ".meta"]
            data = child(work / "SourceOnly", meta["path"]).read_bytes()
            match = GUID.search(data[:65536])
            if not match:
                raise ValueError("Preserved SourceOnly asset metadata has no GUID")
            value.update(metadataPath=str(child(work / "SourceOnly", meta["path"])), metadataSha256=meta["sha256"],
                         metadataGuid=match.group(1).decode().lower(), metadataBackup=descriptor(meta))
        result.append({"productId": row.get("productId", "033"), "path": path, "proof": value})
    return result


def validate_initial_source_only(project, root, manifest, validation):
    """Accept only the four preserved033 files, with their original proof chain."""
    products = {str(product["id"]): product for product in manifest["products"]}
    rows = [(identifier, record) for identifier, product in products.items() for record in product.get("sourceOnlyFiles", [])]
    histories = manifest.get("sourceOnlyHistory", [])
    if not rows and not histories and not any(product.get("sourceOnlyHistory") for product in products.values()):
        return {"files": 0}
    spec = importlib.util.spec_from_file_location("yamyam_install_source_only_verifier", Path(__file__).with_name("quarantine-unity-source-only-terrain.py"))
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    expected = set(verifier.TARGETS) | {path + ".meta" for path in verifier.TARGETS}
    if (len(products) != EXPECTED_PRODUCTS or len(rows) != 4 or any(identifier != "033" for identifier, _ in rows)
            or {record["path"] for _, record in rows} != expected or len(histories) != 1
            or products["033"].get("sourceOnlyHistory") != [{key: value for key, value in histories[0].items() if key != "productId"} | {"terrainAssets": 2}]
            or histories[0].get("productId") != "033" or histories[0].get("files") != 4):
        raise ValueError("SourceOnly may preserve exactly two incomplete033 TerrainData plus their metadata, keeping all84 products")
    work = project / "Library/YamyamAssetLibrary"
    history = histories[0]
    report_path = child(work, "source-only-quarantine/" + history["run"] + "/report.json")
    if Path(history["report"]).resolve() != report_path.resolve():
        raise ValueError("SourceOnly history report escaped its exact owned run")
    report, report_bytes = read_json(report_path)
    if (report.get("run") != history["run"] or report.get("status") != "complete" or report.get("apply") is not True
            or report.get("sourceArchivesModified") is not False or report.get("actualMainAssetsModified") is not False
            or report.get("replacementTexturesInferred") is not False or report.get("rollbackErrors")
            or len(report.get("files", [])) != 4 or {row["path"] for row in report["files"]} != expected):
        raise ValueError("SourceOnly transaction did not complete with exact preserved originals")
    if utc_time(validation.get("completedUtc")) < utc_time(report.get("completedUtc")):
        raise ValueError("Unity validation predates the SourceOnly exclusion transaction")
    run = report_path.parent
    original, original_bytes = read_json(child(run, "manifest.json"))
    receipt, receipt_bytes = read_json(child(run, "receipt033.json"))
    runtime, runtime_bytes = read_json(child(run, "runtime-proof.json"))
    missing, missing_bytes = read_json(child(run, "missing-evidence.json"))
    if (sha(original_bytes) != report.get("sourceManifestSha256") or sha(runtime_bytes) != report.get("sourceRuntimeProofSha256")
            or sha(missing_bytes) != report.get("sourceMissingEvidenceSha256")
            or Path(original["stageRoot"]).resolve() != root.resolve()):
        raise ValueError("SourceOnly immutable original/proof snapshots are stale")
    originals = {str(product["id"]): product for product in original["products"]}
    if len(originals) != EXPECTED_PRODUCTS or set(originals) != set(products) or originals["033"] != receipt:
        raise ValueError("SourceOnly snapshot changed product coverage or its original receipt")
    original_paths = {(identifier, row["path"]) for identifier, product in originals.items() for row in product["files"]}
    current_paths = {(identifier, row["path"]) for identifier, product in products.items() for row in product["files"]}
    if original_paths - current_paths != {("033", path) for path in expected}:
        raise ValueError("SourceOnly excluded additional original library files")
    def binary_scope(source):
        return {(str(product["id"]), path) for product in source["products"]
                for path in set(product.get("originalBinaryGuidCollisionBlockers", [])) | {row["path"] for row in product.get("binaryGuidRecoveryProofs", [])}}
    if binary_scope(original) != binary_scope(manifest) or expected & {path for _, path in binary_scope(manifest)}:
        raise ValueError("SourceOnly changed the original binary GUID audit coverage")
    preserved = {record["path"]: record for _, record in rows}
    inputs = {}
    for row in report["files"]:
        path = row["path"]
        record = preserved[path]
        original_record = row["originalRecord"]
        destination = child(work / "SourceOnly", path)
        if (any(record.get(key) != value for key, value in original_record.items())
                or record.get("sourceOnlyReason") != "unused-provider-terrain-missing-original-textures"
                or record.get("sourceOnlyRun") != history["run"] or record.get("runtimeProofSha256") != sha(runtime_bytes)
                or record.get("missingEvidenceSha256") != sha(missing_bytes)
                or Path(record["preservedPath"]).resolve() != destination.resolve()
                or Path(row["destination"]).resolve() != destination.resolve()
                or row["bytes"] != original_record["bytes"] or row["sha256"] != original_record["sha256"]
                or os.path.lexists(child(root, path))):
            raise ValueError("SourceOnly preserved record/path no longer matches the exact excluded original")
        for actual in (destination, child(run / "backups", path)):
            data = actual.read_bytes()
            if len(data) != original_record["bytes"] or sha(data) != original_record["sha256"]:
                raise ValueError("SourceOnly preserved file/independent backup SHA or byte count changed")
        if path.endswith(".meta"):
            match = GUID.search(destination.read_bytes()[:65536])
            if not match or match.group(1).decode().lower() != verifier.TARGETS[path[:-5]]["guid"]:
                raise ValueError("SourceOnly TerrainData original metadata GUID changed")
        inputs[path] = {"bytes": original_record["bytes"], "sha256": original_record["sha256"]}
    verifier.verify_runtime(runtime, original, original_bytes, receipt_bytes, root.parents[2], inputs)
    verifier.verify_missing_evidence(missing, originals["033"])
    return {"files": 4, "productsPreserved": EXPECTED_PRODUCTS, "report": str(report_path), "reportSha256": sha(report_bytes),
            "completedUtc": report["completedUtc"], "runtimeProofSha256": sha(runtime_bytes), "missingEvidenceSha256": sha(missing_bytes),
            "verifiedFiles": source_only_descriptors(work, report_path, report, report_bytes)}


def validate_group_source_only(project, root, manifest, validation, history):
    """Replay the exact reviewed12-terrain group transaction and immutable proof."""
    kind = history.get("kind")
    optional = kind == "incomplete-optional-demo-script-group"
    if kind not in {"incomplete-provider-demo-group", "incomplete-optional-demo-script-group"}:
        raise ValueError("Unknown exact SourceOnly group history")
    count, role = (49, "incomplete-optional-demo") if optional else (12, "incomplete-terrain")
    work = project / "Library/YamyamAssetLibrary"
    report_path = child(work, ("source-only-optional-demo-quarantine/" if optional else "source-only-group-quarantine/") + history["run"] + "/report.json")
    if Path(history.get("report", "")).resolve() != report_path.resolve():
        raise ValueError("SourceOnly group history escaped its exact owned run")
    report, report_bytes = read_json(report_path)
    if (report.get("schemaVersion") != 2 or report.get("kind") != kind or report.get("run") != history["run"]
            or report.get("status") != "complete" or report.get("apply") is not True or report.get("rollbackErrors")
            or any(report.get(field) is not False for field in ("sourceArchivesModified", "actualMainAssetsModified", "terrainPayloadsChanged"))
            or report.get("historicalBinaryProofFieldsPreserved") is not True or report.get("optionalDemoAssets" if optional else "terrainAssets") != count):
        raise ValueError("SourceOnly group transaction is not a complete exact-source preservation")
    if utc_time(validation.get("completedUtc")) < utc_time(report.get("completedUtc")):
        raise ValueError("Unity validation predates the SourceOnly group transaction")
    run = report_path.parent
    snapshots = {name: read_json(child(run, name + ".json")) for name in ("manifest", "group-plan", "runtime-proof", "missing-evidence", "incoming-graph")}
    original, original_bytes = snapshots["manifest"]
    plan, plan_bytes = snapshots["group-plan"]
    runtime, runtime_bytes = snapshots["runtime-proof"]
    missing, missing_bytes = snapshots["missing-evidence"]
    graph, graph_bytes = snapshots["incoming-graph"]
    for name, field in (("manifest", "sourceManifestSha256"), ("group-plan", "sourceGroupPlanSha256"), ("runtime-proof", "sourceRuntimeProofSha256"),
                        ("missing-evidence", "sourceMissingEvidenceSha256"), ("incoming-graph", "sourceIncomingGraphSha256")):
        if sha(snapshots[name][1]) != report.get(field):
            raise ValueError("SourceOnly group immutable snapshot SHA changed: " + name)
    if (plan.get("schemaVersion") != 1 or plan.get("kind") != kind or plan.get("sourceManifestSha256") != sha(original_bytes)
            or plan.get("missingEvidence", {}).get("sha256") != sha(missing_bytes) or plan.get("sourceIncomingGraph", {}).get("sha256") != sha(graph_bytes)
            or Path(original.get("stageRoot", "")).resolve() != root.resolve() or graph.get("filesChangedWhileRead")
            or graph.get("diagnosisSha256") != missing.get("validationSnapshot" if optional else "diagnosis", {}).get("sha256")):
        raise ValueError("SourceOnly group reviewed plan/evidence/source snapshot binding changed")
    products = {str(product["id"]): product for product in manifest["products"]}
    originals = {str(product["id"]): product for product in original["products"]}
    if len(products) != EXPECTED_PRODUCTS or set(products) != set(originals):
        raise ValueError("SourceOnly group must preserve all84 product receipts")
    prior_histories = original.get("sourceOnlyHistory", [])
    if manifest.get("sourceOnlyHistory") != prior_histories + [history] or history.get("kind") != kind:
        raise ValueError("SourceOnly group is not the exact next canonical history entry")
    targets = {row["path"]: row for row in plan.get("targets", [])}
    if len(targets) != len(plan.get("targets", [])) or not targets:
        raise ValueError("SourceOnly group has duplicate or absent reviewed targets")
    terrains = {path for path, row in targets.items() if row.get("role") == role}
    if len(terrains) != count or any(row.get("metadataPath") != path + ".meta" for path, row in targets.items()):
        raise ValueError("SourceOnly group must pair exactly12 incomplete TerrainData with exact metadata")
    if any(row.get("role") not in {role, "incoming-demo-consumer"}
           or (row["role"] == "incoming-demo-consumer" and Path(path).suffix.lower() not in {".unity", ".prefab"})
           or (optional and row["role"] == role and not path.endswith(".unity")) for path, row in targets.items()):
        raise ValueError("SourceOnly group contains an unreviewed outgoing usable asset")
    expected = set(targets) | {path + ".meta" for path in targets}
    rows = {row["path"]: row for row in report.get("files", [])}
    affected = sorted({row["productId"] for row in targets.values()})
    if (set(rows) != expected or len(rows) != len(report.get("files", [])) or report.get("groupAssets") != len(targets)
            or report.get("consumerAssets") != len(targets) - count or history.get("files") != len(expected)
            or history.get("groupAssets") != len(targets) or history.get("productIds") != affected):
        raise ValueError("SourceOnly group report/history does not match the exact reviewed group")
    graph_targets = {row["relativePath"] for row in graph.get("incompleteOptionalDemoTargets" if optional else "incompleteTerrainTargets", [])}
    closure = {row["path"][len(TARGET) + 1:]: row for row in graph.get("incomingClosureAssets", []) if row.get("path", "").startswith(TARGET + "/")}
    prior_preserved = {TARGET + "/" + row["path"] for product in originals.values() for row in product.get("sourceOnlyFiles", [])}
    if (graph_targets != terrains or set(closure) != set(targets) or len(closure) != len(graph.get("incomingClosureAssets", []))
            or any(error.get("path") not in prior_preserved for error in graph.get("errors", []))):
        raise ValueError("SourceOnly group differs from the exact proved incoming serialized graph")
    reachable = set(terrains)
    edges = []
    for edge in graph.get("incomingEdges", []):
        if not all(str(edge.get(key, "")).startswith(TARGET + "/") for key in ("consumer", "target")):
            raise ValueError("Incoming group edge escaped the canonical library")
        edges.append((edge["consumer"][len(TARGET) + 1:], edge["target"][len(TARGET) + 1:]))
    while True:
        following = reachable | {consumer for consumer, target in edges if target in reachable}
        if following == reachable:
            break
        reachable = following
    if reachable != set(targets):
        raise ValueError("SourceOnly group includes assets unrelated to the incomplete TerrainData")
    original_records = {(identifier, row["path"]): row for identifier, product in originals.items() for row in product["files"]}
    original_paths = set(original_records)
    current_paths = {(identifier, row["path"]) for identifier, product in products.items() for row in product["files"]}
    excluded_keys = {(row["productId"], path) for path, row in rows.items()}
    if original_paths - current_paths != excluded_keys:
        raise ValueError("SourceOnly group excluded additional original asset paths")
    receipts, inputs = {}, {}
    for identifier in affected:
        receipt, raw = read_json(child(run, "receipts/" + identifier + ".json"))
        if receipt != originals[identifier]:
            raise ValueError("SourceOnly group immutable receipt differs from its source manifest")
        receipts[identifier] = raw
    for identifier, original_product in originals.items():
        current_product = products[identifier]
        for field in ("originalBinaryGuidCollisionBlockers", "binaryGuidRecoveryProofs"):
            if original_product.get(field) != current_product.get(field):
                raise ValueError("SourceOnly group changed historical896 binary audit fields")
        own_rows = [row for row in report["files"] if row["productId"] == identifier]
        expected_history = original_product.get("sourceOnlyHistory", [])
        if own_rows:
            expected_history = expected_history + [{"kind": kind, "run": history["run"], "report": str(report_path), "files": len(own_rows), "groupAssets": len(own_rows) // 2}]
        if current_product.get("sourceOnlyHistory", []) != expected_history:
            raise ValueError("SourceOnly group product history differs from the exact transaction")
        preserved_rows = list(original_product.get("sourceOnlyFiles", []))
        for row in own_rows:
            path = row["path"]; canonical = original_records.get((identifier, path)); original_record = row.get("originalRecord")
            target = targets.get(path[:-5] if path.endswith(".meta") else path)
            destination = child(work / "SourceOnly", path); backup = child(run / "backups", path)
            expected_sha = target["metadataSha256"] if path.endswith(".meta") else target["sha256"]
            expected_bytes = target["metadataBytes"] if path.endswith(".meta") else target["bytes"]
            if (canonical is None or original_record != canonical or target["productId"] != identifier
                    or row.get("sha256") != canonical["sha256"] or row.get("bytes") != canonical["bytes"]
                    or expected_sha != canonical["sha256"] or expected_bytes != canonical["bytes"]
                    or Path(row.get("destination", "")).resolve() != destination.resolve()
                    or Path(row.get("backupPath", "")).resolve() != backup.resolve() or os.path.lexists(child(root, path))):
                raise ValueError("SourceOnly group preserved original record/location no longer matches its reviewed target")
            for actual in (destination, backup):
                data = actual.read_bytes()
                if len(data) != canonical["bytes"] or sha(data) != canonical["sha256"]:
                    raise ValueError("SourceOnly group preserved file or independent backup SHA/bytes changed")
            if path.endswith(".meta"):
                match = GUID.search(destination.read_bytes()[:65536])
                if not match or match.group(1).decode().lower() != target["guid"] or canonical.get("guid") != target["guid"]:
                    raise ValueError("SourceOnly group preserved original metadata GUID changed")
            elif closure[path].get("actualSha256") != canonical["sha256"] or closure[path].get("actualBytes") != canonical["bytes"]:
                raise ValueError("SourceOnly group incoming graph source bytes do not match the preserved original")
            record = dict(canonical, preservedPath=str(destination), sourceOnlyRun=history["run"], sourceOnlyReason=kind if optional else "incomplete-provider-terrain-demo-group",
                          runtimeProofSha256=sha(runtime_bytes), missingEvidenceSha256=sha(missing_bytes), groupPlanSha256=sha(plan_bytes))
            preserved_rows.append(record)
            inputs[path] = {"bytes": canonical["bytes"], "sha256": canonical["sha256"]}
        if current_product.get("sourceOnlyFiles", []) != preserved_rows:
            raise ValueError("SourceOnly group added or changed an unreviewed preserved file record")
    spec = importlib.util.spec_from_file_location("yamyam_install_group_source_only_verifier", Path(__file__).with_name("quarantine-unity-optional-demos.py" if optional else "quarantine-unity-source-only-group.py"))
    verifier = importlib.util.module_from_spec(spec); spec.loader.exec_module(verifier)
    verifier.verify_runtime(runtime, plan, plan_bytes, original, original_bytes, receipts, root.parents[2], inputs)
    verifier.verify_missing_evidence(missing, plan, original)
    return {"files": len(expected), "productsPreserved": EXPECTED_PRODUCTS, "report": str(report_path), "reportSha256": sha(report_bytes),
            "completedUtc": report["completedUtc"], "groupPlanSha256": sha(plan_bytes), "runtimeProofSha256": sha(runtime_bytes),
            "missingEvidenceSha256": sha(missing_bytes), "verifiedFiles": source_only_descriptors(work, report_path, report, report_bytes)}, original


def validate_source_only(project, root, manifest, validation):
    """Accept the initial exact4 files and, if present, one reviewed group run."""
    histories = manifest.get("sourceOnlyHistory", [])
    if any(history.get("kind") == "incomplete-optional-demo-script-group" for history in histories):
        if (len(histories) != 3 or histories[0].get("kind") or histories[1].get("kind") != "incomplete-provider-demo-group"
                or histories[2].get("kind") != "incomplete-optional-demo-script-group"):
            raise ValueError("Optional demos require exact immutable initial033 then terrain-group then optional-demo history")
        latest, previous = validate_group_source_only(project, root, manifest, validation, histories[-1])
        earlier = validate_source_only(project, root, previous, validation)
        prior = {str(p["id"]): p.get("sourceOnlyFiles", []) for p in previous["products"]}
        for product in manifest["products"]:
            if product.get("sourceOnlyFiles", [])[:len(prior[str(product["id"])])] != prior[str(product["id"])]:
                raise ValueError("Optional SourceOnly history changed an earlier preserved original")
        return {"files": earlier["files"] + latest["files"], "productsPreserved": EXPECTED_PRODUCTS,
                "runs": earlier["runs"] + [{k: v for k, v in latest.items() if k != "verifiedFiles"}],
                "verifiedFiles": earlier["verifiedFiles"] + latest["verifiedFiles"]}
    group_histories = [history for history in histories if history.get("kind") == "incomplete-provider-demo-group"]
    if not group_histories:
        return validate_initial_source_only(project, root, manifest, validation)
    if len(histories) != 2 or len(group_histories) != 1 or histories[-1] != group_histories[0] or histories[0].get("kind"):
        raise ValueError("SourceOnly accepts the exact initial033 run followed by one reviewed incomplete-demo group run")
    group, previous = validate_group_source_only(project, root, manifest, validation, group_histories[0])
    initial = validate_initial_source_only(project, root, previous, validation)
    # Verify earlier preserved rows remain exact in the current receipt chain.
    prior = {str(product["id"]): product.get("sourceOnlyFiles", []) for product in previous["products"]}
    for product in manifest["products"]:
        if product.get("sourceOnlyFiles", [])[:len(prior[str(product["id"])])] != prior[str(product["id"])]:
            raise ValueError("Later SourceOnly history changed an earlier preserved original")
    return {"files": initial["files"] + group["files"], "productsPreserved": EXPECTED_PRODUCTS,
            "runs": [{key: value for key, value in item.items() if key != "verifiedFiles"} for item in (initial, group)],
            "verifiedFiles": initial["verifiedFiles"] + group["verifiedFiles"]}


def install(project, apply=False, exit_proof=None, reviewed_issues=None):
    project = Path(project).absolute()
    no_links(project, Path(project.anchor))
    project = project.resolve()
    work = project / "Library/YamyamAssetLibrary"
    no_links(work, project)
    version_path = project / "ProjectSettings/ProjectVersion.txt"
    if not version_path.is_file() or not work.is_dir():
        raise ValueError("An existing Unity project and prepared owned library workspace are required")
    report_path = work / "installation-report.json"
    report = {"schemaVersion": 1, "startedUtc": utc(), "status": "checking", "apply": apply,
              "mainProject": str(project), "originalArchivesModified": False, "rollbackErrors": [], "foreignWritesPreserved": []}
    journal = []
    try:
        headless = work / "headless-project"
        if not re.search(r"(?m)^m_EditorVersion:\s*6000\.6\.0f1\s*$", version_path.read_text("utf-8-sig")):
            raise ValueError("Main project Unity version differs from the validated6000.6.0f1 target")
        source = headless / TARGET
        destination = project / TARGET
        for path in (source, source.with_name(source.name + ".meta"), destination, destination.with_name(destination.name + ".meta")):
            no_links(path, project)
        if not source.is_dir() or not destination.parent.is_dir() or os.path.lexists(destination) or os.path.lexists(destination.with_name(destination.name + ".meta")):
            raise ValueError("Owned source/root metadata must exist and destination must be absent")
        if os.path.lexists(headless / "Temp/UnityLockfile"):
            raise ValueError("Isolated Unity lock remains; normal process exit is required")
        result_path = headless / "Library/YamyamAssetLibrary/headless-result.json"
        no_links(result_path, project)
        result, result_bytes = read_json(result_path)
        proof_path = Path(exit_proof).absolute() if exit_proof else work / "headless-process-exit.json"
        no_links(proof_path, work)
        proof, _ = read_json(proof_path)
        if (result.get("active") is not False or result.get("status") != "complete" or result.get("exitCode") != 0 or result.get("error")
                or Path(result["projectPath"]).resolve() != headless.resolve() or not result.get("nonce") or not result.get("completedUtc")):
            raise ValueError("Headless session/result did not complete successfully")
        if (proof.get("status") != "exited" or proof.get("exitCode") != 0 or proof.get("nonce") != result["nonce"]
                or Path(proof["projectPath"]).resolve() != headless.resolve() or proof.get("headlessResultSha256") != sha(result_bytes)
                or process_running(proof.get("pid"))):
            raise ValueError("Exact normal-process-exit proof is missing or process is still running")
        inner = headless / "Library/YamyamAssetLibrary"
        for field, name in (("validationPath", "validation.json"), ("fallbackPath", "fallback-preparation-report.json")):
            value = result.get(field)
            # A fresh validation-only session intentionally reuses the earlier
            # full-finalize fallback evidence; it does not run the builder again.
            if field == "fallbackPath" and value in (None, "") and result.get("command") == "validate":
                report["fallbackEvidenceReusedByValidationOnlySession"] = True
                value = str(inner / name)
            if not value or Path(value).resolve() != (inner / name).resolve():
                raise ValueError("Result points outside its expected isolated report paths")
            no_links(inner / name, project)
        validation, validation_bytes = read_json(inner / "validation.json")
        fallback, fallback_bytes = read_json(inner / "fallback-preparation-report.json")
        if validation.get("nonce") != result["nonce"]:
            raise ValueError("Validation/result session nonce mismatch")
        if validation.get("unityVersion") != "6000.6.0f1":
            raise ValueError("Validation Unity version does not match the installation target")
        review = None
        if reviewed_issues:
            review_path = Path(reviewed_issues).absolute()
            no_links(review_path, work)
            review, _ = read_json(review_path)
        report["reviewedIssues"] = validate_reports(validation, validation_bytes, fallback, fallback_bytes, review)
        manifest_path = work / "staging-manifest.json"
        no_links(manifest_path, project)
        manifest, manifest_bytes = read_json(manifest_path)
        delta_path = work / "final-import-delta.json"
        no_links(delta_path, project)
        delta, _ = read_json(delta_path)
        if (Path(manifest["stageRoot"]).absolute() != source or Path(manifest["stageRoot"]).resolve() != source.resolve()
                or delta.get("status") != "complete" or delta.get("bookkeepingCommitted") is not True
                or delta.get("errors")
                or delta.get("afterManifestSha256") != sha(manifest_bytes) or Path(delta["actualRoot"]).resolve() != source.resolve()
                or Path(delta["manifest"]).resolve() != manifest_path.resolve()):
            raise ValueError("Canonical manifest/final recorder delta is stale or not scoped to the exact isolated Assets root")
        products = manifest.get("products", [])
        if len(products) != EXPECTED_PRODUCTS or len({str(p["id"]) for p in products}) != EXPECTED_PRODUCTS or any(p.get("status") != "complete" or not p.get("finalImportRecordedAt") for p in products):
            raise ValueError("All84 unique products must be complete and recorded after isolated import")
        for product in products:
            receipt_path = child(work / "receipts", str(product["id"]) + ".json")
            receipt, _ = read_json(receipt_path)
            if receipt != product or Path(product["finalImportActualRoot"]).resolve() != source.resolve():
                raise ValueError(f"Canonical product receipt is stale: {product['id']}")
        report["sourceOnlyAcceptance"] = validate_source_only(project, source, manifest, validation)
        preserved = {(row["productId"], row["path"]): row["proof"] for row in report["sourceOnlyAcceptance"].get("verifiedFiles", [])}
        report["binaryGuidV2Acceptance"] = validate_binary_v2(project, source, manifest_path, manifest, preserved)
        report["postRepairValidationAcceptance"] = validate_post_repair(project, source, manifest, result, validation)
        report["assetFiles"], guids = verify_inventory(source, products, manifest.get("assetRootMeta"), full_hash=apply)
        if delta.get("products") != len(products) or delta.get("assetRootFiles") != report["assetFiles"]:
            raise ValueError("Recorder totals do not match the current complete canonical inventory")
        report["fullLibraryHashesVerified"] = apply
        report.update(products=len(products), sourceRoot=str(source), destinationRoot=str(destination),
                      canonicalManifestSha256=sha(manifest_bytes), headlessResultSha256=sha(result_bytes),
                      validationSha256=sha(validation_bytes), fallbackSha256=sha(fallback_bytes))
        baseline_path = work / "preserved-project-baseline.json"
        no_links(baseline_path, project)
        baseline, _ = read_json(baseline_path)
        old_packages, new_packages = package_candidates(project, headless, baseline)
        settings = settings_snapshot(project)
        capture_guard(project)
        if not apply:
            report["status"] = "ready-dry-run"
        else:
            # Ensure the actual main project did not acquire a conflicting GUID
            # while the isolated validation was running. Never follow links.
            for directory, dirs, files in os.walk(project / "Assets", followlinks=False):
                for name in dirs:
                    if is_link((Path(directory) / name).lstat()):
                        raise ValueError("Existing main Assets contains a symlink/reparse directory")
                for name in files:
                    if is_link((Path(directory) / name).lstat()):
                        raise ValueError("Existing main Assets contains a symlink/reparse file")
                    if name.lower().endswith(".meta"):
                        with (Path(directory) / name).open("rb") as stream:
                            match = GUID.search(stream.read(65536))
                        if match and match.group(1).decode().lower() in guids:
                            raise ValueError(f"Existing main-project GUID collides with the incoming library: {name}")
            backup = work / "installation-backups" / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex)
            no_links(backup, project)
            backup.mkdir(parents=True)
            for name, data in old_packages.items():
                (backup / name).write_bytes(data)
            root_meta_bytes = source.with_name(source.name + ".meta").read_bytes()
            if sha(root_meta_bytes) != manifest["assetRootMeta"]["sha256"]:
                raise ValueError("Source root metadata changed after preflight")
            (backup / "asset-root.meta").write_bytes(root_meta_bytes)
            report["packageBackupDirectory"] = str(backup)
            # Check capture/package quiescence again immediately before writes.
            capture_guard(project)
            for name, old in old_packages.items():
                path = project / "Packages" / name
                if path.read_bytes() != old:
                    raise ValueError("Main Packages changed during installation preflight")
                if old != new_packages[name]:
                    replace_bytes(path, new_packages[name])
                    journal.append(("file", path, (old, new_packages[name])))
            # Metadata first prevents an already-open main Editor from making a
            # new root GUID in the brief interval between the two atomic renames.
            for start, end in ((source.with_name(source.name + ".meta"), destination.with_name(destination.name + ".meta")), (source, destination)):
                no_links(start, project); no_links(end, project)
                rename_retry(start, end)
                journal.append(("root-meta", start, (end, root_meta_bytes)) if start.name.endswith(".meta") else ("move", start, end))
            installed_meta = destination.with_name(destination.name + ".meta")
            no_links(installed_meta, project)
            report["destinationRootMetadataObservation"] = {"expectedSha256": manifest["assetRootMeta"]["sha256"], "expectedGuid": manifest["assetRootMeta"]["guid"], "present": installed_meta.is_file()}
            if not installed_meta.is_file():
                raise ValueError("Destination root metadata disappeared after rename")
            installed_bytes = installed_meta.read_bytes()
            installed_guid = GUID.search(installed_bytes[:65536])
            report["destinationRootMetadataObservation"].update(actualSha256=sha(installed_bytes), actualGuid=installed_guid.group(1).decode().lower() if installed_guid else None)
            if (sha(installed_bytes) != manifest["assetRootMeta"]["sha256"] or not installed_guid
                    or installed_guid.group(1).decode().lower() != manifest["assetRootMeta"]["guid"]):
                raise ValueError("Destination root metadata changed after rename; newer foreign content will be preserved")
            if settings_snapshot(project) != settings:
                raise ValueError("Main ProjectSettings changed during installation; owned changes will roll back")
            report.update(status="installed", projectSettingsPreserved=True, canonicalManifestModified=False,
                          addressablesVersion=ADDRESSABLES_VERSION,
                          packageAfterSha256={name: sha(data) for name, data in new_packages.items()})
        report["completedUtc"] = utc()
    except Exception as error:
        for kind, first, second in reversed(journal):
            try:
                if kind == "move":
                    no_links(first, project); no_links(second, project)
                    rename_retry(second, first)
                elif kind == "root-meta":
                    end, original_meta = second
                    no_links(first, project)
                    if destination.is_dir() and not source.is_dir():
                        raise ValueError("Library root could not roll back; keeping its destination metadata beside it")
                    if os.path.lexists(first):
                        raise ValueError("Source root metadata reappeared; rollback will not overwrite it")
                    if (os.path.lexists(end) and not is_link(end.lstat()) and end.is_file()
                            and end.read_bytes() == original_meta):
                        rename_retry(end, first)
                    else:
                        if os.path.lexists(end):
                            report["foreignWritesPreserved"].append(str(end))
                        with first.open("xb") as restore:
                            restore.write(original_meta)
                        report["rootMetadataRestoredFromBackup"] = True
                else:
                    old, installed = second
                    if first.read_bytes() != installed:
                        raise ValueError("Package changed after our write; preserving the newer change instead of overwriting it during rollback")
                    replace_bytes(first, old)
            except Exception as rollback_error:
                report["rollbackErrors"].append(f"{first}: {type(rollback_error).__name__}: {rollback_error}")
        report.update(status="failed", error=f"{type(error).__name__}: {error}", completedUtc=utc(),
                      rollbackAttempted=bool(journal), rollbackComplete=not report["rollbackErrors"] and not report["foreignWritesPreserved"])
    work.mkdir(parents=True, exist_ok=True)
    no_links(report_path, project)
    replace_bytes(report_path, encode(report))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--exit-proof", type=Path)
    parser.add_argument("--reviewed-issues", type=Path)
    args = parser.parse_args(argv)
    result = install(args.project, args.apply, args.exit_proof, args.reviewed_issues)
    print(json.dumps({k: result.get(k) for k in ("status", "products", "assetFiles", "fullLibraryHashesVerified", "error", "rollbackComplete")}, ensure_ascii=False))
    return 0 if result["status"] in {"ready-dry-run", "installed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
