using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using Object = UnityEngine.Object;

namespace YamyamCoding.Shorts.ForgivingHitbox.Editor {
public static class HitboxCapture {
    const string Root = "Assets/VideoScenes/shorts-forgiving-hitbox";
    const string Asset = "Assets/ThirdParty/KayKitAdventurers/";
    const int W=1080,H=1920,Fps=60,Frames=1800;
    [Serializable] public class Shot { public string id; public float start,end,attackStart,attackSeconds,width; }
    [Serializable] public class Job { public string output,mode,ffmpeg; public Shot[] shots; }
    [Serializable] public class Point { public float x,y; public Point(Vector3 p){x=p.x;y=H-p.y;} }
    [Serializable] public class State { public int frame,health; public string shot; public bool overlapping,hitApplied; public float width,separation; public Point[] hurt,attack; public Point projectile; }
    [Serializable] public class Trace { public int width=W,height=H,fps=Fps; public string unity; public string[] animationClips; public List<State> frames=new List<State>(); public string physics="Physics.ComputePenetration(BoxCollider, BoxCollider)"; }
    static Job job; static Camera cam; static GameObject hero,orb; static HitboxDemonstration demo;
    static Dictionary<string,AnimationClip> clips; static Material knightMat; static Texture2D pixels; static RenderTexture rt;
    static System.Diagnostics.Process ff; static Stream pipe; static int index; static bool prepared; static State pending;
    static Trace trace; static Vector3 heroBase; static float scale; static string previousShot=""; static float damageTime=-100;
    static readonly int[] Preview={40,70,230,470,820,900,1120,1540};
    static Color Hex(string s){ColorUtility.TryParseHtmlString(s,out var c);return c;}
    static Material Mat(string name,Color color,Texture texture=null) {
        var p=Root+"/Baked/"+name+".mat"; var m=AssetDatabase.LoadAssetAtPath<Material>(p);
        if(!m){m=new Material(Shader.Find("Yamyam/ShortsCharacterSurface"));AssetDatabase.CreateAsset(m,p);}
        m.shader=Shader.Find("Yamyam/ShortsCharacterSurface");
        m.color=color;m.SetFloat("_Metallic",.15f);m.SetFloat("_Glossiness",.35f);if(texture)m.mainTexture=texture;return m;
    }
    static GameObject Part(string name,PrimitiveType type,Vector3 position,Vector3 size,Material m) {
        var g=GameObject.CreatePrimitive(type);g.name=name;g.transform.position=position;g.transform.localScale=size;
        Object.DestroyImmediate(g.GetComponent<Collider>());g.GetComponent<Renderer>().sharedMaterial=m;return g;
    }
    public static void Run() {
        try {
            var args=Environment.GetCommandLineArgs();string path=args[Array.IndexOf(args,"-hitboxJob")+1];job=JsonUtility.FromJson<Job>(File.ReadAllText(path));
            Directory.CreateDirectory(job.output);Directory.CreateDirectory(Root+"/Baked");Directory.CreateDirectory(Root+"/Scenes");
            Build();
            trace=new Trace{unity=Application.unityVersion,animationClips=clips.Keys.ToArray()};
            rt=new RenderTexture(W,H,24,RenderTextureFormat.ARGB32){antiAliasing=4};rt.Create();
            pixels=new Texture2D(W,H,TextureFormat.RGBA32,false);cam.targetTexture=rt;
            if(job.mode=="full"){
                string output=Path.Combine(job.output,"unity-master.mp4");if(File.Exists(output))throw new Exception("Preserve existing master");
                ff=new System.Diagnostics.Process();ff.StartInfo=new System.Diagnostics.ProcessStartInfo(job.ffmpeg,
                    $"-hide_banner -loglevel warning -n -f rawvideo -pixel_format rgba -video_size {W}x{H} -framerate {Fps} -i pipe:0 -vf vflip -an -frames:v {Frames} -c:v libx264 -threads 4 -preset fast -crf 16 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart \"{output}\"") {UseShellExecute=false,CreateNoWindow=true,RedirectStandardInput=true,RedirectStandardError=true};
                ff.ErrorDataReceived+=(s,e)=>{if(e.Data!=null)File.AppendAllText(Path.Combine(job.output,"ffmpeg.log"),e.Data+"\n");};ff.Start();ff.BeginErrorReadLine();pipe=ff.StandardInput.BaseStream;
            }
            index=0;prepared=false;EditorApplication.update+=Tick;
        } catch(Exception e){Debug.LogException(e);EditorApplication.Exit(1);}
    }
    static void Build() {
        GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;QualitySettings.antiAliasing=4;
        PlayerSettings.colorSpace=ColorSpace.Linear;
        var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        RenderSettings.skybox=null;RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.42f,.46f,.5f);
        var dark=Mat("Stage",Hex("#132820"));var rim=Mat("StageEdge",Hex("#315044"));
        Part("Platform edge",PrimitiveType.Cube,new Vector3(0,-.15f,0),new Vector3(3.5f,.17f,1.8f),rim);
        Part("Platform top",PrimitiveType.Cube,new Vector3(0,-.045f,0),new Vector3(3.5f,.06f,1.8f),dark);
        hero=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Asset+"Knight.fbx"));hero.name="KayKit Knight — same model in every test";
        clips=AssetDatabase.LoadAllAssetsAtPath(Asset+"Knight.fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToDictionary(c=>c.name);
        if(hero.TryGetComponent<Animator>(out var animator))animator.enabled=false;
        knightMat=Mat("Knight",Color.white,AssetDatabase.LoadAssetAtPath<Texture2D>(Asset+"knight_texture.png"));
        foreach(var t in hero.GetComponentsInChildren<Transform>(true))if(t.name.Contains("Sword")||t.name.Contains("Shield"))t.gameObject.SetActive(false);
        foreach(var r in hero.GetComponentsInChildren<Renderer>(true)){r.sharedMaterial=knightMat;if(r is SkinnedMeshRenderer s)s.updateWhenOffscreen=true;}
        clips["Idle"].SampleAnimation(hero,.9f);hero.transform.rotation=Quaternion.identity;
        var rr=hero.GetComponentsInChildren<Renderer>();var b=rr[0].bounds;foreach(var r in rr)b.Encapsulate(r.bounds);
        scale=2.2f/b.size.y;hero.transform.localScale=Vector3.one*scale;
        clips["Idle"].SampleAnimation(hero,.9f);hero.transform.localScale=Vector3.one*scale;
        b=rr[0].bounds;foreach(var r in rr)b.Encapsulate(r.bounds);heroBase=new Vector3(-b.center.x,0,-b.center.z);hero.transform.position=heroBase;
        var red=Mat("AttackMetal",Hex("#DC5C50"));var steel=Mat("AttackRim",Hex("#B9B8B0"));
        orb=Part("Falling attack",PrimitiveType.Sphere,new Vector3(-.64f,3.2f,0),Vector3.one*.34f,red);
        for(int i=0;i<8;i++){float a=i*Mathf.PI/4;var tooth=Part("Attack tip "+i,PrimitiveType.Cube,new Vector3(0,0,0),new Vector3(.13f,.08f,.17f),steel);tooth.transform.SetParent(orb.transform,false);tooth.transform.localScale=new Vector3(.36f,.18f,.42f);tooth.transform.localPosition=new Vector3(Mathf.Cos(a)*.54f,Mathf.Sin(a)*.54f,0);tooth.transform.localRotation=Quaternion.Euler(0,0,i*45);}
        demo=new GameObject("Actual hit detection").AddComponent<HitboxDemonstration>();
        demo.hurtbox=new GameObject("Hurtbox — receiving damage").AddComponent<BoxCollider>();demo.hurtbox.transform.position=new Vector3(0,1.06f,0);demo.hurtbox.isTrigger=true;
        demo.hitbox=new GameObject("Hitbox — attack damage").AddComponent<BoxCollider>();demo.hitbox.size=new Vector3(.22f,.22f,.8f);demo.hitbox.isTrigger=true;
        cam=new GameObject("Portrait camera").AddComponent<Camera>();cam.enabled=false;cam.orthographic=true;cam.orthographicSize=3.5f;cam.aspect=W/(float)H;
        cam.transform.position=new Vector3(0,1,8);cam.transform.LookAt(new Vector3(0,1,0));cam.backgroundColor=Color.black;cam.clearFlags=CameraClearFlags.SolidColor;cam.nearClipPlane=.1f;cam.farClipPlane=30;cam.allowHDR=false;
        MakeLight("Warm key",new Vector3(25,-35,0),new Color(1,.92f,.80f),1.4f);MakeLight("Soft fill",new Vector3(20,145,0),new Color(.65f,.85f,1),.65f);
        for(int s=0;s<job.shots.Length;s++){Apply((int)(job.shots[s].start*60),true);EditorSceneManager.SaveScene(scene,Root+"/Scenes/"+job.shots[s].id+".unity");}
        AssetDatabase.SaveAssets();previousShot="";damageTime=-100;
        File.WriteAllText(Path.Combine(job.output,"model-bounds.txt"),"Normalizedheight=2.2;scale="+scale+";beforeTranslation="+b+";root="+heroBase);
    }
    static void MakeLight(string name,Vector3 rot,Color c,float intensity){var g=new GameObject(name);g.transform.rotation=Quaternion.Euler(rot);var l=g.AddComponent<Light>();l.type=LightType.Directional;l.color=c;l.intensity=intensity;l.shadows=LightShadows.None;}
    static Point[] Box(BoxCollider box) {
        var sz=box.size*.5f;var c=box.transform.position+box.center;float z=.48f;
        return new[]{new Point(cam.WorldToScreenPoint(c+new Vector3(-sz.x,sz.y,z))),new Point(cam.WorldToScreenPoint(c+new Vector3(sz.x,sz.y,z))),new Point(cam.WorldToScreenPoint(c+new Vector3(sz.x,-sz.y,z))),new Point(cam.WorldToScreenPoint(c+new Vector3(-sz.x,-sz.y,z)))};
    }
    static State Apply(int f,bool reset=false) {
        float t=f/(float)Fps;var shot=job.shots.LastOrDefault(s=>s.start<=t)??job.shots[0];
        if(previousShot!=shot.id||reset){demo.ResetAttack(shot.width);previousShot=shot.id;damageTime=-100;}
        float u=Mathf.Clamp01((t-shot.attackStart)/shot.attackSeconds);float y=Mathf.Lerp(3.4f,-.45f,u);
        orb.transform.position=new Vector3(-.64f,y,0);orb.transform.rotation=Quaternion.Euler(0,0,-t*360);orb.SetActive(t>=shot.attackStart&&u<1);
        demo.hitbox.transform.position=orb.transform.position;
        // Random preview seeks replay the attack queries, not a hand-set health result.
        if(job.mode!="full"||reset){demo.ResetAttack(shot.width);for(int k=(int)(shot.attackStart*60);k<=f;k++){float ku=Mathf.Clamp01((k/60f-shot.attackStart)/shot.attackSeconds);demo.hitbox.transform.position=new Vector3(-.64f,Mathf.Lerp(3.4f,-.45f,ku),0);if(demo.EvaluateAttack()&&damageTime<0)damageTime=k/60f;}demo.hitbox.transform.position=orb.transform.position;}
        bool was=demo.hitApplied;demo.EvaluateAttack();if(!was&&demo.hitApplied)damageTime=t;
        var clip=clips["Idle"];float sample=.9f;
        if(demo.hitApplied&&t-damageTime<.6f&&clips.ContainsKey("Hit_A")){clip=clips["Hit_A"];sample=Mathf.Min(t-damageTime,clip.length-.001f);}
        clip.SampleAnimation(hero,sample);hero.transform.localScale=Vector3.one*scale;hero.transform.position=heroBase;hero.transform.rotation=Quaternion.identity;
        bool flash=demo.hitApplied&&t-damageTime<.14f;knightMat.color=flash?new Color(1,.3f,.25f):Color.white;
        return new State{frame=f,health=demo.health,shot=shot.id,overlapping=demo.overlapping,hitApplied=demo.hitApplied,width=shot.width,separation=demo.separationDistance,hurt=Box(demo.hurtbox),attack=Box(demo.hitbox),projectile=new Point(cam.WorldToScreenPoint(orb.transform.position))};
    }
    static void Tick() {
        try {
            int f=job.mode=="full"?index:Preview[index];
            if(!prepared){pending=Apply(f);prepared=true;EditorApplication.QueuePlayerLoopUpdate();return;}
            cam.Render();var old=RenderTexture.active;RenderTexture.active=rt;pixels.ReadPixels(new Rect(0,0,W,H),0,0);pixels.Apply(false);RenderTexture.active=old;
            if(job.mode=="full"){var bytes=pixels.GetRawTextureData<byte>();pipe.Write(bytes.ToArray(),0,bytes.Length);}
            if(job.mode!="full"||Preview.Contains(f))File.WriteAllBytes(Path.Combine(job.output,$"frame-{f:D4}.png"),pixels.EncodeToPNG());
            trace.frames.Add(pending);prepared=false;index++;
            if(index%120==0)Debug.Log("Hitbox capture "+index+"/"+(job.mode=="full"?Frames:Preview.Length));
            if(index<(job.mode=="full"?Frames:Preview.Length))return;
            EditorApplication.update-=Tick;
            if(ff!=null){pipe.Close();ff.WaitForExit();if(ff.ExitCode!=0)throw new Exception("Encoder failed: "+ff.ExitCode);}
            File.WriteAllText(Path.Combine(job.output,"trace.json"),JsonUtility.ToJson(trace,true));
            File.WriteAllText(Path.Combine(job.output,"success.json"),"{\"frames\":"+index+",\"actualPhysics\":true}");EditorApplication.Exit(0);
        } catch(Exception e){EditorApplication.update-=Tick;if(ff!=null&&!ff.HasExited){pipe.Close();ff.Kill();}Debug.LogException(e);EditorApplication.Exit(1);}
    }
}
}
