using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

// Deterministic authored engine demonstration. Wallet outcomes are executed C#,
// while paths/labels in Motion Canvas are explicitly explanatory annotations.
public static class AiCraftSampleBuilder
{
    const string Base = "Assets/AiCraftShopSample";
    const int W = 1920, H = 1080, Fps = 60, Frames = 1560;
    static Scene scene, previous;
    static Camera camera;
    static GameObject hero, potion;
    static Dictionary<string, AnimationClip> clips;
    static RenderTexture target;
    static Texture2D pixels;
    static System.Diagnostics.Process encoder;
    static Stream stream;
    static int frame;
    static bool full, prepared;
    static FrameState pendingState;
    static readonly int[] Samples = {0,90,210,285,330,370,430,560,630,770,870,925,1010,1170,1280,1460,1559};
    static List<FrameState> states = new List<FrameState>();
    static string Out => AiCraftSampleBridge.Output;
    [Serializable] public class FrameState { public int frame,gold,inventory; public string result,clip; public float heroX,heroY,potionX,potionY; }
    [Serializable] public class Capture { public int width=W,height=H,fps=Fps,frames=Frames; public string unity=Application.unityVersion,urp="17.6.0",scenePath=Base+"/ShopSample.unity",kind="self-authored-engine-explanation"; public List<FrameState> timeline; }
    public static void Run(string mode)
    {
        if (encoder != null) throw new Exception("Sample capture already running");
        full = mode == "render";
        var video = Path.Combine(Out,"unity-shop-v1.mp4");
        if (full && File.Exists(video)) throw new Exception("Preserving existing render; choose a new revision explicitly");
        previous = SceneManager.GetActiveScene();
        scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
        SceneManager.SetActiveScene(scene);
        Directory.CreateDirectory(Base); Directory.CreateDirectory(Base+"/Materials");
        Build();
        EditorSceneManager.SaveScene(scene,Base+"/ShopSample.unity");
        SceneManager.SetActiveScene(previous);
        target = new RenderTexture(W,H,24,RenderTextureFormat.ARGB32) { antiAliasing=4 };
        target.Create();
        pixels = new Texture2D(W,H,TextureFormat.RGBA32,false);
        frame=0; prepared=false; states.Clear();
        if(full)
        {
            var start = new System.Diagnostics.ProcessStartInfo("ffmpeg",$"-hide_banner -loglevel error -n -f rawvideo -pixel_format rgba -video_size {W}x{H} -framerate {Fps} -i pipe:0 -vf vflip -an -c:v libx264 -preset fast -crf 17 -pix_fmt yuv420p -movflags +faststart \"{video}\"") { UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardError=true };
            encoder = System.Diagnostics.Process.Start(start);
            stream = encoder.StandardInput.BaseStream;
        }
        EditorApplication.update += Tick;
    }
    static Material Mat(string name, Color color, float metal=0, float smooth=.35f)
    {
        string path=Base+"/Materials/"+name+".mat";
        var m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(!m){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}
        m.SetColor("_BaseColor",color);m.SetFloat("_Metallic",metal);m.SetFloat("_Smoothness",smooth);return m;
    }
    static Color Hex(string s) { ColorUtility.TryParseHtmlString(s,out var c);return c; }
    static GameObject Part(string name, PrimitiveType type, Vector3 pos, Vector3 scale, Material mat, Transform parent=null)
    {
        var g=GameObject.CreatePrimitive(type);g.name=name;g.layer=31;
        if(parent)g.transform.SetParent(parent,false);
        g.transform.localPosition=pos;g.transform.localScale=scale;
        g.GetComponent<Renderer>().sharedMaterial=mat;Object.DestroyImmediate(g.GetComponent<Collider>());return g;
    }
    static void Build()
    {
        var wood=Mat("Walnut",Hex("#684436"));var edge=Mat("WarmWood",Hex("#b78b57"));
        var teal=Mat("TealFabric",Hex("#397e78"));var cream=Mat("CreamFabric",Hex("#e8cf83"));
        var ground=Mat("Stage",Hex("#131c20"));var rim=Mat("StageRim",Hex("#36534f"),.25f);
        var gold=Mat("Gold",Hex("#edbf60"),.6f);var red=Mat("Potion",Hex("#e57376"),.15f,.7f);
        var glass=Mat("BottleNeck",Hex("#b8ded8"),.2f,.8f);
        RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.32f,.36f,.4f);RenderSettings.fog=false;RenderSettings.skybox=null;
        Part("Stage rim",PrimitiveType.Cylinder,new Vector3(0,-.2f,0),new Vector3(7.3f,.12f,5.4f),rim);
        Part("Stage top",PrimitiveType.Cylinder,new Vector3(0,-.08f,0),new Vector3(7.15f,.06f,5.25f),ground);
        // A visibly constructed shop: legs, planks, trim, striped awning and bottles.
        var shop=new GameObject("Potion stall").transform;shop.position=new Vector3(1.15f,0,-.55f);shop.gameObject.layer=31;
        for(int i=0;i<7;i++)Part("Front plank "+i,PrimitiveType.Cube,new Vector3((i-3)*.29f,.46f,.48f),new Vector3(.275f,.85f,.1f),i%2==0?wood:edge,shop);
        Part("Countertop",PrimitiveType.Cube,new Vector3(0,.96f,0),new Vector3(2.28f,.15f,1.12f),edge,shop);
        for(int i=-1;i<=1;i+=2){Part("Awning post",PrimitiveType.Cylinder,new Vector3(i*1.06f,1.5f,-.46f),new Vector3(.09f,1.5f,.09f),wood,shop);}
        for(int i=0;i<8;i++) { var roof=Part("Striped roof "+i,PrimitiveType.Cube,new Vector3((i-3.5f)*.3f,2.94f,0),new Vector3(.3f,.09f,1.5f),i%2==0?teal:cream,shop);roof.transform.localRotation=Quaternion.Euler(-9,0,0);Part("Valance "+i,PrimitiveType.Cube,new Vector3((i-3.5f)*.3f,2.94f,.75f),new Vector3(.3f,.25f,.07f),i%2==0?teal:cream,shop);}
        for(int i=0;i<3;i++) Bottle("Display potion "+i,new Vector3(1.0f+i*.34f,1.17f,-.52f),.6f,red,glass,wood);
        potion=Bottle("Purchased potion",new Vector3(.56f,1.24f,-.12f),.85f,red,glass,wood);
        // Coin stack and wooden price sign form tangible props, not text substitutes.
        for(int i=0;i<4;i++)Part("Counter coin "+i,PrimitiveType.Cylinder,new Vector3(1.93f,1.07f+i*.035f,-.12f),new Vector3(.19f,.02f,.19f),gold);
        Part("Price sign",PrimitiveType.Cube,new Vector3(.32f,1.23f,-.3f),new Vector3(.38f,.4f,.07f),wood);
        var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/ThirdParty/KayKitAdventurers/Knight.fbx");
        hero=(GameObject)PrefabUtility.InstantiatePrefab(prefab,scene);hero.name="Animated customer — KayKit Knight";
        clips=AssetDatabase.LoadAllAssetsAtPath("Assets/ThirdParty/KayKitAdventurers/Knight.fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToDictionary(c=>c.name);
        var knightMat=Mat("Knight",Color.white,.12f,.45f);knightMat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/ThirdParty/KayKitAdventurers/knight_texture.png"));
        foreach(var t in hero.GetComponentsInChildren<Transform>(true)){t.gameObject.layer=31;if(t.name.Contains("Sword")||t.name.Contains("Shield"))t.gameObject.SetActive(false);}
        foreach(var r in hero.GetComponentsInChildren<Renderer>(true)){r.sharedMaterial=knightMat;if(r is SkinnedMeshRenderer sk)sk.updateWhenOffscreen=true;}
        if(hero.TryGetComponent<Animator>(out var anim))anim.enabled=false;
        var cg=new GameObject("Sample Camera");cg.layer=31;camera=cg.AddComponent<Camera>();camera.enabled=false;
        camera.orthographic=true;camera.orthographicSize=2.82f;camera.nearClipPlane=.05f;camera.farClipPlane=60;camera.backgroundColor=Color.black;camera.clearFlags=CameraClearFlags.SolidColor;camera.cullingMask=1<<31;camera.allowHDR=false;camera.allowMSAA=true;
        camera.transform.position=new Vector3(6.6f,5.2f,9.8f);camera.transform.LookAt(new Vector3(0,1.05f,0));
        var cd=camera.GetUniversalAdditionalCameraData();cd.renderPostProcessing=false;cd.renderShadows=true;
        Light("Key",LightType.Directional,new Vector3(35,-28,0),new Color(1,.88f,.72f),2.0f);
        Light("Fill",LightType.Directional,new Vector3(25,150,0),new Color(.55f,.8f,1),.8f);
        Apply(0);AssetDatabase.SaveAssets();
    }
    static GameObject Bottle(string name,Vector3 p,float s,Material liquid,Material neck,Material cork)
    {
        var g=new GameObject(name);g.layer=31;g.transform.position=p;g.transform.localScale=Vector3.one*s;
        Part("Liquid body",PrimitiveType.Sphere,Vector3.zero,new Vector3(.33f,.42f,.33f),liquid,g.transform);
        Part("Glass neck",PrimitiveType.Cylinder,new Vector3(0,.24f,0),new Vector3(.12f,.12f,.12f),neck,g.transform);
        Part("Cork",PrimitiveType.Cylinder,new Vector3(0,.37f,0),new Vector3(.14f,.045f,.14f),cork,g.transform);
        return g;
    }
    static void Light(string name,LightType type,Vector3 rotation,Color color,float intensity)
    {
        var g=new GameObject(name);g.layer=31;g.transform.rotation=Quaternion.Euler(rotation);var l=g.AddComponent<Light>();l.type=type;l.color=color;l.intensity=intensity;l.cullingMask=1<<31;l.shadows=LightShadows.Soft;
    }
    // One transaction function drives both recorded outcomes and overlay values.
    static bool Buy(ref int wallet,ref int items,int price){if(wallet<price)return false;wallet-=price;items++;return true;}
    static FrameState Apply(int f)
    {
        float t=f/(float)Fps; bool second=t>=11;float local=second?t-11:t;
        int wallet=second?20:100,items=0;string result="waiting";
        if(local>=5.6f)result=Buy(ref wallet,ref items,30)?"purchased":"insufficient-gold";
        string clip=local<3.6f?"Walking_A":local<4.6f?"Idle":local<5.9f?"Interact":!second&&local<8.1f?"Cheer":"Idle";
        float ct=clip=="Interact"?local-4.6f:clip=="Cheer"?local-5.9f:local;
        var a=clips[clip];a.SampleAnimation(hero,clip=="Interact"?Mathf.Min(ct,a.length-.001f):ct%a.length);
        float travel=Mathf.Clamp01(local/3.6f);
        hero.transform.position=new Vector3(Mathf.Lerp(-2.7f,-.28f,travel),0,.50f);
        hero.transform.rotation=Quaternion.Euler(0,90,0);
        potion.SetActive(second||local<7.3f);
        var start=new Vector3(.56f,1.24f,-.12f);potion.transform.position=start;potion.transform.localScale=Vector3.one*.85f;
        if(!second&&local>=5.6f){float u=Mathf.Clamp01((local-5.6f)/1.7f);potion.transform.position=Vector3.Lerp(start,hero.transform.position+new Vector3(.05f,1.2f,.3f),u)+Vector3.up*(Mathf.Sin(u*Mathf.PI)*.8f);potion.transform.localScale=Vector3.one*.85f*(1-Mathf.Clamp01((u-.7f)/.3f));}
        var hp=camera.WorldToViewportPoint(hero.transform.position+Vector3.up*1.3f);var pp=camera.WorldToViewportPoint(potion.transform.position);
        return new FrameState{frame=f,gold=wallet,inventory=items,result=result,clip=clip,heroX=hp.x*W,heroY=(1-hp.y)*H,potionX=pp.x*W,potionY=(1-pp.y)*H};
    }
    static void Tick()
    {
        try
        {
            int f=full?frame:Samples[frame];
            // Let Unity propagate static attachment transforms and scene culling
            // before capturing; large preflight time jumps exposed a one-tick lag.
            if(!prepared){pendingState=Apply(f);prepared=true;EditorApplication.QueuePlayerLoopUpdate();return;}
            var state=pendingState;
            var req=new UniversalRenderPipeline.SingleCameraRequest{destination=target};
            RenderPipeline.SubmitRenderRequest(camera,req);
            var prior=RenderTexture.active;RenderTexture.active=target;pixels.ReadPixels(new Rect(0,0,W,H),0,0);pixels.Apply(false);RenderTexture.active=prior;
            if(full){var bytes=pixels.GetRawTextureData<byte>();stream.Write(bytes.ToArray(),0,bytes.Length);states.Add(state);}
            if(!full||Samples.Contains(f))File.WriteAllBytes(Path.Combine(Out,$"unity-{f:D4}.png"),pixels.EncodeToPNG());
            prepared=false;frame++;if(frame%60==0)File.WriteAllText(Path.Combine(Out,"progress.txt"),$"{frame}/{Frames}");
            if(frame>=(full?Frames:Samples.Length))Finish();
        }
        catch(Exception e){File.WriteAllText(Path.Combine(Out,"error.txt"),e.ToString());Finish(false);Debug.LogException(e);}
    }
    static void Finish(bool success=true)
    {
        EditorApplication.update-=Tick;
        if(encoder!=null){stream.Close();string error=encoder.StandardError.ReadToEnd();encoder.WaitForExit();if(encoder.ExitCode!=0){success=false;File.WriteAllText(Path.Combine(Out,"encoder-error.txt"),error);}encoder.Dispose();encoder=null;}
        if(full&&success)File.WriteAllText(Path.Combine(Out,"capture.json"),JsonUtility.ToJson(new Capture{timeline=states},true));
        File.WriteAllText(Path.Combine(Out,full?"render-status.txt":"preflight-status.txt"),success?"complete":"failed");
        if(target){target.Release();Object.DestroyImmediate(target);}if(pixels)Object.DestroyImmediate(pixels);
        if(scene.IsValid())EditorSceneManager.CloseScene(scene,true);
        if(previous.IsValid())SceneManager.SetActiveScene(previous);
    }
}
