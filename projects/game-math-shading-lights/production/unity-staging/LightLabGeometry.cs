using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.GameMath.LightLab {
 public sealed partial class LightLabIllustrations {
  [SerializeField] LightLabStage geometryStage;
  [SerializeField] LineRenderer[] geometryLines;
  [SerializeField] string geometryMode;
  [SerializeField] Text geometryHeading;
  void BuildGeometry(LightLabStage stage,Font font){
   geometryStage=stage;geometryMode=Cue.diagram.Substring(9);
   geometryHeading=Text(font,"",46,1040,310,790,120,Yellow);
   int count=geometryMode=="cosineRays"?7:geometryMode=="volumeBounds"?12:geometryMode=="rangeShells"?6:geometryMode=="solidAngle"?5:4;
   geometryLines=new LineRenderer[count];
   for(int i=0;i<count;i++)geometryLines[i]=Path("Explanatory "+geometryMode+" "+i,i==count-1?Cyan:Yellow,Vector3.zero,Vector3.zero);
   if(geometryMode=="cosineRays")geometryHeading.text="같은 빛 → 기울어진 표면의 더 넓은 영역";
   if(geometryMode=="directPaths")geometryHeading.text="광원 → 표면의 한 점 → 카메라";
   if(geometryMode=="rangeShells")geometryHeading.text="r이 2배이면, 구면 넓이는 4배";
   if(geometryMode=="volumeBounds")geometryHeading.text="광원 로컬 공간의 영향 영역";
   if(geometryMode=="reflectConstruction")geometryHeading.text="L의 법선 성분 p → 두 배 → L 빼기";
   if(geometryMode=="solidAngle")geometryHeading.text="같은 광원도 가까우면 더 넓은 방향을 차지";
   detail.text="화살표·경계는 설명용 표식";
  }
  void SetPath(LineRenderer line,params Vector3[] points){line.positionCount=points.Length;line.SetPositions(points);}
  void ApplyGeometry(float seconds){
   if(geometryStage==null||geometryLines==null)return;
   Vector3 p=geometryStage.TeachingProbe.position+geometryStage.TeachingProbe.up*.035f;
   if(geometryMode=="solidAngle"){
    float u=Mathf.SmoothStep(0,1,Mathf.Clamp01(seconds/Mathf.Max(.001f,Cue.duration)));
    float distance=Mathf.Lerp(1.2f,3.2f,u);
    Vector3 c=p+Vector3.up*distance;
    var corners=new[]{c+new Vector3(-.5f,0,-.5f),c+new Vector3(.5f,0,-.5f),c+new Vector3(.5f,0,.5f),c+new Vector3(-.5f,0,.5f)};
    for(int i=0;i<4;i++)SetPath(geometryLines[i],p,corners[i]);
    SetPath(geometryLines[4],corners[0],corners[1],corners[2],corners[3],corners[0]);
    float omega=4*Mathf.Atan(.25f/(distance*Mathf.Sqrt(distance*distance+.5f)));
    result.text="폭 1 m · 높이 1 m · 정면의 직사각형\n거리 "+distance.ToString("0.00")+" m → Ω = "+omega.ToString("0.000")+" sr";
   }
   if(geometryMode=="reflectConstruction"){
    Vector3 n=geometryStage.TeachingProbe.up;
    Vector3 l=Cue.lightType==0?-geometryStage.CurrentLightDirection:(geometryStage.CurrentLightPosition-p).normalized;
    Vector3 projection=Vector3.Dot(n,l)*n;
    Vector3 reflected=2*projection-l;
    SetPath(geometryLines[0],p,p+projection);
    SetPath(geometryLines[1],p+projection,p+l);
    SetPath(geometryLines[2],p+projection,p+2*projection);
    SetPath(geometryLines[3],p+2*projection,p+reflected);
    int active=3;if(Cue.stepTimes!=null){active=-1;for(int i=0;i<Cue.stepTimes.Length;i++)if(seconds>=Cue.stepTimes[i])active=i;}
    for(int i=0;i<4;i++)geometryLines[i].enabled=i<=active;
    result.text="p = (N·L)N\nR = 2p − L";
   }
   if(geometryMode=="directPaths"){
    var lights=new[]{geometryStage.CurrentLightPosition,new Vector3(2.3f,3,-1),new Vector3(-2,3,1.5f)};
    int revealed=3;if(Cue.stepTimes!=null){revealed=1;for(int i=0;i<Cue.stepTimes.Length;i++)if(seconds>=Cue.stepTimes[i])revealed=i+1;}
    for(int i=0;i<3;i++){geometryLines[i].enabled=i<revealed;SetPath(geometryLines[i],lights[i],p);}
    SetPath(geometryLines[3],p,p-geometryStage.RenderCamera.transform.forward*2);
    result.text="각 광원의 기여를 구한 뒤 합산";
   }
   if(geometryMode=="cosineRays"){
    Vector3 n=geometryStage.TeachingProbe.up;
    float cosine=Mathf.Max(.0001f,n.y);
    for(int i=0;i<7;i++){
     Vector3 start=new Vector3(p.x+(i-3)*.11f,p.y+2,p.z);
     float distance=Vector3.Dot(n,start-p)/cosine;
     Vector3 end=start+Vector3.down*distance;
     geometryLines[i].enabled=n.y>.12f;
     SetPath(geometryLines[i],start,end);
    }
    result.text="법선과 빛의 각도: "+Vector3.Angle(n,Vector3.up).ToString("0")+"°\n받는 면적 비율: "+(1/cosine).ToString("0.00")+"배";
   }
   if(geometryMode=="rangeShells"){
    Vector3 origin=geometryStage.CurrentLightPosition;
    for(int i=0;i<6;i++){
     float radius=i<3?.6f:1.2f;int axis=i%3;var points=new Vector3[65];
     for(int k=0;k<65;k++){float a=k*Mathf.PI*2/64;Vector3 v=axis==0?new Vector3(Mathf.Cos(a),Mathf.Sin(a),0):axis==1?new Vector3(0,Mathf.Cos(a),Mathf.Sin(a)):new Vector3(Mathf.Cos(a),0,Mathf.Sin(a));points[k]=origin+radius*v;}
     SetPath(geometryLines[i],points);geometryLines[i].sharedMaterial.SetColor("_BaseColor",i<3?Yellow:Cyan);
    }
    result.text="같은 전체 복사속 Φ\n같은 면적에 들어오는 양은 1/4";
   }
   if(geometryMode=="volumeBounds"){
    var corners=new Vector3[8];var q=Quaternion.LookRotation(geometryStage.CurrentLightDirection);bool perspective=Cue.volumeMode==2;
    for(int i=0;i<8;i++){
     float depth=(i&4)==0?(perspective?.15f:-Cue.volumeSize.z*.5f):(perspective?Cue.volumeSize.z:Cue.volumeSize.z*.5f);
     float width=perspective?depth/Cue.volumeSize.z:1;
     var local=new Vector3(((i&1)==0?-.5f:.5f)*Cue.volumeSize.x*width,((i&2)==0?-.5f:.5f)*Cue.volumeSize.y*width,depth);
     corners[i]=geometryStage.CurrentLightPosition+q*local;
    }
    int line=0;for(int i=0;i<8;i++)for(int bit=1;bit<=4;bit*=2)if((i&bit)==0)SetPath(geometryLines[line++],corners[i],corners[i|bit]);
    result.text=perspective?"원근 투영 · 멀수록 단면이 커짐":"직교 투영 · 같은 크기의 단면";
   }
  }
 }
}
