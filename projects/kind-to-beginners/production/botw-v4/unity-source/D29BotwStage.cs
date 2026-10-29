using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Yamyam.DesignVisualV2 {
// Independently authored explanation, not a reconstruction of Nintendo's assets,
// HUD, cold thresholds, damage rate, food duration, or clothing statistics.
public class D29BotwStage : DesignBotwLessonStage {
 [Serializable] public class Cue { public string id,mode,title,variant,canonicalTerm; public float[] phaseSeconds; }
 [Serializable] public class CueFile { public bool timingLocked; public Cue[] cuts; }
 Cue spec; string mode; float total,now; int currentStep;
 GameObject person,other,table,cup,marker,guide,meal,bowl,pot,coat,scarf,coldGroup,decisionLeft,decisionRight;
 GameObject[] wind=new GameObject[5]; Vector3[] windStart=new Vector3[5];
 Text status,left,right,temperatureLabel,healthLabel,protectionLabel,durationLabel;
 Image input,temperatureRegion,temperaturePointer,healthFill,protectionRegion;
 GameObject temperatureUi,healthUi,protectionUi;
 Vector3 cupStart,cupEnd,personStart; Transform upperArm,foreArm,hand,pickupTorso,coldHead,coldArmLeft,coldArmRight;
 Text heartText; bool shivering;
 bool poseForEating,poseForPickup; Vector3 bowlRest;
 GameObject firstItem,nextItem,pickupState,nearTarget,farTarget,observerCue; Vector3 firstItemStart;
 readonly List<(GameObject scarf,GameObject actor)> pendingScarfAttachments=new List<(GameObject,GameObject)>();
 Text firstResult; bool competition;
 readonly Color Snow=Hex("B6C7CE"),Cold=Hex("86C2D7"),Dark=Hex("222D34"),Warm=Hex("D9AA72");

 public override void Build(){
  var path=Path.GetFullPath(Path.Combine(Application.dataPath,"../../../projects/kind-to-beginners/production/botw-v4/unity-cues.json"));
  var all=JsonUtility.FromJson<CueFile>(File.ReadAllText(path));spec=all.cuts.First(c=>c.id==cutId);mode=spec.mode;total=frames/60f;
  if(spec.phaseSeconds==null||spec.phaseSeconds.Length!=3||spec.phaseSeconds[0]<=0||spec.phaseSeconds[1]<=spec.phaseSeconds[0]||spec.phaseSeconds[2]<=spec.phaseSeconds[1]||spec.phaseSeconds[2]>total+.001f)throw new Exception("Measured three-phase cue order required: "+cutId);
  Title(spec.title);
  if(!string.IsNullOrWhiteSpace(spec.canonicalTerm))Label(spec.canonicalTerm,960,172,44,White,1600,60);
  switch(mode){
   case "cold-intent":case "cold-goal":BuildFirstExperience();break;
   case "cold-overview":case "cold-information":case "cold-food":case "cold-clothing":case "cold-compare":BuildCold();break;
   case "placement":BuildPlacement();break;
   case "choice":BuildChoice();break;
   case "summary":BuildSummary();break;
   default:throw new Exception("Unsupported botw-v4 mode: "+mode);
  }
  // This isolated editor render request uses ordinary draw submission. Keep
  // only these newly instantiated meshes out of the asynchronous resident set.
  var optOutType=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("UnityEngine.Rendering.DisallowGPUDrivenRendering")).FirstOrDefault(t=>t!=null);
  if(optOutType==null)throw new Exception("Installed URP per-object GPU-driven opt-out component unavailable.");
  foreach(var renderer in GetComponentsInChildren<MeshRenderer>(true))if(!renderer.GetComponent(optOutType))renderer.gameObject.AddComponent(optOutType);
 }
 float Phase(float t,int n){return Mathf.SmoothStep(0,1,Mathf.InverseLerp(n==0?0:spec.phaseSeconds[n-1],spec.phaseSeconds[n],t));}
 int Step(float t){return t<spec.phaseSeconds[0]?0:t<spec.phaseSeconds[1]?1:2;}
 void Place(GameObject o,Vector3 p){if(o)o.transform.position=p;}
 void Track(string name,Vector3[] pts,Color c,float width=.07f){Line(name,pts,c,width);}
 void PathSurface(string name,Vector3 a,Vector3 b,float width,Color color){var d=b-a;var o=Box(name,(a+b)*.5f,new Vector3(d.magnitude,.07f,width),color);o.transform.rotation=Quaternion.Euler(0,-Mathf.Atan2(d.z,d.x)*Mathf.Rad2Deg,0);}
 GameObject Group(string name){var o=new GameObject(name);o.transform.SetParent(transform,false);o.layer=29;return o;}
 void Parent(GameObject child,GameObject group){child.transform.SetParent(group.transform,true);}
 void UiParent(Component child,GameObject group){child.transform.SetParent(group.transform,false);}
 void PairLabels(string a,string b){left=Label(a,500,240,44,White,820,70);right=Label(b,1410,240,44,Teal,820,70);}

 void BuildFirstExperience(){
  competition=spec.variant=="agreed-competition";
  person=Actor("Newcomer controlling their own first action",new Vector3(-3.8f,0,-.6f),false,2.7f,0);
  other=Actor("Experienced companion",new Vector3(-3.8f,0,1.6f),true,2.7f,0);
  PathSurface("One visible trail",new Vector3(-5.5f,.05f,-.6f),new Vector3(5.3f,.05f,-.6f),1.6f,Hex("465356"));
  firstResult=Label("",1170,750,44,White,1080,90);status=Label("",960,833,46,White,1540,90);
  if(competition){
   PathSurface("Second agreed lane",new Vector3(-5.5f,.05f,1.6f),new Vector3(5.3f,.05f,1.6f),1.3f,Hex("465356"));
   Track("Shared finish",new[]{new Vector3(4.6f,.15f,-1.5f),new Vector3(4.6f,.15f,2.3f)},Yellow,.1f);
   PairLabels("함께 겨루기로 동의","같은 목표로 승부");
   observerCue=Line("Both agree",new[]{new Vector3(-1.3f,3.8f,0),new Vector3(-.8f,3.3f,0),new Vector3(.1f,4.3f,0)},Green,.1f);
   return;
  }
  firstItemStart=new Vector3(-.9f,.12f,-.65f);firstItem=Asset("meal",firstItemStart,.12f,0);
  nextItem=Asset("bowl",new Vector3(2.7f,.12f,-.6f),.18f,0);
  Asset("tree",new Vector3(5.2f,0,2.2f),2.7f,20);
  nearTarget=Line("First reachable action",new[]{new Vector3(-1.6f,.2f,-1.3f),new Vector3(-.2f,.2f,-1.3f),new Vector3(-.2f,.2f,.1f),new Vector3(-1.6f,.2f,.1f),new Vector3(-1.6f,.2f,-1.3f)},Teal,.08f);
  farTarget=Line("Distant route",new[]{new Vector3(-2.5f,.2f,1.8f),new Vector3(4.3f,.2f,1.8f),new Vector3(3.7f,.2f,1.3f),new Vector3(4.3f,.2f,1.8f),new Vector3(3.7f,.2f,2.3f)},Yellow,.085f);
  pickupState=Group("Object acquired indicator");
  var check=Line("Acquisition check",new[]{new Vector3(-.3f,3.4f,-.6f),new Vector3(.05f,3.05f,-.6f),new Vector3(.75f,3.95f,-.6f)},Green,.1f);Parent(check,pickupState);
  PairLabels("눈앞의 물건 · 첫 조작","익숙한 목적지 · 빠른 진행");
  input=RectUI(340,750,235,85,Grey);Label("집기",340,750,44,Hex("151A1D"),230,70);
  upperArm=FindBone(person,"Arm.R");foreArm=FindBone(person,"ForeArm.R");hand=FindBone(person,"Hand.R");pickupTorso=FindBone(person,"Torso");
 }

 void ApplyFirstExperience(float t,int step,float p0,float p1,float p2){
  if(competition){
   float walk=step==0?0:step==1?p1:1;
   Place(person,Vector3.Lerp(new Vector3(-3.8f,0,-.6f),new Vector3(3.9f,0,-.6f),walk));
   Place(other,Vector3.Lerp(new Vector3(-3.8f,0,1.6f),new Vector3(3.9f,0,1.6f),walk));
   Pose(person,step==1?"Walk_A":"Idle_A",t);Pose(other,step==1?"Walk_A":"Idle_A",t);
   observerCue.SetActive(step!=1);
   firstResult.text=step==0?"두 사람 모두 같은 승부를 원함":step==1?"약속한 목표에 전력을 다함":"같이 원한 승부";
   status.text="승부의 전제 · 서로 같은 목표에 동의";return;
  }
  bool contrast=mode=="cold-intent"||spec.variant=="first-input";
  bool onboarding=spec.variant=="onboarding";
  farTarget.SetActive(contrast&&step==0);nearTarget.SetActive(step<=1);pickupState.SetActive(step==2);
  Place(other,new Vector3(-3.8f+((step==2)?-.7f*p2:0),0,1.6f));Pose(other,"Idle_A",t);
  Vector3 approach=new Vector3(-1.75f,0,-.65f);Vector3 pos=step==0?Vector3.Lerp(new Vector3(-3.8f,0,-.6f),approach,p0):step==1?approach:Vector3.Lerp(approach,new Vector3(1.65f,0,-.6f),p2);
  Place(person,pos);Pose(person,step==1?"Idle_A":"Walk_A",t);poseForPickup=step==1;
  firstItem.SetActive(step<2);Place(firstItem,firstItemStart);
  nextItem.SetActive(step==2||contrast);input.color=step==1&&p1<.2f?Teal:Grey;
  left.color=step>=1?Teal:White;right.color=contrast&&step==0?Yellow:Grey;
  firstResult.text=step==0?(contrast?"어디로 갈까? · 무엇을 해 볼까?":"할 행동 하나를 고름"):step==1?(onboarding?"입력 → 물건의 변화":"직접 집는 조작"):"물건을 얻음 → 다음 물건은 스스로";
  status.text=step==0?(contrast?"기대하는 경험이 다를 수 있음":"눈앞의 목표 하나"):step==1?"친구가 직접 눌러 보기":spec.variant=="first-pickup"?"옆 사람은 물러나고 · 다음 행동은 직접":"내 조작이 만든 결과를 확인";
 }

 void BuildCold(){
  // One continuous path, a visible snow boundary, the same articulated person.
  Box("Cold snow region",new Vector3(2.7f,-.02f,.4f),new Vector3(8,.12f,5.4f),Snow);
  PathSurface("Walkable trail",new Vector3(-6,.06f,-.4f),new Vector3(6,.06f,-.4f),1.7f,Hex("647079"));
  Track("Cold boundary",new[]{new Vector3(-1.3f,.13f,-2.5f),new Vector3(-1.3f,.13f,2.8f)},Cold,.08f);
  var tree=Asset("tree",new Vector3(5.3f,0,2.2f),2.3f,15);Tint(tree,Hex("52636A"));
  var tree2=Asset("tree",new Vector3(1.6f,0,2.6f),1.8f,55);Tint(tree2,Hex("627680"));
  personStart=new Vector3(-4.6f,.11f,-.5f);person=Actor("Same first-time explorer",personStart,false,2.7f,0);
  coldHead=FindBone(person,"Head");coldArmLeft=FindBone(person,"Arm.L");coldArmRight=FindBone(person,"Arm.R");
  if(mode=="cold-food"||mode=="cold-clothing")personStart=new Vector3(-2.3f,.11f,-.5f);
  coldGroup=Group("Cold movement cues");
  for(int i=0;i<wind.Length;i++){
   float z=.4f+i*.42f,y=.7f+(i%3)*.48f;
   wind[i]=Line("Cold wind "+i,new[]{new Vector3(-.2f,y,z),new Vector3(.25f,y+.12f,z),new Vector3(.75f,y+.08f,z),new Vector3(1.2f,y,z)},Cold,.045f);Parent(wind[i],coldGroup);windStart[i]=new Vector3(.2f+i*.92f,0,0);
  }
  BuildMeters();
  status=Label("추운 곳에 들어감",960,850,46,White,1540,72);
  guide=Line("Information to consequence",new[]{new Vector3(-1.3f,2.6f,.1f),new Vector3(-.1f,3.4f,.1f),new Vector3(2,3.4f,.1f)},Yellow,.08f);guide.SetActive(false);
  if(mode=="cold-food"||mode=="cold-overview"){
   pot=Asset("cookingPot",new Vector3(-4.4f,.1f,-.7f),.9f,0);
   meal=Asset("meal",new Vector3(-3.3f,.15f,-.7f),.36f,0);
   bowlRest=new Vector3(-3.2f,.95f,-.5f);bowl=Asset("bowl",bowlRest,.33f,0);
   upperArm=FindBone(person,"Arm.R");foreArm=FindBone(person,"ForeArm.R");hand=FindBone(person,"Hand.R");
   Label("추위를 견디는 음식",530,270,44,Warm,850,70);
  }
  if(mode=="cold-clothing"){
   coat=CoatSymbol(new Vector3(-4.5f,1.4f,-.3f),1.25f);
   scarf=MakeScarf(person);scarf.SetActive(false);
   Label("추위를 견디는 옷",550,270,44,Warm,900,70);
  }
  if(mode=="cold-intent"){
   other=Actor("Experienced explorer",new Vector3(-4.6f,.11f,1.05f),true,2.7f,0);
   PairLabels("처음: 왜 체력이 줄지?","익숙함: 준비하고 탐험");
   temperatureUi.SetActive(false);healthUi.SetActive(false);
  }
  if(mode=="cold-goal")Label("먼 목표보다 · 눈앞의 원인 하나",960,245,44,White,1500,70);
  if(mode=="cold-information")Label("추위 → 체력 변화",960,245,46,White,1450,70);
  if(mode=="cold-compare"){
   PairLabels("필요한 정보","다음 선택까지 지정");
   decisionLeft=Asset("meal",new Vector3(-4.3f,.15f,-1.8f),.38f,0);
   decisionRight=CoatSymbol(new Vector3(-3.0f,.95f,-1.8f),.85f);
   marker=Line("Only one prescribed choice",new[]{new Vector3(-1,2.8f,-1.4f),new Vector3(-3.1f,1.3f,-1.7f),new Vector3(-2.8f,1.35f,-1.7f)},Red,.1f);
  }
 }
 void BuildMeters(){
  RectUI(1490,500,500,450,Hex("151A1D"));
  temperatureUi=new GameObject("Temperature explanation UI",typeof(RectTransform));temperatureUi.transform.SetParent(canvas.transform,false);temperatureUi.layer=29;
  UiParent(RectUI(1490,350,360,42,Dark),temperatureUi);temperatureRegion=RectUI(1390,350,160,42,Cold);UiParent(temperatureRegion,temperatureUi);
  temperaturePointer=RectUI(1580,350,12,69,White);UiParent(temperaturePointer,temperatureUi);
  temperatureLabel=Label("추운 영역",1490,295,42,White,550,65);UiParent(temperatureLabel,temperatureUi);
  healthUi=new GameObject("Health consequence UI",typeof(RectTransform));healthUi.transform.SetParent(canvas.transform,false);healthUi.layer=29;
  UiParent(RectUI(1490,475,360,42,Dark),healthUi);healthFill=RectUI(1490,475,360,42,Red);UiParent(healthFill,healthUi);
  healthLabel=Label("체력",1490,420,42,White,550,65);UiParent(healthLabel,healthUi);
  heartText=Label("♥",1265,475,58,Red,80,80);UiParent(heartText,healthUi);
  protectionUi=new GameObject("Chosen protection UI",typeof(RectTransform));protectionUi.transform.SetParent(canvas.transform,false);protectionUi.layer=29;
  protectionRegion=RectUI(1490,600,360,72,Dark);UiParent(protectionRegion,protectionUi);
  protectionLabel=Label("추위 가드",1490,600,42,Teal,450,65);UiParent(protectionLabel,protectionUi);
  durationLabel=Label("",1490,675,42,White,450,70);UiParent(durationLabel,protectionUi);
  protectionUi.SetActive(false);
 }
 void Meter(float cold,float loss,bool protectedNow){
  var p=temperaturePointer.rectTransform.anchoredPosition;p.x=Mathf.Lerp(1580,1390,cold)-960;temperaturePointer.rectTransform.anchoredPosition=p;
  // A schematic, nonnumeric indicator. No invented temperature/damage rate.
  healthFill.rectTransform.sizeDelta=new Vector2(Mathf.Lerp(360,220,loss),42);
  var h=healthFill.rectTransform.anchoredPosition;h.x=(1490-180+healthFill.rectTransform.sizeDelta.x*.5f)-960;healthFill.rectTransform.anchoredPosition=h;
  healthFill.color=protectedNow?Teal:Red;
  heartText.color=protectedNow?Teal:Red;
  healthLabel.text=protectedNow?"추가 감소 없음":loss>.05f?"체력이 줄어듦":"체력";
 }
 Transform FindBone(GameObject o,string name){var t=o.GetComponentsInChildren<Transform>(true).FirstOrDefault(x=>x.name==name);if(!t)throw new Exception("Actual imported rig bone not found: "+name);return t;}

 // A recognizable, independently authored garment symbol and a wearable scarf
 // supplement the imported detailed rig. They are not a BOTW item model.
 GameObject CoatSymbol(Vector3 pos,float scale){
  var o=Group("Warm clothing illustration");o.transform.position=pos;
  var points=new[]{new Vector2(-.22f,.62f),new Vector2(-.48f,.52f),new Vector2(-.85f,.08f),new Vector2(-.62f,-.08f),new Vector2(-.43f,.15f),new Vector2(-.40f,-.65f),new Vector2(.40f,-.65f),new Vector2(.43f,.15f),new Vector2(.62f,-.08f),new Vector2(.85f,.08f),new Vector2(.48f,.52f),new Vector2(.22f,.62f),new Vector2(.16f,.38f),new Vector2(-.16f,.38f)};
  MeshPlate(o,points,.12f,Warm,"Garment outline");
  var seam=Line("Coat seam",new[]{new Vector3(0,.34f,-.08f),new Vector3(0,-.62f,-.08f)},Hex("674C36"),.035f);seam.transform.SetParent(o.transform,false);
  var collar=Line("Coat collar",new[]{new Vector3(-.24f,.61f,-.08f),new Vector3(-.16f,.36f,-.08f),new Vector3(.16f,.36f,-.08f),new Vector3(.24f,.61f,-.08f)},White,.055f);collar.transform.SetParent(o.transform,false);
  o.transform.localScale=Vector3.one*scale;return o;
 }
 void MeshPlate(GameObject parent,Vector2[] points,float depth,Color color,string name){
  // Triangles around a deliberately interior origin support this shirt silhouette.
  var v=new List<Vector3>();var tr=new List<int>();v.Add(new Vector3(0,0,-depth));
  foreach(var p in points)v.Add(new Vector3(p.x,p.y,-depth));
  v.Add(new Vector3(0,0,depth));foreach(var p in points)v.Add(new Vector3(p.x,p.y,depth));
  int n=points.Length;for(int i=0;i<n;i++){int a=1+i,b=1+(i+1)%n;tr.AddRange(new[]{0,b,a,n+1,a+n+1,b+n+1,a,b,b+n+1,a,b+n+1,a+n+1});}
  var mesh=new Mesh{name=name};mesh.SetVertices(v);mesh.SetTriangles(tr,0);mesh.RecalculateNormals();mesh.RecalculateBounds();
  #if UNITY_EDITOR
  var folder=Root+"/Generated/Meshes/"+cutId;Directory.CreateDirectory(folder);var path=folder+"/"+name.Replace(' ','-')+".asset";
  var prior=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(prior){DestroyImmediate(mesh);mesh=prior;}else AssetDatabase.CreateAsset(mesh,path);
  #endif
  var o=new GameObject(name,typeof(MeshFilter),typeof(MeshRenderer));o.transform.SetParent(parent.transform,false);o.GetComponent<MeshFilter>().sharedMesh=mesh;o.GetComponent<MeshRenderer>().sharedMaterial=Mat(color);Layer(o);
 }
 GameObject MakeScarf(GameObject actor){
  var o=Group("Equipped warm scarf - illustrative clothing");o.transform.SetParent(actor.transform,false);
  // The imported Head bone is about y=1.95 while shoulders are y=1.80.
  // Keep fabric below the face and drape the tail down the back/near shoulder.
  var loop=new Vector3[25];for(int i=0;i<loop.Length;i++){float a=i*2*Mathf.PI/(loop.Length-1);loop[i]=new Vector3(-.08f+Mathf.Cos(a)*.23f,1.75f,Mathf.Sin(a)*.28f);}
  var neck=Line("Scarf below neck",loop,Warm,.17f);neck.transform.SetParent(o.transform,false);
  var tail=Line("Scarf over back shoulder",new[]{new Vector3(-.29f,1.74f,-.27f),new Vector3(-.36f,1.45f,-.29f),new Vector3(-.32f,1.18f,-.28f)},Warm,.19f);tail.transform.SetParent(o.transform,false);
  pendingScarfAttachments.Add((o,actor));return o;
 }

 void BuildPlacement(){
  table=Asset("table",Vector3.zero,1.8f,0);Asset("chair",new Vector3(3.9f,0,.5f),2.2f,-90);person=Actor("First-time organizer",new Vector3(-4.2f,0,.5f),false,2.8f,0);
  cupStart=new Vector3(-.65f,1.83f,-.2f);cupEnd=new Vector3(.65f,1.83f,-.2f);cup=Asset("cup",cupStart,.8f,0);
  marker=Line("Two available places",new[]{new Vector3(-1.4f,1.9f,-.5f),new Vector3(-1.4f,1.9f,.6f),new Vector3(1.6f,1.9f,.6f),new Vector3(1.6f,1.9f,-.5f)},Teal,.08f);
  guide=Line("Unnecessary instruction",new[]{new Vector3(-.9f,3.3f,-.5f),new Vector3(.65f,2.2f,-.2f)},Red,.09f);PairLabels("조작은 가볍게","놓을 자리는 직접");
  input=RectUI(415,790,250,95,Teal);Label("집기 / 놓기",415,790,42,Hex("151A1D"),245,65);status=Label("컵을 고르고 → 놓고 → 다시 옮기기",1170,790,44,White,1120,100);
 }
 void BuildChoice(){
  person=Actor("Explorer",new Vector3(0,0,-1.8f),false,2.8f,0);Asset("tree",new Vector3(-4,0,1.3f),2.5f,0);Asset("tree",new Vector3(4.1f,0,1.3f),2.3f,50);
  Track("First branch",new[]{new Vector3(0,.12f,-2),new Vector3(0,.12f,0),new Vector3(-4,.12f,1)},Teal,.16f);Track("Second branch",new[]{new Vector3(0,.12f,0),new Vector3(4,.12f,1)},Yellow,.16f);
  guide=Line("Prescriptive direction",new[]{new Vector3(0,3.6f,0),new Vector3(4,1,1),new Vector3(3,1,1.1f)},Red,.14f);marker=Sphere("Self-chosen destination",new Vector3(-3.5f,.35f,1),.55f,Teal);
  PairLabels("내가 가 보고 싶은 곳","정해 준 길만 따라가기");status=Label("조작 안내 뒤에는 선택을 돌려주기",960,820,46,White,1540,90);
 }
 void BuildSummary(){
  person=Actor("Prepared first-time explorer",new Vector3(-5,0,0),false,2.5f,0);scarf=MakeScarf(person);
  table=Asset("table",Vector3.zero,1.5f,0);cup=Asset("cup",new Vector3(-.7f,1.53f,0),.65f,0);
  other=Actor("Independent explorer",new Vector3(3,0,0),true,2.5f,0);Track("Self-chosen trail",new[]{new Vector3(2,.1f,-1.5f),new Vector3(3,.1f,0),new Vector3(5,.1f,1)},Teal,.1f);
  Label("목표 맞추기",440,760,44,Yellow,520,70);Label("첫 행동 돕기",960,760,44,White,520,70);Label("다음 선택 돌려주기",1510,760,44,Teal,650,70);status=Label("다음 시도를 스스로 고르게",960,270,48,White,1500,70);
 }

 public override void Apply(float t){
  now=t;currentStep=Step(t);poseForEating=false;poseForPickup=false;shivering=false;float p0=Phase(t,0),p1=Phase(t,1),p2=Phase(t,2);int step=currentStep;
  if(mode=="cold-intent"||mode=="cold-goal"){ApplyFirstExperience(t,step,p0,p1,p2);return;}
  if(mode.StartsWith("cold-")){ApplyCold(t,step,p0,p1,p2);return;}
  if(mode=="placement"){
   var mid=new Vector3(-.9f,2.9f,-.2f);var target=step==0?Vector3.Lerp(cupStart,mid,p0):step==1?Vector3.Lerp(mid,cupEnd,p1):Vector3.Lerp(cupEnd,new Vector3(-.6f,1.83f,.2f),p2)+Vector3.up*(Mathf.Sin(p2*Mathf.PI)*.65f);Place(cup,target);
   bool click=(t>=.15f&&t<.4f)||(t>=spec.phaseSeconds[1]-.22f&&t<spec.phaseSeconds[1])||(t>=spec.phaseSeconds[1]+.2f&&t<spec.phaseSeconds[1]+.45f);input.color=click?Teal:Grey;Pose(person,"Idle_A",t);
   bool prescribed=spec.variant=="overhelp"||cutId=="06-06";guide.SetActive(prescribed&&step>=1);status.text=prescribed?(step>=1?"모든 자리를 정해 주면":"놓을 곳은 내가 고르기"):step==0?"하나를 집기":step==1?"내가 고른 자리에 놓기":"다시 옮겨도 괜찮음";
  }else if(mode=="choice"){
   bool dictated=spec.variant=="overhelp"||cutId=="07-02";guide.SetActive(dictated||step==0);marker.SetActive(!dictated&&step>0);
   float walk=dictated?Mathf.Clamp01(t/spec.phaseSeconds[2]):step==0?0:step==1?.45f*p1:.45f+.55f*p2;
   Place(person,Vector3.Lerp(new Vector3(0,0,-1.8f),new Vector3(dictated?3:-3,0,.9f),walk));person.transform.rotation=Quaternion.Euler(0,dictated?0:step==0?0:180,0);Pose(person,(dictated||step>0)?"Walk_A":"Idle_A",t);
   right.color=(dictated||step==0)?Red:Grey;left.color=(!dictated&&step>0)?Teal:Grey;status.text=dictated?"다음 선택까지 전부 정해 주면":"조작 안내 뒤에는 선택을 돌려주기";
  }else if(mode=="summary"){
   Place(person,new Vector3(-5+1.3f*p0,0,0));Pose(person,step==0?"Walk_A":"Idle_A",t);Place(cup,new Vector3(-.7f+1.4f*p1,1.53f+Mathf.Sin(p1*Mathf.PI)*.5f,0));Place(other,Vector3.Lerp(new Vector3(3,0,0),new Vector3(5,0,1),p2));other.transform.rotation=Quaternion.Euler(0,-26.565f,0);Pose(other,step==2?"Walk_A":"Idle_A",t);
  }
 }
 void ApplyCold(float t,int step,float p0,float p1,float p2){
  for(int i=0;i<wind.Length;i++){float u=Mathf.Repeat(t*.4f+i*.17f,1);wind[i].transform.localPosition=windStart[i]+new Vector3(-u*1.5f,Mathf.Sin(t+i)*.05f,0);}
  temperatureUi.SetActive(mode!="cold-intent");healthUi.SetActive(mode!="cold-intent");protectionUi.SetActive(false);guide.SetActive(false);
  bool help=mode=="cold-food"||mode=="cold-clothing"||mode=="cold-overview";
  var pos=Vector3.Lerp(personStart,new Vector3(-.65f,.11f,-.5f),p0);if(help&&step>0)pos=Vector3.Lerp(new Vector3(-.65f,.11f,-.5f),new Vector3(1.5f,.11f,-.5f),p2);
  Place(person,pos);person.transform.rotation=Quaternion.identity;Pose(person,(step==0||help&&step==2)?"Walk_A":"Idle_A",t);
  bool protectedNow=help&&step==2;shivering=!protectedNow&&pos.x>-1.6f;
  Meter(step==0?p0:1,step==0?p0:1,protectedNow);status.text=step==0?"추운 곳에 들어감":"무엇 때문에 체력이 줄었을까?";
  if(mode=="cold-intent"){
   Place(other,Vector3.Lerp(new Vector3(-4.6f,.11f,1.05f),new Vector3(4.8f,.11f,1.05f),Mathf.Clamp01(t/spec.phaseSeconds[2])));Pose(other,"Walk_A",t);status.text=step==0?"같은 게임 · 다른 출발점":step==1?"처음에는 현상부터 이해":"익숙한 목표를 그대로 요구하지 않기";
  }else if(mode=="cold-goal"){
   temperatureUi.SetActive(step>=1);healthUi.SetActive(step>=1);guide.SetActive(step==1);status.text=step==0?"먼 목적지만 말하면":step==1?"눈앞의 추위와 체력부터":"이유를 알면 다음 행동을 고를 수 있음";
  }else if(mode=="cold-information"){
   bool signalsFirst=spec.variant=="signals-then-loss";
   temperatureUi.SetActive(signalsFirst||step>=1);healthUi.SetActive(signalsFirst?step>=1:step>=2);Meter(step==0?p0:1,step>=2?p2:0,false);guide.SetActive(step==2);status.text=step==0?(signalsFirst?"온도 표시에서 추위를 확인":"추운 영역으로 들어감"):step==1?(signalsFirst?"하트는 남아 있는 체력":"온도 표시에서 추위를 확인"):"추위와 체력 감소를 연결";
  }else if(mode=="cold-food"||mode=="cold-overview"){
   protectionUi.SetActive(step==2);protectionLabel.text="추위 가드 · 음식";durationLabel.text="남은 시간 있음";healthLabel.text=step==2?"추가 감소 없음":"체력이 줄어듦";
   if(mode=="cold-overview"){healthUi.SetActive(false);shivering=false;}
   meal.SetActive(step==0);bowl.SetActive(step<=1);Place(bowl,bowlRest);poseForEating=step==1;
   status.text=step==0?"보호 효과가 있는 음식을 고름":step==1?"먹기 → 추위 가드":"효과를 확인하고 스스로 이동";
  }else if(mode=="cold-clothing"){
   coat.SetActive(step==0);scarf.SetActive(step>=1);protectionUi.SetActive(step==2);protectionLabel.text="추위 가드 · 옷";durationLabel.text="입고 있는 동안";status.text=step==0?"추위를 견딜 옷을 고름":step==1?"옷을 착용":"추위 가드를 확인하고 탐험";
  }else if(mode=="cold-compare"){
   bool dictated=spec.variant=="overhelp";marker.SetActive(dictated||step==1);left.color=dictated?Grey:Teal;right.color=dictated?Red:Grey;
   decisionLeft.SetActive(!dictated||step==0);decisionRight.SetActive(true);status.text=dictated?"정답과 다음 행동까지 지정":"원인을 알려 주고 · 대안은 직접 고르기";
   if(!dictated&&step==2){protectionUi.SetActive(true);protectionLabel.text="내가 고른 준비";durationLabel.text="다음 길도 직접";Meter(1,1,true);Place(person,Vector3.Lerp(new Vector3(-.65f,.11f,-.5f),new Vector3(1.5f,.11f,-.5f),p2));Pose(person,"Walk_A",t);}
  }
 }
 public override void FlushPoses(){
  base.FlushPoses();
  foreach(var attach in pendingScarfAttachments)attach.scarf.transform.SetParent(FindBone(attach.actor,"Torso"),true);
  pendingScarfAttachments.Clear();
  if(poseForPickup&&upperArm&&foreArm&&hand&&firstItem){
   float p=Phase(now,1),reach=Mathf.SmoothStep(0,1,Mathf.InverseLerp(0,.35f,p)),pickupLift=Mathf.SmoothStep(0,1,Mathf.InverseLerp(.35f,1,p));
   pickupTorso.rotation=Quaternion.AngleAxis(-35*reach*(1-pickupLift),Vector3.forward)*pickupTorso.rotation;
   Vector3 target=Vector3.Lerp(firstItemStart+Vector3.up*.1f,person.transform.position+new Vector3(.55f,1.55f,-.2f),pickupLift);
   target=Vector3.Lerp(hand.position,target,reach);
   var origin=upperArm.position;float a=Vector3.Distance(origin,foreArm.position),b=Vector3.Distance(foreArm.position,hand.position),d=Mathf.Clamp(Vector3.Distance(origin,target),Mathf.Abs(a-b)+.001f,a+b-.001f);
   var direction=(target-origin).normalized;var bend=(Vector3.back-Vector3.Dot(Vector3.back,direction)*direction).normalized;float cosine=Mathf.Clamp((a*a+d*d-b*b)/(2*a*d),-1,1);
   var pickupElbow=origin+direction*(cosine*a)+bend*(Mathf.Sqrt(1-cosine*cosine)*a);
   upperArm.rotation=Quaternion.FromToRotation(foreArm.position-origin,pickupElbow-origin)*upperArm.rotation;
   foreArm.rotation=Quaternion.FromToRotation(hand.position-foreArm.position,origin+direction*d-foreArm.position)*foreArm.rotation;
   Place(firstItem,p<.35f?firstItemStart:hand.position+new Vector3(.04f,-.03f,0));
  }
  if(shivering&&coldHead){float shake=Mathf.Sin(now*27f);coldHead.localRotation*=Quaternion.Euler(0,0,shake*2);coldArmLeft.localRotation*=Quaternion.Euler(shake*3,0,8);coldArmRight.localRotation*=Quaternion.Euler(-shake*3,0,-8);}
  if(!poseForEating||!upperArm||!foreArm||!hand||!bowl)return;
  // Pose once first, then add a bounded eating gesture to the imported rig.
  float lift=Mathf.Sin(Mathf.Clamp01(Phase(now,1))*Mathf.PI);
  var elbow=person.transform.position+new Vector3(.5f,1.45f,-.25f);var mouth=person.transform.position+new Vector3(.27f,2.15f,-.12f);
  upperArm.rotation=Quaternion.Slerp(upperArm.rotation,Quaternion.FromToRotation(foreArm.position-upperArm.position,elbow-upperArm.position)*upperArm.rotation,lift);
  foreArm.rotation=Quaternion.Slerp(foreArm.rotation,Quaternion.FromToRotation(hand.position-foreArm.position,mouth-foreArm.position)*foreArm.rotation,lift);
  Place(bowl,Vector3.Lerp(bowlRest,hand.position+new Vector3(.08f,.06f,0),lift));
 }
}
// One continuous heart has no numeric value. Its changing fill describes loss,
// not BOTW's heart count, damage tick, or a measured health percentage.
public class D29BotwHeartGraphic : MaskableGraphic {
 public float level=1;
 protected override void OnPopulateMesh(VertexHelper vh){
  vh.Clear();var rect=rectTransform.rect;int n=80;var points=new Vector2[n];
  for(int i=0;i<n;i++){float t=i*2*Mathf.PI/n;float x=16*Mathf.Pow(Mathf.Sin(t),3);float y=13*Mathf.Cos(t)-5*Mathf.Cos(2*t)-2*Mathf.Cos(3*t)-Mathf.Cos(4*t);points[i]=new Vector2(x/34*rect.width,(y+2)/34*rect.height);}
  vh.AddVert(Vector3.zero,color,Vector2.zero);
  for(int i=0;i<n;i++){var c=points[i].y<Mathf.Lerp(-rect.height*.5f,rect.height*.5f,level)?color:new Color(.23f,.27f,.3f,1);vh.AddVert(points[i],c,Vector2.zero);}
  for(int i=0;i<n;i++)vh.AddTriangle(0,1+i,1+(i+1)%n);
 }
}
}
