// Explicit one-material correction from verified FBX opacity, never alpha guessing.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;
using FileInfo = YamyamAssetLibraryIO.Info;

public static class YamyamAssetLibraryGlass
{
    const string ExpectedProject = "D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string Root = "Assets/ThirdParty/YamyamAssetLibrary";
    const string Folder = "008-polyvania-halloween-burton-town-948-spooky-low-poly-town-models-godot-unity-bl";
    const string MaterialRelative = Folder + "/Generated/Materials/Transylvania_Glass_Text_6982ccd17f00.mat";
    const string MaterialGuid = "82ccb08aa1f30f14ca0ef814970b1b08";
    const string ProofSha256 = "e71acaf4963eda11d93e6f7976189ceece561451873db0455ff3ba3714fde631";
    [Serializable] public sealed class Record { public string path, sha256, guid; public long bytes; }
    [Serializable] public sealed class Product { public string id, folder; public Record[] files; }
    [Serializable] public sealed class Manifest { public string stageRoot; public Product[] products; }
    [Serializable] public sealed class Target { public string path, guid, sha256, metadataSha256; public long bytes; }
    [Serializable] public sealed class SourceProof
    {
        public string kind, stageRoot; public int sourceFbxInspected, glassFbxCount, uniqueGlassSignatures;
        public bool actualAssetsModified, sourceArchivesModified; public Record[] sourceFiles, glassReferences; public Target targetMaterial;
    }
    [Serializable] public sealed class Report
    {
        public int schemaVersion = 1, observedUnityErrors;
        public string status = "checking", project, startedUtc, completedUtc, sourceProofSha256, materialPath, materialGuid;
        public string materialBeforeSha256, materialAfterSha256, metadataSha256, previewPath, previewPrefab;
        public string originalPreviewsSha256, originalRepresentative, originalRepresentativeImage, originalRepresentativeImageSha256;
        public bool originalRepresentativeDependsOnChangedMaterial;
        public string[] originalRepresentativeDependencies;
        public long localIdBefore, localIdAfter;
        public bool originalSourcesModified, sourceArchivesModified, scenesOpened, unrelatedAssetsSaved;
        public int sourceFbxVerified, referencingGeneratedPrefabs;
        public List<Record> prefabReferences = new List<Record>();
        public List<string> errors = new List<string>();
        public string scope = "Only the positively proved P008 Transylvania_Glass_Text shared material. FBX exports explicit opacity0.28 and no texture connection. No atlas/emission is invented. All sourceFBX/prefab bytes and stable materialGUID remain unchanged.";
    }
    static string Project { get { return YamyamAssetLibraryIO.NormalPath(Path.GetDirectoryName(Application.dataPath)); } }
    static string Work { get { return YamyamAssetLibraryIO.NormalPath(Path.Combine(Project, "..")); } }
    static string Absolute(string path) { return Path.Combine(Project, path.Replace('/', Path.DirectorySeparatorChar)); }
    static string Utc() { return DateTime.UtcNow.ToString("o"); }
    static string HashFile(string path) { using (var input = File.OpenRead(path)) using (var hash = SHA256.Create()) return BitConverter.ToString(hash.ComputeHash(input)).Replace("-", "").ToLowerInvariant(); }
    static void Guard()
    {
        if (!Application.isBatchMode || !string.Equals(Project.Replace('\\', '/'), ExpectedProject, StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Glass correction requires the exact isolated batch project.");
    }
    static void NoLinks(string path)
    {
        string full = YamyamAssetLibraryIO.NormalPath(path), boundary = Work;
        if (!full.StartsWith(boundary + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) && !full.Equals(boundary, StringComparison.OrdinalIgnoreCase)) throw new IOException("Path escaped owned workspace.");
        for (string current = full; !string.IsNullOrEmpty(current); current = Path.GetDirectoryName(current)) {
            try { if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0) throw new IOException("Reparse point refused."); }
            catch (FileNotFoundException) { } catch (DirectoryNotFoundException) { }
            if (current.Equals(Path.GetPathRoot(full), StringComparison.OrdinalIgnoreCase)) return;
        }
        throw new IOException("Volume ownership guard did not finish.");
    }
    static string GuidAt(string path)
    {
        var match = Regex.Match(File.ReadAllText(path), @"(?m)^guid:[ \t]*([a-f0-9]{32})[ \t]*\r?$");
        if (!match.Success) throw new InvalidDataException("Material metadata GUID missing."); return match.Groups[1].Value;
    }
    static bool SameTint(Color color) { return Mathf.Abs(color.r - .42f) < .00001f && Mathf.Abs(color.g - .6f) < .00001f && Mathf.Abs(color.b - .66f) < .00001f && Mathf.Abs(color.a - .28f) < .00001f; }
    static void ValidateOfficialLit(Material material)
    {
        Type type = AppDomain.CurrentDomain.GetAssemblies().Select(assembly => assembly.GetType("UnityEditor.Rendering.Universal.ShaderGUI.LitShader", false)).FirstOrDefault(value => value != null);
        if (type == null) throw new InvalidOperationException("Installed official URP Lit ShaderGUI is unavailable.");
        var validator = Activator.CreateInstance(type, true) as ShaderGUI;
        if (validator == null) throw new InvalidOperationException("Official Lit validator could not be constructed.");
        validator.ValidateMaterial(material); // No inspector/window/OnGUI is opened.
    }
    static string TextureBindings(Material material)
    {
        var values = new List<string>();
        for (int index = 0; index < material.shader.GetPropertyCount(); index++) {
            if (material.shader.GetPropertyType(index) != ShaderPropertyType.Texture) continue;
            string name = material.shader.GetPropertyName(index); Texture texture = material.GetTexture(name); string identity = "null";
            if (texture) { string guid; long localId; identity = AssetDatabase.TryGetGUIDAndLocalFileIdentifier(texture, out guid, out localId) ? guid + ":" + localId + ":" + texture.GetType().FullName : "builtin:" + texture.name + ":" + texture.GetType().FullName; }
            Vector2 scale = material.GetTextureScale(name), offset = material.GetTextureOffset(name);
            values.Add(name + "|" + identity + "|" + scale.x.ToString("R", CultureInfo.InvariantCulture) + "," + scale.y.ToString("R", CultureInfo.InvariantCulture) + "|" + offset.x.ToString("R", CultureInfo.InvariantCulture) + "," + offset.y.ToString("R", CultureInfo.InvariantCulture));
        }
        return string.Join("\n", values.OrderBy(value => value, StringComparer.Ordinal));
    }
    static void VerifyTransparent(Material material, Color tint, Color emission, float smoothness, float metallic, float preserveSpecular, string bindings)
    {
        bool preserve = preserveSpecular > 0;
        if (!material || material.shader.name != "Universal Render Pipeline/Lit" || material.GetFloat("_Surface") != 1 || material.GetFloat("_Blend") != 0 || material.GetFloat("_AlphaClip") != 0
            || material.GetFloat("_SrcBlend") != (float)(preserve ? BlendMode.One : BlendMode.SrcAlpha) || material.GetFloat("_DstBlend") != (float)BlendMode.OneMinusSrcAlpha || material.GetFloat("_ZWrite") != 0
            || material.renderQueue != (int)RenderQueue.Transparent || !material.IsKeywordEnabled("_SURFACE_TYPE_TRANSPARENT") || material.GetShaderPassEnabled("ShadowCaster") || material.GetShaderPassEnabled("DepthOnly")
            || material.IsKeywordEnabled("_ALPHAPREMULTIPLY_ON") != preserve || material.GetFloat("_BlendModePreserveSpecular") != preserveSpecular
            || material.GetColor("_BaseColor") != tint || material.GetColor("_EmissionColor") != emission || material.GetFloat("_Smoothness") != smoothness || material.GetFloat("_Metallic") != metallic || TextureBindings(material) != bindings)
            throw new InvalidDataException("Transparent state, retained colors/scalars or shader texture bindings/scale/offset do not match the verified correction.");
    }
    static void SaveReport(string path, Report report)
    {
        NoLinks(path); Directory.CreateDirectory(Path.GetDirectoryName(path)); string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        File.WriteAllText(temporary, JsonUtility.ToJson(report, true) + "\n", new UTF8Encoding(false));
        for (int attempt = 0; ; attempt++) {
            try { NoLinks(path); if (File.Exists(path)) File.Replace(temporary, path, null); else File.Move(temporary, path); return; }
            catch (IOException error) { int code = error.HResult & 0xffff; if (attempt >= 4 || !(code == 5 || code == 32 || code == 33 || code == 1175)) throw; }
            catch (UnauthorizedAccessException) { if (attempt >= 4) throw; }
            System.Threading.Thread.Sleep(100 * (attempt + 1));
        }
    }
    static void RenderChangedPrefab(string prefabPath, string imagePath)
    {
        Type bridge = typeof(YamyamAssetLibraryBridge);
        var recordType = bridge.GetNestedType("PreviewRecord", BindingFlags.Public);
        object preview = Activator.CreateInstance(recordType);
        recordType.GetField("assetPath").SetValue(preview, prefabPath); recordType.GetField("imagePath").SetValue(preview, imagePath);
        recordType.GetField("kind").SetValue(preview, "source-proved-tinted-glass-after-correction");
        var drawMethod = bridge.GetMethod("Draws", BindingFlags.Static | BindingFlags.NonPublic);
        var renderMethod = bridge.GetMethod("RenderPreview", BindingFlags.Static | BindingFlags.NonPublic);
        object[] arguments = { AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath), new Bounds() };
        object draws = drawMethod.Invoke(null, arguments);
        renderMethod.Invoke(null, new[] { draws, arguments[1], preview });
        string error = recordType.GetField("error").GetValue(preview) as string;
        if (!string.IsNullOrEmpty(error) || !File.Exists(imagePath)) throw new IOException("Changed P008 prefab preview failed: " + error);
    }
    static void Run()
    {
        Guard(); if (Application.unityVersion != "6000.6.0f1" || EditorApplication.isCompiling || EditorApplication.isUpdating) throw new InvalidOperationException("Expected idle Unity6000.6.");
        string local = Path.Combine(Project, "Library/YamyamAssetLibrary"), run = Path.Combine(local, "glass-correction", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N")); NoLinks(run); Directory.CreateDirectory(run);
        string reportPath = Path.Combine(run, "report.json"); var report = new Report { project = Project, startedUtc = Utc(), sourceProofSha256 = ProofSha256, materialPath = Root + "/" + MaterialRelative, materialGuid = MaterialGuid };
        Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } };
        Application.logMessageReceived += capture;
        Material prepared = null;
        try {
            string proofPath = Path.Combine(Work, "product008-tinted-glass-source-evidence.json"); NoLinks(proofPath);
            if (HashFile(proofPath) != ProofSha256) throw new InvalidDataException("Exact source-opacity evidence changed.");
            var proof = JsonUtility.FromJson<SourceProof>(File.ReadAllText(proofPath));
            if (proof.kind != "verified-p008-untextured-tinted-glass" || proof.actualAssetsModified || proof.sourceArchivesModified || proof.sourceFbxInspected != 388 || proof.glassFbxCount != 5 || proof.uniqueGlassSignatures != 1
                || proof.sourceFiles == null || proof.sourceFiles.Length != 388 || proof.glassReferences == null || proof.glassReferences.Length != 5 || proof.targetMaterial.path != MaterialRelative || proof.targetMaterial.guid != MaterialGuid
                || !YamyamAssetLibraryIO.NormalPath(proof.stageRoot).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(Root)), StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Unreviewed source/material proof scope.");
            var manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(Work, "staging-manifest.json")));
            var product = manifest.products.Single(value => value.id == "008" && value.folder == Folder); var canonical = product.files.ToDictionary(value => value.path, StringComparer.Ordinal);
            var sourceModelGuids = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (Record source in proof.sourceFiles) {
                Record record;
                if (!source.path.StartsWith(Folder + "/", StringComparison.Ordinal) || !canonical.TryGetValue(source.path, out record) || record.sha256 != source.sha256 || record.bytes != source.bytes) throw new InvalidDataException("Source FBX receipt binding changed.");
                string path = Absolute(Root + "/" + source.path); NoLinks(path);
                if (new FileInfo(path).Length != source.bytes || HashFile(path) != source.sha256) throw new InvalidDataException("Source FBX payload changed."); report.sourceFbxVerified++;
            }
            foreach (Record source in proof.glassReferences) sourceModelGuids.Add(canonical[source.path + ".meta"].guid, source.path);
            string materialFile = Absolute(report.materialPath), metadataFile = materialFile + ".meta"; NoLinks(materialFile); NoLinks(metadataFile);
            report.materialBeforeSha256 = HashFile(materialFile); report.metadataSha256 = HashFile(metadataFile);
            if (report.materialBeforeSha256 != proof.targetMaterial.sha256 || report.metadataSha256 != proof.targetMaterial.metadataSha256 || GuidAt(metadataFile) != MaterialGuid || AssetDatabase.AssetPathToGUID(report.materialPath) != MaterialGuid) throw new InvalidDataException("Generated material bytes/GUID differ from reviewed target.");
            string prefabFolder = Absolute(Root + "/" + Folder + "/Generated/Prefabs");
            string preview = null; var referencedModels = new HashSet<string>(StringComparer.Ordinal);
            foreach (string prefab in Directory.GetFiles(prefabFolder, "*.prefab", SearchOption.AllDirectories).OrderBy(path => path, StringComparer.Ordinal)) {
                NoLinks(prefab); string text = File.ReadAllText(prefab); if (!text.Contains(MaterialGuid)) continue;
                string[] modelGuids = sourceModelGuids.Keys.Where(guid => text.Contains(guid)).ToArray();
                if (modelGuids.Length != 1 || !referencedModels.Add(modelGuids[0])) throw new InvalidDataException("Generated references must form a bijection with the5proved glass FBX sources.");
                string assetPath = prefab.Substring(Project.Length + 1).Replace('\\', '/');
                report.prefabReferences.Add(new Record { path = assetPath, bytes = new FileInfo(prefab).Length, sha256 = HashFile(prefab) });
                if (sourceModelGuids.Any(pair => pair.Value.EndsWith("EA_Tr_House_01a.fbx", StringComparison.Ordinal) && text.Contains(pair.Key))) preview = assetPath;
            }
            report.referencingGeneratedPrefabs = report.prefabReferences.Count;
            if (report.referencingGeneratedPrefabs != 5 || referencedModels.Count != 5 || preview == null) throw new InvalidDataException("Expected exactly5generated prefabs and House01a preview for the one material.");
            string previewsPath = Path.Combine(local, "previews.json"); NoLinks(previewsPath);
            var previews = JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));
            if (previews.products == null || previews.products.Count != 84 || string.IsNullOrEmpty(previews.completedUtc)) throw new InvalidDataException("Completed84-product preview evidence is required before the scoped correction.");
            var representative = previews.products.Single(value => value.id == "008");
            if (!string.IsNullOrEmpty(representative.error) || string.IsNullOrEmpty(representative.assetPath) || string.IsNullOrEmpty(representative.imagePath)) throw new InvalidDataException("P008 representative preview is incomplete.");
            NoLinks(representative.imagePath); report.originalPreviewsSha256 = HashFile(previewsPath);
            report.originalRepresentative = representative.assetPath; report.originalRepresentativeImage = representative.imagePath; report.originalRepresentativeImageSha256 = HashFile(representative.imagePath);
            report.originalRepresentativeDependencies = AssetDatabase.GetDependencies(representative.assetPath, true).Distinct().OrderBy(path => path, StringComparer.Ordinal).ToArray();
            report.originalRepresentativeDependsOnChangedMaterial = report.originalRepresentativeDependencies.Contains(report.materialPath, StringComparer.Ordinal);
            if (report.originalRepresentativeDependsOnChangedMaterial) throw new InvalidDataException("P008 representative depends on the changed glass material; a scoped representative refresh is required before preserving that image as current.");
            File.Copy(materialFile, Path.Combine(run, "material.before.mat"), false); File.Copy(metadataFile, Path.Combine(run, "material.before.mat.meta"), false);
            if (HashFile(Path.Combine(run, "material.before.mat")) != report.materialBeforeSha256 || HashFile(Path.Combine(run, "material.before.mat.meta")) != report.metadataSha256) throw new IOException("Owned material backup verification failed.");
            var material = AssetDatabase.LoadAssetAtPath<Material>(report.materialPath);
            if (!material || material.shader.name != "Universal Render Pipeline/Lit" || material.name != "Transylvania_Glass_Text_6982ccd17f00" || !SameTint(material.GetColor("_BaseColor")) || material.GetTexture("_BaseMap") || material.GetFloat("_Surface") != 0)
                throw new InvalidDataException("Generated material does not have the exact proved opaque tinted-glass signature.");
            Color beforeTint = material.GetColor("_BaseColor"), beforeEmission = material.GetColor("_EmissionColor"); float beforeSmoothness = material.GetFloat("_Smoothness"), beforeMetallic = material.GetFloat("_Metallic"), beforePreserveSpecular = material.GetFloat("_BlendModePreserveSpecular");
            string beforeBindings = TextureBindings(material); string persistentGuid; long persistentId;
            if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out persistentGuid, out persistentId) || persistentGuid != MaterialGuid) throw new InvalidDataException("Persistent material identity unavailable.");
            report.localIdBefore = persistentId;
            prepared = new Material(material); prepared.name = material.name; prepared.SetFloat("_Surface", 1); prepared.SetFloat("_Blend", 0); prepared.SetFloat("_AlphaClip", 0);
            ValidateOfficialLit(prepared);
            VerifyTransparent(prepared, beforeTint, beforeEmission, beforeSmoothness, beforeMetallic, beforePreserveSpecular, beforeBindings);
            if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity reported errors before the owned material save.");
            report.status = "saving-owned-material"; SaveReport(reportPath, report);
            EditorUtility.CopySerialized(prepared, material); EditorUtility.SetDirty(material); AssetDatabase.SaveAssetIfDirty(material);
            AssetDatabase.ImportAsset(report.materialPath, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
            material = AssetDatabase.LoadAssetAtPath<Material>(report.materialPath);
            VerifyTransparent(material, beforeTint, beforeEmission, beforeSmoothness, beforeMetallic, beforePreserveSpecular, beforeBindings);
            report.materialAfterSha256 = HashFile(materialFile);
            if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out persistentGuid, out persistentId) || persistentGuid != MaterialGuid || persistentId != report.localIdBefore || report.materialAfterSha256 == report.materialBeforeSha256
                || GuidAt(metadataFile) != MaterialGuid || HashFile(metadataFile) != report.metadataSha256 || AssetDatabase.AssetPathToGUID(report.materialPath) != MaterialGuid) throw new InvalidDataException("Material persistent payload/identity verification failed.");
            report.localIdAfter = persistentId;
            foreach (Record prefab in report.prefabReferences) if (HashFile(Absolute(prefab.path)) != prefab.sha256) throw new IOException("A generated prefab source changed during the scoped material-only correction.");
            foreach (Record source in proof.sourceFiles) if (HashFile(Absolute(Root + "/" + source.path)) != source.sha256) throw new IOException("An original FBX source changed.");
            report.previewPrefab = preview; report.previewPath = Path.Combine(run, "P008-House01a-corrected-glass.png"); RenderChangedPrefab(preview, report.previewPath);
            if (HashFile(previewsPath) != report.originalPreviewsSha256 || HashFile(representative.imagePath) != report.originalRepresentativeImageSha256) throw new IOException("Original84-product preview evidence changed during the scoped correction.");
            if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity reported native errors during glass correction/preview.");
            report.status = "complete";
        }
        catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); throw; }
        finally {
            if (prepared) UnityEngine.Object.DestroyImmediate(prepared);
            if (report.status == "complete" && report.observedUnityErrors != 0) { report.status = "failed"; report.errors.Add("Unity error during final temporary-material cleanup."); }
            Application.logMessageReceived -= capture; report.completedUtc = Utc();
            SaveReport(reportPath, report); SaveReport(Path.Combine(local, "glass-correction-report.json"), report);
            if (report.status == "failed" && report.observedUnityErrors != 0) throw new InvalidDataException("Scoped glass correction has recorded native errors.");
        }
    }
    public static void RunHeadless()
    {
        Guard(); int code = 0;
        try { Run(); } catch (Exception error) { UnityEngine.Debug.LogError(error); code = 1; }
        EditorApplication.Exit(code);
    }
}
