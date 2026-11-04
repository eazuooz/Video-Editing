using System;
using System.Collections.Generic;
using UnityEngine;
namespace Yamyam.MathMechanics {
 public sealed partial class MechanicsTeachingStage {
  void SpringTrace(Func<double,double> value,double scale,float baseY,Color color,double until){
   Line(new[]{new Vector3(-8,baseY,-.7f),new Vector3(-.8f,baseY,-.7f)},Muted,.018f);
   var points=new List<Vector3>();int count=Math.Max(1,(int)(180*Math.Min(1,until/shot.timeEnd)));
   for(int i=0;i<=count;i++){
    double time=shot.timeEnd*i/180;float y=(float)(value(time)*scale);
    // Out-of-range values leave the plot, never become a false flat plateau.
    if(float.IsNaN(y)||float.IsInfinity(y)||Mathf.Abs(y)>.65f){if(points.Count>1)Line(points,color,.035f);points.Clear();continue;}
    points.Add(new Vector3(-8+7.2f*i/180,baseY+y,-.8f));
   }
   if(points.Count>1)Line(points,color,.035f);
  }
  ScalarState ControllerAt(double t,double dt){
   var state=new ScalarState(shot.x0,shot.v0,0);int count=(int)Math.Floor(t/dt+1e-8);
   for(int i=0;i<count;i++)state=MechanicsMathModel.SemiImplicitSpring(state,shot.target,shot.k,shot.c,dt);return state;
  }
  string ControllerCode(int active){
   string variable(string s)=>"<color=#73C7C2>"+s+"</color>";
   string[] lines={variable("error")+" = "+variable("value")+" − "+variable("target")+";",
    variable("accel")+" = −K * "+variable("error")+" − C * "+variable("velocity")+";",
    variable("velocity")+" += "+variable("accel")+" * "+variable("dt")+";",
    variable("value")+" += "+variable("velocity")+" * "+variable("dt")+";"};
   for(int i=0;i<lines.Length;i++)lines[i]=(i==active?"▶ ":"   ")+lines[i];return string.Join("\n",lines);
  }
  void ApplySpringPicture(double t){
   double w=MechanicsMathModel.NaturalFrequency(shot.mass,shot.k);var state=MechanicsMathModel.Spring(shot.mass,shot.k,shot.c,shot.x0,shot.v0,t);
   if(shot.picture==MechanicsPicture.SpringDerivatives){
    body.position=Origin+new Vector3((float)state.x*shot.worldScale,1.15f,0);SpringCoil(Origin+new Vector3(-3,1.15f,0),body.position+Vector3.left*.6f,White);
    double amp=Math.Max(.01,MechanicsMathModel.Amplitude(shot.x0,shot.v0,w));
    SpringTrace(s=>MechanicsMathModel.Spring(shot.mass,shot.k,shot.c,shot.x0,shot.v0,s).x,.55/amp,-.3f,Teal,t);
    SpringTrace(s=>MechanicsMathModel.Spring(shot.mass,shot.k,shot.c,shot.x0,shot.v0,s).v,.55/(amp*w),-1.7f,Green,t);
    SpringTrace(s=>MechanicsMathModel.Spring(shot.mass,shot.k,shot.c,shot.x0,shot.v0,s).a,.55/(amp*w*w),-3.1f,Red,t);
    Tag(new Vector3(-8.8f,.2f,0),"x(t)",Teal);Tag(new Vector3(-8.8f,-1.2f,0),"v(t)",Green);Tag(new Vector3(-8.8f,-2.6f,0),"a(t)",Red);
    numbers.text="t = "+N(t)+" s\nx = "+N(state.x)+" m\nv = "+N(state.v)+" m/s\na = "+N(state.a)+" m/s²\n그래프별 세로 눈금: A, Aω, Aω²";
   }else if(shot.picture==MechanicsPicture.SpringPhase){
    double a=MechanicsMathModel.Amplitude(shot.x0,shot.v0,w);double phase=a==0?0:MechanicsMathModel.InitialPhase(shot.x0,shot.v0,w);
    body.position=Origin+Vector3.right*(float)state.x*shot.worldScale;SpringCoil(Origin+Vector3.left*3,body.position+Vector3.left*.6f,White);
    Arrow(body.position+Vector3.down*.9f,Vector3.right*(float)state.v*.5f,Green,"현재 속도");
    Line(new[]{Origin+Vector3.down*1.5f,Origin+Vector3.up*1.5f},Muted,.025f);SpringGraph(t);
    numbers.text="x₀ = "+N(shot.x0)+" m   v₀ = "+N(shot.v0)+" m/s\nω = "+N(w)+" rad/s\nA = "+N(a)+" m\nφ₀ = "+(a==0?"정지: 의미 없음":N(phase)+" rad")+"\nv(t) = "+N(state.v)+" m/s";
   }else if(shot.picture==MechanicsPicture.ControllerCode){
    double err=shot.x0-shot.target,accel=-shot.k*err-shot.c*shot.v0,nextV=shot.v0+accel*shot.dt,nextX=shot.x0+nextV*shot.dt;
    double displayed=shot.codeStage>=3?nextX:shot.x0;body.position=Origin+Vector3.right*(float)displayed*shot.worldScale;
    var target=Origin+Vector3.right*(float)shot.target*shot.worldScale;Line(new[]{target+Vector3.up*1.5f,target-Vector3.up*1.5f},Green,.04f);Tag(target+Vector3.up,"목표",Green);
    Arrow(body.position+Vector3.down*1.2f,Vector3.right*(float)(shot.codeStage>=2?nextV:shot.v0)*.6f,Teal,"속도");
    numbers.text="오차 = "+N(err)+"\n가속도 = "+(shot.codeStage>=1?N(accel):"계산 전")+"\n새 속도 = "+(shot.codeStage>=2?N(nextV):"계산 전")+"\n새 위치 = "+(shot.codeStage>=3?N(nextX):"계산 전")+"\nΔt = "+N(shot.dt)+" s";
   }else if(shot.picture==MechanicsPicture.StabilityComparison){
    double[] dts={.05,.5};Color[] colors={Teal,Red};body.gameObject.SetActive(false);
    for(int i=0;i<2;i++){double dt=dts[i];float baseline=i==0?.9f:-1.5f;var s=ControllerAt(t,dt);SpringTrace(time=>ControllerAt(time,dt).x-shot.target,.55,baseline,colors[i],t);Tag(new Vector3(-8.8f,baseline+.7f,0),"Δt = "+N(dt)+" s",colors[i]);}
    var fine=ControllerAt(t,.05);var coarse=ControllerAt(t,.5);
    numbers.text="동일한 K, C, 초기 상태\nΔt=.05 → x="+N(fine.x)+"\nΔt=.5 → x="+N(coarse.x)+"\n|x−목표|>1.18: 그래프 밖\n값을 숨기지 않고 숫자로 표시";
   }else if(shot.picture==MechanicsPicture.ResponseComparison){
    body.gameObject.SetActive(true);other.gameObject.SetActive(true);third.gameObject.SetActive(true);
    double spring=shot.target+MechanicsMathModel.Spring(shot.mass,shot.k,shot.c,shot.x0-shot.target,shot.v0,t).x;
    double lag=MechanicsMathModel.FirstOrderLag(shot.x0,shot.target,shot.lambda,t);
    double linear=shot.x0+Math.Sign(shot.target-shot.x0)*Math.Min(Math.Abs(shot.target-shot.x0),t);
    body.position=Origin+new Vector3((float)spring*shot.worldScale,1.45f,0);other.position=Origin+Vector3.right*(float)lag*shot.worldScale;third.position=Origin+new Vector3((float)linear*shot.worldScale,-1.45f,0);
    Tag(new Vector3(-8.8f,1.8f,0),"용수철: 속도 상태 유지",Teal);Tag(new Vector3(-8.8f,.3f,0),"일차 지연",Green);Tag(new Vector3(-8.8f,-1.2f,0),"일정 속도",Yellow);
    numbers.text="목표 = "+N(shot.target)+"\n용수철 = "+N(spring)+"\n일차 지연 = "+N(lag)+"\n일정 속도 = "+N(linear)+"\n세 경우에 같은 시간 적용";
   }else throw new InvalidOperationException("Unknown spring picture");
  }
 }
}
