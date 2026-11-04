using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Yamyam.GameMath.LightLab {
 [Serializable] public class LabCue {
  public string id, section, termEnglish, termKorean, plainMeaning, sourceKind="우리 구현 · 국소 조명";
  public string variable="none";
  public float from, to, duration=8, cardSeconds=2.5f;
  public int model=0, diffuseModel=0, shading=0, lightType=0, attenuation=0, volumeMode=0;
  public float exponent=24, referenceDistance=2, innerRange=0, range=6, innerAngle=28, outerAngle=50;
  public Vector4 components=new Vector4(1,1,1,0);
  public bool normalArrow=true, lightArrow=true, reflectionArrow=false, viewArrow=false, halfArrow=false;
  public bool urpLit=false, cookie=false, aimAtSubject=true;
  public bool brdfNormalizedDiffuse=false;
  public bool materialMap=false;
  public float secondLightStrength=0;
  public Vector3 secondLightDirection=new Vector3(1,-1,0);
  public Color secondLightColor=new Color(.3f,.4f,.6f);
  public Vector3 cameraPosition=new Vector3(6,4,-8);
  public Vector3 lightPosition=new Vector3(-2,3,-2);
  public Vector3 lightEuler=new Vector3(45,-35,0);
  public Vector3 volumeSize=new Vector3(6,4,6);
  public Color diffuse=new Color(.48f,.48f,.48f), specular=new Color(.75f,.75f,.75f),lightColor=Color.white;
  public Color ambient=new Color(.025f,.025f,.025f), emission=Color.black;
  public string formula="";
  public string goboKind="circle",falloffKind="symmetric";
  public string diagram="";
  public int diagramVariant=0;
  public float[] stepTimes;
  public float[] valueTimes, values;
  public Vector4[] componentSteps;
  public bool showLamp=true;
  public string[] explanationSteps;
  public string bakeMode="",bakeAction="";
 }
 [ExecuteAlways] public sealed partial class LightLabStage:MonoBehaviour {
  const string LibraryRoot="Assets/ThirdParty/YamyamAssetLibrary/002-analog-memory-80s-90s-crt-vhs-rooms-godot-unity-blend/EmaceArt/it`s 80`s/";
  public const string RobotPrefab=LibraryRoot+"Prefabs/Child Room/Toys/EAThe80_Robot_Toy_01a_PRE.prefab";
  public const string LampPrefab=LibraryRoot+"Prefabs/Kitchen/Props/EAThe80_Lamp_Red_01a_PRE.prefab";
  public Camera RenderCamera;
  public Transform TeachingProbe {get {return surfaceProbe;}}
  public Vector3 CurrentLightPosition {get;private set;}
  public Vector3 CurrentLightDirection {get;private set;}
  public LabCue Cue;
  public List<UnityEngine.Object> GeneratedObjects=new List<UnityEngine.Object>();
  [SerializeField] Material teaching, lit, neutral, lines;
  [SerializeField] Transform objectRoot, lampRoot;
  [SerializeField] Transform surfaceProbe;
  [SerializeField] Light physicalLight;
  [SerializeField] Text english, korean, meaning, kind, value, formula;
  [SerializeField] Text[] vectorLabels;
  [SerializeField] Canvas canvas;
  [SerializeField] LineRenderer normal, towardLight, reflection, towardViewer, halfway;
  [SerializeField] LineRenderer[] cone;
  [SerializeField] LightLabIllustrations illustrations;
  [SerializeField] MeshRenderer[] subjectRenderers;
  [SerializeField] LightLabBakedRoom bakedRoom;
  static readonly Color Yellow=new Color(1,.83f,.25f), Cyan=new Color(.27f,.87f,.9f), Green=new Color(.40f,.9f,.58f), Pink=new Color(1,.42f,.57f);
  void OnEnable(){if(canvas){var font=Font.CreateDynamicFontFromOSFont("Malgun Gothic",48);foreach(var label in canvas.GetComponentsInChildren<Text>(true))label.font=font;}}
  public void Build(LabCue cue, Font font) {
   Cue=cue;
   if(cue.range<=cue.innerRange&&cue.attenuation==2)throw new ArgumentException("Linear falloff requires outer range greater than inner range");
   if(cue.brdfNormalizedDiffuse&&cue.diffuseModel!=0)throw new ArgumentException("Half-Lambert is not the normalized Lambert BRDF");
   if(!font) throw new InvalidOperationException("The approved readable Korean font must be supplied.");
   teaching=NewMaterial("Yamyam/Teaching/LocalIllumination",Color.white);
   lit=NewMaterial("Universal Render Pipeline/Lit",cue.diffuse);
   lit.SetFloat("_Metallic",0); lit.SetFloat("_Smoothness",.55f);
   neutral=NewMaterial("Universal Render Pipeline/Lit",new Color(.045f,.045f,.045f));
   lines=NewMaterial("Universal Render Pipeline/Unlit",Color.white);
   var cameraObject=NewObject("Locked teaching camera");
   RenderCamera=cameraObject.AddComponent<Camera>(); RenderCamera.enabled=false;
   RenderCamera.transform.position=cue.cameraPosition; RenderCamera.transform.LookAt(new Vector3(0,1.35f,0));
   RenderCamera.orthographic=true;RenderCamera.orthographicSize=3.8f; RenderCamera.aspect=16f/9f;
   RenderCamera.clearFlags=CameraClearFlags.SolidColor;RenderCamera.backgroundColor=Color.black;
   RenderCamera.allowHDR=false; RenderCamera.allowMSAA=true;
   RenderCamera.nearClipPlane=.1f;RenderCamera.farClipPlane=50;
   objectRoot=InstantiateAsset(RobotPrefab,"Same robot · material test object",new Vector3(-.7f,.15f,0),2.5f);
   subjectRenderers=objectRoot.GetComponentsInChildren<MeshRenderer>(true);
   foreach(var filter in objectRoot.GetComponentsInChildren<MeshFilter>(true)) {
    var m=TeachingMesh(filter.sharedMesh);GeneratedObjects.Add(m);filter.sharedMesh=m;
   }
   foreach(var r in subjectRenderers){r.gameObject.layer=29;var ms=r.sharedMaterials;for(int n=0;n<ms.Length;n++)ms[n]=cue.urpLit?lit:teaching;r.sharedMaterials=ms;}
   lampRoot=InstantiateAsset(LampPrefab,"Owned desk lamp · light position indicator",cue.lightPosition,.9f);
   var lampMaterial=NewMaterial("Universal Render Pipeline/Lit",new Color(.55f,.23f,.12f));
   foreach(var renderer in lampRoot.GetComponentsInChildren<Renderer>(true)){var ms=renderer.sharedMaterials;for(int i=0;i<ms.Length;i++)ms[i]=lampMaterial;renderer.sharedMaterials=ms;}
   var lightObject=NewObject("Actual URP light (engine-output variant only)"); physicalLight=lightObject.AddComponent<Light>();
   physicalLight.shadows=LightShadows.Soft;physicalLight.intensity=2;physicalLight.range=cue.range;
   var floor=GameObject.CreatePrimitive(PrimitiveType.Cylinder);floor.name="Material-lab turntable";floor.transform.SetParent(transform,false);
   floor.transform.position=new Vector3(-.7f,0,0);floor.transform.localScale=new Vector3(2.3f,.09f,2.3f);floor.GetComponent<Renderer>().sharedMaterial=neutral;
   normal=Arrow("N · surface normal",Green);towardLight=Arrow("L · toward light",Yellow);reflection=Arrow("R · reflected direction",Pink);
   towardViewer=Arrow("V · toward viewer",Cyan);halfway=Arrow("H · halfway direction",new Color(.85f,.65f,1));
   var probe=GameObject.CreatePrimitive(PrimitiveType.Cylinder);probe.name="Visible horizontal teaching probe · known N";probe.transform.SetParent(transform,false);probe.transform.position=new Vector3(1.4f,1.26f,0);probe.transform.localScale=new Vector3(.7f,.035f,.7f);probe.gameObject.layer=29;probe.GetComponent<Renderer>().sharedMaterial=cue.urpLit?lit:teaching;var probeMesh=TeachingMesh(probe.GetComponent<MeshFilter>().sharedMesh);GeneratedObjects.Add(probeMesh);probe.GetComponent<MeshFilter>().sharedMesh=probeMesh;surfaceProbe=probe.transform;
   cone=new LineRenderer[4];for(int i=0;i<4;i++)cone[i]=Arrow("Spot boundary "+i,Yellow);
   BuildUI(font);
   if(!string.IsNullOrEmpty(cue.bakeMode)){
    if(!cue.urpLit)throw new InvalidOperationException("Real baking requires the engine Lit material, not the teaching shader");
    bakedRoom=gameObject.AddComponent<LightLabBakedRoom>();bakedRoom.Build(this,cue,physicalLight,objectRoot,neutral);
   }
   if(cue.diagram=="specularGrid")BuildComparison(font);
   else if(!string.IsNullOrEmpty(cue.diagram)){var illustrationObject=NewObject("Source-matched explanatory diagrams");illustrations=illustrationObject.AddComponent<LightLabIllustrations>();illustrations.Build(this,cue,font,objectRoot);}
   Apply(0);
  }
  GameObject NewObject(string name){var g=new GameObject(name);g.transform.SetParent(transform,false);return g;}
  Material NewMaterial(string shaderName,Color c){var s=Shader.Find(shaderName);if(!s)throw new InvalidOperationException("Missing shader "+shaderName);var m=new Material(s){name="M21 "+shaderName};m.SetColor("_BaseColor",c);GeneratedObjects.Add(m);return m;}
  Transform InstantiateAsset(string path,string name,Vector3 position,float height) {
#if UNITY_EDITOR
   var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);
   if(!prefab)throw new InvalidOperationException("Owned model missing; do not silently replace: "+path);
   var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,transform);go.name=name;
   foreach(var lod in go.GetComponentsInChildren<LODGroup>())lod.ForceLOD(0);
   var rr=go.GetComponentsInChildren<Renderer>();if(rr.Length==0)throw new Exception("No model renderers "+path);
   Bounds bounds=rr[0].bounds;foreach(var r in rr)bounds.Encapsulate(r.bounds);
   float scale=height/Mathf.Max(.0001f,bounds.size.y);go.transform.localScale*=scale;
   go.transform.position=position-new Vector3(bounds.center.x,bounds.min.y,bounds.center.z)*scale;
   return go.transform;
#else
   throw new InvalidOperationException("Build is an editor-only authoring step; reopen the saved scene for playback.");
#endif
  }
  public void Apply(float seconds) {
   if(Cue==null||!teaching)return;
   float u=Mathf.Clamp01(seconds/Mathf.Max(.001f,Cue.duration));u=u*u*(3-2*u);
   float change=Mathf.Lerp(Cue.from,Cue.to,u);
   if(Cue.valueTimes!=null && Cue.values!=null && Cue.valueTimes.Length==Cue.values.Length && Cue.values.Length>0){
    change=Cue.values[0];
    for(int i=1;i<Cue.valueTimes.Length;i++)if(seconds>=Cue.valueTimes[i-1]){
     float interval=Mathf.Max(.001f,Cue.valueTimes[i]-Cue.valueTimes[i-1]);
     float phase=Mathf.Clamp01((seconds-Cue.valueTimes[i-1])/interval);phase=phase*phase*(3-2*phase);
     change=Mathf.Lerp(Cue.values[i-1],Cue.values[i],phase);
    }
   }
   Vector3 pos=Cue.lightPosition;Vector3 direction=Cue.aimAtSubject?(new Vector3(-.7f,1.3f,0)-pos).normalized:Quaternion.Euler(Cue.lightEuler)*Vector3.forward;
   float exponent=Cue.exponent;
   if(Cue.variable=="lightAzimuth") {pos=Quaternion.AngleAxis(change,Vector3.up)*Cue.lightPosition;direction=(new Vector3(-.7f,1.3f,0)-pos).normalized;}
   if(Cue.variable=="lightDistance") pos=surfaceProbe.position+surfaceProbe.up*.035f+Cue.lightPosition.normalized*change;
   if(Cue.variable=="exponent")exponent=change;
   if(Cue.variable=="objectYaw")objectRoot.localRotation=Quaternion.Euler(0,change,0);
   if(Cue.variable=="normalTilt"){surfaceProbe.rotation=Quaternion.Euler(0,0,change);objectRoot.localRotation=Quaternion.Euler(0,0,change);}
   if(Cue.variable=="viewAzimuth") {RenderCamera.transform.position=Quaternion.AngleAxis(change,Vector3.up)*Cue.cameraPosition;RenderCamera.transform.LookAt(new Vector3(0,1.35f,0));}
   CurrentLightPosition=pos;CurrentLightDirection=direction;
   physicalLight.enabled=true;physicalLight.cullingMask=Cue.urpLit?~0:~(1<<29);physicalLight.type=Cue.lightType==0?LightType.Directional:(Cue.lightType==1?LightType.Point:LightType.Spot);
   physicalLight.transform.position=pos;physicalLight.transform.rotation=Quaternion.LookRotation(direction);
   physicalLight.spotAngle=Cue.outerAngle;physicalLight.innerSpotAngle=Cue.innerAngle;
   // Props are visible context, not a fabricated camera-visible light beam.
   lampRoot.position=pos;lampRoot.rotation=Quaternion.LookRotation(direction);lampRoot.gameObject.SetActive(Cue.showLamp);
   teaching.SetColor("_BaseColor",Cue.diffuse);teaching.SetColor("_SpecColor",Cue.specular);
   teaching.SetColor("_AmbientColor",Cue.ambient);teaching.SetColor("_EmissionColor",Cue.emission);
   teaching.SetColor("_LightColor",Cue.lightColor);
   teaching.SetColor("_SecondLightColor",Cue.secondLightColor);
   teaching.SetVector("_SecondLightDirection",Cue.secondLightDirection);
   teaching.SetFloat("_SecondLightStrength",Cue.variable=="secondLightStrength"?change:Cue.secondLightStrength);
   if(Cue.variable=="specularStrength")teaching.SetColor("_SpecColor",Cue.specular*change);
   if(Cue.variable=="ambientStrength")teaching.SetColor("_AmbientColor",Cue.ambient*change);
   if(Cue.variable=="emissionStrength")teaching.SetColor("_EmissionColor",Cue.emission*change);
   Vector4 components=Cue.components;
   if(Cue.componentSteps!=null && Cue.stepTimes!=null){for(int i=0;i<Mathf.Min(Cue.componentSteps.Length,Cue.stepTimes.Length);i++)if(seconds>=Cue.stepTimes[i])components=Cue.componentSteps[i];}
   teaching.SetVector("_Components",components);teaching.SetVector("_LightPosition",pos);
   teaching.SetVector("_LightDirection",direction);teaching.SetVector("_ViewPosition",RenderCamera.transform.position);
   teaching.SetFloat("_UseOrthographicView",RenderCamera.orthographic?1:0);
   teaching.SetVector("_OrthographicViewDirection",-RenderCamera.transform.forward);
   teaching.SetFloat("_Exponent",exponent);teaching.SetFloat("_SpecularModel",Cue.model);teaching.SetFloat("_ShadingMode",Cue.shading);
   teaching.SetFloat("_MaterialMapEnabled",Cue.materialMap?1:0);
   teaching.SetFloat("_DiffuseScale",Cue.brdfNormalizedDiffuse?1/Mathf.PI:1);
   teaching.SetFloat("_DiffuseModel",Cue.diffuseModel);
   teaching.SetFloat("_LightType",Cue.lightType);teaching.SetFloat("_Attenuation",Cue.attenuation);
   teaching.SetFloat("_ReferenceDistance",Cue.referenceDistance);teaching.SetFloat("_Range",Cue.range);
   teaching.SetFloat("_InnerRange",Cue.innerRange);
   teaching.SetVector("_SpotCosines",new Vector4(Mathf.Cos(Cue.innerAngle*Mathf.Deg2Rad*.5f),Mathf.Cos(Cue.outerAngle*Mathf.Deg2Rad*.5f),0,0));
   teaching.SetFloat("_VolumeMode",Cue.volumeMode);teaching.SetFloat("_UseCookie",Cue.cookie?1:0);
   teaching.SetMatrix("_WorldToLight",Matrix4x4.TRS(pos,Quaternion.LookRotation(direction),Vector3.one).inverse);
   teaching.SetMatrix("_LightToTexture",Projection(Cue.volumeSize,Cue.volumeMode==2||Cue.lightType==3));
   // The sample plane is a teaching probe, separate from a guessed robot normal.
   Vector3 p=surfaceProbe.position+surfaceProbe.up*.035f;Vector3 n=surfaceProbe.up;
   Vector3 l=Cue.lightType==0?-direction:(pos-p).normalized,v=RenderCamera.orthographic?-RenderCamera.transform.forward:(RenderCamera.transform.position-p).normalized;
   Vector3 r=2*Vector3.Dot(n,l)*n-l,h=(l+v).normalized;
   SetArrow(normal,p,n,Cue.normalArrow);SetArrow(towardLight,p,l,Cue.lightArrow);SetArrow(reflection,p,r,Cue.reflectionArrow);
   SetArrow(towardViewer,p,v,Cue.viewArrow);SetArrow(halfway,p,h,Cue.halfArrow);
   var directions=new[]{n,l,r,v,h};var enabled=new[]{Cue.normalArrow,Cue.lightArrow,Cue.reflectionArrow,Cue.viewArrow,Cue.halfArrow};
   for(int i=0;i<5;i++){vectorLabels[i].gameObject.SetActive(enabled[i]);if(enabled[i]){var q=RenderCamera.WorldToViewportPoint(p+directions[i].normalized*1.28f);vectorLabels[i].rectTransform.anchoredPosition=new Vector2(q.x*1920,(q.y-1)*1080);}}
   for(int i=0;i<4;i++){float a=i*Mathf.PI*.5f;Vector3 local=new Vector3(Mathf.Cos(a),Mathf.Sin(a),0)*Mathf.Tan(Cue.outerAngle*Mathf.Deg2Rad*.5f)*2+Vector3.forward*2;SetArrow(cone[i],pos,Quaternion.LookRotation(direction)*local,Cue.lightType>=2,false);}
   value.text="";
   if(Cue.normalArrow){float d=Mathf.Max(0,Vector3.Dot(n,l));value.text="해설용 표면 지점   N · L = "+d.ToString("0.00")+(Cue.brdfNormalizedDiffuse?"\nBRDF: ρ / π":"\n고전적 재질 계수 · 수업용 단위");}
   if(Cue.variable=="exponent")value.text="광택 지수 n = "+exponent.ToString("0");
   if(Cue.variable=="lightDistance")value.text="우리 씬의 거리 d = "+change.ToString("0.0")+" m";
   bool card=seconds<Cue.cardSeconds;english.gameObject.SetActive(card);meaning.gameObject.SetActive(card);
   korean.rectTransform.anchoredPosition=new Vector2(96,card?-106:-64);kind.text=Cue.urpLit?"Unity URP Lit · 엔진 출력":Cue.sourceKind;
   if(illustrations){kind.text="우리 씬 + 해설용 도식";value.gameObject.SetActive(false);formula.gameObject.SetActive(false);illustrations.Apply(seconds);}
   if(Cue.diagram=="specularGrid")ApplyComparison(seconds);
   if(bakedRoom)bakedRoom.Apply(seconds);
  }
  public void SetMaps(Texture2D gobo,Texture2D falloff){teaching.SetTexture("_Cookie",gobo);teaching.SetTexture("_Falloff",falloff);}
  public void SetMaterialMaps(Texture2D diffuseMap,Texture2D specularMap){teaching.SetTexture("_MaterialMap",diffuseMap);teaching.SetTexture("_SpecularMap",specularMap);}
  // Column-vector equivalents of the source article's row-vector matrices.
  public static Matrix4x4 Projection(Vector3 s,bool perspective) {
   if(s.x<=0||s.y<=0||s.z<=0)throw new ArgumentException("Positive volume dimensions required");
   var m=Matrix4x4.zero;
   if(!perspective){m.m00=1/s.x;m.m11=-1/s.y;m.m22=1/s.z;m.m03=.5f;m.m13=.5f;m.m23=.5f;m.m33=1;}
   else {m.m00=s.z/s.x;m.m11=-s.z/s.y;m.m02=.5f;m.m12=.5f;m.m22=1/s.z;m.m32=1;}
   return m;
  }
  LineRenderer Arrow(string name,Color c){var g=NewObject(name);var lr=g.AddComponent<LineRenderer>();lr.useWorldSpace=true;lr.sharedMaterial=lines;lr.startColor=lr.endColor=c;lr.widthMultiplier=.023f;lr.numCapVertices=5;lr.positionCount=5;return lr;}
  void SetArrow(LineRenderer line,Vector3 p,Vector3 d,bool enabled,bool normalize=true){line.enabled=enabled;if(!enabled)return;Vector3 delta=normalize?d.normalized*1.1f:d;Vector3 q=p+delta;Vector3 side=Vector3.Cross(delta,RenderCamera.transform.forward).normalized*.09f;Vector3 back=q-delta.normalized*.2f;line.SetPositions(new[]{p,q,back+side,q,back-side});}
  void BuildUI(Font font){
   var g=NewObject("Overlay · caption area reserved");canvas=g.AddComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=RenderCamera;canvas.planeDistance=1;canvas.sortingOrder=100;
   var scaler=g.AddComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1920,1080);
   english=Label(font,Cue.termEnglish,30,96,60,1300,46,Color.white);
   korean=Label(font,Cue.termKorean,52,96,106,1400,66,Yellow);
   meaning=Label(font,Cue.plainMeaning,36,96,176,1450,64,Color.white);
   kind=Label(font,Cue.sourceKind,30,1360,64,480,90,Color.white);
   value=Label(font,"",36,1100,620,720,64,Green);
   formula=Label(font,Cue.formula,40,1100,700,720,128,Color.white);
   vectorLabels=new[]{Label(font,"법선 N",34,0,0,200,48,Green),Label(font,"빛 L",34,0,0,200,48,Yellow),Label(font,"반사 R",34,0,0,200,48,Pink),Label(font,"시선 V",34,0,0,200,48,Cyan),Label(font,"중간 H",34,0,0,200,48,new Color(.85f,.65f,1))};
  }
  Text Label(Font font,string s,int size,float x,float y,float w,float h,Color c){var g=new GameObject(s,typeof(RectTransform));g.transform.SetParent(canvas.transform,false);var t=g.AddComponent<Text>();t.font=font;t.text=s;t.fontSize=size;t.color=c;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;var r=t.rectTransform;r.anchorMin=r.anchorMax=r.pivot=new Vector2(0,1);r.anchoredPosition=new Vector2(x,-y);r.sizeDelta=new Vector2(w,h);return t;}
  public static Mesh TeachingMesh(Mesh input){
   if(!input||!input.isReadable)throw new InvalidOperationException("Model must have readable CPU vertices for verified face/Gouraud comparison.");
   var verts=input.vertices;var normals=input.normals;var originalUV=input.uv;var uvs=new List<Vector2>();var vv=new List<Vector3>();var nn=new List<Vector3>();var centres=new List<Vector3>();var faceNormals=new List<Vector3>();var tris=new List<int[]>();
   for(int sub=0;sub<input.subMeshCount;sub++){var indices=input.GetTriangles(sub);var dst=new int[indices.Length];for(int i=0;i<indices.Length;i+=3){Vector3 a=verts[indices[i]],b=verts[indices[i+1]],c=verts[indices[i+2]],centre=(a+b+c)/3,face=Vector3.Cross(b-a,c-a).normalized;for(int k=0;k<3;k++){int index=indices[i+k];dst[i+k]=vv.Count;vv.Add(verts[index]);uvs.Add(originalUV.Length==verts.Length?originalUV[index]:Vector2.zero);nn.Add(normals.Length==verts.Length?normals[index]:face);centres.Add(centre);faceNormals.Add(face);}}tris.Add(dst);}
   var mesh=new Mesh{name=input.name+" · educational face data",indexFormat=UnityEngine.Rendering.IndexFormat.UInt32};mesh.SetVertices(vv);mesh.SetNormals(nn);mesh.SetUVs(0,uvs);mesh.SetUVs(2,centres);mesh.SetUVs(3,faceNormals);mesh.subMeshCount=tris.Count;for(int s=0;s<tris.Count;s++)mesh.SetTriangles(tris[s],s);mesh.RecalculateBounds();return mesh;
  }
 }
}
