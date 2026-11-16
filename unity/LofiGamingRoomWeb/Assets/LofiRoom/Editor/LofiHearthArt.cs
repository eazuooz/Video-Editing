using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEngine.Rendering;
using Yamyam.LofiRoom;

public static class LofiHearthArt
{
    static Material oak,dark,cream,stone,brick,metal,black,teal,paper;
    static string root;
    static GameObject Box(string n,Vector3 p,Vector3 size,Material m,float radius=.015f)=>LofiRoomBuilder.Box(n,p,size,m,radius);
    static Material Mat(string n,string color,float smooth=.25f)=>LofiRoomBuilder.Mat("hearth-"+n,color,smooth);
    public static void Apply(LofiRoomSample room,string generated)
    {
        root=generated;
        oak=Mat("oak","#98663E");dark=Mat("dark-wood","#4B3222");cream=Mat("plaster","#D1BDA0");
        stone=Mat("stone","#BAAA91");brick=Mat("brick","#745646");metal=Mat("silver","#AAAFAE",.50f);
        black=Mat("charcoal","#141B1D",.2f);teal=Mat("teal","#335D57");paper=Mat("pages","#E5D7B5");
        oak.SetFloat("_Pattern",1);dark.SetFloat("_Pattern",1);stone.SetFloat("_Pattern",3);
        metal.SetFloat("_Metallic",.65f);metal.SetFloat("_Pattern",4);
        foreach(var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(r=>r.name.StartsWith("book shelf")||r.name=="book"||r.name=="fine book spine band").ToArray())UnityEngine.Object.DestroyImmediate(r.gameObject);
        Shelves();Fireplace(room);Desk(room);Turntable(room);
    }
    static void Shelves()
    {
        for(int side=0;side<2;side++)for(int tier=0;tier<2;tier++)
        {
            float z=side==0?-1.25f:1.70f,y=1.55f+tier*.66f;
            Box("two-tier wall shelf",new Vector3(-2.93f,y,z),new Vector3(.48f,.065f,.92f),oak,.02f);
            for(int j=0;j<5;j++)
            {
                float h=.24f+(j%3)*.035f;
                Box("shelf book",new Vector3(-2.94f,y+.035f+h*.5f,z-.33f+j*.15f),new Vector3(.28f,h,.105f),j%3==0?teal:j%3==1?paper:dark,.008f);
            }
            Box("shelf wall bracket",new Vector3(-3.02f,y-.13f,z-.26f),new Vector3(.24f,.22f,.025f),dark);
            Box("shelf wall bracket",new Vector3(-3.02f,y-.13f,z+.26f),new Vector3(.24f,.22f,.025f),dark);
        }
    }
    static void Fireplace(LofiRoomSample room)
    {
        float z=.30f;
        Box("hearth chimney",new Vector3(-3.055f,2.05f,z),new Vector3(.24f,1.94f,1.26f),cream,.04f);
        Box("hearth shadowed chamber",new Vector3(-3.02f,.72f,z),new Vector3(.07f,1.08f,1.16f),black,.02f);
        Box("hearth stone base",new Vector3(-2.83f,.105f,z),new Vector3(.72f,.16f,1.65f),stone,.04f);
        Box("hearth inner floor",new Vector3(-2.83f,.215f,z),new Vector3(.44f,.08f,1.10f),black);
        for(int side=0;side<2;side++)for(int j=0;j<5;j++)
            Box("rounded fireplace brick",new Vector3(-2.86f,.32f+j*.20f,z+(side==0?-.67f:.67f)),new Vector3(.43f,.19f,.26f),j%2==0?brick:stone,.022f);
        for(int j=0;j<6;j++)Box("fireplace lintel brick",new Vector3(-2.86f,1.27f,z-.625f+j*.25f),new Vector3(.43f,.18f,.24f),j%2==0?stone:brick,.022f);
        Box("fireplace oak mantel",new Vector3(-2.82f,1.40f,z),new Vector3(.60f,.13f,1.78f),dark,.03f);
        var ember=LofiRoomBuilder.Mat("glowing-log-embers","#5A1E0D",.16f,"#FA3B04");
        var glowing=new List<Renderer>();
        for(int i=0;i<4;i++)
        {
            var log=GameObject.CreatePrimitive(PrimitiveType.Cylinder);log.name="charred stacked firewood";
            log.transform.position=new Vector3(-2.80f+(i%2)*.09f,.29f+(i/2)*.11f,z+(i%2==0?-.09f:.09f));
            log.transform.localScale=new Vector3(.115f,.41f,.115f);log.transform.rotation=Quaternion.Euler(90,0,i%2==0?14:-14);
            log.GetComponent<Renderer>().sharedMaterial=dark;UnityEngine.Object.DestroyImmediate(log.GetComponent<Collider>());
            var glow=Box("glowing ember bed",new Vector3(-2.69f,.25f,z-.38f+i*.25f),new Vector3(.17f,.025f,.17f),ember,.018f);glowing.Add(glow.GetComponent<Renderer>());
        }
        for(int j=0;j<6;j++)Box("hearth front grate",new Vector3(-2.56f,.34f,z-.48f+j*.19f),new Vector3(.025f,.22f,.025f),black,.008f);
        var light=new GameObject("Hearth warm flicker").AddComponent<Light>();light.type=LightType.Point;light.range=4.8f;
        light.color=new Color(1,.43f,.13f);light.transform.position=new Vector3(-2.40f,.68f,z);light.shadows=LightShadows.Soft;light.shadowBias=.02f;light.shadowNormalBias=.08f;
        var h=new GameObject("Hearth ambience").AddComponent<LofiHearth>();room.hearth=h;h.fireLight=light;h.embers=glowing.ToArray();
        h.crackle=h.gameObject.AddComponent<AudioSource>();h.crackle.clip=AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/LofiRoom/Audio/fireplace.ogg");
        h.crackle.loop=true;h.crackle.volume=.42f;h.crackle.spatialBlend=.20f;h.crackle.minDistance=2;h.crackle.maxDistance=12;h.crackle.rolloffMode=AudioRolloffMode.Linear;h.transform.position=light.transform.position;
        Flames("layered hearth flames",new Vector3(-2.77f,.29f,z),0,36,.95f,new Vector3(.10f,.01f,.72f),new Vector2(.18f,.34f));
        Flames("small golden flame core",new Vector3(-2.66f,.30f,z),0,17,.60f,new Vector3(.03f,.01f,.58f),new Vector2(.10f,.20f));
        Flames("rising warm embers",new Vector3(-2.74f,.48f,z),1,4,2,new Vector3(.10f,.01f,.68f),new Vector2(.009f,.019f));
        Flames("light hearth smoke",new Vector3(-2.85f,.87f,z),2,3,1.3f,new Vector3(.05f,.01f,.50f),new Vector2(.12f,.21f));
    }
    static void Flames(string name,Vector3 p,int mode,float rate,float life,Vector3 box,Vector2 sizes)
    {
        var ps=new GameObject(name).AddComponent<ParticleSystem>();ps.transform.position=p;ps.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);
        var main=ps.main;main.startLifetime=new ParticleSystem.MinMaxCurve(life*.65f,life);main.startSpeed=new ParticleSystem.MinMaxCurve(.13f,.30f);main.maxParticles=mode==0?80:30;
        main.startSize3D=true;main.startSizeX=new ParticleSystem.MinMaxCurve(sizes.x,sizes.y);main.startSizeY=new ParticleSystem.MinMaxCurve(sizes.x*1.8f,sizes.y*2.3f);main.startSizeZ=.1f;
        main.simulationSpace=ParticleSystemSimulationSpace.World;main.startColor=new Color(1,1,1,mode==2?.2f:.8f);
        var shape=ps.shape;shape.shapeType=ParticleSystemShapeType.Box;shape.scale=box;shape.rotation=new Vector3(-90,0,0);
        var emission=ps.emission;emission.rateOverTime=rate;
        var velocity=ps.velocityOverLifetime;velocity.enabled=true;velocity.x=new ParticleSystem.MinMaxCurve(0);velocity.y=new ParticleSystem.MinMaxCurve(.23f);velocity.z=new ParticleSystem.MinMaxCurve(0);velocity.space=ParticleSystemSimulationSpace.World;
        var noise=ps.noise;noise.enabled=true;noise.strength=new ParticleSystem.MinMaxCurve(mode==1?.06f:.025f,mode==1?.09f:.045f);noise.frequency=.7f;noise.scrollSpeed=.25f;
        var size=ps.sizeOverLifetime;size.enabled=true;size.size=new ParticleSystem.MinMaxCurve(1,new AnimationCurve(new Keyframe(0,.35f),new Keyframe(.35f,1),new Keyframe(1,.03f)));
        var color=ps.colorOverLifetime;color.enabled=true;var g=new Gradient();g.SetKeys(new[]{new GradientColorKey(Color.white,0),new GradientColorKey(Color.white,1)},new[]{new GradientAlphaKey(0,0),new GradientAlphaKey(1,.13f),new GradientAlphaKey(.7f,.6f),new GradientAlphaKey(0,1)});color.color=g;
        var renderer=ps.GetComponent<ParticleSystemRenderer>();renderer.renderMode=ParticleSystemRenderMode.Billboard;renderer.alignment=ParticleSystemRenderSpace.View;renderer.shadowCastingMode=ShadowCastingMode.Off;
        var mat=new Material(Shader.Find("Yamyam/Hearth Flame"));mat.SetFloat("_Mode",mode);
        string path=root+"/Materials/fire-"+name.Replace(" ","-")+".mat";
        var old=AssetDatabase.LoadAssetAtPath<Material>(path);if(old){EditorUtility.CopySerialized(mat,old);UnityEngine.Object.DestroyImmediate(mat);mat=old;}else AssetDatabase.CreateAsset(mat,path);
        renderer.sharedMaterial=mat;ps.Play();
    }
    static Transform Target(string name,Vector3 position)
    {var t=new GameObject(name).transform;t.position=position;t.rotation=Quaternion.Euler(90,0,0);return t;}
    static void Desk(LofiRoomSample room)
    {
        string[] remove={"desktop","desk leg","drawer cabinet","drawer","drawer handle","monitor stand","monitor stalk","monitor","screen","screen work lines","desk mat","keyboard","key","mouse","pc","pc light","monitor cable","pc fan rounded bezel","pc radial fan blade","chair seat","chair back","chair post","chair base x","chair base z","armrest","chair sewn piping"};
        foreach(var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(r=>remove.Contains(r.name)).ToArray())UnityEngine.Object.DestroyImmediate(r.gameObject);
        foreach(var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(r=>r.name.StartsWith("lamp ")))r.transform.position+=Vector3.right*.5f;
        room.deskLight.transform.position+=Vector3.right*.5f;
        foreach(var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(r=>r.name.StartsWith("ceramic tea mug")||r.name=="mug handle"||r.name=="tea surface"))r.transform.position+=new Vector3(.05f,0,.23f);
        var headphones=GameObject.Find("Tripo Headphones");if(headphones)headphones.transform.position+=new Vector3(.48f,-.018f,.15f);
        Box("simple oak desktop",new Vector3(1,.77f,1.42f),new Vector3(1.68f,.085f,.67f),oak,.035f);
        for(int x=0;x<2;x++)for(int z=0;z<2;z++)Box("simple desk leg",new Vector3(.25f+x*1.50f,.38f,1.14f+z*.54f),new Vector3(.055f,.71f,.055f),dark,.01f);
        Box("iMac low stand foot",new Vector3(1,.83f,1.63f),new Vector3(.24f,.018f,.18f),metal,.015f);
        Box("iMac slim stand",new Vector3(1,.99f,1.67f),new Vector3(.067f,.30f,.04f),metal);
        Box("iMac all-in-one body",new Vector3(1,1.23f,1.65f),new Vector3(.58f,.395f,.032f),metal,.018f);
        Box("iMac quiet display",new Vector3(1,1.255f,1.630f),new Vector3(.55f,.322f,.005f),Mat("display","#1E474B",.25f),.008f);
        Box("iMac lower chin",new Vector3(1,1.053f,1.63f),new Vector3(.56f,.055f,.008f),cream,.005f);
        var text=Mat("screen-highlight","#83B6A5");
        for(int i=0;i<4;i++)Box("quiet work line",new Vector3(.95f,1.33f-i*.038f,1.626f),new Vector3(.20f+i*.018f,.006f,.003f),text,.001f);
        Box("compact keyboard",new Vector3(.96f,.831f,1.33f),new Vector3(.37f,.019f,.125f),cream,.009f);
        for(int row=0;row<3;row++)for(int x=0;x<10;x++)Box("small keyboard key",new Vector3(.801f+x*.035f,.843f,1.286f+row*.036f),new Vector3(.027f,.006f,.025f),paper,.002f);
        Box("small wireless mouse",new Vector3(1.30f,.837f,1.33f),new Vector3(.050f,.031f,.08f),cream,.019f);
        Box("reading chair seat",new Vector3(1,.45f,.84f),new Vector3(.48f,.10f,.45f),teal,.045f);
        Box("reading chair back",new Vector3(1,.87f,.57f),new Vector3(.48f,.78f,.075f),teal,.045f);
        for(int x=0;x<2;x++)for(int z=0;z<2;z++)Box("reading chair leg",new Vector3(.80f+x*.40f,.24f,.66f+z*.37f),new Vector3(.043f,.39f,.043f),dark,.008f);
        var left=Target("left keyboard contact",new Vector3(.89f,.88f,1.32f));var right=Target("right keyboard contact",new Vector3(1.075f,.88f,1.32f));
        var book=new GameObject("native reading book").transform;book.position=new Vector3(1,.99f,1.12f);
        var cover=Box("open book cover",book.position,new Vector3(.35f,.025f,.23f),dark,.009f);cover.transform.SetParent(book,true);
        var pages=Box("open book paper",book.position+Vector3.up*.018f,new Vector3(.33f,.019f,.21f),paper,.004f);pages.transform.SetParent(book,true);
        Box("open book spine",book.position+Vector3.up*.03f,new Vector3(.006f,.005f,.208f),oak,.002f).transform.SetParent(book,true);
        for(int side=0;side<2;side++)for(int line=0;line<6;line++)Box("book text line",book.position+new Vector3(side==0?-.083f:.083f,.032f,-.075f+line*.027f),new Vector3(.12f,.002f,.0025f),dark,.001f).transform.SetParent(book,true);
        var lp=Target("left book grip",new Vector3(.82f,1.025f,1.14f));lp.SetParent(book,true);
        var rp=Target("right book grip",new Vector3(1.18f,1.025f,1.14f));rp.SetParent(book,true);
        book.rotation=Quaternion.Euler(-18,0,0);LofiHearthMotion.Attach(room,root,left,right,book,lp,rp);book.gameObject.SetActive(false);
        var closed=Box("closed reading book on desk",new Vector3(1.47f,.84f,1.25f),new Vector3(.25f,.035f,.20f),dark,.008f);room.activities.closedBook=closed;
        if(room.music){room.music.playOnAwake=true;room.music.volume=.18f;}
    }
    static void Turntable(LofiRoomSample room)
    {
        Vector3 p=new(-1.8f,.62f,1.86f);
        Box("window music table",p,new Vector3(.93f,.065f,.53f),oak,.025f);
        for(int x=0;x<2;x++)for(int z=0;z<2;z++)Box("music table slender leg",new Vector3(p.x-.38f+x*.76f,.32f,p.z-.20f+z*.40f),new Vector3(.045f,.57f,.045f),dark,.008f);
        var player=Box("record player walnut base",p+Vector3.up*.085f,new Vector3(.64f,.12f,.39f),dark,.025f);
        player.AddComponent<BoxCollider>();
        var vinyl=GameObject.CreatePrimitive(PrimitiveType.Cylinder);vinyl.name="33 rpm vinyl record";
        vinyl.transform.position=p+new Vector3(-.065f,.153f,0);vinyl.transform.localScale=new Vector3(.30f,.005f,.30f);vinyl.GetComponent<Renderer>().sharedMaterial=black;UnityEngine.Object.DestroyImmediate(vinyl.GetComponent<Collider>());
        var label=GameObject.CreatePrimitive(PrimitiveType.Cylinder);label.name="vinyl teal center label";label.transform.SetParent(vinyl.transform,false);label.transform.localScale=new Vector3(.28f,1.1f,.28f);label.transform.localPosition=Vector3.up*.6f;label.GetComponent<Renderer>().sharedMaterial=teal;UnityEngine.Object.DestroyImmediate(label.GetComponent<Collider>());
        Box("vinyl original cream label mark",p+new Vector3(-.066f,.162f,.013f),new Vector3(.043f,.001f,.008f),paper,.001f).transform.SetParent(vinyl.transform,true);
        Box("vinyl small label detail",p+new Vector3(-.077f,.162f,-.009f),new Vector3(.020f,.001f,.005f),paper,.001f).transform.SetParent(vinyl.transform,true);
        var arm=new GameObject("record player tonearm").transform;arm.position=p+new Vector3(.23f,.163f,.13f);
        var bar=Box("tonearm silver wand",arm.position+new Vector3(-.10f,0,-.09f),new Vector3(.014f,.014f,.27f),metal,.006f);bar.transform.rotation=Quaternion.Euler(0,43,0);bar.transform.SetParent(arm,true);
        Box("tonearm cartridge",p+new Vector3(.048f,.156f,-.07f),new Vector3(.035f,.025f,.045f),black,.006f).transform.SetParent(arm,true);
        Box("record player brass control",p+new Vector3(.255f,.14f,-.13f),new Vector3(.045f,.025f,.045f),metal,.01f);
        var turntable=player.AddComponent<LofiTurntable>();turntable.record=vinyl.transform;turntable.tonearm=arm;turntable.music=room.music;
        room.music.transform.position=p+Vector3.up*.13f;room.music.spatialBlend=.2f;room.music.minDistance=3;room.music.maxDistance=14;room.music.rolloffMode=AudioRolloffMode.Linear;
    }
}
