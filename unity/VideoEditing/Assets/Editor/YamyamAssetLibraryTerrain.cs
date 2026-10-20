// Prepared for an explicit, isolated batch job. Never initialize automatically.
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
using Object = UnityEngine.Object;

public static class YamyamAssetLibraryTerrain
{
    const string ExpectedProject = "D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string Root = "Assets/ThirdParty/YamyamAssetLibrary";
    const string Generated = "Assets/_TerrainAutoUpgrade";
    static readonly Regex GuidLine = new Regex(@"(?m)^guid:\s*([a-fA-F0-9]{32})\s*$");
    static readonly Regex TextureSlot = new Regex(@"(m_(?:DiffuseTexture|NormalMapTexture|MaskMapTexture)):\s*\{[^}]*guid:\s*([a-fA-F0-9]{32})[^}]*\}");

    [Serializable] public sealed class Manifest { public string project, stageRoot; public Product[] products; }
    [Serializable] public sealed class Product { public string id, folder, status; }
    [Serializable] public sealed class Receipt { public string id, folder; public FileRecord[] files; }
    [Serializable] public sealed class FileRecord { public string path, sha256; public long bytes; }
    [Serializable] public sealed class Ref { public string guid, type; public long localId; }
    [Serializable] public sealed class LayerState
    {
        public Ref asset, diffuse, normal, mask;
        public string name;
        public Vector2 tileSize, tileOffset;
        public Color specular;
        public float metallic, smoothness, normalScale;
        public Vector4 diffuseRemapMin, diffuseRemapMax, maskMapRemapMin, maskMapRemapMax;
    }
    [Serializable] public sealed class TerrainState
    {
        public Ref asset;
        public string name, heightSha256, alphaSha256, holeSha256, detailSha256, treesSha256, prototypesSha256;
        public int heightResolution, alphaWidth, alphaHeight, alphaLayers, baseMapResolution;
        public int holesResolution, detailWidth, detailHeight, detailResolutionPerPatch, detailPatchCount;
        public float wavingGrassAmount, wavingGrassSpeed, wavingGrassStrength;
        public Color wavingGrassTint;
        public Vector3 size;
        public bool enableHolesTextureCompression;
        public List<LayerState> layers = new List<LayerState>();
    }
    [Serializable] public sealed class TerrainRecord
    {
        public string productId, path, payloadBeforeSha256, payloadAfterSha256, backup;
        public string beforeSemanticSha256, afterSemanticSha256;
        public bool saveStarted, layersRebound, dirtySaveStarted, dirtySaved, saved;
        public string reboundSemanticSha256, postDirtySavePayloadSha256;
        public List<string> externalDependenciesBefore = new List<string>();
        public List<string> externalDependenciesAfter = new List<string>();
        public TerrainState before, after;
    }
    [Serializable] public sealed class LayerRecord
    {
        public string path, destination, guid, assignedProductId, payloadSha256, metadataSha256;
        public bool moveStarted, moved, orphan;
        public List<string> terrainOwners = new List<string>();
        public List<string> terrains = new List<string>();
        public List<string> missingTextureGuids = new List<string>();
        public List<string> externalTexturePaths = new List<string>();
    }
    [Serializable] public sealed class DependencyTarget
    {
        public string path, guid, canonicalSha256, actualSha256, sourceArtifactSha256;
        public string metadataPath, metadataSha256, canonicalMetadataSha256;
        public long bytes, metadataBytes;
        public int checkedInboundReferences;
        public bool referencedByOtherRootAssets;
    }
    [Serializable] public sealed class DependencyProof
    {
        public string status, method = "AssetDatabase.GetDependencies(all current non-folder root asset paths except both target TerrainData, recursive:true). Input paths themselves are excluded, so membership proves another root dependency.";
        public string startedUtc, completedUtc, rootPathsSha256, closurePathsSha256, receiptSha256;
        public int proofVersion = 1, rootAssetsChecked, dependencyClosurePaths;
        public List<DependencyTarget> excludedTargets = new List<DependencyTarget>();
        public double elapsedSeconds;
    }
    [Serializable] public sealed class FreshImport
    {
        public string path, payloadBeforeSha256, payloadAfterSha256, metadataBeforeSha256, metadataAfterSha256, guidBefore, guidAfter;
        public double elapsedSeconds;
    }
    [Serializable] public sealed class Report
    {
        public int schemaVersion = 1;
        public string status = "inspecting", project, startedUtc, completedUtc, runDirectory, manifestPath, manifestSha256;
        public bool apply, originalArchivesModified, scenesOpened, dependencyProofOnly, terrainSemanticsCaptured;
        public int observedUnityWarnings, observedUnityErrors;
        public double elapsedSeconds;
        public List<TerrainRecord> terrains = new List<TerrainRecord>();
        public List<LayerRecord> layers = new List<LayerRecord>();
        public List<FreshImport> freshTerrainImports = new List<FreshImport>();
        public DependencyProof missingProviderTerrainDependencyProof;
        public List<string> blockers = new List<string>();
        public List<string> normalizationBlockers = new List<string>();
        public List<string> warnings = new List<string>();
        public List<string> errors = new List<string>();
        public string scope = "Actual TerrainData.terrainLayers determines ownership after binary repair. Only uniquely owned generated layers move, preserving GUID/local IDs. Only affected owned TerrainData is explicitly reserialized. Orphan outputs remain outside the library. Final whole-library dependency validation remains required.";
        public string failureRecovery = "Operations are individually journaled, not an atomic transaction. Backups preserve prior owned source/meta bytes. A failure requires inspection/recovery after this isolated process exits; it must not be accepted as completed normalization.";
    }

    static string Project { get { return Path.GetDirectoryName(Application.dataPath).Replace('\\', '/'); } }
    static string MainWork { get { return Path.GetFullPath(Path.Combine(Project, "..")); } }
    static string Absolute(string assetPath) { return Path.Combine(Project, assetPath).Replace('\\', '/'); }
    static string Utc() { return DateTime.UtcNow.ToString("o"); }
    // Extended paths belong only to physical IO. AssetDatabase/canonical paths
    // and ownership comparisons always retain their ordinary project form.
    static string NormalPath(string path)
    {
        if (path.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase)) path = @"\\" + path.Substring(8);
        else if (path.StartsWith(@"\\?\", StringComparison.Ordinal)) path = path.Substring(4);
        return Path.GetFullPath(path);
    }
    static string IOPath(string path)
    {
        string full = NormalPath(path);
        if (Path.DirectorySeparatorChar != '\\') return full;
        return full.StartsWith(@"\\", StringComparison.Ordinal) ? @"\\?\UNC\" + full.Substring(2) : @"\\?\" + full;
    }
    static string Hex(byte[] bytes) { return BitConverter.ToString(bytes).Replace("-", "").ToLowerInvariant(); }
    static string HashFile(string path) { using (var input = File.OpenRead(IOPath(path))) using (var hash = SHA256.Create()) return Hex(hash.ComputeHash(input)); }
    static string HashText(string text) { using (var hash = SHA256.Create()) return Hex(hash.ComputeHash(Encoding.UTF8.GetBytes(text))); }
    static bool InRoot(string path) { return path == Root || path.StartsWith(Root + "/", StringComparison.Ordinal); }
    static bool InGenerated(string path) { return path.StartsWith(Generated + "/", StringComparison.Ordinal); }

    static void GuardOwnership()
    {
        if (!Application.isBatchMode || !string.Equals(Project, ExpectedProject, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Terrain normalization is restricted to the exact isolated batch project.");
    }
    static void Guard()
    {
        GuardOwnership();
        if (Application.unityVersion != "6000.6.0f1" || EditorApplication.isCompiling || EditorApplication.isUpdating)
            throw new InvalidOperationException("Expected idle Unity 6000.6.0f1.");
        NoLinks(Project);
    }
    static void NoLinks(string path)
    {
        string full = NormalPath(path), boundary = NormalPath(Project);
        if (full != boundary && !full.StartsWith(boundary + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Path escaped isolated project: " + path);
        for (string current = full; !string.IsNullOrEmpty(current); current = Path.GetDirectoryName(current))
        {
            try {
                if ((File.GetAttributes(IOPath(current)) & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("Reparse path refused: " + current);
            }
            catch (FileNotFoundException) { }
            catch (DirectoryNotFoundException) { }
            if (string.Equals(current, boundary, StringComparison.OrdinalIgnoreCase)) return;
        }
        throw new InvalidOperationException("Ownership boundary not reached.");
    }
    static Ref Reference(Object value)
    {
        if (value == null) return new Ref { guid = "", localId = 0, type = "null" };
        string guid; long localId;
        if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value, out guid, out localId))
            throw new InvalidDataException("Terrain reference has no persistent GUID/local ID: " + value.name);
        return new Ref { guid = guid.ToLowerInvariant(), localId = localId, type = value.GetType().FullName };
    }
    static LayerState SnapshotLayer(TerrainLayer layer)
    {
        if (layer == null) throw new InvalidDataException("Terrain contains a null TerrainLayer.");
        return new LayerState {
            asset = Reference(layer), name = layer.name, diffuse = Reference(layer.diffuseTexture), normal = Reference(layer.normalMapTexture), mask = Reference(layer.maskMapTexture),
            tileSize = layer.tileSize, tileOffset = layer.tileOffset, specular = layer.specular,
            metallic = layer.metallic, smoothness = layer.smoothness, normalScale = layer.normalScale,
            diffuseRemapMin = layer.diffuseRemapMin, diffuseRemapMax = layer.diffuseRemapMax,
            maskMapRemapMin = layer.maskMapRemapMin, maskMapRemapMax = layer.maskMapRemapMax
        };
    }
    static string HashValues(Action<BinaryWriter> write)
    {
        using (var hash = SHA256.Create())
        using (var sink = new CryptoStream(Stream.Null, hash, CryptoStreamMode.Write))
        using (var buffer = new BufferedStream(sink, 65536))
        {
            var writer = new BinaryWriter(buffer, Encoding.UTF8, true);
            write(writer); writer.Flush(); buffer.Flush(); sink.FlushFinalBlock();
            return Hex(hash.Hash);
        }
    }
    static void WriteVector(BinaryWriter output, Vector3 value) { output.Write(value.x); output.Write(value.y); output.Write(value.z); }
    static void WriteColor(BinaryWriter output, Color32 value) { output.Write(value.r); output.Write(value.g); output.Write(value.b); output.Write(value.a); }
    static TerrainState Snapshot(TerrainData data)
    {
        var state = new TerrainState {
            asset = Reference(data), name = data.name, size = data.size, heightResolution = data.heightmapResolution,
            alphaWidth = data.alphamapWidth, alphaHeight = data.alphamapHeight, alphaLayers = data.alphamapLayers,
            baseMapResolution = data.baseMapResolution, holesResolution = data.holesResolution,
            detailWidth = data.detailWidth, detailHeight = data.detailHeight, detailResolutionPerPatch = data.detailResolutionPerPatch,
            detailPatchCount = data.detailPatchCount, enableHolesTextureCompression = data.enableHolesTextureCompression,
            wavingGrassAmount = data.wavingGrassAmount, wavingGrassSpeed = data.wavingGrassSpeed,
            wavingGrassStrength = data.wavingGrassStrength, wavingGrassTint = data.wavingGrassTint
        };
        foreach (var layer in data.terrainLayers) state.layers.Add(SnapshotLayer(layer));
        state.heightSha256 = HashValues(writer => {
            writer.Write(state.heightResolution);
            for (int y = 0; y < state.heightResolution; y += 32) {
                var rows = data.GetHeights(0, y, state.heightResolution, Math.Min(32, state.heightResolution - y));
                foreach (float value in rows) writer.Write(value);
            }
        });
        state.alphaSha256 = HashValues(writer => {
            writer.Write(state.alphaWidth); writer.Write(state.alphaHeight); writer.Write(state.alphaLayers);
            for (int y = 0; y < state.alphaHeight; y += 16) {
                var rows = data.GetAlphamaps(0, y, state.alphaWidth, Math.Min(16, state.alphaHeight - y));
                foreach (float value in rows) writer.Write(value);
            }
        });
        state.holeSha256 = HashValues(writer => {
            writer.Write(state.holesResolution);
            for (int y = 0; y < state.holesResolution; y += 32) {
                var rows = data.GetHoles(0, y, state.holesResolution, Math.Min(32, state.holesResolution - y));
                foreach (bool value in rows) writer.Write(value);
            }
        });
        state.detailSha256 = HashValues(writer => {
            writer.Write(data.detailPrototypes.Length); writer.Write(state.detailWidth); writer.Write(state.detailHeight);
            for (int layer = 0; layer < data.detailPrototypes.Length; layer++) {
                writer.Write(layer);
                for (int y = 0; y < state.detailHeight; y += 32) {
                    var rows = data.GetDetailLayer(0, y, state.detailWidth, Math.Min(32, state.detailHeight - y), layer);
                    foreach (int value in rows) writer.Write(value);
                }
            }
        });
        state.treesSha256 = HashValues(writer => {
            var trees = data.treeInstances; writer.Write(trees.Length);
            foreach (var tree in trees) {
                WriteVector(writer, tree.position); writer.Write(tree.widthScale); writer.Write(tree.heightScale);
                writer.Write(tree.rotation); writer.Write(tree.prototypeIndex); WriteColor(writer, tree.color); WriteColor(writer, tree.lightmapColor);
            }
        });
        state.prototypesSha256 = HashValues(writer => {
            writer.Write(data.treePrototypes.Length);
            foreach (var tree in data.treePrototypes) { writer.Write(JsonUtility.ToJson(Reference(tree.prefab))); writer.Write(tree.bendFactor); writer.Write(tree.navMeshLod); }
            writer.Write(data.detailPrototypes.Length);
            foreach (var detail in data.detailPrototypes) {
                // Instance IDs can change on import. Compare all serialized
                // scalar settings plus persistent identities of both references.
                writer.Write(Regex.Replace(JsonUtility.ToJson(detail), "\"instanceID\"\\s*:\\s*-?\\d+", "\"instanceID\":0"));
                writer.Write(JsonUtility.ToJson(Reference(detail.prototype)));
                writer.Write(JsonUtility.ToJson(Reference(detail.prototypeTexture)));
            }
        });
        return state;
    }
    static List<string> ForeignDependencies(string path)
    {
        return AssetDatabase.GetDependencies(path, true).Where(item => item.StartsWith("Assets/", StringComparison.Ordinal) && !InRoot(item)).Distinct().OrderBy(item => item, StringComparer.Ordinal).ToList();
    }
    static void SaveReport(string path, Report report)
    {
        NoLinks(path); Directory.CreateDirectory(IOPath(Path.GetDirectoryName(path)));
        string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        NoLinks(temporary);
        File.WriteAllText(IOPath(temporary), JsonUtility.ToJson(report, true) + "\n", new UTF8Encoding(false));
        for (int attempt = 0; ; attempt++) {
            try {
                NoLinks(path);
                if (File.Exists(IOPath(path))) File.Replace(IOPath(temporary), IOPath(path), null);
                else File.Move(IOPath(temporary), IOPath(path));
                return;
            }
            catch (IOException error) {
                int code = error.HResult & 0xffff;
                if (attempt >= 4 || (code != 5 && code != 32 && code != 33 && code != 1175))
                    throw new IOException("Atomic terrain report write failed; newest evidence retained at " + temporary, error);
            }
            catch (UnauthorizedAccessException error) {
                if (attempt >= 4) throw new IOException("Atomic terrain report write denied; newest evidence retained at " + temporary, error);
            }
            System.Threading.Thread.Sleep(100 * (attempt + 1));
        }
    }
    static void Backup(string run, string assetPath)
    {
        foreach (string suffix in new[] { "", ".meta" }) {
            string source = Absolute(assetPath) + suffix; NoLinks(source);
            if (!File.Exists(IOPath(source))) throw new FileNotFoundException("Required terrain/layer source missing", source);
            string destination = Path.Combine(run, "backups", assetPath + suffix); NoLinks(destination);
            Directory.CreateDirectory(IOPath(Path.GetDirectoryName(destination))); File.Copy(IOPath(source), IOPath(destination), false);
            if (HashFile(source) != HashFile(destination)) throw new IOException("Terrain backup failed verification: " + assetPath + suffix);
        }
    }
    static void EnsureFolder(string path)
    {
        NoLinks(Absolute(path));
        if (AssetDatabase.IsValidFolder(path)) return;
        string parent = Path.GetDirectoryName(path).Replace('\\', '/'); EnsureFolder(parent);
        if (string.IsNullOrEmpty(AssetDatabase.CreateFolder(parent, Path.GetFileName(path)))) throw new IOException("Cannot create owned generated folder: " + path);
    }
    static string Owner(string path, Product[] products)
    {
        var found = products.Where(product => path.StartsWith(Root + "/" + product.folder + "/", StringComparison.Ordinal)).ToArray();
        if (found.Length != 1) throw new InvalidDataException("TerrainData lacks one canonical product owner: " + path);
        return found[0].id;
    }
    static void InspectLayerFile(LayerRecord record)
    {
        NoLinks(Absolute(record.path)); NoLinks(Absolute(record.path) + ".meta");
        record.payloadSha256 = HashFile(Absolute(record.path)); record.metadataSha256 = HashFile(Absolute(record.path) + ".meta");
        string metadata = File.ReadAllText(IOPath(Absolute(record.path) + ".meta")); var match = GuidLine.Match(metadata);
        if (!match.Success) throw new InvalidDataException("Generated layer metadata GUID missing: " + record.path);
        if (record.orphan && string.IsNullOrEmpty(record.guid)) record.guid = match.Groups[1].Value.ToLowerInvariant();
        if (match.Groups[1].Value.ToLowerInvariant() != record.guid) throw new InvalidDataException("Generated layer metadata GUID mismatch: " + record.path);
        foreach (Match slot in TextureSlot.Matches(File.ReadAllText(IOPath(Absolute(record.path))))) {
            string guid = slot.Groups[2].Value.ToLowerInvariant();
            if (guid == new string('0', 32)) continue;
            string path = AssetDatabase.GUIDToAssetPath(guid);
            if (string.IsNullOrEmpty(path)) record.missingTextureGuids.Add(slot.Groups[1].Value + ":" + guid);
            else if (!InRoot(path)) record.externalTexturePaths.Add(path);
        }
    }
    static IEnumerable<string> GeneratedLayerPaths()
    {
        string root = Absolute(Generated);
        if (!Directory.Exists(IOPath(root))) yield break;
        var pending = new Stack<string>(); pending.Push(root);
        while (pending.Count != 0) {
            string directory = pending.Pop(); NoLinks(directory);
            foreach (string entry in Directory.GetDirectories(IOPath(directory))) { string child = NormalPath(entry); NoLinks(child); pending.Push(child); }
            foreach (string entry in Directory.GetFiles(IOPath(directory))) {
                string file = NormalPath(entry);
                NoLinks(file);
                if (file.EndsWith(".terrainlayer", StringComparison.OrdinalIgnoreCase)) yield return file;
            }
        }
    }
    static DependencyProof InspectProviderTerrainGroup(Manifest manifest)
    {
        var proof = new DependencyProof { startedUtc = Utc() }; var watch = Stopwatch.StartNew();
        Product product = manifest.products.Single(p => p.id == "033");
        string receiptPath = Path.Combine(MainWork, "receipts/033.json");
        proof.receiptSha256 = HashFile(receiptPath);
        var receipt = JsonUtility.FromJson<Receipt>(File.ReadAllText(IOPath(receiptPath)));
        if (receipt.id != product.id || receipt.folder != product.folder || receipt.files == null) throw new InvalidDataException("Product033 canonical receipt does not match current manifest ownership.");
        foreach (string filename in new[] { "Plakat4_terrain.asset", "New Terrain 6.asset" }) {
            string relative = product.folder + "/EmaceArt/PlasticineWorld/Terrain/" + filename;
            string assetPath = Root + "/" + relative;
            var records = receipt.files.Where(file => file.path == relative).ToArray();
            if (records.Length == 0 && !File.Exists(IOPath(Absolute(assetPath)))) continue;
            if (records.Length != 1) throw new InvalidDataException("Provider TerrainData lacks a unique canonical file record: " + relative);
            NoLinks(Absolute(assetPath)); NoLinks(Absolute(assetPath) + ".meta");
            var info = new FileInfo(IOPath(Absolute(assetPath))); string actualSha = HashFile(info.FullName);
            if (info.Length != records[0].bytes || actualSha != records[0].sha256) throw new InvalidDataException("Provider TerrainData differs from its current canonical receipt: " + relative);
            var metas = receipt.files.Where(file => file.path == relative + ".meta").ToArray();
            var metaInfo = new FileInfo(IOPath(Absolute(assetPath) + ".meta")); string metaSha = HashFile(metaInfo.FullName);
            string guid = AssetDatabase.AssetPathToGUID(assetPath).ToLowerInvariant(); var metaGuid = GuidLine.Match(File.ReadAllText(IOPath(metaInfo.FullName)));
            if (metas.Length != 1 || metas[0].sha256 != metaSha || metas[0].bytes != metaInfo.Length || !metaGuid.Success || metaGuid.Groups[1].Value.ToLowerInvariant() != guid || !Regex.IsMatch(guid, "^[a-f0-9]{32}$"))
                throw new InvalidDataException("Provider TerrainData metadata differs from canonical receipt or current asset GUID: " + relative);
            proof.excludedTargets.Add(new DependencyTarget { path = assetPath, guid = guid, canonicalSha256 = records[0].sha256, actualSha256 = actualSha, sourceArtifactSha256 = actualSha, bytes = info.Length,
                metadataPath = assetPath + ".meta", metadataBytes = metaInfo.Length, metadataSha256 = metaSha, canonicalMetadataSha256 = metas[0].sha256, checkedInboundReferences = -1 });
        }
        if (proof.excludedTargets.Count == 0) proof.status = "not-in-current-canonical-library";
        else {
            var excluded = new HashSet<string>(proof.excludedTargets.Select(target => target.path), StringComparer.Ordinal);
            string[] roots = AssetDatabase.GetAllAssetPaths().Where(path => InRoot(path) && !excluded.Contains(path) && !AssetDatabase.IsValidFolder(path) && !path.EndsWith(".meta", StringComparison.OrdinalIgnoreCase)).Distinct().OrderBy(path => path, StringComparer.Ordinal).ToArray();
            foreach (string path in roots) NoLinks(Absolute(path));
            proof.rootAssetsChecked = roots.Length; proof.rootPathsSha256 = HashText(string.Join("\n", roots));
            string[] closure = AssetDatabase.GetDependencies(roots, true).Distinct().OrderBy(path => path, StringComparer.Ordinal).ToArray();
            proof.dependencyClosurePaths = closure.Length; proof.closurePathsSha256 = HashText(string.Join("\n", closure));
            var closureSet = new HashSet<string>(closure, StringComparer.Ordinal);
            foreach (var target in proof.excludedTargets) {
                target.referencedByOtherRootAssets = closureSet.Contains(target.path);
                if (!target.referencedByOtherRootAssets) target.checkedInboundReferences = 0;
                var after = new FileInfo(IOPath(Absolute(target.path)));
                if (after.Length != target.bytes || HashFile(after.FullName) != target.actualSha256) throw new IOException("Provider TerrainData changed during dependency proof: " + target.path);
                var afterMeta = new FileInfo(IOPath(Absolute(target.metadataPath)));
                if (afterMeta.Length != target.metadataBytes || HashFile(afterMeta.FullName) != target.metadataSha256) throw new IOException("Provider TerrainData metadata changed during dependency proof: " + target.path);
            }
            proof.status = proof.excludedTargets.Any(target => target.referencedByOtherRootAssets) ? "referenced-by-other-root-assets" : "unreferenced-by-other-root-assets";
        }
        proof.completedUtc = Utc(); proof.elapsedSeconds = watch.Elapsed.TotalSeconds; return proof;
    }
    static string[] TerrainPaths()
    {
        return AssetDatabase.FindAssets("t:TerrainData", new[] { Root }).Select(AssetDatabase.GUIDToAssetPath).Distinct().OrderBy(path => path, StringComparer.Ordinal).ToArray();
    }
    static void FreshTerrainImports(Report report, string reportPath)
    {
        foreach (string path in TerrainPaths()) {
            NoLinks(Absolute(path)); NoLinks(Absolute(path) + ".meta");
            var watch = Stopwatch.StartNew();
            var item = new FreshImport { path = path, payloadBeforeSha256 = HashFile(Absolute(path)), metadataBeforeSha256 = HashFile(Absolute(path) + ".meta"), guidBefore = AssetDatabase.AssetPathToGUID(path) };
            report.freshTerrainImports.Add(item); SaveReport(reportPath, report);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
            item.payloadAfterSha256 = HashFile(Absolute(path)); item.metadataAfterSha256 = HashFile(Absolute(path) + ".meta"); item.guidAfter = AssetDatabase.AssetPathToGUID(path);
            item.elapsedSeconds = watch.Elapsed.TotalSeconds;
            if (item.payloadBeforeSha256 != item.payloadAfterSha256 || item.guidBefore != item.guidAfter) throw new InvalidDataException("Read-only fresh TerrainData import changed source payload/GUID: " + path);
            SaveReport(reportPath, report);
        }
    }

    // Callable by a controlled combined job. It never exits the Editor.
    public static string NormalizeOwnedTerrains(bool apply) { return RunInspection(apply, false); }
    public static string InspectDependenciesForControlledJob() { return RunInspection(false, true); }
    static string RunInspection(bool apply, bool dependencyProofOnly)
    {
        GuardOwnership();
        string workspace = Absolute("Library/YamyamAssetLibrary"), run = Path.Combine(workspace, "terrain-normalization", DateTime.UtcNow.ToString("yyyyMMddTHHmmss") + "-" + Guid.NewGuid().ToString("N"));
        NoLinks(run); Directory.CreateDirectory(IOPath(run));
        string reportPath = Path.Combine(run, "report.json");
        var report = new Report { project = Project, apply = apply, dependencyProofOnly = dependencyProofOnly, terrainSemanticsCaptured = !dependencyProofOnly, startedUtc = Utc(), runDirectory = run };
        var stopwatch = Stopwatch.StartNew();
        Application.LogCallback observeLog = (condition, stackTrace, type) => {
            if (type == LogType.Warning) { report.observedUnityWarnings++; if (report.warnings.Count < 2000) report.warnings.Add(condition); }
            else if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) {
                report.observedUnityErrors++; if (report.errors.Count < 2000) report.errors.Add(condition + "\n" + stackTrace);
            }
        };
        Application.logMessageReceived += observeLog;
        try {
            Guard();
            string manifestPath = Path.Combine(MainWork, "staging-manifest.json");
            if (!File.Exists(IOPath(manifestPath))) throw new FileNotFoundException("Canonical manifest missing", manifestPath);
            report.manifestPath = manifestPath; report.manifestSha256 = HashFile(manifestPath);
            var manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(IOPath(manifestPath)));
            if (manifest.products == null || manifest.products.Length != 84 || manifest.products.Select(p => p.id).Distinct().Count() != 84 || manifest.products.Any(p => p.status != "complete" || !Regex.IsMatch(p.folder ?? "", @"^[a-zA-Z0-9_-]+$")) ||
                !string.Equals(Path.GetFullPath(manifest.project), Path.GetFullPath(Path.Combine(Project, "../../..")), StringComparison.OrdinalIgnoreCase) ||
                !string.Equals(Path.GetFullPath(manifest.stageRoot), Path.GetFullPath(Absolute(Root)), StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("Canonical product ownership/root is incomplete or differs from this isolated root.");
            if (Environment.GetCommandLineArgs().Contains("-yamyamTerrainFreshImport")) FreshTerrainImports(report, reportPath);
            report.missingProviderTerrainDependencyProof = InspectProviderTerrainGroup(manifest);
            SaveReport(reportPath, report);
            if (dependencyProofOnly) {
                // This entry proves inbound asset dependencies only. Loading
                // every TerrainData here can raise unrelated vendor prototype
                // errors and does not strengthen the completed graph proof.
                if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity reported errors during the dependency-proof phase.");
                if (HashFile(manifestPath) != report.manifestSha256) throw new IOException("Canonical manifest changed during the dependency-proof phase.");
                report.scope = "Dependency proof only: optional explicitly requested fresh native imports, canonical payload/meta/GUID binding for the two provider TerrainData, and one recursive dependency closure over every other current library asset. No generic TerrainData loading, normalization, semantic scan, layer move or asset persistence follows this proof.";
                report.status = "dependency-proof-complete";
                return reportPath;
            }
            var dataByPath = new SortedDictionary<string, TerrainData>(StringComparer.Ordinal);
            var layerByPath = new SortedDictionary<string, LayerRecord>(StringComparer.Ordinal);
            foreach (string path in TerrainPaths()) {
                NoLinks(Absolute(path));
                var data = AssetDatabase.LoadAssetAtPath<TerrainData>(path);
                if (data == null) throw new InvalidDataException("Cannot load owned TerrainData: " + path);
                if (dataByPath.ContainsKey(path)) continue;
                dataByPath[path] = data;
                string owner = Owner(path, manifest.products);
                var terrain = new TerrainRecord { productId = owner, path = path, externalDependenciesBefore = ForeignDependencies(path) };
                terrain.before = Snapshot(data); terrain.payloadBeforeSha256 = HashFile(Absolute(path)); terrain.beforeSemanticSha256 = HashText(JsonUtility.ToJson(terrain.before));
                report.terrains.Add(terrain);
                foreach (var layer in data.terrainLayers) {
                    string layerPath = AssetDatabase.GetAssetPath(layer);
                    if (InRoot(layerPath)) continue;
                    if (!InGenerated(layerPath)) { report.blockers.Add("Unsupported external TerrainLayer: " + path + " -> " + layerPath); continue; }
                    LayerRecord record;
                    if (!layerByPath.TryGetValue(layerPath, out record)) {
                        record = new LayerRecord { path = layerPath, guid = AssetDatabase.AssetPathToGUID(layerPath).ToLowerInvariant() }; layerByPath[layerPath] = record;
                    }
                    if (!record.terrainOwners.Contains(owner)) record.terrainOwners.Add(owner);
                    if (!record.terrains.Contains(path)) record.terrains.Add(path);
                }
            }
            {
                foreach (string path in GeneratedLayerPaths().OrderBy(value => value, StringComparer.Ordinal)) {
                    NoLinks(path); string relative = path.Substring(Project.Length + 1).Replace('\\', '/');
                    if (!layerByPath.ContainsKey(relative)) layerByPath[relative] = new LayerRecord { path = relative, guid = AssetDatabase.AssetPathToGUID(relative).ToLowerInvariant(), orphan = true };
                }
            }
            foreach (var record in layerByPath.Values) {
                InspectLayerFile(record); report.layers.Add(record);
                if (record.orphan) { report.warnings.Add("Unreferenced by owned TerrainData; left outside library: " + record.path); continue; }
                if (record.terrainOwners.Count != 1) { report.blockers.Add("Generated layer has multiple observed product owners: " + record.path); continue; }
                record.assignedProductId = record.terrainOwners[0];
                string folder = manifest.products.Single(p => p.id == record.assignedProductId).folder;
                record.destination = Root + "/" + folder + "/Generated/TerrainLayers/" + Path.GetFileName(record.path);
                if (File.Exists(IOPath(Absolute(record.destination))) || File.Exists(IOPath(Absolute(record.destination) + ".meta"))) report.blockers.Add("Generated layer destination already exists: " + record.destination);
                if (record.missingTextureGuids.Count != 0) report.blockers.Add("Reachable generated layer has missing original texture GUIDs: " + record.path + " " + string.Join(",", record.missingTextureGuids));
                if (record.externalTexturePaths.Count != 0) report.blockers.Add("Reachable generated layer has texture dependencies outside library: " + record.path);
            }
            SaveReport(reportPath, report);
            if (report.blockers.Count != 0) throw new InvalidDataException("Terrain normalization has unresolved ownership/source dependencies. See report.");
            if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity reported errors during TerrainData inspection; see report.");
            if (apply) {
                report.status = "normalizing";
                var affected = new HashSet<string>(report.layers.Where(layer => !layer.orphan).SelectMany(layer => layer.terrains), StringComparer.Ordinal);
                foreach (var terrain in report.terrains.Where(item => affected.Contains(item.path))) { Backup(run, terrain.path); terrain.backup = Path.Combine(run, "backups", terrain.path); }
                foreach (var layer in report.layers.Where(item => !item.orphan)) Backup(run, layer.path);
                SaveReport(reportPath, report);
                foreach (var layer in report.layers.Where(item => !item.orphan)) {
                    if (HashFile(Absolute(layer.path)) != layer.payloadSha256 || HashFile(Absolute(layer.path) + ".meta") != layer.metadataSha256) throw new IOException("Generated layer changed during planning: " + layer.path);
                    EnsureFolder(Path.GetDirectoryName(layer.destination).Replace('\\', '/'));
                    layer.moveStarted = true; SaveReport(reportPath, report);
                    string error = AssetDatabase.MoveAsset(layer.path, layer.destination);
                    if (!string.IsNullOrEmpty(error)) throw new IOException("TerrainLayer MoveAsset: " + error);
                    layer.moved = true;
                    if (AssetDatabase.AssetPathToGUID(layer.destination).ToLowerInvariant() != layer.guid || HashFile(Absolute(layer.destination)) != layer.payloadSha256 || HashFile(Absolute(layer.destination) + ".meta") != layer.metadataSha256)
                        throw new InvalidDataException("Moved TerrainLayer bytes/GUID changed: " + layer.destination);
                    SaveReport(reportPath, report);
                }
                // Explicitly persist only TerrainData whose native legacy-layer
                // upgrade introduced an external generated TerrainLayer. Never save scenes.
                foreach (var terrain in report.terrains.Where(item => affected.Contains(item.path)).OrderBy(item => new FileInfo(IOPath(Absolute(item.path))).Length)) {
                    if (HashFile(Absolute(terrain.path)) != terrain.payloadBeforeSha256) throw new IOException("TerrainData source changed before scoped persistence: " + terrain.path);
                    terrain.saveStarted = true; SaveReport(reportPath, report);
                    // Moving an automatically upgraded legacy layer does not
                    // persist its reference in the legacy TerrainData source.
                    // Rebind the original exact GUID/localID sequence to the
                    // owned moved layers, then save this dirty native object
                    // before asking the serializer/importer to read from disk.
                    var nativeData = dataByPath[terrain.path];
                    var ownedLayers = new TerrainLayer[terrain.before.layers.Count];
                    for (int index = 0; index < ownedLayers.Length; index++) {
                        Ref expected = terrain.before.layers[index].asset;
                        string ownedPath = AssetDatabase.GUIDToAssetPath(expected.guid);
                        if (!InRoot(ownedPath)) throw new InvalidDataException("Original TerrainLayer GUID is not owned after move: " + expected.guid);
                        ownedLayers[index] = AssetDatabase.LoadAssetAtPath<TerrainLayer>(ownedPath);
                        var actual = Reference(ownedLayers[index]);
                        if (actual.guid != expected.guid || actual.localId != expected.localId || actual.type != expected.type)
                            throw new InvalidDataException("Original TerrainLayer GUID/localID differs before explicit native save: " + ownedPath);
                    }
                    nativeData.terrainLayers = ownedLayers;
                    terrain.layersRebound = true;
                    terrain.reboundSemanticSha256 = HashText(JsonUtility.ToJson(Snapshot(nativeData)));
                    if (terrain.reboundSemanticSha256 != terrain.beforeSemanticSha256)
                        throw new InvalidDataException("Explicit TerrainLayer rebind changed semantic state: " + terrain.path);
                    EditorUtility.SetDirty(nativeData);
                    terrain.dirtySaveStarted = true; SaveReport(reportPath, report);
                    AssetDatabase.SaveAssetIfDirty(nativeData);
                    if (EditorUtility.IsDirty(nativeData)) throw new InvalidDataException("Scoped native TerrainData save remains dirty: " + terrain.path);
                    terrain.dirtySaved = true;
                    terrain.postDirtySavePayloadSha256 = HashFile(Absolute(terrain.path)); SaveReport(reportPath, report);
                    AssetDatabase.ForceReserializeAssets(new[] { terrain.path }, ForceReserializeAssetsOptions.ReserializeAssets);
                    // Read the persisted native asset through a targeted import,
                    // rather than verifying only the pre-save in-memory object.
                    AssetDatabase.ImportAsset(terrain.path, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
                    terrain.saved = true;
                    var afterData = AssetDatabase.LoadAssetAtPath<TerrainData>(terrain.path);
                    terrain.after = Snapshot(afterData); terrain.afterSemanticSha256 = HashText(JsonUtility.ToJson(terrain.after)); terrain.payloadAfterSha256 = HashFile(Absolute(terrain.path));
                    terrain.externalDependenciesAfter = ForeignDependencies(terrain.path);
                    if (terrain.beforeSemanticSha256 != terrain.afterSemanticSha256) throw new InvalidDataException("Terrain semantic state changed after native persistence: " + terrain.path);
                    if (terrain.externalDependenciesAfter.Count != 0) throw new InvalidDataException("Terrain still depends on foreign Assets: " + terrain.path);
                    if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity reported errors during scoped terrain persistence; see report.");
                    SaveReport(reportPath, report);
                }
                foreach (var terrain in report.terrains.Where(item => !affected.Contains(item.path))) {
                    terrain.after = Snapshot(dataByPath[terrain.path]); terrain.afterSemanticSha256 = HashText(JsonUtility.ToJson(terrain.after)); terrain.payloadAfterSha256 = HashFile(Absolute(terrain.path));
                    terrain.externalDependenciesAfter = ForeignDependencies(terrain.path);
                    if (terrain.payloadAfterSha256 != terrain.payloadBeforeSha256 || terrain.afterSemanticSha256 != terrain.beforeSemanticSha256 || terrain.externalDependenciesAfter.Count != 0)
                        throw new InvalidDataException("Unmodified TerrainData changed or retains foreign dependencies: " + terrain.path);
                }
            }
            if (HashFile(manifestPath) != report.manifestSha256) throw new IOException("Canonical manifest changed during the controlled Terrain job.");
            report.status = apply ? "normalized" : "audit-pass";
        }
        catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); }
        finally {
            Application.logMessageReceived -= observeLog;
            report.completedUtc = Utc(); report.elapsedSeconds = stopwatch.Elapsed.TotalSeconds;
            SaveReport(reportPath, report); SaveReport(Path.Combine(workspace, "terrain-normalization-report.json"), report);
        }
        if (report.status == "failed") throw new InvalidOperationException("Terrain normalization refused/failed; evidence: " + reportPath);
        return reportPath;
    }
    public static void RunHeadless()
    {
        // Never exit an interactive or unrelated Editor after an unauthorized call.
        GuardOwnership();
        int exitCode = 0;
        try { NormalizeOwnedTerrains(Environment.GetCommandLineArgs().Contains("-yamyamTerrainApply")); }
        catch (Exception error) { UnityEngine.Debug.LogError(error); exitCode = 1; }
        EditorApplication.Exit(exitCode);
    }
    public static void RunDependencyProofHeadless()
    {
        GuardOwnership(); int exitCode = 0;
        try { InspectDependenciesForControlledJob(); }
        catch (Exception error) { UnityEngine.Debug.LogError(error); exitCode = 1; }
        EditorApplication.Exit(exitCode);
    }
}
