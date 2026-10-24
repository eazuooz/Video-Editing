using UnityEngine;
namespace YamyamCoding.PortalTraversal {
 public class PortalDemo : MonoBehaviour {
  public string topic,section;public float elapsed,sectionDuration=6;public Transform entry,exit,body,copy;public Camera observer,player;public Material bodyMaterial,copyMaterial;public AnimationClip walkClip;public LineRenderer incoming,outgoing;public float speed=6;public bool crossed,resetVelocity;public Vector3 velocity;public float signedDistance;
  public static Quaternion Turn=Quaternion.Euler(0,180,0);
  public Vector3 MapPoint(Vector3 p){return exit.TransformPoint(Turn*entry.InverseTransformPoint(p));}
  public Quaternion MapRotation(Quaternion q){return exit.rotation*Turn*Quaternion.Inverse(entry.rotation)*q;}
  public Vector3 MapVector(Vector3 v){return exit.TransformDirection(Turn*entry.InverseTransformDirection(v));}
  public void Arrow(LineRenderer line,Vector3 p,Vector3 v){Vector3 d=v.normalized,b=p+v*.22f,side=Vector3.Cross(d,Vector3.forward).normalized*.14f;if(side.sqrMagnitude<.01f)side=Vector3.right*.14f;line.positionCount=5;line.SetPositions(new[]{p,b,b-d*.25f+side,b,b-d*.25f-side});}
  public void Apply(){if(topic=="momentum")Momentum();else Traversal();}
  void Momentum(){
   observer.transform.position=new Vector3(10,7,-14);observer.transform.LookAt(new Vector3(.7f,1.8f,0));observer.fieldOfView=38;
   resetVelocity=section=="reset";Vector3 vin=Vector3.down*speed,vout=MapVector(vin);velocity=vout;
   // This authored demonstration exposes a paused transform and a normal-time post-exit simulation.
   float t=Mathf.Clamp(elapsed-1.1f,0,1.25f);Vector3 start=entry.position+Vector3.up*2.8f;float fall=2.8f/speed;
   bool teaching=section=="vector"||section=="transform"||section=="numbers";
   if(teaching){body.position=entry.position+Vector3.up*1.6f;copy.position=exit.position+Vector3.right*1.6f;copy.gameObject.SetActive(true);crossed=false;}
   else{crossed=t>=fall;float after=Mathf.Max(0,t-fall);velocity=crossed?(resetVelocity?Vector3.zero:vout)+Vector3.down*9.81f*after:vin;body.position=crossed?exit.position+(resetVelocity?Vector3.zero:vout)*after+Vector3.down*4.905f*after*after:start+vin*t;body.position=new Vector3(body.position.x,Mathf.Max(.3f,body.position.y),body.position.z);copy.gameObject.SetActive(false);}
   float turn=section=="transform"?Mathf.SmoothStep(0,1,Mathf.Clamp01((elapsed-1.0f)/2.4f)):1;
   Arrow(incoming,entry.position+Vector3.up*1.8f,vin);Arrow(outgoing,exit.position+Vector3.right*2.05f,Quaternion.Slerp(Quaternion.identity,exit.rotation*Turn*Quaternion.Inverse(entry.rotation),turn)*vin);
   incoming.enabled=teaching;outgoing.enabled=teaching||crossed; if(!teaching&&crossed)Arrow(outgoing,body.position,resetVelocity?Vector3.down*1.6f:vout);
   signedDistance=entry.InverseTransformPoint(body.position).z;
  }
  void Traversal(){
   if(walkClip){walkClip.SampleAnimation(body.gameObject,elapsed%walkClip.length);walkClip.SampleAnimation(copy.gameObject,elapsed%walkClip.length);}
   observer.transform.position=new Vector3(0,10,-8);observer.transform.LookAt(new Vector3(0,.2f,.8f));observer.fieldOfView=49;
   float duration=Mathf.Max(sectionDuration,3),u=Mathf.Clamp01((elapsed-.4f)/(duration-1));float z;
   if(section=="camera"||section=="screen")z=Mathf.Lerp(-.8f,1.65f,u);else if(section=="half"||section=="clip")z=2.45f+Mathf.Sin(elapsed*1.0f)*.28f;else z=Mathf.Lerp(-.7f,4.0f,u);
   float side=(section=="camera"?Mathf.Sin(elapsed*.8f)*.45f:0);
   Vector3 entryPose=new Vector3(entry.position.x+side,.08f,z);Quaternion facing=Quaternion.Euler(0,0,0);
   crossed=z>=entry.position.z;signedDistance=Vector3.Dot(entryPose-entry.position,entry.forward);
   body.position=crossed?MapPoint(entryPose):entryPose;body.rotation=crossed?MapRotation(facing):facing;
   copy.position=crossed?entryPose:MapPoint(entryPose);copy.rotation=crossed?facing:MapRotation(facing);copy.gameObject.SetActive(Mathf.Abs(z-entry.position.z)<1.15f||section=="half"||section=="clip");
   Vector4 plane=new Vector4(0,0,-1,entry.position.z);bodyMaterial.SetVector("_ClipPlane",plane);copyMaterial.SetVector("_ClipPlane",plane);
   Vector3 eye=entryPose+Vector3.up*1.32f;Quaternion look=Quaternion.LookRotation((entry.position+Vector3.up*.05f-eye).normalized,Vector3.up);
   if(section!="camera")look=Quaternion.identity;
   player.transform.position=crossed?MapPoint(eye):eye;player.transform.rotation=crossed?MapRotation(look):look;
   incoming.enabled=outgoing.enabled=true;Arrow(incoming,new Vector3(entry.position.x,.04f,.1f),Vector3.forward*5);Arrow(outgoing,new Vector3(exit.position.x,.04f,2.0f),Vector3.back*5);
  }
 }
}
