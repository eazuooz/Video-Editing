"""Preserve exactly two proved-unused incomplete033 TerrainData sources outside Assets.

Dry run is the default. Runtime dependency proof and original missing-texture
evidence are mandatory; no replacement texture is inferred and no archive changes.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


SAFE = module("yamyam_source_only_safety", "repair-unity-binary-references.py")
sha, read_bytes, literal, child = SAFE.sha, SAFE.read_bytes, SAFE.literal_path, SAFE.child
atomic_write, write_new, encoded = SAFE.atomic_write, SAFE.write_new, SAFE.json_bytes
ROOT = "Assets/ThirdParty/YamyamAssetLibrary"
FOLDER = "033-burton-style-halloween-plants-130-surreal-spooky-trees-sci-fi-foliage-mega-pac"
DIRECTORY = FOLDER + "/EmaceArt/PlasticineWorld/Terrain/"
TARGETS = {
    DIRECTORY + "Plakat4_terrain.asset": {"guid": "15e7b97ec04b63345aa74df13b90f429", "missing": ["fad419c323a3f0c4695b04680b6866b1", "0375ede6daaa2f04aadb080cfdd66c10"]},
    DIRECTORY + "New Terrain 6.asset": {"guid": "6e40ea2d41b139d4da3b71c89f9f66cc", "missing": ["c49c8c4e3aeb1d249b9b8fa98683b53b", "d049d6c796f84504a842f6cd9b544421", "545054e05d6c0634e9891851da9b6388", "53ead6874a9846145acc10fe5f07db49"]},
}
MISSING = {guid for target in TARGETS.values() for guid in target["missing"]}
SHA = re.compile(r"^[a-f0-9]{64}$")


def json_input(path):
    raw = read_bytes(path)
    return json.loads(raw.decode("utf-8-sig")), raw


def ordinal_key(path):
    # Match the helper's StringComparer.Ordinal, including non-BMP filenames.
    return path.encode("utf-16-be", "surrogatepass")


def verify_current_missing_references(data, target, work):
    if data.startswith(b"%YAML 1.1"):
        guids = {match.group(1).decode().lower() for match in re.finditer(rb"guid:[ \t]*([a-fA-F0-9]{32})", data)}
    else:
        with tempfile.TemporaryDirectory(prefix="source-only-external-proof-", dir=literal(work)) as directory:
            scratch = child(Path(directory), "terrain.bin")
            table = SAFE.parse_data(data, scratch)
            guids = {row["canonicalGuid"] for row in table["externals"]}
    if not set(target["missing"]) <= guids:
        raise ValueError("Current TerrainData no longer contains the exact original missing-texture references")


def verify_missing_evidence(evidence, product):
    if (evidence.get("sourceModified") is not False or set(evidence.get("missingGuids", [])) != MISSING
            or evidence.get("packageMatches") != [] or evidence.get("canonicalReceiptMatches") != []
            or evidence.get("metadataFiles") != 564 or evidence.get("guidFolders") != 564
            or evidence.get("pathnames") != 564 or evidence.get("members") != 2678
            or evidence.get("available033UnitypackageVariants") != 1 or evidence.get("excluded033Files") != []):
        raise ValueError("Missing-original-texture evidence does not match the exact inspected source")
    inputs = [item for item in product.get("inputs", []) if Path(item["path"]).suffix.lower() == ".unitypackage"]
    if len(inputs) != 1 or literal(evidence["package"]) != literal(inputs[0]["path"]) or evidence.get("packageBytes") != inputs[0]["bytes"]:
        raise ValueError("Missing texture proof does not bind this product's sole original Unitypackage")
    archive = literal(evidence["package"])
    if not archive.is_file() or archive.stat().st_size != evidence["packageBytes"]:
        raise ValueError("The preserved original source archive is absent or changed size")
    if len(evidence.get("supplementalArchives", [])) != 3:
        raise ValueError("All three downloaded source supplements must have been inspected")
    for item in evidence["supplementalArchives"]:
        if item.get("unityMetadataFiles") != 0 or item.get("nestedUnitypackages") != [] or item.get("exactMissingGuidMatches") != []:
            raise ValueError("Source supplement contains unresolved original GUID recovery candidates")
    expected = {target["guid"]: "Assets/EmaceArt/PlasticineWorld/Terrain/" + Path(path).name for path, target in TARGETS.items()}
    if evidence.get("sourceTerrainPaths") != expected:
        raise ValueError("Original archive terrain identities differ from the exact two candidates")


def verify_runtime(report, manifest, manifest_raw, receipt_raw, headless, inputs):
    if (report.get("schemaVersion") != 1 or literal(report.get("project", "")) != headless
            or literal(report.get("manifestPath", "")) != headless.parent / "staging-manifest.json"
            or report.get("manifestSha256") != sha(manifest_raw) or report.get("apply") is not False
            or report.get("originalArchivesModified") is not False or report.get("scenesOpened") is not False
            or not report.get("completedUtc") or report.get("observedUnityErrors") != 0):
        raise ValueError("Runtime report is stale, incomplete, mutating or belongs to another project")
    proof = report.get("missingProviderTerrainDependencyProof", {})
    if (proof.get("proofVersion") != 1 or proof.get("status") != "unreferenced-by-other-root-assets"
            or not proof.get("startedUtc") or not proof.get("completedUtc")
            or proof.get("receiptSha256") != sha(receipt_raw)
            or not str(proof.get("method", "")).startswith("AssetDatabase.GetDependencies(")
            or "recursive:true" not in proof.get("method", "")):
        raise ValueError("Explicit completed full-root recursive runtime dependency proof is required")
    roots = sorted((ROOT + "/" + record["path"] for product in manifest["products"] for record in product["files"]
                    if not record["path"].lower().endswith(".meta") and record["path"] not in TARGETS), key=ordinal_key)
    if proof.get("rootAssetsChecked") != len(roots) or proof.get("rootPathsSha256") != sha("\n".join(roots).encode()):
        raise ValueError("Runtime input paths do not cover every current non-folder library asset except exactly two targets")
    if (type(proof.get("dependencyClosurePaths")) is not int or proof["dependencyClosurePaths"] < len(roots)
            or not SHA.fullmatch(str(proof.get("closurePathsSha256", "")))):
        raise ValueError("Runtime dependency closure evidence is missing")
    targets = proof.get("excludedTargets", [])
    if len(targets) != 2 or {row.get("path") for row in targets} != {ROOT + "/" + path for path in TARGETS}:
        raise ValueError("Runtime proof excluded a different asset set")
    for row in targets:
        relative = row["path"][len(ROOT) + 1:]
        body, meta = inputs[relative], inputs[relative + ".meta"]
        if (row.get("guid") != TARGETS[relative]["guid"] or row.get("canonicalSha256") != body["sha256"]
                or row.get("actualSha256") != body["sha256"] or row.get("sourceArtifactSha256") != body["sha256"]
                or row.get("bytes") != body["bytes"] or row.get("referencedByOtherRootAssets") is not False
                or row.get("checkedInboundReferences") != 0 or row.get("metadataPath") != row["path"] + ".meta"
                or row.get("metadataBytes") != meta["bytes"] or row.get("metadataSha256") != meta["sha256"]
                or row.get("canonicalMetadataSha256") != meta["sha256"]):
            raise ValueError("Runtime target payload/meta/GUID/inbound-reference proof no longer matches current bytes")
    if report.get("status") != "dependency-proof-complete" or report.get("errors") != [] or report.get("blockers") != []:
        raise ValueError("Only a clean completed explicit dependency-proof job is accepted")


def quarantine(project, runtime_path, missing_path, apply=False, editor_stopped=False,
               expected_manifest=None, expected_runtime=None, expected_missing=None):
    project = literal(project)
    work = child(project, "Library/YamyamAssetLibrary")
    headless = child(work, "headless-project")
    stage = child(headless, ROOT)
    manifest_path = child(work, "staging-manifest.json")
    manifest, original_manifest = json_input(manifest_path)
    if (literal(manifest["stageRoot"]) != stage or manifest.get("targetAssetRoot", ROOT) != ROOT
            or len(manifest["products"]) != 84 or any(p.get("status") != "complete" or not p.get("files") for p in manifest["products"])):
        raise ValueError("Only the complete84-product isolated current library may be quarantined")
    products = {p["id"]: p for p in manifest["products"]}
    if len(products) != 84 or products.get("033", {}).get("folder") != FOLDER:
        raise ValueError("Canonical product identity differs")
    product = products["033"]
    exact_paths = set(TARGETS) | {path + ".meta" for path in TARGETS}
    if any(exact_paths & (set(p.get("originalBinaryGuidCollisionBlockers", []))
                          | {row["path"] for row in p.get("binaryGuidRecoveryProofs", [])}) for p in manifest["products"]):
        raise ValueError("SourceOnly must not alter the original896 binary-audit coverage")
    guid_owners = {}
    for owner in manifest["products"]:
        for record in owner["files"]:
            if not record["path"].lower().endswith(".meta"):
                continue
            for value in (record.get("guid"), record.get("originalGuid"), record.get("source", {}).get("originalGuid")):
                if value and str(value).lower() in MISSING:
                    raise ValueError("A current canonical original texture recovery candidate exists; SourceOnly is forbidden")
            if record.get("guid"):
                guid_owners.setdefault(record["guid"], []).append(record["path"])
    for relative, target in TARGETS.items():
        if guid_owners.get(target["guid"]) != [relative + ".meta"]:
            raise ValueError("TerrainData GUID does not have exactly one canonical metadata owner")
    receipt_path = child(work, "receipts/033.json")
    receipt, receipt_raw = json_input(receipt_path)
    if receipt != product:
        raise ValueError("Product033 receipt differs from canonical manifest")
    runtime_path, missing_path = literal(runtime_path), literal(missing_path)
    if not runtime_path.is_relative_to(headless / "Library/YamyamAssetLibrary") or not missing_path.is_relative_to(work):
        raise ValueError("Proof reports must be local owned library evidence")
    runtime, runtime_raw = json_input(runtime_path)
    missing, missing_raw = json_input(missing_path)
    records = {r["path"]: r for r in product["files"]}
    inputs, originals = {}, {}
    for relative, target in TARGETS.items():
        for candidate in (relative, relative + ".meta"):
            if candidate not in records:
                raise ValueError("Exact candidate is absent/already quarantined: " + candidate)
            raw = read_bytes(child(stage, candidate))
            record = records[candidate]
            if sha(raw) != record["sha256"] or len(raw) != record["bytes"]:
                raise ValueError("Candidate differs from canonical SHA/bytes: " + candidate)
            inputs[candidate] = {"sha256": sha(raw), "bytes": len(raw)}
            originals[candidate] = raw
        meta = originals[relative + ".meta"]
        match = re.search(rb"(?m)^guid:[ \t]*([a-f0-9]{32})", meta)
        if not match or match.group(1).decode() != target["guid"] or records[relative + ".meta"].get("guid") != target["guid"]:
            raise ValueError("Original TerrainData metadata GUID changed")
        verify_current_missing_references(originals[relative], target, work)
    verify_missing_evidence(missing, product)
    verify_runtime(runtime, manifest, original_manifest, receipt_raw, headless, inputs)
    if apply:
        if (not editor_stopped or expected_manifest != sha(original_manifest)
                or expected_runtime != sha(runtime_raw) or expected_missing != sha(missing_raw)):
            raise ValueError("Apply needs stopped Editor and all three exact reviewed input hashes")
        SAFE.editor_lock_guard(work)
    run = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_root = child(work, "source-only-quarantine/" + run)
    run_root.mkdir(parents=True)
    report_path = run_root / "report.json"
    quarantine_root = child(work, "SourceOnly")
    destinations = {relative: child(quarantine_root, relative) for relative in originals}
    if any(os.path.lexists(path) for path in destinations.values()):
        raise ValueError("A SourceOnly destination already exists; overwrite is forbidden")
    report = {"schemaVersion": 1, "run": run, "status": "prepared" if apply else "dry-run-ready", "apply": apply,
              "sourceManifestSha256": sha(original_manifest), "sourceRuntimeProofSha256": sha(runtime_raw), "sourceMissingEvidenceSha256": sha(missing_raw),
              "runtimeProof": str(runtime_path), "missingEvidence": str(missing_path), "sourceArchivesModified": False,
              "actualMainAssetsModified": False, "replacementTexturesInferred": False, "files": [
                  {"path": relative, **proof, "destination": str(destinations[relative]), "originalRecord": records[relative]} for relative, proof in inputs.items()]}
    atomic_write(report_path, encoded(report))
    latest = child(work, "source-only-quarantine-latest.json")
    atomic_write(latest, encoded({"report": str(report_path), "status": report["status"], "files": 4, "terrainAssets": 2}))
    if not apply:
        return report, report_path
    updated = copy.deepcopy(manifest)
    updated_product = next(p for p in updated["products"] if p["id"] == "033")
    updated_product["files"] = [record for record in updated_product["files"] if record["path"] not in originals]
    for row in report["files"]:
        preserved = copy.deepcopy(row["originalRecord"])
        preserved.update(preservedPath=row["destination"], sourceOnlyReason="unused-provider-terrain-missing-original-textures",
                         sourceOnlyRun=run, runtimeProofSha256=sha(runtime_raw), missingEvidenceSha256=sha(missing_raw))
        updated_product.setdefault("sourceOnlyFiles", []).append(preserved)
    updated_product.setdefault("sourceOnlyHistory", []).append({"run": run, "report": str(report_path), "terrainAssets": 2, "files": 4})
    if "finalImportFileCount" in updated_product:
        updated_product["finalImportFileCount"] = len(updated_product["files"])
    updated.setdefault("sourceOnlyHistory", []).append({"run": run, "report": str(report_path), "productId": "033", "files": 4})
    updated["updatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    summary = updated.setdefault("summary", {})
    summary.update(files=sum(len(p["files"]) for p in updated["products"]), bytes=sum(r["bytes"] for p in updated["products"] for r in p["files"]),
                   sourceOnlyFiles=sum(len(p.get("sourceOnlyFiles", [])) for p in updated["products"]))
    outputs = [(receipt_path, receipt_raw, encoded(updated_product)), (manifest_path, original_manifest, encoded(updated))]
    for relative, raw in originals.items():
        write_new(child(run_root / "backups", relative), raw)
    for name, raw in (("manifest.json", original_manifest), ("receipt033.json", receipt_raw), ("runtime-proof.json", runtime_raw), ("missing-evidence.json", missing_raw)):
        write_new(run_root / name, raw)
    SAFE.editor_lock_guard(work)
    if read_bytes(manifest_path) != original_manifest or read_bytes(receipt_path) != receipt_raw or read_bytes(runtime_path) != runtime_raw or read_bytes(missing_path) != missing_raw:
        raise ValueError("Canonical/proof evidence changed during preparation")
    for relative, raw in originals.items():
        if read_bytes(child(stage, relative)) != raw:
            raise ValueError("Candidate changed during preparation")
    moved, written = [], []
    try:
        for relative, destination in destinations.items():
            source = child(stage, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            literal(destination)
            if os.path.lexists(destination) or sha(read_bytes(source)) != inputs[relative]["sha256"]:
                raise ValueError("Source/destination changed immediately before owned move")
            os.rename(source, destination)
            moved.append((source, destination, inputs[relative]))
            if sha(read_bytes(destination)) != inputs[relative]["sha256"] or source.exists():
                raise ValueError("Moved source bytes were not preserved exactly")
        for path, before, after in outputs:
            if read_bytes(path) != before:
                raise ValueError("Canonical bookkeeping changed before transaction write")
            atomic_write(path, after)
            written.append((path, before, after))
        report.update(status="complete", completedUtc=dt.datetime.now(dt.timezone.utc).isoformat(), updatedManifestSha256=sha(outputs[-1][2]))
        atomic_write(report_path, encoded(report))
        atomic_write(latest, encoded({"report": str(report_path), "status": "complete", "files": 4, "terrainAssets": 2}))
    except BaseException as error:
        rollback_errors = []
        for path, raw, committed in reversed(written):
            try:
                if read_bytes(path) != committed:
                    raise ValueError("Rollback conflict: preserve a later foreign canonical write")
                atomic_write(path, raw)
            except BaseException as failure:
                rollback_errors.append({"path": str(path), "error": str(failure)})
        for source, destination, expected in reversed(moved):
            try:
                if os.path.lexists(source) or not destination.exists():
                    raise ValueError("Rollback source/destination unexpectedly changed")
                current = read_bytes(destination)
                if sha(current) != expected["sha256"] or len(current) != expected["bytes"]:
                    raise ValueError("Rollback conflict: preserve foreign-modified SourceOnly bytes; original backup remains")
                os.rename(literal(destination), literal(source))
            except BaseException as failure:
                rollback_errors.append({"path": str(source), "error": str(failure)})
        report.update(status="failed", error=str(error), rollbackErrors=rollback_errors)
        atomic_write(report_path, encoded(report))
        atomic_write(latest, encoded({"report": str(report_path), "status": "failed", "files": 4, "terrainAssets": 2}))
        raise
    return report, report_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--runtime-proof", type=Path)
    parser.add_argument("--missing-evidence", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--editor-stopped", action="store_true")
    parser.add_argument("--expected-manifest-sha256")
    parser.add_argument("--expected-runtime-proof-sha256")
    parser.add_argument("--expected-missing-evidence-sha256")
    args = parser.parse_args()
    work = args.project / "Library/YamyamAssetLibrary"
    runtime = args.runtime_proof or work / "headless-project/Library/YamyamAssetLibrary/terrain-normalization-report.json"
    missing = args.missing_evidence or work / "product033-missing-texture-package-evidence.json"
    report, path = quarantine(args.project, runtime, missing, args.apply, args.editor_stopped,
                              args.expected_manifest_sha256, args.expected_runtime_proof_sha256, args.expected_missing_evidence_sha256)
    print(json.dumps({"status": report["status"], "report": str(path), "files": len(report["files"]), "terrainAssets": 2}))


if __name__ == "__main__":
    main()
