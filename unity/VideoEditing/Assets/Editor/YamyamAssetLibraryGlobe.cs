// Exact P082 missing-source-map correction. No atlas substitute or package icon is accepted.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;
using FileInfo = YamyamAssetLibraryIO.Info;

public static class YamyamAssetLibraryGlobe
{
    const string Project = "D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string PlanSha = "be558dcc3c113c388f07a13007f88f97d4d3e64312a20c590ff0d99a8498d58d";
    const string Model = "Assets/ThirdParty/YamyamAssetLibrary/082-free-vintage-retro-stylized-pack/Vintage Room/Props 2/Models/Unity FBX/Globe.fbx";
    const string MaterialPath = "Assets/ThirdParty/YamyamAssetLibrary/082-free-vintage-retro-stylized-pack/Generated/Materials/Globe_74c1d21c742c.mat";
    const string MaterialGuid = "ee19337a61a364c47b4c5a00d58877ee", ModelGuid = "0962abd2f625356fb4ff2c22d0fa4ed4";
    const string WrongIcon = "Packages/com.unity.dt.app-ui/PackageResources/Icons/Regular/Globe.png", WrongGuid = "642101e564ebb46149fc1a27d5834cae";
    [Serializable] public sealed class FileRecord { public string path, sha256; public long bytes; }
    [Serializable] public sealed class Plan { public int schemaVersion; public string kind, sourceProofPath, sourceProofSha256, canonicalSha256, previewsSha256; public bool actualAssetsModified, materialAlreadyCleared; public string partialReportPath, partialReportSha256; public FileRecord originalAssignedMaterial; public FileRecord model, modelMetadata, material, materialMetadata; public FileRecord[] preserveFiles; }
    [Serializable] public sealed class Report {
        public int schemaVersion = 1, observedUnityErrors, globeSlotsVerified, remapsBefore, remapsAfter;
        public string kind = "source-confirmed-p082-reject-unrelated-package-globe-icon", status = "checking", project = Project, runDirectory, startedUtc, completedUtc, planSha256 = PlanSha,
            sourceProofSha256, canonicalSha256, materialBeforeSha256, materialAfterSha256, modelMetadataBeforeSha256, modelMetadataAfterSha256,
            nonMapPropertiesBeforeSha256, nonMapPropertiesAfterSha256, meshBeforeSha256, meshAfterSha256;
        public bool materialSaved, remapAdded, existingCorrectRemapReused, forcedReimportVerified, originalFbxBytesPreserved, originalPrefabBytesPreserved,
            otherImporterSettingsPreserved, materialMetadataPreserved, sourceArchivesModified, atlasInvented, scenesOpened, globalSettingsChanged, materialAlreadyClearedReused;
        public string partialSourceReportPath, partialSourceReportSha256;
        public string sourceGap = "Original FBX references external globe.png; the supplied ZIP has no such file and FBX has no embedded Content payload. Props2 atlases have no equivalence proof. Keep both color-map aliases null and explicitly remap only source material Globe to its existing corrected generated material.";
        public List<string> errors = new List<string>();
    }
    static string Physical(string path) { return Path.GetFullPath(Path.Combine(Project, path.Replace('/', Path.DirectorySeparatorChar))); }
    static string Work { get { return Path.GetFullPath(Path.Combine(Project, "..")); } }
    static string Hash(byte[] raw) { using (var h = SHA256.Create()) return BitConverter.ToString(h.ComputeHash(raw)).Replace("-", "").ToLowerInvariant(); }
    static string HashFile(string path) { return Hash(File.ReadAllBytes(path)); }
    static void NoLinks(string path) { for (var p = new DirectoryInfo(Path.GetFullPath(path)); p != null; p = p.Parent) if ((Directory.Exists(p.FullName) || File.Exists(p.FullName)) && (File.GetAttributes(p.FullName) & FileAttributes.ReparsePoint) != 0) throw new InvalidDataException("Link/junction refused: " + p.FullName); }
    static void Exact(FileRecord file) { NoLinks(file.path); if (!File.Exists(file.path) || new FileInfo(file.path).Length != file.bytes || HashFile(file.path) != file.sha256) throw new InvalidDataException("P082 exact owned input changed: " + file.path); }
    static void Atomic(string path, byte[] raw) {
        NoLinks(path); Directory.CreateDirectory(Path.GetDirectoryName(path));
        string temporary = Path.Combine(Path.GetDirectoryName(path), ".ya-" + Guid.NewGuid().ToString("N").Substring(0, 12) + ".tmp"); NoLinks(temporary);
        using (var stream = new YamyamAssetLibraryIO.Stream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None)) { stream.Write(raw, 0, raw.Length); stream.Flush(true); }
        try {
            for (int attempt = 0; ; attempt++) {
                try { NoLinks(path); if (File.Exists(path)) File.Replace(temporary, path, null); else File.Move(temporary, path); break; }
                catch (IOException error) { int code = error.HResult & 0xffff; if (attempt >= 4 || !(code == 5 || code == 32 || code == 33 || code == 1175)) throw; }
                catch (UnauthorizedAccessException) { if (attempt >= 4) throw; }
                System.Threading.Thread.Sleep(100 * (attempt + 1));
            }
        } finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }

    static string Identity(UnityEngine.Object value) { string guid; long id; return value && AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value, out guid, out id) ? guid + ":" + id : "null"; }
    static string F(float v) { return v.ToString("R", CultureInfo.InvariantCulture); }
    static string NonMapProperties(Material m) {
        var text = new StringBuilder(m.shader.name).Append('|').Append(m.renderQueue).Append('|').Append(m.enableInstancing).Append('|').Append(m.doubleSidedGI).Append('|').Append((int)m.globalIlluminationFlags).Append('|').Append(m.GetTag("RenderType", false));
        foreach (string k in m.shaderKeywords.OrderBy(x => x, StringComparer.Ordinal)) text.Append('|').Append(k);
        for (int i = 0; i < m.shader.GetPropertyCount(); i++) {
            string name = m.shader.GetPropertyName(i); var type = m.shader.GetPropertyType(i); text.Append('\n').Append(name).Append(':').Append(type);
            if (type == ShaderPropertyType.Texture) { if (name != "_BaseMap" && name != "_MainTex") text.Append(':').Append(Identity(m.GetTexture(name))); Vector2 s = m.GetTextureScale(name), o = m.GetTextureOffset(name); foreach (float v in new[] { s.x, s.y, o.x, o.y }) text.Append('|').Append(F(v)); }
            else if (type == ShaderPropertyType.Color || type == ShaderPropertyType.Vector) { Vector4 v = m.GetVector(name); for (int j = 0; j < 4; j++) text.Append('|').Append(F(v[j])); }
            else if (type == ShaderPropertyType.Int) text.Append('|').Append(m.GetInteger(name)); else text.Append('|').Append(F(m.GetFloat(name)));
        }
        for (int i = 0; i < m.passCount; i++) { string pass = m.GetPassName(i); text.Append("\npass:").Append(pass).Append(':').Append(m.GetShaderPassEnabled(pass)); }
        return Hash(Encoding.UTF8.GetBytes(text.ToString()));
    }
    static string MapIndependent(string text, bool assigned) {
        int count = 0; var names = new HashSet<string>(StringComparer.Ordinal);
        text = Regex.Replace(text, @"(?m)^(?<head>[ \t]*-[ \t]+(?<name>_BaseMap|_MainTex):[ \t]*\r?\n[ \t]+m_Texture:[ \t]*)\{(?<reference>[^}\r\n]*)\}", m => {
            if (!names.Add(m.Groups["name"].Value)) throw new InvalidDataException("Repeated P082 map alias.");
            string expected = assigned ? "fileID: 2800000, guid: " + WrongGuid + ", type: 3" : "fileID: 0";
            if (m.Groups["reference"].Value != expected) throw new InvalidDataException("Unexpected P082 texture reference."); count++; return m.Groups["head"].Value + "{<verified-missing-original-map>}";
        });
        if (count != 2) throw new InvalidDataException("Both exact color-map aliases are required."); return text;
    }
    static string ImporterIndependent(string text) { int count = 0; string value = Regex.Replace(text, @"(?ms)^  externalObjects:.*?(?=^  materials:)", m => { count++; return "  externalObjects: <exact-owned-Globe-remap>\n"; }); if (count != 1) throw new InvalidDataException("Unexpected ModelImporter layout."); return value; }
    static string Meshes() {
        using (var bytes = new MemoryStream()) using (var writer = new BinaryWriter(bytes)) {
            foreach (Mesh mesh in AssetDatabase.LoadAllAssetsAtPath(Model).OfType<Mesh>().OrderBy(x => Identity(x), StringComparer.Ordinal)) { writer.Write(Identity(mesh)); writer.Write(mesh.vertexCount); foreach (Vector3 v in mesh.vertices) { writer.Write(v.x); writer.Write(v.y); writer.Write(v.z); } foreach (Vector3 v in mesh.normals) { writer.Write(v.x); writer.Write(v.y); writer.Write(v.z); } foreach (Vector2 v in mesh.uv) { writer.Write(v.x); writer.Write(v.y); } writer.Write(mesh.subMeshCount); for (int i = 0; i < mesh.subMeshCount; i++) { writer.Write((int)mesh.GetTopology(i)); foreach (int n in mesh.GetIndices(i)) writer.Write(n); } } writer.Flush(); return Hash(bytes.ToArray());
        }
    }
    public static void RunHeadless() {
        if (!Application.isBatchMode || Application.unityVersion != "6000.6.0f1" || !Path.GetDirectoryName(Application.dataPath).Replace('\\', '/').Equals(Project, StringComparison.OrdinalIgnoreCase) || EditorApplication.isUpdating || EditorApplication.isCompiling) throw new InvalidOperationException("Only idle exact isolated Unity6000.6 is permitted.");
        string local = Path.Combine(Project, "Library/YamyamAssetLibrary"), run = Path.Combine(local, "p082-globe-correction", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N")); NoLinks(run); Directory.CreateDirectory(run);
        var report = new Report { runDirectory = run, startedUtc = DateTime.UtcNow.ToString("o") }; int exit = 0;
        Action persist = () => Atomic(Path.Combine(run, "report.json"), new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(report, true) + "\n"));
        Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } }; Application.logMessageReceived += capture;
        try {
            string planPath = Path.Combine(Work, "helper-candidates/p082-globe-only/plan.json"); NoLinks(planPath); if (HashFile(planPath) != PlanSha) throw new InvalidDataException("Reviewed P082 correction plan changed."); var plan = JsonUtility.FromJson<Plan>(File.ReadAllText(planPath));
            if (plan.schemaVersion != 1 || plan.kind != report.kind || plan.actualAssetsModified || plan.model.path != Physical(Model) || plan.modelMetadata.path != Physical(Model) + ".meta" || plan.material.path != Physical(MaterialPath) || plan.materialMetadata.path != Physical(MaterialPath) + ".meta") throw new InvalidDataException("P082 paths/scope changed.");
            Exact(plan.model); Exact(plan.modelMetadata); Exact(plan.material); Exact(plan.materialMetadata); foreach (var file in plan.preserveFiles) Exact(file);
            if (plan.materialAlreadyCleared) {
                NoLinks(plan.partialReportPath); if (HashFile(plan.partialReportPath) != plan.partialReportSha256) throw new InvalidDataException("P082 exact partial-save report changed.");
                var previous = JsonUtility.FromJson<Report>(File.ReadAllText(plan.partialReportPath));
                if (previous.status != "failed" || !previous.materialSaved || previous.remapAdded || previous.observedUnityErrors != 0 || previous.errors.Count != 1 || !previous.errors[0].StartsWith("System.IO.IOException:", StringComparison.Ordinal)) throw new InvalidDataException("Only exact stopped-after-map-clear/report-replace failure may reuse the completed material.");
                Exact(plan.originalAssignedMaterial);
                if (MapIndependent(File.ReadAllText(plan.originalAssignedMaterial.path), true) != MapIndependent(File.ReadAllText(plan.material.path), false)) throw new InvalidDataException("P082 partial save changed anything beyond the two exact icon references.");
                report.partialSourceReportPath = plan.partialReportPath; report.partialSourceReportSha256 = plan.partialReportSha256;
            }
            NoLinks(plan.sourceProofPath); if (HashFile(plan.sourceProofPath) != plan.sourceProofSha256) throw new InvalidDataException("Supplied FBX/ZIP missing-map proof changed."); report.sourceProofSha256 = plan.sourceProofSha256;
            string manifest = Path.Combine(Work, "staging-manifest.json"), previews = Path.Combine(local, "previews.json"); NoLinks(manifest); NoLinks(previews); if (HashFile(manifest) != plan.canonicalSha256 || HashFile(previews) != plan.previewsSha256) throw new InvalidDataException("Canonical context changed."); report.canonicalSha256 = plan.canonicalSha256;
            var material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath); var wrong = AssetDatabase.LoadAssetAtPath<Texture2D>(WrongIcon); var importer = AssetImporter.GetAtPath(Model) as ModelImporter;
            if (!material || material.shader.name != "Universal Render Pipeline/Lit" || Identity(material) != MaterialGuid + ":2100000" || !wrong || AssetDatabase.AssetPathToGUID(WrongIcon) != WrongGuid || material.GetTexture("_BaseMap") != (plan.materialAlreadyCleared ? null : wrong) || material.GetTexture("_MainTex") != (plan.materialAlreadyCleared ? null : wrong) || importer == null || AssetDatabase.AssetPathToGUID(Model) != ModelGuid) throw new InvalidDataException("Exact native generated material/package icon/model identity changed.");
            var key = new AssetImporter.SourceAssetIdentifier(typeof(Material), "Globe"); var beforeMap = importer.GetExternalObjectMap(); report.remapsBefore = beforeMap.Count;
            UnityEngine.Object existing; bool exists = beforeMap.TryGetValue(key, out existing); if (exists && existing != material || beforeMap.Count != (exists ? 1 : 0)) throw new InvalidDataException("Unexpected pre-existing model remaps; nothing overwritten."); report.existingCorrectRemapReused = exists;
            string originalMeta = File.ReadAllText(plan.modelMetadata.path), originalMaterial = File.ReadAllText(plan.material.path); report.modelMetadataBeforeSha256 = HashFile(plan.modelMetadata.path); report.materialBeforeSha256 = HashFile(plan.material.path); report.nonMapPropertiesBeforeSha256 = NonMapProperties(material); report.meshBeforeSha256 = Meshes();
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(Model); var slotIds = new List<string>(); var otherSlots = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (var renderer in model.GetComponentsInChildren<Renderer>(true)) for (int i = 0; i < renderer.sharedMaterials.Length; i++) { Material slot = renderer.sharedMaterials[i]; string slotKey = Identity(renderer) + "/" + i; if (slot && (slot.name == "Globe" || slot == material)) slotIds.Add(slotKey); else otherSlots.Add(slotKey, Identity(slot)); }
            if (slotIds.Count != 1 || report.observedUnityErrors != 0) throw new InvalidDataException("Exact single source Globe slot required.");
            File.Copy(planPath, Path.Combine(run, "plan.json"), false); File.Copy(plan.material.path, Path.Combine(run, "material.before.mat"), false); File.Copy(plan.materialMetadata.path, Path.Combine(run, "material.before.mat.meta"), false); File.Copy(plan.modelMetadata.path, Path.Combine(run, "model.before.fbx.meta"), false);
            if (!plan.materialAlreadyCleared) { report.status = "clearing-only-two-unrelated-package-map-aliases"; persist(); material.SetTexture("_BaseMap", null); material.SetTexture("_MainTex", null); EditorUtility.SetDirty(material); AssetDatabase.SaveAssetIfDirty(material); report.materialSaved = true; AssetDatabase.ImportAsset(MaterialPath, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport); }
            else { report.materialAlreadyClearedReused = true; }
            material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath); if (material.GetTexture("_BaseMap") || material.GetTexture("_MainTex") || NonMapProperties(material) != report.nonMapPropertiesBeforeSha256 || MapIndependent(originalMaterial, !plan.materialAlreadyCleared) != MapIndependent(File.ReadAllText(plan.material.path), false)) throw new InvalidDataException("Cleared generated material changed non-map values/UVs/bytes.");
            importer = AssetImporter.GetAtPath(Model) as ModelImporter; if (!exists) { report.status = "adding-only-Globe-material-remap"; persist(); importer.AddRemap(key, material); importer.SaveAndReimport(); report.remapAdded = true; } else AssetDatabase.ImportAsset(Model, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
            importer = AssetImporter.GetAtPath(Model) as ModelImporter; var afterMap = importer.GetExternalObjectMap(); report.remapsAfter = afterMap.Count; if (afterMap.Count != 1 || !afterMap.TryGetValue(key, out existing) || Identity(existing) != MaterialGuid + ":2100000" || AssetDatabase.AssetPathToGUID(Model) != ModelGuid || ImporterIndependent(originalMeta) != ImporterIndependent(File.ReadAllText(plan.modelMetadata.path))) throw new InvalidDataException("ModelImporter changed beyond its one exact Globe remap."); report.otherImporterSettingsPreserved = true;
            model = AssetDatabase.LoadAssetAtPath<GameObject>(Model); foreach (var renderer in model.GetComponentsInChildren<Renderer>(true)) for (int i = 0; i < renderer.sharedMaterials.Length; i++) { string slotKey = Identity(renderer) + "/" + i; if (slotIds.Contains(slotKey)) { if (Identity(renderer.sharedMaterials[i]) != MaterialGuid + ":2100000") throw new InvalidDataException("Raw FBX Globe slot did not adopt corrected existing material."); report.globeSlotsVerified++; } else { string previous; if (!otherSlots.TryGetValue(slotKey, out previous) || previous != Identity(renderer.sharedMaterials[i])) throw new InvalidDataException("Another raw FBX material slot changed."); } }
            report.meshAfterSha256 = Meshes(); if (report.globeSlotsVerified != 1 || report.meshAfterSha256 != report.meshBeforeSha256) throw new InvalidDataException("P082 raw FBX geometry/slot identity changed.");
            material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath); report.nonMapPropertiesAfterSha256 = NonMapProperties(material); report.materialAfterSha256 = HashFile(plan.material.path); report.modelMetadataAfterSha256 = HashFile(plan.modelMetadata.path);
            if (material.GetTexture("_BaseMap") || material.GetTexture("_MainTex") || report.nonMapPropertiesAfterSha256 != report.nonMapPropertiesBeforeSha256 || MapIndependent(originalMaterial, !plan.materialAlreadyCleared) != MapIndependent(File.ReadAllText(plan.material.path), false) || HashFile(manifest) != plan.canonicalSha256 || HashFile(previews) != plan.previewsSha256 || report.observedUnityErrors != 0) throw new InvalidDataException("P082 final native/map/context preservation failed.");
            Exact(plan.model); Exact(plan.materialMetadata); foreach (var file in plan.preserveFiles) Exact(file); report.originalFbxBytesPreserved = true; report.originalPrefabBytesPreserved = true; report.materialMetadataPreserved = true; report.forcedReimportVerified = true; report.status = "complete";
        } catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); exit = 1; }
        finally { Application.logMessageReceived -= capture; report.completedUtc = DateTime.UtcNow.ToString("o"); persist(); Atomic(Path.Combine(local, "p082-globe-correction-report.json"), new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(report, true) + "\n")); }
        EditorApplication.Exit(exit);
    }
}
