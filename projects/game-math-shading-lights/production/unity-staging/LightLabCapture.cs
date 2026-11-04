using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object=UnityEngine.Object;

namespace Yamyam.GameMath.LightLab {
 public static class LightLabCapture {
  [Serializable] public class Job {public string id,command="preflight",output,ffmpeg,expectedFingerprint,cueFile;public int frames=480;public int[] sampleFrames=new[]{0,120,240,479};public AdvancedComparisonFrame[] comparisonFrames;}
  [Serializable] public class State {public string status,id,error,scene,output,compiledFingerprint,unity,sourceKind;public int completed,total;public string dimensions="1920x1080",frameRate="60/1";public bool actualGameplay=false;}
  [Serializable] public class BakeEvidence {public string backend,mode;public int lightmapCount,lightmappedRenderers;public bool engineReturnedSuccess,lightIsBaked;}
  static Job job;static State state;static LightLabStage stage;static RenderTexture target;static Texture2D pixels;
  static int cursor;static bool prepared,locked;static System.Diagnostics.Process encoder;static Stream pipe;static string stderr="";
  const string Root="Assets/VideoScenes/game-math-shading-lights";
  public static void Run() {
   try {
    string marker=Path.GetFullPath(Path.Combine(Application.dataPath,"..","M21_SANDBOX.json"));
    if(!File.Exists(marker)||Path.GetFullPath(Application.dataPath).Equals(Path.GetFullPath("D:/Github/VideoEditing/unity/VideoEditing/Assets"),StringComparison.OrdinalIgnoreCase))
      throw new InvalidOperationException("Capture requires the separate M21 sandbox. Shared production project is forbidden.");
    string jobFile=Environment.GetEnvironmentVariable("YAMYAM_M21_JOB");
    if(string.IsNullOrEmpty(jobFile)||!File.Exists(jobFile))throw new FileNotFoundException("YAMYAM_M21_JOB must name a reviewed job JSON.");
    job=JsonUtility.FromJson<Job>(File.ReadAllText(jobFile));
    if(!System.Text.RegularExpressions.Regex.IsMatch(job.id??"",@"^m21-[a-z0-9-]+$"))throw new InvalidDataException("Invalid scene ID");
    if(job.command!="preflight"&&job.command!="render"&&job.command!="build-only")throw new InvalidDataException("Only build-only/preflight/render are supported");
    if(Environment.GetCommandLineArgs().Contains("-nographics")&&job.command!="build-only")throw new InvalidOperationException("No-graphics process cannot capture or render");
    if(job.expectedFingerprint!=LightLabBuildVersion.Value)throw new InvalidDataException("Compiled source fingerprint differs from job");
    if(job.frames<1||job.frames>108000)throw new InvalidDataException("Invalid frame count");
    string allowed=Path.GetFullPath("D:/Github/VideoEditing/projects/game-math-shading-lights/production/").TrimEnd(Path.DirectorySeparatorChar,Path.AltDirectorySeparatorChar)+Path.DirectorySeparatorChar;
    job.output=Path.GetFullPath(job.output);
    if(!job.output.StartsWith(allowed,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Output outside M21");
    if(Directory.Exists(job.output)&&Directory.EnumerateFileSystemEntries(job.output).Any())throw new IOException("Prior result preserved; choose an empty output");
    if(job.command=="preflight"&&(job.sampleFrames==null||job.sampleFrames.Length==0||job.sampleFrames.Any(f=>f<0||f>=job.frames)))throw new InvalidDataException("Invalid sample frames");
    Directory.CreateDirectory(job.output);
    var cue=JsonUtility.FromJson<LabCue>(File.ReadAllText(job.cueFile));
    if(cue.id!=job.id)throw new InvalidDataException("Cue/job ID differs");
    if(job.command=="render" && cue.diagram!=null && (cue.diagram.StartsWith("math:")||cue.diagram.StartsWith("advanced:")) && (cue.stepTimes==null||cue.stepTimes.Length==0))throw new InvalidDataException("Production explanatory cues require actual speech-aligned stepTimes");
    state=new State{status="building",id=job.id,output=job.output,compiledFingerprint=LightLabBuildVersion.Value,unity=Application.unityVersion,total=job.frames,sourceKind=cue.sourceKind};Write();
    string assets=Root+"/Generated/"+LightLabBuildVersion.Value.Substring(0,12)+"/"+job.command+"/"+job.id;
    Directory.CreateDirectory(assets);AssetDatabase.Refresh();
    var renderer=ScriptableObject.CreateInstance<UniversalRendererData>();AssetDatabase.CreateAsset(renderer,assets+"/Renderer.asset");
    var pipeline=UniversalRenderPipelineAsset.Create(renderer);pipeline.msaaSampleCount=4;pipeline.supportsHDR=false;AssetDatabase.CreateAsset(pipeline,assets+"/URP.asset");
    GraphicsSettings.defaultRenderPipeline=pipeline;QualitySettings.renderPipeline=pipeline;
    PlayerSettings.colorSpace=ColorSpace.Linear;QualitySettings.vSyncCount=0;
    var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
    RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.09f,.09f,.09f);RenderSettings.ambientIntensity=1;
    var go=new GameObject("M21 · "+job.id);stage=go.AddComponent<LightLabStage>();stage.AdvancedComparisonFrames=job.comparisonFrames;
    // A local OS font is used only in this workstation render; no font binary is redistributed.
    var font=Font.CreateDynamicFontFromOSFont("Malgun Gothic",48);stage.Build(cue,font);
    var teachingShader=Shader.Find("Yamyam/Teaching/LocalIllumination");
    var shaderMessages=ShaderUtil.GetShaderMessages(teachingShader);
    if(shaderMessages.Any(m=>m.severity.ToString()=="Error"))throw new InvalidOperationException("Teaching shader import failed: "+string.Join("; ",shaderMessages.Select(m=>m.message)));
    var maps=CreateMaps(cue);stage.SetMaps(maps[0],maps[1]);stage.SetMaterialMaps(maps[2],maps[3]);
    foreach(var asset in stage.GeneratedObjects.Concat(maps.Cast<Object>())) {
      if(!asset||AssetDatabase.Contains(asset))continue;
      string extension=asset is Material?".mat":".asset";
      AssetDatabase.CreateAsset(asset,assets+"/"+Guid.NewGuid().ToString("N")+extension);
    }
    state.scene=Root+"/Scenes/"+LightLabBuildVersion.Value.Substring(0,12)+"/"+job.command+"/"+job.id+".unity";
    Directory.CreateDirectory(Path.GetDirectoryName(state.scene));
    if(File.Exists(state.scene))throw new IOException("Prior editable scene preserved");
    if(!EditorSceneManager.SaveScene(scene,state.scene))throw new IOException("Editable scene save failed");
    AssetDatabase.SaveAssets();
    if(job.command=="build-only"){state.completed=0;Finish(null);return;}
    if(!string.IsNullOrEmpty(cue.bakeMode)){
      var settings=new LightingSettings();settings.bakedGI=true;settings.realtimeGI=false;
      settings.lightmapper=LightingSettings.Lightmapper.UnityComputeGPU;
      settings.mixedBakeMode=MixedLightingMode.IndirectOnly;settings.lightmapResolution=20;settings.lightmapMaxSize=1024;
      settings.directSampleCount=64;settings.indirectSampleCount=128;settings.environmentSampleCount=32;
      settings.maxBounces=2;settings.minBounces=2;settings.ao=false;
      AssetDatabase.CreateAsset(settings,assets+"/LightingSettings.lighting");Lightmapping.lightingSettings=settings;
      Lightmapping.giWorkflowMode=Lightmapping.GIWorkflowMode.OnDemand;
      state.status="baking-actual-engine-lightmaps";Write();
      bool baked=Lightmapping.Bake();
      var room=stage.GetComponent<LightLabBakedRoom>();
      var proof=new BakeEvidence{backend=settings.lightmapper.ToString(),mode=cue.bakeMode,engineReturnedSuccess=baked,lightmapCount=LightmapSettings.lightmaps.Length,
        lightmappedRenderers=stage.GetComponentsInChildren<MeshRenderer>().Count(r=>r.lightmapIndex>=0&&r.lightmapIndex<LightmapSettings.lightmaps.Length),lightIsBaked=room.MainLight.bakingOutput.isBaked};
      File.WriteAllText(Path.Combine(job.output,"actual-bake.json"),JsonUtility.ToJson(proof,true));
      if(!baked||proof.lightmapCount==0||proof.lightmappedRenderers==0||!proof.lightIsBaked)throw new InvalidOperationException("No verified baked lightmaps; refuse to render a fake bake");
      room.BakeVerified=true;EditorSceneManager.SaveScene(scene,state.scene);AssetDatabase.SaveAssets();
    }
    target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32){antiAliasing=4};target.Create();
    pixels=new Texture2D(1920,1080,TextureFormat.RGBA32,false);stage.RenderCamera.targetTexture=target;
    if(job.command=="render") {
      if(!File.Exists(job.ffmpeg))throw new FileNotFoundException("An explicit FFmpeg path is required");
      var args="-hide_banner -loglevel error -n -f rawvideo -pixel_format rgba -video_size 1920x1080 -framerate 60 -i pipe:0 -vf vflip,scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p -an -c:v libx264 -preset fast -crf 17 -g 60 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart \""+Path.Combine(job.output,"unity.mp4")+"\"";
      encoder=new System.Diagnostics.Process{StartInfo=new System.Diagnostics.ProcessStartInfo(job.ffmpeg,args){UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardError=true}};
      encoder.ErrorDataReceived+=(s,e)=>{if(e.Data!=null)stderr+=e.Data+"\n";};encoder.Start();encoder.BeginErrorReadLine();pipe=encoder.StandardInput.BaseStream;
    }
    EditorApplication.LockReloadAssemblies();AssetDatabase.DisallowAutoRefresh();locked=true;
    state.status="capturing";Write();EditorApplication.update+=Tick;
   }catch(Exception e){Finish(e);}
  }
  static Texture2D[] CreateMaps(LabCue cue) {
    var gobo=new Texture2D(128,128,TextureFormat.RGBA32,false,true){name="Original smooth circular gobo",wrapMode=TextureWrapMode.Clamp};
    var falloff=new Texture2D(128,1,TextureFormat.RGBA32,false,true){name="Original symmetric falloff",wrapMode=TextureWrapMode.Clamp};
    for(int y=0;y<128;y++)for(int x=0;x<128;x++){float u=x/127f,v=y/127f;float r=Vector2.Distance(new Vector2(u,v),Vector2.one*.5f)*2;float a=Mathf.Clamp01(1-r*r);if(cue.goboKind=="fakeSpot")a=Mathf.Clamp01(1-Mathf.Abs(v-.5f)/Mathf.Max(.0001f,.45f*u))*(1-u);if(cue.goboKind=="window")a=(u>.2f&&u<.8f&&v>.2f&&v<.8f&&Mathf.Abs(u-.5f)>.035f&&Mathf.Abs(v-.5f)>.035f)?1:0;if(x==0||x==127||y==0||y==127)a=0;gobo.SetPixel(x,y,new Color(a,a,a,1));}
    for(int x=0;x<128;x++){float a=cue.falloffKind=="frontToBack"?1-x/127f:1-Mathf.Abs(x/127f*2-1);if(x==0||x==127)a=0;falloff.SetPixel(x,0,new Color(a,a,a,1));}
    var diffuse=new Texture2D(16,16,TextureFormat.RGBA32,false,true){name="Original 16x16 diffuse material map",wrapMode=TextureWrapMode.Repeat,filterMode=FilterMode.Point};
    var specular=new Texture2D(16,16,TextureFormat.RGBA32,false,true){name="Original 16x16 specular strength map",wrapMode=TextureWrapMode.Repeat,filterMode=FilterMode.Point};
    for(int y=0;y<16;y++)for(int x=0;x<16;x++){
      bool bright=((x/2+y/2)%2)==0;diffuse.SetPixel(x,y,bright?new Color(.8f,.65f,.25f):new Color(.08f,.22f,.26f));
      float strength=x<8?.15f:.85f;specular.SetPixel(x,y,new Color(strength,strength,strength));
    }
    gobo.Apply();falloff.Apply();diffuse.Apply();specular.Apply();return new[]{gobo,falloff,diffuse,specular};
  }
  static void Tick(){try{
    int frame=job.command=="preflight"?job.sampleFrames[cursor]:cursor;
    if(!prepared){stage.Apply(frame/60f);Canvas.ForceUpdateCanvases();EditorApplication.QueuePlayerLoopUpdate();prepared=true;return;}
    var request=new RenderPipeline.StandardRequest{destination=target};
    if(!RenderPipeline.SupportsRenderRequest(stage.RenderCamera,request))throw new Exception("URP full camera-stack render request unavailable");
    RenderPipeline.SubmitRenderRequest(stage.RenderCamera,request);
    var old=RenderTexture.active;RenderTexture.active=target;pixels.ReadPixels(new Rect(0,0,1920,1080),0,0);pixels.Apply(false);RenderTexture.active=old;
    if(job.command=="preflight")File.WriteAllBytes(Path.Combine(job.output,"frame-"+frame.ToString("D6")+".png"),pixels.EncodeToPNG());
    else {var bytes=pixels.GetRawTextureData<byte>().ToArray();pipe.Write(bytes,0,bytes.Length);}
    cursor++;prepared=false;state.completed=cursor;if(cursor%60==0)Write();
    if(cursor>=(job.command=="preflight"?job.sampleFrames.Length:job.frames))Finish(null);
   }catch(Exception e){Finish(e);}}
  static void Write(){if(state!=null&&Directory.Exists(state.output))File.WriteAllText(Path.Combine(state.output,"progress.json"),JsonUtility.ToJson(state,true));}
  static void Finish(Exception e){EditorApplication.update-=Tick;
    try{if(encoder!=null){pipe.Close();encoder.WaitForExit();if(encoder.ExitCode!=0)e=new Exception(stderr);encoder.Dispose();}}catch(Exception x){e=x;}
    if(e==null&&stage&&state!=null&&!string.IsNullOrEmpty(state.scene)){
      try{stage.RenderCamera.targetTexture=null;EditorSceneManager.SaveScene(stage.gameObject.scene,state.scene);AssetDatabase.SaveAssets();}catch(Exception x){e=x;}
    }
    if(state!=null){state.status=e==null?"complete":"failed";state.error=e?.ToString();Write();File.WriteAllText(Path.Combine(state.output,e==null?"capture-success.json":"capture-failure.json"),JsonUtility.ToJson(state,true));}
    if(e!=null)Debug.LogException(e);if(stage&&stage.RenderCamera)stage.RenderCamera.targetTexture=null;
    if(target){target.Release();Object.DestroyImmediate(target);}if(pixels)Object.DestroyImmediate(pixels);
    if(locked){AssetDatabase.AllowAutoRefresh();EditorApplication.UnlockReloadAssemblies();}EditorApplication.Exit(e==null?0:1);
  }
 }
}
