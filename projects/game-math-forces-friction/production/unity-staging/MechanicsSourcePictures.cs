using System;
using UnityEngine;
namespace Yamyam.MathMechanics {
 public sealed partial class MechanicsTeachingStage {
  void ApplyAdditionalPicture(double t){
   if(shot.picture==MechanicsPicture.HorizontalForce){
    Floor(0);double force=shot.forceX-shot.opposingForce,a=force/shot.mass,v=shot.initialVelocity+a*t,x=shot.initialVelocity*t+.5*a*t*t;
    body.position=Origin+Vector3.right*((float)x*shot.worldScale-2);
    var p=body.position+Vector3.back;
    Arrow(p,Vector3.right*(float)shot.forceX*shot.forceScale,Teal,"힘 F");
    Arrow(p+Vector3.down*.5f,Vector3.left*(float)shot.opposingForce*shot.forceScale,Yellow,"반대쪽 힘");
    if(shot.showVelocity)Arrow(p+Vector3.up*.8f,Vector3.right*(float)v*shot.velocityScale,Green,"속도 v");
    if(shot.showAcceleration)Arrow(p+Vector3.up*1.5f,Vector3.right*(float)a*shot.accelerationScale,Red,"가속도 a");
    numbers.text="m = "+N(shot.mass)+" kg\nΣF = "+N(force)+" N\na = "+N(a)+" m/s²\nv = "+N(v)+" m/s\nt = "+N(t)+" s";
   }else if(shot.picture==MechanicsPicture.ForcePair){
    other.gameObject.SetActive(true);double force=shot.forceX,a=-force/shot.mass,b=force/shot.secondaryMass;
    body.position=Origin+Vector3.left*1.3f+Vector3.right*(float)(.5*a*t*t)*shot.worldScale;
    other.position=Origin+Vector3.right*1.3f+Vector3.right*(float)(.5*b*t*t)*shot.worldScale;
    Arrow(body.position+Vector3.back,Vector3.left*(float)force*shot.forceScale,Teal,"A가 받는 힘");
    Arrow(other.position+Vector3.back,Vector3.right*(float)force*shot.forceScale,Red,"B가 받는 힘");
    Tag(body.position+Vector3.up,shot.bodyLabel,Teal);Tag(other.position+Vector3.up,shot.otherLabel,Red);
    double centre=(shot.mass*body.position.x+shot.secondaryMass*other.position.x)/(shot.mass+shot.secondaryMass);
    Line(new[]{new Vector3((float)centre,-2,-1),new Vector3((float)centre,2,-1)},Muted,.025f);
    numbers.text="|F_A| = |F_B| = "+N(force)+" N\nm_A = "+N(shot.mass)+" kg\nm_B = "+N(shot.secondaryMass)+" kg\na_A = "+N(a)+" m/s²\na_B = "+N(b)+" m/s²";
   }else if(shot.picture==MechanicsPicture.ReferenceFrames){
    other.gameObject.SetActive(true);double frameX=shot.frameVelocity*t,frameY=.5*shot.frameAcceleration*t*t,fall=-.5*shot.gravity*t*t;
    Vector3 shift=shot.showObserverFrame?new Vector3((float)-frameX,(float)-frameY,0)*shot.worldScale:Vector3.zero;
    body.position=Origin+new Vector3((float)frameX,(float)frameY,0)*shot.worldScale+shift;
    other.position=Origin+Vector3.right*1.5f+new Vector3(0,(float)fall,0)*shot.worldScale+shift;
    Vector3 left=body.position+new Vector3(-1,-.7f,.3f);Line(new[]{left+Vector3.up*2.6f,left,left+Vector3.right*3.2f,left+new Vector3(3.2f,2.6f,0)},Muted,.045f);
    Arrow(other.position+Vector3.back,Vector3.down*(float)(shot.gravity+(shot.showObserverFrame?shot.frameAcceleration:0))*shot.accelerationScale,Red,"선택한 기준의 가속도");
    Tag(body.position+Vector3.up,shot.bodyLabel,Teal);Tag(other.position+Vector3.up,shot.otherLabel,Yellow);
    numbers.text=(shot.showObserverFrame?"이동 기준에서 관찰":"지면 기준에서 관찰")+"\n물체 a_y = −"+N(shot.gravity)+"\n기준계 a_y = "+N(shot.frameAcceleration)+"\n상대 a_y = "+N(-shot.gravity-shot.frameAcceleration)+" m/s²";
   }else if(shot.picture==MechanicsPicture.ContactArea){
    Floor(0);float half=(float)Math.Sqrt(shot.contactArea)*.9f;var p=body.position+Vector3.down*.65f;
    Line(new[]{p+Vector3.left*half,p+Vector3.right*half},Yellow,.13f);
    Arrow(body.position+Vector3.back,Vector3.down*(float)(shot.mass*shot.gravity)*shot.forceScale,Red,"무게");
    double normal=shot.mass*shot.gravity;
    numbers.text="N = "+N(normal)+" N\nA = "+N(shot.contactArea)+" m²\n평균 압력 = "+N(normal/shot.contactArea)+" Pa\n미끄럼 한도 = "+N(shot.muStatic*normal)+" N";
   }else throw new InvalidOperationException("Unimplemented source picture: "+shot.picture);
  }
 }
}
