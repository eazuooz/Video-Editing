"""Build a reviewable, read-only source rewrite plan from VendorCodeAudit output."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--compiler-ports-only", action="store_true", help="After initial scoping, prepare only the two verified Unity6 compiler/API ports.")
    parser.add_argument("--pipeline-closure-only", action="store_true", help="Prepare the verified dependency closure of the optional particles setup UI.")
    parser.add_argument("--editor-helper-cleanup-only", action="store_true", help="Prepare the verified empty cross-product RainbowHierarchy scene helper cleanup.")
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8-sig"))
    root = args.out.parent / "adapted-source-candidates"
    operations, groups = {}, {}
    scripts = audit["scripts"]
    by_path = {script["path"]: script for script in scripts}

    def operation(script):
        return operations.setdefault(script["path"], {
            "inputPath": script["absolutePath"], "expectedSha256": script["sha256"],
            "outputPath": str(root / script["path"]), "namespaceMap": {}, "literalMap": {},
            "globalNamespace": None, "wholeFileGuard": None, "reasons": [],
        })

    def tourist_editor_helper():
        prefix = scripts[0]["absolutePath"]
        stage = Path(prefix)
        for _ in Path(scripts[0]["path"]).parts:
            stage = stage.parent
        relative = "047-philipp-stylized-modular-low-poly-character/EmaceArt/Character#1 PHILIPP/Tourists/Demo/Tourist_Test.unity"
        return {"path": relative, "expectedSha256": hashlib.sha256((stage / relative).read_bytes()).hexdigest(),
                "gameObjectName": "RainbowHierarchyConf", "gameObjectFileId": 458783852, "componentFileId": 458783853,
                "transformFileId": 458783854, "parentTransformFileId": 1979556762, "scriptFileId": -1056051954,
                "scriptGuid": "ebe26e22332665d4c8332b2a624e5e8b", "emptyFields": {"HierarchyItems": "[]", "ShowContent": "0"},
                "reason": "Remove only the verified empty EditorOnly hierarchy configuration and its exact parent-child list entry; preserve every model and other System child."}

    if args.editor_helper_cleanup_only:
        report = {"sourceAudit": str(args.audit), "manifestSha256": audit["manifestSha256"], "readOnlyPlan": True,
                  "vendorInputsChanged": False, "operations": [], "productTypeMaps": {}, "shaderCustomEditorChanges": [],
                  "emptyEditorSceneObjects": [tourist_editor_helper()]}
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"plan": str(args.out), "sceneHelpers": 1, "vendorInputsChanged": False}))
        return

    if args.pipeline_closure_only:
        for script in scripts:
            if script["product"] == "052" and Path(script["path"]).name == "EA_URPModule.cs":
                change = operation(script)
                change["wholeFileGuard"] = "UNITY_EDITOR && YAMYAM_ASSET_LIBRARY_ENABLE_VENDOR_SETUP"
                change["reason"] = "Manual URP pipeline-module depends on the optional automatic setup UI; preserve its entire source behind the same explicit opt-in. No runtime asset dependencies."
        if len(operations) != 1:
            raise ValueError("Expected exactly one reviewed particles pipeline dependency file")
        report = {"sourceAudit": str(args.audit), "manifestSha256": audit["manifestSha256"], "readOnlyPlan": True,
                  "vendorInputsChanged": False, "operations": list(operations.values()), "productTypeMaps": {}, "shaderCustomEditorChanges": []}
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        (args.out.parent / "vendor-source-rewrite-operations.json").write_text(json.dumps(report["operations"], ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"plan": str(args.out), "sourceOperations": len(operations), "pipelineClosureOnly": True, "vendorInputsChanged": False}))
        return

    if args.compiler_ports_only:
        for script in scripts:
            filename = Path(script["path"]).name
            if script["product"] == "000" and filename == "CoreSourceDownloader.cs":
                change = operation(script)
                change["portZipExtraction"] = True
                change["reason"] = "Keep the manual core-source download menu; replace its missing SharpZip ZIP extraction with framework ZipFile API."
            if script["product"] == "017" and filename == "CausticsFeature.cs":
                change = operation(script)
                change["portCausticsRenderGraph"] = True
                change["reason"] = "Port the real additive camera-color/depth pass to URP17.6 RenderGraph; preserve uniforms, shader and original legacy methods. Original optional CausticsEffect shader is absent; existing null guard skips it."
        if len(operations) != 2:
            raise ValueError("Expected exactly two reviewed compiler/API port files")
        report = {"sourceAudit": str(args.audit), "manifestSha256": audit["manifestSha256"], "readOnlyPlan": True,
                  "vendorInputsChanged": False, "operations": list(operations.values()), "productTypeMaps": {}, "shaderCustomEditorChanges": []}
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        (args.out.parent / "vendor-source-rewrite-operations.json").write_text(json.dumps(report["operations"], ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"plan": str(args.out), "sourceOperations": len(operations), "compilerPortsOnly": True, "vendorInputsChanged": False}))
        return

    # Partial declarations of the same type in one product are valid, not a collision.
    # Product scoping cannot resolve a same-product declaration group anyway; valid partial
    # GameFramework declarations and any genuine same-product bug are kept out of this pass.
    collisions = [group for group in audit["duplicateTypes"] if len({owner["product"] for owner in group["owners"]}) > 1]
    owners = [owner for group in collisions for owner in group["owners"]]
    owners.extend(audit["existingMainTypeCollisions"])
    for owner in owners:
        script = by_path[owner["path"]]
        namespace = owner["ns"]
        key = (script["product"], namespace) if namespace else (script["product"], script["path"])
        groups[key] = namespace
    for (product, group), namespace in groups.items():
        prefix = f"Yamyam.Imported.P{product}"
        candidates = [script for script in scripts if script["product"] == product and (
            any(declaration["ns"] == namespace or declaration["ns"].startswith(namespace + ".") for declaration in script["declarations"])
            if namespace else script["path"] == group)]
        for script in candidates:
            change = operation(script)
            if namespace:
                change["namespaceMap"][namespace] = prefix + "." + namespace
            else:
                change["globalNamespace"] = prefix
            change["reasons"].append("Product-scoped genuine duplicate type; keep filename and MonoScript.meta GUID.")

    setup = []
    editor_assemblies = {}
    for script in scripts:
        if script["product"] == "052" and Path(script["path"]).name == "EA_URPModule.cs":
            change = operation(script)
            change["wholeFileGuard"] = "UNITY_EDITOR && YAMYAM_ASSET_LIBRARY_ENABLE_VENDOR_SETUP"
            change["reasons"].append("Manual URP module is the verified dependency closure of the optional automatic setup UI.")
        automatic = set(script["automaticAttributes"])
        if not automatic.intersection({"InitializeOnLoad", "InitializeOnLoadMethod", "DidReloadScripts"}):
            continue
        filename = Path(script["path"]).name
        if script["product"] == "018":
            # The assembly is the dependency closure of each identified automatic UI tool;
            # constraining it avoids undefined sibling references after its source is gated.
            change = operation(script)
            change["wholeFileGuard"] = "UNITY_EDITOR && YAMYAM_ASSET_LIBRARY_ENABLE_VENDOR_EDITOR_TOOLS"
            change["reasons"].append("Identified automatic Editor UI callback; explicit opt-in preserves the user's editor.")
            if script.get("asmdefPath"):
                editor_assemblies[script["asmdefPath"]] = "YAMYAM_ASSET_LIBRARY_ENABLE_VENDOR_EDITOR_TOOLS"
        elif filename.endswith("_ProjectSetup.cs") or filename in {"EA_ParticlesPipelineSetup.cs", "ReadmeEditor.cs"}:
            change = operation(script)
            change["wholeFileGuard"] = "UNITY_EDITOR && YAMYAM_ASSET_LIBRARY_ENABLE_VENDOR_SETUP"
            change["reasons"].append("Automatic welcome/pipeline/package/scene setup is opt-in; no global symbols enabled.")
            setup.append(script["path"])

    # Player guards only for actual unguarded pure-Editor classes. Mixed runtime settings
    # require a manual conditional implementation, not deletion of their runtime types.
    mixed_settings = []
    for script in scripts:
        if not script["unguardedEditorOnlyCode"]:
            continue
        if all(any(base in {"EditorWindow", "ShaderGUI", "EditorTool", "Editor"} for base in declaration["baseTypes"])
               or "+" in declaration["metadataFullName"] for declaration in script["declarations"]):
            change = operation(script)
            change["wholeFileGuard"] = change["wholeFileGuard"] or "UNITY_EDITOR"
            change["reasons"].append("Editor-only window outside Editor assembly needs a player compilation guard.")
        else:
            mixed_settings.append(script["path"])

    # These reviewed mixed settings retain every serialized field/type. Only their
    # AssetDatabase-backed accessors and persistence methods need player fallbacks.
    for script in scripts:
        filename = Path(script["path"]).name
        if script["product"] == "018" and filename in {"SmartHierarchySettings.cs", "SceneNotesSettings.cs"}:
            change = operation(script)
            change["guardEditorUsings"] = True
            change["conditionalEditorMembers"] = ({
                "Instance.get": "if (_instance == null) _instance = CreateInstance<SmartHierarchySettings>(); return _instance;",
                "SaveToDisk": "return;",
            } if filename == "SmartHierarchySettings.cs" else {
                "GetDataDirectoryPath": 'return Path.Combine(Application.persistentDataPath, "YamyamAssetLibrary", "SceneNotesData");',
                "LoadOrCreate": "return CreateInstance<SceneNotesSettings>();",
            })
            change["reasons"].append("Retain runtime settings and serialized fields; isolate Editor asset lookup/persistence from player compilation.")
            mixed_settings.remove(script["path"])
        if script["product"] == "000" and filename == "DefaultCompressionHelper.cs":
            if "Unity.SharpZipLib.GZip" not in script["usingNamespaces"]:
                raise ValueError("Expected the reviewed GZip integration dependency")
            change = operation(script)
            change["portGzip"] = True
            change["reasons"].append("Use framework GZipStream with leaveOpen; finish trailer before preserving the existing fixed MTIME header.")
        if script["product"] == "021" and filename == "TimeWarpAutoSetup.cs":
            change = operation(script)
            change["optionalCinemachineInjection"] = True
            change["reasons"].append("Retain optional Cinemachine injection without a core-to-adapter compile-time dependency or global package changes.")

    json_edits, extra_files = [], []
    for assembly in audit["assemblies"]:
        if assembly["product"] != "021" or assembly["definition"]["name"] != "TimeWarp.Runtime":
            continue
        json_edits.append({"path": assembly["path"], "expectedSha256": assembly["sha256"],
                           "removeReferences": ["Unity.Cinemachine", "Unity.VisualEffectGraph.Runtime"],
                           "reason": "Optional Cinemachine is isolated; VFX classes use installed engine UnityEngine.VFXModule, preserving core behavior."})
        camera_dir = Path(assembly["path"]).parent / "Modules/Cameras"
        definition = {"name": "TimeWarp.Cinemachine", "rootNamespace": "TimeWarp.Modules.Cameras",
                      "references": ["TimeWarp.Runtime", "Unity.Cinemachine"], "includePlatforms": [], "excludePlatforms": [],
                      "allowUnsafeCode": False, "overrideReferences": False, "precompiledReferences": [], "autoReferenced": True,
                      "defineConstraints": ["YAMYAM_TIMEWARP_CINEMACHINE_PRESENT"],
                      "versionDefines": [{"name": "com.unity.cinemachine", "expression": "3.0.0", "define": "YAMYAM_TIMEWARP_CINEMACHINE_PRESENT"}],
                      "noEngineReferences": False}
        relative = (camera_dir / "TimeWarp.Cinemachine.asmdef").as_posix()
        guid = hashlib.sha256(("YamyamAssetLibrary:" + relative).encode()).hexdigest()[:32]
        reason = "Optional Cinemachine3 adapter assembly activates only when its package is present; source and MonoScript GUIDs remain in place."
        extra_files.extend([{"path": relative, "text": json.dumps(definition, indent=2) + "\n", "reason": reason},
                            {"path": relative + ".meta", "text": "fileFormatVersion: 2\nguid: " + guid + "\nAssemblyDefinitionImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n", "reason": reason}])

    plugin_changes, scene_objects = [], []
    for dll in audit["dlls"]:
        if dll["assembly"] not in {"JMOAssets_CartoonFXFreeWelcome", "RainbowHierarchy"}:
            continue
        path = Path(dll["absolutePath"] + ".meta")
        plugin_changes.append({"path": dll["path"] + ".meta", "expectedSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                               "symbol": "YAMYAM_ASSET_LIBRARY_ENABLE_VENDOR_EDITOR_TOOLS",
                               "reason": "PE metadata proves optional automatic Editor tooling; disable importer targets by default, preserving DLL bytes and GUID."})
        if dll["assembly"] == "RainbowHierarchy":
            stage = Path(dll["absolutePath"])
            for _ in Path(dll["path"]).parts:
                stage = stage.parent
            relative = dll["path"].split("/")[0] + "/EmaceArt/EpicMobile 3d Voxel Forest And Atols - Winter/Scenes/EpicWoodland_Winter.unity"
            scene_objects.append({"path": relative, "expectedSha256": hashlib.sha256((stage / relative).read_bytes()).hexdigest(),
                                  "gameObjectName": "RainbowHierarchyRuleset", "gameObjectFileId": 1338581092,
                                  "componentFileId": 1338581093, "transformFileId": 1338581094,
                                  "scriptFileId": 366663908, "scriptGuid": "ebe26e22332665d4c8332b2a624e5e8b",
                                  "reason": "Remove the proven empty standalone EditorOnly hierarchy-rules helper after verifying zero external references; models and prefabs unchanged."})
            scene_objects.append(tourist_editor_helper())

    type_maps = {}
    for path, change in operations.items():
        script = by_path[path]
        mapping = type_maps.setdefault(script["product"], {})
        for declaration in script["declarations"]:
            before = declaration["metadataFullName"]
            after = before
            if change["globalNamespace"]:
                after = change["globalNamespace"] + "." + before
            for old, new in change["namespaceMap"].items():
                if before == old or before.startswith(old + "."):
                    after = new + before[len(old):]
            if after != before:
                mapping[before] = after

    shader_changes = []
    for shader in audit["shaders"]:
        mapping = type_maps.get(shader["product"], {})
        editors = {editor: mapping[editor] for editor in shader["customEditors"] if editor in mapping}
        if editors:
            shader_changes.append({"inputPath": shader["absolutePath"], "path": shader["path"],
                                   "expectedSha256": shader["sha256"], "customEditorMap": editors})

    # Names assigned by GUID can coexist. Scope a duplicate shader name only where a
    # product actually calls Shader.Find, retaining that exact lookup's intended owner.
    shader_names = {}
    for duplicate in audit.get("duplicateShaderNames", []):
        name = duplicate["shaderName"]
        if len({owner["product"] for owner in duplicate["owners"]}) < 2:
            continue
        for owner in duplicate["owners"]:
            product = owner["product"]
            if not any(script["product"] == product and name in script["shaderFindNames"] for script in scripts):
                continue
            prefix = f"YamyamAssetLibrary/P{product}/"
            scoped = "Hidden/" + prefix + name[len("Hidden/"):] if name.startswith("Hidden/") else prefix + name
            shader_names.setdefault(product, {})[name] = scoped
            for script in scripts:
                if script["product"] == product and name in script["shaderFindNames"]:
                    change = operation(script)
                    change["literalMap"][name] = scoped
                    change["reasons"].append("Keep an actual Shader.Find lookup linked to this product's duplicate-named shader.")

    for change in operations.values():
        change["reason"] = " ".join(dict.fromkeys(change.pop("reasons")))
    report = {
        "sourceAudit": str(args.audit), "manifestSha256": audit["manifestSha256"],
        "readOnlyPlan": True, "vendorInputsChanged": False,
        "operations": list(operations.values()), "productTypeMaps": type_maps,
        "shaderCustomEditorChanges": shader_changes,
        "shaderNameMaps": shader_names,
        "shaderRelocationFiles": [{"inputPath": shader["absolutePath"], "path": shader["path"], "expectedSha256": shader["sha256"],
                                   "mapping": shader_names[shader["product"]]} for shader in audit["shaders"] if shader["product"] in shader_names],
        "serializedClassFieldsToCheck": ["m_EditorClassIdentifier", "managedReferenceFullTypename", "managedReference type/ns"],
        "editorToolOptInAssemblyConstraints": editor_assemblies,
        "missingEditorFeelCoreOptInAssemblies": [entry["path"] for entry in audit["assemblies"]
                                                 if entry["product"] == "018" and "EditorFeel.Core" in entry["definition"].get("references", [])],
        "mixedRuntimeSettingsNeedConditionalEditorAPIs": mixed_settings,
        "jsonEdits": json_edits, "extraFiles": extra_files,
        "pluginImporterOptIn": plugin_changes, "emptyEditorSceneObjects": scene_objects,
        "manualIntegrations": [
            "021: Cameras folder contains only two Cinemachine classes: add optional TimeWarp.Cinemachine asmdef using package version constraint; core AutoSetup uses optional reflection injection, not a compile-time circular reference.",
            "021: Remove Unity.VisualEffectGraph.Runtime reference only after engine VFXModule reference confirmed; preserve VFX classes and graph source.",
            "000: Replace four SharpZipLib GZip stream constructions with System.IO.Compression.GZipStream, finalize compression before existing ProcessHeader, preserve caller streams.",
            "Pure Editor DLL opt-in importer metadata requires PE metadata and serialized runtime-reference verification first.",
        ],
    }
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out.parent / "vendor-source-rewrite-operations.json").write_text(json.dumps(report["operations"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"plan": str(args.out), "sourceOperations": len(operations), "customEditorShaders": len(shader_changes),
                      "editorToolAssemblies": len(editor_assemblies), "mixedSettings": len(mixed_settings), "vendorInputsChanged": False}))


if __name__ == "__main__":
    main()
