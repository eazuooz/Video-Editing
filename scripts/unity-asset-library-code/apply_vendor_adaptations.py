"""Apply reviewed, hash-checked local integration candidates to an idle completed stage.

Paid vendor source is read from the local stage and backed up under Library only.
This generic tool contains no copied vendor source bodies. Original archives, the
real Unity Assets tree, package manifests and project settings are never edited.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def write_bytes_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".yamyam-adapt.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def safe_child(root, relative):
    target = (root / str(relative).replace("\\", "/")).resolve()
    if target == root.resolve() or not target.is_relative_to(root.resolve()):
        raise ValueError(f"Path is outside the owned stage: {relative}")
    return target


def disable_editor_plugin(data, symbol):
    text = data.decode("utf-8-sig").replace("\r\n", "\n")
    if "PluginImporter:" not in text:
        raise ValueError("Expected PluginImporter metadata")
    original_guid = re.search(r"(?m)^guid:\s*([a-fA-F0-9]{32})", text).group(1)
    if re.search(r"(?m)^  defineConstraints:", text):
        text, count = re.subn(r"(?m)^  defineConstraints:[ \t]*\[\][ \t]*$",
                              "  defineConstraints:\n  - " + symbol, text)
        if count != 1:
            raise ValueError("Expected exactly one initially empty plugin constraint list")
    else:
        # Unity's older repeated-data PluginImporter schema predates this field.
        # Adding a constraint does not change the DLL bytes or MonoScript GUIDs.
        text, count = re.subn(r"(?m)^  platformData:", "  defineConstraints:\n  - " + symbol + "\n  platformData:", text)
        if count != 1:
            raise ValueError("Expected one PluginImporter platformData field")
    match = re.search(r"(?ms)^  platformData:\r?\n(?P<platforms>.*?)(?=^  [A-Za-z_][A-Za-z_0-9]*:|\Z)", text)
    if not match:
        raise ValueError("PluginImporter platformData was not found")
    platforms = match.group("platforms")
    if not re.search(r"(?m)^\s+(?:Any:[ \t]*|:[ \t]*Any)[ \t]*$", platforms) or not re.search(r"(?m)^\s+Editor:[ \t]*Editor[ \t]*$", platforms):
        raise ValueError("Expected explicitly inspected Editor and Any platform entries")
    # These reviewed DLLs contain only optional editor tooling. Disable every
    # import target, handling both old repeated-data and current sequence YAML.
    platforms, count = re.subn(r"(?m)^(\s+enabled:[ \t]*)[01][ \t]*$", r"\g<1>0", platforms)
    if count < 2:
        raise ValueError("Expected at least two plugin platform enabled flags")
    text = text[:match.start("platforms")] + platforms + text[match.end("platforms"):]
    if re.search(r"(?m)^guid:\s*([a-fA-F0-9]{32})", text).group(1) != original_guid:
        raise ValueError("Plugin GUID changed unexpectedly")
    return text.encode("utf-8")


def remove_empty_editor_scene_object(data, item):
    """Remove only a reviewed empty EditorOnly helper, with no external references."""
    text = data.decode("utf-8-sig")
    headers = list(re.finditer(r"(?m)^--- !u!(\d+) &(-?\d+)(?: stripped)?\r?\n", text))
    documents = {match.group(2): (match, text[match.start():headers[index + 1].start() if index + 1 < len(headers) else len(text)])
                 for index, match in enumerate(headers)}
    game_id, script_id, transform_id = (str(item[name]) for name in ("gameObjectFileId", "componentFileId", "transformFileId"))
    selected = {key: documents[key] for key in (game_id, script_id, transform_id)}
    if [selected[key][0].group(1) for key in (game_id, script_id, transform_id)] != ["1", "114", "4"]:
        raise ValueError("Expected exactly GameObject, MonoBehaviour and Transform scene documents")
    game, script, transform = (selected[key][1] for key in (game_id, script_id, transform_id))
    if not re.search(r"(?m)^  m_TagString: EditorOnly\r?$", game) or not re.search(r"(?m)^  m_Name: " + re.escape(item["gameObjectName"]) + r"\r?$", game):
        raise ValueError("Reviewed scene object identity or EditorOnly tag changed")
    components = re.findall(r"(?m)^  - component: \{fileID: (-?\d+)\}\r?$", game)
    if set(components) != {script_id, transform_id} or len(components) != 2:
        raise ValueError("Editor-only object gained another component")
    parent_id = str(item.get("parentTransformFileId", 0))
    if not re.search(r"(?m)^  m_Children: \[\]\r?$", transform) or not re.search(r"(?m)^  m_Father: \{fileID: " + re.escape(parent_id) + r"\}\r?$", transform):
        raise ValueError("Editor-only object must have the reviewed parent and no children")
    expected_script = r"(?m)^  m_Script: \{fileID: " + re.escape(str(item["scriptFileId"])) + r", guid: " + re.escape(item["scriptGuid"]) + r", type: 3\}\r?$"
    empty_fields = item.get("emptyFields", {"Rules": "[]"})
    if not re.search(expected_script, script) or any(not re.search(r"(?m)^  " + re.escape(key) + ": " + re.escape(value) + r"\r?$", script) for key, value in empty_fields.items()):
        raise ValueError("Editor helper script identity or empty rules changed")
    custom_fields = set(re.findall(r"(?m)^  (?!m_)(\w+):", script))
    if custom_fields != set(empty_fields):
        raise ValueError("Editor helper has additional unreviewed serialized data")
    for document in (script, transform):
        if not re.search(r"(?m)^  m_GameObject: \{fileID: " + re.escape(game_id) + r"\}\r?$", document):
            raise ValueError("Editor helper components do not belong to the reviewed object")
    result = text[:headers[0].start()] if headers else text
    for key, (header, document) in documents.items():
        if key in selected:
            continue
        references = list(re.finditer(r"\bfileID:[ \t]*(" + "|".join(map(re.escape, selected)) + r")\b", document))
        if references:
            parent_reference = header.group(1) == "4" and key == parent_id and parent_id != "0"
            if header.group(1) != "1660057539" and not parent_reference:
                raise ValueError("Another scene object references the Editor-only helper: " + key)
            document, count = re.subn(r"(?m)^  - \{fileID: " + re.escape(transform_id) + r"\}\r?\n", "", document)
            if count != len(references) or count != 1:
                raise ValueError("Unexpected root/parent list reference to Editor-only helper")
            document = re.sub(r"(?m)^  m_Children:\r?\n(?=  [A-Za-z_])", "  m_Children: []\n", document)
        result += document
    return result.encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()
    work = project / "Library/YamyamAssetLibrary"
    manifest_path = work / "staging-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
    stage = Path(manifest["stageRoot"]).resolve()
    allowed_stages = {(work / "staging/CreatorBundle").resolve(),
                      (work / "headless-project/Assets/ThirdParty/YamyamAssetLibrary").resolve()}
    if stage not in allowed_stages:
        raise ValueError("Only this project's local stage or isolated headless import copy may be edited")
    if any(product.get("status") != "complete" for product in manifest["products"]):
        raise ValueError("Every product must be recovered and complete before code adaptation")
    if plan["manifestSha256"] != sha(manifest_path.read_bytes()):
        raise ValueError("Manifest changed since the reviewed plan; refresh the read-only audit/plan")
    changes = {}

    def change(path, candidate, expected=None, reason=None, new=False):
        path = Path(path).resolve()
        if not path.is_relative_to(stage) or path == stage:
            raise ValueError(f"Refusing an edit outside the owned stage: {path}")
        before = path.read_bytes() if path.exists() else None
        if before is None and not new:
            raise FileNotFoundError(path)
        if new and before is not None and before != candidate:
            raise ValueError(f"New integration path already contains different content: {path}")
        if expected and (before is None or sha(before) != expected):
            raise ValueError(f"Original hash changed: {path}")
        if before == candidate:
            return
        relative = path.relative_to(stage).as_posix()
        changes[relative] = {"path": path, "before": before, "after": candidate, "reason": reason or "Reviewed local integration adaptation."}

    for operation in plan["operations"]:
        change(operation["inputPath"], Path(operation["outputPath"]).read_bytes(), operation["expectedSha256"], operation["reason"])
    for item in plan["shaderCustomEditorChanges"]:
        path = Path(item["inputPath"])
        text = path.read_text(encoding="utf-8-sig")
        for old, new in item["customEditorMap"].items():
            text, count = re.subn(r'(\bCustomEditor(?:ForRenderPipeline)?\s+")' + re.escape(old) + r'(")',
                                  lambda match: match.group(1) + new + match.group(2), text)
            if count < 1:
                raise ValueError(f"Exact shader CustomEditor was not found: {path}: {old}")
        change(path, text.encode("utf-8"), item["expectedSha256"], "Keep this product's ShaderGUI linked to its scoped source type.")
    for item in plan.get("shaderRelocationFiles", []):
        path = Path(item["inputPath"])
        relative = path.resolve().relative_to(stage).as_posix()
        text = changes[relative]["after"].decode("utf-8-sig") if relative in changes else path.read_text(encoding="utf-8-sig")
        for old, new in item["mapping"].items():
            text = re.sub(r'(?m)^(\s*Shader\s+")' + re.escape(old) + r'(")', lambda match: match.group(1) + new + match.group(2), text)
            text = re.sub(r'(\bFallback\s+")' + re.escape(old) + r'(")', lambda match: match.group(1) + new + match.group(2), text)
            text = re.sub(r'(\bUsePass\s+")' + re.escape(old) + r'(/)', lambda match: match.group(1) + new + match.group(2), text)
        change(path, text.encode("utf-8"), item["expectedSha256"], "Keep an actual Shader.Find/UsePass lookup scoped to its verified product shader while preserving shader GUIDs.")
    assembly_guards = dict(plan.get("editorToolOptInAssemblyConstraints", {}))
    assembly_guards.update({relative: "YAMYAM_ASSET_LIBRARY_ENABLE_EDITORFEEL_MESHMODIFIERS"
                           for relative in plan.get("missingEditorFeelCoreOptInAssemblies", [])})
    for relative, symbol in assembly_guards.items():
        path = safe_child(stage, relative)
        definition = json.loads(path.read_text(encoding="utf-8-sig"))
        constraints = definition.setdefault("defineConstraints", [])
        if symbol not in constraints:
            constraints.append(symbol)
        change(path, (json.dumps(definition, ensure_ascii=False, indent=2) + "\n").encode(),
               reason="Opt-in dependency closure of an identified automatic Editor tool or missing optional EditorFeel.Core addon.")
    for item in plan.get("jsonEdits", []):
        path = safe_child(stage, item["path"])
        definition = json.loads(path.read_text(encoding="utf-8-sig"))
        for key, value in item.get("set", {}).items():
            definition[key] = value
        if "removeReferences" in item:
            definition["references"] = [reference for reference in definition.get("references", []) if reference not in item["removeReferences"]]
        change(path, (json.dumps(definition, ensure_ascii=False, indent=2) + "\n").encode(), item.get("expectedSha256"), item["reason"])
    for item in plan.get("extraFiles", []):
        change(safe_child(stage, item["path"]), item["text"].encode("utf-8"), reason=item["reason"], new=True)
    for item in plan.get("pluginImporterOptIn", []):
        path = safe_child(stage, item["path"])
        change(path, disable_editor_plugin(path.read_bytes(), item["symbol"]), item["expectedSha256"], item["reason"])
    for item in plan.get("emptyEditorSceneObjects", []):
        path = safe_child(stage, item["path"])
        change(path, remove_empty_editor_scene_object(path.read_bytes(), item), item["expectedSha256"], item["reason"])

    # Update only explicit serialized type-identity fields, never arbitrary prose or GUIDs.
    for product in manifest["products"]:
        mapping = plan.get("productTypeMaps", {}).get(product["id"], {})
        if not mapping:
            continue
        for record in product.get("files", []):
            if Path(record["path"]).suffix.lower() not in {".unity", ".prefab", ".asset"}:
                continue
            path = safe_child(stage, record["path"])
            raw = changes.get(record["path"], {}).get("after", path.read_bytes())
            if not raw.lstrip(b"\xef\xbb\xbf \r\n").startswith((b"%YAML", b"--- !u!")):
                continue
            text = raw.decode("utf-8-sig")
            def replace_identity(match):
                value = match.group(2)
                for old, new in sorted(mapping.items(), key=lambda pair: len(pair[0]), reverse=True):
                    value = re.sub(r"(?<![\w.+`])" + re.escape(old) + r"(?![\w.+`])", new, value)
                return match.group(1) + value
            updated = re.sub(r"(?m)^(\s*(?:m_EditorClassIdentifier|managedReferenceFullTypename):\s*)([^\r\n]*)$", replace_identity, text)
            def replace_managed_type(match):
                fields = match.group(0)
                class_name = re.search(r"\bclass:[ \t]*([^,}]+)", fields)
                namespace = re.search(r"\bns:[ \t]*([^,}]*)", fields)
                if not class_name or not namespace:
                    return fields
                before = (namespace.group(1).strip() + "." if namespace.group(1).strip() else "") + class_name.group(1).strip()
                after = mapping.get(before)
                if not after:
                    return fields
                new_namespace, _, new_class = after.rpartition(".")
                if new_class != class_name.group(1).strip():
                    raise ValueError("Namespace adaptation must preserve managed-reference class identity")
                return fields[:namespace.start(1)] + new_namespace + fields[namespace.end(1):]
            updated = re.sub(r"(?m)^\s*type:[ \t]*\{[^\r\n}]*\}", replace_managed_type, updated)
            if updated != text:
                change(path, updated.encode("utf-8"), reason="Preserve serialized full type identities after product namespace scoping; MonoScript GUIDs unchanged.")

    run = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report_path = work / "vendor-adaptation-report.json"
    report = {"schemaVersion": 1, "run": run, "applied": bool(args.apply), "stageRoot": str(stage),
              "originalArchivesModified": False, "actualProjectAssetsModified": False,
              "headlessProjectAssetsModified": stage == (work / "headless-project/Assets/ThirdParty/YamyamAssetLibrary").resolve(),
              "trackedTool": "scripts/unity-asset-library-code/apply_vendor_adaptations.py", "files": []}
    for relative, entry in sorted(changes.items()):
        report["files"].append({"path": relative, "originalSha256": sha(entry["before"]) if entry["before"] is not None else None,
                                "adaptedSha256": sha(entry["after"]), "bytes": len(entry["after"]), "reason": entry["reason"]})
    if not args.apply:
        write_json(work / "vendor-adaptation-dry-run.json", report)
        print(json.dumps({"apply": False, "files": len(changes), "report": str(work / "vendor-adaptation-dry-run.json")}))
        return
    # Prepare all metadata before writing any vendor file. Full backups and a
    # prepared receipt make an interrupted application recoverable; exceptions
    # roll back only the explicit owned paths written by this invocation.
    original_manifest = manifest_path.read_bytes()
    if sha(original_manifest) != plan["manifestSha256"]:
        raise ValueError("Manifest changed during candidate verification")
    metadata_changes = {}
    for product in manifest["products"]:
        owned = {relative: entry for relative, entry in changes.items() if relative.startswith(product["folder"] + "/")}
        if not owned:
            continue
        records = {record["path"]: record for record in product["files"]}
        for relative, entry in owned.items():
            if relative not in records:
                record = {"path": relative, "source": {"kind": "local-integration", "tool": report["trackedTool"]}}
                product["files"].append(record)
                records[relative] = record
            records[relative]["bytes"] = len(entry["after"])
            records[relative]["sha256"] = sha(entry["after"])
            if Path(relative).suffix.lower() in {".cs", ".dll", ".asmdef", ".asmref"} and relative not in product.setdefault("scripts", []):
                product["scripts"].append(relative)
        if product.get("codeAdaptation"):
            product.setdefault("codeAdaptationHistory", []).append(product["codeAdaptation"])
        product["codeAdaptation"] = {"run": run, "report": str(work / "adaptation-backups" / run / "report.json"), "files": len(owned)}
        receipt = work / "receipts" / (product["id"] + ".json")
        if receipt.exists():
            metadata_changes[receipt] = {"before": receipt.read_bytes(), "after": json.dumps(product, ensure_ascii=False, indent=2).encode("utf-8")}
    manifest["updatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    manifest["summary"] = {"products": len(manifest["products"]), "complete": sum(product["status"] == "complete" for product in manifest["products"]),
                           "blockedOrFailed": sum(product["status"] != "complete" for product in manifest["products"]),
                           "files": sum(len(product.get("files", [])) for product in manifest["products"]),
                           "bytes": sum(record["bytes"] for product in manifest["products"] for record in product.get("files", [])),
                           "guidRemaps": sum(len(product.get("guidRemaps", {})) for product in manifest["products"]),
                           "scripts": sum(len(product.get("scripts", [])) for product in manifest["products"])}
    if manifest.get("codeAdaptation"):
        manifest.setdefault("codeAdaptationHistory", []).append(manifest["codeAdaptation"])
    manifest["codeAdaptation"] = {"run": run, "report": str(work / "adaptation-backups" / run / "report.json"), "files": len(changes)}
    manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    metadata_changes[manifest_path] = {"before": original_manifest, "after": manifest_bytes}
    backup_root = work / "adaptation-backups" / run
    backup_root.mkdir(parents=True)
    shutil.copy2(args.plan, backup_root / "plan.json")
    if report_path.exists():
        shutil.copy2(report_path, backup_root / "previous-report.json")
        report["previousReport"] = str(backup_root / "previous-report.json")
    for relative, entry in changes.items():
        if entry["before"] is not None:
            backup = backup_root / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(entry["before"])
    for path, entry in metadata_changes.items():
        backup = backup_root / path.relative_to(work)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(entry["before"])
    report["status"] = "prepared"
    report["backupRoot"] = str(backup_root)
    write_json(report_path, report)
    written = []
    try:
        for relative, entry in sorted(changes.items()):
            current = entry["path"].read_bytes() if entry["path"].exists() else None
            if current != entry["before"]:
                raise ValueError("Source changed while applying reviewed plan: " + relative)
            write_bytes_atomic(entry["path"], entry["after"])
            written.append((entry["path"], entry["before"]))
        for path, entry in metadata_changes.items():
            if path.read_bytes() != entry["before"]:
                raise ValueError("Receipt changed while applying reviewed plan: " + str(path))
            write_bytes_atomic(path, entry["after"])
            written.append((path, entry["before"]))
    except BaseException as error:
        rollback_errors = []
        for path, original in reversed(written):
            try:
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    write_bytes_atomic(path, original)
            except BaseException as rollback_error:
                rollback_errors.append({"path": str(path), "error": str(rollback_error)})
        report.update(status="failed", applied=False, error=str(error), rollbackErrors=rollback_errors)
        write_json(report_path, report)
        write_json(backup_root / "report.json", report)
        raise
    report["status"] = "complete"
    report["manifestSha256"] = sha(manifest_bytes)
    write_json(report_path, report)
    write_json(backup_root / "report.json", report)
    print(json.dumps({"apply": True, "files": len(changes), "report": str(report_path), "manifestSha256": report["manifestSha256"]}))


if __name__ == "__main__":
    main()
