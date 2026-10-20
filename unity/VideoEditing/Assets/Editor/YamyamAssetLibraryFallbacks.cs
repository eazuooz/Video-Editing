using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;

/// <summary>Incremental, non-destructive FBX/PBR preparation for the downloaded asset library.</summary>
public static class YamyamAssetLibraryFallbacks
{
    [Serializable] sealed class Manifest { public string targetAssetsRoot; public Product[] products; }
    [Serializable] sealed class Product { public int index; public string id, title, folder, assetPath, targetAssetPath; }
    [Serializable] public sealed class Issue { public int product; public string code, path, detail; }
    [Serializable] public sealed class ModelEvidence { public int product, renderers, materialSlots, unresolvedSlots; public string model, prefab; }
    [Serializable] public sealed class MaterialEvidence { public int product; public string material, sourceMaterial, baseColor, resolution; }
    [Serializable] public sealed class VerifiedSourceRepair { public int product, replacementSlot, referenceSlot; public long rendererLocalId; public string kind, model, sourceMaterial, sourceSha256, sourceProofSha256; }
    [Serializable] public sealed class Report
    {
        public string status, startedUtc, completedUtc, unityVersion, pipeline, lastError;
        public int jobsTotal, jobsCompleted, texturesConfigured, materialsCreated, prefabsCreated, animationOnlyModels;
        public List<Issue> issues = new List<Issue>();
        public List<ModelEvidence> models = new List<ModelEvidence>();
        public List<MaterialEvidence> materials = new List<MaterialEvidence>();
        public List<VerifiedSourceRepair> verifiedSourceRepairs = new List<VerifiedSourceRepair>();
    }
    sealed class Pack { public Product product; public string root; public List<string> textures = new List<string>(); }
    sealed class Job { public Pack pack; public string path, kind; }
    static readonly HashSet<int> FallbackIndices = new HashSet<int> { 7, 8, 11, 13, 19, 46, 48, 53, 55, 60, 61, 67, 74, 76, 77, 80, 81, 82 };
    static readonly Queue<Job> Jobs = new Queue<Job>();
    // Keep identities, not native Material objects: a large library must not pin every texture.
    static readonly Dictionary<string, string> MaterialCache = new Dictionary<string, string>();
    static readonly HashSet<string> IssueKeys = new HashSet<string>();
    static Report report;
    static Scene preview;
    static string reportPath;
    static bool running;
    public static bool IsRunning { get { return running; } }
    public static string ReportPath { get { return reportPath; } }
    public static string LastError { get { return report == null ? null : report.lastError; } }
    public static string StatusJson { get { return report == null ? "{}" : JsonUtility.ToJson(report, true); } }

    static YamyamAssetLibraryFallbacks()
    {
        AssemblyReloadEvents.beforeAssemblyReload += BeforeReload;
        EditorApplication.quitting += BeforeReload;
    }

    public static void Begin(string manifestPath)
    {
        if (running) throw new InvalidOperationException("Fallback builder already running.");
        Jobs.Clear(); MaterialCache.Clear(); IssueKeys.Clear();
        reportPath = Path.Combine(Path.GetDirectoryName(Path.GetFullPath(manifestPath)), "fallback-preparation-report.json");
        report = new Report { status = "preparing", startedUtc = DateTime.UtcNow.ToString("o"), unityVersion = Application.unityVersion, pipeline = "Universal Render Pipeline/Lit" };
        try
        {
            var manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(manifestPath));
            if (manifest == null || manifest.products == null) throw new InvalidDataException("Manifest needs products[].");
            foreach (var product in manifest.products.Where(p => FallbackIndices.Contains(p.index)))
            {
                string root = product.assetPath ?? product.targetAssetPath;
                if (String.IsNullOrEmpty(root)) root = (manifest.targetAssetsRoot ?? "Assets/ThirdParty/YamyamAssetLibrary").TrimEnd('/') + "/" + product.folder;
                root = root.Replace('\\', '/').TrimEnd('/');
                if (!root.StartsWith("Assets/ThirdParty/YamyamAssetLibrary/", StringComparison.Ordinal) || root.Contains(".."))
                    throw new InvalidDataException("Unsafe product assetPath: " + root);
                if (!AssetDatabase.IsValidFolder(root)) { AddIssue(product.index, "missing-pack-root", root, "No imported asset folder exists; fallback preparation skipped."); continue; }
                var pack = new Pack { product = product, root = root };
                pack.textures = AssetDatabase.FindAssets("t:Texture2D", new[] { root }).Select(AssetDatabase.GUIDToAssetPath)
                    .Where(p => !p.Contains("/Generated/")).Distinct().OrderBy(p => p, StringComparer.Ordinal).ToList();
                foreach (var path in pack.textures) Jobs.Enqueue(new Job { pack = pack, path = path, kind = "texture" });
                if (product.index == 46)
                    foreach (var path in pack.textures.Where(p => Regex.IsMatch(Path.GetFileNameWithoutExtension(p), @"Plasticine_\d+_8K_BaseColor$", RegexOptions.IgnoreCase)))
                        Jobs.Enqueue(new Job { pack = pack, path = path, kind = "pbr" });
                foreach (var path in AssetDatabase.FindAssets("t:Model", new[] { root }).Select(AssetDatabase.GUIDToAssetPath)
                    .Where(p => p.EndsWith(".fbx", StringComparison.OrdinalIgnoreCase) && !p.Contains("/Generated/")).Distinct().OrderBy(p => p, StringComparer.Ordinal))
                    Jobs.Enqueue(new Job { pack = pack, path = path, kind = "model" });
            }
            preview = EditorSceneManager.NewPreviewScene();
            report.jobsTotal = Jobs.Count; report.status = "running"; running = true; WriteReport();
        }
        catch (Exception e) { Fail(e); throw; }
    }

    /// <returns>True when completed or failed. Call only while the editor is not compiling/updating.</returns>
    public static bool Tick(int maxModels = 2)
    {
        if (!running) return true;
        if (EditorApplication.isCompiling || EditorApplication.isUpdating) return false;
        try
        {
            for (int i = 0; i < Math.Max(1, maxModels) && Jobs.Count > 0; i++)
            {
                var job = Jobs.Dequeue();
                try
                {
                    if (job.kind == "texture") ConfigureTexture(job.path);
                    else if (job.kind == "pbr") BuildPlasticine(job.pack, job.path);
                    else BuildModel(job.pack, job.path);
                }
                catch (Exception e) { AddIssue(job.pack.product.index, "job-error", job.path, e.ToString()); }
                report.jobsCompleted++;
            }
            if (Jobs.Count > 0) { if (report.jobsCompleted % 100 < Math.Max(1, maxModels)) WriteReport(); return false; }
            ClosePreview(); running = false;
            report.status = report.issues.Count == 0 ? "completed" : "completed-with-issues";
            report.completedUtc = DateTime.UtcNow.ToString("o"); WriteReport(); return true;
        }
        catch (Exception e) { Fail(e); return true; }
    }

    static void ConfigureTexture(string path)
    {
        var importer = AssetImporter.GetAtPath(path) as TextureImporter;
        if (importer == null) return;
        string name = Path.GetFileNameWithoutExtension(path).ToLowerInvariant();
        bool normal = IsNormal(name), data = IsDataMap(name);
        bool changed = importer.maxTextureSize != 2048;
        importer.maxTextureSize = 2048;
        if (normal && importer.textureType != TextureImporterType.NormalMap) { importer.textureType = TextureImporterType.NormalMap; changed = true; }
        if ((normal || data) && importer.sRGBTexture) { importer.sRGBTexture = false; changed = true; }
        if (changed) { importer.SaveAndReimport(); report.texturesConfigured++; }
    }
    static bool IsNormal(string n) { return n.Contains("normal") || n.Contains("_nmp") || n.EndsWith("_nrm", StringComparison.Ordinal); }
    static bool IsDataMap(string n) { return n.Contains("metallic") || n.Contains("roughness") || n.Contains("smoothness") || n.Contains("occlusion") || n.EndsWith("_ao", StringComparison.Ordinal) || n.Contains("maskmap"); }
    static bool IsColorMap(string p)
    {
        string n = Path.GetFileNameWithoutExtension(p).ToLowerInvariant();
        return !IsNormal(n) && !IsDataMap(n) && !n.Contains("height") && !n.Contains("displacement") && !n.Contains("emission") && !n.Contains("specular");
    }
    static string Normalize(string name)
    {
        name = Regex.Replace(name.ToLowerInvariant(), @"\s*\(instance\)$", "");
        name = Regex.Replace(name, @"(^mat(?:erial)?[_\s-]+|[_\s-]+mat(?:erial)?$)", "");
        name = Regex.Replace(name, @"([_\s-]+(?:basecolor|base_color|albedo|diffuse|diff|color|colour|[248]k))+$", "");
        return Regex.Replace(name, "[^a-z0-9]", "");
    }
    static string MatchColor(Pack pack, string sourceName)
    {
        string normalized = Normalize(sourceName);
        if (normalized.Length < 3) return null;
        var matches = pack.textures.Where(IsColorMap).Where(p => Normalize(Path.GetFileNameWithoutExtension(p)) == normalized).ToArray();
        return matches.Length == 1 ? matches[0] : null;
    }
    static Texture GetTexture(Material m, params string[] names)
    {
        foreach (string n in names) if (m.HasProperty(n) && m.GetTexture(n)) return m.GetTexture(n);
        return null;
    }
    static float GetFloat(Material m, float fallback, params string[] names)
    {
        foreach (string n in names) if (m.HasProperty(n)) return m.GetFloat(n);
        return fallback;
    }
    static Color GetColor(Material m, Color fallback, params string[] names)
    {
        foreach (string n in names) if (m.HasProperty(n)) return m.GetColor(n);
        return fallback;
    }
    static string ShortHash(string text)
    {
        using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(text))).Replace("-", "").Substring(0, 12).ToLowerInvariant();
    }
    static string SafeName(string text)
    {
        string value = Regex.Replace(text ?? "asset", @"[^\w.-]+", "_");
        return value.Length > 80 ? value.Substring(0, 80) : value;
    }
    static void EnsureFolder(string path)
    {
        var parts = path.Split('/'); string current = parts[0];
        for (int i = 1; i < parts.Length; i++) { string next = current + "/" + parts[i]; if (!AssetDatabase.IsValidFolder(next)) AssetDatabase.CreateFolder(current, parts[i]); current = next; }
    }
    static string TextureIdentity(Texture t) { return t ? AssetDatabase.GetAssetPath(t) + "#" + t.name : ""; }

    // All388P008FBX files were checked: these5exports share this exact explicit
    // untextured tint/opacity. Never infer transparency from arbitrary alpha alone.
    static bool VerifiedP008Glass(Pack pack, string modelPath, Material source, Color tint, Texture color)
    {
        const string root = "Assets/ThirdParty/YamyamAssetLibrary/008-polyvania-halloween-burton-town-948-spooky-low-poly-town-models-godot-unity-bl";
        if (pack.product.index != 8 || pack.root != root || source.name != "Transylvania_Glass_Text" || color
            || Mathf.Abs(tint.r - .42f) >= .00001f || Mathf.Abs(tint.g - .6f) >= .00001f || Mathf.Abs(tint.b - .66f) >= .00001f || Mathf.Abs(tint.a - .28f) >= .00001f) return false;
        return new[] { "EA_Tr_Door_01a", "EA_Tr_House_01a", "EA_Tr_House_01b", "EA_Tr_House_01c", "EA_Tr_House_01d" }
            .Any(name => modelPath == root + "/Fbx Lods/" + name + ".fbx");
    }
    static void ValidateOfficialLit(Material material)
    {
        Type type = AppDomain.CurrentDomain.GetAssemblies().Select(assembly => assembly.GetType("UnityEditor.Rendering.Universal.ShaderGUI.LitShader", false)).FirstOrDefault(value => value != null);
        var validator = type == null ? null : Activator.CreateInstance(type, true) as ShaderGUI;
        if (validator == null) throw new InvalidOperationException("Installed official URP Lit validator is unavailable for verifiedP008glass.");
        validator.ValidateMaterial(material);
    }
    static void ValidateVerifiedGlass(Material material)
    {
        material.SetFloat("_Surface", 1); material.SetFloat("_Blend", 0); material.SetFloat("_AlphaClip", 0);
        ValidateOfficialLit(material);
    }

    const string HairRoot = "Assets/ThirdParty/YamyamAssetLibrary/011-cartoon-city-massive-pack-characters-unity-godot-fbx";
    const string HairProofSha256 = "26abd521aba83171d2ce26dcc981af41107655017ff85651f91fc3228b5d1c46";
    sealed class HairSource { public string sha256, guid; public long bytes, rendererId; }
    static readonly Dictionary<string, HairSource> HairSources = new Dictionary<string, HairSource>(StringComparer.Ordinal)
    {
        { "Character_2_2_1", new HairSource { sha256 = "5a8f86249da514d0a0078b65e9e65930636a3933ad74aa40716ef311a8518e3a", bytes = 263552, guid = "57b5b7b010ecaab425c05b27d2f77a97", rendererId = -3227881213038258786L } },
        { "Character_2_2_10", new HairSource { sha256 = "a598cdd2aae355d37062459c1966ba0f664aba7e8abe8a1da1d7834014192195", bytes = 263568, guid = "258a00c1a40e681be4a18de08fead99e", rendererId = 4303956338540726421L } },
        { "Character_2_2_11", new HairSource { sha256 = "57cb2ec88fc4aa226f21f4725ddedfbf33a83f2f1eb7d7f92fb017bad2234c48", bytes = 263728, guid = "d44705c9323c626dbe437ef760da6224", rendererId = 3181205314977312725L } },
        { "Character_2_2_2", new HairSource { sha256 = "b2d235286778c5c10b46ca33a650b3bb9e2b44df872c19c9d65023ebf10ee234", bytes = 263616, guid = "7227172b62be0e4df90c1a845b153b17", rendererId = 215999548822911404L } },
        { "Character_2_2_3", new HairSource { sha256 = "11166fef0a50ffd49258219914a8203c71269dbd3925c4cfb1487e134aecd74e", bytes = 263536, guid = "21054d70bb399db5862cac2b5dc6b2a8", rendererId = 3239822295029715817L } },
        { "Character_2_2_4", new HairSource { sha256 = "dd341b51557039a9099b4dcdd591d1310b17daf9bbb29a6b0e19074f7ad5ff1b", bytes = 263472, guid = "a7c35af3f8a264b03442264d2d0a57a6", rendererId = 1669564698272902938L } },
        { "Character_2_2_5", new HairSource { sha256 = "92c74726ec07857bf290e2b04ab944b2d4f477a2a539f0bdf142e8aaf301b139", bytes = 263696, guid = "5066ed7a06fd7c03a342bb6a6de2b322", rendererId = -31949720844845429L } },
        { "Character_2_2_7", new HairSource { sha256 = "e600ff29926beb62fd350a5bee6a9462fb0d2ca0d6c9d39c3512a0cd83343e38", bytes = 263600, guid = "4f62e1189d707f14e8bf1dee4c3d54a7", rendererId = 7137082628371617607L } },
        { "Character_2_2_8", new HairSource { sha256 = "287f7c669c16adc571618d70c1b582f15420d719c12cc2a3453bf3f773c511fe", bytes = 263680, guid = "b69c5f8033d6e7f67fba06c62ab5f568", rendererId = -1623219848531997436L } },
        { "Character_2_2_9", new HairSource { sha256 = "85e861ea08f57acb6578203b96902f978a81dde41b1b0f9ebf42be3a9da366aa", bytes = 263632, guid = "f63872a8c654836548064a829f9aaa5b", rendererId = -3813806300671511365L } },
        { "Character_2_3_1", new HairSource { sha256 = "37cc4680b6a5c9f2ac90a9b652ef028a3611f9e23418385b422bf24aa5a38d52", bytes = 277344, guid = "b00badb0a56e3adbc712034a12e45368", rendererId = -5263264537386982883L } },
        { "Character_2_3_2", new HairSource { sha256 = "d68f5d2307ec3708118eb9824fb0a0f7c6196b6517beca3d8690229455cdb685", bytes = 276096, guid = "868a53de4782395e57b7008ba54ad4fc", rendererId = -7936794005500982399L } },
        { "Character_2_3_3", new HairSource { sha256 = "92ce7a7785eaa744ddd84161589d7f986916ea3d08e1190abb8d7d36b187288c", bytes = 276400, guid = "8c4c6f875448ddf03851770e9f078466", rendererId = -5620794671092418857L } },
        { "Character_2_3_4", new HairSource { sha256 = "6c7e6a65b10cbf3d9ddfc2c25d853d6f72306add7d91035537b7098daccab7a6", bytes = 277504, guid = "98cc9ed1ea0a75bbc2139ac3b7956a61", rendererId = 1887318453248505739L } },
        { "Character_2_3_5", new HairSource { sha256 = "7b71f10feed426e6e7023ae48470d898119097eff64d77185de43cde0f057c6d", bytes = 276432, guid = "9f98f3c3c715d671687115b218845684", rendererId = -8529092819895051519L } },
    };
    static HairSource VerifiedHairSource(Pack pack, string path, GameObject model)
    {
        if (pack.product.index != 11 || pack.root != HairRoot) return null;
        string name = Path.GetFileNameWithoutExtension(path); HairSource source;
        if (!HairSources.TryGetValue(name, out source) || path != HairRoot + "/Characters Full/Unity FBX/Characters/" + name + ".fbx") return null;
        if (model.name != name || AssetDatabase.AssetPathToGUID(path) != source.guid) throw new InvalidDataException("VerifiedP011 model identity changed.");
        string physical = Path.Combine(Path.GetDirectoryName(Application.dataPath), path.Replace('/', Path.DirectorySeparatorChar));
        using (var stream = File.OpenRead(physical)) using (var sha = SHA256.Create()) {
            if (stream.Length != source.bytes || BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != source.sha256) throw new InvalidDataException("VerifiedP011 FBX payload differs from the geometric counterpart proof.");
        }
        return source;
    }
    static void ApplyVerifiedHairSlot(Pack pack, string path, Renderer renderer, Material[] materials, HairSource source)
    {
        var original = PrefabUtility.GetCorrespondingObjectFromSource(renderer); string guid; long localId;
        if (!original || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(original, out guid, out localId) || guid != source.guid || localId != source.rendererId
            || materials.Length != 3 || !materials[1] || !materials[2] || materials[1].name != "No Name" || materials[2].name != "Hair")
            throw new InvalidDataException("VerifiedP011 renderer/NoName/Hair slots changed; no replacement was guessed.");
        // Every missing FBX region was matched to the same Hair primitive by all
        // control-point positions, UVs, triangle coverage and supplied GLB atlas.
        materials[1] = materials[2];
        report.verifiedSourceRepairs.Add(new VerifiedSourceRepair { kind = "p011-source-material-slot", product = pack.product.index, model = path, sourceSha256 = source.sha256,
            sourceProofSha256 = HairProofSha256, rendererLocalId = localId, replacementSlot = 1, referenceSlot = 2 });
    }

    const string TracksRoot = "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series";
    const string TracksImage = TracksRoot + "/Generated/Textures/TankTracks.png";
    const string TracksImageSha = "8dd896179f5b684c73c5f2a68c794f03cd755806b613f7019a746c9308260000";
    const string TracksProofSha = "a8bfecea9799683a44a886e2576b675a6f4120b8ea619cf877c0f6b8f9de3642";
    const string PumpkinRoot = "Assets/ThirdParty/YamyamAssetLibrary/067-free-halloween-pumpkin-candle-pack-jack-o-lantern-props-godot-unity-blend";
    const string PumpkinProofSha = "2c659fa0dbc83fc0f6612a7fa10fa6fabca995dee91da73d1b73c07f29949f33";
    sealed class MaterialSource { public string sha256, guid; public long bytes; }
    static readonly Dictionary<string, MaterialSource> TrackSources = new Dictionary<string, MaterialSource>(StringComparer.Ordinal)
    {
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_1_A.fbx", new MaterialSource { sha256 = "b1765b8628756d11a59ddae6ed350dca245cdadaa0c5a4efdff5a9b22426ed14", bytes = 307484, guid = "959566ef24ed0d7be50f142ca7a0ba1d" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_1_B.fbx", new MaterialSource { sha256 = "89810ed42c620a1f8a6bd9c833e104b140f62ba5a91b644f1b4a4fd2d16b4195", bytes = 308828, guid = "9f5c4e595608cc7b4302ca7d6dfb1db9" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_1_C.fbx", new MaterialSource { sha256 = "90ea89bbf782e88a50fc5c5f74f2828e1c574ef7eee6f68784daf543ba0e3498", bytes = 308924, guid = "1bd1a55c221566e3dfafbf001f83e3e0" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_1_D.fbx", new MaterialSource { sha256 = "a89c851d829272e6acd7aed0a6d1c56239cc72a16566eb4f066c9d2d4ae21333", bytes = 309196, guid = "29e3c913e150bc03cafbbfc274f66a51" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_1_E.fbx", new MaterialSource { sha256 = "ad01b60493b31b1f47047978bdb24e95be59ee1f75abf20b88bfb4d209d1722b", bytes = 313804, guid = "865e052a598af2c7bbd9817e3c8d99fd" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_1_F.fbx", new MaterialSource { sha256 = "6635f85f564182443284a31a89dbacb76f993647b1bba800cf43a77a01fc7b97", bytes = 312252, guid = "c4961a2afa99c2a3a328944b489d25c8" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_2_A.fbx", new MaterialSource { sha256 = "f8757f2f5485ff32d5c1d567920ca1cf719f9d60b54b3315ae9144abf71ac83d", bytes = 280780, guid = "d1ed8ba5215aa87f0f7856afcbd6e326" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_2_B.fbx", new MaterialSource { sha256 = "e20f9cc318e95e2c6ed9b13133f27a897a64a991966d17de703700b8dc22d335", bytes = 280844, guid = "8c671ce0783062ea9641adba2e0fb713" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_2_C.fbx", new MaterialSource { sha256 = "2e4dbafec237a04ccba7f841634e2831809780f0b850d6060de2eddcf5c92066", bytes = 280812, guid = "8b467b5e2f6dfe3da620c4ef26867b21" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_2_D.fbx", new MaterialSource { sha256 = "79e362e6651689bd5c5e1d54911fa1a884cc5be06ba4bdd37b5af9c43ba95531", bytes = 280764, guid = "6118faeb2e5a1d1b3bd927e5ac5b4c33" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_2_E.fbx", new MaterialSource { sha256 = "93addc7d0bc8ce3cae83e48e043e27a87239e2ae2f0ad4140c346f4e6bd888f3", bytes = 280652, guid = "f960c2fecbaf63ce52af6804b5646251" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_2_F.fbx", new MaterialSource { sha256 = "09837ea769efaf84cbfd5b7cc2521356f87ab9e1e7aab2e6a207d14a51c89ccb", bytes = 280652, guid = "00377cc506f89b477a5a8c0b21713432" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_3_A.fbx", new MaterialSource { sha256 = "da88df17f59620da9eab734c01ba6d02b919a4a70cb181bb90c08957ebdc9243", bytes = 209276, guid = "41083b4f4b68fd21dfcf8c0d8c0a71bd" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_3_B.fbx", new MaterialSource { sha256 = "4950240dccaf9333bd303cce3b395590e633bfbbe6e04ca8019f0263ce8ce16e", bytes = 209308, guid = "eed64116b3c8f4f2a4f4e764ce42a9d3" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_3_C.fbx", new MaterialSource { sha256 = "5396a05a27c632050fd970da3efb84355da71fd41b55bf7587d825364d7dbc0b", bytes = 209164, guid = "2f73dc9b87784b573f7ebd67d5a21644" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_3_D.fbx", new MaterialSource { sha256 = "39b72e164a9354e8aad3b008b325530ef9ffeaa41da0481be81142c5412dc293", bytes = 208988, guid = "998849cc2152decc661f18b9f7b56552" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_3_E.fbx", new MaterialSource { sha256 = "833c7f1495bb9ab001ba1a7465751fe596e3c794f07ca162291d16467b2cf617", bytes = 209068, guid = "710e17a7daea7160d31667642e5ef398" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/061-army-pack-cute-series/Army Pack/FBX Unity/Tank_3_F.fbx", new MaterialSource { sha256 = "b849f4aad0d2956533be4c44fed962d2f8ee2d0e6300ff140ab0c480e01ee3a4", bytes = 208940, guid = "4c5ee0993264664241377367404ca23f" } },
    };
    static readonly Dictionary<string, MaterialSource> PumpkinSources = new Dictionary<string, MaterialSource>(StringComparer.Ordinal)
    {
        { "Assets/ThirdParty/YamyamAssetLibrary/067-free-halloween-pumpkin-candle-pack-jack-o-lantern-props-godot-unity-blend/FBX/EA_Pumpkin_01a.fbx", new MaterialSource { sha256 = "6b0928084eb525772d5ffdcb4d7d0a35283d878632fcff77aeced78319276e74", bytes = 59532, guid = "6a70cba06e0a5e134ed351ed95b6443b" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/067-free-halloween-pumpkin-candle-pack-jack-o-lantern-props-godot-unity-blend/FBX/EA_Pumpkin_01b.fbx", new MaterialSource { sha256 = "a5b1bbce1c462fcb73c71c589473a1a1d2442b34cb516a5076ecce17e973bb69", bytes = 66156, guid = "95e766c6a1ba36cdab3d27d9d7098383" } },
        { "Assets/ThirdParty/YamyamAssetLibrary/067-free-halloween-pumpkin-candle-pack-jack-o-lantern-props-godot-unity-blend/FBX/EA_Pumpkin_01c.fbx", new MaterialSource { sha256 = "cee6c0f3b005fc684926941fd3886e568b99d4b463f6adb552981703903e6030", bytes = 71020, guid = "814d32d61ef2ec71a298d71508135143" } },
    };
    static MaterialSource VerifiedMaterialSource(Dictionary<string, MaterialSource> sources, string path)
    {
        MaterialSource source;
        if (!sources.TryGetValue(path, out source)) return null;
        if (AssetDatabase.AssetPathToGUID(path) != source.guid) throw new InvalidDataException("Proved source FBX GUID changed.");
        string physical = Path.Combine(Path.GetDirectoryName(Application.dataPath), path.Replace('/', Path.DirectorySeparatorChar));
        using (var stream = File.OpenRead(physical)) using (var sha = SHA256.Create()) {
            if (stream.Length != source.bytes || BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != source.sha256) throw new InvalidDataException("Proved source FBX payload changed.");
        }
        return source;
    }
    static bool VerifiedP061Tracks(Pack pack, Material source, string modelPath, ref Texture color)
    {
        if (pack.product.index != 61 || pack.root != TracksRoot || (source.name != "TankTracks_L" && source.name != "TankTracks_R")) return false;
        // Preserve an independently supplied non-recovered source map.
        if (color && AssetDatabase.GetAssetPath(color) != TracksImage) return false;
        var proof = VerifiedMaterialSource(TrackSources, modelPath); if (proof == null) return false;
        string physical = Path.Combine(Path.GetDirectoryName(Application.dataPath), TracksImage.Replace('/', Path.DirectorySeparatorChar));
        // The dedicated recovery step supplies this exact source PNG. No archive
        // parsing, arbitrary material-name match or image fabrication occurs here.
        if (!File.Exists(physical)) throw new InvalidDataException("Run the bounded source TankTracks recovery before rebuilding these proved materials.");
        using (var stream = File.OpenRead(physical)) using (var sha = SHA256.Create()) {
            if (stream.Length != 7409 || BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != TracksImageSha) throw new InvalidDataException("Recovered TankTracks image payload changed.");
        }
        var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(TracksImage);
        if (!texture || texture.width != 128 || texture.height != 72 || AssetDatabase.GetMainAssetTypeAtPath(TracksImage) != typeof(Texture2D)) throw new InvalidDataException("Recovered TankTracks image must be the proved128x72Texture2D.");
        color = texture;
        report.verifiedSourceRepairs.Add(new VerifiedSourceRepair { kind = "p061-source-image-binding", product = 61, model = modelPath, sourceMaterial = source.name, sourceSha256 = proof.sha256, sourceProofSha256 = TracksProofSha, replacementSlot = -1, referenceSlot = -1 });
        return true;
    }
    static bool VerifiedP067Emission(Pack pack, Material source, string modelPath, Color tint, Texture color)
    {
        if (pack.product.index != 67 || pack.root != PumpkinRoot || source.name != "emiss" || color || GetTexture(source, "_EmissionMap")) return false;
        var proof = VerifiedMaterialSource(PumpkinSources, modelPath); if (proof == null) return false;
        if (Mathf.Abs(tint.r) > .00001f || Mathf.Abs(tint.g) > .00001f || Mathf.Abs(tint.b) > .00001f || Mathf.Abs(tint.a - 1) > .00001f) throw new InvalidDataException("Proved pumpkin emission source no longer has its black untextured base.");
        report.verifiedSourceRepairs.Add(new VerifiedSourceRepair { kind = "p067-source-linear-emission", product = 67, model = modelPath, sourceMaterial = source.name, sourceSha256 = proof.sha256, sourceProofSha256 = PumpkinProofSha, replacementSlot = -1, referenceSlot = -1 });
        return true;
    }
    static void ApplyVerifiedEmission(Material material)
    {
        // glTF emissiveFactor is already linear. SetVector preserves that factor;
        // SetColor would apply an HDR color-space conversion in linear projects.
        var emission = new Vector4(.8000000715255737f, .01814323104918003f, .02997703291475773f, 1);
        material.SetVector("_EmissionColor", emission);
        material.globalIlluminationFlags &= ~MaterialGlobalIlluminationFlags.EmissiveIsBlack;
        ValidateOfficialLit(material);
        if ((material.GetVector("_EmissionColor") - emission).sqrMagnitude > 1e-12f || !material.IsKeywordEnabled("_EMISSION")) throw new InvalidDataException("Source-proved linear emission validation failed.");
    }

    static Material ConvertMaterial(Pack pack, Material source, string modelPath, out bool unresolved)
    {
        unresolved = false;
        if (!source) { AddIssue(pack.product.index, "null-source-material", modelPath, "A renderer slot is null; it is preserved as null."); unresolved = true; return null; }
        Texture color = GetTexture(source, "_BaseMap", "_MainTex"); string resolution = color ? "source-texture-reference" : "source-color-only";
        Color tint = GetColor(source, Color.white, "_BaseColor", "_Color");
        bool verifiedGlass = VerifiedP008Glass(pack, modelPath, source, tint, color);
        bool verifiedTracks = VerifiedP061Tracks(pack, source, modelPath, ref color);
        bool verifiedEmission = VerifiedP067Emission(pack, source, modelPath, tint, color);
        if (verifiedGlass) resolution = "verified-p008-untextured-tinted-glass";
        if (verifiedTracks) resolution = "verified-p061-recovered-source-tank-track-image";
        if (verifiedEmission) resolution = "verified-p067-untextured-source-linear-emission";
        if (!color && !verifiedGlass && !verifiedEmission)
        {
            string match = MatchColor(pack, source.name);
            if (match != null) { color = AssetDatabase.LoadAssetAtPath<Texture2D>(match); resolution = "unique-normalized-material-texture-name"; }
            else if (pack.textures.Any(IsColorMap))
            {
                unresolved = true;
                AddIssue(pack.product.index, "unresolved-basecolor", modelPath + " :: " + source.name,
                    "No existing texture reference or unique normalized material/texture-name match. Original material color retained; no atlas guessed.");
            }
        }
        Texture normal = GetTexture(source, "_BumpMap"), metallic = GetTexture(source, "_MetallicGlossMap"), emission = GetTexture(source, "_EmissionMap"), occlusion = GetTexture(source, "_OcclusionMap");
        float metal = GetFloat(source, 0, "_Metallic"), smooth = GetFloat(source, .5f, "_Smoothness", "_Glossiness");
        string signature = source.shader.name + "|" + source.name + "|" + tint.ToString("R") + "|" + metal.ToString("R", CultureInfo.InvariantCulture) + "|" + smooth.ToString("R", CultureInfo.InvariantCulture)
            + "|" + TextureIdentity(color) + "|" + TextureIdentity(normal) + "|" + TextureIdentity(metallic) + "|" + TextureIdentity(emission) + "|" + TextureIdentity(occlusion)
            + "|" + StableMaterialProperties(source);
        string key = pack.root + "|" + ShortHash(signature);
        string cachedPath;
        if (MaterialCache.TryGetValue(key, out cachedPath))
        {
            var cached = AssetDatabase.LoadAssetAtPath<Material>(cachedPath);
            if (cached) return cached;
        }
        var shader = Shader.Find("Universal Render Pipeline/Lit"); if (!shader) throw new InvalidOperationException("URP/Lit shader unavailable.");
        var material = source.shader == shader ? new Material(source) : new Material(shader);
        material.name = source.name; material.SetColor("_BaseColor", tint); material.SetTexture("_BaseMap", color);
        if (source.HasProperty("_BaseMap")) { material.SetTextureScale("_BaseMap", source.GetTextureScale("_BaseMap")); material.SetTextureOffset("_BaseMap", source.GetTextureOffset("_BaseMap")); }
        else if (source.HasProperty("_MainTex")) { material.SetTextureScale("_BaseMap", source.GetTextureScale("_MainTex")); material.SetTextureOffset("_BaseMap", source.GetTextureOffset("_MainTex")); }
        material.SetFloat("_Metallic", metal); material.SetFloat("_Smoothness", smooth);
        if (normal) { material.SetTexture("_BumpMap", normal); material.SetFloat("_BumpScale", GetFloat(source, 1, "_BumpScale")); material.EnableKeyword("_NORMALMAP"); }
        if (metallic) { material.SetTexture("_MetallicGlossMap", metallic); material.EnableKeyword("_METALLICSPECGLOSSMAP"); }
        if (occlusion) { material.SetTexture("_OcclusionMap", occlusion); material.SetFloat("_OcclusionStrength", GetFloat(source, 1, "_OcclusionStrength")); }
        if (emission) { material.SetTexture("_EmissionMap", emission); material.SetColor("_EmissionColor", GetColor(source, Color.black, "_EmissionColor")); material.EnableKeyword("_EMISSION"); }
        if (source.shader != shader)
        {
            int mode = Mathf.RoundToInt(GetFloat(source, 0, "_Mode"));
            if (mode == 1) { material.SetFloat("_AlphaClip", 1); material.SetFloat("_Cutoff", GetFloat(source, .5f, "_Cutoff")); material.EnableKeyword("_ALPHATEST_ON"); material.renderQueue = (int)RenderQueue.AlphaTest; }
            if (mode == 2 || mode == 3) { material.SetFloat("_Surface", 1); material.SetFloat("_ZWrite", 0); material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha); material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha); material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT"); material.SetOverrideTag("RenderType", "Transparent"); material.renderQueue = (int)RenderQueue.Transparent; }
        }
        if (verifiedGlass) ValidateVerifiedGlass(material);
        if (verifiedEmission) ApplyVerifiedEmission(material);
        string directory = pack.root + "/Generated/Materials"; EnsureFolder(directory);
        string path = directory + "/" + SafeName(source.name) + "_" + ShortHash(signature) + ".mat";
        material = SaveMaterial(material, path); MaterialCache[key] = path;
        report.materials.Add(new MaterialEvidence { product = pack.product.index, material = path, sourceMaterial = source.name, baseColor = color ? AssetDatabase.GetAssetPath(color) : null, resolution = resolution });
        return material;
    }
    static Material SaveMaterial(Material material, string path)
    {
        var existing = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (existing) { EditorUtility.CopySerialized(material, existing); Object.DestroyImmediate(material); EditorUtility.SetDirty(existing); AssetDatabase.SaveAssetIfDirty(existing); return existing; }
        AssetDatabase.CreateAsset(material, path); report.materialsCreated++; return material;
    }
    static void BuildModel(Pack pack, string path)
    {
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
        if (!model) { AddIssue(pack.product.index, "missing-model", path, "No GameObject imported from this FBX; source retained."); return; }
        HairSource hairSource = VerifiedHairSource(pack, path, model);
        GameObject instance = null;
        try
        {
            instance = PrefabUtility.InstantiatePrefab(model, preview) as GameObject;
            if (!instance) throw new InvalidOperationException("Could not instantiate model in isolated preview scene.");
            var renderers = instance.GetComponentsInChildren<Renderer>(true); int slots = 0, unresolved = 0;
            if (hairSource != null && renderers.Length != 1) throw new InvalidDataException("VerifiedP011 renderer count changed.");
            foreach (var renderer in renderers)
            {
                var materials = renderer.sharedMaterials;
                if (hairSource != null) ApplyVerifiedHairSlot(pack, path, renderer, materials, hairSource);
                for (int i = 0; i < materials.Length; i++) { bool issue; materials[i] = ConvertMaterial(pack, materials[i], path, out issue); slots++; if (issue) unresolved++; }
                renderer.sharedMaterials = materials;
            }
            if (renderers.Length == 0 && AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Any()) report.animationOnlyModels++;
            string directory = pack.root + "/Generated/Prefabs"; EnsureFolder(directory);
            string destination = directory + "/" + SafeName(Path.GetFileNameWithoutExtension(path)) + "_" + AssetDatabase.AssetPathToGUID(path).Substring(0, 12) + ".prefab";
            bool success; var prefab = PrefabUtility.SaveAsPrefabAsset(instance, destination, out success);
            if (!success || !prefab) throw new IOException("Saving generated prefab failed: " + destination);
            report.prefabsCreated++;
            report.models.Add(new ModelEvidence { product = pack.product.index, model = path, prefab = destination, renderers = renderers.Length, materialSlots = slots, unresolvedSlots = unresolved });
        }
        finally { if (instance) Object.DestroyImmediate(instance); }
    }

    static Texture2D ReadLinear(Texture texture, int width, int height)
    {
        var target = RenderTexture.GetTemporary(width, height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear);
        var previous = RenderTexture.active; Texture2D result = null;
        try { Graphics.Blit(texture, target); RenderTexture.active = target; result = new Texture2D(width, height, TextureFormat.RGBA32, false, true); result.ReadPixels(new Rect(0, 0, width, height), 0, 0); result.Apply(false, false); return result; }
        catch { if (result) Object.DestroyImmediate(result); throw; }
        finally { RenderTexture.active = previous; RenderTexture.ReleaseTemporary(target); }
    }
    static void BuildPlasticine(Pack pack, string basePath)
    {
        string prefix = Regex.Replace(Path.GetFileNameWithoutExtension(basePath), "_BaseColor$", "", RegexOptions.IgnoreCase);
        Func<string, string> find = suffix => pack.textures.SingleOrDefault(p => String.Equals(Path.GetFileNameWithoutExtension(p), prefix + suffix, StringComparison.OrdinalIgnoreCase));
        string metalPath = find("_Metallic"), roughPath = find("_Roughness"), normalPath = find("_Normal");
        if (metalPath == null || roughPath == null || normalPath == null) { AddIssue(pack.product.index, "incomplete-pbr-set", basePath, "BaseColor, Metallic, Roughness and Normal are all required. No missing map fabricated."); return; }
        var metal = AssetDatabase.LoadAssetAtPath<Texture2D>(metalPath); var rough = AssetDatabase.LoadAssetAtPath<Texture2D>(roughPath);
        if (!metal || !rough) throw new InvalidOperationException("PBR data maps failed to load.");
        int width = Math.Min(2048, metal.width), height = Math.Min(2048, metal.height);
        Texture2D m = null, r = null;
        string directory = pack.root + "/Generated/Materials"; EnsureFolder(directory);
        string combinedPath = directory + "/" + SafeName(prefix) + "_MetallicSmoothness.png";
        try
        {
            m = ReadLinear(metal, width, height); r = ReadLinear(rough, width, height);
            var pixels = m.GetPixels32(); var roughPixels = r.GetPixels32();
            for (int i = 0; i < pixels.Length; i++) pixels[i].a = (byte)(255 - roughPixels[i].r);
            m.SetPixels32(pixels); m.Apply(false, false); File.WriteAllBytes(combinedPath, m.EncodeToPNG());
        }
        finally { if (m) Object.DestroyImmediate(m); if (r) Object.DestroyImmediate(r); }
        AssetDatabase.ImportAsset(combinedPath, ImportAssetOptions.ForceSynchronousImport);
        var importer = (TextureImporter)AssetImporter.GetAtPath(combinedPath); importer.sRGBTexture = false; importer.maxTextureSize = 2048; importer.textureCompression = TextureImporterCompression.Uncompressed; importer.alphaSource = TextureImporterAlphaSource.FromInput; importer.SaveAndReimport();
        var shader = Shader.Find("Universal Render Pipeline/Lit"); if (!shader) throw new InvalidOperationException("URP/Lit unavailable.");
        var material = new Material(shader) { name = prefix };
        material.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(basePath));
        material.SetTexture("_BumpMap", AssetDatabase.LoadAssetAtPath<Texture2D>(normalPath)); material.EnableKeyword("_NORMALMAP");
        material.SetTexture("_MetallicGlossMap", AssetDatabase.LoadAssetAtPath<Texture2D>(combinedPath)); material.SetFloat("_Metallic", 1); material.SetFloat("_Smoothness", 1); material.SetFloat("_SmoothnessTextureChannel", 0); material.EnableKeyword("_METALLICSPECGLOSSMAP");
        string materialPath = directory + "/" + SafeName(prefix) + ".mat"; SaveMaterial(material, materialPath);
        report.materials.Add(new MaterialEvidence { product = pack.product.index, material = materialPath, sourceMaterial = prefix, baseColor = basePath, resolution = "Original basecolor/normal; combined metallicRGB + (1 - roughnessR)alpha, GPU readback at <=2048. Original8K files retained." });
    }
    static void AddIssue(int product, string code, string path, string detail)
    {
        if (IssueKeys.Add(product + "|" + code + "|" + path)) report.issues.Add(new Issue { product = product, code = code, path = path, detail = detail });
    }
    static void WriteReport() { Directory.CreateDirectory(Path.GetDirectoryName(reportPath)); File.WriteAllText(reportPath, JsonUtility.ToJson(report, true), new UTF8Encoding(false)); }
    static string StableMaterialProperties(Material material)
    {
        var text = new StringBuilder(material.shader.name);
        text.Append('|').Append(material.renderQueue).Append('|').Append(material.enableInstancing).Append('|').Append(material.doubleSidedGI);
        foreach (string keyword in material.shaderKeywords.OrderBy(k => k, StringComparer.Ordinal)) text.Append('|').Append(keyword);
        for (int i = 0; i < material.shader.GetPropertyCount(); i++)
        {
            string name = material.shader.GetPropertyName(i); text.Append('|').Append(name).Append('=');
            var type = material.shader.GetPropertyType(i);
            if (type == ShaderPropertyType.Texture)
            {
                text.Append(TextureIdentity(material.GetTexture(name)));
                Vector2 scale = material.GetTextureScale(name), offset = material.GetTextureOffset(name);
                text.Append(scale.x.ToString("R", CultureInfo.InvariantCulture)).Append(',').Append(scale.y.ToString("R", CultureInfo.InvariantCulture));
                text.Append(offset.x.ToString("R", CultureInfo.InvariantCulture)).Append(',').Append(offset.y.ToString("R", CultureInfo.InvariantCulture));
            }
            else if (type == ShaderPropertyType.Color || type == ShaderPropertyType.Vector)
            {
                Vector4 value = material.GetVector(name);
                for (int component = 0; component < 4; component++) text.Append(value[component].ToString("R", CultureInfo.InvariantCulture)).Append(',');
            }
            else if (type == ShaderPropertyType.Int) text.Append(material.GetInt(name).ToString(CultureInfo.InvariantCulture));
            else text.Append(material.GetFloat(name).ToString("R", CultureInfo.InvariantCulture));
        }
        return text.ToString();
    }
    static void BeforeReload()
    {
        if (!running) return;
        running = false; ClosePreview();
        report.status = "interrupted-before-reload";
        report.lastError = "Editor reload interrupted preparation. Begin(manifestPath) can safely restart the deterministic owned-output jobs.";
        WriteReport();
    }
    static void ClosePreview() { if (preview.IsValid()) EditorSceneManager.ClosePreviewScene(preview); preview = default(Scene); }
    static void Fail(Exception exception)
    {
        running = false; ClosePreview();
        if (report == null) return;
        report.lastError = exception.ToString(); report.status = "failed"; report.completedUtc = DateTime.UtcNow.ToString("o");
        if (!String.IsNullOrEmpty(reportPath)) WriteReport();
    }
}
