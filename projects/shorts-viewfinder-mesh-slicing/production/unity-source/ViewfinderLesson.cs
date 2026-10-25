using System;
using System.Collections.Generic;
using UnityEngine;

namespace YamyamCoding.ViewfinderLesson {
// An independently authored teaching implementation, not recovered Viewfinder code.
[ExecuteAlways]
public sealed class Demo : MonoBehaviour {
    [Range(0,1)] public float previewPhase;
    float previousPreview=-1;
    void Update(){if(observer&&original&&previewPhase!=previousPreview)Tick(previewPhase);}
    public Camera observer;
    public GameObject wall, bridge, marker, volume;
    public MeshFilter wallMesh;
    public Material stone, inserted, guide, line;
    [SerializeField] Mesh original;
    public int remainingTriangles;
    public bool probeSupported;
    [SerializeField] List<LineRenderer> wireLines=new List<LineRenderer>();
    public static Demo Build() {
        var d=new GameObject("Viewfinder mesh lesson — original implementation").AddComponent<Demo>();
        d.stone=Mat("Existing world",new Color(.20f,.34f,.39f));
        d.inserted=Mat("Inserted floor",new Color(.95f,.69f,.18f));
        d.guide=new Material(Shader.Find("Sprites/Default")){name="Boundary guide",color=new Color(1,.84f,.35f)};
        d.line=Mat("Mesh edges",new Color(.60f,.87f,.87f));
        var cam=new GameObject("Observer camera").AddComponent<Camera>();cam.transform.position=new Vector3(7,7,-9);cam.transform.LookAt(new Vector3(0,.65f,0));cam.backgroundColor=Color.black;cam.clearFlags=CameraClearFlags.SolidColor;cam.fieldOfView=39;cam.nearClipPlane=.1f;cam.farClipPlane=100;d.observer=cam;
        var key=new GameObject("Soft key").AddComponent<Light>();key.type=LightType.Directional;key.intensity=1.4f;key.transform.rotation=Quaternion.Euler(45,-30,0);
        RenderSettings.ambientLight=new Color(.45f,.45f,.45f);
        Part("Near platform",new Vector3(-3,-.25f,0),new Vector3(3.8f,.5f,4.8f),d.stone);
        Part("Far platform",new Vector3(3,-.25f,0),new Vector3(3.8f,.5f,4.8f),d.stone);
        for(int i=-5;i<=5;i++) { if(Mathf.Abs(i)<1.1f)continue;
            Edge("Ground grid",new[]{new Vector3(i,.014f,-2.4f),new Vector3(i,.014f,2.4f)},d.line,.012f);
        }
        for(int z=-2;z<=2;z++) { Edge("Left grid",new[]{new Vector3(-4.9f,.015f,z),new Vector3(-1.1f,.015f,z)},d.line,.012f);Edge("Right grid",new[]{new Vector3(1.1f,.015f,z),new Vector3(4.9f,.015f,z)},d.line,.012f); }
        d.wall=new GameObject("Existing wall — actual mesh triangles");d.wallMesh=d.wall.AddComponent<MeshFilter>();d.wall.AddComponent<MeshRenderer>().sharedMaterial=d.stone;d.original=GridWall();d.wallMesh.sharedMesh=d.original;
        var wires=new GameObject("Actual triangle edge overlay");var wireMat=new Material(Shader.Find("Sprites/Default"));wireMat.color=new Color(.45f,.95f,.95f);
        for(int i=0;i<360;i++){var o=new GameObject("Mesh edge");o.transform.parent=wires.transform;var l=o.AddComponent<LineRenderer>();l.sharedMaterial=wireMat;l.startWidth=l.endWidth=.022f;l.positionCount=2;d.wireLines.Add(l);}
        d.bridge=Part("Inserted floor and matching collider",new Vector3(0,-.11f,0),new Vector3(2.4f,.22f,3.8f),d.inserted);d.bridge.SetActive(false);
        d.volume=new GameObject("Photo region boundary");
        foreach(float y in new[]{.05f,2.6f})foreach(float z in new[]{-1.9f,1.9f})Edge("Boundary X",new[]{new Vector3(-1.2f,y,z),new Vector3(1.2f,y,z)},d.guide,.055f,d.volume.transform);
        foreach(float x in new[]{-1.2f,1.2f})foreach(float z in new[]{-1.9f,1.9f})Edge("Boundary Y",new[]{new Vector3(x,.05f,z),new Vector3(x,2.6f,z)},d.guide,.055f,d.volume.transform);
        foreach(float x in new[]{-1.2f,1.2f})foreach(float y in new[]{.05f,2.6f})Edge("Boundary Z",new[]{new Vector3(x,y,-1.9f),new Vector3(x,y,1.9f)},d.guide,.055f,d.volume.transform);
        d.marker=GameObject.CreatePrimitive(PrimitiveType.Sphere);d.marker.name="Test probe — our collider test";d.marker.transform.localScale=Vector3.one*.3f;d.marker.GetComponent<Renderer>().sharedMaterial=Mat("Probe",new Color(.5f,1,.55f));
        d.marker.GetComponent<Collider>().enabled=false;
        d.Tick(0);return d;
    }
    public void Tick(float phase) {
        phase=Mathf.Clamp01(phase);previewPhase=previousPreview=phase;volume.SetActive(phase>.12f&&phase<.83f);
        float cut=Mathf.Clamp01((phase-.30f)/.17f);float half=Mathf.Lerp(.001f,1.2f,cut);
        wallMesh.sharedMesh=cut>0?RemoveBox(original,new Vector3(-half,-.1f,-2),new Vector3(half,2.8f,2)):original;
        remainingTriangles=wallMesh.sharedMesh.triangles.Length/3;
        var v=wallMesh.sharedMesh.vertices;var tr=wallMesh.sharedMesh.triangles;
        for(int i=0;i<wireLines.Count;i++){var l=wireLines[i];l.enabled=i<tr.Length&&phase<.65f;if(l.enabled){int start=i/3*3,next=start+(i%3+1)%3;l.SetPosition(0,v[tr[i]]+Vector3.back*.006f);l.SetPosition(1,v[tr[next]]+Vector3.back*.006f);}}
        bridge.SetActive(phase>.51f);
        float x=Mathf.Lerp(-3,3,Mathf.Clamp01((phase-.60f)/.30f));Physics.SyncTransforms();RaycastHit hit;
        probeSupported=Physics.Raycast(new Vector3(x,4,-.65f),Vector3.down,out hit,10);marker.transform.position=new Vector3(x,probeSupported?hit.point.y+.15f:-2,-.65f);
        observer.transform.position=Vector3.Lerp(new Vector3(7,7,-9),new Vector3(6,5,-10),Mathf.Clamp01((phase-.7f)/.3f));observer.transform.LookAt(new Vector3(0,.65f,0));
    }
    static Mesh GridWall() {
        var v=new List<Vector3>();var tr=new List<int>();
        for(int x=0;x<10;x++)for(int y=0;y<4;y++){int b=v.Count;float a=-3+x*.6f,c=y*.65f;v.Add(new Vector3(a,c,.8f));v.Add(new Vector3(a+.6f,c,.8f));v.Add(new Vector3(a+.6f,c+.65f,.8f));v.Add(new Vector3(a,c+.65f,.8f));tr.AddRange(new[]{b,b+2,b+1,b,b+3,b+2});}
        var m=new Mesh();m.name="40 wall quads / 80 source triangles";m.SetVertices(v);m.SetTriangles(tr,0);m.RecalculateNormals();return m;
    }
    static List<Vector3> Clip(List<Vector3> src,Vector3 normal,float plane,bool inside) {
        var dst=new List<Vector3>();if(src.Count==0)return dst;var a=src[src.Count-1];float da=Vector3.Dot(normal,a)-plane;bool ina=inside?da>=0:da<=0;
        foreach(var b in src){float db=Vector3.Dot(normal,b)-plane;bool inb=inside?db>=0:db<=0;if(ina!=inb){float t=da/(da-db);dst.Add(Vector3.LerpUnclamped(a,b,t));}if(inb)dst.Add(b);a=b;da=db;ina=inb;}return dst;
    }
    // Keep the complement of a convex box. Each triangle is divided by six planes.
    static Mesh RemoveBox(Mesh src,Vector3 lo,Vector3 hi) {
        var ns=new[]{Vector3.right,Vector3.left,Vector3.up,Vector3.down,Vector3.forward,Vector3.back};var ds=new[]{lo.x,-hi.x,lo.y,-hi.y,lo.z,-hi.z};var vv=new List<Vector3>();var tt=new List<int>();var verts=src.vertices;var tris=src.triangles;
        for(int i=0;i<tris.Length;i+=3){var remaining=new List<Vector3>{verts[tris[i]],verts[tris[i+1]],verts[tris[i+2]]};for(int p=0;p<6&&remaining.Count>2;p++){var outside=Clip(remaining,ns[p],ds[p],false);Emit(outside,vv,tt);remaining=Clip(remaining,ns[p],ds[p],true);}}
        var m=new Mesh();m.name="Runtime clipped wall";m.SetVertices(vv);m.SetTriangles(tt,0);m.RecalculateNormals();m.RecalculateBounds();return m;
    }
    static void Emit(List<Vector3> poly,List<Vector3> v,List<int> t){if(poly.Count<3)return;int b=v.Count;v.AddRange(poly);for(int k=1;k<poly.Count-1;k++)t.AddRange(new[]{b,b+k,b+k+1});}
    public static Material Mat(string name,Color c){var m=new Material(Shader.Find("Standard"));m.name=name;m.color=c;m.SetFloat("_Glossiness",.05f);return m;}
    static GameObject Part(string name,Vector3 pos,Vector3 scale,Material m){var o=GameObject.CreatePrimitive(PrimitiveType.Cube);o.name=name;o.transform.position=pos;o.transform.localScale=scale;o.GetComponent<Renderer>().sharedMaterial=m;return o;}
    static void Edge(string name,Vector3[] p,Material mat,float w,Transform parent=null){var o=new GameObject(name);if(parent)o.transform.SetParent(parent);var l=o.AddComponent<LineRenderer>();l.sharedMaterial=mat;l.positionCount=p.Length;l.SetPositions(p);l.startWidth=l.endWidth=w;l.numCapVertices=2;}
}
}
