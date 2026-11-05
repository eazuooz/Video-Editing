using UnityEngine;

namespace Yamyam.PipelineTeaching {
 public sealed partial class PipelineTeachingStage {
  GameObject guideSphere;
  Material guideSurface;

  void DrawVector(Vector3 origin, Vector3 delta, float progress, string symbol, Color color, float dx, float dy) {
   if (progress <= 0 || delta.sqrMagnitude < .0001f) return;
   Vector3 end=origin+delta*Mathf.Clamp01(progress);
   Arrow(origin,end,color);
   if(progress>.55f) Tag(end,symbol,color,dx,dy);
  }

  bool MeaningGuide(int beat,float phase) {
   if(beat!=22 && beat!=38 && (beat<54 || beat>58) && (beat<63 || beat>67)) return false;
   hero.SetActive(false);
   if(beat==22) ClipEdgeGuide(phase);
   else if(beat==38) GlossGuide(phase);
   else if(beat<=58) CameraGuide(beat,phase);
   else NormalGuide(beat,phase);
   return true;
  }

  void ClipEdgeGuide(float phase) {
   Vector3 a=new Vector3(.1f,.9f,-1),b=new Vector3(6,2.7f,-1);
   Vector3 hit=Vector3.Lerp(a,b,.57f);
   Path(Muted,a,b);Path(Blue,hit+Vector3.up*1.8f,hit+Vector3.down*1.5f);
   Tag(a,"A · 안쪽",Teal,-135,26); Tag(b,"B · 바깥쪽",Red,0,-55);
   Tag(hit+Vector3.up*1.8f,"절단 경계",Blue,15,-45);
   Vector3 q=Vector3.Lerp(a,hit,Mathf.SmoothStep(0,1,Mathf.InverseLerp(0,.53f,phase)));
   Path(Teal,a,q);Dot(q,Yellow,.22f);Tag(q,"P(t)",Yellow,15,25);
   objectLabel.text="변이 경계와 만나는 위치는?";
   if(phase>.21f)readout.text="P(t) = (1 − t) A + t B";
   meaning.text="같은 t로 위치와 UV를 함께 보간합니다.";
  }

  void GlossGuide(float phase) {
   Vector3 center=new Vector3(3.0f,1.7f,0),light=new Vector3(1.1f,4.6f,-5f);
   if(!guideSphere){
    guideSphere=GameObject.CreatePrimitive(PrimitiveType.Sphere);guideSphere.transform.SetParent(transform,false);
    guideSphere.name="SpecularStrengthSphere";DestroyImmediate(guideSphere.GetComponent<Collider>());
    guideSurface=Own(new Material(heroMaterial));guideSphere.GetComponent<Renderer>().sharedMaterial=guideSurface;
   }
   guideSphere.SetActive(true);guideSphere.transform.position=center;guideSphere.transform.localScale=Vector3.one*3;
   float ks=Mathf.SmoothStep(0,1,Mathf.InverseLerp(.2f,.82f,phase));
   guideSurface.SetFloat("_Mode",1);guideSurface.SetTexture("_BaseMap",Texture2D.whiteTexture);
   guideSurface.SetColor("_BaseColor",new Color(.12f,.44f,.46f));guideSurface.SetColor("_SpecColor",Color.white*ks);
   guideSurface.SetFloat("_Exponent",28);guideSurface.SetFloat("_Ambient",.1f);
   guideSurface.SetFloat("_ThreeLights",0);guideSurface.SetFloat("_LightRange",20);guideSurface.SetVector("_LightPosition",light);
   // Evaluate the same local L and orthographic V used by the material at the marked point.
   Vector3 n=new Vector3(-.2f,.29f,-1).normalized,p=center+1.5f*n;
   Vector3 l=(light-p).normalized,v=-stageCamera.transform.forward,h=(l+v).normalized;
   Dot(p,Yellow,.11f);Tag(p,"P · 표면점",Yellow,25,44);
   DrawVector(p,n*1.85f,Mathf.InverseLerp(.04f,.18f,phase),"N",Blue,25,-46);
   DrawVector(p,l*2.65f,Mathf.InverseLerp(.12f,.25f,phase),"L",Green,-65,-58);
   // V points directly out of this orthographic view. A ring marks its projected point.
   if(phase>.22f)Tag(p,"⊙ V · 카메라 쪽",White,85,-26);
   DrawVector(p,h*2.2f,Mathf.InverseLerp(.36f,.52f,phase),"H",Teal,-80,35);
   Vector3 a=new Vector3(.45f,-.2f,-2),b=new Vector3(5.45f,-.2f,-2);
   Path(Muted,a,b);Dot(Vector3.Lerp(a,b,ks),Yellow,.14f);
   Tag(a,"약함",Muted,-25,18);Tag(b,"강함",Muted,-45,18);
   objectLabel.text="정반사 세기가 커지면 어디가 밝아질까?";
   if(phase>.2f)readout.text="C = C기본 + kₛ · C정반사";
   meaning.text="빛·카메라·바탕색 고정, 정반사 세기 kₛ만 변화";
  }

  void CameraGuide(int beat,float phase) {
   Vector3 eye=new Vector3(.1f,1.5f,-1);
   float blend=Mathf.SmoothStep(0,1,Mathf.InverseLerp(.15f,.85f,phase));
   if(beat==56||beat==57) {
    bool gl=phase<.5f;
    Vector3 near=eye+Vector3.right*1.25f,far=eye+Vector3.right*5;
    Path(Blue,near+Vector3.down*.46f,near+Vector3.up*.46f);
    Path(Teal,far+Vector3.down*1.45f,far+Vector3.up*1.45f);
    Path(Muted,eye,far+Vector3.up*1.45f);Path(Muted,eye,far+Vector3.down*1.45f);
    float t=phase<.5f?phase*2:(phase-.5f)*2;
    Vector3 sample=Vector3.Lerp(near,far,t);
    Dot(sample,Yellow,.2f);Tag(sample,"P · 깊이 표본",Yellow,-60,47);
    Tag(near+Vector3.up*.46f,"near",Blue,-30,-52);Tag(far+Vector3.up*1.45f,"far",Teal,5,-48);
    objectLabel.text="어느 깊이가 화면에 남을까?";kind.text="현재 화면\n투영·깊이 도식";
    if(phase>.15f)readout.text="zNDC = zclip / wclip";
    meaning.text=gl?"OpenGL 예 · 가까운 면 −1, 먼 면 +1":"Direct3D 예 · 가까운 면 0, 먼 면 +1";
    return;
   }
   float aspect=beat==58?Mathf.Lerp(.65f,1.2f,blend):Mathf.Lerp(1.45f,.68f,blend);
   const float xZoom=1.7320508f;
   const float windowDistance=2.6f;
   float halfHeight=windowDistance/(xZoom*aspect);
   Vector3 window=eye+Vector3.right*windowDistance;
   Dot(eye,Yellow,.22f);Tag(eye,"카메라",Yellow,-68,32);
   Path(Muted,eye,window);Path(Teal,eye,window+Vector3.up*halfHeight);Path(Teal,eye,window-Vector3.up*halfHeight);
   Path(Blue,window+Vector3.up*halfHeight,window-Vector3.up*halfHeight);
   Tag(window+Vector3.up*halfHeight,"창의 위쪽",Teal,16,-45);Tag(window-Vector3.up*halfHeight,"아래쪽",Blue,16,15);
   objectLabel.text="창의 비율을 바꾸면 위아래로 얼마나 보일까?";
   if(phase>.17f)readout.text=beat==55?"θᵥ = 2 atan(1 / sᵧ)":"A = 폭 / 높이      sᵧ = A · sₓ";
   meaning.text="수평 시야각 고정 · 창의 비율만 변화";
  }

  void NormalGuide(int beat,float phase) {
   Vector3 p=new Vector3(3,1.4f,-1);
   Vector3 t=new Vector3(1,0,0),n=new Vector3(0,.62f,-.78f).normalized;
   if(beat==67) {
    Quaternion turn=Quaternion.AngleAxis(Mathf.Lerp(-25,38,phase),Vector3.forward);
    t=turn*t;n=turn*n;
   }
   Vector3 b=Vector3.Cross(n,t).normalized;if(beat==66&&phase>.5f)b=-b;
   Path(Muted,p-t*1.33f-b,p+t*1.33f-b,p+t*1.33f+b,p-t*1.33f+b,p-t*1.33f-b);
   float x=beat>=66?.38f:Mathf.Lerp(-.68f,.68f,Mathf.SmoothStep(0,1,Mathf.InverseLerp(.2f,.82f,phase)));
   Vector3 local=new Vector3(x,.27f,.8f).normalized;
   var texel=new Color32((byte)PipelineMath.Encode(local.x),(byte)PipelineMath.Encode(local.y),(byte)PipelineMath.Encode(local.z),255);
   P3 restored=PipelineMath.Normal8(texel.r,texel.g,texel.b);
   Vector3 world=t*(float)restored.x+b*(float)restored.y+n*(float)restored.z;
   Dot(p,White,.11f);DrawVector(p,t*1.45f,Mathf.InverseLerp(0,.18f,phase),"T",Teal,8,20);
   DrawVector(p,b*1.4f,Mathf.InverseLerp(.09f,.28f,phase),"B",Green,-68,12);
   DrawVector(p,n*1.85f,Mathf.InverseLerp(.15f,.37f,phase),"N",Blue,-64,-58);
   DrawVector(p,world*2.6f,Mathf.InverseLerp(.25f,.48f,phase),"n · 복원",Yellow,16,-54);
   Color data=texel;Dot(p+Vector3.right*2.4f,data,.4f);Tag(p+Vector3.right*2.4f,"RGB 표본",White,0,32);
   objectLabel.text=beat<65?"기운 법선을 색으로 어떻게 기록할까?":"저장된 색은 표면의 어느 방향을 가리킬까?";
   if(phase>.18f)readout.text=beat<65?"c = (nₜ + 1) / 2":"n = x T + y B + z N";
   meaning.text=beat==66?"거울 부호가 바뀌면 B의 방향이 바뀝니다.":"같은 표면의 T·B·N을 기준으로 방향을 읽습니다.";
  }
 }
}
