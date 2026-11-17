using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Yamyam.LofiRoom;

public static class LofiNatureArt
{
    public const string Root="Assets/LofiRoom/GeneratedWebFinalV6";
    static System.Random random=new(241106);
    static int number;
    public static int leafCount;
    static float R(float a,float b)=>(float)(a+random.NextDouble()*(b-a));
    static Material leaf,stem,soil,ceramic,brass,paper,dark,wood;

    public static void ConfigureTextureImports()
    {
        foreach(string guid in AssetDatabase.FindAssets("t:Texture2D",new[]{"Assets/LofiRoom/TexturesNatureV2"}))
        {
            string path=AssetDatabase.GUIDToAssetPath(guid);var importer=(TextureImporter)AssetImporter.GetAtPath(path);
            bool normal=Path.GetFileName(path)=="normal.png",color=Path.GetFileName(path)=="basecolor.png"||Path.GetFileName(path)=="map.png";
            var type=normal?TextureImporterType.NormalMap:TextureImporterType.Default;int size=color&&Path.GetFileName(path)!="map.png"?4096:2048;
            if(importer.textureType==type && importer.maxTextureSize==size && importer.anisoLevel==8 && importer.sRGBTexture==color)continue;
            importer.textureType=type;importer.sRGBTexture=color;importer.maxTextureSize=size;importer.mipmapEnabled=true;importer.isReadable=false;importer.anisoLevel=8;importer.filterMode=FilterMode.Trilinear;importer.textureCompression=TextureImporterCompression.CompressedHQ;importer.compressionQuality=100;importer.SaveAndReimport();
        }
    }

    public static void DressRoom()
    {
        number=0;leafCount=0;random=new System.Random(241106);
        foreach(var go in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(r=>r.name=="plant leaf"||r.name=="plant pot").Select(r=>r.gameObject).ToArray())UnityEngine.Object.DestroyImmediate(go);
        leaf=Material("living-leaf",new Color(.25f,.45f,.22f),5,.28f,0);leaf.SetFloat("_Cull",0);leaf.SetFloat("_WindStrength",.028f);
        stem=Material("plant-stem",new Color(.24f,.32f,.12f),0,.23f,0);
        soil=Material("pot-soil",new Color(.17f,.12f,.08f),3,.1f,0);
        ceramic=Material("warm-ceramic",new Color(.69f,.48f,.29f),0,.38f,0);
        brass=Material("brushed-brass",new Color(.58f,.43f,.24f),4,.5f,.7f);
        paper=Material("book-pages",new Color(.83f,.78f,.64f),3,.18f,0);
        dark=Material("hardware-dark",new Color(.065f,.08f,.085f),4,.42f,.35f);
        wood=Material("carved-oak",new Color(.43f,.25f,.13f),1,.32f,0);
        Fern(new Vector3(-2.6f,.04f,-1.55f),.95f);
        BroadPlant(new Vector3(2.55f,.04f,1.55f),1.25f);
        BroadPlant(new Vector3(1.9f,.835f,1.22f),.28f);
        WindowPlanter();HangingVines();FurnitureDetail();WallMap();
    }

    public static Material Material(string name,Color color,float pattern,float smooth,float metallic)
    {
        string path=Root+"/Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(!m){m=new Material(Shader.Find("Yamyam/Lofi Detailed Surface"));AssetDatabase.CreateAsset(m,path);}
        m.SetColor("_BaseColor",color);m.SetFloat("_Pattern",pattern);m.SetFloat("_Smoothness",smooth);m.SetFloat("_Metallic",metallic);m.SetFloat("_DetailStrength",.45f);EditorUtility.SetDirty(m);return m;
    }
    static GameObject MeshObject(string name,Mesh mesh,Material material,Vector3 p,Quaternion q)
    {
        mesh.name=name;string path=Root+"/Meshes/nature-"+(number++)+".asset";
        var previous=AssetDatabase.LoadAssetAtPath<Mesh>(path);
        if(previous){EditorUtility.CopySerialized(mesh,previous);UnityEngine.Object.DestroyImmediate(mesh);mesh=previous;mesh.UploadMeshData(false);EditorUtility.SetDirty(mesh);}else AssetDatabase.CreateAsset(mesh,path);
        var go=new GameObject(name,typeof(MeshFilter),typeof(MeshRenderer));go.transform.SetPositionAndRotation(p,q);go.GetComponent<MeshFilter>().sharedMesh=mesh;go.GetComponent<MeshRenderer>().sharedMaterial=material;return go;
    }
    static Mesh Surface(List<Vector3> v,List<Vector2> uv,List<int> tri,List<Color> colors=null)
    {
        if(v.Any(p=>!float.IsFinite(p.x)||!float.IsFinite(p.y)||!float.IsFinite(p.z)))throw new InvalidOperationException("Non-finite nature mesh vertex");
        var m=new Mesh();if(v.Count>65535)m.indexFormat=UnityEngine.Rendering.IndexFormat.UInt32;
        m.SetVertices(v);m.SetUVs(0,uv);m.SetTriangles(tri,0);if(colors!=null)m.SetColors(colors);m.RecalculateNormals();m.RecalculateTangents();m.RecalculateBounds();return m;
    }
    static GameObject Lathe(string name,Vector3 p,Vector2[] profile,Material material,int sides=32)
    {
        var v=new List<Vector3>();var uv=new List<Vector2>();var tri=new List<int>();
        for(int y=0;y<profile.Length;y++)for(int x=0;x<=sides;x++){float a=x*2*Mathf.PI/sides;v.Add(new Vector3(Mathf.Cos(a)*profile[y].x,profile[y].y,Mathf.Sin(a)*profile[y].x));uv.Add(new Vector2(x/(float)sides,y/(float)(profile.Length-1)));}
        for(int y=0;y<profile.Length-1;y++)for(int x=0;x<sides;x++){int a=y*(sides+1)+x,b=a+sides+1;tri.AddRange(new[]{a,b,a+1,a+1,b,b+1});}
        return MeshObject(name,Surface(v,uv,tri),material,p,Quaternion.identity);
    }
    static Vector3 Bezier(Vector3 a,Vector3 b,Vector3 c,Vector3 d,float t){float s=1-t;return s*s*s*a+3*s*s*t*b+3*s*t*t*c+t*t*t*d;}
    static void Tube(string name,Vector3 a,Vector3 b,Vector3 c,Vector3 d,float radius,Material material,int segments=16)
    {
        const int sides=6;var v=new List<Vector3>();var uv=new List<Vector2>();var tri=new List<int>();
        for(int i=0;i<=segments;i++)
        {
            float t=i/(float)segments;Vector3 p=Bezier(a,b,c,d,t);Vector3 tangent=(Bezier(a,b,c,d,Mathf.Min(1,t+.002f))-Bezier(a,b,c,d,Mathf.Max(0,t-.002f))).normalized;
            Vector3 side=Vector3.Cross(tangent,Vector3.up);if(side.sqrMagnitude<.001f)side=Vector3.Cross(tangent,Vector3.right);side.Normalize();Vector3 up=Vector3.Cross(tangent,side).normalized;
            for(int j=0;j<=sides;j++){float angle=j*2*Mathf.PI/sides;v.Add(p+(side*Mathf.Cos(angle)+up*Mathf.Sin(angle))*radius);uv.Add(new Vector2(j/(float)sides,t));}
        }
        for(int i=0;i<segments;i++)for(int j=0;j<sides;j++){int a0=i*(sides+1)+j,b0=a0+sides+1;tri.AddRange(new[]{a0,a0+1,b0,a0+1,b0+1,b0});}
        MeshObject(name,Surface(v,uv,tri),material,Vector3.zero,Quaternion.identity);
    }
    static void Leaf(Vector3 p,Quaternion rotation,float length,float width,float curl=.18f,bool lobes=false)
    {
        const int rows=14;var v=new List<Vector3>();var uv=new List<Vector2>();var tri=new List<int>();var colors=new List<Color>();
        for(int y=0;y<=rows;y++)for(int x=0;x<5;x++)
        {
            float t=y/(float)rows,u=x*.5f-1;float envelope=Mathf.Pow(Mathf.Max(0,Mathf.Sin(Mathf.PI*t)),.7f);
            if(lobes)envelope*=.78f+.22f*Mathf.Cos(t*9*Mathf.PI);
            v.Add(new Vector3(u*width*.5f*envelope,t*length,length*(curl*t*t+.045f*Mathf.Sin(t*Mathf.PI)*(1-Mathf.Abs(u)))));
            uv.Add(new Vector2((u+1)*.5f,t));colors.Add(new Color(t*t,1,1,1));
        }
        for(int y=0;y<rows;y++)for(int x=0;x<4;x++){int a=y*5+x;tri.AddRange(new[]{a,a+5,a+1,a+1,a+5,a+6});}
        MeshObject("curved veined leaf",Surface(v,uv,tri,colors),leaf,p,rotation);leafCount++;
    }
    static float Pot(Vector3 p,float s)
    {
        Lathe("ceramic plant pot",p,new[]{new Vector2(0,0),new Vector2(.12f*s,0),new Vector2(.16f*s,.035f*s),new Vector2(.20f*s,.29f*s),new Vector2(.215f*s,.31f*s),new Vector2(.21f*s,.335f*s),new Vector2(.175f*s,.335f*s),new Vector2(.17f*s,.285f*s)},ceramic);
        Lathe("visible pot soil",p,new[]{new Vector2(0,.292f*s),new Vector2(.174f*s,.292f*s)},soil);return .30f*s;
    }
    static void BroadPlant(Vector3 p,float s)
    {
        float pot=Pot(p,s*.8f);Vector3 root=p+Vector3.up*pot;
        for(int i=0;i<15;i++)
        {
            float a=i*137.5f*Mathf.Deg2Rad;Vector3 end=root+new Vector3(Mathf.Cos(a)*R(.12f,.31f),R(.28f,.73f),Mathf.Sin(a)*R(.12f,.31f))*s;
            Tube("natural curved stem",root,root+Vector3.up*.3f*s,end-Vector3.up*.15f*s,end,.007f*s,stem);
            Quaternion q=Quaternion.Euler(R(15,55),-a*Mathf.Rad2Deg,R(-25,25));Leaf(end,q,R(.22f,.43f)*s,R(.12f,.23f)*s,.25f,i%3==0);
        }
    }
    static void Fern(Vector3 p,float s)
    {
        Vector3 root=p+Vector3.up*Pot(p,s);
        for(int i=0;i<11;i++)
        {
            float a=i*2*Mathf.PI/11;Vector3 dir=new Vector3(Mathf.Cos(a),0,Mathf.Sin(a));Vector3 end=root+dir*.48f*s+Vector3.up*R(.25f,.58f)*s;
            Tube("fern frond",root,root+Vector3.up*.6f*s,end+Vector3.up*.15f*s,end,.004f*s,stem);
            for(int j=2;j<10;j++)
            {
                float t=j/10f;Vector3 at=Bezier(root,root+Vector3.up*.6f*s,end+Vector3.up*.15f*s,end,t);
                for(int side=-1;side<=1;side+=2){Quaternion q=Quaternion.LookRotation(dir)*Quaternion.Euler(15,side*65,side*63);Leaf(at,q,(.19f*(1-t)+.035f)*s,.045f*s,.12f);}
            }
        }
    }
    static void WindowPlanter()
    {
        var sill=GameObject.CreatePrimitive(PrimitiveType.Cube);sill.name="deep wooden window sill";sill.transform.position=new Vector3(-1.8f,.85f,2.14f);sill.transform.localScale=new Vector3(2.18f,.075f,.37f);sill.GetComponent<Renderer>().sharedMaterial=wood;UnityEngine.Object.DestroyImmediate(sill.GetComponent<Collider>());
        Vector3 p=new(-1.8f,.89f,2.09f);
        for(int i=0;i<3;i++)
        {
            var cp=p+Vector3.right*(i-1)*.5f;float h=Pot(cp,.55f);
            for(int j=0;j<19;j++){Vector3 pos=cp+new Vector3(R(-.06f,.06f),h,R(-.06f,.06f));Leaf(pos,Quaternion.Euler(R(5,35),R(0,360),R(-18,18)),R(.18f,.42f),R(.012f,.03f),.35f);}
        }
    }
    static void HangingVines()
    {
        Vector3 top=new(-2.75f,2.58f,1.74f);Pot(top,.55f);
        Vector3 hook=top+Vector3.up*.43f;
        Tube("hanging planter wall bracket",new Vector3(-3.1f,2.94f,1.74f),new Vector3(-3.0f,2.98f,1.74f),hook,hook,.015f,brass,12);
        for(int i=0;i<3;i++){float a=i*2*Mathf.PI/3;Vector3 bottom=top+new Vector3(Mathf.Cos(a)*.10f,.17f,Mathf.Sin(a)*.10f);Tube("planter suspension cord",bottom,bottom,hook,hook,.004f,stem,10);}
        for(int strand=0;strand<4;strand++)
        {
            Vector3 a=top+new Vector3(.05f*strand,.16f,-.02f*strand),d=a+new Vector3(.15f+strand*.06f,-1.3f-strand*.16f,-.1f*strand);
            Vector3 b=a+new Vector3(.25f,-.12f,0),c=d+new Vector3(-.1f,.36f,.05f);Tube("trailing pothos vine",a,b,c,d,.007f,stem,24);
            for(int j=0;j<12;j++){float t=j/12f;Vector3 p=Bezier(a,b,c,d,t);Leaf(p,Quaternion.Euler(10,j*97+strand*60,125+(j%2)*100),R(.12f,.18f),R(.09f,.14f),.18f);}
        }
    }
    static void FurnitureDetail()
    {
        // Rounded rims and real cross sections replace the initial solid-box props.
        Vector3 mug=new Vector3(1.35f,.83f,1.02f);
        Lathe("ceramic tea mug",mug,new[]{new Vector2(0,0),new Vector2(.055f,0),new Vector2(.066f,.015f),new Vector2(.068f,.135f),new Vector2(.061f,.145f),new Vector2(.054f,.14f),new Vector2(.052f,.027f),new Vector2(0,.027f)},ceramic,40);
        Tube("mug handle",mug+new Vector3(.055f,.115f,0),mug+new Vector3(.135f,.14f,0),mug+new Vector3(.14f,.02f,0),mug+new Vector3(.055f,.035f,0),.013f,ceramic,20);
        Lathe("tea surface",mug,new[]{new Vector2(0,.113f),new Vector2(.053f,.113f)},Material("tea",new Color(.18f,.095f,.035f),0,.65f,0));
        for(int i=0;i<2;i++)
        {
            float x=.32f+i*.75f;
            Tube("monitor cable",new Vector3(x,1.11f,1.69f),new Vector3(x+.2f,.9f,1.9f),new Vector3(x+.4f,.84f,1.7f),new Vector3(1.6f,.86f,1.56f),.009f,dark,24);
        }
        for(int fan=0;fan<2;fan++)
        {
            Vector3 p=new(1.75f,1.0f+fan*.21f,1.362f);
            var ring=Lathe("pc fan rounded bezel",Vector3.zero,new[]{new Vector2(.058f,0),new Vector2(.073f,.005f),new Vector2(.074f,.018f),new Vector2(.06f,.024f)},dark,32);ring.transform.SetPositionAndRotation(p,Quaternion.Euler(90,0,0));
            for(int j=0;j<7;j++){float a=j*2*Mathf.PI/7;Vector3 inner=p+new Vector3(Mathf.Cos(a)*.012f,Mathf.Sin(a)*.012f,-.006f),outer=p+new Vector3(Mathf.Cos(a+.45f)*.055f,Mathf.Sin(a+.45f)*.055f,-.006f);Tube("pc radial fan blade",inner,inner,outer,outer,.008f,dark,4);}
        }
        // Copper window latch, chair piping and book-page bands are separately readable.
        Tube("window brass latch",new Vector3(-1.83f,1.67f,2.19f),new Vector3(-1.8f,1.7f,2.12f),new Vector3(-1.71f,1.7f,2.12f),new Vector3(-1.7f,1.68f,2.19f),.014f,brass,16);
        var piping=Material("chair-fabric-piping",new Color(.31f,.47f,.39f),2,.18f,0);
        for(int side=0;side<2;side++)
        {
            float x=.8f+(side==0?-.24f:.24f);Tube("chair sewn piping",new Vector3(x,.53f,.15f),new Vector3(x,.7f,.11f),new Vector3(x,1.12f,.14f),new Vector3(x,1.27f,.18f),.009f,piping,20);
        }
        var fabric=Material("woven-chair",new Color(.16f,.33f,.32f),2,.18f,0);
        foreach(var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(r=>r.name.StartsWith("chair seat")||r.name.StartsWith("chair back")))r.sharedMaterial=fabric;
        var carpet=Material("woven-rug",new Color(.22f,.38f,.34f),2,.08f,0);
        var rug=GameObject.Find("rug");if(rug)rug.GetComponent<MeshRenderer>().sharedMaterial=carpet;
        foreach(var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(r=>r.name=="book"))
        {
            Vector3 p=r.transform.position;
            for(int j=0;j<4;j++)Tube("fine book spine band",p+new Vector3(.151f,-.11f+j*.065f,-.046f),p+new Vector3(.152f,-.11f+j*.065f,-.046f),p+new Vector3(.152f,-.11f+j*.065f,.046f),p+new Vector3(.151f,-.11f+j*.065f,.046f),.003f,paper,2);
        }
        // Original corner beams and skirting unify the natural wooden room.
        Tube("back wall skirting",new Vector3(-3.07f,.12f,2.23f),new Vector3(-1,.12f,2.23f),new Vector3(1,.12f,2.23f),new Vector3(3.05f,.12f,2.23f),.045f,wood,8);
        Tube("window upper wood trim",new Vector3(-2.9f,2.86f,2.22f),new Vector3(-2,2.86f,2.22f),new Vector3(-1,2.86f,2.22f),new Vector3(-.7f,2.86f,2.22f),.055f,wood,8);
    }
    static void WallMap()
    {
        foreach(var r in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(r=>r.name=="map island"||r.name=="map paper").ToArray())UnityEngine.Object.DestroyImmediate(r.gameObject);
        var frame=GameObject.Find("wall map");frame.transform.localScale=new Vector3(1,1.2f,1);
        var map=GameObject.CreatePrimitive(PrimitiveType.Quad);map.name="original forest map artwork";map.transform.position=new Vector3(.9f,2.4f,2.173f);map.transform.localScale=new Vector3(1.2f,.675f,1);UnityEngine.Object.DestroyImmediate(map.GetComponent<Collider>());
        var mat=Material("original-forest-map",Color.white,0,.12f,0);mat.SetFloat("_Cull",0);mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/LofiRoom/TexturesNatureV2/map.png"));map.GetComponent<Renderer>().sharedMaterial=mat;
    }

    public static void ApplyImportedMaterial(GameObject go,string kind)
    {
        string dir="Assets/LofiRoom/TexturesNatureV2/"+kind;
        var textures=AssetDatabase.FindAssets("t:Texture2D",new[]{dir}).Select(AssetDatabase.GUIDToAssetPath).ToArray();
        string Find(string word)=>textures.First(p=>Path.GetFileName(p).ToLowerInvariant().Contains(word));
        var mat=Material(kind+"-4k-pbr",Color.white,0,.3f,0);
        mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Find("basecolor")));
        mat.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Find("normal")));
        mat.SetTexture("_RoughnessMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Find("roughness")));
        mat.SetTexture("_MetallicMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Find("metallic")));
        mat.SetFloat("_UsePbrMaps",1);mat.SetFloat("_NormalStrength",kind=="hero"?.45f:.6f);
        foreach(var r in go.GetComponentsInChildren<Renderer>())r.sharedMaterial=mat;
        if(kind=="hero")AddHairMask(go,mat,Find("basecolor"));
        EditorUtility.SetDirty(mat);
    }
    static void AddHairMask(GameObject actor,Material material,string basePath)
    {
        var skin=actor.GetComponentInChildren<SkinnedMeshRenderer>();var source=skin.sharedMesh;
        var mesh=UnityEngine.Object.Instantiate(source);var p=mesh.vertices;var uv=mesh.uv;
        var decoded=new Texture2D(2,2,TextureFormat.RGBA32,false);decoded.LoadImage(File.ReadAllBytes(basePath));
        var vertices=mesh.vertices;float low=float.MaxValue,high=float.MinValue;
        var canonical=new Vector3[p.Length];
        for(int i=0;i<p.Length;i++){canonical[i]=actor.transform.InverseTransformPoint(skin.transform.TransformPoint(p[i]));low=Mathf.Min(low,canonical[i].y);high=Mathf.Max(high,canonical[i].y);}
        var head=actor.GetComponentsInChildren<Transform>().First(t=>t.name=="mixamorig:Head");Vector3 center=actor.transform.InverseTransformPoint(head.position);
        var colors=new Color[p.Length];int masked=0;
        for(int i=0;i<p.Length;i++)
        {
            var c=decoded.GetPixelBilinear(uv[i].x,uv[i].y);float luminance=c.r*.3f+c.g*.6f+c.b*.1f;
            float height=(canonical[i].y-low)/(high-low);float rear=center.z-canonical[i].z;
            bool brown=c.r>c.b*1.23f && c.r>c.g*1.03f && luminance<.58f;
            float weight=height>.80f&&brown?Mathf.SmoothStep(0,1,Mathf.Clamp01((rear-.012f)/.17f)):0;
            float along=Mathf.Clamp01((.985f-height)/.16f);
            colors[i]=new Color(weight,along,1,1);if(weight>.05f)masked++;
        }
        UnityEngine.Object.DestroyImmediate(decoded);mesh.colors=colors;mesh.name="Tripo hero with ponytail secondary-motion weights";
        string path=Root+"/Meshes/hero-hair-mask.asset";var existing=AssetDatabase.LoadAssetAtPath<Mesh>(path);
        if(existing){EditorUtility.CopySerialized(mesh,existing);UnityEngine.Object.DestroyImmediate(mesh);mesh=existing;}else AssetDatabase.CreateAsset(mesh,path);
        skin.sharedMesh=mesh;material.SetFloat("_HairEnabled",1);
        var motion=actor.AddComponent<LofiHairMotion>();motion.head=head;motion.skin=skin;
        Debug.Log("LOFI_HAIR_MASK vertices="+masked+" total="+vertices.Length);
    }
}
