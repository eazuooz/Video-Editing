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

// Explicit source limitation: these missing images are not reconstructed. Only
// proven unresolved active slots become explicit nulls, retaining Unity defaults.
public static partial class YamyamAssetLibraryTextureDefaults
{
    const string ProjectExpected = "D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string Root = "Assets/ThirdParty/YamyamAssetLibrary";
    const string PlanSha = "d6abd7538122cbac5ee6345b1bc71ef293a84f3023dfdcb7888e66800e23aea4";
    const string InventorySha = "4b32a244157ba14d8d11e678f76c96cf9715c3d88e81d6f79433f04139d0d009";
    const string AuditSha = "a350b8728efb296fc1e7490460351f1057ae096d9f3b903098db5e4fc05ec6d4";
    [Serializable] public sealed class Pair { public string property, guid, fileID; }
    [Serializable] public sealed class Target { public string path, sha256, guid, metadataSha256, shader; public long bytes; public Pair[] pairs; }
    [Serializable] public sealed class Plan { public int schemaVersion, activeBindings, uniqueMissingGuids; public string kind, stageRoot, sourceAuditSha256, sourceInventorySha256, limitations; public Target[] targets, untouchedAuditMaterials; }
    [Serializable] public sealed class Finding { public string path, materialGuid, sourceSha256, metadataSha256, shader, property, missingGuid, sourceFileId, classification, resolvedAssetPath; public bool effectiveNull, textureProperty; }
    [Serializable] public sealed class Audit { public string status; public int observedUnityErrors; public Finding[] findings; }
    [Serializable] public sealed class Coverage { public string productId; public string[] unscannedNestedPackages, looseUnityMetadataEntries; }
    [Serializable] public sealed class Inventory { public string status, sourceAuditSha256; public string[] wantedGuids; public Coverage[] coverage; public Finding[] matches; public bool sourceArchivesModified, actualAssetsModified; }
    [Serializable] public sealed class Preview { public string id, imagePath; }
    [Serializable] public sealed class Previews { public string completedUtc; public Preview[] products; }
    [Serializable] public sealed class ImageProof { public string id, path, beforeSha256, afterSha256; }
    [Serializable] public sealed class Change {
        public string path, guid, metadataSha256, beforeSha256, afterSha256, beforeNativeStateSha256, afterNativeStateSha256, beforeSerializedStateSha256, afterSerializedStateSha256, backup, metadataBackup;
        public long localId, beforeBytes, afterBytes; public bool intentRecorded, saved, nativeDefaultsPreserved, otherSerializedPropertiesPreserved; public Pair[] bindings;
    }
    [Serializable] public sealed class Report {
        public int schemaVersion = 1, materialsPrepared, materialsSaved, bindingsCleared, untouchedMaterialsVerified, previewsRetained, observedUnityErrors;
        public string kind = "explicit-unavailable-source-texture-default-adaptation", status = "preflight", startedUtc, completedUtc, sourcePlanSha256, sourceAuditSha256, sourceInventorySha256, sourceManifestSha256, nativeRebindProofSha256, previewsBeforeSha256, previewsAfterSha256, limitations;
        public int allCurrentNativeValuesPreserved;
        public string currentNativeBaselinePolicy, recoverySourceReportPath, recoverySourceReportSha256, serializedNormalizationPolicy;
        public bool assetsSaved, originalSourcesModified, sourceArchivesModified, scenesOpened, unrelatedAssetsSaved, effectiveMaterialStatesPreserved, obsoleteSavedBindingsPreserved;
        public List<Change> materials = new List<Change>(); public List<ImageProof> previewImages = new List<ImageProof>(); public List<string> errors = new List<string>();
    }
    sealed class Prepared { public Target target; public Material material; public Change change; public string nativeState, serializedState; }
    static string Project { get { return YamyamAssetLibraryIO.NormalPath(Path.GetDirectoryName(Application.dataPath)); } }
    static string Work { get { return YamyamAssetLibraryIO.NormalPath(Path.Combine(Project, "..")); } }
    static string Absolute(string path) { return Path.Combine(Project, path.Replace('/', Path.DirectorySeparatorChar)); }
    static string Hash(byte[] value) { using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(value)).Replace("-", "").ToLowerInvariant(); }
    static string HashText(string value) { return Hash(Encoding.UTF8.GetBytes(value)); }
    static string HashFile(string path) { using (var input = File.OpenRead(path)) using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(input)).Replace("-", "").ToLowerInvariant(); }
    static string F(float value) { return value.ToString("R", CultureInfo.InvariantCulture); }
    static string V(Vector2 value) { return F(value.x) + "," + F(value.y); }
    static void Guard() { if (!Application.isBatchMode || Application.unityVersion != "6000.6.0f1" || !Project.Replace('\\', '/').Equals(ProjectExpected, StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Exact isolated Unity6000.6 batch project required."); }
    static void NoLinks(string path) {
        string full = YamyamAssetLibraryIO.NormalPath(path); if (!full.StartsWith(Work + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("Owned path escaped.");
        for (string current = full; !string.IsNullOrEmpty(current); current = Path.GetDirectoryName(current)) {
            try { if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0) throw new IOException("Reparse point refused."); } catch (FileNotFoundException) { } catch (DirectoryNotFoundException) { }
            if (current.Equals(Path.GetPathRoot(full), StringComparison.OrdinalIgnoreCase)) return;
        } throw new IOException("Ancestor guard failed.");
    }
    static string AssetPath(Target target) {
        string path = target.path; if (string.IsNullOrEmpty(path) || path.Contains("\\") || path.StartsWith("/", StringComparison.Ordinal) || path.Split('/').Any(part => part == "." || part == ".." || part == "" || part.Contains(":")) || !path.EndsWith(".mat", StringComparison.OrdinalIgnoreCase)) throw new IOException("Material escaped the owned root.");
        return Root + "/" + path;
    }
    static string GuidAt(string path) { var match = Regex.Match(File.ReadAllText(path), @"(?m)^guid:[ \t]*([a-f0-9]{32})[ \t]*\r?$"); if (!match.Success) throw new InvalidDataException("Metadata GUID missing."); return match.Groups[1].Value; }
    static readonly Regex TextureEntry = new Regex(@"(?m)^(?<head>[ \t]*-[ \t]+(?<name>[^:\r\n]+):[ \t]*\r?\n[ \t]+m_Texture:[ \t]*)\{(?<reference>[^}\r\n]*)\}");
    static Dictionary<string, string> References(string text) {
        var result = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (Match match in TextureEntry.Matches(text)) { string name = match.Groups["name"].Value; if (result.ContainsKey(name)) throw new InvalidDataException("Duplicate serialized texture property: " + name); result.Add(name, match.Groups["reference"].Value.Trim()); }
        return result;
    }
    static bool ExactReference(string value, Pair pair) {
        return Regex.IsMatch(value, @"(?:^|,)[ \t]*fileID:[ \t]*" + Regex.Escape(pair.fileID) + @"(?:[ \t]*,|[ \t]*$)") && Regex.IsMatch(value, @"(?:^|,)[ \t]*guid:[ \t]*" + Regex.Escape(pair.guid) + @"(?:[ \t]*,|[ \t]*$)");
    }
    static string SerializedState(string text, IEnumerable<Pair> pairs) {
        var names = new HashSet<string>(pairs.Select(value => value.property), StringComparer.Ordinal); var seen = new HashSet<string>(StringComparer.Ordinal);
        string result = TextureEntry.Replace(text.Replace("\r\n", "\n"), match => { if (!names.Contains(match.Groups["name"].Value)) return match.Value; if (!seen.Add(match.Groups["name"].Value)) throw new InvalidDataException("Target texture property repeated."); return match.Groups["head"].Value + "{<reviewed-null-default-slot>}"; });
        if (!seen.SetEquals(names)) throw new InvalidDataException("Target texture property not serialized uniquely."); return result;
    }
    static string NativeState(Material material) {
        string shaderGuid; long shaderLocalId; if (!material.shader || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material.shader, out shaderGuid, out shaderLocalId)) throw new InvalidDataException("Native shader identity missing.");
        var text = new StringBuilder(material.name + "|" + shaderGuid + ":" + shaderLocalId + "|" + material.shader.name + "|" + material.renderQueue + "|" + material.enableInstancing + "|" + material.doubleSidedGI + "|" + (int)material.globalIlluminationFlags);
        foreach (string word in material.shaderKeywords.OrderBy(value => value, StringComparer.Ordinal)) text.Append('|').Append(word);
        for (int index = 0; index < material.passCount; index++) { string name = material.GetPassName(index); if (!string.IsNullOrEmpty(name)) text.Append("|pass:").Append(name).Append(':').Append(material.GetShaderPassEnabled(name)); }
        for (int index = 0; index < material.shader.GetPropertyCount(); index++) {
            string name = material.shader.GetPropertyName(index); var type = material.shader.GetPropertyType(index); text.Append('|').Append(name).Append(':').Append(type).Append('=');
            if (type == ShaderPropertyType.Texture) {
                Texture texture = material.GetTexture(name); string guid; long id;
                if (!texture) text.Append("null"); else { if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(texture, out guid, out id)) throw new InvalidDataException("Nonpersistent native texture binding."); text.Append(guid).Append(':').Append(id).Append(':').Append(texture.GetType().FullName); }
                text.Append('|').Append(V(material.GetTextureScale(name))).Append('|').Append(V(material.GetTextureOffset(name)));
            } else if (type == ShaderPropertyType.Color || type == ShaderPropertyType.Vector) { Vector4 value = material.GetVector(name); for (int part = 0; part < 4; part++) text.Append(F(value[part])).Append(','); }
            else if (type == ShaderPropertyType.Int) text.Append(material.GetInt(name)); else text.Append(F(material.GetFloat(name)));
        }
        return text.ToString();
    }
    static void WriteAtomic(string path, string json) {
        NoLinks(path); Directory.CreateDirectory(Path.GetDirectoryName(path)); string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp"; File.WriteAllText(temporary, json + "\n", new UTF8Encoding(false));
        for (int attempt = 0; ; attempt++) { try { if (File.Exists(path)) File.Replace(temporary, path, null); else File.Move(temporary, path); return; }
            catch (IOException error) { int code = error.HResult & 0xffff; if (attempt >= 4 || !(code == 5 || code == 32 || code == 33 || code == 1175)) throw; }
            catch (UnauthorizedAccessException) { if (attempt >= 4) throw; } System.Threading.Thread.Sleep(100 * (attempt + 1)); }
    }
    static void SaveReport(string run, string latest, Report report) { WriteAtomic(Path.Combine(run, "report.json"), JsonUtility.ToJson(report, true)); WriteAtomic(latest, JsonUtility.ToJson(report, true)); }
    static void VerifyFile(Target target) {
        string asset = AssetPath(target), path = Absolute(asset); NoLinks(path); NoLinks(path + ".meta");
        if (new FileInfo(path).Length != target.bytes || HashFile(path) != target.sha256 || HashFile(path + ".meta") != target.metadataSha256 || GuidAt(path + ".meta") != target.guid || AssetDatabase.AssetPathToGUID(asset) != target.guid) throw new InvalidDataException("Material/metadata bytes or GUID changed: " + asset);
    }
    static void NoErrors(Report report) { if (report.observedUnityErrors != 0) throw new InvalidDataException("Observed native Unity errors; no waiver is allowed."); }
    public static void RunHeadless() {
        Guard(); int exit = 0; string local = Path.Combine(Project, "Library/YamyamAssetLibrary"), run = Path.Combine(local, "missing-texture-default-adaptation", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N")), latest = Path.Combine(local, "missing-texture-default-adaptation-report.json"); NoLinks(run); Directory.CreateDirectory(run);
        var report = new Report { startedUtc = DateTime.UtcNow.ToString("o") }; Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } }; Application.logMessageReceived += capture;
        try {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating) throw new InvalidOperationException("Texture adaptation requires idle editor.");
            string planPath = Path.Combine(Work, "missing-texture-default-adaptation-plan.json"), inventoryPath = Path.Combine(Work, "missing-texture-source-guid-inventory.json"), auditPath = Path.Combine(local, "missing-texture-native-audit-report.json");
            NoLinks(planPath); NoLinks(inventoryPath); NoLinks(auditPath); report.sourcePlanSha256 = HashFile(planPath); report.sourceAuditSha256 = HashFile(auditPath); report.sourceInventorySha256 = HashFile(inventoryPath);
            if (report.sourcePlanSha256 != PlanSha || report.sourceAuditSha256 != AuditSha || report.sourceInventorySha256 != InventorySha) throw new InvalidDataException("Exact reviewed plan/audit/provided-source inventory changed.");
            var plan = JsonUtility.FromJson<Plan>(File.ReadAllText(planPath)); var audit = JsonUtility.FromJson<Audit>(File.ReadAllText(auditPath)); var inventory = JsonUtility.FromJson<Inventory>(File.ReadAllText(inventoryPath)); report.limitations = plan.limitations;
            if (plan.schemaVersion != 1 || plan.kind != report.kind || plan.sourceAuditSha256 != AuditSha || plan.sourceInventorySha256 != InventorySha || plan.targets == null || plan.targets.Length != 28 || plan.untouchedAuditMaterials == null || plan.untouchedAuditMaterials.Length != 56 || plan.activeBindings != 37 || plan.uniqueMissingGuids != 28 || !YamyamAssetLibraryIO.NormalPath(plan.stageRoot).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(Root)), StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Unexpected adaptation scope.");
            if (audit.status != "complete" || audit.observedUnityErrors != 0 || inventory.status != "complete" || inventory.sourceAuditSha256 != AuditSha || inventory.matches == null || inventory.matches.Length != 0 || inventory.sourceArchivesModified || inventory.actualAssetsModified || inventory.coverage == null || inventory.coverage.Length != 8 || inventory.coverage.Any(value => value.unscannedNestedPackages == null || value.unscannedNestedPackages.Length != 0 || value.looseUnityMetadataEntries == null || value.looseUnityMetadataEntries.Length != 0)) throw new InvalidDataException("Complete native and original-package absence evidence required.");
            report.nativeRebindProofSha256 = ApplyDriftProof(plan, audit);
            var all = plan.targets.Concat(plan.untouchedAuditMaterials).ToArray(); if (all.Select(AssetPath).Distinct(StringComparer.OrdinalIgnoreCase).Count() != 84 || plan.targets.Sum(value => value.pairs.Length) != 37 || plan.targets.SelectMany(value => value.pairs).Select(value => value.guid).Distinct().Count() != 28 || !new HashSet<string>(inventory.wantedGuids, StringComparer.Ordinal).SetEquals(plan.targets.SelectMany(value => value.pairs).Select(value => value.guid))) throw new InvalidDataException("84 material/37 active-slot/28missingGUID scope changed.");
            string manifest = Path.Combine(Work, "staging-manifest.json"); NoLinks(manifest); report.sourceManifestSha256 = HashFile(manifest);
            var prepared = new List<Prepared>();
            foreach (var target in all) VerifyFile(target);
            foreach (var target in plan.targets) {
                string asset = AssetPath(target), path = Absolute(asset); var material = AssetDatabase.LoadAssetAtPath<Material>(asset); string guid; long id;
                if (!material || !material.shader || !material.shader.isSupported || material.shader.name != target.shader || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out id) || guid != target.guid) throw new InvalidDataException("Material/native shader/local identity changed.");
                var references = References(File.ReadAllText(path)); var names = new HashSet<string>(StringComparer.Ordinal);
                foreach (var pair in target.pairs) {
                    string reference; int property = material.shader.FindPropertyIndex(pair.property);
                    if (!names.Add(pair.property) || !references.TryGetValue(pair.property, out reference) || !ExactReference(reference, pair) || property < 0 || material.shader.GetPropertyType(property) != ShaderPropertyType.Texture || material.GetTexture(pair.property) || !string.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(pair.guid))) throw new InvalidDataException("Target is not the exact unresolved active effective-null binding.");
                    if (audit.findings.Count(value => value.path == asset && value.materialGuid == target.guid && value.sourceSha256 == OriginalSha(target) && value.metadataSha256 == target.metadataSha256 && value.shader == target.shader && value.property == pair.property && value.missingGuid == pair.guid && value.sourceFileId == pair.fileID && value.classification == "active-missing-effective-null" && value.effectiveNull && value.textureProperty && string.IsNullOrEmpty(value.resolvedAssetPath)) != 1) throw new InvalidDataException("Target is not bound uniquely by the completed native audit.");
                }
                string backup = Path.Combine(run, "backups", target.path.Replace('/', Path.DirectorySeparatorChar)); NoLinks(backup); Directory.CreateDirectory(Path.GetDirectoryName(backup)); File.Copy(path, backup, false); File.Copy(path + ".meta", backup + ".meta", false);
                if (HashFile(backup) != target.sha256 || HashFile(backup + ".meta") != target.metadataSha256) throw new IOException("Original material backup verification failed.");
                string native = NativeState(material), serialized = SerializedState(File.ReadAllText(path), target.pairs);
                var change = new Change { path = asset, guid = guid, localId = id, metadataSha256 = target.metadataSha256, beforeSha256 = target.sha256, beforeBytes = target.bytes, beforeNativeStateSha256 = HashText(native), beforeSerializedStateSha256 = HashText(serialized), backup = backup, metadataBackup = backup + ".meta", bindings = target.pairs };
                report.materials.Add(change); prepared.Add(new Prepared { target = target, material = material, change = change, nativeState = native, serializedState = serialized }); report.materialsPrepared++;
            }
            string previewsPath = Path.Combine(local, "previews.json"); NoLinks(previewsPath); var previews = JsonUtility.FromJson<Previews>(File.ReadAllText(previewsPath));
            if (previews.products == null || previews.products.Length != 84 || previews.products.Select(value => value.id).Distinct().Count() != 84 || string.IsNullOrEmpty(previews.completedUtc)) throw new InvalidDataException("Complete 84-preview evidence required.");
            report.previewsBeforeSha256 = HashFile(previewsPath); foreach (var preview in previews.products) { NoLinks(preview.imagePath); report.previewImages.Add(new ImageProof { id = preview.id, path = preview.imagePath, beforeSha256 = HashFile(preview.imagePath) }); }
            File.Copy(planPath, Path.Combine(run, "plan.json"), false); File.Copy(auditPath, Path.Combine(run, "native-audit.json"), false); File.Copy(inventoryPath, Path.Combine(run, "source-inventory.json"), false); File.Copy(previewsPath, Path.Combine(run, "previews.before.json"), false);
            NoErrors(report); report.status = "prepared"; SaveReport(run, latest, report);
            foreach (var item in prepared) {
                VerifyFile(item.target); if (NativeState(item.material) != item.nativeState) throw new InvalidDataException("Native material changed after preflight.");
                item.change.intentRecorded = true; report.status = "applying"; SaveReport(run, latest, report); NoErrors(report);
                foreach (var pair in item.target.pairs) item.material.SetTexture(pair.property, null);
                EditorUtility.SetDirty(item.material); AssetDatabase.SaveAssetIfDirty(item.material); report.assetsSaved = true; item.change.saved = true;
                AssetDatabase.ImportAsset(item.change.path, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
                var material = AssetDatabase.LoadAssetAtPath<Material>(item.change.path); string guid; long id; string physical = Absolute(item.change.path);
                if (!material || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out id) || guid != item.change.guid || id != item.change.localId || HashFile(physical + ".meta") != item.change.metadataSha256 || GuidAt(physical + ".meta") != guid) throw new InvalidDataException("Persistent material metadata/GUID/localID changed.");
                string native = NativeState(material), text = File.ReadAllText(physical), serialized = SerializedState(text, item.target.pairs); var refs = References(text);
                foreach (var pair in item.target.pairs) { string value; if (material.GetTexture(pair.property) || !refs.TryGetValue(pair.property, out value) || !Regex.IsMatch(value, @"^fileID:[ \t]*0[ \t]*$")) throw new InvalidDataException("Explicit native/default-null binding was not persisted."); }
                item.change.afterNativeStateSha256 = HashText(native); item.change.afterSerializedStateSha256 = HashText(serialized); item.change.afterSha256 = HashFile(physical); item.change.afterBytes = new FileInfo(physical).Length;
                item.change.nativeDefaultsPreserved = native == item.nativeState; item.change.otherSerializedPropertiesPreserved = serialized == item.serializedState;
                if (!item.change.nativeDefaultsPreserved || !item.change.otherSerializedPropertiesPreserved || item.change.afterSha256 == item.change.beforeSha256) throw new InvalidDataException("Effective material/defaults or unrelated serialized properties changed.");
                NoErrors(report); report.materialsSaved++; report.bindingsCleared += item.target.pairs.Length; SaveReport(run, latest, report);
            }
            foreach (var target in plan.untouchedAuditMaterials) { VerifyFile(target); report.untouchedMaterialsVerified++; }
            report.previewsAfterSha256 = HashFile(previewsPath); if (report.previewsAfterSha256 != report.previewsBeforeSha256) throw new IOException("Preview report changed concurrently.");
            foreach (var image in report.previewImages) { image.afterSha256 = HashFile(image.path); if (image.afterSha256 != image.beforeSha256) throw new IOException("Preview image changed concurrently."); report.previewsRetained++; }
            NoErrors(report); if (report.materialsSaved != 28 || report.bindingsCleared != 37 || report.untouchedMaterialsVerified != 56 || report.previewsRetained != 84) throw new InvalidDataException("Incomplete exact adaptation scope.");
            VerifyFreshBaselineAfter(plan); report.allCurrentNativeValuesPreserved = 84; report.currentNativeBaselinePolicy = "Fresh current84 native baseline, not historical equivalence; exact current values preserved before/after explicit-null clearing in the same Editor session.";
            report.effectiveMaterialStatesPreserved = report.materials.All(value => value.nativeDefaultsPreserved); report.obsoleteSavedBindingsPreserved = report.materials.All(value => value.otherSerializedPropertiesPreserved); report.status = "complete";
        } catch (Exception error) { exit = 1; report.status = "failed"; report.errors.Add(error.ToString()); }
        finally { Application.logMessageReceived -= capture; report.completedUtc = DateTime.UtcNow.ToString("o"); SaveReport(run, latest, report); }
        EditorApplication.Exit(exit);
    }
}
