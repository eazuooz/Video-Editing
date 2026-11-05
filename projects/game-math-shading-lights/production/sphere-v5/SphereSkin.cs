using UnityEngine;
namespace Yamyam.GameMath.LightLab {
 public sealed partial class LightLabStage {
  Transform SphereSubject() {
   var g=GameObject.CreatePrimitive(PrimitiveType.Sphere);g.name="Material sphere";g.transform.SetParent(transform,false);
   g.transform.position=new Vector3(-.7f,1.42f,0);g.transform.localScale=Vector3.one*2.72f;return g.transform;
  }
  Transform SunMarker(){
   var root=NewObject("Sun · editorial light marker").transform;
   var mat=NewMaterial("Universal Render Pipeline/Unlit",new Color(1,.73f,.23f));
   var disk=GameObject.CreatePrimitive(PrimitiveType.Sphere);disk.name="Sun disk";disk.transform.SetParent(root,false);disk.transform.localScale=Vector3.one*.31f;disk.GetComponent<Renderer>().sharedMaterial=mat;
   for(int i=0;i<8;i++){float a=i*Mathf.PI/4;var d=new Vector3(Mathf.Cos(a),Mathf.Sin(a),0);
    var r=GameObject.CreatePrimitive(PrimitiveType.Capsule);r.name="Sun ray";r.transform.SetParent(root,false);r.transform.localPosition=d*.268f;r.transform.localRotation=Quaternion.FromToRotation(Vector3.up,d);r.transform.localScale=new Vector3(.032f,.071f,.032f);r.GetComponent<Renderer>().sharedMaterial=mat;}
   return root;
  }
 }
}
