using UnityEngine;
namespace YamyamCoding.InteriorShort {
 [ExecuteAlways] public class InteriorControls:MonoBehaviour {
  public Material window;public Camera viewer;public bool mapped=true,showPhysicalPlane;
  void Update(){Apply();}
  public void Apply(){if(!window||!viewer)return;window.SetVector("_Viewer",transform.InverseTransformPoint(viewer.transform.position));window.SetFloat("_Mapped",mapped?1:0);window.SetFloat("_Structure",showPhysicalPlane?1:0);}
 }
}
