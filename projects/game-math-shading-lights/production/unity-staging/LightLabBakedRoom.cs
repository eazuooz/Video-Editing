using System;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Yamyam.GameMath.LightLab {
 // A real Unity baked-lighting experiment in the same model/camera test bed.
 // It must not be described as baked until the engine has produced lightmaps.
 [ExecuteAlways] public sealed class LightLabBakedRoom:MonoBehaviour {
  public LabCue Cue;
  public Light MainLight;
  public bool BakeVerified;
  [SerializeField] Transform occluder,subject;
  [SerializeField] Vector3 originalOccluder,originalSubject;
  public void Build(LightLabStage stage,LabCue cue,Light light,Transform actor,Material baseMaterial){
   Cue=cue;MainLight=light;subject=actor;originalSubject=actor.position;
   RenderSettings.ambientLight=Color.black;RenderSettings.ambientIntensity=0;
   RoomPanel(stage,"Floor receiving baked shadows",new Vector3(0,-.08f,0),new Vector3(7,.12f,7),new Color(.65f,.65f,.65f),baseMaterial);
   RoomPanel(stage,"Back wall receiving indirect light",new Vector3(0,1.7f,3),new Vector3(7,3.5f,.12f),new Color(.7f,.7f,.7f),baseMaterial);
   RoomPanel(stage,"Warm side wall",new Vector3(-3.5f,1.7f,0),new Vector3(.12f,3.5f,6),new Color(.62f,.25f,.10f),baseMaterial);
   occluder=RoomPanel(stage,"Movable baffle · original bake configuration",new Vector3(.45f,1,-.4f),new Vector3(.16f,2,1.4f),new Color(.45f,.48f,.5f),baseMaterial);
   originalOccluder=occluder.position;
   var probes=new GameObject("Real Unity light-probe sample positions");probes.transform.SetParent(transform,false);
   var group=probes.AddComponent<LightProbeGroup>();var positions=new System.Collections.Generic.List<Vector3>();
   for(int x=-2;x<=2;x+=2)for(int y=0;y<=3;y+=3)for(int z=-2;z<=2;z+=2)positions.Add(new Vector3(x,y+.35f,z));
   group.probePositions=positions.ToArray();
#if UNITY_EDITOR
   foreach(var renderer in stage.GetComponentsInChildren<MeshRenderer>(true)){
    if(renderer is null)continue;
    bool movingSubject=cue.bakeAction=="walk" && renderer.transform.IsChildOf(actor);
    if(movingSubject){renderer.lightProbeUsage=UnityEngine.Rendering.LightProbeUsage.BlendProbes;continue;}
    var filter=renderer.GetComponent<MeshFilter>();if(!filter||!filter.sharedMesh)continue;
    var mesh=Instantiate(filter.sharedMesh);mesh.name=filter.sharedMesh.name+" · lightmap UV copy";
    if(!Unwrapping.GenerateSecondaryUVSet(mesh))throw new InvalidOperationException("Lightmap UV generation failed for "+renderer.name);
    filter.sharedMesh=mesh;stage.GeneratedObjects.Add(mesh);
    GameObjectUtility.SetStaticEditorFlags(renderer.gameObject,StaticEditorFlags.ContributeGI);
    renderer.receiveGI=ReceiveGI.Lightmaps;renderer.scaleInLightmap=1;
   }
   light.lightmapBakeType=cue.bakeMode=="indirect"?LightmapBakeType.Mixed:LightmapBakeType.Baked;
#endif
  }
  Transform RoomPanel(LightLabStage stage,string name,Vector3 position,Vector3 scale,Color color,Material basis){
   var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name=name;g.transform.SetParent(transform,false);g.transform.position=position;g.transform.localScale=scale;
   var mat=new Material(basis);mat.SetColor("_BaseColor",color);mat.SetFloat("_Smoothness",.15f);stage.GeneratedObjects.Add(mat);g.GetComponent<Renderer>().sharedMaterial=mat;return g.transform;
  }
  public void Apply(float seconds){
   if(Cue==null||!BakeVerified)return;
   float start=Cue.stepTimes!=null&&Cue.stepTimes.Length>0?Cue.stepTimes[0]:Cue.duration*.4f;
   float u=Mathf.SmoothStep(0,1,Mathf.Clamp01((seconds-start)/3));
   if(Cue.bakeAction=="moveOccluder")occluder.position=originalOccluder+Vector3.right*(u*1.8f);
   if(Cue.bakeAction=="switchOff")MainLight.intensity=2*(1-u);
   if(Cue.bakeAction=="walk")subject.position=originalSubject+Vector3.right*Mathf.Lerp(-.8f,1.8f,u);
  }
 }
}
