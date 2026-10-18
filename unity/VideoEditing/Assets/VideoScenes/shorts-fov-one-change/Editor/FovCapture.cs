using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace YamyamCoding.Shorts.FovOneChange.Editor
{
    /// <summary>Explicit finite capture in this Short's disposable built-in project.</summary>
    public static class FovCapture
    {
        public const string Root = "Assets/VideoScenes/shorts-fov-one-change";
        public const string ScenePath = Root+"/Scenes/FovOneChange.unity";
        [Serializable] public class Job { public string outputDirectory; public string mode; public int samples; }
        [Serializable] public class Vec { public float x,y,z; public Vec(Vector3 p) { x=p.x;y=p.y;z=p.z; } }
        [Serializable] public class Pixel { public float x,y; }
        [Serializable] public class PixelBounds { public float x,y,width,height; }
        [Serializable] public class ViewportBounds { public float xMin,yMin,xMax,yMax; }
        [Serializable] public class WorldBounds { public Vec center,size; }
        [Serializable] public class CarProjection
        {
            public string id; public WorldBounds worldBounds; public PixelBounds pixelTopLeftBounds;
            public ViewportBounds viewportBounds; public Pixel anchorPixelTopLeft;
            public bool intersectsViewport,fullyInsideViewport; public bool occlusionMeasured=false;
        }
        [Serializable] public class Frame
        {
            public int index; public float normalized,horizontalFovDegrees,verticalFovDegrees;
            public Vec cameraPosition,cameraRotationEuler; public bool cameraTransformUnchanged;
            public string transformSignature; public CarProjection[] cars;
        }
        [Serializable] public class Projection
        {
            public string schema="unity-actual-camera-projection-v1", renderer="Unity built-in", editorVersion;
            public int width=1920,height=1080; public float aspect=16f/9f;
            public string pixelOrigin="top-left", mode, projectionKind="WorldToViewportPoint of actual MeshRenderer world bounds; editorial annotation anchors, not image detection";
            public string changingParameter="horizontalFovDegrees only", scenePath=ScenePath;
            public bool allTransformsUnchanged; public Frame[] frames;
        }

        public static void Run()
        {
            RequireOwnIsolatedProject();
            string jobPath=Argument("-fovJob");
            if (string.IsNullOrWhiteSpace(jobPath)) throw new ArgumentException("Missing -fovJob.");
            Job job=JsonUtility.FromJson<Job>(File.ReadAllText(jobPath));
            if (job==null || (job.samples!=2 && job.samples!=61)) throw new ArgumentException("Only2 endpoint samples or61 frames are permitted.");
            string expected=Path.GetFullPath(Path.Combine(Application.dataPath,"../output",job.samples==2?"preview":"capture"));
            if (!string.Equals(Path.GetFullPath(job.outputDirectory),expected,StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("Output must stay inside this isolated project's own output mode directory.");
            Directory.CreateDirectory(job.outputDirectory);
            try
            {
                EditorSettings.serializationMode=SerializationMode.ForceText;
                GraphicsSettings.defaultRenderPipeline=null; QualitySettings.renderPipeline=null;
                PlayerSettings.colorSpace=ColorSpace.Linear;
                QualitySettings.antiAliasing=4; QualitySettings.shadows=ShadowQuality.All;
                QualitySettings.shadowResolution=ShadowResolution.High; QualitySettings.shadowDistance=55;
                EditorSceneManager.OpenScene(ScenePath,OpenSceneMode.Single);
                FovDemoScene scene=UnityEngine.Object.FindAnyObjectByType<FovDemoScene>();
                if(scene==null)throw new InvalidOperationException("Owned editable source scene has no FovDemoScene component.");
                scene.BuildWorld(); PersistAssets(scene); scene.SetHorizontalFov(60);
                if(!EditorSceneManager.SaveScene(scene.gameObject.scene,ScenePath))throw new IOException("Scene save failed.");
                AssetDatabase.SaveAssets();
                Capture(scene,job);
                EditorApplication.Exit(0);
            }
            catch(Exception error)
            {
                Debug.LogException(error); File.WriteAllText(Path.Combine(job.outputDirectory,"capture-error.txt"),error.ToString()); EditorApplication.Exit(1);
            }
        }

        private static void Capture(FovDemoScene scene,Job job)
        {
            string baseline=scene.TransformSignature(); var frames=new List<Frame>();
            var target=new RenderTexture(1920,1080,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.Default) { antiAliasing=4, name="Actual fixed-camera FOV comparison" };
            target.Create(); var pixels=new Texture2D(1920,1080,TextureFormat.RGB24,false,false);
            scene.sceneCamera.targetTexture=target;
            try
            {
                int[] indices=job.samples==2?new[]{0,60}:Sequential61();
                foreach(int index in indices)
                {
                    float normalized=index/60f,horizontal=60f+40f*normalized;
                    scene.SetHorizontalFov(horizontal);
                    string signature=scene.TransformSignature();
                    if(signature!=baseline)throw new InvalidOperationException("A camera/object transform changed. Only FOV may vary.");
                    scene.sceneCamera.Render(); RenderTexture.active=target;
                    pixels.ReadPixels(new Rect(0,0,1920,1080),0,0,false);pixels.Apply(false,false);
                    string png=Path.Combine(job.outputDirectory,"frame-"+index.ToString("D3")+".png");
                    if(File.Exists(png))throw new IOException("Existing successful frame must not be overwritten: "+png);
                    File.WriteAllBytes(png,pixels.EncodeToPNG());
                    frames.Add(new Frame { index=index,normalized=normalized,horizontalFovDegrees=horizontal,verticalFovDegrees=scene.sceneCamera.fieldOfView,
                        cameraPosition=new Vec(scene.sceneCamera.transform.position),cameraRotationEuler=new Vec(scene.sceneCamera.transform.eulerAngles),
                        cameraTransformUnchanged=true,transformSignature=signature,
                        cars=new[]{ProjectCar(scene.sceneCamera,"center",scene.centerCar),ProjectCar(scene.sceneCamera,"left",scene.leftCar),ProjectCar(scene.sceneCamera,"right",scene.rightCar)} });
                }
                Frame first=frames[0],last=frames[frames.Count-1];
                if(!first.cars[0].fullyInsideViewport || !last.cars[0].fullyInsideViewport)
                    throw new InvalidOperationException("The center car must remain fully inside both endpoint viewports.");
                if(first.cars[1].intersectsViewport || first.cars[2].intersectsViewport || !last.cars[1].fullyInsideViewport || !last.cars[2].fullyInsideViewport)
                    throw new InvalidOperationException("Side cars must be fully outside60deg and fully inside100deg. Inspect actual projection before accepting this capture.");
                var projection=new Projection { editorVersion=Application.unityVersion,mode=job.samples==2?"preview":"capture",allTransformsUnchanged=true,frames=frames.ToArray() };
                File.WriteAllText(Path.Combine(job.outputDirectory,"capture-projection.json"),JsonUtility.ToJson(projection,true),new UTF8Encoding(false));
                scene.SetHorizontalFov(60);scene.sceneCamera.targetTexture=null;
                EditorSceneManager.SaveScene(scene.gameObject.scene,ScenePath);
                File.WriteAllText(Path.Combine(job.outputDirectory,"capture-success.json"),"{\"frames\":"+frames.Count+",\"width\":1920,\"height\":1080,\"horizontalFovStart\":60,\"horizontalFovEnd\":100,\"allTransformsUnchanged\":true,\"editor\":\""+Application.unityVersion+"\"}");
            }
            finally
            {
                scene.sceneCamera.targetTexture=null; RenderTexture.active=null;target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(pixels);
            }
        }

        private static CarProjection ProjectCar(Camera camera,string id,Transform root)
        {
            Renderer[] renderers=root.GetComponentsInChildren<Renderer>();if(renderers.Length==0)throw new InvalidOperationException("No car renderers.");
            Bounds bounds=renderers[0].bounds;for(int i=1;i<renderers.Length;i++)bounds.Encapsulate(renderers[i].bounds);
            float minX=float.PositiveInfinity,maxX=float.NegativeInfinity,minY=float.PositiveInfinity,maxY=float.NegativeInfinity;
            foreach(int x in new[]{-1,1})foreach(int y in new[]{-1,1})foreach(int z in new[]{-1,1})
            {
                Vector3 point=camera.WorldToViewportPoint(bounds.center+Vector3.Scale(bounds.extents,new Vector3(x,y,z)));
                if(point.z<=camera.nearClipPlane)throw new InvalidOperationException("A car crosses the camera near plane.");
                minX=Mathf.Min(minX,point.x);maxX=Mathf.Max(maxX,point.x);minY=Mathf.Min(minY,point.y);maxY=Mathf.Max(maxY,point.y);
            }
            Vector3 center=camera.WorldToViewportPoint(bounds.center);
            return new CarProjection { id=id,worldBounds=new WorldBounds{center=new Vec(bounds.center),size=new Vec(bounds.size)},
                viewportBounds=new ViewportBounds{xMin=minX,yMin=minY,xMax=maxX,yMax=maxY},
                pixelTopLeftBounds=new PixelBounds{x=minX*1920,y=(1-maxY)*1080,width=(maxX-minX)*1920,height=(maxY-minY)*1080},
                anchorPixelTopLeft=new Pixel{x=center.x*1920,y=(1-center.y)*1080},
                intersectsViewport=maxX>0 && minX<1 && maxY>0 && minY<1,
                fullyInsideViewport=minX>=0 && maxX<=1 && minY>=0 && maxY<=1 };
        }

        private static void PersistAssets(FovDemoScene scene)
        {
            string folder=Root+"/Baked";Directory.CreateDirectory(folder);AssetDatabase.Refresh();
            var meshes=new Dictionary<Mesh,Mesh>();var materials=new Dictionary<Material,Material>();int meshIndex=0,materialIndex=0;
            foreach(MeshFilter filter in scene.GetComponentsInChildren<MeshFilter>(true))
            {
                Mesh value=filter.sharedMesh;if(value==null || EditorUtility.IsPersistent(value))continue;
                if(!meshes.TryGetValue(value,out Mesh saved))
                {
                    string path=folder+"/mesh-"+(meshIndex++).ToString("D3")+".asset";saved=AssetDatabase.LoadAssetAtPath<Mesh>(path);
                    if(saved==null){saved=UnityEngine.Object.Instantiate(value);AssetDatabase.CreateAsset(saved,path);}else{EditorUtility.CopySerialized(value,saved);EditorUtility.SetDirty(saved);}
                    meshes.Add(value,saved);
                }
                filter.sharedMesh=saved;
            }
            foreach(Renderer item in scene.GetComponentsInChildren<Renderer>(true))
            {
                Material value=item.sharedMaterial;if(value==null || EditorUtility.IsPersistent(value))continue;
                if(!materials.TryGetValue(value,out Material saved))
                {
                    string path=folder+"/material-"+(materialIndex++).ToString("D3")+".mat";saved=AssetDatabase.LoadAssetAtPath<Material>(path);
                    if(saved==null){saved=UnityEngine.Object.Instantiate(value);AssetDatabase.CreateAsset(saved,path);}else{EditorUtility.CopySerialized(value,saved);EditorUtility.SetDirty(saved);}
                    materials.Add(value,saved);
                }
                item.sharedMaterial=saved;
            }
        }
        private static int[] Sequential61(){var result=new int[61];for(int i=0;i<61;i++)result[i]=i;return result;}
        private static string Argument(string key){string[] args=Environment.GetCommandLineArgs();for(int i=0;i<args.Length-1;i++)if(args[i]==key)return args[i+1];return null;}
        private static void RequireOwnIsolatedProject()
        {
            string path=Path.GetFullPath(Application.dataPath).Replace('\\','/');
            if(!Application.isBatchMode || !path.EndsWith("/projects/shorts-fov-one-change/production/local/unity-capture/Assets",StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Capture runs only in this Short's isolated batch project. The user's editor is never modified.");
        }
    }
}
