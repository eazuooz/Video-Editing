using System;
using UnityEngine;

namespace Yamyam.TechTen {
 public sealed partial class TechTenDemo {
  // These are our captured teaching buffers, not extracted commercial buffers.
  public Transform snowCurrentPanel,snowAccumulatedPanel;
  public Renderer snowCurrentImage,snowAccumulatedImage;
  public TextMesh snowCurrentLabel,snowAccumulatedLabel,snowRenderLabel;
  public LineRenderer[] snowGeometryLines;
  public Material snowReliefMaterial;
  public bool snowVirtualDepthActive;
  const int SnowWidth=194,SnowHeight=98;
  const float SnowDepth=.12f;
  Texture2D snowCurrentTexture,snowHeightTexture;
  float[] snowHeightValues;
  Color32[] snowContactColors,snowHeightColors;
  Font snowFont;
  Material snowCurrentRuntimeMaterial,snowAccumulatedRuntimeMaterial;
  SkinnedMeshRenderer[] snowSkins;
  Mesh[] snowBakedMeshes;

  void PrepareSnowBuffers() {
   if(baseVertices==null){baseVertices=dynamicSurface.mesh.vertices;snow=new float[baseVertices.Length];}
   if(contactTarget)return;
   contactTarget=new RenderTexture(SnowWidth,SnowHeight,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.Linear);
   contactTarget.Create();
   contactPixels=new Texture2D(SnowWidth,SnowHeight,TextureFormat.RGB24,false,true);
   snowCurrentTexture=new Texture2D(SnowWidth,SnowHeight,TextureFormat.RGBA32,false,true);
   snowHeightTexture=new Texture2D(SnowWidth,SnowHeight,TextureFormat.RGBA32,false,true);
   snowCurrentTexture.wrapMode=snowHeightTexture.wrapMode=TextureWrapMode.Clamp;
   snowCurrentTexture.filterMode=snowHeightTexture.filterMode=FilterMode.Bilinear;
   snowHeightValues=new float[SnowWidth*SnowHeight];
   snowContactColors=new Color32[snowHeightValues.Length];snowHeightColors=new Color32[snowHeightValues.Length];
   contactCamera.targetTexture=contactTarget;
   contactCamera.SetReplacementShader(Shader.Find("Yamyam/TechTen/ContactCapture"),"");
   snowCurrentRuntimeMaterial=snowCurrentImage.material;
   snowAccumulatedRuntimeMaterial=snowAccumulatedImage.material;
   snowCurrentRuntimeMaterial.mainTexture=snowCurrentTexture;
   snowAccumulatedRuntimeMaterial.mainTexture=snowHeightTexture;
   snowReliefMaterial=new Material(snowReliefMaterial);
   snowReliefMaterial.SetTexture("_HeightMap",snowHeightTexture);
   snowReliefMaterial.SetFloat("_Depth",SnowDepth);
   // The saved-scene diagnostic confirms changing bones and BakeMesh vertices,
   // but this isolated synchronous editor capture cached the GPU skin pose.
   // Bake the actual sampled rig geometry for BOTH cameras; never paint stamps.
   snowSkins=actors[0].GetComponentsInChildren<SkinnedMeshRenderer>();
   snowBakedMeshes=new Mesh[snowSkins.Length];
   for(int i=0;i<snowSkins.Length;i++){
    var skin=snowSkins[i];var g=new GameObject("Sampled animated geometry - "+skin.name);
    g.transform.SetParent(skin.transform,false);g.layer=9;
    snowBakedMeshes[i]=new Mesh{name="Actual sampled rig vertices - "+skin.name};
    g.AddComponent<MeshFilter>().sharedMesh=snowBakedMeshes[i];
    g.AddComponent<MeshRenderer>().sharedMaterials=skin.sharedMaterials;skin.enabled=false;
   }
   // OS dynamic font is used at capture time; no font file is redistributed.
   snowFont=Font.CreateDynamicFontFromOSFont(new[]{"Malgun Gothic","Arial"},64);
   snowFont.RequestCharactersInTexture("현재 접촉 · 실제 촬영누적 높이맵 ONOFF릴리프 매핑평면 + 가상 깊이메시 변형꼭짓점 이동",64);
   foreach(var label in new[]{snowCurrentLabel,snowAccumulatedLabel,snowRenderLabel}){
    label.font=snowFont;label.GetComponent<MeshRenderer>().sharedMaterial=snowFont.material;
   }
  }
  bool AccumulateSnow(float t) {
   return stage>0 && !(actionKind=="accumulation-toggle"&&t>=actionStartSeconds&&t<actionResumeSeconds);
  }
  void PositionSnowWalker(float t) {
   actors[0].position=new Vector3(Mathf.PingPong(t*1.1f,6)-3,.12f,0);
   if(walk)walk.SampleAnimation(actors[0].gameObject,t%walk.length);
   actors[0].rotation=Quaternion.Euler(0,Mathf.Repeat(t*1.1f,12)<6?90:-90,0);
   if(snowSkins!=null)for(int i=0;i<snowSkins.Length;i++)snowSkins[i].BakeMesh(snowBakedMeshes[i],false);
  }
  void CaptureSnowFrame(float t) {
   PositionSnowWalker(t);contactCamera.Render();
   var previous=RenderTexture.active;RenderTexture.active=contactTarget;
   contactPixels.ReadPixels(new Rect(0,0,SnowWidth,SnowHeight),0,0);contactPixels.Apply();
   RenderTexture.active=previous;
   Color32[] captured=contactPixels.GetPixels32();
   bool accumulate=AccumulateSnow(t);
   for(int y=0;y<SnowHeight;y++)for(int x=0;x<SnowWidth;x++){
    int i=y*SnowWidth+x;
    // Upward camera screen-right is -X: flip only X into shared world-map UV.
    int cameraX=SnowWidth-1-x;
    byte raw=captured[y*SnowWidth+cameraX].r;
    snowContactColors[i]=new Color32(raw,raw,raw,255);
    // Small separable 1-2-1 filter. This is our simple demonstration filter,
    // not a claim to reproduce the disclosed production Poisson kernel.
    float filtered=0;
    for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){
     int sx=Mathf.Clamp(cameraX+dx,0,SnowWidth-1),sy=Mathf.Clamp(y+dy,0,SnowHeight-1);
     filtered+=captured[sy*SnowWidth+sx].r*((dx==0?2:1)*(dy==0?2:1))/(255f*16);
    }
    snowHeightValues[i]=accumulate?Mathf.Max(snowHeightValues[i],filtered):filtered;
   }
  }
  void SampleSnow() {
   PrepareSnowBuffers();
   contactCamera.transform.position=new Vector3(0,-.8f,0);
   // Measured sampled sole minima span .084-.173. A .17 upper plane
   // captures airborne toes almost continuously; keep only surface contact.
   contactCamera.nearClipPlane=.915f;contactCamera.farClipPlane=.925f;
   int now=Mathf.FloorToInt(elapsed*60);
   if(now<snowFrame){Array.Clear(snowHeightValues,0,snowHeightValues.Length);snowFrame=-1;}
   for(int frame=snowFrame+1;frame<=now;frame++)CaptureSnowFrame(frame/60f);
   snowFrame=now;
   for(int i=0;i<snowHeightColors.Length;i++){
    byte value=(byte)Mathf.RoundToInt(Mathf.Clamp01(snowHeightValues[i])*255);
    snowHeightColors[i]=new Color32(value,value,value,255);
   }
   snowCurrentTexture.SetPixels32(snowContactColors);snowCurrentTexture.Apply(false);
   snowHeightTexture.SetPixels32(snowHeightColors);snowHeightTexture.Apply(false);
   bool renderingComparison=actionKind=="relief-to-geometry";
   bool relief=renderingComparison&&elapsed<actionStartSeconds;
   snowVirtualDepthActive=relief;
   Vector3[] vertices=new Vector3[baseVertices.Length];
   for(int i=0;i<vertices.Length;i++){
    Vector3 v=baseVertices[i];snow[i]=snowHeightTexture.GetPixelBilinear((v.x+4)/8,(v.z+2)/4).r*SnowDepth;
    vertices[i]=v;if(!relief)vertices[i].y-=snow[i];
   }
   var mesh=dynamicSurface.mesh;mesh.vertices=vertices;mesh.RecalculateNormals();mesh.RecalculateBounds();
   PositionSnowWalker(elapsed);
   // Same material and height data; relief ray-marches on flat geometry, while
   // the other state changes actual mesh vertices. No hardware tessellation claim.
   snowReliefMaterial.SetFloat("_ReliefEnabled",relief?1:0);
   dynamicSurface.GetComponent<Renderer>().sharedMaterial=stage==1?effects[1]:snowReliefMaterial;
   props[0].gameObject.SetActive(stage==1);
   foreach(var line in lines)line.enabled=stage==1;
   foreach(var r in FindObjectsByType<Renderer>(FindObjectsSortMode.None))
    if(r.name=="Dark teaching stage"||r.name.StartsWith("GridX")||r.name.StartsWith("GridZ"))r.enabled=stage!=1;
   // The fixed camera-child panels end near y320. Aim above the world so even
   // the rear-most walking pose clears them; contact camera geometry is unchanged.
   if(stage==1){shot.transform.position=new Vector3(7,3,-8);shot.transform.LookAt(new Vector3(0,1,0));}
   else if(renderingComparison){shot.transform.position=new Vector3(7,3.4f,-7);shot.transform.LookAt(new Vector3(0,.25f,0));}
   else if(stage==2){shot.transform.position=new Vector3(7,6,-7);shot.transform.LookAt(new Vector3(0,1.5f,0));}
   bool maps=stage>0&&!renderingComparison;
   snowCurrentPanel.gameObject.SetActive(maps);snowAccumulatedPanel.gameObject.SetActive(maps&&stage==2);
   snowCurrentLabel.text="현재 접촉";
   snowAccumulatedLabel.text=AccumulateSnow(elapsed)?"누적 높이맵 · ON":"누적 높이맵 · OFF";
   snowRenderLabel.gameObject.SetActive(renderingComparison);
   snowRenderLabel.text=relief?"릴리프 매핑\n평면 + 가상 깊이":"메시 변형\n실제 꼭짓점 이동";
   // These lines follow the actual changed vertices, not a decorative flat grid.
   int n=96;
   for(int row=0;row<snowGeometryLines.Length;row++){
    var line=snowGeometryLines[row];line.enabled=renderingComparison&&!relief;
    if(!line.enabled)continue;
    var points=new Vector3[n+1];int fixedIndex=(row%13)*8;
    for(int i=0;i<=n;i++){int index=row<13?fixedIndex*(n+1)+i:i*(n+1)+fixedIndex;points[i]=vertices[index]+Vector3.up*.002f;}
    line.positionCount=points.Length;line.SetPositions(points);
   }
   lastGap=Max(snow);
  }
  void OnDestroy() {
   if(topic!="batman-origins-snow-below-camera"||!contactTarget)return;
   contactTarget.Release();
   foreach(UnityEngine.Object resource in new UnityEngine.Object[]{contactTarget,contactPixels,snowCurrentTexture,snowHeightTexture,snowFont,snowCurrentRuntimeMaterial,snowAccumulatedRuntimeMaterial,snowReliefMaterial}){
    if(!resource)continue;if(Application.isPlaying)Destroy(resource);else DestroyImmediate(resource);
   }
   if(snowBakedMeshes!=null)foreach(var mesh in snowBakedMeshes){if(Application.isPlaying)Destroy(mesh);else DestroyImmediate(mesh);}
  }
 }
}
