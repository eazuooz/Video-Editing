using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace YamyamCoding.GameMath.EulerAxisAngle.V6.Editor
{
    // Separate one-still entry; does not save or change the existing scene assets.
    public static class EulerV6RecapStill
    {
        [Serializable] public class Job { public string outputDirectory; }
        public static void Run()
        {
            string project=Path.GetFullPath(Path.Combine(Application.dataPath,"..")).Replace('\\','/');
            if(!Application.isBatchMode||!project.EndsWith("/production/local/revision-v6/unity-capture",StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Recap still requires the task-owned isolated batch project.");
            var args=Environment.GetCommandLineArgs();string file=null;
            for(int i=0;i<args.Length-1;i++)if(args[i]=="-m04V6RecapJob")file=args[i+1];
            if(file==null)throw new ArgumentException("Missing recap job.");
            Job job=JsonUtility.FromJson<Job>(File.ReadAllText(file));Directory.CreateDirectory(job.outputDirectory);
            try
            {
                if(SystemInfo.graphicsDeviceType==GraphicsDeviceType.Null)throw new InvalidOperationException("A real one-still render requires graphics.");
                EulerV6Math.Validate();GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;QualitySettings.antiAliasing=2;
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
                var owner=new GameObject("V6 same actual Y90 recap pose, no guides").AddComponent<EulerV6Scene>();
                owner.shotCatalog=AssetDatabase.LoadAssetAtPath<TextAsset>(EulerV6Capture.Root+"/spatial-shots.json");
                owner.LoadShot("v6-41.answer-y90");owner.shot.axes=false;owner.shot.activeAxis="none";owner.shot.gimbals=false;
                owner.Build();owner.Evaluate(1f);
                var target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.Default){antiAliasing=2};target.Create();
                var pixels=new Texture2D(1920,1080,TextureFormat.RGB24,false,false);owner.SceneCamera.targetTexture=target;
                try
                {
                    owner.SceneCamera.Render();RenderTexture.active=target;pixels.ReadPixels(new Rect(0,0,1920,1080),0,0,false);pixels.Apply(false,false);
                    File.WriteAllBytes(Path.Combine(job.outputDirectory,"summary-y90-neutral.png"),pixels.EncodeToPNG());
                    File.WriteAllText(Path.Combine(job.outputDirectory,"state.json"),JsonUtility.ToJson(owner.State(0,1f)));
                    File.WriteAllText(Path.Combine(job.outputDirectory,"success.json"),"{\"nativeFrames\":1,\"width\":1920,\"height\":1080,\"shotId\":\"v6-41.answer-y90\",\"normalizedTime\":1,\"axes\":false,\"gimbals\":false,\"activeGuide\":false,\"savedScenes\":0}");
                }
                finally{owner.SceneCamera.targetTexture=null;RenderTexture.active=null;target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(pixels);}
                EditorApplication.Exit(0);
            }
            catch(Exception ex){Debug.LogException(ex);File.WriteAllText(Path.Combine(job.outputDirectory,"error.txt"),ex.ToString());EditorApplication.Exit(1);}
        }
    }
}
