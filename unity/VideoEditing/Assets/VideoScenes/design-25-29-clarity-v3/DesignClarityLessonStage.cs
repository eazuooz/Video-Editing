using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEngine;
using UnityEngine.UI;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Yamyam.DesignVisualV2 {
// Each saved cut uses the same camera and assets; only its teaching action changes.
public abstract class DesignClarityLessonStage : MonoBehaviour {
 public string slug,cutId; public int frames; public new Camera camera;
 public List<string> usedAssetPaths=new List<string>();
 public List<string> usedAnimationPaths=new List<string>();
 public const string Root="Assets/VideoScenes/design-25-29-clarity-v3";
 public const string Library="Assets/ThirdParty/YamyamAssetLibrary/";
 public static readonly Color White=Hex("F5F5F5"), Yellow=Hex("E8CF83"), Teal=Hex("73C7C2"), Red=Hex("ED9292"), Green=Hex("86CFA3"), Grey=Hex("B8B8B8");
 protected Canvas canvas; protected Font font;
 readonly Dictionary<GameObject,GameObject> actorModels=new Dictionary<GameObject,GameObject>();
 readonly Dictionary<GameObject,(string clip,float seconds)> pendingPoses=new Dictionary<GameObject,(string clip,float seconds)>();
 readonly Dictionary<string,AnimationClip> clips=new Dictionary<string,AnimationClip>();
 readonly Dictionary<string,Material> materials=new Dictionary<string,Material>();
 [Serializable] public class AssetEntry { public string key,path,productId,license,url; }
 [Serializable] public class AssetMap { public AssetEntry[] assets; }
 AssetMap assetMap;
 public abstract void Build();
 public abstract void Apply(float t);
 public static Color Hex(string hex){Color c;ColorUtility.TryParseHtmlString("#"+hex,out c);return c;}
 public void Initialize(){
  #if UNITY_EDITOR
  assetMap=JsonUtility.FromJson<AssetMap>(File.ReadAllText(Root+"/asset-map.json"));
  font=Font.CreateDynamicFontFromOSFont("Malgun Gothic",64);
  var cam=new GameObject("Explanation camera");cam.transform.SetParent(transform,false);camera=cam.AddComponent<Camera>();
  camera.transform.position=new Vector3(0,7,-14);camera.transform.LookAt(new Vector3(0,1,0));camera.orthographic=true;camera.orthographicSize=5.5f;camera.nearClipPlane=.05f;camera.farClipPlane=100;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=Color.black;camera.cullingMask=1<<29;camera.enabled=false;camera.allowHDR=false;camera.allowMSAA=true;
  var cv=new GameObject("Speech-synchronized labels");cv.transform.SetParent(transform,false);canvas=cv.AddComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=camera;canvas.planeDistance=1;canvas.sortingOrder=100;cv.layer=29;
  var scaler=cv.AddComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1920,1080);scaler.matchWidthOrHeight=0;
  Light("Key",new Vector3(48,-35,0),2.0f,Color.white);Light("Soft fill",new Vector3(25,145,0),.7f,new Color(.72f,.82f,1));
  Box("Dark stage",new Vector3(0,-.18f,0),new Vector3(18,.28f,8),Hex("151A1D"));
  Label("해설용 시연",1740,73,28,Grey,210,45);
  #endif
 }
 void Light(string name,Vector3 rot,float power,Color color){var o=new GameObject(name);o.transform.SetParent(transform,false);o.transform.eulerAngles=rot;var l=o.AddComponent<Light>();l.type=LightType.Directional;l.intensity=power;l.color=color;l.cullingMask=1<<29;l.shadows=LightShadows.Soft;l.shadowStrength=.6f;}
 protected void Title(string title){Label(title,830,98,54,Yellow,1470,90);}
 protected Material Mat(Color color,bool unlit=false){
  var key=ColorUtility.ToHtmlStringRGBA(color)+(unlit?"-unlit":"-lit");if(materials.TryGetValue(key,out var m))return m;
  m=new Material(Shader.Find(unlit?"Universal Render Pipeline/Unlit":"Universal Render Pipeline/Lit"));m.name=key;m.SetColor("_BaseColor",color);if(m.HasProperty("_Smoothness"))m.SetFloat("_Smoothness",.3f);
  #if UNITY_EDITOR
  var folder=Root+"/Generated/Materials";Directory.CreateDirectory(folder);var path=folder+"/"+key+".mat";var prior=AssetDatabase.LoadAssetAtPath<Material>(path);if(prior){DestroyImmediate(m);m=prior;}else AssetDatabase.CreateAsset(m,path);
  #endif
  materials[key]=m;return m;
 }
 protected GameObject Asset(string key,Vector3 pos,float height=2f,float yaw=0){
  #if UNITY_EDITOR
  var entry=assetMap.assets.FirstOrDefault(a=>a.key==key);if(entry==null)throw new Exception("Unknown asset key "+key);
  var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(entry.path);if(!prefab)throw new Exception("Missing selected asset "+entry.path);
  var holder=new GameObject(key);holder.transform.SetParent(transform,false);holder.transform.position=pos;holder.transform.rotation=Quaternion.Euler(0,yaw,0);
  var model=(GameObject)PrefabUtility.InstantiatePrefab(prefab,holder.transform);model.transform.localPosition=Vector3.zero;model.transform.localRotation=Quaternion.identity;
  foreach(var c in model.GetComponentsInChildren<Collider>(true))c.enabled=false;
  foreach(var a in model.GetComponentsInChildren<Animator>(true)){a.enabled=false;a.applyRootMotion=false;}
  foreach(var r in model.GetComponentsInChildren<SkinnedMeshRenderer>(true))r.updateWhenOffscreen=true;
  Layer(holder);
  // Bounds before turning the holder gives a stable geometric height, including rigs.
  var rs=model.GetComponentsInChildren<Renderer>(true);if(rs.Length==0)throw new Exception("No renderer "+entry.path);
  var bounds=rs[0].bounds;foreach(var r in rs)bounds.Encapsulate(r.bounds);
  var factor=height/Mathf.Max(.01f,bounds.size.y);model.transform.localScale*=factor;
  bounds=rs[0].bounds;foreach(var r in rs)bounds.Encapsulate(r.bounds);
  model.transform.position+=new Vector3(pos.x-bounds.center.x,pos.y-bounds.min.y,pos.z-bounds.center.z);
  if(!usedAssetPaths.Contains(entry.path))usedAssetPaths.Add(entry.path);
  actorModels[holder]=model;return holder;
  #else
  return null;
  #endif
 }
 protected GameObject Actor(string name,Vector3 pos,bool alternate=false,float height=2.6f,float yaw=0){var o=Asset(alternate?"heroAlt":"hero",pos,height,yaw);o.name=name;Pose(o,"Idle_A",0);return o;}
 protected void Pose(GameObject actor,string clipName,float seconds){
  if(actor)pendingPoses[actor]=(clipName,seconds);
 }
 // Resolve the final requested pose once per actor/frame. Intermediate default
 // poses must not prime Unity's sampling cache before the scene's override.
 public void FlushPoses(){
  foreach(var pair in pendingPoses)ApplyPose(pair.Key,pair.Value.clip,pair.Value.seconds);
  pendingPoses.Clear();
 }
 void ApplyPose(GameObject actor,string clipName,float seconds){
  #if UNITY_EDITOR
  if(!actorModels.TryGetValue(actor,out var model))return;
  if(!clips.TryGetValue(clipName,out var clip)){
   var resolved=clipName.StartsWith("Fight_")?clipName.Replace("Fight_","FightM_"):clipName;
   var path=Library+"011-cartoon-city-massive-pack-characters-unity-godot-fbx/Characters Full/Unity FBX/Animations/"+resolved+".fbx";
   clip=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().FirstOrDefault(c=>!c.name.StartsWith("__preview__"));if(!clip)throw new Exception("Animation unavailable: "+path);
   clips[clipName]=clip;if(!usedAnimationPaths.Contains(path))usedAnimationPaths.Add(path);
  }
  var p=model.transform.localPosition;var q=model.transform.localRotation;var s=model.transform.localScale;
  clip.SampleAnimation(model,Mathf.Repeat(Mathf.Max(0,seconds),Mathf.Max(.001f,clip.length)));
  model.transform.localPosition=p;model.transform.localRotation=q;model.transform.localScale=s;
  #endif
 }
 protected GameObject Box(string name,Vector3 pos,Vector3 size,Color color){return Primitive(name,PrimitiveType.Cube,pos,size,color);}
 protected GameObject Sphere(string name,Vector3 pos,float diameter,Color color){return Primitive(name,PrimitiveType.Sphere,pos,Vector3.one*diameter,color);}
 GameObject Primitive(string name,PrimitiveType type,Vector3 pos,Vector3 scale,Color color){var o=GameObject.CreatePrimitive(type);o.name=name;o.transform.SetParent(transform,false);o.transform.localPosition=pos;o.transform.localScale=scale;var c=o.GetComponent<Collider>();if(c)DestroyImmediate(c);o.GetComponent<Renderer>().sharedMaterial=Mat(color);Layer(o);return o;}
 protected GameObject Line(string name,Vector3[] pts,Color color,float width=.04f){var o=new GameObject(name);o.transform.SetParent(transform,false);o.layer=29;var l=o.AddComponent<LineRenderer>();l.useWorldSpace=false;l.positionCount=pts.Length;l.SetPositions(pts);l.widthMultiplier=width;l.numCapVertices=6;l.numCornerVertices=5;l.sharedMaterial=Mat(color,true);return o;}
 protected void Tint(GameObject o,Color color){foreach(var r in o.GetComponentsInChildren<Renderer>(true))r.sharedMaterial=Mat(color);}
 public static void Layer(GameObject o){foreach(var t in o.GetComponentsInChildren<Transform>(true))t.gameObject.layer=29;}
 protected Text Label(string text,float x,float y,int size=44,Color? color=null,float width=800,float height=80){
  var o=new GameObject("Label: "+text,typeof(RectTransform));o.transform.SetParent(canvas.transform,false);o.layer=29;var r=o.GetComponent<RectTransform>();r.anchorMin=r.anchorMax=new Vector2(.5f,.5f);r.sizeDelta=new Vector2(width,height);r.anchoredPosition=new Vector2(x-960,540-y);
  var t=o.AddComponent<Text>();t.font=font;t.text=text;t.fontSize=size;t.color=color??White;t.alignment=TextAnchor.MiddleCenter;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;t.supportRichText=true;t.raycastTarget=false;return t;
 }
 protected Image RectUI(float x,float y,float width,float height,Color color){var o=new GameObject("Visual region",typeof(RectTransform));o.transform.SetParent(canvas.transform,false);o.layer=29;var r=o.GetComponent<RectTransform>();r.anchorMin=r.anchorMax=new Vector2(.5f,.5f);r.sizeDelta=new Vector2(width,height);r.anchoredPosition=new Vector2(x-960,540-y);var i=o.AddComponent<Image>();i.color=color;i.raycastTarget=false;return i;}
 protected Texture2D ReferenceTexture(string path){
  #if UNITY_EDITOR
  string hash;using(var alg=SHA256.Create())using(var f=File.OpenRead(path))hash=BitConverter.ToString(alg.ComputeHash(f)).Replace("-","").ToLowerInvariant();
  var folder=Root+"/Generated/ReferenceImages";Directory.CreateDirectory(folder);var dest=folder+"/"+hash+Path.GetExtension(path).ToLowerInvariant();
  if(!File.Exists(dest)){File.Copy(path,dest);AssetDatabase.ImportAsset(dest,ImportAssetOptions.ForceSynchronousImport);}
  var importer=(TextureImporter)AssetImporter.GetAtPath(dest);
  if(importer.textureType!=TextureImporterType.Sprite){importer.textureType=TextureImporterType.Sprite;importer.spriteImportMode=SpriteImportMode.Single;importer.mipmapEnabled=false;importer.textureCompression=TextureImporterCompression.Uncompressed;importer.maxTextureSize=2048;importer.SaveAndReimport();}
  if(!usedAssetPaths.Contains(dest))usedAssetPaths.Add(dest);
  File.WriteAllText(dest+".source.json",JsonUtility.ToJson(new SourceImage{source=path,sha256=hash,asset=dest},true));
  return AssetDatabase.LoadAssetAtPath<Texture2D>(dest);
  #else
  return null;
  #endif
 }
 [Serializable]class SourceImage{public string source,sha256,asset;}
 protected Image Picture(string path,float x,float y,float width,float height){
  var i=RectUI(x,y,width,height,White);var texture=ReferenceTexture(path);
  #if UNITY_EDITOR
  i.sprite=AssetDatabase.LoadAssetAtPath<Sprite>(AssetDatabase.GetAssetPath(texture));
  #endif
  i.preserveAspect=true;return i;
 }
}
}
