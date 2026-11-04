#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Yamyam.SkinNormal;

public static class SkinNormalSceneBuilder {
    const string Knight="Assets/ThirdParty/KayKitAdventurers/Knight.fbx";
    static void IsolatedOnly(){string p=Path.GetFullPath(Application.dataPath).Replace('\\','/');if(!p.Contains("/game-math-skinning-normal-map/production/unity-staging/LocalUnity"))throw new InvalidOperationException("M22 validation is allowed only in its isolated LocalUnity project; shared Assets are protected.");}
    // Root explicitly invokes this after project provisioning. It never starts Unity or renders.
    public static void ValidateRigOnly(){
        IsolatedOnly();var importer=AssetImporter.GetAtPath(Knight) as ModelImporter;if(importer==null)throw new InvalidOperationException("Copy licensed source and original provenance first.");if(!importer.isReadable){importer.isReadable=true;importer.SaveAndReimport();}
        GameObject instance=UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(Knight));KnightRigAdapter rig=null;
        try{
            foreach(var t in instance.GetComponentsInChildren<Transform>(true))if(t.name.Contains("Sword")||t.name.Contains("Shield"))t.gameObject.SetActive(false);
            var clips=AssetDatabase.LoadAllAssetsAtPath(Knight).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToArray();rig=new KnightRigAdapter(instance,clips);rig.SelectActualArmProbe();
            var results=new System.Collections.Generic.List<RigProbe>();
            foreach(string clipName in new[]{"T-Pose","Interact","Cheer"}){float len=rig.ClipLength(clipName);foreach(float u in new[]{0f,.25f,.5f,.75f,1f}){rig.Sample(clipName,len*u);var probe=rig.Probe(true);if(float.IsNaN(probe.cpuVsBakeWorldError)||probe.cpuVsBakeWorldError>.0005f)throw new InvalidOperationException("CPU LBS vs BakeMesh mismatch: "+clipName+" @ "+u+" = "+probe.cpuVsBakeWorldError);results.Add(probe);}}
            string output=Path.Combine(Path.GetDirectoryName(Application.dataPath),"rig-runtime-validation.json");File.WriteAllText(output,JsonUtility.ToJson(new RigValidation{unityVersion=Application.unityVersion,clips=clips.Select(c=>c.name).ToArray(),probes=results.ToArray()},true));Debug.Log("M22 CPU rig validation written: "+output);
        }finally{if(rig!=null)rig.Dispose();UnityEngine.Object.DestroyImmediate(instance);}
    }
    [Serializable] class RigValidation {public string unityVersion;public string status="cpu-rig-validated-not-rendered";public string[] clips;public RigProbe[] probes;}
    public static SkinNormalTeachingStage BuildStage(SkinNormalShot shot){
        IsolatedOnly();var go=new GameObject("M22_"+shot.beatId);var stage=go.AddComponent<SkinNormalTeachingStage>();stage.shot=shot;stage.knightPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(Knight);stage.knightClips=AssetDatabase.LoadAllAssetsAtPath(Knight).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToArray();stage.knightColorTexture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/ThirdParty/KayKitAdventurers/knight_texture.png");stage.koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",44);stage.Build();return stage;
    }
}
#endif
