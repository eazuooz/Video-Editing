// Bounded completion of the exact source-proved P067 color save whose import disabled _EMISSION.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

public static partial class YamyamAssetLibraryMaterialSlots
{
    const string ActivationRecoveryPlanSha256 = "107515cea72f43f8c0e8dcb73a9dca7fc1bf16e6b661176e0c932a7245c34d09";
    [Serializable] public sealed class ActivationRecoveryImage { public string id, path, sha256; }
    [Serializable] public sealed class ActivationRecoveryPlan
    {
        public int schemaVersion;
        public string kind, status, canonicalSha256, originalSourcePlanSha256, failedReportPath, failedReportSha256,
            nativeProbePath, nativeProbeSha256, currentPreviewsSha256, officialValidatorSourcePath, officialValidatorSourceSha256;
        public bool actualAssetsModified;
        public Record currentMaterial, currentMetadata;
        public ActivationRecoveryImage[] images;
    }
    [Serializable] public sealed class ActivationRecoveryReport
    {
        public int schemaVersion = 1, product = 67, observedUnityErrors, retainedSourceFiles, retainedPreviewImages;
        public string kind = "bounded-p067-material-local-emission-activation", status = "checking", project, runDirectory, startedUtc, completedUtc,
            recoveryPlanSha256 = ActivationRecoveryPlanSha256, originalFailedReportPath, originalFailedReportSha256, canonicalSha256,
            currentMaterialBeforeSha256, materialAfterSha256, otherPropertiesBeforeSha256, otherPropertiesAfterSha256,
            completedStandardReportPath, completedStandardReportSha256;
        public int originalSourceGiFlags, currentGiFlagsBefore, currentGiFlagsAfter;
        public bool writeStarted, materialSaved, forcedReimportVerified, sourceArchivesModified, originalSourcesModified,
            originalFailedEvidenceModified, scenesOpened, unrelatedAssetsSaved, globalBakeRequested, bloomOrProjectSettingsChanged, sourceGltfBakedGiClaimed;
        public string activationPolicy = "The existing URP Lit material needs its local BakedEmissive bit for persistent official-validator emission activation. This is an engine-local material flag, not a source-glTF baked-GI claim or a global bake request. Realtime GI and every non-emission value remain unchanged.";
        public List<string> errors = new List<string>();
    }
    static string NormalizeActivationSerialized(string text, bool includeColor)
    {
        int flags = 0, keywords = 0, color = 0;
        text = Regex.Replace(text, @"(?m)^  m_LightmapFlags: [0-9]+\r?$", m => { flags++; return "  m_LightmapFlags: <bounded-emission-activation>"; });
        text = Regex.Replace(text, @"(?m)^  m_ValidKeywords:(?: \[\]\r?$| *\r?\n  - _EMISSION\r?$)", m => { keywords++; return "  m_ValidKeywords: <bounded-emission-activation>"; });
        if (includeColor) text = Regex.Replace(text, @"(?m)^    - _EmissionColor: \{[^}\r\n]+\}\r?$", m => { color++; return "    - _EmissionColor: <already-source-proved-linear-factor>"; });
        if (flags != 1 || keywords != 1 || includeColor && color != 1) throw new InvalidDataException("Unexpected P067 serialized activation layout.");
        return text;
    }
    static void RecoverP067EmissionActivation()
    {
        Guard();
        if (Application.unityVersion != "6000.6.0f1" || EditorApplication.isCompiling || EditorApplication.isUpdating || QualitySettings.activeColorSpace != ColorSpace.Linear)
            throw new InvalidOperationException("Expected idle isolated Unity6000.6/Linear for bounded emission completion.");
        string local = Path.Combine(Project, "Library/YamyamAssetLibrary");
        string run = Path.Combine(local, "emission-activation-recovery", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N"));
        NoLinks(run); Directory.CreateDirectory(run);
        var report = new ActivationRecoveryReport { project = Project, runDirectory = run, startedUtc = Utc() };
        Action persist = () => Atomic(Path.Combine(run, "report.json"), new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(report, true) + "\n"));
        Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } };
        Application.logMessageReceived += capture; Material prepared = null;
        try {
            string planPath = Path.Combine(Work, "helper-candidates/p067-validator/activation-recovery-plan.json"); NoLinks(planPath);
            if (HashFile(planPath) != ActivationRecoveryPlanSha256) throw new InvalidDataException("Reviewed P067 activation recovery plan changed.");
            var plan = JsonUtility.FromJson<ActivationRecoveryPlan>(File.ReadAllText(planPath));
            if (plan.schemaVersion != 1 || plan.kind != report.kind || plan.status != "prepared-read-only" || plan.actualAssetsModified || plan.originalSourcePlanSha256 != EmissionPlanSha256
                || plan.images == null || plan.images.Length != 84 || plan.images.Select(x => x.id).Distinct().Count() != 84)
                throw new InvalidDataException("Unreviewed P067 bounded-completion scope.");
            string sourcePlanPath = Path.Combine(Work, "product067-emission-correction-plan.json"), manifestPath = Path.Combine(Work, "staging-manifest.json");
            NoLinks(sourcePlanPath); NoLinks(manifestPath);
            if (HashFile(sourcePlanPath) != EmissionPlanSha256 || HashFile(manifestPath) != plan.canonicalSha256) throw new InvalidDataException("P067 original source plan or canonical context changed.");
            report.canonicalSha256 = plan.canonicalSha256;
            var sourcePlan = JsonUtility.FromJson<EmissionPlan>(File.ReadAllText(sourcePlanPath));
            if (sourcePlan.sourceFactorColorSpace != "linear-sRGB" || sourcePlan.sourceCounterparts.Length != 3 || sourcePlan.prefabs.Length != 3 || sourcePlan.sourceEmissionFactor.Length != 3)
                throw new InvalidDataException("Original P067 source-region proof changed.");
            Vector4 linear = new Vector4(sourcePlan.sourceEmissionFactor[0], sourcePlan.sourceEmissionFactor[1], sourcePlan.sourceEmissionFactor[2], 1);
            if (!NearVector(linear, new Vector4(.8000000715255737f, .01814323104918003f, .02997703291475773f, 1))) throw new InvalidDataException("Source linear emission changed.");
            NoLinks(plan.failedReportPath);
            string failedRoot = Path.Combine(local, "emission-correction");
            if (!Path.GetFullPath(plan.failedReportPath).StartsWith(Path.GetFullPath(failedRoot) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)
                || Path.GetFileName(plan.failedReportPath) != "report.json" || HashFile(plan.failedReportPath) != plan.failedReportSha256)
                throw new InvalidDataException("P067 immutable failed report escaped its exact history.");
            var failed = JsonUtility.FromJson<EmissionReport>(File.ReadAllText(plan.failedReportPath));
            if (failed.status != "failed" || !failed.applied || !failed.writeStarted || failed.observedUnityErrors != 0 || failed.errors.Count != 1
                || !failed.errors[0].StartsWith("System.IO.InvalidDataException: Saved P067 linear emission/keyword/other shader values or identity differs.", StringComparison.Ordinal)
                || failed.sourceProofSha256 != EmissionPlanSha256 || failed.sourceModelsVerified != 3 || failed.affectedGeneratedPrefabs != 3
                || failed.giFlagsBefore != 4 || failed.giFlagsAfter != 0 || !NearVector(failed.storedLinearEmissionFactor, linear)
                || failed.otherShaderPropertiesBeforeSha256 != failed.otherShaderPropertiesAfterSha256 || !string.IsNullOrEmpty(failed.previewPath))
                throw new InvalidDataException("Only exact saved-color/import-disabled-keyword partial completion is recoverable.");
            report.originalFailedReportPath = plan.failedReportPath; report.originalFailedReportSha256 = plan.failedReportSha256; report.originalSourceGiFlags = failed.giFlagsBefore;
            NoLinks(plan.nativeProbePath); NoLinks(plan.officialValidatorSourcePath);
            if (HashFile(plan.nativeProbePath) != plan.nativeProbeSha256 || HashFile(plan.officialValidatorSourcePath) != plan.officialValidatorSourceSha256
                || !File.ReadAllText(plan.officialValidatorSourcePath).Contains("material.globalIlluminationFlags & MaterialGlobalIlluminationFlags.AnyEmissive"))
                throw new InvalidDataException("Read-only native/official validator activation evidence changed.");
            var probe = JsonUtility.FromJson<P067ValidatorProbeReport>(File.ReadAllText(plan.nativeProbePath));
            var bakedProbe = probe.snapshots.Single(x => x.name == "temporary-baked-flag-control-after-validator");
            if (probe.status != "complete-read-only" || probe.assetsWritten || probe.observedUnityErrors != 0 || !probe.originalFileBytesUnchanged || !probe.originalMaterialMemoryUnchanged
                || bakedProbe.giFlags != (int)MaterialGlobalIlluminationFlags.BakedEmissive || !bakedProbe.emissionKeyword
                || bakedProbe.otherShaderPropertiesSha256 != failed.otherShaderPropertiesBeforeSha256 || !NearVector(bakedProbe.emissionColor, linear))
                throw new InvalidDataException("Native temporary BakedEmissive control did not prove the exact unchanged source-linear activation.");
            Record target = plan.currentMaterial, metadata = plan.currentMetadata;
            if (target.assetPath != Root + EmissionFolder + "/Generated/Materials/emiss_3bf86f37223e.mat" || target.path != Absolute(target.assetPath) || target.guid != EmissionGuid
                || metadata.path != target.path + ".meta" || sourcePlan.targetMaterial.assetPath != target.assetPath || sourcePlan.targetMaterial.guid != target.guid
                || sourcePlan.targetMetadata.sha256 != metadata.sha256 || failed.materialBeforeSha256 != sourcePlan.targetMaterial.sha256)
                throw new InvalidDataException("P067 completion target differs from the exact original source identity.");
            Exact(target.path, target.bytes, target.sha256); Exact(metadata.path, metadata.bytes, metadata.sha256);
            string originalBackup = Path.Combine(Path.GetDirectoryName(plan.failedReportPath), "material.before.mat");
            Exact(originalBackup, sourcePlan.targetMaterial.bytes, sourcePlan.targetMaterial.sha256);
            if (NormalizeActivationSerialized(File.ReadAllText(originalBackup), true) != NormalizeActivationSerialized(File.ReadAllText(target.path), true))
                throw new InvalidDataException("Partial saved material differs outside source-proved color/activation fields.");
            foreach (Record retained in failed.retainedSources) { Exact(retained.path, retained.bytes, retained.sha256); report.retainedSourceFiles++; }
            if (report.retainedSourceFiles != 12) throw new InvalidDataException("Exact three source FBX/prefab metadata pairs required.");
            foreach (EmissionPrefab prefab in sourcePlan.prefabs) EmissionIdentity(prefab, sourcePlan.targetMaterial);
            Material material = AssetDatabase.LoadAssetAtPath<Material>(target.assetPath); string guid; long id;
            if (!material || material.shader.name != "Universal Render Pipeline/Lit" || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out id)
                || guid != EmissionGuid || id != 2100000 || GuidAt(metadata.path) != EmissionGuid || material.globalIlluminationFlags != MaterialGlobalIlluminationFlags.None
                || material.IsKeywordEnabled("_EMISSION") || !NearVector(material.GetVector("_EmissionColor"), linear) || OtherEmissionProperties(material) != failed.otherShaderPropertiesBeforeSha256)
                throw new InvalidDataException("Current native P067 partial-state color/None-GI/keyword/identity signature changed.");
            report.currentGiFlagsBefore = (int)material.globalIlluminationFlags; report.currentMaterialBeforeSha256 = HashFile(target.path); report.otherPropertiesBeforeSha256 = OtherEmissionProperties(material);
            prepared = new Material(material) { name = material.name };
            prepared.globalIlluminationFlags = material.globalIlluminationFlags | MaterialGlobalIlluminationFlags.BakedEmissive;
            ValidateEmissionLit(prepared);
            if (!NearVector(prepared.GetVector("_EmissionColor"), linear) || !prepared.IsKeywordEnabled("_EMISSION")
                || prepared.globalIlluminationFlags != MaterialGlobalIlluminationFlags.BakedEmissive
                || (prepared.globalIlluminationFlags & MaterialGlobalIlluminationFlags.RealtimeEmissive) != (material.globalIlluminationFlags & MaterialGlobalIlluminationFlags.RealtimeEmissive)
                || OtherEmissionProperties(prepared, ObjectIdentity(material)) != report.otherPropertiesBeforeSha256)
                throw new InvalidDataException("Official material-local BakedEmissive activation changed non-emission source values or Realtime GI.");
            string previewsPath = Path.Combine(local, "previews.json"); NoLinks(previewsPath);
            if (HashFile(previewsPath) != plan.currentPreviewsSha256) throw new InvalidDataException("Current canonical previews changed before bounded P067 completion.");
            var previews = JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));
            if (previews.products.Count != 84) throw new InvalidDataException("Current complete84-preview evidence is required.");
            foreach (var image in plan.images) { NoLinks(image.path); if (HashFile(image.path) != image.sha256 || previews.products.Single(x => x.id == image.id).imagePath != image.path) throw new InvalidDataException("Current preview image/identity changed."); }
            var representative = previews.products.Single(x => x.id == "067");
            bool depends = AssetDatabase.GetDependencies(representative.assetPath, true).Contains(target.assetPath, StringComparer.Ordinal);
            var completed = JsonUtility.FromJson<EmissionReport>(File.ReadAllText(plan.failedReportPath)); completed.errors.Clear(); completed.status = "checking-activation-recovery";
            completed.runDirectory = run; completed.startedUtc = report.startedUtc; completed.originalPreviewsSha256 = plan.currentPreviewsSha256;
            completed.representativeAssetPath = representative.assetPath; completed.representativeImageBeforeSha256 = HashFile(representative.imagePath);
            completed.representativeDependsOnChangedMaterial = depends; completed.unchangedPreviews.Clear();
            foreach (var previous in previews.products.Where(x => x.id != "067")) completed.unchangedPreviews.Add(new RetainedPreview { id = previous.id, imagePath = previous.imagePath, imageSha256 = HashFile(previous.imagePath), recordSha256 = Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(previous))) });
            File.Copy(planPath, Path.Combine(run, "recovery-plan.json"), false); File.Copy(plan.failedReportPath, Path.Combine(run, "original-failed-report.json"), false);
            File.Copy(target.path, Path.Combine(run, "material.partial-before.mat"), false); File.Copy(metadata.path, Path.Combine(run, "material.partial-before.mat.meta"), false);
            File.Copy(previewsPath, Path.Combine(run, "previews.before.json"), false); File.Copy(representative.imagePath, Path.Combine(run, "representative.before.png"), false);
            if (report.observedUnityErrors != 0) throw new InvalidDataException("Native error before the single material save.");
            report.status = "saving-material-local-emission-activation"; report.writeStarted = true; persist(); Exact(target.path, target.bytes, target.sha256);
            EditorUtility.CopySerialized(prepared, material); EditorUtility.SetDirty(material); AssetDatabase.SaveAssetIfDirty(material); report.materialSaved = true;
            AssetDatabase.ImportAsset(target.assetPath, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport); material = AssetDatabase.LoadAssetAtPath<Material>(target.assetPath);
            report.currentGiFlagsAfter = (int)material.globalIlluminationFlags; report.otherPropertiesAfterSha256 = OtherEmissionProperties(material); report.materialAfterSha256 = HashFile(target.path);
            if (!NearVector(material.GetVector("_EmissionColor"), linear) || !material.IsKeywordEnabled("_EMISSION") || material.globalIlluminationFlags != MaterialGlobalIlluminationFlags.BakedEmissive
                || report.otherPropertiesAfterSha256 != report.otherPropertiesBeforeSha256 || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out id) || guid != EmissionGuid || id != 2100000
                || NormalizeActivationSerialized(File.ReadAllText(Path.Combine(run, "material.partial-before.mat")), false) != NormalizeActivationSerialized(File.ReadAllText(target.path), false))
                throw new InvalidDataException("Persistent material activation/reimport changed source color, non-emission bytes, GI mode or identity.");
            report.forcedReimportVerified = true; Exact(metadata.path, metadata.bytes, metadata.sha256);
            completed.materialAfterSha256 = report.materialAfterSha256; completed.storedLinearEmissionFactor = material.GetVector("_EmissionColor"); completed.giFlagsAfter = report.currentGiFlagsAfter;
            completed.otherShaderPropertiesAfterSha256 = report.otherPropertiesAfterSha256; completed.localIdAfter = id;
            completed.previewPrefab = sourcePlan.prefabs.Single(x => x.sourceModel.EndsWith("/EA_Pumpkin_01a.fbx", StringComparison.Ordinal)).prefab.assetPath;
            completed.previewPath = Path.Combine(run, "P067-Pumpkin01a-persistent-emission.png");
            completed.additionalPreview = RenderChanged(completed.previewPrefab, completed.previewPath, "067", representative.title, "source-linear-material-local-activation");
            if (depends) {
                if (HashFile(previewsPath) != plan.currentPreviewsSha256 || HashFile(representative.imagePath) != completed.representativeImageBeforeSha256) throw new InvalidDataException("P067 representative changed before scoped refresh.");
                completed.representativeWriteStarted = true;
                completed.representativeAfter = RenderChanged(representative.assetPath, representative.imagePath, "067", representative.title, representative.kind);
                Atomic(previewsPath, Encoding.UTF8.GetBytes(ReplaceOnePreviewRecord(File.ReadAllText(previewsPath), completed.representativeAfter))); completed.representativeRefreshed = true;
            } else completed.representativeAfter = representative;
            completed.previewsAfterSha256 = HashFile(previewsPath); completed.representativeImageAfterSha256 = HashFile(representative.imagePath);
            var afterPreviews = JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));
            foreach (var retained in completed.unchangedPreviews) {
                if (HashFile(retained.imagePath) != retained.imageSha256 || Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(afterPreviews.products.Single(x => x.id == retained.id)))) != retained.recordSha256)
                    throw new InvalidDataException("One of83 unrelated P067 completion previews changed."); report.retainedPreviewImages++;
            }
            if (!depends && (completed.previewsAfterSha256 != plan.currentPreviewsSha256 || completed.representativeImageBeforeSha256 != completed.representativeImageAfterSha256)) throw new InvalidDataException("Unrelated P067 representative changed.");
            foreach (Record retained in failed.retainedSources) Exact(retained.path, retained.bytes, retained.sha256);
            if (report.retainedPreviewImages != 83 || HashFile(plan.failedReportPath) != plan.failedReportSha256 || HashFile(manifestPath) != plan.canonicalSha256 || report.observedUnityErrors != 0)
                throw new InvalidDataException("P067 final source/history/context/error check failed.");
            completed.conversionPolicy += " Persistent URP activation uses only the material-local BakedEmissive bit; no global bake or source-glTF baked-GI claim.";
            completed.status = "complete"; completed.completedUtc = Utc();
            string standardPath = Path.Combine(run, "completed-standard-report.json"); Atomic(standardPath, new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(completed, true) + "\n"));
            report.completedStandardReportPath = standardPath; report.completedStandardReportSha256 = HashFile(standardPath);
            Atomic(Path.Combine(local, "emission-correction-report.json"), new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(completed, true) + "\n")); report.status = "complete";
        } catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); throw; }
        finally {
            if (prepared) UnityEngine.Object.DestroyImmediate(prepared);
            bool cleanupFailure = report.observedUnityErrors != 0 && report.status == "complete";
            if (cleanupFailure) { report.status = "failed"; report.errors.Add("Native error during temporary-material cleanup."); }
            Application.logMessageReceived -= capture; report.completedUtc = Utc(); persist();
            Atomic(Path.Combine(local, "emission-activation-recovery-report.json"), new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(report, true) + "\n"));
            if (cleanupFailure) throw new InvalidDataException("P067 activation cleanup recorded native errors; failed report requires exit1.");
        }
    }
    public static void RecoverP067EmissionActivationHeadless()
    {
        Guard(); int exit = 0;
        try { RecoverP067EmissionActivation(); } catch (Exception error) { Debug.LogError(error); exit = 1; }
        EditorApplication.Exit(exit);
    }
}
