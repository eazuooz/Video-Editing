using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
namespace YamyamCoding.GravityLesson.Editor {
public static class Capture {
 [Serializable] class FramePlan { public float[] phases; }
 [Serializable] class Receipt { public string device,deviceType,unityVersion; public int frames,width,height; public string kind="CPU/WARP own implementation"; }
 public static void Run(){
  try {
   var args=Environment.GetCommandLineArgs();string output=args[Array.IndexOf(args,"-lessonOutput")+1];int frames=int.Parse(args[Array.IndexOf(args,"-lessonFrames")+1]);Directory.CreateDirectory(output);
   int phaseArg=Array.IndexOf(args,"-lessonPhaseFile");var plan=phaseArg>=0?JsonUtility.FromJson<FramePlan>(File.ReadAllText(args[phaseArg+1])):null;if(plan!=null&&plan.phases.Length!=frames)throw new Exception("Phase-plan count mismatch");
   var device=SystemInfo.graphicsDeviceName;if(!device.Contains("Microsoft"))throw new Exception("Expected WARP CPU rendering, received: "+device);
   EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);var demo=Demo.Build();
   var target=new RenderTexture(1080,1080,24){antiAliasing=4};target.Create();var pixels=new Texture2D(1080,1080,TextureFormat.RGB24,false);demo.observer.targetTexture=target;
   Directory.CreateDirectory("Assets/Lesson/Scenes");Directory.CreateDirectory("Assets/Lesson/Generated");AssetDatabase.Refresh();
   foreach(var mat in Resources.FindObjectsOfTypeAll<Material>().Where(m=>!AssetDatabase.Contains(m)&&m.name!="Default-Material"&&m.name!="Default-Line"&&m.name!="Default-Particle").ToArray()){
     if(mat.hideFlags!=HideFlags.None)continue;AssetDatabase.CreateAsset(mat,AssetDatabase.GenerateUniqueAssetPath("Assets/Lesson/Generated/Material.mat"));
   }
   int[] saveAt={0,Mathf.RoundToInt((frames-1)*.2f),Mathf.RoundToInt((frames-1)*.45f),Mathf.RoundToInt((frames-1)*.58f),Mathf.RoundToInt((frames-1)*.9f)};
   for(int f=0;f<frames;f++){
    demo.Tick(plan!=null?plan.phases[f]:frames==1?.6f:(float)f/(frames-1));demo.observer.Render();var old=RenderTexture.active;RenderTexture.active=target;pixels.ReadPixels(new Rect(0,0,1080,1080),0,0);pixels.Apply();RenderTexture.active=old;
    File.WriteAllBytes(Path.Combine(output,f.ToString("D5")+".jpg"),pixels.EncodeToJPG(92));
    if(saveAt.Contains(f)){
     foreach(var mf in UnityEngine.Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None)){var m=mf.sharedMesh;if(m&&!AssetDatabase.Contains(m)){AssetDatabase.CreateAsset(m,AssetDatabase.GenerateUniqueAssetPath("Assets/Lesson/Generated/Mesh.asset"));}}
     demo.observer.targetTexture=null;EditorSceneManager.SaveScene(demo.gameObject.scene,"Assets/Lesson/Scenes/Stage-"+f.ToString("D5")+".unity");demo.observer.targetTexture=target;
    }
   }
   File.WriteAllText(Path.Combine(output,"success.json"),JsonUtility.ToJson(new Receipt{device=device,deviceType=SystemInfo.graphicsDeviceType.ToString(),unityVersion=Application.unityVersion,frames=frames,width=1080,height=1080},true));
   EditorApplication.Exit(0);
  }catch(Exception ex){Debug.LogException(ex);EditorApplication.Exit(1);}
 }
}
}
