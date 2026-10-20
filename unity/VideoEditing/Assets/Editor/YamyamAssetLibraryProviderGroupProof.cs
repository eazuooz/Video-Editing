// Explicit read-only batch proof. This candidate never loads TerrainData or scenes.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;
using FileInfo = YamyamAssetLibraryIO.Info;

public static class YamyamAssetLibraryProviderGroupProof
{
    const string ExpectedProject = "D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string Root = "Assets/ThirdParty/YamyamAssetLibrary";
    const string Kind = "incomplete-provider-demo-group";
    const string OptionalKind = "incomplete-optional-demo-script-group";
    static bool OptionalDemo { get { return Array.IndexOf(Environment.GetCommandLineArgs(), "-yamyamOptionalDemoScriptGroup") >= 0; } }
    static readonly Regex GuidLine = new Regex(@"(?m)^guid:[ \t]*([a-fA-F0-9]{32})[ \t]*\r?$");
    static readonly Regex Hash = new Regex("^[a-f0-9]{64}$");

    [Serializable] public sealed class FileRecord { public string path, sha256; public long bytes; }
    [Serializable] public sealed class Product { public string id, folder, status; public FileRecord[] files; }
    [Serializable] public sealed class Manifest { public string stageRoot, targetAssetRoot; public Product[] products; }
    [Serializable] public sealed class Artifact { public string path, sha256; }
    [Serializable] public sealed class Target
    {
        public string productId, path, sha256, metadataPath, metadataSha256, guid, reason, role;
        public long bytes, metadataBytes;
    }
    [Serializable] public sealed class Plan
    {
        public int schemaVersion;
        public string kind, sourceManifestSha256;
        public Artifact missingEvidence, sourceIncomingGraph, scriptResolutionEvidence;
        public Target[] targets;
    }
    [Serializable] public sealed class ScriptCase { public string originalGuid, originalFileId, guid, fileId, expectedClass; public bool expectedResolved; }
    [Serializable] public sealed class ScriptCases { public int schemaVersion; public ScriptCase[] cases; }
    [Serializable] public sealed class ScriptResult { public string originalGuid, originalFileId, guid, fileId, path, resolvedClass; public bool expectedResolved, actualResolved, matches; }
    [Serializable] public sealed class ReceiptHash { public string productId, sha256; }
    [Serializable] public sealed class TargetProof
    {
        public string productId, path, relativePath, guid, canonicalSha256, actualSha256, sourceArtifactSha256;
        public string metadataPath, metadataSha256, canonicalMetadataSha256, role, reason;
        public long bytes, metadataBytes;
        public int checkedInboundReferences = -1;
        public bool referencedByOtherRootAssets;
    }
    [Serializable] public sealed class Proof
    {
        public int proofVersion = 1, rootAssetsChecked, dependencyClosurePaths;
        public string status, rootPathsSha256, closurePathsSha256, startedUtc, completedUtc;
        public double elapsedSeconds;
        public string method = "AssetDatabase.GetDependencies(all current canonical non-folder root asset paths except exact reviewed group, recursive:true). Excluded targets cannot enter the closure merely by being input roots.";
        public List<TargetProof> excludedTargets = new List<TargetProof>();
    }
    [Serializable] public sealed class Report
    {
        public int schemaVersion = 1, observedUnityWarnings, observedUnityErrors;
        public string kind = Kind, status = "checking", project, runDirectory, startedUtc, completedUtc;
        public string manifestPath, manifestSha256, groupPlanPath, groupPlanSha256, sourceMissingEvidenceSha256, sourceIncomingGraphSha256;
        public bool apply, originalArchivesModified, scenesOpened, terrainDataLoaded, assetsSaved;
        public string scriptResolutionEvidenceSha256;
        public List<ScriptResult> scriptResolutions = new List<ScriptResult>();
        public double elapsedSeconds;
        public List<ReceiptHash> receiptSha256ByProduct = new List<ReceiptHash>();
        public Proof dependencyProof;
        public List<string> blockers = new List<string>();
        public List<string> warnings = new List<string>();
        public List<string> errors = new List<string>();
    }

    static string Project { get { return YamyamAssetLibraryIO.NormalPath(Path.GetDirectoryName(Application.dataPath)); } }
    static string Work { get { return YamyamAssetLibraryIO.NormalPath(Path.Combine(Project, "..")); } }
    static string Absolute(string path) { return Path.Combine(Project, path.Replace('/', Path.DirectorySeparatorChar)); }
    static string Utc() { return DateTime.UtcNow.ToString("o"); }
    static string Hex(byte[] value) { return BitConverter.ToString(value).Replace("-", "").ToLowerInvariant(); }
    static string HashFile(string path) { using (var input = File.OpenRead(path)) using (var hash = SHA256.Create()) return Hex(hash.ComputeHash(input)); }
    static string HashText(string value) { using (var hash = SHA256.Create()) return Hex(hash.ComputeHash(Encoding.UTF8.GetBytes(value))); }
    static bool InRoot(string path) { return path.StartsWith(Root + "/", StringComparison.Ordinal); }

    static void GuardOwnership()
    {
        if (!Application.isBatchMode || !string.Equals(Project.Replace('\\', '/'), ExpectedProject, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Provider-group proof requires the exact isolated batch project.");
    }
    static void NoLinks(string path)
    {
        string full = YamyamAssetLibraryIO.NormalPath(path), boundary = Work;
        if (!string.Equals(full, boundary, StringComparison.OrdinalIgnoreCase) && !full.StartsWith(boundary + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Path escaped the owned isolated workspace: " + path);
        for (string current = full; !string.IsNullOrEmpty(current); current = Path.GetDirectoryName(current)) {
            try { if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("Reparse point refused: " + current); }
            catch (FileNotFoundException) { }
            catch (DirectoryNotFoundException) { }
            if (string.Equals(current, boundary, StringComparison.OrdinalIgnoreCase)) return;
        }
        throw new InvalidOperationException("Owned path boundary was not reached.");
    }
    static string SafeRelative(string value)
    {
        if (string.IsNullOrEmpty(value) || value.Contains("\\") || value.StartsWith("/", StringComparison.Ordinal) || value.Contains(":"))
            throw new InvalidDataException("A canonical forward-slash relative path is required.");
        foreach (string part in value.Split('/')) if (part == "" || part == "." || part == ".." || part.IndexOf('\0') >= 0)
            throw new InvalidDataException("Unsafe canonical relative path: " + value);
        return value;
    }
    // Pure structural checks are exercised by the companion offline Mono fixtures.
    static void ValidatePlan(Plan plan)
    {
        if (plan == null || plan.schemaVersion != 1 || (plan.kind != Kind && plan.kind != OptionalKind) || !Hash.IsMatch(plan.sourceManifestSha256 ?? "") || plan.targets == null)
            throw new InvalidDataException("Unsupported or incomplete reviewed group plan.");
        if (plan.missingEvidence == null || plan.sourceIncomingGraph == null || !Hash.IsMatch(plan.missingEvidence.sha256 ?? "") || !Hash.IsMatch(plan.sourceIncomingGraph.sha256 ?? ""))
            throw new InvalidDataException("Both source-missing and incoming-graph evidence hashes are required.");
        var paths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        int terrains = 0, optionalScenes = 0;
        foreach (Target target in plan.targets) {
            if (target == null || string.IsNullOrEmpty(target.productId) || string.IsNullOrWhiteSpace(target.reason) || target.reason.Length < 8)
                throw new InvalidDataException("Every target requires exact ownership and a substantive reason.");
            SafeRelative(target.path); SafeRelative(target.metadataPath);
            if (!paths.Add(target.path) || !paths.Add(target.metadataPath) || target.metadataPath != target.path + ".meta" || target.path.EndsWith(".meta", StringComparison.OrdinalIgnoreCase)
                || target.bytes < 1 || target.metadataBytes < 1 || !Hash.IsMatch(target.sha256 ?? "") || !Hash.IsMatch(target.metadataSha256 ?? "") || !Regex.IsMatch(target.guid ?? "", "^[a-f0-9]{32}$"))
                throw new InvalidDataException("Duplicate, unsafe or incomplete target pair: " + target.path);
            if (target.role == "incomplete-optional-demo" && plan.kind == OptionalKind) {
                if (!target.path.EndsWith(".unity", StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Optional-demo seeds must be scenes.");
                optionalScenes++;
            }
            else if (target.role == "incomplete-terrain" && plan.kind == Kind) {
                if (!target.path.EndsWith(".asset", StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Incomplete TerrainData must be a native .asset.");
                terrains++;
            }
            else if (target.role != "incoming-demo-consumer" || !(target.path.EndsWith(".unity", StringComparison.OrdinalIgnoreCase) || target.path.EndsWith(".prefab", StringComparison.OrdinalIgnoreCase)))
                throw new InvalidDataException("Only incomplete TerrainData and their exact incoming scene/prefab consumer closure may be excluded.");
        }
        if ((plan.kind == Kind && (terrains != 12 || optionalScenes != 0)) || (plan.kind == OptionalKind && (optionalScenes != 49 || terrains != 0)))
            throw new InvalidDataException("This route requires exactly12 TerrainData or separately reviewed49 optional scenes.");
        if (plan.kind == OptionalKind && (plan.scriptResolutionEvidence == null || !Hash.IsMatch(plan.scriptResolutionEvidence.sha256 ?? "")))
            throw new InvalidDataException("Optional scenes require exact native script-resolution evidence.");
    }
    static void VerifyArtifact(Artifact artifact)
    {
        string path = YamyamAssetLibraryIO.NormalPath(artifact.path); NoLinks(path);
        if (HashFile(path) != artifact.sha256) throw new InvalidDataException("Reviewed evidence hash changed: " + path);
    }
    static void SaveReport(string path, Report report)
    {
        NoLinks(path); Directory.CreateDirectory(Path.GetDirectoryName(path));
        string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        File.WriteAllText(temporary, JsonUtility.ToJson(report, true) + "\n", new UTF8Encoding(false));
        for (int attempt = 0; ; attempt++) {
            try { NoLinks(path); if (File.Exists(path)) File.Replace(temporary, path, null); else File.Move(temporary, path); return; }
            catch (IOException error) { int code = error.HResult & 0xffff; if (attempt >= 4 || !(code == 5 || code == 32 || code == 33 || code == 1175)) throw; }
            catch (UnauthorizedAccessException) { if (attempt >= 4) throw; }
            System.Threading.Thread.Sleep(100 * (attempt + 1));
        }
    }
    static void VerifyTarget(TargetProof proof)
    {
        string path = Absolute(proof.path), metaPath = Absolute(proof.metadataPath); NoLinks(path); NoLinks(metaPath);
        if (new FileInfo(path).Length != proof.bytes || HashFile(path) != proof.actualSha256 || new FileInfo(metaPath).Length != proof.metadataBytes || HashFile(metaPath) != proof.metadataSha256)
            throw new InvalidDataException("Reviewed group asset/metadata changed: " + proof.relativePath);
        Match match = GuidLine.Match(File.ReadAllText(metaPath));
        if (!match.Success || match.Groups[1].Value.ToLowerInvariant() != proof.guid || AssetDatabase.AssetPathToGUID(proof.path).ToLowerInvariant() != proof.guid)
            throw new InvalidDataException("Reviewed group asset GUID changed: " + proof.relativePath);
    }
    static Report Inspect()
    {
        GuardOwnership();
        if (Application.unityVersion != "6000.6.0f1" || EditorApplication.isCompiling || EditorApplication.isUpdating) throw new InvalidOperationException("Expected idle Unity6000.6.0f1.");
        NoLinks(Project);
        string localWork = Path.Combine(Project, "Library/YamyamAssetLibrary");
        string run = Path.Combine(localWork, OptionalDemo ? "optional-demo-group-proof" : "provider-group-proof", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N"));
        NoLinks(run); Directory.CreateDirectory(run);
        var report = new Report { kind = OptionalDemo ? OptionalKind : Kind, project = Project, runDirectory = run, startedUtc = Utc(), manifestPath = Path.Combine(Work, "staging-manifest.json"), groupPlanPath = Path.Combine(Work, OptionalDemo ? "incomplete-optional-demo-script-group-plan.json" : "incomplete-provider-demo-group-plan.json") };
        string reportPath = Path.Combine(run, "report.json"); var watch = Stopwatch.StartNew();
        Application.LogCallback capture = (message, stack, type) => {
            if (type == LogType.Warning) { report.observedUnityWarnings++; if (report.warnings.Count < 128) report.warnings.Add(message); }
            else if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; if (report.errors.Count < 128) report.errors.Add("Unity: " + message); }
        };
        Application.logMessageReceived += capture;
        try {
            NoLinks(report.manifestPath); NoLinks(report.groupPlanPath);
            report.manifestSha256 = HashFile(report.manifestPath); report.groupPlanSha256 = HashFile(report.groupPlanPath);
            Manifest manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(report.manifestPath));
            Plan plan = JsonUtility.FromJson<Plan>(File.ReadAllText(report.groupPlanPath)); ValidatePlan(plan);
            if (plan.kind != report.kind) throw new InvalidDataException("Explicit command route and plan kind differ.");
            if (OptionalDemo) VerifyScriptResolutions(plan.scriptResolutionEvidence, report);
            if (plan.sourceManifestSha256 != report.manifestSha256 || manifest.products == null || manifest.products.Length != 84 || manifest.targetAssetRoot != Root
                || !string.Equals(YamyamAssetLibraryIO.NormalPath(manifest.stageRoot), YamyamAssetLibraryIO.NormalPath(Absolute(Root)), StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("Group plan or canonical root/product coverage is stale.");
            VerifyArtifact(plan.missingEvidence); VerifyArtifact(plan.sourceIncomingGraph);
            report.sourceMissingEvidenceSha256 = plan.missingEvidence.sha256; report.sourceIncomingGraphSha256 = plan.sourceIncomingGraph.sha256;
            var products = manifest.products.ToDictionary(item => item.id, StringComparer.Ordinal);
            var proof = new Proof { startedUtc = Utc() }; report.dependencyProof = proof; var proofWatch = Stopwatch.StartNew();
            foreach (var group in plan.targets.GroupBy(target => target.productId).OrderBy(group => group.Key, StringComparer.Ordinal)) {
                Product product;
                if (!products.TryGetValue(group.Key, out product) || product.status != "complete" || product.files == null) throw new InvalidDataException("Reviewed group owner lacks a complete canonical receipt.");
                string receiptPath = Path.Combine(Work, "receipts", group.Key + ".json"); NoLinks(receiptPath);
                Product receipt = JsonUtility.FromJson<Product>(File.ReadAllText(receiptPath));
                if (receipt.id != product.id || receipt.folder != product.folder || receipt.status != product.status || receipt.files == null || receipt.files.Length != product.files.Length)
                    throw new InvalidDataException("Reviewed group receipt ownership or file count changed.");
                var records = product.files.ToDictionary(item => item.path, StringComparer.Ordinal);
                var receiptRecords = receipt.files.ToDictionary(item => item.path, StringComparer.Ordinal);
                foreach (var record in records.Values) {
                    FileRecord other;
                    if (!receiptRecords.TryGetValue(record.path, out other) || other.sha256 != record.sha256 || other.bytes != record.bytes) throw new InvalidDataException("Canonical receipt file records differ from manifest.");
                }
                report.receiptSha256ByProduct.Add(new ReceiptHash { productId = group.Key, sha256 = HashFile(receiptPath) });
                foreach (Target target in group) {
                    FileRecord body, meta;
                    if (!target.path.StartsWith(product.folder + "/", StringComparison.Ordinal) || !records.TryGetValue(target.path, out body) || !records.TryGetValue(target.metadataPath, out meta)
                        || body.sha256 != target.sha256 || body.bytes != target.bytes || meta.sha256 != target.metadataSha256 || meta.bytes != target.metadataBytes)
                        throw new InvalidDataException("Reviewed target pair differs from canonical ownership/bytes: " + target.path);
                    var item = new TargetProof { productId = target.productId, relativePath = target.path, path = Root + "/" + target.path, metadataPath = Root + "/" + target.metadataPath,
                        bytes = target.bytes, metadataBytes = target.metadataBytes, guid = target.guid, role = target.role, reason = target.reason,
                        canonicalSha256 = target.sha256, actualSha256 = target.sha256, sourceArtifactSha256 = target.sha256, metadataSha256 = target.metadataSha256, canonicalMetadataSha256 = target.metadataSha256 };
                    VerifyTarget(item); proof.excludedTargets.Add(item);
                }
            }
            var excluded = new HashSet<string>(proof.excludedTargets.Select(target => target.path), StringComparer.Ordinal);
            string[] canonicalRoots = manifest.products.SelectMany(product => product.files).Where(record => !record.path.EndsWith(".meta", StringComparison.OrdinalIgnoreCase)).Select(record => Root + "/" + record.path).Where(path => !excluded.Contains(path)).OrderBy(path => path, StringComparer.Ordinal).ToArray();
            string[] roots = AssetDatabase.GetAllAssetPaths().Where(path => InRoot(path) && !excluded.Contains(path) && !AssetDatabase.IsValidFolder(path) && !path.EndsWith(".meta", StringComparison.OrdinalIgnoreCase)).Distinct().OrderBy(path => path, StringComparer.Ordinal).ToArray();
            if (!canonicalRoots.SequenceEqual(roots, StringComparer.Ordinal)) throw new InvalidDataException("Actual Unity non-folder root path set differs from current canonical files minus exact group.");
            foreach (string path in roots) NoLinks(Absolute(path));
            proof.rootAssetsChecked = roots.Length; proof.rootPathsSha256 = HashText(string.Join("\n", roots));
            SaveReport(reportPath, report);
            string[] closure = AssetDatabase.GetDependencies(roots, true).Distinct().OrderBy(path => path, StringComparer.Ordinal).ToArray();
            proof.dependencyClosurePaths = closure.Length; proof.closurePathsSha256 = HashText(string.Join("\n", closure));
            var closureSet = new HashSet<string>(closure, StringComparer.Ordinal);
            foreach (TargetProof target in proof.excludedTargets) {
                target.referencedByOtherRootAssets = closureSet.Contains(target.path);
                if (target.referencedByOtherRootAssets) report.blockers.Add("Group asset is referenced from outside the group: " + target.path);
                else target.checkedInboundReferences = 0;
                VerifyTarget(target);
            }
            proof.status = report.blockers.Count == 0 ? "unreferenced-by-other-root-assets" : "referenced-by-other-root-assets";
            proof.completedUtc = Utc(); proof.elapsedSeconds = proofWatch.Elapsed.TotalSeconds;
            foreach (ReceiptHash receipt in report.receiptSha256ByProduct) if (HashFile(Path.Combine(Work, "receipts", receipt.productId + ".json")) != receipt.sha256) throw new IOException("Canonical group receipt changed during proof.");
            VerifyArtifact(plan.missingEvidence); VerifyArtifact(plan.sourceIncomingGraph);
            if (HashFile(report.manifestPath) != report.manifestSha256 || HashFile(report.groupPlanPath) != report.groupPlanSha256) throw new IOException("Canonical manifest or reviewed group plan changed during proof.");
            if (report.observedUnityErrors != 0 || report.blockers.Count != 0) throw new InvalidDataException("Group dependency proof contains native errors or inbound references.");
            report.status = "dependency-proof-complete";
        }
        catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); throw; }
        finally {
            Application.logMessageReceived -= capture;
            report.completedUtc = Utc(); report.elapsedSeconds = watch.Elapsed.TotalSeconds;
            SaveReport(reportPath, report); SaveReport(Path.Combine(localWork, OptionalDemo ? "optional-demo-group-proof-report.json" : "provider-group-proof-report.json"), report);
        }
        return report;
    }
    static void VerifyScriptResolutions(Artifact artifact, Report report)
    {
        VerifyArtifact(artifact); report.scriptResolutionEvidenceSha256 = artifact.sha256;
        ScriptCases input = JsonUtility.FromJson<ScriptCases>(File.ReadAllText(artifact.path));
        if (input.schemaVersion != 1 || input.cases == null || input.cases.Length != 44 || input.cases.Count(c => c.expectedResolved) != 30)
            throw new InvalidDataException("Expected exact44 script identities including30 restored/current runtime classes.");
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (ScriptCase item in input.cases) {
            long expectedId;
            if (!Regex.IsMatch(item.guid ?? "", "^[a-f0-9]{32}$") || !long.TryParse(item.fileId, out expectedId) || !seen.Add(item.originalGuid + ":" + item.originalFileId)) throw new InvalidDataException("Invalid/duplicate script identity.");
            var result = new ScriptResult { originalGuid = item.originalGuid, originalFileId = item.originalFileId, guid = item.guid, fileId = item.fileId, expectedResolved = item.expectedResolved, path = AssetDatabase.GUIDToAssetPath(item.guid) };
            MonoScript found = null;
            if (!string.IsNullOrEmpty(result.path)) {
                foreach (UnityEngine.Object asset in AssetDatabase.LoadAllAssetsAtPath(result.path)) {
                    MonoScript script = asset as MonoScript; string guid; long id;
                    if (script != null && AssetDatabase.TryGetGUIDAndLocalFileIdentifier(script, out guid, out id) && guid.Equals(item.guid, StringComparison.OrdinalIgnoreCase) && id == expectedId) { found = script; break; }
                }
            }
            Type type = found == null ? null : found.GetClass(); result.actualResolved = type != null; result.resolvedClass = type == null ? "" : type.FullName;
            result.matches = result.actualResolved == item.expectedResolved && (!item.expectedResolved || result.resolvedClass == item.expectedClass);
            report.scriptResolutions.Add(result);
            if (!result.matches) throw new InvalidDataException("Native MonoScript resolution differs; do not quarantine a newly restored class: " + item.originalGuid + ":" + item.originalFileId + " -> " + result.resolvedClass);
        }
        VerifyArtifact(artifact);
    }
    public static void RunHeadless()
    {
        GuardOwnership(); int exitCode = 0;
        try { Inspect(); }
        catch (Exception error) { UnityEngine.Debug.LogError(error); exitCode = 1; }
        EditorApplication.Exit(exitCode);
    }
}
