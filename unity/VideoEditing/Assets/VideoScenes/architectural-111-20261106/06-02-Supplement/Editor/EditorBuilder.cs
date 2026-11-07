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

namespace Yamyam.Architectural111.ProspectRefugeSupplement.Editor {
    public static class EditorBuilder {
        const string Folder="Assets/VideoScenes/architectural-111-20261106/06-02-Supplement";
        const string Knight="Assets/ThirdParty/KayKitAdventurers/Knight.fbx";
        const string SharedShader="Assets/VideoScenes/architectural-111-20261106/ArchitecturalSurface.shader";
        static readonly string[] Modes={"scale","protected","atrium","structure","openings","refuge","courtyard","plaza","alcove","flying","shield","boss","footings"};
        static readonly List<AnchorDefinition> Anchors=new List<AnchorDefinition>();
        static readonly List<RayDefinition> Rays=new List<RayDefinition>();
        static string ActiveMode;
        static Material stone,wood,iron,blue,orange,leaf,white,red,green;
        [Serializable] sealed class Pin {public string path,sha256;public long bytes;}
        [Serializable] sealed class ModeRecord {
            public string fingerprint,mode,sourceKind="our-authored-illustration",configSHA256,frameConvention;
            public int frames,fps,width,height;public string[] cameras={"player","observer"};
            public bool actualSceneSaved;public string actualScenePath;
        }
        [Serializable] sealed class SceneRecord {
            public string fingerprint,mode,unityVersion,sourceKind="our-authored-illustration";
            public string[] scenePaths,animationClipNames;public Pin[] files,dependencies;
            public bool actualSceneFilesSaved;
        }
        static string Sha(byte[] bytes){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();}
        static Pin FilePin(string path){var b=File.ReadAllBytes(path);return new Pin{path=path.Replace('\\','/'),sha256=Sha(b),bytes=b.LongLength};}
        static SupplementConfig Config(){
            var c=JsonUtility.FromJson<SupplementConfig>(File.ReadAllText(Folder+"/config.json"));
            if(c.frames!=720||c.fps!=60||c.width!=1920||c.height!=1080||c.scenes==null||c.scenes.Length!=Modes.Length||c.sceneFolder!=Folder)throw new InvalidOperationException("Selected supplementary capture contract changed");
            int next=0;foreach(var x in c.encounterCommands){if(x.startFrame!=next||x.endFrameExclusive<=next||string.IsNullOrEmpty(x.id))throw new InvalidOperationException("Invalid shared encounter command tape");next=x.endFrameExclusive;}
            if(next!=c.frames)throw new InvalidOperationException("Tape does not cover finite capture");
            var seen=new HashSet<string>();foreach(var x in c.scenes)if(Array.IndexOf(Modes,x.mode)<0||!seen.Add(x.mode)||string.IsNullOrEmpty(x.sceneFile)||x.sceneFile.Contains("/")||x.sceneFile.Contains("\\"))throw new InvalidOperationException("Invalid independent editable scene mapping");
            return c;
        }
        static string ScenePath(SupplementConfig c,string mode){foreach(var x in c.scenes)if(x.mode==mode)return Folder+"/"+x.sceneFile;throw new ArgumentException("Unknown mode");}
        static Material Mat(string name,Color color,Texture texture=null){
            string path=Folder+"/Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
            var shader=AssetDatabase.LoadAssetAtPath<Shader>(SharedShader);if(!shader)throw new InvalidOperationException("Pinned explicit shared ArchitecturalSurface shader dependency is required");
            if(!m){m=new Material(shader);AssetDatabase.CreateAsset(m,path);}m.shader=shader;m.color=color;m.mainTexture=texture;EditorUtility.SetDirty(m);return m;
        }
        static void Layer(Transform t,int layer){t.gameObject.layer=layer;foreach(Transform child in t)Layer(child,layer);}
        static Transform Shape(string name,PrimitiveType type,Vector3 p,Vector3 size,Material m,bool solid=true,Transform parent=null,int layer=Experiment.EnvironmentLayer){
            var go=GameObject.CreatePrimitive(type);go.name=name;go.layer=layer;go.transform.SetParent(parent,false);go.transform.localPosition=p;go.transform.localScale=size;go.GetComponent<Renderer>().sharedMaterial=m;
            if(!solid)UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());return go.transform;
        }
        static Transform Box(string name,Vector3 p,Vector3 size,Material m,bool solid=true,Transform parent=null,int layer=Experiment.EnvironmentLayer){return Shape(name,PrimitiveType.Cube,p,size,m,solid,parent,layer);}
        static void Anchor(string id,Transform target,Vector3 localPoint,string role){Anchors.Add(new AnchorDefinition{id=id,target=target,localPoint=localPoint,role=role});}
        static Transform Point(string id,Vector3 p,string role){var t=new GameObject(id).transform;t.position=p;Anchor(id,t,Vector3.zero,role);return t;}
        static LineRenderer Guide(string name,Color color,float width=.04f){
            var go=new GameObject(name);go.layer=Experiment.GuideLayer;var l=go.AddComponent<LineRenderer>();string path=Folder+"/Materials/Observer guides.mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(!m){m=new Material(Shader.Find("Sprites/Default"));AssetDatabase.CreateAsset(m,path);}l.sharedMaterial=m;l.startColor=l.endColor=color;l.startWidth=l.endWidth=width;l.useWorldSpace=true;l.numCapVertices=6;l.shadowCastingMode=ShadowCastingMode.Off;return l;
        }
        static void Ray(string id,string meaning,Transform from,Vector3 fromPoint,Transform to,Vector3 toPoint){Rays.Add(new RayDefinition{id=id,meaning=meaning,from=from,fromLocal=fromPoint,to=to,toLocal=toPoint});}
        static void BodyRays(Transform threat,Transform player,string prefix){
            Ray(prefix+"-head","Declared threat direction to head sample; not whole mesh visibility",threat,Vector3.up*1.65f,player,Vector3.up*1.55f);
            Ray(prefix+"-torso","Declared threat direction to torso sample",threat,Vector3.up*1.65f,player,Vector3.up*.95f);
            Ray(prefix+"-hips","Declared threat direction to hips sample",threat,Vector3.up*1.65f,player,Vector3.up*.55f);
        }
        static void Label(string text,Vector3 p,Camera camera){
            var go=new GameObject("Observer label: "+text);go.layer=Experiment.GuideLayer;go.transform.position=p;go.transform.rotation=Quaternion.LookRotation(p-camera.transform.position);
            var tm=go.AddComponent<TextMesh>();tm.text=text;tm.anchor=TextAnchor.MiddleCenter;tm.alignment=TextAlignment.Center;tm.fontSize=48;tm.characterSize=.055f;tm.color=new Color(1,.84f,.35f);
            string fontPath=Folder+"/Materials/NativeGuideFont.asset";var font=AssetDatabase.LoadAssetAtPath<Font>(fontPath);
            if(!font){font=Font.CreateDynamicFontFromOSFont("Malgun Gothic",48);if(!font)throw new InvalidOperationException("Native Korean guide font is missing");font.name="Native guide OS-font descriptor";AssetDatabase.CreateAsset(font,fontPath);EditorUtility.SetDirty(font);}
            // Persist the font descriptor for scene reload; do not redistribute
            // the external Windows font binary. Its OS dependency is pinned by
            // the CPU preparation receipt and must be rechecked by the caller.
            tm.font=font;go.GetComponent<Renderer>().sharedMaterial=tm.font.material;
        }
        static ModelRest Actor(string name,Transform parent,Material m,float height=1.72f){
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(Knight);if(!prefab)throw new InvalidOperationException("Pinned CC0 Knight FBX missing");var go=UnityEngine.Object.Instantiate(prefab,parent);go.name=name;
            var rs=go.GetComponentsInChildren<Renderer>();if(rs.Length==0)throw new InvalidOperationException("Knight renderer missing");Bounds bounds=rs[0].bounds;foreach(var r in rs)bounds.Encapsulate(r.bounds);
            if(bounds.size.y<=0)throw new InvalidOperationException("Invalid Knight bounds");go.transform.localScale=Vector3.one*(height/bounds.size.y);bounds=rs[0].bounds;foreach(var r in rs)bounds.Encapsulate(r.bounds);
            Vector3 origin=parent.position;go.transform.position+=new Vector3(origin.x-bounds.center.x,origin.y-bounds.min.y,origin.z-bounds.center.z);
            foreach(var r in rs)r.sharedMaterial=m;foreach(var a in go.GetComponentsInChildren<Animator>()){a.applyRootMotion=false;a.enabled=false;}foreach(var a in go.GetComponentsInChildren<Animation>())a.enabled=false;foreach(var x in go.GetComponentsInChildren<Collider>())UnityEngine.Object.DestroyImmediate(x);
            return new ModelRest{model=go.transform,position=go.transform.localPosition,rotation=go.transform.localRotation,scale=go.transform.localScale};
        }
        static Transform Enemy(Experiment e,string name,Vector3 p,bool second=false,float height=1.72f){
            var t=new GameObject(name).transform;t.position=p;t.rotation=Quaternion.Euler(0,270,0);var model=Actor(name+" articulated Knight",t,red,height);Layer(t,Experiment.EnemyLayer);
            var cap=t.gameObject.AddComponent<CapsuleCollider>();cap.height=height;cap.radius=height*.23f;cap.center=Vector3.up*height*.5f;
            if(second){e.secondEnemy=t;e.secondEnemyModel=model;}else{e.enemy=t;e.enemyModel=model;}Anchor(name+"-eye",t,Vector3.up*height*.95f,"Declared actor eye, not game AI");return t;
        }
        static void Bench(string name,Vector3 p){
            var root=new GameObject(name).transform;root.position=p;
            for(int i=0;i<4;i++)Box("Seat plank",new Vector3(0,.42f,(i-1.5f)*.12f),new Vector3(1.8f,.1f,.1f),wood,true,root);
            foreach(float x in new[]{-.65f,.65f})foreach(float z in new[]{-.17f,.17f})Box("Bench leg",new Vector3(x,.2f,z),new Vector3(.12f,.4f,.12f),wood,true,root);
            Box("Bench back",new Vector3(0,.8f,.28f),new Vector3(1.8f,.12f,.1f),wood,true,root);
        }
        static Transform Chest(Vector3 p,Experiment e){
            var root=new GameObject("Recognizable hidden treasure chest").transform;root.position=p;
            Box("Wood chest body",new Vector3(0,.35f,0),new Vector3(1.1f,.7f,.65f),wood,true,root);
            foreach(float x in new[]{-.36f,.36f})Box("Chest iron strap",new Vector3(x,.35f,0),new Vector3(.09f,.72f,.67f),iron,false,root);
            var lid=new GameObject("Chest lid pivot").transform;lid.SetParent(root,false);lid.localPosition=new Vector3(0,.7f,.325f);Box("Chest lid",new Vector3(0,.08f,-.325f),new Vector3(1.1f,.16f,.65f),wood,true,lid);e.chestLid=lid;
            Box("Gold lock",new Vector3(0,.48f,-.35f),new Vector3(.15f,.2f,.06f),orange,false,root);Anchor("hidden-item-center",root,Vector3.up*.5f,"Item concealed by real projecting wall");return root;
        }
        static void Tree(Vector3 p){
            var t=new GameObject("Own modeled tree screening").transform;t.position=p;Shape("Trunk",PrimitiveType.Cylinder,new Vector3(0,1.2f,0),new Vector3(.24f,1.2f,.24f),wood,true,t);
            foreach(Vector3 x in new[]{new Vector3(0,2.7f,0),new Vector3(-.6f,2.3f,.2f),new Vector3(.6f,2.4f,0)})Shape("Foliage solid illustration",PrimitiveType.Sphere,x,new Vector3(1.5f,1.6f,1.4f),leaf,true,t);
        }
        static void Hearth(Vector3 p){
            var t=new GameObject("Central hearth with logs and stones").transform;t.position=p;
            for(int i=0;i<12;i++){float a=i*Mathf.PI/6;Shape("Hearth stone",PrimitiveType.Sphere,new Vector3(Mathf.Cos(a)*.7f,.15f,Mathf.Sin(a)*.7f),new Vector3(.4f,.3f,.3f),stone,true,t);}
            for(int i=0;i<3;i++){var log=Shape("Visible wood log",PrimitiveType.Cylinder,new Vector3(0,.22f,0),new Vector3(.18f,.55f,.18f),wood,false,t);log.localRotation=Quaternion.Euler(90,i*60,0);}
            Shape("Illustrated warm flame, not thermal simulation",PrimitiveType.Sphere,new Vector3(0,.62f,0),new Vector3(.45f,.8f,.45f),orange,false,t);Anchor("hearth-center",t,Vector3.up*.6f,"Organizing focus of inward refuge");
        }
        static void Ramp(string name,float x,float z0,float z1,float y0,float y1,float width){
            var go=new GameObject(name);go.layer=Experiment.EnvironmentLayer;string meshPath=Folder+"/Meshes/"+ActiveMode+"-"+name+".asset";
            var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);bool created=!mesh;if(created){mesh=new Mesh();mesh.name=name;}else mesh.Clear();float a=x-width*.5f,b=x+width*.5f;
            mesh.vertices=new[]{new Vector3(a,y0,z0),new Vector3(b,y0,z0),new Vector3(a,y1,z1),new Vector3(b,y1,z1),new Vector3(a,y0-.15f,z0),new Vector3(b,y0-.15f,z0),new Vector3(a,y0-.15f,z1),new Vector3(b,y0-.15f,z1)};
            mesh.triangles=new[]{0,2,1,1,2,3,0,4,2,2,4,6,1,3,5,3,7,5,2,6,3,3,6,7,0,1,4,1,5,4};mesh.RecalculateNormals();if(created)AssetDatabase.CreateAsset(mesh,meshPath);EditorUtility.SetDirty(mesh);go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=stone;go.AddComponent<MeshCollider>().sharedMesh=mesh;Anchor(name+"-top",go.transform,new Vector3(x,y1,z1),"Actual ramp endpoint");
        }
        static void Refuge(Experiment e,bool depressed){
            float floor=depressed?-.65f:0;Box("Refuge floor",new Vector3(0,floor-.15f,-2),new Vector3(6,.3f,6),wood);
            if(depressed){Box("Outside ground beyond front",new Vector3(0,-.15f,5),new Vector3(18,.3f,8),stone);Box("Outside ground right",new Vector3(6,-.15f,-2),new Vector3(6,.3f,6),stone);Box("Outside ground left",new Vector3(-6,-.15f,-2),new Vector3(6,.3f,6),stone);}
            // The open-top/rear sectional model is intentional geometry in BOTH
            // cameras, never a camera-specific removed collider or fake x-ray.
            Box("Front right full-height wall",new Vector3(1,1.5f,1),new Vector3(4,3,.3f),wood);
            Box("Front far-left pier",new Vector3(-2.9f,1.5f,1),new Vector3(.2f,3,.3f),wood);
            Box("Window sill",new Vector3(-1.9f,.55f,1),new Vector3(1.8f,1.1f,.3f),wood);
            Box("Window lintel",new Vector3(-1.9f,2.7f,1),new Vector3(1.8f,.6f,.3f),wood);
            Box("Right refuge boundary",new Vector3(3,1.5f,-2),new Vector3(.25f,3,6),wood);
            e.outwardTarget=Point("different-direction-outlook-target",new Vector3(-4,1.8f,5),"Different outward direction, not enemy eye reciprocal ray");
            Shape("Outlook landmark target, excluded from occluding environment",PrimitiveType.Cylinder,new Vector3(-4,.9f,5),new Vector3(.2f,.9f,.2f),orange,false,null,0);
            Box("Outlook marker flag",new Vector3(-3.6f,1.65f,5),new Vector3(.8f,.3f,.05f),orange,false,null,0);
            Enemy(e,"Declared threat on other side",new Vector3(5,0,5));BodyRays(e.enemy,e.player.transform,"declared-threat");Ray("outward-camera-target","Other-direction outward view; not one-way visibility",e.playerCamera.transform,Vector3.zero,e.outwardTarget,Vector3.zero);
            Label("선언한 방향의 몸 가림",new Vector3(2.4f,3.6f,1),e.observerCamera);Label("다른 쪽 바깥 보기",new Vector3(-4,2.4f,5),e.observerCamera);
            Point("window-opening-center",new Vector3(-1.9f,1.75f,1),"Actual opening center; distinct from outward landscape target");
            if(depressed){Bench("Depressed seating left",new Vector3(-1.3f,floor,-3.2f));Bench("Depressed seating right",new Vector3(1.3f,floor,-3.2f));Hearth(new Vector3(0,floor,-1));Box("Deep real exterior overhang",new Vector3(0,2.7f,1.8f),new Vector3(6.6f,.25f,2.4f),wood);Tree(new Vector3(4,0,2.5f));Tree(new Vector3(4.8f,0,4.3f));}
        }
        static void Atrium(Experiment e){
            Box("Public atrium floor",new Vector3(0,-.15f,1),new Vector3(11,.3f,9),stone);
            Box("Private loft floor",new Vector3(0,2.85f,-4.2f),new Vector3(9,.3f,3.4f),wood);
            Box("Enclosed loft rear wall",new Vector3(0,4.25f,-5.9f),new Vector3(9,2.5f,.2f),wood);
            foreach(float x in new[]{-4.5f,0,4.5f})Box("Private room side partition",new Vector3(x,4.25f,-4.2f),new Vector3(.2f,2.5f,3.4f),wood);
            for(int i=0;i<17;i++)Box("Loft railing baluster",new Vector3(-4+i*.5f,3.5f,-2.5f),new Vector3(.045f,1,.045f),iron);
            Box("Low loft handrail",new Vector3(0,4,-2.5f),new Vector3(8.2f,.06f,.06f),iron);Bench("Private room bench",new Vector3(-2.4f,3,-4.9f));
            Enemy(e,"Public circulation personA",new Vector3(-2,0,1.2f));Enemy(e,"Public circulation personB",new Vector3(2,0,2.6f),true);
            Anchor("public-atrium",Point("public-area-point",new Vector3(0,.02f,1.8f),"Public circulation and gathering"),Vector3.zero,"Open public space");Anchor("enclosed-loft",e.player.transform,Vector3.up*.8f,"Higher enclosed private position");
        }
        static void Structure(Experiment e,bool openings){
            Box("Building ground slab",new Vector3(0,-.1f,0),new Vector3(6,.2f,7),stone);var roof=Box("Usable roof slab",new Vector3(0,openings?2.9f:3.05f,0),new Vector3(6,.2f,7),stone);Anchor("actual-roof-surface",roof,Vector3.up*.5f,"Actual roof top, not an invented height marker");
            var cols=new List<Transform>();foreach(float x in new[]{-2.6f,2.6f})foreach(float z in new[]{-2.8f,2.8f}){
                var t=Shape("Illustrated column, not computed load",PrimitiveType.Cylinder,new Vector3(x,1.5f,z),new Vector3(.24f,1.5f,.24f),white);cols.Add(t);Anchor("column-"+cols.Count+"-top",t,Vector3.up,"Cylinder local cap is at y1: actual column top");Box("Column base",new Vector3(x,.1f,z),new Vector3(.5f,.2f,.5f),stone);
            }e.columns=cols.ToArray();
            var walls=new List<Transform>();foreach(float z in new[]{-3.5f,3.5f})for(int i=0;i<2;i++)walls.Add(Box("Withdrawable facade panel",new Vector3(i==0?-1.5f:1.5f,1.5f,z),new Vector3(2.95f,3,.15f),wood));
            e.facadePanels=walls.ToArray();e.facadeRest=new Vector3[walls.Count];for(int i=0;i<walls.Count;i++){e.facadeRest[i]=walls[i].position;Anchor("moving-facade-panel-"+i,walls[i],Vector3.zero,"Actual moving wall-panel center");}
            if(openings){
                var ps=new List<Transform>();foreach(float x in new[]{-1,1})ps.Add(Box("Interior movable partition",new Vector3(x,1.4f,0),new Vector3(.15f,2.8f,5),wood));e.partitions=ps.ToArray();e.partitionRest=new Vector3[ps.Count];for(int i=0;i<ps.Count;i++){e.partitionRest[i]=ps[i].position;Anchor("moving-partition-"+i,ps[i],Vector3.zero,"Actual retracting room partition");}
                foreach(float z in new[]{-3.55f,3.55f}){Box("Ribbon window sill",new Vector3(0,.75f,z),new Vector3(6,1.5f,.17f),stone);Box("Ribbon window header",new Vector3(0,2.8f,z),new Vector3(6,.4f,.17f),stone);}
                Ramp("Actual continuous roof ramp",3.6f,-3.5f,2.5f,0,3,1.4f);Box("Ramp roof landing",new Vector3(3.2f,2.9f,3),new Vector3(2,.2f,2),stone);
                foreach(float x in new[]{-2.9f,2.9f})Box("Roof safety rail",new Vector3(x,3.5f,0),new Vector3(.06f,1,7),iron);
            }
        }
        static void Courtyard(Experiment e){
            Box("Blue courtyard floor",new Vector3(0,-.15f,1.7f),new Vector3(12,.3f,8.6f),blue);
            foreach(float x in new[]{-3.9f,3.9f})Box("Ground beside real lowered entry ramp",new Vector3(x,-.15f,-3.3f),new Vector3(5.4f,.3f,1.4f),blue);
            // Remove the arrival patch from the generic floor by placing entry
            // in front of its extent; it is an actual lower floor and ramp.
            Box("Lowered arrival floor",new Vector3(0,-.85f,-5.2f),new Vector3(3,.3f,2.2f),stone);Ramp("Lowered entry ramp",0,-4.1f,-2.6f,-.7f,0,2.4f);
            foreach(float x in new[]{-1.6f,1.6f})Box("Entry side protection",new Vector3(x,.55f,-4.7f),new Vector3(.3f,2.5f,3),wood);
            Box("Orange destination house rear",new Vector3(0,1.4f,6.5f),new Vector3(4,2.8f,.3f),wood);
            foreach(float x in new[]{-1.5f,1.5f})Box("Orange door jamb",new Vector3(x,1.4f,5),new Vector3(1,2.8f,.3f),orange);Box("Orange doorway lintel",new Vector3(0,2.7f,5),new Vector3(2,.2f,.3f),orange);
            Enemy(e,"Scripted crossing guardA",new Vector3(-3,0,.5f));Enemy(e,"Scripted crossing guardB",new Vector3(3,0,2.2f),true);BodyRays(e.enemy,e.player.transform,"guardA-to-declared-body");BodyRays(e.secondEnemy,e.player.transform,"guardB-to-declared-body");
            Anchor("lowered-arrival",Point("entry-point",new Vector3(0,-.7f,-5.5f),"Scripted initial observation"),Vector3.zero,"Lower entry floor");Anchor("orange-next-refuge",Point("goal-point",new Vector3(0,1,5.3f),"Next protected doorway"),Vector3.zero,"Goal distinct from route");
        }
        static void Plaza(Experiment e){
            Box("Open plaza",new Vector3(0,-.15f,1),new Vector3(12,.3f,10),stone);Box("Elevated visible path",new Vector3(0,1.45f,-2.8f),new Vector3(10,.3f,2),stone);Box("Crossing visible path",new Vector3(2,.75f,1),new Vector3(2,.25f,6),stone);
            Enemy(e,"Opposing open position",new Vector3(4,0,4));Ray("plaza-view","Illustrated crossing sightline; not multiplayer AI",e.playerCamera.transform,Vector3.zero,e.enemy,Vector3.up*1.4f);
        }
        static void Alcove(Experiment e){
            Box("Item-concealing projecting wall",new Vector3(0,1.2f,0),new Vector3(3,2.4f,.5f),wood);Box("Alcove rear",new Vector3(0,1.3f,2.6f),new Vector3(4,2.6f,.3f),stone);Box("Alcove left return",new Vector3(-2,1.3f,1.3f),new Vector3(.3f,2.6f,2.6f),stone);
            var t=Chest(new Vector3(0,0,1.4f),e);e.outwardTarget=Point("item-look-target",t.position+Vector3.up*.6f,"Hidden item target, not player concealment");Ray("camera-to-hidden-item","Actual ray blocked by projection then clears around edge",e.playerCamera.transform,Vector3.zero,e.outwardTarget,Vector3.zero);
        }
        static void Encounters(Experiment e){
            Box("Shared encounter floor",new Vector3(0,-.2f,0),new Vector3(20,.4f,6),stone);
            if(e.mode=="flying"){
                foreach(var p in new[]{new Vector3(-2,.4f,0),new Vector3(.5f,.85f,0)})Box("Different height jump ledge",p,new Vector3(1.8f,p.y*2,2),wood);
                var t=new GameObject("Recognizable modeled flying drone").transform;e.enemy=t;t.position=new Vector3(4.8f,2.5f,0);t.gameObject.layer=Experiment.EnemyLayer;
                Shape("Drone body",PrimitiveType.Sphere,Vector3.zero,new Vector3(.9f,.55f,.65f),iron,false,t,Experiment.EnemyLayer);
                foreach(float x in new[]{-.65f,.65f}){Box("Drone wing",new Vector3(x,0,0),new Vector3(.7f,.08f,.45f),white,false,t,Experiment.EnemyLayer);Shape("Engine",PrimitiveType.Cylinder,new Vector3(x,-.1f,0),new Vector3(.22f,.15f,.22f),orange,false,t,Experiment.EnemyLayer);}
                Shape("Drone forward eye",PrimitiveType.Sphere,new Vector3(-.4f,0,-.1f),Vector3.one*.2f,red,false,t,Experiment.EnemyLayer);var col=t.gameObject.AddComponent<SphereCollider>();col.radius=.5f;Anchor("flying-enemy-center",t,Vector3.zero,"Own moving drone");
            }else{
                var t=Enemy(e,e.mode=="boss"?"Large open-room enemy":"Shielded burst-firing enemy",new Vector3(4.8f,0,0),false,e.mode=="boss"?3.1f:2.5f);
                if(e.mode=="shield"){
                    Box("Solid partial cover; actual shots decide contact",new Vector3(-1.7f,.5f,0),new Vector3(.5f,1.0f,2),wood);
                    e.enemyShield=Box("Actual enemy shield collider; scripted firing cycle",new Vector3(0,1.1f,.52f),new Vector3(1.2f,2.1f,.16f),iron,true,t);
                    Box("Shield center emblem",new Vector3(0,0,.55f),new Vector3(.2f,.65f,.05f),orange,false,e.enemyShield);
                }
            }
        }
        static Transform Board(string name,Vector3 p){
            var t=new GameObject(name).transform;t.position=p;
            for(int i=0;i<3;i++)Box("Bridge plank",new Vector3(0,0,(i-1)*.38f),new Vector3(2.6f,.15f,.36f),wood,true,t);
            foreach(float x in new[]{-.9f,.9f})Box("Board cross brace",new Vector3(x,-.11f,0),new Vector3(.18f,.1f,1.1f),iron,true,t);
            Anchor(name+"-top-center",t,Vector3.up*.075f,"Actual board top surface");return t;
        }
        static void Footings(Experiment e){
            var hazard=Mat("Illustrated ground hazard, no damage simulation",new Color(.33f,.12f,.11f));Box("Fully visible illustrated hazardous ground",new Vector3(0,-.15f,0),new Vector3(16,.3f,10),hazard);
            foreach(float x in new[]{-4f,4f}){
                var rock=Box("Own flat-topped rock support",new Vector3(x,.2f,0),new Vector3(2,.4f,2),stone);
                foreach(float z in new[]{-.9f,.9f}){var edge=Box("Irregular rock edge",new Vector3(x,.15f,z),new Vector3(1.8f,.3f,.4f),stone);edge.rotation=Quaternion.Euler(0,z>0?7:-7,0);}
                Anchor("rock-"+x.ToString(CultureInfo.InvariantCulture)+"-top",rock,Vector3.up*.5f,"Actual flat support top; own illustrated safe region");
            }
            var pallet=new GameObject("Own ordinary wooden pallet support").transform;
            for(int i=0;i<7;i++)Box("Pallet top slat",new Vector3(0,.35f,(i-3)*.27f),new Vector3(2,.1f,.24f),wood,true,pallet);
            foreach(float x in new[]{-.8f,0,.8f})Box("Pallet foot",new Vector3(x,.15f,0),new Vector3(.2f,.3f,1.9f),wood,true,pallet);
            Anchor("next-pallet-top",pallet,new Vector3(0,.4f,0),"Next actual wooden support");
            Box("Board storage trestle top",new Vector3(-4,.35f,2.2f),new Vector3(2.8f,.1f,1.4f),wood);
            foreach(float x in new[]{-5f,-3f})foreach(float z in new[]{1.7f,2.7f})Box("Storage trestle leg",new Vector3(x,.15f,z),new Vector3(.12f,.3f,.12f),wood);
            e.movableBoard=Board("Own movable board",new Vector3(-4,.475f,2.2f));Board("Second already placed board",new Vector3(2,.325f,0));
            var tool=new GameObject("Own conceptual object-moving tool, not Gravity Gun replica").transform;tool.SetParent(e.player.transform,false);tool.localPosition=new Vector3(.3f,1,.1f);
            Shape("Tool grip",PrimitiveType.Cylinder,Vector3.zero,new Vector3(.12f,.18f,.12f),iron,false,tool,Experiment.PlayerLayer);
            foreach(float z in new[]{-.15f,.15f})Box("Tool prong",new Vector3(.2f,0,z),new Vector3(.4f,.08f,.08f),orange,false,tool,Experiment.PlayerLayer);
            Anchor("own-object-moving-tool",tool,Vector3.zero,"Conceptual tool, no simulated magnetic/GravityGun force");
            Ray("tool-to-board","Conceptual tool connection, actual geometric hit; not force or AI measurement",tool,Vector3.zero,e.movableBoard,Vector3.up*.075f);
            Label("자체 설명: 바닥과 발판의 대비",new Vector3(0,1.5f,2.5f),e.observerCamera);
        }
        public static Experiment Build(string mode){
            if(Array.IndexOf(Modes,mode)<0)throw new ArgumentException("Unknown supplementary mode");var c=Config();
            ActiveMode=mode;Directory.CreateDirectory(Folder+"/Materials");Directory.CreateDirectory(Folder+"/Meshes");AssetDatabase.Refresh();EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);Anchors.Clear();Rays.Clear();
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.42f,.44f,.45f);
            var light=new GameObject("Own stage key light").AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.1f;light.transform.rotation=Quaternion.Euler(45,-30,0);light.shadows=LightShadows.Soft;
            stone=Mat("Stone",new Color(.24f,.30f,.29f));wood=Mat("Wood",new Color(.42f,.29f,.16f));iron=Mat("Iron",new Color(.13f,.16f,.17f));blue=Mat("Courtyard blue",new Color(.12f,.29f,.38f));orange=Mat("Warm goal",new Color(.95f,.58f,.14f));leaf=Mat("Leaf",new Color(.18f,.33f,.22f));white=Mat("White",new Color(.8f,.83f,.79f));red=Mat("Enemy",new Color(.9f,.43f,.36f));green=Mat("Player",new Color(.63f,.9f,.76f));
            var texture=AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/ThirdParty/KayKitAdventurers/knight_texture.png");if(!texture)throw new InvalidOperationException("Pinned original Knight texture missing");green.mainTexture=texture;red.mainTexture=texture;EditorUtility.SetDirty(green);EditorUtility.SetDirty(red);
            var e=new GameObject("OUR ILLUSTRATION: "+mode).AddComponent<Experiment>();e.mode=mode;e.config=c;
            var actor=new GameObject("Player articulated actor");actor.layer=Experiment.PlayerLayer;e.player=actor.AddComponent<CharacterController>();e.player.height=c.playerHeight;e.player.radius=c.playerRadius;e.player.center=Vector3.up*c.playerHeight*.5f;e.player.skinWidth=.01f;e.player.stepOffset=.15f;e.player.minMoveDistance=0;
            e.playerModel=Actor("CC0 Knight player",actor.transform,green);Layer(actor.transform,Experiment.PlayerLayer);Anchor("player-head",actor.transform,Vector3.up*1.55f,"Declared point, not whole mesh visibility");Anchor("player-torso",actor.transform,Vector3.up*.95f,"Declared point");
            foreach(var a in AssetDatabase.LoadAllAssetsAtPath(Knight)){var clip=a as AnimationClip;if(!clip)continue;if(clip.name.EndsWith("Walking_A",StringComparison.OrdinalIgnoreCase))e.walkingClip=clip;if(clip.name.Equals("Idle",StringComparison.OrdinalIgnoreCase)||clip.name.EndsWith("|Idle",StringComparison.OrdinalIgnoreCase))e.idleClip=clip;}
            if(!e.walkingClip||!e.idleClip)throw new InvalidOperationException("Exact imported Idle/Walking_A animation clips required");
            e.playerCamera=new GameObject("Player/main view").AddComponent<Camera>();e.observerCamera=new GameObject("Observer guide view").AddComponent<Camera>();
            foreach(var cam in new[]{e.playerCamera,e.observerCamera}){cam.enabled=false;cam.aspect=c.width/(float)c.height;cam.fieldOfView=55;cam.nearClipPlane=.04f;cam.farClipPlane=80;cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.012f,.018f,.018f);}
            bool firstPerson=mode=="protected"||mode=="refuge"||mode=="atrium"||mode=="openings"||mode=="courtyard"||mode=="alcove"||mode=="plaza";
            e.playerCamera.cullingMask=~(1<<Experiment.GuideLayer);if(firstPerson)e.playerCamera.cullingMask&=~(1<<Experiment.PlayerLayer);
            e.observerCamera.transform.position=c.observerPosition;e.observerCamera.transform.rotation=Quaternion.LookRotation(c.observerLookAt-c.observerPosition);
            if(mode!="refuge"&&mode!="courtyard")Box("Shared dark stage ground",new Vector3(0,-.18f,0),new Vector3(22,.3f,18),stone);
            if(mode=="scale"){e.boundaries=new[]{Box("Same body left boundary",new Vector3(-.55f,1.5f,0),new Vector3(.15f,3,4),wood),Box("Same body right boundary",new Vector3(.55f,1.5f,0),new Vector3(.15f,3,4),wood)};foreach(var x in e.boundaries)Anchor(x.name,x,Vector3.zero,"Changing boundary with unchanged articulated body");}
            else if(mode=="protected"||mode=="refuge")Refuge(e,mode=="refuge");else if(mode=="atrium")Atrium(e);else if(mode=="structure"||mode=="openings")Structure(e,mode=="openings");else if(mode=="courtyard")Courtyard(e);else if(mode=="plaza")Plaza(e);else if(mode=="alcove")Alcove(e);else if(mode=="footings")Footings(e);else Encounters(e);
            e.anchorDefinitions=Anchors.ToArray();e.rayDefinitions=Rays.ToArray();e.rayLines=new LineRenderer[Rays.Count];for(int i=0;i<Rays.Count;i++)e.rayLines[i]=Guide(Rays[i].id,new Color(.2f,.9f,.65f));e.travelledLine=Guide("Actual/scripted route by declared mode",new Color(.2f,.7f,1),.035f);
            e.playerShotMaterial=orange;e.enemyShotMaterial=red;e.ResetExperiment();return e;
        }
        static void SaveScene(string mode){var e=Build(mode);if(!EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),ScenePath(e.config,mode)))throw new InvalidOperationException("Actual supplementary scene save failed");}
        [MenuItem("Yamyam/Architectural 111/Build supplementary Prospect Refuge scenes")]
        public static void BuildScenes(){foreach(string mode in Modes)SaveScene(mode);AssetDatabase.SaveAssets();}
        static void WriteSceneRecord(string output,string fp,Experiment rig,string[] actualScenes,string mode){
            AssetDatabase.SaveAssets();var files=new List<Pin>();foreach(string f in Directory.GetFiles(Folder,"*",SearchOption.AllDirectories))files.Add(FilePin(f));if(File.Exists(Folder+".meta"))files.Add(FilePin(Folder+".meta"));files.Sort((a,b)=>String.CompareOrdinal(a.path,b.path));
            var deps=new List<Pin>();foreach(string x in new[]{"Knight.fbx","Knight.fbx.meta","knight_texture.png","knight_texture.png.meta","LICENSE.txt","LICENSE.txt.meta","provenance.json","provenance.json.meta"}){string f="Assets/ThirdParty/KayKitAdventurers/"+x;if(!File.Exists(f))throw new InvalidOperationException("Missing original shared asset proof "+f);deps.Add(FilePin(f));}
            if(!File.Exists(SharedShader))throw new InvalidOperationException("Explicit shared shader source is missing");deps.Add(FilePin(SharedShader));if(File.Exists(SharedShader+".meta"))deps.Add(FilePin(SharedShader+".meta"));
            var record=new SceneRecord{fingerprint=fp,mode=mode,unityVersion=Application.unityVersion,actualSceneFilesSaved=true,scenePaths=actualScenes,animationClipNames=new[]{rig.idleClip.name,rig.walkingClip.name},files=files.ToArray(),dependencies=deps.ToArray()};
            string target=Path.Combine(output,"scene-record.json");if(File.Exists(target))throw new InvalidOperationException("Preserve prior actual scene proof");File.WriteAllText(target,JsonUtility.ToJson(record,true));
        }
        public static void Capture(){
            string output=null,fp=null,list=null;var args=Environment.GetCommandLineArgs();for(int i=0;i<args.Length-1;i++){if(args[i]=="-supplementOutput")output=args[i+1];if(args[i]=="-supplementFingerprint")fp=args[i+1];if(args[i]=="-supplementModes")list=args[i+1];}
            if(string.IsNullOrEmpty(output)||!Path.IsPathRooted(output)||string.IsNullOrEmpty(fp)||fp.Length!=64||fp.Trim("0123456789abcdef".ToCharArray()).Length!=0||string.IsNullOrEmpty(list))throw new ArgumentException("Explicit absolute output,64hex fingerprint and selected mode list required");
            var requested=list.Split(',');var unique=new HashSet<string>();foreach(string m in requested)if(Array.IndexOf(Modes,m)<0||!unique.Add(m))throw new ArgumentException("Unknown/duplicate supplementary mode");
            if(Directory.Exists(output)&&Directory.GetFileSystemEntries(output).Length>0)throw new InvalidOperationException("Preserve previous/partial supplementary attempt; use a fresh versioned directory");Directory.CreateDirectory(output);
            var actualScenes=new List<string>();Experiment last=null;
            foreach(string mode in requested){
                var e=Build(mode);last=e;e.previewInPlayMode=false;var c=e.config;string scene=ScenePath(c,mode);
                if(!EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),scene))throw new InvalidOperationException("Actual scene save failed");actualScenes.Add(scene);AssetDatabase.SaveAssets();
                string dir=Path.Combine(output,mode);Directory.CreateDirectory(dir);byte[] config=File.ReadAllBytes(Folder+"/config.json");File.WriteAllBytes(Path.Combine(dir,"config.json"),config);
                var contract=new ModeRecord{fingerprint=fp,mode=mode,frames=c.frames,fps=c.fps,width=c.width,height=c.height,configSHA256=Sha(config),frameConvention=c.frameConvention,actualSceneSaved=true,actualScenePath=scene};
                File.WriteAllText(Path.Combine(dir,"mode-contract.json"),JsonUtility.ToJson(contract,true));
                // A completed mode keeps its own pre-capture saved-scene proof
                // even when a later requested mode fails. Resume in a fresh
                // attempt; never overwrite this partial or complete attempt.
                WriteSceneRecord(dir,fp,e,new[]{scene},mode);
                var target=new RenderTexture(c.width,c.height,24);target.antiAliasing=2;target.Create();var image=new Texture2D(c.width,c.height,TextureFormat.RGB24,false);
                try{
                    using(var states=new StreamWriter(Path.Combine(dir,"states.jsonl")))using(var rays=new StreamWriter(Path.Combine(dir,"rays.jsonl")))using(var anchors=new StreamWriter(Path.Combine(dir,"projected-anchors.jsonl"))){
                        for(int frame=0;frame<c.frames;frame++){
                            if(e.Frame!=frame)throw new InvalidOperationException("Supplementary shared integer frame drift");states.WriteLine(JsonUtility.ToJson(e.CurrentState));rays.WriteLine(JsonUtility.ToJson(new RayFrame{frame=frame,rays=e.CurrentRays}));anchors.WriteLine(JsonUtility.ToJson(e.ProjectedAnchors()));
                            foreach(var pair in new[]{Tuple.Create("player",e.playerCamera),Tuple.Create("observer",e.observerCamera)}){var cam=pair.Item2;cam.targetTexture=target;cam.Render();RenderTexture.active=target;image.ReadPixels(new Rect(0,0,c.width,c.height),0,0);image.Apply();string folder=Path.Combine(dir,pair.Item1);Directory.CreateDirectory(folder);File.WriteAllBytes(Path.Combine(folder,frame.ToString("D4")+".jpg"),image.EncodeToJPG(93));}
                            if(frame<c.frames-1)e.AdvanceOneFrame();
                        }
                    }
                }finally{e.playerCamera.targetTexture=null;e.observerCamera.targetTexture=null;RenderTexture.active=null;target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(image);}
                string done=Path.Combine(dir,"mode-complete.json");File.WriteAllText(done+".tmp",JsonUtility.ToJson(contract,true));File.Move(done+".tmp",done);
            }
            WriteSceneRecord(output,fp,last,actualScenes.ToArray(),"selected-aggregate");File.WriteAllText(Path.Combine(output,"capture-complete.txt"),fp+"; actual selected modes="+list+"; own illustration;720frames/60fps;two synchronized cameras");EditorApplication.Exit(0);
        }
    }
}
