// Explicit isolated repair of generated raw-image importer shape, never vendor settings.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
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

public static class YamyamAssetLibraryTexture2D
{
    const string ExpectedProject = "D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string Root = "Assets/ThirdParty/YamyamAssetLibrary";
    const string ExpectedPlanSha256 = "e7d1a8cb6bd848ba4a716a916adc01aaab6c921d644858f007d642c1d817a78b";
    const string ExpectedPathsSha256 = "5b3aaa54504692ff744b8b45cd68001e0f59b301ea43887c4a76313df588a372";
    const string FailedRun = "20261019T1319288477672Z-d8ca0de59c624435a401711e94f3e906";
    const string FailedReportSha256 = "470844fe83b30c76d1010c111c862c25794c9b97b2048106c330d8f06a027bf0";
    static readonly HashSet<string> RasterExtensions = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { ".png", ".jpg", ".jpeg", ".tga", ".tif", ".tiff", ".bmp", ".psd", ".dds", ".hdr", ".exr", ".gif" };
    static readonly Regex GuidLine = new Regex(@"(?m)^guid:[ \t]*([a-fA-F0-9]{32})[ \t]*\r?$");
    [Serializable] public sealed class Source { public string kind; }
    [Serializable] public sealed class Record { public string path, sha256, guid; public long bytes; public Source source; }
    [Serializable] public sealed class Product { public string id, folder, status; public Record[] files; }
    [Serializable] public sealed class Manifest { public string stageRoot, targetAssetRoot; public Product[] products; }
    [Serializable] public sealed class Candidate
    {
        public string productId, path, assetPath, canonicalPayloadSha256, headerSha256, format, metadataPath, guid;
        public string canonicalMetadataSha256, actualMetadataSha256, metadataSourceKind, textureShape, classification;
        public long bytes, payloadBytesNow, canonicalMetadataBytes, actualMetadataBytes;
        public bool payloadSha256FreshlyRead, originalVendorImporterSettings;
    }
    [Serializable] public sealed class Plan
    {
        public int schemaVersion, imagesChecked, selectedRaw2DShapeCorrections, requiresReview;
        public string kind, manifestPath, manifestSha256, stageRoot, targetAssetRoot, selectedPathSetSha256;
        public bool readOnlyAssetInspection, actualAssetsModified, unityLaunched, sourceArchivesModified;
        public Candidate[] candidates;
    }
    [Serializable] public sealed class Result
    {
        public string productId, path, guid, payloadBeforeSha256, payloadAfterSha256, metadataBeforeSha256, metadataAfterSha256;
        public string beforeType, afterType, settingsBeforePath, settingsAfterPath, backupMetadata, otherSettingsBeforeSha256, otherSettingsAfterSha256;
        public long bytes, localIdBefore, localIdAfter;
        public int width, height;
        public bool importStarted, complete, resumedPreviouslyComplete, settingsPersisted;
        public double elapsedSeconds;
    }
    [Serializable] public sealed class Setting { public string path, type, value; }
    [Serializable] public sealed class Settings { public List<Setting> values = new List<Setting>(); }
    [Serializable] public sealed class Report
    {
        public int schemaVersion = 1, candidates = 200, completed, observedUnityErrors, observedUnityWarnings;
        public string status = "checking", project, runDirectory, startedUtc, completedUtc, manifestSha256, planSha256, pathSetSha256;
        public string previousFailedReport, previousFailedReportSha256;
        public int previousFailedObservedUnityErrors, shapeSettingsChanged, synchronousVerificationImports;
        public bool apply = true, originalArchivesModified, vendorImporterSettingsModified, scenesOpened, allSettingsPersistedBeforeImportFlush, importFlushStarted, importFlushCompleted;
        public double elapsedSeconds;
        public List<Result> results = new List<Result>();
        public List<string> errors = new List<string>();
        public List<string> warnings = new List<string>();
        public string scope = "Only200 exact reviewed raw2D images with generated-stable-meta provenance. The exact one-complete failed run is verified, never accepted as success. All199 remaining shape settings are persisted while StartAssetEditing pauses imports, then the complete200-image set is queued before StopAssetEditing. No texture or model asset is loaded until after the flush. Payload/GUID and all other importer settings must remain unchanged; dependent generated materials/prefabs are built after this phase.";
    }
    static string Project { get { return YamyamAssetLibraryIO.NormalPath(Path.GetDirectoryName(Application.dataPath)); } }
    static string Work { get { return YamyamAssetLibraryIO.NormalPath(Path.Combine(Project, "..")); } }
    static string Absolute(string path) { return Path.Combine(Project, path.Replace('/', Path.DirectorySeparatorChar)); }
    static string Utc() { return DateTime.UtcNow.ToString("o"); }
    static string Hex(byte[] value) { return BitConverter.ToString(value).Replace("-", "").ToLowerInvariant(); }
    static string HashFile(string path) { using (var input = File.OpenRead(path)) using (var hash = SHA256.Create()) return Hex(hash.ComputeHash(input)); }
    static string HashText(string text) { using (var hash = SHA256.Create()) return Hex(hash.ComputeHash(Encoding.UTF8.GetBytes(text))); }
    static void Guard()
    {
        if (!Application.isBatchMode || !string.Equals(Project.Replace('\\', '/'), ExpectedProject, StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Texture2D correction requires the exact isolated batch project.");
    }
    static void NoLinks(string path)
    {
        string full = YamyamAssetLibraryIO.NormalPath(path), boundary = Work;
        if (!full.Equals(boundary, StringComparison.OrdinalIgnoreCase) && !full.StartsWith(boundary + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("Path escaped the owned workspace.");
        for (string current = full; !string.IsNullOrEmpty(current); current = Path.GetDirectoryName(current)) {
            try { if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0) throw new IOException("Reparse point refused: " + current); }
            catch (FileNotFoundException) { } catch (DirectoryNotFoundException) { }
            // Check ancestors above Work too: a junction on Library/main project
            // must not turn an apparently owned path into a foreign write.
            if (current.Equals(Path.GetPathRoot(full), StringComparison.OrdinalIgnoreCase)) return;
        }
        throw new IOException("Owned path boundary not reached.");
    }
    static void SafeRelative(string value)
    {
        if (string.IsNullOrEmpty(value) || value.Contains("\\") || value.StartsWith("/", StringComparison.Ordinal) || value.Contains(":")) throw new InvalidDataException("Unsafe relative image path.");
        if (value.Split('/').Any(part => part == "" || part == "." || part == ".." || part.IndexOf('\0') >= 0)) throw new InvalidDataException("Unsafe image path component.");
    }
    static void ValidatePlan(Plan plan)
    {
        if (plan == null || plan.schemaVersion != 1 || plan.kind != "generated-raw-2d-texture-shape-audit" || !plan.readOnlyAssetInspection || plan.actualAssetsModified || plan.unityLaunched || plan.sourceArchivesModified
            || plan.imagesChecked != 200 || plan.selectedRaw2DShapeCorrections != 200 || plan.requiresReview != 0 || plan.candidates == null || plan.candidates.Length != 200 || plan.selectedPathSetSha256 != ExpectedPathsSha256)
            throw new InvalidDataException("Only the exact reviewed200-image plan is accepted.");
        var paths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (Candidate item in plan.candidates) {
            SafeRelative(item.path); SafeRelative(item.metadataPath);
            if (!paths.Add(item.path) || item.assetPath != Root + "/" + item.path || item.metadataPath != item.path + ".meta" || item.classification != "raw-2d-raster" || item.textureShape != "2"
                || item.metadataSourceKind != "generated-stable-meta" || item.originalVendorImporterSettings || item.bytes < 1 || item.actualMetadataBytes < 1
                || !(item.format == "PNG" || item.format == "JPEG") || !Regex.IsMatch(item.guid ?? "", "^[a-f0-9]{32}$"))
                throw new InvalidDataException("Unreviewed, duplicate or vendor image importer target: " + item.path);
        }
        string joined = string.Join("\n", plan.candidates.Select(item => item.path).OrderBy(path => path, StringComparer.Ordinal));
        if (HashText(joined) != ExpectedPathsSha256) throw new InvalidDataException("Exact reviewed image path set changed.");
    }
    static byte[] Header(string path)
    {
        byte[] buffer = new byte[128]; int count = 0;
        using (var input = File.OpenRead(path)) { while (count < buffer.Length) { int read = input.Read(buffer, count, buffer.Length - count); if (read == 0) break; count += read; } }
        return buffer.Take(count).ToArray();
    }
    static string HashBytes(byte[] bytes) { using (var hash = SHA256.Create()) return Hex(hash.ComputeHash(bytes)); }
    static string ReadGuid(string path)
    {
        Match match = GuidLine.Match(File.ReadAllText(path));
        if (!match.Success) throw new InvalidDataException("Image metadata has no GUID."); return match.Groups[1].Value.ToLowerInvariant();
    }
    static bool IsExcludedSetting(string path)
    {
        string first = path.Split('.')[0];
        // m_Output is derived import instructions/diagnostics, not a setting.
        return first == "m_TextureShape" || first == "m_UsedFileIDs" || first == "m_Output" || first == "m_ObjectHideFlags"
            || first == "m_CorrespondingSourceObject" || first == "m_PrefabInstance" || first == "m_PrefabAsset" || first == "m_Name"
            || first == "m_AssetPath" || first == "m_AssetTimeStamp" || first == "m_ImportTimeStamp";
    }
    static string Numbers(params float[] values) { return string.Join(",", values.Select(value => value.ToString("R", CultureInfo.InvariantCulture))); }
    static string SettingValue(SerializedProperty property)
    {
        switch (property.propertyType) {
            case SerializedPropertyType.Integer: return property.longValue.ToString(CultureInfo.InvariantCulture);
            case SerializedPropertyType.Boolean: return property.boolValue ? "true" : "false";
            case SerializedPropertyType.Float: return property.doubleValue.ToString("R", CultureInfo.InvariantCulture);
            case SerializedPropertyType.String: return property.stringValue;
            case SerializedPropertyType.Enum: case SerializedPropertyType.ArraySize: case SerializedPropertyType.Character: case SerializedPropertyType.LayerMask: return property.intValue.ToString(CultureInfo.InvariantCulture);
            case SerializedPropertyType.Color: var c = property.colorValue; return Numbers(c.r, c.g, c.b, c.a);
            case SerializedPropertyType.Vector2: var v2 = property.vector2Value; return Numbers(v2.x, v2.y);
            case SerializedPropertyType.Vector3: var v3 = property.vector3Value; return Numbers(v3.x, v3.y, v3.z);
            case SerializedPropertyType.Vector4: var v4 = property.vector4Value; return Numbers(v4.x, v4.y, v4.z, v4.w);
            case SerializedPropertyType.Rect: var rect = property.rectValue; return Numbers(rect.x, rect.y, rect.width, rect.height);
            case SerializedPropertyType.ObjectReference:
                var value = property.objectReferenceValue; if (value == null) return "null";
                string guid; long localId;
                if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value, out guid, out localId)) throw new InvalidDataException("An importer setting has no persistent reference identity.");
                return guid + ":" + localId.ToString(CultureInfo.InvariantCulture) + ":" + value.GetType().FullName;
            default: throw new InvalidDataException("Unhandled texture importer setting: " + property.propertyPath + ":" + property.propertyType);
        }
    }
    static string OtherSettings(TextureImporter importer)
    {
        var result = new Settings();
        using (var serialized = new SerializedObject(importer))
        using (var property = serialized.GetIterator())
            while (property.Next(true))
                if (!IsExcludedSetting(property.propertyPath) && property.propertyType != SerializedPropertyType.Generic)
                    result.values.Add(new Setting { path = property.propertyPath, type = property.propertyType.ToString(), value = SettingValue(property) });
        result.values = result.values.OrderBy(value => value.path, StringComparer.Ordinal).ToList();
        return JsonUtility.ToJson(result, true);
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
    static void Run()
    {
        Guard(); if (Application.unityVersion != "6000.6.0f1" || EditorApplication.isCompiling || EditorApplication.isUpdating) throw new InvalidOperationException("Expected idle Unity6000.6.0f1.");
        NoLinks(Project);
        string local = Path.Combine(Project, "Library/YamyamAssetLibrary"), planPath = Path.Combine(Work, "generated-raw-2d-texture-shape-audit.json"), manifestPath = Path.Combine(Work, "staging-manifest.json");
        NoLinks(planPath); NoLinks(manifestPath);
        string run = Path.Combine(local, "texture2d-correction", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N")); NoLinks(run); Directory.CreateDirectory(run);
        string reportPath = Path.Combine(run, "report.json");
        var report = new Report { project = Project, runDirectory = run, startedUtc = Utc(), manifestSha256 = HashFile(manifestPath), planSha256 = HashFile(planPath), pathSetSha256 = ExpectedPathsSha256 };
        var watch = Stopwatch.StartNew();
        Application.LogCallback capture = (message, stack, type) => {
            if (type == LogType.Warning) { report.observedUnityWarnings++; if (report.warnings.Count < 256) report.warnings.Add(message); }
            else if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; if (report.errors.Count < 256) report.errors.Add("Unity: " + message); }
        };
        Application.logMessageReceived += capture;
        try {
            if (report.planSha256 != ExpectedPlanSha256) throw new InvalidDataException("Reviewed image audit SHA changed.");
            Plan plan = JsonUtility.FromJson<Plan>(File.ReadAllText(planPath)); ValidatePlan(plan);
            Manifest manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(manifestPath));
            if (report.manifestSha256 != plan.manifestSha256 || !string.Equals(YamyamAssetLibraryIO.NormalPath(plan.manifestPath), manifestPath, StringComparison.OrdinalIgnoreCase)
                || manifest.products == null || manifest.products.Length != 84 || manifest.products.Select(product => product.id).Distinct().Count() != 84 || manifest.products.Any(product => product.status != "complete")
                || manifest.targetAssetRoot != Root || !string.Equals(YamyamAssetLibraryIO.NormalPath(manifest.stageRoot), YamyamAssetLibraryIO.NormalPath(Absolute(Root)), StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("Image audit is stale or canonical84-product ownership/root differs.");
            var ownership = manifest.products.SelectMany(product => product.files.Select(record => new { product, record })).ToDictionary(item => item.record.path, StringComparer.Ordinal);
            var eligible = ownership.Values.Where(item => !item.record.path.EndsWith(".meta", StringComparison.OrdinalIgnoreCase) && RasterExtensions.Contains(Path.GetExtension(item.record.path))
                && ownership.ContainsKey(item.record.path + ".meta") && ownership[item.record.path + ".meta"].record.source != null && ownership[item.record.path + ".meta"].record.source.kind == "generated-stable-meta")
                .Select(item => item.record.path).OrderBy(path => path, StringComparer.Ordinal).ToArray();
            if (!eligible.SequenceEqual(plan.candidates.Select(item => item.path).OrderBy(path => path, StringComparer.Ordinal), StringComparer.Ordinal)) throw new InvalidDataException("Generated raster scope differs from the exact200-image plan.");
            // Preserve and bind the only previous mutation. The failed report
            // remains failed, including all native errors; it cannot be waived.
            string failedPath = Path.Combine(local, "texture2d-correction", FailedRun, "report.json"); NoLinks(failedPath);
            if (HashFile(failedPath) != FailedReportSha256) throw new InvalidDataException("The exact preserved failed run report changed.");
            var failed = JsonUtility.FromJson<Report>(File.ReadAllText(failedPath));
            if (failed.status != "failed" || failed.completed != 1 || failed.observedUnityErrors != 289 || failed.planSha256 != report.planSha256 || failed.manifestSha256 != report.manifestSha256 || failed.results == null || failed.results.Count != 200)
                throw new InvalidDataException("Resume requires the exact one-complete failed run, with its native errors preserved.");
            var priorRows = failed.results.ToDictionary(item => item.path, StringComparer.Ordinal);
            var priorComplete = failed.results.Where(item => item.complete).ToArray();
            if (priorComplete.Length != 1 || priorComplete[0].path != Root + "/007-kitchen-restaurant-megapack-unity-godot-fbx/Restourant/Textures/Kithcen.png"
                || priorComplete[0].payloadBeforeSha256 != priorComplete[0].payloadAfterSha256 || priorComplete[0].otherSettingsBeforeSha256 != priorComplete[0].otherSettingsAfterSha256)
                throw new InvalidDataException("The previous mutation does not have a complete payload/settings-preservation proof.");
            report.previousFailedReport = failedPath; report.previousFailedReportSha256 = FailedReportSha256; report.previousFailedObservedUnityErrors = failed.observedUnityErrors;
            // Complete preflight and all metadata backups before the first mutation.
            foreach (Candidate item in plan.candidates) {
                var body = ownership[item.path]; var meta = ownership[item.metadataPath];
                if (body.product.id != item.productId || meta.product.id != item.productId || !item.path.StartsWith(body.product.folder + "/", StringComparison.Ordinal)
                    || body.record.sha256 != item.canonicalPayloadSha256 || body.record.bytes != item.bytes || meta.record.sha256 != item.canonicalMetadataSha256
                    || meta.record.bytes != item.canonicalMetadataBytes || meta.record.guid != item.guid || meta.record.source == null || meta.record.source.kind != "generated-stable-meta"
                    || body.record.source == null || (body.record.source.kind != "archive-files" && body.record.source.kind != "nested-archive-files"))
                    throw new InvalidDataException("Generated image provenance/receipt changed: " + item.path);
                string path = Absolute(item.assetPath), metadata = path + ".meta"; NoLinks(path); NoLinks(metadata);
                Result prior;
                if (!priorRows.TryGetValue(item.assetPath, out prior) || prior.guid != item.guid || prior.payloadBeforeSha256 != item.canonicalPayloadSha256 || prior.metadataBeforeSha256 != item.actualMetadataSha256
                    || prior.importStarted != prior.complete) throw new InvalidDataException("The preserved failed preflight differs from the reviewed200-image plan.");
                string expectedMeta = prior.complete ? prior.metadataAfterSha256 : item.actualMetadataSha256;
                NoLinks(prior.backupMetadata);
                if (HashFile(prior.backupMetadata) != item.actualMetadataSha256) throw new InvalidDataException("The preserved original Cubemap metadata backup changed.");
                if (new FileInfo(path).Length != item.bytes || HashFile(path) != item.canonicalPayloadSha256 || HashFile(metadata) != expectedMeta
                    || HashBytes(Header(path)) != item.headerSha256 || ReadGuid(metadata) != item.guid || AssetDatabase.AssetPathToGUID(item.assetPath).ToLowerInvariant() != item.guid)
                    throw new InvalidDataException("Generated image actual payload/header/metadata/GUID differs from reviewed plan: " + item.path);
                var importer = AssetImporter.GetAtPath(item.assetPath) as TextureImporter;
                if (importer == null || importer.textureShape != (prior.complete ? TextureImporterShape.Texture2D : TextureImporterShape.TextureCube)
                    || AssetDatabase.GetMainAssetTypeAtPath(item.assetPath) != (prior.complete ? typeof(Texture2D) : typeof(Cubemap))) throw new InvalidDataException("Unexpected before-state image type/shape: " + item.path);
                string backup = Path.Combine(run, "metadata-backups", item.metadataPath); NoLinks(backup); Directory.CreateDirectory(Path.GetDirectoryName(backup));
                if (File.Exists(backup)) throw new IOException("Refusing to overwrite a metadata backup.");
                File.Copy(metadata, backup, false); if (HashFile(backup) != expectedMeta) throw new IOException("Metadata backup verification failed.");
                var result = new Result { productId = item.productId, path = item.assetPath, guid = item.guid, bytes = item.bytes, payloadBeforeSha256 = item.canonicalPayloadSha256, metadataBeforeSha256 = expectedMeta,
                    resumedPreviouslyComplete = prior.complete, localIdBefore = prior.complete ? prior.localIdAfter : 0, beforeType = prior.complete ? typeof(Texture2D).FullName : typeof(Cubemap).FullName,
                    backupMetadata = backup, settingsBeforePath = Path.Combine(run, "settings", item.guid + ".before.json"), settingsAfterPath = Path.Combine(run, "settings", item.guid + ".after.json") };
                Directory.CreateDirectory(Path.GetDirectoryName(result.settingsBeforePath)); File.WriteAllText(result.settingsBeforePath, EditorJsonUtility.ToJson(importer, true), new UTF8Encoding(false));
                string otherSettings = OtherSettings(importer); result.otherSettingsBeforeSha256 = HashText(otherSettings);
                if (result.otherSettingsBeforeSha256 != prior.otherSettingsBeforeSha256) throw new InvalidDataException("Preflight importer settings changed since the preserved failed run: " + item.path);
                File.WriteAllText(result.settingsBeforePath + ".semantic.json", otherSettings, new UTF8Encoding(false));
                report.results.Add(result);
            }
            if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity reported errors during image preflight; no shape was changed.");
            report.status = "staging-all-shapes"; SaveReport(reportPath, report);
            bool editing = false;
            try {
                AssetDatabase.StartAssetEditing(); editing = true;
                foreach (Result result in report.results) {
                    string metadata = Absolute(result.path) + ".meta";
                    if (HashFile(metadata) != result.metadataBeforeSha256) throw new IOException("Image metadata changed between preflight and paused settings staging: " + result.path);
                    var importer = AssetImporter.GetAtPath(result.path) as TextureImporter;
                    if (importer == null || importer.textureShape != (result.resumedPreviouslyComplete ? TextureImporterShape.Texture2D : TextureImporterShape.TextureCube)) throw new InvalidDataException("Image importer changed before settings staging.");
                    if (!result.resumedPreviouslyComplete) {
                        importer.textureShape = TextureImporterShape.Texture2D;
                        if (!AssetDatabase.WriteImportSettingsIfDirty(result.path)) throw new IOException("Changed image importer settings were not written: " + result.path);
                        report.shapeSettingsChanged++;
                    }
                    if (ReadGuid(metadata) != result.guid || !Regex.IsMatch(File.ReadAllText(metadata), @"(?m)^  textureShape:[ \t]*1[ \t]*\r?$")) throw new InvalidDataException("Texture2D shape/GUID was not persisted while imports were paused: " + result.path);
                    result.settingsPersisted = true; SaveReport(reportPath, report);
                }
                if (report.shapeSettingsChanged != 199 || report.results.Any(result => !result.settingsPersisted) || report.observedUnityErrors != 0) throw new InvalidDataException("All199 pending shapes must be written before any import flush.");
                report.allSettingsPersistedBeforeImportFlush = true; report.status = "all-settings-persisted"; SaveReport(reportPath, report);
                foreach (Result result in report.results) {
                    result.importStarted = true;
                    AssetDatabase.ImportAsset(result.path, ImportAssetOptions.ForceUpdate); // Queued while imports remain paused.
                }
                report.importFlushStarted = true; report.status = "flushing-imports"; SaveReport(reportPath, report);
            }
            finally { if (editing) AssetDatabase.StopAssetEditing(); }
            report.importFlushCompleted = true; report.status = "verifying"; SaveReport(reportPath, report);
            if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity reported errors while flushing the complete200-image import batch.");
            foreach (Result result in report.results) {
                var itemWatch = Stopwatch.StartNew(); string path = Absolute(result.path), metadata = path + ".meta";
                // Synchronize any pending artifact without forcing a second import.
                AssetDatabase.ImportAsset(result.path, ImportAssetOptions.ForceSynchronousImport); report.synchronousVerificationImports++;
                var importer = AssetImporter.GetAtPath(result.path) as TextureImporter;
                var actual = AssetDatabase.LoadMainAssetAtPath(result.path); var texture = actual as Texture2D;
                string guid; long afterLocalId;
                if (importer == null || importer.textureShape != TextureImporterShape.Texture2D || texture == null || actual is Cubemap || AssetDatabase.GetMainAssetTypeAtPath(result.path) != typeof(Texture2D)
                    || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(actual, out guid, out afterLocalId) || guid.ToLowerInvariant() != result.guid || texture.width < 1 || texture.height < 1)
                    throw new InvalidDataException("Official import did not produce a persistent Texture2D: " + result.path);
                result.afterType = actual.GetType().FullName; result.localIdAfter = afterLocalId; result.width = texture.width; result.height = texture.height;
                result.payloadAfterSha256 = HashFile(path); result.metadataAfterSha256 = HashFile(metadata);
                if (result.payloadAfterSha256 != result.payloadBeforeSha256 || new FileInfo(path).Length != result.bytes || ReadGuid(metadata) != result.guid || AssetDatabase.AssetPathToGUID(result.path).ToLowerInvariant() != result.guid)
                    throw new InvalidDataException("Image correction changed source payload or stable GUID: " + result.path);
                File.WriteAllText(result.settingsAfterPath, EditorJsonUtility.ToJson(importer, true), new UTF8Encoding(false));
                string otherSettings = OtherSettings(importer); result.otherSettingsAfterSha256 = HashText(otherSettings);
                File.WriteAllText(result.settingsAfterPath + ".semantic.json", otherSettings, new UTF8Encoding(false));
                if (result.otherSettingsBeforeSha256 != result.otherSettingsAfterSha256) throw new InvalidDataException("A texture setting other than shape changed: " + result.path);
                result.complete = true; result.elapsedSeconds = itemWatch.Elapsed.TotalSeconds; report.completed++;
                SaveReport(reportPath, report);
                if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity reported errors during image shape correction.");
                if (report.completed % 20 == 0) {
                    UnityEngine.Debug.Log("Yamyam raw Texture2D correction " + report.completed + "/200.");
                    EditorUtility.UnloadUnusedAssetsImmediate(true); // Isolated process only; no scenes or user selection touched.
                }
            }
            if (HashFile(manifestPath) != report.manifestSha256 || HashFile(planPath) != report.planSha256 || HashFile(failedPath) != FailedReportSha256 || report.completed != 200 || report.observedUnityErrors != 0) throw new IOException("Canonical image audit/manifest/failed evidence changed, native errors occurred, or work is incomplete.");
            report.status = "complete";
        }
        catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); throw; }
        finally {
            Application.logMessageReceived -= capture; report.completedUtc = Utc(); report.elapsedSeconds = watch.Elapsed.TotalSeconds;
            SaveReport(reportPath, report); SaveReport(Path.Combine(local, "texture2d-correction-report.json"), report);
        }
    }
    public static void RunHeadless()
    {
        Guard(); int code = 0;
        try { Run(); } catch (Exception error) { UnityEngine.Debug.LogError(error); code = 1; }
        EditorApplication.Exit(code);
    }
}
