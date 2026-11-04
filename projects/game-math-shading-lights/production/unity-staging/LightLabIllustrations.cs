using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.GameMath.LightLab {
 // Explicitly labelled teaching illustrations. These do not claim to be a
 // Unity light bake, captured commercial renderer buffers, or measured probes.
 [ExecuteAlways] public sealed partial class LightLabIllustrations:MonoBehaviour {
  public LabCue Cue;
  [SerializeField] Transform areaDisk, mover;
  [SerializeField] Transform[] probes;
  [SerializeField] Image[] cells;
  [SerializeField] Text result,detail;
  [SerializeField] Canvas canvas;
  [SerializeField] Camera cameraRef;
  [SerializeField] Material ink;
  [SerializeField] LineRenderer[] paths;
  [SerializeField] Vector3 objectStart;
  static readonly Color Yellow=new Color(1,.83f,.25f), Cyan=new Color(.27f,.87f,.9f), Green=new Color(.40f,.9f,.58f), Rose=new Color(1,.42f,.57f);
  public void Build(LightLabStage stage,LabCue cue,Font font,Transform subject) {
   Cue=cue;cameraRef=stage.RenderCamera;mover=subject;objectStart=subject.position;
   ink=new Material(Shader.Find("Universal Render Pipeline/Unlit"));ink.SetColor("_BaseColor",Color.white);stage.GeneratedObjects.Add(ink);
   var ui=Node("Illustration overlays · not measured renderer data");canvas=ui.AddComponent<Canvas>();canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=cameraRef;canvas.planeDistance=.9f;canvas.sortingOrder=90;
   var scale=ui.AddComponent<CanvasScaler>();scale.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize;scale.referenceResolution=new Vector2(1920,1080);
   // The scene remains visible beneath explanations; no black-card reset.
   if(cue.diagram!="visibility")Panel(new Color(0,0,0,.22f),0,260,1920,600);
   detail=Text(font,"해설용 도식",40,96,805,1720,50,Color.white);
   result=Text(font,"",42,1040,650,790,125,Color.white);
   if(cue.diagram=="delta")BuildDelta(stage,font);
   if(cue.diagram=="visibility")BuildVisibility(stage,font);
   if(cue.diagram=="fresnel"||cue.diagram=="retroreflection"||cue.diagram=="anisotropy")BuildLimitDiagram(font);
   if(cue.diagram=="lightmap"||cue.diagram=="vertexBake")BuildLightmap(font);
   if(cue.diagram=="probe")BuildProbes(stage,font);
   if(cue.diagram=="sh")BuildDirectionalBasis(font);
   if(cue.diagram.StartsWith("math:"))BuildMath(font);
   if(cue.diagram.StartsWith("geometry:"))BuildGeometry(stage,font);
   Apply(0);
  }
  void OnEnable(){if(canvas){var f=Font.CreateDynamicFontFromOSFont("Malgun Gothic",48);foreach(var t in canvas.GetComponentsInChildren<Text>(true))t.font=f;}}
  GameObject Node(string name){var g=new GameObject(name);g.transform.SetParent(transform,false);return g;}
  Transform Primitive(LightLabStage stage,PrimitiveType type,string name,Vector3 p,Vector3 s,Color c){var g=GameObject.CreatePrimitive(type);g.name=name;g.transform.SetParent(transform,false);g.transform.position=p;g.transform.localScale=s;var mat=new Material(ink);mat.SetColor("_BaseColor",c);stage.GeneratedObjects.Add(mat);g.GetComponent<Renderer>().sharedMaterial=mat;return g.transform;}
  LineRenderer Path(string name,Color c,params Vector3[] points){var g=Node(name);var lr=g.AddComponent<LineRenderer>();lr.sharedMaterial=ink;lr.startColor=lr.endColor=c;lr.widthMultiplier=.025f;lr.useWorldSpace=true;lr.numCapVertices=4;lr.positionCount=points.Length;lr.SetPositions(points);return lr;}
  Image Panel(Color c,float x,float y,float w,float h){var g=new GameObject("Diagram panel",typeof(RectTransform));g.transform.SetParent(canvas.transform,false);var im=g.AddComponent<Image>();im.color=c;var r=im.rectTransform;r.anchorMin=r.anchorMax=r.pivot=new Vector2(0,1);r.anchoredPosition=new Vector2(x,-y);r.sizeDelta=new Vector2(w,h);return im;}
  Text Text(Font f,string s,int size,float x,float y,float w,float h,Color c){var g=new GameObject(s,typeof(RectTransform));g.transform.SetParent(canvas.transform,false);var t=g.AddComponent<Text>();t.font=f;t.text=s;t.fontSize=size;t.color=c;t.horizontalOverflow=HorizontalWrapMode.Wrap;t.verticalOverflow=VerticalWrapMode.Truncate;var r=t.rectTransform;r.anchorMin=r.anchorMax=r.pivot=new Vector2(0,1);r.anchoredPosition=new Vector2(x,-y);r.sizeDelta=new Vector2(w,h);return t;}
  void BuildDelta(LightLabStage stage,Font f){
   areaDisk=Primitive(stage,PrimitiveType.Cylinder,"Shrinking finite emitter · thought experiment",new Vector3(0,3,0),new Vector3(2,.035f,2),Yellow);
   Text(f,"면적은 줄이고, 전체 복사속 Φ는 유지",42,1040,330,790,120,Yellow);
   Text(f,"점 광원은 이 극한을 표현하는 추상적인 광원입니다.",36,1040,455,790,160,Color.white);
  }
  void BuildVisibility(LightLabStage stage,Font f){
   Primitive(stage,PrimitiveType.Cube,"Occluder not tested by the teaching local shader",new Vector3(-1.6f,1.6f,-.8f),new Vector3(.13f,2.8f,2.1f),new Color(.17f,.19f,.20f));
   Text(f,"가림 검사 없음",42,1100,340,700,70,Rose);
   Text(f,"이 국소 모델은 N·L과 R·V만 계산합니다.\n사이에 벽이 있는지는 별도 문제입니다.",36,1100,430,700,170,Color.white);
  }
  void BuildLimitDiagram(Font f){
   Vector3 p=new Vector3(1.4f,1.3f,0);
   paths=new LineRenderer[2];
   paths[0]=Path("Incoming ray",Yellow,p+new Vector3(-1.4f,1.6f,0),p);
   paths[1]=Path("Illustrated outgoing ray",Cyan,p,p+new Vector3(1.4f,1.6f,0));
   string text=Cue.diagram=="fresnel"?"비스듬히 볼수록 달라지는 반사율":Cue.diagram=="retroreflection"?"들어온 쪽으로 되돌아가는 빛":"표면의 결 방향에 따라 달라지는 반사";
   Text(f,text,42,1040,330,790,140,Yellow);
   Text(f,"표준 국소 모델이 놓치는 성질",36,1040,510,790,70,Color.white);
  }
  void BuildLightmap(Font f){
   Text(f,Cue.diagram=="vertexBake"?"정점에 저장한 조명값":"추가 UV로 배치한 라이트맵 텍셀",42,1035,295,790,90,Yellow);
   int columns=Cue.diagram=="vertexBake"?5:8, rows=Cue.diagram=="vertexBake"?4:5;
   cells=new Image[columns*rows];
   for(int y=0;y<rows;y++)for(int x=0;x<columns;x++){
    float a=.16f+.7f*(1-Mathf.Abs(x-(columns-1)*.5f)/columns)*(1-y/(float)(rows+2));
    cells[y*columns+x]=Panel(new Color(a,a,a,1),1040+x*85,390+y*42,Cue.diagram=="vertexBake"?13:78,Cue.diagram=="vertexBake"?13:35);
   }
   Text(f,"표면의 위치와 저장된 조명값을 연결",40,1035,770,790,90,Color.white);
  }
  void BuildProbes(LightLabStage stage,Font f){
   probes=new Transform[4];Vector3[] positions={new Vector3(-2,.6f,-.3f),new Vector3(2,.6f,-.3f),new Vector3(-2,3,-.3f),new Vector3(2,3,-.3f)};
   for(int i=0;i<4;i++)probes[i]=Primitive(stage,PrimitiveType.Sphere,"Illustrated light-probe sample "+i,positions[i],Vector3.one*.16f,Yellow);
   paths=new LineRenderer[4];for(int i=0;i<4;i++)paths[i]=Path("Nearby probe relation "+i,Cyan,positions[i],objectStart);
   Text(f,"공간에 저장한 빛 → 움직이는 물체",42,1040,330,790,100,Yellow);
   Text(f,"주변에 저장된 조명 정보를 섞어 적용\n아래 선: 거리 기반 가중치의 예",40,1040,470,790,150,Color.white);
  }
  void BuildDirectionalBasis(Font f){
   Text(f,"방향별 밝기를 여러 기저의 가중합으로 압축",40,1035,290,790,105,Yellow);
   Text(f,"기저 하나는 구 전체의 부드러운 분포",40,1035,395,790,100,Color.white);
   // A sampled spherical field from actual real-SH basis functions. This is
   // a scalar mathematical illustration, not measured irradiance/probe data.
   cells=new Image[24*8];for(int y=0;y<8;y++)for(int x=0;x<24;x++)cells[y*24+x]=Panel(Color.gray,1035+x*30,500+y*17,28,15);
   Text(f,"펼친 구면: 가로는 방위각, 세로는 고도",30,1035,790,790,50,Color.white);
  }
  public void Apply(float seconds){
   if(Cue==null)return;float u=Mathf.Clamp01(seconds/Mathf.Max(.001f,Cue.duration));u=u*u*(3-2*u);
   if(Cue.diagram=="delta"&&areaDisk){float r=Mathf.Lerp(1,.15f,u);areaDisk.localScale=new Vector3(2*r,.035f,2*r);float area=Mathf.PI*r*r;result.text="A = πr² = "+area.ToString("0.00")+"\nΦ를 유지하면 단위 면적당 값 ∝ 1/A";}
   if(Cue.diagram=="visibility")result.text="국소 조명값과 광원 가시성은 별개";
   if(Cue.diagram=="fresnel"&&paths!=null){float theta=Mathf.Lerp(10,78,u)*Mathf.Deg2Rad;Vector3 p=new Vector3(1.4f,1.3f,0),d=new Vector3(Mathf.Sin(theta),Mathf.Cos(theta),0)*1.8f;paths[0].SetPositions(new[]{p+new Vector3(-d.x,d.y,0),p});paths[1].SetPositions(new[]{p,p+d});result.text="입사각 θ = "+(theta*Mathf.Rad2Deg).ToString("0")+"°\n표면에 비스듬히 들어오는 빛";}
   if(Cue.diagram=="retroreflection"&&paths!=null){Vector3 p=new Vector3(1.4f,1.3f,0),q=p+new Vector3(-1.4f,1.6f,0);paths[1].SetPositions(new[]{p,q+Vector3.right*.12f});result.text="재귀 반사: 광원 쪽으로 되돌아감";}
   if(Cue.diagram=="anisotropy")result.text="등방성: 방향을 돌려도 같음\n이방성: 결 방향에 따라 달라짐";
   if((Cue.diagram=="lightmap"||Cue.diagram=="vertexBake")&&cells!=null){int selected=Mathf.Min(cells.Length-1,(int)(u*cells.Length));for(int i=0;i<cells.Length;i++){float a=.25f+.6f*(1-i/(float)cells.Length);cells[i].color=i==selected?Yellow:new Color(a,a,a,1);}result.text="표본 "+(selected+1)+" / "+cells.Length+"\n저장된 값은 원래 배치에 대응";}
   if(Cue.diagram=="probe"&&probes!=null){mover.position=objectStart+Vector3.right*Mathf.Lerp(-.65f,.65f,u);Vector3 target=mover.position+Vector3.up*1.1f;float total=0;float[] weights=new float[4];for(int i=0;i<4;i++){weights[i]=1/Mathf.Max(.1f,Vector3.Distance(probes[i].position,target));total+=weights[i];paths[i].SetPositions(new[]{probes[i].position,target});}for(int i=0;i<4;i++)paths[i].widthMultiplier=.015f+.07f*weights[i]/total;result.text="움직이는 대상과 주변 표본의 관계\n선 굵기: 설명용 가중치";}
   if(Cue.diagram=="sh"&&cells!=null){int basis=Mathf.Clamp(Cue.diagramVariant,0,3);for(int y=0;y<8;y++)for(int x=0;x<24;x++){float az=(x+.5f)/24*Mathf.PI*2,polar=(y+.5f)/8*Mathf.PI;float nx=Mathf.Sin(polar)*Mathf.Cos(az),ny=Mathf.Cos(polar),nz=Mathf.Sin(polar)*Mathf.Sin(az);float b=basis==0?.282095f:.488603f*(basis==1?ny:basis==2?nz:nx);float a=Mathf.Clamp01(.5f+b*u);cells[y*24+x].color=b>=0?new Color(a,a*.83f,a*.25f):new Color(a*.27f,a*.87f,a*.9f);}result.text=basis==0?"0차 기저: 전체 평균 성분":"1차 기저: 넓은 방향 차이의 성분";}
   if(Cue.diagram.StartsWith("math:"))ApplyMath(seconds);
   if(Cue.diagram.StartsWith("geometry:"))ApplyGeometry(seconds);
  }
 }
}
