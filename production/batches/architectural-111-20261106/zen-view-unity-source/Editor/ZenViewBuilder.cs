using System;
using System.IO;
using System.Text;
using System.Globalization;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Yamyam.Architectural111.ZenView.Editor {
    public static class ZenViewBuilder {
        const string Folder="Assets/VideoScenes/architectural-111-20261106/07-04";
        [Serializable] sealed class ModeReceipt {public string fingerprint,mode;public int frames,width,height,fps;public string[] cameras={"player","observer"};}
        [Serializable] sealed class Snapshot {public ZenViewConfig contract;public string mode;public float openingWidth;public string observerCutaway="Only lintel render layer hidden for overhead observer; full physical walls and player occlusion retained";}
        [Serializable] sealed class ExportFile {public string path,sha256;public long bytes;}
        [Serializable] sealed class SceneRecord {public string fingerprint;public bool actualSceneFilesSaved=true;public string[] scenePaths;public ExportFile[] files,sharedDependencies;}
        static ZenViewConfig Config(){return JsonUtility.FromJson<ZenViewConfig>(File.ReadAllText(Folder+"/capture-config.json"));}
        static Material Mat(string name,Color color) {
            string path=Folder+"/"+name+".mat";var mat=AssetDatabase.LoadAssetAtPath<Material>(path);var shader=Shader.Find("Yamyam/ZenViewSurface");
            if(!shader)throw new InvalidOperationException("Missing ZenViewSurface shader");
            if(!mat){mat=new Material(shader);AssetDatabase.CreateAsset(mat,path);}mat.shader=shader;mat.color=color;return mat;
        }
        static GameObject Shape(string name,PrimitiveType type,Vector3 position,Vector3 scale,Material mat) {
            var go=GameObject.CreatePrimitive(type);go.name=name;go.transform.position=position;go.transform.localScale=scale;
            go.GetComponent<Renderer>().sharedMaterial=mat;UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());return go;
        }
        // Closed convex hexahedron; slanted inner faces are real render/collision geometry.
        static GameObject Prism(string name,float lf,float rf,float lb,float rb,float bottom,float top,ZenViewConfig c,Material mat,string mode,int layer) {
            var vertices=new[]{new Vector3(lf,bottom,c.frontZ),new Vector3(rf,bottom,c.frontZ),new Vector3(rf,top,c.frontZ),new Vector3(lf,top,c.frontZ),
                new Vector3(lb,bottom,c.backZ),new Vector3(rb,bottom,c.backZ),new Vector3(rb,top,c.backZ),new Vector3(lb,top,c.backZ)};
            int[] triangles={0,2,1,0,3,2,4,5,6,4,6,7,0,4,7,0,7,3,1,2,6,1,6,5,0,1,5,0,5,4,3,7,6,3,6,2};
            string path=Folder+"/"+mode+"-"+name+".asset";var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if(!mesh){mesh=new Mesh();AssetDatabase.CreateAsset(mesh,path);}mesh.Clear();mesh.name=name;mesh.vertices=vertices;mesh.triangles=triangles;mesh.RecalculateNormals();mesh.RecalculateBounds();
            var go=new GameObject(name);go.layer=layer;go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=mat;
            go.AddComponent<MeshCollider>().sharedMesh=mesh;EditorUtility.SetDirty(mesh);return go;
        }
        static LineRenderer Guide(string name,Color color,float width=.065f) {
            var go=new GameObject(name);go.layer=ZenViewExperiment.GuideLayer;var line=go.AddComponent<LineRenderer>();
            string path=Folder+"/Guide lines.mat";var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(!mat){mat=new Material(Shader.Find("Sprites/Default"));AssetDatabase.CreateAsset(mat,path);}
            line.sharedMaterial=mat;line.startColor=line.endColor=color;
            line.startWidth=line.endWidth=width;line.numCapVertices=6;return line;
        }
        static void LayerRecursive(Transform root,int layer){root.gameObject.layer=layer;foreach(Transform child in root)LayerRecursive(child,layer);}
        static void Island(ZenViewConfig c) {
            var rock=Mat("Fixed island rock",new Color(.33f,.37f,.32f));var sand=Mat("Fixed sand",new Color(.73f,.65f,.41f));
            var grass=Mat("Fixed island green",new Color(.22f,.40f,.25f));
            Shape("Fixed island base",PrimitiveType.Sphere,new Vector3(c.targetX,.12f,c.targetZ),new Vector3(3.7f,.65f,2.7f),rock);
            Shape("Fixed shore",PrimitiveType.Cylinder,new Vector3(c.targetX,.18f,c.targetZ),new Vector3(3.25f,.10f,2.35f),sand);
            Shape("Fixed green island",PrimitiveType.Cylinder,new Vector3(c.targetX,.30f,c.targetZ),new Vector3(2.85f,.12f,1.95f),grass);
            var white=Mat("Lighthouse ivory",new Color(.87f,.87f,.77f));var red=Mat("Lighthouse red",new Color(.69f,.23f,.18f));
            Shape("Fixed lighthouse tower",PrimitiveType.Cylinder,new Vector3(c.targetX,1.55f,c.targetZ),new Vector3(.49f,1.25f,.49f),white);
            Shape("Fixed lighthouse stripe",PrimitiveType.Cylinder,new Vector3(c.targetX,1.65f,c.targetZ),new Vector3(.51f,.23f,.51f),red);
            Shape("Fixed lighthouse lantern",PrimitiveType.Cylinder,new Vector3(c.targetX,2.91f,c.targetZ),new Vector3(.63f,.12f,.63f),white);
            Shape("Fixed lighthouse cap",PrimitiveType.Sphere,new Vector3(c.targetX,3.10f,c.targetZ),new Vector3(.75f,.25f,.75f),red);
        }
        public static ZenViewExperiment Build(string mode) {
            Directory.CreateDirectory(Folder);AssetDatabase.Refresh();var c=Config();
            if(mode!="narrow"&&mode!="wide")throw new ArgumentException("Unknown Zen View mode");
            float width=mode=="narrow"?c.narrowWidth:c.wideWidth,half=width*.5f;
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.4f,.43f,.45f);
            var rig=new GameObject("Zen View — original width-only visibility experiment").AddComponent<ZenViewExperiment>();rig.config=c;rig.openingWidth=width;
            var stone=Mat("Same opaque stone wall",new Color(.34f,.37f,.36f));var ground=Mat("Same path",new Color(.18f,.23f,.21f));
            var sea=Mat("Fixed ocean illustration",new Color(.12f,.43f,.62f));
            Shape("Fixed walking ground",PrimitiveType.Cube,new Vector3(0,-.12f,-2.4f),new Vector3(23,.2f,5.2f),ground);
            Shape("Fixed ocean surface",PrimitiveType.Cube,new Vector3(6,-.25f,12),new Vector3(44,.2f,21),sea);Island(c);
            Prism("left-wall",c.wallLeftX,c.frontCenterX-half,c.wallLeftX,c.backCenterX-half,0,c.wallHeight,c,stone,mode,ZenViewExperiment.WallLayer);
            Prism("right-wall",c.frontCenterX+half,c.wallRightX,c.backCenterX+half,c.wallRightX,0,c.wallHeight,c,stone,mode,ZenViewExperiment.WallLayer);
            Prism("sill",c.frontCenterX-half,c.frontCenterX+half,c.backCenterX-half,c.backCenterX+half,0,c.openingBottom,c,stone,mode,ZenViewExperiment.WallLayer);
            Prism("lintel",c.frontCenterX-half,c.frontCenterX+half,c.backCenterX-half,c.backCenterX+half,c.openingTop,c.wallHeight,c,stone,mode,ZenViewExperiment.LintelLayer);
            rig.actor=new GameObject("Same articulated CC0 Knight on fixed lateral path").transform;rig.actor.rotation=Quaternion.Euler(0,90,0);
            string fbx="Assets/ThirdParty/KayKitAdventurers/Knight.fbx";var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(fbx);
            if(!prefab)throw new InvalidOperationException("Missing provenance-bound Knight FBX");
            var model=UnityEngine.Object.Instantiate(prefab,rig.actor);model.name="KayKit articulated Knight — CC0";rig.actorModel=model.transform;
            var renderers=model.GetComponentsInChildren<Renderer>();if(renderers.Length==0)throw new InvalidOperationException("Knight has no actual renderers");
            Bounds bounds=renderers[0].bounds;foreach(var r in renderers)bounds.Encapsulate(r.bounds);model.transform.localScale=Vector3.one*(1.72f/bounds.size.y);
            bounds=renderers[0].bounds;foreach(var r in renderers)bounds.Encapsulate(r.bounds);
            model.transform.position-=new Vector3(bounds.center.x,bounds.min.y,bounds.center.z);
            var skin=Mat("Knight texture",Color.white);skin.mainTexture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/ThirdParty/KayKitAdventurers/knight_texture.png");
            foreach(var r in renderers)r.sharedMaterial=skin;LayerRecursive(rig.actor,ZenViewExperiment.ActorLayer);
            rig.modelBasePosition=model.transform.localPosition;rig.modelBaseScale=model.transform.localScale;rig.modelBaseRotation=model.transform.localRotation;
            foreach(var asset in AssetDatabase.LoadAllAssetsAtPath(fbx)){var clip=asset as AnimationClip;if(clip&&clip.name.EndsWith("Walking_A",StringComparison.OrdinalIgnoreCase))rig.walkingClip=clip;}
            if(!rig.walkingClip)throw new InvalidOperationException("Original Walking_A clip is required");
            rig.playerCamera=new GameObject("Player eye — normal opaque wall occlusion").AddComponent<Camera>();rig.playerCamera.fieldOfView=c.verticalFieldOfView;
            rig.playerCamera.aspect=c.width/(float)c.height;rig.playerCamera.nearClipPlane=.04f;rig.playerCamera.farClipPlane=100;
            rig.playerCamera.clearFlags=CameraClearFlags.SolidColor;rig.playerCamera.backgroundColor=new Color(.52f,.66f,.71f);
            rig.playerCamera.cullingMask=~((1<<ZenViewExperiment.GuideLayer)|(1<<ZenViewExperiment.ActorLayer));
            rig.observerCamera=new GameObject("Observer overhead — synchronized cutaway and actual raycasts").AddComponent<Camera>();
            rig.observerCamera.transform.position=new Vector3(c.observerX,c.observerY,c.observerZ);rig.observerCamera.transform.rotation=Quaternion.Euler(90,0,0);
            rig.observerCamera.orthographic=true;rig.observerCamera.orthographicSize=c.observerOrthographicSize;rig.observerCamera.aspect=c.width/(float)c.height;
            rig.observerCamera.nearClipPlane=.04f;rig.observerCamera.farClipPlane=100;rig.observerCamera.clearFlags=CameraClearFlags.SolidColor;
            rig.observerCamera.backgroundColor=new Color(.018f,.025f,.023f);rig.observerCamera.cullingMask=~(1<<ZenViewExperiment.LintelLayer);
            rig.playerCamera.enabled=false;rig.observerCamera.enabled=false;
            rig.sightLines=new LineRenderer[7];for(int i=0;i<7;i++)rig.sightLines[i]=Guide("Actual clipped sight ray "+i,Color.white,i==0?.10f:.055f);
            rig.frontOpening=Guide("Actual front opening edges",new Color(.25f,.75f,1));rig.backOpening=Guide("Actual back opening edges",new Color(1,.82f,.32f));
            Physics.SyncTransforms();rig.SetFrame(0);return rig;
        }
        [MenuItem("Yamyam/Architectural 111/Build Zen View scenes")]
        public static void BuildScenes() {
            Build("narrow");if(!EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),Folder+"/S02-ZenView-Narrow.unity"))throw new InvalidOperationException("Narrow editable scene save failed");
            Build("wide");if(!EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),Folder+"/S03-ZenView-Wide.unity"))throw new InvalidOperationException("Wide editable scene save failed");AssetDatabase.SaveAssets();
        }
        static ExportFile FileRecord(string path) {
            byte[] data=File.ReadAllBytes(path);string hash;
            using(var digest=SHA256.Create())hash=BitConverter.ToString(digest.ComputeHash(data)).Replace("-","").ToLowerInvariant();
            return new ExportFile{path=path.Replace('\\','/'),sha256=hash,bytes=data.LongLength};
        }
        static void ExportRecord(string output,string fingerprint) {
            AssetDatabase.SaveAssets();AssetDatabase.Refresh();
            var files=new System.Collections.Generic.List<ExportFile>();
            foreach(string path in Directory.GetFiles(Folder,"*",SearchOption.AllDirectories))files.Add(FileRecord(path));
            if(File.Exists(Folder+".meta"))files.Add(FileRecord(Folder+".meta"));
            files.Sort((a,b)=>String.CompareOrdinal(a.path,b.path));
            var shared=new System.Collections.Generic.List<ExportFile>();
            foreach(string name in new[]{"Knight.fbx","Knight.fbx.meta","knight_texture.png","knight_texture.png.meta","LICENSE.txt","LICENSE.txt.meta","provenance.json"}) {
                string path="Assets/ThirdParty/KayKitAdventurers/"+name;if(File.Exists(path))shared.Add(FileRecord(path));
            }
            var record=new SceneRecord{fingerprint=fingerprint,files=files.ToArray(),sharedDependencies=shared.ToArray(),
                scenePaths=new[]{Folder+"/S02-ZenView-Narrow.unity",Folder+"/S03-ZenView-Wide.unity"}};
            string target=Path.Combine(output,"scene-record.json");if(File.Exists(target))throw new InvalidOperationException("Preserve prior scene export proof");
            File.WriteAllText(target,JsonUtility.ToJson(record,true));
        }
        public static void Capture() {
            string output=null,fingerprint=null,modes="narrow,wide";var args=Environment.GetCommandLineArgs();
            for(int i=0;i<args.Length-1;i++){if(args[i]=="-zenViewOutput")output=args[i+1];if(args[i]=="-zenViewFingerprint")fingerprint=args[i+1];if(args[i]=="-zenViewModes")modes=args[i+1];}
            if(string.IsNullOrEmpty(output)||string.IsNullOrEmpty(fingerprint)||fingerprint.Length!=64)throw new ArgumentException("Explicit empty output and64hex input fingerprint required");
            var requested=modes.Split(',');foreach(var mode in requested)if(mode!="narrow"&&mode!="wide")throw new ArgumentException("Unknown capture mode");
            Directory.CreateDirectory(output);BuildScenes();
            foreach(var mode in requested) {
                string dir=Path.Combine(output,mode);if(Directory.Exists(dir)&&Directory.GetFiles(dir,"*",SearchOption.AllDirectories).Length>0)throw new InvalidOperationException("Preserve prior mode output");
                var rig=Build(mode);var c=rig.config;Directory.CreateDirectory(dir);
                File.WriteAllText(Path.Combine(dir,"capture-config.json"),JsonUtility.ToJson(new Snapshot{contract=c,mode=mode,openingWidth=rig.openingWidth},true));
                var target=new RenderTexture(c.width,c.height,24);target.antiAliasing=2;target.Create();var tex=new Texture2D(c.width,c.height,TextureFormat.RGB24,false);
                var trace=new StringBuilder("frame,timeSeconds,openingWidth,eyeX,eyeY,eyeZ,centerInFrustum,centerBlocked,centerVisible,sampleVisibleCount,sampleCount\n");
                using(var rays=new StreamWriter(Path.Combine(dir,"rays.jsonl")))using(var anchors=new StreamWriter(Path.Combine(dir,"projected-anchors.jsonl"))) {
                    for(int frame=0;frame<c.frames;frame++) {
                        rig.SetFrame(frame);var r=rig.CurrentRays[0];Vector3 p=rig.Eye;
                        trace.AppendLine(string.Join(",",frame,(frame/(float)c.fps).ToString("R",CultureInfo.InvariantCulture),rig.openingWidth.ToString("R",CultureInfo.InvariantCulture),p.x.ToString("R",CultureInfo.InvariantCulture),p.y.ToString("R",CultureInfo.InvariantCulture),p.z.ToString("R",CultureInfo.InvariantCulture),r.inFrustum?"1":"0",r.blocked?"1":"0",r.visible?"1":"0",rig.VisibleSampleCount,rig.SampleCount));
                        rays.WriteLine(JsonUtility.ToJson(new ZenFrameRays{frame=frame,rays=rig.CurrentRays}));anchors.WriteLine(JsonUtility.ToJson(rig.ProjectedAnchors()));
                        foreach(var pair in new[]{Tuple.Create("player",rig.playerCamera),Tuple.Create("observer",rig.observerCamera)}) {
                            var camera=pair.Item2;camera.targetTexture=target;camera.Render();RenderTexture.active=target;tex.ReadPixels(new Rect(0,0,c.width,c.height),0,0);tex.Apply();
                            string folder=Path.Combine(dir,pair.Item1);Directory.CreateDirectory(folder);File.WriteAllBytes(Path.Combine(folder,frame.ToString("D4")+".jpg"),tex.EncodeToJPG(93));
                        }
                    }
                }
                File.WriteAllText(Path.Combine(dir,"trace.csv"),trace.ToString());
                rig.playerCamera.targetTexture=null;rig.observerCamera.targetTexture=null;RenderTexture.active=null;target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(tex);
                string receipt=Path.Combine(dir,"mode-complete.json");File.WriteAllText(receipt+".tmp",JsonUtility.ToJson(new ModeReceipt{fingerprint=fingerprint,mode=mode,frames=c.frames,width=c.width,height=c.height,fps=c.fps},true));File.Move(receipt+".tmp",receipt);
            }
            ExportRecord(output,fingerprint);EditorApplication.Exit(0);
        }
    }
}
