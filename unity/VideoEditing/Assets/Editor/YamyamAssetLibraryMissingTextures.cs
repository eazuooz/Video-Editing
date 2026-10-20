using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;
using FileInfo = YamyamAssetLibraryIO.Info;

// Read-only native property classification. This entry never repairs/clears a map.
public static class YamyamAssetLibraryMissingTextures
{
    const string ProjectExpected = "D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string Root = "Assets/ThirdParty/YamyamAssetLibrary";
    const string PlanSha = "874fff17c312cb817b243370f4f860637d7da412bd252498b86873e235ef7f15";
    [Serializable] public sealed class Pair { public string property, fileID, guid; }
    [Serializable] public sealed class MaterialRecord { public string path, sha256, guid, metadataSha256; public long bytes; public Pair[] pairs; }
    [Serializable] public sealed class Plan { public string kind, stageRoot, validationSha256; public MaterialRecord[] materials; }
    [Serializable] public sealed class Finding { public string path, materialGuid, sourceSha256, metadataSha256, shader, property, missingGuid, sourceFileId, resolvedAssetPath, classification; public bool effectiveNull, textureProperty; }
    [Serializable] public sealed class Report {
        public int schemaVersion = 1, materialsChecked, activeMissingSlots, inactiveSavedSlots, unknownShaderSlots, recoveredSlots, observedUnityErrors;
        public string kind = "read-only-native-missing-texture-classification", status = "checking", startedUtc, completedUtc, sourcePlanSha256, validationSha256;
        public bool assetsSaved, materialsModified, scenesOpened, sourceArchivesModified;
        public List<Finding> findings = new List<Finding>(); public List<string> errors = new List<string>();
    }
    static string Project { get { return YamyamAssetLibraryIO.NormalPath(Path.GetDirectoryName(Application.dataPath)); } }
    static string Work { get { return YamyamAssetLibraryIO.NormalPath(Path.Combine(Project, "..")); } }
    static string HashFile(string path) { using (var input = File.OpenRead(path)) using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(input)).Replace("-", "").ToLowerInvariant(); }
    static string Absolute(string path) { return Path.Combine(Project, path.Replace('/', Path.DirectorySeparatorChar)); }
    static void Guard() { if (!Application.isBatchMode || Application.unityVersion != "6000.6.0f1" || !Project.Replace('\\', '/').Equals(ProjectExpected, StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Exact isolated Unity6000.6 batch project required."); }
    static void NoLinks(string path) {
        string full = YamyamAssetLibraryIO.NormalPath(path); if (!full.StartsWith(Work + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("Owned path escaped.");
        for (string current = full; !string.IsNullOrEmpty(current); current = Path.GetDirectoryName(current)) {
            try { if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0) throw new IOException("Reparse point refused."); } catch (FileNotFoundException) { } catch (DirectoryNotFoundException) { }
            if (current.Equals(Path.GetPathRoot(full), StringComparison.OrdinalIgnoreCase)) return;
        } throw new IOException("Ancestor guard failed.");
    }
    static void Save(string path, Report report) {
        NoLinks(path); Directory.CreateDirectory(Path.GetDirectoryName(path)); string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp"; File.WriteAllText(temporary, JsonUtility.ToJson(report, true) + "\n", new UTF8Encoding(false));
        for (int attempt = 0; ; attempt++) { try { if (File.Exists(path)) File.Replace(temporary, path, null); else File.Move(temporary, path); return; }
            catch (IOException error) { int code = error.HResult & 0xffff; if (attempt >= 4 || !(code == 5 || code == 32 || code == 33 || code == 1175)) throw; }
            catch (UnauthorizedAccessException) { if (attempt >= 4) throw; } System.Threading.Thread.Sleep(100 * (attempt + 1)); }
    }
    public static void RunHeadlessAudit() {
        Guard(); int exit = 0; string local = Path.Combine(Project, "Library/YamyamAssetLibrary"), run = Path.Combine(local, "missing-texture-audit", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N")); NoLinks(run); Directory.CreateDirectory(run);
        var report = new Report { startedUtc = DateTime.UtcNow.ToString("o") }; Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } }; Application.logMessageReceived += capture;
        try {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating) throw new InvalidOperationException("Native audit requires idle editor.");
            string planPath = Path.Combine(Work, "missing-texture-native-audit-plan.json"); NoLinks(planPath); report.sourcePlanSha256 = HashFile(planPath); if (report.sourcePlanSha256 != PlanSha) throw new InvalidDataException("Exact reviewed native audit plan changed."); var plan = JsonUtility.FromJson<Plan>(File.ReadAllText(planPath)); report.validationSha256 = plan.validationSha256;
            if (plan.kind != "missing-texture-native-property-audit" || plan.materials == null || plan.materials.Length != 84 || !YamyamAssetLibraryIO.NormalPath(plan.stageRoot).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(Root)), StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Unexpected native texture audit scope.");
            if (HashFile(Path.Combine(local, "validation.json")) != plan.validationSha256 || plan.materials.Select(value => value.path).Distinct().Count() != 84 || plan.materials.SelectMany(value => value.pairs).Select(value => value.guid).Distinct().Count() != 47) throw new InvalidDataException("Native audit original validation/84material/47GUID binding changed.");
            foreach (var source in plan.materials) {
                string path = Root + "/" + source.path, physical = Absolute(path); if (!path.StartsWith(Root + "/", StringComparison.Ordinal) || path.Contains("..")) throw new IOException("Material escaped root."); NoLinks(physical); NoLinks(physical + ".meta");
                if (new FileInfo(physical).Length != source.bytes || HashFile(physical) != source.sha256 || HashFile(physical + ".meta") != source.metadataSha256 || AssetDatabase.AssetPathToGUID(path) != source.guid) throw new InvalidDataException("Audit source material/metadata changed.");
                var material = AssetDatabase.LoadAssetAtPath<Material>(path); if (!material) throw new InvalidDataException("Material failed to load."); bool known = material.shader && material.shader.name != "Hidden/InternalErrorShader" && material.shader.isSupported; var textures = new HashSet<string>(StringComparer.Ordinal);
                if (known) for (int index = 0; index < material.shader.GetPropertyCount(); index++) if (material.shader.GetPropertyType(index) == ShaderPropertyType.Texture) textures.Add(material.shader.GetPropertyName(index));
                foreach (var pair in source.pairs) {
                    bool active = textures.Contains(pair.property); string resolved = AssetDatabase.GUIDToAssetPath(pair.guid); bool effectiveNull = !active || !material.GetTexture(pair.property);
                    string classification = !known ? "unknown-shader-hard-block" : !active ? "inactive-saved-property" : effectiveNull && string.IsNullOrEmpty(resolved) ? "active-missing-effective-null" : effectiveNull ? "active-guid-resolves-but-native-texture-null" : "active-recovered-reference";
                    report.findings.Add(new Finding { path = path, materialGuid = source.guid, sourceSha256 = source.sha256, metadataSha256 = source.metadataSha256, shader = material.shader ? material.shader.name : "<missing>", property = pair.property, missingGuid = pair.guid, sourceFileId = pair.fileID, resolvedAssetPath = resolved, classification = classification, effectiveNull = effectiveNull, textureProperty = active });
                    if (!known) report.unknownShaderSlots++; else if (!active) report.inactiveSavedSlots++; else if (effectiveNull) report.activeMissingSlots++; else report.recoveredSlots++;
                }
                if (HashFile(physical) != source.sha256 || HashFile(physical + ".meta") != source.metadataSha256) throw new IOException("Read-only classification changed source bytes."); report.materialsChecked++;
            }
            if (report.observedUnityErrors != 0 || report.materialsChecked != 84) throw new InvalidDataException("Native audit had errors/incomplete coverage."); report.status = "complete";
        } catch (Exception error) { exit = 1; report.status = "failed"; report.errors.Add(error.ToString()); }
        finally { Application.logMessageReceived -= capture; report.completedUtc = DateTime.UtcNow.ToString("o"); Save(Path.Combine(run, "report.json"), report); Save(Path.Combine(local, "missing-texture-native-audit-report.json"), report); }
        EditorApplication.Exit(exit);
    }
}
