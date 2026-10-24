using System;using System.IO;using System.Linq;using System.Collections.Generic;
using UnityEngine;using UnityEditor;using UnityEditor.SceneManagement;using UnityEngine.Rendering;
using Object=UnityEngine.Object;
namespace YamyamCoding.InteriorShort.Editor {
 public static class InteriorCapture {
  const string Root="Assets/VideoScenes/shorts-interior-mapping-window";const int W=1080,H=1080;
  [Serializable]public class Job{public string output,mode,timeline;}
  [Serializable]public class Section{public string id;public int startFrame,endFrame;public float start,end;}
  [Serializable]public class Timeline{public int frames;public float durationSeconds;public Section[]sections;}
  [Serializable]public class Record{public int frame;public string id,hitFace;public Vector3 viewer,entry,hit,screenViewer,screenEntry,screenHit;public float mapped;}
  [Serializable]public class Report{public int width=W,height=H,frames;public string pipeline="Built-in explicit custom shader";public string graphicsDriver;public int windowVertices=4,windowTriangles=2;public bool actualShader=true;public List<Record>records=new List<Record>();public string[]scenes;}
  static Job job;static Camera cam,viewer;static GameObject window,guides,rayGroup;static Material material,lineMaterial,virtualWall;static RenderTexture rt;static Texture2D image;static InteriorControls controls;
  static void Line(string name,Vector3 a,Vector3 b,Color colour,float width=.025f){var g=new GameObject(name);g.transform.parent=guides.transform;var line=g.AddComponent<LineRenderer>();line.sharedMaterial=lineMaterial;line.startColor=line.endColor=colour;line.startWidth=line.endWidth=width;line.positionCount=2;line.SetPositions(new[]{a,b});line.numCapVertices=4;}
  static void Dot(string name,Vector3 pos,Color colour,float size){var g=GameObject.CreatePrimitive(PrimitiveType.Sphere);g.name=name;g.transform.parent=guides.transform;g.transform.position=pos;g.transform.localScale=Vector3.one*size;var m=new Material(Shader.Find("Unlit/Color"));m.color=colour;g.GetComponent<Renderer>().sharedMaterial=m;}
  static void Build(){
   foreach(var f in new[]{"Materials","Meshes","Scenes"})Directory.CreateDirectory(Root+"/"+f);AssetDatabase.Refresh();EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
   GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;PlayerSettings.colorSpace=ColorSpace.Linear;QualitySettings.antiAliasing=1;
   var mesh=new Mesh{name="Window surface: four vertices, two triangles"};mesh.vertices=new[]{new Vector3(-2,-1.5f,0),new Vector3(2,-1.5f,0),new Vector3(-2,1.5f,0),new Vector3(2,1.5f,0)};mesh.uv=new[]{new Vector2(0,0),new Vector2(1,0),new Vector2(0,1),new Vector2(1,1)};mesh.triangles=new[]{0,2,1,1,2,3};mesh.RecalculateNormals();var oldMesh=AssetDatabase.LoadAssetAtPath<Mesh>(Root+"/Meshes/Window.asset");if(oldMesh){EditorUtility.CopySerialized(mesh,oldMesh);Object.DestroyImmediate(mesh);mesh=oldMesh;}else AssetDatabase.CreateAsset(mesh,Root+"/Meshes/Window.asset");
   material=AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/Interior.mat");if(!material){material=new Material(Shader.Find("Yamyam/InteriorMappingRoom"));AssetDatabase.CreateAsset(material,Root+"/Materials/Interior.mat");}window=new GameObject("Actual flat window mesh");window.AddComponent<MeshFilter>().sharedMesh=mesh;window.AddComponent<MeshRenderer>().sharedMaterial=material;
   viewer=new GameObject("Player camera").AddComponent<Camera>();viewer.enabled=false;viewer.transform.position=new Vector3(-2,0,-6);viewer.transform.LookAt(Vector3.zero);
   cam=new GameObject("Observer / capture camera").AddComponent<Camera>();cam.enabled=false;cam.aspect=1;cam.fieldOfView=43;cam.nearClipPlane=.05f;cam.farClipPlane=100;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=Color.black;cam.allowHDR=false;
   controls=window.AddComponent<InteriorControls>();controls.window=material;controls.viewer=viewer;controls.Apply();
   lineMaterial=AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/Guide.mat");if(!lineMaterial){lineMaterial=new Material(Shader.Find("Sprites/Default"));AssetDatabase.CreateAsset(lineMaterial,Root+"/Materials/Guide.mat");}
   virtualWall=AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/VirtualWallGuide.mat");if(!virtualWall){virtualWall=new Material(Shader.Find("Yamyam/InteriorMappingRoom"));AssetDatabase.CreateAsset(virtualWall,Root+"/Materials/VirtualWallGuide.mat");}virtualWall.SetFloat("_Structure",2);
   rt=new RenderTexture(W,H,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);rt.Create();cam.targetTexture=rt;image=new Texture2D(W,H,TextureFormat.RGB24,false);
   string[] names={"01-WindowHero","02-PhysicalPlane","03-RayIntersection","04-CameraMove","05-FlatVsMapped","06-CityWindows","07-TextureSample","08-PixelRepetition"};
   string[] ids={"hero","plane","ray","move","compare","close","sample","pixels"};
   for(int i=0;i<names.Length;i++){State(0,ids[i],2);cam.enabled=true;cam.targetTexture=null;EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),Root+"/Scenes/"+names[i]+".unity");cam.enabled=false;cam.targetTexture=rt;}
   AssetDatabase.SaveAssets();
  }
  static Vector3 Screen(Vector3 p){var s=cam.WorldToScreenPoint(p);return new Vector3(s.x,H-s.y,s.z);}
  static Record State(int frame,string id,float e){
   if(guides)Object.DestroyImmediate(guides);guides=new GameObject("Illustrative guides - not room mesh");
   var teal=new Color(.45f,.84f,.80f);var yellow=new Color(1,.82f,.35f);var red=new Color(.95f,.48f,.44f);
   float vx=id=="move"?Mathf.Lerp(-2,4.4f,Mathf.SmoothStep(0,1,e/5)):id=="compare"?Mathf.Sin(e*.6f)*3.5f:Mathf.Sin(e*.5f)*1.6f;
   if(id=="ray"||id=="room"||id=="sample")vx=-2;viewer.transform.position=new Vector3(vx,.1f,-6);viewer.transform.LookAt(Vector3.zero);controls.showPhysicalPlane=id=="plane"||id=="ray"||id=="room"||id=="sample";controls.mapped=true;controls.Apply();
   bool diagram=id=="ray"||id=="room"||id=="sample";
   if(diagram){cam.transform.position=new Vector3(10,7,-13);cam.transform.LookAt(new Vector3(-.5f,0,-1));cam.fieldOfView=43;}
   else if(id=="plane"){float angle=Mathf.Lerp(10,84,Mathf.SmoothStep(0,1,e/3))*Mathf.Deg2Rad;cam.transform.position=new Vector3(Mathf.Sin(angle)*7,.35f,-Mathf.Cos(angle)*7);cam.transform.LookAt(Vector3.zero);cam.fieldOfView=43;}
   else{cam.transform.position=viewer.transform.position;cam.transform.rotation=viewer.transform.rotation;cam.fieldOfView=43;}
   Vector3 entry=Vector3.zero,d=(entry-viewer.transform.position).normalized;
   float tx=(d.x>=0?2:-2)/(Mathf.Abs(d.x)<.00001f?.00001f:d.x),ty=(d.y>=0?1.5f:-1.5f)/(Mathf.Abs(d.y)<.00001f?.00001f:d.y),tz=4/d.z;
   float t=Mathf.Min(tx,Mathf.Min(ty,tz));Vector3 hit=entry+d*t;string face=tz<=tx&&tz<=ty?"back":tx<=ty?"side":"floor/ceiling";
   if(diagram){
    var a=new[]{new Vector3(-2,-1.5f,0),new Vector3(2,-1.5f,0),new Vector3(2,1.5f,0),new Vector3(-2,1.5f,0)};
    if(id!="ray")for(int i=0;i<4;i++){int j=(i+1)%4;Line("Virtual room edge",a[i],a[j],teal*.65f);Line("Virtual room depth",a[i],a[i]+Vector3.forward*4,teal*.65f);Line("Virtual room back",a[i]+Vector3.forward*4,a[j]+Vector3.forward*4,teal*.65f);}
    float reveal=id=="sample"?1:Mathf.Clamp01(e/1.8f);Vector3 end=id=="ray"?Vector3.Lerp(viewer.transform.position,entry,reveal):Vector3.Lerp(entry,hit,reveal);Line("View ray",viewer.transform.position,end,yellow,.05f);Dot("Window sample pixel",entry,Color.white,.14f);if(id!="ray"&&reveal>.98f)Dot("Computed intersection",hit,yellow,.2f);
    Dot("Viewpoint",viewer.transform.position,teal,.25f);
   }
   if(id=="sample"){var g=new GameObject("Illustrative virtual backwall - not implementation geometry");g.transform.parent=guides.transform;g.transform.position=new Vector3(0,0,4);g.AddComponent<MeshFilter>().sharedMesh=window.GetComponent<MeshFilter>().sharedMesh;g.AddComponent<MeshRenderer>().sharedMaterial=virtualWall;}
   if(id=="plane"){
    Line("Physical mesh triangle diagonal",new Vector3(-2,-1.5f,-.006f),new Vector3(2,1.5f,-.006f),yellow,.025f);
   }
   return new Record{frame=frame,id=id,viewer=viewer.transform.position,entry=entry,hit=hit,hitFace=face,screenViewer=Screen(viewer.transform.position),screenEntry=Screen(entry),screenHit=Screen(hit),mapped=1};
  }
  static void Picture(string path){cam.Render();RenderTexture.active=rt;image.ReadPixels(new Rect(0,0,W,H),0,0);image.Apply();File.WriteAllBytes(path,image.EncodeToJPG(94));RenderTexture.active=null;}
  public static void Run(){try{
   var args=Environment.GetCommandLineArgs();job=JsonUtility.FromJson<Job>(File.ReadAllText(args[Array.IndexOf(args,"-interiorJob")+1]));Directory.CreateDirectory(job.output);Build();var report=new Report{graphicsDriver=SystemInfo.graphicsDeviceName};
   if(job.mode.StartsWith("preview")){
    foreach(string id in new[]{"hero","plane","ray","sample","move","compare","close"}){var r=State(120,id,id=="move"?5:2);Picture(Path.Combine(job.output,id+".jpg"));if(id=="compare"){material.SetFloat("_Mapped",0);Picture(Path.Combine(job.output,"flat-photo.jpg"));material.SetFloat("_Mapped",1);}report.records.Add(r);}
   }else{
    var timeline=JsonUtility.FromJson<Timeline>(File.ReadAllText(job.timeline));Directory.CreateDirectory(Path.Combine(job.output,"frames"));Directory.CreateDirectory(Path.Combine(job.output,"flat"));
    for(int f=0;f<timeline.frames;f++){var s=timeline.sections.First(x=>f>=x.startFrame&&f<x.endFrame);var r=State(f,s.id,(f-s.startFrame)/60f);Picture(Path.Combine(job.output,"frames",f.ToString("D5")+".jpg"));if(s.id=="compare"){material.SetFloat("_Mapped",0);Picture(Path.Combine(job.output,"flat",f.ToString("D5")+".jpg"));material.SetFloat("_Mapped",1);}report.records.Add(r);if(f%300==0)Debug.Log("INTERIOR_FRAME "+f+" / "+timeline.frames);}
   }
   report.frames=report.records.Count;report.scenes=Directory.GetFiles(Root+"/Scenes","*.unity");File.WriteAllText(Path.Combine(job.output,"readback.json"),JsonUtility.ToJson(report,true));File.WriteAllText(Path.Combine(job.output,"success.json"),"{\"frames\":"+report.frames+",\"width\":1080,\"height\":1080,\"actualShader\":true}");EditorApplication.Exit(0);
  }catch(Exception ex){Debug.LogException(ex);EditorApplication.Exit(1);}}
 }
}
