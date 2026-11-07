using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Yamyam.Architectural111.SolutionPathV4.Editor {
    public static class EditorBuilder {
        public const string Folder="Assets/VideoScenes/architectural-111-20261106/11-05-SolutionPathV4";
        const string Knight="Assets/ThirdParty/KayKitAdventurers/Knight.fbx",ShaderPath="Assets/VideoScenes/architectural-111-20261106/ArchitecturalSurface.shader";
        static List<Anchor> anchors;static Material floor,stone,wood,green,red,yellow,blue,guide;
        [Serializable] public sealed class Pin {public string path,sha256,snapshotFile;public long bytes;}
        [Serializable] public sealed class ModeRecord {public string fingerprint,mode,sourceKind="our-own-implementation",configSHA256,graphSHA256,scenePath,frameConvention="capture0=initial; command f produces capture f+1";public int frames,fps,width,height;public bool actualSceneSaved;public string[] cameras={"player","observer"};}
        [Serializable] public sealed class SceneRecord {public string fingerprint,mode,unityVersion,sourceKind="our-own-implementation",animationClipCatalogFile="animation-clip-catalog.json",animationClipCatalogSHA256,warmupFile="warmup.json",warmupSHA256;public bool actualSceneFilesSaved;public string[] scenePaths,animationClips;public Pin[] files,dependencies;}
        static string Sha(byte[] b){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
        static string Canonical(string p){return p.Replace('\\','/');}
        static Pin Snapshot(string path,string output){
            path=Canonical(path);byte[] b=File.ReadAllBytes(path);string name="editable/"+Sha(Encoding.UTF8.GetBytes(path))+".bin";Directory.CreateDirectory(Path.Combine(output,"editable"));string dest=Path.Combine(output,name);if(File.Exists(dest))throw new InvalidOperationException("Duplicate editable snapshot");File.WriteAllBytes(dest,b);return new Pin{path=path,sha256=Sha(b),bytes=b.Length,snapshotFile=name};
        }
        static Config Configuration(){
            var c=JsonUtility.FromJson<Config>(File.ReadAllText(Folder+"/config.json"));if(c.fps!=60||c.width!=1920||c.height!=1080||c.frames!=3120||c.walkSpeed!=1.5f||c.themeStartFrame!=3000||c.themeBlendFrames!=80||c.modes.Length!=8)throw new InvalidOperationException("Exact finite own generator config required");
            if(c.animationDiagnosticFrames==null||c.animationDiagnosticFrames.Length!=15)throw new InvalidOperationException("Exactly15 finite diagnostic frames required");
            for(int i=0;i<c.animationDiagnosticFrames.Length;i++)if(c.animationDiagnosticFrames[i]<0||c.animationDiagnosticFrames[i]>=c.frames||(i>0&&c.animationDiagnosticFrames[i]<=c.animationDiagnosticFrames[i-1]))throw new InvalidOperationException("Diagnostic frames must be unique, ordered and within capture");
            foreach(var color in new[]{c.themeFloorTarget,c.themeStoneTarget,c.themeWoodTarget})foreach(float x in new[]{color.r,color.g,color.b,color.a})if(float.IsNaN(x)||float.IsInfinity(x)||x<0||x>1)throw new InvalidOperationException("Finite per-role theme colors required");
            return c;
        }
        static Material Mat(string name,Color color,Texture texture=null){string path=Folder+"/Materials/"+name+".mat";var shader=AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);if(!shader)throw new InvalidOperationException("Explicit original shared shader required");var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(shader);AssetDatabase.CreateAsset(m,path);}m.color=color;m.mainTexture=texture;EditorUtility.SetDirty(m);return m;}
        static void Layer(Transform t,int n){t.gameObject.layer=n;foreach(Transform c in t)Layer(c,n);}
        static Transform Box(string name,Vector3 p,Vector3 size,Material m,bool solid=true,Transform parent=null,int layer=Experiment.WorldLayer){var go=GameObject.CreatePrimitive(PrimitiveType.Cube);go.name=name;go.layer=layer;go.transform.SetParent(parent,false);go.transform.localPosition=p;go.transform.localScale=size;go.GetComponent<Renderer>().sharedMaterial=m;if(!solid)UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());return go.transform;}
        static void Anchor(string id,Transform target,Vector3 local,string meaning){anchors.Add(new Anchor{id=id,target=target,localPoint=local,meaning=meaning});}
        static Transform Point(string id,Vector3 p,string meaning){var t=new GameObject(id).transform;t.position=p;Anchor(id,t,Vector3.zero,meaning);return t;}
        static ModelPose Actor(string name,Transform parent,Material material){
            var original=AssetDatabase.LoadAssetAtPath<GameObject>(Knight);if(!original)throw new InvalidOperationException("Original CC0 Knight missing");var go=UnityEngine.Object.Instantiate(original,parent);go.name=name;var rs=go.GetComponentsInChildren<Renderer>();if(rs.Length==0)throw new InvalidOperationException("Knight mesh missing");Bounds b=rs[0].bounds;foreach(var r in rs)b.Encapsulate(r.bounds);if(b.size.y<=0)throw new InvalidOperationException("Knight scale invalid");go.transform.localScale=Vector3.one*(1.7f/b.size.y);b=rs[0].bounds;foreach(var r in rs){b.Encapsulate(r.bounds);r.sharedMaterial=material;}go.transform.position+=new Vector3(parent.position.x-b.center.x,parent.position.y-b.min.y,parent.position.z-b.center.z);
            foreach(var a in go.GetComponentsInChildren<Animator>()){a.enabled=false;a.applyRootMotion=false;}foreach(var a in go.GetComponentsInChildren<Animation>())a.enabled=false;foreach(var col in go.GetComponentsInChildren<Collider>())UnityEngine.Object.DestroyImmediate(col);
            // Unity requires this for manually rendering a sampled SMR repeatedly
            // in one update. Keep the original FBX, importer, clips and clock.
            foreach(var skin in go.GetComponentsInChildren<SkinnedMeshRenderer>(true)){skin.forceMatrixRecalculationPerRender=true;skin.updateWhenOffscreen=true;}
            return new ModelPose{model=go.transform,position=go.transform.localPosition,rotation=go.transform.localRotation,scale=go.transform.localScale};
        }
        static AnimationClip CanonicalClip(string canonical){
            var candidates=new List<AnimationClip>();foreach(var asset in AssetDatabase.LoadAllAssetsAtPath(Knight)){
                var clip=asset as AnimationClip;if(!clip||clip.name.StartsWith("__preview__",StringComparison.OrdinalIgnoreCase))continue;
                if(clip.name.Equals(canonical,StringComparison.Ordinal)||clip.name.EndsWith("|"+canonical,StringComparison.Ordinal))candidates.Add(clip);
            }
            if(candidates.Count!=1)throw new InvalidOperationException("Exactly one non-preview original "+canonical+" clip is required; found "+candidates.Count);
            if(candidates[0].empty||candidates[0].length<=0)throw new InvalidOperationException("Canonical original clip has no usable animation: "+canonical);return candidates[0];
        }
        static Transform Text(string text,Vector3 p,Camera camera,Color color){
            var go=new GameObject("Observer editorial label: "+text);go.layer=Experiment.GuideLayer;go.transform.position=p;go.transform.rotation=Quaternion.LookRotation(p-camera.transform.position);var t=go.AddComponent<TextMesh>();t.text=text;t.anchor=TextAnchor.MiddleCenter;t.alignment=TextAlignment.Center;t.fontSize=48;t.characterSize=.055f;t.color=color;
            string path=Folder+"/Materials/OSFontDescriptor.asset";var f=AssetDatabase.LoadAssetAtPath<Font>(path);if(!f){f=Font.CreateDynamicFontFromOSFont("Malgun Gothic",48);if(!f)throw new InvalidOperationException("OS Korean font unavailable");AssetDatabase.CreateAsset(f,path);}t.font=f;go.GetComponent<Renderer>().sharedMaterial=f.material;return go.transform;
        }
        static GameObject Arrow(string id,Vector3 a,Vector3 b){
            var go=new GameObject(id);go.layer=Experiment.GuideLayer;var l=go.AddComponent<LineRenderer>();l.sharedMaterial=guide;l.startColor=l.endColor=new Color(.25f,.9f,.65f);l.startWidth=l.endWidth=.11f;l.useWorldSpace=true;l.shadowCastingMode=ShadowCastingMode.Off;Vector3 dir=(b-a).normalized,side=Vector3.Cross(Vector3.up,dir);a+=Vector3.up*.16f;b+=Vector3.up*.16f;l.positionCount=5;l.SetPositions(new[]{a,b,b-dir*.65f+side*.35f,b,b-dir*.65f-side*.35f});return go;
        }
        static void Perimeter(Experiment e,int a,int b,List<GameObject> closers,List<int> aa,List<int> bb){
            Vector3 p=(e.Center(a)+e.Center(b))*.5f;bool east=a/4==b/4;float half=(e.config.cellSize-1.8f)*.5f;Vector3 side=east?Vector3.forward:Vector3.right;Vector3 size=east?new Vector3(.18f,2.2f,half):new Vector3(half,2.2f,.18f);
            for(int sign=-1;sign<=1;sign+=2)Box("R"+a+"-R"+b+" fixed door-side wall",p+side*sign*(.9f+half*.5f)+Vector3.up*1.1f,size,stone);
            // Deliberately roofless: an overhead lintel would hide an open port
            // in the true-topdown observer. Fixed jambs and the actual closer remain.
            var close=Box("Connector R"+a+"-R"+b+" actual closed port",p+Vector3.up*1.1f,east?new Vector3(.18f,2.2f,1.8f):new Vector3(1.8f,2.2f,.18f),wood);closers.Add(close.gameObject);aa.Add(a);bb.Add(b);Point("port-"+a+"-"+b,p+Vector3.up*.2f,"Actual shared door aperture center; connector-closing state comes from visible graph, not label visibility");Anchor("closed-port-"+a+"-"+b,close,Vector3.zero,"Actual closed connector; active only while collider blocks port");
        }
        static void Spike(string id,Vector3 p,Transform parent){
            // Recognizable own spike cluster, not commercial geometry or a damage simulation.
            var root=new GameObject(id);root.layer=Experiment.ContentLayer;root.transform.SetParent(parent,false);root.transform.localPosition=p;
            for(int i=0;i<3;i++){string asset=Folder+"/Meshes/Spike.asset";var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(asset);if(!mesh){mesh=new Mesh();mesh.name="Own four-sided spike";mesh.vertices=new[]{new Vector3(-.18f,0,-.18f),new Vector3(.18f,0,-.18f),new Vector3(.18f,0,.18f),new Vector3(-.18f,0,.18f),new Vector3(0,.55f,0)};mesh.triangles=new[]{0,4,1,1,4,2,2,4,3,3,4,0,0,1,2,0,2,3};mesh.RecalculateNormals();AssetDatabase.CreateAsset(mesh,asset);}var go=new GameObject("Own spike");go.layer=Experiment.ContentLayer;go.transform.SetParent(root.transform,false);go.transform.localPosition=new Vector3((i-1)*.4f,0,0);go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=red;}
            var col=root.AddComponent<BoxCollider>();col.center=Vector3.up*.25f;col.size=new Vector3(1.25f,.5f,.4f);col.isTrigger=true;Anchor(id,root.transform,Vector3.up*.5f,"Own modeled spike trigger; contact is not a playability/damage proof");
        }
        static void Chest(Vector3 p,Transform parent){var t=new GameObject("Own side-room treasure chest").transform;t.SetParent(parent,false);t.localPosition=p;Box("Wooden chest body",Vector3.up*.24f,new Vector3(.8f,.45f,.5f),wood,false,t);Box("Chest lid",Vector3.up*.52f,new Vector3(.85f,.14f,.55f),yellow,false,t);foreach(float x in new[]{-.28f,.28f})Box("Chest metal strap",new Vector3(x,.4f,-.26f),new Vector3(.065f,.45f,.035f),stone,false,t);Anchor("chest-"+parent.name,t,Vector3.up*.55f,"Own reward prop in optional/dead-end room");}
        public static Experiment Build(string modeId,Action<Experiment,ModelPose,AnimationClip,float,string> diagnostic=null){
            var c=Configuration();var mode=Array.Find(c.modes,m=>m.id==modeId);if(mode==null)throw new ArgumentException("Unknown scoped generator mode");Directory.CreateDirectory(Folder+"/Materials");Directory.CreateDirectory(Folder+"/Meshes");AssetDatabase.Refresh();EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);anchors=new List<Anchor>();
            var e=new GameObject("OUR OWN GENERATOR — "+modeId).AddComponent<Experiment>();e.config=c;e.mode=mode;e.graph=GraphModel.Generate(c.seed,mode.sideVariant,mode.templateVariant,mode.broken);
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.48f,.49f,.5f);var light=new GameObject("Own stage light").AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.1f;light.transform.rotation=Quaternion.Euler(48,-28,0);
            var tex=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/ThirdParty/KayKitAdventurers/knight_texture.png");if(!tex)throw new InvalidOperationException("Knight original texture required");floor=Mat("Black green floor",new Color(.09f,.13f,.12f));stone=Mat("Stone boundaries",new Color(.3f,.35f,.34f));wood=Mat("Wood props",new Color(.4f,.26f,.15f));green=Mat("Player original texture",new Color(.7f,.95f,.8f),tex);red=Mat("Threat original texture",new Color(.95f,.45f,.35f),tex);yellow=Mat("Goal warm yellow",new Color(.95f,.72f,.25f));blue=Mat("Entrance blue",new Color(.22f,.62f,.87f));
            string guidePath=Folder+"/Materials/ObserverGuides.mat";guide=AssetDatabase.LoadAssetAtPath<Material>(guidePath);if(!guide){guide=new Material(Shader.Find("Sprites/Default"));AssetDatabase.CreateAsset(guide,guidePath);}
            e.playerCamera=new GameObject("Player follow camera — own 3D movement").AddComponent<Camera>();e.observerCamera=new GameObject("Observer room graph camera").AddComponent<Camera>();foreach(var camera in new[]{e.playerCamera,e.observerCamera}){camera.enabled=false;camera.aspect=c.width/(float)c.height;camera.nearClipPlane=.04f;camera.farClipPlane=100;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=Color.black;camera.fieldOfView=58;}e.playerCamera.cullingMask=~(1<<Experiment.GuideLayer);e.observerCamera.orthographic=true;e.observerCamera.orthographicSize=14.6f;e.observerCamera.transform.position=new Vector3(0,36,-.01f);e.observerCamera.transform.rotation=Quaternion.Euler(90,0,0);
            var templates=new List<GameObject>();var closers=new List<GameObject>();var aa=new List<int>();var bb=new List<int>();
            for(int id=0;id<16;id++){
                Vector3 p=e.Center(id);Box("R"+id.ToString("D2")+" own room floor",p+Vector3.down*.15f,new Vector3(c.cellSize-.08f,.3f,c.cellSize-.08f),floor);var origin=Point("room-"+id.ToString("D2"),p+Vector3.up*.03f,"Room center; role="+e.graph.roomRoles[id]+"; degree="+e.graph.Degree(id));Text("R"+id.ToString("D2"),p+new Vector3(-2.1f,.2f,2.1f),e.observerCamera,new Color(.8f,.83f,.8f));
                var t=new GameObject("Template-R"+id.ToString("D2")).transform;t.position=p;templates.Add(t.gameObject);int variant=e.graph.roomVariants[id];
                Box("Hand-authored corner platform variant"+variant,new Vector3(variant==0?-1.85f:1.85f,.22f,1.8f),new Vector3(1.25f,.44f,1.25f),stone,true,t);Box("Hand-authored pillar variant"+variant,new Vector3(variant==0?1.85f:-1.85f,.7f,-1.8f),new Vector3(.7f,1.4f,.7f),wood,true,t);
                if(id%5==0)Spike("template-spikes-R"+id,new Vector3(1.6f,0,1.6f),t);if(e.graph.roomRoles[id]=="side"&&e.graph.Degree(id)==1)Chest(new Vector3(-1.6f,0,-1.6f),t);
                if(id%4<3)Perimeter(e,id,id+1,closers,aa,bb);if(id/4<3)Perimeter(e,id,id+4,closers,aa,bb);
                if(id%4==0)Box("West outer boundary",p+new Vector3(-3,1.1f,0),new Vector3(.18f,2.2f,6),stone);if(id%4==3)Box("East outer boundary",p+new Vector3(3,1.1f,0),new Vector3(.18f,2.2f,6),stone);if(id/4==0)Box("North outer boundary",p+new Vector3(0,1.1f,3),new Vector3(6,2.2f,.18f),stone);if(id/4==3)Box("South outer boundary",p+new Vector3(0,1.1f,-3),new Vector3(6,2.2f,.18f),stone);
            }
            e.connectorClosers=closers.ToArray();e.closerA=aa.ToArray();e.closerB=bb.ToArray();e.templateRoots=templates.ToArray();var arrows=new List<GameObject>();for(int i=1;i<e.graph.mandatoryRoute.Length;i++)arrows.Add(Arrow("mandatory-direction-"+(i-1),e.Center(e.graph.mandatoryRoute[i-1]),e.Center(e.graph.mandatoryRoute[i])));e.routeArrows=arrows.ToArray();
            foreach(var pair in new[]{Tuple.Create("entrance",e.graph.entrance,blue),Tuple.Create("derived-bottom-exit",e.graph.exit,yellow)}){var p=e.Center(pair.Item2);var visual=new GameObject(pair.Item1+" visual root").transform;var sign=Box(pair.Item1,p+new Vector3(0,.08f,0),new Vector3(1.3f,.16f,1.3f),pair.Item3,false);sign.SetParent(visual,true);Anchor(pair.Item1,sign,Vector3.up*.5f,"Entrance/top row or exit derived at bottom terminus; not preselected exit target");var label=Text(pair.Item1=="entrance"?"입구":"출구",p+new Vector3(0,.3f,-1.8f),e.observerCamera,new Color(1,.85f,.3f));label.SetParent(visual,true);if(pair.Item1=="derived-bottom-exit")e.exitVisualRoot=visual.gameObject;}
            var actor=new GameObject("Own articulated player");actor.layer=Experiment.PlayerLayer;e.player=actor.AddComponent<CharacterController>();e.player.height=1.72f;e.player.radius=.24f;e.player.center=Vector3.up*.86f;e.player.skinWidth=.01f;e.player.stepOffset=.2f;e.player.minMoveDistance=0;e.playerModel=Actor("CC0 articulated Knight",actor.transform,green);Layer(actor.transform,Experiment.PlayerLayer);Anchor("player-head",actor.transform,Vector3.up*1.55f,"Declared body point, not mesh visibility guarantee");
            e.contentRoot=new GameObject("Illustrative later enemy/content pass");e.enemy=new GameObject("Own patrol/contact actor").transform;e.enemy.SetParent(e.contentRoot.transform,false);e.enemyModel=Actor("CC0 articulated enemy Knight",e.enemy,red);Layer(e.enemy,Experiment.ContentLayer);var enemyCollider=e.enemy.gameObject.AddComponent<CapsuleCollider>();enemyCollider.height=1.7f;enemyCollider.radius=.32f;enemyCollider.center=Vector3.up*.85f;enemyCollider.isTrigger=true;Anchor("enemy-body",e.enemy,Vector3.up*.9f,"Own contact trigger; no commercial AI or safety measurement");
            var finalHazard=new GameObject("Illustrative later hazard parent").transform;finalHazard.SetParent(e.contentRoot.transform,false);finalHazard.position=e.Center(e.graph.mandatoryRoute[Math.Max(1,e.graph.mandatoryRoute.Length/3)]);Spike("later-illustrative-spikes",new Vector3(-1.8f,0,1.7f),finalHazard);
            e.walkingClip=CanonicalClip("Walking_A");e.idleClip=CanonicalClip("Idle");
            var themes=new List<Renderer>();var themeColors=new List<Color>();var themeTargets=new List<Color>();var themeRoles=new List<string>();foreach(var r in UnityEngine.Object.FindObjectsByType<Renderer>()){if(r.sharedMaterial==floor||r.sharedMaterial==stone||r.sharedMaterial==wood){themes.Add(r);themeColors.Add(r.sharedMaterial.color);themeRoles.Add(r.sharedMaterial==floor?"floor":r.sharedMaterial==stone?"stone":"wood");themeTargets.Add(r.sharedMaterial==floor?c.themeFloorTarget:r.sharedMaterial==stone?c.themeStoneTarget:c.themeWoodTarget);}}e.themeRenderers=themes.ToArray();e.themeBaseColors=themeColors.ToArray();e.themeTargetColors=themeTargets.ToArray();e.themeRoles=themeRoles.ToArray();
            e.anchorDefinitions=anchors.ToArray();if(diagnostic!=null)e.animationDiagnosticObserver=(pose,clip,time,stage)=>diagnostic(e,pose,clip,time,stage);e.ResetExperiment();return e;
        }
        [Serializable] public sealed class BoneDiagnostic {
            public string role,path,name;public Vector3 localPosition,localScale,worldPosition,worldScale;public Quaternion localRotation,worldRotation;
        }
        [Serializable] public sealed class SkinDiagnostic {
            public string path,rootBonePath,meshName,bakedVertexSHA256,vertexCoordinateSpace="renderer-local; BakeMesh(useScale:false); little-endian float32 XYZ";
            public bool enabled,activeInHierarchy,forceMatrixRecalculationPerRender,updateWhenOffscreen;public int boneCount,vertexCount;public float[] localToWorld;
        }
        [Serializable] public sealed class AnimationDiagnostic {
            public string schemaVersion="11-05-animation-diagnostic-v2",fingerprint,mode,stage,actor,clipName,clipAssetPath,clipGUID;
            public int frame;public long clipLocalID;public float clipLength,clipSampleTime;public BoneDiagnostic[] bones;public SkinDiagnostic[] renderers;
            public bool cpuBakeMeshDiagnostic=true,actualVisualMotionApproved=false;
        }
        [Serializable] public sealed class DiagnosticSummary {
            public string schemaVersion="11-05-animation-diagnostics-summary-v2",fingerprint,mode,file="animation-diagnostics.jsonl",sha256;
            public int records;public int[] selectedFrames;public string[] actors={"player","enemy"},stages={"pre-sample","post-sample","post-root-restore","post-render-player","post-render-observer"};
            public bool actualVisualMotionApproved=false;public string limit="Bone/BakeMesh changes are diagnostics, not a visual gait, speed, sliding or pixel-QA pass.";
        }
        static string Relative(Transform t,Transform root){
            if(!t)return "";if(t==root)return "";var names=new List<string>();for(var q=t;q&&q!=root;q=q.parent)names.Insert(0,q.name);
            if(!t.IsChildOf(root))throw new InvalidOperationException("Diagnostic bone/renderer escaped its actual model");return string.Join("/",names);
        }
        static float[] MatrixValues(Matrix4x4 m){var values=new float[16];for(int r=0;r<4;r++)for(int c=0;c<4;c++)values[r*4+c]=m[r,c];return values;}
        static void Finite(params float[] values){foreach(float v in values)if(float.IsNaN(v)||float.IsInfinity(v))throw new InvalidOperationException("Nonfinite actual animation diagnostic");}
        static void Finite(Vector3 v){Finite(v.x,v.y,v.z);}
        static void Finite(Quaternion v){Finite(v.x,v.y,v.z,v.w);}
        static BoneDiagnostic Bone(ModelPose model,string role,string path){
            var t=path==""?model.model:model.model.Find(path);if(!t)throw new InvalidOperationException("Required actual Knight bone missing: "+path);
            Finite(t.localPosition);Finite(t.localRotation);Finite(t.localScale);Finite(t.position);Finite(t.rotation);Finite(t.lossyScale);
            return new BoneDiagnostic{role=role,path=path,name=t.name,localPosition=t.localPosition,localRotation=t.localRotation,localScale=t.localScale,worldPosition=t.position,worldRotation=t.rotation,worldScale=t.lossyScale};
        }
        static SkinDiagnostic Skin(ModelPose model,SkinnedMeshRenderer skin){
            var baked=new Mesh();try{
                skin.BakeMesh(baked,false);var vertices=baked.vertices;if(vertices.Length==0)throw new InvalidOperationException("Actual baked Knight mesh has no vertices");string hash;
                using(var bytes=new MemoryStream()){using(var writer=new BinaryWriter(bytes,Encoding.UTF8,true)){foreach(var v in vertices){Finite(v);writer.Write(v.x);writer.Write(v.y);writer.Write(v.z);}}hash=Sha(bytes.ToArray());}
                var matrix=MatrixValues(skin.localToWorldMatrix);Finite(matrix);
                return new SkinDiagnostic{path=Relative(skin.transform,model.model),rootBonePath=Relative(skin.rootBone,model.model),meshName=skin.sharedMesh?skin.sharedMesh.name:"",enabled=skin.enabled,activeInHierarchy=skin.gameObject.activeInHierarchy,forceMatrixRecalculationPerRender=skin.forceMatrixRecalculationPerRender,updateWhenOffscreen=skin.updateWhenOffscreen,boneCount=skin.bones.Length,vertexCount=vertices.Length,bakedVertexSHA256=hash,localToWorld=matrix};
            }finally{UnityEngine.Object.DestroyImmediate(baked);}
        }
        [Serializable] public sealed class WarmupRecord {
            public string schemaVersion="11-05-camera-warmup-v3",fingerprint,mode;public int frameBefore,frameAfter,renderCalls=2,advanceOneFrameCalls=0,capturedFrames=0,jpegFilesWritten=0;
            public string[] cameras={"player","observer"};public Vector3 playerPositionBefore,playerPositionAfter,enemyPositionBefore,enemyPositionAfter;
            public BoneDiagnostic playerModelRootBefore,playerModelRootAfter,enemyModelRootBefore,enemyModelRootAfter;public bool actualVisualMotionApproved=false;
        }
        static void Warmup(Experiment e,RenderTexture target,string output,string fp){
            var record=new WarmupRecord{fingerprint=fp,mode=e.mode.id,frameBefore=e.Frame,playerPositionBefore=e.player.transform.position,enemyPositionBefore=e.enemy.position,playerModelRootBefore=Bone(e.playerModel,"model-root",""),enemyModelRootBefore=Bone(e.enemyModel,"model-root","")};
            if(e.Frame!=0||e.animationDiagnosticObserver!=null)throw new InvalidOperationException("Warm-up must precede the diagnostic frame-zero reset");
            foreach(var camera in new[]{e.playerCamera,e.observerCamera}){camera.targetTexture=target;camera.Render();}
            record.frameAfter=e.Frame;record.playerPositionAfter=e.player.transform.position;record.enemyPositionAfter=e.enemy.position;record.playerModelRootAfter=Bone(e.playerModel,"model-root","");record.enemyModelRootAfter=Bone(e.enemyModel,"model-root","");
            if(record.frameBefore!=0||record.frameAfter!=0||!record.playerPositionBefore.Equals(record.playerPositionAfter)||!record.enemyPositionBefore.Equals(record.enemyPositionAfter)||JsonUtility.ToJson(record.playerModelRootBefore)!=JsonUtility.ToJson(record.playerModelRootAfter)||JsonUtility.ToJson(record.enemyModelRootBefore)!=JsonUtility.ToJson(record.enemyModelRootAfter))throw new InvalidOperationException("Warm-up changed the physical/model roots or simulation clock");
            File.WriteAllText(Path.Combine(output,"warmup.json"),JsonUtility.ToJson(record,true));
        }
        sealed class DiagnosticWriter:IDisposable {
            readonly string output,fingerprint,mode,path;readonly StreamWriter writer;readonly HashSet<string> seen=new HashSet<string>();int records;
            public DiagnosticWriter(string output,string fingerprint,string mode){this.output=output;this.fingerprint=fingerprint;this.mode=mode;path=Path.Combine(output,"animation-diagnostics.jsonl");writer=new StreamWriter(path,false,new UTF8Encoding(false));}
            public void Record(Experiment e,ModelPose pose,AnimationClip clip,float time,string stage){
                if(Array.BinarySearch(e.config.animationDiagnosticFrames,e.Frame)<0)return;
                string actor=pose==e.playerModel?"player":pose==e.enemyModel?"enemy":throw new InvalidOperationException("Unknown actual actor model");
                if(Array.IndexOf(new[]{"pre-sample","post-sample","post-root-restore","post-render-player","post-render-observer"},stage)<0)throw new InvalidOperationException("Unknown diagnostic stage");
                if(!seen.Add(e.Frame+"|"+actor+"|"+stage))throw new InvalidOperationException("Duplicate actual diagnostic record");
                string guid;long localId;if(!clip||AssetDatabase.GetAssetPath(clip)!=Knight||!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(clip,out guid,out localId)||string.IsNullOrEmpty(guid)||localId==0)throw new InvalidOperationException("Actual original animation asset binding missing");Finite(time,clip.length);
                var bones=new[]{Bone(pose,"model-root",""),Bone(pose,"rig-root","Rig/root"),Bone(pose,"hips","Rig/root/hips"),Bone(pose,"upperleg-left","Rig/root/hips/upperleg.l"),Bone(pose,"lowerleg-left","Rig/root/hips/upperleg.l/lowerleg.l"),Bone(pose,"foot-left","Rig/root/hips/upperleg.l/lowerleg.l/foot.l"),Bone(pose,"upperleg-right","Rig/root/hips/upperleg.r"),Bone(pose,"lowerleg-right","Rig/root/hips/upperleg.r/lowerleg.r"),Bone(pose,"foot-right","Rig/root/hips/upperleg.r/lowerleg.r/foot.r")};
                var skins=pose.model.GetComponentsInChildren<SkinnedMeshRenderer>(true);if(skins.Length==0)throw new InvalidOperationException("Actual Knight SMR diagnostic missing");Array.Sort(skins,(a,b)=>string.CompareOrdinal(Relative(a.transform,pose.model),Relative(b.transform,pose.model)));var renderers=new SkinDiagnostic[skins.Length];for(int i=0;i<skins.Length;i++)renderers[i]=Skin(pose,skins[i]);
                writer.WriteLine(JsonUtility.ToJson(new AnimationDiagnostic{fingerprint=fingerprint,mode=mode,frame=e.Frame,stage=stage,actor=actor,clipName=clip.name,clipAssetPath=Knight,clipGUID=guid,clipLocalID=localId,clipLength=clip.length,clipSampleTime=time,bones=bones,renderers=renderers}));records++;
            }
            public void AfterRender(Experiment e,string camera){Record(e,e.playerModel,e.playerModel.lastSampledClip,e.playerModel.lastSampledTime,"post-render-"+camera);Record(e,e.enemyModel,e.enemyModel.lastSampledClip,e.enemyModel.lastSampledTime,"post-render-"+camera);}
            public void Complete(Experiment e){
                var summary=new DiagnosticSummary{fingerprint=fingerprint,mode=mode,selectedFrames=e.config.animationDiagnosticFrames,records=records};
                foreach(int frame in summary.selectedFrames)foreach(string actor in summary.actors)foreach(string stage in summary.stages)if(!seen.Contains(frame+"|"+actor+"|"+stage))throw new InvalidOperationException("Missing actual diagnostic stage");
                if(records!=summary.selectedFrames.Length*summary.actors.Length*summary.stages.Length)throw new InvalidOperationException("Unexpected diagnostic count");writer.Flush();writer.Close();summary.sha256=Sha(File.ReadAllBytes(path));File.WriteAllText(Path.Combine(output,"animation-diagnostics-summary.json"),JsonUtility.ToJson(summary,true));
            }
            public void Dispose(){writer.Dispose();}
        }
        [Serializable] public sealed class ClipBinding {
            public string path,propertyName,type,kind;public int keyCount;public bool hasFloatKeyStatistics;public float firstTime,lastTime,firstValue,lastValue,minValue,maxValue;
        }
        [Serializable] public sealed class ClipEntry {
            public string name,assetPath,guid;public long localID;public float length,frameRate;public bool empty,preview,selectedIdle,selectedWalking;
            public int floatBindingCount,objectReferenceBindingCount,uniqueBindingPathCount,uniquePropertyNameCount;public ClipBinding[] bindings;
        }
        [Serializable] public sealed class ClipCatalog {
            public string schemaVersion="11-05-animation-clip-catalog-v3",fingerprint,mode,assetPath=Knight,sourceFBXSHA256,sourceImporterMetaSHA256;
            public ClipEntry[] clips;public ClipEntry selectedIdle,selectedWalking;public bool actualVisualMotionApproved=false;
            public string limit="Actual imported clip identities and curve bindings; root/bone curve statistics are not rendered gait or speed approval.";
        }
        static ClipEntry CatalogEntry(AnimationClip clip,Experiment e){
            string guid;long localId;if(!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(clip,out guid,out localId)||string.IsNullOrEmpty(guid)||localId==0||AssetDatabase.GetAssetPath(clip)!=Knight)throw new InvalidOperationException("Imported clip catalog asset binding missing");Finite(clip.length,clip.frameRate);
            var entries=new List<ClipBinding>();var paths=new HashSet<string>();var properties=new HashSet<string>();var floats=AnimationUtility.GetCurveBindings(clip);var objects=AnimationUtility.GetObjectReferenceCurveBindings(clip);
            foreach(var binding in floats){
                var curve=AnimationUtility.GetEditorCurve(clip,binding);var keys=curve==null?new Keyframe[0]:curve.keys;var row=new ClipBinding{path=binding.path,propertyName=binding.propertyName,type=binding.type.FullName,kind="float",keyCount=keys.Length};
                if(keys.Length>0){row.hasFloatKeyStatistics=true;row.firstTime=keys[0].time;row.lastTime=keys[keys.Length-1].time;row.firstValue=keys[0].value;row.lastValue=keys[keys.Length-1].value;row.minValue=row.maxValue=keys[0].value;foreach(var key in keys){Finite(key.time,key.value);row.minValue=Mathf.Min(row.minValue,key.value);row.maxValue=Mathf.Max(row.maxValue,key.value);}}
                paths.Add(binding.path);properties.Add(binding.propertyName);entries.Add(row);
            }
            foreach(var binding in objects){var keys=AnimationUtility.GetObjectReferenceCurve(clip,binding);foreach(var key in keys)Finite(key.time);paths.Add(binding.path);properties.Add(binding.propertyName);entries.Add(new ClipBinding{path=binding.path,propertyName=binding.propertyName,type=binding.type.FullName,kind="object-reference",keyCount=keys.Length});}
            entries.Sort((a,b)=>{int x=string.CompareOrdinal(a.path,b.path);if(x!=0)return x;x=string.CompareOrdinal(a.propertyName,b.propertyName);return x!=0?x:string.CompareOrdinal(a.kind,b.kind);});
            return new ClipEntry{name=clip.name,assetPath=Knight,guid=guid,localID=localId,length=clip.length,frameRate=clip.frameRate,empty=clip.empty,preview=clip.name.StartsWith("__preview__",StringComparison.OrdinalIgnoreCase),selectedIdle=clip==e.idleClip,selectedWalking=clip==e.walkingClip,floatBindingCount=floats.Length,objectReferenceBindingCount=objects.Length,uniqueBindingPathCount=paths.Count,uniquePropertyNameCount=properties.Count,bindings=entries.ToArray()};
        }
        static string ClipCatalogProof(Experiment e,string output,string fp){
            var clips=new List<ClipEntry>();foreach(var asset in AssetDatabase.LoadAllAssetsAtPath(Knight)){var clip=asset as AnimationClip;if(clip)clips.Add(CatalogEntry(clip,e));}clips.Sort((a,b)=>{int x=string.CompareOrdinal(a.name,b.name);return x!=0?x:a.localID.CompareTo(b.localID);});
            var catalog=new ClipCatalog{fingerprint=fp,mode=e.mode.id,sourceFBXSHA256=Sha(File.ReadAllBytes(Knight)),sourceImporterMetaSHA256=Sha(File.ReadAllBytes(Knight+".meta")),clips=clips.ToArray(),selectedIdle=CatalogEntry(e.idleClip,e),selectedWalking=CatalogEntry(e.walkingClip,e)};
            if(catalog.selectedIdle.preview||catalog.selectedWalking.preview||!catalog.selectedIdle.selectedIdle||!catalog.selectedWalking.selectedWalking)throw new InvalidOperationException("Canonical selected catalog entries differ");
            byte[] bytes=Encoding.UTF8.GetBytes(JsonUtility.ToJson(catalog,true));File.WriteAllBytes(Path.Combine(output,"animation-clip-catalog.json"),bytes);return Sha(bytes);
        }
        static string ScenePath(Config c,string id){var mode=Array.Find(c.modes,m=>m.id==id);if(mode==null||Path.GetFileName(mode.sceneFile)!=mode.sceneFile)throw new InvalidOperationException("Invalid independent scene path");return Folder+"/"+mode.sceneFile;}
        static void SceneProof(Experiment e,string output,string fp,string scene){
            var files=new List<Pin>();foreach(string raw in Directory.GetFiles(Folder,"*",SearchOption.AllDirectories)){string p=Canonical(raw);if((p.EndsWith(".unity")||p.EndsWith(".unity.meta"))&&p!=scene&&p!=scene+".meta")continue;files.Add(Snapshot(p,output));}if(File.Exists(Folder+".meta"))files.Add(Snapshot(Folder+".meta",output));
            var deps=new List<Pin>();foreach(string name in new[]{"Knight.fbx","Knight.fbx.meta","knight_texture.png","knight_texture.png.meta","LICENSE.txt","LICENSE.txt.meta","provenance.json","provenance.json.meta"})deps.Add(Snapshot("Assets/ThirdParty/KayKitAdventurers/"+name,output));deps.Add(Snapshot(ShaderPath,output));deps.Add(Snapshot(ShaderPath+".meta",output));
            string catalogSHA=ClipCatalogProof(e,output,fp);
            File.WriteAllText(Path.Combine(output,"mode-scene-record.json"),JsonUtility.ToJson(new SceneRecord{fingerprint=fp,mode=e.mode.id,unityVersion=Application.unityVersion,actualSceneFilesSaved=true,scenePaths=new[]{scene},animationClips=new[]{e.idleClip.name,e.walkingClip.name},animationClipCatalogSHA256=catalogSHA,warmupSHA256=Sha(File.ReadAllBytes(Path.Combine(output,"warmup.json"))),files=files.ToArray(),dependencies=deps.ToArray()},true));
        }
        [MenuItem("Yamyam/Architectural111/Build own solution-path V4 scenes")]
        public static void BuildScenes(){var c=Configuration();foreach(var m in c.modes){var e=Build(m.id);if(!EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),ScenePath(c,m.id)))throw new InvalidOperationException("Scene save failed");}AssetDatabase.SaveAssets();}
        public static void Capture(){
            string output=null,fp=null,list=null;var args=Environment.GetCommandLineArgs();for(int i=0;i<args.Length-1;i++){if(args[i]=="-solutionOutput")output=args[i+1];if(args[i]=="-solutionFingerprint")fp=args[i+1];if(args[i]=="-solutionModes")list=args[i+1];}
            if(string.IsNullOrEmpty(output)||!Path.IsPathRooted(output)||string.IsNullOrEmpty(fp)||fp.Length!=64||fp.Trim("0123456789abcdef".ToCharArray()).Length!=0||string.IsNullOrEmpty(list))throw new ArgumentException("Fresh absolute output/64hex fingerprint/mode list required");
            if(Directory.Exists(output)&&Directory.GetFileSystemEntries(output).Length!=0)throw new InvalidOperationException("Preserve old/partial capture; select a fresh attempt");Directory.CreateDirectory(output);var seen=new HashSet<string>();foreach(string id in list.Split(',')){
                if(!seen.Add(id))throw new ArgumentException("Duplicate mode");string dir=Path.Combine(output,id);Directory.CreateDirectory(dir);
                using(var diagnostic=new DiagnosticWriter(dir,fp,id)){
                    var e=Build(id);e.previewInPlayMode=false;var c=e.config;string scene=ScenePath(c,id);if(!EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),scene))throw new InvalidOperationException("Actual scene save failed");AssetDatabase.SaveAssets();AssetDatabase.Refresh();
                    byte[] config=File.ReadAllBytes(Folder+"/config.json");byte[] graph=Encoding.UTF8.GetBytes(JsonUtility.ToJson(e.graph,true));File.WriteAllBytes(Path.Combine(dir,"config.json"),config);File.WriteAllBytes(Path.Combine(dir,"generation-graph.json"),graph);var contract=new ModeRecord{fingerprint=fp,mode=id,frames=c.frames,fps=c.fps,width=c.width,height=c.height,configSHA256=Sha(config),graphSHA256=Sha(graph),scenePath=scene,actualSceneSaved=true};File.WriteAllText(Path.Combine(dir,"mode-contract.json"),JsonUtility.ToJson(contract,true));
                    var target=new RenderTexture(c.width,c.height,24);target.antiAliasing=2;target.Create();var image=new Texture2D(c.width,c.height,TextureFormat.RGB24,false);
                    try{Warmup(e,target,dir,fp);e.animationDiagnosticObserver=(pose,clip,time,stage)=>diagnostic.Record(e,pose,clip,time,stage);e.ResetExperiment();SceneProof(e,dir,fp,scene);using(var states=new StreamWriter(Path.Combine(dir,"states.jsonl")))using(var projected=new StreamWriter(Path.Combine(dir,"projected-anchors.jsonl"))){for(int frame=0;frame<c.frames;frame++){if(e.Frame!=frame)throw new InvalidOperationException("Shared integer clock drift");states.WriteLine(JsonUtility.ToJson(e.CurrentState));projected.WriteLine(JsonUtility.ToJson(e.ProjectedAnchors()));foreach(var pair in new[]{Tuple.Create("player",e.playerCamera),Tuple.Create("observer",e.observerCamera)}){var cam=pair.Item2;cam.targetTexture=target;cam.Render();diagnostic.AfterRender(e,pair.Item1);RenderTexture.active=target;image.ReadPixels(new Rect(0,0,c.width,c.height),0,0);string folder=Path.Combine(dir,pair.Item1);Directory.CreateDirectory(folder);File.WriteAllBytes(Path.Combine(folder,frame.ToString("D4")+".jpg"),image.EncodeToJPG(93));}if(frame<c.frames-1)e.AdvanceOneFrame();}}}
                    finally{e.animationDiagnosticObserver=null;e.playerCamera.targetTexture=null;e.observerCamera.targetTexture=null;RenderTexture.active=null;target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(image);}
                    diagnostic.Complete(e);
                    File.WriteAllText(Path.Combine(dir,"mode-complete.json.tmp"),JsonUtility.ToJson(contract,true));File.Move(Path.Combine(dir,"mode-complete.json.tmp"),Path.Combine(dir,"mode-complete.json"));
                }
            }File.WriteAllText(Path.Combine(output,"capture-complete.txt"),fp+"; actual own modes="+list);EditorApplication.Exit(0);
        }
    }
}
