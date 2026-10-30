using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace Yamyam.TechTen.Editor {
 public static class TechTenCapture {
  const string Owned="C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/unity-capture";
  [Serializable]public class Section{public string id,kind,actionKind;public int startFrame,endFrame,unityStage;public float start,end,actionStartSeconds,actionResumeSeconds;}
  [Serializable]public class Timeline{public int frames,fps=60;public Section[] sections;}
  [Serializable]public class Job{public string topic,mode,output,timeline,voiceSha256,sceneVersion;public int[] stages;}
  [Serializable]public class Artifact{public string path,sha256;public long bytes;}
  [Serializable]public class Sample{public string scene,section;public int frame;public float seconds,fillNormalY,maskEnabled,maxSnowDepth,tautPathLength,planeScrollMeters;public int firingCount;public bool collisionBypassed,planeInset;public Vector3 planeOnboardPosition,planeObserverPosition;}
  [Serializable]public class Receipt{public bool success;public string topic,voiceSha256,sourceKind="independently-authored-Unity-teaching-implementation";public int width=1080,height=1080,fps=60;public List<Artifact> artifacts=new List<Artifact>();public List<Sample> samples=new List<Sample>();public List<string> savedScenes=new List<string>();public string limitation="The snow capture/accumulation and rectangular boat mask are simplified teaching implementations; they are not the commercial games' exact render buffers. No original game source or measured game data is represented.";}
  public static void Run(){try{Execute();EditorApplication.Exit(0);}catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
  static void Execute(){
   if(!string.Equals(Path.GetFullPath(".").Replace('\\','/').TrimEnd('/'),Owned,StringComparison.OrdinalIgnoreCase))throw new Exception("Only isolated owned capture project allowed");
   var args=Environment.GetCommandLineArgs();int at=Array.IndexOf(args,"-techTenJob");if(at<0)throw new Exception("Explicit job required");var job=JsonUtility.FromJson<Job>(File.ReadAllText(args[at+1]));
   if(!TechTenBuilder.Topics.Contains(job.topic))throw new Exception("Unknown topic");
   if(string.IsNullOrEmpty(job.sceneVersion)||!System.Text.RegularExpressions.Regex.IsMatch(job.sceneVersion,"^[a-z0-9-]+$"))throw new Exception("Explicit source-scoped scene version required");TechTenBuilder.SceneVersion=job.sceneVersion;
   var output=Path.GetFullPath(job.output).Replace('\\','/');if(!output.StartsWith("C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030/",StringComparison.OrdinalIgnoreCase))throw new Exception("Output outside batch");
   if(File.Exists(Path.Combine(output,"native-receipt.json")))throw new Exception("Preserve previous capture receipt");Directory.CreateDirectory(output);
   var receipt=new Receipt{topic=job.topic,voiceSha256=job.voiceSha256};var scenes=new Dictionary<int,string>();
   foreach(int stage in job.stages??new[]{0,1,2}){string p=TechTenBuilder.ScenePath(job.topic,stage);if(!File.Exists(p))p=TechTenBuilder.Build(job.topic,stage);scenes[stage]=p;receipt.savedScenes.Add(p);}
   // Opening saved scenes unloads unreferenced transient textures. Keep the capture
   // buffers alive across scene switches; they are never saved into the scene.
   var rt=new RenderTexture(1080,1080,24,RenderTextureFormat.ARGB32){antiAliasing=2,hideFlags=HideFlags.HideAndDontSave};rt.Create();var pixels=new Texture2D(1080,1080,TextureFormat.RGB24,false){hideFlags=HideFlags.HideAndDontSave};
   RenderTexture inset=null;Color[] insetBorder=null;
   if(job.topic=="uncharted3-fixed-plane-scrolling-desert"){
    inset=new RenderTexture(432,270,24,RenderTextureFormat.ARGB32){antiAliasing=2,hideFlags=HideFlags.HideAndDontSave};inset.Create();
    insetBorder=Enumerable.Repeat(new Color(.32f,.86f,.77f),444*282).ToArray();
   }
   Action<string,int,float,int,string> capture=(section,frame,seconds,stage,path)=>{
    var d=UnityEngine.Object.FindFirstObjectByType<TechTenDemo>();d.Sample(seconds);d.shot.targetTexture=rt;d.shot.Render();var prev=RenderTexture.active;RenderTexture.active=rt;pixels.ReadPixels(new Rect(0,0,1080,1080),0,0);
    if(d.PlaneHasInset){
     if(!inset)throw new Exception("Plane inset buffer is missing");
     d.planeOnboardCamera.targetTexture=inset;d.planeOnboardCamera.Render();RenderTexture.active=inset;
     // The actual secondary camera uses the very same sampled scene/time. Keep
     // the observer frame intact except for this explicitly bordered upper inset.
     pixels.SetPixels(606,742,444,282,insetBorder);pixels.ReadPixels(new Rect(0,0,432,270),612,748);
    }
    pixels.Apply();RenderTexture.active=prev;Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllBytes(path,pixels.EncodeToJPG(94));
    if(job.mode=="preview"||frame%120==0)receipt.samples.Add(new Sample{scene=scenes[stage],section=section,frame=frame,seconds=seconds,fillNormalY=d.lastFillNormalY,maskEnabled=d.lastMaskEnabled,maxSnowDepth=d.lastGap,tautPathLength=d.lastRopeLength,firingCount=d.firedCount,collisionBypassed=d.collisionBypassed,planeInset=d.PlaneHasInset,planeScrollMeters=d.planeScrollMeters,planeOnboardPosition=d.planeOnboardCamera?d.planeOnboardCamera.transform.position:Vector3.zero,planeObserverPosition=d.shot.transform.position});
   };
   if(job.mode=="preview"){
    foreach(var pair in scenes){EditorSceneManager.OpenScene(pair.Value);foreach(float t in new[]{.75f,3.5f}){string p=Path.Combine(output,pair.Key+"-"+t.ToString("0.00",System.Globalization.CultureInfo.InvariantCulture)+".jpg");capture("preview",0,t,pair.Key,p);receipt.artifacts.Add(Hash(p));}}
   }else{
    if(string.IsNullOrWhiteSpace(job.voiceSha256))throw new Exception("Full capture requires exact PCM hash");var timing=JsonUtility.FromJson<Timeline>(File.ReadAllText(job.timeline));if(timing.fps!=60)throw new Exception("Require60fps");
    foreach(var s in timing.sections.Where(s=>s.kind=="unity")){if(!scenes.ContainsKey(s.unityStage))throw new Exception("Missing scene stage");ValidateAction(s);EditorSceneManager.OpenScene(scenes[s.unityStage]);var demo=UnityEngine.Object.FindFirstObjectByType<TechTenDemo>();demo.actionKind=s.actionKind??"";demo.actionStartSeconds=s.actionStartSeconds;demo.actionResumeSeconds=s.actionResumeSeconds;for(int f=s.startFrame;f<s.endFrame;f++){string p=Path.Combine(output,s.id,(f-s.startFrame).ToString("D5")+".jpg");capture(s.id,f-s.startFrame,(f-s.startFrame)/60f,s.unityStage,p);receipt.artifacts.Add(Hash(p));if(f%180==0)Debug.Log("TECH_FRAME "+job.topic+" "+f+"/"+timing.frames);}}
   }
   foreach(string s in scenes.Values)receipt.artifacts.Add(Hash(s));receipt.success=true;File.WriteAllText(Path.Combine(output,"native-receipt.json"),JsonUtility.ToJson(receipt,true));rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(pixels);if(inset){inset.Release();UnityEngine.Object.DestroyImmediate(inset);}Debug.Log("TECH_CAPTURE_SUCCESS "+job.topic);
  }
  static void ValidateAction(Section s){
   float duration=(s.endFrame-s.startFrame)/60f;if(duration<=0)throw new Exception("Nonpositive native section duration");
   if(string.IsNullOrEmpty(s.actionKind))return;
   if(float.IsNaN(s.actionStartSeconds)||float.IsInfinity(s.actionStartSeconds)||s.actionStartSeconds<0||s.actionStartSeconds>=duration)throw new Exception("Invalid measured action cue: "+s.id);
   if(s.actionKind=="background-toggle"||s.actionKind=="accumulation-toggle"){
    if(float.IsNaN(s.actionResumeSeconds)||float.IsInfinity(s.actionResumeSeconds)||s.actionResumeSeconds<=s.actionStartSeconds||s.actionResumeSeconds>=duration)throw new Exception("Invalid measured stop/resume cues: "+s.id);
   }
  }
  static Artifact Hash(string p){byte[] b=File.ReadAllBytes(p);using(var sha=SHA256.Create())return new Artifact{path=Path.GetFullPath(p),bytes=b.LongLength,sha256=BitConverter.ToString(sha.ComputeHash(b)).Replace("-","").ToLowerInvariant()};}
 }
}
