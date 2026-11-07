using System;
using UnityEngine;
namespace Yamyam.Architectural111.ProspectRefuge.Closeup {
 [Serializable] public sealed class CloseupConfig {
  public int frames,fps,width,height;
  public Vector3 cameraOffset,lookOffset;
  public float verticalFieldOfView,nearClip,farClip;
  public string comparisonPolicy,sourceKind;
 }
 // A third camera only. No main rig, actor, collider, input or guide is modified.
 [DefaultExecutionOrder(-100)]
 public sealed class ProspectRefugeCloseupCamera:MonoBehaviour {
  public ProspectRefugeExperiment originalRig;
  public Transform subject;
  public Camera view;
  public CloseupConfig config;
  public static void RestoreSourceAspect(ProspectRefugeExperiment rig) {
   if(!rig||rig.config==null||rig.config.width!=1920||rig.config.height!=1080||!rig.playerCamera||!rig.observerCamera)throw new InvalidOperationException("Pinned original camera capture settings required");
   float aspect=rig.config.width/(float)rig.config.height;
   rig.playerCamera.aspect=aspect;rig.observerCamera.aspect=aspect;
  }
  void Start(){if(Application.isPlaying&&originalRig){RestoreSourceAspect(originalRig);Refresh();}}
  public void Refresh() {
   if(!subject||!view||config==null)throw new InvalidOperationException("Missing derivative camera inputs");
   view.transform.position=subject.position+config.cameraOffset;
   view.transform.LookAt(subject.position+config.lookOffset,Vector3.up);
   view.fieldOfView=config.verticalFieldOfView;view.aspect=config.width/(float)config.height;
   view.nearClipPlane=config.nearClip;view.farClipPlane=config.farClip;
  }
  void LateUpdate(){if(Application.isPlaying&&subject&&view&&config!=null)Refresh();}
 }
}
