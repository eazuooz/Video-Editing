#if UNITY_EDITOR
using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using Yamyam.MathMechanics;
public static class MechanicsSceneBuilder {
 public static MechanicsLessonStage BuildStage(MechanicsLessonShot shot){
  string root=Path.GetFullPath(Application.dataPath).Replace('\\','/');
  if(!root.Contains("/game-math-forces-friction/production/unity-staging/LocalUnity-")&&!root.Contains("/game-math-springs-damping/production/unity-staging/LocalUnity-"))throw new InvalidOperationException("Dedicated M27/M28 capture project required");
  var stage=new GameObject("Mechanics_"+shot.beatId).AddComponent<MechanicsLessonStage>();stage.shot=shot;
  stage.objectPrefab=Asset(shot.steps[0].model.subjectKind);stage.secondaryPrefab=Asset(shot.steps[0].model.secondaryKind);stage.koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",42);stage.Build();
  foreach(var r in stage.GetComponentsInChildren<Renderer>(true)){
   var mats=r.sharedMaterials;
   for(int i=0;i<mats.Length;i++){
    if(!mats[i])throw new InvalidOperationException("Missing selected material");if(mats[i].shader.name.StartsWith("Universal Render Pipeline/"))continue;
    var source=mats[i];var material=new Material(Shader.Find("Universal Render Pipeline/Lit")){name=source.name+"_MechanicsInstance"};
    material.SetColor("_BaseColor",source.HasProperty("_BaseColor")?source.GetColor("_BaseColor"):source.HasProperty("_Color")?source.GetColor("_Color"):Color.white);
    var texture=source.HasProperty("_BaseMap")?source.GetTexture("_BaseMap"):source.HasProperty("_MainTex")?source.GetTexture("_MainTex"):null;if(texture)material.SetTexture("_BaseMap",texture);mats[i]=material;stage.RememberMaterial(material);
   }r.sharedMaterials=mats;
  }return stage;
 }
 static GameObject Asset(string kind){
  string path;
  const string a="Assets/ThirdParty/YamyamAssetLibrary/002-analog-memory-80s-90s-crt-vhs-rooms-godot-unity-blend/EmaceArt/it`s 80`s/Prefabs/";
  switch(kind){
   case "robot":path=a+"Child Room/Toys/EAThe80_Robot_Toy_01a_PRE.prefab";break;
   case "box":path=a+"Youth bedroom/Props/EAThe80_Prop_Cardbox_01a_PRE.prefab";break;
   case "book":path=a+"Youth bedroom/Props/EAThe80_Prop_Book_01a_PRE.prefab";break;
   case "sandwich":path=a+"Kitchen/Foods/EAThe80_Prop_BreadJam_01a_PRE.prefab";break;
   case "pot":path="Assets/ThirdParty/YamyamAssetLibrary/004-viking-world-stylized-environment/Viking World/Prefabs/Other/FlowerPot_1.prefab";break;
   default:throw new InvalidOperationException("Unknown source-matched prop "+kind);
  }
  var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(!prefab)throw new FileNotFoundException("Missing licensed prop",path);return prefab;
 }
}
#endif
