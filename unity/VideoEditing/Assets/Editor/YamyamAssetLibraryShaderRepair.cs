// Explicit adaptation of34 missing HDRP shaders and one unused vertex-color material.
// Only the exact reviewed material files are saved. No source mesh, scene or setting is changed.
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

public static class YamyamAssetLibraryShaderRepair
{
    const string ExpectedProject="D:/Github/VideoEditing/unity/VideoEditing/Library/YamyamAssetLibrary/headless-project";
    const string Root="Assets/ThirdParty/YamyamAssetLibrary/";
    const string PlanSha="0fb20688a43b56151a7ca248aa5d634d5602dc5eac178cb7ae32078897c52655";
    const string HdrpGuid="6e4ae4064600d784cac1e41a9e6f2e59";
    [Serializable] public sealed class Record { public string path,assetPath,sha256,guid;public long bytes; }
    [Serializable] public sealed class Target
    {
        public string kind,name,sourceShaderGuid,baseTextureGuid,baseTextureFileId;public Record body,metadata,baseTexture,baseTextureMetadata,vertexShader,vertexShaderMetadata;
        public int renderQueue,sourceLightmapFlags,sourceModelsWithColorLayers;public bool instancing,doubleSidedGI;
        public Vector4 baseColor,emission;public Vector2 baseScale,baseOffset;public float metallic,smoothness,normalScale,surface,alphaClip,cutoff,cull,preserveSpecular;
        public string[] ownedIncomingReferences;public Record[] vertexColorSourceModels,retainedVertexSourceModels;
    }
    [Serializable] public sealed class Plan { public int schemaVersion;public string kind,sourceManifestSha256,stageRoot;public bool actualAssetsModified,sourceArchivesModified;public Target[] targets; }
    [Serializable] public sealed class Result
    {
        public string path,guid,kind,sourceShaderGuid,beforeSha256,afterSha256,metadataSha256,shader,otherSavedBeforeSha256,otherSavedAfterSha256;
        public long localId;public bool writeStarted,complete;public int preservedSavedProperties;
        public Vector4 baseColor,linearEmission;public float surface,alphaClip,cull;public int renderQueue;
    }
    [Serializable] public sealed class PreviewProof { public string id,imagePath,imageSha256,recordSha256;public bool affected,refreshed;public string[] dependencies; }
    [Serializable] public sealed class Report
    {
        public int schemaVersion=1,materialsCompleted,hdrpMaterials,vertexAdaptations,vertexColorModelsVerified,unaffectedPreviewRecordsVerified,unaffectedPreviewImagesVerified,observedUnityErrors;
        public string kind="bounded-missing-shader-adaptation",status="checking",project,runDirectory,startedUtc,completedUtc,planSha256=PlanSha,manifestSha256,previewsBeforeSha256,previewsAfterSha256;
        public bool sourceArchivesModified,originalSourcesModified,scenesOpened,projectSettingsModified,unrelatedAssetsSaved;
        public string[] limitations={"HDRP standard material parameters are adapted to URP lighting, not a pixel-identical HDRP reconstruction.","HDRP mirrored backface normals are represented by URP two-sided culling.","The omitted P084 custom shader is replaced only on its unused material by another supplied URP vertex-color shader; source mesh colors and bindings are preserved."};
        public List<Result> materials=new List<Result>();public List<PreviewProof> previews=new List<PreviewProof>();public List<string> errors=new List<string>();
    }
    sealed class Prepared { public Target target;public Material actual,temporary;public Texture baseTexture;public Dictionary<string,string> retained;public Result result; }
    static string Project { get{return YamyamAssetLibraryIO.NormalPath(Path.GetDirectoryName(Application.dataPath));} }
    static string Work { get{return YamyamAssetLibraryIO.NormalPath(Path.Combine(Project,".."));} }
    static string Absolute(string asset){return Path.Combine(Project,asset.Replace('/',Path.DirectorySeparatorChar));}
    static string Utc(){return DateTime.UtcNow.ToString("o");}
    static string Hash(byte[] bytes){using(var sha=SHA256.Create())return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();}
    static string HashFile(string path){using(var stream=File.OpenRead(path))using(var sha=SHA256.Create())return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-","").ToLowerInvariant();}
    static void Guard(){if(!Application.isBatchMode||Application.unityVersion!="6000.6.0f1"||!Project.Replace('\\','/').Equals(ExpectedProject,StringComparison.OrdinalIgnoreCase)||QualitySettings.activeColorSpace!=ColorSpace.Linear)throw new InvalidOperationException("Exact isolated Unity6000.6 Linear batch project required.");}
    static void NoLinks(string path)
    {
        string full=YamyamAssetLibraryIO.NormalPath(path);if(!full.StartsWith(Work+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))throw new IOException("Path escaped owned work.");
        for(string cursor=full;!string.IsNullOrEmpty(cursor);cursor=Path.GetDirectoryName(cursor)){try{if((File.GetAttributes(cursor)&FileAttributes.ReparsePoint)!=0)throw new IOException("Reparse ancestor refused.");}catch(FileNotFoundException){}catch(DirectoryNotFoundException){}if(cursor.Equals(Path.GetPathRoot(full),StringComparison.OrdinalIgnoreCase))return;}throw new IOException("Ancestor validation incomplete.");
    }
    static string GuidAt(string path){var match=Regex.Match(File.ReadAllText(path),@"(?m)^guid:[ \t]*([a-f0-9]{32})[ \t]*\r?$");if(!match.Success)throw new InvalidDataException("Metadata GUID unavailable.");return match.Groups[1].Value;}
    static void Exact(Record record)
    {
        if(record==null||string.IsNullOrEmpty(record.assetPath)||!record.assetPath.StartsWith(Root,StringComparison.Ordinal)||!YamyamAssetLibraryIO.NormalPath(record.path).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(record.assetPath)),StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Record escaped exact owned asset path.");
        NoLinks(record.path);if(new FileInfo(record.path).Length!=record.bytes||HashFile(record.path)!=record.sha256)throw new InvalidDataException("Reviewed file changed: "+record.assetPath);if(!string.IsNullOrEmpty(record.guid)&&GuidAt(record.path)!=record.guid)throw new InvalidDataException("Reviewed metadata GUID changed.");
    }
    static void Atomic(string path,string json)
    {
        NoLinks(path);Directory.CreateDirectory(Path.GetDirectoryName(path));string temporary=path+"."+Guid.NewGuid().ToString("N")+".tmp";File.WriteAllText(temporary,json+"\n",new UTF8Encoding(false));
        for(int attempt=0;;attempt++){try{if(File.Exists(path))File.Replace(temporary,path,null);else File.Move(temporary,path);return;}catch(IOException error){int code=error.HResult&0xffff;bool safe=code==1175&&File.Exists(path)&&File.Exists(temporary);if(attempt>=7||!(code==5||code==32||code==33||safe))throw;}catch(UnauthorizedAccessException){if(attempt>=7)throw;}System.Threading.Thread.Sleep(Math.Min(1000,25<<attempt));}
    }
    static string ObjectId(UnityEngine.Object value){if(!value)return "null";string guid;long id;return AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value,out guid,out id)?guid+":"+id:value.GetType().FullName+":"+value.name;}
    static readonly HashSet<string> ChangedNames=new HashSet<string>(new[]{"_BaseColor","_BaseMap","_Metallic","_Smoothness","_EmissionColor","_EmissionMap","_BumpMap","_BumpScale","_MetallicGlossMap","_OcclusionMap","_SmoothnessTextureChannel","_Surface","_Blend","_AlphaClip","_Cutoff","_Cull","_QueueOffset","_WorkflowMode","_BlendModePreserveSpecular","_ZWrite","_SrcBlend","_DstBlend","_SrcBlendAlpha","_DstBlendAlpha","_AlphaToMask","_AlphaToMaskInspectorValue"},StringComparer.Ordinal);
    static Dictionary<string,string> RetainedSaved(Material material)
    {
        var result=new Dictionary<string,string>(StringComparer.Ordinal);var serialized=new SerializedObject(material);serialized.Update();var saved=serialized.FindProperty("m_SavedProperties");
        foreach(string arrayName in new[]{"m_TexEnvs","m_Ints","m_Floats","m_Colors"}){var array=saved.FindPropertyRelative(arrayName);if(array==null)continue;for(int i=0;i<array.arraySize;i++){
            var element=array.GetArrayElementAtIndex(i);string name=element.FindPropertyRelative("first").stringValue;if(ChangedNames.Contains(name))continue;var value=element.FindPropertyRelative("second");string encoded;
            if(arrayName=="m_TexEnvs"){var scale=value.FindPropertyRelative("m_Scale").vector2Value;var offset=value.FindPropertyRelative("m_Offset").vector2Value;encoded=ObjectId(value.FindPropertyRelative("m_Texture").objectReferenceValue)+"|"+scale.ToString("R")+"|"+offset.ToString("R");}
            else if(arrayName=="m_Colors")encoded=value.colorValue.ToString("R");else if(arrayName=="m_Ints")encoded=value.longValue.ToString(CultureInfo.InvariantCulture);else encoded=value.floatValue.ToString("R",CultureInfo.InvariantCulture);
            result.Add(arrayName+"/"+name,encoded);
        }}return result;
    }
    static string RetainedHash(Dictionary<string,string> values){return Hash(Encoding.UTF8.GetBytes(string.Join("\n",values.OrderBy(x=>x.Key,StringComparer.Ordinal).Select(x=>x.Key+"="+x.Value))));}
    static void CheckRetained(Prepared item,Material material){var after=RetainedSaved(material);foreach(var value in item.retained){string current;if(!after.TryGetValue(value.Key,out current)||current!=value.Value)throw new InvalidDataException("Unrelated saved property changed: "+item.target.body.assetPath+" "+value.Key);}item.result.otherSavedAfterSha256=RetainedHash(item.retained.ToDictionary(x=>x.Key,x=>after[x.Key]));if(item.result.otherSavedAfterSha256!=item.result.otherSavedBeforeSha256)throw new InvalidDataException("Retained source property hash differs.");}
    static bool Near(float a,float b){return !float.IsNaN(a)&&!float.IsInfinity(a)&&Math.Abs(a-b)<=Math.Max(0.000001f,Math.Abs(b)*0.0000001f);}
    static bool Near(Vector4 a,Vector4 b){for(int i=0;i<4;i++)if(!Near(a[i],b[i]))return false;return true;}
    static void ValidateLit(Material material)
    {
        Type type=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("UnityEditor.Rendering.Universal.ShaderGUI.LitShader",false)).FirstOrDefault(t=>t!=null);var gui=type==null?null:Activator.CreateInstance(type,true) as ShaderGUI;if(gui==null)throw new InvalidOperationException("Installed official URP Lit validator unavailable.");gui.ValidateMaterial(material);
    }
    static void CheckNative(Prepared item,Material material,bool persistent)
    {
        Target target=item.target;string expected=target.kind=="hdrp-lit"?"Universal Render Pipeline/Lit":"Custom/URP/VertexColor";
        if(!material||!material.shader||material.shader.name!=expected||!material.shader.isSupported||ShaderUtil.ShaderHasError(material.shader)||material.name!=target.name||!Near(material.GetVector("_BaseColor"),target.baseColor)||!Near(material.GetFloat("_Metallic"),target.metallic)||!Near(material.GetFloat("_Smoothness"),target.smoothness)||material.enableInstancing!=target.instancing||material.doubleSidedGI!=target.doubleSidedGI)throw new InvalidDataException("Adapted native shader/material values unavailable or different.");
        int expectedQueue=target.renderQueue<0?material.shader.renderQueue:target.renderQueue;if(material.renderQueue!=expectedQueue)throw new InvalidDataException("Material render ordering changed.");
        if(target.kind=="hdrp-lit"){
            if(!Near(material.GetVector("_EmissionColor"),target.emission)||material.GetTexture("_BaseMap")!=item.baseTexture||material.GetTextureScale("_BaseMap")!=target.baseScale||material.GetTextureOffset("_BaseMap")!=target.baseOffset||!Near(material.GetFloat("_BumpScale"),target.normalScale)||!Near(material.GetFloat("_Surface"),target.surface)||!Near(material.GetFloat("_AlphaClip"),target.alphaClip)||!Near(material.GetFloat("_Cutoff"),target.cutoff)||!Near(material.GetFloat("_Cull"),target.cull)||material.IsKeywordEnabled("_EMISSION")!=(target.emission.x>0||target.emission.y>0||target.emission.z>0))throw new InvalidDataException("Active HDRP→URP color/map/linear HDR/transparency/cull transfer differs.");
        }
        CheckRetained(item,material);if(persistent){string guid;long id;if(!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(material,out guid,out id)||guid!=target.metadata.guid||id!=item.result.localId||AssetDatabase.AssetPathToGUID(target.body.assetPath)!=guid)throw new InvalidDataException("Persistent material GUID/localID changed.");Exact(target.metadata);}
    }
    static void VerifyVertexSources(Target target,Report report)
    {
        if(target.ownedIncomingReferences==null||target.ownedIncomingReferences.Length!=0||target.vertexColorSourceModels==null||target.vertexColorSourceModels.Length!=3||target.retainedVertexSourceModels==null||target.retainedVertexSourceModels.Length!=12||target.sourceModelsWithColorLayers!=8)throw new InvalidDataException("Unused vertex-material source proof scope changed.");
        foreach(var model in target.retainedVertexSourceModels)Exact(model);
        foreach(var source in target.vertexColorSourceModels){Exact(source);var model=AssetDatabase.LoadAssetAtPath<GameObject>(source.assetPath);if(!model)throw new InvalidDataException("Vertex-color source model unavailable.");bool colored=false;foreach(var renderer in model.GetComponentsInChildren<Renderer>(true)){Mesh mesh=null;var skin=renderer as SkinnedMeshRenderer;if(skin)mesh=skin.sharedMesh;else{var filter=renderer.GetComponent<MeshFilter>();if(filter)mesh=filter.sharedMesh;}if(!mesh)continue;Color32[] colors=mesh.colors32;if(colors.Length==mesh.vertexCount&&colors.Length>0&&colors.Any(c=>c.r!=colors[0].r||c.g!=colors[0].g||c.b!=colors[0].b))colored=true;}if(!colored)throw new InvalidDataException("Native source mesh does not retain the proved varying vertex colors.");report.vertexColorModelsVerified++;}
    }
    static YamyamAssetLibraryBridge.PreviewRecord Render(YamyamAssetLibraryBridge.PreviewRecord original)
    {
        var result=JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewRecord>(JsonUtility.ToJson(original));result.drawCalls=result.visiblePixels=result.magentaLikePixels=result.totalPixels=0;result.error=null;
        var bridge=typeof(YamyamAssetLibraryBridge);object[] args={AssetDatabase.LoadAssetAtPath<GameObject>(result.assetPath),new Bounds()};object draws=bridge.GetMethod("Draws",BindingFlags.NonPublic|BindingFlags.Static).Invoke(null,args);bridge.GetMethod("RenderPreview",BindingFlags.NonPublic|BindingFlags.Static).Invoke(null,new[]{draws,args[1],result});if(!string.IsNullOrEmpty(result.error)||!File.Exists(result.imagePath))throw new IOException("Affected representative render failed: "+result.error);return result;
    }
    static void Run()
    {
        Guard();if(EditorApplication.isCompiling||EditorApplication.isUpdating)throw new InvalidOperationException("Editor must be idle.");
        string local=Path.Combine(Project,"Library/YamyamAssetLibrary"),run=Path.Combine(local,"shader-repair",DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffffZ")+"-"+Guid.NewGuid().ToString("N"));NoLinks(run);Directory.CreateDirectory(run);
        var report=new Report{project=Project,runDirectory=run,startedUtc=Utc()};string reportPath=Path.Combine(run,"report.json");Action persist=()=>Atomic(reportPath,JsonUtility.ToJson(report,true));var prepared=new List<Prepared>();
        Application.LogCallback capture=(message,stack,type)=>{if(type==LogType.Error||type==LogType.Assert||type==LogType.Exception){report.observedUnityErrors++;report.errors.Add(message);}};Application.logMessageReceived+=capture;
        try{
            string planPath=Path.Combine(Work,"missing-shader-repair-plan.json");NoLinks(planPath);if(HashFile(planPath)!=PlanSha)throw new InvalidDataException("Reviewed shader adaptation plan changed.");var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(planPath));
            if(plan.schemaVersion!=1||plan.kind!="bounded-missing-hdrp-and-unused-vertex-shader-adaptation"||plan.actualAssetsModified||plan.sourceArchivesModified||plan.targets==null||plan.targets.Length!=35||plan.targets.Count(t=>t.kind=="hdrp-lit")!=34||plan.targets.Select(t=>t.body.assetPath).Distinct(StringComparer.Ordinal).Count()!=35||!YamyamAssetLibraryIO.NormalPath(plan.stageRoot).Equals(YamyamAssetLibraryIO.NormalPath(Absolute(Root.TrimEnd('/'))),StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Exact35-target isolated plan required.");
            string manifest=Path.Combine(Work,"staging-manifest.json");NoLinks(manifest);report.manifestSha256=HashFile(manifest);if(report.manifestSha256!=plan.sourceManifestSha256)throw new InvalidDataException("Plan canonical context changed.");File.Copy(planPath,Path.Combine(run,"plan.json"),false);
            foreach(var target in plan.targets){
                if(target.metadata.assetPath!=target.body.assetPath+".meta"||!target.body.assetPath.EndsWith(".mat",StringComparison.Ordinal)||target.metadata.guid==null)throw new InvalidDataException("Invalid exact material scope.");Exact(target.body);Exact(target.metadata);
                if(target.kind=="hdrp-lit"&&target.sourceShaderGuid!=HdrpGuid||target.kind!="hdrp-lit"&&target.kind!="unused-vertex-color-adaptation")throw new InvalidDataException("Unexpected source shader identity.");
                var actual=AssetDatabase.LoadAssetAtPath<Material>(target.body.assetPath);string guid;long id;if(!actual||actual.shader&&actual.shader.name!="Hidden/InternalErrorShader"||!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(actual,out guid,out id)||guid!=target.metadata.guid||id!=2100000)throw new InvalidDataException("Target is not the proved missing-shader material.");
                Shader shader;Texture texture=null;if(target.kind=="hdrp-lit"){shader=Shader.Find("Universal Render Pipeline/Lit");if(target.baseTextureFileId!="0"){Exact(target.baseTexture);Exact(target.baseTextureMetadata);texture=AssetDatabase.LoadAssetAtPath<Texture2D>(target.baseTexture.assetPath);string imageGuid;long imageId;if(!texture||AssetDatabase.GetMainAssetTypeAtPath(target.baseTexture.assetPath)!=typeof(Texture2D)||!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(texture,out imageGuid,out imageId)||imageGuid!=target.baseTextureGuid||imageId.ToString(CultureInfo.InvariantCulture)!=target.baseTextureFileId)throw new InvalidDataException("Active source HDRP texture identity/type unresolved.");}}else{Exact(target.vertexShader);Exact(target.vertexShaderMetadata);VerifyVertexSources(target,report);shader=AssetDatabase.LoadAssetAtPath<Shader>(target.vertexShader.assetPath);if(AssetDatabase.AssetPathToGUID(target.vertexShader.assetPath)!=target.vertexShaderMetadata.guid)throw new InvalidDataException("Supplied vertex shader identity changed.");}
                if(!shader||!shader.isSupported||ShaderUtil.ShaderHasError(shader))throw new InvalidDataException("Destination shader unavailable.");
                var item=new Prepared{target=target,actual=actual,temporary=new Material(actual),baseTexture=texture,retained=RetainedSaved(actual),result=new Result{path=target.body.assetPath,guid=guid,localId=id,kind=target.kind,sourceShaderGuid=target.sourceShaderGuid,beforeSha256=target.body.sha256,metadataSha256=target.metadata.sha256}};prepared.Add(item);report.materials.Add(item.result);item.result.otherSavedBeforeSha256=RetainedHash(item.retained);item.result.preservedSavedProperties=item.retained.Count;
                var material=item.temporary;material.name=target.name;material.shader=shader;material.SetVector("_BaseColor",target.baseColor);material.SetFloat("_Metallic",target.metallic);material.SetFloat("_Smoothness",target.smoothness);material.enableInstancing=target.instancing;material.doubleSidedGI=target.doubleSidedGI;
                if(target.kind=="hdrp-lit"){
                    material.SetTexture("_BaseMap",texture);material.SetTextureScale("_BaseMap",target.baseScale);material.SetTextureOffset("_BaseMap",target.baseOffset);material.SetVector("_EmissionColor",target.emission);foreach(string property in new[]{"_EmissionMap","_BumpMap","_MetallicGlossMap","_OcclusionMap"})material.SetTexture(property,null);
                    material.SetFloat("_BumpScale",target.normalScale);material.SetFloat("_SmoothnessTextureChannel",0);material.SetFloat("_WorkflowMode",1);material.SetFloat("_Surface",target.surface);material.SetFloat("_Blend",0);material.SetFloat("_AlphaClip",target.alphaClip);material.SetFloat("_Cutoff",target.cutoff);material.SetFloat("_Cull",target.cull);material.SetFloat("_BlendModePreserveSpecular",target.preserveSpecular);int baseQueue=target.surface>0?3000:target.alphaClip>0?2450:2000;material.SetFloat("_QueueOffset",target.renderQueue<0?0:target.renderQueue-baseQueue);if(target.emission.x>0||target.emission.y>0||target.emission.z>0)material.globalIlluminationFlags&=~MaterialGlobalIlluminationFlags.EmissiveIsBlack;ValidateLit(material);
                }
                material.renderQueue=target.renderQueue;CheckNative(item,material,false);
                string backup=Path.Combine(run,"backups",target.body.assetPath.Substring(Root.Length).Replace('/',Path.DirectorySeparatorChar));NoLinks(backup);Directory.CreateDirectory(Path.GetDirectoryName(backup));File.Copy(target.body.path,backup,false);File.Copy(target.metadata.path,backup+".meta",false);if(HashFile(backup)!=target.body.sha256||HashFile(backup+".meta")!=target.metadata.sha256)throw new IOException("Material backup verification failed.");
            }
            string previewsPath=Path.Combine(local,"previews.json");NoLinks(previewsPath);string previewsText=File.ReadAllText(previewsPath);var previews=JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(previewsText);if(previews.products==null||previews.products.Count!=84||previews.products.Select(p=>p.id).Distinct().Count()!=84||string.IsNullOrEmpty(previews.completedUtc))throw new InvalidDataException("Completed exact84 preview evidence required.");report.previewsBeforeSha256=HashFile(previewsPath);File.Copy(previewsPath,Path.Combine(run,"previews.before.json"),false);
            var changed=new HashSet<string>(plan.targets.Select(t=>t.body.assetPath),StringComparer.Ordinal);foreach(var preview in previews.products){NoLinks(preview.imagePath);var proof=new PreviewProof{id=preview.id,imagePath=preview.imagePath,imageSha256=HashFile(preview.imagePath),recordSha256=Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(preview)))};if(new[]{"002","012","030","070","084"}.Contains(preview.id)){proof.dependencies=AssetDatabase.GetDependencies(preview.assetPath,true);proof.affected=proof.dependencies.Any(p=>changed.Contains(p));if(proof.affected){if(!string.IsNullOrEmpty(preview.error))throw new InvalidDataException("Affected representative already unreadable.");File.Copy(preview.imagePath,Path.Combine(run,"P"+preview.id+".before.png"),false);if(HashFile(Path.Combine(run,"P"+preview.id+".before.png"))!=proof.imageSha256)throw new IOException("Affected preview backup differs.");}}report.previews.Add(proof);}
            if(HashFile(Path.Combine(run,"previews.before.json"))!=report.previewsBeforeSha256||report.observedUnityErrors!=0)throw new InvalidDataException("Preflight/backup produced native errors.");report.status="prepared-all35-backed-up";persist();
            foreach(var item in prepared){Exact(item.target.body);Exact(item.target.metadata);item.result.writeStarted=true;report.status="saving-owned-material";persist();EditorUtility.CopySerialized(item.temporary,item.actual);EditorUtility.SetDirty(item.actual);AssetDatabase.SaveAssetIfDirty(item.actual);AssetDatabase.ImportAsset(item.target.body.assetPath,ImportAssetOptions.ForceUpdate|ImportAssetOptions.ForceSynchronousImport);var current=AssetDatabase.LoadAssetAtPath<Material>(item.target.body.assetPath);CheckNative(item,current,true);item.result.shader=current.shader.name;item.result.baseColor=current.GetVector("_BaseColor");item.result.linearEmission=item.target.kind=="hdrp-lit"?current.GetVector("_EmissionColor"):Vector4.zero;item.result.surface=item.target.surface;item.result.alphaClip=item.target.alphaClip;item.result.cull=item.target.cull;item.result.renderQueue=current.renderQueue;item.result.afterSha256=HashFile(item.target.body.path);if(item.result.afterSha256==item.result.beforeSha256)throw new InvalidDataException("Material adaptation did not persist.");item.result.complete=true;report.materialsCompleted++;if(item.target.kind=="hdrp-lit")report.hdrpMaterials++;else report.vertexAdaptations++;if(report.observedUnityErrors!=0)throw new InvalidDataException("Native error during bounded material adaptation.");persist();}
            if(HashFile(previewsPath)!=report.previewsBeforeSha256)throw new IOException("Preview report changed concurrently.");foreach(var proof in report.previews.Where(p=>p.affected)){var row=previews.products.Single(p=>p.id==proof.id);if(HashFile(row.imagePath)!=proof.imageSha256)throw new IOException("Affected preview changed concurrently.");report.status="refreshing-dependent-representative";persist();var replacement=Render(row);previewsText=YamyamAssetLibraryMaterialSlots.ReplaceOnePreviewRecord(previewsText,replacement);Atomic(previewsPath,previewsText);proof.refreshed=true;}
            var after=JsonUtility.FromJson<YamyamAssetLibraryBridge.PreviewReport>(File.ReadAllText(previewsPath));if(after.products.Count!=84)throw new InvalidDataException("Preview scope changed.");foreach(var proof in report.previews.Where(p=>!p.affected)){var row=after.products.Single(p=>p.id==proof.id);if(HashFile(proof.imagePath)!=proof.imageSha256||Hash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(row)))!=proof.recordSha256)throw new IOException("Unrelated preview record/image changed.");report.unaffectedPreviewRecordsVerified++;report.unaffectedPreviewImagesVerified++;}report.previewsAfterSha256=HashFile(previewsPath);
            foreach(var item in prepared){Exact(item.target.metadata);if(item.target.baseTexture!=null){Exact(item.target.baseTexture);Exact(item.target.baseTextureMetadata);}if(item.target.vertexShader!=null){Exact(item.target.vertexShader);Exact(item.target.vertexShaderMetadata);foreach(var source in item.target.retainedVertexSourceModels)Exact(source);}}
            if(HashFile(manifest)!=report.manifestSha256||report.materialsCompleted!=35||report.observedUnityErrors!=0)throw new InvalidDataException("Canonical context/count/native errors changed.");report.status="complete";
        }catch(Exception error){report.status="failed";report.errors.Add(error.ToString());throw;}
        finally{foreach(var item in prepared)if(item.temporary)UnityEngine.Object.DestroyImmediate(item.temporary);bool cleanupFailure=report.observedUnityErrors!=0&&report.status=="complete";if(cleanupFailure){report.status="failed";report.errors.Add("Native error during temporary cleanup.");}Application.logMessageReceived-=capture;report.completedUtc=Utc();persist();Atomic(Path.Combine(local,"shader-repair-report.json"),JsonUtility.ToJson(report,true));if(cleanupFailure)throw new InvalidDataException("Native cleanup errors require failed exit.");}
    }
    public static void RunHeadless(){Guard();int exit=0;try{Run();}catch(Exception error){Debug.LogError(error);exit=1;}EditorApplication.Exit(exit);}
}
