using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace YamyamCoding.GameMath.EulerAxisAngle.V6.Editor
{
    public static class EulerV6Capture
    {
        public const string Root="Assets/VideoScenes/game-math-euler-axis-angle/revision-v6";
        [Serializable] public class Clip {public string shotId;public int frames=180;}
        [Serializable] public class Job {public string outputDirectory,ffmpegPath;public bool bakeScenes,captureTestbed,bakeOnly;public Clip[] clips;}
        public static void Run()
        {
            RequireIsolated();EulerV6Math.Validate();
            string path=Argument("-m04V6Job");Job job=JsonUtility.FromJson<Job>(File.ReadAllText(path));
            Directory.CreateDirectory(job.outputDirectory);
            GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;QualitySettings.antiAliasing=2;
            try
            {
                TextAsset catalog=AssetDatabase.LoadAssetAtPath<TextAsset>(Root+"/spatial-shots.json");
                if(catalog==null)throw new InvalidOperationException("V6 catalog was not imported.");
                if(job.bakeOnly)
                {
                    if(SystemInfo.graphicsDeviceType!=GraphicsDeviceType.Null)throw new InvalidOperationException("CPU-only bake must use -nographics and the Null graphics device.");
                    if(job.captureTestbed||(job.clips!=null&&job.clips.Length>0))throw new InvalidOperationException("CPU-only job must contain no capture clips or testbed render.");
                    Bake(catalog,false);
                    File.WriteAllText(Path.Combine(job.outputDirectory,"bake-success.json"),"{\"editor\":\""+Application.unityVersion+"\",\"graphicsDeviceType\":\"Null\",\"cameraRenderCalls\":0,\"capturedFrames\":0,\"encodedClips\":0,\"textMetricsPrimed\":false,\"renderReview\":\"pending actual GPU sample\"}");
                    EditorApplication.Exit(0);return;
                }
                if(SystemInfo.graphicsDeviceType==GraphicsDeviceType.Null)throw new InvalidOperationException("Actual capture requires a graphics device; Null is reserved for bake-only.");
                if(job.bakeScenes)Bake(catalog,true);
                foreach(var clip in job.clips)Capture(job,clip,catalog);
                if(job.captureTestbed)CaptureTestbedStill(job,catalog);
                File.WriteAllText(Path.Combine(job.outputDirectory,"capture-success.json"),"{\"editor\":\""+Application.unityVersion+"\",\"pipeline\":\"isolated built-in\",\"handedness\":\"left\",\"vectorConvention\":\"row\",\"width\":1920,\"height\":1080,\"fps\":60}");
                EditorApplication.Exit(0);
            }
            catch(Exception ex){UnityEngine.Debug.LogException(ex);File.WriteAllText(Path.Combine(job.outputDirectory,"capture-error.txt"),ex.ToString());EditorApplication.Exit(1);}
        }
        private static void Bake(TextAsset catalog,bool primeText)
        {
            var data=JsonUtility.FromJson<V6Catalog>(catalog.text);
            var first=new Dictionary<string,V6Shot>();foreach(var s in data.shots)if(!first.ContainsKey(s.sceneId))first[s.sceneId]=s;
            var saved=new List<string>();
            foreach(var item in first)
            {
                Scene sc=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
                EditorUtility.UnloadUnusedAssetsImmediate();
                var owner=new GameObject("Yamyam M04 V6 "+item.Key).AddComponent<EulerV6Scene>();
                owner.shotCatalog=catalog;owner.LoadShot(item.Value.id);owner.Build();owner.Evaluate(0);if(primeText)owner.PrimeTextGeometry();
                Persist(owner);string dest=Root+"/Scenes/"+item.Key+".unity";
                if(!EditorSceneManager.SaveScene(sc,dest))throw new IOException("Could not save "+dest);saved.Add(dest);
            }
            Scene test=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var bed=new GameObject("Yamyam M04 V6 shared aircraft testbed").AddComponent<EulerV6Scene>();
            bed.shotCatalog=catalog;bed.LoadShot("v6-04.B01");bed.shot.axes=false;bed.shot.activeAxis="none";bed.Build();bed.Evaluate(0);if(primeText)bed.PrimeTextGeometry();Persist(bed);
            EditorSceneManager.SaveScene(test,Root+"/Scenes/testbed.unity");
            AssetDatabase.SaveAssets();AssetDatabase.Refresh();
            File.WriteAllText("m04-v6-scenes-saved.json","{\"sceneCount\":"+saved.Count+",\"testbedSaved\":true,\"totalSceneFiles\":"+(saved.Count+1)+",\"mathChecks\":\"passed\",\"editor\":\""+Application.unityVersion+"\",\"graphicsDeviceType\":\""+SystemInfo.graphicsDeviceType+"\",\"textMetricsPrimed\":"+(primeText?"true":"false")+",\"mode\":\""+(primeText?"gpu-capable-bake":"cpu-null-geometry-bake")+"\"}");
        }
        private static void Persist(EulerV6Scene owner)
        {
            Directory.CreateDirectory(Root+"/Shared");
            foreach(var filter in owner.GetComponentsInChildren<MeshFilter>(true))
            {
                Mesh mesh=filter.sharedMesh;if(mesh==null||EditorUtility.IsPersistent(mesh))continue;
                var b=new StringBuilder(mesh.name);foreach(var v in mesh.vertices)b.Append(v.x.ToString("R",CultureInfo.InvariantCulture)).Append(',').Append(v.y.ToString("R",CultureInfo.InvariantCulture)).Append(',').Append(v.z.ToString("R",CultureInfo.InvariantCulture)).Append(';');foreach(int i in mesh.triangles)b.Append(i).Append(',');
                string path=Root+"/Shared/mesh-"+Hash(b.ToString())+".asset";
                Mesh shared=AssetDatabase.LoadAssetAtPath<Mesh>(path);
                if(shared==null){shared=UnityEngine.Object.Instantiate(mesh);AssetDatabase.CreateAsset(shared,path);}filter.sharedMesh=shared;
            }
            foreach(var renderer in owner.GetComponentsInChildren<Renderer>(true))
            {
                // A Null graphics import may not have allocated the dynamic
                // font atlas. Always preserve the built-in TextMesh font
                // material rather than misclassifying it as a solid color.
                if(renderer.GetComponent<TextMesh>()!=null)continue;
                Material mat=renderer.sharedMaterial;if(mat==null||EditorUtility.IsPersistent(mat))continue;
                // Legacy font materials are built-in references; generated solid-color materials are shared.
                if(mat.mainTexture!=null)continue;
                string key=mat.shader.name+ColorUtility.ToHtmlStringRGBA(mat.color);
                string path=Root+"/Shared/material-"+Hash(key)+".mat";Material shared=AssetDatabase.LoadAssetAtPath<Material>(path);
                if(shared==null){shared=UnityEngine.Object.Instantiate(mat);AssetDatabase.CreateAsset(shared,path);}renderer.sharedMaterial=shared;
            }
        }
        private static string Hash(string text)
        {using(var sha=SHA256.Create())return BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(text))).Replace("-","").ToLowerInvariant().Substring(0,20);}
        private static void Capture(Job job,Clip clip,TextAsset catalog)
        {
            if(clip.frames<2||clip.frames>3600)throw new ArgumentException("Finite V6 clip must have2..3600 frames.");
            var sc=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            EditorUtility.UnloadUnusedAssetsImmediate();
            var owner=new GameObject("V6 finite capture "+clip.shotId).AddComponent<EulerV6Scene>();owner.shotCatalog=catalog;owner.LoadShot(clip.shotId);owner.Build();
            var target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.Default){antiAliasing=2};target.Create();
            var pixels=new Texture2D(1920,1080,TextureFormat.RGB24,false,false);owner.SceneCamera.targetTexture=target;
            owner.PrimeTextGeometry();
            string stem=clip.shotId;var errors=new StringBuilder();Process encoder=null;
            try
            {
                var info=new ProcessStartInfo(job.ffmpegPath){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardError=true,CreateNoWindow=true,
                    Arguments="-hide_banner -loglevel warning -n -f rawvideo -pixel_format rgb24 -video_size 1920x1080 -framerate60 -i pipe:0 -vf vflip -an -c:v libx264 -threads2 -preset fast -crf16 -pix_fmt yuv420p -movflags +faststart "+Quote(Path.Combine(job.outputDirectory,stem+".mp4"))};
                info.Arguments=info.Arguments.Replace("-framerate60","-framerate 60").Replace("-threads2","-threads 2").Replace("-crf16","-crf 16");
                encoder=new Process{StartInfo=info};encoder.ErrorDataReceived+=(_,e)=>{if(e.Data!=null)lock(errors)errors.AppendLine(e.Data);};encoder.Start();encoder.BeginErrorReadLine();
                using(var anchors=new StreamWriter(Path.Combine(job.outputDirectory,stem+".anchors.ndjson"),false,new UTF8Encoding(false)))
                {
                    for(int f=0;f<clip.frames;f++)
                    {
                        float t=f/(float)(clip.frames-1);owner.Evaluate(t);owner.SceneCamera.Render();RenderTexture.active=target;
                        pixels.ReadPixels(new Rect(0,0,1920,1080),0,0,false);pixels.Apply(false,false);
                        if(f==0||f==clip.frames-1)
                        {
                            string suffix=f==0?".first.png":".last.png";
                            File.WriteAllBytes(Path.Combine(job.outputDirectory,stem+suffix),pixels.EncodeToPNG());
                        }
                        anchors.WriteLine(JsonUtility.ToJson(owner.State(f,t)));
                        byte[] raw=pixels.GetRawTextureData();encoder.StandardInput.BaseStream.Write(raw,0,raw.Length);
                    }
                }
                encoder.StandardInput.Close();encoder.WaitForExit();File.WriteAllText(Path.Combine(job.outputDirectory,stem+".encode.log"),errors.ToString());
                if(encoder.ExitCode!=0)throw new InvalidOperationException("Own V6 encoder failed: "+errors);
            }
            finally
            {
                if(encoder!=null){if(!encoder.HasExited)encoder.Kill();encoder.Dispose();}
                owner.SceneCamera.targetTexture=null;RenderTexture.active=null;target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(pixels);
            }
        }
        private static void CaptureTestbedStill(Job job,TextAsset catalog)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);EditorUtility.UnloadUnusedAssetsImmediate();
            var owner=new GameObject("Shared neutral V6 testbed still").AddComponent<EulerV6Scene>();owner.shotCatalog=catalog;owner.LoadShot("v6-04.B01");owner.shot.axes=false;owner.shot.activeAxis="none";owner.Build();owner.Evaluate(0);
            var target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.Default){antiAliasing=2};target.Create();
            var pixels=new Texture2D(1920,1080,TextureFormat.RGB24,false,false);owner.SceneCamera.targetTexture=target;
            try{owner.PrimeTextGeometry();owner.SceneCamera.Render();RenderTexture.active=target;pixels.ReadPixels(new Rect(0,0,1920,1080),0,0,false);pixels.Apply(false,false);File.WriteAllBytes(Path.Combine(job.outputDirectory,"testbed-still.png"),pixels.EncodeToPNG());}
            finally{owner.SceneCamera.targetTexture=null;RenderTexture.active=null;target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(pixels);}
        }
        private static void RequireIsolated()
        {
            string p=Path.GetFullPath(Path.Combine(Application.dataPath,"..")).Replace('\\','/');
            if(!Application.isBatchMode||!p.EndsWith("/production/local/revision-v6/unity-capture",StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException("V6 capture/bake requires the task's own isolated project.");
        }
        private static string Argument(string name)
        {var a=Environment.GetCommandLineArgs();for(int i=0;i<a.Length-1;i++)if(a[i]==name)return a[i+1];throw new ArgumentException("Missing "+name);}
        private static string Quote(string s)=>"\""+Path.GetFullPath(s).Replace("\"","")+"\"";
    }
}
