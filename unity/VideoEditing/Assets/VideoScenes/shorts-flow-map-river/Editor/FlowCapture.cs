using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.Rendering;
using Object=UnityEngine.Object;
namespace YamyamCoding.FlowShort.Editor {
public static class FlowCapture {
 const string Root="Assets/VideoScenes/shorts-flow-map-river";const int W=1080,H=1080;
 [Serializable]public class Job{public string output,mode,timeline;public int[]sampleFrames;}
 [Serializable]public class Section{public string id;public int startFrame,endFrame;public float start,end;}
 [Serializable]public class Timeline{public int frames;public float durationSeconds;public Section[]sections;}
 [Serializable]public class Arrow{public Vector2 uv;public Vector2 value;public Vector3 a,b;}
 [Serializable]public class Record{public int frame;public string id;public float clock,useFlow,blend,longStretch,mapCentre,rockCentre;public Arrow[]arrows;}
 [Serializable]public class Report{public int width=W,height=H;public int frames;public bool actualShader=true;public string pipeline="Built-in capture, own shader (SRPDefaultUnlit pass compatible)";public List<Record>records=new List<Record>();public string[]scenes;}
 static Job job;static Camera cam;static Material water;static Texture2D flow,ripple;static GameObject rock,arrows;static FlowRiverDemo demo;static RenderTexture rt;static Texture2D read;static float fieldCentre;
 static Material Mat(string name,Color col){var m=new Material(Shader.Find("Yamyam/FlowSolid"));m.color=col;AssetDatabase.CreateAsset(m,Root+"/Materials/"+name+".mat");return m;}
 static GameObject MeshObject(string name,Mesh mesh,Material m,Vector3 pos){var g=new GameObject(name);g.AddComponent<MeshFilter>().sharedMesh=mesh;g.AddComponent<MeshRenderer>().sharedMaterial=m;g.transform.position=pos;return g;}
 static Mesh Plane(){var m=new Mesh{name="Actual water plane, two triangles"};m.vertices=new[]{new Vector3(-4.6f,0,-2.3f),new Vector3(4.6f,0,-2.3f),new Vector3(-4.6f,0,2.3f),new Vector3(4.6f,0,2.3f)};m.uv=new[]{new Vector2(0,0),new Vector2(1,0),new Vector2(0,1),new Vector2(1,1)};m.triangles=new[]{0,2,1,1,2,3};m.RecalculateNormals();AssetDatabase.CreateAsset(m,Root+"/Meshes/Water.asset");return m;}
 static Mesh Boulder(string name,int seed){var m=new Mesh{name=name};var vertices=new List<Vector3>();var tri=new List<int>();var rand=new System.Random(seed);int rings=7,sides=13;var grid=new Vector3[rings+1,sides];
  for(int j=0;j<=rings;j++)for(int i=0;i<sides;i++){float p=Mathf.PI*j/rings,a=Mathf.PI*2*i/sides,noise=.87f+(float)rand.NextDouble()*.22f;grid[j,i]=new Vector3(Mathf.Sin(p)*Mathf.Cos(a)*noise,Mathf.Cos(p)*.76f,Mathf.Sin(p)*Mathf.Sin(a)*noise);}
  for(int j=0;j<rings;j++)for(int i=0;i<sides;i++){int k=(i+1)%sides;foreach(var v in new[]{grid[j,i],grid[j+1,k],grid[j+1,i],grid[j,i],grid[j,k],grid[j+1,k]}){tri.Add(vertices.Count);vertices.Add(v);}}m.vertices=vertices.ToArray();m.triangles=tri.ToArray();m.RecalculateNormals();AssetDatabase.CreateAsset(m,Root+"/Meshes/"+name+".asset");return m;}
 static Vector2 Field(Vector2 uv,float centre){float x=(uv.x-.5f)*9.2f-centre,z=(uv.y-.5f)*4.6f;float r2=x*x+z*z;const float a2=.79f*.79f;if(r2<a2)return Vector2.zero;float r4=r2*r2;return Vector2.ClampMagnitude(new Vector2(.42f*(1-a2*(x*x-z*z)/r4),-.42f*2*a2*x*z/r4),.9f);}
 static void SetMap(float centre){fieldCentre=centre;var colours=new Color[256*256];for(int y=0;y<256;y++)for(int x=0;x<256;x++){var f=Field(new Vector2((x+.5f)/256,(y+.5f)/256),centre);colours[y*256+x]=new Color(f.x*.5f+.5f,f.y*.5f+.5f,0,1);}flow.SetPixels(colours);flow.Apply();}
 static float Noise(float x,float y){return Mathf.PerlinNoise(x*8+3,y*8+7)*.65f+Mathf.PerlinNoise(x*21+27,y*21+18)*.23f+Mathf.Sin(x*67+y*13)*.06f;}
 static void Build(){
  foreach(var folder in new[]{"Materials","Meshes","Generated","Scenes"})Directory.CreateDirectory(Root+"/"+folder);AssetDatabase.Refresh();EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
  GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;PlayerSettings.colorSpace=ColorSpace.Linear;QualitySettings.antiAliasing=1;RenderSettings.ambientLight=Color.black;
  flow=new Texture2D(256,256,TextureFormat.RGBAFloat,false,true){name="Linear RG signed flow data",filterMode=FilterMode.Bilinear,wrapMode=TextureWrapMode.Clamp};SetMap(0);AssetDatabase.CreateAsset(flow,Root+"/Generated/Flow.asset");
  ripple=new Texture2D(512,512,TextureFormat.RGBA32,false,true){name="Procedural ripple normal and foam",filterMode=FilterMode.Bilinear,wrapMode=TextureWrapMode.Repeat};var pixels=new Color[512*512];for(int y=0;y<512;y++)for(int x=0;x<512;x++){float u=x/512f,v=y/512f,e=1f/512;float gx=(Noise(u+e,v)-Noise(u-e,v))*8,gz=(Noise(u,v+e)-Noise(u,v-e))*8;pixels[y*512+x]=new Color(gx*.5f+.5f,gz*.5f+.5f,Noise(u,v),1);}ripple.SetPixels(pixels);ripple.Apply();AssetDatabase.CreateAsset(ripple,Root+"/Generated/Ripple.asset");
  water=new Material(Shader.Find("Yamyam/FlowMapWater")){name="Actual flow map shader"};water.SetTexture("_Flow",flow);water.SetTexture("_Ripple",ripple);AssetDatabase.CreateAsset(water,Root+"/Materials/Water.mat");MeshObject("Water surface",Plane(),water,Vector3.zero);
  var stone=Mat("Rock",new Color(.33f,.36f,.34f));rock=MeshObject("Controlled central rock",Boulder("CentralRock",89),stone,new Vector3(0,.17f,0));rock.transform.localScale=new Vector3(.78f,.9f,.78f);
  var bankMat=Mat("Shore",new Color(.17f,.23f,.19f));for(int j=0;j<2;j++)for(int i=0;i<8;i++){var b=MeshObject("River bank pebble",Boulder("Bank"+j+"_"+i,17+j*20+i),bankMat,new Vector3(-4.3f+i*1.2f,-.20f,j==0?-2.48f:2.48f));b.transform.localScale=new Vector3(.87f,.52f,.44f);}
  cam=new GameObject("Fixed river camera").AddComponent<Camera>();cam.enabled=false;cam.orthographic=true;cam.orthographicSize=5.0f;cam.aspect=1;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=Color.black;cam.allowHDR=false;cam.nearClipPlane=.1f;cam.farClipPlane=40;cam.transform.position=new Vector3(0,9,-6);cam.transform.LookAt(Vector3.zero);
  rt=new RenderTexture(W,H,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);rt.Create();cam.targetTexture=rt;read=new Texture2D(W,H,TextureFormat.RGB24,false);
  demo=new GameObject("Editable flow shader controls").AddComponent<FlowRiverDemo>();demo.water=water;demo.animate=false;demo.clock=1;demo.Apply();
  // Saved editing scenes play in the Game view; capture uses a private target only afterwards.
  cam.enabled=true;cam.targetTexture=null;demo.animate=true;
  for(int i=0;i<6;i++){demo.useFlow=i==1?0:1;demo.displayMap=i==2?1:0;demo.blendPhases=i==4?0:1;demo.Apply();EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),Root+"/Scenes/"+(i+1).ToString("D2")+"-FlowStage.unity");}cam.enabled=false;cam.targetTexture=rt;demo.animate=false;demo.displayMap=0;demo.useFlow=1;demo.blendPhases=1;demo.Apply();AssetDatabase.SaveAssets();
 }
 static Vector3 Screen(Vector3 p){var s=cam.WorldToScreenPoint(p);return new Vector3(s.x,H-s.y,s.z);}
 static Record State(int frame,string id,float local){
  demo.clock=frame/60f;demo.useFlow=id=="uniform"?0:1;demo.displayMap=id=="map"?1:0;demo.blendPhases=id=="stretch"||id=="reset"?0:1;demo.longStretch=id=="stretch"?1:0;
  float centre=id=="update"?Mathf.SmoothStep(0,1.35f,Mathf.Clamp01(local/1.1f)):0; if(Mathf.Abs(centre-fieldCentre)>.0001f)SetMap(centre);
  rock.transform.position=new Vector3(id=="move"?Mathf.SmoothStep(0,1.35f,Mathf.Clamp01(local/1.1f)):id=="update"||id=="close"?1.35f:0,.17f,0);if(id=="close"&&fieldCentre!=1.35f)SetMap(1.35f);
  if(id=="stretch")demo.clock=local*2.4f;
  demo.Apply();if(arrows)Object.DestroyImmediate(arrows);arrows=new GameObject("Sampled flow arrows");var rows=new List<Arrow>();
  for(int y=0;y<7;y++)for(int x=0;x<12;x++){var uv=new Vector2(.06f+x*.08f,.1f+y*.13f);var c=flow.GetPixelBilinear(uv.x,uv.y);var f=new Vector2(c.r*2-1,c.g*2-1);if(f.sqrMagnitude<.008f)continue;var a=new Vector3((uv.x-.5f)*9.2f,.035f,(uv.y-.5f)*4.6f);var b=a+new Vector3(f.x,0,f.y)*.65f;rows.Add(new Arrow{uv=uv,value=f,a=Screen(a),b=Screen(b)});}
  return new Record{frame=frame,id=id,clock=demo.clock,useFlow=demo.useFlow,blend=demo.blendPhases,longStretch=demo.longStretch,mapCentre=fieldCentre,rockCentre=rock.transform.position.x,arrows=rows.ToArray()};
 }
 static void Picture(string path){cam.Render();RenderTexture.active=rt;read.ReadPixels(new Rect(0,0,W,H),0,0);read.Apply();File.WriteAllBytes(path,read.EncodeToJPG(95));RenderTexture.active=null;}
 public static void Run(){try{var args=Environment.GetCommandLineArgs();job=JsonUtility.FromJson<Job>(File.ReadAllText(args[Array.IndexOf(args,"-flowJob")+1]));Directory.CreateDirectory(job.output);Build();var report=new Report();
  if(job.mode.StartsWith("preview")){string[]ids={"hero","uniform","arrows","map","decode","flow","stretch","reset","blend","move","update","close"};for(int i=0;i<ids.Length;i++){var r=State(120+i*90,ids[i],2);Picture(Path.Combine(job.output,ids[i]+".jpg"));report.records.Add(r);}}
  else{var timing=JsonUtility.FromJson<Timeline>(File.ReadAllText(job.timeline));Directory.CreateDirectory(Path.Combine(job.output,"frames"));for(int f=0;f<timing.frames;f++){if(job.mode=="samples"&&!job.sampleFrames.Contains(f))continue;var sec=timing.sections.First(s=>f>=s.startFrame&&f<s.endFrame);var r=State(f,sec.id,(f-sec.startFrame)/60f);Picture(Path.Combine(job.output,"frames",f.ToString("D5")+".jpg"));report.records.Add(r);if(f%300==0)Debug.Log("FLOW_FRAME "+f+" / "+timing.frames);}}
  report.frames=report.records.Count;report.scenes=Directory.GetFiles(Root+"/Scenes","*.unity");File.WriteAllText(Path.Combine(job.output,"readback.json"),JsonUtility.ToJson(report,true));File.WriteAllText(Path.Combine(job.output,"success.json"),"{\"frames\":"+report.frames+",\"width\":1080,\"height\":1080,\"actualShader\":true}");EditorApplication.Exit(0);
 }catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}}
}
}
