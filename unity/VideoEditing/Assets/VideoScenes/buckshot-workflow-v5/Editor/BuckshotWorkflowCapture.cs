using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace Yamyam.BuckshotWorkflowV5 {
[InitializeOnLoad]
public static class BuckshotWorkflowCapture {
    static readonly string Root = Path.GetFullPath(Application.dataPath + "/../../..");
    static readonly string Media = Path.Combine(Root, "projects/buckshot-roulette-reverse-engineering/production/local/unity-v5");
    static string Request => Path.GetFullPath(Application.dataPath + "/../Library/BuckshotWorkflowV5.request.json");
    static string Status => Path.GetFullPath(Application.dataPath + "/../Library/BuckshotWorkflowV5.status.json");
    [Serializable] public class Job { public string command, id, mode, output, config, expectedFingerprint,jobToken; public int frames; public int[] sampleFrames; }
    [Serializable] class State { public string status,id,mode,output,scene,error,jobToken,unity=Application.unityVersion,fingerprint,assembly; public int completed,frames; }
    static Job job; static State state; static Scene scene, prior; static BuckshotWorkflowStage stage;
    static RenderTexture target; static Texture2D pixels; static System.Diagnostics.Process encoder;
    static Stream stream; static int cursor; static bool prepared,locked; static string errors="";
    static double lastRefresh;
    static BuckshotWorkflowCapture() { EditorApplication.update += Poll; }
    static void Poll() {
        if(job!=null || EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode || !File.Exists(Request)) return;
        Job j=null;
        try {
            j=JsonUtility.FromJson<Job>(File.ReadAllText(Request));
            if(j.expectedFingerprint!=BuckshotWorkflowBuildVersion.Value) {
                // A request prepared outside the editor may precede its domain
                // reload. Refresh only while idle; never interrupt a capture.
                if(EditorApplication.timeSinceStartup-lastRefresh>5) {lastRefresh=EditorApplication.timeSinceStartup;AssetDatabase.Refresh();}
                return;
            }
            File.Move(Request,Request+".consumed-"+DateTime.UtcNow.ToString("yyyyMMddHHmmssfff"));
            Start(j);
        } catch(Exception e) {
            if(job!=null) Finish(e);
            else {state=new State{status="rejected",id=j?.id,jobToken=j?.jobToken,fingerprint=BuckshotWorkflowBuildVersion.Value,error=e.ToString()};Write();}
        }
    }
    static void Start(Job j) {
        if(j.command!="preflight" && j.command!="render") throw new Exception("Unknown capture command");
        if(!System.Text.RegularExpressions.Regex.IsMatch(j.id??"",@"^(v4-(01-02|02-01|02-02|08-01)|b04-02-p01|b05-02-p02|b23-06-p01|b24-06-p02)$")) throw new Exception("Unknown selected cut");
        string expectedMode=j.id=="v4-01-02"?"workflow":j.id=="v4-02-01"?"rea":j.id=="v4-02-02"?"tools":j.id=="b04-02-p01"?"inventory":j.id=="b05-02-p02"?"trace":j.id=="b23-06-p01"?"implement":j.id=="b24-06-p02"?"tests":"recap";
        if(j.mode!=expectedMode) throw new Exception("Cut/mode mismatch");
        if(!Path.GetFullPath(j.config).Equals(Path.GetFullPath(Path.Combine(Media,j.id,"config.json")),StringComparison.OrdinalIgnoreCase)) throw new Exception("Configuration outside selected cut");
        var resolved=Path.GetFullPath(j.output); var allowed=Path.GetFullPath(Media)+Path.DirectorySeparatorChar;
        if(!resolved.StartsWith(allowed,StringComparison.OrdinalIgnoreCase)) throw new Exception("Output outside selected video");
        if(j.frames<1 || j.frames>3600) throw new Exception("Invalid frame count");
        if(Directory.Exists(resolved) && (File.Exists(Path.Combine(resolved,"progress.json")) || Directory.GetFiles(resolved,"frame-*.png").Length>0 || File.Exists(Path.Combine(resolved,"unity.mp4")))) throw new Exception("Existing capture or partial result preserved");
        if(j.command=="preflight" && (j.sampleFrames==null || j.sampleFrames.Length==0)) throw new Exception("Missing samples");
        Directory.CreateDirectory(resolved); job=j;
        state=new State{status="building",id=j.id,mode=j.mode,output=resolved,frames=j.frames,jobToken=j.jobToken,fingerprint=BuckshotWorkflowBuildVersion.Value,assembly=typeof(BuckshotWorkflowStage).Assembly.ManifestModule.ModuleVersionId.ToString()}; Write();
        prior=SceneManager.GetActiveScene(); scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
        ulong isolatedMask=EditorSceneManager.CalculateAvailableSceneCullingMask();
        if(isolatedMask==0) throw new Exception("No unused scene-culling bit available");
        EditorSceneManager.SetSceneCullingMask(scene,isolatedMask); SceneManager.SetActiveScene(scene);
        var go=new GameObject("Buckshot workflow / "+j.mode); SceneManager.MoveGameObjectToScene(go,scene);
        stage=go.AddComponent<BuckshotWorkflowStage>(); stage.Initialize(j.mode,j.frames,j.config);
        // The Core package's own opt-out component calls Unity's internal
        // renderer switch. Apply it only to our generated meshes, not globally.
        var optOut=typeof(GPUResidentDrawer).Assembly.GetType("UnityEngine.Rendering.DisallowGPUDrivenRendering");
        if(optOut==null) throw new Exception("Core renderer opt-out component unavailable");
        foreach(var mesh in stage.GetComponentsInChildren<MeshRenderer>(true)) mesh.gameObject.AddComponent(optOut);
        stage.RenderCamera.overrideSceneCullingMask=isolatedMask;
        target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32){antiAliasing=4}; target.Create();
        pixels=new Texture2D(1920,1080,TextureFormat.RGBA32,false); stage.RenderCamera.targetTexture=target;
        stage.Apply(0); Canvas.ForceUpdateCanvases();
        for(int n=0;n<SceneManager.sceneCount;n++) {
            var other=SceneManager.GetSceneAt(n);
            if(other!=scene && other.isLoaded && (EditorSceneManager.GetSceneCullingMask(other)&isolatedMask)!=0) throw new Exception("Scene-culling mask overlap");
        }
        state.scene="Assets/VideoScenes/buckshot-workflow-v5/Scenes/"+j.expectedFingerprint.Substring(0,12)+"/"+j.command+"/"+j.id+".unity";
        Directory.CreateDirectory(Path.GetDirectoryName(state.scene));
        if(File.Exists(state.scene)) throw new Exception("Prior editable scene preserved");
        if(!EditorSceneManager.SaveScene(scene,state.scene)) throw new Exception("Scene save failed");
        File.WriteAllText(Path.Combine(resolved,"scene-culling-mask.txt"),isolatedMask.ToString());
        cursor=0; prepared=false;
        if(j.command=="render") {
            string movie=Path.Combine(resolved,"unity.mp4"); if(File.Exists(movie)) throw new Exception("Existing movie preserved");
            string ffmpeg="C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe";
            var ps=new System.Diagnostics.ProcessStartInfo(ffmpeg,"-hide_banner -loglevel error -n -f rawvideo -pixel_format rgba -video_size 1920x1080 -framerate 60 -i pipe:0 -vf vflip,scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p -an -c:v h264_nvenc -preset p4 -rc constqp -qp 18 -bf 2 -g 60 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart \""+movie+"\"") {UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardError=true};
            encoder=new System.Diagnostics.Process{StartInfo=ps}; encoder.ErrorDataReceived+=(s,a)=>{if(a.Data!=null)errors+=a.Data+"\n";}; encoder.Start(); encoder.BeginErrorReadLine(); stream=encoder.StandardInput.BaseStream;
        }
        EditorApplication.LockReloadAssemblies(); AssetDatabase.DisallowAutoRefresh(); locked=true;
        state.status="capturing"; Write(); EditorApplication.update+=Tick;
    }
    static void Tick() { try {
        int f=job.command=="preflight"?job.sampleFrames[cursor]:cursor;
        if(f<0 || f>=job.frames) throw new Exception("Sample outside timeline");
        if(!prepared) { stage.Apply(f/60f); Canvas.ForceUpdateCanvases(); EditorApplication.QueuePlayerLoopUpdate(); prepared=true; return; }
        var request=new RenderPipeline.StandardRequest{destination=target};
        if(!RenderPipeline.SupportsRenderRequest(stage.RenderCamera,request)) throw new Exception("URP StandardRequest is required for isolated timeline capture");
        RenderPipeline.SubmitRenderRequest(stage.RenderCamera,request);
        var old=RenderTexture.active; RenderTexture.active=target; pixels.ReadPixels(new Rect(0,0,1920,1080),0,0); pixels.Apply(false); RenderTexture.active=old;
        if(encoder!=null) { var data=pixels.GetRawTextureData<byte>(); stream.Write(data.ToArray(),0,data.Length); }
        if(job.command=="preflight") File.WriteAllBytes(Path.Combine(state.output,"frame-"+f.ToString("D5")+".png"),pixels.EncodeToPNG());
        cursor++; prepared=false; state.completed=cursor; if(cursor%120==0) Write();
        if(cursor >= (job.command=="preflight"?job.sampleFrames.Length:job.frames)) Finish(null);
    } catch(Exception e) { Finish(e); } }
    static void Atomic(string path,string text) {
        var temp=path+"."+Guid.NewGuid().ToString("N")+".tmp"; File.WriteAllText(temp,text);
        // Windows status readers can briefly hold the destination without
        // FILE_SHARE_DELETE. Retry the atomic rename without losing frames.
        for(int attempt=0;;attempt++) {
            try { if(File.Exists(path))File.Replace(temp,path,null);else File.Move(temp,path); return; }
            catch(IOException) { if(attempt>=39)throw; System.Threading.Thread.Sleep(25); }
        }
    }
    static void Write() { Atomic(Status,JsonUtility.ToJson(state,true)); if(job!=null)Atomic(Path.Combine(state.output,"progress.json"),JsonUtility.ToJson(state,true)); }
    static void Finish(Exception e) {
        EditorApplication.update-=Tick;
        try { if(encoder!=null) { stream.Close(); encoder.WaitForExit(); if(encoder.ExitCode!=0)e=new Exception(errors); encoder.Dispose(); encoder=null; } } catch(Exception x) {e=x;}
        if(state==null)state=new State(); state.status=e==null?"complete":"failed"; state.error=e?.ToString();
        try { Write(); if(job!=null)Atomic(Path.Combine(state.output,job.command+(e==null?"-success":"-failure")+".json"),JsonUtility.ToJson(state,true)); } catch {}
        if(stage && stage.RenderCamera)stage.RenderCamera.targetTexture=null;
        if(target){target.Release();Object.DestroyImmediate(target);} if(pixels)Object.DestroyImmediate(pixels); stage=null;
        if(scene.IsValid() && scene.isLoaded)EditorSceneManager.CloseScene(scene,true);
        if(prior.IsValid() && prior.isLoaded)SceneManager.SetActiveScene(prior);
        if(locked){AssetDatabase.AllowAutoRefresh();EditorApplication.UnlockReloadAssemblies();locked=false;}
        job=null; errors="";
    }
}
}
