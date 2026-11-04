using System;
#if !M21_ADVANCED_MATH_ONLY
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEngine;
using UnityEngine.UI;
#endif

namespace Yamyam.GameMath.LightLab {
 // Pure numerical functions can be checked without starting Unity or using a GPU.
 public struct AdvancedDirection {
  public double x,y,z;
  public AdvancedDirection(double x,double y,double z){this.x=x;this.y=y;this.z=z;}
  public static AdvancedDirection operator +(AdvancedDirection a,AdvancedDirection b)=>new AdvancedDirection(a.x+b.x,a.y+b.y,a.z+b.z);
  public static AdvancedDirection operator *(AdvancedDirection a,double s)=>new AdvancedDirection(a.x*s,a.y*s,a.z*s);
  public static double Dot(AdvancedDirection a,AdvancedDirection b)=>a.x*b.x+a.y*b.y+a.z*b.z;
  public static AdvancedDirection Cross(AdvancedDirection a,AdvancedDirection b)=>new AdvancedDirection(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);
  public static AdvancedDirection Unit(AdvancedDirection a){double d=Math.Sqrt(Dot(a,a));if(d<1e-12)throw new ArgumentException("Zero direction");return a*(1/d);}
 }
 public struct AdvancedRGB {
  public double r,g,b;
  public AdvancedRGB(double r,double g,double b){this.r=r;this.g=g;this.b=b;}
  public static AdvancedRGB operator +(AdvancedRGB a,AdvancedRGB b)=>new AdvancedRGB(a.r+b.r,a.g+b.g,a.b+b.b);
  public static AdvancedRGB operator *(AdvancedRGB a,double s)=>new AdvancedRGB(a.r*s,a.g*s,a.b*s);
 }
 public static class LightLabAdvancedMath {
  public static double Clamp(double x,double a,double b)=>Math.Max(a,Math.Min(b,x));
  public static double Schlick(double cosine,double f0){if(f0<0||f0>1)throw new ArgumentException("F0 must be a reflectance fraction.");return f0+(1-f0)*Math.Pow(1-Clamp(cosine,0,1),5);}
  // A directional response illustration, not a complete or energy-normalized BRDF.
  public static double GrainResponse(double direction,double grain,double alphaT=.55,double alphaB=.18,double slope=.25){if(alphaT<=0||alphaB<=0)throw new ArgumentException();double a=direction-grain;return Math.Exp(-Math.Pow(slope*Math.Cos(a)/alphaT,2)-Math.Pow(slope*Math.Sin(a)/alphaB,2));}
  public static AdvancedDirection SphereSample(int i,int count){if(count<=0||i<0||i>=count)throw new ArgumentOutOfRangeException();double y=1-2*(i+.5)/count,az=2*Math.PI*((i*.6180339887498949)%1),r=Math.Sqrt(Math.Max(0,1-y*y));return new AdvancedDirection(r*Math.Cos(az),y,r*Math.Sin(az));}
  public static AdvancedDirection LatLong(double u,double v){double az=2*Math.PI*u,polar=Math.PI*v;return new AdvancedDirection(Math.Sin(polar)*Math.Cos(az),Math.Cos(polar),Math.Sin(polar)*Math.Sin(az));}
  // Nine real orthonormal SH functions, l<=2; coordinate/order are explicit.
  public static double Basis(int index,AdvancedDirection d){
   switch(index){
    case 0:return .28209479177387814;
    case 1:return .4886025119029199*d.y;
    case 2:return .4886025119029199*d.z;
    case 3:return .4886025119029199*d.x;
    case 4:return 1.0925484305920792*d.x*d.y;
    case 5:return 1.0925484305920792*d.y*d.z;
    case 6:return .31539156525252005*(3*d.z*d.z-1);
    case 7:return 1.0925484305920792*d.x*d.z;
    case 8:return .5462742152960396*(d.x*d.x-d.y*d.y);
    default:throw new ArgumentOutOfRangeException(nameof(index));
   }
  }
  // Synthetic angular brightness. These bright caps are not a measured room/probe.
  public static double ScalarEnvironment(AdvancedDirection d){var a=AdvancedDirection.Unit(new AdvancedDirection(.6,.65,.3));var b=AdvancedDirection.Unit(new AdvancedDirection(-.7,.2,-.4));return .12+(AdvancedDirection.Dot(d,a)>Math.Cos(12*Math.PI/180)?.9:0)+(AdvancedDirection.Dot(d,b)>Math.Cos(20*Math.PI/180)?.55:0);}
  public static AdvancedRGB ColorEnvironment(AdvancedDirection d){var a=AdvancedDirection.Unit(new AdvancedDirection(.6,.65,.3));var b=AdvancedDirection.Unit(new AdvancedDirection(-.7,.2,-.4));double warm=AdvancedDirection.Dot(d,a)>Math.Cos(12*Math.PI/180)?1:0,cool=AdvancedDirection.Dot(d,b)>Math.Cos(20*Math.PI/180)?1:0;return new AdvancedRGB(.06+.95*warm+.08*cool,.07+.70*warm+.55*cool,.09+.22*warm+.80*cool);}
  public static double[] ProjectSH(Func<AdvancedDirection,double> field,int samples=8192){if(samples<128)throw new ArgumentException("Insufficient sphere quadrature samples.");var c=new double[9];for(int j=0;j<samples;j++){var d=SphereSample(j,samples);double f=field(d);for(int k=0;k<9;k++)c[k]+=f*Basis(k,d)*4*Math.PI/samples;}return c;}
  public static double ReconstructSH(double[] c,AdvancedDirection d,int count){if(c==null||c.Length<9||count<1||count>9)throw new ArgumentException();double sum=0;for(int i=0;i<count;i++)sum+=c[i]*Basis(i,d);return sum;}
  public static double ReconstructionRMSE(double[] c,int count,int samples=2048){double total=0;for(int i=0;i<samples;i++){var d=SphereSample(i,samples);double e=ReconstructSH(c,d,count)-ScalarEnvironment(d);total+=e*e;}return Math.Sqrt(total/samples);}
  public static AdvancedDirection KernelDirection(AdvancedDirection centre,double exponent,int i,int count){
   if(exponent<0||count<=0)throw new ArgumentException();centre=AdvancedDirection.Unit(centre);
   var helper=Math.Abs(centre.y)<.95?new AdvancedDirection(0,1,0):new AdvancedDirection(1,0,0);
   var tangent=AdvancedDirection.Unit(AdvancedDirection.Cross(helper,centre));var bitangent=AdvancedDirection.Cross(centre,tangent);
   double cos=Math.Pow((i+.5)/count,1/(exponent+1)),sin=Math.Sqrt(Math.Max(0,1-cos*cos)),az=2*Math.PI*((i*.6180339887498949)%1);
   return tangent*(sin*Math.Cos(az))+bitangent*(sin*Math.Sin(az))+centre*cos;
  }
  // Importance-sampled normalized cosine-power kernel, K=(n+1)/(2pi) cos^n(theta).
  // n=1 around N is E(N)/pi for a Lambert diffuse filter; around R it is a
  // pedagogical Phong-lobe reflection prefilter, NOT Unity's GGX implementation.
  public static AdvancedRGB FilterEnvironment(AdvancedDirection centre,double exponent,int samples=512){var sum=new AdvancedRGB();for(int i=0;i<samples;i++)sum+=ColorEnvironment(KernelDirection(centre,exponent,i,samples));return sum*(1.0/samples);}
 }

#if !M21_ADVANCED_MATH_ONLY
 [Serializable] public class AdvancedComparisonFrame {
  public string imagePath,sha256,label,sourceKind;
  public Rect crop=new Rect(0,0,1,1);
 }
 public sealed partial class LightLabStage {
  // Supply before Build for advanced:final-grid. Only verified existing captures.
  public AdvancedComparisonFrame[] AdvancedComparisonFrames;
 }
 public sealed partial class LightLabIllustrations {
  [SerializeField] LightLabStage advancedStage;
  [SerializeField] Transform advancedWall;
  [SerializeField] LineRenderer[] advancedPaths,advancedGrain,advancedFan;
  [SerializeField] LineRenderer advancedLobe;
  [SerializeField] Text advancedHeading,advancedInfo,advancedStatus;
  [SerializeField] RawImage[] advancedImages;
  [SerializeField] Text[] advancedLabels;
  [SerializeField] Image[] advancedBorders;
  [SerializeField] Texture2D[] advancedWeightedBasis,advancedSums;
  [SerializeField] Texture2D advancedEnvironment,advancedFullSH;
  [SerializeField] double[] advancedCoefficients;
  [SerializeField] float[] advancedErrors;
  [SerializeField] Material advancedRayMaterial;
  [SerializeField] Font advancedFont;
  static readonly Color AYellow=new Color(.910f,.812f,.514f),ATeal=new Color(.451f,.780f,.761f),ARed=new Color(.937f,.522f,.522f),AGreen=new Color(.643f,.776f,.627f);

  // Integration: call from Build when Cue.diagram.StartsWith("advanced:").
  void BuildAdvanced(LightLabStage stage,Font font){
   advancedStage=stage;advancedFont=font;
   result.gameObject.SetActive(false);detail.gameObject.SetActive(false);
   advancedHeading=Text(font,"",40,1035,285,790,90,AYellow);
   advancedInfo=Text(font,"",40,1035,748,790,166,Color.white);
   advancedStatus=Text(font,"",40,96,840,900,52,Color.white);
   advancedRayMaterial=new Material(Shader.Find("Universal Render Pipeline/Unlit"));stage.GeneratedObjects.Add(advancedRayMaterial);
   string mode=Cue.diagram.Substring("advanced:".Length);
   if(mode=="ambient-bounce"||mode=="bake-paths")BuildAdvancedBounce(stage,font);
   else if(mode=="fresnel-retro")BuildAdvancedFresnel(font);
   else if(mode=="anisotropy")BuildAdvancedAnisotropy(font);
   else if(mode=="sh-sum")BuildAdvancedSH(stage,font);
   else if(mode=="environment-filter")BuildAdvancedEnvironment(stage,font);
   else if(mode=="final-grid")BuildAdvancedFinalGrid(stage,font);
   else throw new ArgumentException("Unknown advanced teaching diagram: "+Cue.diagram);
  }
  // Integration: call from Apply when Cue.diagram.StartsWith("advanced:").
  void ApplyAdvanced(float seconds){
   if(advancedStage==null)return;
   float u=Mathf.Clamp01(seconds/Mathf.Max(.001f,Cue.duration));
   switch(Cue.diagram){
    case "advanced:ambient-bounce":case "advanced:bake-paths":ApplyAdvancedBounce(seconds,u);break;
    case "advanced:fresnel-retro":ApplyAdvancedFresnel(seconds,u);break;
    case "advanced:anisotropy":ApplyAdvancedAnisotropy(seconds,u);break;
    case "advanced:sh-sum":ApplyAdvancedSH(seconds,u);break;
    case "advanced:environment-filter":ApplyAdvancedEnvironment(seconds,u);break;
    case "advanced:final-grid":ApplyAdvancedFinalGrid(seconds,u);break;
   }
  }
  int AdvancedStep(float seconds,int count){
   if(Cue.stepTimes!=null&&Cue.stepTimes.Length>0){int step=0;for(int i=0;i<Mathf.Min(count,Cue.stepTimes.Length);i++)if(seconds>=Cue.stepTimes[i])step=i;return step;}
   // Preview-only proportional progression. Final production must bind stepTimes
   // to actual speech; this fallback adds no pauses and never loops.
   return Mathf.Min(count-1,Mathf.FloorToInt(Mathf.Clamp01(seconds/Mathf.Max(.001f,Cue.duration))*count));
  }
  LineRenderer AdvancedPath(string name,Color color,int points=2){
   var lr=Path(name,Color.white,new Vector3[points]);
   var mat=new Material(advancedRayMaterial);mat.SetColor("_BaseColor",color);mat.SetColor("_Color",color);advancedStage.GeneratedObjects.Add(mat);lr.sharedMaterial=mat;lr.startColor=lr.endColor=Color.white;lr.widthMultiplier=.032f;return lr;
  }
  void AdvancedArrow(LineRenderer line,Vector3 start,Vector3 end,float width=.035f){
   Vector3 delta=end-start;if(delta.sqrMagnitude<1e-10f){line.enabled=false;return;}line.enabled=true;Vector3 d=delta.normalized,side=Vector3.Cross(d,cameraRef.transform.forward).normalized*.075f;
   if(side.sqrMagnitude<1e-8f)side=cameraRef.transform.right*.075f;Vector3 back=end-d*Mathf.Min(.18f,delta.magnitude*.25f);
   line.positionCount=5;line.SetPositions(new[]{start,end,back+side,end,back-side});line.widthMultiplier=width;
  }
  RawImage AdvancedImage(Rect rect){var go=new GameObject("Advanced image · source kind explicit",typeof(RectTransform));go.transform.SetParent(canvas.transform,false);var image=go.AddComponent<RawImage>();SetAdvancedRect(image.rectTransform,rect);return image;}
  void SetAdvancedRect(RectTransform tr,Rect rect){tr.anchorMin=tr.anchorMax=tr.pivot=new Vector2(0,1);tr.anchoredPosition=new Vector2(rect.x,-rect.y);tr.sizeDelta=new Vector2(rect.width,rect.height);}
  void BuildAdvancedFourMaps(Font font){
   advancedImages=new RawImage[4];advancedLabels=new Text[4];advancedBorders=new Image[4];
   for(int i=0;i<4;i++){
    float x=1035+(i%2)*405,y=360+(i/2)*205;
    advancedBorders[i]=Panel(new Color(.18f,.18f,.18f),x-3,y-3,356,181);
    advancedImages[i]=AdvancedImage(new Rect(x,y,350,175));
    advancedLabels[i]=Text(font,"",40,x,y-48,385,48,Color.white);
   }
   advancedHeading.fontSize=40;SetAdvancedRect(advancedHeading.rectTransform,new Rect(1035,255,790,55));
  }
  Texture2D AdvancedTexture(Func<AdvancedDirection,Color> sample,string name,int width=128,int height=64){
   var tex=new Texture2D(width,height,TextureFormat.RGBA32,false,true){name=name,filterMode=FilterMode.Bilinear,wrapMode=TextureWrapMode.Clamp};var pixels=new Color[width*height];
   for(int y=0;y<height;y++)for(int x=0;x<width;x++){var d=LightLabAdvancedMath.LatLong((x+.5)/width,1-(y+.5)/height);pixels[y*width+x]=sample(d);}tex.SetPixels(pixels);tex.Apply();advancedStage.GeneratedObjects.Add(tex);return tex;
  }
  static Color AdvancedBrightness(double value){float v=(float)LightLabAdvancedMath.Clamp(value/1.1,0,1);return value>=0?new Color(v,v,v,1):new Color(0,.25f+(float)Math.Min(.5,-value),.35f+(float)Math.Min(.5,-value),1);}
  static Color AdvancedSigned(double value){float magnitude=(float)LightLabAdvancedMath.Clamp(Math.Abs(value)/.25,0,1);return Color.Lerp(new Color(.035f,.035f,.035f),value>=0?AYellow:ATeal,magnitude);}
  static Color AdvancedColor(AdvancedRGB c)=>new Color((float)Math.Max(0,c.r),(float)Math.Max(0,c.g),(float)Math.Max(0,c.b),1);

  void BuildAdvancedBounce(LightLabStage stage,Font font){
   advancedWall=Primitive(stage,PrimitiveType.Cube,"Illustrated bounce surface · not a baked result",new Vector3(-2.5f,1.45f,.95f),new Vector3(.12f,2.8f,2.5f),new Color(.12f,.15f,.15f));
   advancedPaths=new[]{AdvancedPath("Direct relation",AYellow),AdvancedPath("Light to wall relation",AYellow),AdvancedPath("Wall to object relation",ATeal),AdvancedPath("Secondary wall sample",AGreen)};
   advancedHeading.text="직접 경로와 반사 경로";
   Text(font,"광원 → 표면\n광원 → 벽 → 표면",44,1035,390,790,150,Color.white);
   Text(font,Cue.diagram=="advanced:bake-paths"?"고정할 배치\n광원 위치 · 표면 · 재질":"복잡한 간접광을\n환경광 한 값으로 근사",40,1035,565,790,140,ATeal);
   advancedStatus.text="해설용 빛의 경로";
  }
  void ApplyAdvancedBounce(float seconds,float u){
   int phase=AdvancedStep(seconds,3);Vector3 light=advancedStage.CurrentLightPosition,target=mover.position+Vector3.up*1.2f,wall=new Vector3(-2.42f,1.7f,.55f);
   AdvancedArrow(advancedPaths[0],light,target);AdvancedArrow(advancedPaths[1],light,wall);AdvancedArrow(advancedPaths[2],wall,target);AdvancedArrow(advancedPaths[3],wall+Vector3.up*.6f,target+Vector3.up*.3f,.024f);
   advancedPaths[1].enabled=advancedPaths[2].enabled=phase>=1;advancedPaths[3].enabled=phase>=2;
   advancedInfo.text=Cue.diagram=="advanced:bake-paths"?phase<2?"경로 계산의 대상과 배치를 먼저 정합니다":"이 고정 관계를 저장한 뒤 실제 베이크 결과와 비교":phase<2?"밝기에는 표면으로 바로 온 빛과\n다른 표면을 거친 빛이 함께 기여":"환경광 상수는 이 복잡한 분포를\n한 값으로 대신하는 근사입니다";
  }
  void BuildAdvancedFresnel(Font font){
   advancedPaths=new[]{AdvancedPath("Incident light · diagram",AYellow),AdvancedPath("Mirror outgoing direction · diagram",ATeal),AdvancedPath("Return toward source · diagram",AGreen),AdvancedPath("Known surface normal",new Color(.55f,.7f,.55f))};
   advancedHeading.text="입사각과 되돌아가는 방향";
   Text(font,"Fresnel / Retroreflection\n프레넬 효과 / 재귀반사",40,1035,385,790,110,Color.white);
   Text(font,"같은 표면·카메라에서\n한 가지 성질만 바꿉니다",36,1035,550,790,100,Color.white);
   advancedStatus.text="해설용 방향 모델 · Schlick 근사";
  }
  void ApplyAdvancedFresnel(float seconds,float u){
   int phase=AdvancedStep(seconds,2);Vector3 p=advancedStage.TeachingProbe.position+Vector3.up*.06f,n=Vector3.up;
   float local=phase==0?(Cue.stepTimes!=null&&Cue.stepTimes.Length>1?Mathf.Clamp01(seconds/Mathf.Max(.001f,Cue.stepTimes[1])):Mathf.Clamp01(u*2)):1;
   float angle=Mathf.Lerp(10,80,local)*Mathf.Deg2Rad;Vector3 l=new Vector3(-Mathf.Sin(angle),Mathf.Cos(angle),0),r=Vector3.Reflect(-l,n),source=p+l*1.9f;
   double f=LightLabAdvancedMath.Schlick(Math.Cos(angle),.04);
   AdvancedArrow(advancedPaths[0],source,p);AdvancedArrow(advancedPaths[3],p,p+n*1.2f,.025f);
   AdvancedArrow(advancedPaths[1],p,p+r*1.8f,.025f+.10f*(float)f);
   AdvancedArrow(advancedPaths[2],p+cameraRef.transform.right*.055f,source+cameraRef.transform.right*.055f,.065f);
   advancedPaths[2].enabled=phase==1;advancedPaths[1].enabled=phase==0;
   advancedHeading.text=phase==0?"프레넬 효과: 각도에 따라 반사율 변화":"재귀반사: 빛이 들어온 쪽으로 돌아감";
   advancedInfo.text=phase==0?"θ = "+(angle*Mathf.Rad2Deg).ToString("0")+"°   F ≈ "+f.ToString("0.000")+"\nF₀ = 0.04\nF₀ + (1−F₀)(1−cosθ)⁵":"입사 방향과 귀환 방향 비교\n반사광이 광원 쪽으로 돌아갑니다";
  }
  void BuildAdvancedAnisotropy(Font font){
   advancedGrain=new LineRenderer[9];for(int i=0;i<advancedGrain.Length;i++)advancedGrain[i]=AdvancedPath("Surface grain guide "+i,AGreen);
   advancedLobe=AdvancedPath("Illustrated anisotropic response lobe",AYellow,97);
   advancedPaths=new[]{AdvancedPath("Fixed projected half direction",ATeal)};
   advancedHeading.text="광원과 시선은 고정 · 표면의 결만 회전";
   Text(font,"결 방향 T / 수직 방향 B\n두 방향의 반응 폭이 다릅니다",40,1035,390,790,135,Color.white);
   Text(font,"초록 선: 결 방향\n노란 곡선: 방향별 응답 예",36,1035,570,790,100,Color.white);
   advancedStatus.text="해설용 방향 응답";
  }
  void ApplyAdvancedAnisotropy(float seconds,float u){
   Vector3 p=advancedStage.TeachingProbe.position+Vector3.up*.065f;float grain=Mathf.Lerp(0,90,u)*Mathf.Deg2Rad;
   Vector3 t=new Vector3(Mathf.Cos(grain),0,Mathf.Sin(grain)),b=Vector3.Cross(Vector3.up,t);
   for(int i=0;i<advancedGrain.Length;i++){float offset=(i-4)*.065f,len=Mathf.Sqrt(Mathf.Max(0,.31f*.31f-offset*offset));advancedGrain[i].positionCount=2;advancedGrain[i].SetPositions(new[]{p+b*offset-t*len,p+b*offset+t*len});advancedGrain[i].widthMultiplier=.009f;}
   var points=new Vector3[97];for(int i=0;i<points.Length;i++){double a=i*2*Math.PI/(points.Length-1),response=LightLabAdvancedMath.GrainResponse(a,grain);float radius=.48f+(float)response*.7f;points[i]=p+new Vector3((float)Math.Cos(a),.03f,(float)Math.Sin(a))*radius;}advancedLobe.positionCount=points.Length;advancedLobe.SetPositions(points);
   AdvancedArrow(advancedPaths[0],p,p+Vector3.right*1.35f,.035f);
   double current=LightLabAdvancedMath.GrainResponse(0,grain);
   advancedInfo.text="결 회전 = "+(grain*Mathf.Rad2Deg).ToString("0")+"°\n고정 방향의 교육용 응답 = "+current.ToString("0.000");
  }
  void BuildAdvancedSH(LightLabStage stage,Font font){
   BuildAdvancedFourMaps(font);advancedHeading.text="기저 × 계수 → 방향 분포";
   advancedCoefficients=LightLabAdvancedMath.ProjectSH(LightLabAdvancedMath.ScalarEnvironment,8192);
   advancedEnvironment=AdvancedTexture(d=>AdvancedBrightness(LightLabAdvancedMath.ScalarEnvironment(d)),"Synthetic SH source field");
   advancedFullSH=AdvancedTexture(d=>AdvancedBrightness(LightLabAdvancedMath.ReconstructSH(advancedCoefficients,d,9)),"Nine-term SH reconstruction");
   advancedWeightedBasis=new Texture2D[9];for(int i=0;i<9;i++){int k=i;advancedWeightedBasis[i]=AdvancedTexture(d=>AdvancedSigned(advancedCoefficients[k]*LightLabAdvancedMath.Basis(k,d)),"Weighted SH basis "+i);}
   int[] counts={1,2,4,9};advancedSums=new Texture2D[counts.Length];advancedErrors=new float[counts.Length];
   for(int i=0;i<counts.Length;i++){int count=counts[i];advancedSums[i]=AdvancedTexture(d=>AdvancedBrightness(LightLabAdvancedMath.ReconstructSH(advancedCoefficients,d,count)),"Partial SH sum "+count);advancedErrors[i]=(float)LightLabAdvancedMath.ReconstructionRMSE(advancedCoefficients,count);}
   advancedStatus.text="합성 분포 · 노랑(+) / 청록(−)";
  }
  void ApplyAdvancedSH(float seconds,float u){
   int step=AdvancedStep(seconds,4);int[] basisIndices={0,1,3,6},counts={1,2,4,9};int k=basisIndices[step],count=counts[step];
   advancedImages[0].texture=advancedEnvironment;advancedImages[1].texture=advancedWeightedBasis[k];advancedImages[2].texture=advancedSums[step];advancedImages[3].texture=advancedFullSH;
   advancedLabels[0].text="원래 분포";advancedLabels[1].text="c"+k+" × Y"+k;advancedLabels[2].text=count+"항의 합";advancedLabels[3].text="9항 재구성";
   for(int i=0;i<4;i++)advancedBorders[i].color=i==2?AYellow:new Color(.18f,.18f,.18f);
   var direction=LightLabAdvancedMath.LatLong(.18,.3);double basis=LightLabAdvancedMath.Basis(k,direction),weighted=advancedCoefficients[k]*basis;
   advancedInfo.text="c"+k+" = "+advancedCoefficients[k].ToString("0.000")+"   Y"+k+" = "+basis.ToString("0.000")+"\n이 항의 기여 = "+weighted.ToString("0.000")+"\n날카로운 무늬는 흐려집니다";
  }
  void BuildAdvancedEnvironment(LightLabStage stage,Font font){
   BuildAdvancedFourMaps(font);advancedHeading.text="같은 환경 · 다른 방향 필터";
   advancedImages[0].texture=AdvancedTexture(d=>AdvancedColor(LightLabAdvancedMath.ColorEnvironment(d)),"Synthetic incident environment");
   advancedImages[1].texture=AdvancedTexture(d=>AdvancedColor(LightLabAdvancedMath.FilterEnvironment(d,1)),"Diffuse cosine filter E over pi");
   advancedImages[2].texture=AdvancedTexture(d=>AdvancedColor(LightLabAdvancedMath.FilterEnvironment(d,64)),"Narrow cosine-power reflection prefilter");
   advancedImages[3].texture=AdvancedTexture(d=>AdvancedColor(LightLabAdvancedMath.FilterEnvironment(d,2)),"Broad cosine-power reflection prefilter");
   advancedLabels[0].text="환경 L(ω)";advancedLabels[1].text="난반사 E/π";advancedLabels[2].text="반사 n=64";advancedLabels[3].text="반사 n=2";
   advancedFan=new LineRenderer[24];for(int i=0;i<advancedFan.Length;i++)advancedFan[i]=AdvancedPath("Filter direction sample "+i,ATeal);
   advancedStatus.text="합성 환경 · Phong 필터";
  }
  void ApplyAdvancedEnvironment(float seconds,float u){
   int phase=AdvancedStep(seconds,3),selected=phase+1;for(int i=0;i<4;i++)advancedBorders[i].color=i==selected?AYellow:new Color(.18f,.18f,.18f);
   Vector3 p=advancedStage.TeachingProbe.position+Vector3.up*.08f,n=advancedStage.TeachingProbe.up,v=cameraRef.orthographic?-cameraRef.transform.forward:(cameraRef.transform.position-p).normalized,r=Vector3.Reflect(-v,n);
   Vector3 centre=phase==0?n:r;double exponent=phase==0?1:phase==1?64:2;
   var c=new AdvancedDirection(centre.x,centre.y,centre.z);
   for(int i=0;i<advancedFan.Length;i++){var d=LightLabAdvancedMath.KernelDirection(c,exponent,i,advancedFan.Length);Vector3 direction=new Vector3((float)d.x,(float)d.y,(float)d.z);AdvancedArrow(advancedFan[i],p+direction*1.2f,p,.012f);}
   advancedInfo.text=phase==0?"법선 N 주변 반구를 cosθ로 가중\nρ=1인 램버트 출사값은 E/π":"반사 방향 R 주변을 로브 폭에 맞게 필터\n현재 교육용 지수 n = "+exponent.ToString("0");
  }
  void BuildAdvancedFinalGrid(LightLabStage stage,Font font){
   var records=stage.AdvancedComparisonFrames;
   if(records==null||records.Length!=4)throw new InvalidOperationException("Final comparison requires four verified finished same-scene captures; no placeholder grid is accepted.");
   advancedImages=new RawImage[4];advancedLabels=new Text[4];advancedBorders=new Image[4];
   advancedHeading.gameObject.SetActive(false);advancedInfo.gameObject.SetActive(false);
   for(int i=0;i<4;i++){
    var rec=records[i];if(rec==null||string.IsNullOrWhiteSpace(rec.label)||string.IsNullOrWhiteSpace(rec.sourceKind)||string.IsNullOrWhiteSpace(rec.imagePath)||string.IsNullOrWhiteSpace(rec.sha256))throw new InvalidOperationException("Each comparison capture needs path, label, source kind and SHA256.");
    string path=System.IO.Path.GetFullPath(rec.imagePath);string normalized=path.Replace('\\','/');
    if(!normalized.Contains("/game-math-shading-lights/")||!File.Exists(path))throw new InvalidOperationException("Comparison captures must be existing local M21 files: "+path);
    byte[] bytes=File.ReadAllBytes(path);string hash;using(var sha=SHA256.Create())hash=BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();
    if(hash!=rec.sha256.ToLowerInvariant())throw new InvalidOperationException("Comparison capture hash mismatch: "+path);
    var tex=new Texture2D(2,2,TextureFormat.RGBA32,false,true);if(!ImageConversion.LoadImage(tex,bytes,false)||tex.width<1920||tex.height<1080)throw new InvalidOperationException("Comparison requires original FHD-or-larger frame: "+path);stage.GeneratedObjects.Add(tex);
    if(rec.crop.width<=0||rec.crop.height<=0||rec.crop.xMin<0||rec.crop.yMin<0||rec.crop.xMax>1||rec.crop.yMax>1)throw new ArgumentException("Comparison crop must be normalized and positive.");
    float x=150+(i%2)*870,y=300+(i/2)*300;float aspect=tex.width*rec.crop.width/(tex.height*rec.crop.height),w=Mathf.Min(720,240*aspect),h=w/aspect;
    advancedBorders[i]=Panel(new Color(.18f,.18f,.18f),x-4,y-4,728,248);
    advancedImages[i]=AdvancedImage(new Rect(x+(720-w)/2,y+(240-h)/2,w,h));advancedImages[i].texture=tex;advancedImages[i].uvRect=rec.crop;
    advancedLabels[i]=Text(font,rec.label,40,x,y-48,730,48,Color.white);
    Text(font,rec.sourceKind,40,x,y+244,730,48,Color.white);
   }
   advancedStatus.gameObject.SetActive(false);
  }
  void ApplyAdvancedFinalGrid(float seconds,float u){
   int selected=AdvancedStep(seconds,4);for(int i=0;i<4;i++){advancedBorders[i].color=i==selected?AYellow:new Color(.18f,.18f,.18f);advancedLabels[i].color=i==selected?AYellow:Color.white;}
  }
 }
#endif
}
