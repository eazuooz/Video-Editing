// Explicit correction of15 proved missing FBX material slots in generated prefabs.
// No source FBX/material/mesh/animation is changed and no scene is opened.
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
using File = YamyamAssetLibraryIO.Files;
using Directory = YamyamAssetLibraryIO.Directories;
using FileInfo = YamyamAssetLibraryIO.Info;

public static partial class YamyamAssetLibraryMaterialSlots
{
    const string ExpectedProject = "D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string Root = "Assets/ThirdParty/YamyamAssetLibrary/";
    const string Folder = "011-cartoon-city-massive-pack-characters-unity-godot-fbx";
    const string PlanSha256 = "26abd521aba83171d2ce26dcc981af41107655017ff85651f91fc3228b5d1c46";
    const string HairGuid = "a8b1fcda727fe3c4192b752eace455eb";
    const string PlaceholderGuid = "6aebbaae9fab25f4e9c8dc3e379305da";
    [Serializable] public sealed class Record { public string path, assetPath, guid, sha256; public long bytes; }
    [Serializable] public sealed class RendererPlan { public string fileId, sourceFbxGuid, oldMaterialGuid, newMaterialGuid, materialLocalId; public int slotCount, replacementSlot, referenceSlot; }
    [Serializable] public sealed class Corner { public double x, y, z, u, v; }
    [Serializable] public sealed class Polygon { public int polygon, sourceMaterialIndex; public Corner[] corners; }
    [Serializable] public sealed class PrefabPlan
    {
        public string sourceModel, sourceFbxSha256, sourceFbxGuid, sourceMetadataSha256, prefab, prefabSha256, prefabGuid, prefabMetadataSha256;
        public long sourceFbxBytes, sourceMetadataBytes, prefabBytes, prefabMetadataBytes;
        public RendererPlan[] renderers; public Polygon[] sourceHairRegions;
    }
    [Serializable] public sealed class Plan
    {
        public int schemaVersion, product; public string kind, status; public bool actualAssetsModified, sourceArchivesModified;
        public Record topologyEvidence, importedAtlas, existingHairBoundAtlas, replacementMaterial, placeholderMaterial;
        public PrefabPlan[] prefabs;
    }
    [Serializable] public sealed class Product { public string id; public Record[] files; }
    [Serializable] public sealed class Manifest { public string stageRoot; public Product[] products; }
    [Serializable] public sealed class NativeProof
    {
        public int replacementSlot, referenceSlot, replacementTriangles, referenceTriangles, sourcePolygons, matchedPolygons;
        public int[] replacementRawMaterialIndices, referenceRawMaterialIndices, axes, signs; public double scale, maxPositionError, maxUvError;
        public bool uvVFlipped; public string meshGuid, meshLocalId, meshDataBeforeSha256, meshDataAfterSha256;
    }
    [Serializable] public sealed class Result
    {
        public string prefab, sourceModel, prefabGuid, prefabBeforeSha256, prefabAfterSha256, metadataSha256, sourceFbxSha256;
        public string rendererFileId; public bool writeStarted, complete, otherPrefabBytesExact, metadataExact, sourceExact;
        public long bytes; public NativeProof nativeProof;
    }
    [Serializable] public sealed class RetainedPreview { public string id, imagePath, imageSha256, recordSha256; }
    [Serializable] public sealed class Report
    {
        public int schemaVersion = 1, product = 11, observedUnityErrors;
        public string kind = "source-proven-missing-fbx-material-slot", status = "checking", project, runDirectory, startedUtc, completedUtc, planSha256, manifestSha256;
        public string previewPrefab, previewPath, originalPreviewsSha256, previewsAfterSha256, originalRepresentative, originalRepresentativeImageSha256, representativeImageAfterSha256;
        public bool originalRepresentativeDependsOnChangedPrefab, representativeWriteStarted, representativeRefreshed, sourceArchivesModified, originalSourcesModified, scenesOpened, unrelatedAssetsSaved;
        public string[] originalRepresentativeDependencies; public List<Result> prefabs = new List<Result>(); public List<string> errors = new List<string>();
        public List<RetainedPreview> unchangedPreviews = new List<RetainedPreview>(); public YamyamAssetLibraryBridge.PreviewRecord representativeAfter, additionalPreview;
    }
    sealed class Prepared { public PrefabPlan plan; public Result result; public byte[] before, after; public string absolute; }
    static string Project { get { return YamyamAssetLibraryIO.NormalPath(Path.GetDirectoryName(Application.dataPath)); } }
    static string Work { get { return YamyamAssetLibraryIO.NormalPath(Path.Combine(Project, "..")); } }
    static string Utc() { return DateTime.UtcNow.ToString("o"); }
    static string Absolute(string asset) { return Path.Combine(Project, asset.Replace('/', Path.DirectorySeparatorChar)); }
    static string Hash(byte[] value) { using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(value)).Replace("-", "").ToLowerInvariant(); }
    static string HashFile(string path) { using (var stream = File.OpenRead(path)) using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant(); }
    static void Guard()
    {
        if (!Application.isBatchMode || !Project.Replace('\\', '/').Equals(ExpectedProject, StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Material slot correction requires the exact isolated batch project.");
    }
    static void NoLinks(string path)
    {
        string full = YamyamAssetLibraryIO.NormalPath(path);
        if (!full.StartsWith(Work + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) && !full.Equals(Work, StringComparison.OrdinalIgnoreCase)) throw new IOException("Path escaped owned work.");
        for (string cursor = full; !string.IsNullOrEmpty(cursor); cursor = Path.GetDirectoryName(cursor)) {
            try { if ((File.GetAttributes(cursor) & FileAttributes.ReparsePoint) != 0) throw new IOException("Reparse path refused."); }
            catch (FileNotFoundException) { } catch (DirectoryNotFoundException) { }
            if (cursor.Equals(Path.GetPathRoot(full), StringComparison.OrdinalIgnoreCase)) return;
        }
        throw new IOException("Ownership guard failed.");
    }
    static string GuidAt(string path)
    {
        var match = Regex.Match(File.ReadAllText(path), @"(?m)^guid:[ \t]*([a-f0-9]{32})[ \t]*\r?$");
        if (!match.Success) throw new InvalidDataException("Metadata GUID missing."); return match.Groups[1].Value;
    }
    static void Exact(string path, long bytes, string sha)
    {
        NoLinks(path); if (new FileInfo(path).Length != bytes || HashFile(path) != sha) throw new InvalidDataException("Reviewed bytes changed: " + path);
    }
    static void Atomic(string path, byte[] bytes)
    {
        NoLinks(path); Directory.CreateDirectory(Path.GetDirectoryName(path)); string temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp"; NoLinks(temporary);
        using (var stream = new YamyamAssetLibraryIO.Stream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None)) { stream.Write(bytes, 0, bytes.Length); stream.Flush(true); }
        for (int attempt = 0; ; attempt++) {
            try { NoLinks(path); if (File.Exists(path)) File.Replace(temporary, path, null); else File.Move(temporary, path); return; }
            catch (IOException error) { int code = error.HResult & 0xffff; if (attempt >= 4 || !(code == 5 || code == 32 || code == 33 || code == 1175)) throw; }
            catch (UnauthorizedAccessException) { if (attempt >= 4) throw; }
            System.Threading.Thread.Sleep(100 * (attempt + 1));
        }
    }
    static void SaveReport(string path, Report value) { Atomic(path, new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(value, true) + "\n")); }
    public static byte[] PreparePatch(byte[] bytes, string rendererId, string modelGuid, string oldGuid, string newGuid)
    {
        string text = new UTF8Encoding(false, true).GetString(bytes);
        if (!text.StartsWith("%YAML 1.1", StringComparison.Ordinal)) throw new InvalidDataException("Only canonical Unity YAML variants are accepted.");
        string pattern = @"(?m)^    - target: \{fileID: " + Regex.Escape(rendererId) + @", guid: " + Regex.Escape(modelGuid) + @", type: 3\}\r?\n      propertyPath: '?m_Materials\.Array\.data\[1\]'?\r?\n      value: *\r?\n      objectReference: \{fileID: 2100000, guid: (" + Regex.Escape(oldGuid) + @"), type: 2\}";
        MatchCollection matches = Regex.Matches(text, pattern); if (matches.Count != 1) throw new InvalidDataException("Exactly one reviewed variant slot1 override is required.");
        Group group = matches[0].Groups[1]; string changed = text.Substring(0, group.Index) + newGuid + text.Substring(group.Index + group.Length);
        byte[] after = new UTF8Encoding(false, true).GetBytes(changed); int offset = Encoding.UTF8.GetByteCount(text.Substring(0, group.Index));
        if (after.Length != bytes.Length || group.Length != 32 || newGuid.Length != 32) throw new InvalidDataException("Slot correction changed serialized length.");
        for (int index = 0; index < bytes.Length; index++) if ((index < offset || index >= offset + 32) && bytes[index] != after[index]) throw new InvalidDataException("A byte outside the exact material GUID changed.");
        return after;
    }
    static string ObjectIdentity(UnityEngine.Object value)
    {
        string guid; long id; if (!value || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value, out guid, out id)) throw new InvalidDataException("Persistent object identity unavailable.");
        return guid + ":" + id.ToString(CultureInfo.InvariantCulture);
    }
    static Renderer RendererAt(PrefabPlan plan, bool after)
    {
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(plan.prefab); if (!prefab) throw new InvalidDataException("Generated prefab unavailable.");
        var renderers = prefab.GetComponentsInChildren<Renderer>(true); if (renderers.Length != 1 || plan.renderers.Length != 1) throw new InvalidDataException("Only the reviewed single-renderer variants are allowed.");
        var renderer = renderers[0]; var slots = renderer.sharedMaterials;
        if (slots.Length != 3 || ObjectIdentity(slots[2]) != HairGuid + ":2100000" || ObjectIdentity(slots[1]) != (after ? HairGuid : PlaceholderGuid) + ":2100000") throw new InvalidDataException("Native material slot order differs from the reviewed NoName/Hair signature.");
        UnityEngine.Object source = PrefabUtility.GetCorrespondingObjectFromOriginalSource(renderer);
        if (ObjectIdentity(source) != plan.sourceFbxGuid + ":" + plan.renderers[0].fileId) throw new InvalidDataException("Renderer original FBX identity changed.");
        return renderer;
    }
    static Mesh MeshAt(Renderer renderer)
    {
        var skin = renderer as SkinnedMeshRenderer; if (skin && skin.sharedMesh) return skin.sharedMesh;
        var filter = renderer.GetComponent<MeshFilter>(); if (filter && filter.sharedMesh) return filter.sharedMesh;
        throw new InvalidDataException("Native renderer mesh unavailable.");
    }
    static string MeshHash(Mesh mesh)
    {
        using (var memory = new MemoryStream()) using (var writer = new BinaryWriter(memory)) {
            writer.Write(ObjectIdentity(mesh)); writer.Write(mesh.vertexCount); writer.Write(mesh.subMeshCount);
            foreach (Vector3 point in mesh.vertices) { writer.Write(point.x); writer.Write(point.y); writer.Write(point.z); }
            foreach (Vector3 normal in mesh.normals) { writer.Write(normal.x); writer.Write(normal.y); writer.Write(normal.z); }
            foreach (Vector4 tangent in mesh.tangents) { writer.Write(tangent.x); writer.Write(tangent.y); writer.Write(tangent.z); writer.Write(tangent.w); }
            for (int channel = 0; channel < 8; channel++) { var uv = new List<Vector4>(); mesh.GetUVs(channel, uv); writer.Write(uv.Count); foreach (Vector4 value in uv) { writer.Write(value.x); writer.Write(value.y); writer.Write(value.z); writer.Write(value.w); } }
            foreach (Color color in mesh.colors) { writer.Write(color.r); writer.Write(color.g); writer.Write(color.b); writer.Write(color.a); }
            foreach (Matrix4x4 matrix in mesh.bindposes) for (int i = 0; i < 16; i++) writer.Write(matrix[i]);
            foreach (BoneWeight weight in mesh.boneWeights) { writer.Write(weight.boneIndex0); writer.Write(weight.boneIndex1); writer.Write(weight.boneIndex2); writer.Write(weight.boneIndex3); writer.Write(weight.weight0); writer.Write(weight.weight1); writer.Write(weight.weight2); writer.Write(weight.weight3); }
            writer.Write(mesh.blendShapeCount);if(mesh.blendShapeCount>0){var dv=new Vector3[mesh.vertexCount];var dn=new Vector3[mesh.vertexCount];var dt=new Vector3[mesh.vertexCount];
                for(int shape=0;shape<mesh.blendShapeCount;shape++){writer.Write(mesh.GetBlendShapeName(shape));int frames=mesh.GetBlendShapeFrameCount(shape);writer.Write(frames);for(int frame=0;frame<frames;frame++){writer.Write(mesh.GetBlendShapeFrameWeight(shape,frame));mesh.GetBlendShapeFrameVertices(shape,frame,dv,dn,dt);foreach(Vector3[] values in new[]{dv,dn,dt})foreach(Vector3 value in values){writer.Write(value.x);writer.Write(value.y);writer.Write(value.z);}}}}
            for (int submesh = 0; submesh < mesh.subMeshCount; submesh++) { writer.Write((int)mesh.GetTopology(submesh)); int[] indices = mesh.GetIndices(submesh); writer.Write(indices.Length); foreach (int index in indices) writer.Write(index); }
            writer.Flush(); return Hash(memory.ToArray());
        }
    }
    static double Coordinate(Corner c,int axis) { return axis==0?c.x:axis==1?c.y:c.z; }
    static Vector3 Transform(Corner c, int[] axes, int[] signs, double scale) { return new Vector3((float)(Coordinate(c,axes[0]) * signs[0] * scale), (float)(Coordinate(c,axes[1]) * signs[1] * scale), (float)(Coordinate(c,axes[2]) * signs[2] * scale)); }
    static bool Close(Vector3 a, Vector3 b, double epsilon) { return Math.Abs(a.x-b.x) <= epsilon && Math.Abs(a.y-b.y) <= epsilon && Math.Abs(a.z-b.z) <= epsilon; }
    static NativeProof RegionProof(PrefabPlan plan, Renderer renderer)
    {
        Mesh mesh = MeshAt(renderer); if (mesh.subMeshCount != 3 || mesh.GetTopology(1) != MeshTopology.Triangles || mesh.GetTopology(2) != MeshTopology.Triangles) throw new InvalidDataException("Expected three triangle submeshes.");
        Vector3[] vertices = mesh.vertices; Vector2[] uv = mesh.uv; if (uv.Length != vertices.Length || plan.sourceHairRegions == null || plan.sourceHairRegions.Length < 190) throw new InvalidDataException("Source/native corner data unavailable.");
        int[][] indices = { mesh.GetIndices(1), mesh.GetIndices(2) }; int[] used = indices.SelectMany(value => value).Distinct().ToArray();
        Vector3 minimum = vertices[used[0]], maximum = minimum; foreach (int i in used) { minimum = Vector3.Min(minimum, vertices[i]); maximum = Vector3.Max(maximum, vertices[i]); }
        int[][] permutations = { new[] {0,1,2}, new[] {0,2,1}, new[] {1,0,2}, new[] {1,2,0}, new[] {2,0,1}, new[] {2,1,0} };
        var solutions = new List<NativeProof>(); const double tolerance = .00001;
        foreach (int[] axes in permutations) for (int mask = 0; mask < 8; mask++) foreach (double scale in new[] {.01, 1d, 100d}) {
            int[] signs = { (mask&1)==0 ? 1:-1, (mask&2)==0 ? 1:-1, (mask&4)==0 ? 1:-1 };
            Vector3[] source = plan.sourceHairRegions.SelectMany(p => p.corners).Select(c => Transform(c,axes,signs,scale)).ToArray();
            Vector3 sourceMin = source[0], sourceMax = source[0]; foreach (Vector3 p in source) { sourceMin = Vector3.Min(sourceMin,p); sourceMax = Vector3.Max(sourceMax,p); }
            if (!Close(minimum,sourceMin,tolerance) || !Close(maximum,sourceMax,tolerance)) continue;
            foreach (bool flip in new[] {false,true}) {
                var counts = new Dictionary<int,int>(); var edges = new Dictionary<int,Dictionary<string,int>>(); var materialIndices = new[] {new HashSet<int>(),new HashSet<int>()}; bool valid = true; double maxPosition = 0, maxUv = 0;
                for (int sub = 0; sub < 2 && valid; sub++) for (int tri = 0; tri < indices[sub].Length && valid; tri += 3) {
                    var candidates = new List<Tuple<Polygon,int[]>>();
                    foreach (Polygon polygon in plan.sourceHairRegions) {
                        int[] local = new int[3]; bool polygonMatch = true;
                        for (int corner = 0; corner < 3; corner++) {
                            int index = indices[sub][tri+corner]; var found = new List<int>();
                            for (int n = 0; n < polygon.corners.Length; n++) { Corner c = polygon.corners[n]; Vector3 target = Transform(c,axes,signs,scale); double v = flip ? 1-c.v : c.v;
                                if (Close(vertices[index],target,tolerance) && Math.Abs(uv[index].x-c.u) <= tolerance && Math.Abs(uv[index].y-v) <= tolerance) found.Add(n); }
                            if (found.Count != 1) { polygonMatch=false;break; } local[corner]=found[0];
                        }
                        if (polygonMatch) candidates.Add(Tuple.Create(polygon,local));
                    }
                    if (candidates.Count != 1) { valid=false;break; }
                    Polygon matched = candidates[0].Item1; int[] localCorners = candidates[0].Item2;
                    if (localCorners.Distinct().Count()!=3) { valid=false;break; }
                    int previous; counts.TryGetValue(matched.polygon,out previous);counts[matched.polygon]=previous+1; materialIndices[sub].Add(matched.sourceMaterialIndex);
                    Dictionary<string,int> polygonEdges; if (!edges.TryGetValue(matched.polygon,out polygonEdges)) edges.Add(matched.polygon,polygonEdges=new Dictionary<string,int>());
                    for (int c = 0;c<3;c++) { int a=localCorners[c],b=localCorners[(c+1)%3];string edge=Math.Min(a,b)+":"+Math.Max(a,b);polygonEdges.TryGetValue(edge,out previous);polygonEdges[edge]=previous+1;
                        Corner expected=matched.corners[a];Vector3 expectedPosition=Transform(expected,axes,signs,scale);Vector3 actualPosition=vertices[indices[sub][tri+c]];
                        maxPosition=Math.Max(maxPosition,Math.Max(Math.Abs(expectedPosition.x-actualPosition.x),Math.Max(Math.Abs(expectedPosition.y-actualPosition.y),Math.Abs(expectedPosition.z-actualPosition.z))));
                        maxUv=Math.Max(maxUv,Math.Max(Math.Abs(expected.u-uv[indices[sub][tri+c]].x),Math.Abs((flip?1-expected.v:expected.v)-uv[indices[sub][tri+c]].y))); }
                }
                foreach (Polygon polygon in plan.sourceHairRegions) {
                    int actual; Dictionary<string,int> pe; if (!counts.TryGetValue(polygon.polygon,out actual) || actual!=polygon.corners.Length-2 || !edges.TryGetValue(polygon.polygon,out pe)) { valid=false;break; }
                    var boundary=new HashSet<string>();for(int n=0;n<polygon.corners.Length;n++){int next=(n+1)%polygon.corners.Length;boundary.Add(Math.Min(n,next)+":"+Math.Max(n,next));}
                    if (boundary.Any(e=>!pe.ContainsKey(e)||pe[e]!=1)||pe.Any(e=>!boundary.Contains(e.Key)&&e.Value!=2)) {valid=false;break;}
                }
                if (valid) { string guid;long id; if(!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(mesh,out guid,out id)||guid!=plan.sourceFbxGuid) throw new InvalidDataException("Native mesh is not owned by the exact source FBX.");
                    solutions.Add(new NativeProof {replacementSlot=1,referenceSlot=2,replacementTriangles=indices[0].Length/3,referenceTriangles=indices[1].Length/3,sourcePolygons=plan.sourceHairRegions.Length,matchedPolygons=counts.Count,
                        replacementRawMaterialIndices=materialIndices[0].OrderBy(n=>n).ToArray(),referenceRawMaterialIndices=materialIndices[1].OrderBy(n=>n).ToArray(),axes=axes,signs=signs,scale=scale,uvVFlipped=flip,maxPositionError=maxPosition,maxUvError=maxUv,meshGuid=guid,meshLocalId=id.ToString(CultureInfo.InvariantCulture),meshDataBeforeSha256=MeshHash(mesh)}); }
            }
        }
        if (solutions.Count!=1) throw new InvalidDataException("Native imported material regions must uniquely match the proved FBX Hair polygon/UV coverage: "+solutions.Count);
        return solutions[0];
    }
    static YamyamAssetLibraryBridge.PreviewRecord RenderChanged(string prefab, string image, string id, string title, string kind)
    {
        Type type=typeof(YamyamAssetLibraryBridge);var record=new YamyamAssetLibraryBridge.PreviewRecord{id=id,title=title,assetPath=prefab,imagePath=image,kind=kind};
        object[] args={AssetDatabase.LoadAssetAtPath<GameObject>(prefab),new Bounds()};object draws=type.GetMethod("Draws",BindingFlags.Static|BindingFlags.NonPublic).Invoke(null,args);
        type.GetMethod("RenderPreview",BindingFlags.Static|BindingFlags.NonPublic).Invoke(null,new[]{draws,args[1],record});
        if(!string.IsNullOrEmpty(record.error)||!File.Exists(image))throw new InvalidDataException("Corrected prefab preview failed: "+record.error);return record;
    }
    public static string ReplaceOnePreviewRecord(string json,YamyamAssetLibraryBridge.PreviewRecord replacement)
    {
        // String-aware object boundaries retain every byte outside this record.
        var stack=new Stack<int>();var matches=new List<Tuple<int,int>>();bool quoted=false,escape=false;
        for(int i=0;i<json.Length;i++){char c=json[i];if(quoted){if(escape)escape=false;else if(c=='\\')escape=true;else if(c=='"')quoted=false;continue;}if(c=='"'){quoted=true;continue;}if(c=='{')stack.Push(i);else if(c=='}'){
            if(stack.Count==0)throw new InvalidDataException("Unbalanced preview JSON.");int start=stack.Pop();string candidate=json.Substring(start,i-start+1);
            if(candidate.IndexOf("\"products\"",StringComparison.Ordinal)>=0)continue;
            var record=JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewRecord>(candidate);if(record!=null&&record.id==replacement.id)matches.Add(Tuple.Create(start,i+1));}}
        if(quoted||stack.Count!=0||matches.Count!=1)throw new InvalidDataException("Exactly one preview record must match the affected product.");
        int begin=matches[0].Item1,end=matches[0].Item2,line=json.LastIndexOf('\n',begin);string indent=json.Substring(line+1,begin-line-1);if(indent.Any(c=>c!=' '&&c!='\t'))throw new InvalidDataException("Unexpected preview record indentation.");
        string serialized=JsonUtility.ToJson(replacement,true).Replace("\n","\n"+indent);return json.Substring(0,begin)+serialized+json.Substring(end);
    }
    static void Run()
    {
        Guard();if(Application.unityVersion!="6000.6.0f1"||EditorApplication.isCompiling||EditorApplication.isUpdating)throw new InvalidOperationException("Expected idle Unity6000.6.");
        string local=Path.Combine(Project,"Library/YamyamAssetLibrary"),run=Path.Combine(local,"material-slot-correction",DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ")+"-"+Guid.NewGuid().ToString("N"));NoLinks(run);Directory.CreateDirectory(run);
        string reportPath=Path.Combine(run,"report.json");var report=new Report{project=Project,runDirectory=run,startedUtc=Utc(),planSha256=PlanSha256};
        Application.LogCallback capture=(message,stack,type)=>{if(type==LogType.Error||type==LogType.Assert||type==LogType.Exception){report.observedUnityErrors++;report.errors.Add(message);}};Application.logMessageReceived+=capture;
        try {
            string planPath=Path.Combine(Work,"product011-missing-material-correction-plan.json");NoLinks(planPath);if(HashFile(planPath)!=PlanSha256)throw new InvalidDataException("Reviewed source/material plan changed.");
            Plan plan=JsonUtility.FromJson<Plan>(File.ReadAllText(planPath));if(plan.schemaVersion!=1||plan.product!=11||plan.kind!="source-proven-missing-fbx-material-slot"||plan.status!="prepared-read-only"||plan.actualAssetsModified||plan.sourceArchivesModified||plan.prefabs==null||plan.prefabs.Length!=15)throw new InvalidDataException("Unexpected plan scope.");
            Exact(plan.topologyEvidence.path,plan.topologyEvidence.bytes,plan.topologyEvidence.sha256);
            string manifestPath=Path.Combine(Work,"staging-manifest.json");NoLinks(manifestPath);report.manifestSha256=HashFile(manifestPath);Manifest manifest=JsonUtility.FromJson<Manifest>(File.ReadAllText(manifestPath));
            if(manifest.products==null||manifest.products.Length!=84||manifest.products.Select(p=>p.id).Distinct().Count()!=84||!YamyamAssetLibraryIO.NormalPath(manifest.stageRoot).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(Root.TrimEnd('/'))),StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Exact84-product isolated manifest required.");
            Product product=manifest.products.Single(p=>p.id=="011");var canonical=product.files.ToDictionary(r=>r.path,StringComparer.Ordinal);
            foreach(Record asset in new[]{plan.importedAtlas,plan.existingHairBoundAtlas,plan.replacementMaterial,plan.placeholderMaterial}){Exact(asset.path,asset.bytes,asset.sha256);if(GuidAt(asset.path+".meta")!=asset.guid||AssetDatabase.AssetPathToGUID(asset.assetPath)!=asset.guid)throw new InvalidDataException("Proved texture/material GUID changed.");}
            if(plan.replacementMaterial.guid!=HairGuid||plan.placeholderMaterial.guid!=PlaceholderGuid||HashFile(plan.importedAtlas.path)!=HashFile(plan.existingHairBoundAtlas.path))throw new InvalidDataException("Exact source atlas/replacement material binding changed.");
            Material nativeHair=AssetDatabase.LoadAssetAtPath<Material>(plan.replacementMaterial.assetPath);Texture nativeAtlas=nativeHair?nativeHair.GetTexture("_BaseMap"):null;
            if(!nativeHair||nativeHair.shader.name!="Universal Render Pipeline/Lit"||ObjectIdentity(nativeHair)!=HairGuid+":2100000"||!(nativeAtlas is Texture2D)||ObjectIdentity(nativeAtlas)!=plan.existingHairBoundAtlas.guid+":2800000"||nativeHair.GetTexture("_MainTex")!=nativeAtlas)throw new InvalidDataException("Native Hair material/Texture2D atlas binding does not match the exact-byte source proof.");
            File.Copy(planPath,Path.Combine(run,"plan.json"),false);File.Copy(plan.topologyEvidence.path,Path.Combine(run,"topology-evidence.json"),false);
            var prepared=new List<Prepared>();var unique=new HashSet<string>(StringComparer.Ordinal);
            foreach(PrefabPlan item in plan.prefabs){
                if(!unique.Add(item.prefab)||!item.prefab.StartsWith(Root+Folder+"/Generated/Prefabs/",StringComparison.Ordinal)||!item.prefab.EndsWith(".prefab",StringComparison.Ordinal)||!item.sourceModel.StartsWith(Root+Folder+"/Characters Full/Unity FBX/Characters/Character_2_",StringComparison.Ordinal)||item.renderers==null||item.renderers.Length!=1)throw new InvalidDataException("Unreviewed target/source path.");
                RendererPlan rendererPlan=item.renderers[0];if(rendererPlan.replacementSlot!=1||rendererPlan.referenceSlot!=2||rendererPlan.slotCount!=3||rendererPlan.oldMaterialGuid!=PlaceholderGuid||rendererPlan.newMaterialGuid!=HairGuid||rendererPlan.sourceFbxGuid!=item.sourceFbxGuid)throw new InvalidDataException("Unexpected source/slot plan.");
                string relative=item.sourceModel.Substring(Root.Length);Record source;if(!canonical.TryGetValue(relative,out source)||source.sha256!=item.sourceFbxSha256||source.bytes!=item.sourceFbxBytes)throw new InvalidDataException("Canonical source FBX receipt differs.");
                Exact(Absolute(item.sourceModel),item.sourceFbxBytes,item.sourceFbxSha256);Exact(Absolute(item.sourceModel)+".meta",item.sourceMetadataBytes,item.sourceMetadataSha256);
                Exact(Absolute(item.prefab),item.prefabBytes,item.prefabSha256);Exact(Absolute(item.prefab)+".meta",item.prefabMetadataBytes,item.prefabMetadataSha256);
                if(GuidAt(Absolute(item.sourceModel)+".meta")!=item.sourceFbxGuid||GuidAt(Absolute(item.prefab)+".meta")!=item.prefabGuid||AssetDatabase.AssetPathToGUID(item.prefab)!=item.prefabGuid)throw new InvalidDataException("Source/prefab GUID differs.");
                NativeProof native=RegionProof(item,RendererAt(item,false));byte[] before=File.ReadAllBytes(Absolute(item.prefab));if(Hash(before)!=item.prefabSha256)throw new InvalidDataException("Prefab changed during native preflight.");
                byte[] after=PreparePatch(before,rendererPlan.fileId,item.sourceFbxGuid,PlaceholderGuid,HairGuid);
                var result=new Result{prefab=item.prefab,sourceModel=item.sourceModel,prefabGuid=item.prefabGuid,prefabBeforeSha256=item.prefabSha256,prefabAfterSha256=Hash(after),metadataSha256=item.prefabMetadataSha256,sourceFbxSha256=item.sourceFbxSha256,rendererFileId=rendererPlan.fileId,bytes=before.Length,nativeProof=native};
                report.prefabs.Add(result);prepared.Add(new Prepared{plan=item,result=result,before=before,after=after,absolute=Absolute(item.prefab)});
            }
            string generatedFolder=Absolute(Root+Folder+"/Generated/Prefabs");NoLinks(generatedFolder);var placeholderPrefabs=new HashSet<string>(StringComparer.Ordinal);
            foreach(string path in Directory.EnumerateFileSystemEntries(generatedFolder)){NoLinks(path);if(Directory.Exists(path))throw new InvalidDataException("Unexpected nested prefab folder.");if(!path.EndsWith(".prefab",StringComparison.Ordinal))continue;
                if(File.ReadAllText(path).Contains(PlaceholderGuid))placeholderPrefabs.Add(path.Substring(Project.Length+1).Replace('\\','/'));}
            if(!placeholderPrefabs.SetEquals(unique))throw new InvalidDataException("Complete P011 generated placeholder uses no longer match the exact15proved prefabs.");
            string previewsPath=Path.Combine(local,"previews.json");NoLinks(previewsPath);var previews=JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));
            if(previews.products==null||previews.products.Count!=84||string.IsNullOrEmpty(previews.completedUtc))throw new InvalidDataException("Completed84-product preview proof required.");
            var representative=previews.products.Single(p=>p.id=="011");if(!string.IsNullOrEmpty(representative.error)||string.IsNullOrEmpty(representative.assetPath)||string.IsNullOrEmpty(representative.imagePath))throw new InvalidDataException("P011 preview incomplete.");
            NoLinks(representative.imagePath);report.originalPreviewsSha256=HashFile(previewsPath);report.originalRepresentative=representative.assetPath;report.originalRepresentativeImageSha256=HashFile(representative.imagePath);
            report.originalRepresentativeDependencies=AssetDatabase.GetDependencies(representative.assetPath,true).Distinct().OrderBy(p=>p,StringComparer.Ordinal).ToArray();report.originalRepresentativeDependsOnChangedPrefab=report.originalRepresentativeDependencies.Any(p=>unique.Contains(p));
            File.Copy(previewsPath,Path.Combine(run,"previews.before.json"),false);File.Copy(representative.imagePath,Path.Combine(run,"representative.before.png"),false);
            if(HashFile(Path.Combine(run,"previews.before.json"))!=report.originalPreviewsSha256||HashFile(Path.Combine(run,"representative.before.png"))!=report.originalRepresentativeImageSha256)throw new IOException("Representative backup verification failed.");
            foreach(var prior in previews.products.Where(p=>p.id!="011")){if(!string.IsNullOrEmpty(prior.error)||string.IsNullOrEmpty(prior.imagePath))throw new InvalidDataException("Unchanged representative proof incomplete.");NoLinks(prior.imagePath);report.unchangedPreviews.Add(new RetainedPreview{id=prior.id,imagePath=prior.imagePath,imageSha256=HashFile(prior.imagePath),recordSha256=Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(prior)))});}
            if(report.unchangedPreviews.Count!=83)throw new InvalidDataException("Exactly83 other preview products must be preserved.");
            foreach(Prepared item in prepared){string backup=Path.Combine(run,"backups",item.plan.prefab.Substring(Root.Length));NoLinks(backup);Directory.CreateDirectory(Path.GetDirectoryName(backup));Exact(item.absolute,item.plan.prefabBytes,item.plan.prefabSha256);File.Copy(item.absolute,backup,false);File.Copy(item.absolute+".meta",backup+".meta",false);Exact(backup,item.plan.prefabBytes,item.plan.prefabSha256);Exact(backup+".meta",item.plan.prefabMetadataBytes,item.plan.prefabMetadataSha256);}
            if(report.observedUnityErrors!=0)throw new InvalidDataException("Native errors during complete preflight; no targets written.");
            foreach(Prepared item in prepared){report.status="writing-owned-prefab";item.result.writeStarted=true;SaveReport(reportPath,report);Exact(item.absolute,item.plan.prefabBytes,item.plan.prefabSha256);Atomic(item.absolute,item.after);AssetDatabase.ImportAsset(item.plan.prefab,ImportAssetOptions.ForceUpdate|ImportAssetOptions.ForceSynchronousImport);
                Mesh mesh=MeshAt(RendererAt(item.plan,true));item.result.nativeProof.meshDataAfterSha256=MeshHash(mesh);if(item.result.nativeProof.meshDataAfterSha256!=item.result.nativeProof.meshDataBeforeSha256)throw new InvalidDataException("Mesh/UV/skin/index identity changed.");
                Exact(item.absolute,item.after.Length,item.result.prefabAfterSha256);Exact(item.absolute+".meta",item.plan.prefabMetadataBytes,item.plan.prefabMetadataSha256);Exact(Absolute(item.plan.sourceModel),item.plan.sourceFbxBytes,item.plan.sourceFbxSha256);Exact(Absolute(item.plan.sourceModel)+".meta",item.plan.sourceMetadataBytes,item.plan.sourceMetadataSha256);
                if(AssetDatabase.AssetPathToGUID(item.plan.prefab)!=item.plan.prefabGuid)throw new InvalidDataException("Stable prefab GUID changed.");item.result.otherPrefabBytesExact=true;item.result.metadataExact=true;item.result.sourceExact=true;item.result.complete=true;SaveReport(reportPath,report);
            }
            report.previewPrefab=prepared.Single(p=>p.plan.sourceModel.EndsWith("/Character_2_2_1.fbx",StringComparison.Ordinal)).plan.prefab;report.previewPath=Path.Combine(run,"P011-Character_2_2_1-corrected-material-slot.png");report.additionalPreview=RenderChanged(report.previewPrefab,report.previewPath,"011",representative.title,"source-proven-material-slot-correction");
            if(report.originalRepresentativeDependsOnChangedPrefab){
                if(HashFile(previewsPath)!=report.originalPreviewsSha256||HashFile(representative.imagePath)!=report.originalRepresentativeImageSha256)throw new InvalidDataException("Representative proof changed before its targeted refresh.");
                report.status="refreshing-owned-P011-preview";report.representativeWriteStarted=true;SaveReport(reportPath,report);
                report.representativeAfter=RenderChanged(representative.assetPath,representative.imagePath,"011",representative.title,representative.kind);string originalJson=File.ReadAllText(previewsPath);Atomic(previewsPath,Encoding.UTF8.GetBytes(ReplaceOnePreviewRecord(originalJson,report.representativeAfter)));report.representativeRefreshed=true;
            }else report.representativeAfter=representative;
            report.previewsAfterSha256=HashFile(previewsPath);report.representativeImageAfterSha256=HashFile(representative.imagePath);
            foreach(Prepared item in prepared){Exact(item.absolute,item.after.Length,item.result.prefabAfterSha256);Exact(item.absolute+".meta",item.plan.prefabMetadataBytes,item.plan.prefabMetadataSha256);Exact(Absolute(item.plan.sourceModel),item.plan.sourceFbxBytes,item.plan.sourceFbxSha256);Exact(Absolute(item.plan.sourceModel)+".meta",item.plan.sourceMetadataBytes,item.plan.sourceMetadataSha256);}
            foreach(Record asset in new[]{plan.importedAtlas,plan.existingHairBoundAtlas,plan.replacementMaterial,plan.placeholderMaterial})Exact(asset.path,asset.bytes,asset.sha256);
            if(HashFile(manifestPath)!=report.manifestSha256)throw new InvalidDataException("Canonical proof changed during scoped correction.");
            if(!report.representativeRefreshed&&(report.previewsAfterSha256!=report.originalPreviewsSha256||report.representativeImageAfterSha256!=report.originalRepresentativeImageSha256))throw new InvalidDataException("Unaffected P011 representative changed.");
            var afterPreviews=JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));if(afterPreviews.products.Count!=84)throw new InvalidDataException("Preview product count changed.");
            foreach(RetainedPreview retained in report.unchangedPreviews){var current=afterPreviews.products.Single(p=>p.id==retained.id);if(Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(current)))!=retained.recordSha256||HashFile(retained.imagePath)!=retained.imageSha256)throw new InvalidDataException("One of83 untouched preview records/PNGs changed.");}
            if(report.observedUnityErrors!=0)throw new InvalidDataException("Native errors during scoped correction/render.");report.status="complete";
        }
        catch(Exception error){report.status="failed";report.errors.Add(error.ToString());throw;}
        finally{Application.logMessageReceived-=capture;report.completedUtc=Utc();SaveReport(reportPath,report);SaveReport(Path.Combine(local,"material-slot-correction-report.json"),report);}
    }
    public static void RunHeadless()
    {
        Guard();int code=0;try{Run();}catch(Exception error){UnityEngine.Debug.LogError(error);code=1;}EditorApplication.Exit(code);
    }
}

// Separate explicit entrypoint: recover only the source-proved P067 emission.
public static partial class YamyamAssetLibraryMaterialSlots
{
    const string EmissionFolder = "067-free-halloween-pumpkin-candle-pack-jack-o-lantern-props-godot-unity-blend";
    const string EmissionPlanSha256 = "2c659fa0dbc83fc0f6612a7fa10fa6fabca995dee91da73d1b73c07f29949f33";
    const string EmissionGuid = "37680d02d08672948bd6b4f95b52d11b";
    [Serializable] public sealed class EmissionComparison { public string status; public int ambiguousTriangleCount, polygonTriangleCountMismatchCount, sourcePolygonCoverage, sourcePolygonCount, topologyErrorCount; public double maxPositionError, maxUvError; }
    [Serializable] public sealed class EmissionSource { public string sourceModel, sourceFbxGuid, glbMember, glbSha256; public long glbBytes; public Record sourceFbx, sourceMetadata; public EmissionComparison regionComparison; }
    [Serializable] public sealed class EmissionPrefab { public string sourceModel, rendererFileId; public int materialSlot; public Record prefab, prefabMetadata; }
    [Serializable] public sealed class EmissionPlan
    {
        public int schemaVersion; public string kind, status, sourceFactorColorSpace; public float[] sourceEmissionFactor;
        public bool noTextureConnectionOrAtlasInEitherSource, sourceArchivesModified, actualAssetsModified;
        public EmissionSource[] sourceCounterparts; public Record targetMaterial, targetMetadata; public EmissionPrefab[] prefabs;
    }
    [Serializable] public sealed class EmissionReport
    {
        public int schemaVersion=1, product=67, sourceModelsVerified, affectedGeneratedPrefabs, observedUnityErrors;
        public string kind="source-proven-p067-gltf-emission",status="checking",project,runDirectory,startedUtc,completedUtc,sourceProofSha256,manifestSha256;
        public string materialPath,materialGuid,materialBeforeSha256,materialAfterSha256,metadataSha256,otherShaderPropertiesBeforeSha256,otherShaderPropertiesAfterSha256;
        public long localIdBefore,localIdAfter;public Vector4 sourceLinearEmissionFactor,storedLinearEmissionFactor;public string activeColorSpace,conversionPolicy;
        public int giFlagsBefore,giFlagsAfter;public bool writeStarted,applied,sourceArchivesModified,originalSourcesModified,scenesOpened,unrelatedAssetsSaved,bloomOrProjectSettingsChanged;
        public string originalPreviewsSha256,previewsAfterSha256,representativeImageBeforeSha256,representativeImageAfterSha256,representativeAssetPath,previewPath,previewPrefab;
        public bool representativeDependsOnChangedMaterial,representativeWriteStarted,representativeRefreshed;
        public List<Record> retainedSources=new List<Record>();public List<RetainedPreview> unchangedPreviews=new List<RetainedPreview>();
        public YamyamAssetLibraryBridge.PreviewRecord representativeAfter,additionalPreview;public List<string> errors=new List<string>();
    }
    static string OtherEmissionProperties(Material material,string persistentIdentity=null)
    {
        var text=new StringBuilder();text.Append(material.shader.name).Append('|').Append(persistentIdentity??ObjectIdentity(material)).Append('|').Append(material.renderQueue).Append('|').Append(material.enableInstancing).Append('|').Append(material.doubleSidedGI).Append('|').Append(material.GetTag("RenderType",false));
        foreach(string keyword in material.shaderKeywords.Where(k=>k!="_EMISSION").OrderBy(k=>k,StringComparer.Ordinal))text.Append("\nkeyword:").Append(keyword);
        for(int index=0;index<material.shader.GetPropertyCount();index++){
            string name=material.shader.GetPropertyName(index);if(name=="_EmissionColor")continue;var type=material.shader.GetPropertyType(index);text.Append('\n').Append(name).Append(':').Append(type).Append(':');
            if(type==UnityEngine.Rendering.ShaderPropertyType.Texture){Texture texture=material.GetTexture(name);text.Append(texture?ObjectIdentity(texture):"null");Vector2 scale=material.GetTextureScale(name),offset=material.GetTextureOffset(name);foreach(float value in new[]{scale.x,scale.y,offset.x,offset.y})text.Append('|').Append(value.ToString("R",CultureInfo.InvariantCulture));}
            else if(type==UnityEngine.Rendering.ShaderPropertyType.Color||type==UnityEngine.Rendering.ShaderPropertyType.Vector){Vector4 value=material.GetVector(name);for(int n=0;n<4;n++)text.Append('|').Append(value[n].ToString("R",CultureInfo.InvariantCulture));}
            else if(type==UnityEngine.Rendering.ShaderPropertyType.Int)text.Append(material.GetInteger(name));else text.Append(material.GetFloat(name).ToString("R",CultureInfo.InvariantCulture));
        }
        for(int pass=0;pass<material.passCount;pass++){string name=material.GetPassName(pass);text.Append("\npass:").Append(name).Append(':').Append(material.GetShaderPassEnabled(name));}
        return Hash(Encoding.UTF8.GetBytes(text.ToString()));
    }
    static void ValidateEmissionLit(Material material)
    {
        Type type=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("UnityEditor.Rendering.Universal.ShaderGUI.LitShader",false)).FirstOrDefault(t=>t!=null);
        var validator=type==null?null:Activator.CreateInstance(type,true) as ShaderGUI;if(validator==null)throw new InvalidOperationException("Installed official URP Lit validator unavailable.");validator.ValidateMaterial(material);
    }
    static void EmissionIdentity(EmissionPrefab target,Record material)
    {
        var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(target.prefab.assetPath);if(!prefab)throw new InvalidDataException("Proved P067 prefab unavailable.");var renderers=prefab.GetComponentsInChildren<Renderer>(true);
        if(renderers.Length!=1||target.materialSlot!=1)throw new InvalidDataException("P067 renderer/slot scope changed.");Renderer renderer=renderers[0];Material[] slots=renderer.sharedMaterials;
        if(slots.Length!=2||ObjectIdentity(slots[1])!=material.guid+":2100000")throw new InvalidDataException("P067 native emission material binding differs from proved slot1.");
        string sourceGuid=AssetDatabase.AssetPathToGUID(target.sourceModel);var original=PrefabUtility.GetCorrespondingObjectFromOriginalSource(renderer);
        if(ObjectIdentity(original)!=sourceGuid+":"+target.rendererFileId||ObjectIdentity(MeshAt(renderer)).Split(':')[0]!=sourceGuid)throw new InvalidDataException("P067 native renderer/mesh source identity changed.");
    }
    static bool NearVector(Vector4 a,Vector4 b){for(int n=0;n<4;n++)if(Math.Abs(a[n]-b[n])>.000001f)return false;return true;}
    static void RunEmission()
    {
        Guard();if(Application.unityVersion!="6000.6.0f1"||EditorApplication.isCompiling||EditorApplication.isUpdating||QualitySettings.activeColorSpace!=ColorSpace.Linear)throw new InvalidOperationException("Expected idle Unity6000.6 with the unchanged Linear project color space.");
        string local=Path.Combine(Project,"Library/YamyamAssetLibrary"),run=Path.Combine(local,"emission-correction",DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ")+"-"+Guid.NewGuid().ToString("N"));NoLinks(run);Directory.CreateDirectory(run);
        var report=new EmissionReport{project=Project,runDirectory=run,startedUtc=Utc(),sourceProofSha256=EmissionPlanSha256,activeColorSpace=QualitySettings.activeColorSpace.ToString(),conversionPolicy="glTF emissiveFactor is already linear; SetVector writes the exact shader uniform without SetColor HDR gamma-to-linear conversion."};string reportPath=Path.Combine(run,"report.json");
        Action persist=()=>Atomic(reportPath,new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(report,true)+"\n"));Application.LogCallback capture=(message,stack,type)=>{if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert){report.observedUnityErrors++;report.errors.Add(message);}};Application.logMessageReceived+=capture;Material prepared=null;
        try{
            string planPath=Path.Combine(Work,"product067-emission-correction-plan.json");NoLinks(planPath);if(HashFile(planPath)!=EmissionPlanSha256)throw new InvalidDataException("Reviewed P067 source/region proof changed.");var plan=JsonUtility.FromJson<EmissionPlan>(File.ReadAllText(planPath));
            if(plan.schemaVersion!=1||plan.kind!="source-proven-p067-gltf-emission"||plan.status!="prepared-read-only"||plan.sourceFactorColorSpace!="linear-sRGB"||plan.sourceArchivesModified||plan.actualAssetsModified||!plan.noTextureConnectionOrAtlasInEitherSource||plan.sourceCounterparts==null||plan.sourceCounterparts.Length!=3||plan.prefabs==null||plan.prefabs.Length!=3||plan.sourceEmissionFactor==null||plan.sourceEmissionFactor.Length!=3)throw new InvalidDataException("Unreviewed P067 correction scope.");
            Vector4 linear=new Vector4(plan.sourceEmissionFactor[0],plan.sourceEmissionFactor[1],plan.sourceEmissionFactor[2],1);if(!NearVector(linear,new Vector4(.8000000715255737f,.01814323104918003f,.02997703291475773f,1)))throw new InvalidDataException("Unexpected source-linear emission factor.");report.sourceLinearEmissionFactor=linear;
            string manifestPath=Path.Combine(Work,"staging-manifest.json");NoLinks(manifestPath);report.manifestSha256=HashFile(manifestPath);var manifest=JsonUtility.FromJson<Manifest>(File.ReadAllText(manifestPath));
            if(manifest.products==null||manifest.products.Length!=84||manifest.products.Select(p=>p.id).Distinct().Count()!=84||!YamyamAssetLibraryIO.NormalPath(manifest.stageRoot).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(Root.TrimEnd('/'))),StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Exact isolated84-product manifest required.");var canonical=manifest.products.Single(p=>p.id=="067").files.ToDictionary(r=>r.path,StringComparer.Ordinal);
            foreach(EmissionSource source in plan.sourceCounterparts){
                if(!Regex.IsMatch(source.sourceModel,"^"+Regex.Escape(Root+EmissionFolder+"/FBX/EA_Pumpkin_01")+"[abc]\\.fbx$")||source.sourceFbx.path!=Absolute(source.sourceModel)||source.sourceMetadata.path!=Absolute(source.sourceModel)+".meta")throw new InvalidDataException("P067 source escaped exact3pumpkin scope.");
                Record current;if(!canonical.TryGetValue(source.sourceModel.Substring(Root.Length),out current)||current.sha256!=source.sourceFbx.sha256||current.bytes!=source.sourceFbx.bytes)throw new InvalidDataException("Canonical P067 source receipt differs.");
                Exact(source.sourceFbx.path,source.sourceFbx.bytes,source.sourceFbx.sha256);Exact(source.sourceMetadata.path,source.sourceMetadata.bytes,source.sourceMetadata.sha256);if(GuidAt(source.sourceMetadata.path)!=source.sourceFbxGuid||AssetDatabase.AssetPathToGUID(source.sourceModel)!=source.sourceFbxGuid)throw new InvalidDataException("P067 source metadata identity changed.");
                EmissionComparison proof=source.regionComparison;if(proof==null||proof.status!="exact-region-topology-and-uv-match"||proof.sourcePolygonCoverage!=proof.sourcePolygonCount||proof.ambiguousTriangleCount!=0||proof.polygonTriangleCountMismatchCount!=0||proof.topologyErrorCount!=0||proof.maxPositionError>.000001||proof.maxUvError>.000001)throw new InvalidDataException("P067 GLB/FBX region proof is incomplete.");report.sourceModelsVerified++;report.retainedSources.Add(source.sourceFbx);report.retainedSources.Add(source.sourceMetadata);
            }
            if(plan.sourceCounterparts.Select(s=>s.sourceModel).Distinct().Count()!=3||!new HashSet<string>(plan.prefabs.Select(p=>p.sourceModel)).SetEquals(plan.sourceCounterparts.Select(s=>s.sourceModel)))throw new InvalidDataException("P067 source/prefab mapping is not a bijection.");
            Record target=plan.targetMaterial;if(target.assetPath!=Root+EmissionFolder+"/Generated/Materials/emiss_3bf86f37223e.mat"||target.guid!=EmissionGuid||target.path!=Absolute(target.assetPath)||plan.targetMetadata.path!=target.path+".meta")throw new InvalidDataException("Unexpected P067 shared material.");report.materialPath=target.assetPath;report.materialGuid=target.guid;report.materialBeforeSha256=target.sha256;report.metadataSha256=plan.targetMetadata.sha256;
            Exact(target.path,target.bytes,target.sha256);Exact(plan.targetMetadata.path,plan.targetMetadata.bytes,plan.targetMetadata.sha256);if(GuidAt(plan.targetMetadata.path)!=EmissionGuid||AssetDatabase.AssetPathToGUID(target.assetPath)!=EmissionGuid)throw new InvalidDataException("P067 material GUID changed.");
            foreach(EmissionPrefab prefab in plan.prefabs){if(!prefab.prefab.assetPath.StartsWith(Root+EmissionFolder+"/Generated/Prefabs/",StringComparison.Ordinal)||prefab.prefab.path!=Absolute(prefab.prefab.assetPath)||prefab.prefabMetadata.path!=prefab.prefab.path+".meta")throw new InvalidDataException("P067 generated prefab scope changed.");Exact(prefab.prefab.path,prefab.prefab.bytes,prefab.prefab.sha256);Exact(prefab.prefabMetadata.path,prefab.prefabMetadata.bytes,prefab.prefabMetadata.sha256);if(GuidAt(prefab.prefabMetadata.path)!=prefab.prefab.guid)throw new InvalidDataException("P067 prefab GUID differs.");EmissionIdentity(prefab,target);report.affectedGeneratedPrefabs++;report.retainedSources.Add(prefab.prefab);report.retainedSources.Add(prefab.prefabMetadata);}
            string folder=Absolute(Root+EmissionFolder+"/Generated/Prefabs");NoLinks(folder);var actualReferences=new HashSet<string>(StringComparer.Ordinal);foreach(string path in Directory.EnumerateFileSystemEntries(folder)){NoLinks(path);if(Directory.Exists(path))throw new InvalidDataException("Unexpected nested P067 prefab folder.");if(path.EndsWith(".prefab",StringComparison.Ordinal)&&File.ReadAllText(path).Contains(EmissionGuid))actualReferences.Add(path.Substring(Project.Length+1).Replace('\\','/'));}
            if(!actualReferences.SetEquals(plan.prefabs.Select(p=>p.prefab.assetPath)))throw new InvalidDataException("P067 material references exceed the exact3proved pumpkins.");
            var material=AssetDatabase.LoadAssetAtPath<Material>(target.assetPath);string materialGuid;long materialId;if(!material||material.shader.name!="Universal Render Pipeline/Lit"||!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material,out materialGuid,out materialId)||materialGuid!=EmissionGuid||materialId!=2100000)throw new InvalidDataException("Persistent P067 URP Lit material missing.");
            int emissionIndex=material.shader.FindPropertyIndex("_EmissionColor");if(emissionIndex<0||material.shader.GetPropertyType(emissionIndex)!=UnityEngine.Rendering.ShaderPropertyType.Color||(material.shader.GetPropertyFlags(emissionIndex)&UnityEngine.Rendering.ShaderPropertyFlags.HDR)==0||material.GetTexture("_EmissionMap")||material.GetTexture("_BaseMap")||!NearVector(material.GetVector("_BaseColor"),new Vector4(0,0,0,1))||!NearVector(material.GetVector("_EmissionColor"),new Vector4(0,0,0,1))||material.IsKeywordEnabled("_EMISSION"))throw new InvalidDataException("P067 original untextured black/nonemissive signature differs.");
            report.localIdBefore=materialId;report.giFlagsBefore=(int)material.globalIlluminationFlags;report.otherShaderPropertiesBeforeSha256=OtherEmissionProperties(material);prepared=new Material(material);prepared.name=material.name;
            prepared.SetVector("_EmissionColor",linear);prepared.globalIlluminationFlags=material.globalIlluminationFlags&~MaterialGlobalIlluminationFlags.EmissiveIsBlack;ValidateEmissionLit(prepared);
            // The temporary material has a different instance identity; compare
            // identical shader values using the original material identity.
            if(!NearVector(prepared.GetVector("_EmissionColor"),linear)||!prepared.IsKeywordEnabled("_EMISSION")||(int)prepared.globalIlluminationFlags!=(report.giFlagsBefore&~(int)MaterialGlobalIlluminationFlags.EmissiveIsBlack)||OtherEmissionProperties(prepared,ObjectIdentity(material))!=report.otherShaderPropertiesBeforeSha256)throw new InvalidDataException("Official Lit validator did not preserve the exact linear emission/activation/other shader values.");
            string previewsPath=Path.Combine(local,"previews.json");NoLinks(previewsPath);var previews=JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));if(previews.products==null||previews.products.Count!=84||string.IsNullOrEmpty(previews.completedUtc))throw new InvalidDataException("Completed84product previews required.");var representative=previews.products.Single(p=>p.id=="067");if(!string.IsNullOrEmpty(representative.error)||string.IsNullOrEmpty(representative.assetPath)||string.IsNullOrEmpty(representative.imagePath))throw new InvalidDataException("P067 representative preview incomplete.");NoLinks(representative.imagePath);report.originalPreviewsSha256=HashFile(previewsPath);report.representativeAssetPath=representative.assetPath;report.representativeImageBeforeSha256=HashFile(representative.imagePath);report.representativeDependsOnChangedMaterial=AssetDatabase.GetDependencies(representative.assetPath,true).Contains(target.assetPath,StringComparer.Ordinal);
            foreach(var previous in previews.products.Where(p=>p.id!="067")){NoLinks(previous.imagePath);report.unchangedPreviews.Add(new RetainedPreview{id=previous.id,imagePath=previous.imagePath,imageSha256=HashFile(previous.imagePath),recordSha256=Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(previous)))});}if(report.unchangedPreviews.Count!=83)throw new InvalidDataException("Exactly83other previews must remain exact.");
            File.Copy(planPath,Path.Combine(run,"plan.json"),false);File.Copy(target.path,Path.Combine(run,"material.before.mat"),false);File.Copy(plan.targetMetadata.path,Path.Combine(run,"material.before.mat.meta"),false);File.Copy(previewsPath,Path.Combine(run,"previews.before.json"),false);File.Copy(representative.imagePath,Path.Combine(run,"representative.before.png"),false);
            Exact(Path.Combine(run,"material.before.mat"),target.bytes,target.sha256);Exact(Path.Combine(run,"material.before.mat.meta"),plan.targetMetadata.bytes,plan.targetMetadata.sha256);if(HashFile(Path.Combine(run,"previews.before.json"))!=report.originalPreviewsSha256||HashFile(Path.Combine(run,"representative.before.png"))!=report.representativeImageBeforeSha256)throw new IOException("P067 backup verification failed.");
            if(report.observedUnityErrors!=0)throw new InvalidDataException("Native errors before the bounded P067 save.");report.status="saving-owned-P067-emission";report.writeStarted=true;persist();Exact(target.path,target.bytes,target.sha256);EditorUtility.CopySerialized(prepared,material);EditorUtility.SetDirty(material);AssetDatabase.SaveAssetIfDirty(material);report.applied=true;AssetDatabase.ImportAsset(target.assetPath,ImportAssetOptions.ForceUpdate|ImportAssetOptions.ForceSynchronousImport);material=AssetDatabase.LoadAssetAtPath<Material>(target.assetPath);
            report.storedLinearEmissionFactor=material.GetVector("_EmissionColor");report.giFlagsAfter=(int)material.globalIlluminationFlags;report.otherShaderPropertiesAfterSha256=OtherEmissionProperties(material);report.materialAfterSha256=HashFile(target.path);
            if(!NearVector(report.storedLinearEmissionFactor,linear)||!material.IsKeywordEnabled("_EMISSION")||report.giFlagsAfter!=(report.giFlagsBefore&~(int)MaterialGlobalIlluminationFlags.EmissiveIsBlack)||report.otherShaderPropertiesAfterSha256!=report.otherShaderPropertiesBeforeSha256||!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material,out materialGuid,out materialId)||materialGuid!=EmissionGuid||materialId!=report.localIdBefore)throw new InvalidDataException("Saved P067 linear emission/keyword/other shader values or identity differs.");report.localIdAfter=materialId;Exact(plan.targetMetadata.path,plan.targetMetadata.bytes,plan.targetMetadata.sha256);
            report.previewPrefab=plan.prefabs.Single(p=>p.sourceModel.EndsWith("/EA_Pumpkin_01a.fbx",StringComparison.Ordinal)).prefab.assetPath;report.previewPath=Path.Combine(run,"P067-Pumpkin01a-source-emission.png");report.additionalPreview=RenderChanged(report.previewPrefab,report.previewPath,"067",representative.title,"source-proven-gltf-emission-correction");
            if(report.representativeDependsOnChangedMaterial){if(HashFile(previewsPath)!=report.originalPreviewsSha256||HashFile(representative.imagePath)!=report.representativeImageBeforeSha256)throw new InvalidDataException("P067 representative changed before targeted refresh.");report.status="refreshing-owned-P067-preview";report.representativeWriteStarted=true;persist();report.representativeAfter=RenderChanged(representative.assetPath,representative.imagePath,"067",representative.title,representative.kind);Atomic(previewsPath,Encoding.UTF8.GetBytes(ReplaceOnePreviewRecord(File.ReadAllText(previewsPath),report.representativeAfter)));report.representativeRefreshed=true;}else report.representativeAfter=representative;
            report.previewsAfterSha256=HashFile(previewsPath);report.representativeImageAfterSha256=HashFile(representative.imagePath);if(!report.representativeRefreshed&&(report.previewsAfterSha256!=report.originalPreviewsSha256||report.representativeImageAfterSha256!=report.representativeImageBeforeSha256))throw new InvalidDataException("Unaffected P067 representative changed.");
            var afterPreviews=JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));foreach(RetainedPreview retained in report.unchangedPreviews){var current=afterPreviews.products.Single(p=>p.id==retained.id);if(Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(current)))!=retained.recordSha256||HashFile(retained.imagePath)!=retained.imageSha256)throw new InvalidDataException("One of83other P067-phase preview records/PNGs changed.");}
            foreach(Record retained in report.retainedSources)Exact(retained.path,retained.bytes,retained.sha256);if(HashFile(manifestPath)!=report.manifestSha256||report.observedUnityErrors!=0)throw new InvalidDataException("P067 correction changed canonical inputs or recorded native errors.");report.status="complete";
        }catch(Exception error){report.status="failed";report.errors.Add(error.ToString());throw;}
        finally{if(prepared)UnityEngine.Object.DestroyImmediate(prepared);bool cleanupFailure=report.observedUnityErrors!=0&&report.status=="complete";if(cleanupFailure){report.status="failed";report.errors.Add("Native error during final temporary-material cleanup.");}Application.logMessageReceived-=capture;report.completedUtc=Utc();persist();Atomic(Path.Combine(local,"emission-correction-report.json"),new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(report,true)+"\n"));if(cleanupFailure)throw new InvalidDataException("P067 cleanup recorded native errors; durable failed report requires exit1.");}
    }
    public static void RunP067EmissionHeadless(){Guard();int code=0;try{RunEmission();}catch(Exception error){UnityEngine.Debug.LogError(error);code=1;}EditorApplication.Exit(code);}
}
