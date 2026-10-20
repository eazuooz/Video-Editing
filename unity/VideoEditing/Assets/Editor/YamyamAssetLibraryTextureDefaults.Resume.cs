using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;

public static partial class YamyamAssetLibraryTextureDefaults
{
    const string ResumePlanSha = "40da00c8a5b109882cd2086acfc149093d71b7799c5c1c43182180a8730525ef";
    [Serializable] public sealed class ResumeInput { public Target current; public string snapshotPath; public bool target, alreadyCleared; }
    [Serializable] public sealed class ResumePlan {
        public int schemaVersion;
        public string kind, failedReportPath, failedReportSha256, currentBaselineProofPath, currentBaselineProofSha256, canonicalSha256, previewsSha256;
        public string priorResumeReportPath, priorResumeReportSha256, priorResumePlanPath, priorResumePlanSha256;
        public bool actualAssetsModified;
        public ResumeInput[] inputs;
        public ImageProof[] images;
    }
    [Serializable] public sealed class ResumeNative {
        public string path, currentState, beforeSha256, afterSha256, guid;
        public long beforeLocalId, afterLocalId;
    }
    [Serializable] public sealed class ResumeChange {
        public string path, beforeSha256, expectedPatchSha256, actualAfterSha256;
        public bool intentRecorded, written, alreadyCleared;
        public string[] explicitDefaultAdditions;
    }
    [Serializable] public sealed class ResumeReport {
        public int schemaVersion = 1, observedUnityErrors, currentNativeBaselineCaptured, currentNativeValuesPreserved, reusedMaterials, newlyPatchedMaterials, completedMaterials, clearedBindings, untouchedMaterialsVerified, previewsRetained;
        public string kind = "bounded-ten-retained18-atomic-text-null-reference-resume", status = "checking", startedUtc, completedUtc, project, runDirectory, sourcePlanSha256 = ResumePlanSha,
            priorResumeReportPath, priorResumeReportSha256, priorResumePlanPath, priorResumePlanSha256, originalFailedReportPath, originalFailedReportSha256, sourceCurrentBaselineProofPath, sourceCurrentBaselineProofSha256, canonicalSha256, completedReportPath, completedReportSha256;
        public bool assetsModified, originalSourcesModified, sourceArchivesModified, originalFailedEvidenceModified;
        public string normalizationPolicy = "Existing serialized values remain exact. Only two official SSR float properties may be newly serialized at value1, with strict full-native equality; each addition is explicitly listed. No native Save/SetDirty/SetTexture is called by this recovery.";
        public List<ResumeNative> native = new List<ResumeNative>(); public List<ResumeChange> changes = new List<ResumeChange>(); public List<string> errors = new List<string>();
    }
    static readonly string[] AllowedExplicitDefaults = { "_ScreenSpaceReflections", "_ScreenSpaceReflectionsContributeTransparent" };
    static string NullOnlyPatch(string text, Pair[] pairs, bool alreadyNull)
    {
        var target = pairs.ToDictionary(value => value.property, StringComparer.Ordinal); var seen = new HashSet<string>(StringComparer.Ordinal);
        string result = TextureEntry.Replace(text, match => {
            Pair pair; if (!target.TryGetValue(match.Groups["name"].Value, out pair)) return match.Value;
            if (!seen.Add(pair.property) || (alreadyNull ? !Regex.IsMatch(match.Groups["reference"].Value.Trim(), @"^fileID:[ \t]*0[ \t]*$") : !ExactReference(match.Groups["reference"].Value, pair)))
                throw new InvalidDataException("Exact unique pending/cleared texture reference changed.");
            return match.Groups["head"].Value + "{fileID: 0}";
        });
        if (!seen.SetEquals(target.Keys)) throw new InvalidDataException("Pending texture slot was not serialized exactly once."); return result;
    }
    static string[] VerifyPatchAndOnlyExplicitDefaults(string expected, string actual)
    {
        string retained = actual; var additions = new List<string>();
        foreach (string name in AllowedExplicitDefaults) {
            string declaration = @"(?m)^    - " + Regex.Escape(name) + @":[^\r\n]*\r?\n";
            if (Regex.IsMatch(expected, declaration)) continue;
            var values = Regex.Matches(retained, declaration); if (values.Count == 0) continue;
            if (values.Count != 1 || !Regex.IsMatch(values[0].Value, @"^    - " + Regex.Escape(name) + @": 1\r?\n$"))
                throw new InvalidDataException("Unreviewed explicit SSR value or duplicate serialized default.");
            retained = retained.Remove(values[0].Index, values[0].Length); additions.Add(name);
        }
        if (retained != expected) throw new InvalidDataException("Import changed serialized content outside the exact null references and two explicit SSR defaults.");
        return additions.ToArray();
    }
    static void ResumeAtomicBytes(string path, byte[] bytes)
    {
        NoLinks(path); string temporary = Path.Combine(Path.GetDirectoryName(path), ".nr-" + Guid.NewGuid().ToString("N").Substring(0, 12) + ".tmp"); NoLinks(temporary);
        using (var stream = new YamyamAssetLibraryIO.Stream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None)) { stream.Write(bytes, 0, bytes.Length); stream.Flush(true); }
        if (HashFile(temporary) != Hash(bytes)) throw new IOException("Exact patch temporary verification failed.");
        string destinationSha = HashFile(path);
        for (int attempt = 0; ; attempt++) {
            try {
                NoLinks(path); NoLinks(temporary);
                if (HashFile(path) != destinationSha || HashFile(temporary) != Hash(bytes)) throw new InvalidDataException("Atomic patch input changed during retry.");
                File.Replace(temporary, path, null);
                if (HashFile(path) != Hash(bytes)) throw new InvalidDataException("Atomic patch destination verification failed."); return;
            }
            catch (IOException error) { int code = error.HResult & 0xffff; if (attempt >= 4 || !(code == 5 || code == 32 || code == 33 || code == 1175)) throw; }
            catch (UnauthorizedAccessException) { if (attempt >= 4) throw; }
            System.Threading.Thread.Sleep(100 * (attempt + 1));
        }
    }
    static void ResumePendingReferences()
    {
        Guard(); if (EditorApplication.isCompiling || EditorApplication.isUpdating) throw new InvalidOperationException("Resume requires idle editor.");
        string local = Path.Combine(Project, "Library/YamyamAssetLibrary"), run = Path.Combine(local, "missing-texture-default-atomic-resume", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N"));
        NoLinks(run); Directory.CreateDirectory(run); var report = new ResumeReport { project = Project, runDirectory = run, startedUtc = DateTime.UtcNow.ToString("o") };
        Action persist = () => WriteAtomic(Path.Combine(run, "report.json"), JsonUtility.ToJson(report, true));
        Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } };
        Application.logMessageReceived += capture;
        try {
            string planPath = Path.Combine(Work, "helper-candidates/missing-texture-atomic-resume/atomic-resume-plan.json"); NoLinks(planPath);
            if (HashFile(planPath) != ResumePlanSha) throw new InvalidDataException("Bounded84/28/10/18 atomic resume plan changed.");
            var plan = JsonUtility.FromJson<ResumePlan>(File.ReadAllText(planPath));
            if (plan.schemaVersion != 1 || plan.kind != report.kind || plan.actualAssetsModified || plan.inputs == null || plan.inputs.Length != 84 || plan.inputs.Select(value => value.current.path).Distinct().Count() != 84
                || plan.inputs.Count(value => value.target) != 28 || plan.inputs.Count(value => value.alreadyCleared) != 10 || plan.inputs.Any(value => value.alreadyCleared && !value.target)
                || plan.images == null || plan.images.Length != 84) throw new InvalidDataException("Exact current84/28targets/10reused/18pending scope required.");
            string manifestPath = Path.Combine(Work, "staging-manifest.json"), originalPlanPath = Path.Combine(Work, "missing-texture-default-adaptation-plan.json"), auditPath = Path.Combine(local, "missing-texture-native-audit-report.json"), inventoryPath = Path.Combine(Work, "missing-texture-source-guid-inventory.json");
            foreach (string path in new[] { manifestPath, originalPlanPath, auditPath, inventoryPath, plan.failedReportPath, plan.currentBaselineProofPath, plan.priorResumeReportPath, plan.priorResumePlanPath }) NoLinks(path);
            if (HashFile(manifestPath) != plan.canonicalSha256 || HashFile(originalPlanPath) != PlanSha || HashFile(auditPath) != AuditSha || HashFile(inventoryPath) != InventorySha
                || HashFile(plan.failedReportPath) != plan.failedReportSha256 || HashFile(plan.currentBaselineProofPath) != plan.currentBaselineProofSha256
                || HashFile(plan.priorResumeReportPath) != plan.priorResumeReportSha256 || HashFile(plan.priorResumePlanPath) != plan.priorResumePlanSha256)
                throw new InvalidDataException("Canonical or immutable original/absence/baseline/failure evidence changed.");
            var original = JsonUtility.FromJson<Plan>(File.ReadAllText(originalPlanPath)); var failed = JsonUtility.FromJson<Report>(File.ReadAllText(plan.failedReportPath));
            var baseline = JsonUtility.FromJson<DriftReport>(File.ReadAllText(plan.currentBaselineProofPath));
            if (failed.status != "failed" || failed.observedUnityErrors != 0 || failed.materialsPrepared != 28 || failed.materialsSaved != 1 || failed.materials.Count != 28
                || failed.materials.Count(value => value.saved) != 2 || failed.nativeRebindProofSha256 != plan.currentBaselineProofSha256 || failed.errors.Count != 1
                || !failed.errors[0].StartsWith("System.IO.InvalidDataException: Effective material/defaults or unrelated serialized properties changed.", StringComparison.Ordinal)
                || baseline.status != "complete" || baseline.observedUnityErrors != 0 || baseline.currentNativeBaselineCaptured != 84 || baseline.activeSlotsVerified != 37)
                throw new InvalidDataException("Only the exact first-complete/second-explicit-SSR terminal failure can resume.");
            var priorResume = JsonUtility.FromJson<ResumeReport>(File.ReadAllText(plan.priorResumeReportPath));
            var priorPlan = JsonUtility.FromJson<ResumePlan>(File.ReadAllText(plan.priorResumePlanPath));
            if (plan.priorResumePlanSha256 != "a17b543fde034838dc5032a7ce7c587b6760dbaa564f40f2795deae801ce54fa" || priorResume.sourcePlanSha256 != plan.priorResumePlanSha256
                || priorResume.status != "failed" || priorResume.observedUnityErrors != 0 || priorResume.completedMaterials != 10 || priorResume.reusedMaterials != 2 || priorResume.newlyPatchedMaterials != 8
                || priorResume.currentNativeBaselineCaptured != 84 || priorResume.native.Count != 84 || priorResume.native.Select(value => value.path).Distinct().Count() != 84
                || priorResume.errors.Count != 1 || !priorResume.errors[0].StartsWith("System.IO.IOException:", StringComparison.Ordinal) || !priorResume.errors[0].Contains("ResumeAtomicBytes")
                || priorResume.changes.Count != 11 || priorResume.changes.Count(value => !string.IsNullOrEmpty(value.actualAfterSha256)) != 10
                || priorResume.changes.Count(value => value.written && !string.IsNullOrEmpty(value.actualAfterSha256)) != 8
                || !priorResume.changes[10].intentRecorded || priorResume.changes[10].written || !string.IsNullOrEmpty(priorResume.changes[10].actualAfterSha256))
                throw new InvalidDataException("Only the exact completed10/pending18 atomic-file-replacement failure can resume.");
            report.priorResumeReportPath = plan.priorResumeReportPath; report.priorResumeReportSha256 = plan.priorResumeReportSha256;
            report.priorResumePlanPath = plan.priorResumePlanPath; report.priorResumePlanSha256 = plan.priorResumePlanSha256;
            report.originalFailedReportPath = plan.failedReportPath; report.originalFailedReportSha256 = plan.failedReportSha256; report.sourceCurrentBaselineProofPath = plan.currentBaselineProofPath;
            report.sourceCurrentBaselineProofSha256 = plan.currentBaselineProofSha256; report.canonicalSha256 = plan.canonicalSha256;
            var materials = new Dictionary<string, Material>(StringComparer.Ordinal);
            var retainedNormalizations = new Dictionary<string, string[]>(StringComparer.Ordinal);
            foreach (var input in plan.inputs) {
                var target = input.current; VerifyFile(target); NoLinks(input.snapshotPath); NoLinks(input.snapshotPath + ".meta");
                if (HashFile(input.snapshotPath) != target.sha256 || HashFile(input.snapshotPath + ".meta") != target.metadataSha256) throw new InvalidDataException("Preserved current input snapshot changed.");
                var material = AssetDatabase.LoadAssetAtPath<Material>(AssetPath(target)); string guid; long id;
                if (!material || !material.shader || !material.shader.isSupported || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out id) || guid != target.guid)
                    throw new InvalidDataException("Current native material/shader/GUID identity differs.");
                materials.Add(target.path, material); string state = NativeState(material);
                var fixedNative = priorResume.native.Single(value => value.path == target.path);
                if (fixedNative.currentState != state || fixedNative.beforeSha256 != HashText(state) || fixedNative.guid != guid || fixedNative.beforeLocalId != id)
                    throw new InvalidDataException("Current native state differs from the exact immutable prior84 baseline; no rebaseline is permitted.");
                report.native.Add(new ResumeNative { path = target.path, currentState = state, beforeSha256 = HashText(state), guid = guid, beforeLocalId = id }); report.currentNativeBaselineCaptured++;
                if (input.target) {
                    var source = original.targets.Single(value => value.path == target.path); var prior = failed.materials.Single(value => value.path == AssetPath(target));
                    if (source.guid != target.guid || source.metadataSha256 != target.metadataSha256 || prior.saved != priorPlan.inputs.Single(value => value.current.path == target.path).alreadyCleared || prior.guid != target.guid || prior.localId != id
                        || HashFile(prior.backup) != prior.beforeSha256 || HashFile(prior.metadataBackup) != target.metadataSha256 || prior.bindings.Length != source.pairs.Length)
                        throw new InvalidDataException("Exact original target/backup/pending status changed.");
                    if (input.alreadyCleared) {
                        var completedChange = priorResume.changes.Single(value => value.path == AssetPath(target));
                        if (string.IsNullOrEmpty(completedChange.actualAfterSha256) || target.sha256 != completedChange.actualAfterSha256 || !(completedChange.written || completedChange.alreadyCleared))
                            throw new InvalidDataException("A retained completed material differs from the prior verified actual file.");
                        retainedNormalizations[target.path] = VerifyPatchAndOnlyExplicitDefaults(NullOnlyPatch(File.ReadAllText(prior.backup), source.pairs, false), File.ReadAllText(Absolute(AssetPath(target))));
                        foreach (string name in retainedNormalizations[target.path]) {
                            int index = material.shader.FindPropertyIndex(name);
                            if (index < 0 || material.shader.GetPropertyType(index) != ShaderPropertyType.Float || material.GetFloat(name) != 1)
                                throw new InvalidDataException("Retained serialized SSR addition is not an actual native float default1.");
                        }
                    } else if (target.sha256 != prior.beforeSha256) throw new InvalidDataException("An unfinished material changed after the original complete preflight.");
                    NullOnlyPatch(File.ReadAllText(Absolute(AssetPath(target))), source.pairs, input.alreadyCleared);
                    foreach (var pair in source.pairs) {
                        int property = material.shader.FindPropertyIndex(pair.property);
                        if (property < 0 || material.shader.GetPropertyType(property) != ShaderPropertyType.Texture || material.GetTexture(pair.property) || !string.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(pair.guid)))
                            throw new InvalidDataException("Target is not still the proved active effective-null missing source binding.");
                    }
                }
                VerifyFile(target);
            }
            string previewsPath = Path.Combine(local, "previews.json"); NoLinks(previewsPath);
            if (HashFile(previewsPath) != plan.previewsSha256) throw new InvalidDataException("84-preview source report changed.");
            foreach (var image in plan.images) { NoLinks(image.path); if (HashFile(image.path) != image.beforeSha256) throw new InvalidDataException("Preview source image changed."); }
            File.Copy(planPath, Path.Combine(run, "resume-plan.json"), false); File.Copy(plan.failedReportPath, Path.Combine(run, "original-failed-report.json"), false);
            File.Copy(plan.currentBaselineProofPath, Path.Combine(run, "original-current-baseline-proof.json"), false);
            File.Copy(plan.priorResumeReportPath, Path.Combine(run, "prior-resume-failed-report.json"), false); File.Copy(plan.priorResumePlanPath, Path.Combine(run, "prior-resume-plan.json"), false);
            if (report.currentNativeBaselineCaptured != 84 || report.observedUnityErrors != 0) throw new InvalidDataException("Complete current84 baseline is required before patching.");
            foreach (var input in plan.inputs.Where(value => value.target)) {
                var target = input.current; var source = original.targets.Single(value => value.path == target.path); string path = Absolute(AssetPath(target));
                VerifyFile(target); string before = File.ReadAllText(path), expected = NullOnlyPatch(before, source.pairs, input.alreadyCleared);
                var change = new ResumeChange { path = AssetPath(target), beforeSha256 = target.sha256, expectedPatchSha256 = HashText(expected), alreadyCleared = input.alreadyCleared };
                report.changes.Add(change);
                if (!input.alreadyCleared) {
                    string backup = Path.Combine(run, "backups", target.path); NoLinks(backup); Directory.CreateDirectory(Path.GetDirectoryName(backup)); File.Copy(path, backup, false); File.Copy(path + ".meta", backup + ".meta", false);
                    if (HashFile(backup) != target.sha256 || HashFile(backup + ".meta") != target.metadataSha256) throw new IOException("Fresh pending original backup changed.");
                    change.intentRecorded = true; report.status = "patching-owned-text-reference-only"; persist();
                    if (HashFile(path) != target.sha256) throw new InvalidDataException("Target changed just before exact text patch.");
                    ResumeAtomicBytes(path, Encoding.UTF8.GetBytes(expected)); change.written = true; report.assetsModified = true;
                    AssetDatabase.ImportAsset(AssetPath(target), ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport); report.newlyPatchedMaterials++;
                } else report.reusedMaterials++;
                string actual = File.ReadAllText(path); var additions = VerifyPatchAndOnlyExplicitDefaults(expected, actual);
                change.explicitDefaultAdditions = input.alreadyCleared ? retainedNormalizations[target.path].Concat(additions).Distinct().ToArray() : additions; change.actualAfterSha256 = HashFile(path);
                var material = AssetDatabase.LoadAssetAtPath<Material>(AssetPath(target)); var native = report.native.Single(value => value.path == target.path);
                if (!material || NativeState(material) != native.currentState || HashFile(path + ".meta") != target.metadataSha256) throw new InvalidDataException("Exact reference clearing changed current native values or metadata.");
                foreach (string name in change.explicitDefaultAdditions) {
                    int index = material.shader.FindPropertyIndex(name);
                    if (index < 0 || material.shader.GetPropertyType(index) != ShaderPropertyType.Float || material.GetFloat(name) != 1)
                        throw new InvalidDataException("Serialized SSR addition is not a declared unchanged native float default1.");
                }
                foreach (var pair in source.pairs) if (material.GetTexture(pair.property) || !Regex.IsMatch(References(actual)[pair.property], @"^fileID:[ \t]*0[ \t]*$")) throw new InvalidDataException("Explicit null binding did not persist.");
                report.completedMaterials++; report.clearedBindings += source.pairs.Length; persist();
            }
            foreach (var input in plan.inputs) {
                var target = input.current; var material = AssetDatabase.LoadAssetAtPath<Material>(AssetPath(target)); string guid; long id; var native = report.native.Single(value => value.path == target.path);
                if (!material || NativeState(material) != native.currentState || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out id) || guid != native.guid || id != native.beforeLocalId
                    || HashFile(Absolute(AssetPath(target)) + ".meta") != target.metadataSha256) throw new InvalidDataException("One of84 current native material values/identities changed.");
                native.afterSha256 = HashText(NativeState(material)); native.afterLocalId = id; report.currentNativeValuesPreserved++;
                if (!input.target) { VerifyFile(target); report.untouchedMaterialsVerified++; }
            }
            foreach (var image in plan.images) { if (HashFile(image.path) != image.beforeSha256) throw new InvalidDataException("A retained preview image changed."); report.previewsRetained++; }
            if (HashFile(previewsPath) != plan.previewsSha256 || HashFile(manifestPath) != plan.canonicalSha256 || HashFile(plan.failedReportPath) != plan.failedReportSha256
                || HashFile(plan.priorResumeReportPath) != plan.priorResumeReportSha256 || HashFile(plan.priorResumePlanPath) != plan.priorResumePlanSha256
                || HashFile(plan.currentBaselineProofPath) != plan.currentBaselineProofSha256 || HashFile(originalPlanPath) != PlanSha || HashFile(auditPath) != AuditSha || HashFile(inventoryPath) != InventorySha
                || report.observedUnityErrors != 0 || report.currentNativeValuesPreserved != 84 || report.completedMaterials != 28 || report.reusedMaterials != 10 || report.newlyPatchedMaterials != 18
                || report.clearedBindings != 37 || report.untouchedMaterialsVerified != 56 || report.previewsRetained != 84) throw new InvalidDataException("Final exact84/28/37/10/18 preservation counts/context failed.");
            var completed = JsonUtility.FromJson<Report>(File.ReadAllText(plan.failedReportPath)); completed.errors.Clear(); completed.startedUtc = report.startedUtc; completed.completedUtc = DateTime.UtcNow.ToString("o");
            completed.recoverySourceReportPath = plan.failedReportPath; completed.recoverySourceReportSha256 = plan.failedReportSha256; completed.serializedNormalizationPolicy = report.normalizationPolicy;
            foreach (var item in completed.materials) {
                var input = plan.inputs.Single(value => AssetPath(value.current) == item.path); var native = report.native.Single(value => value.path == input.current.path);
                item.afterSha256 = HashFile(Absolute(item.path)); item.afterBytes = new YamyamAssetLibraryIO.Info(Absolute(item.path)).Length;
                string beforeText = File.ReadAllText(item.backup), actualText = File.ReadAllText(Absolute(item.path));
                var explicitAdditions = VerifyPatchAndOnlyExplicitDefaults(NullOnlyPatch(beforeText, item.bindings, false), actualText);
                foreach (string name in explicitAdditions) actualText = Regex.Replace(actualText, @"(?m)^    - " + Regex.Escape(name) + @": 1\r?\n", "");
                item.beforeSerializedStateSha256 = HashText(SerializedState(beforeText, item.bindings)); item.afterSerializedStateSha256 = HashText(SerializedState(actualText, item.bindings));
                if (item.beforeSerializedStateSha256 != item.afterSerializedStateSha256) throw new InvalidDataException("Existing serialized properties differ after explicit recorded-default projection.");
                item.beforeNativeStateSha256 = native.beforeSha256; item.afterNativeStateSha256 = native.afterSha256; item.nativeDefaultsPreserved = true; item.otherSerializedPropertiesPreserved = true; item.saved = true;
            }
            completed.materialsPrepared = completed.materialsSaved = 28; completed.bindingsCleared = 37; completed.untouchedMaterialsVerified = 56; completed.previewsRetained = 84;
            completed.previewsAfterSha256 = plan.previewsSha256; completed.effectiveMaterialStatesPreserved = completed.obsoleteSavedBindingsPreserved = true; completed.allCurrentNativeValuesPreserved = 84;
            completed.currentNativeBaselinePolicy = "All actual84 states equal the immutable prior resume84 native baseline before and after exact-null-reference patches in one session; no rebaseline permitted. Ten verified completed files retained byte-exact, eighteen patched."; completed.status = "complete";
            string completedPath = Path.Combine(run, "completed-standard-report.json");
            WriteAtomic(completedPath, JsonUtility.ToJson(completed, true)); WriteAtomic(Path.Combine(local, "missing-texture-default-adaptation-report.json"), JsonUtility.ToJson(completed, true));
            report.completedReportPath = completedPath; report.completedReportSha256 = HashFile(completedPath); report.status = "complete";
        } catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); throw; }
        finally { Application.logMessageReceived -= capture; report.completedUtc = DateTime.UtcNow.ToString("o"); persist(); WriteAtomic(Path.Combine(local, "missing-texture-default-atomic-resume-report.json"), JsonUtility.ToJson(report, true)); }
    }
    public static void ResumeAtomicHeadless() { Guard(); int exit = 0; try { ResumePendingReferences(); } catch (Exception error) { Debug.LogError(error); exit = 1; } EditorApplication.Exit(exit); }
}
