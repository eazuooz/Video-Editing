using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.GameMath.LightLab {
 public sealed partial class LightLabIllustrations {
  [SerializeField] MeshRenderer storedSurface;
  [SerializeField] Vector3[] storedWorldPoints;
  [SerializeField] Vector2[] storedAtlasPoints;
  [SerializeField] Color[] storedColors;
  [SerializeField] Transform[] storedMarkers;
  [SerializeField] Text[] storedLabels;
  [SerializeField] LineRenderer storedLeader;
  [SerializeField] Image atlasMarker;
  [SerializeField] Text storageHeading;
  [SerializeField] RawImage actualAtlas;
  [SerializeField] bool atlasBuilt;
  void BuildSurfaceStorage(LightLabStage stage,Font font) {
   storageHeading=Text(font,"",44,1035,300,790,130,Yellow);
   if(Cue.diagram=="surface:lightmap") {
    foreach(var renderer in stage.GetComponentsInChildren<MeshRenderer>())
     if(renderer.name=="Floor receiving baked shadows")storedSurface=renderer;
    if(!storedSurface)throw new InvalidOperationException("Actual room floor is required for a lightmap UV demonstration.");
    storageHeading.text="표면의 UV2 → 실제 저장 텍스처";
    storedLeader=Path("Actual surface point to UV chart",Cyan,Vector3.zero,Vector3.zero);
    atlasMarker=Panel(Yellow,0,0,18,18);
    detail.text="청록: 바닥 UV2 경계 · 노랑: 선택한 표면 지점";
   } else {
    storageHeading.text="같은 로봇의 정점에 저장한 조명값";
    var points=new List<Vector3>();var colors=new List<Color>();
    foreach(var renderer in mover.GetComponentsInChildren<MeshRenderer>()) {
     var filter=renderer.GetComponent<MeshFilter>();if(!filter)continue;
     var mesh=filter.sharedMesh;var vertices=mesh.vertices;var normals=mesh.normals;
     var baked=new Color[vertices.Length];
     for(int i=0;i<vertices.Length;i++) {
      var world=filter.transform.TransformPoint(vertices[i]);
      var normal=filter.transform.worldToLocalMatrix.transpose.MultiplyVector(normals[i]).normalized;
      var direction=Cue.aimAtSubject?(new Vector3(-.7f,1.3f,0)-Cue.lightPosition).normalized:Quaternion.Euler(Cue.lightEuler)*Vector3.forward;
      var light=Cue.lightType==0?-direction:(Cue.lightPosition-world).normalized;
      float d=Mathf.Max(0,Vector3.Dot(normal,light));
      baked[i]=Cue.diffuse*(Cue.lightColor*d+Cue.ambient);baked[i].a=1;
      var screen=cameraRef.WorldToViewportPoint(world);
      if(screen.z>0&&screen.x>.08f&&screen.x<.52f&&screen.y>.25f&&screen.y<.7f) {
       bool distinct=true;foreach(var p in points)if(Vector3.Distance(p,world)<.32f){distinct=false;break;}
       if(distinct&&points.Count<4){points.Add(world);colors.Add(baked[i]);}
      }
     }
     // The mesh is already an owned generated copy, never a vendor source.
     mesh.colors=baked;
    }
    storedWorldPoints=points.ToArray();storedColors=colors.ToArray();
    storedMarkers=new Transform[points.Count];storedLabels=new Text[points.Count];
    for(int i=0;i<points.Count;i++) {
     storedMarkers[i]=Primitive(stage,PrimitiveType.Sphere,"Stored vertex "+i,points[i],Vector3.one*.045f,Yellow);
     storedLabels[i]=Text(font,"",40,1040,440+i*62,760,55,Color.white);
    }
    detail.text="우리 구현 · 직접광+환경광을 한 번 계산해 정점 색으로 저장";
   }
  }
  void BuildAtlasChart() {
   if(!storedSurface||storedSurface.lightmapIndex<0||storedSurface.lightmapIndex>=LightmapSettings.lightmaps.Length)return;
   var mesh=storedSurface.GetComponent<MeshFilter>().sharedMesh;var uv=mesh.uv2;var vertices=mesh.vertices;var triangles=mesh.triangles;
   if(uv.Length!=vertices.Length)throw new InvalidOperationException("Actual UV2 must match this mesh.");
   var st=storedSurface.lightmapScaleOffset;
   var map=LightmapSettings.lightmaps[storedSurface.lightmapIndex].lightmapColor;
   var atlasObject=new GameObject("Actual baked lightmap RGB texture",typeof(RectTransform));
   atlasObject.transform.SetParent(canvas.transform,false);actualAtlas=atlasObject.AddComponent<RawImage>();actualAtlas.texture=map;
   var rect=actualAtlas.rectTransform;rect.anchorMin=rect.anchorMax=rect.pivot=new Vector2(0,1);
   rect.anchoredPosition=new Vector2(1080,-390);rect.sizeDelta=new Vector2(360,360f*map.height/map.width);
   // Display actual stored RGB; no synthetic brightness image or invented lux.
   // The square atlas retains its native aspect and UV correspondence.
   actualAtlas.transform.SetSiblingIndex(Mathf.Max(0,atlasMarker.transform.GetSiblingIndex()-1));
   var world=new List<Vector3>();var coords=new List<Vector2>();
   for(int i=0;i<triangles.Length;i+=3) {
    Vector3 p=Vector3.zero;Vector2 q=Vector2.zero;
    for(int k=0;k<3;k++){int n=triangles[i+k];p+=storedSurface.transform.TransformPoint(vertices[n])/3;q+=uv[n]/3;}
    world.Add(p);coords.Add(new Vector2(q.x*st.x+st.z,q.y*st.y+st.w));
    for(int k=0;k<3;k++) {
     Vector2 a=uv[triangles[i+k]],b=uv[triangles[i+(k+1)%3]];
     a=new Vector2(a.x*st.x+st.z,a.y*st.y+st.w);b=new Vector2(b.x*st.x+st.z,b.y*st.y+st.w);
     DrawAtlasEdge(a,b);
    }
   }
   storedWorldPoints=world.ToArray();storedAtlasPoints=coords.ToArray();atlasBuilt=true;
  }
  void DrawAtlasEdge(Vector2 a,Vector2 b) {
   float h=actualAtlas.rectTransform.sizeDelta.y;
   Vector2 start=new Vector2(1080+a.x*360,390+(1-a.y)*h),end=new Vector2(1080+b.x*360,390+(1-b.y)*h);
   var line=Panel(Cyan,start.x,start.y,(end-start).magnitude,3);line.rectTransform.pivot=new Vector2(0,.5f);
   line.rectTransform.localEulerAngles=new Vector3(0,0,-Mathf.Atan2(end.y-start.y,end.x-start.x)*Mathf.Rad2Deg);
  }
  void ApplySurfaceStorage(float seconds) {
   if(Cue.diagram=="surface:lightmap") {
    if(!atlasBuilt)BuildAtlasChart();
    if(!atlasBuilt){result.text="실제 베이크 데이터 준비 전";atlasMarker.enabled=false;return;}
    int n=Mathf.Min(storedWorldPoints.Length-1,(int)(Mathf.Clamp01(seconds/Cue.duration)*storedWorldPoints.Length));
    var uv=storedAtlasPoints[n];var point=storedWorldPoints[n];
    float h=actualAtlas.rectTransform.sizeDelta.y;
    atlasMarker.enabled=true;atlasMarker.transform.SetAsLastSibling();atlasMarker.rectTransform.anchoredPosition=new Vector2(1080+uv.x*360-9,-(390+(1-uv.y)*h-9));
    var atlasScreen=new Vector3((1080+uv.x*360)/1920,1-(390+(1-uv.y)*h)/1080,1.1f);
    storedLeader.SetPositions(new[]{point,cameraRef.ViewportToWorldPoint(atlasScreen)});
    var map=LightmapSettings.lightmaps[storedSurface.lightmapIndex].lightmapColor;
    result.rectTransform.anchoredPosition=new Vector2(1480,-440);result.rectTransform.sizeDelta=new Vector2(345,260);result.fontSize=36;
    result.text="실제 아틀라스 #"+storedSurface.lightmapIndex+" · "+map.width+" × "+map.height+"\nUV ("+uv.x.ToString("0.000")+", "+uv.y.ToString("0.000")+")";
   } else {
    if(storedLabels==null)return;
    for(int i=0;i<storedLabels.Length;i++){var c=storedColors[i];storedLabels[i].text="정점 "+(i+1)+"   RGB ("+c.r.ToString("0.00")+", "+c.g.ToString("0.00")+", "+c.b.ToString("0.00")+")";}
    result.rectTransform.anchoredPosition=new Vector2(1040,-710);result.fontSize=38;
    result.text="저장 이후에는 조명을 다시 계산하지 않고\n보간";
   }
  }
 }
}
