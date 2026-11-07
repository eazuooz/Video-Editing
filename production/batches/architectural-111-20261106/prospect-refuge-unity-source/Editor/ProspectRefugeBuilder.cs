using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Yamyam.Architectural111.ProspectRefuge.Editor {
    public static class ProspectRefugeBuilder {
        const string Folder="Assets/VideoScenes/architectural-111-20261106/06-02";
        const string Knight="Assets/ThirdParty/KayKitAdventurers/Knight.fbx";
        static readonly string[] Modes={"baseline","shifted"};
        [Serializable] sealed class TapeRecord { public MoveCommand[] commands; }
        [Serializable] sealed class ModeReceipt {
            public string fingerprint,mode,configSHA256,commandTapeSHA256,frameConvention;
            public int frames,width,height,fps;
            public string[] cameras={"player","observer"};
        }
        [Serializable] sealed class FilePin { public string path,sha256;public long bytes; }
        [Serializable] sealed class SceneRecord {
            public string fingerprint,unityVersion,sourceKind="own-physical-visibility-implementation";
            public bool actualSceneFilesSaved=true;
            public string[] scenePaths,animationClipNames;
            public FilePin[] files,sharedDependencies;
        }
        static string Sha(byte[] bytes) {
            using(var digest=SHA256.Create())return BitConverter.ToString(digest.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();
        }
        static FilePin Pin(string path) {var bytes=File.ReadAllBytes(path);return new FilePin{path=path.Replace('\\','/'),sha256=Sha(bytes),bytes=bytes.LongLength};}
        static string ScenePath(string mode) {return Folder+(mode=="baseline"?"/S02-ProspectRefuge-Baseline.unity":"/S03-ProspectRefuge-Shifted.unity");}
        static ProspectRefugeConfig Config() {
            var config=JsonUtility.FromJson<ProspectRefugeConfig>(File.ReadAllText(Folder+"/capture-config.json"));
            if(config.frames!=600||config.fps!=60||config.width!=1920||config.height!=1080)throw new InvalidOperationException("Selected06.02 capture contract changed");
            if(config.commands==null||config.commands.Length!=4)throw new InvalidOperationException("Expected exact four-part fixed command tape");
            int next=0;
            foreach(var command in config.commands) {
                if(string.IsNullOrEmpty(command.id)||command.startFrame!=next||command.endFrameExclusive<=next||Mathf.Abs(command.velocity.y)>1e-6f)
                    throw new InvalidOperationException("Command tape must be ordered, contiguous and horizontal");
                next=command.endFrameExclusive;
            }
            if(next!=config.frames||config.capsuleHeight<=2*config.capsuleRadius||config.skinWidth<=0||config.stepOffset<0||config.groundStickSpeed<=0)
                throw new InvalidOperationException("Invalid finite tape/capsule configuration");
            if(config.enemyTurnStartSeconds<=0||config.enemyTurnEndSeconds<=config.enemyTurnStartSeconds||config.enemyPauseStartSeconds<=config.enemyTurnEndSeconds
                ||config.enemyPauseStartSeconds>=config.frames/(float)config.fps||config.enemyRange<=0||config.enemyHorizontalHalfFovDegrees<=0||config.enemyHorizontalHalfFovDegrees>=90)
                throw new InvalidOperationException("Invalid scripted patrol/FOV configuration");
            if(config.firstCoverSize.y>=config.cameraEyeHeight||config.headSampleHeight>=config.capsuleHeight||config.hipsSampleHeight<=0
                ||config.torsoSampleHeight<=config.hipsSampleHeight||config.headSampleHeight<=config.torsoSampleHeight||config.secondCoverSize.y<=config.headSampleHeight)
                throw new InvalidOperationException("Partial-cover observation and declared sample heights must remain explicit");
            return config;
        }
        static Material Mat(string name,Color color,Texture texture=null) {
            string path=Folder+"/"+name+".mat";var material=AssetDatabase.LoadAssetAtPath<Material>(path);
            var shader=Shader.Find("Yamyam/ArchitecturalSurface");
            if(!shader)throw new InvalidOperationException("Stage the pinned original ArchitecturalSurface.shader dependency first");
            if(!material){material=new Material(shader);AssetDatabase.CreateAsset(material,path);}
            material.shader=shader;material.color=color;material.mainTexture=texture;return material;
        }
        static GameObject Shape(string name,PrimitiveType type,Vector3 localPosition,Vector3 scale,Material material,Transform parent,int layer) {
            var go=GameObject.CreatePrimitive(type);go.name=name;go.layer=layer;go.transform.SetParent(parent,false);
            go.transform.localPosition=localPosition;go.transform.localScale=scale;go.GetComponent<Renderer>().sharedMaterial=material;
            // All physical solids are explicit parent BoxColliders. Decorations
            // and sampled-point markers cannot accidentally become occluders.
            UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());return go;
        }
        static Transform Cover(string name,Vector3 center,Vector3 size,Material boards,Material straps) {
            var root=new GameObject(name).transform;root.gameObject.layer=ProspectRefugeExperiment.EnvironmentLayer;root.position=center;
            root.gameObject.AddComponent<BoxCollider>().size=size;
            // Recognizable solid barricade. Its parent box defines collision;
            // tiny decorative seams/straps do not introduce openings/ray targets.
            Shape("Opaque solid wood body",PrimitiveType.Cube,Vector3.zero,size,boards,root,ProspectRefugeExperiment.EnvironmentLayer);
            for(int i=1;i<4;i++)Shape("Board seam "+i,PrimitiveType.Cube,new Vector3(0,-size.y*.5f+size.y*i/4, -size.z*.5f-.001f),new Vector3(size.x,.025f,.006f),straps,root,ProspectRefugeExperiment.EnvironmentLayer);
            foreach(float x in new[]{-size.x*.34f,size.x*.34f})
                Shape("Vertical iron strap",PrimitiveType.Cube,new Vector3(x,0,0),new Vector3(.075f,size.y+.006f,size.z+.006f),straps,root,ProspectRefugeExperiment.EnvironmentLayer);
            return root;
        }
        static void LayerRecursive(Transform root,int layer) {root.gameObject.layer=layer;foreach(Transform child in root)LayerRecursive(child,layer);}
        static Transform ArticulatedModel(Transform parent,string name,Material material) {
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(Knight);if(!prefab)throw new InvalidOperationException("Missing provenance-bound KayKit Knight FBX");
            var go=UnityEngine.Object.Instantiate(prefab,parent);go.name=name;var renderers=go.GetComponentsInChildren<Renderer>();
            if(renderers.Length==0)throw new InvalidOperationException("Knight has no actual renderers");
            Bounds bounds=renderers[0].bounds;foreach(var renderer in renderers)bounds.Encapsulate(renderer.bounds);
            if(bounds.size.y<=0)throw new InvalidOperationException("Invalid articulated model bounds");
            go.transform.localScale=Vector3.one*(1.72f/bounds.size.y);
            bounds=renderers[0].bounds;foreach(var renderer in renderers)bounds.Encapsulate(renderer.bounds);
            go.transform.position-=new Vector3(bounds.center.x,bounds.min.y,bounds.center.z);
            foreach(var renderer in renderers)renderer.sharedMaterial=material;
            foreach(var animator in go.GetComponentsInChildren<Animator>()){animator.applyRootMotion=false;animator.enabled=false;}
            foreach(var animation in go.GetComponentsInChildren<Animation>())animation.enabled=false;
            foreach(var collider in go.GetComponentsInChildren<Collider>())UnityEngine.Object.DestroyImmediate(collider);
            return go.transform;
        }
        static LineRenderer Guide(string name,Color color,float width=.045f) {
            var go=new GameObject(name);go.layer=ProspectRefugeExperiment.GuideLayer;var line=go.AddComponent<LineRenderer>();
            string path=Folder+"/Observer guides.mat";var material=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(!material){var shader=Shader.Find("Sprites/Default");if(!shader)throw new InvalidOperationException("Missing built-in guide shader");material=new Material(shader);AssetDatabase.CreateAsset(material,path);}
            line.sharedMaterial=material;line.useWorldSpace=true;line.startWidth=line.endWidth=width;line.numCapVertices=6;
            line.startColor=line.endColor=color;line.shadowCastingMode=ShadowCastingMode.Off;return line;
        }
        static Camera Camera(string name,ProspectRefugeConfig c) {
            var camera=new GameObject(name).AddComponent<Camera>();camera.aspect=c.width/(float)c.height;camera.nearClipPlane=.04f;camera.farClipPlane=80;
            camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.018f,.025f,.023f);camera.enabled=false;return camera;
        }
        public static ProspectRefugeExperiment Build(string mode) {
            if(Array.IndexOf(Modes,mode)<0)throw new ArgumentException("Unknown selected06.02 mode");
            Directory.CreateDirectory(Folder);AssetDatabase.Refresh();var c=Config();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.4f,.43f,.45f);
            var rig=new GameObject("Prospect and Refuge — same physical commands, one cover offset").AddComponent<ProspectRefugeExperiment>();
            rig.config=c;rig.mode=mode;rig.secondCoverOffsetX=mode=="baseline"?c.baselineSecondCoverOffsetX:c.shiftedSecondCoverOffsetX;
            var floorMat=Mat("Ground",new Color(.12f,.17f,.16f));var wood=Mat("Solid cover wood",new Color(.42f,.30f,.18f));var iron=Mat("Cover straps",new Color(.13f,.18f,.18f));
            var floor=Shape("Physical floor — top y0",PrimitiveType.Cube,new Vector3(1,-.15f,.5f),new Vector3(16,.3f,14),floorMat,null,ProspectRefugeExperiment.EnvironmentLayer);
            floor.AddComponent<BoxCollider>();
            Cover("First PARTIAL cover — torso/hips occlusion is not guaranteed head concealment",c.firstCoverCenter,c.firstCoverSize,wood,iron);
            rig.secondCover=Cover("Second full-height cover — only centerX changes",c.secondCoverCenter+Vector3.right*rig.secondCoverOffsetX,c.secondCoverSize,wood,iron);
            var texture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/ThirdParty/KayKitAdventurers/knight_texture.png");if(!texture)throw new InvalidOperationException("Missing original Knight texture");
            var player=new GameObject("Player — physical capsule with fixed input tape");player.layer=ProspectRefugeExperiment.PlayerLayer;
            rig.player=player.AddComponent<CharacterController>();rig.player.height=c.capsuleHeight;rig.player.radius=c.capsuleRadius;rig.player.center=Vector3.up*c.capsuleCenterY;
            rig.player.skinWidth=c.skinWidth;rig.player.stepOffset=c.stepOffset;rig.player.minMoveDistance=0;rig.player.slopeLimit=45;
            rig.playerModel=ArticulatedModel(player.transform,"CC0 Knight player — sampled Walking_A and Idle",Mat("Player Knight",new Color(.76f,.96f,.86f),texture));
            rig.playerModelBasePosition=rig.playerModel.localPosition;rig.playerModelBaseRotation=rig.playerModel.localRotation;rig.playerModelBaseScale=rig.playerModel.localScale;
            LayerRecursive(player.transform,ProspectRefugeExperiment.PlayerLayer);
            rig.enemy=new GameObject("Enemy — fixed scripted patrol, declared three-point visibility rule").transform;
            rig.enemyModel=ArticulatedModel(rig.enemy,"CC0 Knight enemy — visible separate layer",Mat("Enemy Knight",new Color(1,.51f,.46f),texture));
            rig.enemyModelBasePosition=rig.enemyModel.localPosition;rig.enemyModelBaseRotation=rig.enemyModel.localRotation;rig.enemyModelBaseScale=rig.enemyModel.localScale;
            LayerRecursive(rig.enemy,ProspectRefugeExperiment.EnemyLayer);
            foreach(var asset in AssetDatabase.LoadAllAssetsAtPath(Knight)) {
                var clip=asset as AnimationClip;if(!clip)continue;
                if(clip.name.EndsWith("Walking_A",StringComparison.OrdinalIgnoreCase))rig.walkingClip=clip;
                if(clip.name.Equals("Idle",StringComparison.OrdinalIgnoreCase)||clip.name.EndsWith("|Idle",StringComparison.OrdinalIgnoreCase))rig.idleClip=clip;
            }
            if(!rig.walkingClip||!rig.idleClip)throw new InvalidOperationException("Actual Knight Walking_A/Idle clips required; inspect imported names rather than invent substitutes");
            rig.playerCamera=Camera("Player view — fixed eye1.65m/pitch8deg, ordinary opaque geometry",c);rig.playerCamera.fieldOfView=c.verticalFieldOfView;
            rig.playerCamera.cullingMask=~((1<<ProspectRefugeExperiment.PlayerLayer)|(1<<ProspectRefugeExperiment.GuideLayer));
            rig.observerCamera=Camera("Observer overhead — synchronized actual actor and ray-hit evidence",c);
            rig.observerCamera.transform.position=c.observerPosition;rig.observerCamera.transform.rotation=Quaternion.Euler(90,0,0);
            rig.observerCamera.orthographic=true;rig.observerCamera.orthographicSize=c.observerOrthographicSize;
            // No physical collider or render wall is removed in either view.
            rig.sightLines=new LineRenderer[3];rig.bodyMarkers=new Transform[3];
            var markerMat=Mat("Declared sample markers",Color.white);
            for(int i=0;i<3;i++) {
                rig.sightLines[i]=Guide("Actual enemy eye to body sample "+i,Color.white,.055f);
                rig.bodyMarkers[i]=Shape("Declared body sample "+i,PrimitiveType.Sphere,Vector3.zero,Vector3.one*.105f,markerMat,null,ProspectRefugeExperiment.GuideLayer).transform;
            }
            rig.enemyEyeMarker=Shape("Declared enemy eye — exact ray origin",PrimitiveType.Sphere,Vector3.zero,Vector3.one*.13f,Mat("Enemy eye marker",new Color(1,.82f,.32f)),null,ProspectRefugeExperiment.GuideLayer).transform;
            rig.actualTravelPath=Guide("Actual travelled capsule path",new Color(.25f,.75f,1),.055f);
            rig.playerFootprint=Guide("Actual capsule footprint",new Color(.25f,.75f,1),.04f);
            rig.enemyFovBoundary=Guide("Own horizontal FOV definition — not a visibility result",new Color(1,.82f,.32f,.32f),.025f);
            rig.ResetExperiment();return rig;
        }
        [MenuItem("Yamyam/Architectural 111/Build Prospect and Refuge scenes")]
        public static void BuildScenes() {
            foreach(var mode in Modes) {
                Build(mode);
                if(!EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),ScenePath(mode)))throw new InvalidOperationException("Actual editable scene save failed: "+mode);
            }
            AssetDatabase.SaveAssets();
        }
        static void ExportRecord(string output,string fingerprint,ProspectRefugeExperiment rig) {
            AssetDatabase.SaveAssets();AssetDatabase.Refresh();var files=new List<FilePin>();
            foreach(string path in Directory.GetFiles(Folder,"*",SearchOption.AllDirectories))files.Add(Pin(path));
            if(File.Exists(Folder+".meta"))files.Add(Pin(Folder+".meta"));files.Sort((a,b)=>String.CompareOrdinal(a.path,b.path));
            var dependencies=new List<FilePin>();
            foreach(string name in new[]{"Knight.fbx","Knight.fbx.meta","knight_texture.png","knight_texture.png.meta","LICENSE.txt","LICENSE.txt.meta","provenance.json"}) {
                string path="Assets/ThirdParty/KayKitAdventurers/"+name;if(!File.Exists(path))throw new InvalidOperationException("Missing asset provenance/import file "+path);dependencies.Add(Pin(path));
            }
            string shaderPath=AssetDatabase.GetAssetPath(Shader.Find("Yamyam/ArchitecturalSurface"));
            if(string.IsNullOrEmpty(shaderPath)||!File.Exists(shaderPath))throw new InvalidOperationException("Original shader dependency is not an editable file");
            dependencies.Add(Pin(shaderPath));if(File.Exists(shaderPath+".meta"))dependencies.Add(Pin(shaderPath+".meta"));
            string target=Path.Combine(output,"scene-record.json");if(File.Exists(target))throw new InvalidOperationException("Preserve prior editable-scene export proof");
            File.WriteAllText(target,JsonUtility.ToJson(new SceneRecord{fingerprint=fingerprint,unityVersion=Application.unityVersion,files=files.ToArray(),sharedDependencies=dependencies.ToArray(),
                scenePaths=new[]{ScenePath("baseline"),ScenePath("shifted")},animationClipNames=new[]{rig.walkingClip.name,rig.idleClip.name}},true));
        }
        static string F(float value) {return value.ToString("R",CultureInfo.InvariantCulture);}
        static string Vec(Vector3 value) {return F(value.x)+","+F(value.y)+","+F(value.z);}
        static void AppendTrace(StringBuilder trace,FrameState state,string stateSha) {
            trace.AppendLine(string.Join(",",state.frame,F(state.timeSeconds),F(state.secondCoverOffsetX),state.appliedCommandFrame,state.appliedCommandId,state.nextCommandId,
                Vec(state.appliedVelocity),Vec(state.playerPosition),Vec(state.requestedPlayerPosition),Vec(state.actualMoveDelta),state.collisionFlags,
                Vec(state.enemyPosition),F(state.enemyYawDegrees),state.enemyPhase,Vec(state.enemyEye),Vec(state.playerCameraEye),Vec(state.cameraRotationEuler),Vec(state.observerCameraPosition),Vec(state.observerCameraRotationEuler),
                state.seenBodySamples,state.blockedBodySamples,state.enemySeesAnyDeclaredBodySample?1:0,state.playerCameraCanObserveEnemyTorso?1:0,
                state.bodyRays[0].seen?1:0,state.bodyRays[1].seen?1:0,state.bodyRays[2].seen?1:0,stateSha));
        }
        public static void Capture() {
            string output=null,fingerprint=null,modeList="baseline,shifted";var args=Environment.GetCommandLineArgs();
            for(int i=0;i<args.Length-1;i++) {
                if(args[i]=="-prospectRefugeOutput")output=args[i+1];
                if(args[i]=="-prospectRefugeFingerprint")fingerprint=args[i+1];
                if(args[i]=="-prospectRefugeModes")modeList=args[i+1];
            }
            if(string.IsNullOrEmpty(output)||!Path.IsPathRooted(output)||string.IsNullOrEmpty(fingerprint)||fingerprint.Length!=64
                ||fingerprint.Trim("0123456789abcdef".ToCharArray()).Length!=0)throw new ArgumentException("Explicit absolute output and64lowercase-hex fingerprint required");
            var requested=modeList.Split(',');var unique=new HashSet<string>();
            foreach(string mode in requested)if(Array.IndexOf(Modes,mode)<0||!unique.Add(mode))throw new ArgumentException("Unknown or duplicate requested mode");
            if(requested.Length<1)throw new ArgumentException("At least one capture mode required");
            foreach(string mode in requested) {
                string dir=Path.Combine(output,mode);
                if(Directory.Exists(dir)&&Directory.GetFileSystemEntries(dir).Length>0)throw new InvalidOperationException("Preserve prior capture/partial output: "+dir);
            }
            if(File.Exists(Path.Combine(output,"scene-record.json")))throw new InvalidOperationException("Use a fresh versioned attempt, preserving old scene record");
            Directory.CreateDirectory(output);BuildScenes();ProspectRefugeExperiment lastRig=null;
            foreach(string mode in requested) {
                var rig=Build(mode);lastRig=rig;rig.previewInPlayMode=false;var c=rig.config;
                string dir=Path.Combine(output,mode);Directory.CreateDirectory(dir);
                byte[] sourceConfig=File.ReadAllBytes(Folder+"/capture-config.json");string configSha=Sha(sourceConfig);
                byte[] tapeBytes=Encoding.UTF8.GetBytes(JsonUtility.ToJson(new TapeRecord{commands=c.commands}));
                string tapeSha=Sha(tapeBytes);File.WriteAllBytes(Path.Combine(dir,"command-tape.json"),tapeBytes);
                File.WriteAllBytes(Path.Combine(dir,"capture-config.json"),sourceConfig);
                var receipt=new ModeReceipt{fingerprint=fingerprint,mode=mode,frames=c.frames,width=c.width,height=c.height,fps=c.fps,configSHA256=configSha,commandTapeSHA256=tapeSha,
                    frameConvention="Frame0 before Move; capture f, then apply command f once for1/60s to capture f+1; both cameras share evaluated frame"};
                File.WriteAllText(Path.Combine(dir,"mode-contract.json"),JsonUtility.ToJson(receipt,true));
                // NewScene can unload transient textures: buffers exist only
                // after Build and are released before any subsequent NewScene.
                var target=new RenderTexture(c.width,c.height,24);target.antiAliasing=2;target.Create();
                var texture=new Texture2D(c.width,c.height,TextureFormat.RGB24,false);
                var trace=new StringBuilder("frame,timeSeconds,secondCoverOffsetX,appliedCommandFrame,appliedCommandId,nextCommandId,commandX,commandY,commandZ,playerX,playerY,playerZ,requestedX,requestedY,requestedZ,actualDeltaX,actualDeltaY,actualDeltaZ,collisionFlags,enemyX,enemyY,enemyZ,enemyYaw,enemyPhase,enemyEyeX,enemyEyeY,enemyEyeZ,cameraEyeX,cameraEyeY,cameraEyeZ,cameraPitch,cameraYaw,cameraRoll,observerX,observerY,observerZ,observerPitch,observerYaw,observerRoll,seenBodySamples,blockedBodySamples,enemySeesAnySample,playerCameraObservesEnemyTorso,headSeen,torsoSeen,hipsSeen,stateSHA256\n");
                try {
                    using(var states=new StreamWriter(Path.Combine(dir,"states.jsonl")))
                    using(var rays=new StreamWriter(Path.Combine(dir,"rays.jsonl")))
                    using(var anchors=new StreamWriter(Path.Combine(dir,"projected-anchors.jsonl"))) {
                        for(int frame=0;frame<c.frames;frame++) {
                            if(rig.Frame!=frame)throw new InvalidOperationException("Shared capture clock drift");
                            string state=JsonUtility.ToJson(rig.CurrentState);states.WriteLine(state);AppendTrace(trace,rig.CurrentState,Sha(Encoding.UTF8.GetBytes(state)));
                            rays.WriteLine(JsonUtility.ToJson(new FrameRays{frame=frame,enemyToBody=rig.BodyRays,playerCameraToEnemy=rig.PlayerObservationRay}));
                            anchors.WriteLine(JsonUtility.ToJson(rig.ProjectedAnchors()));
                            foreach(var pair in new[]{Tuple.Create("player",rig.playerCamera),Tuple.Create("observer",rig.observerCamera)}) {
                                var camera=pair.Item2;camera.targetTexture=target;camera.Render();RenderTexture.active=target;
                                texture.ReadPixels(new Rect(0,0,c.width,c.height),0,0);texture.Apply();
                                string folder=Path.Combine(dir,pair.Item1);Directory.CreateDirectory(folder);File.WriteAllBytes(Path.Combine(folder,frame.ToString("D4")+".jpg"),texture.EncodeToJPG(93));
                            }
                            if(frame<c.frames-1)rig.AdvanceOneFrame();
                        }
                    }
                    File.WriteAllText(Path.Combine(dir,"trace.csv"),trace.ToString());
                } finally {
                    rig.playerCamera.targetTexture=null;rig.observerCamera.targetTexture=null;RenderTexture.active=null;
                    target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(texture);
                }
                string receiptPath=Path.Combine(dir,"mode-complete.json");
                File.WriteAllText(receiptPath+".tmp",JsonUtility.ToJson(receipt,true));File.Move(receiptPath+".tmp",receiptPath);
            }
            ExportRecord(output,fingerprint,lastRig);
            bool both=true;string expectedConfigSha=Sha(File.ReadAllBytes(Folder+"/capture-config.json"));
            string expectedTapeSha=Sha(Encoding.UTF8.GetBytes(JsonUtility.ToJson(new TapeRecord{commands=lastRig.config.commands})));
            foreach(string mode in Modes) {
                string receipt=Path.Combine(output,mode,"mode-complete.json");if(!File.Exists(receipt)){both=false;break;}
                var value=JsonUtility.FromJson<ModeReceipt>(File.ReadAllText(receipt));
                if(value.fingerprint!=fingerprint||value.mode!=mode||value.frames!=600||value.fps!=60||value.width!=1920||value.height!=1080
                    ||value.configSHA256!=expectedConfigSha||value.commandTapeSHA256!=expectedTapeSha||value.cameras==null||value.cameras.Length!=2||value.cameras[0]!="player"||value.cameras[1]!="observer"){both=false;break;}
            }
            if(both)File.WriteAllText(Path.Combine(output,"capture-complete.txt"),fingerprint+"; "+Application.unityVersion+";600frames;two synchronized cameras; fixed physical commands; only second cover offsetX differs");
            EditorApplication.Exit(0);
        }
    }
}
