using System;
#if !M21_TRIANGLE_MATH_ONLY
using UnityEngine;
using UnityEngine.UI;
#endif

namespace Yamyam.GameMath.LightLab {
 public static class TriangleHighlightMath {
  // Flat triangle N=V=(0,0,1); a point light is h units along N from its centre.
  // No attenuation, diffuse, ambient, second source or emission in this test.
  public static double PhongSpecular(double x,double y,double h=1.5,double exponent=64){
   if(exponent<=0||double.IsNaN(exponent))throw new ArgumentOutOfRangeException(nameof(exponent));
   if(h<=0)return 0;
   double ndotl=h/Math.Sqrt(x*x+y*y+h*h);
   return Math.Pow(ndotl,exponent); // R dot V = N dot L in this fixed arrangement.
  }
  public static double[] CornerValues(double radius=1.5,double height=1.5,double exponent=64){
   if(radius<=0)throw new ArgumentException("Positive triangle radius required.");
   return new[]{PhongSpecular(0,radius,height,exponent),PhongSpecular(-Math.Sqrt(3)*radius*.5,-radius*.5,height,exponent),PhongSpecular(Math.Sqrt(3)*radius*.5,-radius*.5,height,exponent)};
  }
  public static double GouraudCentroid(double radius=1.5,double height=1.5,double exponent=64){var values=CornerValues(radius,height,exponent);return (values[0]+values[1]+values[2])/3;}
 }

#if !M21_TRIANGLE_MATH_ONLY
 public sealed partial class LightLabStage {
  [SerializeField] Material[] triangleMaterials;
  [SerializeField] Transform[] triangleObjects;
  [SerializeField] Vector3[] triangleCentres,triangleLightPositions;
  [SerializeField] Vector3 triangleNormal,triangleCameraPosition;
  [SerializeField] Quaternion triangleCameraRotation;
  [SerializeField] Text[] triangleTitle,triangleCentreValue;
  [SerializeField] Text triangleConditions,triangleDerivation;
  [SerializeField] LineRenderer[] triangleBorders,triangleCentreRings,triangleCornerRings;
  const float TriangleRadius=1.5f,TriangleLightHeight=1.5f,TriangleExponent=64;
  // Integration: Stage.Build routes diagram=="triangle-highlight" here instead
  // of creating an unimplemented generic illustration component.
  void BuildTriangleHighlight(Font font){
   if(Cue.urpLit)throw new InvalidOperationException("The controlled triangle test uses our local-lighting shader, not URP Lit.");
   if(!RenderCamera.orthographic)throw new InvalidOperationException("The paired triangle comparison requires one orthographic view.");
   objectRoot.gameObject.SetActive(false);surfaceProbe.gameObject.SetActive(false);lampRoot.gameObject.SetActive(false);
   triangleCameraPosition=RenderCamera.transform.position;triangleCameraRotation=RenderCamera.transform.rotation;
   triangleNormal=-RenderCamera.transform.forward;
   triangleMaterials=new Material[2];triangleObjects=new Transform[2];triangleCentres=new Vector3[2];triangleLightPositions=new Vector3[2];
   triangleTitle=new Text[2];triangleCentreValue=new Text[2];triangleBorders=new LineRenderer[2];triangleCentreRings=new LineRenderer[2];triangleCornerRings=new LineRenderer[6];
   Vector3 centre=new Vector3(0,1.35f,0);
   Vector3[] vertices={new Vector3(0,TriangleRadius,0),new Vector3(-Mathf.Sqrt(3)*TriangleRadius*.5f,-TriangleRadius*.5f,0),new Vector3(Mathf.Sqrt(3)*TriangleRadius*.5f,-TriangleRadius*.5f,0)};
   var sourceMesh=new Mesh{name="Single true triangle · 3 vertices"};sourceMesh.vertices=vertices;sourceMesh.normals=new[]{Vector3.forward,Vector3.forward,Vector3.forward};sourceMesh.uv=new[]{new Vector2(.5f,1),new Vector2(0,0),new Vector2(1,0)};sourceMesh.triangles=new[]{0,1,2};sourceMesh.RecalculateBounds();GeneratedObjects.Add(sourceMesh);
   var mesh=TeachingMesh(sourceMesh);mesh.name="Single triangle · face metadata · still 3 vertices";GeneratedObjects.Add(mesh);
   if(mesh.vertexCount!=3||mesh.triangles.Length!=3)throw new InvalidOperationException("Interior-highlight proof requires exactly one triangle, not a dense substitute.");
   for(int i=0;i<2;i++){
    var go=NewObject(i==0?"Gouraud · one triangle":"Per-pixel Phong · same triangle");go.layer=29;go.AddComponent<MeshFilter>().sharedMesh=mesh;
    var renderer=go.AddComponent<MeshRenderer>();var mat=new Material(teaching){name=i==0?"Triangle Gouraud lighting":"Triangle pixel Phong lighting"};GeneratedObjects.Add(mat);renderer.sharedMaterial=mat;triangleMaterials[i]=mat;
    go.transform.position=centre+RenderCamera.transform.right*(i==0?-2.45f:2.45f);go.transform.rotation=Quaternion.LookRotation(triangleNormal,RenderCamera.transform.up);triangleObjects[i]=go.transform;triangleCentres[i]=go.transform.position;
    // Each displayed copy is a translated replica of one local setup. Moving
    // its light by the identical offset prevents a changed L from confounding it.
    triangleLightPositions[i]=triangleCentres[i]+triangleNormal*TriangleLightHeight;
    triangleBorders[i]=TriangleGuide("Triangle boundary "+i,new Color(.42f,.46f,.48f));var outline=new Vector3[4];for(int k=0;k<4;k++)outline[k]=go.transform.TransformPoint(vertices[k%3])+triangleNormal*.004f;triangleBorders[i].positionCount=4;triangleBorders[i].SetPositions(outline);
    for(int k=0;k<3;k++){int j=i*3+k;triangleCornerRings[j]=TriangleGuide("Sampled vertex "+j,new Color(.643f,.776f,.627f));TriangleRing(triangleCornerRings[j],go.transform.TransformPoint(vertices[k])+triangleNormal*.006f,.07f);}
    triangleCentreRings[i]=TriangleGuide("Hollow centre callout "+i,new Color(.910f,.812f,.514f));TriangleRing(triangleCentreRings[i],triangleCentres[i]+triangleNormal*.006f,.34f);
    Vector3 screen=RenderCamera.WorldToViewportPoint(triangleCentres[i]);float x=screen.x*1920-350;
    triangleTitle[i]=Label(font,i==0?"정점 조명 → 색 보간":"픽셀마다 조명 계산",46,x,245,700,64,Color.white);
    triangleCentreValue[i]=Label(font,"",46,x,684,700,64,Color.white);
   }
   triangleConditions=Label(font,"정점 3개 · 같은 법선 · 같은 상대 광원 · 같은 시선",40,230,754,1500,55,Color.white);
   triangleDerivation=Label(font,"정반사만 비교 · 광택 지수 64 · 거리 감쇠 없음",40,230,812,1500,55,new Color(.722f,.722f,.722f));
  }
  LineRenderer TriangleGuide(string name,Color color){
   var go=NewObject(name);var lr=go.AddComponent<LineRenderer>();var material=NewMaterial("Universal Render Pipeline/Unlit",color);lr.sharedMaterial=material;lr.startColor=lr.endColor=Color.white;lr.useWorldSpace=true;lr.widthMultiplier=.035f;lr.numCapVertices=4;lr.numCornerVertices=4;return lr;
  }
  void TriangleRing(LineRenderer line,Vector3 centre,float radius){
   var points=new Vector3[49];for(int k=0;k<points.Length;k++){float a=k*2*Mathf.PI/(points.Length-1);points[k]=centre+RenderCamera.transform.right*(Mathf.Cos(a)*radius)+RenderCamera.transform.up*(Mathf.Sin(a)*radius);}line.positionCount=points.Length;line.SetPositions(points);
  }
  // Integration: call at the end of Stage.Apply for diagram=="triangle-highlight".
  void ApplyTriangleHighlight(float seconds){
   if(triangleMaterials==null||triangleMaterials.Length!=2)return;
   RenderCamera.transform.SetPositionAndRotation(triangleCameraPosition,triangleCameraRotation);RenderCamera.orthographic=true;
   objectRoot.gameObject.SetActive(false);surfaceProbe.gameObject.SetActive(false);lampRoot.gameObject.SetActive(false);
   normal.enabled=towardLight.enabled=reflection.enabled=towardViewer.enabled=halfway.enabled=false;foreach(var c in cone)c.enabled=false;foreach(var l in vectorLabels)l.gameObject.SetActive(false);
   value.gameObject.SetActive(false);formula.gameObject.SetActive(false);kind.text="우리 구현 · 정점 / 픽셀 조명 비교";
   int phase=0;if(Cue.stepTimes!=null){for(int k=0;k<Cue.stepTimes.Length;k++)if(seconds>=Cue.stepTimes[k])phase=k;}else phase=Mathf.Min(2,(int)(Mathf.Clamp01(seconds/Mathf.Max(.001f,Cue.duration))*3));
   for(int i=0;i<2;i++){
    var m=triangleMaterials[i];m.CopyPropertiesFromMaterial(teaching);
    m.SetFloat("_ShadingMode",i==0?2:0);m.SetFloat("_SpecularModel",0);m.SetFloat("_Exponent",TriangleExponent);
    m.SetVector("_Components",new Vector4(0,1,0,0));m.SetColor("_SpecColor",Color.white);m.SetColor("_LightColor",Color.white);m.SetColor("_BaseColor",Color.black);m.SetColor("_AmbientColor",Color.black);m.SetColor("_EmissionColor",Color.black);
    m.SetFloat("_LightType",1);m.SetVector("_LightPosition",triangleLightPositions[i]);m.SetFloat("_Attenuation",0);m.SetFloat("_UseCookie",0);m.SetFloat("_VolumeMode",0);m.SetFloat("_SecondLightStrength",0);m.SetFloat("_MaterialMapEnabled",0);
    m.SetFloat("_UseOrthographicView",1);m.SetVector("_OrthographicViewDirection",triangleNormal);
    // _ViewPosition is irrelevant in the orthographic branch but is also offset
    // identically for auditability if inspected in the saved material.
    m.SetVector("_ViewPosition",triangleCentres[i]+triangleNormal*8);
    triangleTitle[i].color=(phase==0||phase==1&&i==0||phase>=2&&i==1)?Yellow:Color.white;
    triangleCentreRings[i].enabled=phase>=1&&i==0||phase>=2&&i==1;
    for(int k=0;k<3;k++)triangleCornerRings[i*3+k].enabled=phase<=1;
    double centreValue=i==0?TriangleHighlightMath.GouraudCentroid(TriangleRadius,TriangleLightHeight,TriangleExponent):TriangleHighlightMath.PhongSpecular(0,0,TriangleLightHeight,TriangleExponent);
    triangleCentreValue[i].text=i==0?"중심 계산값 < 0.001":"중심 계산값 = "+centreValue.ToString("0.000");
   }
   if(phase==0)triangleConditions.text="세 정점의 정반사 값은 모두 0.001보다 작습니다";
   else if(phase==1)triangleConditions.text="정점 색을 평균해도, 정점의 최댓값보다 밝아지지 않습니다";
   else triangleConditions.text="같은 삼각형 안쪽에서 다시 계산하면 밝은 점을 찾습니다";
  }
 }
#endif
}
