using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace Yamyam.TechTen.Editor {
 // Bounded diagnostic only: no scene/asset mutation or final production output.
 public static class TechTenSnowAudit {
  [Serializable] public class Bone {public string name,path;public Vector3 localPosition,worldPosition,euler;}
  [Serializable] public class SurfaceBounds {public string name;public float minimumWorldY,maximumWorldY;}
  [Serializable] public class Pose {public float seconds;public List<Bone> bones=new List<Bone>();public List<string> meshHashes=new List<string>();public List<SurfaceBounds> surfaceBounds=new List<SurfaceBounds>();}
  [Serializable] public class Method {public string method;public List<Pose> poses=new List<Pose>();}
  [Serializable] public class Clip {public string name;public float length,frameRate;public bool legacy,human;public int bindingCount;public string[] bindingExamples,missingPaths;public List<Method> methods=new List<Method>();}
  [Serializable] public class Report {public string importerType,animatorPath,avatar,selectedClipName,selectedScene;public long selectedClipFileId;public int selectedBindingCount;public string[] selectedMissingPaths;public List<Pose> actualScenePoses=new List<Pose>();public List<Clip> clips=new List<Clip>();}
  static string PathOf(Transform t,Transform root){return t==root?"":AnimationUtility.CalculateTransformPath(t,root);}
  static Pose Measure(GameObject g,float t){
   var pose=new Pose{seconds=t};
   foreach(var bone in g.GetComponentsInChildren<Transform>())if(new[]{"hips","upperleg.l","lowerleg.l","foot.l","upperleg.r","lowerleg.r","foot.r"}.Contains(bone.name))pose.bones.Add(new Bone{name=bone.name,path=PathOf(bone,g.transform),localPosition=bone.localPosition,worldPosition=bone.position,euler=bone.localEulerAngles});
   foreach(var skin in g.GetComponentsInChildren<SkinnedMeshRenderer>()){
    var mesh=new Mesh();skin.BakeMesh(mesh);var vertices=mesh.vertices;var bytes=new byte[vertices.Length*12];float minimum=float.PositiveInfinity,maximum=float.NegativeInfinity;
    for(int i=0;i<vertices.Length;i++){Buffer.BlockCopy(BitConverter.GetBytes(vertices[i].x),0,bytes,i*12,4);Buffer.BlockCopy(BitConverter.GetBytes(vertices[i].y),0,bytes,i*12+4,4);Buffer.BlockCopy(BitConverter.GetBytes(vertices[i].z),0,bytes,i*12+8,4);}
    foreach(var vertex in vertices){float y=skin.transform.TransformPoint(vertex).y;minimum=Mathf.Min(minimum,y);maximum=Mathf.Max(maximum,y);}pose.surfaceBounds.Add(new SurfaceBounds{name=skin.name,minimumWorldY=minimum,maximumWorldY=maximum});
    using(var sha=SHA256.Create())pose.meshHashes.Add(skin.name+":"+BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-","").ToLowerInvariant());UnityEngine.Object.DestroyImmediate(mesh);
   }return pose;
  }
  public static void Run(){try{
   const string owned="C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/unity-capture";
   if(!string.Equals(Path.GetFullPath(".").Replace('\\','/').TrimEnd('/'),owned,StringComparison.OrdinalIgnoreCase))throw new Exception("Only owned isolated capture project allowed");
   var args=Environment.GetCommandLineArgs();int at=Array.IndexOf(args,"-techTenAudit");if(at<0)throw new Exception("Explicit audit output required");
   var output=Path.GetFullPath(args[at+1]).Replace('\\','/');if(!output.StartsWith("C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/",StringComparison.OrdinalIgnoreCase)||File.Exists(output))throw new Exception("Preserve prior audit/outside scope");
   const string path="Assets/ThirdParty/KayKitAdventurers/Knight.fbx";var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);var report=new Report{importerType=((ModelImporter)AssetImporter.GetAtPath(path)).animationType.ToString()};
   int sceneAt=Array.IndexOf(args,"-techTenScene");if(sceneAt>=0){
    string scene=args[sceneAt+1];if(!scene.StartsWith("Assets/VideoScenes/tech-ten-shorts-20261030/Scenes/batman-origins-snow-below-camera/",StringComparison.Ordinal))throw new Exception("Only selected saved Batman scene");
    EditorSceneManager.OpenScene(scene);var demo=UnityEngine.Object.FindFirstObjectByType<TechTenDemo>();
    report.selectedScene=scene;report.selectedClipName=demo.walk.name;string guid;long fileId;AssetDatabase.TryGetGUIDAndLocalFileIdentifier(demo.walk,out guid,out fileId);report.selectedClipFileId=fileId;
    var selectedBindings=AnimationUtility.GetCurveBindings(demo.walk);report.selectedBindingCount=selectedBindings.Length;report.selectedMissingPaths=selectedBindings.Select(b=>b.path).Distinct().Where(p=>p!=""&&!demo.actors[0].Find(p)).ToArray();
    demo.actors[0].position=new Vector3(0,.12f,0);
    for(int phase=0;phase<=32;phase++){float t=demo.walk.length*phase/32;demo.walk.SampleAnimation(demo.actors[0].gameObject,t);report.actualScenePoses.Add(Measure(demo.actors[0].gameObject,t));}
   }
   foreach(var clip in AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Where(c=>c.name.ToLowerInvariant().Contains("walk")&&!c.name.StartsWith("__preview__"))){
    var bindings=AnimationUtility.GetCurveBindings(clip);var item=new Clip{name=clip.name,length=clip.length,frameRate=clip.frameRate,legacy=clip.legacy,human=clip.isHumanMotion,bindingCount=bindings.Length,bindingExamples=bindings.Take(24).Select(b=>b.path+" | "+b.type.Name+" | "+b.propertyName).ToArray()};
    foreach(string mode in new[]{"SampleAnimation","ManualPlayable"}){
     var g=UnityEngine.Object.Instantiate(asset);var animator=g.GetComponentInChildren<Animator>();report.animatorPath=animator?PathOf(animator.transform,g.transform):"none";report.avatar=animator&&animator.avatar?animator.avatar.name+" valid="+animator.avatar.isValid:"none";
     item.missingPaths=bindings.Select(b=>b.path).Distinct().Where(p=>p!=""&&!g.transform.Find(p)).ToArray();
     var method=new Method{method=mode};PlayableGraph graph=default(PlayableGraph);AnimationClipPlayable playable=default(AnimationClipPlayable);
     if(mode=="ManualPlayable"){
      if(!animator)animator=g.AddComponent<Animator>();animator.enabled=true;animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
      graph=PlayableGraph.Create("Bounded snow diagnostic");graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);playable=AnimationClipPlayable.Create(graph,clip);playable.SetApplyFootIK(false);var o=AnimationPlayableOutput.Create(graph,"walk",animator);o.SetSourcePlayable(playable);graph.Play();
     }else if(animator)animator.enabled=false;
     foreach(float phase in new[]{0f,.125f,.25f,.375f,.5f}){
      float t=clip.length*phase;if(mode=="ManualPlayable"){playable.SetTime(t);graph.Evaluate(0);}else clip.SampleAnimation(g,t);method.poses.Add(Measure(g,t));
     }
     if(graph.IsValid())graph.Destroy();item.methods.Add(method);UnityEngine.Object.DestroyImmediate(g);
    }report.clips.Add(item);
   }
   Directory.CreateDirectory(Path.GetDirectoryName(output));File.WriteAllText(output,JsonUtility.ToJson(report,true));Debug.Log("TECH_SNOW_RIG_AUDIT_SUCCESS "+output);EditorApplication.Exit(0);
  }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
 }
}
