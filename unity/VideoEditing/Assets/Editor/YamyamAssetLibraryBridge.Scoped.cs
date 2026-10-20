using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;

public static partial class YamyamAssetLibraryBridge
{
    [Serializable] public sealed class ScopedFile { public string path, sha256, metadataSha256, guid; public long bytes; }
    [Serializable] public sealed class ScopedInput {
        public int schemaVersion;
        public string nonce, expectedUnityVersion, compiledAckSha256, compiledAckNotBeforeUtc;
        public ScopedFile[] files;
        public string[] previewPaths;
    }
    [Serializable] public sealed class ScopedValidationReport {
        public int schemaVersion = 1, selectedFilesVerifiedBefore, selectedFilesVerifiedAfter, requestedFiles, dependencyClosureFiles, observedUnityErrors;
        public string status = "validating", nonce, startedUtc, completedUtc, inputPath, inputSha256, compiledAckSha256, compiledAckUtc, unityVersion, runDirectory;
        public string scope = "Exactly hash-bound918 post-import YAML payloads plus owned recursive native dependencies; existing hierarchy/script/material/shader/texture/dependency checks. Scenes are never opened. Source TerrainData/other non-script scene content and artistic/runtime equivalence are outside these checks; previously documented source limitations remain separate.";
        public bool scenesOpened, assetsSaved, materialsUpgraded, canonicalPreviewsModified;
        public string[] requestedPaths, inspectedPaths;
        public Report validation;
        public List<PreviewRecord> previews = new List<PreviewRecord>();
        public List<string> errors = new List<string>();
    }
    static ScopedInput scopedInput;
    static ScopedValidationReport scopedReport;
    static Application.LogCallback scopedLogCapture;

    static void ScopedNoLinks(string path, string boundary)
    {
        string full = Path.GetFullPath(path), root = Path.GetFullPath(boundary);
        if (!full.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new IOException("Scoped path escaped its fixed owned boundary.");
        for (string current = full; !string.IsNullOrEmpty(current); current = Path.GetDirectoryName(current)) {
            try { if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0) throw new IOException("Scoped path has a reparse ancestor."); }
            catch (FileNotFoundException) { } catch (DirectoryNotFoundException) { }
            if (current.Equals(Path.GetPathRoot(full), StringComparison.OrdinalIgnoreCase)) return;
        }
        throw new IOException("Scoped ancestor walk failed.");
    }
    static string ScopedSha(string path) { using (var stream = File.OpenRead(path)) using (var sha = SHA256.Create()) return Hex(sha.ComputeHash(stream)); }
    static string ScopedAssetAbsolute(string path)
    {
        if (string.IsNullOrEmpty(path) || !path.StartsWith(AssetsRoot + "/", StringComparison.Ordinal) || path.Contains("\\") || path.IndexOf(':') >= 0 ||
            path.Split('/').Any(part => part.Length == 0 || part == "." || part == "..") || path.EndsWith(".meta", StringComparison.OrdinalIgnoreCase))
            throw new IOException("Scoped asset path is outside the owned root or not a payload.");
        string absolute = Path.GetFullPath(Path.Combine(Project, path)); ScopedNoLinks(absolute, Destination); return absolute;
    }
    static void VerifyScopedFiles()
    {
        foreach (var input in scopedInput.files) {
            string absolute = ScopedAssetAbsolute(input.path); ScopedNoLinks(absolute + ".meta", Destination);
            if (!Regex.IsMatch(input.sha256 ?? "", "^[a-f0-9]{64}$") || !Regex.IsMatch(input.metadataSha256 ?? "", "^[a-f0-9]{64}$") ||
                !Regex.IsMatch(input.guid ?? "", "^[a-f0-9]{32}$") || new YamyamAssetLibraryIO.Info(absolute).Length != input.bytes || ScopedSha(absolute) != input.sha256 || ScopedSha(absolute + ".meta") != input.metadataSha256)
                throw new InvalidDataException("Scoped payload/meta exact hash or size changed: " + input.path);
            string text = File.ReadAllText(absolute);
            if (!text.TrimStart('\uFEFF').StartsWith("%YAML ", StringComparison.Ordinal)) throw new InvalidDataException("Scoped payloads, including scenes, must be actual YAML: " + input.path);
            if (AssetDatabase.AssetPathToGUID(input.path) != input.guid || !Regex.IsMatch(File.ReadAllText(absolute + ".meta"), @"(?m)^guid:[ \t]*" + input.guid + @"[ \t]*\r?$"))
                throw new InvalidDataException("Scoped native/meta GUID identity changed: " + input.path);
        }
    }
    static void VerifyScopedContext()
    {
        string inputPath = Path.Combine(Work, "scoped-validation-input.json"); ScopedNoLinks(inputPath, Work);
        if (!Regex.IsMatch(job.scopedInputSha256 ?? "", "^[a-f0-9]{64}$") || ScopedSha(inputPath) != job.scopedInputSha256)
            throw new InvalidDataException("Scoped input changed after the SHA was persisted in the request/job.");
        string ackPath = Path.Combine(Work, "compiled.json"); ScopedNoLinks(ackPath, Work);
        if (!Regex.IsMatch(scopedInput.compiledAckSha256 ?? "", "^[a-f0-9]{64}$") || ScopedSha(ackPath) != scopedInput.compiledAckSha256)
            throw new InvalidDataException("Current compiled acknowledgement differs from the scoped input.");
        var ack = JsonUtility.FromJson<Status>(File.ReadAllText(ackPath)); DateTime earliest, actual;
        if (ack == null || ack.status != "compiled" || ack.unityVersion != "6000.6.0f1" || !string.IsNullOrEmpty(ack.error) || ack.compiling || ack.updating || ack.playing ||
            !DateTime.TryParse(scopedInput.compiledAckNotBeforeUtc, null, System.Globalization.DateTimeStyles.RoundtripKind, out earliest) ||
            !DateTime.TryParse(ack.updatedUtc, null, System.Globalization.DateTimeStyles.RoundtripKind, out actual) || actual.ToUniversalTime() < earliest.ToUniversalTime() || actual.ToUniversalTime() > DateTime.UtcNow)
            throw new InvalidDataException("Fresh exact-version successful compiled acknowledgement is required.");
        scopedReport.compiledAckSha256 = scopedInput.compiledAckSha256; scopedReport.compiledAckUtc = ack.updatedUtc;
    }
    static void PersistScopedReport()
    {
        if (scopedReport == null) return;
        scopedReport.validation = report;
        WriteJson(Path.Combine(scopedReport.runDirectory, "report.json"), scopedReport);
        WriteJson(Path.Combine(Work, "scoped-validation-report.json"), scopedReport);
    }
    static void ValidateScopedChunk()
    {
        RequireRoot();
        try {
            if (scopedReport == null) {
                string inputPath = Path.Combine(Work, "scoped-validation-input.json"); ScopedNoLinks(inputPath, Work);
                if (!Regex.IsMatch(job.scopedInputSha256 ?? "", "^[a-f0-9]{64}$") || ScopedSha(inputPath) != job.scopedInputSha256) throw new InvalidDataException("Scoped input SHA changed.");
                scopedInput = JsonUtility.FromJson<ScopedInput>(File.ReadAllText(inputPath));
                if (scopedInput == null || scopedInput.schemaVersion != 1 || scopedInput.nonce != job.nonce || scopedInput.expectedUnityVersion != Application.unityVersion || Application.unityVersion != "6000.6.0f1" ||
                    scopedInput.files == null || scopedInput.files.Length != 918 || scopedInput.files.Any(value => value == null) || scopedInput.files.Select(value => value.path).Distinct(StringComparer.OrdinalIgnoreCase).Count() != 918)
                    throw new InvalidDataException("Exactly918 unique nonce/version-bound YAML payloads are required.");
                report = new Report { nonce = job.nonce, unityVersion = Application.unityVersion, validationScope = "Post-import exact918 YAML payloads and their owned recursive native dependency closure; scenes never opened. This is separate from the earlier full isolated validation." };
                string token; using (var sha = SHA256.Create()) token = Hex(sha.ComputeHash(Encoding.UTF8.GetBytes(job.nonce)));
                scopedReport = new ScopedValidationReport { nonce = job.nonce, startedUtc = Utc(), unityVersion = Application.unityVersion, inputPath = inputPath, inputSha256 = job.scopedInputSha256,
                    requestedFiles = 918, requestedPaths = scopedInput.files.Select(value => value.path).OrderBy(value => value, StringComparer.Ordinal).ToArray(), runDirectory = Path.Combine(Work, "scoped-validation", token) };
                ScopedNoLinks(scopedReport.runDirectory, Work);
                scopedLogCapture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { scopedReport.observedUnityErrors++; scopedReport.errors.Add(message); } };
                Application.logMessageReceived += scopedLogCapture;
                VerifyScopedContext(); VerifyScopedFiles(); scopedReport.selectedFilesVerifiedBefore = 918;
                paths = AssetDatabase.GetDependencies(scopedReport.requestedPaths, true).Concat(scopedReport.requestedPaths)
                    .Where(value => value.StartsWith(AssetsRoot + "/", StringComparison.Ordinal) && !AssetDatabase.IsValidFolder(value)).Distinct(StringComparer.OrdinalIgnoreCase).OrderBy(value => value, StringComparer.Ordinal).ToArray();
                if (paths.Length < 918) throw new InvalidDataException("Scoped native closure omitted a requested path.");
                foreach (string path in paths) {
                    string absolute = ScopedAssetAbsolute(path);
                    if (path.EndsWith(".unity", StringComparison.OrdinalIgnoreCase) && !File.ReadAllText(absolute).TrimStart('\uFEFF').StartsWith("%YAML ", StringComparison.Ordinal))
                        throw new InvalidDataException("Scoped native closure contains an unsupported binary scene: " + path);
                }
                scopedReport.dependencyClosureFiles = paths.Length; scopedReport.inspectedPaths = paths;
                Directory.CreateDirectory(scopedReport.runDirectory); File.Copy(inputPath, Path.Combine(scopedReport.runDirectory, "input.json"), false);
                WriteStatus("validating-scoped"); PersistScopedReport();
            }
            double deadline = EditorApplication.timeSinceStartup + .1;
            while (cursor < paths.Length && EditorApplication.timeSinceStartup < deadline) {
                string path = paths[cursor++];
                try {
                    InspectAsset(path);
                    string extension = Path.GetExtension(path).ToLowerInvariant();
                    if ((extension == ".asset" || extension == ".lighting") && scopedReport.requestedPaths.Contains(path)) {
                        if (!AssetDatabase.LoadMainAssetAtPath(path)) throw new InvalidDataException("Scoped native asset did not load.");
                        InspectSceneScripts(path); // Reuse explicit YAML m_Script resolution; never opens a scene.
                    }
                } catch (Exception error) { report.unreadableAssets++; report.issues.Add(new Issue(path, "asset-inspection-error", Unwrap(error))); }
            }
            Progress("validating-scoped"); if (cursor < paths.Length) return;
            InspectDependencyClosure();
            VerifyScopedContext(); VerifyScopedFiles(); scopedReport.selectedFilesVerifiedAfter = 918;
            if (scopedInput.previewPaths != null) {
                if (scopedInput.previewPaths.Length != 0 && scopedInput.previewPaths.Length != 2) throw new InvalidDataException("Optional scoped previews must be exactly two selected native objects.");
                foreach (string path in scopedInput.previewPaths) {
                    ScopedAssetAbsolute(path); if (!paths.Contains(path) || !(path.EndsWith(".prefab", StringComparison.OrdinalIgnoreCase) || AssetImporter.GetAtPath(path) is ModelImporter)) throw new InvalidDataException("Optional preview is outside the inspected closure or not a model/prefab.");
                    var asset = AssetDatabase.LoadAssetAtPath<GameObject>(path); if (!asset) throw new InvalidDataException("Optional preview object did not load.");
                    Bounds bounds; var draws = Draws(asset, out bounds); if (draws.Count == 0) throw new InvalidDataException("Optional preview has no actual mesh draws.");
                    var preview = new PreviewRecord { id = path.Substring(AssetsRoot.Length + 1).Split('/')[0].Substring(0, 3), title = Path.GetFileNameWithoutExtension(path), assetPath = path,
                        imagePath = Path.Combine(scopedReport.runDirectory, "preview-" + scopedReport.previews.Count.ToString("D2") + ".png"), sourceSelectionReason = "Explicitly selected scoped native object; separate QA output, no canonical promotion." };
                    RenderPreview(draws, bounds, preview); scopedReport.previews.Add(preview);
                    if (!string.IsNullOrEmpty(preview.error)) throw new InvalidDataException("Optional scoped preview failed: " + preview.error);
                }
                VerifyScopedContext(); VerifyScopedFiles();
            }
            report.assetFiles = paths.Length; report.animationClips = clips.Count; report.shaders = shaderCounts.OrderBy(value => value.Key).Select(value => new ShaderCount { shader = value.Key, count = value.Value }).ToList();
            report.completedUtc = Utc(); report.status = report.missingMonoScripts + report.missingTextureReferences + report.missingShaders + report.unsupportedShaders + report.shaderCompileErrors + report.unreadableAssets + report.externalAssetDependencyCount + scopedReport.observedUnityErrors == 0 ? "pass" : "completed-with-issues";
            scopedReport.status = report.status; scopedReport.completedUtc = report.completedUtc; PersistScopedReport();
            job.phase = "complete"; SaveJob(); WriteStatus(report.status); ResetSession();
        } catch (Exception error) {
            if (scopedReport != null) { scopedReport.status = "failed"; scopedReport.completedUtc = Utc(); scopedReport.errors.Add(Unwrap(error)); PersistScopedReport(); }
            throw;
        }
    }
    static void ResetScopedValidation()
    {
        if (scopedLogCapture != null) Application.logMessageReceived -= scopedLogCapture;
        scopedLogCapture = null; scopedInput = null; scopedReport = null;
    }
}
