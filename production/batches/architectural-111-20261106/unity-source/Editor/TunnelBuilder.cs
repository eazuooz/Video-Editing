using System;
using System.IO;
using System.Globalization;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Yamyam.Architectural111.Editor {
    public static class TunnelBuilder {
        const string Folder="Assets/VideoScenes/architectural-111-20261106/03-02";
        static Material Mat(string name,Color col) {
            string path=Folder+"/"+name+".mat";
            var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
            var shader=Shader.Find("Yamyam/ArchitecturalSurface");
            if(!shader)throw new InvalidOperationException("Missing original portable scene surface shader");
            if(!mat){mat=new Material(shader);AssetDatabase.CreateAsset(mat,path);}
            mat.shader=shader;mat.color=col;return mat;
        }
        static GameObject Shape(string name,PrimitiveType type,Vector3 p,Vector3 s,Material m,Transform parent=null,bool solid=true) {
            var go=GameObject.CreatePrimitive(type);go.name=name;go.transform.SetParent(parent,false);
            go.transform.localPosition=p;go.transform.localScale=s;go.GetComponent<Renderer>().sharedMaterial=m;
            if(!solid)UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());return go;
        }
        static LineRenderer Guide(string name,Color color) {
            var g=new GameObject(name).AddComponent<LineRenderer>();g.sharedMaterial=new Material(Shader.Find("Sprites/Default"));
            g.startWidth=g.endWidth=.045f;g.startColor=g.endColor=color;g.numCapVertices=6;return g;
        }
        static Camera CameraAt(string name,Vector3 p,Vector3 target,float size) {
            var c=new GameObject(name).AddComponent<Camera>();c.transform.position=p;c.transform.LookAt(target);
            c.orthographic=true;c.orthographicSize=size;c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=new Color(.018f,.025f,.023f);
            c.nearClipPlane=.04f;c.farClipPlane=80;return c;
        }
        public static TunnelExperiment Build(float width) {
            Directory.CreateDirectory(Folder);AssetDatabase.Refresh();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.36f,.4f,.43f);
            var light=new GameObject("Key light").AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.5f;
            light.transform.rotation=Quaternion.Euler(48,-35,0);light.shadows=LightShadows.Soft;
            var rig=new GameObject("Tunnel width experiment — original implementation").AddComponent<TunnelExperiment>();
            var floor=Mat("Floor",new Color(.10f,.14f,.14f));var wall=Mat("Tunnel stone",new Color(.27f,.31f,.32f));
            var iron=Mat("Minecart iron",new Color(.24f,.38f,.43f));var edge=Mat("Metal rims",new Color(.47f,.58f,.60f));
            var rail=Mat("Rails",new Color(.58f,.59f,.55f));var wood=Mat("Sleepers",new Color(.30f,.21f,.13f));
            var wheelmat=Mat("Wheels",new Color(.09f,.12f,.13f));
            Shape("Ground",PrimitiveType.Cube,new Vector3(0,-.18f,0),new Vector3(9,.3f,12),floor);
            rig.leftWall=Shape("Left boundary",PrimitiveType.Cube,new Vector3(-width/2-.17f,1.15f,0),new Vector3(.34f,2.3f,6),wall).transform;
            // Keep the full-height physical wall. Remove only the near wall's
            // upper render mesh so the observer can see the passing character.
            rig.rightWall=new GameObject("Right boundary — full collision, cutaway render").transform;
            rig.rightWall.position=new Vector3(width/2+.17f,1.15f,0);
            rig.rightWall.gameObject.AddComponent<BoxCollider>().size=new Vector3(.34f,2.3f,6);
            Shape("Near wall cutaway — upper render omitted for observation",PrimitiveType.Cube,new Vector3(0,-.99f,0),new Vector3(.34f,.32f,6),wall,rig.rightWall,false);
            // The roof is deliberately removed for the observer cutaway, not made transparent in gameplay.
            for(int z=-5;z<=5;z++)Shape("Rail sleeper "+z,PrimitiveType.Cube,new Vector3(0,.018f,z),new Vector3(1.7f,.06f,.18f),wood,null,false);
            foreach(float x in new[]{-.52f,.52f})Shape("Rail",PrimitiveType.Cube,new Vector3(x,.07f,0),new Vector3(.09f,.12f,11),rail,null,false);
            var cart=new GameObject("Minecart — chassis, four wheels, open metal bin").transform;
            var collider=cart.gameObject.AddComponent<BoxCollider>();collider.center=new Vector3(0,.65f,0);collider.size=new Vector3(1.5f,1.3f,2.2f);
            Shape("Chassis",PrimitiveType.Cube,new Vector3(0,.45f,0),new Vector3(1.42f,.18f,2.12f),iron,cart,false);
            Shape("Bin bottom",PrimitiveType.Cube,new Vector3(0,.65f,0),new Vector3(1.5f,.13f,2.2f),iron,cart,false);
            foreach(float x in new[]{-.70f,.70f}) {
                Shape("Bin side",PrimitiveType.Cube,new Vector3(x,1.02f,0),new Vector3(.1f,.7f,2.2f),iron,cart,false);
                Shape("Side rim",PrimitiveType.Cube,new Vector3(x,1.4f,0),new Vector3(.1f,.1f,2.2f),edge,cart,false);
            }
            foreach(float z in new[]{-1.05f,1.05f})Shape("Bin end",PrimitiveType.Cube,new Vector3(0,1.02f,z),new Vector3(1.5f,.7f,.1f),iron,cart,false);
            var wheels=new System.Collections.Generic.List<Transform>();
            foreach(float x in new[]{-.63f,.63f})foreach(float z in new[]{-.73f,.73f}) {
                var g=Shape("Flanged wheel",PrimitiveType.Cylinder,new Vector3(x,.26f,z),new Vector3(.47f,.12f,.47f),wheelmat,cart,false);
                g.transform.localRotation=Quaternion.Euler(0,0,90);wheels.Add(g.transform);
            }
            rig.wheels=wheels.ToArray();
            var actor=new GameObject("Player collision capsule");rig.player=actor.AddComponent<CharacterController>();
            rig.player.height=1.8f;rig.player.radius=.36f;rig.player.center=new Vector3(0,.9f,0);rig.player.skinWidth=.01f;
            rig.player.stepOffset=.10f;rig.player.minMoveDistance=0;
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/ThirdParty/KayKitAdventurers/Knight.fbx");
            if(!prefab)throw new InvalidOperationException("Missing licensed articulated Knight model");
            var model=UnityEngine.Object.Instantiate(prefab,actor.transform);model.name="KayKit articulated Knight — CC0";
            var renderers=model.GetComponentsInChildren<Renderer>();Bounds bounds=renderers[0].bounds;
            foreach(var renderer in renderers)bounds.Encapsulate(renderer.bounds);
            model.transform.localScale=Vector3.one*(1.72f/bounds.size.y);
            bounds=renderers[0].bounds;foreach(var renderer in renderers)bounds.Encapsulate(renderer.bounds);
            model.transform.localPosition=new Vector3(-bounds.center.x,-bounds.min.y,-bounds.center.z);
            var texture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/ThirdParty/KayKitAdventurers/knight_texture.png");
            var skin=Mat("Knight texture",Color.white);skin.mainTexture=texture;
            foreach(var renderer in renderers)renderer.sharedMaterial=skin;rig.playerModel=model.transform;
            rig.modelBasePosition=model.transform.localPosition;rig.modelBaseRotation=model.transform.localRotation;rig.modelBaseScale=model.transform.localScale;
            foreach(var asset in AssetDatabase.LoadAllAssetsAtPath("Assets/ThirdParty/KayKitAdventurers/Knight.fbx")) {
                var clip=asset as AnimationClip;if(!clip)continue;
                if(clip.name.EndsWith("Walking_A",StringComparison.OrdinalIgnoreCase))rig.walkingClip=clip;
                if(clip.name.Equals("Idle",StringComparison.OrdinalIgnoreCase)||clip.name.EndsWith("|Idle",StringComparison.OrdinalIgnoreCase))rig.idleClip=clip;
            }
            if(!rig.walkingClip||!rig.idleClip)throw new InvalidOperationException("Missing original Knight Walking_A/Idle animation clips; preserve source and inspect imported clip names");
            rig.clearance=Guide("Side clearance attached to cart and wall",new Color(1,.82f,.32f));
            rig.collisionOutline=Guide("Player collision footprint",new Color(.25f,.95f,.69f));
            rig.travelArrow=Guide("Attempted travel direction",new Color(.25f,.95f,.69f));
            rig.observer=CameraAt("Observer camera — visible geometry",new Vector3(6,8,-10),Vector3.zero,5.5f);
            rig.playerView=CameraAt("Top camera — same physics state",new Vector3(0,12,-.001f),Vector3.zero,5.7f);
            rig.playerView.transform.rotation=Quaternion.Euler(90,0,0);rig.playerView.enabled=false;
            rig.ResetExperiment(width);rig.Step(0);return rig;
        }
        [MenuItem("Yamyam/Architectural 111/Build tunnel experiment")]
        public static void BuildScenes() {
            Build(2.5f);EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),Folder+"/02-narrow.unity");
            Build(3.5f);EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),Folder+"/04-wide.unity");
            AssetDatabase.SaveAssets();
        }
        public static void Capture() {
            string output=null;var args=Environment.GetCommandLineArgs();
            for(int i=0;i<args.Length-1;i++)if(args[i]=="-architecturalOutput")output=args[i+1];
            if(string.IsNullOrEmpty(output))throw new ArgumentException("Explicit output path required");
            Directory.CreateDirectory(output);BuildScenes();
            var target=new RenderTexture(1920,1080,24);target.antiAliasing=2;target.Create();
            var tex=new Texture2D(1920,1080,TextureFormat.RGB24,false);
            foreach(float width in new[]{2.5f,3.5f}) {
                var rig=Build(width);string name=width<3?"narrow":"wide";string dir=Path.Combine(output,name);Directory.CreateDirectory(dir);
                var trace=new StringBuilder("frame,width,sideClearance,playerDiameter,commandX,commandZ,playerX,playerZ,travelled,blocked\n");
                for(int frame=0;frame<270;frame++) {
                    rig.Step(1f/60f);Physics.SyncTransforms();
                    trace.AppendLine(string.Join(",",frame,width.ToString(CultureInfo.InvariantCulture),rig.SideClearance.ToString(CultureInfo.InvariantCulture),rig.playerDiameter.ToString(CultureInfo.InvariantCulture),rig.CommandedVelocity.x.ToString(CultureInfo.InvariantCulture),rig.CommandedVelocity.z.ToString(CultureInfo.InvariantCulture),rig.player.transform.position.x.ToString(CultureInfo.InvariantCulture),rig.player.transform.position.z.ToString(CultureInfo.InvariantCulture),rig.Travelled.ToString(CultureInfo.InvariantCulture),rig.Blocked?"1":"0"));
                    foreach(var pair in new[]{Tuple.Create("observer",rig.observer),Tuple.Create("top",rig.playerView)}) {
                        var camera=pair.Item2;camera.targetTexture=target;camera.Render();RenderTexture.active=target;
                        tex.ReadPixels(new Rect(0,0,1920,1080),0,0);tex.Apply();
                        string dest=Path.Combine(dir,pair.Item1);Directory.CreateDirectory(dest);
                        File.WriteAllBytes(Path.Combine(dest,frame.ToString("D4")+".jpg"),tex.EncodeToJPG(93));
                    }
                }
                File.WriteAllText(Path.Combine(dir,"trace.csv"),trace.ToString());
            }
            File.WriteAllText(Path.Combine(output,"capture-complete.txt"),Application.unityVersion+"; two cameras; 1920x1080; 60 physics steps/sec; simplified original collision experiment");
            EditorApplication.Exit(0);
        }
    }
}
