using System;
using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
namespace Yamyam.MathMechanics {
 [Serializable] public class MechanicsStep {
  public string anchor,formula,meaning;
  public MechanicsShot model=new MechanicsShot();
 }
 [Serializable] public class MechanicsLessonShot {
  public string beatId="UNBOUND";
  public MechanicsStep[] steps=Array.Empty<MechanicsStep>();
  public double durationSeconds;
  public double[] stepSeconds=Array.Empty<double>(),stepPositions=Array.Empty<double>();
 }
 [ExecuteAlways] public sealed class MechanicsLessonStage:MonoBehaviour {
  public MechanicsLessonShot shot=new MechanicsLessonShot();
  public GameObject objectPrefab,secondaryPrefab;
  public Font koreanFont;
  [NonSerialized] public MechanicsTeachingStage stage;
  public Camera observer,stageCamera;
  public double previewSeconds;
  readonly List<UnityEngine.Object> owned=new List<UnityEngine.Object>();
  public void RememberMaterial(Material m){owned.Add(m);}
  void OnEnable(){koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",42);foreach(var label in GetComponentsInChildren<Text>(true))label.font=koreanFont;}
  [ContextMenu("Preview teaching time")] public void Preview(){Evaluate(previewSeconds);}
  public void Build(){
   if(stage!=null)return;
   if(shot.steps.Length==0)throw new InvalidOperationException("Source teaching steps required");
   while(transform.childCount>0)DestroyImmediate(transform.GetChild(0).gameObject);
   var go=new GameObject("Mechanics source experiment");go.transform.SetParent(transform,false);stage=go.AddComponent<MechanicsTeachingStage>();
   stage.shot=shot.steps[0].model;stage.objectPrefab=objectPrefab;stage.secondaryPrefab=secondaryPrefab;stage.koreanFont=koreanFont;stage.Build();observer=stage.observer;stageCamera=observer;RememberMaterial(stage.GuideMaterial);
  }
  public void Evaluate(double seconds){
   if(shot.durationSeconds<=0)throw new InvalidOperationException("Explicit cue duration required");if(stage==null)Build();
   double u=Math.Max(0,Math.Min(1,seconds/shot.durationSeconds));
   if(shot.stepSeconds.Length>0){
    if(shot.stepSeconds.Length!=shot.stepPositions.Length||shot.stepSeconds.Length<2||Math.Abs(shot.stepSeconds[0])>1e-8||Math.Abs(shot.stepSeconds[shot.stepSeconds.Length-1]-shot.durationSeconds)>.001)throw new InvalidOperationException("Complete speech map required");
    for(int i=1;i<shot.stepSeconds.Length;i++){
     double a=shot.stepSeconds[i-1],b=shot.stepSeconds[i];if(b<=a||shot.stepPositions[i]<shot.stepPositions[i-1])throw new InvalidOperationException("Monotonic speech map required");
     if(seconds>=a)u=shot.stepPositions[i-1]+(shot.stepPositions[i]-shot.stepPositions[i-1])*Math.Max(0,Math.Min(1,(seconds-a)/(b-a)));
    }
   }
   int index=Math.Min(shot.steps.Length-1,(int)(u*shot.steps.Length));double phase=Math.Min(1,u*shot.steps.Length-index);
   var step=shot.steps[index];stage.shot=step.model;stage.Evaluate(phase);stage.SetSourceStep(step.formula,step.meaning);
  }
 }
}
