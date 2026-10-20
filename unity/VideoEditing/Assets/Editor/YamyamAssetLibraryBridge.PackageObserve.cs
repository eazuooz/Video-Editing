using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using PackageInfo = UnityEditor.PackageManager.PackageInfo;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;

public static partial class YamyamAssetLibraryBridge
{
    [Serializable] public sealed class PackageObserveInput {
        public int schemaVersion;
        public string nonce, expectedUnityVersion, manifestSha256, actualLockSha256, priorFailedReportPath, priorFailedReportSha256, compiledAckNotBeforeUtc;
    }
    [Serializable] public sealed class ObservedPackage { public string name, version, source, packageId, type, assetPath, resolvedPath; }
    [Serializable] public sealed class ObservedMismatch { public string name, expected, actual; public int matchingRows; }
    [Serializable] public sealed class ObservedDefine { public int buildTargetGroup; public string groupName, namedTarget, defines; }
    [Serializable] public sealed class ObservedScene { public string path; public bool loaded, active; }
    [Serializable] public sealed class PackageObserveReport {
        public int schemaVersion = 1;
        public string status = "observing", nonce, startedUtc, completedUtc, inputSha256, manifestSha256, actualLockSha256, priorFailedReportPath, priorFailedReportSha256, compiledAckSha256, runDirectory, error;
        public string scope = "Read-only installed-package and online/offline List metadata observation. No Resolve/Add/Remove/settings mutation/asset save/scene opening. List metadata disagreement is reported separately and never relabeled as a pass.";
        public bool registeredBaselineAndPostprocessVersionsMatch, lockAndManifestUnchanged, nativeProfileTypeLoaded, offlineRequestIssued, offlineRequestCompleted, onlineRequestIssued, onlineRequestCompleted;
        public List<ObservedPackage> registeredBefore = new List<ObservedPackage>(), registeredAfter = new List<ObservedPackage>(), offlineRows = new List<ObservedPackage>(), onlineRows = new List<ObservedPackage>();
        public List<ObservedMismatch> registeredMismatches = new List<ObservedMismatch>(), offlineMismatches = new List<ObservedMismatch>(), onlineMismatches = new List<ObservedMismatch>();
        public List<ObservedDefine> nativeDefines = new List<ObservedDefine>(); public List<ObservedScene> sceneSetup = new List<ObservedScene>();
        public string activeScenePath; public bool activeSceneDirty;
    }
    static PackageObserveInput observeInput;
    static PackageObserveReport observeReport;
    static ResolveInput observeBaseline;
    static ListRequest observeList;
    static List<ObservedPackage> ObserveRows(IEnumerable<PackageInfo> packages) { return packages.OrderBy(value => value.name, StringComparer.Ordinal).Select(value => new ObservedPackage { name = value.name, version = value.version, source = value.source.ToString(), packageId = value.packageId, type = value.type, assetPath = value.assetPath, resolvedPath = value.resolvedPath }).ToList(); }
    static List<ObservedMismatch> ObserveMismatches(List<ObservedPackage> rows)
    {
        var expected = observeBaseline.baselinePackages.Concat(new[] { new ResolveVersion { name = "com.unity.postprocessing", version = "3.5.4" } });
        var result = new List<ObservedMismatch>();
        foreach (var item in expected) {
            var matching = rows.Where(value => value.name == item.name).ToArray();
            if (matching.Length != 1 || matching[0].version != item.version)
                result.Add(new ObservedMismatch { name = item.name, expected = item.version, actual = matching.Length == 0 ? "<missing>" : string.Join(" | ", matching.Select(value => value.version + " [" + value.source + "]").ToArray()), matchingRows = matching.Length });
        }
        return result;
    }
    static void CaptureNativeDefinesAndScenes()
    {
        observeReport.nativeDefines.Clear();
        foreach (BuildTargetGroup group in Enum.GetValues(typeof(BuildTargetGroup))) {
            if (group == BuildTargetGroup.Unknown || typeof(BuildTargetGroup).GetField(group.ToString()).GetCustomAttributes(typeof(ObsoleteAttribute), false).Length > 0) continue;
            var named = NamedBuildTarget.FromBuildTargetGroup(group);
            observeReport.nativeDefines.Add(new ObservedDefine { buildTargetGroup = (int)group, groupName = group.ToString(), namedTarget = named.TargetName, defines = PlayerSettings.GetScriptingDefineSymbols(named) });
        }
        observeReport.sceneSetup = EditorSceneManager.GetSceneManagerSetup().Select(value => new ObservedScene { path = value.path, loaded = value.isLoaded, active = value.isActive }).ToList();
        var active = SceneManager.GetActiveScene(); observeReport.activeScenePath = active.path; observeReport.activeSceneDirty = active.isDirty;
    }
    static void PersistObserveReport()
    {
        WriteJson(Path.Combine(observeReport.runDirectory, "report.json"), observeReport);
        WriteJson(Path.Combine(Work, "package-observe-report.json"), observeReport);
    }
    static void VerifyObserveContext()
    {
        string inputPath = Path.Combine(Work, "package-observe-input.json"); ScopedNoLinks(inputPath, Work);
        if (ResolveHash(inputPath) != job.packageObserveInputSha256) throw new InvalidDataException("Package observation input changed.");
        string manifestPath = Path.Combine(Project, "Packages/manifest.json"), lockPath = Path.Combine(Project, "Packages/packages-lock.json"); ScopedNoLinks(manifestPath, Project); ScopedNoLinks(lockPath, Project);
        if (ResolveHash(manifestPath) != observeInput.manifestSha256 || ResolveHash(lockPath) != observeInput.actualLockSha256) throw new InvalidDataException("Actual package manifest/lock changed during read-only observation.");
        ScopedNoLinks(observeInput.priorFailedReportPath, Work);
        if (ResolveHash(observeInput.priorFailedReportPath) != observeInput.priorFailedReportSha256) throw new InvalidDataException("Original failed Resolve evidence changed.");
        string ackPath = Path.Combine(Work, "compiled.json"); ScopedNoLinks(ackPath, Work); var ack = JsonUtility.FromJson<Status>(File.ReadAllText(ackPath));
        if (ack == null || ack.status != "compiled" || ack.unityVersion != "6000.6.0f1" || !string.IsNullOrEmpty(ack.error) || ack.compiling || ack.updating || ack.playing ||
            ack.compiledBridgeSourceSha256 != ResolveHash(Path.Combine(Project, "Assets/Editor/YamyamAssetLibraryBridge.cs")) || string.IsNullOrEmpty(ack.compiledAssemblyMvid) ||
            DateTime.Parse(ack.updatedUtc, null, System.Globalization.DateTimeStyles.RoundtripKind).ToUniversalTime() < DateTime.Parse(observeInput.compiledAckNotBeforeUtc, null, System.Globalization.DateTimeStyles.RoundtripKind).ToUniversalTime())
            throw new InvalidDataException("Fresh exact native compiled acknowledgement required for package observation.");
        observeReport.compiledAckSha256 = ResolveHash(ackPath);
    }
    static bool PollPackageObserve()
    {
        if (job == null && File.Exists(StatePath)) job = JsonUtility.FromJson<Job>(File.ReadAllText(StatePath));
        if (job == null || job.command != "observePackages" || job.phase != "observing-packages") return false;
        if (observeReport != null && observeReport.nonce != job.nonce) { observeReport = null; observeInput = null; observeBaseline = null; observeList = null; }
        try {
            if (observeReport == null) {
                string inputPath = Path.Combine(Work, "package-observe-input.json"); ScopedNoLinks(inputPath, Work);
                if (!Regex.IsMatch(job.packageObserveInputSha256 ?? "", "^[a-f0-9]{64}$") || ResolveHash(inputPath) != job.packageObserveInputSha256) throw new InvalidDataException("Package observation input SHA differs.");
                observeInput = JsonUtility.FromJson<PackageObserveInput>(File.ReadAllText(inputPath)); DateTime lower;
                if (observeInput == null || observeInput.schemaVersion != 1 || observeInput.nonce != job.nonce || observeInput.expectedUnityVersion != "6000.6.0f1" || Application.unityVersion != "6000.6.0f1" ||
                    !Regex.IsMatch(observeInput.manifestSha256 ?? "", "^[a-f0-9]{64}$") || !Regex.IsMatch(observeInput.actualLockSha256 ?? "", "^[a-f0-9]{64}$") || !Regex.IsMatch(observeInput.priorFailedReportSha256 ?? "", "^[a-f0-9]{64}$") ||
                    !DateTime.TryParse(observeInput.compiledAckNotBeforeUtc, null, System.Globalization.DateTimeStyles.RoundtripKind, out lower) || lower.ToUniversalTime() > DateTime.UtcNow)
                    throw new InvalidDataException("Exact current package graph/compile/failed-source observation scope required.");
                ScopedNoLinks(observeInput.priorFailedReportPath, Work);
                if (ResolveHash(observeInput.priorFailedReportPath) != observeInput.priorFailedReportSha256) throw new InvalidDataException("Source failed report hash differs.");
                var failed = JsonUtility.FromJson<ResolveReport>(File.ReadAllText(observeInput.priorFailedReportPath));
                string originalInput = Path.Combine(Work, "package-resolve-input.json"); ScopedNoLinks(originalInput, Work);
                if (failed == null || failed.status != "failed" || !failed.resolveCallIntentRecorded || !failed.resolveCallReturned || !failed.listRequestCompleted || failed.baselineVersionsVerifiedBefore != 71 || !failed.nativePostProcessProfileTypeLoaded || ResolveHash(originalInput) != failed.inputSha256)
                    throw new InvalidDataException("Only the completed actual Resolve followed by failed offline-list validation can be observed.");
                observeBaseline = JsonUtility.FromJson<ResolveInput>(File.ReadAllText(originalInput));
                if (observeBaseline == null || observeBaseline.baselinePackages == null || observeBaseline.baselinePackages.Length != 71 || observeBaseline.baselinePackages.Select(value => value.name).Distinct().Count() != 71) throw new InvalidDataException("Preserved71 baseline rows missing.");
                string token; using (var hash = SHA256.Create()) token = Hex(hash.ComputeHash(Encoding.UTF8.GetBytes(job.nonce)));
                string run = Path.Combine(Work, "package-observe", token); ScopedNoLinks(run, Work);
                observeReport = new PackageObserveReport { nonce = job.nonce, startedUtc = Utc(), inputSha256 = job.packageObserveInputSha256, manifestSha256 = observeInput.manifestSha256, actualLockSha256 = observeInput.actualLockSha256, priorFailedReportPath = observeInput.priorFailedReportPath, priorFailedReportSha256 = observeInput.priorFailedReportSha256, runDirectory = run };
                Directory.CreateDirectory(run); VerifyObserveContext(); CaptureNativeDefinesAndScenes();
                observeReport.registeredBefore = ObserveRows(PackageInfo.GetAllRegisteredPackages()); observeReport.registeredMismatches = ObserveMismatches(observeReport.registeredBefore);
                observeReport.nativeProfileTypeLoaded = AppDomain.CurrentDomain.GetAssemblies().Any(value => value.GetType("UnityEngine.Rendering.PostProcessing.PostProcessProfile", false) != null);
                File.Copy(inputPath, Path.Combine(run, "input.json"), false); PersistObserveReport();
                if (observeReport.registeredMismatches.Count != 0 || !observeReport.nativeProfileTypeLoaded) throw new InvalidDataException("Actual registered package graph/type differs; see full registered rows and expected/actual mismatches.");
            }
            if (DateTime.UtcNow - DateTime.Parse(observeReport.startedUtc, null, System.Globalization.DateTimeStyles.RoundtripKind).ToUniversalTime() > TimeSpan.FromSeconds(180)) throw new TimeoutException("180-second read-only List observation expired; no native service was cancelled or killed.");
            VerifyObserveContext();
            if (EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode) return true;
            if (!observeReport.offlineRequestIssued) { observeReport.offlineRequestIssued = true; PersistObserveReport(); observeList = Client.List(true, true); return true; }
            if (observeList == null) throw new InvalidOperationException("Actual ListRequest handle lost after domain reload; completion cannot be fabricated.");
            if (!observeList.IsCompleted) return true;
            if (observeList.Status != StatusCode.Success) throw new InvalidOperationException("Native read-only ListRequest failed: " + (observeList.Error != null ? observeList.Error.message : observeList.Status.ToString()));
            if (!observeReport.offlineRequestCompleted) {
                observeReport.offlineRows = ObserveRows(observeList.Result); observeReport.offlineMismatches = ObserveMismatches(observeReport.offlineRows); observeReport.offlineRequestCompleted = true; PersistObserveReport();
                if (observeReport.offlineMismatches.Count != 0) { observeReport.onlineRequestIssued = true; PersistObserveReport(); observeList = Client.List(false, true); return true; }
            } else if (observeReport.onlineRequestIssued && !observeReport.onlineRequestCompleted) {
                observeReport.onlineRows = ObserveRows(observeList.Result); observeReport.onlineMismatches = ObserveMismatches(observeReport.onlineRows); observeReport.onlineRequestCompleted = true; PersistObserveReport();
            }
            observeReport.registeredAfter = ObserveRows(PackageInfo.GetAllRegisteredPackages()); observeReport.registeredMismatches = ObserveMismatches(observeReport.registeredAfter); CaptureNativeDefinesAndScenes();
            VerifyObserveContext(); observeReport.lockAndManifestUnchanged = true; observeReport.registeredBaselineAndPostprocessVersionsMatch = observeReport.registeredMismatches.Count == 0;
            if (!observeReport.registeredBaselineAndPostprocessVersionsMatch) throw new InvalidDataException("Actual registered graph changed during observation; expected/actual rows preserved.");
            observeReport.status = observeReport.onlineRequestIssued && observeReport.onlineMismatches.Count != 0 ? "observed-with-list-graph-disagreement" : "complete";
            observeReport.completedUtc = Utc(); PersistObserveReport(); job.phase = "complete"; SaveJob(); WriteStatus(observeReport.status); return true;
        } catch (Exception error) {
            if (observeReport != null) { observeReport.status = "failed"; observeReport.error = Unwrap(error); observeReport.completedUtc = Utc(); PersistObserveReport(); }
            job.phase = "failed"; job.error = Unwrap(error); SaveJob(); WriteStatus("package-observation-failed", job.error); Debug.LogException(error); return true;
        }
    }
}
