using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;

public static partial class YamyamAssetLibraryTextureDefaults
{
    const string DriftKind = "bounded-ten-drift-current-native-baseline";
    const string DriftPlanSha = "4983b25365843c950c876f585f105adfa2cd8169e234d3b8a5068873107c9f0c";
    [Serializable] public sealed class DriftRow {
        public string path, originalSha256, previousSha256, currentSha256, metadataSha256, guid, expectedNativeStateSha256, rawSnapshotPath;
        public long originalBytes, currentBytes;
    }
    [Serializable] public sealed class DriftPlan {
        public int schemaVersion, changedSincePreviousProof, historicalBodyBindings;
        public string kind, originalPlanSha256, originalAuditSha256, inventorySha256, canonicalSha256, previousProofPath, previousProofSha256;
        public bool actualAssetsModified;
        public DriftRow[] rows;
    }
    [Serializable] public sealed class CurrentNativeBaseline {
        public string path, currentNativeStateSha256, previousNativeStateSha256, currentNativeState;
        public bool equalToPrevious;
    }
    [Serializable] public sealed class DriftReport {
        public int schemaVersion = 1, materialsVerified, metadataVerified, nativeStatesEqualToPreviousProof, activeSlotsVerified, driftBodiesVerified, observedUnityErrors;
        public string kind = DriftKind, status = "checking", startedUtc, completedUtc, project, runDirectory, driftPlanSha256 = DriftPlanSha,
            originalPlanSha256 = PlanSha, originalAuditSha256 = AuditSha, inventorySha256 = InventorySha, canonicalSha256, previousProofPath, previousProofSha256;
        public int currentNativeBaselineCaptured, historicalNativeMismatches;
        public string baselinePolicy = "Current unapproved integration state; no historical-native equivalence claim. Exact current84 native values are compared before/after null clearing in the same session.";
        public List<CurrentNativeBaseline> nativeBaseline = new List<CurrentNativeBaseline>();
        public bool assetsSaved, materialsModified, sourceArchivesModified, scenesOpened;
        public List<string> errors = new List<string>();
    }
    static string DriftPlanPath { get { return Path.Combine(Work, "helper-candidates/missing-texture-current-baseline/current-baseline-plan.json"); } }
    static string DriftLatestPath { get { return Path.Combine(Project, "Library/YamyamAssetLibrary/missing-texture-current-baseline-proof-report.json"); } }
    static DriftPlan BindBoundedDrift(Plan original, Audit audit)
    {
        NoLinks(DriftPlanPath); if (HashFile(DriftPlanPath) != DriftPlanSha) throw new InvalidDataException("Reviewed ten-body drift plan changed.");
        var plan = JsonUtility.FromJson<DriftPlan>(File.ReadAllText(DriftPlanPath));
        if (plan.schemaVersion != 1 || plan.kind != DriftKind || plan.actualAssetsModified || plan.originalPlanSha256 != PlanSha
            || plan.originalAuditSha256 != AuditSha || plan.inventorySha256 != InventorySha || plan.changedSincePreviousProof != 10
            || plan.historicalBodyBindings != 13 || plan.rows == null || plan.rows.Length != 84 || plan.rows.Select(value => value.path).Distinct().Count() != 84
            || plan.rows.Count(value => value.currentSha256 != value.previousSha256) != 10 || plan.rows.Count(value => value.originalSha256 != value.previousSha256) != 3
            || plan.rows.Count(value => value.currentSha256 != value.originalSha256) != 13)
            throw new InvalidDataException("Exact84/10drift/3historical/13current scope required.");
        NoLinks(plan.previousProofPath); if (HashFile(plan.previousProofPath) != plan.previousProofSha256) throw new InvalidDataException("Previous immutable native proof changed.");
        var previous = JsonUtility.FromJson<RebindReport>(File.ReadAllText(plan.previousProofPath));
        NoLinks(RebindPlanPath); if (HashFile(RebindPlanPath) != RebindPlanSha) throw new InvalidDataException("Original three-body canonical plan changed.");
        ValidateReportIdentity(previous, JsonUtility.FromJson<RebindPlan>(File.ReadAllText(RebindPlanPath)));
        string manifestPath = Path.Combine(Work, "staging-manifest.json"); NoLinks(manifestPath);
        if (HashFile(manifestPath) != plan.canonicalSha256 || previous.canonicalSha256 != plan.canonicalSha256) throw new InvalidDataException("Canonical/previous-proof context changed.");
        var manifest = JsonUtility.FromJson<RebindCanonicalManifest>(File.ReadAllText(manifestPath));
        if (manifest.products == null || manifest.products.Length != 84 || manifest.products.Select(value => value.id).Distinct().Count() != 84
            || manifest.products.Any(value => value.status != "complete") || !YamyamAssetLibraryIO.NormalPath(manifest.stageRoot).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(Root)), StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("Exact current84-product root/coverage changed.");
        var all = original.targets.Concat(original.untouchedAuditMaterials).ToArray(); OriginalHashes.Clear();
        if (all.Length != 84 || all.Select(value => value.path).Distinct().Count() != 84) throw new InvalidDataException("Original84-material identity set changed.");
        foreach (var target in all) {
            var row = plan.rows.Single(value => value.path == target.path); var old = previous.materials.Single(value => value.path == target.path);
            var owner = manifest.products.Single(value => target.path.StartsWith(value.folder + "/", StringComparison.Ordinal));
            var canonical = owner.files.Single(value => value.path == target.path); var meta = owner.files.Single(value => value.path == target.path + ".meta");
            if (target.sha256 != row.originalSha256 || target.bytes != row.originalBytes || target.guid != row.guid || target.metadataSha256 != row.metadataSha256
                || old.sha256 != row.previousSha256 || old.nativeStateSha256 != row.expectedNativeStateSha256 || old.metadataSha256 != row.metadataSha256 || old.guid != row.guid
                || canonical.sha256 != row.previousSha256 || canonical.bytes != old.bytes || meta.sha256 != row.metadataSha256 || meta.guid != row.guid)
                throw new InvalidDataException("Historical/current/canonical drift or metadata binding changed.");
            NoLinks(row.rawSnapshotPath); NoLinks(row.rawSnapshotPath + ".meta");
            if (HashFile(row.rawSnapshotPath) != row.currentSha256 || new YamyamAssetLibraryIO.Info(row.rawSnapshotPath).Length != row.currentBytes
                || HashFile(row.rawSnapshotPath + ".meta") != row.metadataSha256) throw new InvalidDataException("Preserved exact current body/metadata snapshot changed.");
            OriginalHashes.Add(target.path, target.sha256); target.sha256 = row.currentSha256; target.bytes = row.currentBytes; VerifyFile(target);
            var material = AssetDatabase.LoadAssetAtPath<Material>(AssetPath(target));
            if (!material) throw new InvalidDataException("Current native material failed to load: " + AssetPath(target));
        }
        VerifyCurrentUnresolvedSlots(original, audit); foreach (var target in all) VerifyFile(target); return plan;
    }
    static void ValidateDriftReport(DriftReport report, DriftPlan plan)
    {
        if (report.schemaVersion != 1 || report.kind != DriftKind || report.status != "complete" || report.observedUnityErrors != 0 || report.errors == null || report.errors.Count != 0
            || report.assetsSaved || report.materialsModified || report.sourceArchivesModified || report.scenesOpened
            || string.IsNullOrEmpty(report.completedUtc) || string.IsNullOrEmpty(report.project) || report.project.Replace('\\', '/') != ProjectExpected
            || report.driftPlanSha256 != DriftPlanSha || report.originalPlanSha256 != PlanSha || report.originalAuditSha256 != AuditSha || report.inventorySha256 != InventorySha
            || report.canonicalSha256 != plan.canonicalSha256 || report.previousProofPath != plan.previousProofPath || report.previousProofSha256 != plan.previousProofSha256
            || report.materialsVerified != 84 || report.metadataVerified != 84 || report.currentNativeBaselineCaptured != 84 || report.activeSlotsVerified != 37 || report.driftBodiesVerified != 10
            || report.nativeBaseline == null || report.nativeBaseline.Count != 84 || report.nativeBaseline.Select(value => value.path).Distinct().Count() != 84
            || report.nativeStatesEqualToPreviousProof != report.nativeBaseline.Count(value => value.equalToPrevious)
            || report.historicalNativeMismatches != report.nativeBaseline.Count(value => !value.equalToPrevious)
            || report.nativeStatesEqualToPreviousProof + report.historicalNativeMismatches != 84
            || report.nativeBaseline.Any(value => string.IsNullOrEmpty(value.currentNativeState) || HashText(value.currentNativeState) != value.currentNativeStateSha256
                || value.equalToPrevious != (value.currentNativeStateSha256 == value.previousNativeStateSha256)))
            throw new InvalidDataException("Complete exact ten-body read-only proof is absent or changed.");
    }
    static string ApplyDriftProof(Plan original, Audit audit)
    {
        var plan = BindBoundedDrift(original, audit); NoLinks(DriftLatestPath);
        var report = JsonUtility.FromJson<DriftReport>(File.ReadAllText(DriftLatestPath)); ValidateDriftReport(report, plan);
        foreach (var target in original.targets.Concat(original.untouchedAuditMaterials)) {
            var baseline = report.nativeBaseline.Single(value => value.path == target.path); var row = plan.rows.Single(value => value.path == target.path);
            var material = AssetDatabase.LoadAssetAtPath<Material>(AssetPath(target));
            if (baseline.previousNativeStateSha256 != row.expectedNativeStateSha256 || !material || NativeState(material) != baseline.currentNativeState)
                throw new InvalidDataException("Current native state changed after its fresh same-session baseline: " + AssetPath(target));
        }
        return HashFile(DriftLatestPath);
    }
    static void BuildDriftProof()
    {
        Guard(); string local = Path.Combine(Project, "Library/YamyamAssetLibrary"), run = Path.Combine(local, "missing-texture-current-baseline-proof", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N"));
        NoLinks(run); Directory.CreateDirectory(run); var report = new DriftReport { project = Project, runDirectory = run, startedUtc = DateTime.UtcNow.ToString("o") };
        Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } };
        Application.logMessageReceived += capture;
        try {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating) throw new InvalidOperationException("Drift proof requires idle editor.");
            string originalPlanPath = Path.Combine(Work, "missing-texture-default-adaptation-plan.json"), auditPath = Path.Combine(local, "missing-texture-native-audit-report.json"), inventoryPath = Path.Combine(Work, "missing-texture-source-guid-inventory.json");
            foreach (string path in new[] { originalPlanPath, auditPath, inventoryPath }) NoLinks(path);
            if (HashFile(originalPlanPath) != PlanSha || HashFile(auditPath) != AuditSha || HashFile(inventoryPath) != InventorySha) throw new InvalidDataException("Original plan/audit/source-absence evidence changed.");
            var original = JsonUtility.FromJson<Plan>(File.ReadAllText(originalPlanPath)); var audit = JsonUtility.FromJson<Audit>(File.ReadAllText(auditPath));
            if (audit.status != "complete" || audit.observedUnityErrors != 0 || original.targets.Length != 28 || original.untouchedAuditMaterials.Length != 56 || original.targets.Sum(value => value.pairs.Length) != 37)
                throw new InvalidDataException("Historical complete84/28/37 native scope changed.");
            var plan = BindBoundedDrift(original, audit); report.canonicalSha256 = plan.canonicalSha256; report.previousProofPath = plan.previousProofPath; report.previousProofSha256 = plan.previousProofSha256;
            foreach (var target in original.targets.Concat(original.untouchedAuditMaterials)) {
                var row = plan.rows.Single(value => value.path == target.path); var material = AssetDatabase.LoadAssetAtPath<Material>(AssetPath(target));
                if (!material) throw new InvalidDataException("Current baseline material failed to load.");
                string current = NativeState(material), currentHash = HashText(current); bool same = currentHash == row.expectedNativeStateSha256;
                report.nativeBaseline.Add(new CurrentNativeBaseline { path = target.path, currentNativeState = current, currentNativeStateSha256 = currentHash,
                    previousNativeStateSha256 = row.expectedNativeStateSha256, equalToPrevious = same });
                report.currentNativeBaselineCaptured++; if (same) report.nativeStatesEqualToPreviousProof++; else report.historicalNativeMismatches++;
                VerifyFile(target);
            }
            report.materialsVerified = report.metadataVerified = 84; report.activeSlotsVerified = 37; report.driftBodiesVerified = 10;
            File.Copy(DriftPlanPath, Path.Combine(run, "drift-plan.json"), false); File.Copy(plan.previousProofPath, Path.Combine(run, "previous-complete-native-proof.json"), false);
            if (report.observedUnityErrors != 0) throw new InvalidDataException("Native errors observed during the complete read-only proof."); report.status = "complete";
        } catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); throw; }
        finally { Application.logMessageReceived -= capture; report.completedUtc = DateTime.UtcNow.ToString("o"); WriteAtomic(Path.Combine(run, "report.json"), JsonUtility.ToJson(report, true)); WriteAtomic(DriftLatestPath, JsonUtility.ToJson(report, true)); }
    }
    static void VerifyFreshBaselineAfter(Plan original)
    {
        NoLinks(DriftLatestPath); var report = JsonUtility.FromJson<DriftReport>(File.ReadAllText(DriftLatestPath));
        NoLinks(DriftPlanPath); if (HashFile(DriftPlanPath) != DriftPlanSha) throw new InvalidDataException("Baseline plan changed during null clearing.");
        var plan = JsonUtility.FromJson<DriftPlan>(File.ReadAllText(DriftPlanPath)); ValidateDriftReport(report, plan);
        foreach (var target in original.targets.Concat(original.untouchedAuditMaterials)) {
            var baseline = report.nativeBaseline.Single(value => value.path == target.path); var material = AssetDatabase.LoadAssetAtPath<Material>(AssetPath(target));
            if (!material || NativeState(material) != baseline.currentNativeState || HashFile(Absolute(AssetPath(target)) + ".meta") != target.metadataSha256)
                throw new InvalidDataException("Explicit-null clearing changed a current native material value or metadata: " + AssetPath(target));
        }
    }
    public static void RunHeadlessCurrentBaseline()
    {
        Guard(); try { BuildDriftProof(); } catch (Exception error) { Debug.LogError(error); EditorApplication.Exit(1); return; }
        // The existing adapter owns both its success/failure report and Exit;
        // no second Editor startup or later Exit0 may override that result.
        RunHeadless();
    }
}
