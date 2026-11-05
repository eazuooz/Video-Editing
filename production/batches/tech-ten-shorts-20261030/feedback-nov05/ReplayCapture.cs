using System;
using System.IO;
using System.Text;
using System.Globalization;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class ReplayCapture
{
    const string Folder = "Assets/VideoScenes/FeedbackRTS";
    static Camera camera;
    static Material MaterialFor(string key, Color color, bool atlas = false)
    {
        var material = new Material(Shader.Find("Standard"));
        material.color = color; material.SetFloat("_Glossiness", .05f);
        if (atlas) material.mainTexture = AssetDatabase.LoadAssetAtPath<Texture2D>(Folder + "/Models/Military Atlas.png");
        var path=Folder + "/" + key + ".mat";
        var prior=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(prior){EditorUtility.CopySerialized(material,prior); UnityEngine.Object.DestroyImmediate(material);return prior;}
        AssetDatabase.CreateAsset(material,path); return material;
    }
    static Transform Prop(string model, Vector3 at, float length, Material material, float heading)
    {
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(Folder + "/Models/" + model + ".fbx");
        if (!prefab) throw new Exception("Missing " + model);
        var anchor = new GameObject(model).transform;
        var obj = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
        obj.transform.SetParent(anchor,false); obj.transform.localRotation = Quaternion.Euler(0,heading,0);
        var renderers=obj.GetComponentsInChildren<Renderer>(); var bounds = renderers[0].bounds;
        foreach(var r in renderers) {bounds.Encapsulate(r.bounds); var slots=r.sharedMaterials; for(int k=0;k<slots.Length;k++) slots[k]=material; r.sharedMaterials=slots;}
        float s=length/Mathf.Max(bounds.size.x,bounds.size.z,.001f);
        obj.transform.localPosition=-new Vector3(bounds.center.x,bounds.min.y,bounds.center.z);
        anchor.localScale=Vector3.one*s;anchor.position=at;return anchor;
    }
    static Transform Box(string name,Vector3 at,Vector3 size,Material m)
    {
        var obj=GameObject.CreatePrimitive(PrimitiveType.Cube);obj.name=name;obj.transform.position=at;
        obj.transform.localScale=size;obj.GetComponent<Renderer>().sharedMaterial=m;return obj.transform;
    }
    public static void Run()
    {
        try
        {
            string gpu=SystemInfo.graphicsDeviceName.ToLowerInvariant();
            if(!gpu.Contains("basic render")&&!gpu.Contains("warp")) throw new Exception("Software renderer required: "+gpu);
            string output=Environment.GetEnvironmentVariable("YAMYAM_REPLAY_FRAMES");
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;
            var ground=MaterialFor("Ground",new Color(.13f,.21f,.22f));
            var grid=MaterialFor("Grid",new Color(.19f,.31f,.30f));
            var blue=MaterialFor("Squad",new Color(.77f,.94f,1f),true);
            var red=MaterialFor("Opposition",new Color(1f,.58f,.43f),true);
            var teal=MaterialFor("Selection",new Color(.1f,.9f,.68f));
            var gold=MaterialFor("Pulse",new Color(1f,.84f,.22f));
            Box("Terrain",new Vector3(0,-.14f,0),new Vector3(35,.25f,23),ground);
            for(int k=-14;k<=14;k+=2) Box("Grid x",new Vector3(k,0,0),new Vector3(.018f,.005f,19),grid);
            for(int k=-8;k<=8;k+=2) Box("Grid z",new Vector3(0,0,k),new Vector3(29,.005f,.018f),grid);
            var sim=new GameObject("Fixed tick command simulation").AddComponent<CommandReplay>();
            string[] models={"Tank_1_A","Jeep_A","Tank_2_A","Jeep_A","Tank_1_A","Heli_1_A"};
            sim.squad=new Transform[models.Length];sim.spawn=new Vector3[models.Length];
            for(int i=0;i<models.Length;i++) {
                var p=new Vector3(-6f+(i%3)*2.05f,i==5?.72f:.03f,1.35f-(i/3)*3.4f);
                sim.spawn[i]=p;sim.squad[i]=Prop(models[i],p,1.85f,blue,75f);
                var ring=GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                ring.name="Squad selection";ring.transform.position=new Vector3(p.x,.018f,p.z);
                ring.transform.localScale=new Vector3(1.54f,.009f,1.54f);
                ring.GetComponent<Renderer>().sharedMaterial=teal;ring.transform.SetParent(sim.squad[i],true);
            }
            sim.enemy=Prop("Turret_1_A",new Vector3(6,.04f,.45f),2.2f,red,-95);
            Prop("Hangar_1_A",new Vector3(6,.03f,3.8f),3.2f,red,190);
            var tracer=GameObject.CreatePrimitive(PrimitiveType.Cylinder);tracer.GetComponent<Renderer>().sharedMaterial=gold;
            sim.tracer=tracer.transform;
            sim.inputs=new[]{new CommandReplay.Order{tick=120,target=new Vector3(-1.2f,.03f,1.1f)},new CommandReplay.Order{tick=240,attack=true}};
            var light=new GameObject("Key").AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.15f;light.transform.rotation=Quaternion.Euler(55,-32,0);
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.73f,.75f,.79f);
            camera=new GameObject("Observer").AddComponent<Camera>();camera.orthographic=true;camera.orthographicSize=4.75f;
            camera.transform.position=new Vector3(0,17,-10);camera.transform.LookAt(Vector3.zero);
            camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.025f,.055f,.06f);
            sim.ResetMatch(2.85f); EditorSceneManager.SaveScene(scene,Folder+"/ReplaySquad.unity"); AssetDatabase.SaveAssets();
            var rt=new RenderTexture(1080,548,24);rt.antiAliasing=2;rt.Create();camera.targetTexture=rt;
            var tex=new Texture2D(1080,548,TextureFormat.RGB24,false);
            string previous=null;
            foreach(var take in new[]{"record","replay","patch"}) {
                var trace=new StringBuilder(); string dest=Path.Combine(output,take);Directory.CreateDirectory(dest);
                sim.ResetMatch(take=="patch"?.95f:2.85f);
                for(int tick=0;tick<390;tick++) {
                    sim.Step();
                    if(tick%2!=0)continue;
                    trace.Append(tick).Append(',').Append(sim.hitPoints);
                    foreach(var unit in sim.squad)foreach(var v in new[]{unit.position.x,unit.position.y,unit.position.z})trace.Append(',').Append(v.ToString("F5",CultureInfo.InvariantCulture));
                    trace.Append('\n');
                    camera.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1080,548),0,0);tex.Apply();
                    File.WriteAllBytes(Path.Combine(dest,(tick/2).ToString("D4")+".jpg"),tex.EncodeToJPG(93));
                }
                string state=trace.ToString();
                if(take=="replay" && state!=previous)throw new Exception("Replay diverged");
                if(take=="patch" && state==previous)throw new Exception("Changed-speed case did not diverge");
                File.WriteAllText(Path.Combine(dest,"state.csv"),state);previous=state;
            }
            File.WriteAllText(Path.Combine(output,"renderer.txt"),gpu);EditorApplication.Exit(0);
        }
        catch(Exception ex){Debug.LogException(ex);EditorApplication.Exit(1);}
    }
}
