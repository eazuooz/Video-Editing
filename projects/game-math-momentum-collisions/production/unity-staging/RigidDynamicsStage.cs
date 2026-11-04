using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Object=UnityEngine.Object;

namespace Yamyam.RigidTeaching {
 public enum DynamicsPicture {ImpulseHistory,MassCenter,LinearCollision,InclinedContact,Torque,InertiaComparison,OffCenterCollision,IntegratorComparison,DeltaRectangle,TruckComposite}
 [Serializable] public class DynamicsShot {
  public string beatId="UNBOUND",englishTerm="Impulse",koreanTerm="충격량",meaning="힘을 시간에 대해 더한 운동량 변화";
  public DynamicsPicture picture;
  public double duration=4,massA=2,massB=1,initialVelocity=1,force=10,forceDuration=.3,restitution=.9,normalX=1,normalY=3;
  public double leverArm=2,pointMassRadius=1,torqueForce=3,stepSize=.1;
  public double rectangleWidth=.4,rectangleArea=1;
  public bool showWholeSystem=false,expandedTerm=true;
  public int spokenStep; // Supplied by the speech cue controller, not wall-clock time.
 }
 // Deterministic numerical teaching scenes. Commercial gameplay is composited separately.
 // No Update/FixedUpdate or automatic looping: the renderer supplies the reviewed cue progress.
 public sealed class RigidDynamicsStage:MonoBehaviour {
  public DynamicsShot shot=new DynamicsShot();public GameObject cratePrefab;public Font koreanFont;public Camera stageCamera;
  bool built;Canvas canvas;Text term,kind,formula,values,note;Material guides,surface;GameObject crate,truckModel;
  readonly List<GameObject> truckParts=new List<GameObject>();
  readonly List<LineRenderer> lines=new List<LineRenderer>();readonly List<GameObject> balls=new List<GameObject>();readonly List<Text> labels=new List<Text>();readonly List<Object> owned=new List<Object>();int lineIndex,ballIndex,labelIndex;
  static readonly Color White=new Color(.96f,.96f,.96f),Yellow=new Color(.91f,.812f,.514f),Teal=new Color(.451f,.78f,.761f),Red=new Color(.937f,.522f,.522f),Blue=new Color(.55f,.72f,.95f),Muted=new Color(.68f,.70f,.71f);
  static string N(double x,string f="0.###")=>x.ToString(f,System.Globalization.CultureInfo.InvariantCulture);
  static string V(D3 v)=>"("+N(v.x)+", "+N(v.y)+", "+N(v.z)+")";
  static Vector3 P(D3 p)=>new Vector3((float)p.x,(float)p.y,(float)-p.z);
  GameObject GO(string n){var g=new GameObject(n);g.transform.SetParent(transform,false);owned.Add(g);return g;}
  T Own<T>(T o) where T:Object{owned.Add(o);return o;}
  public void Build(){
   if(built)return;if(koreanFont==null)throw new InvalidOperationException("Local OS Korean font required");
   var unlit=Shader.Find("Universal Render Pipeline/Unlit");if(!unlit)throw new InvalidOperationException("URP Unlit required");guides=Own(new Material(unlit));guides.SetColor("_BaseColor",Color.white);surface=Own(new Material(Shader.Find("Universal Render Pipeline/Lit")));surface.SetColor("_BaseColor",new Color(.6f,.63f,.65f));
   if(!stageCamera){stageCamera=GO("Dynamics_Camera").AddComponent<Camera>();stageCamera.transform.position=new Vector3(0,0,-20);stageCamera.transform.rotation=Quaternion.identity;stageCamera.orthographic=true;stageCamera.orthographicSize=5.4f;stageCamera.nearClipPlane=.1f;stageCamera.farClipPlane=70;stageCamera.clearFlags=CameraClearFlags.SolidColor;stageCamera.backgroundColor=Color.black;}
   var light=GO("Dynamics_Key").AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.6f;light.transform.rotation=Quaternion.Euler(35,-30,0);
   var fill=GO("Dynamics_Fill").AddComponent<Light>();fill.type=LightType.Directional;fill.intensity=.4f;fill.transform.rotation=Quaternion.Euler(10,120,0);
   var ui=GO("Dynamics_SpeechLabels");canvas=ui.AddComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=stageCamera;canvas.planeDistance=1;var scaler=ui.AddComponent<CanvasScaler>();scaler.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scaler.referenceResolution=new Vector2(1920,1080);
   term=TextAt("CanonicalTerm",new Rect(80,40,1180,166),44,Yellow);kind=TextAt("SourceKind",new Rect(1330,45,510,110),38,Muted);
   formula=TextAt("WorkedCalculation",new Rect(1110,270,730,420),44,White);values=TextAt("ActualModelValues",new Rect(80,750,1760,74),46,Teal);note=TextAt("MeaningAndLimits",new Rect(80,834,1760,65),40,White);
   built=true;
  }
  Text TextAt(string n,Rect r,int size,Color color){var g=GO(n);g.transform.SetParent(canvas.transform,false);var rt=g.AddComponent<RectTransform>();rt.anchorMin=rt.anchorMax=rt.pivot=new Vector2(0,1);rt.anchoredPosition=new Vector2(r.x,-r.y);rt.sizeDelta=new Vector2(r.width,r.height);var t=g.AddComponent<Text>();t.font=koreanFont;t.fontSize=size;t.color=color;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;t.supportRichText=true;return t;}
  void Path(Color color,params Vector3[] points){LineRenderer l;if(lineIndex==lines.Count){l=GO("Guide_"+lineIndex).AddComponent<LineRenderer>();l.sharedMaterial=guides;l.useWorldSpace=true;l.numCapVertices=6;l.numCornerVertices=4;lines.Add(l);}else l=lines[lineIndex];lineIndex++;l.enabled=true;l.startWidth=l.endWidth=.045f;l.positionCount=points.Length;l.SetPositions(points);var b=new MaterialPropertyBlock();b.SetColor("_BaseColor",color);l.SetPropertyBlock(b);}
  void Arrow(Vector3 a,Vector3 b,Color color){if((a-b).sqrMagnitude<1e-8)return;var d=(b-a).normalized;var side=Vector3.Cross(d,stageCamera.transform.forward).normalized;Path(color,a,b);Path(color,b-d*.18f+side*.10f,b,b-d*.18f-side*.10f);}
  void Dot(Vector3 p,float radius,Color c){GameObject g;if(ballIndex==balls.Count){g=GameObject.CreatePrimitive(PrimitiveType.Sphere);g.name="MathParticle_"+ballIndex;g.transform.SetParent(transform,false);DestroyImmediate(g.GetComponent<Collider>());g.GetComponent<Renderer>().sharedMaterial=surface;balls.Add(g);owned.Add(g);}else g=balls[ballIndex];ballIndex++;g.SetActive(true);g.transform.position=p;g.transform.localScale=Vector3.one*radius*2;var b=new MaterialPropertyBlock();b.SetColor("_BaseColor",c);g.GetComponent<Renderer>().SetPropertyBlock(b);}
  void Tag(Vector3 p,string text,Color color,int width=470){Text t;if(labelIndex==labels.Count){t=TextAt("ObjectLabel_"+labelIndex,new Rect(0,0,width,112),40,color);labels.Add(t);}else t=labels[labelIndex];labelIndex++;t.gameObject.SetActive(true);t.text=text;t.color=color;var v=stageCamera.WorldToViewportPoint(p);t.rectTransform.sizeDelta=new Vector2(width,112);t.rectTransform.anchoredPosition=new Vector2(Mathf.Clamp(v.x*1920,70,1830-width),-Mathf.Clamp((1-v.y)*1080,232,630));}
  void Crate(Vector3 p){if(crate==null){if(cratePrefab==null)throw new InvalidOperationException("Assign licensed recognizable crate; do not replace it with a generic box");crate=Instantiate(cratePrefab,transform);crate.name="LicensedCrate_Instance";Bounds b=new Bounds();bool first=true;foreach(var r in crate.GetComponentsInChildren<Renderer>()){if(first){b=r.bounds;first=false;}else b.Encapsulate(r.bounds);}if(first||b.size.magnitude<1e-5)throw new InvalidOperationException("No visible crate bounds");float k=1.25f/Mathf.Max(b.size.x,b.size.y,b.size.z);crate.transform.localScale*=k;var pivot=GO("CrateCenter");pivot.transform.position=b.center*k;crate.transform.SetParent(pivot.transform,true);crate=pivot;}crate.SetActive(true);crate.transform.position=p;}
  void Grid(float y=-1.6f){Path(Muted,new Vector3(-8,y,0),new Vector3(.6f,y,0));for(int i=-7;i<=0;i++)Path(Muted,new Vector3(i,y-.06f,0),new Vector3(i,y+.06f,0));}
  void Plot(Func<double,double> f,double maxT,double scaleY,Color c,Vector3 origin,float width=7.8f){var p=new Vector3[121];for(int i=0;i<p.Length;i++){double t=maxT*i/(p.Length-1);p[i]=origin+new Vector3(width*i/(p.Length-1),(float)(f(t)*scaleY),0);}Path(c,p);}
  public void Evaluate(double progress){
   Build();progress=Math.Max(0,Math.Min(1,progress));double t=progress*shot.duration;lineIndex=ballIndex=labelIndex=0;if(crate)crate.SetActive(false);if(truckModel)truckModel.SetActive(false);
   term.text=shot.expandedTerm?shot.englishTerm+"\n"+shot.koreanTerm+"\n"+shot.meaning:shot.koreanTerm+" · "+shot.englishTerm;kind.text="현재 화면\n우리 수학 구현 · Unity";formula.text=values.text=note.text="";
   switch(shot.picture){
    case DynamicsPicture.ImpulseHistory:ImpulseHistory(t);break;
    case DynamicsPicture.MassCenter:MassCenter(progress);break;
    case DynamicsPicture.LinearCollision:LinearCollision(t);break;
    case DynamicsPicture.InclinedContact:InclinedContact(progress);break;
    case DynamicsPicture.Torque:Torque(progress);break;
    case DynamicsPicture.InertiaComparison:InertiaComparison(t);break;
    case DynamicsPicture.OffCenterCollision:OffCenterCollision(progress);break;
    case DynamicsPicture.IntegratorComparison:IntegratorComparison(t);break;
    case DynamicsPicture.DeltaRectangle:DeltaRectangle(progress);break;
    case DynamicsPicture.TruckComposite:TruckComposite(progress);break;
    default:throw new ArgumentOutOfRangeException();
   }
   for(int i=lineIndex;i<lines.Count;i++)lines[i].enabled=false;for(int i=ballIndex;i<balls.Count;i++)balls[i].SetActive(false);for(int i=labelIndex;i<labels.Count;i++)labels[i].gameObject.SetActive(false);
  }
  void ImpulseHistory(double t){
   double during=Math.Min(t,shot.forceDuration),impulse=shot.force*during,v=shot.initialVelocity+impulse/shot.massA;
   double x=shot.initialVelocity*t+shot.force/shot.massA*(during*during/2+during*Math.Max(0,t-shot.forceDuration));
   var p=new Vector3(-7.2f+(float)x*.65f,-.9f,0);Grid();Crate(p);Arrow(p+Vector3.up*.9f,p+new Vector3((float)v*.55f,.9f,0),Teal);
   if(t<shot.forceDuration)Arrow(p+Vector3.left*1.2f,p,Red);
   Plot(s=>s<shot.forceDuration?shot.force:0,Math.Max(shot.duration,shot.forceDuration*1.5),.12,Red,new Vector3(-7.5f,1.0f,0));Tag(new Vector3(-7.4f,2.9f,0),"힘 F(t) · 빨강\n넓이 = 충격량 J",Red,640);
   formula.text="J = F × Δt\n= "+N(shot.force)+" × "+N(during)+"\n= "+N(impulse)+" N·s\n\nΔv = J / m = "+N(impulse/shot.massA)+" m/s";
   values.text="m = "+N(shot.massA)+" kg     v = "+N(v)+" m/s     p = "+N(shot.massA*v)+" kg·m/s";
   note.text="힘은 작용하는 동안, 충격량은 그동안 누적된 운동량 변화입니다.";
  }
  void MassCenter(double u){
   double xa=0,xb=shot.showWholeSystem?4-2*u:4;D3 c=Dynamics.Center(new[]{new MassPoint(shot.massA,new D3(xa,0)),new MassPoint(shot.massB,new D3(xb,0))});
   var left=new Vector3(-7,0,0);Dot(left,.38f,Blue);Dot(left+Vector3.right*(float)xb,.38f*Mathf.Pow((float)(shot.massB/shot.massA),1f/3),Red);Path(Muted,left,left+Vector3.right*(float)xb);
   var center=left+Vector3.right*(float)c.x;Dot(center+Vector3.down*.65f,.11f,Yellow);Arrow(center+Vector3.down*1.1f,center,Yellow);
   Tag(left+Vector3.up*1.2f,N(shot.massA)+" kg\nx = 0",Blue);Tag(left+new Vector3((float)xb,1.2f,0),N(shot.massB)+" kg\nx = "+N(xb),Red);Tag(center+Vector3.down*1.2f,"질량중심 x = "+N(c.x),Yellow);
   formula.text="x₍cm₎ = Σ(mᵢxᵢ) / Σmᵢ\n\n= ("+N(shot.massA)+" × 0\n + "+N(shot.massB)+" × "+N(xb)+") / "+N(shot.massA+shot.massB)+"\n\n= "+N(c.x)+" m";values.text="질량으로 가중한 평균 위치";note.text="기하학적 가운데와 질량중심은 다를 수 있습니다.";
  }
  void LinearCollision(double t){
   double contact=shot.duration*.45;Body a=new Body{inverseMass=1/shot.massA,velocity=new D3(2,0)},b=new Body{inverseMass=1/shot.massB,velocity=new D3(-1,0)};
   var result=Dynamics.Resolve(a,b,new D3(),new D3(),new D3(1,0),shot.restitution);double dt=t-contact;bool after=dt>=0;
   D3 va=after?result.a.velocity:a.velocity,vb=after?result.b.velocity:b.velocity;
   Vector3 pa=new Vector3(-5.2f+(float)(va.x*dt*.65),0,0),pb=new Vector3(-4f+(float)(vb.x*dt*.65),0,0);Dot(pa,.6f,Blue);Dot(pb,.6f,Red);Arrow(pa+Vector3.up*.9f,pa+new Vector3((float)va.x*.6f,.9f,0),Blue);Arrow(pb+Vector3.up*1.4f,pb+new Vector3((float)vb.x*.6f,1.4f,0),Red);
   Tag(new Vector3(-7,2.9f,0),after?"충돌 뒤 · 한 번 적용한 충격량":"충돌 전 · 서로 접근",Yellow,900);
   formula.text="p₍total₎ = m₁v₁ + m₂v₂\n= "+N(shot.massA*va.x+shot.massB*vb.x)+" kg·m/s\n\nv₁ = "+N(va.x)+" m/s\nv₂ = "+N(vb.x)+" m/s";
   values.text="e = "+N(shot.restitution)+"     J = "+N(result.impulseOnB.Length)+" N·s";note.text="두 물체의 운동량 변화는 크기가 같고 방향이 반대입니다.";
  }
  void InclinedContact(double u){
   D3 n=new D3(shot.normalX,shot.normalY),unit=n.Unit(),tangent=new D3(unit.y,-unit.x);var floor=new Body();var incoming=new Body{inverseMass=20,velocity=new D3(-4,-4)};
   var hit=Dynamics.Resolve(floor,incoming,new D3(),new D3(),n,shot.restitution);var contact=new Vector3(-4,-.3f,0);Path(Muted,contact+P(tangent)*4,contact-P(tangent)*4);Arrow(contact,contact+P(unit)*1.7f,Yellow);Tag(contact+P(unit)*1.8f,"n = "+V(n),Yellow);
   double phase=(u-.5)*2;var v=phase<0?incoming.velocity:hit.b.velocity;var point=contact+P(v)*(float)(phase*.32)+P(unit)*.26f;Dot(point,.26f,Blue);
   Arrow(contact-P(incoming.velocity)*.4f,contact,Red);Arrow(contact,contact+P(hit.b.velocity)*.4f,Teal);
   formula.text="n · n = "+N(n.Sqr)+"\n(v₁ − v₂) · n = "+N(hit.approach)+"\n\nk = "+N(hit.multiplier)+"\nΔv₂ = "+V(hit.impulseOnB*20)+"\nv₂′ = "+V(hit.b.velocity);
   values.text="e = "+N(shot.restitution)+"     법선 성분만 반발 · 마찰 없음";note.text="법선이 단위 길이가 아니므로 k와 충격량의 크기는 다릅니다.";
  }
  void Torque(double u){
   var pivot=new Vector3(-4.4f,0,0);float radius=(float)shot.pointMassRadius;double angle=u*.8;var radial=new Vector3(Mathf.Cos((float)angle),Mathf.Sin((float)angle),0);Path(White,pivot,pivot+radial*radius);Dot(pivot,.13f,Muted);Dot(pivot+radial*radius,.33f,Blue);
   var forcePoint=pivot+radial*(float)shot.leverArm;var forceDir=new Vector3(-radial.y,radial.x,0);Arrow(forcePoint,forcePoint+forceDir*(float)shot.torqueForce*.45f,Red);Arrow(pivot,forcePoint,Yellow);
   double tau=shot.leverArm*shot.torqueForce,inertia=shot.massA*radius*radius;
   Tag(pivot+new Vector3(-2,2.7f,0),"힘을 가하는 거리 ≠ 질량의 거리",Yellow,920);
   formula.text="τ = r₍force₎ × F\n|τ| = "+N(tau)+" N·m\n\nI = m r₍mass₎²\n= "+N(inertia)+" kg·m²\nα = τ / I = "+N(tau/inertia);
   values.text="지렛팔 "+N(shot.leverArm)+" m     질량의 반지름 "+N(radius)+" m";note.text="이 그림은 두 거리의 역할을 분리한 고정축 사고실험입니다.";
  }
  void InertiaComparison(double t){
   double[][] masses={new[]{2.0,2,2},new[]{2.0,2,2},new[]{3.0,2,1},new[]{1.0,2,3}};
   double[][] radii={new[]{3.0,2,1},new[]{3.0,3,3},new[]{3.0,2,1},new[]{3.0,2,1}};
   for(int j=0;j<4;j++){float x=j%2==0?-6.5f:-2.4f,y=j<2?1.6f:-1.2f;var c=new Vector3(x,y,0);double inertia=0;for(int k=0;k<3;k++)inertia+=masses[j][k]*radii[j][k]*radii[j][k];double turn=.5*shot.torqueForce/inertia*t*t;
    Dot(c,.06f,Muted);for(int k=0;k<3;k++){double angle=turn+k*Math.PI*2/3;var p=c+new Vector3((float)(Math.Cos(angle)*radii[j][k]*.38),(float)(Math.Sin(angle)*radii[j][k]*.38),0);Path(Muted,c,p);Dot(p,.09f+(float)masses[j][k]*.035f,Teal);}Tag(c+new Vector3(-1.1f,1.4f,0),"I = "+N(inertia),Yellow,380);
   }
   formula.text="I = Σ mᵢrᵢ²\n\n같은 총질량: 6 kg\n같은 토크: "+N(shot.torqueForce)+" N·m\n\nα = τ / I";values.text="28 · 54 · 36 · 20 kg·m²";note.text="같은 질량이어도 분포에 따라 회전 가속도가 달라집니다.";
  }
  void OffCenterCollision(double u){
   if(Math.Abs(shot.leverArm)>2.2)throw new ArgumentException("Contact must lie on the 4.4 m rod");
   var inertia=Dynamics.BoxInertia(2,new D3(.3,4.4,.3));var a=new Body{inverseMass=.5,velocity=new D3(2,0),inverseInertiaWorld=inertia.Inverse()};var b=new Body();D3 ra=new D3(0,shot.leverArm),normal=new D3(1,0);
   var hit=Dynamics.Resolve(a,b,ra,new D3(),normal,shot.restitution);double dt=Math.Max(0,u-.5)*1.1;var c=new Vector3(-4.5f+(float)(hit.a.velocity.x*dt),0,0);double angle=hit.a.omega.z*dt;var d=new Vector3(-(float)Math.Sin(angle),(float)Math.Cos(angle),0);Path(White,c-d*2.2f,c+d*2.2f);Dot(c,.14f,Yellow);var at=c+d*(float)shot.leverArm;Dot(at,.12f,Red);Arrow(at,at+P(hit.impulseOnB)*-.35f,Red);Arrow(c,c+P(hit.a.velocity)*.5f,Teal);
   formula.text="v₍point₎ = v₍cm₎ + ω × r\n\nΔv = −J / m\nΔω = −I⁻¹(r × J)\n\nω′ = "+V(hit.a.omega);
   values.text="접촉점 충격량 "+N(hit.impulseOnB.Length)+" N·s     회전 포함";note.text="같은 충격량이 질량중심 이동과 회전을 함께 바꿉니다.";
  }
  void IntegratorComparison(double t){
   double h=shot.stepSize;int steps=(int)Math.Floor(t/h);KinematicState a=new KinematicState(0,0),b=a;
   for(int i=0;i<steps;i++){a=Dynamics.Integrate(a,i*h,h,(tt,x,v)=>2,Integration.ExplicitEuler);b=Dynamics.Integrate(b,i*h,h,(tt,x,v)=>2,Integration.SemiImplicitEuler);}double end=steps*h,exact=end*end;float scale=2.5f/(float)Math.Max(.1,shot.duration*shot.duration);
   var start=new Vector3(-7,1.8f,0);Dot(start+Vector3.right*(float)a.position*scale,.23f,Red);Dot(start+new Vector3((float)b.position*scale,-1.7f,0),.23f,Blue);Dot(start+new Vector3((float)exact*scale,-3.4f,0),.23f,Teal);Tag(start+Vector3.up*.7f,"명시적 오일러",Red);Tag(start+Vector3.down,"반암시적 오일러",Blue);Tag(start+Vector3.down*2.7f,"등가속도 정확해",Teal);
   formula.text="h = "+N(h)+" s,  a = 2 m/s²\n\nx₍explicit₎ = "+N(a.position)+" m\nx₍semi₎ = "+N(b.position)+" m\nx₍exact₎ = "+N(exact)+" m\n\nv = "+N(a.velocity)+" m/s";values.text="t = "+N(end)+" s     두 줄의 갱신 순서 비교";note.text="정확도뿐 아니라 힘의 성질과 안정성도 함께 비교합니다.";
  }
  void DeltaRectangle(double u){
   double width=shot.rectangleWidth;var o=new Vector3(-7.5f,-1.0f,0);double height=shot.rectangleArea/width;double maxH=Math.Max(1,shot.rectangleArea/.05);
   Plot(t=>Dynamics.ImpulseRectangle(t,2,width,shot.rectangleArea),4,2.7/maxH,Red,o);Path(Muted,o,o+Vector3.right*8);double time=4*u;Dot(o+new Vector3((float)time*1.95f,(float)(Dynamics.ImpulseRectangle(time,2,width,shot.rectangleArea)*2.7/maxH),0),.08f,Yellow);
   formula.text="폭 w = "+N(width)+" s\n높이 = "+N(height)+"\n넓이 = "+N(shot.rectangleArea)+"\n\n적분 누적값 =\n"+N(Dynamics.ImpulseRectangleIntegral(time,2,width,shot.rectangleArea));
   values.text="폭이 달라도 넓이는 같습니다.";note.text="유한한 직사각형 근사입니다. δ(0)에 무한대를 대입하는 계산이 아닙니다.";
  }
  void TruckComposite(double u){
   double[] masses={1000,600,400,50,50,50,50};D3[] centers={new D3(0,1,2.25),new D3(0,1.25,.75),new D3(0,1,-1.2),new D3(-1,.35,2.3),new D3(1,.35,2.3),new D3(-1,.35,-1.5),new D3(1,.35,-1.5)};var points=new MassPoint[7];for(int i=0;i<7;i++)points[i]=new MassPoint(masses[i],centers[i]);var com=Dynamics.Center(points);
   // The source exercise explicitly approximates a truck with three cuboids
   // and four cylinders. Build those actual dimensions, not decorative dots.
   if(!truckModel){
    truckModel=GO("Truck_ThreeCuboids_FourCylinders");truckModel.transform.position=new Vector3(-4.4f,-1,0);truckModel.transform.rotation=Quaternion.Euler(12,-25,0);
    D3[] sides={new D3(2,.8,1.5),new D3(2,1.3,1.5),new D3(2,.8,2.4)};
    for(int i=0;i<7;i++){
     var g=GameObject.CreatePrimitive(i<3?PrimitiveType.Cube:PrimitiveType.Cylinder);g.name="TruckApproximation_Part"+i;g.transform.SetParent(truckModel.transform,false);DestroyImmediate(g.GetComponent<Collider>());
     g.transform.localPosition=new Vector3((float)centers[i].z,(float)centers[i].y,(float)-centers[i].x);
     if(i<3)g.transform.localScale=new Vector3((float)sides[i].z,(float)sides[i].y,(float)sides[i].x);
     else{g.transform.localScale=new Vector3(.7f,.1f,.7f);g.transform.localRotation=Quaternion.Euler(90,0,0);}
     g.GetComponent<Renderer>().sharedMaterial=surface;var property=new MaterialPropertyBlock();property.SetColor("_BaseColor",i<3?(i==1?Teal:Blue):new Color(.16f,.18f,.2f));g.GetComponent<Renderer>().SetPropertyBlock(property);truckParts.Add(g);
    }
   }
   truckModel.SetActive(true);Func<D3,Vector3> projection=p=>truckModel.transform.TransformPoint(new Vector3((float)p.z,(float)p.y,(float)-p.x));
   for(int i=0;i<7;i++){var p=projection(centers[i]);Dot(p,.07f,i<3?White:Muted);if(shot.spokenStep>0)Path(Muted,p,projection(com));if(i<3)Tag(p+Vector3.up*(i==1?1.4f:.9f),N(masses[i])+" kg",White,260);}
   Dot(projection(com),.14f,Yellow);Arrow(projection(com)+Vector3.down*1.3f,projection(com),Yellow);
   formula.text="총질량 = 2,200 kg\n\nc = (0, 1.009, 1.045) m\n\nI₍part→cm₎\n= I₍part₎ + m(d²1 − ddᵀ)";
   values.text="상자 3개 + 원기둥 바퀴 4개 · 교재 수치의 근사 모형";note.text="센티미터를 미터로 바꾸고 모든 관성의 기준점을 일치시킵니다.";kind.text="현재 화면\n관성 계산용 근사 모형";
  }
 }
}
