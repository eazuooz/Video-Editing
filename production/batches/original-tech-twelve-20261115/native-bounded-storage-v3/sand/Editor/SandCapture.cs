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
namespace Yamyam.OriginalTechTwelve.Sand.Editor {
    public static class SandCapture {
        const string Root="Assets/OriginalTechTwelve/SandV1";const int Size=1080,Fps=60,Frames=720;
        static readonly int[] Preview={0,90,150,240,330,420,510,600,660,719};
        [Serializable] public class Job{public string output,fingerprint,mode,ffmpeg;public int frameLimit;}
        [Serializable] public class Frame{public int frame;public SandState model;}
        [Serializable] public class Trace{public string engine,mode,camera,fingerprint;public int fps=60;public string interpretation="Own layered sand shader and synthetic dune; not Journey implementation, performance, grain counts or gameplay footage";public List<Frame>frames=new List<Frame>();}
        static Job job;static int Limit{get{return job.frameLimit>0?job.frameLimit:Frames;}}static LosslessFrameSink sink;static SandLesson demo;static Trace trace;static int modeIndex,cameraIndex,index;static RenderTexture rt;static Texture2D pixels;
        static Texture2D GrainTexture(bool keep){
            string path=Root+"/Baked/"+(keep?"distribution-preserved":"averaged")+".asset";var existing=AssetDatabase.LoadAssetAtPath<Texture2D>(path);if(existing)return existing;
            var tex=new Texture2D(128,128,TextureFormat.RGBA32,true,true);tex.name=keep?"Authored distribution per mip":"Ordinary averaged mips";tex.wrapMode=TextureWrapMode.Repeat;tex.filterMode=FilterMode.Trilinear;tex.anisoLevel=4;
            Color[] previous=null;
            for(int mip=0;mip<tex.mipmapCount;mip++){
                int size=Math.Max(1,128>>mip);var colors=new Color[size*size];var rng=new System.Random(7123+mip*17);
                for(int y=0;y<size;y++)for(int x=0;x<size;x++){
                    if(keep||mip==0){var n=SandModel.Grain(rng);colors[y*size+x]=new Color(n[0]*.5f+.5f,n[1]*.5f+.5f,n[2]*.5f+.5f,1);}
                    else{int psize=size*2;colors[y*size+x]=(previous[(y*2)*psize+x*2]+previous[(y*2)*psize+x*2+1]+previous[(y*2+1)*psize+x*2]+previous[(y*2+1)*psize+x*2+1])*.25f;}
                }
                tex.SetPixels(colors,mip);previous=colors;
            }
            tex.Apply(false,false);AssetDatabase.CreateAsset(tex,path);return tex;
        }
        static Mesh Dune(){
            string path=Root+"/Baked/dune.asset";var old=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(old)return old;
            const int side=97;var vertices=new Vector3[side*side];var uv=new Vector2[vertices.Length];var triangles=new List<int>();
            for(int z=0;z<side;z++)for(int x=0;x<side;x++){float wx=(x/(float)(side-1)-.5f)*28,wz=(z/(float)(side-1)-.5f)*28;int k=z*side+x;vertices[k]=new Vector3(wx,SandModel.Height(wx,wz),wz);uv[k]=new Vector2(x/(float)(side-1),z/(float)(side-1));if(x+1<side&&z+1<side){triangles.AddRange(new[]{k,k+side,k+1,k+1,k+side,k+side+1});}}
            var mesh=new Mesh{name="Self-authored synthetic dune"};mesh.vertices=vertices;mesh.uv=uv;mesh.triangles=triangles.ToArray();mesh.RecalculateNormals();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,path);return mesh;
        }
        static Camera View(string name){var c=new GameObject(name).AddComponent<Camera>();c.enabled=false;c.aspect=1;c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=Color.black;c.fieldOfView=52;c.nearClipPlane=.1f;c.farClipPlane=70;return c;}
        public static void Run(){try{
            var args=Environment.GetCommandLineArgs();int j=Array.IndexOf(args,"-ot12Job");if(j<0)throw new Exception("Exact job required");job=JsonUtility.FromJson<Job>(File.ReadAllText(args[j+1]));if(job.mode!="pilot"&&job.mode!="full")throw new Exception("Invalid capture mode");Directory.CreateDirectory(job.output);if(Directory.EnumerateFiles(job.output,"*",SearchOption.AllDirectories).Any())throw new Exception("Preserve prior output");Directory.CreateDirectory(Root+"/Baked");Directory.CreateDirectory(Root+"/Scenes");modeIndex=0;Prepare();EditorApplication.update+=Tick;
        }catch(Exception e){Debug.LogException(e);captureEnded=true;EditorApplication.Exit(1);}}
        static void Prepare(){
            GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;QualitySettings.antiAliasing=4;var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);RenderSettings.skybox=null;
            var shader=Shader.Find("Yamyam/OriginalTechTwelve/SandLesson");if(!shader||ShaderUtil.ShaderHasError(shader))throw new Exception("Authored shader failed compilation");
            string mp=Root+"/Baked/"+SandModel.Modes[modeIndex]+".mat";var mat=AssetDatabase.LoadAssetAtPath<Material>(mp);if(!mat){mat=new Material(shader);AssetDatabase.CreateAsset(mat,mp);}
            var dune=new GameObject("Same synthetic dune mesh");dune.AddComponent<MeshFilter>().sharedMesh=Dune();dune.AddComponent<MeshRenderer>().sharedMaterial=mat;
            demo=new GameObject("Layered sand explanation").AddComponent<SandLesson>();demo.mode=SandModel.Modes[modeIndex];demo.material=mat;demo.averaged=GrainTexture(false);demo.preserved=GrainTexture(true);demo.duneView=View("Dune viewpoint");demo.detailView=View("Grain detail viewpoint");demo.Apply(0);demo.livePlayback=true;demo.duneView.enabled=true;EditorSceneManager.SaveScene(scene,Root+"/Scenes/"+demo.mode+".unity");demo.livePlayback=false;demo.duneView.enabled=false;AssetDatabase.SaveAssets();
            if(rt)Object.DestroyImmediate(rt);if(pixels)Object.DestroyImmediate(pixels);rt=new RenderTexture(Size,Size,24,RenderTextureFormat.ARGB32){antiAliasing=4};rt.Create();pixels=new Texture2D(Size,Size,TextureFormat.RGB24,false);cameraIndex=(demo.mode=="smooth-surface"||demo.mode=="masked-glints-broad-light")?0:1;BeginCamera();
        }
        static void BeginCamera(){index=0;trace=new Trace{engine=Application.unityVersion,mode=demo.mode,camera=cameraIndex==0?"dune":"detail",fingerprint=job.fingerprint};Directory.CreateDirectory(Path.Combine(job.output,demo.mode,trace.camera));if(job.mode=="full")sink=new LosslessFrameSink(Path.Combine(job.output,demo.mode,trace.camera),job.ffmpeg,Size,Size,Fps,Limit);}
        static bool captureEnded;
        static void Tick(){for(int n=0;n<8&&!captureEnded;n++)CaptureStep();}
        static void CaptureStep(){try{
            int f=job.mode=="full"?index:Preview[index];demo.Apply(f/(float)Fps);var camera=cameraIndex==0?demo.duneView:demo.detailView;camera.targetTexture=rt;camera.Render();var previous=RenderTexture.active;RenderTexture.active=rt;pixels.ReadPixels(new Rect(0,0,Size,Size),0,0);pixels.Apply(false);RenderTexture.active=previous;trace.frames.Add(new Frame{frame=f,model=demo.current});if(job.mode=="full"){sink.Write(pixels,f);if(Array.IndexOf(Preview,f)>=0||f==Limit-1)File.WriteAllBytes(Path.Combine(job.output,demo.mode,trace.camera,$"reference-{f:D5}.png"),pixels.EncodeToPNG());}else File.WriteAllBytes(Path.Combine(job.output,demo.mode,trace.camera,$"{f:D5}.png"),pixels.EncodeToPNG());if(++index<(job.mode=="full"?Limit:Preview.Length))return;if(sink!=null){sink.Close();sink=null;}File.WriteAllText(Path.Combine(job.output,demo.mode,trace.camera,"trace.json"),JsonUtility.ToJson(trace,true));/* Record only the source-order selected viewpoint for this mode. */if(++modeIndex<SandModel.Modes.Length){Prepare();return;}
            File.WriteAllText(Path.Combine(job.output,"complete.json"),"{\"fingerprint\":\""+job.fingerprint+"\",\"modes\":7,\"camerasPerMode\":1,\"framesPerCamera\":"+(job.mode=="full"?Limit:Preview.Length)+",\"actualUnityCapture\":true}");EditorApplication.update-=Tick;captureEnded=true;EditorApplication.Exit(0);
        }catch(Exception e){if(sink!=null)try{sink.Close();}catch(Exception){}EditorApplication.update-=Tick;Debug.LogException(e);captureEnded=true;EditorApplication.Exit(1);}}
    }
}
