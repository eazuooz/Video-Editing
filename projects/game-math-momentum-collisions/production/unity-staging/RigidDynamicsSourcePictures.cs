using System;
using System.Collections.Generic;
using UnityEngine;
namespace Yamyam.RigidTeaching {
 public sealed partial class RigidDynamicsStage {
  readonly List<GameObject> sourceObjects=new List<GameObject>();
  GameObject hammer,plate;
  GameObject Part(GameObject parent,PrimitiveType shape,Vector3 p,Vector3 size,Color color){var g=GameObject.CreatePrimitive(shape);DestroyImmediate(g.GetComponent<Collider>());g.transform.SetParent(parent.transform,false);g.transform.localPosition=p;g.transform.localScale=size;var mat=Own(new Material(surface));mat.SetColor("_BaseColor",color);g.GetComponent<Renderer>().sharedMaterial=mat;return g;}
  GameObject Hammer(){if(!hammer){hammer=GO("Own_hammer_head_and_handle");sourceObjects.Add(hammer);Part(hammer,PrimitiveType.Cylinder,new Vector3(0,-.65f,0),new Vector3(.18f,.9f,.18f),new Color(.45f,.25f,.1f));Part(hammer,PrimitiveType.Cube,new Vector3(0,.4f,0),new Vector3(1.15f,.5f,.48f),new Color(.55f,.58f,.62f));}hammer.SetActive(true);return hammer;}
  GameObject Plate(){if(!plate){plate=GO("Own_uniform_irregular_lamina");sourceObjects.Add(plate);var mesh=Own(new Mesh());mesh.vertices=new[]{new Vector3(-1,-1),new Vector3(1,-1),new Vector3(1,.15f),new Vector3(.2f,.15f),new Vector3(.2f,1),new Vector3(-1,1)};mesh.triangles=new[]{0,3,1,1,3,2,0,5,3,3,5,4};mesh.RecalculateNormals();plate.AddComponent<MeshFilter>().sharedMesh=mesh;plate.AddComponent<MeshRenderer>().sharedMaterial=surface;}plate.SetActive(true);return plate;}
  void Circle(Vector3 c,float radius,Color color){var points=new Vector3[65];for(int i=0;i<points.Length;i++){float a=i*2*Mathf.PI/64;points[i]=c+new Vector3(Mathf.Cos(a),Mathf.Sin(a))*radius;}Path(color,points);}
  void Cross(Vector3 p,Color color){Path(color,p+Vector3.left*.12f,p+Vector3.right*.12f);Path(color,p+Vector3.down*.12f,p+Vector3.up*.12f);}
  void SourcePicture(double u){
   switch(shot.picture){
    case DynamicsPicture.MomentumVector:MomentumVector(u);break;
    case DynamicsPicture.VariableImpulse:VariableImpulse(u);break;
    case DynamicsPicture.EqualArea:EqualArea(u);break;
    case DynamicsPicture.EarthTransfer:EarthTransfer(u);break;
    case DynamicsPicture.HangingPlate:HangingPlate(u);break;
    case DynamicsPicture.HammerFlight:HammerFlight(u,false);break;
    case DynamicsPicture.ModelOrigin:HammerFlight(u,true);break;
    case DynamicsPicture.InternalMass:InternalMass(u);break;
    case DynamicsPicture.Barycentre:Barycentre(u);break;
    case DynamicsPicture.StickingImpact:StickingImpact(u);break;
    case DynamicsPicture.CarImpact:CarImpact(u);break;
    case DynamicsPicture.ContactDetection:ContactBasis(u,true);break;
    case DynamicsPicture.ContactBasis:ContactBasis(u,false);break;
    case DynamicsPicture.RestitutionBounce:RestitutionBounce(u);break;
    case DynamicsPicture.Penetration:Penetration(u);break;
    case DynamicsPicture.Kinematic:Kinematic(u);break;
    case DynamicsPicture.ApplyOnce:ApplyOnce(u);break;
    case DynamicsPicture.VelocityJump:VelocityJump(u);break;
    case DynamicsPicture.Summary:Summary(u);break;
    default:throw new ArgumentOutOfRangeException();
   }
  }
  void MomentumVector(double u){var p=new Vector3(-5,.1f,0);Crate(p);double v=shot.velocityA;Arrow(p+Vector3.up*1.05f,p+new Vector3((float)v*.7f,1.05f),Teal);Arrow(p+Vector3.down*.95f,p+new Vector3((float)(shot.massA*v)*.7f,-.95f),Yellow);Tag(new Vector3(-7,2.8f),"속도 v · 운동량 p",White,850);formula.text="p = m v\n\nm = "+N(shot.massA)+" kg\nv = "+N(v)+" m/s\np = "+N(shot.massA*v)+" kg·m/s";values.text="같은 속도에서 질량만 바꾸어 비교";}
  void VariableImpulse(double u){double t=2*u,J=2.5*t*t,p=shot.massA*shot.initialVelocity+J;Vector3 o=new Vector3(-7.5f,-1);Path(Muted,o,o+Vector3.right*7.5f);Plot(s=>5*s,2,.27,Red,o,7.5f);for(int i=0;i<32*u;i++){double x=(i+.5)/16.0;Path(new Color(.4f,.6f,.55f),o+new Vector3((float)x*3.75f,0),o+new Vector3((float)x*3.75f,(float)(5*x*.27)));}Tag(o+new Vector3(0,3.6f),"F(t) = 5t · 넓이가 누적",Red,850);formula.text="J(t) = ∫₀ᵗ 5s ds\n= 2.5 t²\n\np(t) = p₀ + J(t)\np₀ = "+N(shot.massA*shot.initialVelocity);values.text="t = "+N(t)+" s     J = "+N(J)+" N·s     p = "+N(p)+" kg·m/s";}
  void EqualArea(double u){double dt=shot.forceDuration,J=3,F=J/dt;var o=new Vector3(-7,-1);Path(Muted,o,o+Vector3.right*7);float width=(float)dt*10,height=(float)F*.12f;Path(Red,o,o+Vector3.up*height,o+new Vector3(width,height),o+Vector3.right*width);formula.text="같은 Δp = 3 N·s\n\n평균 F = Δp / Δt\n= "+N(F)+" N\n\nΔt = "+N(dt)+" s";Tag(o+Vector3.up*3.3f,"시간은 짧게 · 높이는 크게",Yellow,850);values.text="직사각형 넓이 FΔt는 동일";}
  void EarthTransfer(double u){Vector3 a=new Vector3(-5.6f,.7f),b=new Vector3(-3.1f,.7f);Crate(a);Dot(b,.7f,Blue);Path(Muted,new Vector3(-8,-.7f),new Vector3(.2f,-.7f));double j=3*u;Arrow(a+Vector3.up,a+new Vector3((float)j*.5f,1),Teal);Arrow(b+Vector3.down*1.2f,b+new Vector3((float)-j*.5f,-1.2f),Red);Tag(new Vector3(-7,2.9f),"상자와 지구를 하나의 계로",Yellow,850);formula.text="Δp상자 = +J\nΔp지구 = −J\n\nΔptotal = 0\n\nΔv지구 = −J / M지구";values.text="내부 충격량은 크기가 같고 방향이 반대 · 지구 크기와 속도는 개념도";}
  void HangingPlate(double u){
   // Exact centroid of a 2×2 plate with the upper-right .8×.85 rectangle removed.
   Vector3 cm=new Vector3((float)(-.68*.6/3.32),(float)(-.68*.575/3.32),0);var obj=Plate();obj.transform.position=new Vector3(-4.6f,.4f);Vector3[] pins={new Vector3(-1,1),new Vector3(1,-1),new Vector3(.2f,1)};int index=Math.Min(2,shot.spokenStep);Vector3 d=cm-pins[index];float angle=-90-Mathf.Atan2(d.y,d.x)*Mathf.Rad2Deg;obj.transform.rotation=Quaternion.Euler(0,0,angle);Vector3 c=obj.transform.TransformPoint(cm),pin=obj.transform.TransformPoint(pins[index]);
   for(int i=0;i<=index;i++){Vector3 axis=(cm-pins[i]).normalized;Path(i==index?Yellow:Teal,obj.transform.TransformPoint(cm-axis*2),obj.transform.TransformPoint(cm+axis*2));}Dot(pin,.1f,Red);Path(Yellow,pin+Vector3.up*.7f,pin-Vector3.up*3.2f);Dot(c,.12f,Yellow);Tag(new Vector3(-7,3.0f),"매다는 점 "+(index+1)+" · 줄은 수직",White,850);formula.text="균일한 중력\n\n정지하면\n질량중심이 매단 점 아래\n\n서로 다른 매달림 선의 교점";values.text="동일한 판을 다른 지점에 매달아 같은 질량중심을 확인";
  }
  Vector3 HammerCenter(double t)=>new Vector3(-7.2f+(float)t*3.5f,(float)(.2+3*t-2*t*t),0);
  Vector3 HammerTip(double t){var q=Quaternion.Euler(0,0,(float)t*260);return HammerCenter(t)+q*new Vector3(0,-1.55f);}
  void HammerFlight(double u,bool origin){double t=u*1.6;var h=Hammer();h.transform.position=HammerCenter(t);h.transform.rotation=Quaternion.Euler(0,0,(float)t*260);var center=h.transform.position;Dot(center,.1f,Yellow);var tip=HammerTip(t);Dot(tip,.08f,Teal);var cm=new Vector3[81];var ends=new Vector3[81];for(int i=0;i<=80;i++){double a=t*i/80;cm[i]=HammerCenter(a);ends[i]=HammerTip(a);}Path(Yellow,cm);Path(Teal,ends);if(origin){Arrow(tip,center,Red);Tag(tip+Vector3.down*.5f,"모델 원점",Teal);formula.text="c = 물리 질량중심\nr = 몸체 기준 오프셋\n\nmodelOrigin = c − Rr\n\n현재 자세 R로 오프셋도 회전";}else formula.text="c(t) = c₀ + v₀t + ½gt²\n\n노랑: 질량중심\n청록: 손잡이 끝\n\n병진 + 중심 주위의 회전";values.text="손에서 놓은 뒤의 자유 비행 · 공기저항 생략";}
  void InternalMass(double u){double ma=3,mb=1,relative=2-1.8*u,xa=-mb*relative/(ma+mb),xb=ma*relative/(ma+mb);var origin=new Vector3(-4.8f,.5f);Dot(origin+Vector3.right*(float)xa,.7f,Blue);Dot(origin+Vector3.right*(float)xb,.3f,Red);Cross(origin,Yellow);Path(Muted,origin+Vector3.left*3,origin+Vector3.right*3);formula.text="외력이 없을 때\n전체 질량중심은 유지\n\n3xA + 1xB = 0\n\nxA = "+N(xa)+"\nxB = "+N(xb);Tag(new Vector3(-7,2.9f),"내부 간격 변화 · 전체 중심 고정",White,900);values.text="큰 물체에 대한 작은 물체의 위치가 변해도 계 전체 중심은 그대로";}
  void Barycentre(double u){var c=new Vector3(-4.6f,.6f);float a=(float)(u*2*Math.PI),d=3,ratio=81.3f;Vector3 r=new Vector3(Mathf.Cos(a),Mathf.Sin(a));Vector3 earth=c-r*d/(ratio+1),moon=c+r*d*ratio/(ratio+1);Circle(c,d*ratio/(ratio+1),Muted);Dot(earth,.9f,Blue);Dot(moon,.25f,White);Cross(c,Yellow);Tag(new Vector3(-7,3.5f),"지구–달 공통 질량중심",Yellow,900);formula.text="c = (M지구 x지구 + M달 x달)\n    / (M지구 + M달)\n\n노랑 + : 공통 중심\n지구 중심과 구별";values.text="두 천체의 공전 개념도 · 거리와 크기 비율은 확대해 표시";}
  void StickingImpact(double u){double ma=.01,mb=2,va=350,v=ma*va/(ma+mb);var c=new Vector3(-3.9f,.2f);bool after=u>=.5;Crate(c+Vector3.right*(float)(after?(u-.5)*2:0));Vector3 bullet=after?c+new Vector3((float)(u-.5)*2-.55f,0):c+Vector3.left*(float)(.55+(1-2*u)*3.4);Dot(bullet,.11f,Yellow);Arrow(bullet+Vector3.up*.8f,bullet+new Vector3(after?.6f:1.5f,.8f),Teal);formula.text="m탄환 = 0.01 kg\n초기 p = 0.01 × 350 = 3.5\n\nv′ = 3.5 / 2.01\n= "+N(v)+" m/s";values.text=after?"충돌 직후: 두 물체가 같은 속도로 이동":"충돌 전: 탄환만 이동 · 상자는 정지";note.text="충돌의 전후를 보기 위한 시간축 확대이며 탄환 속력의 축척은 생략";}
  void CarImpact(double u){D3 va=new D3(-35,0),vb=new D3(65*Math.Cos(115*Math.PI/180),65*Math.Sin(115*Math.PI/180));D3 pa=va*1500,pb=vb*2500,total=pa+pb,v=total/4000;Vector3 c=new Vector3(-4.5f,-.2f);Arrow(c,c+P(pa)*.000018f,Blue);Arrow(c+P(pa)*.000018f,c+P(total)*.000018f,Red);Arrow(c,c+P(total)*.000018f,Yellow);Path(Muted,c+Vector3.left*3,c+Vector3.right*3);Path(Muted,c+Vector3.down*1.3f,c+Vector3.up*3.1f);Tag(c+Vector3.right*2,"동쪽 +x",White,300);Tag(c+Vector3.up*3.2f,"북쪽 +y",White,300);formula.text="pA = (−52,500, 0)\npB = 162,500(cos115°, sin115°)\n\nv′ = (pA + pB) / 4,000\n= ("+N(v.x)+", "+N(v.y)+") km/h";values.text="같은 운동량 보존을 x, y 각각 계산 · 화살표는 계산된 운동량 벡터";}
  void ContactBasis(double u,bool detection){
   var c=new Vector3(-4.7f,.1f);bool swapped=shot.spokenStep==1,separating=shot.spokenStep==3;
   if(detection&&shot.spokenStep==2){
    Vector3 origin=new Vector3(-7,.3f),target=new Vector3(-3,.3f);Crate(target);Dot(origin,.16f,Teal);Vector3 point=Vector3.Lerp(origin,target-Vector3.right*.65f,(float)u);Path(Yellow,origin,point);Dot(point,.1f,Yellow);if(u>.9){Cross(point,Red);Arrow(point,point+Vector3.left,Red);}
    Tag(new Vector3(-7,3),"설계한 광선 판정 · 물리 충돌과 구별",White,1000);formula.text="광선 시작점 + 방향 + 거리\n\n대상 표면과 교차 → 타격 사건\n접촉 위치와 반응 방향을 전달";values.text="노랑: 검사 광선 · 빨강: 교차 지점과 표면 법선";return;
   }
   float overlap=detection?.2f:0,spread=separating?(float)u*.9f:0;Vector3 left=c+Vector3.left*(.7f-overlap+spread),right=c+Vector3.right*(.7f+spread);
   Dot(left,.7f,swapped?Red:Blue);Dot(right,.7f,swapped?Blue:Red);Cross(c,Yellow);Arrow(c,c+Vector3.right*(swapped?-2.2f:2.2f),Yellow);Path(Teal,c+Vector3.down*1.4f,c+Vector3.up*1.4f);
   float sign=separating?-1:1;Arrow(left+Vector3.up*1.05f,left+new Vector3(sign*.75f,1.05f),Blue);Arrow(right+Vector3.up*1.5f,right+new Vector3(-sign*.75f,1.5f),Red);
   Tag(new Vector3(-7,3),detection?"접촉점 · 법선 · 침투 깊이":"법선 n과 접선 방향",White,900);
   formula.text=detection?"검출: 어디에서 닿았는가?\n\n반응: 어떤 움직임으로 바뀌는가?\n\n접촉점 + 법선 + 침투 깊이":"n: A에서 B 방향\nvrel = vA − vB\n\nvrel · n > 0: 접근\nvrel · n ≤ 0: 반발 생략";
   values.text=detection?"검출 결과를 물리 반응 또는 설계한 게임 사건에 연결":separating?"멀어지는 접촉에는 새 반발 충격량을 넣지 않음":swapped?"물체 이름을 바꾸면 법선과 속도 차이도 함께 반전":"마찰 없는 반발: 법선 성분만 바꾸고 접선 성분은 유지";
  }
  void RestitutionBounce(double u){
   double g=9.8,e=shot.restitution,hit=Math.Sqrt(2/g),t=u*(hit+2*e*hit);
   double vy=t<hit?-g*t:e*g*hit-g*(t-hit);
   double y=t<hit?1-.5*g*t*t:e*g*hit*(t-hit)-.5*g*(t-hit)*(t-hit);
   var origin=new Vector3(-5.2f,-1.2f);
   var ball=origin+new Vector3(0,(float)(3*Math.Max(0,y))+.22f);
   Path(Muted,origin+Vector3.left*2,origin+Vector3.right*3);
   Dot(ball,.22f,Blue);
   var tip=ball+Vector3.up*(float)(vy*.25);
   Arrow(ball,tip,Teal);
   Tag(tip+Vector3.left*.65f,"vᵧ",Teal,160);
   var initial=origin+Vector3.up*3;
   var rebound=origin+Vector3.up*(float)(3*e*e);
   Path(Yellow,initial+Vector3.right*.6f,initial+Vector3.right*2.3f);
   Path(Teal,rebound+Vector3.right*.6f,rebound+Vector3.right*2.3f);
   Tag(initial+Vector3.right*2.5f,"처음 h₀",Yellow,280);
   Tag(rebound+Vector3.right*2.5f,"반발 h₁",Teal,280);
   values.text="같은 낙하 높이 h₀ · 반발계수 e = "+N(e);
  }
  void Penetration(double u){float depth=(float)(.35*(1-u));Vector3 c=new Vector3(-4.5f,0);Dot(c+Vector3.left*(.7f-depth/2),.7f,Blue);Dot(c+Vector3.right*(.7f-depth/2),.7f,Red);Path(Yellow,c+new Vector3(-depth/2,1),c+new Vector3(depth/2,1));formula.text="속도 보정: 더 들어가지 않게\n\n위치 보정: 기존 겹침을 분리\n\n침투 깊이 = "+N(depth);values.text="위치 분리의 개념도 · 별도 처리임을 구분";}
  void Kinematic(double u){double t=1.2*u,vp=1,vin=-3,e=.6,vout=vp+e*(vp-vin);Vector3 basePoint=new Vector3(-4.7f,(float)(vp*t)-.7f);Path(Teal,basePoint+Vector3.left*2,basePoint+Vector3.right*2);double dt=t-.5;double y=dt<0?(-3-vp)*dt:(vout-vp)*dt;Dot(basePoint+new Vector3(0,(float)y+.25f),.25f,Blue);Arrow(basePoint+Vector3.right*2.4f,basePoint+new Vector3(2.4f,1),Teal);formula.text="발판 invMass = 0\n발판 v = +1 m/s\n\n공의 상대 입사속도 = −4\n공 v′ = 1 + 0.6 × 4\n= 3.4 m/s";values.text="역질량 0: 충격량에 반응하지 않음 · 속도 0이라는 뜻은 아님";}
  void ApplyOnce(double u){
   double t=(shot.spokenStep+u)/3.0,press=Math.Min(t,.5);
   int count=0;double repeatedPosition=0;
   for(int tick=0;tick<5;tick++){
    double since=t-tick*.2;
    if(since<=0)break;
    count++;repeatedPosition+=3*since;
   }
   double[] speeds={t>0?3:0,6*press,3*count};
   double[] positions={3*t,3*press*press+6*press*(t-press),repeatedPosition};
   Color[] colors={Teal,Blue,Red};
   string[] labels={"충격량 J 한 번","힘 F · 0.5초","매 틱 J 반복"};
   for(int i=0;i<3;i++){
    var start=new Vector3(-7.2f,1.6f-1.5f*i);
    var at=start+Vector3.right*(float)positions[i]*.52f;
    Path(Muted*.6f,start,start+Vector3.right*6.7f);
    Dot(at,.14f,colors[i]);
    Arrow(at,at+Vector3.right*(float)speeds[i]*.16f,colors[i]);
    Tag(start+Vector3.up*.63f,labels[i],colors[i],560);
   }
   values.text="같은 질량 · 같은 출발점     시간 t = "+N(t)+" s";
  }
  void VelocityJump(double u){var o=new Vector3(-7.4f,0);Path(Muted,o+Vector3.down*2.2f,o+Vector3.up*2.2f);Path(Muted,o,o+Vector3.right*7.5f);Path(Teal,o+Vector3.down*1.6f,o+new Vector3(3.7f,-1.6f),o+new Vector3(3.7f,1.6f),o+new Vector3(7.4f,1.6f));Arrow(o+Vector3.right*3.7f,o+new Vector3(3.7f,2.4f),Yellow);formula.text="v(2−) = −130 ft/s\nv(2+) = +130 ft/s\nΔv = 260 ft/s\n\na(t) = 260 δ(t−2)\n힘은 F = ma";values.text="t=2 주변에서 가속도를 적분하면 속도 변화 260 ft/s";}
  void Summary(double u){string[] labels={"힘을 시간에 대해 모음","충격량 → 운동량 변화","보존 + 접촉 조건 → 새 속도"};for(int i=0;i<3;i++){var p=new Vector3(-7,2.4f-i*1.4f);Tag(p,labels[i],i==shot.spokenStep?Yellow:White,950);if(i<2)Arrow(p+new Vector3(.3f,-.5f),p+new Vector3(.3f,-1.05f),Teal);}formula.text="J = ∫F dt\np′ = p + J\n\n다음: 질량중심을 비껴 미는 힘\n병진 + 회전";values.text="같은 사건의 전과 후를 연결하는 세 단계";}
 }
}
