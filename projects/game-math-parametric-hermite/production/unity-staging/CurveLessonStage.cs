using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using UnityEngine.UI;
namespace Yamyam.MathCurves {
 [Serializable] public class CurveStep {public string anchor,formula,meaning;public CurveShot model=new CurveShot();}
 [Serializable] public class CurveLessonShot {public string beatId="UNBOUND";public double durationSeconds;public double[] stepSeconds=Array.Empty<double>(),stepPositions=Array.Empty<double>();public CurveStep[] steps=Array.Empty<CurveStep>();}
 [ExecuteAlways] public sealed class CurveLessonStage:MonoBehaviour {
  public CurveLessonShot shot=new CurveLessonShot();public Font koreanFont;public Camera stageCamera;
  [NonSerialized] public CurveTeachingStage stage;public double previewSeconds;
  readonly List<UnityEngine.Object> owned=new List<UnityEngine.Object>();
  void OnEnable(){koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",42);foreach(var t in GetComponentsInChildren<Text>(true))t.font=koreanFont;}
  [ContextMenu("Preview source teaching cue")]public void Preview(){Evaluate(previewSeconds);}
  public void Build(){if(stage)return;if(shot.steps.Length==0)throw new InvalidOperationException("Complete source teaching steps required");while(transform.childCount>0)DestroyImmediate(transform.GetChild(0).gameObject);var g=new GameObject("Curves source experiment");g.transform.SetParent(transform,false);stage=g.AddComponent<CurveTeachingStage>();stage.koreanFont=koreanFont;stage.shot=shot.steps[0].model;stage.Build();stageCamera=stage.stageCamera;}
  public void Evaluate(double seconds){if(shot.durationSeconds<=0)throw new InvalidOperationException("Explicit duration required");Build();double u=Math.Max(0,Math.Min(1,seconds/shot.durationSeconds));if(shot.stepSeconds.Length>0){if(shot.stepSeconds.Length!=shot.stepPositions.Length||shot.stepSeconds.Length<2||Math.Abs(shot.stepSeconds[0])>1e-7||Math.Abs(shot.stepSeconds[shot.stepSeconds.Length-1]-shot.durationSeconds)>.001)throw new InvalidOperationException("Full speech map required");for(int i=1;i<shot.stepSeconds.Length;i++){double a=shot.stepSeconds[i-1],b=shot.stepSeconds[i];if(b<=a||shot.stepPositions[i]<shot.stepPositions[i-1])throw new InvalidOperationException("Monotonic speech map required");if(seconds>=a)u=shot.stepPositions[i-1]+(shot.stepPositions[i]-shot.stepPositions[i-1])*Math.Max(0,Math.Min(1,(seconds-a)/(b-a)));}}
   int index=Math.Min(shot.steps.Length-1,(int)(u*shot.steps.Length));double phase=Math.Min(1,u*shot.steps.Length-index);var step=shot.steps[index];stage.shot=step.model;stage.shot.steps=new[]{step.formula};stage.shot.stepIndex=0;stage.Evaluate(phase);
   if(stage.sharedLineMaterial&&!owned.Contains(stage.sharedLineMaterial))owned.Add(stage.sharedLineMaterial);
  }
 }
}
