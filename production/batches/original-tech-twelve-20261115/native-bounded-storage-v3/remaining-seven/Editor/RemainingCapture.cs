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
namespace Yamyam.OriginalTechTwelve.RemainingSeven.Editor {
    public static class RemainingCapture {
        const string Root="Assets/OriginalTechTwelve/RemainingSevenV1",Asset="Assets/ThirdParty/KayKitAdventurers/";
        const int Size=1080,Fps=60,Frames=720;static readonly int[] Preview={0,76,120,144,180,240,300,420,600,719};
        [Serializable]public class Job{public string output,fingerprint,mode,ffmpeg;public int frameLimit;}
        [Serializable]public class Projection{public string id;public float x,y,z;public bool active;}
        [Serializable]public class Frame{public int frame;public State model;public List<Projection>projections=new List<Projection>();}
        [Serializable]public class Trace{public string engine,topic,mode,camera,fingerprint;public int fps=60;public string interpretation="Authored teaching rules with licensed generic actors. Not original game code, assets, collision telemetry or performance. Projections are not visibility proof.";public List<Frame>frames=new List<Frame>();}
        static Job job;static int Limit{get{return job.frameLimit>0?job.frameLimit:Frames;}}static LosslessFrameSink sink;static RemainingLesson demo;static int topicIndex,modeIndex,cameraIndex,index;static Trace trace;static RenderTexture rt;static Texture2D pixels;
        static Color ColorFor(string name){switch(name){case"hero":case"title":return new Color(1,.84f,.32f);case"relation":return new Color(.45f,.9f,.78f);case"changed":case"burning-wood":return new Color(.98f,.48f,.24f);case"result":return new Color(.4f,.85f,.5f);case"problem":return new Color(.94f,.35f,.35f);case"water":return new Color(.35f,.65f,.95f);case"wood":return new Color(.5f,.3f,.15f);case"ink":return new Color(.035f,.05f,.07f);case"dust":return new Color(.67f,.61f,.47f);case"muted":return new Color(.42f,.48f,.52f);default:return new Color(.12f,.18f,.22f);}}
        static Material Mat(string name,Color color,Texture texture=null){string path=Root+"/Baked/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Yamyam/ArchitecturalSurface"));AssetDatabase.CreateAsset(m,path);}m.color=color;if(texture)m.mainTexture=texture;return m;}
        static GameObject Shape(string name,PrimitiveType type,Material material,Transform parent=null){var g=GameObject.CreatePrimitive(type);g.name=name;if(parent)g.transform.SetParent(parent,false);g.GetComponent<Renderer>().sharedMaterial=material;Object.DestroyImmediate(g.GetComponent<Collider>());return g;}
        static GameObject Box(string name,Vector3 p,Vector3 scale,Material material,Transform parent=null){var g=Shape(name,PrimitiveType.Cube,material,parent);g.transform.localPosition=p;g.transform.localScale=scale;return g;}
        static LineRenderer Line(string name,Color color,int count,float width,Transform parent=null,bool local=false){var l=new GameObject(name).AddComponent<LineRenderer>();if(parent)l.transform.SetParent(parent,false);l.sharedMaterial=Mat("line-"+name,color);l.positionCount=count;l.startWidth=l.endWidth=width;l.numCapVertices=5;l.useWorldSpace=!local;return l;}
        static Camera View(string name,Vector3 p,Vector3 target,bool ortho,float size=8){var c=new GameObject(name).AddComponent<Camera>();c.enabled=false;c.aspect=1;c.transform.position=p;c.transform.LookAt(target);c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=Color.black;c.fieldOfView=52;c.nearClipPlane=.1f;c.farClipPlane=100;c.orthographic=ortho;c.orthographicSize=size;return c;}
        static GameObject Actor(Pose pose,RemainingLesson lesson,out Transform animation){
            animation=null;var material=Mat(pose.color,ColorFor(pose.color));GameObject g;
            if(pose.kind=="hero"){
                g=new GameObject(pose.id);var original=AssetDatabase.LoadAssetAtPath<GameObject>(Asset+"Knight.fbx");if(!original)throw new Exception("Licensed generic actor absent");
                var child=(GameObject)PrefabUtility.InstantiatePrefab(original);child.transform.SetParent(g.transform,false);animation=child.transform;
                foreach(var t in child.GetComponentsInChildren<Transform>(true))if(t.name.Contains("Sword")||t.name.Contains("Shield"))t.gameObject.SetActive(false);
                var animator=child.GetComponent<Animator>();if(animator)animator.enabled=false;
                var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(Asset+"knight_texture.png");
                foreach(var rr in child.GetComponentsInChildren<Renderer>(true)){rr.sharedMaterial=Mat("licensed actor "+pose.color,pose.id=="hero"?Color.white:new Color(.8f,.6f,.6f),texture);if(rr is SkinnedMeshRenderer sk)sk.updateWhenOffscreen=true;}
                lesson.idle.SampleAnimation(child,.4f);var rr0=child.GetComponentsInChildren<Renderer>();var bounds=rr0[0].bounds;foreach(var rr in rr0)bounds.Encapsulate(rr.bounds);child.transform.localScale=Vector3.one/Mathf.Max(.001f,bounds.size.y);
            }else if(pose.kind=="kart"){
                g=new GameObject(pose.id);Box("Own cuboid kart body",Vector3.zero,new Vector3(.8f,.32f,1.05f),material,g.transform);Box("Seat",new Vector3(0,.27f,-.08f),new Vector3(.45f,.3f,.48f),Mat("seat",ColorFor("ink")),g.transform);
                foreach(int x in new[]{-1,1})foreach(int z in new[]{-1,1}){var w=Shape("Wheel "+x+" "+z,PrimitiveType.Cylinder,Mat("tyre",ColorFor("muted")),g.transform);w.transform.localPosition=new Vector3(x*.48f,-.12f,z*.38f);w.transform.localScale=new Vector3(.36f,.1f,.36f);}
                Box("Front marker",new Vector3(0,.05f,.56f),new Vector3(.35f,.08f,.08f),Mat("front marker",ColorFor("relation")),g.transform);
            }else if(pose.kind=="portal"){
                g=new GameObject(pose.id);var l=Line(pose.id,ColorFor(pose.color),65,.08f,g.transform,true);for(int n=0;n<65;n++){float a=n/64f*Mathf.PI*2;l.SetPosition(n,new Vector3(Mathf.Cos(a),Mathf.Sin(a),0));}
            }else if(pose.kind=="wire-box"){
                g=new GameObject(pose.id);Vector3[] v={new Vector3(-.5f,-.5f,-.5f),new Vector3(.5f,-.5f,-.5f),new Vector3(.5f,.5f,-.5f),new Vector3(-.5f,.5f,-.5f),new Vector3(-.5f,-.5f,.5f),new Vector3(.5f,-.5f,.5f),new Vector3(.5f,.5f,.5f),new Vector3(-.5f,.5f,.5f)};int[,] edges={{0,1},{1,2},{2,3},{3,0},{4,5},{5,6},{6,7},{7,4},{0,4},{1,5},{2,6},{3,7}};for(int n=0;n<12;n++){var l=Line(pose.id+n,ColorFor(pose.color),2,.018f,g.transform,true);l.SetPosition(0,v[edges[n,0]]);l.SetPosition(1,v[edges[n,1]]);}
            }else g=Shape(pose.id,pose.kind=="sphere"?PrimitiveType.Sphere:PrimitiveType.Cube,material);
            g.name=pose.id;return g;
        }
        public static void Run(){try{
            var args=Environment.GetCommandLineArgs();int j=Array.IndexOf(args,"-ot12Job");if(j<0)throw new Exception("Exact job required");job=JsonUtility.FromJson<Job>(File.ReadAllText(args[j+1]));if(job.mode!="pilot"&&job.mode!="full")throw new Exception("Invalid capture mode");Directory.CreateDirectory(job.output);if(Directory.EnumerateFiles(job.output,"*",SearchOption.AllDirectories).Any())throw new Exception("Preserve prior capture");Directory.CreateDirectory(Root+"/Baked");Directory.CreateDirectory(Root+"/Scenes");topicIndex=modeIndex=0;Prepare();EditorApplication.update+=Tick;
        }catch(Exception e){Debug.LogException(e);captureEnded=true;EditorApplication.Exit(1);}}
        static void Prepare(){
            GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;QualitySettings.antiAliasing=4;var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);RenderSettings.skybox=null;RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=Color.white;
            demo=new GameObject("Authored rule comparison").AddComponent<RemainingLesson>();demo.topic=RuleModels.Topics[topicIndex];demo.mode=RuleModels.Modes[modeIndex];demo.colorNames=new[]{"hero","title","relation","changed","burning-wood","result","problem","water","wood","ink","dust","muted","structure"};demo.colors=demo.colorNames.Select(ColorFor).ToArray();
            var clips=AssetDatabase.LoadAllAssetsAtPath(Asset+"Knight.fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToDictionary(c=>c.name);demo.walk=clips["Walking_A"];demo.idle=clips["Idle"];
            var state=RuleModels.Sample(demo.topic,demo.mode,0);var actors=new List<Transform>();var animated=new List<Transform>();
            foreach(var p in state.poses){Transform animation;actors.Add(Actor(p,demo,out animation).transform);animated.Add(animation);}demo.actorIds=state.poses.Select(p=>p.id).ToArray();demo.actors=actors.ToArray();demo.animatedChildren=animated.ToArray();
            var lines=new List<LineRenderer>();foreach(var l in state.links)lines.Add(Line(l.a+" to "+l.b,ColorFor(l.color),2,l.width));demo.relationships=lines.ToArray();demo.linkA=state.links.Select(l=>l.a).ToArray();demo.linkB=state.links.Select(l=>l.b).ToArray();demo.linkColors=state.links.Select(l=>l.color).ToArray();
            if(demo.topic!="mariokart8"){Box("Context ground",new Vector3(0,demo.topic=="spiderman"?-.7f:-.18f,0),new Vector3(24,.25f,24),Mat("ground",new Color(.035f,.06f,.065f)));for(int n=-8;n<=8;n++){Box("Reference grid",new Vector3(n,.005f,0),new Vector3(.018f,.012f,16),Mat("grid",new Color(.09f,.13f,.14f)));Box("Reference grid",new Vector3(0,.005f,n),new Vector3(16,.012f,.018f),Mat("grid",new Color(.09f,.13f,.14f)));}}
            Vector3 center=new Vector3(0,1.4f,0),view=new Vector3(8,7,-11);float span=6;
            switch(demo.topic){case"spiderman":center=new Vector3(0,4.5f,0);view=new Vector3(7,7,-17);span=7;break;case"control":center=new Vector3(0,1,0);view=new Vector3(6,5,-8);span=4;break;case"returnal":center=new Vector3(0,2.2f,0);view=new Vector3(6,5,-9);span=4;break;case"ratchet":center=new Vector3(0,1.5f,1);view=new Vector3(11,9,-13);span=7;break;case"doom":center=new Vector3(1,1,-3);view=new Vector3(9,10,-13);span=7;break;case"botw":center=new Vector3(-.5f,1.2f,0);view=new Vector3(7,6,-10);span=4.5f;break;case"mariokart8":center=new Vector3(0,0,8);view=new Vector3(12,20,-8);span=16;break;}
            demo.overview=View("Overview",view,center,true,span);demo.detail=View("Detail",center+new Vector3(4,2.8f,-7),center,false);demo.Apply(0);demo.overview.enabled=true;demo.livePlayback=true;EditorSceneManager.SaveScene(scene,Root+"/Scenes/"+demo.topic+"-"+demo.mode+".unity");demo.overview.enabled=false;demo.livePlayback=false;AssetDatabase.SaveAssets();if(rt)Object.DestroyImmediate(rt);if(pixels)Object.DestroyImmediate(pixels);rt=new RenderTexture(Size,Size,24,RenderTextureFormat.ARGB32){antiAliasing=4};rt.Create();pixels=new Texture2D(Size,Size,TextureFormat.RGB24,false);cameraIndex=0;BeginCamera();
        }
        static void BeginCamera(){index=0;trace=new Trace{engine=Application.unityVersion,topic=demo.topic,mode=demo.mode,camera=cameraIndex==0?"overview":"detail",fingerprint=job.fingerprint};Directory.CreateDirectory(Path.Combine(job.output,demo.topic,demo.mode,trace.camera));if(job.mode=="full")sink=new LosslessFrameSink(Path.Combine(job.output,demo.topic,demo.mode,trace.camera),job.ffmpeg,Size,Size,Fps,Limit);}
        static bool captureEnded;
        static void Tick(){for(int n=0;n<8&&!captureEnded;n++)CaptureStep();}
        static void CaptureStep(){try{
            int frame=job.mode=="full"?index:Preview[index];demo.Apply(frame);var camera=cameraIndex==0?demo.overview:demo.detail;camera.targetTexture=rt;camera.Render();var previous=RenderTexture.active;RenderTexture.active=rt;pixels.ReadPixels(new Rect(0,0,Size,Size),0,0);pixels.Apply(false);RenderTexture.active=previous;var row=new Frame{frame=frame,model=demo.current};foreach(var actor in demo.actors){var p=camera.WorldToViewportPoint(actor.position);row.projections.Add(new Projection{id=actor.name,x=p.x,y=p.y,z=p.z,active=actor.gameObject.activeSelf});}trace.frames.Add(row);if(job.mode=="full"){sink.Write(pixels,frame);if(Array.IndexOf(Preview,frame)>=0||frame==Limit-1)File.WriteAllBytes(Path.Combine(job.output,demo.topic,demo.mode,trace.camera,$"reference-{frame:D5}.png"),pixels.EncodeToPNG());}else File.WriteAllBytes(Path.Combine(job.output,demo.topic,demo.mode,trace.camera,$"{frame:D5}.png"),pixels.EncodeToPNG());if(++index<(job.mode=="full"?Limit:Preview.Length))return;if(sink!=null){sink.Close();sink=null;}File.WriteAllText(Path.Combine(job.output,demo.topic,demo.mode,trace.camera,"trace.json"),JsonUtility.ToJson(trace,true));if(cameraIndex++==0){BeginCamera();return;}if(++modeIndex<RuleModels.Modes.Length){Prepare();return;}modeIndex=0;if(++topicIndex<RuleModels.Topics.Length){Prepare();return;}File.WriteAllText(Path.Combine(job.output,"complete.json"),"{\"fingerprint\":\""+job.fingerprint+"\",\"topics\":7,\"modesPerTopic\":2,\"camerasPerMode\":2,\"framesPerCamera\":"+(job.mode=="full"?Limit:Preview.Length)+",\"actualUnityCapture\":true}");EditorApplication.update-=Tick;captureEnded=true;EditorApplication.Exit(0);
        }catch(Exception e){if(sink!=null)try{sink.Close();}catch(Exception){}EditorApplication.update-=Tick;Debug.LogException(e);captureEnded=true;EditorApplication.Exit(1);}}
    }
}
