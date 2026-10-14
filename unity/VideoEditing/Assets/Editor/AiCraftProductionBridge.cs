using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object=UnityEngine.Object;

[InitializeOnLoad]
public static class AiCraftProductionBridge
{
    static readonly string Repo=Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
    static readonly string Output=Path.Combine(Repo,"shared/output/ai-game-development-human-craft/unity-production");
    const string Scenes="Assets/VideoScenes/ai-game-development-human-craft";
    static string RequestPath=>Path.Combine(Application.dataPath,"../Library/AiCraftProduction.request");
    [Serializable] public class Request {public string command,scene;public int frames=1800;public int fps=60;public int[] sampleFrames;}
    [Serializable] public class Capture {public string scenePath,unity=Application.unityVersion,urp="17.6.0",kind="self-authored-engine-explanation";public int width=1920,height=1080,fps=60,frames;public List<AiCraftLessonScene.State> timeline=new List<AiCraftLessonScene.State>();}
    static Scene opened, previous;
    static AiCraftLessonScene lesson;
    static Request request;
    static Capture capture;
    static RenderTexture target;
    static Texture2D pixels;
    static System.Diagnostics.Process encoder;
    static Stream stream;
    static int frame;
    static bool prepared;
    static AiCraftLessonScene.State pending;
    static AiCraftProductionBridge(){EditorApplication.update+=Poll;}
    static void Poll()
    {
        if(EditorApplication.isCompiling||EditorApplication.isUpdating||lesson||!File.Exists(RequestPath))return;
        Directory.CreateDirectory(Output);
        try{
            request=JsonUtility.FromJson<Request>(File.ReadAllText(RequestPath));File.Delete(RequestPath);
            if(request.command=="build"){Build();return;}
            if(request.command!="preflight"&&request.command!="render")throw new Exception("Unknown production command");
            StartCapture();
        }catch(Exception e){File.WriteAllText(Path.Combine(Output,"error.txt"),e.ToString());Debug.LogException(e);}
    }
    static void Build()
    {
        Directory.CreateDirectory(Scenes);AssetDatabase.Refresh();
        string sheetPath="Assets/ThirdParty/KenneyTinyDungeon/tilemap_packed.png";
        var importer=(TextureImporter)AssetImporter.GetAtPath(sheetPath);importer.textureType=TextureImporterType.Default;importer.filterMode=FilterMode.Point;importer.textureCompression=TextureImporterCompression.Uncompressed;importer.mipmapEnabled=false;importer.npotScale=TextureImporterNPOTScale.None;importer.alphaIsTransparency=true;importer.SaveAndReimport();
        var old=SceneManager.GetActiveScene();
        foreach(var id in new[]{"09","17","18","23","25","28"}){
            string path=Scenes+"/"+id+"-shop.unity";
            if(File.Exists(path))continue;
            if(!AssetDatabase.CopyAsset("Assets/AiCraftShopSample/ShopSample.unity",path))throw new Exception("Could not copy sample into owned scene: "+path);
            var scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            try{
                var roots=scene.GetRootGameObjects();var go=new GameObject("Lesson execution — "+id);SceneManager.MoveGameObjectToScene(go,scene);
                var c=go.AddComponent<AiCraftLessonScene>();c.sceneId=id;
                c.hero=roots.First(x=>x.name.StartsWith("Animated customer"));c.potion=roots.First(x=>x.name=="Purchased potion");c.captureCamera=roots.Select(x=>x.GetComponent<Camera>()).First(x=>x);
                var clips=AssetDatabase.LoadAllAssetsAtPath("Assets/ThirdParty/KayKitAdventurers/Knight.fbx").OfType<AnimationClip>().ToArray();
                c.walk=clips.First(x=>x.name=="Walking_A");c.idle=clips.First(x=>x.name=="Idle");c.interact=clips.First(x=>x.name=="Interact");c.cheer=clips.First(x=>x.name=="Cheer");
                c.ApplyFrame(0);EditorSceneManager.SaveScene(scene,path);
            }finally{EditorSceneManager.CloseScene(scene,true);}
        }
        string jumpPath=Scenes+"/20-input-response.unity";
        {
            var scene=File.Exists(jumpPath)?EditorSceneManager.OpenScene(jumpPath,OpenSceneMode.Additive):EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);SceneManager.SetActiveScene(scene);
            try{
                foreach(var item in scene.GetRootGameObjects())Object.DestroyImmediate(item);
                var sheet=AssetDatabase.LoadAssetAtPath<Texture2D>(sheetPath);
                string spritePath="Assets/AiCraftProduction/PixelKnightNativeSize.asset";
                var sprite=AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
                if(!sprite){sprite=Sprite.Create(sheet,new Rect(0,32,16,16),new Vector2(.5f,0),16);AssetDatabase.CreateAsset(sprite,spritePath);}
                var go=new GameObject("Lesson execution — 20");var c=go.AddComponent<AiCraftLessonScene>();c.sceneId="20";
                var cam=new GameObject("Pixel Camera").AddComponent<Camera>();cam.orthographic=true;cam.orthographicSize=4.5f;cam.transform.position=new Vector3(0,0,-10);cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=Color.black;cam.cullingMask=1<<31;cam.enabled=false;c.captureCamera=cam;
                var left=new GameObject("Immediate response — Kenney knight");left.layer=31;var sr=left.AddComponent<SpriteRenderer>();sr.sprite=sprite;left.transform.localScale=Vector3.one*2;c.pixelHero=sr;
                var right=Object.Instantiate(left);right.name="18-frame delayed response — same sprite";c.delayedHero=right.transform;
                c.ApplyFrame(0);EditorSceneManager.SaveScene(scene,jumpPath);
            }finally{EditorSceneManager.CloseScene(scene,true);}
        }
        if(old.IsValid())SceneManager.SetActiveScene(old);
        AiCraftExtraBuilder.Build();
        var a=new AiCraftLessonScene.Wallet(100);if(a.Buy("A")!="purchased"||a.gold!=70||a.items!=1)throw new Exception("Normal transaction failed");
        if(a.Buy("A")!="duplicate-ignored"||a.gold!=70||a.items!=1)throw new Exception("Duplicate handling failed");
        if(a.Buy("B")!="purchased"||a.gold!=40||a.items!=2)throw new Exception("Distinct purchase failed");
        var b=new AiCraftLessonScene.Wallet(20);if(b.Buy("A")!="insufficient-gold"||b.gold!=20||b.items!=0)throw new Exception("Insufficient transaction changed state");
        var cfull=new AiCraftLessonScene.Wallet(100,3);if(cfull.Buy("A")!="inventory-full"||cfull.gold!=100||cfull.items!=3)throw new Exception("Full inventory changed state");
        File.WriteAllText(Path.Combine(Output,"build-status.json"),"{\"status\":\"pass\",\"savedScenes\":12,\"transactionChecks\":[\"normal\",\"insufficient\",\"full\",\"duplicate\",\"distinct\"],\"networkAndPersistence\":\"not-implemented\"}");
    }
    static void StartCapture()
    {
        string scene=Directory.GetFiles(Scenes,request.scene+"-*.unity").Single();
        string directory=Path.Combine(Output,request.scene);Directory.CreateDirectory(directory);
        string movie=Path.Combine(directory,"unity.mp4");
        if(request.command=="render"&&File.Exists(movie))throw new Exception("Preserving existing scene render");
        previous=SceneManager.GetActiveScene();opened=SceneManager.GetSceneByPath(scene);
        if(!opened.IsValid()||!opened.isLoaded)opened=EditorSceneManager.OpenScene(scene,OpenSceneMode.Additive);
        if(previous==opened)previous=SceneManager.GetSceneAt(0);
        SceneManager.SetActiveScene(opened);
        lesson=opened.GetRootGameObjects().Select(x=>x.GetComponent<AiCraftLessonScene>()).First(x=>x);lesson.durationFrames=request.frames;lesson.captureFps=request.fps;
        target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32){antiAliasing=4};target.Create();pixels=new Texture2D(1920,1080,TextureFormat.RGBA32,false);
        capture=new Capture{scenePath=scene,fps=request.fps,frames=request.frames};frame=0;prepared=false;
        if(request.command=="render"){
            var psi=new System.Diagnostics.ProcessStartInfo("ffmpeg",$"-hide_banner -loglevel error -n -f rawvideo -pixel_format rgba -video_size 1920x1080 -framerate {request.fps} -i pipe:0 -vf vflip -an -c:v libx264 -preset fast -crf 17 -pix_fmt yuv420p -movflags +faststart \"{movie}\""){UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardError=true};
            encoder=System.Diagnostics.Process.Start(psi);stream=encoder.StandardInput.BaseStream;
        }
        // A focus-triggered asset refresh must not unload an active capture.
        EditorApplication.LockReloadAssemblies();AssetDatabase.DisallowAutoRefresh();
        EditorApplication.update+=Tick;
    }
    static void Tick()
    {
        try{
            bool custom=request.sampleFrames!=null&&request.sampleFrames.Length>0;
            int f=request.command=="preflight"?(custom?request.sampleFrames[frame]:Mathf.Min(request.frames-1,frame*Mathf.Max(1,request.frames/12))):frame;
            if(!prepared){pending=lesson.ApplyFrame(f);prepared=true;EditorApplication.QueuePlayerLoopUpdate();return;}
            RenderPipeline.SubmitRenderRequest(lesson.captureCamera,new UniversalRenderPipeline.SingleCameraRequest{destination=target});
            var prior=RenderTexture.active;RenderTexture.active=target;pixels.ReadPixels(new Rect(0,0,1920,1080),0,0);pixels.Apply(false);RenderTexture.active=prior;
            string dir=Path.Combine(Output,request.scene);
            if(encoder!=null){var bytes=pixels.GetRawTextureData<byte>();stream.Write(bytes.ToArray(),0,bytes.Length);}
            if(request.command=="preflight")File.WriteAllBytes(Path.Combine(dir,$"frame-{f:D5}.png"),pixels.EncodeToPNG());
            capture.timeline.Add(pending);prepared=false;frame++;
            if(frame%60==0)File.WriteAllText(Path.Combine(dir,"progress.txt"),$"{frame}/{request.frames}");
            if(frame>=(request.command=="preflight"?(custom?request.sampleFrames.Length:12):request.frames))Finish(null);
        }catch(Exception e){Finish(e);}
    }
    static void Finish(Exception error)
    {
        EditorApplication.update-=Tick;
        if(encoder!=null){stream.Close();string e=encoder.StandardError.ReadToEnd();encoder.WaitForExit();if(encoder.ExitCode!=0)error=new Exception(e);encoder.Dispose();encoder=null;}
        string dir=Path.Combine(Output,request.scene);
        File.WriteAllText(Path.Combine(dir,request.command+"-capture.json"),JsonUtility.ToJson(capture,true));
        File.WriteAllText(Path.Combine(dir,request.command+"-status.txt"),error==null?"complete":error.ToString());
        if(target){target.Release();Object.DestroyImmediate(target);}if(pixels)Object.DestroyImmediate(pixels);
        lesson=null;if(opened.IsValid())EditorSceneManager.CloseScene(opened,true);if(previous.IsValid())SceneManager.SetActiveScene(previous);
        AssetDatabase.AllowAutoRefresh();EditorApplication.UnlockReloadAssemblies();
    }
}
