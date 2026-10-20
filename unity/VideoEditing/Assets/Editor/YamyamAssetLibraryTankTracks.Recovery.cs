using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;

public static partial class YamyamAssetLibraryTankTracks
{
    const string RecoveryPlanSha = "3cb9badbce6360687142678e27147ce336c90d2c8321cf884449f8f2c191cf8e";
    [Serializable] public sealed class RecoveryTarget {
        public string path, beforeSha256, currentSha256, metadataSha256, backupPath, backupMetadataPath, guid;
        public long beforeBytes, currentBytes, localId;
        public bool alreadyAssigned;
    }
    [Serializable] public sealed class RecoveryImage { public string id, path, sha256; }
    [Serializable] public sealed class RecoveryPlan {
        public int schemaVersion;
        public string kind, failedReportPath, failedReportSha256, sourceProofSha256, canonicalSha256, textureMetadataSha256,
            previewsSha256, officialAliasSourcePath, officialAliasSourceSha256;
        public bool actualAssetsModified;
        public RecoveryTarget[] targets;
        public RecoveryImage[] images;
    }
    [Serializable] public sealed class RecoveryReport {
        public int schemaVersion = 1, observedUnityErrors, sourceFbxVerified, sourcePrefabsVerified, sourceMaterialStatesVerified,
            alreadyAssignedMaterialsVerified, resumedMaterialsSaved, retainedPreviewImages;
        public string kind = "bounded-p061-official-maintex-alias-completion", status = "checking", startedUtc, completedUtc, project, runDirectory,
            recoveryPlanSha256 = RecoveryPlanSha, originalFailedReportPath, originalFailedReportSha256, canonicalSha256,
            completedStandardReportPath, completedStandardReportSha256;
        public bool rightWriteIntent, assetsSaved, sourceArchivesModified, originalSourcesModified, originalFailedEvidenceModified;
        public List<string> errors = new List<string>();
    }
    static readonly Regex RecoveryTexture = new Regex(@"(?m)^(?<head>[ \t]*-[ \t]+(?<name>_BaseMap|_MainTex):[ \t]*\r?\n[ \t]+m_Texture:[ \t]*)\{(?<reference>[^}\r\n]*)\}");
    static string MapIndependentText(string text, bool assigned)
    {
        var seen = new HashSet<string>(StringComparer.Ordinal);
        string result = RecoveryTexture.Replace(text, match => {
            string name = match.Groups["name"].Value, value = match.Groups["reference"].Value;
            if (!seen.Add(name)) throw new InvalidDataException("Repeated recovered texture alias.");
            string expected = assigned ? "fileID: 2800000, guid: " + TextureGuid + ", type: 3" : "fileID: 0";
            if (value != expected) throw new InvalidDataException("Recovered alias is not the exact source image or original null.");
            return match.Groups["head"].Value + "{<source-proved-track-image-alias>}";
        });
        if (!seen.SetEquals(new[] { "_BaseMap", "_MainTex" })) throw new InvalidDataException("Both exact URP texture aliases are required.");
        return result;
    }
    static void ExactRecoveryFile(string path, long bytes, string hash)
    {
        NoLinks(path); if (!File.Exists(path) || new YamyamAssetLibraryIO.Info(path).Length != bytes || HashFile(path) != hash)
            throw new InvalidDataException("Bounded recovery input changed: " + path);
    }
    static void CheckRecoveredImage(RecoveryPlan plan)
    {
        string path = Absolute(TexturePath); NoLinks(path); NoLinks(path + ".meta");
        if (HashFile(path) != ImageSha || HashFile(path + ".meta") != plan.textureMetadataSha256 || GuidAt(path + ".meta") != TextureGuid
            || AssetDatabase.AssetPathToGUID(TexturePath) != TextureGuid) throw new InvalidDataException("Existing recovered source PNG/metadata changed.");
        var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(TexturePath); var importer = AssetImporter.GetAtPath(TexturePath) as TextureImporter;
        if (!texture || texture.width != 128 || texture.height != 72 || AssetDatabase.GetMainAssetTypeAtPath(TexturePath) != typeof(Texture2D)
            || importer == null || importer.textureShape != TextureImporterShape.Texture2D || importer.textureType != TextureImporterType.Default
            || !importer.sRGBTexture || importer.alphaIsTransparency || importer.npotScale != TextureImporterNPOTScale.None || !importer.mipmapEnabled
            || importer.wrapModeU != TextureWrapMode.Repeat || importer.wrapModeV != TextureWrapMode.Repeat || importer.filterMode != FilterMode.Trilinear
            || importer.textureCompression != TextureImporterCompression.Uncompressed) throw new InvalidDataException("Existing recovered image importer/type/dimensions differ.");
    }
    static Material LoadRecoveryTarget(RecoveryTarget target, Texture2D texture, bool assigned)
    {
        string physical = Absolute(target.path); NoLinks(physical); NoLinks(physical + ".meta");
        if (HashFile(physical + ".meta") != target.metadataSha256 || GuidAt(physical + ".meta") != target.guid || AssetDatabase.AssetPathToGUID(target.path) != target.guid)
            throw new InvalidDataException("Recovery metadata/GUID changed.");
        var material = AssetDatabase.LoadAssetAtPath<Material>(target.path); string guid; long id;
        if (!material || material.shader.name != "Universal Render Pipeline/Lit" || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out id)
            || guid != target.guid || id != target.localId || material.GetFloat("_Surface") != 0 || material.GetFloat("_AlphaClip") != 0
            || material.GetTexture("_BaseMap") != (assigned ? texture : null) || material.GetTexture("_MainTex") != (assigned ? texture : null))
            throw new InvalidDataException("Recovery native shader/map aliases/identity differ.");
        return material;
    }
    static void RecoverCompletedImageAndLeftMaterial()
    {
        Guard(); if (EditorApplication.isUpdating || EditorApplication.isCompiling) throw new InvalidOperationException("Recovery requires an idle editor.");
        string local = Path.Combine(Project, "Library/YamyamAssetLibrary"), run = Path.Combine(local, "tank-track-recovery", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N"));
        NoLinks(run); Directory.CreateDirectory(run); var report = new RecoveryReport { project = Project, runDirectory = run, startedUtc = DateTime.UtcNow.ToString("o") };
        string reportPath = Path.Combine(run, "report.json"); Action persist = () => WriteAtomic(reportPath, JsonUtility.ToJson(report, true));
        Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } };
        Application.logMessageReceived += capture;
        try {
            string planPath = Path.Combine(Work, "helper-candidates/tank-tracks-recovery/recovery-plan.json"); NoLinks(planPath);
            if (HashFile(planPath) != RecoveryPlanSha) throw new InvalidDataException("Reviewed bounded recovery plan changed.");
            var plan = JsonUtility.FromJson<RecoveryPlan>(File.ReadAllText(planPath));
            if (plan.schemaVersion != 1 || plan.kind != report.kind || plan.actualAssetsModified || plan.sourceProofSha256 != ProofSha
                || plan.targets == null || plan.targets.Length != 2 || plan.targets.Count(value => value.alreadyAssigned) != 1
                || plan.images == null || plan.images.Length != 84 || plan.images.Select(value => value.id).Distinct().Count() != 84)
                throw new InvalidDataException("Unreviewed one-reuse/one-resume recovery scope.");
            string manifestPath = Path.Combine(Work, "staging-manifest.json"); NoLinks(manifestPath);
            if (HashFile(manifestPath) != plan.canonicalSha256) throw new InvalidDataException("Recovery canonical context changed.");
            report.canonicalSha256 = plan.canonicalSha256; report.originalFailedReportPath = plan.failedReportPath; report.originalFailedReportSha256 = plan.failedReportSha256;
            NoLinks(plan.failedReportPath); if (HashFile(plan.failedReportPath) != plan.failedReportSha256) throw new InvalidDataException("Immutable failed report changed.");
            var failed = JsonUtility.FromJson<Report>(File.ReadAllText(plan.failedReportPath));
            if (failed.status != "failed" || failed.observedUnityErrors != 0 || !failed.texture2DVerified || failed.sourceFbxVerified != 18 || failed.importedSourceMaterialsValidated != 36
                || failed.materials.Count != 2 || failed.errors.Count != 1 || !failed.errors[0].StartsWith("System.IO.InvalidDataException: Persistent material map/unchanged settings/identity verification failed.", StringComparison.Ordinal)
                || failed.sourceProofSha256 != ProofSha || failed.textureMetadataSha256 != plan.textureMetadataSha256 || failed.originalRepresentativeDependsOnChangedMaterials
                || !string.IsNullOrEmpty(failed.previewPath) || failed.originalPreviewsSha256 != plan.previewsSha256)
                throw new InvalidDataException("Only the exact stopped-after-left-map/official-alias failure is recoverable.");
            NoLinks(plan.officialAliasSourcePath); if (HashFile(plan.officialAliasSourcePath) != plan.officialAliasSourceSha256
                || !File.ReadAllText(plan.officialAliasSourcePath).Contains("material.SetTexture(\"_MainTex\", material.GetTexture(\"_BaseMap\"))"))
                throw new InvalidDataException("Official installed URP alias normalization evidence changed.");
            string sourcePath = Path.Combine(Work, "product061-tank-track-source-evidence.json"); NoLinks(sourcePath);
            if (HashFile(sourcePath) != ProofSha) throw new InvalidDataException("Original source-image proof changed.");
            var proof = JsonUtility.FromJson<Proof>(File.ReadAllText(sourcePath)); VerifyPayloads(proof.sourceFbxFiles); VerifyPayloads(proof.generatedPrefabReferences);
            report.sourceFbxVerified = proof.sourceFbxFiles.Length; report.sourcePrefabsVerified = proof.generatedPrefabReferences.Length;
            CheckRecoveredImage(plan); var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(TexturePath);
            var native = new Dictionary<string, Material>(StringComparer.Ordinal); var settings = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (var target in plan.targets) {
                var original = failed.materials.Single(value => value.path == target.path); var source = proof.generatedMaterials.Single(value => Root + "/" + value.path == target.path);
                if (!target.path.StartsWith(Root + "/" + Folder + "/Generated/Materials/TankTracks_", StringComparison.Ordinal)
                    || original.guid != target.guid || original.localId != target.localId || original.beforeSha256 != target.beforeSha256 || original.metadataSha256 != target.metadataSha256
                    || source.sha256 != target.beforeSha256 || source.bytes != target.beforeBytes || source.guid != target.guid || source.metadataSha256 != target.metadataSha256)
                    throw new InvalidDataException("Recovery target differs from original failed/source material identity.");
                ExactRecoveryFile(target.backupPath, target.beforeBytes, target.beforeSha256); NoLinks(target.backupMetadataPath);
                if (HashFile(target.backupMetadataPath) != target.metadataSha256) throw new InvalidDataException("Original material metadata backup changed.");
                ExactRecoveryFile(Absolute(target.path), target.currentBytes, target.currentSha256);
                if (MapIndependentText(File.ReadAllText(target.backupPath), false) != MapIndependentText(File.ReadAllText(Absolute(target.path)), target.alreadyAssigned))
                    throw new InvalidDataException("Current material changed outside exactly the two official texture aliases.");
                var material = LoadRecoveryTarget(target, texture, target.alreadyAssigned); native.Add(target.path, material); settings.Add(target.path, OtherSettings(material));
                if (target.alreadyAssigned) report.alreadyAssignedMaterialsVerified++;
            }
            foreach (var state in failed.sourceMaterialStates) {
                GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(state.model); if (!model) throw new InvalidDataException("Proved source model failed to load.");
                var values = model.GetComponentsInChildren<Renderer>(true).SelectMany(value => value.sharedMaterials).Where(value => value && value.name == state.material).Distinct().ToArray();
                if (values.Length != 1 || C(Tint(values[0])) != state.color || V(values[0].GetTextureScale(ColorMapProperty(values[0]))) != state.scale
                    || V(values[0].GetTextureOffset(ColorMapProperty(values[0]))) != state.offset || values[0].GetTexture(ColorMapProperty(values[0])))
                    throw new InvalidDataException("One of36 original source track states changed."); report.sourceMaterialStatesVerified++;
            }
            string previewsPath = Path.Combine(local, "previews.json"); NoLinks(previewsPath);
            if (HashFile(previewsPath) != plan.previewsSha256) throw new InvalidDataException("Existing84-preview report changed before recovery.");
            var previews = JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));
            if (previews.products.Count != 84 || AssetDatabase.GetDependencies(failed.originalRepresentative, true).Any(value => plan.targets.Any(target => target.path == value)))
                throw new InvalidDataException("P061 representative unexpectedly depends on the corrected materials.");
            foreach (var image in plan.images) { NoLinks(image.path); if (HashFile(image.path) != image.sha256 || previews.products.Single(value => value.id == image.id).imagePath != image.path) throw new InvalidDataException("Current preview identity changed."); }
            File.Copy(planPath, Path.Combine(run, "recovery-plan.json"), false); File.Copy(plan.failedReportPath, Path.Combine(run, "original-failed-report.json"), false);
            File.Copy(previewsPath, Path.Combine(run, "previews.before.json"), false);
            var pending = plan.targets.Single(value => !value.alreadyAssigned); var materialToSave = native[pending.path];
            if (report.observedUnityErrors != 0 || report.alreadyAssignedMaterialsVerified != 1 || report.sourceFbxVerified != 18 || report.sourcePrefabsVerified != 18 || report.sourceMaterialStatesVerified != 36)
                throw new InvalidDataException("Complete native/source preflight required before the single right material save.");
            report.status = "saving-only-unfinished-right-material"; report.rightWriteIntent = true; persist();
            ExactRecoveryFile(Absolute(pending.path), pending.currentBytes, pending.currentSha256);
            File.Copy(Absolute(pending.path), Path.Combine(run, "right.before.mat"), false); File.Copy(Absolute(pending.path) + ".meta", Path.Combine(run, "right.before.mat.meta"), false);
            materialToSave.SetTexture("_BaseMap", texture); materialToSave.SetTexture("_MainTex", texture); EditorUtility.SetDirty(materialToSave); AssetDatabase.SaveAssetIfDirty(materialToSave);
            report.assetsSaved = true; AssetDatabase.ImportAsset(pending.path, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
            var completed = JsonUtility.FromJson<Report>(File.ReadAllText(plan.failedReportPath)); completed.errors.Clear(); completed.status = "checking-recovery";
            completed.startedUtc = report.startedUtc; completed.recoverySourceReportPath = plan.failedReportPath; completed.recoverySourceReportSha256 = plan.failedReportSha256;
            completed.recoveryOtherSettingsScope = "All native properties and texture UVs unchanged, excluding only both official aliases _BaseMap and _MainTex; original narrower hashes remain in the immutable failed report.";
            foreach (var target in plan.targets) {
                Material material = LoadRecoveryTarget(target, texture, true);
                if (OtherSettings(material) != settings[target.path] || MapIndependentText(File.ReadAllText(target.backupPath), false) != MapIndependentText(File.ReadAllText(Absolute(target.path)), true))
                    throw new InvalidDataException("Completed material changed non-map native/serialized settings.");
                if (target.alreadyAssigned) ExactRecoveryFile(Absolute(target.path), target.currentBytes, target.currentSha256);
                else report.resumedMaterialsSaved++;
                var materialResult = completed.materials.Single(value => value.path == target.path);
                materialResult.afterSha256 = HashFile(Absolute(target.path)); materialResult.unchangedSettingsSha256 = Hash(Encoding.UTF8.GetBytes(settings[target.path]));
            }
            CheckRecoveredImage(plan); VerifyPayloads(proof.sourceFbxFiles); VerifyPayloads(proof.generatedPrefabReferences);
            completed.sourceAssetsUnchanged = true; completed.generatedPrefabsUnchanged = true;
            completed.previewPrefab = Root + "/" + proof.generatedPrefabReferences.First(value => value.path.Contains("/Tank_1_A_")).path;
            completed.previewPath = Path.Combine(run, "P061-Tank1A-recovered-tracks.png"); RenderPreview(completed.previewPrefab, completed.previewPath);
            foreach (var image in plan.images) { if (HashFile(image.path) != image.sha256) throw new InvalidDataException("An existing preview image changed during recovery."); report.retainedPreviewImages++; }
            if (HashFile(previewsPath) != plan.previewsSha256 || HashFile(plan.failedReportPath) != plan.failedReportSha256 || HashFile(manifestPath) != plan.canonicalSha256
                || report.retainedPreviewImages != 84 || report.resumedMaterialsSaved != 1 || report.observedUnityErrors != 0)
                throw new InvalidDataException("Recovery final native/error/context count check failed.");
            completed.observedUnityErrors = 0; completed.unaffectedPreviewImagesVerified = completed.unaffectedPreviewRecordsVerified = 83;
            completed.previewsAfterSha256 = plan.previewsSha256; completed.representativeAfterImageSha256 = failed.originalRepresentativeImageSha256;
            completed.status = "complete"; completed.completedUtc = DateTime.UtcNow.ToString("o");
            string completePath = Path.Combine(run, "completed-standard-report.json"); SaveReport(completePath, completed);
            report.completedStandardReportPath = completePath; report.completedStandardReportSha256 = HashFile(completePath);
            SaveReport(Path.Combine(local, "tank-track-correction-report.json"), completed); report.status = "complete";
        } catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); throw; }
        finally { Application.logMessageReceived -= capture; report.completedUtc = DateTime.UtcNow.ToString("o"); persist(); WriteAtomic(Path.Combine(local, "tank-track-recovery-report.json"), JsonUtility.ToJson(report, true)); }
    }
    public static void RecoverHeadless() { Guard(); int exit = 0; try { RecoverCompletedImageAndLeftMaterial(); } catch (Exception error) { Debug.LogError(error); exit = 1; } EditorApplication.Exit(exit); }
}
