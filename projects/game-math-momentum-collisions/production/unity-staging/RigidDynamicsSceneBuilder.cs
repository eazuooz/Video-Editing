#if UNITY_EDITOR
using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using Yamyam.RigidTeaching;
public static class RigidDynamicsSceneBuilder {
 public static RigidDynamicsLessonStage BuildStage(DynamicsLessonShot shot){
  string path=Path.GetFullPath(Application.dataPath).Replace('\\','/');if(!path.Contains("/game-math-momentum-collisions/production/unity-staging/LocalUnity-")&&!path.Contains("/game-math-rigid-body-inertia/production/unity-staging/LocalUnity-"))throw new InvalidOperationException("Isolated M29/M30 project required");
  const string prefab="Assets/ThirdParty/YamyamAssetLibrary/002-analog-memory-80s-90s-crt-vhs-rooms-godot-unity-blend/EmaceArt/it`s 80`s/Prefabs/Youth bedroom/Props/EAThe80_Prop_Cardbox_01a_PRE.prefab";
  var asset=AssetDatabase.LoadAssetAtPath<GameObject>(prefab);if(!asset)throw new FileNotFoundException("Licensed crate missing",prefab);
  var stage=new GameObject("SourceDynamics_"+shot.beatId).AddComponent<RigidDynamicsLessonStage>();stage.shot=shot;stage.cratePrefab=asset;stage.koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",42);stage.Build();return stage;
 }
}
#endif
