// A02-owned stage. Source-backed reconstruction is explicit; old A01 scenes stay unchanged.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Yamyam.AnimationSeries {
public sealed class AnimationExaggerationStage : AnimationLessonStage {
 public string presentationId;
 public string presentationProfilePath;
 [TextArea(4,20)] public string profileSnapshotJson;
 public string sourceCodeFingerprint;
 public float editorPreviewSeconds;
 protected override string ProductionSlug => "animation-exaggeration";
 protected override string StageSourceName => "AnimationExaggerationStage.cs";
 protected override string PresentationSourceName => "animation-exaggeration-presentations.json";
 protected override string GeneratedAssetRoot => "Assets/VideoScenes/animation-exaggeration/grid-v1";
 public const string PunchClip = "FightM_Punch_A";
 const int LeftLayer = 27, RightLayer = 28;
 const float Fps = 60f, ActorHeight = 2.7f;
 const int PanelWidth = 800, PanelHeight = 570;
 const float PanelTop = 250f;
 static readonly Color Ink = Hex("252B30"), GridBg = Hex("EDEDEB");
 static readonly Color GridMajor = Hex("B6BBBD"), GridMinor = Hex("D3D6D6");
 static readonly Color AxisRed = Hex("C9444E"), AxisBlue = Hex("527DAA");
 static Type DirectMeshComponent => Type.GetType("UnityEngine.Rendering.DisallowGPUDrivenRendering, Unity.RenderPipelines.GPUDriven.Runtime",true);

 // Times are measured speech/edit-relative seconds supplied by the editor.
 // Each phase is contiguous, explicit and finite. No hidden loop or time stretching.
 [Serializable] public sealed class Cue {
  public int phase;
  public float start, end, motionStart, motionDuration;
  public string replayReason,holdNativeAt;
 }
 [Serializable] public sealed class Profile {
  public string id, episode, revision, mode;
  public float duration, freezeSeconds;
  // Zero means retain the established per-mode view. A selected cut may use
  // another authored yaw when foreshortening would hide its teaching target.
  public float actorYawDegrees;
  public Cue[] phases;
 }
 [Serializable] public sealed class ProfileBook {
  public int schemaVersion;
  public Profile[] presentations;
 }
 [Serializable] public sealed class ArmEvidence {
  public string side;
  public float upperLength, lowerLength, endpointError;
  public Vector3 targetPanelLocal, wristPanelLocal, shoulderPanelLocal;
 }
 // Inspect after FlushPoses; these values belong only to this authored scene.
 public ArmEvidence[] lastArmEvidence = new ArmEvidence[0];
 public float lastBaselineMetres, lastOvershootMetres, lastBaselineRadius, lastOvershootRadius;
 public float lastClipSeconds;
 public string activeMode;
 public int activePhase;

 Profile profile;
 Cue cue;
 float time, phaseElapsed, motionElapsed, clipLength, appliedActorYaw;
 bool built;
 readonly List<GameObject> phaseLabels = new List<GameObject>();
 readonly List<GameObject> leftHeaders = new List<GameObject>();
 readonly List<GameObject> rightHeaders = new List<GameObject>();
 readonly List<UnityEngine.Object> runtimeOwned = new List<UnityEngine.Object>();
 readonly List<LineRenderer> globalGuides = new List<LineRenderer>();
 ActorRig[] rigs;
 Panel[] panels;
 RectTransform playhead;
 GameObject leftDot, rightDot, zeroLabels, targetLabels, peakLabels, differenceLabels;
 GameObject beforePlaybackLabel, afterPlaybackLabel, afterPlaybackPeakLabel;
 Mesh[] spikeMeshes;
 Vector3[][] spikeVertices;
 GameObject[] spikeObjects;
 LineRenderer[] radiusGuides;
 Mesh bakeScratch;

 sealed class TransformState {
  public Transform transform;
  public Vector3 position, scale;
  public Quaternion rotation;
  public TransformState(Transform t) {
   transform=t; position=t.localPosition; rotation=t.localRotation; scale=t.localScale;
  }
  public void Restore() {
   transform.localPosition=position; transform.localRotation=rotation; transform.localScale=scale;
  }
 }
 sealed class ActorRig {
  public GameObject actor;
  public TransformState[] rest;
  public Transform torso, shoulderL, shoulderR, arm, forearm, hand, hips, thighL, thighR, foot;
  public Quaternion referenceTorso, referenceShoulder;
  public Vector3 origin;
  public LineRenderer chain, shoulderGuide, hipGuide, footGuide, translationGuide;
  public GameObject pivotMarker, targetMarker, originalPivotMarker;
 }
 sealed class Panel {
  public Camera camera;
  public RenderTexture texture;
  public RawImage image;
  public float centreX;
  public int layer;
 }

 public override void Build() {
  if(built) throw new InvalidOperationException("A02 stage Build may run only once.");
  LoadProfile(); activeMode=profile.mode;
  if(IsActorMode(activeMode)) {
   var outerFloor=transform.Find("Light grid floor");
   if(outerFloor)outerFloor.gameObject.SetActive(false);
  } else BuildGridShell();
  RectUI(960,80,1920,160,Hex("101214"));
  RectUI(960,1000,1920,200,Hex("101214"));
  Label(TitleForMode(activeMode),735,68,54,Yellow,1320,86);
  // Compositor owns the top-right picture-kind chip and captions at (960,970).
  // No live text, leader or comparison panel enters y>=900.
  RectUI(960,875,1320,4,Hex("929B9E"));
  playhead=RectUI(300,875,12,22,AxisRed).rectTransform;
  bakeScratch=new Mesh {name="A02 grounding scratch"}; runtimeOwned.Add(bakeScratch);
  if(IsActorMode(activeMode)) {
   LoadClipLength();
   if(!Finite(profile.freezeSeconds) || profile.freezeSeconds<0 || profile.freezeSeconds>clipLength)
    throw new InvalidDataException("freezeSeconds must identify an inspected frame inside FightM_Punch_A.");
   BuildActorsAndPanels(); BuildActorLabels();
  } else if(activeMode=="linear-overshoot") BuildLinear();
  else BuildShape();
  BuildPhaseLabels();
  // Capture cameras stay disabled and are rendered explicitly after a scene
  // mask/reconstruction change. GPU Resident Drawer can retain stale static
  // mesh registration in that editor path. Keep only these owned instances on
  // Unity's synchronous mesh path; do not change the shared render pipeline.
  // The installed Core package exposes the supported component in the editor,
  // while its underlying MeshRenderer property is internal to Unity assemblies.
  var directMeshType=DirectMeshComponent;
  foreach(var renderer in GetComponentsInChildren<MeshRenderer>(true))
   if(!renderer.GetComponent(directMeshType))renderer.gameObject.AddComponent(directMeshType);
  ValidatePhaseMotion(); built=true;
 }
 void LoadProfile() {
  if(string.IsNullOrWhiteSpace(presentationId))
   throw new InvalidDataException("A02 needs an explicit measured presentation id and JSON path; no timing fallback.");
  if(!string.IsNullOrEmpty(profileSnapshotJson)) {
   profile=JsonUtility.FromJson<Profile>(profileSnapshotJson);
   if(profile==null || profile.id!=presentationId)throw new InvalidDataException("Saved A02 profile does not match its presentation id.");
  } else {
   if(string.IsNullOrWhiteSpace(presentationProfilePath))throw new InvalidDataException("Missing explicit A02 profile path.");
   var book=JsonUtility.FromJson<ProfileBook>(File.ReadAllText(presentationProfilePath));
   if(book==null || book.schemaVersion!=1 || book.presentations==null)
    throw new InvalidDataException("Invalid A02 presentation book.");
   var matches=book.presentations.Where(p=>p!=null && p.id==presentationId).ToArray();
   if(matches.Length!=1) throw new InvalidDataException("A02 presentation id is missing or ambiguous.");
   profile=matches[0];profileSnapshotJson=JsonUtility.ToJson(profile,true);
  }
  if(profile.episode!="A02" || profile.revision!="grid-v1" || slug!="animation-exaggeration")
   throw new InvalidDataException("A02 presentation episode/revision/slug mismatch.");
  if(frames<1 || !Finite(profile.duration) || Mathf.Abs(profile.duration-frames/Fps)>.001f)
   throw new InvalidDataException("Measured A02 duration must equal capture frame duration.");
  if(!new[]{"normal-and-pause","size-amplitude","shoulder-control","paused-pose-context","linear-overshoot","shape-overshoot"}.Contains(profile.mode))
   throw new InvalidDataException("Unknown A02 mode.");
  if(!Finite(profile.actorYawDegrees) || Mathf.Abs(profile.actorYawDegrees)>360 ||
     (!IsActorMode(profile.mode) && profile.actorYawDegrees!=0))
   throw new InvalidDataException("Actor view override must be a finite angle in an actor mode.");
  if(profile.phases==null || profile.phases.Length==0) throw new InvalidDataException("A02 has no speech phases.");
  float end=0; int priorPhase=-1;
  foreach(var p in profile.phases) {
   if(p==null || !Finite(p.start) || !Finite(p.end) || !Finite(p.motionStart) || !Finite(p.motionDuration) ||
      p.start!=end || p.end<=p.start || p.motionStart<0 || p.motionDuration<0 ||
      p.motionStart>p.end-p.start || p.phase<0 || p.phase<priorPhase || p.phase>=PhaseCount(profile.mode) ||
      (p.phase==priorPhase && string.IsNullOrWhiteSpace(p.replayReason)) ||
      (!string.IsNullOrEmpty(p.holdNativeAt) && p.holdNativeAt!="end" && p.holdNativeAt!="peak"))
    throw new InvalidDataException("A02 phases must cover the cut in explicit contiguous order.");
   end=p.end;priorPhase=p.phase;
  }
  if(end!=profile.duration) throw new InvalidDataException("A02 phases do not cover the measured duration.");
 }
 static bool Finite(float f) {return !float.IsNaN(f) && !float.IsInfinity(f);}
 static bool IsActorMode(string mode) {return mode!="linear-overshoot" && mode!="shape-overshoot";}
 static int PhaseCount(string mode) {
  if(mode=="shoulder-control") return 4;
  if(mode=="linear-overshoot") return 5;
  if(mode=="shape-overshoot") return 4;
  return 3;
 }
 static string TitleForMode(string mode) {
  switch(mode) {
   case "normal-and-pause": return "동작의 과장 · 움직임과 정지 자세";
   case "size-amplitude": return "동작의 과장 · 실제 화면 크기";
   case "shoulder-control": return "리그 (Rig) · 회전과 이동";
   case "paused-pose-context": return "움직임 전체 → 필요한 순간";
   case "linear-overshoot": return "오버슈트 (Overshoot) · 목표를 지나 돌아오기";
   default: return "오버슈트 · 모양의 변화";
  }
 }
 void LoadClipLength() {
  #if UNITY_EDITOR
  string path=Library+"011-cartoon-city-massive-pack-characters-unity-godot-fbx/Characters Full/Unity FBX/Animations/"+PunchClip+".fbx";
  var clip=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().FirstOrDefault(c=>!c.name.StartsWith("__preview__"));
  if(!clip || clip.length<=0) throw new InvalidDataException("Required Generic animation is missing: "+path);
  clipLength=clip.length;
  #else
  throw new InvalidOperationException("A02 proposal is an editor-capture stage.");
  #endif
 }
 void ValidatePhaseMotion() {
  foreach(var p in profile.phases) {
   float remaining=p.end-p.start-p.motionStart;
   bool nativePlay=IsNativePlayPhase(activeMode,p.phase);
   float needed=activeMode=="paused-pose-context" && p.phase==2 ? clipLength-profile.freezeSeconds : clipLength;
   if(nativePlay && remaining+1/Fps<needed)
    throw new InvalidDataException("Phase does not leave time for the native one-shot: "+p.phase);
   if(IsAuthoredMotionPhase(activeMode,p.phase) && (p.motionDuration<=0 || p.motionDuration>remaining+.002f))
    throw new InvalidDataException("Authored demonstration needs a finite measured motionDuration within its phase.");
  }
 }
 static bool IsNativePlayPhase(string mode,int phase) {
  return (mode=="normal-and-pause" && phase!=1) || mode=="size-amplitude" ||
    (mode=="paused-pose-context" && phase!=1);
 }
 static bool IsAuthoredMotionPhase(string mode,int phase) {
  return mode=="shoulder-control" && phase>0 || mode=="linear-overshoot" && (phase==1 || phase==2) ||
    mode=="shape-overshoot" && (phase==1 || phase==3);
 }
 void BuildGridShell() {
  for(int i=-24;i<=24;i++) {
   float x=i*.25f;
   Line("Grid vertical "+i,new[]{new Vector3(x,-.02f,1.8f),new Vector3(x,5.2f,1.8f)},i%4==0?GridMajor:GridMinor,i%4==0?.014f:.007f);
  }
  for(int i=0;i<=21;i++) {
   float y=i*.25f;
   Line("Grid horizontal "+i,new[]{new Vector3(-6,y,1.8f),new Vector3(6,y,1.8f)},i%4==0?GridMajor:GridMinor,i%4==0?.014f:.007f);
  }
  Line("Floor reference",new[]{new Vector3(-6,0,-.2f),new Vector3(6,0,-.2f)},AxisRed,.025f);
  foreach(float x in new[]{-2.4f,2.4f})
   Line("Pose origin",new[]{new Vector3(x,0,1.65f),new Vector3(x,3.6f,1.65f)},AxisBlue,.018f);
 }
 void BuildActorsAndPanels() {
  rigs=new ActorRig[2]; panels=new Panel[2];
  for(int i=0;i<2;i++) {
   float worldX=i==0?-20f:20f; int layer=i==0?LeftLayer:RightLayer;
   panels[i]=BuildPanel(worldX,layer,i==0?505:1415);
   float yaw=profile.actorYawDegrees!=0?profile.actorYawDegrees:
    (activeMode=="normal-and-pause" || activeMode=="paused-pose-context")?105:160;
   appliedActorYaw=yaw;
   var actor=Actor(i==0?"Reference Generic rig":"Comparison Generic rig",new Vector3(worldX,0,0),false,ActorHeight,yaw);
   SetLayer(actor,layer);
   var r=new ActorRig {actor=actor,origin=actor.transform.position};
   r.rest=actor.GetComponentsInChildren<Transform>(true).Select(t=>new TransformState(t)).ToArray();
   r.torso=Bone(actor,"Torso"); r.shoulderL=Bone(actor,"Shoulder.L"); r.shoulderR=Bone(actor,"Shoulder.R");
   r.arm=Bone(actor,"Arm.R"); r.forearm=Bone(actor,"ForeArm.R"); r.hand=Bone(actor,"Hand.R");
   r.hips=Bone(actor,"Hips"); r.thighL=Bone(actor,"UpperLeg.L"); r.thighR=Bone(actor,"UpperLeg.R"); r.foot=Bone(actor,"Foot.L");
   if(!r.forearm.IsChildOf(r.arm) || !r.hand.IsChildOf(r.forearm) || !r.arm.IsChildOf(r.shoulderR))
    throw new InvalidDataException("Selected Generic rig has an unexpected right-arm hierarchy.");
   rigs[i]=r; PoseOnce(actor,PunchClip,0);
  }
  base.FlushPoses();
  foreach(var r in rigs) {
   r.referenceTorso=r.torso.localRotation; r.referenceShoulder=r.shoulderR.localRotation;
   int layer=r.actor.layer;
   r.chain=PanelLine("Right-arm bone guide",layer,Teal,.055f,3);
   r.shoulderGuide=PanelLine("Shoulder orientation guide",layer,Teal,.055f,2);
   r.hipGuide=PanelLine("Pelvis orientation guide",layer,Yellow,.055f,2);
   r.footGuide=PanelLine("Torso and left-foot guide",layer,AxisBlue,.055f,3);
   r.translationGuide=PanelLine("Shoulder translation guide",layer,Green,.055f,2);
   r.pivotMarker=PanelSphere("Actual arm pivot",layer,Teal,.09f);
   r.targetMarker=PanelSphere("Common hand target",layer,Green,.095f);
   r.originalPivotMarker=PanelSphere("Untranslated pivot",layer,Yellow,.075f);
   HideGuides(r);
  }
  foreach(var light in GetComponentsInChildren<Light>(true)) light.cullingMask|=(1<<LeftLayer)|(1<<RightLayer);
 }
 Panel BuildPanel(float worldX,int layer,float uiCentreX) {
  var tex=new RenderTexture(PanelWidth,PanelHeight,24,RenderTextureFormat.ARGB32) {
   name="A02 panel "+layer,antiAliasing=4,filterMode=FilterMode.Bilinear,wrapMode=TextureWrapMode.Clamp
  };
  tex.Create(); runtimeOwned.Add(tex);
  var go=new GameObject("A02 isolated panel camera "+layer); go.transform.SetParent(transform,false);
  var cam=go.AddComponent<Camera>(); cam.orthographic=true; cam.enabled=false; cam.nearClipPlane=.05f; cam.farClipPlane=50;
  cam.clearFlags=CameraClearFlags.SolidColor; cam.backgroundColor=GridBg; cam.cullingMask=1<<layer;
  cam.allowHDR=false; cam.allowMSAA=true; cam.targetTexture=tex; cam.aspect=(float)PanelWidth/PanelHeight;
  cam.GetUniversalAdditionalCameraData().renderType=CameraRenderType.Base;
  var ui=new GameObject("Independent panel "+layer); ui.layer=29; ui.transform.SetParent(canvas.transform,false);
  var rt=ui.AddComponent<RectTransform>(); rt.anchorMin=rt.anchorMax=new Vector2(.5f,.5f);
  rt.sizeDelta=new Vector2(PanelWidth,PanelHeight); rt.anchoredPosition=new Vector2(uiCentreX-960,540-(PanelTop+PanelHeight/2f));
  var image=ui.AddComponent<RawImage>(); image.texture=tex; image.raycastTarget=false;
  var panel=new Panel {camera=cam,texture=tex,image=image,centreX=worldX,layer=layer};
  SetPanelHeight(panel,440);
  for(int i=-24;i<=24;i++) {
   float x=worldX+i*.25f;
   var line=Line("Panel grid vertical "+layer+" "+i,new[]{new Vector3(x,-.03f,1.8f),new Vector3(x,7,1.8f)},i%4==0?GridMajor:GridMinor,i%4==0?.014f:.007f);
   SetLayer(line.gameObject,layer);
  }
  for(int i=0;i<=28;i++) {
   float y=i*.25f;
   var line=Line("Panel grid horizontal "+layer+" "+i,new[]{new Vector3(worldX-6,y,1.8f),new Vector3(worldX+6,y,1.8f)},i%4==0?GridMajor:GridMinor,i%4==0?.014f:.007f);
   SetLayer(line.gameObject,layer);
  }
  SetLayer(Line("Panel floor",new[]{new Vector3(worldX-6,0,-.2f),new Vector3(worldX+6,0,-.2f)},AxisRed,.025f).gameObject,layer);
  SetLayer(Line("Panel origin",new[]{new Vector3(worldX,0,1.65f),new Vector3(worldX,6,1.65f)},AxisBlue,.018f).gameObject,layer);
  SetLayer(Box("Panel ground",new Vector3(worldX,-.12f,0),new Vector3(12,.2f,6),Hex("D2D4D3")),layer);
  return panel;
 }
 void SetPanelHeight(Panel panel,float pixelHeight) {
  float size=ActorHeight*PanelHeight/(2f*pixelHeight); panel.camera.orthographicSize=size;
  // Equal screen-space floor at panel bottom-35; model scale and native clip are unchanged.
  float centreY=size*(1f-70f/PanelHeight);
  panel.camera.transform.position=new Vector3(panel.centreX,centreY,-14);
  panel.camera.transform.rotation=Quaternion.identity;
 }
 static Transform Bone(GameObject actor,string name) {
  var bone=actor.GetComponentsInChildren<Transform>(true).SingleOrDefault(t=>t.name==name);
  if(!bone) throw new InvalidDataException("Missing or duplicated Generic bone: "+name);
  return bone;
 }
 static void SetLayer(GameObject go,int layer) {foreach(var t in go.GetComponentsInChildren<Transform>(true)) t.gameObject.layer=layer;}
 new LineRenderer Line(string name,Vector3[] points,Color color,float width=.04f) {
  return base.Line(name,points,color,width).GetComponent<LineRenderer>();
 }
 LineRenderer PanelLine(string name,int layer,Color color,float width,int count) {
  var line=Line(name,Enumerable.Repeat(Vector3.zero,count).ToArray(),color,width);
  line.useWorldSpace=true; SetLayer(line.gameObject,layer); return line;
 }
 GameObject PanelSphere(string name,int layer,Color color,float diameter) {
  var ball=Sphere(name,Vector3.zero,diameter,color); SetLayer(ball,layer); return ball;
 }
 void BuildActorLabels() {
  // Register every text before PrepareKnownGlyphs. Apply toggles objects; no Text.text writes.
  if(activeMode=="normal-and-pause") {
   HeaderPair("원래 동작","같은 동작"); HeaderPair("원래 동작","몸통 움직임을 줄인 비교");
  } else if(activeMode=="size-amplitude") {
   HeaderPair("크게 보기 · 같은 동작","작게 보기 · 같은 동작");
   HeaderPair("작게 보기 · 기준 동작","작게 보기 · 기준 동작");
   HeaderPair("작게 보기 · 기준 동작","작게 보기 · 어깨와 몸통 확대");
  } else if(activeMode=="shoulder-control") {
   HeaderPair("기준 리그 · 오른팔","비교 리그 · 오른팔");
   HeaderPair("관절 위치 고정","방향 바꾸기 · 회전");
   HeaderPair("어깨 위치 고정","어깨 위치 옮기기 · 이동");
   HeaderPair("어깨 위치 고정","어깨 이동 허용 · 같은 손 목표");
  } else {
   HeaderPair("동작 전체","같은 동작");
   HeaderPair("같은 순간 · 어깨와 골반","같은 순간 · 몸통과 발");
  }
 }
 void HeaderPair(string left,string right) {
  leftHeaders.Add(Label(left,505,212,42,Ink,800,72).gameObject);
  rightHeaders.Add(Label(right,1415,212,42,Ink,800,72).gameObject);
 }
 void BuildPhaseLabels() {
  // The global floor/grid must not cross explanatory text below the viewports.
  RectUI(960,843,1920,54,GridBg);
  string[] messages;
  switch(activeMode) {
   case "normal-and-pause": messages=new[]{"정상 속도 · 동작 전체","정지 분석 · 같은 순간","정상 속도 · 몸통만 바꾼 비교"}; break;
   case "size-amplitude": messages=new[]{"모델과 재생 시간은 같게 · 화면 크기만 변경","카메라와 재생 시간 고정","같은 클립 · 선택한 관절의 움직임만 확대"}; break;
   case "shoulder-control": messages=new[]{"리그 · 연결된 기준을 움직이면 표면도 변함","회전 · 붙은 자리는 그대로, 방향을 변경","이동 · 어깨가 붙은 자리 자체를 이동","같은 손 목표 · 어깨 위치가 만드는 자세 비교"}; break;
   case "paused-pose-context": messages=new[]{"정상 속도로 먼저 보기","정지 분석 · 방향이 겹치는 순간","정지한 순간부터 동작 이어 보기"}; break;
   case "linear-overshoot": messages=new[]{"설계 예시 · 출발 0 cm, 목표 100 cm","100 cm에서 멈추기","같은 시간 · 목표에서 멈추기 / 지나서 돌아오기","정지 분석 · 목표를 10 cm 지난 순간","두 경우 모두 100 cm에 도착"}; break;
   default: messages=new[]{"자체 제작 도형 · 가시가 펼쳐지는 모양","같은 시간 · 목표 모양 / 더 펼쳤다 돌아오기","정지 분석 · 가장 크게 펼쳐진 순간","조금 작아지며 목표 모양에 자리 잡기"}; break;
  }
  foreach(var s in messages) phaseLabels.Add(Label(s,960,843,38,Ink,1760,54).gameObject);
  beforePlaybackLabel=Label("준비 자세 · 정상 속도 재생 전",960,843,38,Ink,1760,54).gameObject;
  afterPlaybackLabel=Label("동작 종료 · 끝자세 확인",960,843,38,Ink,1760,54).gameObject;
  afterPlaybackPeakLabel=Label("정지 분석 · 방금 본 동작의 자세",960,843,38,Ink,1760,54).gameObject;
 }

 void BuildLinear() {
  camera.orthographicSize=.75f;
  foreach(var line in GetComponentsInChildren<LineRenderer>())
   if(line.name.StartsWith("Grid "))line.widthMultiplier*=.75f/3.2f;
  const float left=-.55f, upper=2.12f, lower=1.53f;
  foreach(float y in new[]{upper,lower}) {
   Line("Metre rail",new[]{new Vector3(left,y,0),new Vector3(left+1.1f,y,0)},Ink,.007f);
   for(int i=0;i<=11;i++) {
    float x=left+i*.1f;
    Line("Actual tenth-metre tick "+i,new[]{new Vector3(x,y-.027f,-.01f),new Vector3(x,y+.027f,-.01f)},i==10?Green:Grey,i==10?.014f:.006f);
   }
  }
  leftDot=Sphere("Baseline position in metres",new Vector3(left,upper,-.12f),.085f,Teal);
  rightDot=Sphere("Overshoot position in metres",new Vector3(left,lower,-.12f),.085f,Green);
  // Exact values arise from authored world coordinates: 1 Unity unit = 1 metre here.
  Label("목표에서 멈추기",270,315,42,Ink,450,90);
  Label("지나갔다 돌아오기",270,725,42,Ink,450,90);
  zeroLabels=UiGroup("Zero labels"); targetLabels=UiGroup("Target labels"); peakLabels=UiGroup("Peak labels"); differenceLabels=UiGroup("Difference labels");
  GroupLabel(zeroLabels,"0 cm",564,392,42,Ink,200,70);
  GroupLabel(zeroLabels,"0 cm",564,788,42,Ink,200,70);
  GroupLabel(targetLabels,"목표 100 cm",1284,235,42,Ink,330,70);
  GroupLabel(targetLabels,"목표 100 cm",1284,625,42,Ink,330,70);
  GroupLabel(peakLabels,"110 cm",1510,735,42,Ink,250,70);
  GroupLabel(differenceLabels,"10 cm 지나침",1490,555,40,Ink,350,70);
  globalGuides.Add(Line("Peak label leader",new[]{new Vector3(.55f,lower,-.2f),new Vector3(.62f,lower,-.2f)},Green,.009f));
  globalGuides.Add(Line("Actual tenth-metre overshoot bracket",new[]{new Vector3(.45f,lower+.08f,-.2f),new Vector3(.45f,lower+.13f,-.2f),new Vector3(.55f,lower+.13f,-.2f),new Vector3(.55f,lower+.08f,-.2f)},Green,.009f));
 }
 void BuildShape() {
  spikeMeshes=new Mesh[2]; spikeVertices=new Vector3[2][]; spikeObjects=new GameObject[2]; radiusGuides=new LineRenderer[2];
  for(int i=0;i<2;i++) {
   float x=i==0?-2.4f:2.4f;
   var go=new GameObject(i==0?"Original authored radial shape":"Authored overshoot radial shape");
   go.transform.SetParent(transform,false); go.transform.localPosition=new Vector3(x,2.0f,0); go.layer=29;
   var mesh=new Mesh {name="A02 original radial twelve-tip mesh "+i}; runtimeOwned.Add(mesh);
   var vertices=new Vector3[25]; var triangles=new int[24*3];
   for(int k=0;k<24;k++){triangles[k*3]=0;triangles[k*3+1]=1+(k+1)%24;triangles[k*3+2]=1+k;}
   mesh.vertices=vertices; mesh.triangles=triangles;
   go.AddComponent<MeshFilter>().sharedMesh=mesh; go.AddComponent<MeshRenderer>().sharedMaterial=Mat(i==0?Teal:Green,true);
   spikeMeshes[i]=mesh; spikeVertices[i]=vertices; spikeObjects[i]=go;
   radiusGuides[i]=Line("Actual shape radius "+i,new[]{Vector3.zero,Vector3.right},Ink,.035f);
   radiusGuides[i].useWorldSpace=true;
  }
  HeaderPair("목표 모양까지 펴기","더 크게 폈다가 돌아오기");
 }
 GameObject UiGroup(string name) {
  var go=new GameObject(name,typeof(RectTransform)); go.layer=29;go.transform.SetParent(canvas.transform,false);
  var rt=go.GetComponent<RectTransform>();rt.anchorMin=Vector2.zero;rt.anchorMax=Vector2.one;rt.offsetMin=rt.offsetMax=Vector2.zero;
  return go;
 }
 void GroupLabel(GameObject group,string text,float x,float y,int size,Color color,float w,float h) {
  var label=Label(text,x,y,size,color,w,h);label.transform.SetParent(group.transform,false);
 }

 public override void Apply(float t) {
  if(!built) throw new InvalidOperationException("Build must precede Apply.");
  if(!Finite(t) || t<0 || t>profile.duration+.002f) throw new ArgumentOutOfRangeException(nameof(t));
  time=Mathf.Min(t,profile.duration);
  cue=profile.phases.FirstOrDefault(p=>time>=p.start && time<p.end);
  if(cue==null && time==profile.duration)cue=profile.phases.Last();
  if(cue==null)throw new InvalidDataException("Capture time falls outside the contiguous measured phase map.");
  activePhase=cue.phase; phaseElapsed=time-cue.start; motionElapsed=Mathf.Max(0,phaseElapsed-cue.motionStart);
  foreach(var label in phaseLabels)label.SetActive(false);
  phaseLabels[activePhase].SetActive(true);
  beforePlaybackLabel.SetActive(false);afterPlaybackLabel.SetActive(false);afterPlaybackPeakLabel.SetActive(false);
  for(int i=0;i<leftHeaders.Count;i++){leftHeaders[i].SetActive(false);rightHeaders[i].SetActive(false);}
  if(playhead)playhead.anchoredPosition=new Vector2(Mathf.Lerp(-660,660,time/profile.duration),540-875);
  if(rigs!=null) {
   int header=0;
   if(activeMode=="normal-and-pause") header=activePhase==2?1:0;
   if(activeMode=="size-amplitude" || activeMode=="shoulder-control") header=activePhase;
   if(activeMode=="paused-pose-context") header=activePhase==1?1:0;
   leftHeaders[header].SetActive(true);rightHeaders[header].SetActive(true);
   lastClipSeconds=SampleSeconds();
   if(IsNativePlayPhase(activeMode,activePhase)) {
    float remainingClip=activeMode=="paused-pose-context" && activePhase==2?clipLength-profile.freezeSeconds:clipLength;
    bool waiting=phaseElapsed<cue.motionStart;
    bool ended=motionElapsed>=remainingClip;
    if(waiting || ended) {
     phaseLabels[activePhase].SetActive(false);
     beforePlaybackLabel.SetActive(waiting);
     afterPlaybackLabel.SetActive(!waiting && ended && cue.holdNativeAt!="peak");
     afterPlaybackPeakLabel.SetActive(!waiting && ended && cue.holdNativeAt=="peak");
    }
   }
   foreach(var rig in rigs) PoseOnce(rig.actor,PunchClip,lastClipSeconds);
   SetPanelHeight(panels[0],activeMode=="size-amplitude" && activePhase>0?240:440);
   SetPanelHeight(panels[1],activeMode=="size-amplitude"?240:440);
  } else if(activeMode=="linear-overshoot") ApplyLinear();
  else ApplyShape();
 }
 float SampleSeconds() {
  if(activeMode=="shoulder-control")return 0;
  if((activeMode=="normal-and-pause" || activeMode=="paused-pose-context") && activePhase==1)return profile.freezeSeconds;
  if(activeMode=="paused-pose-context" && activePhase==2) {
   if(cue.holdNativeAt=="peak" && motionElapsed>=clipLength-profile.freezeSeconds)return profile.freezeSeconds;
   return Mathf.Min(clipLength,profile.freezeSeconds+motionElapsed);
  }
  if(cue.holdNativeAt=="peak" && motionElapsed>=clipLength)return profile.freezeSeconds;
  return Mathf.Min(clipLength,motionElapsed);
 }
 public override void FlushPoses() {
  if(rigs==null){base.FlushPoses();return;}
  // Restore every transform from the asset instance, not the previous modified frame.
  // Sparse clip channels and out-of-order preflight samples must not accumulate offsets.
  foreach(var r in rigs)foreach(var state in r.rest)state.Restore();
  base.FlushPoses();
  foreach(var r in rigs)HideGuides(r);
  lastArmEvidence=new ArmEvidence[0];
  if(activeMode=="normal-and-pause" && activePhase==2)
   ScaleRotation(rigs[1].torso,rigs[1].referenceTorso,.55f);
  if(activeMode=="size-amplitude" && activePhase==2) {
   ScaleRotation(rigs[1].torso,rigs[1].referenceTorso,2.2f);
   ScaleRotation(rigs[1].shoulderR,rigs[1].referenceShoulder,2.2f);
  }
  foreach(var r in rigs)Ground(r.actor);
  if(activeMode=="shoulder-control")ApplyShoulder();
  if((activeMode=="normal-and-pause" || activeMode=="paused-pose-context") && activePhase==1) {
   UpdatePostureGuides(rigs[0],false);UpdatePostureGuides(rigs[1],true);
  }
  // IK follows grounding. Never shift the actor after solving the common target.
  if(activeMode=="shoulder-control") foreach(var r in rigs) {
   if(MinimumSkinY(r.actor)<-.005f)
    throw new InvalidOperationException("Shoulder illustration crossed the floor after IK; inspect instead of silently shifting the target.");
  }
  RenderPanels();
 }
 static void ScaleRotation(Transform bone,Quaternion reference,float amplitude) {
  bone.localRotation=ScaleLocalExcursion(reference,bone.localRotation,amplitude);
 }
 static Quaternion ScaleLocalExcursion(Quaternion reference,Quaternion sampled,float amplitude) {
  Quaternion delta=Quaternion.Inverse(reference)*sampled;
  if(delta.w<0)delta=new Quaternion(-delta.x,-delta.y,-delta.z,-delta.w);
  return reference*Quaternion.SlerpUnclamped(Quaternion.identity,delta,amplitude);
 }
 void Ground(GameObject actor) {actor.transform.position+=Vector3.up*(.02f-MinimumSkinY(actor));}
 float MinimumSkinY(GameObject actor) {
  float min=float.PositiveInfinity;
  foreach(var skin in actor.GetComponentsInChildren<SkinnedMeshRenderer>(true)) {
   bakeScratch.Clear();skin.BakeMesh(bakeScratch);
   foreach(var v in bakeScratch.vertices)min=Mathf.Min(min,skin.transform.TransformPoint(v).y);
  }
  if(!Finite(min))throw new InvalidOperationException("Grounding needs actual baked skinned vertices.");
  return min;
 }
 static Vector3 AnatomicalRight(ActorRig r) {
  var right=Vector3.ProjectOnPlane(r.shoulderR.position-r.shoulderL.position,Vector3.up);
  if(right.sqrMagnitude<.000001f)throw new InvalidOperationException("Cannot derive anatomical right from shoulders.");
  return right.normalized;
 }
 void ApplyShoulder() {
  float u=cue.motionDuration>0?Mathf.Clamp01(motionElapsed/cue.motionDuration):0;
  Vector3 right=AnatomicalRight(rigs[0]),forward=Vector3.Cross(right,Vector3.up).normalized;
  float upper=Vector3.Distance(rigs[0].arm.position,rigs[0].forearm.position);
  float lower=Vector3.Distance(rigs[0].forearm.position,rigs[0].hand.position),reach=upper+lower;
  Vector3[] originalPivots=rigs.Select(r=>r.arm.position).ToArray();
  if(activePhase==1 || activePhase==2) {
   // The controlled rotation/translation exercise starts with the same extended
   // elbow on both copies. A bent guard would send the lifted fist into the face.
   // This fixed baseline is established before the one varying shoulder control.
   foreach(var r in rigs) {
    float forearmLength=Vector3.Distance(r.forearm.position,r.hand.position);
    Vector3 axis=(r.forearm.position-r.arm.position).normalized;
    AlignChildTo(r.forearm,r.hand,r.forearm.position+axis*forearmLength);
   }
  }
  if(activePhase==1) {
   var r=rigs[1];
   // Rotation only: the upper-arm origin does not translate.
   r.arm.rotation=Quaternion.AngleAxis(-55f*Smooth01(u),right)*r.arm.rotation;
  } else if(activePhase==2) {
   rigs[1].shoulderR.position+=forward*(.12f*reach*Smooth01(u));
  } else if(activePhase==3) {
   // One reachable target in each panel's identical local frame.
   Vector3 targetOffset=originalPivots[0]-rigs[0].origin+forward*(.88f*reach)+Vector3.up*(.18f*reach);
   rigs[1].shoulderR.position+=forward*(.12f*reach*Smooth01(u));
   lastArmEvidence=new ArmEvidence[2];
   for(int i=0;i<2;i++) {
    var r=rigs[i];Vector3 target=r.origin+targetOffset;
    Vector3 pole=r.arm.position+right*(.35f*reach)-Vector3.up*(.7f*reach);
    float l1=Vector3.Distance(r.arm.position,r.forearm.position),l2=Vector3.Distance(r.forearm.position,r.hand.position);
    Vector3 elbow,wrist;
    if(!TrySolveArmPositions(r.arm.position,target,pole,l1,l2,out elbow,out wrist))
     throw new InvalidOperationException("Common hand target is unreachable or elbow pole is degenerate.");
    AlignChildTo(r.arm,r.forearm,elbow); AlignChildTo(r.forearm,r.hand,wrist);
    float error=Vector3.Distance(r.hand.position,target);
    if(error>.002f*(l1+l2))throw new InvalidOperationException("Generic two-bone IK failed to reach the unchanged target.");
    r.targetMarker.SetActive(true);r.targetMarker.transform.position=GuidePoint(target);
    lastArmEvidence[i]=new ArmEvidence {side=i==0?"fixed":"translation-enabled",upperLength=l1,lowerLength=l2,endpointError=error,
     targetPanelLocal=target-r.origin,wristPanelLocal=r.hand.position-r.origin,shoulderPanelLocal=r.arm.position-r.origin};
   }
   if(Vector3.Distance(lastArmEvidence[0].targetPanelLocal,lastArmEvidence[1].targetPanelLocal)>.0001f)
    throw new InvalidOperationException("Panel-local hand targets diverged.");
  }
  for(int i=0;i<2;i++) {
   var r=rigs[i];
   r.chain.gameObject.SetActive(true);r.chain.SetPositions(new[]{GuidePoint(r.arm.position),GuidePoint(r.forearm.position),GuidePoint(r.hand.position)});
   r.pivotMarker.SetActive(true);r.pivotMarker.transform.position=GuidePoint(r.arm.position);
   if(i==1 && activePhase>=2) {
    r.originalPivotMarker.SetActive(true);r.originalPivotMarker.transform.position=GuidePoint(originalPivots[i]);
    r.translationGuide.gameObject.SetActive(true);r.translationGuide.SetPositions(new[]{GuidePoint(originalPivots[i]),GuidePoint(r.arm.position)});
   }
  }
 }
 static void AlignChildTo(Transform bone,Transform child,Vector3 desiredChildPosition) {
  Vector3 current=child.position-bone.position,desired=desiredChildPosition-bone.position;
  if(current.sqrMagnitude<1e-10f || desired.sqrMagnitude<1e-10f)throw new InvalidOperationException("Zero length Generic bone.");
  // No assumption that the bone's local +X is its longitudinal axis.
  bone.rotation=Quaternion.FromToRotation(current,desired)*bone.rotation;
 }
 static bool TrySolveArmPositions(Vector3 shoulder,Vector3 target,Vector3 pole,float upper,float lower,out Vector3 elbow,out Vector3 wrist) {
  elbow=shoulder;wrist=target;if(upper<=0 || lower<=0)return false;
  Vector3 offset=target-shoulder;float d=offset.magnitude,epsilon=(upper+lower)*.0001f;
  if(d<=Mathf.Abs(upper-lower)+epsilon || d>=upper+lower-epsilon)return false;
  Vector3 direction=offset/d,perpendicular=pole-shoulder;
  perpendicular-=Vector3.Dot(perpendicular,direction)*direction;
  if(perpendicular.sqrMagnitude<=epsilon*epsilon)return false;
  perpendicular.Normalize();
  float a=(upper*upper-lower*lower+d*d)/(2*d),heightSquared=upper*upper-a*a;
  if(heightSquared<-epsilon*epsilon)return false;
  elbow=shoulder+direction*a+perpendicular*Mathf.Sqrt(Mathf.Max(0,heightSquared));return true;
 }
 static Vector3 GuidePoint(Vector3 p) {return new Vector3(p.x,p.y,-4);}
 void UpdatePostureGuides(ActorRig r,bool foot) {
  r.shoulderGuide.gameObject.SetActive(true);
  r.shoulderGuide.SetPositions(new[]{GuidePoint(r.shoulderL.position),GuidePoint(r.shoulderR.position)});
  r.hipGuide.gameObject.SetActive(true);
  r.hipGuide.SetPositions(new[]{GuidePoint(r.thighL.position),GuidePoint(r.thighR.position)});
  r.footGuide.gameObject.SetActive(foot);
  r.footGuide.SetPositions(new[]{GuidePoint(r.torso.position),GuidePoint(r.hips.position),GuidePoint(r.foot.position)});
 }
 static void HideGuides(ActorRig r) {
  foreach(var l in new[]{r.chain,r.shoulderGuide,r.hipGuide,r.footGuide,r.translationGuide})l.gameObject.SetActive(false);
  r.pivotMarker.SetActive(false);r.targetMarker.SetActive(false);r.originalPivotMarker.SetActive(false);
 }
 void RenderPanels() {
  foreach(var p in panels) {
   // Follow the capture scene's mask; do not render unrelated open scenes.
   p.camera.overrideSceneCullingMask=camera.overrideSceneCullingMask;
   var request=new UniversalRenderPipeline.SingleCameraRequest {destination=p.texture};
   if(!RenderPipeline.SupportsRenderRequest(p.camera,request))throw new InvalidOperationException("URP panel single-camera render requests are unsupported.");
   RenderPipeline.SubmitRenderRequest(p.camera,request);
  }
 }
 void ApplyLinear() {
  float u=cue.motionDuration>0?Mathf.Clamp01(motionElapsed/cue.motionDuration):0;
  float baseline=0,overshoot=0;
  if(activePhase==1)baseline=StopAtTargetMetres(u);
  if(activePhase==2){baseline=StopAtTargetMetres(u);overshoot=OvershootMetres(u);}
  if(activePhase==3){baseline=StopAtTargetMetres(.72f);overshoot=1.1f;}
  if(activePhase==4){baseline=1;overshoot=1;}
  lastBaselineMetres=baseline;lastOvershootMetres=overshoot;
  leftDot.transform.position=new Vector3(-.55f+baseline,2.12f,-.12f);
  rightDot.transform.position=new Vector3(-.55f+overshoot,1.53f,-.12f);
  rightDot.SetActive(activePhase>=2);zeroLabels.SetActive(true);targetLabels.SetActive(true);
  // Peak labels accompany the actual frozen peak, not every trajectory point.
  peakLabels.SetActive(activePhase==3);differenceLabels.SetActive(activePhase==3);
  foreach(var guide in globalGuides)guide.gameObject.SetActive(activePhase==3);
 }
 void ApplyShape() {
  leftHeaders[0].SetActive(true);rightHeaders[0].SetActive(true);
  float u=cue.motionDuration>0?Mathf.Clamp01(motionElapsed/cue.motionDuration):0;
  float left=.42f,right=.42f;
  if(activePhase==1){left=Mathf.Lerp(.42f,1,Smooth01(u));right=SpikeRadius(u);}
  if(activePhase==2){left=Mathf.Lerp(.42f,1,Smooth01(.72f));right=1.1f;}
  if(activePhase==3){left=Mathf.Lerp(.42f,1,Smooth01(.72f+.28f*u));right=Mathf.Lerp(1.1f,1,Smooth01(u));}
  lastBaselineRadius=left;lastOvershootRadius=right;
  float[] radii={left,right};
  for(int i=0;i<2;i++) {
   var v=spikeVertices[i];v[0]=Vector3.zero;
   for(int k=0;k<24;k++) {
    float angle=k*Mathf.PI/12,radius=(k%2==0?radii[i]:.42f)*1.2f;
    v[k+1]=new Vector3(Mathf.Cos(angle)*radius,Mathf.Sin(angle)*radius,0);
   }
   spikeMeshes[i].vertices=v;spikeMeshes[i].RecalculateBounds();spikeMeshes[i].RecalculateNormals();
   radiusGuides[i].gameObject.SetActive(activePhase==2);
   Vector3 centre=spikeObjects[i].transform.position;
   radiusGuides[i].SetPositions(new[]{new Vector3(centre.x,centre.y,-.2f),new Vector3(centre.x+radii[i]*1.2f,centre.y,-.2f)});
  }
 }
 static float Smooth01(float u){u=Mathf.Clamp01(u);return u*u*(3-2*u);}
 static float StopAtTargetMetres(float u){return Smooth01(u);}
 static float OvershootMetres(float u) {
  u=Mathf.Clamp01(u);
  return u<=.72f?1.1f*Smooth01(u/.72f):Mathf.LerpUnclamped(1.1f,1,Smooth01((u-.72f)/.28f));
 }
 static float SpikeRadius(float u) {
  u=Mathf.Clamp01(u);
  return u<=.72f?Mathf.Lerp(.42f,1.1f,Smooth01(u/.72f)):Mathf.Lerp(1.1f,1,Smooth01((u-.72f)/.28f));
 }
 [Serializable] public sealed class Diagnostics {
  public string mode,profileId,sourceFingerprint,sourceKind="self-authored-explanation";
  public string holdNativeAt,replayReason,activeRenderPipeline;
  public float time,clipSeconds,clipLength,baselineMetres,overshootMetres,baselineRadius,overshootRadius,actorYawDegrees;
  public int phase,createdPanelTextures,generatedMeshCount,meshRendererCount,directMeshRendererCount;
  public float[] orthographicSizes,minimumSkinY;
  public ArmEvidence[] arms;
  public bool reconstructedFromSavedProfile;
 }
 bool reconstructed;
 public string A02DiagnosticJson() {
  return JsonUtility.ToJson(new Diagnostics {
   mode=activeMode,profileId=presentationId,sourceFingerprint=sourceCodeFingerprint,
   holdNativeAt=cue==null?null:cue.holdNativeAt,replayReason=cue==null?null:cue.replayReason,
   activeRenderPipeline=GraphicsSettings.currentRenderPipeline?GraphicsSettings.currentRenderPipeline.name:"built-in",
   meshRendererCount=GetComponentsInChildren<MeshRenderer>(true).Length,
   directMeshRendererCount=GetComponentsInChildren<MeshRenderer>(true).Count(r=>r.GetComponent(DirectMeshComponent)),
   time=time,clipSeconds=lastClipSeconds,clipLength=clipLength,phase=activePhase,actorYawDegrees=appliedActorYaw,
   baselineMetres=lastBaselineMetres,overshootMetres=lastOvershootMetres,baselineRadius=lastBaselineRadius,overshootRadius=lastOvershootRadius,
   createdPanelTextures=panels==null?0:panels.Count(p=>p.texture && p.texture.IsCreated() && p.image.texture==p.texture),
   generatedMeshCount=spikeMeshes==null?0:spikeMeshes.Count(m=>m && m.vertexCount==25 && m.bounds.size.sqrMagnitude>0),
   orthographicSizes=panels==null?new float[0]:panels.Select(p=>p.camera.orthographicSize).ToArray(),
   minimumSkinY=rigs==null?new float[0]:rigs.Select(r=>MinimumSkinY(r.actor)).ToArray(),
   arms=lastArmEvidence,reconstructedFromSavedProfile=reconstructed
  },true);
 }
 // A saved scene contains its own frozen timing and source fingerprint. Rebuild creates new
 // RTs/meshes from that source; it never relies on an old RT cache or overwrites vendor assets.
 public void RebuildFromSavedSource(RenderTexture output,ulong sceneMask,float previewTime) {
  if(string.IsNullOrEmpty(profileSnapshotJson) || string.IsNullOrEmpty(sourceCodeFingerprint))
   throw new InvalidDataException("Saved scene has no frozen A02 source/profile receipt.");
  if(sourceCodeFingerprint!=AnimationExaggerationBuildVersion.For("AnimationExaggerationStage"))
   throw new InvalidDataException("Restore the scene's recorded A02 source snapshot before rebuilding this historic scene.");
  ReleaseRuntimeObjects();
  for(int i=transform.childCount-1;i>=0;i--)DestroyImmediate(transform.GetChild(i).gameObject);
  ResetTransientForReconstruction();
  phaseLabels.Clear();leftHeaders.Clear();rightHeaders.Clear();globalGuides.Clear();
  rigs=null;panels=null;spikeMeshes=null;spikeVertices=null;spikeObjects=null;radiusGuides=null;
  built=false;reconstructed=false;
  Initialize();camera.targetTexture=output;camera.overrideSceneCullingMask=sceneMask;
  Canvas.ForceUpdateCanvases();Build();PrepareKnownGlyphs();Apply(previewTime);FlushPoses();RefreshUi();
  editorPreviewSeconds=previewTime;reconstructed=true;
 }
 void ReleaseRuntimeObjects() {
  foreach(var obj in runtimeOwned) {
   var rt=obj as RenderTexture;if(rt)rt.Release();
   if(obj)DestroyImmediate(obj);
  }
  runtimeOwned.Clear();
 }
 void OnDestroy() {
  ReleaseRuntimeObjects();
 }
}
}
