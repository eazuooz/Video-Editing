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

namespace Yamyam.AnimationSeries {
[InitializeOnLoad]
public static class AnimationGridCapture {
 const string MediaRoot = "D:/Github/VideoEditing/projects/animation-assigning/production/local/grid-v1";
 static string Library => Path.GetFullPath(Application.dataPath + "/../Library");
 static string Request => Path.Combine(Library, "AnimationGridV1.request.json");
 static string Status => Path.Combine(Library, "AnimationGridV1.status.json");
 [Serializable] public class Job {
  public string command="preflight", slug, cutId, stageClass, output, expectedFingerprint, presentationId;
  public int frames;
  public int[] sampleFrames;
 }
 [Serializable] class State {
  public string status, slug, cutId, output, scene, error, presentationId;
  public string unity=Application.unityVersion, compiledSourceFingerprint, stageAssemblyMvid;
  public string renderRequest="RenderPipeline.StandardRequest (full camera stack)";
  public int completed, frames;
  public string[] assets, animations;
 }
 [Serializable] class SceneStamp { public string slug, cutId, stageClass, fingerprint, presentationId; public int frames; }
 [Serializable] class CompiledStage { public string stageClass, fingerprint, assemblyMvid; public bool typeAvailable; }
 [Serializable] class CompileAck { public string status="compiled", atUtc, unityVersion, bridgeAssemblyMvid; public CompiledStage[] stages; }
 [Serializable] class SceneViewEvidence {public string path,name,sceneMask;public bool isDirty,isCaptureScene;public string[] roots;public int layer29Renderers,layer29Canvases;}
 [Serializable] class IsolationEvidence {public string cameraMask;public SceneViewEvidence[] scenes;public string principle="Only the newly created capture scene gets an unused culling bit; existing loaded scenes are preserved.";}
 static Job job;
 static State state;
 static Scene scene, prior;
 static AnimationLessonStage stage;
 static RenderTexture target;
 static Texture2D pixels;
 static System.Diagnostics.Process encoder;
 static Stream stream;
 static int cursor;
 static bool prepared, locked;
 static string stderr="";
 static AnimationGridCapture() { EditorApplication.update += Poll; EditorApplication.update += WriteCompiledAckWhenIdle; }
 static void WriteCompiledAckWhenIdle() {
  if(EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode) return;
  var stages=new[]{"AnimationGridStage"}.Select(name=>{
   var type=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("Yamyam.AnimationSeries."+name)).FirstOrDefault(t=>t!=null);
   return new CompiledStage{stageClass=name,fingerprint=AnimationGridBuildVersion.For(name),
    typeAvailable=type!=null && typeof(AnimationLessonStage).IsAssignableFrom(type),
    assemblyMvid=type?.Assembly.ManifestModule.ModuleVersionId.ToString()};
  }).ToArray();
  var ack=new CompileAck{atUtc=DateTime.UtcNow.ToString("o"),unityVersion=Application.unityVersion,
   bridgeAssemblyMvid=typeof(AnimationGridCapture).Assembly.ManifestModule.ModuleVersionId.ToString(),stages=stages};
  File.WriteAllText(Path.Combine(Library,"AnimationGridV1.compiled.json"),JsonUtility.ToJson(ack,true));
  EditorApplication.update-=WriteCompiledAckWhenIdle;
 }

 static string StageFor(string slug) {
  switch(slug) {
   case "animation-assigning": return "AnimationGridStage";
   default: throw new InvalidDataException("Only selected A01 animation-assigning is supported by this capture revision.");
  }
 }
 static void Validate(Job j) {
  if(j==null || (j.command!="preflight" && j.command!="render")) throw new InvalidDataException("Unsupported command.");
  if(j.stageClass!=StageFor(j.slug)) throw new InvalidDataException("Slug/stage mismatch.");
  if(!Regex.IsMatch(j.cutId??"", @"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")) throw new InvalidDataException("Invalid cut ID.");
  if(j.frames<1 || j.frames>36000) throw new InvalidDataException("Invalid frame count.");
  if(!Regex.IsMatch(j.expectedFingerprint??"", "^[a-f0-9]{64}$")) throw new InvalidDataException("Missing frozen fingerprint.");
  var root=Path.GetFullPath(MediaRoot).Replace('\\','/').TrimEnd('/')+"/";
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
  foreach(var name in new[]{"DesignVisualV2","DesignClarityV3","DesignBotwV4"}) {
   if(File.Exists(Path.Combine(Library,name+".request.json")))return true;
   var path=Path.Combine(Library,name+".status.json");
   if(File.Exists(path)){try{var s=JsonUtility.FromJson<State>(File.ReadAllText(path));if(s.status=="building"||s.status=="capturing")return true;}catch{return true;}}
  }
  return Directory.GetFiles(Library,"*.request",SearchOption.TopDirectoryOnly).Length>0 || Directory.GetFiles(Library,"*.request.json",SearchOption.TopDirectoryOnly).Any(p=>p!=Request);
 }
 static void Poll() {
  if(job!=null || EditorApplication.isCompiling || EditorApplication.isUpdating ||
     EditorApplication.isPlayingOrWillChangePlaymode || !File.Exists(Request) || OtherCapturePending()) return;
  Job parsed=null;
  try {
   parsed=JsonUtility.FromJson<Job>(File.ReadAllText(Request)); Validate(parsed);
   // Leave the request pending while a newly written fingerprint awaits compilation.
   if(parsed.expectedFingerprint!=AnimationGridBuildVersion.For(parsed.stageClass)) return;
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
  job=j; state=new State{status="building",slug=j.slug,cutId=j.cutId,frames=j.frames,output=j.output,presentationId=j.presentationId,
   compiledSourceFingerprint=AnimationGridBuildVersion.For(j.stageClass)}; Write();
  prior=SceneManager.GetActiveScene();
  scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
  ulong isolatedMask=EditorSceneManager.CalculateAvailableSceneCullingMask();
  if(isolatedMask==0)throw new Exception("No unused scene-culling bit is available; preserve existing scenes.");
  EditorSceneManager.SetSceneCullingMask(scene,isolatedMask);
  SceneManager.SetActiveScene(scene);
  var go=new GameObject("Editable Animation teaching lesson — "+j.slug+" / "+j.cutId);
  SceneManager.MoveGameObjectToScene(go,scene);
  var type=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("Yamyam.AnimationSeries."+j.stageClass)).FirstOrDefault(t=>t!=null);
  if(type==null || !typeof(AnimationLessonStage).IsAssignableFrom(type)) throw new Exception("BOTW stage is not compiled: "+j.stageClass);
  state.stageAssemblyMvid=type.Assembly.ManifestModule.ModuleVersionId.ToString();
  target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32){antiAliasing=4}; target.Create();
  pixels=new Texture2D(1920,1080,TextureFormat.RGBA32,false);
  stage=(AnimationLessonStage)go.AddComponent(type);
  stage.slug=j.slug; stage.cutId=j.cutId; stage.frames=j.frames;
  if(stage is AnimationGridStage grid)grid.presentationId=j.presentationId;
  stage.Initialize(); stage.camera.targetTexture=target;
  stage.camera.overrideSceneCullingMask=isolatedMask;
  Canvas.ForceUpdateCanvases(); stage.Build(); stage.PrepareKnownGlyphs(); stage.Apply(0); stage.FlushPoses(); stage.RefreshUi();
  var sceneEvidence=Enumerable.Range(0,SceneManager.sceneCount).Select(i=>SceneManager.GetSceneAt(i)).Where(s=>s.isLoaded).Select(s=>new SceneViewEvidence{path=s.path,name=s.name,isDirty=s.isDirty,isCaptureScene=s==scene,sceneMask=EditorSceneManager.GetSceneCullingMask(s).ToString(),roots=s.GetRootGameObjects().Select(o=>o.name).ToArray(),layer29Renderers=s.GetRootGameObjects().Sum(o=>o.GetComponentsInChildren<Renderer>(true).Count(r=>r.gameObject.layer==29)),layer29Canvases=s.GetRootGameObjects().Sum(o=>o.GetComponentsInChildren<Canvas>(true).Count(c=>c.gameObject.layer==29))}).ToArray();
  if(sceneEvidence.Any(s=>!s.isCaptureScene&&(ulong.Parse(s.sceneMask)&isolatedMask)!=0))throw new Exception("Capture scene mask overlaps another loaded scene.");
  File.WriteAllText(Path.Combine(j.output,"scene-isolation.json"),JsonUtility.ToJson(new IsolationEvidence{cameraMask=isolatedMask.ToString(),scenes=sceneEvidence},true));
  var request=new RenderPipeline.StandardRequest{destination=target};
  if(!RenderPipeline.SupportsRenderRequest(stage.camera,request)) throw new Exception("Active pipeline does not support full camera-stack requests.");
  // Provisional speech timing must not occupy the final editable scene path.
  // Each preflight revision is retained; only full render saves the canonical cut.
  var sceneRoot="Assets/VideoScenes/animation-assigning/grid-v1/";
  var revision=Path.GetFileName(Path.GetDirectoryName(j.output));
  var saved=sceneRoot+(j.command=="preflight"?"Preflight/":"RenderRevisions/")+revision+"/"+j.cutId+".unity";
  var stampPath=saved+".capture-source.json";
  var stamp=new SceneStamp{slug=j.slug,cutId=j.cutId,stageClass=j.stageClass,fingerprint=j.expectedFingerprint,frames=j.frames,presentationId=j.presentationId};
  Directory.CreateDirectory(Path.GetDirectoryName(saved)); state.scene=saved;
  if(File.Exists(saved)) {
   if(!File.Exists(stampPath)) throw new IOException("Existing editable scene has no source receipt; preserved.");
   var old=JsonUtility.FromJson<SceneStamp>(File.ReadAllText(stampPath));
   if(old.slug!=stamp.slug || old.cutId!=stamp.cutId || old.stageClass!=stamp.stageClass || old.fingerprint!=stamp.fingerprint || old.frames!=stamp.frames || old.presentationId!=stamp.presentationId)
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
    stage.Apply(f/60f); stage.FlushPoses(); stage.RefreshUi();
    if(job.command=="preflight")File.WriteAllText(Path.Combine(job.output,$"pose-{f:D5}.json"),stage.PoseDiagnostic());
    EditorApplication.QueuePlayerLoopUpdate(); prepared=true; return;
   }
   // This isolated D29 stage uses one camera for world and editorial UI.
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
