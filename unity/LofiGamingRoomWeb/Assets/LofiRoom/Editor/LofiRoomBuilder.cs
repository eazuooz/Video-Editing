using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Yamyam.LofiRoom;
using Unity.Pipeline.Commands;

public static class LofiRoomBuilder
{
    const string Root = "Assets/LofiRoom";
    static readonly Dictionary<string, Material> mats = new();
    static readonly Dictionary<string, Mesh> meshes = new();

    [CliCommand("lofi_scene", "Build only the Yamyam LOFI sample scene and its authored room assets", MainThreadRequired = true)]
    public static string CreateViaMcp()
    {
        BuildScene();
        return "Assets/LofiRoom/Scenes/LofiRoomSample.unity";
    }

    [CliCommand("lofi_state", "Read the running LOFI sample and motion state", MainThreadRequired = true)]
    public static string ReadViaMcp()
    {
        var sample = UnityEngine.Object.FindAnyObjectByType<LofiRoomSample>();
        return sample ? sample.GetStateJson() : "{\"sampleLoaded\":false}";
    }

    public static void BuildScene()
    {
        foreach (var folder in new[] { Root + "/Generated", Root + "/Generated/Materials", Root + "/Generated/Meshes", Root + "/Scenes", Root + "/Models" })
            Directory.CreateDirectory(folder);
        AssetDatabase.Refresh();
        PrepareNativeImports();
        mats.Clear(); meshes.Clear();
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var owner = new GameObject("LofiRoom");
        var ctl = owner.AddComponent<LofiRoomSample>();
        var wood = Mat("wood", "#9A623D", .32f);
        var darkWood = Mat("wood-dark", "#543C2D", .25f);
        var cream = Mat("wall", "#C8B59A", .25f);
        var teal = Mat("teal", "#376D69", .28f);
        var ink = Mat("charcoal", "#262B30", .27f);
        var warmWhite = Mat("cream", "#E5D9B8", .32f);
        var metal = Mat("metal", "#4A4540", .62f);
        var blue = Mat("night-blue", "#244A66", .25f, "#264B69");
        var glow = Mat("pc-indicator", "#71C2B2", .3f, "#81CFB9");
        Box("foundation", new Vector3(0,-.12f,0), new Vector3(6.55f,.22f,4.85f), darkWood, .08f);
        for (int i=0;i<19;i++)
            Box("wood floor " + i, new Vector3(0,.005f,-2.28f+i*.25f), new Vector3(6.35f,.055f,.24f), i%3==0 ? darkWood:wood,.012f);
        Box("left wall",new Vector3(-3.2f,1.55f,0),new Vector3(.15f,3.1f,4.7f),cream,.02f);
        Box("back wall right",new Vector3(1.17f,1.55f,2.36f),new Vector3(4.06f,3.1f,.14f),cream,.02f);
        Box("back wall left",new Vector3(-2.98f,1.55f,2.36f),new Vector3(.44f,3.1f,.14f),cream,.02f);
        Box("window below",new Vector3(-1.8f,.4f,2.36f),new Vector3(1.95f,.8f,.14f),cream,.02f);
        Box("window above",new Vector3(-1.8f,2.93f,2.36f),new Vector3(1.95f,.34f,.14f),cream,.02f);
        Box("night outside",new Vector3(-1.8f,1.78f,2.72f),new Vector3(1.9f,1.95f,.03f),blue,.015f);
        for(int i=0;i<2;i++)
            Box("window side",new Vector3(-2.79f+i*1.98f,1.78f,2.29f),new Vector3(.1f,2.06f,.18f),darkWood,.016f);
        for(int i=0;i<2;i++)
            Box("window rail",new Vector3(-1.8f,.79f+i*1.99f,2.29f),new Vector3(2.08f,.1f,.18f),darkWood,.016f);
        Box("window mullion",new Vector3(-1.8f,1.78f,2.27f),new Vector3(.06f,1.96f,.1f),darkWood,.01f);
        Box("window crossbar",new Vector3(-1.8f,1.74f,2.27f),new Vector3(1.94f,.06f,.1f),darkWood,.01f);
        Box("rug",new Vector3(-.45f,.05f,-.7f),new Vector3(3.5f,.025f,2.08f),teal,.012f);
        Box("rug border",new Vector3(-.45f,.067f,-1.64f),new Vector3(3.28f,.008f,.035f),warmWhite,.004f);

        // Furniture uses explicit dimensions. It is authored geometry, not a
        // claim that Tripo generated the whole room from the concept image.
        Box("desktop",new Vector3(.8f,.77f,1.41f),new Vector3(2.35f,.105f,.83f),wood,.045f);
        for(int x=0;x<2;x++) for(int z=0;z<2;z++)
            Box("desk leg",new Vector3(-.25f+x*2.1f,.38f,1.08f+z*.65f),new Vector3(.075f,.71f,.075f),darkWood,.012f);
        Box("drawer cabinet",new Vector3(1.55f,.39f,1.43f),new Vector3(.56f,.7f,.7f),darkWood,.03f);
        for(int i=0;i<3;i++)
        {
            Box("drawer",new Vector3(1.55f,.18f+i*.21f,1.068f),new Vector3(.49f,.18f,.018f),wood,.01f);
            Box("drawer handle",new Vector3(1.55f,.18f+i*.21f,1.046f),new Vector3(.13f,.025f,.03f),metal,.012f);
        }
        for(int i=0;i<2;i++)
        {
            float x=.32f+i*.75f;
            Box("monitor stand",new Vector3(x,.85f,1.64f),new Vector3(.32f,.035f,.23f),ink,.012f);
            Box("monitor stalk",new Vector3(x,1.03f,1.68f),new Vector3(.045f,.35f,.045f),ink,.008f);
            Box("monitor",new Vector3(x,1.3f,1.66f),new Vector3(.70f,.43f,.045f),ink,.018f);
            Box("screen",new Vector3(x,1.3f,1.633f),new Vector3(.65f,.38f,.008f),blue,.008f);
            for(int line=0;line<4;line++)
                Box("screen work lines",new Vector3(x-.08f,1.39f-line*.055f,1.626f),new Vector3(.28f+line*.03f,.009f,.004f),line%2==0?glow:warmWhite,.002f);
        }
        Box("desk mat",new Vector3(.62f,.829f,1.2f),new Vector3(1.05f,.012f,.36f),teal,.018f);
        Box("keyboard",new Vector3(.48f,.847f,1.2f),new Vector3(.53f,.025f,.17f),ink,.012f);
        for(int row=0;row<3;row++) for(int col=0;col<12;col++)
            Box("key",new Vector3(.245f+col*.042f,.864f,1.145f+row*.049f),new Vector3(.032f,.008f,.03f),warmWhite,.002f);
        Box("mouse",new Vector3(.99f,.853f,1.18f),new Vector3(.067f,.045f,.11f),ink,.025f);
        Box("pc",new Vector3(1.75f,1.10f,1.63f),new Vector3(.31f,.56f,.50f),ink,.025f);
        Box("pc light",new Vector3(1.75f,1.1f,1.371f),new Vector3(.012f,.32f,.008f),glow,.003f);
        Box("chair seat",new Vector3(.8f,.45f,.48f),new Vector3(.52f,.11f,.52f),teal,.055f);
        Box("chair back",new Vector3(.8f,.89f,.19f),new Vector3(.52f,.83f,.10f),teal,.05f);
        Box("chair post",new Vector3(.8f,.23f,.48f),new Vector3(.065f,.33f,.065f),metal,.018f);
        Box("chair base x",new Vector3(.8f,.07f,.48f),new Vector3(.66f,.055f,.065f),metal,.02f);
        Box("chair base z",new Vector3(.8f,.07f,.48f),new Vector3(.065f,.055f,.66f),metal,.02f);
        for(int i=0;i<2;i++) Box("armrest",new Vector3(.49f+i*.62f,.66f,.48f),new Vector3(.065f,.06f,.37f),darkWood,.025f);
        Box("lamp base",new Vector3(-.18f,.84f,1.68f),new Vector3(.26f,.035f,.22f),metal,.018f);
        Box("lamp stem",new Vector3(-.18f,1.25f,1.72f),new Vector3(.035f,.8f,.035f),metal,.01f);
        Box("lamp hood",new Vector3(-.12f,1.62f,1.58f),new Vector3(.30f,.12f,.25f),darkWood,.045f);
        Box("lamp inner",new Vector3(-.12f,1.55f,1.58f),new Vector3(.23f,.015f,.20f),Mat("lamp-glow","#F7DE9C",.3f,"#FFC46C"),.012f);
        var lamp = new GameObject("Desk practical light").AddComponent<Light>();
        lamp.type=LightType.Spot;lamp.range=4.5f;lamp.spotAngle=110;lamp.intensity=5;
        lamp.color=new Color(1,.68f,.34f);lamp.shadows=LightShadows.Soft;
        lamp.transform.position=new Vector3(-.12f,1.48f,1.50f);lamp.transform.rotation=Quaternion.Euler(65,0,0);ctl.deskLight=lamp;

        Box("book shelf side",new Vector3(-2.96f,1.06f,.9f),new Vector3(.38f,2.1f,.10f),darkWood,.025f);
        for(int level=0;level<4;level++)
        {
            float y=.28f+level*.5f;
            Box("book shelf",new Vector3(-2.93f,y,.74f),new Vector3(.49f,.07f,2.03f),wood,.02f);
            for(int i=0;i<7;i++)
            {
                var color=i%3==0?teal:(i%3==1?warmWhite:darkWood);
                Box("book",new Vector3(-2.92f,y+.21f,-.12f+i*.27f),new Vector3(.29f,.33f+(i%3)*.04f,.1f),color,.012f);
            }
        }
        Plant(new Vector3(-2.6f,.12f,-1.65f),.9f,wood,teal);
        Plant(new Vector3(2.5f,.12f,1.7f),1.0f,wood,teal);
        Plant(new Vector3(1.92f,.83f,1.22f),.3f,warmWhite,teal);
        Box("wall map",new Vector3(.9f,2.4f,2.24f),new Vector3(1.35f,.7f,.08f),darkWood,.035f);
        Box("map paper",new Vector3(.9f,2.4f,2.191f),new Vector3(1.2f,.56f,.015f),warmWhite,.015f);
        for(int i=0;i<5;i++) Box("map island",new Vector3(.55f+i*.15f,2.35f+(i%2)*.16f,2.175f),new Vector3(.13f,.12f,.008f),teal,.035f);
        Box("cat cushion",new Vector3(-2.05f,.18f,-1.74f),new Vector3(.66f,.22f,.58f),warmWhite,.08f);

        var camObj=new GameObject("Main Camera",typeof(Camera),typeof(AudioListener));
        var cam=camObj.GetComponent<Camera>();cam.tag="MainCamera";cam.orthographic=true;cam.nearClipPlane=.1f;cam.farClipPlane=80;ctl.roomCamera=cam;ctl.CameraRoom();
        cam.clearFlags=CameraClearFlags.SolidColor;
        var cd=cam.GetUniversalAdditionalCameraData();cd.renderPostProcessing=true;
        cd.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;
        cd.antialiasingQuality=AntialiasingQuality.High;
        // Forward mobile renderer is also suited to the eventual WebGL build.
        // Disable the GPU Resident Drawer: one-off offscreen camera captures
        // otherwise omit its opaque draw data on this installed Editor.
        var webRp=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset");
        webRp.gpuResidentDrawerMode=GPUResidentDrawerMode.Disabled;
        GraphicsSettings.defaultRenderPipeline=webRp;QualitySettings.renderPipeline=webRp;
        EditorUtility.SetDirty(webRp);
        var sun=new GameObject("Window fill").AddComponent<Light>();
        sun.type=LightType.Directional;sun.transform.rotation=Quaternion.Euler(35,-35,0);sun.shadows=LightShadows.Soft;ctl.fillLight=sun;
        var softFill=new GameObject("Soft room fill").AddComponent<Light>();softFill.type=LightType.Point;softFill.range=9;softFill.intensity=3;softFill.color=new Color(1,.83f,.65f);softFill.transform.position=new Vector3(0,2,-1);
        RenderSettings.ambientMode=AmbientMode.Flat;
        var volume=new GameObject("Room grade").AddComponent<Volume>();volume.isGlobal=true;
        var profile=ScriptableObject.CreateInstance<VolumeProfile>();
        var bloom=profile.Add<Bloom>(true);bloom.intensity.Override(.2f);bloom.threshold.Override(1.2f);
        var tone=profile.Add<Tonemapping>(true);tone.mode.Override(TonemappingMode.ACES);
        var vignette=profile.Add<Vignette>(true);vignette.intensity.Override(.12f);
        AssetDatabase.DeleteAsset(Root+"/Generated/RoomGrade.asset");AssetDatabase.CreateAsset(profile, Root+"/Generated/RoomGrade.asset");volume.sharedProfile=profile;

        var rainObj=new GameObject("Window rain");
        rainObj.transform.position=new Vector3(-1.8f,2.7f,2.53f);
        var ps=rainObj.AddComponent<ParticleSystem>();ps.Stop();
        var main=ps.main;main.startLifetime=.65f;main.startSpeed=2.4f;main.startSize=.015f;main.startColor=new Color(.6f,.78f,1,.65f);main.maxParticles=150;main.simulationSpace=ParticleSystemSimulationSpace.World;
        var em=ps.emission;em.rateOverTime=90;
        var sh=ps.shape;sh.shapeType=ParticleSystemShapeType.Box;sh.scale=new Vector3(1.7f,.01f,.03f);sh.rotation=new Vector3(90,0,0);
        var pr=ps.GetComponent<ParticleSystemRenderer>();pr.renderMode=ParticleSystemRenderMode.Stretch;pr.lengthScale=3;pr.velocityScale=.08f;
        var rainMat=new Material(Shader.Find("Universal Render Pipeline/Particles/Unlit"));rainMat.SetColor("_BaseColor",new Color(.5f,.7f,1,.7f));AssetDatabase.DeleteAsset(Root+"/Generated/Materials/rain.mat");AssetDatabase.CreateAsset(rainMat,Root+"/Generated/Materials/rain.mat");pr.sharedMaterial=rainMat;ctl.rain=ps;ps.Play();
        ctl.music=new GameObject("Room music").AddComponent<AudioSource>();ctl.music.loop=true;ctl.music.playOnAwake=false;ctl.music.volume=.22f;
        var audio=AssetDatabase.FindAssets("t:AudioClip",new[]{Root}).FirstOrDefault();
        if(audio!=null) ctl.music.clip=AssetDatabase.LoadAssetAtPath<AudioClip>(AssetDatabase.GUIDToAssetPath(audio));
        AttachActor(ctl);
        AttachProp();
        foreach (var light in UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None)) light.useColorTemperature=false;
        EditorSceneManager.SaveScene(scene,Root+"/Scenes/LofiRoomSample.unity");
        EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(Root+"/Scenes/LofiRoomSample.unity",true)};
        PlayerSettings.companyName="YamyamCoding";PlayerSettings.productName="Yamyam Lofi Room";
        PlayerSettings.defaultScreenWidth=1920;PlayerSettings.defaultScreenHeight=1080;
        PlayerSettings.runInBackground=true;
        PlayerSettings.WebGL.compressionFormat=WebGLCompressionFormat.Gzip;
        PlayerSettings.WebGL.decompressionFallback=true;
        PlayerSettings.WebGL.dataCaching=true;
        AssetDatabase.SaveAssets();
        File.WriteAllText(Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/scene-build.json"),JsonUtility.ToJson(new SceneReport{scene=Root+"/Scenes/LofiRoomSample.unity",actorLoaded=ctl.actor!=null,walkLoaded=ctl.hasWalk,idleLoaded=ctl.hasIdle,sitLoaded=ctl.hasSit,walkSpeed=ctl.calibratedWalkSpeed},true));
        Debug.Log("LOFI_SCENE_READY "+ctl.GetStateJson());
    }

    static void AttachActor(LofiRoomSample ctl)
    {
        var candidates=AssetDatabase.FindAssets("t:Model",new[]{Root+"/Models"}).Select(AssetDatabase.GUIDToAssetPath).ToArray();
        string walkPath=candidates.FirstOrDefault(p=>p.Contains("/hero-walk/"));
        string mainPath=walkPath??candidates.FirstOrDefault(p=>p.Contains("/hero-"));
        if(mainPath==null)return;
        var go=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(mainPath));
        go.name="Tripo Hero";go.transform.position=Vector3.zero;
        var renderers=go.GetComponentsInChildren<Renderer>();if(renderers.Length==0)return;
        var bounds=renderers[0].bounds;foreach(var rr in renderers)bounds.Encapsulate(rr.bounds);
        float scale=1.7f/Mathf.Max(.01f,bounds.size.y);go.transform.localScale*=scale;
        go.transform.position=new Vector3(-.8f,-bounds.min.y*scale,-.8f);
        FixMaterials(go,mainPath);
        var animator=go.GetComponent<Animator>();if(!animator)animator=go.AddComponent<Animator>();
        AssetDatabase.DeleteAsset(Root+"/Generated/Hero.controller");var ac=AnimatorController.CreateAnimatorControllerAtPath(Root+"/Generated/Hero.controller");
        foreach(var pair in new[]{("Idle","idle"),("Walk","walk"),("Sit","sit")})
        {
            string path=candidates.FirstOrDefault(p=>p.Contains("/hero-"+pair.Item2+"/"));
            if(path==null)continue;
            var clip=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().FirstOrDefault(c=>!c.name.StartsWith("__preview"));
            if(clip==null)continue;
            var st=ac.layers[0].stateMachine.AddState(pair.Item1);st.motion=clip;
            if(pair.Item1=="Idle")ctl.hasIdle=true;
            if(pair.Item1=="Walk"){ctl.hasWalk=true;float measured=clip.averageSpeed.magnitude*scale;if(measured>.05f)ctl.calibratedWalkSpeed=measured;}
            if(pair.Item1=="Sit")ctl.hasSit=true;
        }
        animator.avatar=AssetDatabase.LoadAllAssetsAtPath(mainPath).OfType<Avatar>().FirstOrDefault();
        animator.runtimeAnimatorController=ac;ctl.actor=animator;
        animator.applyRootMotion=true;
        go.AddComponent<LofiRootMotion>().owner=ctl;
        ctl.groundY=go.transform.position.y;
    }
    static void AttachProp()
    {
        string path=AssetDatabase.FindAssets("t:Model",new[]{Root+"/Models"}).Select(AssetDatabase.GUIDToAssetPath).FirstOrDefault(p=>p.Contains("/headphones/"));
        if(path==null)return;
        var go=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));go.name="Tripo Headphones";
        var rr=go.GetComponentsInChildren<Renderer>();var b=rr[0].bounds;foreach(var x in rr)b.Encapsulate(x.bounds);
        float s=.25f/Mathf.Max(b.size.x,Mathf.Max(b.size.y,b.size.z));go.transform.localScale*=s;go.transform.position=new Vector3(-.02f,.835f-b.min.y*s,1.2f);FixMaterials(go,path);
    }
    static void PrepareNativeImports()
    {
        var paths=AssetDatabase.FindAssets("t:Model",new[]{Root+"/Models"}).Select(AssetDatabase.GUIDToAssetPath).ToArray();
        foreach(var path in paths.Where(p=>p.Contains("/hero-")))
        {
            var mi=(ModelImporter)AssetImporter.GetAtPath(path);
            if(mi.animationType==ModelImporterAnimationType.Human && mi.clipAnimations.Length>0)continue;
            mi.animationType=ModelImporterAnimationType.Human;
            mi.avatarSetup=ModelImporterAvatarSetup.CreateFromThisModel;
            mi.motionNodeName="";
            mi.importAnimation=true;
            var clips=mi.defaultClipAnimations;
            foreach(var clip in clips){clip.loopTime=true;clip.loopPose=false;clip.lockRootRotation=true;clip.lockRootHeightY=true;clip.lockRootPositionXZ=false;}
            mi.clipAnimations=clips;mi.SaveAndReimport();
        }
    }
    static void FixMaterials(GameObject go,string modelPath)
    {
        string dir=Path.GetDirectoryName(modelPath).Replace('\\','/');
        var basePath=AssetDatabase.FindAssets("t:Texture2D",new[]{dir}).Select(AssetDatabase.GUIDToAssetPath).FirstOrDefault(p=>p.ToLowerInvariant().Contains("basecolor"));
        var fallback=basePath==null?null:AssetDatabase.LoadAssetAtPath<Texture2D>(basePath);
        foreach(var rr in go.GetComponentsInChildren<Renderer>())
        {
            var list=rr.sharedMaterials;
            for(int i=0;i<list.Length;i++)
            {
                var old=list[i];if(old==null)continue;
                var m=new Material(Shader.Find("Universal Render Pipeline/Lit"));
                var texture=fallback ? fallback : (old.HasProperty("_BaseMap")?old.GetTexture("_BaseMap"):old.mainTexture);
                m.SetTexture("_BaseMap",texture);m.SetColor("_BaseColor",texture?Color.white:old.color);m.SetFloat("_Smoothness",.25f);
                string name=go.name.Replace(" ","")+"-"+rr.name+"-"+i;string target=AssetDatabase.GenerateUniqueAssetPath(Root+"/Generated/Materials/"+name+".mat");AssetDatabase.CreateAsset(m,target);list[i]=m;
            }
            rr.sharedMaterials=list;
        }
    }
    static Material Mat(string name,string html,float smooth,string emission=null)
    {
        if(mats.TryGetValue(name,out var existing))return existing;
        ColorUtility.TryParseHtmlString(html,out var color);
        var mat=new Material(Shader.Find("Universal Render Pipeline/Lit"));mat.name=name;mat.SetColor("_BaseColor",color);mat.SetFloat("_Smoothness",smooth);
        if(emission!=null){ColorUtility.TryParseHtmlString(emission,out var e);mat.EnableKeyword("_EMISSION");mat.SetColor("_EmissionColor",e*1.3f);}
        string path=Root+"/Generated/Materials/"+name+".mat";
        var previous=AssetDatabase.LoadAssetAtPath<Material>(path);if(previous){EditorUtility.CopySerialized(mat,previous);UnityEngine.Object.DestroyImmediate(mat);mat=previous;}else AssetDatabase.CreateAsset(mat,path);
        mats[name]=mat;return mat;
    }
    static GameObject Box(string name,Vector3 pos,Vector3 size,Material mat,float radius)
    {
        string key=size.ToString("F3")+"-"+radius;
        if(!meshes.TryGetValue(key,out var mesh))
        {
            mesh=RoundedBox(size,radius);mesh.name="rounded";
            string path=Root+"/Generated/Meshes/box-"+meshes.Count+".asset";AssetDatabase.DeleteAsset(path);AssetDatabase.CreateAsset(mesh,path);meshes[key]=mesh;
        }
        var go=new GameObject(name,typeof(MeshFilter),typeof(MeshRenderer));go.transform.position=pos;go.GetComponent<MeshFilter>().sharedMesh=mesh;go.GetComponent<MeshRenderer>().sharedMaterial=mat;go.isStatic=true;return go;
    }
    static Mesh RoundedBox(Vector3 size,float radius)
    {
        Vector3 h=size*.5f;float rad=Mathf.Min(radius,Mathf.Min(h.x,Mathf.Min(h.y,h.z))*.95f);
        Vector3 inner=h-Vector3.one*rad;var vs=new List<Vector3>();var ns=new List<Vector3>();var uv=new List<Vector2>();var ts=new List<int>();const int steps=4;
        Vector3[] normals={Vector3.right,Vector3.left,Vector3.up,Vector3.down,Vector3.forward,Vector3.back};
        foreach(var normal in normals)
        {
            Vector3 u=normal.y==0?Vector3.up:Vector3.right;Vector3 v=Vector3.Cross(normal,u);int offset=vs.Count;
            for(int y=0;y<=steps;y++)for(int x=0;x<=steps;x++)
            {
                Vector3 raw=Vector3.Scale(normal+u*(x/(float)steps*2-1)+v*(y/(float)steps*2-1),h);
                Vector3 close=new Vector3(Mathf.Clamp(raw.x,-inner.x,inner.x),Mathf.Clamp(raw.y,-inner.y,inner.y),Mathf.Clamp(raw.z,-inner.z,inner.z));
                Vector3 nn=(raw-close).normalized;vs.Add(close+nn*rad);ns.Add(nn);uv.Add(new Vector2(x/(float)steps,y/(float)steps));
            }
            for(int y=0;y<steps;y++)for(int x=0;x<steps;x++)
            {int a=offset+y*(steps+1)+x,b=a+1,c=a+steps+1,d=c+1;ts.AddRange(new[]{a,b,c,b,d,c});}
        }
        var m=new Mesh();m.SetVertices(vs);m.SetNormals(ns);m.SetUVs(0,uv);m.SetTriangles(ts,0);m.RecalculateBounds();return m;
    }
    static void Plant(Vector3 p,float s,Material pot,Material leaf)
    {
        Box("plant pot",p+new Vector3(0,.18f*s,0),new Vector3(.34f,.36f,.34f)*s,pot,.07f*s);
        for(int i=0;i<7;i++)
        {
            float a=i*Mathf.PI*2/7;var go=GameObject.CreatePrimitive(PrimitiveType.Sphere);go.name="plant leaf";go.transform.position=p+new Vector3(Mathf.Cos(a)*.21f*s,(.43f+(i%3)*.09f)*s,Mathf.Sin(a)*.21f*s);go.transform.localScale=new Vector3(.18f,.35f,.12f)*s;go.transform.rotation=Quaternion.Euler(20,i*51,25);go.GetComponent<Renderer>().sharedMaterial=leaf;UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());go.isStatic=true;
        }
    }
    public static void BuildWeb()
    {
        string dest=Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/webgl-sample");
        Directory.CreateDirectory(dest);
        var report=BuildPipeline.BuildPlayer(EditorBuildSettings.scenes,dest,BuildTarget.WebGL,BuildOptions.None);
        Debug.Log("LOFI_WEB_BUILD "+report.summary.result+" "+report.summary.totalSize);
        if(report.summary.result!=UnityEditor.Build.Reporting.BuildResult.Succeeded)throw new Exception("Web build failed");
    }
    [CliCommand("lofi_native_build", "Build the local Windows review sample; does not build WebGL",MainThreadRequired=true)]
    public static string BeginNativeBuild()
    {
        if(EditorApplication.isPlaying)throw new Exception("Stop Play mode before building");
        string dest=Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/unity-sample-v1/windows/YamyamLofiRoom.exe");
        Directory.CreateDirectory(Path.GetDirectoryName(dest));
        EditorApplication.delayCall+=()=>{
            PlayerSettings.fullScreenMode=FullScreenMode.Windowed;
            var report=BuildPipeline.BuildPlayer(EditorBuildSettings.scenes,dest,BuildTarget.StandaloneWindows64,BuildOptions.None);
            File.WriteAllText(Path.GetFullPath("../../projects/ai-3d-lofi-gaming-room/production/local/unity-sample-v1/native-build.json"),JsonUtility.ToJson(new NativeReport{result=report.summary.result.ToString(),bytes=(long)report.summary.totalSize,errors=report.summary.totalErrors},true));
        };
        return dest;
    }
    [Serializable] class NativeReport { public string result;public long bytes;public int errors; }
    [Serializable] class SceneReport { public string scene; public bool actorLoaded,walkLoaded,idleLoaded,sitLoaded;public float walkSpeed; }
}
