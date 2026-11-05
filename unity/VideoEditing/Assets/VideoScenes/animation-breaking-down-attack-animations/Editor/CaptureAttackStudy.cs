using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
namespace Yamyam.AnimationSeries {
public static class CaptureAttackStudy {
    const string SceneRoot="Assets/VideoScenes/animation-breaking-down-attack-animations/Scenes";
    static string Local => Path.GetFullPath(Path.Combine(Application.dataPath,"../../../projects/animation-breaking-down-attack-animations/production/local/grid-v1/native"));
    [Serializable] public class Sample {
        public int outputFrame,simulationFrame,freezeLeft,contactFrame;
        public bool hit,transitionAccepted;public string state;
        public Vector3 grip,tip;
    }
    [Serializable] class Trace {public int chapter,frames;public string scene,video; public List<Sample> samples=new List<Sample>();}
    static AttackStudy stage;static RenderTexture rt;static Texture2D pixels;
    static Process encoder;static int chapter=1,variant=0,cursor;static bool prepared;
    static Trace trace;const int Count=108;
    static string Key => "ch"+chapter+(chapter==5?new[]{"-early","-wait","-noinput"}[variant]:"");
    public static void Run() {
        if(!Application.isBatchMode)throw new InvalidOperationException("Dedicated batch editor required.");
        Directory.CreateDirectory(Local);Directory.CreateDirectory(SceneRoot);
        try{Start();EditorApplication.update+=Tick;}catch(Exception e){Fail(e);}
    }
    static void Start() {
        var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        var root=new GameObject("Attack study | chapter "+chapter);
        stage=root.AddComponent<AttackStudy>();stage.slug="animation-breaking-down-attack-animations";stage.chapter=chapter;
        stage.cutId="ch"+chapter;stage.frames=Count;stage.Initialize();stage.Build();
        var path=SceneRoot+"/Attack-"+chapter+".unity";
        // The three threshold variants for chapter five use the same editable scene.
        if(variant==0 && !EditorSceneManager.SaveScene(scene,path))throw new IOException(path);
        rt=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32){antiAliasing=2};rt.Create();
        pixels=new Texture2D(1920,1080,TextureFormat.RGBA32,false);
        string video=Path.Combine(Local,Key+".mp4");
        var info=new ProcessStartInfo("ffmpeg","-v error -y -f rawvideo -pix_fmt rgba -video_size 1920x1080 -framerate 60 -i pipe:0 -vf vflip,format=yuv420p -an -c:v h264_nvenc -preset p4 -cq 16 -b:v 0 -movflags +faststart \""+video+"\""){
            UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true
        };
        encoder=Process.Start(info);trace=new Trace{chapter=chapter,frames=Count,scene=path,video=video};
        cursor=0;prepared=false;
    }
    static void Tick(){
        try {
            if(!prepared){
                int f=Mathf.Max(0,cursor-18);
                stage.SetSample(f,variant==0,chapter==5 && variant!=2,chapter==3);
                trace.samples.Add(new Sample{outputFrame=cursor,simulationFrame=stage.simulationFrame,freezeLeft=stage.freezeLeft,
                    contactFrame=stage.contactFrame,hit=stage.hit,transitionAccepted=stage.released,state=stage.visibleState,grip=stage.hand.position,tip=stage.tip.position});
                prepared=true;EditorApplication.QueuePlayerLoopUpdate();return;
            }
            RenderPipeline.SubmitRenderRequest(stage.camera,new RenderPipeline.StandardRequest{destination=rt});
            var previous=RenderTexture.active;RenderTexture.active=rt;
            try{pixels.ReadPixels(new Rect(0,0,1920,1080),0,0);pixels.Apply(false);}finally{RenderTexture.active=previous;}
            var raw=pixels.GetRawTextureData<byte>();encoder.StandardInput.BaseStream.Write(raw.ToArray(),0,raw.Length);
            if(chapter==3 && (cursor==18||cursor==28||cursor==32||cursor==47||cursor==66))File.WriteAllBytes(Path.Combine(Local,"pose-"+cursor+".png"),pixels.EncodeToPNG());
            prepared=false;cursor++;
            if(cursor<Count)return;
            encoder.StandardInput.Close();encoder.WaitForExit();if(encoder.ExitCode!=0)throw new IOException("Video encoder failed.");
            File.WriteAllText(Path.Combine(Local,Key+".json"),JsonUtility.ToJson(trace,true));
            rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(pixels);
            if(chapter==5 && variant<2)variant++;else{chapter++;variant=0;}
            if(chapter<=6){Start();return;}
            EditorApplication.update-=Tick;AssetDatabase.SaveAssets();
            File.WriteAllText(Path.Combine(Local,"complete.txt"),Application.unityVersion);EditorApplication.Exit(0);
        }catch(Exception e){Fail(e);}
    }
    static void Fail(Exception e){UnityEngine.Debug.LogException(e);EditorApplication.update-=Tick;
        try{if(encoder!=null&&!encoder.HasExited)encoder.StandardInput.Close();}catch{}
        File.WriteAllText(Path.Combine(Local,"error.txt"),e.ToString());EditorApplication.Exit(1);}
}
}
