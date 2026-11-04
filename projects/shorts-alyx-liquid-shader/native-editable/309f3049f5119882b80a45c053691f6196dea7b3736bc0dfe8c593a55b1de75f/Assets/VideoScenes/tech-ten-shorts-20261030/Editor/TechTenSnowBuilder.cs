using System;
using System.Linq;
using UnityEngine;
using UnityEditor;

namespace Yamyam.TechTen.Editor {
 public static partial class TechTenBuilder {
  static TextMesh SnowLabel(Transform parent,string name,string text,Vector3 position,float size,Color color) {
   var label=new GameObject(name).AddComponent<TextMesh>();label.transform.SetParent(parent,false);
   label.transform.localPosition=position;label.anchor=TextAnchor.MiddleCenter;label.alignment=TextAlignment.Center;
   label.fontSize=64;label.characterSize=size;label.color=color;label.text=text;
   label.font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");label.GetComponent<MeshRenderer>().sharedMaterial=label.font.material;
   return label;
  }
  static Transform SnowPanel(TechTenDemo d,string name,float x,Color border,out Renderer image,out TextMesh label) {
   var panel=new GameObject(name).transform;panel.SetParent(d.shot.transform,false);
   panel.localPosition=new Vector3(x,.225f,1);
   var back=Part(name+" border",PrimitiveType.Quad,Vector3.zero,new Vector3(.297f,.153f,1),Mat(name+"-border",border,"Yamyam/TechTen/SnowBuffer"),panel);
   back.GetComponent<Renderer>().sharedMaterial.renderQueue=4000;
   var face=Part(name+" actual texture",PrimitiveType.Quad,new Vector3(0,0,-.001f),new Vector3(.289f,.1445f,1),Mat(name+"-image",Color.white,"Yamyam/TechTen/SnowBuffer"),panel);
   face.GetComponent<Renderer>().sharedMaterial.renderQueue=4001;image=face.GetComponent<Renderer>();
   label=SnowLabel(panel,name+" label",name,new Vector3(0,.101f,-.01f),.0035f,border);
   return panel;
  }
  static void BuildSnow(TechTenDemo d) {
   const int n=96;var v=new Vector3[(n+1)*(n+1)];var uv=new Vector2[v.Length];var tri=new int[n*n*6];
   for(int z=0;z<=n;z++)for(int x=0;x<=n;x++){int i=z*(n+1)+x;v[i]=new Vector3((x/(float)n-.5f)*8,.12f,(z/(float)n-.5f)*4);uv[i]=new Vector2(x/(float)n,z/(float)n);}
   int k=0;for(int z=0;z<n;z++)for(int x=0;x<n;x++){int a=z*(n+1)+x;foreach(int q in new[]{a,a+n+1,a+1,a+1,a+n+1,a+n+2})tri[k++]=q;}
   var mesh=new Mesh{name="Deformable snow teaching mesh"};mesh.vertices=v;mesh.uv=uv;mesh.triangles=tri;mesh.RecalculateNormals();AssetDatabase.CreateAsset(mesh,Root+"/Meshes/"+prefix+".asset");
   var g=new GameObject("Accumulated contact height surface");d.dynamicSurface=g.AddComponent<MeshFilter>();d.dynamicSurface.sharedMesh=mesh;
   d.snowReliefMaterial=Mat("snow-relief",new Color(.83f,.91f,.98f),"Yamyam/TechTen/SnowRelief");
   g.AddComponent<MeshRenderer>().sharedMaterial=d.snowReliefMaterial;
   var knight=Knight();knight.rotation=Quaternion.Euler(0,90,0);foreach(var t in knight.GetComponentsInChildren<Transform>())t.gameObject.layer=9;d.actors=new[]{knight};
   // SampleAnimation and Camera.Render run many times in one editor update.
   // Force fresh skinning for each real camera capture rather than dragging a
   // cached standing pose across the surface (which produces false ski tracks).
   foreach(var skin in knight.GetComponentsInChildren<SkinnedMeshRenderer>()){
    skin.updateWhenOffscreen=true;skin.forceMatrixRecalculationPerRender=true;
   }
   d.walk=AssetDatabase.LoadAllAssetsAtPath("Assets/ThirdParty/KayKitAdventurers/Knight.fbx").OfType<AnimationClip>().FirstOrDefault(a=>a.name.ToLower().Contains("walk"));if(!d.walk)throw new Exception("Walking clip required for snow");
   d.contactCamera=new GameObject("Actual orthographic contact camera").AddComponent<Camera>();d.contactCamera.transform.position=new Vector3(0,-.8f,0);
   d.contactCamera.transform.rotation=Quaternion.LookRotation(Vector3.up,Vector3.forward);d.contactCamera.orthographic=true;d.contactCamera.orthographicSize=2;d.contactCamera.aspect=2;
   d.contactCamera.nearClipPlane=.915f;d.contactCamera.farClipPlane=.925f;d.contactCamera.cullingMask=1<<9;d.contactCamera.backgroundColor=Color.black;d.contactCamera.clearFlags=CameraClearFlags.SolidColor;d.contactCamera.enabled=false;
   var camera=new GameObject("Actual contact camera location marker").transform;camera.position=new Vector3(0,-.8f,0);
   Part("Camera housing",PrimitiveType.Cube,Vector3.zero,new Vector3(.55f,.35f,.4f),Mat("camera",teal),camera);
   Part("Upward camera lens",PrimitiveType.Cylinder,new Vector3(0,.24f,0),new Vector3(.22f,.15f,.22f),Mat("camera-lens",yellow),camera);
   d.props=new[]{camera};d.effects=new[]{d.snowReliefMaterial,Mat("snow-cutaway",new Color(.7f,.88f,1,.18f),"Yamyam/TechTen/Glass")};
   d.lines=new[]{Line("Upward viewing direction",yellow,.035f)};d.lines[0].SetPositions(new[]{new Vector3(0,-.35f,0),new Vector3(0,.1f,0)});
   d.snowCurrentPanel=SnowPanel(d,"Current contact",-.158f,teal,out d.snowCurrentImage,out d.snowCurrentLabel);
   d.snowAccumulatedPanel=SnowPanel(d,"Accumulated height",.158f,yellow,out d.snowAccumulatedImage,out d.snowAccumulatedLabel);
   d.snowRenderLabel=SnowLabel(d.shot.transform,"Actual rendering state","",new Vector3(0,.25f,.99f),.0055f,yellow);
   d.snowGeometryLines=new LineRenderer[26];for(int i=0;i<26;i++){d.snowGeometryLines[i]=Line("Actual snow vertices row "+i,teal,.008f);d.snowGeometryLines[i].enabled=false;}
   d.shot.transform.position=d.stage==1?new Vector3(7,3,-8):new Vector3(7,6,-7);
   d.shot.transform.LookAt(new Vector3(0,d.stage==1?1:d.stage==2?1.5f:.3f,0));
  }
 }
}
