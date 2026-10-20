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
using Object = UnityEngine.Object;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;
using FileInfo = YamyamAssetLibraryIO.Info;

/// <summary>Explicit isolated-batch metadata migration; never runs automatically.</summary>
public static class YamyamAssetLibraryMetadata
{
    const string Root = "Assets/ThirdParty/YamyamAssetLibrary";
    const string OriginalProject = "D:/Github/VideoEditing/unity/VideoEditing";
    const int TextureMinimum = 10, ModelMinimum = 25, BatchSize = 128;
    static readonly string Project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
    static readonly string Work = Path.Combine(Project, "Library/YamyamAssetLibrary");
    static readonly Regex GuidPattern = new Regex(@"(?m)^guid:[ \t]*([a-fA-F0-9]{32})[ \t]*\r?$", RegexOptions.Compiled);
    static readonly HashSet<string> TextureExtensions = new HashSet<string>(new[] { ".png", ".jpg", ".jpeg", ".tga", ".tif", ".tiff", ".psd", ".bmp", ".exr", ".hdr", ".gif", ".iff", ".pict" }, StringComparer.OrdinalIgnoreCase);
    static readonly HashSet<string> ModelExtensions = new HashSet<string>(new[] { ".fbx", ".obj", ".dae", ".3ds", ".dxf" }, StringComparer.OrdinalIgnoreCase);
    static readonly HashSet<string> TransientProperties = new HashSet<string>(new[] { "m_ObjectHideFlags", "m_CorrespondingSourceObject", "m_PrefabInstance", "m_PrefabAsset", "m_Name", "m_AssetPath", "m_AssetTimeStamp", "m_ImportTimeStamp" });
    static Report report;
    static string runDirectory;
    static bool observing;
    static readonly HashSet<string> observedImports = new HashSet<string>(StringComparer.Ordinal);
    [Serializable] sealed class Manifest { public string project, stageRoot; }
    [Serializable] public sealed class Value { public string path, type, value; }
    [Serializable] public sealed class Settings { public string importerType; public List<Value> properties = new List<Value>(); }
    [Serializable] public sealed class Identity { public string guid, type, name, animation; public long localId; }
    [Serializable] public sealed class Snapshot
    {
        public string assetPath, importerType, payloadSha256, metadataSha256, guid, settingsJsonPath, semanticSettingsSha256;
        public int serializedVersion; public List<Identity> subassets;
    }
    [Serializable] public sealed class Canary { public string role; public long elapsedMilliseconds, totalElapsedMilliseconds; public Snapshot before, after; public List<string> observedImportedAssets; public bool passed; }
    [Serializable] public sealed class Change
    {
        public string assetPath, kind, reason, guid, beforeSha256, afterSha256, backup;
        public int versionBefore, versionAfter; public long payloadBytes, payloadLastWriteUtcTicks;
    }
    [Serializable] public sealed class Batch { public int index, count; public long elapsedMilliseconds; public List<string> observedImportedAssets; }
    [Serializable] public sealed class Report
    {
        public string status, run, projectPath, startedUtc, completedUtc, unityVersion, error;
        public string root = Root;
        public string mode = "Explicit ForceReserializeAssets(paths, ReserializeMetadata); metadata only.";
        public string importObservationScope = "Only OnPostprocessAllAssets notifications observed synchronously during each explicit metadata operation; queued imports outside this interval are not claimed absent.";
        public bool originalArchivesModified, assetPayloadWritesRequested;
        public int candidates, warnings, errors;
        public List<Canary> canaries = new List<Canary>();
        public List<Change> changes = new List<Change>();
        public List<Batch> batches = new List<Batch>();
        public List<string> messages = new List<string>();
    }

    // Invoke only after the preceding isolated import has exited normally.
    // Optional -yamyamMetadataCanaryOnly stops after four verified canaries.
    public static void RunHeadless()
    {
        // Refusal must never close an interactive or unrelated Editor. Later
        // failures in the authorized isolated process still exit normally1.
        string expected = Path.GetFullPath(Path.Combine(OriginalProject, "Library/YamyamAssetLibrary/headless-project"));
        if (!Application.isBatchMode || !string.Equals(Project, expected, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Only the exact isolated batch project is authorized.");
        int exit = 1;
        try
        {
            NoLinks(Project, OriginalProject);
            string run = DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ");
            runDirectory = Path.Combine(Work, "metadata-upgrade", run);
            NoLinks(runDirectory, Project);
            Directory.CreateDirectory(runDirectory);
            report = new Report { status = "checking", run = run, projectPath = Project, startedUtc = Utc(), unityVersion = Application.unityVersion };
            Guard();
            Application.logMessageReceived += ObserveLog;
            var candidates = Census(); report.candidates = candidates.Count;
            var canaries = CanaryPaths();
            foreach (var pair in canaries)
            {
                var totalWatch = Stopwatch.StartNew();
                var record = new Canary { role = pair.Key }; report.canaries.Add(record);
                record.before = Capture(pair.Value, "before");
                if (pair.Key == "animated-model-011" && !record.before.subassets.Any(a => a.type == typeof(AnimationClip).FullName))
                    throw new InvalidDataException("The selected011 FBX has no persistent actual animation clip.");
                var change = Prepare(pair.Value, "canary"); report.changes.Add(change);
                SaveReport();
                var watch = Stopwatch.StartNew();
                ObserveBegin();
                try { AssetDatabase.ForceReserializeAssets(new[] { pair.Value }, ForceReserializeAssetsOptions.ReserializeMetadata); }
                finally { record.observedImportedAssets = ObserveEnd(); watch.Stop(); record.elapsedMilliseconds = watch.ElapsedMilliseconds; }
                record.after = Capture(pair.Value, "after"); FinishChange(change);
                if (record.before.payloadSha256 != record.after.payloadSha256 || record.before.guid != record.after.guid
                    || record.before.semanticSettingsSha256 != record.after.semanticSettingsSha256
                    || JsonUtility.ToJson(new Identities { values = record.before.subassets }) != JsonUtility.ToJson(new Identities { values = record.after.subassets }))
                    throw new InvalidDataException("Canary changed payload, GUID, effective importer settings or persistent subasset identities: " + pair.Value);
                totalWatch.Stop(); record.totalElapsedMilliseconds = totalWatch.ElapsedMilliseconds;
                if (report.errors != 0) throw new InvalidDataException("Unity logged errors during the canary; inspect the recorded messages before any bulk migration.");
                record.passed = true; SaveReport();
            }
            if (Environment.GetCommandLineArgs().Contains("-yamyamMetadataCanaryOnly"))
            { report.status = "canary-pass"; exit = 0; return; }
            var tested = new HashSet<string>(canaries.Select(p => p.Value), StringComparer.Ordinal);
            candidates = candidates.Where(p => !tested.Contains(p)).ToList();
            for (int start = 0; start < candidates.Count; start += BatchSize)
            {
                string[] paths = candidates.Skip(start).Take(BatchSize).ToArray();
                var changes = paths.Select(p => Prepare(p, "missing/unsupported importer metadata")).ToArray();
                report.changes.AddRange(changes);
                var batch = new Batch { index = report.batches.Count, count = paths.Length }; report.batches.Add(batch);
                SaveReport();
                var watch = Stopwatch.StartNew(); ObserveBegin();
                try { AssetDatabase.ForceReserializeAssets(paths, ForceReserializeAssetsOptions.ReserializeMetadata); }
                finally { batch.observedImportedAssets = ObserveEnd(); watch.Stop(); batch.elapsedMilliseconds = watch.ElapsedMilliseconds; }
                foreach (var change in changes) FinishChange(change);
                if (report.errors != 0) throw new InvalidDataException("Unity logged errors during metadata migration; later batches are refused.");
                SaveReport();
            }
            report.status = "complete"; exit = 0;
        }
        catch (Exception error) { if (report != null) { report.status = "failed"; report.error = error.ToString(); } UnityEngine.Debug.LogException(error); }
        finally
        {
            observing = false; Application.logMessageReceived -= ObserveLog;
            try { if (report != null) { report.completedUtc = Utc(); SaveReport(); } }
            catch (Exception error) { exit = 1; UnityEngine.Debug.LogError("Metadata migration report could not be finalized: " + error); }
            finally { EditorApplication.Exit(exit); }
        }
    }
    [Serializable] sealed class Identities { public List<Identity> values; }
    static string Utc() { return DateTime.UtcNow.ToString("o"); }
    static string Hash(byte[] data) { using (var h = SHA256.Create()) return BitConverter.ToString(h.ComputeHash(data)).Replace("-", "").ToLowerInvariant(); }
    static string HashFile(string path) { using (var stream = File.OpenRead(path)) using (var h = SHA256.Create()) return BitConverter.ToString(h.ComputeHash(stream)).Replace("-", "").ToLowerInvariant(); }
    static string Absolute(string assetPath)
    {
        if (!assetPath.StartsWith(Root + "/", StringComparison.Ordinal)) throw new InvalidDataException("Unowned asset path: " + assetPath);
        string full = Path.GetFullPath(Path.Combine(Project, assetPath.Replace('/', Path.DirectorySeparatorChar)));
        string boundary = Path.GetFullPath(Path.Combine(Project, Root));
        if (!full.StartsWith(boundary + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Asset escaped owned root.");
        NoLinks(full, Project); return full;
    }
    static void NoLinks(string path, string boundary)
    {
        var cursor = new FileInfo(Path.GetFullPath(path));
        string stop = Path.GetFullPath(boundary).TrimEnd(Path.DirectorySeparatorChar);
        string current = cursor.FullName;
        while (true)
        {
            if ((File.Exists(current) || Directory.Exists(current)) && (File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0) throw new IOException("Reparse/symlink refused: " + current);
            if (string.Equals(current.TrimEnd(Path.DirectorySeparatorChar), stop, StringComparison.OrdinalIgnoreCase)) return;
            current = Path.GetDirectoryName(current);
            if (string.IsNullOrEmpty(current)) throw new IOException("Ownership boundary not reached.");
        }
    }
    static void Guard()
    {
        string expected = Path.GetFullPath(Path.Combine(OriginalProject, "Library/YamyamAssetLibrary/headless-project"));
        if (!Application.isBatchMode || !string.Equals(Project, expected, StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Only the exact isolated batch project is authorized.");
        if (Application.unityVersion != "6000.6.0f1" || EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Expected idle Unity6000.6.0f1 after initial import.");
        NoLinks(Project, OriginalProject);
        var manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(OriginalProject, "Library/YamyamAssetLibrary/staging-manifest.json")));
        if (!string.Equals(Path.GetFullPath(manifest.project), Path.GetFullPath(OriginalProject), StringComparison.OrdinalIgnoreCase)
            || !string.Equals(Path.GetFullPath(manifest.stageRoot), Path.GetFullPath(Path.Combine(Project, Root)), StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Canonical manifest does not bind this exact isolated root.");
        NoLinks(Path.Combine(Project, Root), OriginalProject);
    }
    static byte[] Prefix(string path)
    {
        using (var f = File.OpenRead(path)) { byte[] bytes = new byte[Math.Min(65536L, f.Length)]; int read = f.Read(bytes, 0, bytes.Length); if (read != bytes.Length) Array.Resize(ref bytes, read); return bytes; }
    }
    static int Version(string assetPath, string kind)
    {
        string meta = Absolute(assetPath) + ".meta";
        byte[] prefix = Prefix(meta);
        // A truncated prefix cannot establish the complete importer block (or
        // rule out another root block). Large metadata therefore uses its full
        // text before choosing the one direct importer version field.
        string text = new FileInfo(meta).Length > prefix.LongLength ? File.ReadAllText(meta) : Encoding.UTF8.GetString(prefix);
        return ImporterVersion(text, kind);
    }
    static int ImporterVersion(string text, string kind)
    {
        if (kind != "TextureImporter" && kind != "ModelImporter") return -1;
        text = text.TrimStart('\uFEFF');
        var headers = Regex.Matches(text, @"(?m)^" + Regex.Escape(kind) + @":[ \t]*\r?$");
        if (headers.Count != 1) return -1;
        int start = headers[0].Index + headers[0].Length;
        // Search from the chosen header's end, not the file's first root key.
        var nextRoot = new Regex(@"(?m)^[^ \t\r\n#][^\r\n]*").Match(text, start);
        string block = text.Substring(start, (nextRoot.Success ? nextRoot.Index : text.Length) - start);
        var versions = Regex.Matches(block, @"(?m)^  serializedVersion:[ \t]*([0-9]+)[ \t]*\r?$");
        int version;
        return versions.Count == 1 && int.TryParse(versions[0].Groups[1].Value, NumberStyles.None, CultureInfo.InvariantCulture, out version) ? version : -1;
    }
    static string Kind(string assetPath)
    {
        var importer = AssetImporter.GetAtPath(assetPath);
        if (importer is ModelImporter) return "ModelImporter";
        if (importer is TextureImporter) return "TextureImporter";
        throw new InvalidDataException("Unsupported/non-model/texture importer: " + assetPath);
    }
    static List<string> Census()
    {
        var result = new List<string>(); var pending = new Stack<string>(); pending.Push(Path.Combine(Project, Root));
        while (pending.Count != 0)
        {
            string directory = pending.Pop();
            foreach (string entry in Directory.EnumerateFileSystemEntries(directory))
            {
                var attributes = File.GetAttributes(entry);
                if ((attributes & FileAttributes.ReparsePoint) != 0) throw new IOException("Reparse point in scoped root: " + entry);
                if ((attributes & FileAttributes.Directory) != 0) { pending.Push(entry); continue; }
                string extension = Path.GetExtension(entry);
                if (!TextureExtensions.Contains(extension) && !ModelExtensions.Contains(extension)) continue;
                string asset = entry.Substring(Project.Length + 1).Replace('\\', '/');
                string kind = ModelExtensions.Contains(extension) ? "ModelImporter" : "TextureImporter";
                if (!File.Exists(entry + ".meta")) throw new FileNotFoundException("Existing source metadata missing", entry + ".meta");
                int version = Version(asset, kind), minimum = kind == "ModelImporter" ? ModelMinimum : TextureMinimum;
                if (version < minimum && Kind(asset) == kind) result.Add(asset);
            }
        }
        result.Sort(StringComparer.Ordinal); return result;
    }
    static List<KeyValuePair<string, string>> CanaryPaths()
    {
        const string food = Root + "/007-kitchen-restaurant-megapack-unity-godot-fbx/Restourant/Unity FBX/Food/BagFood_1_A.fbx";
        const string animated = Root + "/011-cartoon-city-massive-pack-characters-unity-godot-fbx/Characters Full/Unity FBX/Animations/Death_A.fbx";
        string palette = Directory.EnumerateFiles(Path.Combine(Project, Root, "007-kitchen-restaurant-megapack-unity-godot-fbx/Restourant/Textures"), "*.png").OrderBy(p => p, StringComparer.Ordinal).First();
        const string pbr = Root + "/046-12-toon-plasticine-pbr-material-substance-texture/Plasticine_01_8K_BaseColor.png";
        return new List<KeyValuePair<string, string>> { new KeyValuePair<string, string>("static-model-007", food), new KeyValuePair<string, string>("animated-model-011", animated), new KeyValuePair<string, string>("palette-texture-007", palette.Substring(Project.Length + 1).Replace('\\', '/')), new KeyValuePair<string, string>("pbr-texture-046", pbr) };
    }
    static string ObjectIdentity(Object value)
    {
        if (!value) return "null";
        string guid; long localId;
        if (AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value, out guid, out localId)) return guid + ":" + localId.ToString(CultureInfo.InvariantCulture) + ":" + value.GetType().FullName;
        return "builtin:" + value.GetType().FullName + ":" + value.name;
    }
    static string Numbers(params float[] values) { return string.Join(",", values.Select(v => v.ToString("R", CultureInfo.InvariantCulture))); }
    static string PropertyValue(SerializedProperty p)
    {
        switch (p.propertyType)
        {
            case SerializedPropertyType.Integer: return p.longValue.ToString(CultureInfo.InvariantCulture);
            case SerializedPropertyType.Boolean: return p.boolValue ? "true" : "false";
            case SerializedPropertyType.Float: return p.doubleValue.ToString("R", CultureInfo.InvariantCulture);
            case SerializedPropertyType.String: return p.stringValue;
            case SerializedPropertyType.Enum: case SerializedPropertyType.ArraySize: case SerializedPropertyType.Character: case SerializedPropertyType.LayerMask: return p.intValue.ToString(CultureInfo.InvariantCulture);
            case SerializedPropertyType.ObjectReference: return ObjectIdentity(p.objectReferenceValue);
            case SerializedPropertyType.ExposedReference: return ObjectIdentity(p.exposedReferenceValue);
            case SerializedPropertyType.Color: var c = p.colorValue; return Numbers(c.r, c.g, c.b, c.a);
            case SerializedPropertyType.Vector2: var v2 = p.vector2Value; return Numbers(v2.x, v2.y);
            case SerializedPropertyType.Vector3: var v3 = p.vector3Value; return Numbers(v3.x, v3.y, v3.z);
            case SerializedPropertyType.Vector4: var v4 = p.vector4Value; return Numbers(v4.x, v4.y, v4.z, v4.w);
            case SerializedPropertyType.Quaternion: var q = p.quaternionValue; return Numbers(q.x, q.y, q.z, q.w);
            case SerializedPropertyType.Rect: var rect = p.rectValue; return Numbers(rect.x, rect.y, rect.width, rect.height);
            case SerializedPropertyType.Bounds: var b = p.boundsValue; return Numbers(b.center.x, b.center.y, b.center.z, b.size.x, b.size.y, b.size.z);
            case SerializedPropertyType.Vector2Int: return p.vector2IntValue.ToString();
            case SerializedPropertyType.Vector3Int: return p.vector3IntValue.ToString();
            case SerializedPropertyType.RectInt: return p.rectIntValue.ToString();
            case SerializedPropertyType.BoundsInt: return p.boundsIntValue.ToString();
            case SerializedPropertyType.Hash128: return p.hash128Value.ToString();
            case SerializedPropertyType.AnimationCurve: return JsonUtility.ToJson(new Curve { keys = p.animationCurveValue.keys, pre = p.animationCurveValue.preWrapMode, post = p.animationCurveValue.postWrapMode });
            case SerializedPropertyType.Gradient: return JsonUtility.ToJson(new GradientData { color = p.gradientValue.colorKeys, alpha = p.gradientValue.alphaKeys, mode = p.gradientValue.mode });
            case SerializedPropertyType.FixedBufferSize: return p.fixedBufferSize.ToString(CultureInfo.InvariantCulture);
            case SerializedPropertyType.ManagedReference: return p.managedReferenceFullTypename + ":" + JsonUtility.ToJson(p.managedReferenceValue);
            default: throw new InvalidDataException("Unhandled importer setting type: " + p.propertyType + ":" + p.propertyPath);
        }
    }
    [Serializable] sealed class Curve { public Keyframe[] keys; public WrapMode pre, post; }
    [Serializable] sealed class GradientData { public GradientColorKey[] color; public GradientAlphaKey[] alpha; public GradientMode mode; }
    static Settings SemanticSettings(AssetImporter importer)
    {
        var result = new Settings { importerType = importer.GetType().FullName };
        using (var serialized = new SerializedObject(importer))
        using (var p = serialized.GetIterator())
            while (p.Next(true))
            {
                string first = p.propertyPath.Split('.')[0];
                if (TransientProperties.Contains(first) || p.propertyType == SerializedPropertyType.Generic) continue;
                result.properties.Add(new Value { path = p.propertyPath, type = p.propertyType.ToString(), value = PropertyValue(p) });
            }
        result.properties = result.properties.OrderBy(v => v.path, StringComparer.Ordinal).ToList(); return result;
    }
    static Snapshot Capture(string assetPath, string suffix)
    {
        string absolute = Absolute(assetPath), guid = MetaGuid(absolute + ".meta");
        var importer = AssetImporter.GetAtPath(assetPath); if (!importer) throw new InvalidDataException("Importer unavailable: " + assetPath);
        string raw = Path.Combine(runDirectory, "canary-settings", guid + "." + suffix + ".json");
        Directory.CreateDirectory(Path.GetDirectoryName(raw)); File.WriteAllText(raw, EditorJsonUtility.ToJson(importer, true));
        string semantic = JsonUtility.ToJson(SemanticSettings(importer), true); File.WriteAllText(raw + ".semantic.json", semantic);
        var identities = new List<Identity>();
        foreach (var value in AssetDatabase.LoadAllAssetsAtPath(assetPath))
        {
            if (!value || value.name.StartsWith("__preview__", StringComparison.Ordinal)) continue;
            string assetGuid; long localId;
            if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value, out assetGuid, out localId)) throw new InvalidDataException("Persistent subasset identity unavailable: " + assetPath + " :: " + value.name);
            var clip = value as AnimationClip;
            identities.Add(new Identity { guid = assetGuid, localId = localId, type = value.GetType().FullName, name = value.name,
                animation = clip ? Numbers(clip.length, clip.frameRate) + ":legacy=" + clip.legacy : null });
        }
        identities = identities.OrderBy(v => v.guid, StringComparer.Ordinal).ThenBy(v => v.localId).ThenBy(v => v.type, StringComparer.Ordinal).ThenBy(v => v.name, StringComparer.Ordinal).ToList();
        return new Snapshot { assetPath = assetPath, importerType = importer.GetType().FullName, payloadSha256 = HashFile(absolute), metadataSha256 = HashFile(absolute + ".meta"), guid = guid,
            serializedVersion = Version(assetPath, Kind(assetPath)), settingsJsonPath = raw, semanticSettingsSha256 = Hash(Encoding.UTF8.GetBytes(semantic)), subassets = identities };
    }
    static string MetaGuid(string meta)
    {
        var match = GuidPattern.Match(Encoding.UTF8.GetString(Prefix(meta)));
        if (!match.Success) throw new InvalidDataException("No canonical metadata GUID: " + meta);
        return match.Groups[1].Value.ToLowerInvariant();
    }
    static Change Prepare(string assetPath, string reason)
    {
        string absolute = Absolute(assetPath), kind = Kind(assetPath), meta = absolute + ".meta";
        var info = new FileInfo(absolute);
        string backup = Path.Combine(runDirectory, "metadata-before", assetPath.Substring(Root.Length + 1).Replace('/', Path.DirectorySeparatorChar) + ".meta");
        Directory.CreateDirectory(Path.GetDirectoryName(backup)); File.Copy(meta, backup, false);
        return new Change { assetPath = assetPath, kind = kind, reason = reason, guid = MetaGuid(meta), beforeSha256 = HashFile(meta), versionBefore = Version(assetPath, kind), backup = backup, payloadBytes = info.Length, payloadLastWriteUtcTicks = info.LastWriteTimeUtc.Ticks };
    }
    static void FinishChange(Change change)
    {
        string absolute = Absolute(change.assetPath); var info = new FileInfo(absolute);
        change.afterSha256 = HashFile(absolute + ".meta"); change.versionAfter = Version(change.assetPath, change.kind);
        int minimum = change.kind == "ModelImporter" ? ModelMinimum : TextureMinimum;
        if (MetaGuid(absolute + ".meta") != change.guid || info.Length != change.payloadBytes || info.LastWriteTimeUtc.Ticks != change.payloadLastWriteUtcTicks || change.versionAfter < minimum)
            throw new InvalidDataException("GUID/payload identity changed or unsupported metadata remains: " + change.assetPath);
    }
    static void ObserveBegin() { observedImports.Clear(); observing = true; }
    static List<string> ObserveEnd() { observing = false; return observedImports.OrderBy(p => p, StringComparer.Ordinal).ToList(); }
    internal static void Imported(string[] paths) { if (observing) foreach (string path in paths) if (path.StartsWith(Root + "/", StringComparison.Ordinal)) observedImports.Add(path); }
    static void ObserveLog(string message, string stack, LogType type)
    {
        if (report == null || type == LogType.Log) return;
        if (type == LogType.Warning) report.warnings++; else report.errors++;
        if (report.messages.Count < 2000) report.messages.Add(type + ": " + message);
    }
    static void SaveReport()
    {
        string json = JsonUtility.ToJson(report, true);
        AtomicReport(Path.Combine(runDirectory, "report.json"), json);
        AtomicReport(Path.Combine(Work, "metadata-upgrade-report.json"), json);
    }
    static void AtomicReport(string path, string json)
    {
        NoLinks(path, Project);
        string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        NoLinks(temporary, Project);
        File.WriteAllText(temporary, json + "\n", new UTF8Encoding(false));
        for (int attempt = 0; ; attempt++)
        {
            try
            {
                NoLinks(path, Project);
                if (File.Exists(path)) File.Replace(temporary, path, null);
                else File.Move(temporary, path);
                return;
            }
            catch (IOException error)
            {
                int code = error.HResult & 0xffff;
                if (attempt >= 4 || (code != 5 && code != 32 && code != 33 && code != 1175))
                    throw new IOException("Atomic metadata report failed; newest evidence retained at " + temporary, error);
            }
            catch (UnauthorizedAccessException error)
            {
                if (attempt >= 4) throw new IOException("Atomic metadata report denied; newest evidence retained at " + temporary, error);
            }
            System.Threading.Thread.Sleep(100 * (attempt + 1));
        }
    }
}

sealed class YamyamAssetLibraryMetadataImportObserver : AssetPostprocessor
{
    static void OnPostprocessAllAssets(string[] imported, string[] deleted, string[] moved, string[] movedFrom)
    { YamyamAssetLibraryMetadata.Imported(imported); }
}
