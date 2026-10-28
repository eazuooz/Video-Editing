using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.DesignVisualV2 {
// A new editable stage; all v2 sources, saved scenes and captures stay intact.
// Cue boundaries are measured speech times supplied by the isolated edit builder.
public class D29ClarityStage : DesignClarityLessonStage {
 [Serializable] public class Cue { public string id,mode,title; public float[] phaseSeconds; }
 [Serializable] public class CueFile { public bool timingLocked; public Cue[] cuts; }
 Cue spec; string mode; GameObject car,other,person,cup,table,marker,guide,trail;
 Text left,right,status,evidenceLabel; Image input,secondary,evidence; Vector3 carStart,cupStart,cupEnd;
 Image[] antennaMarks;
 float total; Vector3[] road; GameObject[] bars=new GameObject[3];
 public override void Build(){
  var path=Path.Combine(Application.dataPath,"../../../projects/kind-to-beginners/production/clarity-v3/unity-cues.json");
  var all=JsonUtility.FromJson<CueFile>(File.ReadAllText(Path.GetFullPath(path)));
  spec=all.cuts.First(c=>c.id==cutId); mode=spec.mode;total=Mathf.Max(.1f,frames/60f);
  if(spec.phaseSeconds==null||spec.phaseSeconds.Length!=3)throw new Exception("Three speech cue times required: "+cutId);
  if(spec.phaseSeconds[0]<0||spec.phaseSeconds[1]<=spec.phaseSeconds[0]||spec.phaseSeconds[2]<=spec.phaseSeconds[1]||spec.phaseSeconds[2]>total)throw new Exception("Invalid cue order: "+cutId);
  Title(mode=="steering"?"핸들 어시스트 · Smart Steering":mode=="acceleration"?"자동 액셀 · Auto-Accelerate":spec.title);
  switch(mode){
   case "intent":BuildIntent();break;
   case "goal":BuildRoad(false);break;
   case "onboarding":BuildRoad(false);break;
   case "steering":BuildRoad(true);break;
   case "acceleration":BuildRoad(true);break;
   case "turbo":BuildTurbo();break;
   case "placement":BuildPlacement();break;
   case "choice":BuildChoice();break;
   case "summary":BuildSummary();break;
   default:throw new Exception("Unknown D29 mode "+mode);
  }
 }
 float Phase(float t,int n){float start=n==0?0:spec.phaseSeconds[n-1];float end=spec.phaseSeconds[n];return Mathf.SmoothStep(0,1,Mathf.InverseLerp(start,end,t));}
 int Step(float t){return t<spec.phaseSeconds[0]?0:t<spec.phaseSeconds[1]?1:2;}
 void Place(GameObject o,Vector3 p){if(o)o.transform.position=p;}
 void LabelPair(string a,string b){left=Label(a,500,250,44,White,800,70);right=Label(b,1400,250,44,Teal,800,70);}
 void Track(Vector3[] points,Color c,float width=.08f){Line("Illustrative route",points,c,width);}
 void RoadSurface(Vector3[] points,float width){
  // The road is horizontal geometry. A wide camera-facing LineRenderer would
  // stand up like a billboard and incorrectly occlude the moving vehicle.
  for(int i=0;i<points.Length-1;i++){
   Vector3 delta=points[i+1]-points[i],center=(points[i+1]+points[i])*.5f;center.y=.035f;
   var tile=Box("Flat road section "+i,center,new Vector3(width,.06f,delta.magnitude+.04f),Hex("303A40"));
   tile.transform.rotation=Quaternion.Euler(0,Mathf.Atan2(delta.x,delta.z)*Mathf.Rad2Deg,0);
  }
 }
 void CarPose(GameObject o,Vector3 p,Vector3 tangent){Place(o,p);if(tangent.sqrMagnitude>.0001f)o.transform.rotation=Quaternion.Euler(0,Mathf.Atan2(tangent.x,tangent.z)*Mathf.Rad2Deg,0);}
 void BuildIntent(){
  LabelPair("숙련자 · 결승선","첫 시도 · 코너 하나");
  Box("Shared track",new Vector3(0,.02f,0),new Vector3(14,.08f,3.8f),Hex("303A40"));
  Track(new[]{new Vector3(-6,.1f,-.8f),new Vector3(6,.1f,-.8f)},Yellow);
  Track(new[]{new Vector3(-6,.1f,1.2f),new Vector3(0,.1f,1.2f),new Vector3(1.5f,.1f,-.3f),new Vector3(5,.1f,-.3f)},Teal);
  car=Asset("car",new Vector3(-5.5f,.12f,-.8f),1.25f,90);
  other=Asset("car",new Vector3(-5.5f,.12f,1.2f),1.25f,90);Tint(other,Teal);
  // A roadside barrier is an object the beginner must turn before, not a combat wall.
  Box("Corner edge",new Vector3(1.3f,.4f,1.8f),new Vector3(.2f,.8f,1.7f),Grey);
  marker=Line("Finish",new[]{new Vector3(5.5f,.12f,-2),new Vector3(5.5f,.12f,2)},White,.15f);
  status=Label("같은 레이스, 다른 첫 목표",960,805,46,White,1500,85);
 }
 void BuildRoad(bool help){
  var pts=new Vector3[51];for(int i=0;i<pts.Length;i++){float u=i/(float)(pts.Length-1);pts[i]=new Vector3(-6+12*u,.12f,-1.3f+2.2f*Mathf.Sin(u*Mathf.PI));}road=pts;
  RoadSurface(pts,2.4f);Track(pts,Teal,.1f);
  car=Asset("car",pts[0],1.35f,90);carStart=pts[0];
  input=RectUI(390,745,220,100,Grey);Label("방향",390,745,44,Hex("151A1D"),210,70);
  secondary=RectUI(760,745,300,100,Grey);Label("가속 유지",760,745,44,Hex("151A1D"),290,70);
  status=Label("직접 입력 → 화면의 변화",1340,745,44,White,650,120);
  if(mode=="steering"){
   guide=Line("Outward approach",new[]{pts[15],new Vector3(-1,.15f,3)},Red,.13f);
   marker=Line("Corrected inward route",new[]{new Vector3(-1,.15f,3),pts[30],pts[44]},Green,.13f);
   Label("원리 시연 · 실제 보정값 아님",960,845,32,Grey,1300,45);
   evidence=Picture("D:/Github/VideoEditing/projects/kind-to-beginners/production/local/batch-v1/sources/mk8-official-035.jpg",420,376,530,298);
   evidenceLabel=Label("실제 게임 · 켜진 보조의 안테나",420,205,36,White,710,60);
   evidence.gameObject.SetActive(false);evidenceLabel.gameObject.SetActive(false);
   // Source035.jpg was inspected directly: rear rod/glow x640..715,y300..460.
   // The marks are editorial guides on the preserved full-aspect photo.
   antennaMarks=new[]{RectUI(411,384,4,88,Green),RectUI(465,384,4,88,Green),RectUI(438,340,58,4,Green),RectUI(438,428,58,4,Green)};
   foreach(var m in antennaMarks)m.gameObject.SetActive(false);
  }
  else if(mode=="acceleration")Label("버튼을 놓아도 앞으로",960,270,46,White,1300,65);
  else Label("첫 코너 하나를 직접 돌아보기",960,270,46,White,1400,65);
 }
 Vector3 Road(float u){float n=Mathf.Clamp01(u)*(road.Length-1);int k=Mathf.Min(road.Length-2,Mathf.FloorToInt(n));return Vector3.Lerp(road[k],road[k+1],n-k);}
 Vector3 RoadPosition(float t){
  float u=.08f+.84f*Mathf.Clamp01(t/Mathf.Max(.1f,spec.phaseSeconds[2]));
  if(mode!="steering")return Road(u);
  int step=Step(t);
  if(step==0)return Vector3.Lerp(Road(.12f),new Vector3(-1,.15f,3),Phase(t,0));
  if(step==1)return Vector3.Lerp(new Vector3(-1,.15f,3),Road(.6f),Phase(t,1));
  return Road(.6f+.32f*Phase(t,2));
 }
 void BuildTurbo(){
  var pts=new Vector3[41];for(int i=0;i<pts.Length;i++){float a=-Mathf.PI/2+i/(float)(pts.Length-1)*Mathf.PI;pts[i]=new Vector3(4*Mathf.Sin(a),.12f,2*Mathf.Cos(a));}road=pts;
  RoadSurface(pts,2.1f);Track(pts,Teal);
  car=Asset("car",pts[0],1.3f,90);
  string[] names={"미니 터보","슈퍼 미니 터보","울트라 미니 터보"};Color[] colors={Teal,Yellow,Red};
  for(int i=0;i<3;i++){bars[i]=Box("Illustrative charge tier "+i,new Vector3(-2.6f+i*2.6f,.6f,-2.3f),new Vector3(2.2f,.8f,.5f),colors[i]);Label(names[i],610+i*350,765,40,colors[i],345,65);}
  status=Label("드리프트 → 모은 힘 → 짧은 가속",960,270,44,White,1450,65);
  Label("단계 설명 · 실제 충전량 측정 아님",960,845,32,Grey,1500,45);
 }
 void BuildPlacement(){
  table=Asset("table",new Vector3(0,0,0),1.8f,0);
  Asset("chair",new Vector3(3.9f,0,.5f),2.2f,-90);
  person=Actor("First-time organizer",new Vector3(-4.2f,0,.5f),false,2.8f,0);
  cupStart=new Vector3(-.65f,1.83f,-.2f);cupEnd=new Vector3(.65f,1.83f,-.2f);
  cup=Asset("cup",cupStart,.8f,0);
  marker=Line("Two available places",new[]{new Vector3(-1.4f,1.9f,-.5f),new Vector3(-1.4f,1.9f,.6f),new Vector3(1.6f,1.9f,.6f),new Vector3(1.6f,1.9f,-.5f)},Teal,.08f);
  guide=Line("Unnecessary instruction",new[]{new Vector3(-.9f,3.3f,-.5f),new Vector3(.65f,2.2f,-.2f)},Red,.09f);
  guide.SetActive(false);
  LabelPair("조작은 가볍게","놓을 자리는 직접");
  input=RectUI(415,790,250,95,Teal);Label("집기 / 놓기",415,790,42,Hex("151A1D"),245,65);
  status=Label("컵을 고르고 → 놓고 → 다시 옮기기",1170,790,44,White,1120,100);
  Label("배치 원리 시연 · Unpacking 게임 UI 아님",960,865,30,Grey,1500,45);
 }
 void BuildChoice(){
  person=Actor("Explorer",new Vector3(0,0,-1.8f),false,2.8f,0);
  Asset("tree",new Vector3(-4,0,1.3f),2.5f,0);Asset("tree",new Vector3(4.1f,0,1.3f),2.3f,50);
  Track(new[]{new Vector3(0,.12f,-2),new Vector3(0,.12f,0),new Vector3(-4,.12f,1)},Teal,.16f);
  Track(new[]{new Vector3(0,.12f,0),new Vector3(4,.12f,1)},Yellow,.16f);
  guide=Line("Prescriptive direction",new[]{new Vector3(0,3.6f,0),new Vector3(4,1,1),new Vector3(3,1,1.1f)},Red,.14f);
  marker=Sphere("Self-chosen destination",new Vector3(-3.5f,.35f,1),.55f,Teal);
  LabelPair("내가 가 보고 싶은 곳","정해 준 길만 따라가기");
  status=Label("조작 안내 뒤에는 선택을 돌려주기",960,820,46,White,1540,90);
 }
 void BuildSummary(){
  car=Asset("car",new Vector3(-5,0,0),1.5f,90);
  table=Asset("table",new Vector3(0,0,0),1.5f,0);cup=Asset("cup",new Vector3(-.7f,1.53f,0),.65f,0);
  person=Actor("Independent explorer",new Vector3(3,0,0),false,2.5f,0);
  Track(new[]{new Vector3(2,.1f,-1.5f),new Vector3(3,.1f,0),new Vector3(5,.1f,1)},Teal,.1f);
  Label("목표 맞추기",440,760,44,Yellow,520,70);Label("첫 행동 돕기",960,760,44,White,520,70);Label("다음 선택 돌려주기",1510,760,44,Teal,650,70);
  status=Label("다음 한 판을 스스로 고르게",960,270,48,White,1500,70);
 }
 public override void Apply(float t){
  int step=Step(t);float p0=Phase(t,0),p1=Phase(t,1),p2=Phase(t,2);
  switch(mode){
   case "intent":
    CarPose(car,new Vector3(Mathf.Lerp(-5.5f,5.2f,p0),.12f,-.8f),Vector3.right);
    Vector3 q=step==0?Vector3.Lerp(new Vector3(-5.5f,.12f,1.2f),new Vector3(-1,.12f,1.2f),p0):step==1?Vector3.Lerp(new Vector3(-1,.12f,1.2f),new Vector3(1.5f,.12f,-.3f),p1):Vector3.Lerp(new Vector3(1.5f,.12f,-.3f),new Vector3(4.5f,.12f,-.3f),p2);
    CarPose(other,q,step==1?new Vector3(2.5f,0,-1.5f):Vector3.right);right.color=step>0?Green:Teal;break;
   case "goal": case "onboarding": case "acceleration": case "steering":
    Vector3 pos=RoadPosition(t);
    if(mode=="steering"){
     guide.SetActive(step<2);marker.SetActive(step>0);
     evidence.gameObject.SetActive(step==2);evidenceLabel.gameObject.SetActive(step==2);
     foreach(var m in antennaMarks)m.gameObject.SetActive(step==2);
    }
    Vector3 tangent=RoadPosition(Mathf.Min(total,t+.02f))-RoadPosition(Mathf.Max(0,t-.02f));
    if(tangent.sqrMagnitude<.000001f)tangent=Road(.92f)-Road(.91f);
    CarPose(car,pos,tangent);
    input.color=(step==1&&mode!="acceleration")?Teal:Grey;
    secondary.color=(mode=="acceleration"&&step>0)?Grey:Yellow;
    status.text=mode=="acceleration"?(step==0?"누르고 출발":"손은 놓아도 · 주행은 계속"):mode=="steering"?(step==0?"코스 바깥으로 접근":"안쪽으로 방향을 보조"):step==0?"하나의 입력":step==1?"내 입력으로 코너 통과":"다음 길은 스스로";break;
   case "turbo":
    float tu=.08f+.8f*Mathf.Clamp01(t/Mathf.Max(.1f,spec.phaseSeconds[2]));CarPose(car,Road(tu),Road(Mathf.Min(.99f,tu+.02f))-Road(Mathf.Max(0,tu-.02f)));
    for(int i=0;i<3;i++){bars[i].transform.localScale=new Vector3(2.2f,.25f+(.75f*(i<=step?1:0)),.5f);bars[i].SetActive(i<2||step==2);}
    if(step==2){Tint(bars[2],Grey);status.text="핸들 어시스트 ON · 3단계는 사용 불가";}break;
   case "placement":
    Vector3 mid=new Vector3(-.9f,2.9f,-.2f);Vector3 target=Vector3.Lerp(cupStart,mid,p0);
    if(step==1)target=Vector3.Lerp(mid,cupEnd,p1);
    if(step==2)target=Vector3.Lerp(cupEnd,new Vector3(-.6f,1.83f,.2f),p2)+Vector3.up*(Mathf.Sin(p2*Mathf.PI)*.65f);
    Place(cup,target);
    // Brief clicks with released intervals communicate that no button hold is needed.
    bool click=(t>=.15f&&t<.4f)||(t>=spec.phaseSeconds[1]-.22f&&t<spec.phaseSeconds[1])||(t>=spec.phaseSeconds[1]+.2f&&t<spec.phaseSeconds[1]+.45f);
    input.color=click?Teal:Grey;Pose(person,"Idle_A",t);
    bool last=cutId=="06-06";guide.SetActive(last&&step>=1);status.text=last?(step>=1?"모든 자리를 정해 주면":"놓을 곳은 내가 고르기"):step==0?"하나를 집기":step==1?"내가 고른 자리에 놓기":"다시 옮겨도 괜찮음";break;
   case "choice":
    bool dictated=cutId=="07-02";
    guide.SetActive(dictated||step==0);marker.SetActive(!dictated&&step>0);
    float walk=dictated?Mathf.Clamp01(t/Mathf.Max(.1f,spec.phaseSeconds[2])):step==0?0:step==1?.45f*p1:.45f+.55f*p2;
    Vector3 dest=Vector3.Lerp(new Vector3(0,0,-1.8f),new Vector3(dictated?3:-3,0,.9f),walk);Place(person,dest);
    person.transform.rotation=Quaternion.Euler(0,dictated?0:step==0?0:180,0);Pose(person,(dictated||step>0)?"Walk_A":"Idle_A",t);
    right.color=(dictated||step==0)?Red:Grey;left.color=(!dictated&&step>0)?Teal:Grey;
    if(dictated)status.text="다음 선택까지 전부 정해 주면";
    break;
   case "summary":
    Place(car,new Vector3(-5+1.3f*p0,0,0));Place(cup,new Vector3(-.7f+1.4f*p1,1.53f+Mathf.Sin(p1*Mathf.PI)*.5f,0));Place(person,Vector3.Lerp(new Vector3(3,0,0),new Vector3(5,0,1),p2));person.transform.rotation=Quaternion.Euler(0,-26.565f,0);Pose(person,step==2?"Walk_A":"Idle_A",t);break;
  }
 }
}
}
