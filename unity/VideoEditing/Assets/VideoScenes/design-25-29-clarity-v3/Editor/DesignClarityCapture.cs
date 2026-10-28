using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace Yamyam.DesignVisualV2 {
[InitializeOnLoad]
public static class DesignClarityCapture {
 const string MediaRoot = "C:/Users/1/.codex/video-production/design-25-30-review-actions-20261029";
 static string Library => Path.GetFullPath(Application.dataPath + "/../Library");
 static string Request => Path.Combine(Library, "DesignClarityV3.request.json");
 static string Status => Path.Combine(Library, "DesignClarityV3.status.json");
 [Serializable] public class Job {
  public string command="preflight", slug, cutId, stageClass, output, expectedFingerprint;
  public int frames;
  public int[] sampleFrames;
 }
 [Serializable] class State {
  public string status, slug, cutId, output, scene, error;
  public string unity=Application.unityVersion, compiledSourceFingerprint, stageAssemblyMvid;
  public string renderRequest="RenderPipeline.StandardRequest (full camera stack)";
  public int completed, frames;
  public string[] assets, animations;
 }
 [Serializable] class SceneStamp { public string slug, cutId, stageClass, fingerprint; public int frames; }
 [Serializable] class CompiledStage { public string stageClass, fingerprint, assemblyMvid; public bool typeAvailable; }
 [Serializable] class CompileAck { public string status="compiled", atUtc, unityVersion, bridgeAssemblyMvid; public CompiledStage[] stages; }
 static Job job;
 static State state;
 static Scene scene, prior;
 static DesignClarityLessonStage stage;
 static RenderTexture target;
 static Texture2D pixels;
 static System.Diagnostics.Process encoder;
 static Stream stream;
 static int cursor;
 static bool prepared, locked;
 static string stderr="";
 static DesignClarityCapture() { EditorApplication.update += Poll; EditorApplication.update += WriteCompiledAckWhenIdle; }
 static void WriteCompiledAckWhenIdle() {
  if(EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode) return;
  var stages=new[]{"D25ColorClarityStage","D29ClarityStage"}.Select(name=>{
   var type=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("Yamyam.DesignVisualV2."+name)).FirstOrDefault(t=>t!=null);
   return new CompiledStage{stageClass=name,fingerprint=DesignClarityBuildVersion.For(name),
    typeAvailable=type!=null && typeof(DesignClarityLessonStage).IsAssignableFrom(type),
    assemblyMvid=type?.Assembly.ManifestModule.ModuleVersionId.ToString()};
  }).ToArray();
  var ack=new CompileAck{atUtc=DateTime.UtcNow.ToString("o"),unityVersion=Application.unityVersion,
   bridgeAssemblyMvid=typeof(DesignClarityCapture).Assembly.ManifestModule.ModuleVersionId.ToString(),stages=stages};
  File.WriteAllText(Path.Combine(Library,"DesignClarityV3.compiled.json"),JsonUtility.ToJson(ack,true));
  EditorApplication.update-=WriteCompiledAckWhenIdle;
 }

 static string StageFor(string slug) {
  switch(slug) {
   case "limited-color-world": return "D25ColorClarityStage";
   case "kind-to-beginners": return "D29ClarityStage";
   default: throw new InvalidDataException("Only the two explicitly selected clarity revisions are supported.");
  }
 }
 static void Validate(Job j) {
  if(j==null || (j.command!="preflight" && j.command!="render")) throw new InvalidDataException("Unsupported command.");
  if(j.stageClass!=StageFor(j.slug)) throw new InvalidDataException("Slug/stage mismatch.");
  if(!Regex.IsMatch(j.cutId??"", @"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")) throw new InvalidDataException("Invalid cut ID.");
  if(j.frames<1 || j.frames>36000) throw new InvalidDataException("Invalid frame count.");
  if(!Regex.IsMatch(j.expectedFingerprint??"", "^[a-f0-9]{64}$")) throw new InvalidDataException("Missing frozen fingerprint.");
  var root=Path.GetFullPath(MediaRoot+"/"+j.slug+"/clarity-v3").Replace('\\','/').TrimEnd('/')+"/";
  var output=Path.GetFullPath(j.output??"").Replace('\\','/');
  if(!output.StartsWith(root,StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Output outside this slug's scoped media folder.");
  var tail=output.Substring(root.Length);
  if(!Regex.IsMatch(tail,"^"+j.command+"/[A-Za-z0-9_-]+/"+Regex.Escape(j.cutId)+"$")) throw new InvalidDataException("Output must be phase/revision/cutId.");
  j.output=output;
  if(j.command=="preflight" && (j.sampleFrames==null || j.sampleFrames.Length==0 || j.sampleFrames.Length>1000 ||
      j.sampleFrames.Any(f=>f<0 || f>=j.frames) || !j.sampleFrames.SequenceEqual(j.sampleFrames.Distinct().OrderBy(f=>f))))
   throw new InvalidDataException("Preflight frames must be sorted, unique and in range.");
 }
 static bool OtherCapturePending() {
  if(File.Exists(Path.Combine(Library,"DesignVisualV2.request.json")) ||
   Directory.GetFiles(Library,"*.request",SearchOption.TopDirectoryOnly).Length>0) return true;
  var priorStatus=Path.Combine(Library,"DesignVisualV2.status.json");
  if(File.Exists(priorStatus)) {
   try {var s=JsonUtility.FromJson<State>(File.ReadAllText(priorStatus));return s.status=="building"||s.status=="capturing";}
   catch {return true;}
  }
  return false;
 }
 static void Poll() {
  if(job!=null || EditorApplication.isCompiling || EditorApplication.isUpdating ||
     EditorApplication.isPlayingOrWillChangePlaymode || !File.Exists(Request) || OtherCapturePending()) return;
  Job parsed=null;
  try {
   parsed=JsonUtility.FromJson<Job>(File.ReadAllText(Request)); Validate(parsed);
   // Leave the request pending while a newly written fingerprint awaits compilation.
   if(parsed.expectedFingerprint!=DesignClarityBuildVersion.For(parsed.stageClass)) return;
   File.Move(Request,Request+".consumed-"+DateTime.UtcNow.ToString("yyyyMMddHHmmssfff"));
   Start(parsed);
  } catch(Exception e) {
   if(job!=null) Finish(e);
   else {
    // Invalid requests are quarantined without writing to their untrusted output path.
    if(File.Exists(Request)) File.Move(Request,Request+".rejected-"+DateTime.UtcNow.ToString("yyyyMMddHHmmssfff"));
    File.WriteAllText(Status,JsonUtility.ToJson(new State{status="rejected",slug=parsed?.slug,cutId=parsed?.cutId,output=parsed?.output,error=e.ToString()},true));
   }
  }
 }
 static void Start(Job j) {
  Validate(j);
  var movie=Path.Combine(j.output,"unity.mp4");
  if(Directory.Exists(j.output) && (File.Exists(Path.Combine(j.output,j.command+"-success.json")) ||
      File.Exists(Path.Combine(j.output,"progress.json")) || File.Exists(movie) || Directory.GetFiles(j.output,"frame-*.png").Length>0))
   throw new IOException("Prior capture or partial output preserved; choose a fresh revision directory.");
  Directory.CreateDirectory(j.output);
  job=j; state=new State{status="building",slug=j.slug,cutId=j.cutId,frames=j.frames,output=j.output,
   compiledSourceFingerprint=DesignClarityBuildVersion.For(j.stageClass)}; Write();
  prior=SceneManager.GetActiveScene();
  scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
  SceneManager.SetActiveScene(scene);
  var go=new GameObject("Editable clarity lesson — "+j.slug+" / "+j.cutId);
  SceneManager.MoveGameObjectToScene(go,scene);
  var type=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("Yamyam.DesignVisualV2."+j.stageClass)).FirstOrDefault(t=>t!=null);
  if(type==null || !typeof(DesignClarityLessonStage).IsAssignableFrom(type)) throw new Exception("Clarity stage is not compiled: "+j.stageClass);
  state.stageAssemblyMvid=type.Assembly.ManifestModule.ModuleVersionId.ToString();
  target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32){antiAliasing=4}; target.Create();
  pixels=new Texture2D(1920,1080,TextureFormat.RGBA32,false);
  stage=(DesignClarityLessonStage)go.AddComponent(type);
  stage.slug=j.slug; stage.cutId=j.cutId; stage.frames=j.frames;
  stage.Initialize(); stage.camera.targetTexture=target;
  Canvas.ForceUpdateCanvases(); stage.Build(); stage.Apply(0); stage.FlushPoses(); Canvas.ForceUpdateCanvases();
  if(j.slug=="limited-color-world") {
   // D25 editorial UI is composited after the world capture. Enforce this boundary
   // explicitly; camera stacking failed native preflight and is not retried here.
   stage.camera.GetUniversalAdditionalCameraData().cameraStack.Clear();
   foreach(var c in stage.GetComponentsInChildren<Canvas>(true)) c.enabled=false;
   foreach(var c in stage.GetComponentsInChildren<Camera>(true)) if(c!=stage.camera)c.enabled=false;
   state.renderRequest="RenderPipeline.StandardRequest (D25 world only; editorial UI composited separately)";
  }
  var request=new RenderPipeline.StandardRequest{destination=target};
  if(!RenderPipeline.SupportsRenderRequest(stage.camera,request)) throw new Exception("Active pipeline does not support full camera-stack requests.");
  // Provisional speech timing must not occupy the final editable scene path.
  // Each preflight revision is retained; only full render saves the canonical cut.
  var sceneRoot="Assets/VideoScenes/"+j.slug+"/clarity-v3/";
  var preflightRevision=Path.GetFileName(Path.GetDirectoryName(j.output));
  // Preserve the first complete native revision. Only the five approved D25
  // contrast repairs save a separately editable scene in a new owned revision.
  var contrastRepair=j.command=="render" && j.slug=="limited-color-world" && preflightRevision=="contrast-v2" &&
   new[]{"c025","c026","c027","c030","c032"}.Contains(j.cutId);
  var saved=sceneRoot+(j.command=="preflight"?"Preflight/"+preflightRevision+"/":
   contrastRepair?"RenderRevisions/contrast-v2/":"")+j.cutId+".unity";
  var stampPath=saved+".capture-source.json";
  var stamp=new SceneStamp{slug=j.slug,cutId=j.cutId,stageClass=j.stageClass,fingerprint=j.expectedFingerprint,frames=j.frames};
  Directory.CreateDirectory(Path.GetDirectoryName(saved)); state.scene=saved;
  if(File.Exists(saved)) {
   if(!File.Exists(stampPath)) throw new IOException("Existing editable scene has no source receipt; preserved.");
   var old=JsonUtility.FromJson<SceneStamp>(File.ReadAllText(stampPath));
   if(old.slug!=stamp.slug || old.cutId!=stamp.cutId || old.stageClass!=stamp.stageClass || old.fingerprint!=stamp.fingerprint || old.frames!=stamp.frames)
    throw new IOException("Existing scene belongs to different source/timing. Archive that owned scene and receipt explicitly before a new revision; it is not overwritten.");
   // Same frozen source and timing: preserve the existing editable scene exactly.
  } else {
   if(!EditorSceneManager.SaveScene(scene,saved)) throw new IOException("Editable scene save failed.");
   File.WriteAllText(stampPath,JsonUtility.ToJson(stamp,true));
  }
  state.assets=stage.usedAssetPaths.ToArray(); state.animations=stage.usedAnimationPaths.ToArray();
  cursor=0; prepared=false;
  if(j.command=="render") {
   var p=new System.Diagnostics.ProcessStartInfo("ffmpeg",
    $"-hide_banner -loglevel error -n -f rawvideo -pixel_format rgba -video_size 1920x1080 -framerate 60 -i pipe:0 -vf vflip,scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p -an -c:v h264_nvenc -preset p4 -rc constqp -qp 18 -bf 2 -g 60 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart \"{movie}\"")
    {UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardError=true};
   encoder=new System.Diagnostics.Process{StartInfo=p};
   encoder.ErrorDataReceived+=(sender,args)=>{if(args.Data!=null)stderr+=args.Data+"\n";};
   encoder.Start(); encoder.BeginErrorReadLine(); stream=encoder.StandardInput.BaseStream;
  }
  EditorApplication.LockReloadAssemblies(); AssetDatabase.DisallowAutoRefresh(); locked=true;
  state.status="capturing"; Write(); EditorApplication.update+=Tick;
 }
 static void Tick() {
  try {
   int f=job.command=="preflight"?job.sampleFrames[cursor]:cursor;
   if(!prepared) {
    stage.Apply(f/60f); stage.FlushPoses(); Canvas.ForceUpdateCanvases();
    EditorApplication.QueuePlayerLoopUpdate(); prepared=true; return;
   }
   // D25 captures its grayscale world alone; D29 keeps its single-camera UI.
   // The failed D25 overlay-stack and two-pass diagnostics are preserved separately.
   RenderPipeline.SubmitRenderRequest(stage.camera,new RenderPipeline.StandardRequest{destination=target});
   var old=RenderTexture.active;
   try { RenderTexture.active=target; pixels.ReadPixels(new Rect(0,0,1920,1080),0,0); pixels.Apply(false); }
   finally { RenderTexture.active=old; }
   if(encoder!=null) { var bytes=pixels.GetRawTextureData<byte>(); stream.Write(bytes.ToArray(),0,bytes.Length); }
   if(job.command=="preflight") {
    var path=Path.Combine(job.output,$"frame-{f:D5}.png");
    using(var file=new FileStream(path,FileMode.CreateNew)) {var png=pixels.EncodeToPNG();file.Write(png,0,png.Length);}
   }
   cursor++; prepared=false; state.completed=cursor;
   if(cursor%120==0) Write();
   if(cursor>=(job.command=="preflight"?job.sampleFrames.Length:job.frames)) Finish(null);
  } catch(Exception e) { Finish(e); }
 }
 static void Write() {
  File.WriteAllText(Status,JsonUtility.ToJson(state,true));
  if(job!=null) File.WriteAllText(Path.Combine(job.output,"progress.json"),JsonUtility.ToJson(state,true));
 }
 static void Finish(Exception error) {
  EditorApplication.update-=Tick;
  try {
   if(encoder!=null) { stream?.Close(); encoder.WaitForExit(); if(encoder.ExitCode!=0) error=new Exception(stderr,error); encoder.Dispose(); encoder=null; }
  } catch(Exception e) { error=e; }
  if(state==null) state=new State();
  if(stage) {state.assets=stage.usedAssetPaths.ToArray();state.animations=stage.usedAnimationPaths.ToArray();}
  state.status=error==null?"complete":"failed"; state.error=error?.ToString();
  try { Write(); if(job!=null) File.WriteAllText(Path.Combine(job.output,job.command+(error==null?"-success":"-failure")+".json"),JsonUtility.ToJson(state,true)); } catch(Exception e) { Debug.LogException(e); }
  if(target) {target.Release();Object.DestroyImmediate(target);} if(pixels) Object.DestroyImmediate(pixels);
  stage=null; target=null; pixels=null; stream=null;
  if(scene.IsValid()&&scene.isLoaded) EditorSceneManager.CloseScene(scene,true);
  if(prior.IsValid()&&prior.isLoaded) SceneManager.SetActiveScene(prior);
  if(locked) {AssetDatabase.AllowAutoRefresh();EditorApplication.UnlockReloadAssemblies();locked=false;}
  job=null; state=null; stderr="";
 }
}
}
