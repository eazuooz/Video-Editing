using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using Unity.Pipeline.Commands;
using Yamyam.LofiRoom;
public static class LofiSofaCatBuilder
{
    const string Folder="Assets/LofiRoom/GeneratedSofaV10";
    public const string Scene="Assets/LofiRoom/Scenes/LofiSofaRoomV10.unity";
    static string Delivery=>Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/living-room-v10");
    [CliCommand("lofi_sofa_prepare","Prepare a separate sofa-reading scene and inspect licensed native clips",MainThreadRequired=true)]
    public static string Prepare()
    {
        if(EditorApplication.isPlaying)throw new Exception("Edit mode required");
        Directory.CreateDirectory(Folder);Directory.CreateDirectory(Delivery);AssetDatabase.Refresh();
        EditorSceneManager.OpenScene("Assets/LofiRoom/Scenes/LofiLivingRoomV9.unity");
        var r=UnityEngine.Object.FindAnyObjectByType<LofiRoomSample>();
        string controller=Folder+"/SofaController.controller";
        if(!AssetDatabase.LoadAssetAtPath<AnimatorController>(controller))AssetDatabase.CopyAsset(AssetDatabase.GetAssetPath(r.actor.runtimeAnimatorController),controller);
        var ac=AssetDatabase.LoadAssetAtPath<AnimatorController>(controller);r.actor.runtimeAnimatorController=ac;
        var layer=ac.layers[0];layer.iKPass=true;ac.layers=new[]{layer};
        foreach(var item in new[]{("SofaDown","Sit_Chair_Down"),("SofaUp","Sit_Chair_StandUp"),("SofaIdle","Sit_Chair_Idle")})
        {
            var state=layer.stateMachine.states.Select(x=>x.state).FirstOrDefault(x=>x.name==item.Item1)??layer.stateMachine.AddState(item.Item1);
            state.motion=LofiHearthMotion.Clip(item.Item2);state.speed=item.Item1=="SofaDown"?.36f:item.Item1=="SofaUp"?.65f:1;state.iKOnFeet=false;
        }
        foreach(var item in new[]{("SofaRead","Tourist_sit_02_Map"),("SofaReadAlt","Tourist_sit_01_Map"),("SofaRest","Tourist_sit_03")})
        {
            var clip=AssetDatabase.LoadAssetAtPath<AnimationClip>("Assets/LofiRoom/NativeMotion/"+item.Item2+".anim");
            if(!clip||!clip.isHumanMotion)throw new Exception("Missing native Humanoid source: "+item.Item2);
            var state=layer.stateMachine.states.Select(x=>x.state).FirstOrDefault(x=>x.name==item.Item1)??layer.stateMachine.AddState(item.Item1);
            state.motion=item.Item1=="SofaRead"?AssetDatabase.LoadAssetAtPath<AnimationClip>("Assets/LofiRoom/NativeMotion/Tourist_sit_03.anim"):clip;state.speed=.8f;state.iKOnFeet=false;
        }
        string maskPath=Folder+"/ReadingArms.mask";var mask=AssetDatabase.LoadAssetAtPath<AvatarMask>(maskPath);
        if(!mask){mask=new AvatarMask();AssetDatabase.CreateAsset(mask,maskPath);}
        for(int i=0;i<(int)AvatarMaskBodyPart.LastBodyPart;i++)mask.SetHumanoidBodyPartActive((AvatarMaskBodyPart)i,i==(int)AvatarMaskBodyPart.LeftArm||i==(int)AvatarMaskBodyPart.RightArm||i==(int)AvatarMaskBodyPart.LeftFingers||i==(int)AvatarMaskBodyPart.RightFingers);
        var layers=ac.layers.ToList();var arms=layers.FirstOrDefault(x=>x.name=="Sofa reading arms");
        if(arms==null){var sm=new AnimatorStateMachine{name="Sofa reading arms"};AssetDatabase.AddObjectToAsset(sm,ac);arms=new AnimatorControllerLayer{name="Sofa reading arms",stateMachine=sm,defaultWeight=0,avatarMask=mask};layers.Add(arms);}
        var armState=arms.stateMachine.states.Select(x=>x.state).FirstOrDefault(x=>x.name=="Native reading arms")??arms.stateMachine.AddState("Native reading arms");armState.motion=AssetDatabase.LoadAssetAtPath<AnimationClip>("Assets/LofiRoom/NativeMotion/Tourist_sit_02_Map.anim");armState.speed=.8f;arms.stateMachine.defaultState=armState;arms.avatarMask=mask;arms.iKPass=false;ac.layers=layers.ToArray();
        string src="Assets/LofiRoom/ThirdParty/VintageSofaV10/";
        foreach(string name in new[]{"BaseColor","Normal","MetallicSmoothness"})
        {
            var ti=(TextureImporter)AssetImporter.GetAtPath(src+name+".png");ti.sRGBTexture=name=="BaseColor";ti.textureType=name=="Normal"?TextureImporterType.NormalMap:TextureImporterType.Default;ti.maxTextureSize=4096;ti.mipmapEnabled=true;ti.textureCompression=TextureImporterCompression.CompressedHQ;ti.SaveAndReimport();
        }
        string matPath=Folder+"/VintageLeather.mat";var mat=AssetDatabase.LoadAssetAtPath<Material>(matPath);
        if(!mat){mat=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(mat,matPath);}
        mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(src+"BaseColor.png"));mat.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(src+"Normal.png"));mat.SetTexture("_MetallicGlossMap",AssetDatabase.LoadAssetAtPath<Texture2D>(src+"MetallicSmoothness.png"));mat.SetColor("_BaseColor",Color.white);mat.SetFloat("_BumpScale",.6f);mat.SetFloat("_Smoothness",.35f);mat.EnableKeyword("_NORMALMAP");mat.EnableKeyword("_METALLICSPECGLOSSMAP");
        var root=new GameObject("Vintage sofa - RG Poly CC0");var model=UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(src+"Sofa.fbx"),root.transform);model.transform.localPosition=Vector3.zero;
        var renderers=model.GetComponentsInChildren<Renderer>();var b=renderers[0].bounds;foreach(var mr in renderers){b.Encapsulate(mr.bounds);mr.sharedMaterials=mr.sharedMaterials.Select(_=>mat).ToArray();}
        var originalSize=b.size;model.transform.localScale*=2.35f/b.size.x;
        b=renderers[0].bounds;foreach(var mr in renderers)b.Encapsulate(mr.bounds);model.transform.localPosition-=new Vector3(b.center.x,b.min.y,b.center.z);
        PrefabUtility.SaveAsPrefabAsset(root,Folder+"/ReadingSofa.prefab");UnityEngine.Object.DestroyImmediate(root);
        var living=r.GetComponent<LofiLivingRoom>();living.readingSofaPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(Folder+"/ReadingSofa.prefab");
        string catSource="Assets/LofiRoom/TripoSleepingCatV10/";
        var ci=(ModelImporter)AssetImporter.GetAtPath(catSource+"Cat.fbx");ci.materialImportMode=ModelImporterMaterialImportMode.None;ci.isReadable=true;ci.importAnimation=false;ci.SaveAndReimport();
        foreach(var name in new[]{"BaseColor","Normal","Roughness","Metallic"}){var ti=(TextureImporter)AssetImporter.GetAtPath(catSource+name+".png");ti.sRGBTexture=name=="BaseColor";ti.textureType=name=="Normal"?TextureImporterType.NormalMap:TextureImporterType.Default;ti.maxTextureSize=4096;ti.mipmapEnabled=true;ti.textureCompression=TextureImporterCompression.CompressedHQ;ti.SaveAndReimport();}
        string catMatPath=Folder+"/TripoCalico.mat";var catMat=AssetDatabase.LoadAssetAtPath<Material>(catMatPath);if(!catMat){catMat=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(catMat,catMatPath);}catMat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(catSource+"BaseColor.png"));catMat.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(catSource+"Normal.png"));catMat.SetColor("_BaseColor",Color.white);catMat.SetFloat("_Metallic",0);catMat.SetFloat("_Smoothness",.08f);catMat.SetFloat("_BumpScale",.55f);catMat.EnableKeyword("_NORMALMAP");
        var catRoot=new GameObject("Tripo generated sleeping calico");var cat=UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(catSource+"Cat.fbx"),catRoot.transform);cat.transform.localRotation=Quaternion.Euler(0,180,0);var cr=cat.GetComponentsInChildren<Renderer>();var cb=cr[0].bounds;foreach(var mr in cr){cb.Encapsulate(mr.bounds);mr.sharedMaterials=mr.sharedMaterials.Select(_=>catMat).ToArray();}var catOriginalSize=cb.size;cat.transform.localScale*=.78f/Mathf.Max(cb.size.x,cb.size.z);cb=cr[0].bounds;foreach(var mr in cr)cb.Encapsulate(mr.bounds);cat.transform.localPosition-=new Vector3(cb.center.x,cb.min.y,cb.center.z);
        var catTriangles=cat.GetComponentsInChildren<MeshFilter>().Sum(x=>x.sharedMesh.triangles.Length/3);PrefabUtility.SaveAsPrefabAsset(catRoot,Folder+"/TripoCalico.prefab");UnityEngine.Object.DestroyImmediate(catRoot);living.sleepingCatPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(Folder+"/TripoCalico.prefab");
        EditorUtility.SetDirty(ac);EditorUtility.SetDirty(mat);EditorSceneManager.SaveScene(r.gameObject.scene,Scene);AssetDatabase.SaveAssets();
        string result=Newtonsoft.Json.JsonConvert.SerializeObject(new{scene=Scene,sofaOriginalSize=originalSize.ToString("F3"),sofaWidth=2.35f,catOriginalSize=catOriginalSize.ToString("F3"),catTriangles,states=layer.stateMachine.states.Select(x=>new{x.state.name,clip=x.state.motion?x.state.motion.name:null}).ToArray()},Newtonsoft.Json.Formatting.Indented);File.WriteAllText(Delivery+"/prepared.json",result);return result;
    }
    [CliCommand("lofi_sofa_web_build","Build only the selected sofa and Tripo cat scene",MainThreadRequired=true)]
    public static string Build()
    {
        if(EditorApplication.isPlaying)throw new Exception("Edit mode required");Directory.CreateDirectory(Delivery);var dst=Delivery+"/webgl";
        EditorApplication.delayCall+=()=>{PlayerSettings.WebGL.compressionFormat=WebGLCompressionFormat.Gzip;PlayerSettings.WebGL.decompressionFallback=true;PlayerSettings.WebGL.nameFilesAsHashes=false;var b=BuildPipeline.BuildPlayer(new[]{Scene},dst,BuildTarget.WebGL,BuildOptions.None);File.WriteAllText(Delivery+"/web-build.json",Newtonsoft.Json.JsonConvert.SerializeObject(new{result=b.summary.result.ToString(),errors=b.summary.totalErrors,bytes=b.summary.totalSize},Newtonsoft.Json.Formatting.Indented));};return dst;
    }
}
