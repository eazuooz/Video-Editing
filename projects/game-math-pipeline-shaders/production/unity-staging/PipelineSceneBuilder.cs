#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Yamyam.PipelineTeaching;

public static class PipelineSceneBuilder {
 const string Knight="Assets/ThirdParty/KayKitAdventurers/Knight.fbx";
 static void IsolatedOnly(){string p=Path.GetFullPath(Application.dataPath).Replace('\\','/');if(!p.Contains("/game-math-pipeline-shaders/production/unity-staging/LocalUnity"))throw new InvalidOperationException("Use only the independently provisioned M23 project; shared Assets are protected.");}
 // Root calls this from its serial runner. No capture, Unity startup or invented timeline occurs here.
 public static PipelineTeachingStage BuildStage(PipelineShot shot){
  IsolatedOnly();var go=new GameObject("M23_"+shot.beatId);var stage=go.AddComponent<PipelineTeachingStage>();stage.shot=shot;stage.knightPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(Knight);stage.knightClips=AssetDatabase.LoadAllAssetsAtPath(Knight).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToArray();stage.knightTexture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/ThirdParty/KayKitAdventurers/knight_texture.png");stage.koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",44);stage.Build();return stage;
 }
}
#endif
