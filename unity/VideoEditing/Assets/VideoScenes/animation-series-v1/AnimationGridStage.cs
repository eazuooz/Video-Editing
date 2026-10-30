using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.AnimationSeries {
// Editorial animation study. All numerical time marks belong to this scene,
// never to a commercial game's private animation data.
public sealed class AnimationGridStage : AnimationLessonStage {
 // Optional measured editorial profile. Empty preserves every legacy mode.
 public string presentationId;
 [System.Serializable] public sealed class PresentationCue {
  public string key; public float start,end; public int value;
 }
 [System.Serializable] public sealed class PresentationProfile {
  public string id,mode; public float duration; public PresentationCue[] cues; public string[] notes;
 }
 [System.Serializable] public sealed class PresentationBook { public int schemaVersion; public PresentationProfile[] presentations; }
 sealed class BonePose { public Quaternion rotation; public Vector3 position; }
 PresentationProfile presentation;
 readonly System.Collections.Generic.Dictionary<Transform,BonePose> presentationOffsets=new System.Collections.Generic.Dictionary<Transform,BonePose>();
 GameObject[] presentationMessages;
 GameObject timingIntervalGroup,timingSixtyGroup,timingFormulaGroup,timingIntervalCaption;
 LineRenderer presentationLeaderLeft,presentationLeaderRight;
 Transform presentationTargetLeft,presentationTargetRight;
 GameObject overlapPropLeft,overlapPropRight;
 GameObject exclusionMark;
 float presentationTime;
 int presentationPhase,presentationRow;
 GameObject referenceActor, movingActor;
 // One editorial posture variable; both copies retain the same sampled walk.
 sealed class WalkIntentRig {
  public Transform torso, head, leftShoulder, rightShoulder;
  public Quaternion sampledTorsoLocal, sampledHeadLocal;
  public bool hasPostureOffset;
  public void RestoreSampledPose() {
   if(!hasPostureOffset)return;
   torso.localRotation=sampledTorsoLocal;
   head.localRotation=sampledHeadLocal;
   hasPostureOffset=false;
  }
 }
 WalkIntentRig referenceWalkIntent, movingWalkIntent;
 float walkIntentBlend;
 RectTransform playhead, attackPlayhead, requestedMeter, limitedMeter;
 Image[] rowMarks;
 Image intervalMark;
 GameObject silhouette;
 Transform referenceArm, limitedArm, documentArm, documentFoot;
 Quaternion referenceArmBase, limitedArmBase;
 bool jointBasesCaptured;
 float requestedArmAngle;
 const float DemonstrationTarget=55f, DemonstrationLimit=30f;
 GameObject documentPaper;
 GameObject[] documentNotes;
 Image[] documentSteps;
 Renderer[] documentRenderers;
 Material[][] documentMaterials;
 LineRenderer documentArmLine, documentFootLine;
 int documentPhase=-1;
 readonly Color Ink=Hex("252B30");
 public override void Build() {
  for(int i=-24;i<=24;i++) {
   float x=i*.25f;
   Line("Grid vertical "+i,new[]{new Vector3(x,-.02f,1.8f),new Vector3(x,5.2f,1.8f)},
     i%4==0?Hex("B6BBBD"):Hex("D3D6D6"),i%4==0?.014f:.007f);
  }
  for(int i=0;i<=21;i++) {
   float y=i*.25f;
   Line("Grid horizontal "+i,new[]{new Vector3(-6,y,1.8f),new Vector3(6,y,1.8f)},
     i%4==0?Hex("B6BBBD"):Hex("D3D6D6"),i%4==0?.014f:.007f);
  }
  Line("Floor reference",new[]{new Vector3(-6,0,-.2f),new Vector3(6,0,-.2f)},Hex("C9444E"),.025f);
  foreach(float x in new[]{-2.4f,2.4f})
   Line("Pose origin",new[]{new Vector3(x,0,1.65f),new Vector3(x,3.6f,1.65f)},Hex("527DAA"),.018f);
  RectUI(960,80,1920,160,Hex("101214"));
  RectUI(960,1000,1920,200,Hex("101214"));
  Label("애니메이션 제작 지시",735,68,54,Yellow,1320,86);
  // The final compositor supplies the picture-kind chip in this corner.
  LoadPresentation();
  if(presentation!=null) BuildPresentation();
  else if(cutId=="motion-list") BuildList();
  else if(cutId=="attack-timing") BuildTiming();
  else if(cutId=="pose-document") BuildDocument();
  else if(cutId=="reference-transfer") BuildTransfer();
  else if(cutId=="joint-limit") BuildLimit();
  else if(cutId=="walk-intent") BuildWalkIntent();
  else if(cutId=="idle-intent") BuildIdleIntent();
  else if(cutId=="motion-brief" || cutId=="pose-connection") BuildMotionBrief();
  else BuildPoseComparison();
  if(cutId!="attack-timing") {
   RectUI(960,870,1320,5,Hex("929B9E"));
   playhead=RectUI(300,870,14,24,Hex("C9444E")).rectTransform;
   if(presentation==null && cutId!="walk-intent" && cutId!="idle-intent")Label("설명 진행",960,820,38,Ink,300,60);
  }
 }
 void BuildList() {
  Label("애니메이션 목록",490,220,48,Ink,820,80);
  Label("선택한 동작 미리보기",1395,220,48,Ink,900,80);
  string[] names={"대기 · 반복 (Loop)","걷기 · 반복 (Loop)","공격 · 한 번 (Once)"};
  rowMarks=new Image[3];
  for(int i=0;i<3;i++) {
   rowMarks[i]=RectUI(460,365+i*145,700,100,new Color(.3f,.58f,.6f,.16f));
   Label(names[i],460,365+i*145,42,Ink,680,90);
  }
  movingActor=Actor("Listed motion",new Vector3(2.5f,0,0),false,2.7f,160);
 }
 void BuildTiming() {
  Label("설계 예시 · 1초 / 60fps",505,220,44,Ink,880,80);
  Label("공격 동작 · 같은 시간축",1390,220,44,Ink,900,80);
  movingActor=Actor("Illustrative one-second attack",new Vector3(2.5f,0,0),false,2.7f,160);
  Label("가정한 공격 구간 · 12프레임",500,310,40,Ink,840,70);
  RectUI(500,390,720,24,Hex("B1B9BC"));
  // 1-second clock: x140..860; frames12..23 occupy [0.2,0.4).
  intervalMark=RectUI(356,390,144,24,Hex("B5464E"));
  attackPlayhead=RectUI(140,390,10,50,Hex("C9444E")).rectTransform;
  Label("0프레임",140,444,32,Ink,200,58);
  Label("60프레임 · 1초",820,444,32,Ink,300,58);
  Label("12 ÷ 60 = 0.2초",500,540,46,Ink,800,80);
  Label("동작 전체 길이와 공격 구간을 구분",500,645,34,Ink,820,76);
 }
 void BuildDocument() {
  Label("기준 자세 · Pose Reference",520,220,42,Ink,900,80);
  Label("포즈 명세서 · Specification",1370,220,42,Ink,960,80);
  referenceActor=Actor("Photographed pose",new Vector3(-2.5f,0,0),false,2.7f,160);
  silhouette=Actor("Pose silhouette",new Vector3(2.5f,0,0),false,2.7f,160);
  documentRenderers=silhouette.GetComponentsInChildren<Renderer>(true);
  documentMaterials=new Material[documentRenderers.Length][];
  for(int i=0;i<documentRenderers.Length;i++)documentMaterials[i]=documentRenderers[i].sharedMaterials;
  // This is a staged digital workflow illustration, not a claim of a saved photo.
  documentPaper=Box("Isolated pose sheet",new Vector3(2.5f,1.5f,1.25f),new Vector3(3.5f,3.05f,.015f),White);
  documentPaper.GetComponent<Renderer>().sharedMaterial=Mat(White,true);
  Line("Pose image frame",new[]{new Vector3(.75f,-.025f,-.4f),new Vector3(.75f,3.025f,-.4f),new Vector3(4.25f,3.025f,-.4f),new Vector3(4.25f,-.025f,-.4f),new Vector3(.75f,-.025f,-.4f)},Hex("A7AFB2"),.015f);
  string[] steps={"1. 자세 고정 · 촬영", "2. 배경 분리 · 대비", "3. 의도 주석"};
  documentSteps=new Image[3];
  for(int i=0;i<3;i++) {
   documentSteps[i]=RectUI(350+610*i,302,540,68,new Color(.28f,.6f,.59f,.08f));
   Label(steps[i],350+610*i,302,33,Ink,530,66);
  }
  documentArm=FindBone(silhouette,"Hand.L","Wrist.L","Arm.L");
  documentFoot=FindBone(silhouette,"Foot.L","Toes.L","Foot.R");
  documentArmLine=Line("Arm intention leader",new[]{Vector3.zero,Vector3.zero,Vector3.zero},Hex("236F78"),.024f).GetComponent<LineRenderer>();
  documentFootLine=Line("Foot position leader",new[]{Vector3.zero,Vector3.zero,Vector3.zero},Hex("236F78"),.024f).GetComponent<LineRenderer>();
  documentNotes=new[]{Label("팔이 향할 곳",960,580,34,Ink,320,65).gameObject,Label("발을 놓을 곳",960,745,34,Ink,320,65).gameObject};
 }
 void BuildTransfer() {
  Label("기준이 되는 몸짓",520,220,48,Ink,900,80);
  Label("새 캐릭터에서 비교",1370,220,48,Ink,960,80);
  referenceActor=Actor("Reference movement",new Vector3(-2.5f,0,0),false,2.7f,160);
  movingActor=Actor("Movement on different character",new Vector3(2.5f,0,0),true,2.7f,160);
 }
 void BuildLimit() {
  Label("같은 목표 · 추가 회전",520,220,42,Ink,900,80);
  Label("같은 목표 · 30°에서 제한",1370,220,42,Ink,960,80);
  referenceActor=Actor("Unconstrained demonstration",new Vector3(-2.5f,0,0),false,2.7f,180);
  movingActor=Actor("Illustrative limited joint",new Vector3(2.5f,0,0),false,2.7f,180);
  referenceArm=FindBone(referenceActor,"Arm.L");limitedArm=FindBone(movingActor,"Arm.L");
  Label("설명용 각도 · 0° → 55°",520,302,34,Ink,820,64);
  Label("설명용 상한 · 추가 회전 30°",1370,302,34,Ink,840,64);
  RectUI(535,350,430,12,Hex("C3C9CA"));
  RectUI(1375,350,430,12,Hex("C3C9CA"));
  requestedMeter=Meter(320,350,Hex("327C88"));
  limitedMeter=Meter(1160,350,Hex("327C88"));
  RectUI(1160+430*DemonstrationLimit/DemonstrationTarget,350,5,32,Hex("C9444E"));
  Label("가동 범위 · Range of Motion",960,760,34,Ink,500,62);
 }
 void BuildPoseComparison() {
  Label("포즈 · 한 순간",535,218,48,Ink,820,80);
  Label("애니메이션 · 움직임",1385,218,48,Ink,900,80);
  referenceActor=Actor("Reference pose",new Vector3(-2.5f,0,0),false,2.7f,160);
  movingActor=Actor("Moving realization",new Vector3(2.5f,0,0),false,2.7f,160);
 }
 void BuildWalkIntent() {
  Label("어깨 펴고 · 힘차게",535,218,48,Ink,870,80);
  Label("고개 숙여 · 조심스럽게",1385,218,48,Ink,960,80);
  Label("같은 걸음 · 같은 속도 · 상체 자세만 변경",960,310,42,Ink,1700,76);
  referenceActor=Actor("Open posture same walk",new Vector3(-2.5f,0,0),false,2.7f,160);
  movingActor=Actor("Bowed posture same walk",new Vector3(2.5f,0,0),false,2.7f,160);
  referenceWalkIntent=RequireWalkIntentRig(referenceActor);
  movingWalkIntent=RequireWalkIntentRig(movingActor);
 }
 void BuildIdleIntent() {
  Label("어깨를 편 대기 자세",535,218,48,Ink,900,80);
  Label("고개를 숙인 대기 자세",1385,218,48,Ink,960,80);
  Label("대기 자세 · 같은 동작의 상체 인상 비교",960,310,42,Ink,1740,76);
  referenceActor=Actor("Open posture same idle",new Vector3(-2.5f,0,0),false,2.7f,160);
  movingActor=Actor("Bowed posture same idle",new Vector3(2.5f,0,0),false,2.7f,160);
  referenceWalkIntent=RequireWalkIntentRig(referenceActor);
  movingWalkIntent=RequireWalkIntentRig(movingActor);
 }
 WalkIntentRig RequireWalkIntentRig(GameObject actor) {
  var rig=new WalkIntentRig {
   torso=FindBone(actor,"Torso"),head=FindBone(actor,"Head"),
   leftShoulder=FindBone(actor,"Shoulder.L"),rightShoulder=FindBone(actor,"Shoulder.R")
  };
  if(!rig.torso || !rig.head || !rig.leftShoulder || !rig.rightShoulder)
   throw new System.InvalidOperationException("Walk-intent requires Torso, Head, Shoulder.L and Shoulder.R on the selected rig.");
  return rig;
 }
 void ApplyWalkIntent(WalkIntentRig rig,float intent) {
  // Restore before sampling and save the new sample every frame. This also
  // prevents drift if a clip omits a bone or the capture requests a frame twice.
  rig.sampledTorsoLocal=rig.torso.localRotation;
  rig.sampledHeadLocal=rig.head.localRotation;
  var anatomicalRight=rig.rightShoulder.position-rig.leftShoulder.position;
  if(anatomicalRight.sqrMagnitude<.000001f)
   throw new System.InvalidOperationException("Walk-intent shoulder axis is degenerate.");
  anatomicalRight.Normalize();
  // In this verified side view +rotation bends toward the facing direction.
  // These angles are our artistic settings, not measured human/game values.
  // One signed intent controls fixed torso/head weights; gait never changes.
  float torsoDegrees=(intent<0?6f:14f)*intent;
  float headDegrees=(intent<0?5f:20f)*intent;
  rig.torso.rotation=Quaternion.AngleAxis(torsoDegrees,anatomicalRight)*rig.torso.rotation;
  // Read Head.rotation AFTER Torso so the inherited torso bend is retained.
  rig.head.rotation=Quaternion.AngleAxis(headDegrees,anatomicalRight)*rig.head.rotation;
  rig.hasPostureOffset=true;
 }
 void BuildMotionBrief() {
  Label("자료 · 기준으로 삼은 자세",535,218,43,Ink,870,80);
  Label("동작 · 자세 앞뒤의 연결",1385,218,43,Ink,900,80);
  referenceActor=Actor("Reference attack pose",new Vector3(-2.5f,0,0),false,2.7f,160);
  movingActor=Actor("Attack realization",new Vector3(2.5f,0,0),false,2.7f,160);
 }
 public override void Apply(float t) {
  if(presentation!=null) {
   ApplyPresentation(t);
   if(playhead)playhead.anchoredPosition=new Vector2(-660+1320*CutProgress(t),540-870);
   return;
  }
  if(cutId=="motion-list") {
   float rowDuration=Mathf.Max(.1f,frames/180f);
   int active=Mathf.Clamp(Mathf.FloorToInt(t/rowDuration),0,2);
   float localTime=Mathf.Max(0,t-active*rowDuration);
   string[] clips={"Idle_A","Walk_A","FightM_Punch_A"};
   if(active==2)PoseOnce(movingActor,clips[active],localTime);
   else Pose(movingActor,clips[active],localTime);
   for(int i=0;i<3;i++)rowMarks[i].color=i==active?new Color(.28f,.6f,.59f,.35f):new Color(.28f,.6f,.59f,.07f);
  } else if(cutId=="attack-timing") {
   // Editorial timing example: one sampled action is fitted to our 1-second
   // design clock. The red interval is a chosen brief, not measured collision.
   float clock=Mathf.Repeat(Mathf.Max(0,t),1f);
   PoseNormalized(movingActor,"FightM_Punch_A",clock);
   if(intervalMark)intervalMark.color=clock>=12f/60f && clock<24f/60f?Hex("C9444E"):Hex("D5A7AA");
   if(attackPlayhead)attackPlayhead.anchoredPosition=new Vector2(140+720*clock-960,540-390);
  } else if(cutId=="pose-document") {
   PoseOnce(referenceActor,"FightM_Punch_A",.3f);PoseOnce(silhouette,"FightM_Punch_A",.3f);
   float progress=CutProgress(t);
   SetDocumentPhase(progress<.28f?0:progress<.62f?1:2);
  } else if(cutId=="reference-transfer") {
   Pose(referenceActor,"LookingAround",t);Pose(movingActor,"LookingAround",t);
  } else if(cutId=="joint-limit") {
   PoseOnce(referenceActor,"FightM_Pose",0);PoseOnce(movingActor,"FightM_Pose",0);
   requestedArmAngle=Mathf.SmoothStep(0,DemonstrationTarget,Mathf.Clamp01(CutProgress(t)/.65f));
   requestedMeter.sizeDelta=new Vector2(430*requestedArmAngle/DemonstrationTarget,12);
   limitedMeter.sizeDelta=new Vector2(430*Mathf.Min(requestedArmAngle,DemonstrationLimit)/DemonstrationTarget,12);
  } else if(cutId=="walk-intent" || cutId=="idle-intent") {
   // Same clip, sample time, phase, speed, scale, facing and grounding on both.
   string sameClip=cutId=="idle-intent"?"Idle_A":"Walk_A";
   Pose(referenceActor,sameClip,t);Pose(movingActor,sameClip,t);
   walkIntentBlend=Mathf.SmoothStep(0,1,Mathf.Clamp01(t/.8f));
  } else if(cutId=="motion-brief" || cutId=="pose-connection") {
   Pose(referenceActor,"FightM_Punch_A",.05f);
   Pose(movingActor,"FightM_Punch_A",t);
  } else {
   Pose(referenceActor,"Walk_A",.30f);
   Pose(movingActor,"Walk_A",t);
  }
  if(playhead)playhead.anchoredPosition=new Vector2(-660+1320*CutProgress(t),540-870);
 }
 public override void FlushPoses() {
  if(presentation!=null) {FlushPresentationPoses();return;}
  if(cutId=="walk-intent" || cutId=="idle-intent") {
   referenceWalkIntent.RestoreSampledPose();movingWalkIntent.RestoreSampledPose();
  }
  base.FlushPoses();
  if(cutId=="walk-intent" || cutId=="idle-intent") {
   ApplyWalkIntent(referenceWalkIntent,-walkIntentBlend);
   ApplyWalkIntent(movingWalkIntent,walkIntentBlend);
  }
  // Both selected clips are grounded actions. Register the sampled, baked
  // lowest point on our floor; do not apply this to future jumps/airborne clips.
  if(cutId=="joint-limit") {
   // Same camera-plane world-Z offset on both sides; only the right side clamps.
   // These are added rotations from this pose, not anatomical measurements.
   if(!referenceArm || !limitedArm)throw new System.InvalidOperationException("Joint-limit demo requires the selected rig's Arm.L bone on both actors.");
   if(!jointBasesCaptured) {
    referenceArmBase=referenceArm.rotation;limitedArmBase=limitedArm.rotation;
    jointBasesCaptured=true;
   }
   // Rotate in the visible picture plane. This rig's local Z mainly moves
   // its hand in depth, which hides the very limit this comparison teaches.
   referenceArm.rotation=Quaternion.AngleAxis(-requestedArmAngle,Vector3.forward)*referenceArmBase;
   limitedArm.rotation=Quaternion.AngleAxis(-Mathf.Min(requestedArmAngle,DemonstrationLimit),Vector3.forward)*limitedArmBase;
  }
  Ground(referenceActor); Ground(movingActor); Ground(silhouette);
  if(cutId=="pose-document" && documentPhase==2) {
   UpdateDocumentLeader(documentArmLine,documentArm,new Vector3(1f,1.55f,-.4f));
   UpdateDocumentLeader(documentFootLine,documentFoot,new Vector3(1f,.585f,-.4f));
  }
 }
 void LoadPresentation() {
  if(string.IsNullOrWhiteSpace(presentationId))return;
  var path=Root+"/animation-grid-presentations.json";
  if(!System.IO.File.Exists(path))throw new System.InvalidOperationException("Missing measured presentation profiles: "+path);
  var book=JsonUtility.FromJson<PresentationBook>(System.IO.File.ReadAllText(path));
  if(book==null || book.presentations==null)throw new System.InvalidOperationException("Invalid measured presentation profiles.");
  foreach(var item in book.presentations)if(item.id==presentationId)presentation=item;
  if(presentation==null || presentation.mode!=cutId)
   throw new System.InvalidOperationException("Presentation ID/mode does not match this cut: "+presentationId+" / "+cutId);
  if(Mathf.Abs(presentation.duration-frames/60f)>.018f)
   throw new System.InvalidOperationException("Measured presentation duration differs from requested full-cut frames.");
 }
 int PresentationValue(string key,float t,int fallback=0) {
  int value=fallback;float latest=float.NegativeInfinity;
  if(presentation.cues!=null)foreach(var cue in presentation.cues)
   if(cue.key==key && cue.start<=t+.0001f && cue.start>=latest){latest=cue.start;value=cue.value;}
  return value;
 }
 float PresentationCueStart(string key,float t) {
  float latest=0;
  if(presentation.cues!=null)foreach(var cue in presentation.cues)
   if(cue.key==key && cue.start<=t+.0001f)latest=Mathf.Max(latest,cue.start);
  return latest;
 }
 void BuildPresentation() {
  switch(presentationId) {
   case "A01-E004": case "A01-E053": BuildWorkflowPresentation();break;
   case "A01-E007": case "A01-E012":
    BuildList();break;
   case "A01-E009": BuildTimingPresentation();break;
   case "A01-E014":
    BuildPresentationPair("기준 자세","바꾼 자세");
    BuildPresentationMessages(new[]{"오른팔을 앞으로 내밀기","어깨 높이만 바꾸기","팔꿈치 방향만 바꾸기","허리 기울기만 바꾸기","무엇이 달라졌는지 자세로 보여 주기"});
    BuildPresentationLeaders();break;
   case "A01-E015":
    BuildDocument();
    foreach(var text in canvas.GetComponentsInChildren<Text>(true)) {
     if(text.text=="1. 자세 고정 · 촬영")text.text="1. 자세 고정";
     if(text.text=="2. 배경 분리 · 대비")text.text="2. 배경 · 명암";
     if(text.text=="3. 의도 주석")text.text="3. 의도 주석";
    }
    break;
   case "A01-E018": case "A01-E041":
    BuildMotionBrief();
    BuildPresentationMessages(new[]{"기준 자세와 움직임을 함께 보기","디딘 발과 몸의 중심","몸통이 향하는 방향","다음 자세로 돌아오기"});
    BuildPresentationLeaders();break;
   case "A01-E032":
    BuildMotionBrief();
    BuildPresentationMessages(new[]{"동작마다 필요한 조건이 달라져요","회피는 방향 · 대기는 성격 · 몸짓은 의도"});break;
   case "A01-E043":
    BuildPresentationPair("기준 자세 · 도해","검토할 자세 · 도해");
    BuildPresentationMessages(new[]{"어깨 주변의 모양도 확인","소품이 지나갈 공간도 확인"});
    BuildPresentationProps();BuildPresentationLeaders();break;
   case "A01-E044":
    BuildPresentationPair("사진의 모양 그대로","힘과 방향을 살린 대안");
    BuildPresentationMessages(new[]{"형태를 그대로 맞추기 어려울 때","전달할 방향은 유지하고 자세를 바꾸기"});
    BuildPresentationLeaders();break;
   case "A01-E049":
    BuildMotionBrief();BuildPresentationMessages(new[]{"검토할 항목 · 조작과 잘 맞는가?"});break;
   case "A01-E050":
    BuildPresentationPair("처음의 후보","수정한 후보");
    BuildPresentationMessages(new[]{"수정한 이유를 함께 남기기","맞지 않는 후보는 이번 동작에서 제외"});
    exclusionMark=Label("이번 동작에서 제외",535,400,42,Hex("9D3943"),850,70).gameObject;
    exclusionMark.SetActive(false);break;
   case "A01-E052":
    BuildPresentationPair("수정 전","수정 후");
    BuildPresentationMessages(new[]{"수정한 이유를 함께 공유","발의 위치를 바꾼 이유","무기가 지나갈 공간 · 설명용 도해","다음 동작에도 수정 이유를 남기기"});
    BuildPresentationProps();BuildPresentationLeaders();break;
   default:throw new System.InvalidOperationException("No native builder for measured presentation "+presentationId);
  }
  // Every label exists before the rasterizer runs, including inactive phases.
  foreach(var text in canvas.GetComponentsInChildren<Text>(true))if(text.fontSize<40)text.fontSize=40;
 }
 void BuildWorkflowPresentation() {
  Label("함께 맞춰 가는 제작 지시",490,220,46,Ink,850,80);
  Label("같은 목표 · 움직이는 결과",1395,220,46,Ink,900,80);
  string[] names={"1. 필요한 동작 정하기","2. 포즈와 시간 보여 주기","3. 결과를 함께 다듬기"};
  rowMarks=new Image[3];
  for(int i=0;i<3;i++) {
   rowMarks[i]=RectUI(460,365+i*145,700,100,new Color(.28f,.6f,.59f,.08f));
   Label(names[i],460,365+i*145,44,Ink,680,90);
  }
  movingActor=Actor("Shared animation intention",new Vector3(2.5f,0,0),false,2.7f,160);
 }
 void BuildPresentationPair(string left,string right) {
  Label(left,535,218,44,Ink,900,80);Label(right,1385,218,44,Ink,960,80);
  referenceActor=Actor("Measured presentation reference",new Vector3(-2.5f,0,0),false,2.7f,160);
  movingActor=Actor("Measured presentation variation",new Vector3(2.5f,0,0),false,2.7f,160);
 }
 void BuildPresentationMessages(string[] messages) {
  presentationMessages=new GameObject[messages.Length];
  for(int i=0;i<messages.Length;i++) {
   presentationMessages[i]=Label(messages[i],960,310,42,Ink,1740,76).gameObject;
   presentationMessages[i].SetActive(i==0);
  }
 }
 void BuildPresentationLeaders() {
  presentationLeaderLeft=Line("Reference editorial leader",new[]{Vector3.zero,Vector3.zero,Vector3.zero},Hex("236F78"),.026f).GetComponent<LineRenderer>();
  presentationLeaderRight=Line("Variation editorial leader",new[]{Vector3.zero,Vector3.zero,Vector3.zero},Hex("A43D48"),.026f).GetComponent<LineRenderer>();
 }
 void BuildPresentationProps() {
  // These solid rods illustrate occupied space. No collider query or physical
  // measurement is claimed; the original vendor assets are never edited.
  overlapPropLeft=Box("Illustrative prop overlap",Vector3.zero,new Vector3(.09f,1,.09f),Hex("A66532"));
  overlapPropRight=Box("Illustrative prop clearance",Vector3.zero,new Vector3(.09f,1,.09f),Hex("A66532"));
  overlapPropLeft.SetActive(false);overlapPropRight.SetActive(false);
 }
 GameObject PresentationUiGroup(string name) {
  var group=new GameObject(name,typeof(RectTransform));group.transform.SetParent(canvas.transform,false);group.layer=29;
  var rect=(RectTransform)group.transform;rect.anchorMin=rect.anchorMax=new Vector2(.5f,.5f);rect.sizeDelta=Vector2.zero;
  return group;
 }
 void InPresentationGroup(GameObject item,GameObject group){item.transform.SetParent(group.transform,false);}
 void BuildTimingPresentation() {
  Label("설계 예시 · 1초",505,220,44,Ink,880,80);
  Label("같은 시간축의 공격",1390,220,44,Ink,900,80);
  movingActor=Actor("Authored one second timing example",new Vector3(2.5f,0,0),false,2.7f,160);
  RectUI(500,390,720,24,Hex("B1B9BC"));
  attackPlayhead=RectUI(140,390,10,50,Hex("C9444E")).rectTransform;
  Label("동작 전체와 판정 구간을 구분",500,690,40,Ink,900,76);
  timingIntervalGroup=PresentationUiGroup("Chosen interval labels");
  intervalMark=RectUI(356,390,144,24,Hex("B5464E"));InPresentationGroup(intervalMark.gameObject,timingIntervalGroup);
  timingIntervalCaption=Label("가정한 판정 구간",500,310,40,Ink,900,70).gameObject;
  InPresentationGroup(timingIntervalCaption,timingIntervalGroup);
  timingSixtyGroup=PresentationUiGroup("Sixty authored frame marks");
  InPresentationGroup(Label("0프레임",165,450,40,Ink,250,60).gameObject,timingSixtyGroup);
  InPresentationGroup(Label("60프레임",815,450,40,Ink,250,60).gameObject,timingSixtyGroup);
  for(int i=0;i<=60;i++)InPresentationGroup(RectUI(140+i*12,390,i%10==0?3:2,i%10==0?34:16,Ink).gameObject,timingSixtyGroup);
  InPresentationGroup(Label("1초를 60개 구간으로",500,535,42,Ink,850,76).gameObject,timingSixtyGroup);
  timingFormulaGroup=PresentationUiGroup("Worked duration calculation");
  InPresentationGroup(Label("가정한 구간 · 12프레임",500,310,40,Ink,900,70).gameObject,timingFormulaGroup);
  InPresentationGroup(Label("12 ÷ 60 = 0.2초",500,610,46,Ink,850,80).gameObject,timingFormulaGroup);
  timingIntervalGroup.SetActive(false);timingSixtyGroup.SetActive(false);timingFormulaGroup.SetActive(false);
 }
 void ShowPresentationMessage(int phase) {
  if(presentationMessages==null)return;
  for(int i=0;i<presentationMessages.Length;i++)presentationMessages[i].SetActive(i==Mathf.Clamp(phase,0,presentationMessages.Length-1));
 }
 void HighlightPresentationRow(int row) {
  if(rowMarks==null)return;
  for(int i=0;i<rowMarks.Length;i++)rowMarks[i].color=i==row?new Color(.28f,.6f,.59f,.35f):new Color(.28f,.6f,.59f,.07f);
 }
 void ApplyPresentation(float t) {
  presentationTime=t;presentationPhase=PresentationValue("phase",t);presentationRow=PresentationValue("row",t);
  ShowPresentationMessage(presentationPhase);
  switch(presentationId) {
   case "A01-E004": case "A01-E053":
    HighlightPresentationRow(presentationPhase);
    if(presentationPhase==0)Pose(movingActor,"Walk_A",t);
    else if(presentationPhase==1)PoseOnce(movingActor,"FightM_Punch_A",.3f);
    else Pose(movingActor,"FightM_Punch_A",t-PresentationCueStart("phase",t));
    break;
   case "A01-E007": case "A01-E012":
    HighlightPresentationRow(presentationRow);
    if(presentationRow==2)PoseOnce(movingActor,"FightM_Punch_A",t-PresentationCueStart("row",t));
    else Pose(movingActor,presentationRow==0?"Idle_A":"Walk_A",t-PresentationCueStart("row",t));
    break;
   case "A01-E009":
    float clock=Mathf.Repeat(t,1);
    PoseNormalized(movingActor,"FightM_Punch_A",clock);
    attackPlayhead.anchoredPosition=new Vector2(140+720*clock-960,540-390);
    timingIntervalGroup.SetActive(presentationPhase>=1);timingSixtyGroup.SetActive(presentationPhase>=2);timingFormulaGroup.SetActive(presentationPhase>=3);
    timingIntervalCaption.SetActive(presentationPhase<3);
    intervalMark.color=clock>=12f/60f && clock<24f/60f?Hex("C9444E"):Hex("D5A7AA");
    break;
   case "A01-E015":
    PoseOnce(referenceActor,"FightM_Punch_A",.3f);PoseOnce(silhouette,"FightM_Punch_A",.3f);SetDocumentPhase(Mathf.Clamp(presentationPhase,0,2));break;
   case "A01-E014": case "A01-E043": case "A01-E044": case "A01-E050":
    PoseOnce(referenceActor,"FightM_Pose",0);PoseOnce(movingActor,"FightM_Pose",0);
    if(exclusionMark)exclusionMark.SetActive(presentationPhase==1);
    break;
   case "A01-E052":
    if(presentationPhase==1) {PoseOnce(referenceActor,"Walk_A",.05f);PoseOnce(movingActor,"Walk_A",.3f);}
    else {PoseOnce(referenceActor,"FightM_Pose",0);PoseOnce(movingActor,"FightM_Pose",0);}
    break;
   default:
    PoseOnce(referenceActor,"FightM_Punch_A",.3f);Pose(movingActor,"FightM_Punch_A",t);break;
  }
 }
 void RememberPresentationBone(Transform bone) {
  if(!bone)throw new System.InvalidOperationException("Required presentation bone missing.");
  if(!presentationOffsets.ContainsKey(bone))presentationOffsets.Add(bone,new BonePose{rotation=bone.localRotation,position=bone.localPosition});
 }
 void RestorePresentationBones() {
  foreach(var item in presentationOffsets) {item.Key.localRotation=item.Value.rotation;item.Key.localPosition=item.Value.position;}
  presentationOffsets.Clear();
 }
 void AimPresentationBone(Transform bone,Transform child,Vector3 direction,float weight=1) {
  if(!bone || !child)throw new System.InvalidOperationException("Right-arm presentation requires the verified Arm.R/ForeArm.R/Hand.R chain.");
  RememberPresentationBone(bone);
  var axis=child.position-bone.position;
  if(axis.sqrMagnitude>.000001f)bone.rotation=Quaternion.Slerp(Quaternion.identity,Quaternion.FromToRotation(axis,direction.normalized),Mathf.Clamp01(weight))*bone.rotation;
 }
 void ExtendRightArm(GameObject actor) {
  AimPresentationBone(FindBone(actor,"Arm.R"),FindBone(actor,"ForeArm.R"),Vector3.left);
  AimPresentationBone(FindBone(actor,"ForeArm.R"),FindBone(actor,"Hand.R"),Vector3.left);
 }
 void BendPresentationTorso(GameObject actor,float degrees) {
  var torso=FindBone(actor,"Torso");var left=FindBone(actor,"Shoulder.L");var right=FindBone(actor,"Shoulder.R");
  if(!torso || !left || !right)throw new System.InvalidOperationException("Torso/shoulder bones required by presentation.");
  RememberPresentationBone(torso);torso.rotation=Quaternion.AngleAxis(degrees,(right.position-left.position).normalized)*torso.rotation;
 }
 void FlushPresentationPoses() {
  RestorePresentationBones();base.FlushPoses();
  presentationTargetLeft=null;presentationTargetRight=null;
  if(presentationId=="A01-E014") {
   ExtendRightArm(referenceActor);ExtendRightArm(movingActor);
   float phaseBlend=Mathf.SmoothStep(0,1,Mathf.Clamp01((presentationTime-PresentationCueStart("phase",presentationTime))/.3f));
   string target="Hand.R";
   if(presentationPhase==1) {
    var shoulder=FindBone(movingActor,"Shoulder.R");RememberPresentationBone(shoulder);shoulder.position+=Vector3.up*(.13f*phaseBlend);target="Shoulder.R";
   } else if(presentationPhase==2) {
    AimPresentationBone(FindBone(movingActor,"ForeArm.R"),FindBone(movingActor,"Hand.R"),new Vector3(-.7f,.6f,0),phaseBlend);target="ForeArm.R";
   } else if(presentationPhase>=3) {BendPresentationTorso(movingActor,presentationPhase==4?13:13*phaseBlend);target="Torso";}
   presentationTargetLeft=FindBone(referenceActor,target);presentationTargetRight=FindBone(movingActor,target);
  } else if(presentationId=="A01-E043" || presentationId=="A01-E052") {
   if(presentationId=="A01-E043" || presentationPhase!=1) {ExtendRightArm(referenceActor);ExtendRightArm(movingActor);}
   var target=presentationId=="A01-E052" && presentationPhase==1?"Foot.L":presentationPhase==0?"Shoulder.R":"Hand.R";
   presentationTargetLeft=FindBone(referenceActor,target);presentationTargetRight=FindBone(movingActor,target);
  } else if(presentationId=="A01-E044" || presentationId=="A01-E050") {
   ExtendRightArm(referenceActor);ExtendRightArm(movingActor);
   // An alternative authored pose preserves the screen-left action direction.
   // It is not a solved anatomical limit, physical force or controller test.
   float alternativeBlend=presentationId=="A01-E050"?1:presentationPhase==0?0:Mathf.SmoothStep(0,1,Mathf.Clamp01((presentationTime-PresentationCueStart("phase",presentationTime))/.45f));
   BendPresentationTorso(movingActor,10*alternativeBlend);
   AimPresentationBone(FindBone(movingActor,"ForeArm.R"),FindBone(movingActor,"Hand.R"),new Vector3(-1,.2f,0),alternativeBlend);
   presentationTargetLeft=FindBone(referenceActor,"Hand.R");presentationTargetRight=FindBone(movingActor,"Hand.R");
  } else if(presentationId=="A01-E018" || presentationId=="A01-E041") {
   string target=presentationPhase==1?"Foot.L":presentationPhase==2?"Torso":"Hand.R";
   presentationTargetLeft=FindBone(referenceActor,target);presentationTargetRight=FindBone(movingActor,target);
  }
  Ground(referenceActor);Ground(movingActor);Ground(silhouette);
  if(presentationId=="A01-E015" && documentPhase==2) {
   UpdateDocumentLeader(documentArmLine,documentArm,new Vector3(1f,1.55f,-.4f));
   UpdateDocumentLeader(documentFootLine,documentFoot,new Vector3(1f,.585f,-.4f));
  }
  if(presentationLeaderLeft) {
   presentationLeaderLeft.gameObject.SetActive(presentationTargetLeft);presentationLeaderRight.gameObject.SetActive(presentationTargetRight);
   if(presentationTargetLeft)UpdateDocumentLeader(presentationLeaderLeft,presentationTargetLeft,new Vector3(-3.7f,2.75f,-.4f));
   if(presentationTargetRight)UpdateDocumentLeader(presentationLeaderRight,presentationTargetRight,new Vector3(3.7f,2.75f,-.4f));
  }
  if(overlapPropLeft) {
   bool show=presentationId=="A01-E043"?presentationPhase>=1:presentationPhase>=2;
   overlapPropLeft.SetActive(show);overlapPropRight.SetActive(show);
   if(show){PlaceIllustrativeProp(overlapPropLeft,referenceActor,true);PlaceIllustrativeProp(overlapPropRight,movingActor,false);}
  }
 }
 void PlaceIllustrativeProp(GameObject prop,GameObject actor,bool overlaps) {
  var hand=FindBone(actor,"Hand.R");var torso=FindBone(actor,"Torso");
  if(!hand || !torso)throw new System.InvalidOperationException("Illustrative prop needs Hand.R and Torso.");
  var begin=hand.position;
  var end=overlaps?torso.position+Vector3.up*.27f:begin+new Vector3(-.8f,.35f,0);
  var delta=end-begin;
  prop.transform.position=(begin+end)*.5f;prop.transform.rotation=Quaternion.FromToRotation(Vector3.up,delta.normalized);
  prop.transform.localScale=new Vector3(.09f,Mathf.Max(.01f,delta.magnitude),.09f);
 }
 float CutProgress(float t){return Mathf.Clamp01(t/Mathf.Max(.1f,(frames-1)/60f));}
 Transform FindBone(GameObject actor,params string[] names) {
  if(!actor)return null;
  var transforms=actor.GetComponentsInChildren<Transform>(true);
  foreach(var name in names)foreach(var bone in transforms)if(bone.name==name)return bone;
  return null;
 }
 RectTransform Meter(float x,float y,Color color) {
  var rect=RectUI(x,y,0,12,color).rectTransform;
  rect.pivot=new Vector2(0,.5f);return rect;
 }
 void SetDocumentPhase(int phase) {
  if(phase==documentPhase)return;
  documentPhase=phase;documentPaper.SetActive(phase>0);
  for(int i=0;i<documentSteps.Length;i++)documentSteps[i].color=i==phase?new Color(.28f,.6f,.59f,.3f):new Color(.28f,.6f,.59f,.07f);
  for(int i=0;i<documentRenderers.Length;i++) {
   if(phase==0)documentRenderers[i].sharedMaterials=documentMaterials[i];
   else {
    var flat=new Material[documentMaterials[i].Length];
    for(int j=0;j<flat.Length;j++)flat[j]=Mat(Ink,true);
    documentRenderers[i].sharedMaterials=flat;
   }
  }
  documentNotes[0].SetActive(phase==2 && documentArm);
  documentNotes[1].SetActive(phase==2 && documentFoot);
  documentArmLine.gameObject.SetActive(phase==2 && documentArm);
  documentFootLine.gameObject.SetActive(phase==2 && documentFoot);
 }
 void UpdateDocumentLeader(LineRenderer line,Transform target,Vector3 start) {
  if(!line || !target)return;
  var endpoint=transform.InverseTransformPoint(target.position);
  endpoint.z=-.4f;
  line.SetPositions(new[]{start,new Vector3(start.x+.28f,start.y,start.z),endpoint});
 }
 void Ground(GameObject actor) {
  if(!actor)return;
  float minY=float.PositiveInfinity;
  foreach(var skin in actor.GetComponentsInChildren<SkinnedMeshRenderer>()) {
   var mesh=new Mesh();skin.BakeMesh(mesh);
   foreach(var v in mesh.vertices)minY=Mathf.Min(minY,skin.transform.TransformPoint(v).y);
   DestroyImmediate(mesh);
  }
  if(!float.IsInfinity(minY))actor.transform.position+=Vector3.up*(.02f-minY);
 }
}
}
