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
namespace Yamyam.OriginalTechTwelve.Temporal.Editor {
    public static class TemporalCapture {
        const string Root="Assets/OriginalTechTwelve/TemporalV1";
        const int Internal=540,Size=1080,Fps=60,Frames=720;
        static readonly int[] Preview={0,90,150,240,330,420,510,600,660,719};
        [Serializable] public class Job{public string output,fingerprint,mode,ffmpeg;public int frameLimit;}
        [Serializable] public class Frame{public int frame,historyFrameIndex,jitterIndex;public TemporalState model;public Vector4 actualJitter;public bool velocityBufferAvailable;public float previousObjectX,currentObjectX;}
        [Serializable] public class Trace{public string engine,mode,camera,fingerprint;public int fps=60,internalRenderWidth=Internal,presentationWidth=Size;public bool everyHistoryFrameRendered=true;public string interpretation="Our synthetic test geometry using the licensed published Playdead temporal renderer. Not INSIDE settings, game buffers, resolution or a performance test.540px test image enlarged2x with point sampling.";public List<Frame>frames=new List<Frame>();}
        static Job job;static int Limit{get{return job.frameLimit>0?job.frameLimit:Frames;}}static LosslessFrameSink[] sinks;static TemporalLesson demo;static VelocityBufferTag tag;static Trace[] traces;static int modeIndex,index;
        static RenderTexture[] targets;static RenderTexture presentation;static Texture2D pixels;
        static Material Mat(string name,Color color){string path=Root+"/Baked/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){var shader=Shader.Find("Standard");if(!shader)throw new Exception("Built-in depth-capable material missing");m=new Material(shader);AssetDatabase.CreateAsset(m,path);}m.color=color;m.SetFloat("_Glossiness",0);return m;}
        static GameObject Block(string name,Vector3 p,Vector3 size,Material material){var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name=name;g.transform.position=p;g.transform.localScale=size;g.GetComponent<Renderer>().sharedMaterial=material;Object.DestroyImmediate(g.GetComponent<Collider>());return g;}
        static Camera View(string name,float fov,string mode){
            var c=new GameObject(name).AddComponent<Camera>();c.enabled=false;c.aspect=1;c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=new Color(.025f,.03f,.04f);c.fieldOfView=fov;c.nearClipPlane=.1f;c.farClipPlane=40;c.allowMSAA=false;c.allowHDR=false;c.depthTextureMode=DepthTextureMode.Depth;
            if(mode=="jitter-only"||mode=="temporal-clipping"){var j=c.gameObject.AddComponent<FrustumJitter>();j.pattern=FrustumJitter.Pattern.Halton_2_3_X8;j.patternScale=1;}
            if(mode=="naive-history-overlay"){var blend=c.gameObject.AddComponent<NaiveHistoryBlend>();blend.shader=Shader.Find("Hidden/Yamyam/NaiveHistory");if(!blend.shader||ShaderUtil.ShaderHasError(blend.shader))throw new Exception("Naive-history shader failed compilation");}
            if(mode=="temporal-clipping"){
                var velocity=c.gameObject.AddComponent<VelocityBuffer>();velocity.velocityShader=Shader.Find("Playdead/Post/VelocityBuffer");
                var temporal=c.gameObject.AddComponent<TemporalReprojection>();temporal.reprojectionShader=Shader.Find("Playdead/Post/TemporalReprojection");temporal.useYCoCg=false;temporal.useClipping=true;temporal.useMotionBlur=false;
                if(!velocity.velocityShader||!temporal.reprojectionShader||ShaderUtil.ShaderHasError(velocity.velocityShader)||ShaderUtil.ShaderHasError(temporal.reprojectionShader))throw new Exception("Published temporal shader compilation failed");
            }
            return c;
        }
        public static void Run(){try{
            var args=Environment.GetCommandLineArgs();int j=Array.IndexOf(args,"-ot12Job");if(j<0)throw new Exception("Exact job required");job=JsonUtility.FromJson<Job>(File.ReadAllText(args[j+1]));if(job.mode!="pilot"&&job.mode!="full")throw new Exception("Invalid capture mode");Directory.CreateDirectory(job.output);if(Directory.EnumerateFiles(job.output,"*",SearchOption.AllDirectories).Any())throw new Exception("Preserve prior attempt");Directory.CreateDirectory(Root+"/Baked");Directory.CreateDirectory(Root+"/Scenes");modeIndex=0;Prepare();EditorApplication.update+=Tick;
        }catch(Exception e){Debug.LogException(e);captureEnded=true;EditorApplication.Exit(1);}}
        static void Prepare(){
            GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;QualitySettings.antiAliasing=0;var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);RenderSettings.skybox=null;RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=Color.white;
            var lamp=new GameObject("Constant test light").AddComponent<Light>();lamp.type=LightType.Directional;lamp.intensity=.5f;lamp.transform.rotation=Quaternion.Euler(40,-25,0);lamp.shadows=LightShadows.None;
            Block("Floor",new Vector3(0,-.12f,3),new Vector3(16,.2f,18),Mat("floor",new Color(.06f,.08f,.1f)));
            var white=Mat("thin edges",new Color(.82f,.86f,.9f));for(int n=-15;n<=15;n++){var g=Block("Fine edge "+n,new Vector3(n*.21f,1.65f,2.5f),new Vector3(.018f,3.3f,.06f),white);if(n%3==0)g.transform.rotation=Quaternion.Euler(0,0,25);}
            Block("Background patch",new Vector3(.7f,1.5f,3),new Vector3(1.8f,2.7f,.15f),Mat("background patch",new Color(.2f,.55f,.58f)));
            var cube=Block("Moving occluder",new Vector3(0,1.5f,-.7f),new Vector3(.75f,2.8f,.6f),Mat("occluder",new Color(.78f,.18f,.13f)));tag=cube.AddComponent<VelocityBufferTag>();tag.captureDriven=false;
            demo=new GameObject("Temporal test motion").AddComponent<TemporalLesson>();demo.mode=TemporalSceneModel.Modes[modeIndex];demo.occluder=cube.transform;demo.fullView=View("Full test view",52,demo.mode);demo.detailView=View("Edge detail view",30,demo.mode);demo.fullView.tag="MainCamera";demo.Apply(0);demo.livePlayback=true;demo.fullView.enabled=true;EditorSceneManager.SaveScene(scene,Root+"/Scenes/"+demo.mode+".unity");demo.fullView.enabled=false;demo.livePlayback=false;tag.captureDriven=true;AssetDatabase.SaveAssets();
            if(targets!=null)foreach(var target in targets)if(target)Object.DestroyImmediate(target);targets=new RenderTexture[2];traces=new Trace[2];sinks=new LosslessFrameSink[2];
            for(int i=0;i<2;i++){targets[i]=new RenderTexture(Internal,Internal,24,RenderTextureFormat.ARGB32){antiAliasing=1,filterMode=FilterMode.Point};targets[i].Create();traces[i]=new Trace{engine=Application.unityVersion,mode=demo.mode,camera=i==0?"full":"detail",fingerprint=job.fingerprint};Directory.CreateDirectory(Path.Combine(job.output,demo.mode,traces[i].camera));if(job.mode=="full")sinks[i]=new LosslessFrameSink(Path.Combine(job.output,demo.mode,traces[i].camera),job.ffmpeg,Size,Size,Fps,Limit);}
            if(presentation)Object.DestroyImmediate(presentation);if(pixels)Object.DestroyImmediate(pixels);presentation=new RenderTexture(Size,Size,0,RenderTextureFormat.ARGB32){filterMode=FilterMode.Point};presentation.Create();pixels=new Texture2D(Size,Size,TextureFormat.RGB24,false);index=0;
        }
        static bool captureEnded;
        static void Tick(){for(int n=0;n<8&&!captureEnded;n++)CaptureStep();}
        static void CaptureStep(){try{
            // A temporal effect cannot jump between sparse pilot timestamps.
            // Advance every requested state and both camera histories; only
            // PNG saving is sparse in pilot mode.
            demo.Apply(index/(float)Fps);tag.CaptureStep(index==0);var cameras=new[]{demo.fullView,demo.detailView};
            for(int c=0;c<2;c++){
                cameras[c].targetTexture=targets[c];cameras[c].Render();var jitter=cameras[c].GetComponent<FrustumJitter>();var velocity=cameras[c].GetComponent<VelocityBuffer>();
                if(jitter&&index>1&&jitter.activeIndex<0)throw new Exception("Actual jitter callback did not advance");if(velocity&&index>1&&!velocity.activeVelocityBuffer)throw new Exception("Actual velocity buffer was not produced");
                traces[c].frames.Add(new Frame{frame=index,historyFrameIndex=index,model=demo.current,jitterIndex=jitter?jitter.activeIndex:-1,actualJitter=jitter?jitter.activeSample:Vector4.zero,velocityBufferAvailable=velocity&&velocity.activeVelocityBuffer,previousObjectX=tag.localToWorldPrev.m03,currentObjectX=tag.localToWorldCurr.m03});
                if(job.mode=="full"||Array.IndexOf(Preview,index)>=0){Graphics.Blit(targets[c],presentation);var previous=RenderTexture.active;RenderTexture.active=presentation;pixels.ReadPixels(new Rect(0,0,Size,Size),0,0);pixels.Apply(false);RenderTexture.active=previous;if(job.mode=="full"){sinks[c].Write(pixels,index);if(Array.IndexOf(Preview,index)>=0||index==Limit-1)File.WriteAllBytes(Path.Combine(job.output,demo.mode,traces[c].camera,$"reference-{index:D5}.png"),pixels.EncodeToPNG());}else File.WriteAllBytes(Path.Combine(job.output,demo.mode,traces[c].camera,$"{index:D5}.png"),pixels.EncodeToPNG());}
            }
            if(++index<Limit)return;if(sinks!=null)foreach(var sink in sinks)if(sink!=null)sink.Close();foreach(var trace in traces)File.WriteAllText(Path.Combine(job.output,demo.mode,trace.camera,"trace.json"),JsonUtility.ToJson(trace,true));if(++modeIndex<TemporalSceneModel.Modes.Length){Prepare();return;}
            File.WriteAllText(Path.Combine(job.output,"complete.json"),"{\"fingerprint\":\""+job.fingerprint+"\",\"modes\":4,\"camerasPerMode\":2,\"renderedFramesPerCamera\":"+Limit+",\"framesPerCamera\":"+(job.mode=="full"?Limit:Preview.Length)+",\"internalRenderWidth\":540,\"presentationWidth\":1080,\"everyHistoryFrameRendered\":true,\"actualUnityCapture\":true}");EditorApplication.update-=Tick;captureEnded=true;EditorApplication.Exit(0);
        }catch(Exception e){if(sinks!=null)foreach(var sink in sinks)if(sink!=null)try{sink.Close();}catch(Exception){}EditorApplication.update-=Tick;Debug.LogException(e);captureEnded=true;EditorApplication.Exit(1);}}
    }
}
