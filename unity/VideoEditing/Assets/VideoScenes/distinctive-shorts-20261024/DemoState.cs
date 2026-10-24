using System;using UnityEngine;
namespace YamyamCoding.DistinctiveShorts {
 [ExecuteAlways] public class DemoState:MonoBehaviour {
  public string topic,section="reveal"; public float elapsed;public bool autoplay;
  public Camera observer,player;public Transform actor,pawn,armA,armB;public Transform[] leaves;public Vector3[] leafSeeds;
  public Transform guideRoot,portalSurface;public Material portalMaterial;public GameObject windGuides;public float heightDifference=10,baseDistance=2,baseSize=.8f;
  [NonSerialized] public float distance,scale,angle,offset,velocity;[NonSerialized] public int depth=1;
  void Update(){if(autoplay&&Application.isPlaying){elapsed+=Time.deltaTime;Apply();}}
  public static float Residual(float t,float x0,float v0,float duration){
   if(t<=0)return x0;if(v0>0)v0=0;float T=v0<0?Mathf.Min(duration,-5*x0/v0):duration;
   if(t>=T)return 0;float a0=Mathf.Max(0,(-8*v0*T-20*x0)/(T*T));
   float A=-(a0*T*T+6*v0*T+12*x0)/(2*Mathf.Pow(T,5));float B=(3*a0*T*T+16*v0*T+30*x0)/(2*Mathf.Pow(T,4));float C=-(3*a0*T*T+12*v0*T+20*x0)/(2*Mathf.Pow(T,3));
   return (((A*t+B)*t+C)*t+a0/2)*t*t+v0*t+x0;
  }
  public void Apply(){float e=elapsed;
   if(topic=="titanfall"){
    float action=section=="numbers"?4.15f:section=="transfer"?2.9f:section=="view"?1.2f:2.5f;
    bool top=(section=="stack"||section=="reveal")?false:e>=action;
    actor.position=new Vector3(-1,top?heightDifference:0,1);player.transform.position=new Vector3(-1,1.6f+actor.position.y,-2.4f);player.transform.rotation=Quaternion.identity;
    observer.transform.position=new Vector3(16,14,-19);observer.transform.LookAt(new Vector3(0,5.5f,1));observer.fieldOfView=48;
    if(section=="view"){observer.transform.position=player.transform.position;observer.transform.rotation=player.transform.rotation;observer.fieldOfView=60;}
   }else if(topic=="superliminal"){
    distance=Mathf.Lerp(2,6,Mathf.SmoothStep(0,1,(e-.7f)/3));scale=distance/baseDistance;pawn.position=new Vector3(0,1.55f,distance);pawn.localScale=Vector3.one*scale;
    player.transform.position=new Vector3(0,1.55f,0);player.transform.rotation=Quaternion.identity;player.fieldOfView=43;
    if(guideRoot){guideRoot.gameObject.SetActive(section=="rays");int i=0;foreach(var line in guideRoot.GetComponentsInChildren<LineRenderer>(true)){
     Vector3 sample;if(i<9){float x=(i%3-1)*.075f,y=(i/3-1)*.075f;sample=new Vector3(x,.27f+y,-Mathf.Sqrt(.14f*.14f-x*x-y*y));}
     else if(i<15){float x=((i-9)%3-1)*.06f,y=-.20f+((i-9)/3)*.22f;sample=new Vector3(x,y,-Mathf.Sqrt(.11f*.11f-x*x));}
     else{float x=(i-17)*.08f;sample=new Vector3(x,-.34f,-Mathf.Sqrt(.21f*.21f-x*x));}
     line.SetPosition(0,player.transform.position);line.SetPosition(1,pawn.position+sample*scale);i++;
    }}

    observer.transform.position=new Vector3(9,6,-6);observer.transform.LookAt(new Vector3(0,1.3f,3));observer.fieldOfView=47;
    if(section=="reveal"){observer.transform.position=player.transform.position;observer.transform.rotation=player.transform.rotation;observer.fieldOfView=43;}
   }else if(topic=="ghost"){
    bool wind=section!="problem"&&section!="off";windGuides.SetActive(wind);float sim=Mathf.Min(e,8);
    for(int i=0;i<leaves.Length;i++){
     Vector3 pos=leafSeeds[i],v=new Vector3(1.05f,-.55f,0);int steps=Mathf.CeilToInt(sim*60);
     for(int k=0;k<steps;k++){float dt=Mathf.Min(1f/60,sim-k/60f);float r=Mathf.Sqrt(pos.x*pos.x+pos.z*pos.z);float w=wind&&pos.y<4?Mathf.Clamp01(1-r*r/(1.65f*1.65f)):0;
      v+=new Vector3(pos.x*w*.8f,-.25f+w*5.6f,pos.z*w*.8f)*dt;pos+=v*dt;if(pos.y<.08f){pos.y=.08f;v=Vector3.zero;}}
     leaves[i].position=pos;leaves[i].rotation=Quaternion.Euler(30+Mathf.Sin(e*2+i)*25,e*80+i*43,Mathf.Sin(e*2+i)*40);
    }
    observer.transform.position=new Vector3(7,5,-9);observer.transform.LookAt(new Vector3(0,1.35f,0));observer.fieldOfView=43;
   }else if(topic=="gears"){
    float t=e-1.2f;float before=50-20*t;
    offset=Residual(t,30,-20,1.6f);angle=t<0?before:20+offset;float eps=.001f;velocity=t<0?-20:(Residual(t+eps,30,-20,1.6f)-Residual(t-eps,30,-20,1.6f))/(2*eps);
    armA.localRotation=Quaternion.Euler(0,0,+(t<0?before:20));armB.localRotation=Quaternion.Euler(0,0,+angle);
    if(section=="difference"){angle=50;offset=30;velocity=0;armA.localRotation=Quaternion.Euler(0,0,20);armB.localRotation=Quaternion.Euler(0,0,50);}
    observer.transform.position=new Vector3(0,2.4f,-9);observer.transform.LookAt(new Vector3(0,1.25f,0));observer.fieldOfView=37;
   }else if(topic=="portal"){
    depth=section=="depth"||section=="close"?e<2?1:3:section=="recursive"?Mathf.Clamp(1+(int)(e/1.4f),1,3):3;
    observer.transform.position=new Vector3(Mathf.Sin(e*.3f)*.45f,1.6f,-2.7f);observer.transform.rotation=Quaternion.identity;observer.fieldOfView=52;
    portalMaterial.SetFloat("_MaskOnly",section=="mask"&&e<2.5f?1:0);
   }
  }
 }
}
