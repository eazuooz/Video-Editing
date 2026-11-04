#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object=UnityEngine.Object;

namespace Yamyam.RemainingMathCapture {
 // Shared capture transport for two independently implemented teaching modules.
 // It does not select lecture content, create narration, or infer speech timing.
 public static class UnityLectureCapture {
  [Serializable] public class Job {
   public string projectSlug,id,command,output,ffmpeg,expectedFingerprint,shotFile,factoryType;
   public int frames;public int[] sampleFrames;public bool speechTimingVerified;
  }
  [Serializable] public class State {
   public string status,error,scene,output,id,unity,fingerprint;
   public int completed,total;public bool actualGameplay=false,finalVisualQa=false;
   public string sourceKind="our implementation / Unity",size="1920x1080",fps="60/1";
  }
  static Job job;static State state;static Component stage;static Camera camera;static MethodInfo evaluate;
  static RenderTexture target;static Texture2D pixels;static int cursor,warmup;static bool prepared,locked;
  static System.Diagnostics.Process encoder;static Stream pipe;static string encoderErrors="";static string assets;
  public static void Run(){try {
   string project=Path.GetFullPath(Path.Combine(Application.dataPath,".."));
   if(!File.Exists(Path.Combine(project,"MATH_CAPTURE_SANDBOX.json")))throw new InvalidOperationException("Dedicated capture sandbox marker required");
   var file=Environment.GetEnvironmentVariable("YAMYAM_MATH_CAPTURE_JOB");
   if(string.IsNullOrEmpty(file)||!File.Exists(file))throw new FileNotFoundException("Explicit capture job required");
   job=JsonUtility.FromJson<Job>(File.ReadAllText(file));
   string factory=job.projectSlug=="game-math-skinning-normal-map"?"SkinNormalSceneBuilder":job.projectSlug=="game-math-pipeline-shaders"?"PipelineSceneBuilder":null;
   if(factory==null||job.factoryType!=factory)throw new InvalidDataException("Unsupported lecture/factory pair");
   string scope=Path.GetFullPath("D:/Github/VideoEditing/projects/"+job.projectSlug+"/production/");
   if(!project.StartsWith(scope,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException("Shared/user editor project is not a capture target");
   if(!System.Text.RegularExpressions.Regex.IsMatch(job.id??"",@"^m(22|23)-[a-z0-9-]+$"))throw new InvalidDataException("Invalid cue ID");
   if(job.command!="preflight"&&job.command!="render")throw new InvalidDataException("Unsupported command");
   if(Environment.GetCommandLineArgs().Contains("-nographics"))throw new InvalidOperationException("Graphics context required");
   if(job.expectedFingerprint!=LectureBuildVersion.Value)throw new InvalidDataException("Compiled code changed since reviewed job");
   if(job.frames<1||job.frames>108000)throw new InvalidDataException("Frame count outside one cue scope");
   if(job.command=="render"&&!job.speechTimingVerified)throw new InvalidDataException("Actual narration timing must be reviewed before final capture");
   job.output=Path.GetFullPath(job.output);
   if(!job.output.StartsWith(scope,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Output outside selected lecture");
   if(Directory.Exists(job.output)&&Directory.EnumerateFileSystemEntries(job.output).Any())throw new IOException("Existing output preserved; use a new revision");
   if(job.command=="preflight"&&(job.sampleFrames==null||job.sampleFrames.Length==0||job.sampleFrames.Any(f=>f<0||f>=job.frames)))throw new InvalidDataException("Invalid sample frames");
   Directory.CreateDirectory(job.output);state=new State{status="building",id=job.id,output=job.output,total=job.frames,unity=Application.unityVersion,fingerprint=LectureBuildVersion.Value};Write();
   assets="Assets/VideoScenes/"+job.projectSlug+"/Generated/"+LectureBuildVersion.Value.Substring(0,12)+"/"+job.command+"/"+job.id;
   Directory.CreateDirectory(assets);AssetDatabase.Refresh();
   var renderer=ScriptableObject.CreateInstance<UniversalRendererData>();AssetDatabase.CreateAsset(renderer,assets+"/Renderer.asset");
   var pipeline=UniversalRenderPipelineAsset.Create(renderer);pipeline.msaaSampleCount=4;pipeline.supportsHDR=false;AssetDatabase.CreateAsset(pipeline,assets+"/URP.asset");
   GraphicsSettings.defaultRenderPipeline=pipeline;QualitySettings.renderPipeline=pipeline;PlayerSettings.colorSpace=ColorSpace.Linear;QualitySettings.vSyncCount=0;
   var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.09f,.09f,.09f);
   var factoryClass=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType(factory)).FirstOrDefault(t=>t!=null);
   if(factoryClass==null)throw new TypeLoadException(factory);
   var build=factoryClass.GetMethod("BuildStage",BindingFlags.Public|BindingFlags.Static);
   if(build==null||build.GetParameters().Length!=1)throw new InvalidDataException("Expected typed BuildStage(shot)");
   var shotType=build.GetParameters()[0].ParameterType;var shot=JsonUtility.FromJson(File.ReadAllText(job.shotFile),shotType);
   double duration=(double)shotType.GetField("durationSeconds").GetValue(shot);
   if(duration<=0||double.IsNaN(duration)||double.IsInfinity(duration))throw new InvalidDataException("Positive explicit cue duration required");
   if(job.command=="render"&&Math.Abs(duration*60-job.frames)>1.01)throw new InvalidDataException("Audio/frame timing mismatch");
   stage=(Component)build.Invoke(null,new[]{shot});camera=(Camera)stage.GetType().GetField("stageCamera").GetValue(stage);
   evaluate=stage.GetType().GetMethod("Evaluate",new[]{typeof(double)});if(!camera||evaluate==null)throw new InvalidDataException("Module capture interface missing");
   foreach(var shader in stage.GetComponentsInChildren<Renderer>(true).SelectMany(r=>r.sharedMaterials).Where(m=>m).Select(m=>m.shader).Distinct())
    if(ShaderUtil.GetShaderMessages(shader).Any(m=>m.severity.ToString()=="Error"))throw new InvalidOperationException("Shader compilation failed: "+shader.name);
   evaluate.Invoke(stage,new object[]{0.0});PersistOwnedAssets();
   state.scene="Assets/VideoScenes/"+job.projectSlug+"/Scenes/"+LectureBuildVersion.Value.Substring(0,12)+"/"+job.command+"/"+job.id+".unity";
   Directory.CreateDirectory(Path.GetDirectoryName(state.scene));if(File.Exists(state.scene))throw new IOException("Existing editable scene preserved");
   if(!EditorSceneManager.SaveScene(scene,state.scene))throw new IOException("Editable scene save failed");AssetDatabase.SaveAssets();
   target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32){antiAliasing=4};target.Create();pixels=new Texture2D(1920,1080,TextureFormat.RGBA32,false);camera.targetTexture=target;
   if(job.command=="render"){
    if(!File.Exists(job.ffmpeg))throw new FileNotFoundException("Explicit FFmpeg binary required");
    var args="-hide_banner -loglevel error -n -f rawvideo -pixel_format rgba -video_size 1920x1080 -framerate 60 -i pipe:0 -vf vflip,scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p -an -c:v libx264 -threads 4 -preset fast -crf 17 -g 60 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart \""+Path.Combine(job.output,"unity.mp4")+"\"";
    encoder=new System.Diagnostics.Process{StartInfo=new System.Diagnostics.ProcessStartInfo(job.ffmpeg,args){UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardError=true}};
    encoder.ErrorDataReceived+=(s,e)=>{if(e.Data!=null)encoderErrors+=e.Data+"\n";};encoder.Start();encoder.BeginErrorReadLine();pipe=encoder.StandardInput.BaseStream;
   }
   EditorApplication.LockReloadAssemblies();AssetDatabase.DisallowAutoRefresh();locked=true;state.status="capturing";Write();EditorApplication.update+=Tick;
  }catch(Exception e){Finish(e);}}
  static void PersistOwnedAssets(){
   var f=stage.GetType().GetField("owned",BindingFlags.NonPublic|BindingFlags.Instance);
   if(f?.GetValue(stage) is System.Collections.IEnumerable list)foreach(var o in list){
    if(!(o is Object obj)||!obj||AssetDatabase.Contains(obj)||(!(obj is Mesh)&&!(obj is Material)&&!(obj is Texture2D)))continue;
    AssetDatabase.CreateAsset(obj,assets+"/"+Guid.NewGuid().ToString("N")+(obj is Material?".mat":".asset"));
   }
  }
  static void RefreshText(){var labels=stage.GetComponentsInChildren<UnityEngine.UI.Text>(true);foreach(var t in labels)if(t.isActiveAndEnabled&&t.font)t.font.RequestCharactersInTexture(t.text,t.fontSize,t.fontStyle);foreach(var t in labels)if(t.isActiveAndEnabled){t.cachedTextGenerator.Invalidate();t.SetAllDirty();}Canvas.ForceUpdateCanvases();}
  static void Tick(){try{
   int frame=job.command=="preflight"?job.sampleFrames[cursor]:cursor;
   if(!prepared){evaluate.Invoke(stage,new object[]{frame/60.0});RefreshText();EditorApplication.QueuePlayerLoopUpdate();prepared=true;warmup=job.command=="preflight"||cursor==0?2:0;return;}
   RefreshText();var req=new RenderPipeline.StandardRequest{destination=target};if(!RenderPipeline.SupportsRenderRequest(camera,req))throw new InvalidOperationException("URP camera-stack rendering unavailable");RenderPipeline.SubmitRenderRequest(camera,req);
   if(warmup>0){warmup--;EditorApplication.QueuePlayerLoopUpdate();return;}
   var old=RenderTexture.active;RenderTexture.active=target;pixels.ReadPixels(new Rect(0,0,1920,1080),0,0);pixels.Apply(false);RenderTexture.active=old;
   if(job.command=="preflight")File.WriteAllBytes(Path.Combine(job.output,"frame-"+frame.ToString("D6")+".png"),pixels.EncodeToPNG());else{var bytes=pixels.GetRawTextureData<byte>().ToArray();pipe.Write(bytes,0,bytes.Length);}
   cursor++;prepared=false;state.completed=cursor;if(cursor%60==0)Write();if(cursor>=(job.command=="preflight"?job.sampleFrames.Length:job.frames))Finish(null);
  }catch(Exception e){Finish(e);}}
  static void Write(){if(state!=null)File.WriteAllText(Path.Combine(state.output,"progress.json"),JsonUtility.ToJson(state,true));}
  static void Finish(Exception error){EditorApplication.update-=Tick;
   try{if(encoder!=null){pipe.Close();encoder.WaitForExit();if(encoder.ExitCode!=0)error=new IOException(encoderErrors);encoder.Dispose();}}catch(Exception e){error=e;}
   if(camera)camera.targetTexture=null;
   if(error==null&&stage){try{PersistOwnedAssets();EditorSceneManager.SaveScene(stage.gameObject.scene,state.scene);AssetDatabase.SaveAssets();}catch(Exception e){error=e;}}
   if(state!=null){state.status=error==null?"complete":"failed";state.error=error?.ToString();Write();File.WriteAllText(Path.Combine(state.output,error==null?"capture-success.json":"capture-failure.json"),JsonUtility.ToJson(state,true));}
   if(error!=null)Debug.LogException(error);if(target){target.Release();Object.DestroyImmediate(target);}if(pixels)Object.DestroyImmediate(pixels);if(locked){AssetDatabase.AllowAutoRefresh();EditorApplication.UnlockReloadAssemblies();}EditorApplication.Exit(error==null?0:1);
  }
 }
}
#endif
