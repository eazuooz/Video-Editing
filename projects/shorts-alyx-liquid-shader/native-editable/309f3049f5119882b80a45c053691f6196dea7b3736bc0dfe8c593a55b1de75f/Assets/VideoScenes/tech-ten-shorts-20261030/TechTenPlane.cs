using UnityEngine;

namespace Yamyam.TechTen {
 public sealed partial class TechTenDemo {
  public Camera planeOnboardCamera;
  public Transform planeCameraMarker;
  public LineRenderer planeViewDirection;
  public TextMesh planeCameraLabel,planeOnboardLabel;
  public float planeScrollMeters;
  public bool PlaneHasInset { get { return topic=="uncharted3-fixed-plane-scrolling-desert" && stage==2 && planeOnboardCamera; } }

  // This is an original, fixed-plane teaching model. The repeating tiles and
  // two-camera layout are not claimed to reproduce Naughty Dog's implementation.
  void PlaneSample() {
   foreach(var r in FindObjectsByType<Renderer>())
    if(r.name=="Dark teaching stage"||r.name.StartsWith("GridX")||r.name.StartsWith("GridZ"))r.enabled=false;
   float runningSeconds=stage==0?0:Mathf.Max(0,elapsed);
   if(stage!=0 && actionKind=="background-toggle") {
    float stop=Mathf.Max(0,actionStartSeconds),resume=Mathf.Max(stop,actionResumeSeconds);
    // Integrate the enabled intervals. Resuming continues from the held position.
    runningSeconds=Mathf.Min(Mathf.Max(0,elapsed),stop)+Mathf.Max(0,elapsed-resume);
   }
   planeScrollMeters=runningSeconds*3;
   float offset=planeScrollMeters%12;
   for(int i=0;i<props.Length;i++)props[i].localPosition=new Vector3(0,-1,(i-1)*12-offset);
   var plane=actors[0];plane.position=new Vector3(0,1.5f,0);lastGap=plane.position.z;
   foreach(var p in plane.GetComponentsInChildren<Transform>())
    if(p.name.StartsWith("Propeller "))p.localRotation=Quaternion.Euler(0,0,elapsed*1400);
   shot.transform.position=stage==2?new Vector3(11,10,-13):new Vector3(4,6,-10);
   shot.transform.LookAt(stage==2?new Vector3(0,0,0):new Vector3(0,1,1));
   for(int i=0;i<lines.Length;i++)lines[i].enabled=stage==2;
   if(!planeOnboardCamera)throw new System.InvalidOperationException("Saved plane scene lacks its fixed onboard camera.");
   // Position/rotation are fixed relative to the stationary plane, not animated
   // to create apparent travel. Only the desert is translated.
   planeOnboardCamera.transform.position=plane.TransformPoint(new Vector3(0,.68f,2.75f));
   planeOnboardCamera.transform.rotation=Quaternion.LookRotation(new Vector3(0,-1,1),Vector3.up);
   bool show=stage==2;
   if(planeCameraMarker){planeCameraMarker.gameObject.SetActive(show);planeCameraMarker.SetPositionAndRotation(planeOnboardCamera.transform.position,planeOnboardCamera.transform.rotation);}
   if(planeViewDirection){planeViewDirection.enabled=show;Vector3 eye=planeOnboardCamera.transform.position,forward=planeOnboardCamera.transform.forward,tip=eye+forward*3,right=planeOnboardCamera.transform.right*.24f;planeViewDirection.SetPositions(new[]{eye,tip,tip-forward*.45f+right,tip,tip-forward*.45f-right});}
   if(planeCameraLabel){planeCameraLabel.gameObject.SetActive(show);planeCameraLabel.transform.position=planeOnboardCamera.transform.position+Vector3.up*.85f-shot.transform.right*2.5f;planeCameraLabel.transform.rotation=shot.transform.rotation;}
   if(planeOnboardLabel){planeOnboardLabel.gameObject.SetActive(show);planeOnboardLabel.transform.position=planeOnboardCamera.ViewportToWorldPoint(new Vector3(.04f,.94f,2));planeOnboardLabel.transform.rotation=planeOnboardCamera.transform.rotation;}
  }
 }
}
