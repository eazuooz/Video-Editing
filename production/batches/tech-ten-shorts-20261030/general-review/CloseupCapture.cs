using System;
using System.IO;
using System.Globalization;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class CloseupCapture
{
    static readonly CultureInfo Inv=CultureInfo.InvariantCulture;
    static string root;
    const string Scenes="Assets/VideoScenes/GeneralReview";
    static Texture2D pixels;
    static RenderTexture target;
    static void PrepareTarget() {
        target=new RenderTexture(1080,548,24);target.antiAliasing=2;target.Create();
        pixels=new Texture2D(1080,548,TextureFormat.RGB24,false);
    }
    static Material Mat(string key, Color c) {
        string path=Scenes+"/"+key+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(!m){m=new Material(Shader.Find("Unlit/Color"));AssetDatabase.CreateAsset(m,path);}
        m.color=c;EditorUtility.SetDirty(m);return m;
    }
    static void Photo(Camera cam,string dir,int frame) {
        cam.targetTexture=target;cam.Render();RenderTexture.active=target;
        pixels.ReadPixels(new Rect(0,0,target.width,target.height),0,0);pixels.Apply();
        File.WriteAllBytes(Path.Combine(dir,frame.ToString("D4")+".jpg"),pixels.EncodeToJPG(94));
    }
    static string Out(string name) {
        string path=Path.Combine(root,name);Directory.CreateDirectory(path);return path;
    }
    static GameObject Solid(string name,PrimitiveType shape,Vector3 pos,Vector3 scale,Material material) {
        var g=GameObject.CreatePrimitive(shape);g.name=name;g.transform.position=pos;g.transform.localScale=scale;
        g.GetComponent<Renderer>().sharedMaterial=material;return g;
    }
    static LineRenderer Line(string name,Material material,float width) {
        var l=new GameObject(name).AddComponent<LineRenderer>();l.sharedMaterial=material;
        l.startWidth=l.endWidth=width;l.numCapVertices=l.numCornerVertices=5;l.positionCount=2;return l;
    }
    static void CaptureReplay(){
        EditorSceneManager.OpenScene("Assets/VideoScenes/FeedbackRTS/ReplaySquad.unity");
        PrepareTarget();
        var sim=UnityEngine.Object.FindFirstObjectByType<CommandReplay>();
        var cam=UnityEngine.Object.FindFirstObjectByType<Camera>();
        foreach(int seed in new[]{42,7}) {
            string dir=Out("seed-"+seed);
            var csv=new StringBuilder("tick,hp,nextShot\n");sim.ResetMatch(2.85f,seed);
            for(int tick=0;tick<390;tick++){
                sim.Step();csv.AppendLine(tick+","+sim.hitPoints+","+sim.NextShotTick(0));
                if(tick%2==0)Photo(cam,dir,tick/2);
            }
            File.WriteAllText(Path.Combine(dir,"ticks.csv"),csv.ToString());
        }
    }
    static string Screen(Camera cam,Vector3 world) {
        var v=cam.WorldToViewportPoint(world);
        return (v.x*1080).ToString("F2",Inv)+","+((1-v.y)*548).ToString("F2",Inv);
    }
    static void CaptureRope(){
        var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        PrepareTarget();
        var rig=new GameObject("Rope cutaway").AddComponent<RopeRig>();
        var baseMat=Mat("Ground",new Color(.08f,.14f,.15f));
        var postMat=Mat("Post",new Color(.48f,.34f,.23f));
        var wood=Mat("Wood rings",new Color(.60f,.47f,.35f));
        var yellow=Mat("Rope",new Color(1f,.83f,.34f));var red=Mat("Crossing",new Color(1f,.24f,.18f));
        var green=Mat("Contact",new Color(.23f,.99f,.69f));
        Solid("Floor",PrimitiveType.Cube,new Vector3(0,-.12f,0),new Vector3(15,.22f,12),baseMat);
        var post=Solid("Post cross-section",PrimitiveType.Cube,new Vector3(0,.25f,0),new Vector3(2*RopeRig.HalfWidth,.5f,2*RopeRig.HalfDepth),postMat);
        for(int k=0;k<4;k++){float a=.28f+k*.18f;var ring=Line("Wood grain",wood,.017f);ring.transform.SetParent(post.transform,true);ring.loop=true;ring.positionCount=40;for(int i=0;i<40;i++){float r=i*Mathf.PI/20;ring.SetPosition(i,new Vector3(a*Mathf.Cos(r),.52f,.7f*a*Mathf.Sin(r)));}}
        rig.rope=Line("Rope",yellow,.09f);rig.intersection=Line("Segment inside post",red,.17f);
        rig.cornerMark=Solid("Contact point",PrimitiveType.Sphere,Vector3.zero,Vector3.one*.24f,green);
        rig.winchArm=Solid("Winch guide",PrimitiveType.Cube,Vector3.zero,Vector3.one,wood).transform;
        var hitch=Solid("Anchor",PrimitiveType.Cylinder,new Vector3(-3.65f,.75f,1.5f),new Vector3(.34f,.76f,.34f),wood);
        var vehicle=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/VideoScenes/FeedbackRTS/Models/Jeep_A.fbx");
        var model=(GameObject)PrefabUtility.InstantiatePrefab(vehicle);var anchor=new GameObject("Jeep with winch").transform;
        model.transform.SetParent(anchor,false);model.transform.localRotation=Quaternion.Euler(0,90,0);
        var rs=model.GetComponentsInChildren<Renderer>();var bounds=rs[0].bounds;
        var army=AssetDatabase.LoadAssetAtPath<Material>("Assets/VideoScenes/FeedbackRTS/Squad.mat");
        foreach(var r in rs){bounds.Encapsulate(r.bounds);var slots=r.sharedMaterials;for(int j=0;j<slots.Length;j++)slots[j]=army;r.sharedMaterials=slots;}
        model.transform.localPosition=-new Vector3(bounds.center.x,bounds.min.y,bounds.center.z);
        anchor.localScale=Vector3.one*(1.55f/Mathf.Max(bounds.size.x,bounds.size.z));rig.jeep=anchor;
        var light=new GameObject("Sun").AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.4f;light.transform.rotation=Quaternion.Euler(55,-32,0);
        RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=Color.gray;
        var cam=new GameObject("Teaching camera").AddComponent<Camera>();cam.orthographic=true;cam.orthographicSize=2.65f;
        cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.055f,.095f,.10f);cam.targetTexture=target;
        foreach(string mode in new[]{"side","direct","wrapped"}) {
            bool side=mode=="side";post.SetActive(!side);hitch.transform.position=new Vector3(side?-2.15f:-3.65f,.52f,side?0:1.50f);
            hitch.transform.localScale=new Vector3(.32f,.53f,.32f);cam.orthographicSize=side?1.67f:2.65f;
            cam.transform.position=side?new Vector3(0,1.8f,-9):new Vector3(0,10,0);
            if(side)cam.transform.LookAt(new Vector3(0,.7f,0));else cam.transform.rotation=Quaternion.LookRotation(Vector3.down,Vector3.forward);
            string dir=Out(mode);var csv=new StringBuilder("pose,hit,wrapped,anchorX,anchorY,endX,endY,cornerX,cornerY\n");
            for(int i=0;i<=90;i++){
                rig.Pose(mode,i/90f);Photo(cam,dir,i);
                csv.AppendLine(i+","+(rig.Intersects?1:0)+","+(rig.Wrapped?1:0)+","+Screen(cam,rig.Anchor)+","+Screen(cam,rig.End)+","+Screen(cam,rig.Contact));
            }
            File.WriteAllText(Path.Combine(dir,"poses.csv"),csv.ToString());
        }
        cam.targetTexture=null;rig.Pose("wrapped",1);EditorSceneManager.SaveScene(scene,Scenes+"/RopeAroundPost.unity");AssetDatabase.SaveAssets();
    }
    public static void Run(){
        try{
            string device=SystemInfo.graphicsDeviceName.ToLowerInvariant();
            if(!device.Contains("basic render")&&!device.Contains("warp"))throw new Exception("Expected WARP: "+device);
            root=Environment.GetEnvironmentVariable("YAMYAM_GENERAL_REVIEW");GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;
            CaptureReplay();CaptureRope();File.WriteAllText(Path.Combine(root,"complete.txt"),device);EditorApplication.Exit(0);
        }catch(Exception error){Debug.LogException(error);EditorApplication.Exit(1);}
    }
}
