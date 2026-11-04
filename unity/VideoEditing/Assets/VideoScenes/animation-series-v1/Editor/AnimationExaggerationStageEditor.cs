using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Yamyam.AnimationSeries {
[CustomEditor(typeof(AnimationExaggerationStage))]
public sealed class AnimationExaggerationStageEditor : Editor {
 RenderTexture preview;
 string error;
 public override void OnInspectorGUI() {
  DrawDefaultInspector();
  EditorGUILayout.HelpBox("저장된 profile JSON과 소스 지문으로 RT·도형을 다시 만듭니다. 현재 소스 지문이 다르면 과거 스냅샷을 먼저 복원해야 합니다.",MessageType.Info);
  if(GUILayout.Button("저장된 소스로 미리보기 재구성")) {
   try {
    var stage=(AnimationExaggerationStage)target;
    if(!preview){preview=new RenderTexture(1920,1080,24){antiAliasing=4};preview.Create();}
    var scene=stage.gameObject.scene;
    var mask=EditorSceneManager.CalculateAvailableSceneCullingMask();
    if(mask==0)throw new System.InvalidOperationException("No available scene-culling bit.");
    EditorSceneManager.SetSceneCullingMask(scene,mask);
    stage.RebuildFromSavedSource(preview,mask,stage.editorPreviewSeconds);
    RenderPipeline.SubmitRenderRequest(stage.camera,new RenderPipeline.StandardRequest{destination=preview});
    EditorSceneManager.MarkSceneDirty(scene);SceneView.RepaintAll();error=null;
   } catch(System.Exception e){error=e.ToString();}
  }
  if(!string.IsNullOrEmpty(error))EditorGUILayout.HelpBox(error,MessageType.Error);
  if(preview)GUILayout.Label(preview,GUILayout.Width(EditorGUIUtility.currentViewWidth-40),GUILayout.Height((EditorGUIUtility.currentViewWidth-40)*9/16));
 }
 void OnDisable(){if(preview){preview.Release();DestroyImmediate(preview);}}
}
}
