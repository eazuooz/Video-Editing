using UnityEngine;

namespace Yamyam.TechTen.Editor {
 public static partial class TechTenBuilder {
  const int PlaneMarkerLayer=10,PlaneInsetLabelLayer=11;
  static TextMesh PlaneLabel(string name,string text,float size,Color color,int layer) {
   var label=new GameObject(name).AddComponent<TextMesh>();label.gameObject.layer=layer;
   label.font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
   label.GetComponent<MeshRenderer>().sharedMaterial=label.font.material;
   label.fontSize=64;label.characterSize=size;label.anchor=TextAnchor.UpperLeft;
   label.color=color;label.text=text;return label;
  }
  static void PlaneAdditionalViews(TechTenDemo d) {
   var onboard=new GameObject("Fixed onboard camera - actual inset render").AddComponent<Camera>();
   onboard.enabled=false;onboard.clearFlags=CameraClearFlags.SolidColor;
   onboard.backgroundColor=new Color(.09f,.16f,.2f);onboard.nearClipPlane=.05f;onboard.farClipPlane=100;
   onboard.fieldOfView=48;onboard.aspect=432f/270;
   onboard.cullingMask=~(1<<PlaneMarkerLayer);
   d.shot.cullingMask&=~(1<<PlaneInsetLabelLayer);d.planeOnboardCamera=onboard;
   var marker=new GameObject("Onboard camera location - observer-only guide").transform;
   Part("Onboard camera body",PrimitiveType.Cube,Vector3.zero,new Vector3(.65f,.43f,.45f),Mat("onboard-camera",teal),marker);
   var lens=Part("Onboard camera lens",PrimitiveType.Cylinder,new Vector3(0,0,.34f),new Vector3(.29f,.22f,.29f),Mat("onboard-lens",yellow),marker);lens.localRotation=Quaternion.Euler(90,0,0);
   foreach(var t in marker.GetComponentsInChildren<Transform>())t.gameObject.layer=PlaneMarkerLayer;
   d.planeCameraMarker=marker;
   d.planeViewDirection=Line("Fixed onboard camera view direction",teal,.055f);d.planeViewDirection.positionCount=5;d.planeViewDirection.gameObject.layer=PlaneMarkerLayer;
   d.planeCameraLabel=PlaneLabel("Onboard camera position label","ONBOARD CAMERA",.11f,teal,PlaneMarkerLayer);
   d.planeCameraLabel.anchor=TextAnchor.MiddleCenter;
   d.planeOnboardLabel=PlaneLabel("Inset view label","ONBOARD VIEW",.18f,Color.white,PlaneInsetLabelLayer);
   // Save concrete fixed camera transforms as well as updating them per sample.
   onboard.transform.position=new Vector3(0,2.18f,2.75f);
   onboard.transform.rotation=Quaternion.LookRotation(new Vector3(0,-1,1),Vector3.up);
  }
 }
}
