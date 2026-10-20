// Diagnostic only: clones the exact reviewed P067 material and never saves an asset.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static partial class YamyamAssetLibraryMaterialSlots
{
    [Serializable] public sealed class P067ProbeValue { public string key, value; }
    [Serializable] public sealed class P067ProbeSnapshot
    {
        public string name, otherShaderPropertiesSha256;
        public bool emissionKeyword;
        public int giFlags, anyEmissiveMask;
        public Vector4 emissionColor;
        public List<P067ProbeValue> values = new List<P067ProbeValue>();
    }
    [Serializable] public sealed class P067ProbeDelta { public string key, before, after; }
    [Serializable] public sealed class P067ProbeComparison
    {
        public string beforeSnapshot, afterSnapshot;
        public List<P067ProbeDelta> changes = new List<P067ProbeDelta>();
    }
    [Serializable] public sealed class P067ValidatorProbeReport
    {
        public string kind = "read-only-p067-official-validator-clone-diagnostic", status = "checking", project, runDirectory, startedUtc, completedUtc;
        public string sourceProofSha256, canonicalManifestSha256, materialPath, materialBeforeSha256, materialAfterSha256;
        public string metadataBeforeSha256, metadataAfterSha256, originalSerializedBeforeSha256, originalSerializedAfterSha256;
        public string officialValidator = "UnityEditor.Rendering.Universal.ShaderGUI.LitShader.ValidateMaterial";
        public bool assetsWritten, scenesOpened, sourceArchivesModified, originalMaterialMemoryUnchanged, originalFileBytesUnchanged;
        public int observedUnityErrors, anyEmissiveEnumValue, bakedEmissiveEnumValue, realtimeEmissiveEnumValue, blackEmissiveEnumValue;
        public Vector4 sourceLinearEmissionFactor;
        public List<P067ProbeSnapshot> snapshots = new List<P067ProbeSnapshot>();
        public List<P067ProbeComparison> comparisons = new List<P067ProbeComparison>();
        public List<string> errors = new List<string>();
    }

    static string ProbeFloat(float value) { return value.ToString("R", CultureInfo.InvariantCulture); }
    static string ProbeVector(Vector4 v) { return string.Join("|", new[] { ProbeFloat(v.x), ProbeFloat(v.y), ProbeFloat(v.z), ProbeFloat(v.w) }); }
    static void ProbeValue(P067ProbeSnapshot snapshot, string key, string value) { snapshot.values.Add(new P067ProbeValue { key = key, value = value }); }
    static P067ProbeSnapshot CaptureP067Probe(Material material, string name, string originalIdentity)
    {
        var state = new P067ProbeSnapshot { name = name, giFlags = (int)material.globalIlluminationFlags,
            anyEmissiveMask = (int)(material.globalIlluminationFlags & MaterialGlobalIlluminationFlags.AnyEmissive),
            emissionKeyword = material.IsKeywordEnabled("_EMISSION"), emissionColor = material.GetVector("_EmissionColor"),
            otherShaderPropertiesSha256 = OtherEmissionProperties(material, originalIdentity) };
        ProbeValue(state, "shader", material.shader.name);
        ProbeValue(state, "renderQueue", material.renderQueue.ToString(CultureInfo.InvariantCulture));
        ProbeValue(state, "enableInstancing", material.enableInstancing.ToString());
        ProbeValue(state, "doubleSidedGI", material.doubleSidedGI.ToString());
        ProbeValue(state, "globalIlluminationFlags", ((int)material.globalIlluminationFlags).ToString(CultureInfo.InvariantCulture));
        ProbeValue(state, "RenderType", material.GetTag("RenderType", false));
        ProbeValue(state, "keywords", string.Join("|", material.shaderKeywords.OrderBy(k => k, StringComparer.Ordinal)));
        for (int i = 0; i < material.shader.GetPropertyCount(); i++) {
            string key = material.shader.GetPropertyName(i); ShaderPropertyType type = material.shader.GetPropertyType(i);
            ProbeValue(state, "property-type:" + key, type.ToString());
            if (type == ShaderPropertyType.Texture) {
                Texture t = material.GetTexture(key); Vector2 scale = material.GetTextureScale(key), offset = material.GetTextureOffset(key);
                ProbeValue(state, "texture:" + key, t ? ObjectIdentity(t) : "null");
                ProbeValue(state, "texture-transform:" + key, ProbeVector(new Vector4(scale.x, scale.y, offset.x, offset.y)));
            } else if (type == ShaderPropertyType.Color || type == ShaderPropertyType.Vector) ProbeValue(state, "vector:" + key, ProbeVector(material.GetVector(key)));
            else if (type == ShaderPropertyType.Int) ProbeValue(state, "int:" + key, material.GetInteger(key).ToString(CultureInfo.InvariantCulture));
            else ProbeValue(state, "float:" + key, ProbeFloat(material.GetFloat(key)));
        }
        for (int i = 0; i < material.passCount; i++) { string pass = material.GetPassName(i); ProbeValue(state, "pass:" + i + ":" + pass, material.GetShaderPassEnabled(pass).ToString()); }
        return state;
    }
    static P067ProbeComparison CompareP067Probe(P067ProbeSnapshot before, P067ProbeSnapshot after)
    {
        var result = new P067ProbeComparison { beforeSnapshot = before.name, afterSnapshot = after.name };
        var a = before.values.ToDictionary(x => x.key, x => x.value, StringComparer.Ordinal);
        var b = after.values.ToDictionary(x => x.key, x => x.value, StringComparer.Ordinal);
        foreach (string key in a.Keys.Union(b.Keys).OrderBy(k => k, StringComparer.Ordinal)) {
            string old, current; a.TryGetValue(key, out old); b.TryGetValue(key, out current);
            if (old != current) result.changes.Add(new P067ProbeDelta { key = key, before = old, after = current });
        }
        return result;
    }

    // Can be called before another explicitly selected bounded phase in one held Editor session.
    public static void ProbeP067ValidatorReadOnly()
    {
        Guard();
        if (Application.unityVersion != "6000.6.0f1" || EditorApplication.isCompiling || EditorApplication.isUpdating || QualitySettings.activeColorSpace != ColorSpace.Linear)
            throw new InvalidOperationException("Expected idle Unity6000.6 with unchanged Linear color space for the read-only clone probe.");
        string local = Path.Combine(Project, "Library/YamyamAssetLibrary");
        string run = Path.Combine(local, "p067-validator-probe", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ") + "-" + Guid.NewGuid().ToString("N"));
        NoLinks(run); Directory.CreateDirectory(run);
        var report = new P067ValidatorProbeReport { project = Project, runDirectory = run, startedUtc = Utc(), sourceProofSha256 = EmissionPlanSha256,
            anyEmissiveEnumValue = (int)MaterialGlobalIlluminationFlags.AnyEmissive, bakedEmissiveEnumValue = (int)MaterialGlobalIlluminationFlags.BakedEmissive,
            realtimeEmissiveEnumValue = (int)MaterialGlobalIlluminationFlags.RealtimeEmissive, blackEmissiveEnumValue = (int)MaterialGlobalIlluminationFlags.EmissiveIsBlack };
        var clones = new List<Material>(); Material original = null; string materialFile = null, metadataFile = null, manifestFile = null, planFile = null;
        Application.LogCallback capture = (message, stack, type) => { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) { report.observedUnityErrors++; report.errors.Add(message); } };
        Application.logMessageReceived += capture;
        try {
            planFile = Path.Combine(Work, "product067-emission-correction-plan.json"); NoLinks(planFile);
            if (HashFile(planFile) != EmissionPlanSha256) throw new InvalidDataException("Reviewed P067 source/region plan changed.");
            var plan = JsonUtility.FromJson<EmissionPlan>(File.ReadAllText(planFile));
            if (plan.schemaVersion != 1 || plan.kind != "source-proven-p067-gltf-emission" || plan.status != "prepared-read-only" || plan.sourceFactorColorSpace != "linear-sRGB"
                || plan.sourceArchivesModified || plan.actualAssetsModified || !plan.noTextureConnectionOrAtlasInEitherSource || plan.sourceEmissionFactor == null || plan.sourceEmissionFactor.Length != 3)
                throw new InvalidDataException("Unreviewed P067 clone-probe scope.");
            var linear = new Vector4(plan.sourceEmissionFactor[0], plan.sourceEmissionFactor[1], plan.sourceEmissionFactor[2], 1);
            if (!NearVector(linear, new Vector4(.8000000715255737f, .01814323104918003f, .02997703291475773f, 1))) throw new InvalidDataException("Source-linear factor changed.");
            report.sourceLinearEmissionFactor = linear;
            Record target = plan.targetMaterial;
            if (target.assetPath != Root + EmissionFolder + "/Generated/Materials/emiss_3bf86f37223e.mat" || target.guid != EmissionGuid || target.path != Absolute(target.assetPath) || plan.targetMetadata.path != target.path + ".meta")
                throw new InvalidDataException("P067 clone-probe target escaped exact material scope.");
            materialFile = target.path; metadataFile = plan.targetMetadata.path;
            Exact(materialFile, target.bytes, target.sha256); Exact(metadataFile, plan.targetMetadata.bytes, plan.targetMetadata.sha256);
            report.materialPath = target.assetPath; report.materialBeforeSha256 = HashFile(materialFile); report.metadataBeforeSha256 = HashFile(metadataFile);
            manifestFile = Path.Combine(Work, "staging-manifest.json"); NoLinks(manifestFile); report.canonicalManifestSha256 = HashFile(manifestFile);
            original = AssetDatabase.LoadAssetAtPath<Material>(target.assetPath); string guid; long id;
            if (!original || original.shader.name != "Universal Render Pipeline/Lit" || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(original, out guid, out id) || guid != EmissionGuid || id != 2100000
                || GuidAt(metadataFile) != EmissionGuid || original.IsKeywordEnabled("_EMISSION") || !NearVector(original.GetVector("_EmissionColor"), new Vector4(0, 0, 0, 1)))
                throw new InvalidDataException("Original P067 native material signature changed.");
            report.originalSerializedBeforeSha256 = Hash(Encoding.UTF8.GetBytes(EditorJsonUtility.ToJson(original)));
            string identity = ObjectIdentity(original);
            Action<Material, string> snapshot = (material, name) => report.snapshots.Add(CaptureP067Probe(material, name, identity));
            snapshot(original, "original");
            var prepared = new Material(original) { name = original.name }; clones.Add(prepared); snapshot(prepared, "clone-unchanged");
            prepared.SetVector("_EmissionColor", linear); prepared.globalIlluminationFlags = original.globalIlluminationFlags & ~MaterialGlobalIlluminationFlags.EmissiveIsBlack;
            snapshot(prepared, "linear-color-and-black-flag-cleared"); ValidateEmissionLit(prepared); snapshot(prepared, "after-official-validator");
            prepared.EnableKeyword("_EMISSION"); snapshot(prepared, "after-validator-temporary-keyword-only");
            ValidateEmissionLit(prepared); snapshot(prepared, "after-second-official-validator");
            var bakedControl = new Material(original) { name = original.name }; clones.Add(bakedControl);
            bakedControl.SetVector("_EmissionColor", linear); bakedControl.globalIlluminationFlags = (original.globalIlluminationFlags & ~MaterialGlobalIlluminationFlags.EmissiveIsBlack) | MaterialGlobalIlluminationFlags.BakedEmissive;
            snapshot(bakedControl, "temporary-baked-flag-control-before-validator"); ValidateEmissionLit(bakedControl); snapshot(bakedControl, "temporary-baked-flag-control-after-validator");
            // The Baked control is diagnostic only; no GI setting or proposed production change is applied.
            foreach (var state in report.snapshots.Skip(1)) report.comparisons.Add(CompareP067Probe(report.snapshots[0], state));
            report.comparisons.Add(CompareP067Probe(report.snapshots[2], report.snapshots[3]));
            report.comparisons.Add(CompareP067Probe(report.snapshots[4], report.snapshots[5]));
            report.comparisons.Add(CompareP067Probe(report.snapshots[6], report.snapshots[7]));
            report.originalSerializedAfterSha256 = Hash(Encoding.UTF8.GetBytes(EditorJsonUtility.ToJson(original)));
            report.originalMaterialMemoryUnchanged = report.originalSerializedBeforeSha256 == report.originalSerializedAfterSha256;
            report.materialAfterSha256 = HashFile(materialFile); report.metadataAfterSha256 = HashFile(metadataFile);
            report.originalFileBytesUnchanged = report.materialBeforeSha256 == report.materialAfterSha256 && report.metadataBeforeSha256 == report.metadataAfterSha256;
            if (!report.originalMaterialMemoryUnchanged || !report.originalFileBytesUnchanged || HashFile(planFile) != EmissionPlanSha256 || HashFile(manifestFile) != report.canonicalManifestSha256 || report.observedUnityErrors != 0)
                throw new InvalidDataException("Read-only material/metadata/plan/manifest preservation or native-error guard failed.");
            report.status = "complete-read-only";
        } catch (Exception error) { report.status = "failed"; report.errors.Add(error.ToString()); throw; }
        finally {
            foreach (Material clone in clones) if (clone) UnityEngine.Object.DestroyImmediate(clone);
            if (report.observedUnityErrors != 0 && report.status == "complete-read-only") report.status = "failed";
            report.completedUtc = Utc(); Application.logMessageReceived -= capture;
            byte[] data = new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(report, true) + "\n");
            Atomic(Path.Combine(run, "report.json"), data); Atomic(Path.Combine(local, "p067-validator-probe-report.json"), data);
        }
    }
    public static void RunP067ValidatorProbeHeadless()
    {
        Guard(); int code = 0;
        try { ProbeP067ValidatorReadOnly(); } catch (Exception error) { Debug.LogError(error); code = 1; }
        EditorApplication.Exit(code);
    }
}
