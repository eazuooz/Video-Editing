using Yamyam.OriginalTechTwelve.CaptureStorageV2;
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using Object=UnityEngine.Object;

namespace Yamyam.OriginalTechTwelve.LockOn.Editor {
    public static class LockOnCapture {
        const string Root="Assets/OriginalTechTwelve/LockOnV1",Asset="Assets/ThirdParty/KayKitAdventurers/";
        const int Size=1080,Fps=60,Frames=720;
        [Serializable] public class Job {public string output,fingerprint,mode,ffmpeg;public int frameLimit;}
        [Serializable] public class Frame {public int frame;public State model;public float heroScreenX,heroScreenY,targetScreenX,targetScreenY;}
        [Serializable] public class Trace {public string engine,mode,camera,fingerprint;public int fps=Fps;public string interpretation="Own deterministic teaching model; not Nintendo code, AI, input telemetry or damage";public List<Frame>frames=new List<Frame>();}
        static Job job;static int Limit{get{return job.frameLimit>0?job.frameLimit:Frames;}}static LosslessFrameSink sink;static int modeIndex,index,cameraIndex;static string[]modes;
        static LockOnPresentation demo;static Dictionary<string,AnimationClip>clips;
        static RenderTexture rt;static Texture2D pixels;static Trace trace;
        static readonly int[] Preview={0,60,150,240,360,420,510,570,660,719};
        static Material Mat(string name,Color color,Texture texture=null){
            string path=Root+"/Baked/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(!m){m=new Material(Shader.Find("Yamyam/ArchitecturalSurface"));AssetDatabase.CreateAsset(m,path);}
            m.color=color;if(texture)m.mainTexture=texture;return m;
        }
        static GameObject Block(string name,Vector3 p,Vector3 size,Material m){var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name=name;g.transform.position=p;g.transform.localScale=size;g.GetComponent<Renderer>().sharedMaterial=m;Object.DestroyImmediate(g.GetComponent<Collider>());return g;}
        static GameObject Actor(string name,Material material){
            var original=AssetDatabase.LoadAssetAtPath<GameObject>(Asset+"Knight.fbx");if(!original)throw new Exception("Missing licensed Knight");
            var g=(GameObject)PrefabUtility.InstantiatePrefab(original);g.name=name;
            foreach(var t in g.GetComponentsInChildren<Transform>(true))if(t.name.Contains("Sword")||t.name.Contains("Shield"))t.gameObject.SetActive(false);
            var animator=g.GetComponent<Animator>();if(animator)animator.enabled=false;
            foreach(var renderer in g.GetComponentsInChildren<Renderer>(true)){renderer.sharedMaterial=material;if(renderer is SkinnedMeshRenderer sk){sk.updateWhenOffscreen=true;sk.forceMatrixRecalculationPerRender=true;}}
            clips["Idle"].SampleAnimation(g,.4f);var rr=g.GetComponentsInChildren<Renderer>();var bounds=rr[0].bounds;foreach(var a in rr)bounds.Encapsulate(a.bounds);
            g.transform.localScale=Vector3.one*(1.65f/bounds.size.y);
            return g;
        }
        static LineRenderer Line(string name,Color c,int points,float width){var g=new GameObject(name);var line=g.AddComponent<LineRenderer>();line.sharedMaterial=Mat(name,c);line.positionCount=points;line.startWidth=line.endWidth=width;line.useWorldSpace=true;line.numCapVertices=5;return line;}
        static Camera Camera(string name,Vector3 p,Vector3 target,bool ortho){var c=new GameObject(name).AddComponent<Camera>();c.enabled=false;c.transform.position=p;c.transform.LookAt(target);c.backgroundColor=Color.black;c.clearFlags=CameraClearFlags.SolidColor;c.aspect=1;c.nearClipPlane=.1f;c.farClipPlane=50;c.fieldOfView=52;c.orthographic=ortho;c.orthographicSize=6;return c;}
        public static void Run(){try{
            var args=Environment.GetCommandLineArgs();int flag=Array.IndexOf(args,"-ot12Job");if(flag<0||flag+1>=args.Length)throw new Exception("Exact job argument required");
            job=JsonUtility.FromJson<Job>(File.ReadAllText(args[flag+1]));if(job==null||string.IsNullOrEmpty(job.fingerprint))throw new Exception("No fingerprint");
            if(job.mode!="pilot"&&job.mode!="full")throw new Exception("Choose pilot or full");
            Directory.CreateDirectory(job.output);if(Directory.EnumerateFiles(job.output,"*",SearchOption.AllDirectories).Any())throw new Exception("Preserve existing output");
            Directory.CreateDirectory(Root+"/Baked");Directory.CreateDirectory(Root+"/Scenes");
            clips=AssetDatabase.LoadAllAssetsAtPath(Asset+"Knight.fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToDictionary(c=>c.name);
            if(!clips.ContainsKey("Idle")||!clips.ContainsKey("Walking_A"))throw new Exception("Exact approved animation clips absent");
            modes=Model.Modes;modeIndex=0;Prepare();EditorApplication.update+=Tick;
        }catch(Exception e){Debug.LogException(e);captureEnded=true;EditorApplication.Exit(1);}}
        static void Prepare(){
            GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;QualitySettings.antiAliasing=4;
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            RenderSettings.skybox=null;RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=Color.white;
            Block("Same arena",new Vector3(0,-.14f,-.3f),new Vector3(12,.25f,12),Mat("floor",new Color(.045f,.07f,.08f)));
            var grid=Mat("grid",new Color(.11f,.16f,.18f));for(int k=-5;k<=5;k++){Block("X reference",new Vector3(k,.005f,0),new Vector3(.025f,.012f,10),grid);Block("Z reference",new Vector3(0,.005f,k),new Vector3(10,.012f,.025f),grid);}
            var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(Asset+"knight_texture.png");
            var heroMat=Mat("hero",Color.white,texture);var aMat=Mat("enemyA",Color.white,texture);var bMat=Mat("enemyB",Color.white,texture);
            var hero=Actor("Player model",heroMat);var a=Actor("Opponent A model",aMat);var b=Actor("Opponent B model",bMat);
            demo=new GameObject("Explicit target relationship model").AddComponent<LockOnPresentation>();demo.mode=modes[modeIndex];demo.hero=hero.transform;demo.enemyA=a.transform;demo.enemyB=b.transform;
            demo.enemyAMaterial=aMat;demo.enemyBMaterial=bMat;demo.idle=clips["Idle"];demo.walk=clips["Walking_A"];
            demo.link=Line("Target link",new Color(.45f,.9f,.78f),2,.055f);demo.facing=Line("Player facing",new Color(.95f,.86f,.47f),2,.08f);demo.ring=Line("Selected target",new Color(.45f,.9f,.78f),65,.055f);
            demo.playerView=Camera("Player viewpoint",new Vector3(0,2.5f,-10),Vector3.zero,false);demo.observerView=Camera("Observer viewpoint",new Vector3(7,9,-10),new Vector3(0,.2f,-1),true);
            demo.Initialize();demo.livePlayback=true;demo.playerView.enabled=true;EditorSceneManager.SaveScene(scene,Root+"/Scenes/"+demo.mode+".unity");demo.livePlayback=false;demo.playerView.enabled=false;AssetDatabase.SaveAssets();
            if(rt)Object.DestroyImmediate(rt);if(pixels)Object.DestroyImmediate(pixels);
            rt=new RenderTexture(Size,Size,24,RenderTextureFormat.ARGB32){antiAliasing=4};rt.Create();pixels=new Texture2D(Size,Size,TextureFormat.RGB24,false);
            cameraIndex=0;BeginCamera();
        }
        static void BeginCamera(){index=0;trace=new Trace{engine=Application.unityVersion,mode=demo.mode,camera=cameraIndex==0?"player":"observer",fingerprint=job.fingerprint};Directory.CreateDirectory(Path.Combine(job.output,demo.mode,trace.camera));if(job.mode=="full")sink=new LosslessFrameSink(Path.Combine(job.output,demo.mode,trace.camera),job.ffmpeg,Size,Size,Fps,Limit);}
        static bool captureEnded;
        static void Tick(){for(int n=0;n<8&&!captureEnded;n++)CaptureStep();}
        static void CaptureStep(){try{
            int f=job.mode=="full"?index:Preview[index];demo.Apply(f/(float)Fps);
            var cam=cameraIndex==0?demo.playerView:demo.observerView;cam.targetTexture=rt;cam.Render();var before=RenderTexture.active;RenderTexture.active=rt;pixels.ReadPixels(new Rect(0,0,Size,Size),0,0);pixels.Apply(false);RenderTexture.active=before;
            var hero=cam.WorldToViewportPoint(demo.hero.position+Vector3.up*.9f);var target=cam.WorldToViewportPoint((demo.current.selectedEnemy==0?demo.enemyA:demo.enemyB).position+Vector3.up*.9f);
            trace.frames.Add(new Frame{frame=f,model=demo.current,heroScreenX=hero.x,heroScreenY=hero.y,targetScreenX=target.x,targetScreenY=target.y});
            if(job.mode=="full"){sink.Write(pixels,f);if(Array.IndexOf(Preview,f)>=0||f==Limit-1)File.WriteAllBytes(Path.Combine(job.output,demo.mode,trace.camera,$"reference-{f:D5}.png"),pixels.EncodeToPNG());}else File.WriteAllBytes(Path.Combine(job.output,demo.mode,trace.camera,$"{f:D5}.png"),pixels.EncodeToPNG());index++;
            if(index<(job.mode=="full"?Limit:Preview.Length))return;
            if(sink!=null){sink.Close();sink=null;}File.WriteAllText(Path.Combine(job.output,demo.mode,trace.camera,"trace.json"),JsonUtility.ToJson(trace,true));
            if(cameraIndex++==0){BeginCamera();return;}
            if(++modeIndex<modes.Length){Prepare();return;}
            File.WriteAllText(Path.Combine(job.output,"complete.json"),"{\"fingerprint\":\""+job.fingerprint+"\",\"modes\":4,\"camerasPerMode\":2,\"framesPerCamera\":"+(job.mode=="full"?Limit:Preview.Length)+",\"actualUnityCapture\":true}");
            EditorApplication.update-=Tick;captureEnded=true;EditorApplication.Exit(0);
        }catch(Exception e){if(sink!=null)try{sink.Close();}catch(Exception){}EditorApplication.update-=Tick;Debug.LogException(e);captureEnded=true;EditorApplication.Exit(1);}}
    }
}
