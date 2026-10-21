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

namespace YamyamCoding.GameMath.OrientationMatrix.V8.Editor
{
    public static class OrientationMatrixV8Capture
    {
        public const string Root="Assets/VideoScenes/game-math-orientation-matrix";
        [Serializable]public class Clip {public string shotId;public int frames;public int[] stillFrames;}
        [Serializable]public class Job
        {public string outputDirectory,ffmpegPath;public bool bakeScenes,sampleOnly;public Clip[] clips;public string[] sceneShots;}
        [Serializable]public class ShaderEntry {public string shader;public bool supported;public int compilerErrors,compilerWarnings;}
        [Serializable]public class ShaderAudit {public string shot;public bool afterActualCameraRender=true;public ShaderEntry[] entries;}
        public static void Run()
        {
            RequireIsolated();string path=Argument("-orientationV8Job");Job job=JsonUtility.FromJson<Job>(File.ReadAllText(path));
            Directory.CreateDirectory(job.outputDirectory);
            GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;QualitySettings.antiAliasing=2;
            try
            {
                if(SystemInfo.graphicsDeviceType==GraphicsDeviceType.Null)throw new InvalidOperationException("Actual V8 capture needs graphics device");
                TextAsset catalog=AssetDatabase.LoadAssetAtPath<TextAsset>(Root+"/spatial-shots.json");
                if(catalog==null)throw new InvalidOperationException("V8 catalog not imported");
                ValidateMath();if(job.bakeScenes)Bake(job,catalog);
                foreach(var clip in job.clips)Capture(job,clip,catalog);
                File.WriteAllText(Path.Combine(job.outputDirectory,"capture-success.json"),"{\"editor\":\""+Application.unityVersion+"\",\"pipeline\":\"isolated built-in\",\"handedness\":\"left\",\"vectors\":\"row objectToUpright\",\"width\":1000,\"height\":700,\"fps\":60,\"mathValidated\":true,\"sampleOnly\":"+(job.sampleOnly?"true":"false")+"}");
                EditorApplication.Exit(0);
            }
            catch(Exception ex){UnityEngine.Debug.LogException(ex);File.WriteAllText(Path.Combine(job.outputDirectory,"capture-error.txt"),ex.ToString());EditorApplication.Exit(1);}
        }
        private static void ValidateMath()
        {
            var c=Matrix4x4.Rotate(Quaternion.AngleAxis(90,Vector3.up));
            if((c.MultiplyVector(Vector3.forward)-Vector3.right).sqrMagnitude>1e-9f)throw new InvalidOperationException("Y90 positive convention");
            var p=new Vector3(1,0,2);var q=c.MultiplyVector(p);
            if((q-new Vector3(2,0,-1)).sqrMagnitude>1e-9f||(c.inverse.MultiplyVector(q)-p).sqrMagnitude>1e-9f)throw new InvalidOperationException("Worked point/inverse");
            if((c.MultiplyVector(c.MultiplyVector(Vector3.right))-Vector3.left).sqrMagnitude>1e-9f)throw new InvalidOperationException("Two quarter turns of narrated right unit vector");
        }
        private static OrientationMatrixV8Scene Owner(TextAsset catalog,string id)
        {EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);EditorUtility.UnloadUnusedAssetsImmediate();var x=new GameObject("Yamyam V8 "+id).AddComponent<OrientationMatrixV8Scene>();x.shotCatalog=catalog;x.Load(id);x.Build();return x;}
        private static void Bake(Job job,TextAsset catalog)
        {
            Directory.CreateDirectory(Root+"/Scenes");Directory.CreateDirectory(Root+"/Shared");AssetDatabase.Refresh();
            var saved=new List<string>();
            foreach(string id in job.sceneShots)
            {var owner=Owner(catalog,id);owner.Evaluate(0);Persist(owner);string file=Root+"/Scenes/"+owner.shot.sceneId+".unity";if(!EditorSceneManager.SaveScene(owner.gameObject.scene,file))throw new IOException(file);saved.Add(file);}
            var bed=Owner(catalog,"basis-y90");bed.Evaluate(1);Persist(bed);string test=Root+"/Scenes/testbed.unity";if(!EditorSceneManager.SaveScene(bed.gameObject.scene,test))throw new IOException(test);
            AssetDatabase.SaveAssets();AssetDatabase.Refresh();
            File.WriteAllText(Path.Combine(job.outputDirectory,"scenes-saved.json"),"{\"scriptSceneCount\":"+saved.Count+",\"testbedSaved\":true,\"totalSceneFiles\":"+(saved.Count+1)+",\"editor\":\""+Application.unityVersion+"\",\"saved\":[\""+string.Join("\",\"",saved)+"\"]}");
        }
        private static void Persist(OrientationMatrixV8Scene owner)
        {
            foreach(var filter in owner.GetComponentsInChildren<MeshFilter>(true))
            {
                Mesh mesh=filter.sharedMesh;if(mesh==null||EditorUtility.IsPersistent(mesh))continue;
                var b=new StringBuilder(mesh.name);foreach(var v in mesh.vertices)b.Append(v.x.ToString("R",CultureInfo.InvariantCulture)).Append(',').Append(v.y.ToString("R",CultureInfo.InvariantCulture)).Append(',').Append(v.z.ToString("R",CultureInfo.InvariantCulture)).Append(';');foreach(int i in mesh.triangles)b.Append(i).Append(',');
                string path=Root+"/Shared/mesh-"+Hash(b.ToString())+".asset";Mesh saved=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(saved==null){saved=UnityEngine.Object.Instantiate(mesh);AssetDatabase.CreateAsset(saved,path);}filter.sharedMesh=saved;
            }
            foreach(var renderer in owner.GetComponentsInChildren<Renderer>(true))
            {
                Material mat=renderer.sharedMaterial;if(mat==null||EditorUtility.IsPersistent(mat)||mat.mainTexture!=null)continue;
                string key=mat.shader.name+ColorUtility.ToHtmlStringRGBA(mat.color)+"-queue"+mat.renderQueue;string path=Root+"/Shared/material-"+Hash(key)+".mat";Material saved=AssetDatabase.LoadAssetAtPath<Material>(path);if(saved==null){saved=UnityEngine.Object.Instantiate(mat);AssetDatabase.CreateAsset(saved,path);}renderer.sharedMaterial=saved;
            }
        }
        private static string Hash(string text)
        {using(var sha=SHA256.Create())return BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(text))).Replace("-","").ToLowerInvariant().Substring(0,20);}
        private static void Capture(Job job,Clip clip,TextAsset catalog)
        {
            if(clip.frames<2||clip.frames>1801)throw new ArgumentException("Finite V8 clip requires2..1801frames");
            var owner=Owner(catalog,clip.shotId);
            const int w=OrientationMatrixV8Scene.Width,h=OrientationMatrixV8Scene.Height;
            var target=new RenderTexture(w,h,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.Default){antiAliasing=2};target.Create();
            var pixels=new Texture2D(w,h,TextureFormat.RGB24,false,false);owner.SceneCamera.targetTexture=target;
            string stem=clip.shotId;var errors=new StringBuilder();Process encoder=null;
            try
            {
                var info=new ProcessStartInfo(job.ffmpegPath){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardError=true,CreateNoWindow=true,
                    Arguments="-hide_banner -loglevel warning -n -f rawvideo -pixel_format rgb24 -video_size 1000x700 -framerate 60 -i pipe:0 -vf vflip -an -c:v libx264 -threads 2 -preset fast -crf 16 -pix_fmt yuv420p -movflags +faststart "+Quote(Path.Combine(job.outputDirectory,stem+".mp4"))};
                encoder=new Process{StartInfo=info};encoder.ErrorDataReceived+=(_,e)=>{if(e.Data!=null)lock(errors)errors.AppendLine(e.Data);};encoder.Start();encoder.BeginErrorReadLine();
                using(var anchors=new StreamWriter(Path.Combine(job.outputDirectory,stem+".anchors.ndjson"),false,new UTF8Encoding(false)))
                {
                    for(int f=0;f<clip.frames;f++)
                    {
                        float t=f/(float)(clip.frames-1);owner.Evaluate(t);owner.SceneCamera.Render();RenderTexture.active=target;
                        pixels.ReadPixels(new Rect(0,0,w,h),0,0,false);pixels.Apply(false,false);
                        if(f==0||f==clip.frames/2||f==clip.frames-1)
                        {string suffix=f==0?".first.png":f==clip.frames-1?".last.png":".middle.png";File.WriteAllBytes(Path.Combine(job.outputDirectory,stem+suffix),pixels.EncodeToPNG());}
                        if(clip.stillFrames!=null&&Array.IndexOf(clip.stillFrames,f)>=0)
                            File.WriteAllBytes(Path.Combine(job.outputDirectory,stem+".frame-"+f.ToString("0000")+".png"),pixels.EncodeToPNG());
                        anchors.WriteLine(JsonUtility.ToJson(owner.State(f,t)));byte[] raw=pixels.GetRawTextureData();encoder.StandardInput.BaseStream.Write(raw,0,raw.Length);
                    }
                }
                encoder.StandardInput.Close();encoder.WaitForExit();File.WriteAllText(Path.Combine(job.outputDirectory,stem+".encode.log"),errors.ToString());
                if(encoder.ExitCode!=0)throw new InvalidOperationException(errors.ToString());
                AuditShaders(owner,job.outputDirectory,stem);
            }
            finally
            {if(encoder!=null){if(!encoder.HasExited)encoder.Kill();encoder.Dispose();}owner.SceneCamera.targetTexture=null;RenderTexture.active=null;target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(pixels);}
        }
        private static void AuditShaders(OrientationMatrixV8Scene owner,string output,string stem)
        {
            var entries=new List<ShaderEntry>();var seen=new HashSet<Shader>();
            foreach(var r in owner.GetComponentsInChildren<Renderer>(true))foreach(var m in r.sharedMaterials)
            {
                if(m==null||m.shader==null)throw new InvalidOperationException("Missing actual model material/shader");
                Shader s=m.shader;if(!seen.Add(s))continue;var e=new ShaderEntry{shader=s.name,supported=s.isSupported};
                foreach(var msg in ShaderUtil.GetShaderMessages(s))
                {if(msg.severity.ToString().Equals("Error",StringComparison.OrdinalIgnoreCase))e.compilerErrors++;else if(msg.severity.ToString().Equals("Warning",StringComparison.OrdinalIgnoreCase))e.compilerWarnings++;}
                entries.Add(e);
                if(!e.supported||e.compilerErrors!=0||(s.name!="Standard"&&s.name!="Unlit/Color"&&s.name!="Yamyam/DiagramGuideOverlay"))throw new InvalidOperationException("Unexpected/unsupported actual isolated capture shader "+s.name);
            }
            File.WriteAllText(Path.Combine(output,stem+".shaders.json"),JsonUtility.ToJson(new ShaderAudit{shot=stem,entries=entries.ToArray()},true));
        }
        private static void RequireIsolated()
        {string p=Path.GetFullPath(Path.Combine(Application.dataPath,"..")).Replace('\\','/');if(!Application.isBatchMode||!p.EndsWith("/production/local/revision-v6/unity-capture",StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException("Only task-owned isolated capture project is allowed");}
        private static string Argument(string name)
        {var a=Environment.GetCommandLineArgs();for(int i=0;i<a.Length-1;i++)if(a[i]==name)return a[i+1];throw new ArgumentException("Missing "+name);}
        private static string Quote(string s)=>"\""+Path.GetFullPath(s).Replace("\"","")+"\"";
    }
}
