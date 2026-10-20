using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using Object = UnityEngine.Object;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;
using FileInfo = YamyamAssetLibraryIO.Info;
using FileStream = YamyamAssetLibraryIO.Stream;

// File requests only affect the explicitly named local asset-library subtree.
// No active scene, selection, package manifest or project setting is changed.
[InitializeOnLoad]
public static class YamyamAssetLibraryBridge
{
    const string AssetsRoot = "Assets/ThirdParty/YamyamAssetLibrary";
    static readonly string Project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
    static readonly string Work = Path.Combine(Project, "Library/YamyamAssetLibrary");
    static readonly string Stage = Path.Combine(Work, "staging/CreatorBundle");
    static readonly string Destination = Path.Combine(Project, AssetsRoot);
    static readonly string RequestPath = Path.Combine(Work, "request.json");
    static readonly string StatePath = Path.Combine(Work, "state.json");
    static readonly string StatusPath = Path.Combine(Work, "status.json");
    static readonly string ValidationPath = Path.Combine(Work, "validation.json");
    static readonly string HeadlessPath = Path.Combine(Work, "headless-session.json");
    static readonly string ImportOnlyPath = Path.Combine(Work, "import-only-once.json");
    static readonly Regex ScriptReference = new Regex(@"m_Script:\s*\{fileID:\s*(-?\d+)(?:,\s*guid:\s*([a-fA-F0-9]{32}))?", RegexOptions.Compiled);
    static readonly Regex TextureReference = new Regex(@"m_Texture:\s*\{fileID:\s*(-?\d+)(?:,\s*guid:\s*([a-fA-F0-9]{32}))?", RegexOptions.Compiled);
    static readonly PropertyInfo ReferenceIdProperty = typeof(SerializedProperty).GetProperty("objectReferenceEntityIdValue") ?? typeof(SerializedProperty).GetProperty("objectReferenceInstanceIDValue");
    static double nextPoll, idleSince = -1, lastProgress;
    static Job job;
    static Report report;
    static string[] paths;
    static int cursor;
    static List<object> upgraders;
    static PropertyInfo oldShaderProperty, newShaderProperty;
    static MethodInfo upgradeMethod;
    static object upgradeFlags;
    static readonly HashSet<string> clips = new HashSet<string>();
    static readonly HashSet<string> materials = new HashSet<string>();
    static readonly Dictionary<string, int> shaderCounts = new Dictionary<string, int>();
    static readonly Dictionary<string, bool> sceneScriptReferences = new Dictionary<string, bool>();
    static bool offlineBinaryEvidenceLoaded;
    static string offlineBinaryEvidenceError, offlineBinaryEvidenceSha256;
    static OfflineBinaryEvidence offlineBinaryEvidence;
    static readonly Dictionary<string, OfflineBinaryScene> offlineBinaryScenes = new Dictionary<string, OfflineBinaryScene>(StringComparer.OrdinalIgnoreCase);
    static readonly HashSet<string> offlineBinaryScenesChecked = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
    static Manifest manifest;
    static PreviewReport previewReport;
    static int previewCursor;
    static bool fallbackStarted;
    static HeadlessSession headless;
    static bool collectMemory;
    static bool terminalHeadlessStateLoaded;
    static int heavyLoads, collectionCount;
    static readonly List<MemoryRecord> memoryEvidence = new List<MemoryRecord>();

    [Serializable] public class Request
    {
        public string nonce;
        public string command;
        public bool upgradeMaterials = true;
    }
    [Serializable] public class Job
    {
        public string nonce, command, phase, startedUtc, updatedUtc, error;
        public bool upgradeMaterials, moved;
        public int upgradedMaterials, examinedMaterials;
        public List<UpgradeRecord> upgrades = new List<UpgradeRecord>();
        public List<Issue> upgradeIssues = new List<Issue>();
    }
    [Serializable] public class Status
    {
        public string status, nonce, command, phase, updatedUtc, unityVersion;
        public string assetsRoot = AssetsRoot, stagingRoot = Stage;
        public string error;
        public bool rootExists, stagingExists, compiling, updating, playing;
        public int processed, total, upgradedMaterials;
    }
    [Serializable] public class Issue
    {
        public string path, kind, detail;
        public int count;
        public Issue(string path, string kind, string detail, int count = 1)
        { this.path = path; this.kind = kind; this.detail = detail; this.count = count; }
    }
    [Serializable] public class UpgradeRecord
    {
        public string path, before, after;
    }
    [Serializable] public class ShaderCount
    {
        public string shader;
        public int count;
    }
    [Serializable] public class Report
    {
        public string nonce, completedUtc, unityVersion, assetsRoot = AssetsRoot;
        public string status = "validating";
        public string validationScope = "Imported subtree only; prefab/model hierarchies, recursive asset dependency closure, Unity YAML script/texture references and source-SHA-bound offline binary-scene explicit m_Script fields. Scene assets are never opened. Prefab-inherited components are covered by prefab validation separately.";
        public int assetFiles, prefabs, modelFiles, materialFiles, embeddedMaterials, animationClips;
        public int textureFiles, scenes, missingMonoScripts, missingTextureReferences, missingShaders;
        public int unsupportedShaders, shaderCompileErrors, unreadableAssets, upgradedMaterials, unassignedTextureSlots;
        public int inactiveSavedTextureReferenceCount;
        public List<Issue> inactiveSavedTextureReferences = new List<Issue>();
        public int externalAssetDependencyCount;
        public List<ExternalAssetDependency> externalAssetDependencies = new List<ExternalAssetDependency>();
        public int binarySceneSourcesVerified, binaryExplicitMonoBehaviours, binaryScriptReferencesResolved;
        public List<BinarySceneCheck> binaryScenes = new List<BinarySceneCheck>();
        public List<ShaderCount> shaders = new List<ShaderCount>();
        public List<UpgradeRecord> upgrades = new List<UpgradeRecord>();
        public List<Issue> issues = new List<Issue>();
    }
    [Serializable] public class OfflineBinaryEvidence
    {
        public int schemaVersion;
        public string stageRoot, sourceManifestSha256, parser, parserVersion;
        public OfflineBinaryScene[] scenes;
    }
    [Serializable] public class OfflineBinaryScene
    {
        public string scenePath, relativePath, status, sourceSha256;
        public long sourceBytes;
        public int monoBehaviourCount;
        public OfflineBinaryReference[] references;
        public OfflineDecodeFailure[] decodeFailures;
    }
    [Serializable] public class OfflineDecodeFailure { public string error; }
    [Serializable] public class OfflineBinaryReference
    {
        public string objectPathId, decodeStatus, scriptReferenceKind, scriptLocalFileId, scriptGuid;
        public int scriptExternalFileId;
    }
    [Serializable] public class BinarySceneCheck
    {
        public string path, status, sourceSha256, evidenceSha256, parser, parserVersion, detail;
        public long sourceBytes;
        public int explicitMonoBehaviours, resolvedScriptReferences, unresolvedScriptReferences;
    }
    [Serializable] public class ExternalAssetDependency
    {
        public string path;
        public string[] ownerProductFolders;
    }
    [Serializable] public class Manifest { public Product[] products; }
    [Serializable] public class Product { public string id, title, folder; public int index; }
    [Serializable] public class PreviewRecord
    {
        public string id, title, assetPath, imagePath, error;
        public string kind = "isolated-static-mesh-preview";
        public int drawCalls, visiblePixels, magentaLikePixels, totalPixels;
        public int renderTextureWidth, renderTextureHeight, outputWidth, outputHeight;
        public float editorPixelsPerPoint, fittedDistance, boundsRadius;
        public string framingAlgorithm, sourceSelectionReason;
        public Vector3 boundsCenter, boundsExtents, viewportMin, viewportMax;
        public bool boundsInsideViewport;
    }
    [Serializable] public class PreviewReport
    {
        public string completedUtc, unityVersion;
        public string scope = "One representative imported prefab/model per product, rendered in a temporary PreviewRenderUtility scene. Static mesh/bind-pose import QA, not animation or full-product artistic approval. Magenta-like pixels are an inspection cue, not automatically a shader error.";
        public List<PreviewRecord> products = new List<PreviewRecord>();
    }
    [Serializable] public class HeadlessSession
    {
        public string projectPath, nonce, command, startedUtc, completedUtc, status, error;
        public string validationPath, previewsPath, fallbackPath;
        public bool active;
        public int exitCode;
    }
    [Serializable] public class MemoryRecord
    {
        public string utc, phase;
        public int collection, heavyLoadUnits;
        public long beforeBytes, afterBytes;
    }
    struct MeshDraw { public Mesh mesh; public Matrix4x4 matrix; public Material[] materials; public bool temporary; }

    static YamyamAssetLibraryBridge()
    {
        EditorApplication.update += Poll;
        // Deferred acknowledgement demonstrates that this script compiled in the running editor.
        EditorApplication.delayCall += () =>
        {
            Directory.CreateDirectory(Work);
            WriteJson(Path.Combine(Work, "compiled.json"), new Status
            { status = "compiled", unityVersion = Application.unityVersion, updatedUtc = Utc() });
            ResumeHeadless();
        };
    }

    // -executeMethod entry point. This refuses both interactive editors and the real project,
    // even if somebody copied a stale headless-session marker into that project's Library.
    public static void RunHeadless() { StartHeadless("finalize"); }

    // Read-only asset validation after repairs; preserves previously rendered previews.
    public static void RunHeadlessValidation() { StartHeadless("validate"); }

    static void StartHeadless(string command)
    {
        if (command != "finalize" && command != "validate") throw new ArgumentException("Unsupported headless command.", "command");
        if (!CanRunHeadless())
            throw new InvalidOperationException("RunHeadless requires batchmode in the isolated Library/YamyamAssetLibrary/headless-project checkout.");
        Directory.CreateDirectory(Work);
        if (TryFinishImportOnly()) return;
        ResumeHeadless();
        if (headless != null && headless.active)
        {
            string activeCommand = string.IsNullOrEmpty(headless.command) ? "finalize" : headless.command;
            if (activeCommand != command)
                throw new IOException("Preserving an active headless session with a different command: " + activeCommand);
            // Recover the narrow crash boundary between writing the session marker and request.
            var savedJob = File.Exists(StatePath) ? JsonUtility.FromJson<Job>(File.ReadAllText(StatePath)) : null;
            if (!File.Exists(RequestPath) && (savedJob == null || savedJob.nonce != headless.nonce))
            {
                if (File.Exists(Receipt(headless.nonce)))
                    throw new IOException("A consumed headless nonce has no matching persisted job; inspect the isolated project before retrying.");
                WriteJson(RequestPath, new Request { nonce = headless.nonce, command = command, upgradeMaterials = command == "finalize" });
            }
            nextPoll = 0; idleSince = -1; return;
        }
        if (File.Exists(RequestPath))
            throw new IOException("Preserving an existing isolated-project request. Inspect it before starting another headless session.");
        if (File.Exists(StatePath))
        {
            var previous = JsonUtility.FromJson<Job>(File.ReadAllText(StatePath));
            if (previous != null && previous.phase != "complete" && previous.phase != "failed")
                throw new IOException("Preserving an unfinished isolated-project job without an active matching headless marker.");
        }
        headless = new HeadlessSession { projectPath = Project, nonce = "headless-" + Guid.NewGuid().ToString("N"), command = command,
            active = true, startedUtc = Utc(), status = "running", validationPath = ValidationPath,
            previewsPath = command == "validate" ? null : Path.Combine(Work, "previews.json"),
            fallbackPath = command == "validate" ? null : Path.Combine(Work, "fallback-preparation-report.json") };
        WriteJson(HeadlessPath, headless);
        WriteJson(RequestPath, new Request { nonce = headless.nonce, command = command, upgradeMaterials = command == "finalize" });
        job = null; ResetSession(); nextPoll = 0; idleSince = -1;
        Debug.Log("Yamyam asset-library isolated headless session started: " + headless.nonce);
    }

    static bool CanRunHeadless()
    {
        string suffix = Path.DirectorySeparatorChar + Path.Combine("Library", "YamyamAssetLibrary", "headless-project");
        return Application.isBatchMode && Project.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
            .EndsWith(suffix, StringComparison.OrdinalIgnoreCase);
    }

    static void ResumeHeadless()
    {
        if (!CanRunHeadless() || !File.Exists(HeadlessPath)) return;
        var saved = JsonUtility.FromJson<HeadlessSession>(File.ReadAllText(HeadlessPath));
        if (saved == null || !saved.active || !string.Equals(saved.projectPath, Project, StringComparison.OrdinalIgnoreCase)) return;
        headless = saved;
    }

    static void FinishHeadlessIfReady()
    {
        if (!CanRunHeadless() || headless == null || !headless.active || job == null ||
            headless.nonce != job.nonce || job.phase != "complete" && job.phase != "failed") return;
        headless.active = false; headless.completedUtc = Utc(); headless.status = job.phase;
        headless.error = job.error; headless.exitCode = job.phase == "complete" ? 0 : 1;
        WriteJson(HeadlessPath, headless);
        WriteJson(Path.Combine(Work, "headless-result.json"), headless);
        Debug.Log("Yamyam asset-library isolated headless session " + headless.status + "; exit=" + headless.exitCode);
        EditorApplication.Exit(headless.exitCode);
    }

    static string Utc() { return DateTime.UtcNow.ToString("o"); }
    static bool Busy()
    {
        if (EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode)
            return true;
        // Preserve the existing video capture bridges and their request queues.
        return Directory.Exists(Path.Combine(Project, "Library")) &&
            Directory.GetFiles(Path.Combine(Project, "Library"), "*.request", SearchOption.TopDirectoryOnly).Length != 0;
    }

    static void Poll()
    {
        if (EditorApplication.timeSinceStartup < nextPoll) return;
        nextPoll = EditorApplication.timeSinceStartup + (CanRunHeadless() ? .025 : .25);
        if (FinishOwnTerminalHeadlessBeforeBusy()) return;
        if (Busy()) { idleSince = -1; return; }
        if (idleSince < 0) idleSince = EditorApplication.timeSinceStartup;
        if (EditorApplication.timeSinceStartup - idleSince < 2) return;
        if (TryFinishImportOnly()) return;
        try
        {
            if (job == null && File.Exists(StatePath)) job = JsonUtility.FromJson<Job>(File.ReadAllText(StatePath));
            if (job != null && job.phase != "complete" && job.phase != "failed")
            { Advance(); return; }
            if (File.Exists(RequestPath)) Accept();
        }
        catch (Exception exception) { Fail(exception); }
        finally
        {
            CollectHeadlessMemoryIfNeeded();
            FinishHeadlessIfReady();
        }
    }

    static void Accept()
    {
        var request = JsonUtility.FromJson<Request>(File.ReadAllText(RequestPath));
        if (request == null || string.IsNullOrWhiteSpace(request.nonce) || request.nonce.Length > 256)
            throw new InvalidDataException("Request must contain a unique nonempty nonce of at most256 characters.");
        string receipt = Receipt(request.nonce);
        if (File.Exists(receipt))
        {
            File.Delete(RequestPath);
            WriteStatus("duplicate-request-ignored", "Nonce already consumed: " + request.nonce);
            return;
        }
        if (request.command != "probe" && request.command != "status" && request.command != "install" &&
            request.command != "validate" && request.command != "upgrade" && request.command != "finalize" && request.command != "preview")
            throw new InvalidDataException("Supported commands: probe, status, install, validate, upgrade, finalize, preview.");
        job = new Job { nonce = request.nonce, command = request.command, phase = "accepted",
            startedUtc = Utc(), upgradeMaterials = request.upgradeMaterials };
        SaveJob(); // Persist the nonce before consuming or carrying out any mutation.
        WriteJson(receipt, request);
        File.Delete(RequestPath);
        ResetSession();
        if (request.command == "status" || request.command == "probe")
        { job.phase = "complete"; SaveJob(); WriteStatus("ready"); return; }
        WriteStatus("accepted");
    }

    static void Advance()
    {
        if (job.phase == "accepted")
        {
            if (job.command == "install") Install();
            else
            {
                RequireRoot();
                job.phase = job.command == "preview" ? "previewing" : job.command == "validate" || !job.upgradeMaterials ? "validating" : "upgrading";
                SaveJob(); ResetSession();
            }
            return;
        }
        if (job.phase == "moving")
        {
            // Directory.Move is atomic on this volume. Recover if a domain reload followed it.
            if (Directory.Exists(Destination) && !Directory.Exists(Stage))
            { job.moved = true; job.phase = "waiting-for-import"; SaveJob(); AssetDatabase.Refresh(); idleSince = -1; }
            else throw new IOException("Interrupted move needs inspection; no automatic overwrite or retry was attempted.");
            return;
        }
        if (job.phase == "waiting-for-import")
        {
            RequireRoot();
            if (EditorApplication.timeSinceStartup - idleSince < 5) return;
            if (!AssetDatabase.IsValidFolder(AssetsRoot))
                throw new IOException("Imported root is not visible to AssetDatabase after refresh.");
            job.phase = job.upgradeMaterials ? "upgrading" : "validating";
            SaveJob(); ResetSession(); return;
        }
        if (job.phase == "upgrading") UpgradeChunk();
        else if (job.phase == "building-fallbacks") FallbackChunk();
        else if (job.phase == "validating") ValidateChunk();
        else if (job.phase == "previewing") PreviewChunk();
        else throw new InvalidDataException("Unknown persisted phase: " + job.phase);
    }

    static void Install()
    {
        if (!Directory.Exists(Stage)) throw new DirectoryNotFoundException("Prepared staging root is missing: " + Stage);
        if (Directory.Exists(Destination) && Directory.EnumerateFileSystemEntries(Destination).Any())
            throw new IOException("Destination is not empty; preserving all existing assets.");
        AssertContained(Stage, Work);
        AssertContained(Destination, Path.Combine(Project, "Assets/ThirdParty"));
        job.phase = "moving"; SaveJob(); WriteStatus("moving");
        bool refreshHeld = false, editing = false;
        try
        {
            AssetDatabase.DisallowAutoRefresh(); refreshHeld = true;
            AssetDatabase.StartAssetEditing(); editing = true;
            Directory.CreateDirectory(Path.GetDirectoryName(Destination));
            if (Directory.Exists(Destination)) Directory.Delete(Destination, false); // Already verified empty.
            Directory.Move(Stage, Destination);
            job.moved = true; job.phase = "waiting-for-import"; SaveJob();
        }
        finally
        {
            try { if (editing) AssetDatabase.StopAssetEditing(); }
            finally { if (refreshHeld) AssetDatabase.AllowAutoRefresh(); }
        }
        WriteStatus("waiting-for-import");
        idleSince = -1;
        AssetDatabase.Refresh(); // Default asynchronous pipeline; no forced global reimport.
    }

    static void PrepareUpgraders()
    {
        Type upgraderType = FindType("UnityEditor.Rendering.MaterialUpgrader");
        Type pipelineType = FindType("UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset");
        if (upgraderType == null || pipelineType == null)
            throw new InvalidOperationException("Installed official URP MaterialUpgrader API is unavailable.");
        var fetch = upgraderType.GetMethod("FetchAllUpgradersForPipeline", BindingFlags.Public | BindingFlags.Static,
            null, new[] { typeof(Type) }, null);
        if (fetch == null) throw new MissingMethodException(upgraderType.FullName, "FetchAllUpgradersForPipeline");
        upgraders = ((IEnumerable)fetch.Invoke(null, new object[] { pipelineType })).Cast<object>()
            .Where(value => value.GetType().GetInterfaces().Any(type => type.Name == "IBuiltInToURPMaterialUpgrader")).ToList();
        oldShaderProperty = upgraderType.GetProperty("OldShaderPath");
        newShaderProperty = upgraderType.GetProperty("NewShaderPath");
        Type flagsType = upgraderType.GetNestedType("UpgradeFlags");
        upgradeMethod = upgraderType.GetMethod("Upgrade", BindingFlags.Public | BindingFlags.Instance,
            null, new[] { typeof(Material), flagsType }, null);
        upgradeFlags = Enum.ToObject(flagsType, 0);
        if (oldShaderProperty == null || newShaderProperty == null || upgradeMethod == null)
            throw new MissingMethodException("Official material-upgrader members were not found.");
    }

    static Type FindType(string name)
    { return AppDomain.CurrentDomain.GetAssemblies().Select(assembly => assembly.GetType(name, false)).FirstOrDefault(type => type != null); }

    static void UpgradeChunk()
    {
        RequireRoot();
        if (paths == null)
        {
            paths = AssetDatabase.FindAssets("t:Material", new[] { AssetsRoot }).Select(AssetDatabase.GUIDToAssetPath)
                .Where(path => path.EndsWith(".mat", StringComparison.OrdinalIgnoreCase)).Distinct().OrderBy(path => path).ToArray();
            PrepareUpgraders(); WriteStatus("upgrading");
        }
        double deadline = EditorApplication.timeSinceStartup + .1;
        while (cursor < paths.Length && EditorApplication.timeSinceStartup < deadline)
        {
            string path = paths[cursor++];
            try
            {
                AssertAssetPath(path);
                var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (!material || !material.shader) continue;
                string before = material.shader.name;
                var upgrader = upgraders.FirstOrDefault(value => (string)oldShaderProperty.GetValue(value) == before);
                if (upgrader == null) continue;
                string after = (string)newShaderProperty.GetValue(upgrader);
                if (!Shader.Find(after)) throw new InvalidOperationException("Destination shader unavailable: " + after);
                upgradeMethod.Invoke(upgrader, new[] { (object)material, upgradeFlags });
                if (material.shader && material.shader.name == after)
                {
                    EditorUtility.SetDirty(material);
                    AssetDatabase.SaveAssetIfDirty(material); // Never SaveAssets: unrelated dirty assets are preserved.
                    job.upgrades.Add(new UpgradeRecord { path = path, before = before, after = after });
                    job.upgradedMaterials++;
                }
                else job.upgradeIssues.Add(new Issue(path, "material-upgrade-unverified", before + " -> " + after));
            }
            catch (Exception exception) { job.upgradeIssues.Add(new Issue(path, "material-upgrade-error", Unwrap(exception))); }
            finally { job.examinedMaterials++; NoteHeavyLoad(1); }
        }
        Progress("upgrading");
        if (cursor < paths.Length) return;
        job.phase = "building-fallbacks"; SaveJob(); ResetSession();
    }

    static void FallbackChunk()
    {
        var helper = FindType("YamyamAssetLibraryFallbacks");
        if (helper == null) throw new InvalidOperationException("The separate YamyamAssetLibraryFallbacks helper has not compiled.");
        if (!fallbackStarted)
        {
            var begin = helper.GetMethod("Begin", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(string) }, null);
            if (begin == null) throw new MissingMethodException(helper.FullName, "Begin(string manifestPath)");
            begin.Invoke(null, new object[] { Path.Combine(Work, "staging-manifest.json") });
            fallbackStarted = true; WriteStatus("building-fallbacks");
        }
        var tick = helper.GetMethod("Tick", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(int) }, null);
        if (tick == null) throw new MissingMethodException(helper.FullName, "Tick(int maxModels)");
        bool complete = (bool)tick.Invoke(null, new object[] { 2 });
        NoteHeavyLoad(4); // Model/PBR jobs can load several material/texture dependencies.
        if (!complete) return;
        var errorMember = helper.GetProperty("LastError", BindingFlags.Public | BindingFlags.Static);
        string error = errorMember != null ? errorMember.GetValue(null) as string : null;
        if (!string.IsNullOrEmpty(error)) throw new InvalidOperationException("Fallback builder reported: " + error);
        job.phase = "validating"; SaveJob(); ResetSession();
    }

    static void ValidateChunk()
    {
        RequireRoot();
        if (paths == null)
        {
            paths = AssetDatabase.FindAssets("", new[] { AssetsRoot }).Select(AssetDatabase.GUIDToAssetPath)
                .Where(path => !AssetDatabase.IsValidFolder(path)).Distinct().OrderBy(path => path).ToArray();
            report = new Report { nonce = job.nonce, unityVersion = Application.unityVersion,
                upgradedMaterials = job.upgradedMaterials, upgrades = new List<UpgradeRecord>(job.upgrades) };
            report.issues.AddRange(job.upgradeIssues);
            WriteStatus("validating");
        }
        double deadline = EditorApplication.timeSinceStartup + .1;
        while (cursor < paths.Length && EditorApplication.timeSinceStartup < deadline)
        {
            string path = paths[cursor++];
            try { InspectAsset(path); }
            catch (Exception exception)
            { report.unreadableAssets++; report.issues.Add(new Issue(path, "asset-inspection-error", Unwrap(exception))); }
        }
        Progress("validating");
        if (cursor < paths.Length) return;
        CompleteBinarySceneEvidence();
        InspectDependencyClosure();
        report.assetFiles = paths.Length;
        report.animationClips = clips.Count;
        report.shaders = shaderCounts.OrderBy(pair => pair.Key).Select(pair => new ShaderCount { shader = pair.Key, count = pair.Value }).ToList();
        report.completedUtc = Utc();
        report.status = report.missingMonoScripts + report.missingTextureReferences + report.missingShaders +
            report.unsupportedShaders + report.shaderCompileErrors + report.unreadableAssets == 0 && job.upgradeIssues.Count == 0 ? "pass" : "completed-with-issues";
        WriteJson(ValidationPath, report);
        job.phase = job.command == "validate" ? "complete" : "previewing";
        SaveJob(); WriteStatus(job.phase == "complete" ? report.status : "previewing"); ResetSession();
    }

    static void PreviewChunk()
    {
        RequireRoot();
        if (manifest == null)
        {
            string manifestPath = Path.Combine(Work, "staging-manifest.json");
            if (!File.Exists(manifestPath)) throw new FileNotFoundException("Product manifest is needed for scoped previews.", manifestPath);
            manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(manifestPath));
            if (manifest == null || manifest.products == null) throw new InvalidDataException("Product manifest has no products array.");
            previewReport = new PreviewReport { unityVersion = Application.unityVersion };
            WriteStatus("previewing");
        }
        if (previewCursor < manifest.products.Length)
        {
            Product product = manifest.products[previewCursor++];
            var result = new PreviewRecord { id = product.id, title = product.title };
            try
            {
                string folder = (product.folder ?? "").Replace('\\', '/').Trim('/');
                string productRoot = folder.StartsWith(AssetsRoot + "/", StringComparison.Ordinal) ? folder : AssetsRoot + "/" + folder;
                AssertAssetPath(productRoot + "/");
                if (!AssetDatabase.IsValidFolder(productRoot)) throw new DirectoryNotFoundException(productRoot);
                var candidates = PreviewAssetCandidates(productRoot);
                List<MeshDraw> draws = null; Bounds bounds = new Bounds();
                foreach (string candidate in candidates)
                {
                    var asset = AssetDatabase.LoadAssetAtPath<GameObject>(candidate);
                    if (!asset) continue;
                    draws = Draws(asset, out bounds);
                    if (draws.Count == 0) continue;
                    result.assetPath = candidate;
                    result.sourceSelectionReason = PreviewCandidateKind(candidate) + "; generated prefab, native prefab, then raw model ordering; visible static mesh only";
                    break;
                }
                string name = product.index.ToString("D3") + "-" + SafeName(product.id ?? product.folder);
                result.imagePath = Path.Combine(Work, "previews", name + ".png");
                if (string.IsNullOrEmpty(result.assetPath))
                {
                    var materialPaths = AssetDatabase.FindAssets("t:Material", new[] { productRoot }).Select(AssetDatabase.GUIDToAssetPath)
                        .Where(path => path.EndsWith(".mat", StringComparison.OrdinalIgnoreCase)).OrderByDescending(path => path.Contains("/Generated/"));
                    foreach (string path in materialPaths)
                    {
                        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                        if (!material) continue;
                        result.assetPath = path; result.kind = "isolated-material-sphere-preview";
                        var mesh = PreviewSphere();
                        draws = new List<MeshDraw> { new MeshDraw { mesh = mesh, matrix = Matrix4x4.identity, materials = new[] { material }, temporary = true } };
                        bounds = mesh.bounds; break;
                    }
                }
                if (string.IsNullOrEmpty(result.assetPath))
                {
                    string path = AssetDatabase.FindAssets("t:Texture2D", new[] { productRoot }).Select(AssetDatabase.GUIDToAssetPath).OrderBy(value => value).FirstOrDefault();
                    if (path == null) throw new InvalidDataException("No representative mesh, material or texture asset was available.");
                    result.assetPath = path; result.kind = "imported-texture-preview";
                    RenderTexturePreview(AssetDatabase.LoadAssetAtPath<Texture2D>(path), result);
                }
                else RenderPreview(draws, bounds, result);
            }
            catch (Exception exception) { result.error = Unwrap(exception); }
            previewReport.products.Add(result);
            WriteJson(Path.Combine(Work, "previews.json"), previewReport);
            WriteStatus("previewing");
            if (previewCursor % 4 == 0) collectMemory = true;
            return;
        }
        previewReport.completedUtc = Utc();
        WriteJson(Path.Combine(Work, "previews.json"), previewReport);
        job.phase = "complete"; SaveJob();
        WriteStatus(previewReport.products.Any(product => !string.IsNullOrEmpty(product.error)) ? "completed-with-preview-issues" : "complete");
        ResetSession();
    }

    static string PreviewCandidateKind(string path)
    {
        bool prefab = path.EndsWith(".prefab", StringComparison.OrdinalIgnoreCase);
        if (prefab && path.Replace('\\', '/').IndexOf("/Generated/", StringComparison.OrdinalIgnoreCase) >= 0) return "generated-prefab";
        return prefab ? "native-prefab" : "raw-model";
    }
    static string[] PreviewAssetCandidates(string productRoot)
    {
        return AssetDatabase.FindAssets("t:GameObject", new[] { productRoot }).Select(AssetDatabase.GUIDToAssetPath)
            .Distinct().OrderBy(path => PreviewCandidateKind(path) == "generated-prefab" ? 0 : PreviewCandidateKind(path) == "native-prefab" ? 1 : 2)
            .ThenBy(path => path, StringComparer.Ordinal).ToArray();
    }
    static IEnumerable<Vector3> PreviewBoundsCorners(Bounds bounds)
    {
        for (int x = -1; x <= 1; x += 2)
            for (int y = -1; y <= 1; y += 2)
                for (int z = -1; z <= 1; z += 2)
                    yield return bounds.center + Vector3.Scale(bounds.extents, new Vector3(x, y, z));
    }
    // Fit every AABB corner in camera coordinates. A margin of .90 leaves5% on each edge.
    // This is preview-only camera placement, not a modification of any source asset transform.
    static void FitPreviewCamera(Camera camera, Bounds bounds, int width, int height, PreviewRecord result)
    {
        const float occupancy = .90f;
        camera.rect = new Rect(0, 0, 1, 1);
        camera.pixelRect = new Rect(0, 0, width, height);
        camera.aspect = (float)width / height;
        camera.orthographic = false;
        camera.fieldOfView = 32;
        camera.ResetProjectionMatrix();
        Vector3 outward = new Vector3(1, .65f, -1.4f).normalized;
        Quaternion rotation = Quaternion.LookRotation(-outward, Vector3.up);
        Quaternion inverse = Quaternion.Inverse(rotation);
        float radius = Mathf.Max(.01f, bounds.extents.magnitude);
        float tanV = Mathf.Tan(camera.fieldOfView * .5f * Mathf.Deg2Rad);
        float tanH = tanV * camera.aspect;
        float distance = radius * .01f;
        foreach (Vector3 corner in PreviewBoundsCorners(bounds))
        {
            Vector3 relative = inverse * (corner - bounds.center);
            distance = Mathf.Max(distance, Mathf.Abs(relative.x) / (tanH * occupancy) - relative.z);
            distance = Mathf.Max(distance, Mathf.Abs(relative.y) / (tanV * occupancy) - relative.z);
            distance = Mathf.Max(distance, radius * .01f - relative.z);
        }
        camera.transform.SetPositionAndRotation(bounds.center + outward * distance, rotation);
        float minDepth = float.PositiveInfinity, maxDepth = 0;
        foreach (Vector3 corner in PreviewBoundsCorners(bounds))
        {
            float depth = (inverse * (corner - camera.transform.position)).z;
            minDepth = Mathf.Min(minDepth, depth); maxDepth = Mathf.Max(maxDepth, depth);
        }
        camera.nearClipPlane = Mathf.Max(.00001f, minDepth * .5f);
        camera.farClipPlane = Mathf.Max(camera.nearClipPlane * 2, maxDepth + radius * .1f);
        result.framingAlgorithm = "eight-bounds-corners-perspective-fit-v1; fullHiDPIviewport; wholeRT-resample";
        result.boundsCenter = bounds.center; result.boundsExtents = bounds.extents;
        result.boundsRadius = radius; result.fittedDistance = distance;
        result.viewportMin = new Vector3(float.PositiveInfinity, float.PositiveInfinity, float.PositiveInfinity);
        result.viewportMax = new Vector3(float.NegativeInfinity, float.NegativeInfinity, float.NegativeInfinity);
        foreach (Vector3 corner in PreviewBoundsCorners(bounds))
        {
            Vector3 point = camera.WorldToViewportPoint(corner);
            result.viewportMin = Vector3.Min(result.viewportMin, point); result.viewportMax = Vector3.Max(result.viewportMax, point);
        }
        result.boundsInsideViewport = result.viewportMin.x >= .049f && result.viewportMin.y >= .049f && result.viewportMin.z > 0 &&
            result.viewportMax.x <= .951f && result.viewportMax.y <= .951f && result.viewportMax.z <= camera.farClipPlane;
        if (!result.boundsInsideViewport) throw new InvalidDataException("Fitted preview bounds escaped5% viewport margin.");
    }

    static List<MeshDraw> Draws(GameObject asset, out Bounds bounds)
    {
        var draws = new List<MeshDraw>(); bounds = new Bounds(); bool first = true;
        foreach (var renderer in asset.GetComponentsInChildren<Renderer>(true))
        {
            if (!renderer.enabled || !renderer.gameObject.activeSelf) continue;
            Mesh mesh = null;
            var skinned = renderer as SkinnedMeshRenderer;
            if (skinned) mesh = skinned.sharedMesh;
            else
            {
                var filter = renderer.GetComponent<MeshFilter>();
                if (filter) mesh = filter.sharedMesh;
            }
            if (!mesh || mesh.vertexCount == 0) continue;
            Matrix4x4 matrix = renderer.localToWorldMatrix;
            var transformed = new Bounds(matrix.MultiplyPoint3x4(mesh.bounds.center), Vector3.zero);
            Vector3 extents = mesh.bounds.extents;
            for (int x = -1; x <= 1; x += 2)
                for (int y = -1; y <= 1; y += 2)
                    for (int z = -1; z <= 1; z += 2)
                        transformed.Encapsulate(matrix.MultiplyPoint3x4(mesh.bounds.center + Vector3.Scale(extents, new Vector3(x, y, z))));
            if (first) { bounds = transformed; first = false; } else bounds.Encapsulate(transformed);
            draws.Add(new MeshDraw { mesh = mesh, matrix = matrix, materials = renderer.sharedMaterials });
        }
        return draws;
    }

    static void RenderPreview(List<MeshDraw> draws, Bounds bounds, PreviewRecord result)
    {
        const int width = 640, height = 480;
        var preview = new PreviewRenderUtility();
        Texture2D pixels = null; bool begun = false;
        var priorTarget = RenderTexture.active;
        RenderTexture outputTarget = null;
        bool priorAsyncCompilation = ShaderUtil.allowAsyncCompilation;
        try
        {
            ShaderUtil.allowAsyncCompilation = false;
            preview.camera.backgroundColor = new Color(.055f, .065f, .08f, 1);
            preview.camera.clearFlags = CameraClearFlags.SolidColor;
            preview.camera.fieldOfView = 32;
            preview.camera.allowHDR = false;
            preview.ambientColor = new Color(.4f, .4f, .4f, 1);
            preview.lights[0].intensity = 1.3f; preview.lights[0].color = Color.white;
            preview.lights[0].transform.rotation = Quaternion.Euler(35, 30, 0);
            preview.lights[1].intensity = .75f; preview.lights[1].color = new Color(.85f, .9f, 1);
            preview.lights[1].transform.rotation = Quaternion.Euler(335, 210, 0);
            preview.BeginPreview(new Rect(0, 0, width, height), GUIStyle.none); begun = true;
            var target = preview.camera.targetTexture;
            if (!target) throw new InvalidOperationException("Preview camera has no target RenderTexture.");
            result.renderTextureWidth = target.width; result.renderTextureHeight = target.height;
            result.outputWidth = width; result.outputHeight = height; result.editorPixelsPerPoint = EditorGUIUtility.pixelsPerPoint;
            // BeginPreview's RT is in device pixels, while its Rect is in UI points. Fit AFTER initialization,
            // use the whole device-pixel viewport and later resample the WHOLE RT to the requested PNG size.
            FitPreviewCamera(preview.camera, bounds, target.width, target.height, result);
            foreach (var draw in draws)
                for (int submesh = 0; submesh < draw.mesh.subMeshCount; submesh++)
                {
                    if (draw.materials == null || draw.materials.Length == 0) continue;
                    Material material = draw.materials[Mathf.Min(submesh, draw.materials.Length - 1)];
                    if (!material) continue;
                    preview.DrawMesh(draw.mesh, draw.matrix, material, submesh);
                    result.drawCalls++;
                }
            // Unity's official preview API opts into the active SRP only for this temporary scene.
            preview.Render(true, false);
            var rendered = preview.EndPreview() as RenderTexture; begun = false;
            if (!rendered) throw new InvalidOperationException("Preview API returned no RenderTexture.");
            // Reading only640x480 of a larger HiDPI RT crops its lower-left quadrant.
            // Resampling the complete texture preserves framing at all editor display scales.
            outputTarget = RenderTexture.GetTemporary(width, height, 0, RenderTextureFormat.ARGB32);
            Graphics.Blit(rendered, outputTarget);
            RenderTexture.active = outputTarget;
            pixels = new Texture2D(width, height, TextureFormat.RGB24, false);
            pixels.ReadPixels(new Rect(0, 0, width, height), 0, 0); pixels.Apply(false);
            var colors = pixels.GetPixels32(); Color32 background = colors[0];
            result.totalPixels = colors.Length;
            foreach (var color in colors)
            {
                if (Math.Abs(color.r - background.r) + Math.Abs(color.g - background.g) + Math.Abs(color.b - background.b) > 36) result.visiblePixels++;
                if (color.r > 200 && color.b > 200 && color.g < 85) result.magentaLikePixels++;
            }
            Directory.CreateDirectory(Path.GetDirectoryName(result.imagePath));
            File.WriteAllBytes(result.imagePath, pixels.EncodeToPNG());
            if (result.drawCalls == 0 || result.visiblePixels < 64) result.error = "Preview contained no visible rendered mesh; inspect output.";
        }
        finally
        {
            try { if (begun) preview.EndPreview(); }
            finally
            {
                try { RenderTexture.active = priorTarget; preview.Cleanup(); }
                finally
                {
                    ShaderUtil.allowAsyncCompilation = priorAsyncCompilation;
                    RenderTexture.active = priorTarget;
                    if (outputTarget) RenderTexture.ReleaseTemporary(outputTarget);
                    if (pixels) Object.DestroyImmediate(pixels);
                    foreach (var draw in draws) if (draw.temporary && draw.mesh) Object.DestroyImmediate(draw.mesh);
                }
            }
        }
    }

    [Serializable] public class PreviewProbeRow
    {
        public string id, beforeAsset, afterAsset, sourceSha256, imageBeforeSha256, imageAfterSha256;
        public int visiblePixels, magentaLikePixels;
        public List<string> materialShaderEvidence = new List<string>();
    }
    [Serializable] public class PreviewProbeReport
    {
        public string status, startedUtc, completedUtc, error, previewsBeforeSha256, previewsAfterSha256, runDirectory;
        public int retainedRecords, retainedImages;
        public bool scenesOpened, sourceAssetsSaved, mainProjectModified;
        public List<PreviewProbeRow> rows = new List<PreviewProbeRow>();
        public List<string> nativeErrors = new List<string>();
    }
    static string HashPreviewProbeFile(string path)
    { using(var stream=File.OpenRead(path)) using(var hash=SHA256.Create()) return Hex(hash.ComputeHash(stream)); }
    [Serializable] public class PreviewAssetOverride
    {
        public string id, assetPath, sha256, reason;
    }
    [Serializable] public class PreviewFramingRequest
    {
        public string nonce, expectedPreviewsSha256;
        public string[] ids;
        public bool preferPrefab;
        public PreviewAssetOverride[] assetOverrides;
    }
    [Serializable] public class PreviewFramingRow
    {
        public string id, beforeAsset, afterAsset, beforeImageSha256, afterImageSha256, sourceSha256;
        public bool representativeChanged;
        public PreviewRecord result;
        public List<string> materialEvidence = new List<string>();
    }
    [Serializable] public class PreviewFramingReport
    {
        public string status, startedUtc, completedUtc, nonce, runDirectory, error, priorPreviewsSha256;
        public string scope = "Read-only source assets; bounded explicit product IDs, one representative static preview each; outputs only into this probe's Library run directory. No canonical preview promotion, animation or full-product approval.";
        public List<PreviewFramingRow> rows = new List<PreviewFramingRow>();
        public List<string> nativeErrors = new List<string>();
    }
    // Run only after root has placed an explicit hash-bound ID list. This never replaces current previews.json/PNGs.
    public static void RunHeadlessPreviewFramingProbe()
    {
        if (!CanRunHeadless()) throw new InvalidOperationException("Framing probe is isolated batch-only.");
        RequireRoot();
        string requestPath = Path.Combine(Work, "preview-framing-request.json");
        string jsonPath = Path.Combine(Work, "previews.json");
        string run = Path.Combine(Work, "preview-framing", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(run);
        var probe = new PreviewFramingReport { status = "checking", startedUtc = Utc(), runDirectory = run };
        Application.LogCallback capture = (condition, trace, type) => {
            if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) probe.nativeErrors.Add(condition);
        };
        int exitCode = 0;
        try
        {
            if (File.Exists(RequestPath)) throw new IOException("Existing bridge request must be preserved.");
            var request = JsonUtility.FromJson<PreviewFramingRequest>(File.ReadAllText(requestPath));
            if (request == null || string.IsNullOrEmpty(request.nonce) || request.ids == null || request.ids.Length < 1 || request.ids.Length > 84 || request.ids.Distinct().Count() != request.ids.Length)
                throw new InvalidDataException("Explicit unique1..84 product IDs and nonce required.");
            var explicitOverrides = request.assetOverrides ?? new PreviewAssetOverride[0];
            if (explicitOverrides.Length > request.ids.Length || explicitOverrides.Any(x => x == null || !request.ids.Contains(x.id, StringComparer.Ordinal) ||
                string.IsNullOrEmpty(x.assetPath) || x.assetPath.Contains("\\") || x.assetPath.Split('/').Any(p => p == "." || p == "..") ||
                string.IsNullOrEmpty(x.sha256) || !Regex.IsMatch(x.sha256, "^[a-f0-9]{64}$") ||
                !(x.assetPath.EndsWith(".prefab", StringComparison.OrdinalIgnoreCase) || x.assetPath.EndsWith(".fbx", StringComparison.OrdinalIgnoreCase) || x.assetPath.EndsWith(".obj", StringComparison.OrdinalIgnoreCase))) ||
                explicitOverrides.Select(x => x.id).Distinct(StringComparer.Ordinal).Count() != explicitOverrides.Length)
                throw new InvalidDataException("Representative overrides require unique requested IDs, normalized prefab/model paths and exact SHA256.");
            probe.nonce = request.nonce;
            var existing = JsonUtility.FromJson<PreviewReport>(File.ReadAllText(jsonPath));
            if (existing == null || existing.products == null || existing.products.Count != 84 || string.IsNullOrEmpty(existing.completedUtc))
                throw new InvalidDataException("Completed84 current previews required.");
            probe.priorPreviewsSha256 = HashPreviewProbeFile(jsonPath);
            if (!string.Equals(request.expectedPreviewsSha256, probe.priorPreviewsSha256, StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("Current preview record hash differs from explicit request.");
            File.Copy(jsonPath, Path.Combine(run, "previews.before.json"), false);
            File.Copy(requestPath, Path.Combine(run, "request.json"), false);
            var immutableImages = existing.products.ToDictionary(x => x.id, x => HashPreviewProbeFile(x.imagePath), StringComparer.Ordinal);
            var productManifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(Work, "staging-manifest.json")));
            if (productManifest == null || productManifest.products == null) throw new InvalidDataException("Product manifest unavailable.");
            Application.logMessageReceived += capture;
            foreach (string id in request.ids)
            {
                var current = existing.products.Single(x => x.id == id);
                var product = productManifest.products.Single(x => x.id == id);
                string folder = (product.folder ?? "").Replace('\\', '/').Trim('/');
                string productRoot = folder.StartsWith(AssetsRoot + "/", StringComparison.Ordinal) ? folder : AssetsRoot + "/" + folder;
                AssertAssetPath(productRoot + "/");
                var row = new PreviewFramingRow { id = id, beforeAsset = current.assetPath, beforeImageSha256 = immutableImages[id] };
                probe.rows.Add(row);
                var result = new PreviewRecord { id = id, title = current.title, imagePath = Path.Combine(run, id + ".png") };
                row.result = result;
                Bounds bounds = new Bounds(); List<MeshDraw> draws = null;
                var explicitOverride = explicitOverrides.SingleOrDefault(x => x.id == id);
                if (explicitOverride != null)
                {
                    if (!explicitOverride.assetPath.StartsWith(productRoot + "/", StringComparison.Ordinal)) throw new InvalidDataException("Representative override escaped its exact product.");
                    AssertAssetPath(explicitOverride.assetPath);
                    AssertContained(Path.Combine(Project, explicitOverride.assetPath), Path.Combine(Project, productRoot));
                    if (HashPreviewProbeFile(Path.Combine(Project, explicitOverride.assetPath)) != explicitOverride.sha256) throw new InvalidDataException("Explicit representative override SHA changed.");
                }
                string[] candidates = explicitOverride != null ? new[] { explicitOverride.assetPath } : request.preferPrefab ? PreviewAssetCandidates(productRoot) : new[] { current.assetPath };
                foreach (string candidate in candidates)
                {
                    if (!candidate.StartsWith(productRoot + "/", StringComparison.Ordinal)) throw new InvalidDataException("Representative escaped exact product scope.");
                    var asset = AssetDatabase.LoadAssetAtPath<GameObject>(candidate);
                    if (!asset) continue;
                    var candidateDraws = Draws(asset, out bounds);
                    if (candidateDraws.Count == 0) continue;
                    draws = candidateDraws; result.assetPath = candidate;
                    result.sourceSelectionReason = explicitOverride != null ? "explicit SHA-bound product-owned representative override; " + (explicitOverride.reason ?? "") : request.preferPrefab ? PreviewCandidateKind(candidate) + "; explicit request permits generated-prefab/native-prefab/raw-model priority" : "exact existing representative preserved";
                    break;
                }
                if (draws == null)
                {
                    if (explicitOverride != null) throw new InvalidDataException("Explicit representative override has no static mesh draws; no silent fallback permitted.");
                    result.assetPath = current.assetPath; result.kind = current.kind;
                    result.sourceSelectionReason = "exact existing material/texture fallback preserved";
                    var material = AssetDatabase.LoadAssetAtPath<Material>(current.assetPath);
                    if (material)
                    {
                        Mesh sphere = PreviewSphere(); bounds = sphere.bounds;
                        draws = new List<MeshDraw> { new MeshDraw { mesh = sphere, matrix = Matrix4x4.identity, materials = new[] { material }, temporary = true } };
                    }
                    else
                    {
                        var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(current.assetPath);
                        if (!texture) throw new InvalidDataException("No renderable representative in explicit product scope.");
                        RenderTexturePreview(texture, result);
                    }
                }
                row.afterAsset = result.assetPath;
                row.representativeChanged = row.beforeAsset != row.afterAsset;
                row.sourceSha256 = HashPreviewProbeFile(Path.Combine(Project, row.afterAsset));
                if (draws != null)
                {
                    foreach (var material in draws.SelectMany(x => x.materials ?? new Material[0]).Where(x => x).Distinct())
                    {
                        string detail = AssetDatabase.GetAssetPath(material) + " | shader=" + (material.shader ? material.shader.name : "NULL");
                        foreach (string property in material.GetTexturePropertyNames())
                        {
                            var texture = material.GetTexture(property);
                            if (texture) detail += " | " + property + "=" + AssetDatabase.GetAssetPath(texture);
                        }
                        row.materialEvidence.Add(detail);
                    }
                    RenderPreview(draws, bounds, result);
                }
                if (!string.IsNullOrEmpty(result.error)) throw new InvalidDataException(result.error);
                if (HashPreviewProbeFile(Path.Combine(Project, row.afterAsset)) != row.sourceSha256) throw new IOException("Probe changed source payload.");
                row.afterImageSha256 = HashPreviewProbeFile(result.imagePath);
                WriteJson(Path.Combine(run, "report.json"), probe);
                if (probe.rows.Count % 8 == 0) { EditorUtility.UnloadUnusedAssetsImmediate(); GC.Collect(); }
            }
            if (probe.nativeErrors.Count != 0) throw new InvalidDataException("Native errors occurred during framing probe.");
            if (HashPreviewProbeFile(jsonPath) != probe.priorPreviewsSha256) throw new IOException("Canonical preview record changed during probe.");
            foreach (var prior in existing.products)
                if (HashPreviewProbeFile(prior.imagePath) != immutableImages[prior.id]) throw new IOException("Canonical preview PNG changed during probe.");
            probe.status = "complete";
        }
        catch (Exception error) { probe.status = "failed"; probe.error = Unwrap(error); exitCode = 1; }
        finally
        {
            Application.logMessageReceived -= capture;
            probe.completedUtc = Utc();
            WriteJson(Path.Combine(run, "report.json"), probe);
            WriteJson(Path.Combine(Work, "preview-framing-report.json"), probe);
        }
        if (exitCode != 0) Debug.LogError(probe.error);
        EditorApplication.Exit(exitCode);
    }

    public static void RunHeadlessPreviewProbe()
    {
        if (!CanRunHeadless()) throw new InvalidOperationException("Scoped preview probe is isolated batch-only.");
        RequireRoot();
        string run=Path.Combine(Work,"preview-probe",DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ")+"-"+Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(run);
        var probe=new PreviewProbeReport {status="checking",startedUtc=Utc(),runDirectory=run};
        string reportPath=Path.Combine(run,"report.json"), jsonPath=Path.Combine(Work,"previews.json");
        Application.LogCallback capture=(condition,trace,type)=> {if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert) probe.nativeErrors.Add(condition);};
        int exitCode=0;
        try
        {
            if(File.Exists(RequestPath)) throw new IOException("Existing bridge request must be preserved.");
            var existing=JsonUtility.FromJson<PreviewReport>(File.ReadAllText(jsonPath));
            if(existing.products==null||existing.products.Count!=84||string.IsNullOrEmpty(existing.completedUtc)) throw new InvalidDataException("Completed84 previews required.");
            probe.previewsBeforeSha256=HashPreviewProbeFile(jsonPath);
            File.Copy(jsonPath,Path.Combine(run,"previews.before.json"),false);
            var untouchedRows=existing.products.Where(x=>x.id!="015"&&x.id!="038").ToDictionary(x=>x.id,x=>JsonUtility.ToJson(x),StringComparer.Ordinal);
            var untouchedImages=existing.products.Where(x=>x.id!="015"&&x.id!="038").ToDictionary(x=>x.id,x=>HashPreviewProbeFile(x.imagePath),StringComparer.Ordinal);
            Application.logMessageReceived+=capture;
            foreach(string id in new[]{"015","038"})
            {
                var current=existing.products.Single(x=>x.id==id);
                var row=new PreviewProbeRow {id=id,beforeAsset=current.assetPath,imageBeforeSha256=HashPreviewProbeFile(current.imagePath)};probe.rows.Add(row);
                File.Copy(current.imagePath,Path.Combine(run,id+".before.png"),false);
                string path=id=="015" ? AssetsRoot+"/015-desert-canyon-stylized-environment/Desert World - Stylized Environment/3D/Plants/Cactus_1A.fbx" : current.assetPath;
                string prefix=AssetsRoot+"/"+id+"-";
                if(!path.StartsWith(prefix,StringComparison.Ordinal)||!path.EndsWith(".fbx",StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Probe representative escaped its exact product/model scope.");
                var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!asset)throw new InvalidDataException("Representative model unavailable.");
                row.sourceSha256=HashPreviewProbeFile(Path.Combine(Project,path));
                Bounds bounds;var draws=Draws(asset,out bounds);if(draws.Count==0)throw new InvalidDataException("Representative has no mesh draws.");
                foreach(var material in draws.SelectMany(x=>x.materials??new Material[0]).Where(x=>x).Distinct())
                {
                    string shaderPath=material.shader?AssetDatabase.GetAssetPath(material.shader):"";
                    row.materialShaderEvidence.Add(AssetDatabase.GetAssetPath(material)+" | "+(material.shader?material.shader.name:"NULL")+" | "+shaderPath+" | supported="+(material.shader&&material.shader.isSupported)+" | keywords="+string.Join(",",material.shaderKeywords));
                    if(material.shader&&material.passCount>0) ShaderUtil.CompilePass(material,0,true);
                }
                var replacement=new PreviewRecord{id=id,title=current.title,assetPath=path,imagePath=current.imagePath,kind="isolated-static-mesh-preview"};
                RenderPreview(draws,bounds,replacement);
                if(!string.IsNullOrEmpty(replacement.error))throw new InvalidDataException(replacement.error);
                if(id=="038"&&replacement.magentaLikePixels>1000)throw new InvalidDataException("P038 remains error-magenta after forced synchronous shader compilation; inspect native shader evidence.");
                if(HashPreviewProbeFile(Path.Combine(Project,path))!=row.sourceSha256)throw new IOException("Probe changed a source payload.");
                row.afterAsset=path;row.visiblePixels=replacement.visiblePixels;row.magentaLikePixels=replacement.magentaLikePixels;row.imageAfterSha256=HashPreviewProbeFile(current.imagePath);
                existing.products[existing.products.IndexOf(current)]=replacement;
            }
            if(probe.nativeErrors.Count!=0)throw new InvalidDataException("Native error occurred during scoped preview probe.");
            if(HashPreviewProbeFile(jsonPath)!=probe.previewsBeforeSha256)throw new IOException("Concurrent preview record write detected.");
            WriteJson(jsonPath,existing);
            var after=JsonUtility.FromJson<PreviewReport>(File.ReadAllText(jsonPath));
            foreach(var item in after.products.Where(x=>x.id!="015"&&x.id!="038"))
            {
                if(JsonUtility.ToJson(item)!=untouchedRows[item.id])throw new IOException("Untouched preview record changed.");probe.retainedRecords++;
                if(HashPreviewProbeFile(item.imagePath)!=untouchedImages[item.id])throw new IOException("Untouched preview image changed.");probe.retainedImages++;
            }
            if(probe.retainedRecords!=82||probe.retainedImages!=82)throw new InvalidDataException("Exactly82 untouched previews required.");
            probe.previewsAfterSha256=HashPreviewProbeFile(jsonPath);probe.status="complete";
        }
        catch(Exception error){probe.status="failed";probe.error=Unwrap(error);exitCode=1;}
        finally
        {
            Application.logMessageReceived-=capture;probe.completedUtc=Utc();WriteJson(reportPath,probe);WriteJson(Path.Combine(Work,"preview-probe-report.json"),probe);
        }
        if(exitCode!=0)Debug.LogError(probe.error);
        EditorApplication.Exit(exitCode);
    }

    static Mesh PreviewSphere()
    {
        const int rows = 20, columns = 32;
        var vertices = new Vector3[(rows + 1) * (columns + 1)];
        var uv = new Vector2[vertices.Length]; var triangles = new List<int>();
        for (int row = 0; row <= rows; row++)
            for (int column = 0; column <= columns; column++)
            {
                float latitude = Mathf.PI * row / rows, longitude = 2 * Mathf.PI * column / columns;
                int index = row * (columns + 1) + column;
                vertices[index] = new Vector3(Mathf.Sin(latitude) * Mathf.Cos(longitude), Mathf.Cos(latitude), Mathf.Sin(latitude) * Mathf.Sin(longitude));
                uv[index] = new Vector2((float)column / columns, 1f - (float)row / rows);
                if (row == rows || column == columns) continue;
                int next = index + columns + 1;
                triangles.AddRange(new[] { index, index + 1, next, next, index + 1, next + 1 });
            }
        var mesh = new Mesh { name = "Temporary asset-library QA sphere", hideFlags = HideFlags.HideAndDontSave };
        mesh.vertices = vertices; mesh.uv = uv; mesh.triangles = triangles.ToArray(); mesh.RecalculateNormals(); mesh.RecalculateBounds();
        return mesh;
    }
    static void RenderTexturePreview(Texture2D texture, PreviewRecord result)
    {
        if (!texture) throw new InvalidDataException("Representative texture did not load.");
        float scale = Mathf.Min(1f, Mathf.Min(640f / texture.width, 480f / texture.height));
        int width = Mathf.Max(1, Mathf.RoundToInt(texture.width * scale)), height = Mathf.Max(1, Mathf.RoundToInt(texture.height * scale));
        var target = RenderTexture.GetTemporary(width, height, 0, RenderTextureFormat.ARGB32);
        var prior = RenderTexture.active; Texture2D pixels = null;
        try
        {
            Graphics.Blit(texture, target); RenderTexture.active = target;
            pixels = new Texture2D(width, height, TextureFormat.RGBA32, false);
            pixels.ReadPixels(new Rect(0, 0, width, height), 0, 0); pixels.Apply(false);
            result.totalPixels = width * height; result.visiblePixels = result.totalPixels;
            Directory.CreateDirectory(Path.GetDirectoryName(result.imagePath));
            File.WriteAllBytes(result.imagePath, pixels.EncodeToPNG());
        }
        finally { RenderTexture.active = prior; RenderTexture.ReleaseTemporary(target); if (pixels) Object.DestroyImmediate(pixels); }
    }
    static string SafeName(string value)
    {
        string name = Regex.Replace(value ?? "product", @"[^a-zA-Z0-9_-]+", "-").Trim('-');
        return name.Length > 70 ? name.Substring(0, 70) : name.Length == 0 ? "product" : name;
    }

    static void InspectAsset(string path)
    {
        AssertAssetPath(path);
        string extension = Path.GetExtension(path).ToLowerInvariant();
        bool prefab = extension == ".prefab", scene = extension == ".unity";
        bool model = AssetImporter.GetAtPath(path) is ModelImporter;
        if (model) NoteHeavyLoad(4);
        else if (prefab) NoteHeavyLoad(2);
        else if (extension == ".mat" || extension == ".anim") NoteHeavyLoad(1);
        if (prefab) report.prefabs++;
        if (scene) report.scenes++;
        if (model) report.modelFiles++;
        if (AssetImporter.GetAtPath(path) is TextureImporter) report.textureFiles++;
        if (prefab || model)
        {
            var root = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (!root) { report.unreadableAssets++; report.issues.Add(new Issue(path, "missing-prefab-or-model", "Main GameObject did not load.")); }
            else foreach (var transform in root.GetComponentsInChildren<Transform>(true))
            {
                int count = GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(transform.gameObject);
                if (count == 0) continue;
                report.missingMonoScripts += count;
                report.issues.Add(new Issue(path, "missing-mono-script", Hierarchy(transform), count));
            }
        }
        // Scenes are checked as serialized assets to avoid opening or executing vendor scenes.
        if (scene) InspectSceneScripts(path);
        if (extension == ".mat" || extension == ".anim" || model)
            foreach (var asset in AssetDatabase.LoadAllAssetsAtPath(path))
            {
                var material = asset as Material;
                if (material) InspectMaterial(path, material, extension == ".mat");
                var clip = asset as AnimationClip;
                if (clip && !clip.name.StartsWith("__preview__", StringComparison.Ordinal)) clips.Add(Identity(path, clip));
            }
    }

    static void InspectMaterial(string path, Material material, bool standalone)
    {
        if (!materials.Add(Identity(path, material))) return;
        if (standalone) report.materialFiles++; else report.embeddedMaterials++;
        string shader = material.shader ? material.shader.name : "<missing>";
        if (!shaderCounts.ContainsKey(shader)) shaderCounts[shader] = 0;
        shaderCounts[shader]++;
        if (!material.shader || shader == "Hidden/InternalErrorShader")
        { report.missingShaders++; report.issues.Add(new Issue(path, "missing-shader", material.name)); }
        else if (!material.shader.isSupported)
        { report.unsupportedShaders++; report.issues.Add(new Issue(path, "unsupported-shader", material.name + ": " + shader)); }
        if (material.shader)
        {
            var shaderError = typeof(ShaderUtil).GetMethod("ShaderHasError", BindingFlags.Public | BindingFlags.Static,
                null, new[] { typeof(Shader) }, null);
            if (shaderError != null && (bool)shaderError.Invoke(null, new object[] { material.shader }))
            { report.shaderCompileErrors++; report.issues.Add(new Issue(path, "shader-compile-error", material.name + ": " + shader)); }
        }
        if (!standalone && !shader.StartsWith("Universal Render Pipeline/", StringComparison.Ordinal) &&
            !shader.StartsWith("Sprites/", StringComparison.Ordinal))
            report.issues.Add(new Issue(path, "embedded-material-review", material.name + ": " + shader + "; read-only model material was not rewritten."));
        // Old shader data remains serialized for reversibility. Only texture properties
        // exposed by a known current shader can be visually active. Unknown/error
        // shaders retain the conservative unfiltered checks until repaired.
        bool knownShader = material.shader && shader != "Hidden/InternalErrorShader" && material.shader.isSupported;
        var activeTextures = new HashSet<string>(StringComparer.Ordinal);
        if (knownShader)
            for (int index = 0; index < material.shader.GetPropertyCount(); index++)
                if (material.shader.GetPropertyType(index) == UnityEngine.Rendering.ShaderPropertyType.Texture)
                    activeTextures.Add(material.shader.GetPropertyName(index));
        var missing = new HashSet<string>();
        var inactive = new HashSet<string>();
        var nativeSavedNames = new HashSet<string>(StringComparer.Ordinal);
        using (var serialized = new SerializedObject(material))
        {
            var textures = serialized.FindProperty("m_SavedProperties.m_TexEnvs");
            if (textures != null && textures.isArray)
                for (int index = 0; index < textures.arraySize; index++)
                {
                    var pair = textures.GetArrayElementAtIndex(index);
                    var value = pair.FindPropertyRelative("second.m_Texture");
                    string property = pair.FindPropertyRelative("first").stringValue;
                    nativeSavedNames.Add(property);
                    bool active = !knownShader || activeTextures.Contains(property);
                    if (value != null && value.objectReferenceValue == null)
                    {
                        if (HasReferenceId(value)) { if (active) missing.Add(property); else inactive.Add(property); }
                        else if (active) report.unassignedTextureSlots++;
                    }
                }
        }
        if (standalone)
        {
            string text = File.ReadAllText(Path.Combine(Project, path));
            List<YamyamAssetLibraryMaterialTextureParser.Reference> named;
            bool mapped = YamyamAssetLibraryMaterialTextureParser.TryParse(text, nativeSavedNames, out named);
            if (!mapped)
            {
                // An unfamiliar serialization shape must never silently hide a GUID.
                report.unreadableAssets++;
                report.issues.Add(new Issue(path, "texture-reference-property-parser-incomplete", "Raw texture references could not all be bound to native saved property names; unfiltered reference validation retained."));
                foreach (Match match in TextureReference.Matches(text))
                {
                    string guid = match.Groups[2].Value.ToLowerInvariant();
                    if (match.Groups[1].Value == "0" || guid.Length == 0 || guid.All(character => character == '0') || IsBuiltInGuid(guid)) continue;
                    if (!TextureReferenceResolves(AssetDatabase.GUIDToAssetPath(guid), match.Groups[1].Value)) missing.Add("guid:" + guid);
                }
            }
            else foreach (var reference in named)
            {
                string guid = reference.guid, fileId = reference.fileId, property = reference.property;
                if (fileId == "0" || guid.Length == 0 || guid.All(character => character == '0') || IsBuiltInGuid(guid)) continue;
                if (!TextureReferenceResolves(AssetDatabase.GUIDToAssetPath(guid), fileId))
                {
                    if (!knownShader || activeTextures.Contains(property)) missing.Add("guid:" + guid);
                    else inactive.Add(property + " :: guid:" + guid);
                }
            }
        }
        if (inactive.Count > 0)
        {
            report.inactiveSavedTextureReferenceCount += inactive.Count;
            report.inactiveSavedTextureReferences.Add(new Issue(path, "inactive-saved-texture-reference", shader + ": " + string.Join(", ", inactive.OrderBy(value => value, StringComparer.Ordinal).ToArray()), inactive.Count));
        }
        if (missing.Count > 0)
        {
            report.missingTextureReferences += missing.Count;
            report.issues.Add(new Issue(path, "missing-texture-reference", string.Join(", ", missing.ToArray()), missing.Count));
        }
    }

    static void InspectSceneScripts(string path)
    {
        string text = File.ReadAllText(Path.Combine(Project, path));
        if (!text.TrimStart('\uFEFF').StartsWith("%YAML ", StringComparison.Ordinal))
        {
            InspectBinarySceneScripts(path);
            return;
        }
        foreach (Match match in ScriptReference.Matches(text))
        {
            string guid = match.Groups[2].Value;
            long localId;
            if (long.TryParse(match.Groups[1].Value, out localId) && localId != 0 && guid.Length > 0)
            {
                if (IsBuiltInGuid(guid) || SceneScriptReferenceResolves(guid, localId)) continue;
            }
            report.missingMonoScripts++;
            report.issues.Add(new Issue(path, "missing-scene-mono-script", "guid:" + guid + "; fileID:" + match.Groups[1].Value));
        }
    }
    static bool SceneScriptReferenceResolves(string guid, long expectedId)
    {
        string key = guid.ToLowerInvariant() + ":" + expectedId.ToString(System.Globalization.CultureInfo.InvariantCulture);
        bool resolved;
        if (sceneScriptReferences.TryGetValue(key, out resolved)) return resolved;
        string scriptPath = AssetDatabase.GUIDToAssetPath(guid);
        resolved = false;
        if (!string.IsNullOrEmpty(scriptPath))
            foreach (var script in AssetDatabase.LoadAllAssetsAtPath(scriptPath).OfType<MonoScript>())
            {
                string actualGuid; long actualId;
                if (AssetDatabase.TryGetGUIDAndLocalFileIdentifier(script, out actualGuid, out actualId) &&
                    actualId == expectedId && string.Equals(actualGuid, guid, StringComparison.OrdinalIgnoreCase) && script.GetClass() != null)
                { resolved = true; break; }
            }
        sceneScriptReferences[key] = resolved;
        return resolved;
    }
    static void InspectDependencyClosure()
    {
        try
        {
            var foreign = AssetDatabase.GetDependencies(paths, true)
                .Where(path => path.StartsWith("Assets/", StringComparison.OrdinalIgnoreCase) &&
                    !path.StartsWith(AssetsRoot + "/", StringComparison.OrdinalIgnoreCase) &&
                    !string.Equals(path, AssetsRoot, StringComparison.OrdinalIgnoreCase))
                .Distinct(StringComparer.OrdinalIgnoreCase).OrderBy(path => path, StringComparer.OrdinalIgnoreCase).ToArray();
            if (foreign.Length == 0) return;
            var ownership = foreign.ToDictionary(path => path, path => new List<string>(), StringComparer.OrdinalIgnoreCase);
            foreach (var product in paths.GroupBy(path => path.Substring(AssetsRoot.Length + 1).Split('/')[0], StringComparer.OrdinalIgnoreCase))
                foreach (string dependency in AssetDatabase.GetDependencies(product.ToArray(), true).Distinct(StringComparer.OrdinalIgnoreCase))
                {
                    List<string> owners;
                    if (ownership.TryGetValue(dependency, out owners)) owners.Add(product.Key);
                }
            foreach (string path in foreign)
            {
                string[] owners = ownership[path].OrderBy(owner => owner, StringComparer.OrdinalIgnoreCase).ToArray();
                report.externalAssetDependencies.Add(new ExternalAssetDependency { path = path, ownerProductFolders = owners });
                report.externalAssetDependencyCount++;
                report.unreadableAssets++;
                report.issues.Add(new Issue(path, "external-assets-dependency", "Owned library depends on Assets outside its movable root. Referencing product folders: " + string.Join(", ", owners)));
            }
        }
        catch (Exception exception)
        {
            report.unreadableAssets++;
            report.issues.Add(new Issue(AssetsRoot, "dependency-closure-error", Unwrap(exception)));
        }
    }
    static void LoadOfflineBinaryEvidence()
    {
        if (offlineBinaryEvidenceLoaded)
        {
            if (!string.IsNullOrEmpty(offlineBinaryEvidenceError)) throw new InvalidDataException(offlineBinaryEvidenceError);
            return;
        }
        offlineBinaryEvidenceLoaded = true;
        try
        {
            if (!CanRunHeadless()) throw new InvalidOperationException("Offline binary evidence is consumed only in the isolated batch project.");
            string evidencePath = Path.Combine(Path.GetDirectoryName(Project), "binary-scene-script-references.json");
            if ((File.GetAttributes(evidencePath) & FileAttributes.ReparsePoint) != 0)
                throw new IOException("Offline binary evidence cannot be a reparse point.");
            byte[] evidenceBytes = File.ReadAllBytes(evidencePath);
            using (var hash = SHA256.Create()) offlineBinaryEvidenceSha256 = Hex(hash.ComputeHash(evidenceBytes));
            offlineBinaryEvidence = JsonUtility.FromJson<OfflineBinaryEvidence>(Encoding.UTF8.GetString(evidenceBytes).TrimStart('\uFEFF'));
            if (offlineBinaryEvidence == null || offlineBinaryEvidence.schemaVersion != 1 || offlineBinaryEvidence.scenes == null ||
                !string.Equals(Path.GetFullPath(offlineBinaryEvidence.stageRoot), Path.GetFullPath(Destination), StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("Offline evidence does not identify this exact owned library root.");
            foreach (var scene in offlineBinaryEvidence.scenes)
            {
                if (scene == null || string.IsNullOrEmpty(scene.relativePath) || string.IsNullOrEmpty(scene.scenePath))
                    throw new InvalidDataException("Offline evidence has an incomplete scene identity.");
                string expected = AssetsRoot + "/" + scene.relativePath;
                if (scene.scenePath != expected || !scene.scenePath.EndsWith(".unity", StringComparison.OrdinalIgnoreCase) ||
                    scene.relativePath.Contains("\\") || scene.relativePath.Split('/').Any(part => part == ".." || part == "." || part.Length == 0) ||
                    scene.scenePath.IndexOf(':') >= 0)
                    throw new InvalidDataException("Offline evidence has an unsafe or mismatched scene path: " + scene.scenePath);
                AssertAssetPath(scene.scenePath);
                string absolute = Path.GetFullPath(Path.Combine(Project, scene.scenePath));
                AssertContained(absolute, Destination);
                if ((File.GetAttributes(absolute) & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("Binary scene source cannot be a reparse point.");
                if (offlineBinaryScenes.ContainsKey(scene.scenePath))
                    throw new InvalidDataException("Offline evidence contains duplicate Windows-casefold scene paths: " + scene.scenePath);
                offlineBinaryScenes.Add(scene.scenePath, scene);
            }
        }
        catch (Exception exception)
        {
            offlineBinaryEvidenceError = Unwrap(exception);
            throw;
        }
    }
    static string Hex(byte[] bytes) { return BitConverter.ToString(bytes).Replace("-", "").ToLowerInvariant(); }
    static void InspectBinarySceneScripts(string path)
    {
        var check = new BinarySceneCheck { path = path, status = "unavailable" };
        report.binaryScenes.Add(check);
        try
        {
            if (!CanRunHeadless()) throw new InvalidOperationException("Binary scenes are not opened or validated through external evidence in the interactive project.");
            LoadOfflineBinaryEvidence();
            OfflineBinaryScene scene;
            if (!offlineBinaryScenes.TryGetValue(path, out scene))
                throw new InvalidDataException("No unique offline evidence exists for this current binary scene.");
            if (!offlineBinaryScenesChecked.Add(path)) throw new InvalidDataException("A binary scene was inspected more than once.");
            check.evidenceSha256 = offlineBinaryEvidenceSha256;
            check.parser = offlineBinaryEvidence.parser; check.parserVersion = offlineBinaryEvidence.parserVersion;
            check.sourceSha256 = scene.sourceSha256; check.sourceBytes = scene.sourceBytes;
            if (scene.status != "decoded" || scene.references == null || scene.decodeFailures == null || scene.decodeFailures.Length != 0 ||
                scene.monoBehaviourCount < 0 || scene.references.Length != scene.monoBehaviourCount ||
                !Regex.IsMatch(scene.sourceSha256 ?? "", "^[a-f0-9]{64}$"))
                throw new InvalidDataException("Offline binary scene decoding is incomplete or failed.");
            string absolute = Path.Combine(Project, path);
            var before = new FileInfo(absolute);
            if (before.Length != scene.sourceBytes) throw new InvalidDataException("Offline binary scene size is stale.");
            long beforeBytes = before.Length, beforeTicks = before.LastWriteTimeUtc.Ticks;
            string actualSha;
            using (var input = File.OpenRead(absolute))
            using (var hash = SHA256.Create()) actualSha = Hex(hash.ComputeHash(input));
            var after = new FileInfo(absolute);
            if (actualSha != scene.sourceSha256 || after.Length != beforeBytes || after.LastWriteTimeUtc.Ticks != beforeTicks)
                throw new InvalidDataException("Offline binary scene source SHA is stale or the source changed during verification.");
            var objectIds = new HashSet<string>();
            foreach (var reference in scene.references)
            {
                long localId, objectId;
                if (reference == null || reference.decodeStatus != "decoded" || reference.scriptReferenceKind != "external" ||
                    reference.scriptExternalFileId <= 0 || !Regex.IsMatch(reference.scriptGuid ?? "", "^[a-f0-9]{32}$") ||
                    !long.TryParse(reference.objectPathId, out objectId) || objectId == 0 || !objectIds.Add(reference.objectPathId) ||
                    !long.TryParse(reference.scriptLocalFileId, out localId) || localId == 0)
                    throw new InvalidDataException("Offline m_Script reference is null, internal, duplicated, invalid or undecoded.");
                if (SceneScriptReferenceResolves(reference.scriptGuid, localId)) check.resolvedScriptReferences++;
                else
                {
                    check.unresolvedScriptReferences++; report.missingMonoScripts++;
                    report.issues.Add(new Issue(path, "missing-binary-scene-mono-script", "objectPathID:" + reference.objectPathId + "; guid:" + reference.scriptGuid + "; fileID:" + reference.scriptLocalFileId));
                }
            }
            check.explicitMonoBehaviours = scene.monoBehaviourCount;
            check.status = check.unresolvedScriptReferences == 0 ? "pass" : "missing-script-references";
            report.binarySceneSourcesVerified++;
            report.binaryExplicitMonoBehaviours += scene.monoBehaviourCount;
            report.binaryScriptReferencesResolved += check.resolvedScriptReferences;
        }
        catch (Exception exception)
        {
            check.detail = Unwrap(exception);
            report.unreadableAssets++;
            report.issues.Add(new Issue(path, "scene-script-validation-unavailable", check.detail));
        }
    }
    static void CompleteBinarySceneEvidence()
    {
        if (!offlineBinaryEvidenceLoaded || offlineBinaryEvidence == null || !string.IsNullOrEmpty(offlineBinaryEvidenceError)) return;
        foreach (string path in offlineBinaryScenes.Keys)
            if (!offlineBinaryScenesChecked.Contains(path))
            {
                report.unreadableAssets++;
                report.issues.Add(new Issue(path, "unused-binary-scene-evidence", "Offline evidence scene was not encountered as a current binary scene in this validation."));
            }
    }
    static bool TryFinishImportOnly()
    {
        // The main interactive project neither reads nor consumes this marker.
        if (!CanRunHeadless() || Busy() || !File.Exists(ImportOnlyPath)) return false;
        var marker = JsonUtility.FromJson<Request>(File.ReadAllText(ImportOnlyPath));
        string refusal = null;
        if (marker == null || marker.command != "import-only" || string.IsNullOrWhiteSpace(marker.nonce) || marker.nonce.Length > 256)
            refusal = "Import-only marker requires command=import-only and a unique nonempty nonce of at most256 characters.";
        var pending = job ?? (File.Exists(StatePath) ? JsonUtility.FromJson<Job>(File.ReadAllText(StatePath)) : null);
        bool terminal = pending == null || pending.phase == "complete" || pending.phase == "failed";
        bool untouched = pending != null && (pending.phase == "accepted" || pending.phase == "upgrading") && !pending.moved &&
            pending.upgradedMaterials == 0 && (pending.upgrades == null || pending.upgrades.Count == 0) &&
            (pending.upgradeIssues == null || pending.upgradeIssues.Count == 0);
        if (!terminal && !untouched)
            refusal = "Preserving an already-progressed headless job; import-only exit cannot interrupt mutations or later phases.";
        if (refusal == null && File.Exists(Receipt(marker.nonce))) refusal = "Import-only nonce was already consumed; inspect the previous result.";
        if (refusal != null)
        {
            WriteJson(Path.Combine(Work, "import-only-refused.json"), new Status { status = "import-only-refused", command = "import-only",
                nonce = marker != null ? marker.nonce : null, updatedUtc = Utc(), error = refusal });
            File.Move(ImportOnlyPath, Path.Combine(Work, "import-only-refused-" + Guid.NewGuid().ToString("N") + ".json"));
            Debug.LogWarning(refusal);
            return false;
        }
        string token = Path.GetFileNameWithoutExtension(Receipt(marker.nonce));
        // Preserve untouched queued work before consuming only our own pipeline request.
        if (File.Exists(RequestPath))
        {
            var request = JsonUtility.FromJson<Request>(File.ReadAllText(RequestPath));
            var session = File.Exists(HeadlessPath) ? JsonUtility.FromJson<HeadlessSession>(File.ReadAllText(HeadlessPath)) : null;
            if (request == null || session == null || request.nonce != session.nonce ||
                !string.Equals(session.projectPath, Project, StringComparison.OrdinalIgnoreCase))
            {
                WriteJson(Path.Combine(Work, "import-only-refused.json"), new Status { status = "import-only-refused", command = "import-only",
                    nonce = marker.nonce, updatedUtc = Utc(), error = "Preserving a request not owned by this headless session." });
                File.Move(ImportOnlyPath, Path.Combine(Work, "import-only-refused-" + Guid.NewGuid().ToString("N") + ".json"));
                return false;
            }
            File.Move(RequestPath, Path.Combine(Work, "import-only-deferred-request-" + token + ".json"));
        }
        if (!terminal) WriteJson(Path.Combine(Work, "import-only-deferred-job-" + token + ".json"), pending);
        if (File.Exists(HeadlessPath))
            File.Copy(HeadlessPath, Path.Combine(Work, "import-only-deferred-session-" + token + ".json"), false);
        string stamp = Utc();
        headless = new HeadlessSession { projectPath = Project, nonce = marker.nonce, command = "import-only", active = false,
            startedUtc = stamp, completedUtc = stamp, status = "complete", exitCode = 0,
            validationPath = null, previewsPath = null, fallbackPath = null };
        job = new Job { nonce = marker.nonce, command = "import-only", phase = "complete", startedUtc = stamp };
        WriteJson(Receipt(marker.nonce), marker);
        SaveJob(); WriteJson(HeadlessPath, headless); WriteJson(Path.Combine(Work, "headless-result.json"), headless);
        File.Delete(ImportOnlyPath);
        WriteStatus("import-only-complete");
        Debug.Log("Yamyam isolated import-only marker consumed; no material/fallback/validation/preview job was run. Exit=0; nonce=" + marker.nonce);
        EditorApplication.Exit(0);
        return true;
    }
    static bool FinishOwnTerminalHeadlessBeforeBusy()
    {
        // Optional Search indexing may keep isUpdating true after our job ends.
        // A terminal persisted job performs no further asset work before normal exit.
        if (!CanRunHeadless()) return false;
        ResumeHeadless();
        if (headless == null || !headless.active) return false;
        if (job == null && !terminalHeadlessStateLoaded)
        {
            terminalHeadlessStateLoaded = true;
            if (File.Exists(StatePath))
            {
                var saved = JsonUtility.FromJson<Job>(File.ReadAllText(StatePath));
                if (saved != null && saved.nonce == headless.nonce) job = saved;
            }
        }
        if (job == null || job.nonce != headless.nonce || job.phase != "failed" && job.phase != "complete") return false;
        FinishHeadlessIfReady();
        return true;
    }
    static bool HasReferenceId(SerializedProperty property)
    {
        if (ReferenceIdProperty == null) return false;
        object id = ReferenceIdProperty.GetValue(property);
        return id != null && !id.Equals(Activator.CreateInstance(ReferenceIdProperty.PropertyType));
    }
    static bool IsBuiltInGuid(string guid)
    { return Regex.IsMatch(guid, "^0{16}[d-fD-F]0{15}$"); }
    static bool TextureReferenceResolves(string path, string localId)
    {
        if (string.IsNullOrEmpty(path)) return false;
        Type type = AssetDatabase.GetMainAssetTypeAtPath(path);
        if (type != null && typeof(Texture).IsAssignableFrom(type)) return true; // Metadata check avoids decoding another texture.
        long expected;
        if (!long.TryParse(localId, out expected)) return false;
        foreach (var asset in AssetDatabase.LoadAllAssetsAtPath(path).OfType<Texture>())
        {
            string guid; long actual;
            if (AssetDatabase.TryGetGUIDAndLocalFileIdentifier(asset, out guid, out actual) && actual == expected) return true;
        }
        return false;
    }

    static void NoteHeavyLoad(int units)
    {
        heavyLoads += units;
        if (heavyLoads >= 128 || heavyLoads >= 16 && UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong() >= 4L * 1024 * 1024 * 1024)
            collectMemory = true;
    }
    static void CollectHeadlessMemoryIfNeeded()
    {
        // Global cache collection is confined to our disposable batch project. It never runs
        // in the user's interactive project, and only after all current asset/preview calls return.
        if (!collectMemory || !CanRunHeadless() || headless == null || !headless.active || Busy()) return;
        collectMemory = false;
        var evidence = new MemoryRecord { utc = Utc(), phase = job != null ? job.phase : null,
            collection = ++collectionCount, heavyLoadUnits = heavyLoads,
            beforeBytes = UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong() };
        GC.Collect(); GC.WaitForPendingFinalizers();
        EditorUtility.UnloadUnusedAssetsImmediate(true); // Retain valid managed/static/scene roots.
        GC.Collect();
        evidence.afterBytes = UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong();
        heavyLoads = 0; memoryEvidence.Add(evidence);
        WriteJson(Path.Combine(Work, "memory-collections.json"), new MemoryReport { collections = memoryEvidence });
    }
    [Serializable] public class MemoryReport { public List<MemoryRecord> collections; }

    static string Hierarchy(Transform transform)
    {
        string name = transform.name;
        while (transform.parent) { transform = transform.parent; name = transform.name + "/" + name; }
        return name;
    }
    static string Identity(string path, Object asset)
    {
        string guid; long local;
        return AssetDatabase.TryGetGUIDAndLocalFileIdentifier(asset, out guid, out local) ? guid + ":" + local : path + ":" + asset.GetType().Name + ":" + asset.name;
    }
    static void RequireRoot()
    { if (!Directory.Exists(Destination)) throw new DirectoryNotFoundException("Imported asset root is missing: " + Destination); }
    static void AssertAssetPath(string path)
    { if (!path.StartsWith(AssetsRoot + "/", StringComparison.Ordinal)) throw new IOException("Asset is outside the owned library: " + path); }
    static void AssertContained(string path, string parent)
    {
        if (!Path.GetFullPath(path).StartsWith(Path.GetFullPath(parent).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new IOException("Path escaped the expected library subtree: " + path);
    }
    static void Progress(string status)
    {
        if (EditorApplication.timeSinceStartup - lastProgress < 2) return;
        lastProgress = EditorApplication.timeSinceStartup;
        SaveJob(); WriteStatus(status);
    }
    static void SaveJob() { job.updatedUtc = Utc(); WriteJson(StatePath, job); }
    static void WriteStatus(string status, string error = null)
    {
        WriteJson(StatusPath, new Status { status = status, nonce = job != null ? job.nonce : null,
            command = job != null ? job.command : null, phase = job != null ? job.phase : null,
            updatedUtc = Utc(), unityVersion = Application.unityVersion, error = error,
            rootExists = Directory.Exists(Destination), stagingExists = Directory.Exists(Stage),
            compiling = EditorApplication.isCompiling, updating = EditorApplication.isUpdating,
            playing = EditorApplication.isPlayingOrWillChangePlaymode, processed = cursor,
            total = paths != null ? paths.Length : manifest != null && manifest.products != null ? manifest.products.Length : 0,
            upgradedMaterials = job != null ? job.upgradedMaterials : 0 });
    }
    static string Receipt(string nonce)
    {
        using (var hash = SHA256.Create())
            return Path.Combine(Work, "receipts", BitConverter.ToString(hash.ComputeHash(Encoding.UTF8.GetBytes(nonce))).Replace("-", "").ToLowerInvariant() + ".json");
    }
    static bool TransientJsonWriteException(Exception exception, Func<bool> safeReplaceState = null)
    {
        if (!(exception is IOException) && !(exception is UnauthorizedAccessException)) return false;
        int code = exception.HResult & 0xffff;
        if (code == 5 || code == 32 || code == 33) return true;
        // ReplaceFileW1175 preserves both original filenames. Unity Mono reports
        // this for a locked target.1176/1177 describe partial states and are not retried.
        return code == 1175 && safeReplaceState != null && safeReplaceState();
    }
    static void RetryTransientJsonWrite(Action operation, Action<int> wait = null, Func<bool> safeReplaceState = null)
    {
        int[] delays = { 25, 50, 100, 200, 400, 800, 1000 };
        for (int attempt = 0; ; attempt++)
        {
            try { operation(); return; }
            catch (Exception exception) when (TransientJsonWriteException(exception, safeReplaceState) && attempt < delays.Length)
            {
                if (wait != null) wait(delays[attempt]); else System.Threading.Thread.Sleep(delays[attempt]);
            }
        }
    }
    static void WriteJson(string path, object value)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path));
        string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            byte[] bytes = new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(value, true));
            using (var output = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            { output.Write(bytes, 0, bytes.Length); output.Flush(true); }
            RetryTransientJsonWrite(() =>
            {
                if (File.Exists(path)) File.Replace(temporary, path, null);
                else File.Move(temporary, path);
            }, safeReplaceState: () => File.Exists(path) && File.Exists(temporary));
        }
        finally
        {
            if (File.Exists(temporary))
                try { RetryTransientJsonWrite(() => File.Delete(temporary)); }
                catch (Exception exception) { Debug.LogWarning("Could not clean owned JSON temporary file: " + temporary + "; " + exception.Message); }
        }
    }
    static string Unwrap(Exception exception)
    { return (exception is TargetInvocationException && exception.InnerException != null ? exception.InnerException : exception).ToString(); }
    static void Fail(Exception exception)
    {
        Directory.CreateDirectory(Work);
        if (File.Exists(RequestPath))
        {
            string rejected = Path.Combine(Work, "rejected-request-" + DateTime.UtcNow.ToString("yyyyMMddHHmmssfff") + ".json");
            File.Move(RequestPath, rejected); // Consume malformed input once; never spin on it.
        }
        if (CanRunHeadless() && headless != null && headless.active && (job == null || job.nonce != headless.nonce))
            job = new Job { nonce = headless.nonce, command = string.IsNullOrEmpty(headless.command) ? "finalize" : headless.command, startedUtc = headless.startedUtc };
        if (job != null) { job.phase = "failed"; job.error = Unwrap(exception); SaveJob(); }
        WriteStatus("failed", Unwrap(exception));
        ResetSession(); Debug.LogException(exception);
    }
    static void ResetSession()
    {
        paths = null; cursor = 0; report = null; upgraders = null;
        clips.Clear(); materials.Clear(); shaderCounts.Clear(); sceneScriptReferences.Clear(); lastProgress = 0;
        offlineBinaryEvidenceLoaded = false; offlineBinaryEvidenceError = null; offlineBinaryEvidenceSha256 = null;
        terminalHeadlessStateLoaded = false;
        offlineBinaryEvidence = null; offlineBinaryScenes.Clear(); offlineBinaryScenesChecked.Clear();
        manifest = null; previewReport = null; previewCursor = 0; fallbackStarted = false;
        collectMemory = true;
    }
}
