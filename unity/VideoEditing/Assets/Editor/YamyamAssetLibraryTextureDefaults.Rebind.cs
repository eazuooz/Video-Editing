using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;

// Fresh native evidence for three already-canonical material bodies. Historical
// audit/absence evidence stays immutable; no semantic equivalence is invented.
public static partial class YamyamAssetLibraryTextureDefaults
{
    const string RebindKind = "three-canonical-material-native-texture-rebind";
    const string RebindPlanSha = "17f665071053894592971ba0c623a3aa618c94dc0f61bcf912a88be8fe559fb0";
    [Serializable] public sealed class RebindBinding {
        public string path, oldSha256, currentSha256, metadataSha256, guid;
        public long oldBytes, currentBytes;
    }
    [Serializable] public sealed class RebindPlan {
        public int schemaVersion, expectedMaterials, expectedActiveSlots;
        public string kind, originalPlanSha256, originalAuditSha256, inventorySha256, canonicalSha256;
        public bool actualAssetsModified, sourceArchivesModified;
        public RebindBinding[] bindings;
    }
    [Serializable] public sealed class RebindCanonicalFile { public string path, sha256, guid; public long bytes; }
    [Serializable] public sealed class RebindCanonicalProduct { public string id, folder, status; public RebindCanonicalFile[] files; }
    [Serializable] public sealed class RebindCanonicalManifest { public string stageRoot; public RebindCanonicalProduct[] products; }
    [Serializable] public sealed class RebindMaterial {
        public string path, sha256, metadataSha256, guid, nativeStateSha256;
        public long bytes;
    }
    [Serializable] public sealed class RebindReport {
        public int schemaVersion = 1, materialsVerified, activeSlotsVerified, metadataVerified, observedUnityErrors;
        public string kind = RebindKind, status = "checking", startedUtc, completedUtc, project, runDirectory,
            rebindPlanSha256, originalPlanSha256, originalAuditSha256, inventorySha256, canonicalSha256;
        public bool assetsSaved, materialsModified, sourceArchivesModified, scenesOpened;
        public RebindBinding[] bindings;
        public List<RebindMaterial> materials = new List<RebindMaterial>();
        public List<string> errors = new List<string>();
    }
    static readonly Dictionary<string, string> OriginalHashes = new Dictionary<string, string>(StringComparer.Ordinal);
    static string OriginalSha(Target target) { string value; return OriginalHashes.TryGetValue(target.path, out value) ? value : target.sha256; }
    static string RebindPlanPath { get { return Path.Combine(Work, "helper-candidates/missing-texture-rebind/rebind-plan.json"); } }
    static string RebindLatestPath { get { return Path.Combine(Project, "Library/YamyamAssetLibrary/missing-texture-rebind-proof-report.json"); } }
    static RebindPlan BindThreeCurrentCanonicalBodies(Plan plan)
    {
        NoLinks(RebindPlanPath);
        if (HashFile(RebindPlanPath) != RebindPlanSha) throw new InvalidDataException("Exact three-material rebind plan changed.");
        var binding = JsonUtility.FromJson<RebindPlan>(File.ReadAllText(RebindPlanPath));
        if (binding.schemaVersion != 1 || binding.kind != RebindKind || binding.actualAssetsModified || binding.sourceArchivesModified
            || binding.originalPlanSha256 != PlanSha || binding.originalAuditSha256 != AuditSha || binding.inventorySha256 != InventorySha
            || binding.expectedMaterials != 84 || binding.expectedActiveSlots != 37 || binding.bindings == null || binding.bindings.Length != 3
            || binding.bindings.Select(value => value.path).Distinct(StringComparer.Ordinal).Count() != 3)
            throw new InvalidDataException("Unreviewed rebind scope or historical evidence identity.");
        string manifestPath = Path.Combine(Work, "staging-manifest.json"); NoLinks(manifestPath);
        if (HashFile(manifestPath) != binding.canonicalSha256) throw new InvalidDataException("Rebind canonical snapshot changed; inspect and prepare a new bounded proof.");
        var manifest = JsonUtility.FromJson<RebindCanonicalManifest>(File.ReadAllText(manifestPath));
        if (manifest.products == null || manifest.products.Length != 84 || manifest.products.Select(value => value.id).Distinct().Count() != 84
            || manifest.products.Any(value => value.status != "complete")
            || !YamyamAssetLibraryIO.NormalPath(manifest.stageRoot).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(Root)), StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("Current exact84-product canonical root/coverage changed.");
        var all = plan.targets.Concat(plan.untouchedAuditMaterials).ToArray(); OriginalHashes.Clear();
        foreach (var row in binding.bindings) {
            var matches = plan.targets.Where(value => value.path == row.path).ToArray();
            var owners = manifest.products.Where(value => row.path.StartsWith(value.folder + "/", StringComparison.Ordinal)).ToArray();
            if (matches.Length != 1 || owners.Length != 1) throw new InvalidDataException("Rebind target lacks one original active target and current product owner.");
            var target = matches[0]; var body = owners[0].files.Where(value => value.path == row.path).ToArray();
            var meta = owners[0].files.Where(value => value.path == row.path + ".meta").ToArray();
            if (target.sha256 != row.oldSha256 || target.bytes != row.oldBytes || target.guid != row.guid || target.metadataSha256 != row.metadataSha256
                || body.Length != 1 || body[0].sha256 != row.currentSha256 || body[0].bytes != row.currentBytes
                || meta.Length != 1 || meta[0].sha256 != row.metadataSha256 || meta[0].guid != row.guid
                || row.oldSha256 == row.currentSha256) throw new InvalidDataException("Rebind changes unreviewed original/current body or metadata ownership.");
            OriginalHashes.Add(target.path, target.sha256); target.sha256 = row.currentSha256; target.bytes = row.currentBytes;
        }
        foreach (var target in all) VerifyFile(target);
        return binding;
    }
    static void VerifyCurrentUnresolvedSlots(Plan plan, Audit audit)
    {
        foreach (var target in plan.targets) {
            string asset = AssetPath(target); var material = AssetDatabase.LoadAssetAtPath<Material>(asset);
            string guid; long localId;
            if (!material || !material.shader || !material.shader.isSupported || material.shader.name != target.shader
                || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out localId) || guid != target.guid)
                throw new InvalidDataException("Fresh native material/shader identity differs.");
            var references = References(File.ReadAllText(Absolute(asset)));
            foreach (var pair in target.pairs) {
                string reference; int property = material.shader.FindPropertyIndex(pair.property);
                if (!references.TryGetValue(pair.property, out reference) || !ExactReference(reference, pair) || property < 0
                    || material.shader.GetPropertyType(property) != ShaderPropertyType.Texture || material.GetTexture(pair.property)
                    || !string.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(pair.guid)))
                    throw new InvalidDataException("Fresh binding is not the same unresolved active effective-null slot.");
                if (audit.findings.Count(value => value.path == asset && value.materialGuid == target.guid && value.sourceSha256 == OriginalSha(target)
                    && value.metadataSha256 == target.metadataSha256 && value.shader == target.shader && value.property == pair.property
                    && value.missingGuid == pair.guid && value.sourceFileId == pair.fileID && value.classification == "active-missing-effective-null"
                    && value.effectiveNull && value.textureProperty && string.IsNullOrEmpty(value.resolvedAssetPath)) != 1)
                    throw new InvalidDataException("Fresh unresolved slot lacks the exact immutable historical audit identity.");
            }
        }
    }
    static string ApplyNativeRebindProof(Plan plan, Audit audit)
    {
        var binding = BindThreeCurrentCanonicalBodies(plan); NoLinks(RebindLatestPath);
        var report = JsonUtility.FromJson<RebindReport>(File.ReadAllText(RebindLatestPath));
        ValidateReportIdentity(report, binding);
        foreach (var target in plan.targets.Concat(plan.untouchedAuditMaterials)) {
            var current = report.materials.Single(value => value.path == target.path);
            var material = AssetDatabase.LoadAssetAtPath<Material>(AssetPath(target));
            if (current.sha256 != target.sha256 || current.bytes != target.bytes || current.guid != target.guid || current.metadataSha256 != target.metadataSha256
                || !material || HashText(NativeState(material)) != current.nativeStateSha256)
                throw new InvalidDataException("Material body/native state changed after the read-only rebind proof.");
        }
        VerifyCurrentUnresolvedSlots(plan, audit); return HashFile(RebindLatestPath);
    }
    static void ValidateReportIdentity(RebindReport report, RebindPlan binding)
    {
        if (report.schemaVersion != 1 || report.kind != RebindKind || report.status != "complete" || report.observedUnityErrors != 0
            || report.assetsSaved || report.materialsModified || report.sourceArchivesModified || report.scenesOpened || report.errors == null || report.errors.Count != 0
            || string.IsNullOrEmpty(report.project) || !report.project.Replace('\\', '/').Equals(ProjectExpected, StringComparison.OrdinalIgnoreCase)
            || report.rebindPlanSha256 != RebindPlanSha || report.originalPlanSha256 != PlanSha || report.originalAuditSha256 != AuditSha
            || report.inventorySha256 != InventorySha || report.canonicalSha256 != binding.canonicalSha256
            || report.materialsVerified != 84 || report.activeSlotsVerified != 37 || report.metadataVerified != 84
            || string.IsNullOrEmpty(report.completedUtc) || report.materials == null || report.materials.Count != 84
            || report.materials.Select(value => value.path).Distinct().Count() != 84
            || report.bindings == null || report.bindings.Length != 3 || binding.bindings == null || binding.bindings.Length != 3)
            throw new InvalidDataException("Completed exact read-only native rebind proof is absent or changed.");
        for (int index = 0; index < 3; index++) {
            var actual = report.bindings[index]; var expected = binding.bindings[index];
            if (actual.path != expected.path || actual.oldSha256 != expected.oldSha256 || actual.oldBytes != expected.oldBytes
                || actual.currentSha256 != expected.currentSha256 || actual.currentBytes != expected.currentBytes
                || actual.guid != expected.guid || actual.metadataSha256 != expected.metadataSha256)
                throw new InvalidDataException("Native rebind proof altered an exact old/current body or metadata binding.");
        }
    }
    public static void RunHeadlessRebindProof()
    {
        Guard(); int exit = 0; string local = Path.Combine(Project, "Library/YamyamAssetLibrary");
        string run = Path.Combine(local, "missing-texture-rebind-proof", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N"));
        NoLinks(run); Directory.CreateDirectory(run); var report = new RebindReport { project = Project, runDirectory = run, startedUtc = DateTime.UtcNow.ToString("o") };
        Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } };
        Application.logMessageReceived += capture;
        try {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating) throw new InvalidOperationException("Native proof requires an idle editor.");
            string planPath = Path.Combine(Work, "missing-texture-default-adaptation-plan.json"), auditPath = Path.Combine(local, "missing-texture-native-audit-report.json"), inventoryPath = Path.Combine(Work, "missing-texture-source-guid-inventory.json");
            foreach (string path in new[] { planPath, auditPath, inventoryPath }) NoLinks(path);
            if (HashFile(planPath) != PlanSha || HashFile(auditPath) != AuditSha || HashFile(inventoryPath) != InventorySha) throw new InvalidDataException("Historical plan/native audit/original-package absence inventory changed.");
            var plan = JsonUtility.FromJson<Plan>(File.ReadAllText(planPath)); var audit = JsonUtility.FromJson<Audit>(File.ReadAllText(auditPath));
            if (audit.status != "complete" || audit.observedUnityErrors != 0 || plan.targets == null || plan.targets.Length != 28
                || plan.untouchedAuditMaterials == null || plan.untouchedAuditMaterials.Length != 56 || plan.targets.Sum(value => value.pairs.Length) != 37)
                throw new InvalidDataException("Historical complete84/28/37 scope changed.");
            var binding = BindThreeCurrentCanonicalBodies(plan); report.bindings = binding.bindings;
            report.rebindPlanSha256 = RebindPlanSha; report.originalPlanSha256 = PlanSha; report.originalAuditSha256 = AuditSha;
            report.inventorySha256 = InventorySha; report.canonicalSha256 = binding.canonicalSha256;
            VerifyCurrentUnresolvedSlots(plan, audit); report.activeSlotsVerified = plan.targets.Sum(value => value.pairs.Length);
            foreach (var target in plan.targets.Concat(plan.untouchedAuditMaterials)) {
                VerifyFile(target); var material = AssetDatabase.LoadAssetAtPath<Material>(AssetPath(target)); if (!material) throw new InvalidDataException("Native proof material failed to load.");
                report.materials.Add(new RebindMaterial { path = target.path, sha256 = target.sha256, bytes = target.bytes, guid = target.guid, metadataSha256 = target.metadataSha256, nativeStateSha256 = HashText(NativeState(material)) });
                report.materialsVerified++; report.metadataVerified++;
            }
            foreach (var target in plan.targets.Concat(plan.untouchedAuditMaterials)) VerifyFile(target);
            if (HashFile(Path.Combine(Work, "staging-manifest.json")) != binding.canonicalSha256 || report.observedUnityErrors != 0
                || report.materialsVerified != 84 || report.activeSlotsVerified != 37 || report.metadataVerified != 84) throw new InvalidDataException("Native proof context/count/error changed.");
            File.Copy(RebindPlanPath, Path.Combine(run, "rebind-plan.json"), false); File.Copy(planPath, Path.Combine(run, "original-plan.json"), false);
            File.Copy(auditPath, Path.Combine(run, "original-audit.json"), false); File.Copy(inventoryPath, Path.Combine(run, "original-source-inventory.json"), false);
            report.status = "complete";
        } catch (Exception error) { exit = 1; report.status = "failed"; report.errors.Add(error.ToString()); }
        finally { Application.logMessageReceived -= capture; report.completedUtc = DateTime.UtcNow.ToString("o");
            WriteAtomic(Path.Combine(run, "report.json"), JsonUtility.ToJson(report, true)); WriteAtomic(RebindLatestPath, JsonUtility.ToJson(report, true)); }
        EditorApplication.Exit(exit);
    }
}
