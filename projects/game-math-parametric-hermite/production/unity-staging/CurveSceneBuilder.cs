#if UNITY_EDITOR
using System;
using System.IO;
using UnityEngine;
using Yamyam.MathCurves;
public static class CurveSceneBuilder {
 public static CurveLessonStage BuildStage(CurveLessonShot shot){
  string path=Path.GetFullPath(Application.dataPath).Replace('\\','/');
  bool valid=false;foreach(var slug in new[]{"game-math-parametric-hermite","game-math-bezier-subdivision","game-math-splines-continuity"})valid|=path.Contains("/"+slug+"/production/unity-staging/LocalUnity-");
  if(!valid)throw new InvalidOperationException("Isolated M31/M32/M33 project required");
  var stage=new GameObject("SourceCurves_"+shot.beatId).AddComponent<CurveLessonStage>();stage.shot=shot;stage.koreanFont=Font.CreateDynamicFontFromOSFont("Malgun Gothic",42);stage.Build();return stage;
 }
}
#endif
