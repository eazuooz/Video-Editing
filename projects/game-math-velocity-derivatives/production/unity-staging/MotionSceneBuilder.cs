#if UNITY_EDITOR
using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using Yamyam.MathMotion;

public static class MotionSceneBuilder {
    const string Robot="Assets/ThirdParty/YamyamAssetLibrary/002-analog-memory-80s-90s-crt-vhs-rooms-godot-unity-blend/EmaceArt/it`s 80`s/Prefabs/Child Room/Toys/EAThe80_Robot_Toy_01a_PRE.prefab";
    public static MotionLessonStage BuildStage(MotionLessonShot shot){
        string path=Path.GetFullPath(Application.dataPath).Replace('\\','/');
        if(!path.Contains("/game-math-velocity-derivatives/production/unity-staging/LocalUnity-"))throw new InvalidOperationException("Use the separately provisioned M24 capture project.");
        var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(Robot);if(!prefab)throw new InvalidOperationException("Exact licensed robot asset is required.");
        var stage=new GameObject("M24_"+shot.beatId).AddComponent<MotionLessonStage>();stage.shot=shot;stage.subjectPrefab=prefab;stage.koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",42);stage.Build();
        foreach(var renderer in stage.movement.subjectAnchor.GetComponentsInChildren<Renderer>()){
            var mats=renderer.sharedMaterials;
            for(int i=0;i<mats.Length;i++){
                if(!mats[i])throw new InvalidOperationException("Imported subject material missing.");
                if(mats[i].shader.name.StartsWith("Universal Render Pipeline/"))continue;
                var source=mats[i];var converted=new Material(Shader.Find("Universal Render Pipeline/Lit")){name=source.name+"_MotionInstance"};
                converted.SetColor("_BaseColor",source.HasProperty("_BaseColor")?source.GetColor("_BaseColor"):source.HasProperty("_Color")?source.GetColor("_Color"):Color.white);
                var texture=source.HasProperty("_BaseMap")?source.GetTexture("_BaseMap"):source.HasProperty("_MainTex")?source.GetTexture("_MainTex"):null;if(texture)converted.SetTexture("_BaseMap",texture);
                converted.SetFloat("_Smoothness",.35f);mats[i]=converted;stage.RememberMaterial(converted);
            }
            renderer.sharedMaterials=mats;
        }
        return stage;
    }
}
#endif
