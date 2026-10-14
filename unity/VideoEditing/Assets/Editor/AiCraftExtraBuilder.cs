using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using System.IO;
using System.Collections.Generic;
using Object=UnityEngine.Object;

public static class AiCraftExtraBuilder
{
 const string Base="Assets/AiCraftProduction", Scenes="Assets/VideoScenes/ai-game-development-human-craft";
 static Material Mat(string name,Color color){var path=Base+"/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}m.color=color;return m;}
 static GameObject Part(string name,PrimitiveType type,Vector3 pos,Vector3 scale,Material m,Transform parent=null){var g=GameObject.CreatePrimitive(type);g.name=name;g.layer=31;if(parent)g.transform.SetParent(parent,false);g.transform.localPosition=pos;g.transform.localScale=scale;g.GetComponent<Renderer>().sharedMaterial=m;Object.DestroyImmediate(g.GetComponent<Collider>());return g;}
 public static void Build(){
  var previous=SceneManager.GetActiveScene();
  foreach(var id in new[]{"02","06","08","14","26"}){
   string path=Scenes+"/"+id+"-illustration.unity";
   if(File.Exists(path)){
    if(id=="26"){
     var existing=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
     try{foreach(var item in existing.GetRootGameObjects())if(item.name=="Wood board"){item.transform.position=new Vector3(0,.065f,0);item.transform.localScale=new Vector3(3.6f,.8f,1.7f);}EditorSceneManager.SaveScene(existing,path);}finally{EditorSceneManager.CloseScene(existing,true);}
    }
    continue;
   }
   var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);SceneManager.SetActiveScene(scene);
   try{
    RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.3f,.34f,.38f);RenderSettings.skybox=null;RenderSettings.fog=false;
    var root=new GameObject("Lesson execution — "+id);var c=root.AddComponent<AiCraftLessonScene>();c.sceneId=id;c.extra=root.AddComponent<AiCraftExtraScene>();
    var camera=new GameObject("Teaching Camera").AddComponent<Camera>();camera.enabled=false;camera.orthographic=true;camera.orthographicSize=3.2f;camera.cullingMask=1<<31;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=Color.black;camera.allowHDR=false;camera.transform.position=new Vector3(6,4,9);camera.transform.LookAt(new Vector3(0,1,0));c.captureCamera=camera;camera.GetUniversalAdditionalCameraData().renderShadows=true;
    var key=new GameObject("Key").AddComponent<Light>();key.type=LightType.Directional;key.transform.rotation=Quaternion.Euler(35,-25,0);key.intensity=1.8f;key.color=new Color(1,.88f,.72f);key.cullingMask=1<<31;key.shadows=LightShadows.Soft;
    if(id=="06")BuildUv(c);if(id=="14"||id=="02")BuildInteraction(c);if(id=="26")BuildTool(c);if(id=="08")BuildChair(c);
    c.ApplyFrame(0);EditorSceneManager.SaveScene(scene,path);
   }finally{EditorSceneManager.CloseScene(scene,true);}
  }
  if(previous.IsValid())SceneManager.SetActiveScene(previous);AssetDatabase.SaveAssets();
 }
 static void BuildUv(AiCraftLessonScene c){
  var mpath=Base+"/UvTeaching.mat";var m=AssetDatabase.LoadAssetAtPath<Material>(mpath);if(!m){m=new Material(Shader.Find("Yamyam/UvTeaching"));AssetDatabase.CreateAsset(m,mpath);}
  string meshpath=Base+"/UvBottle.asset";var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(meshpath);
  if(!mesh){mesh=new Mesh();var v=new List<Vector3>();var uv=new List<Vector2>();var tr=new List<int>();float[] radii={.05f,.45f,.65f,.73f,.71f,.5f,.23f,.23f};
   for(int y=0;y<8;y++)for(int x=0;x<=32;x++){float a=x/32f*Mathf.PI*2;v.Add(new Vector3(Mathf.Cos(a)*radii[y],y*.34f,Mathf.Sin(a)*radii[y]));uv.Add(new Vector2(x/32f,y/7f));if(y<7&&x<32){int i=y*33+x;tr.AddRange(new[]{i,i+33,i+1,i+1,i+33,i+34});}}
   mesh.SetVertices(v);mesh.SetUVs(0,uv);mesh.SetTriangles(tr,0);mesh.RecalculateNormals();AssetDatabase.CreateAsset(mesh,meshpath);
  }
  var bottle=new GameObject("UV mapped potion bottle");bottle.layer=31;bottle.transform.position=new Vector3(-1.5f,-.2f,0);bottle.AddComponent<MeshFilter>().sharedMesh=mesh;var r=bottle.AddComponent<MeshRenderer>();r.sharedMaterial=m;c.extra.uvBody=r;c.extra.subject=bottle.transform;
  Part("Cork",PrimitiveType.Cylinder,new Vector3(0,2.45f,0),new Vector3(.48f,.12f,.48f),Mat("Cork",new Color(.45f,.25f,.14f)),bottle.transform);
  var plane=Part("Flat UV texture",PrimitiveType.Quad,new Vector3(1.8f,1.1f,0),new Vector3(2.5f,2.5f,1),m);c.extra.uvPlane=plane.GetComponent<Renderer>();plane.transform.LookAt(c.captureCamera.transform);plane.transform.Rotate(0,180,0);
 }
 static Sprite Sprite(string name,Rect rect){string p=Base+"/"+name+".asset";var s=AssetDatabase.LoadAssetAtPath<Sprite>(p);if(!s){s=UnityEngine.Sprite.Create(AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/ThirdParty/KenneyTinyDungeon/tilemap_packed.png"),rect,new Vector2(.5f,.5f),16);AssetDatabase.CreateAsset(s,p);}return s;}
 static GameObject Pixel(string name,Sprite sprite,Vector3 pos,float scale){var g=new GameObject(name);g.layer=31;g.transform.position=pos;g.transform.localScale=Vector3.one*scale;g.AddComponent<SpriteRenderer>().sprite=sprite;return g;}
 static void BuildInteraction(AiCraftLessonScene c){
  c.captureCamera.transform.position=new Vector3(0,0,-10);c.captureCamera.transform.rotation=Quaternion.identity;c.captureCamera.orthographicSize=3.2f;
  c.extra.subject=Pixel("Knight",Sprite("InteractionKnight",new Rect(0,32,16,16)),new Vector3(-3.8f,-.8f,0),1.5f).transform;
  var key=new GameObject("Key to unlock door");key.layer=31;key.transform.position=new Vector3(-.8f,-.6f,0);c.extra.reward=key.transform;
  var keymat=Mat("KeyGold",new Color(.91f,.81f,.51f));Part("Key bow",PrimitiveType.Sphere,new Vector3(-.15f,0,0),new Vector3(.32f,.32f,.08f),keymat,key.transform);Part("Key shank",PrimitiveType.Cube,new Vector3(.12f,0,0),new Vector3(.5f,.1f,.08f),keymat,key.transform);Part("Key tooth",PrimitiveType.Cube,new Vector3(.3f,-.09f,0),new Vector3(.1f,.22f,.08f),keymat,key.transform);
  c.extra.door=Pixel("Door",Sprite("InteractionDoor",new Rect(144,128,16,16)),new Vector3(3.6f,-.25f,0),2.2f).transform;
  var stone=Sprite("InteractionStone",new Rect(32,128,16,16));for(int i=0;i<12;i++)Pixel("Floor "+i,stone,new Vector3(-5.5f+i,-1.9f,.2f),1);
 }
 static void BuildTool(AiCraftLessonScene c){
  var teal=Mat("DrillTeal",new Color(.18f,.45f,.43f));var dark=Mat("ToolGrip",new Color(.08f,.1f,.12f));var steel=Mat("ToolSteel",new Color(.65f,.69f,.72f));steel.SetFloat("_Metallic",.7f);steel.SetFloat("_Smoothness",.6f);var wood=Mat("ToolWood",new Color(.43f,.27f,.16f));var yellow=Mat("ToolAccent",new Color(.91f,.81f,.51f));
  var drill=new GameObject("Power drill illustration").transform;drill.position=new Vector3(-.15f,2f,0);drill.rotation=Quaternion.Euler(0,0,-90);c.extra.subject=drill;
  var housing=Part("Motor housing",PrimitiveType.Capsule,new Vector3(-.75f,.15f,0),new Vector3(.63f,.68f,.63f),teal,drill);housing.transform.localRotation=Quaternion.Euler(0,0,90);
  Part("Grip",PrimitiveType.Capsule,new Vector3(-1.05f,-.52f,0),new Vector3(.35f,.55f,.4f),dark,drill);
  Part("Battery",PrimitiveType.Cube,new Vector3(-1.05f,-1.03f,0),new Vector3(.76f,.28f,.65f),teal,drill);
  Part("Trigger",PrimitiveType.Cube,new Vector3(-.75f,-.28f,.02f),new Vector3(.15f,.24f,.3f),yellow,drill);
  for(int i=0;i<5;i++)Part("Motor vent "+i,PrimitiveType.Cube,new Vector3(-1.15f+i*.1f,.19f,.31f),new Vector3(.045f,.22f,.035f),dark,drill);
  var chuck=Part("Chuck and clutch",PrimitiveType.Cylinder,new Vector3(-.08f,.15f,0),new Vector3(.4f,.27f,.4f),dark,drill);chuck.transform.localRotation=Quaternion.Euler(0,0,90);c.extra.movingPart=chuck.transform;
  var bit=Part("Driver bit",PrimitiveType.Cylinder,new Vector3(.25f,.15f,0),new Vector3(.09f,.23f,.09f),steel,drill);bit.transform.localRotation=Quaternion.Euler(0,0,90);
  // Keep screw/board visibly separate from the drill; movement is a labeled analogy.
  var screw=new GameObject("Screw seating").transform;screw.position=new Vector3(0,1.4f,0);c.extra.reward=screw;
  Part("Screw shaft",PrimitiveType.Cylinder,new Vector3(0,-.2f,0),new Vector3(.14f,.35f,.14f),steel,screw);
  Part("Screw head",PrimitiveType.Cylinder,new Vector3(0,.18f,0),new Vector3(.3f,.055f,.3f),steel,screw);
  for(int i=0;i<8;i++)Part("Thread ridge "+i,PrimitiveType.Cylinder,new Vector3(0,-.46f+i*.065f,0),new Vector3(.22f,.012f,.22f),steel,screw);
  Part("Drive recess",PrimitiveType.Cube,new Vector3(0,.24f,0),new Vector3(.18f,.01f,.04f),dark,screw);
  Part("Wood board",PrimitiveType.Cube,new Vector3(0,.065f,0),new Vector3(3.6f,.8f,1.7f),wood);
  for(int i=0;i<5;i++)Part("Wood grain "+i,PrimitiveType.Cube,new Vector3(0,.465f,-.65f+i*.3f),new Vector3(3.3f,.004f,.015f),dark);
  c.captureCamera.transform.position=new Vector3(4,4,7);c.captureCamera.transform.LookAt(new Vector3(-.3f,1.4f,0));c.captureCamera.orthographicSize=2.65f;
 }
 static void BuildChair(AiCraftLessonScene c){
  var wood=Mat("ChairWalnut",new Color(.38f,.19f,.09f));var edge=Mat("ChairPolish",new Color(.65f,.39f,.17f));
  var chair=new GameObject("Authored wooden chair illustration").transform;c.extra.subject=chair;
  for(int x=-1;x<=1;x+=2)for(int z=-1;z<=1;z+=2){Part("Turned leg",PrimitiveType.Cylinder,new Vector3(x*.75f,.65f,z*.65f),new Vector3(.16f,.65f,.16f),wood,chair);for(int r=0;r<3;r++)Part("Leg carved bead",PrimitiveType.Sphere,new Vector3(x*.75f,.2f+r*.32f,z*.65f),new Vector3(.23f,.2f,.23f),edge,chair);}
  for(int i=0;i<7;i++)Part("Seat plank",PrimitiveType.Cube,new Vector3((i-3)*.24f,1.35f,0),new Vector3(.235f,.16f,1.55f),i%2==0?wood:edge,chair);
  for(int x=-1;x<=1;x+=2){Part("Back post",PrimitiveType.Cylinder,new Vector3(x*.75f,2.05f,-.65f),new Vector3(.15f,.75f,.15f),wood,chair);Part("Finial",PrimitiveType.Sphere,new Vector3(x*.75f,2.85f,-.65f),Vector3.one*.25f,edge,chair);}
  Part("Curved back crest",PrimitiveType.Capsule,new Vector3(0,2.65f,-.65f),new Vector3(.24f,.85f,.24f),edge,chair).transform.localRotation=Quaternion.Euler(0,0,90);
  for(int i=-2;i<=2;i++){Part("Back spindle",PrimitiveType.Cylinder,new Vector3(i*.25f,2,-.65f),new Vector3(.07f,.55f,.07f),wood,chair);Part("Spindle carving",PrimitiveType.Sphere,new Vector3(i*.25f,2,-.65f),new Vector3(.14f,.3f,.14f),edge,chair);}
  for(int z=-1;z<=1;z+=2){var rail=Part("Cross rail",PrimitiveType.Cylinder,new Vector3(0,.5f,z*.65f),new Vector3(.08f,.75f,.08f),edge,chair);rail.transform.localRotation=Quaternion.Euler(0,0,90);}
  c.captureCamera.transform.position=new Vector3(5,3.8f,7);c.captureCamera.transform.LookAt(new Vector3(0,1.4f,0));c.captureCamera.orthographicSize=2.1f;
 }
}
