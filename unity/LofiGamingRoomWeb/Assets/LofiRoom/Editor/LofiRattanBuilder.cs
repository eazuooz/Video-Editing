using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Unity.Pipeline.Commands;
using Yamyam.LofiRoom;
public static class LofiRattanBuilder
{
    const string Folder="Assets/LofiRoom/GeneratedRattanV11",Scene="Assets/LofiRoom/Scenes/LofiRattanRoomV11.unity";
    static string Delivery=>Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/living-room-v11");
    static Bounds BoundsOf(GameObject go){var rr=go.GetComponentsInChildren<Renderer>();var b=rr[0].bounds;foreach(var r in rr)b.Encapsulate(r.bounds);return b;}
    static GameObject Furniture(string key,Vector3 dimensions,bool sofa)
    {
        string source="Assets/LofiRoom/TripoRattanV11/"+key+"/";var file=source+"Model.fbx";
        var importer=AssetImporter.GetAtPath(file) as ModelImporter;if(!importer)throw new Exception("Download/import the completed Tripo "+key+" first: "+file);
        importer.materialImportMode=ModelImporterMaterialImportMode.None;importer.importAnimation=false;importer.isReadable=true;importer.SaveAndReimport();
        foreach(var name in new[]{"BaseColor","Normal"})
        {
            var t=AssetImporter.GetAtPath(source+name+".png") as TextureImporter;if(!t)throw new Exception("Missing actual Tripo texture: "+name);
            t.sRGBTexture=name=="BaseColor";t.textureType=name=="Normal"?TextureImporterType.NormalMap:TextureImporterType.Default;t.maxTextureSize=4096;t.mipmapEnabled=true;t.textureCompression=TextureImporterCompression.CompressedHQ;t.SaveAndReimport();
        }
        string materialPath=Folder+"/"+key+".mat";var material=AssetDatabase.LoadAssetAtPath<Material>(materialPath);
        if(!material){material=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(material,materialPath);}
        material.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(source+"BaseColor.png"));material.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(source+"Normal.png"));material.SetColor("_BaseColor",Color.white);material.SetFloat("_Metallic",0);material.SetFloat("_Smoothness",.22f);material.SetFloat("_BumpScale",.5f);material.EnableKeyword("_NORMALMAP");
        var root=new GameObject("Tripo rattan "+key);var model=UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(file),root.transform);var bounds=BoundsOf(model);
        if(sofa)
        {
            // The upper back, unlike the seat, identifies the asset's back side.
            var top=model.GetComponentsInChildren<MeshFilter>().SelectMany(f=>f.sharedMesh.vertices.Select(v=>f.transform.TransformPoint(v))).Where(p=>p.y>bounds.min.y+bounds.size.y*.72f).ToArray();
            if(top.Length>0&&top.Average(v=>v.z)>bounds.center.z)model.transform.localRotation=Quaternion.Euler(0,180,0);
        }
        bounds=BoundsOf(model);model.transform.localScale=Vector3.Scale(model.transform.localScale,new Vector3(dimensions.x/bounds.size.x,dimensions.y/bounds.size.y,dimensions.z/bounds.size.z));bounds=BoundsOf(model);model.transform.localPosition-=new Vector3(bounds.center.x,bounds.min.y,bounds.center.z);
        foreach(var r in model.GetComponentsInChildren<Renderer>())r.sharedMaterials=r.sharedMaterials.Select(_=>material).ToArray();
        string prefab=Folder+"/"+key+".prefab";PrefabUtility.SaveAsPrefabAsset(root,prefab);UnityEngine.Object.DestroyImmediate(root);return AssetDatabase.LoadAssetAtPath<GameObject>(prefab);
    }
    [CliCommand("lofi_rattan_prepare","Use actual generated wood/rattan sofa and foot-resting coffee table",MainThreadRequired=true)]
    public static string Prepare()
    {
        if(EditorApplication.isPlaying)throw new Exception("Edit mode required");Directory.CreateDirectory(Delivery);Directory.CreateDirectory(Folder);AssetDatabase.Refresh();
        EditorSceneManager.OpenScene("Assets/LofiRoom/Scenes/LofiSofaRoomV10.unity");var room=UnityEngine.Object.FindAnyObjectByType<LofiRoomSample>();var living=room.GetComponent<LofiLivingRoom>();
        living.readingSofaPrefab=Furniture("sofa",new Vector3(1.85f,.92f,.76f),true);living.readingTablePrefab=Furniture("table",new Vector3(1.25f,.44f,.68f),false);
        EditorSceneManager.SaveScene(room.gameObject.scene,Scene);AssetDatabase.SaveAssets();
        var result=Newtonsoft.Json.JsonConvert.SerializeObject(new{scene=Scene,sofa=new{width=1.85,height=.92,depth=.76},table=new{width=1.25,height=.44,depth=.68},cat="Existing real Tripo mesh with localized breathing and tail motion",models=new[]{living.readingSofaPrefab,living.readingTablePrefab}.Select(x=>new{name=x.name,triangles=x.GetComponentsInChildren<MeshFilter>().Sum(f=>f.sharedMesh.triangles.Length/3)})},Newtonsoft.Json.Formatting.Indented);File.WriteAllText(Delivery+"/prepared.json",result);return result;
    }
    [CliCommand("lofi_rattan_web_build","Build the selected rattan room scene only",MainThreadRequired=true)]
    public static string Build()
    {
        if(EditorApplication.isPlaying)throw new Exception("Edit mode required");Directory.CreateDirectory(Delivery);string destination=Delivery+"/webgl";
        EditorApplication.delayCall+=()=>{PlayerSettings.WebGL.compressionFormat=WebGLCompressionFormat.Gzip;PlayerSettings.WebGL.decompressionFallback=true;PlayerSettings.WebGL.nameFilesAsHashes=false;var b=BuildPipeline.BuildPlayer(new[]{Scene},destination,BuildTarget.WebGL,BuildOptions.None);File.WriteAllText(Delivery+"/web-build.json",Newtonsoft.Json.JsonConvert.SerializeObject(new{result=b.summary.result.ToString(),errors=b.summary.totalErrors,bytes=b.summary.totalSize},Newtonsoft.Json.Formatting.Indented));};return destination;
    }
}
