// Recover one positively identified source image; change two owned material maps only.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;
using FileInfo = YamyamAssetLibraryIO.Info;

public static class YamyamAssetLibraryTankTracks
{
    const string ExpectedProject = "D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string Root = "Assets/ThirdParty/YamyamAssetLibrary";
    const string Folder = "061-army-pack-cute-series";
    const string ProofSha = "a8bfecea9799683a44a886e2576b675a6f4120b8ea619cf877c0f6b8f9de3642";
    const string ImageSha = "8dd896179f5b684c73c5f2a68c794f03cd755806b613f7019a746c9308260000";
    const string TexturePath = Root + "/" + Folder + "/Generated/Textures/TankTracks.png";
    const string TextureGuid = "b438723bcf1d1d6fa2f0c8ec4f23b82f";
    [Serializable] public sealed class Record { public string path, sha256, guid; public long bytes; }
    [Serializable] public sealed class Target { public string path, sourceMaterial, sha256, metadataSha256, guid; public long bytes; }
    [Serializable] public sealed class Proof { public string kind, stageRoot, uniqueTrackImageSha256; public int sourceFbxCount, materialReferenceCount, uniqueTrackImageBytes; public bool actualAssetsModified, sourceArchivesModified; public Record[] sourceFbxFiles, generatedPrefabReferences; public Target[] generatedMaterials; }
    [Serializable] public sealed class MaterialChange { public string path, guid, beforeSha256, afterSha256, metadataSha256, unchangedSettingsSha256; public long localId; }
    [Serializable] public sealed class SourceState { public string model, material, color, scale, offset; }
    [Serializable] public sealed class Report
    {
        public int schemaVersion = 1, observedUnityErrors, sourceFbxVerified, importedSourceMaterialsValidated;
        public int textureWidth, textureHeight;
        public string kind = "verified-p061-embedded-tank-track-image-correction", status = "checking", startedUtc, completedUtc, project, sourceProofSha256 = ProofSha;
        public string texturePath = TexturePath, textureGuid = TextureGuid, textureSha256 = ImageSha, textureMetadataSha256, previewPath, previewPrefab;
        public string originalPreviewsSha256, originalRepresentative, originalRepresentativeImage, originalRepresentativeImageSha256;
        public string previewsAfterSha256, representativeAfterImageSha256;
        public bool originalRepresentativeDependsOnChangedMaterials, representativeRefreshed;
        public int unaffectedPreviewRecordsVerified, unaffectedPreviewImagesVerified;
        public string[] originalRepresentativeDependencies;
        public bool sourceArchivesModified, originalSourcesModified, prefabsModified, scenesOpened, unrelatedAssetsSaved;
        public bool texture2DVerified, sourceAssetsUnchanged, generatedPrefabsUnchanged;
        public string alphaDecision = "Keep opaque/AlphaClip0: exact source PNG alpha is255 at every pixel and all36 GLB track materials defaultOPAQUE; no cutoff or transparency is invented.";
        public List<MaterialChange> materials = new List<MaterialChange>();
        public List<SourceState> sourceMaterialStates = new List<SourceState>();
        public List<string> errors = new List<string>();
    }
    static string Project { get { return YamyamAssetLibraryIO.NormalPath(Path.GetDirectoryName(Application.dataPath)); } }
    static string Work { get { return YamyamAssetLibraryIO.NormalPath(Path.Combine(Project, "..")); } }
    static string Absolute(string path) { return Path.Combine(Project, path.Replace('/', Path.DirectorySeparatorChar)); }
    static string Hash(byte[] bytes) { using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(); }
    static string HashFile(string path) { using (var input = File.OpenRead(path)) using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(input)).Replace("-", "").ToLowerInvariant(); }
    static void Guard() { if (!Application.isBatchMode || Application.unityVersion != "6000.6.0f1" || !Project.Replace('\\', '/').Equals(ExpectedProject, StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Tank-track recovery requires the exact isolated Unity6000.6 batch project."); }
    static void NoLinks(string path)
    {
        string full = YamyamAssetLibraryIO.NormalPath(path);
        if (!full.StartsWith(Work + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("Path escaped owned workspace.");
        for (string current = full; !string.IsNullOrEmpty(current); current = Path.GetDirectoryName(current)) {
            try { if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0) throw new IOException("Reparse point refused."); } catch (FileNotFoundException) { } catch (DirectoryNotFoundException) { }
            if (current.Equals(Path.GetPathRoot(full), StringComparison.OrdinalIgnoreCase)) return;
        }
        throw new IOException("Ancestor guard did not finish.");
    }
    static string GuidAt(string path) { var match = Regex.Match(File.ReadAllText(path), @"(?m)^guid:[ \t]*([a-f0-9]{32})[ \t]*\r?$"); if (!match.Success) throw new InvalidDataException("Metadata GUID missing."); return match.Groups[1].Value; }
    static string F(float value) { return value.ToString("R", CultureInfo.InvariantCulture); }
    static string V(Vector2 value) { return F(value.x) + "," + F(value.y); }
    static string C(Color value) { return F(value.r) + "," + F(value.g) + "," + F(value.b) + "," + F(value.a); }
    static Color Tint(Material material) { return material.GetColor(material.HasProperty("_BaseColor") ? "_BaseColor" : "_Color"); }
    static string ColorMapProperty(Material material) { return material.HasProperty("_BaseMap") ? "_BaseMap" : "_MainTex"; }
    static string OtherSettings(Material material)
    {
        var text = new StringBuilder(material.name + "|" + material.shader.name + "|" + material.renderQueue + "|" + material.enableInstancing + "|" + material.doubleSidedGI + "|" + (int)material.globalIlluminationFlags);
        foreach (string word in material.shaderKeywords.OrderBy(value => value, StringComparer.Ordinal)) text.Append('|').Append(word);
        for (int index = 0; index < material.passCount; index++) { string name = material.GetPassName(index); text.Append('|').Append(name).Append(':').Append(material.GetShaderPassEnabled(name)); }
        for (int index = 0; index < material.shader.GetPropertyCount(); index++) {
            string name = material.shader.GetPropertyName(index); var type = material.shader.GetPropertyType(index); text.Append('|').Append(name).Append('=');
            if (type == ShaderPropertyType.Texture) {
                if (name != "_BaseMap") { Texture texture = material.GetTexture(name); string guid; long local;
                    text.Append(!texture ? "null" : AssetDatabase.TryGetGUIDAndLocalFileIdentifier(texture, out guid, out local) ? guid + ":" + local : texture.name + ":" + texture.GetType().FullName); }
                text.Append('|').Append(V(material.GetTextureScale(name))).Append('|').Append(V(material.GetTextureOffset(name)));
            } else if (type == ShaderPropertyType.Color || type == ShaderPropertyType.Vector) { Vector4 value = material.GetVector(name); for (int part = 0; part < 4; part++) text.Append(F(value[part])).Append(','); }
            else if (type == ShaderPropertyType.Int) text.Append(material.GetInt(name)); else text.Append(F(material.GetFloat(name)));
        }
        return text.ToString();
    }
    static void WriteAtomic(string path, string json)
    {
        NoLinks(path); Directory.CreateDirectory(Path.GetDirectoryName(path)); string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        File.WriteAllText(temporary, json + "\n", new UTF8Encoding(false));
        for (int attempt = 0; ; attempt++) { try { if (File.Exists(path)) File.Replace(temporary, path, null); else File.Move(temporary, path); return; }
            catch (IOException error) { int code = error.HResult & 0xffff; if (attempt >= 4 || !(code == 5 || code == 32 || code == 33 || code == 1175)) throw; }
            catch (UnauthorizedAccessException) { if (attempt >= 4) throw; } System.Threading.Thread.Sleep(100 * (attempt + 1)); }
    }
    static void SaveReport(string path, Report report) { WriteAtomic(path, JsonUtility.ToJson(report, true)); }
    static void VerifyPayloads(Record[] files) { foreach (var file in files) { string path = Absolute(Root + "/" + file.path); NoLinks(path); if (new FileInfo(path).Length != file.bytes || HashFile(path) != file.sha256) throw new InvalidDataException("Source/prefab payload changed: " + file.path); } }
    static void RenderPreview(string path, string image)
    {
        RenderRecord(new YamyamAssetLibraryBridge.PreviewRecord { assetPath = path, imagePath = image, kind = "verified-source-image-tank-track-correction" });
    }
    static void RenderRecord(YamyamAssetLibraryBridge.PreviewRecord record)
    {
        Type bridge = typeof(YamyamAssetLibraryBridge); record.drawCalls = 0; record.visiblePixels = 0; record.magentaLikePixels = 0; record.totalPixels = 0; record.error = null;
        object[] arguments = { AssetDatabase.LoadAssetAtPath<GameObject>(record.assetPath), new Bounds() }; object draws = bridge.GetMethod("Draws", BindingFlags.Static | BindingFlags.NonPublic).Invoke(null, arguments);
        bridge.GetMethod("RenderPreview", BindingFlags.Static | BindingFlags.NonPublic).Invoke(null, new[] { draws, arguments[1], record });
        if (!string.IsNullOrEmpty(record.error) || !File.Exists(record.imagePath)) throw new IOException("Tank-track preview failed: " + record.error);
    }
    static void Run()
    {
        Guard(); if (EditorApplication.isUpdating || EditorApplication.isCompiling) throw new InvalidOperationException("Editor must be idle.");
        string local = Path.Combine(Project, "Library/YamyamAssetLibrary"), run = Path.Combine(local, "tank-track-correction", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N")); NoLinks(run); Directory.CreateDirectory(run);
        string reportPath = Path.Combine(run, "report.json"); var report = new Report { project = Project, startedUtc = DateTime.UtcNow.ToString("o") };
        Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } }; Application.logMessageReceived += capture;
        try {
            string evidence = Path.Combine(Work, "product061-tank-track-source-evidence.json"); NoLinks(evidence); if (HashFile(evidence) != ProofSha) throw new InvalidDataException("Reviewed track source evidence changed.");
            var proof = JsonUtility.FromJson<Proof>(File.ReadAllText(evidence));
            if (proof.kind != "verified-p061-embedded-tank-track-image" || proof.actualAssetsModified || proof.sourceArchivesModified || proof.sourceFbxCount != 18 || proof.materialReferenceCount != 36 || proof.uniqueTrackImageSha256 != ImageSha || proof.uniqueTrackImageBytes != 7409
                || proof.sourceFbxFiles == null || proof.sourceFbxFiles.Length != 18 || proof.generatedMaterials == null || proof.generatedMaterials.Length != 2 || proof.generatedPrefabReferences == null || proof.generatedPrefabReferences.Length != 18
                || !YamyamAssetLibraryIO.NormalPath(proof.stageRoot).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(Root)), StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Unreviewed track proof scope.");
            VerifyPayloads(proof.sourceFbxFiles); VerifyPayloads(proof.generatedPrefabReferences); report.sourceFbxVerified = 18;
            string imageFile = Path.Combine(Work, "helper-candidates/tank-tracks/source-image/TankTracks.png"); NoLinks(imageFile); byte[] encoded = File.ReadAllBytes(imageFile); if (encoded.Length != 7409 || Hash(encoded) != ImageSha) throw new InvalidDataException("Recovered PNG is not the exact proved source image.");
            var targets = proof.generatedMaterials.ToDictionary(value => value.sourceMaterial, StringComparer.Ordinal); var loaded = new Dictionary<string, Material>(); var settings = new Dictionary<string, string>();
            foreach (string name in new[] { "TankTracks_L", "TankTracks_R" }) {
                var target = targets[name]; if (!target.path.StartsWith(Folder + "/Generated/Materials/", StringComparison.Ordinal) || Path.GetFileNameWithoutExtension(target.path).Split('_').Length < 3) throw new InvalidDataException("Target material escaped proved generated folder.");
                string path = Root + "/" + target.path, physical = Absolute(path), meta = physical + ".meta"; NoLinks(physical); NoLinks(meta);
                if (HashFile(physical) != target.sha256 || HashFile(meta) != target.metadataSha256 || GuidAt(meta) != target.guid || AssetDatabase.AssetPathToGUID(path) != target.guid) throw new InvalidDataException("Reviewed generated material bytes/GUID changed.");
                Material material = AssetDatabase.LoadAssetAtPath<Material>(path); string guid; long id;
                if (!material || material.shader.name != "Universal Render Pipeline/Lit" || material.name != Path.GetFileNameWithoutExtension(path) || material.GetTexture("_BaseMap") || material.GetFloat("_Surface") != 0 || material.GetFloat("_AlphaClip") != 0
                    || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out id) || guid != target.guid) throw new InvalidDataException("Track material is not the proved opaque untextured target.");
                File.Copy(physical, Path.Combine(run, name + ".before.mat"), false); File.Copy(meta, Path.Combine(run, name + ".before.mat.meta"), false);
                if (HashFile(Path.Combine(run, name + ".before.mat")) != target.sha256 || HashFile(Path.Combine(run, name + ".before.mat.meta")) != target.metadataSha256) throw new IOException("Material backup verification failed.");
                loaded.Add(name, material); settings.Add(name, OtherSettings(material)); report.materials.Add(new MaterialChange { path = path, guid = guid, localId = id, beforeSha256 = target.sha256, metadataSha256 = target.metadataSha256, unchangedSettingsSha256 = Hash(Encoding.UTF8.GetBytes(settings[name])) });
            }
            foreach (var source in proof.sourceFbxFiles) {
                string path = Root + "/" + source.path; GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(path); if (!model) throw new InvalidDataException("Source tank model failed to load.");
                var found = new HashSet<string>();
                foreach (Material material in model.GetComponentsInChildren<Renderer>(true).SelectMany(renderer => renderer.sharedMaterials).Where(material => material && targets.ContainsKey(material.name)).Distinct()) {
                    string name = material.name, property = ColorMapProperty(material); Material target = loaded[name];
                    if (material.GetTexture(property) || Tint(material) != Tint(target) || material.GetTextureScale(property) != target.GetTextureScale("_BaseMap") || material.GetTextureOffset(property) != target.GetTextureOffset("_BaseMap")) throw new InvalidDataException("Imported source track tint/UV differs from generated material; no correction was guessed.");
                    found.Add(name); report.sourceMaterialStates.Add(new SourceState { model = path, material = name, color = C(Tint(material)), scale = V(material.GetTextureScale(property)), offset = V(material.GetTextureOffset(property)) });
                }
                if (found.Count != 2) throw new InvalidDataException("Expected both source track material names in every proved tank model."); report.importedSourceMaterialsValidated += 2;
            }
            string previewsPath = Path.Combine(local, "previews.json"); NoLinks(previewsPath);
            var previews = JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));
            if (previews.products == null || previews.products.Count != 84 || string.IsNullOrEmpty(previews.completedUtc)) throw new InvalidDataException("Completed84-product preview evidence required.");
            var representative = previews.products.Single(value => value.id == "061");
            if (!string.IsNullOrEmpty(representative.error) || string.IsNullOrEmpty(representative.assetPath) || string.IsNullOrEmpty(representative.imagePath)) throw new InvalidDataException("P061 representative preview incomplete.");
            NoLinks(representative.imagePath); report.originalPreviewsSha256 = HashFile(previewsPath); report.originalRepresentative = representative.assetPath; report.originalRepresentativeImage = representative.imagePath; report.originalRepresentativeImageSha256 = HashFile(representative.imagePath);
            report.originalRepresentativeDependencies = AssetDatabase.GetDependencies(representative.assetPath, true).Distinct().OrderBy(path => path, StringComparer.Ordinal).ToArray();
            report.originalRepresentativeDependsOnChangedMaterials = report.materials.Any(change => report.originalRepresentativeDependencies.Contains(change.path, StringComparer.Ordinal));
            var otherPreviewRows = previews.products.Where(value => value.id != "061").ToDictionary(value => value.id, value => Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(value))), StringComparer.Ordinal);
            var otherPreviewImages = previews.products.Where(value => value.id != "061").ToDictionary(value => value.id, value => { NoLinks(value.imagePath); return HashFile(value.imagePath); }, StringComparer.Ordinal);
            File.Copy(previewsPath, Path.Combine(run, "previews.before.json"), false);
            if (HashFile(Path.Combine(run, "previews.before.json")) != report.originalPreviewsSha256) throw new IOException("Preview report backup verification failed.");
            if (report.originalRepresentativeDependsOnChangedMaterials) { File.Copy(representative.imagePath, Path.Combine(run, "P061-representative.before.png"), false); if (HashFile(Path.Combine(run, "P061-representative.before.png")) != report.originalRepresentativeImageSha256) throw new IOException("P061 representative backup verification failed."); }
            if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity errors occurred before the first owned asset mutation.");
            string textureFile = Absolute(TexturePath), textureMeta = textureFile + ".meta"; NoLinks(textureFile); NoLinks(textureMeta);
            if (File.Exists(textureFile) || File.Exists(textureMeta) || !string.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(TextureGuid))) throw new IOException("Recovered texture destination/GUID already exists; refuse overwrite.");
            string folder = Root + "/" + Folder + "/Generated/Textures"; if (!AssetDatabase.IsValidFolder(folder)) AssetDatabase.CreateFolder(Root + "/" + Folder + "/Generated", "Textures");
            report.status = "creating-proved-source-image"; SaveReport(reportPath, report);
            File.WriteAllText(textureMeta, "fileFormatVersion: 2\nguid: " + TextureGuid + "\nTextureImporter:\n  externalObjects: {}\n  serializedVersion: 13\n  textureShape: 1\n", new UTF8Encoding(false)); File.WriteAllBytes(textureFile, encoded);
            AssetDatabase.ImportAsset(TexturePath, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
            var importer = AssetImporter.GetAtPath(TexturePath) as TextureImporter; if (importer == null) throw new InvalidDataException("Recovered texture importer unavailable.");
            importer.textureShape = TextureImporterShape.Texture2D; importer.textureType = TextureImporterType.Default; importer.sRGBTexture = true; importer.alphaSource = TextureImporterAlphaSource.FromInput; importer.alphaIsTransparency = false;
            importer.wrapModeU = TextureWrapMode.Repeat; importer.wrapModeV = TextureWrapMode.Repeat; importer.filterMode = FilterMode.Trilinear; importer.maxTextureSize = 2048;
            importer.npotScale = TextureImporterNPOTScale.None; importer.mipmapEnabled = true; importer.textureCompression = TextureImporterCompression.Uncompressed; importer.SaveAndReimport();
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(TexturePath);
            importer = AssetImporter.GetAtPath(TexturePath) as TextureImporter;
            if (!texture || texture.width != 128 || texture.height != 72 || AssetDatabase.GetMainAssetTypeAtPath(TexturePath) != typeof(Texture2D) || GuidAt(textureMeta) != TextureGuid || AssetDatabase.AssetPathToGUID(TexturePath) != TextureGuid || HashFile(textureFile) != ImageSha
                || importer == null || importer.textureShape != TextureImporterShape.Texture2D || importer.textureType != TextureImporterType.Default || !importer.sRGBTexture || importer.alphaIsTransparency || importer.npotScale != TextureImporterNPOTScale.None || !importer.mipmapEnabled
                || importer.wrapModeU != TextureWrapMode.Repeat || importer.wrapModeV != TextureWrapMode.Repeat || importer.filterMode != FilterMode.Trilinear || importer.textureCompression != TextureImporterCompression.Uncompressed) throw new InvalidDataException("Recovered texture type/dimensions/payload/GUID/sampler verification failed.");
            report.texture2DVerified = true; report.textureWidth = texture.width; report.textureHeight = texture.height;
            report.textureMetadataSha256 = HashFile(textureMeta); report.status = "assigning-two-proved-material-maps"; SaveReport(reportPath, report);
            foreach (var change in report.materials) {
                Material material = loaded[targets.Values.Single(value => Root + "/" + value.path == change.path).sourceMaterial]; material.SetTexture("_BaseMap", texture); EditorUtility.SetDirty(material); AssetDatabase.SaveAssetIfDirty(material);
                AssetDatabase.ImportAsset(change.path, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport); material = AssetDatabase.LoadAssetAtPath<Material>(change.path); string guid; long id;
                string name = targets.Values.Single(value => Root + "/" + value.path == change.path).sourceMaterial;
                if (!material || material.GetTexture("_BaseMap") != texture || OtherSettings(material) != settings[name] || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material, out guid, out id) || guid != change.guid || id != change.localId
                    || HashFile(Absolute(change.path) + ".meta") != change.metadataSha256) throw new InvalidDataException("Persistent material map/unchanged settings/identity verification failed.");
                change.afterSha256 = HashFile(Absolute(change.path)); if (change.afterSha256 == change.beforeSha256) throw new InvalidDataException("Material map assignment did not persist.");
            }
            VerifyPayloads(proof.sourceFbxFiles); VerifyPayloads(proof.generatedPrefabReferences);
            report.sourceAssetsUnchanged = true; report.generatedPrefabsUnchanged = true;
            if (HashFile(textureFile) != ImageSha || GuidAt(textureMeta) != TextureGuid || HashFile(textureMeta) != report.textureMetadataSha256) throw new IOException("Recovered source image/metadata changed.");
            report.previewPrefab = Root + "/" + proof.generatedPrefabReferences.First(value => value.path.Contains("/Tank_1_A_")).path; report.previewPath = Path.Combine(run, "P061-Tank1A-recovered-tracks.png"); RenderPreview(report.previewPrefab, report.previewPath);
            if (HashFile(previewsPath) != report.originalPreviewsSha256) throw new IOException("Preview report changed concurrently before a scoped refresh.");
            if (report.originalRepresentativeDependsOnChangedMaterials) { RenderRecord(representative); WriteAtomic(previewsPath, JsonUtility.ToJson(previews, true)); report.representativeRefreshed = true; }
            else if (HashFile(representative.imagePath) != report.originalRepresentativeImageSha256) throw new IOException("Unaffected P061 representative image changed.");
            var currentPreviews = JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));
            if (currentPreviews.products.Count != 84) throw new IOException("Preview scope count changed.");
            foreach (var value in currentPreviews.products.Where(value => value.id != "061")) {
                if (Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(value))) != otherPreviewRows[value.id]) throw new IOException("An unrelated preview record changed."); report.unaffectedPreviewRecordsVerified++;
                if (HashFile(value.imagePath) != otherPreviewImages[value.id]) throw new IOException("An unrelated preview image changed."); report.unaffectedPreviewImagesVerified++;
            }
            if (report.unaffectedPreviewRecordsVerified != 83 || report.unaffectedPreviewImagesVerified != 83) throw new IOException("Expected exact83 unaffected preview rows/images.");
            report.previewsAfterSha256 = HashFile(previewsPath); report.representativeAfterImageSha256 = HashFile(representative.imagePath);
            if (report.observedUnityErrors != 0) throw new InvalidDataException("Unity reported errors during scoped track correction/preview."); report.status = "complete";
        } catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); throw; }
        finally { Application.logMessageReceived -= capture; report.completedUtc = DateTime.UtcNow.ToString("o"); SaveReport(reportPath, report); SaveReport(Path.Combine(local, "tank-track-correction-report.json"), report); }
    }
    public static void RunHeadless() { Guard(); int code = 0; try { Run(); } catch (Exception error) { Debug.LogError(error); code = 1; } EditorApplication.Exit(code); }
}
