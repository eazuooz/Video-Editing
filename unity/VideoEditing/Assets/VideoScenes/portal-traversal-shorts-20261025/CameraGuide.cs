using UnityEngine;
namespace YamyamCoding.PortalTraversal {
 // Observer-only geometry at the real optical centre. Never rendered into either view.
 public class CameraGuide : MonoBehaviour {
  public Camera target; public LineRenderer frustum,axis; public Transform opticalCentre;
  public void Sync(bool visible) {
   gameObject.SetActive(visible); if(!visible||!target)return;
   transform.SetPositionAndRotation(target.transform.position,target.transform.rotation);
   float z=1.15f,h=Mathf.Tan(target.fieldOfView*Mathf.Deg2Rad*.5f)*z,w=h*target.aspect;
   Vector3 o=Vector3.zero,a=new Vector3(-w,-h,z),b=new Vector3(w,-h,z),c=new Vector3(w,h,z),d=new Vector3(-w,h,z);
   frustum.positionCount=16;frustum.SetPositions(new[]{o,a,b,o,b,c,o,c,d,o,d,a,o,a,d,c});
   axis.positionCount=5;axis.SetPositions(new[]{o,new Vector3(0,0,1.55f),new Vector3(-.13f,0,1.28f),new Vector3(0,0,1.55f),new Vector3(.13f,0,1.28f)});
  }
 }
}
