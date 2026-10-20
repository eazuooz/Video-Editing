using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;
using PackageInfo = UnityEditor.PackageManager.PackageInfo;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;

public static partial class YamyamAssetLibraryBridge
{
    [Serializable] public sealed class ResolveVersion { public string name, version; }
    [Serializable] public sealed class ResolveInput {
        public int schemaVersion;
        public string nonce, expectedUnityVersion, manifestSha256, baselineLockSha256, compiledAckNotBeforeUtc;
        public ResolveVersion[] baselinePackages;
    }
    [Serializable] public sealed class ResolveReport {
        public int schemaVersion = 1, baselineVersionsVerifiedBefore, baselineVersionsVerifiedAfter, nativePackageCount;
        public string status = "checking", nonce, startedUtc, completedUtc, inputSha256, manifestSha256, baselineLockSha256, actualLockSha256, runDirectory, packagePath, compiledAckSha256;
        public bool resolveCallIntentRecorded, resolveCallReturned, listRequestIssued, listRequestCompleted, baselineVersionsUnchanged, nativePostProcessProfileTypeLoaded;
        public string api = "Client.Resolve returns void; completion is established by actual registered3.5.4, fresh native compilation ACK and a successful real Client.List(true,true) Request.", error;
        public List<ResolveVersion> nativePackages = new List<ResolveVersion>();
    }
    static ResolveInput resolveInput;
    static ResolveReport resolveReport;
    static ListRequest resolveList;
    static string ResolveHash(string path) { using (var stream = File.OpenRead(path)) using (var hash = SHA256.Create()) return Hex(hash.ComputeHash(stream)); }
    static void PersistResolveReport()
    {
        WriteJson(Path.Combine(resolveReport.runDirectory, "report.json"), resolveReport);
        WriteJson(Path.Combine(Work, "package-resolve-report.json"), resolveReport);
    }
    static void VerifyResolveContext()
    {
        string path = Path.Combine(Work, "package-resolve-input.json"); ScopedNoLinks(path, Work);
        if (!Regex.IsMatch(job.packageResolveInputSha256 ?? "", "^[a-f0-9]{64}$") || ResolveHash(path) != job.packageResolveInputSha256) throw new InvalidDataException("Package resolution input changed after request/job pinning.");
        string manifestPath = Path.Combine(Project, "Packages/manifest.json"); ScopedNoLinks(manifestPath, Project);
        if (ResolveHash(manifestPath) != resolveInput.manifestSha256 || Regex.Matches(File.ReadAllText(manifestPath), @"""com\.unity\.postprocessing""[ \t]*:[ \t]*""3\.5\.4""").Count != 1)
            throw new InvalidDataException("Exact approved manifest with postprocessing3.5.4 is required.");
        string baselinePath = Path.Combine(Work, "headless-project/Packages/packages-lock.json"); ScopedNoLinks(baselinePath, Work);
        if (ResolveHash(baselinePath) != resolveInput.baselineLockSha256) throw new InvalidDataException("Preserved pre-addition71-package lock changed.");
        string baseline = File.ReadAllText(baselinePath);
        foreach (var package in resolveInput.baselinePackages)
            if (Regex.Matches(baseline, @"(?m)^    """ + Regex.Escape(package.name) + @"""[ \t]*:[ \t]*\{\r?\n[ \t]*""version""[ \t]*:[ \t]*""" + Regex.Escape(package.version) + @"""").Count != 1)
                throw new InvalidDataException("Baseline input name/version differs from its exact preserved lock.");
    }
    static void VerifyResolveVersions(IEnumerable<PackageInfo> packages)
    {
        var rows = packages.ToDictionary(value => value.name, StringComparer.Ordinal);
        foreach (var baseline in resolveInput.baselinePackages) {
            PackageInfo actual;
            if (!rows.TryGetValue(baseline.name, out actual) || actual.version != baseline.version) throw new InvalidDataException("Native Package Manager baseline version differs: " + baseline.name + "; expected=" + baseline.version + "; actual=" + (actual == null ? "<missing>" : actual.version));
        }
    }
    static bool PollPackageResolve()
    {
        if (job == null && File.Exists(StatePath)) job = JsonUtility.FromJson<Job>(File.ReadAllText(StatePath));
        if (job == null || job.command != "resolvePackages" || job.phase != "resolving-packages") return false;
        if (resolveReport != null && resolveReport.nonce != job.nonce) { resolveReport = null; resolveInput = null; resolveList = null; }
        try {
            if (resolveReport == null) {
                string path = Path.Combine(Work, "package-resolve-input.json"); ScopedNoLinks(path, Work);
                if (!Regex.IsMatch(job.packageResolveInputSha256 ?? "", "^[a-f0-9]{64}$") || ResolveHash(path) != job.packageResolveInputSha256) throw new InvalidDataException("Package resolution input SHA differs.");
                resolveInput = JsonUtility.FromJson<ResolveInput>(File.ReadAllText(path));
                DateTime compiledLowerBound;
                if (resolveInput == null || resolveInput.schemaVersion != 1 || resolveInput.nonce != job.nonce || resolveInput.expectedUnityVersion != "6000.6.0f1" || Application.unityVersion != "6000.6.0f1" ||
                    !Regex.IsMatch(resolveInput.manifestSha256 ?? "", "^[a-f0-9]{64}$") || !Regex.IsMatch(resolveInput.baselineLockSha256 ?? "", "^[a-f0-9]{64}$") ||
                    !DateTime.TryParse(resolveInput.compiledAckNotBeforeUtc, null, System.Globalization.DateTimeStyles.RoundtripKind, out compiledLowerBound) || compiledLowerBound.ToUniversalTime() > DateTime.UtcNow ||
                    resolveInput.baselinePackages == null || resolveInput.baselinePackages.Length != 71 || resolveInput.baselinePackages.Any(value => value == null || string.IsNullOrEmpty(value.name) || string.IsNullOrEmpty(value.version)) ||
                    resolveInput.baselinePackages.Select(value => value.name).Distinct(StringComparer.Ordinal).Count() != 71 || resolveInput.baselinePackages.Any(value => value.name == "com.unity.postprocessing"))
                    throw new InvalidDataException("Exact71 baseline rows plus approved3.5.4 input required.");
                string token; using (var hash = SHA256.Create()) token = Hex(hash.ComputeHash(Encoding.UTF8.GetBytes(job.nonce)));
                string run = Path.Combine(Work, "package-resolve", token); ScopedNoLinks(run, Work);
                string prior = Path.Combine(run, "report.json");
                if (File.Exists(prior)) {
                    resolveReport = JsonUtility.FromJson<ResolveReport>(File.ReadAllText(prior));
                    if (resolveReport == null || resolveReport.nonce != job.nonce || resolveReport.inputSha256 != job.packageResolveInputSha256 || resolveReport.runDirectory != run || resolveReport.completedUtc != null && resolveReport.completedUtc.Length > 0)
                        throw new InvalidDataException("Resolution resume report is terminal or differs.");
                } else {
                    resolveReport = new ResolveReport { nonce = job.nonce, startedUtc = Utc(), inputSha256 = job.packageResolveInputSha256, manifestSha256 = resolveInput.manifestSha256, baselineLockSha256 = resolveInput.baselineLockSha256, runDirectory = run };
                    VerifyResolveContext(); VerifyResolveVersions(PackageInfo.GetAllRegisteredPackages()); resolveReport.baselineVersionsVerifiedBefore = 71;
                    Directory.CreateDirectory(run); File.Copy(path, Path.Combine(run, "input.json"), false); PersistResolveReport();
                }
            }
            VerifyResolveContext();
            if (DateTime.UtcNow - DateTime.Parse(resolveReport.startedUtc, null, System.Globalization.DateTimeStyles.RoundtripKind).ToUniversalTime() > TimeSpan.FromSeconds(180))
                throw new TimeoutException("180-second bounded Package Manager observation expired; the native service is not cancelled or killed.");
            if (!resolveReport.resolveCallIntentRecorded) {
                resolveReport.resolveCallIntentRecorded = true; resolveReport.status = "resolve-call-intent-recorded"; PersistResolveReport();
                Client.Resolve(); resolveReport.resolveCallReturned = true; resolveReport.status = "waiting-for-native-registration-and-compile"; PersistResolveReport(); return true;
            }
            var registered = PackageInfo.GetAllRegisteredPackages(); var current = registered.SingleOrDefault(value => value.name == "com.unity.postprocessing");
            if (current == null) { WriteStatus("waiting-for-package-registration"); return true; }
            if (current.version != "3.5.4" || current.source != PackageSource.Registry) throw new InvalidDataException("Native package source/version differs from official registry3.5.4.");
            VerifyResolveVersions(registered);
            if (EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode) return true;
            resolveReport.nativePostProcessProfileTypeLoaded = AppDomain.CurrentDomain.GetAssemblies().Any(value => value.GetType("UnityEngine.Rendering.PostProcessing.PostProcessProfile", false) != null);
            string ackPath = Path.Combine(Work, "compiled.json"); ScopedNoLinks(ackPath, Work); var ack = JsonUtility.FromJson<Status>(File.ReadAllText(ackPath));
            if (!resolveReport.nativePostProcessProfileTypeLoaded || ack == null || ack.status != "compiled" || ack.unityVersion != "6000.6.0f1" || !string.IsNullOrEmpty(ack.error) || ack.compiling || ack.updating || ack.playing ||
                ack.compiledBridgeSourceSha256 != ResolveHash(Path.Combine(Project, "Assets/Editor/YamyamAssetLibraryBridge.cs")) || string.IsNullOrEmpty(ack.compiledAssemblyMvid) ||
                DateTime.Parse(ack.updatedUtc, null, System.Globalization.DateTimeStyles.RoundtripKind).ToUniversalTime() < DateTime.Parse(resolveInput.compiledAckNotBeforeUtc, null, System.Globalization.DateTimeStyles.RoundtripKind).ToUniversalTime()) return true;
            resolveReport.compiledAckSha256 = ResolveHash(ackPath);
            if (!resolveReport.listRequestIssued) { resolveReport.listRequestIssued = true; PersistResolveReport(); resolveList = Client.List(true, true); return true; }
            if (resolveList == null) throw new InvalidOperationException("The actual ListRequest handle was lost after a domain reload; do not fabricate completion or rerun Resolve.");
            if (!resolveList.IsCompleted) return true;
            resolveReport.listRequestCompleted = true;
            if (resolveList.Status != StatusCode.Success) throw new InvalidOperationException("Native Package Manager ListRequest failed: " + (resolveList.Error != null ? resolveList.Error.message : resolveList.Status.ToString()));
            resolveReport.nativePackages = resolveList.Result.OrderBy(value => value.name, StringComparer.Ordinal).Select(value => new ResolveVersion { name = value.name, version = value.version }).ToList();
            resolveReport.nativePackageCount = resolveReport.nativePackages.Count; PersistResolveReport();
            VerifyResolveVersions(resolveList.Result);
            var resolved = resolveList.Result.SingleOrDefault(value => value.name == "com.unity.postprocessing");
            if (resolved == null || resolved.version != "3.5.4" || resolved.source != PackageSource.Registry) throw new InvalidDataException("Native ListRequest does not confirm official3.5.4.");
            string lockPath = Path.Combine(Project, "Packages/packages-lock.json"); ScopedNoLinks(lockPath, Project);
            if (ResolveHash(lockPath) == resolveInput.baselineLockSha256 || Regex.Matches(File.ReadAllText(lockPath), @"(?m)^    ""com\.unity\.postprocessing""[ \t]*:[ \t]*\{\r?\n[ \t]*""version""[ \t]*:[ \t]*""3\.5\.4""").Count != 1)
                throw new InvalidDataException("Actual native lock has not recorded3.5.4; it is never written by this helper.");
            resolveReport.packagePath = resolved.resolvedPath; resolveReport.actualLockSha256 = ResolveHash(lockPath); resolveReport.nativePackageCount = resolveList.Result.Count();
            resolveReport.nativePackages = resolveList.Result.OrderBy(value => value.name, StringComparer.Ordinal).Select(value => new ResolveVersion { name = value.name, version = value.version }).ToList();
            resolveReport.baselineVersionsVerifiedAfter = 71; resolveReport.baselineVersionsUnchanged = true; resolveReport.status = "complete"; resolveReport.completedUtc = Utc(); PersistResolveReport();
            job.phase = "complete"; SaveJob(); WriteStatus("package-resolution-complete"); return true;
        } catch (Exception error) {
            if (resolveReport != null) { resolveReport.status = "failed"; resolveReport.error = Unwrap(error); resolveReport.completedUtc = Utc(); PersistResolveReport(); }
            job.phase = "failed"; job.error = Unwrap(error); SaveJob(); WriteStatus("package-resolution-failed", job.error); Debug.LogException(error); return true;
        }
    }
}
