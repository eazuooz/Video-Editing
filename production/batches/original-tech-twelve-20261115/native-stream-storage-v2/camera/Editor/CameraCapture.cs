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
namespace Yamyam.OriginalTechTwelve.Camera.Editor {
    public static class CameraCapture {
        const string Root="Assets/OriginalTechTwelve/CameraV1",Asset="Assets/ThirdParty/KayKitAdventurers/";
        const int Size=1080,Fps=60,Frames=720;
        static readonly int[] Preview={0,90,150,240,330,420,510,600,660,719};
        [Serializable] public class Job{public string output,fingerprint,mode,ffmpeg;public int frameLimit;}
        [Serializable] public class Frame{public int frame;public CameraState model;public float heroScreenX,heroScreenY,landmarkScreenX,landmarkScreenY;}
        [Serializable] public class Trace{public string engine,mode,camera,fingerprint;public int fps=60;public string interpretation="Authored camera relationship illustration; not Mario64 code, geometry, input telemetry or exact game limits";public List<Frame>frames=new List<Frame>();}
        static Job job;static int Limit{get{return job.frameLimit>0?job.frameLimit:Frames;}}static LosslessFrameSink sink;static int modeIndex,cameraIndex,index;static CameraLesson demo;static Trace trace;
        static RenderTexture rt;static Texture2D pixels;static Transform landmark;
        static Material Mat(string name,Color c,Texture texture=null){string p=Root+"/Baked/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(p);if(!m){m=new Material(Shader.Find("Yamyam/ArchitecturalSurface"));AssetDatabase.CreateAsset(m,p);}m.color=c;if(texture)m.mainTexture=texture;return m;}
        static GameObject Shape(string name,PrimitiveType type,Vector3 p,Vector3 scale,Material m){var g=GameObject.CreatePrimitive(type);g.name=name;g.transform.position=p;g.transform.localScale=scale;g.GetComponent<Renderer>().sharedMaterial=m;Object.DestroyImmediate(g.GetComponent<Collider>());return g;}
        static LineRenderer Line(string name,Color c,int count,float width){var l=new GameObject(name).AddComponent<LineRenderer>();l.sharedMaterial=Mat(name,c);l.positionCount=count;l.startWidth=l.endWidth=width;l.numCapVertices=5;return l;}
        static UnityEngine.Camera View(string name,Vector3 p,Vector3 target,bool observer){var c=new GameObject(name).AddComponent<UnityEngine.Camera>();c.enabled=false;c.transform.position=p;c.transform.LookAt(target);c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=Color.black;c.aspect=1;c.nearClipPlane=.1f;c.farClipPlane=60;c.orthographic=observer;c.orthographicSize=8.5f;c.fieldOfView=55;return c;}
        public static void Run(){try{
            string[] args=Environment.GetCommandLineArgs();int j=Array.IndexOf(args,"-ot12Job");if(j<0)throw new Exception("Exact job missing");job=JsonUtility.FromJson<Job>(File.ReadAllText(args[j+1]));
            if(job.mode!="pilot"&&job.mode!="full")throw new Exception("Invalid capture mode");
            Directory.CreateDirectory(job.output);if(Directory.EnumerateFiles(job.output,"*",SearchOption.AllDirectories).Any())throw new Exception("Preserve prior capture");
            Directory.CreateDirectory(Root+"/Baked");Directory.CreateDirectory(Root+"/Scenes");modeIndex=0;Prepare();EditorApplication.update+=Tick;
        }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
        static void Prepare(){
            GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;QualitySettings.antiAliasing=4;
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            RenderSettings.skybox=null;RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=Color.white;
            var ground=Mat("ground",new Color(.045f,.075f,.08f));Shape("Ground",PrimitiveType.Cube,new Vector3(0,-.15f,0),new Vector3(24,.3f,24),ground);
            var grid=Mat("grid",new Color(.1f,.17f,.18f));for(int n=-10;n<=10;n++){Shape("Reference grid",PrimitiveType.Cube,new Vector3(n,.01f,0),new Vector3(.025f,.01f,20),grid);Shape("Reference grid",PrimitiveType.Cube,new Vector3(0,.01f,n),new Vector3(20,.01f,.025f),grid);}
            var trunk=Mat("trunk",new Color(.3f,.19f,.12f));var leaves=Mat("leaves",new Color(.22f,.4f,.3f));
            Shape("Occluding trunk",PrimitiveType.Cylinder,new Vector3(1.6f,1.1f,2.8f),new Vector3(.5f,1.1f,.5f),trunk);
            Shape("Tree crown",PrimitiveType.Sphere,new Vector3(1.6f,3.3f,2.8f),new Vector3(2.4f,2.8f,2.4f),leaves);
            landmark=Shape("Destination landmark",PrimitiveType.Cube,new Vector3(2,1.1f,6),new Vector3(.9f,.9f,.9f),Mat("landmark",new Color(1,.84f,.32f))).transform;landmark.rotation=Quaternion.Euler(25,45,25);
            Shape("High landmark",PrimitiveType.Sphere,new Vector3(-1,4.8f,5),Vector3.one*.7f,Mat("high landmark",new Color(.45f,.9f,.78f)));
            Shape("Low platform",PrimitiveType.Cube,new Vector3(0,.3f,5),new Vector3(6,.6f,2),Mat("platform",new Color(.13f,.2f,.24f)));
            var original=AssetDatabase.LoadAssetAtPath<GameObject>(Asset+"Knight.fbx");var hero=(GameObject)PrefabUtility.InstantiatePrefab(original);hero.name="Same hero";
            foreach(var t in hero.GetComponentsInChildren<Transform>(true))if(t.name.Contains("Sword")||t.name.Contains("Shield"))t.gameObject.SetActive(false);
            var animator=hero.GetComponent<Animator>();if(animator)animator.enabled=false;
            var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(Asset+"knight_texture.png");foreach(var rr in hero.GetComponentsInChildren<Renderer>(true)){rr.sharedMaterial=Mat("hero",Color.white,tex);if(rr is SkinnedMeshRenderer sk)sk.updateWhenOffscreen=true;}
            var clips=AssetDatabase.LoadAllAssetsAtPath(Asset+"Knight.fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToDictionary(c=>c.name);clips["Idle"].SampleAnimation(hero,.4f);
            var renderers=hero.GetComponentsInChildren<Renderer>();var bounds=renderers[0].bounds;foreach(var rr in renderers)bounds.Encapsulate(rr.bounds);hero.transform.localScale=Vector3.one*(1.65f/bounds.size.y);
            demo=new GameObject("Camera relationship teaching scene").AddComponent<CameraLesson>();demo.mode=CameraModel.Modes[modeIndex];demo.hero=hero.transform;demo.walk=clips["Walking_A"];demo.idle=clips["Idle"];
            demo.playerView=View("Player view",new Vector3(0,2.6f,-6),Vector3.up,false);demo.observerView=View("Observer view",new Vector3(10,12,-13),new Vector3(0,0,0),true);
            var rig=Shape("Camera position indicator",PrimitiveType.Cube,Vector3.zero,new Vector3(.6f,.4f,.7f),Mat("camera indicator",new Color(.45f,.9f,.78f)));demo.rigIndicator=rig.transform;
            demo.viewLine=Line("View direction",new Color(.45f,.9f,.78f),2,.06f);demo.orbitTrail=Line("Camera orbit path",new Color(.95f,.84f,.37f),65,.05f);demo.Apply(0);
            demo.playerView.enabled=true;demo.livePlayback=true;EditorSceneManager.SaveScene(scene,Root+"/Scenes/"+demo.mode+".unity");demo.playerView.enabled=false;demo.livePlayback=false;AssetDatabase.SaveAssets();
            if(rt)Object.DestroyImmediate(rt);if(pixels)Object.DestroyImmediate(pixels);rt=new RenderTexture(Size,Size,24,RenderTextureFormat.ARGB32){antiAliasing=4};rt.Create();pixels=new Texture2D(Size,Size,TextureFormat.RGB24,false);cameraIndex=0;BeginCamera();
        }
        static void BeginCamera(){index=0;trace=new Trace{engine=Application.unityVersion,mode=demo.mode,camera=cameraIndex==0?"player":"observer",fingerprint=job.fingerprint};Directory.CreateDirectory(Path.Combine(job.output,demo.mode,trace.camera));if(job.mode=="full")sink=new LosslessFrameSink(Path.Combine(job.output,demo.mode,trace.camera),job.ffmpeg,Size,Size,Fps,Limit);}
        static void Tick(){try{
            int f=job.mode=="full"?index:Preview[index];demo.Apply(f/(float)Fps);var cam=cameraIndex==0?demo.playerView:demo.observerView;
            demo.rigIndicator.gameObject.SetActive(cameraIndex==1);demo.viewLine.enabled=cameraIndex==1;cam.targetTexture=rt;cam.Render();var previous=RenderTexture.active;RenderTexture.active=rt;pixels.ReadPixels(new Rect(0,0,Size,Size),0,0);pixels.Apply(false);RenderTexture.active=previous;
            var hero=cam.WorldToViewportPoint(demo.hero.position+Vector3.up*.85f);var mark=cam.WorldToViewportPoint(landmark.position);trace.frames.Add(new Frame{frame=f,model=demo.current,heroScreenX=hero.x,heroScreenY=hero.y,landmarkScreenX=mark.x,landmarkScreenY=mark.y});
            if(job.mode=="full"){sink.Write(pixels,f);if(Array.IndexOf(Preview,f)>=0||f==Limit-1)File.WriteAllBytes(Path.Combine(job.output,demo.mode,trace.camera,$"reference-{f:D5}.png"),pixels.EncodeToPNG());}else File.WriteAllBytes(Path.Combine(job.output,demo.mode,trace.camera,$"{f:D5}.png"),pixels.EncodeToPNG());
            if(++index<(job.mode=="full"?Limit:Preview.Length))return;if(sink!=null){sink.Close();sink=null;}File.WriteAllText(Path.Combine(job.output,demo.mode,trace.camera,"trace.json"),JsonUtility.ToJson(trace,true));
            if(cameraIndex++==0){BeginCamera();return;}if(++modeIndex<CameraModel.Modes.Length){Prepare();return;}
            File.WriteAllText(Path.Combine(job.output,"complete.json"),"{\"fingerprint\":\""+job.fingerprint+"\",\"modes\":5,\"camerasPerMode\":2,\"framesPerCamera\":"+(job.mode=="full"?Limit:Preview.Length)+",\"actualUnityCapture\":true}");EditorApplication.update-=Tick;EditorApplication.Exit(0);
        }catch(Exception e){if(sink!=null)try{sink.Close();}catch(Exception){}EditorApplication.update-=Tick;Debug.LogException(e);EditorApplication.Exit(1);}}
    }
}
