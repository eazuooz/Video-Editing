using UnityEngine;
namespace Yamyam.SkinNormal {
 public sealed partial class SkinNormalTeachingStage {
  static float Ramp(float t,float a,float b){return Mathf.Clamp01((t-a)/(b-a));}
  void Mark(Vector3 o, Vector3 end,string name,Color c,float dx,float dy,float progress=1){
   if(progress<=0)return;
   Vector3 p=Vector3.Lerp(o,end,progress);Arrow(o,p,c);
   if(progress>.42f)Tag(p,name,c,new Vector2(dx,dy));
  }
  void Bar(float t,string left,string right){
   Vector3 a=new Vector3(.65f,-.06f,-3),b=new Vector3(6,-.06f,-3);
   Path(Muted,a,b);Dot(Vector3.Lerp(a,b,t),Yellow,.18f);
   Tag(a,left,Muted,new Vector2(-50,13));Tag(b,right,Muted,new Vector2(-100,13));
  }
  void SetText(string purpose,string formula,string result,float u){
   objectLabel.text=purpose;code.text="";readout.text=u<.12f?"":formula;explanation.text=result;
  }
  void TeachingFrame(Vector3 o,Vector3 t,Vector3 b,Vector3 n,Vector3 world,float u,bool axes=true){
   if(axes){
    Mark(o,o+t*1.35f,"T",Teal,12,5,Ramp(u,.02f,.22f));
    Mark(o,o+b*1.35f,"B",Green,-58,-55,Ramp(u,.12f,.34f));
    Mark(o,o+n*1.4f,"N",Blue,-80,12,Ramp(u,.20f,.42f));}
   Mark(o,o+world*2.25f,"n · 복원",Yellow,-80,-70,Ramp(u,.36f,.55f));Dot(o,White,.14f);
  }
  void DrawMeaning(int i,float u){
   if(i==1||i==2||i==3||i==9||i==14||i==15||i==17||i==18||i==22||i==34||i==35)return;
   // Replace the old coordinate worksheets instead of layering a second set
   // of labels over them. Keep the measured animation clock and original rig.
   lineCursor=dotCursor=tagCursor=0;code.text="";
   if(i<=13){
    if(i==4||i==5||i==6||i==7||i==12){
     armGroup.SetActive(true);float angle=i==5?80:Mathf.Lerp(34,92,u);
     float w=i==5?Mathf.Lerp(.16f,.86f,Ramp(u,.28f,.83f)):.52f;
     // Use the exact same pair of transforms and paint weight on the sleeve
     // vertex we mark. Mark a known front-facing point of its mesh.
     int vi=15*16+14;Vector3 bind=armBind[vi],rot=Quaternion.AngleAxis(angle,Vector3.forward)*bind;
     var vv=new Vector3[armBind.Length];
     for(int v=0;v<vv.Length;v++){float wi=i==5?Mathf.Clamp01(armWeights[v]+(w-armWeights[vi])):armWeights[v];
      vv[v]=Vector3.Lerp(armBind[v],Quaternion.AngleAxis(angle,Vector3.forward)*armBind[v],wi);}
     if(i!=5)w=armWeights[vi];
     armMesh.vertices=vv;armMesh.RecalculateNormals();armMesh.RecalculateBounds();
     armGroup.transform.localScale=new Vector3(1.65f,1.65f,1.65f);
     Vector3 a=armGroup.transform.TransformPoint(bind),b=armGroup.transform.TransformPoint(rot),p=armGroup.transform.TransformPoint(vv[vi]);
     // Put the leaders in front of the material while retaining each projected anchor.
     a.z=b.z=p.z=-3;Vector3 aNote=new Vector3(.9f,3.45f,-3),bNote=new Vector3(5.2f,3.55f,-3),pNote=new Vector3(5.3f,.65f,-3);
     if(u>.1f){Path(Blue,a,aNote);Dot(a,Blue,.14f);Tag(aNote,"A · 위팔",Blue,new Vector2(-125,-52));}
     if(u>.32f||i!=4){Path(Green,b,bNote);Dot(b,Green,.14f);Tag(bNote,"B · 아래팔",Green,new Vector2(-35,-52));}
     if(u>.58f||i!=4){Path(Yellow,p,pNote);Dot(p,Yellow,.16f);Tag(pNote,"P · 소매",Yellow,new Vector2(10,-30));}
     string aim=i==6?"무엇을 저장해야 이 점을 다시 찾을까?":i==7?"본을 하나씩 더하면 어디에 도착할까?":i==12?"정점 위치 한 벌로 같은 결과를 얻을까?":"소매의 점 P는 어디에 놓일까?";
     string f=i==12?"Mᵢ = Jᵢ Bᵢ⁻¹      P = (Σ wᵢ Mᵢ) p":i==6?"wA + wB = 1":"P = wA A + wB B";
     SetText(aim,f,i==5?"아래팔의 몫이 커질수록 P가 B에 가까워집니다.":"두 본이 옮긴 위치를 섞으면 소매가 이어집니다.",u);
     if(i==5)Bar(w,"wB · 작음","wB · 큼");
     if(i==6||i==7||i==12){hero.SetActive(false);code.text=i==7?C("for",Blue)+" each bone\n  P += "+C("weight",Green)+" × "+C("position",Teal):i==6?C("boneIndex",Teal)+"   어느 본인가\n"+C("boneWeight",Green)+"   얼마나 따를까":C("B",Blue)+"   바인드 본\n"+C("J",Green)+"   현재 본\n"+C("p",Yellow)+"   원래 정점";
     }
     return;
    }
    if(i==10||i==11){
     hero.SetActive(false);armGroup.SetActive(false);Vector3 bind=new Vector3(-3.3f,1.45f,-2),delta=new Vector3(1.65f,1f,0),now=bind+Vector3.right*5.6f;
     Vector3 bone=Vector3.Lerp(bind,now,Ramp(u,.45f,.88f)),button=bone+delta;
     Path(Muted,bind,now);Dot(bind,Blue,.24f);Tag(bind,"B · 처음 본",Blue,new Vector2(-155,34));
     Dot(bone,Green,.20f);if(u>.58f)Tag(bone,"J · 현재 본",Green,new Vector2(12,29));
     Mark(bone,button,"P · 단추",Yellow,20,-48,Ramp(u,.08f,.4f));
     if(u>.50f){Path(Muted,bind+delta,button);Dot(bind+delta,Blue,.12f);Tag(bind+delta,"p · 원래 단추",Blue,new Vector2(-230,-68));}
     SetText("같은 단추는 새 자세에서 어디에 있을까?","P = J B⁻¹ p","본에서 본 간격은 그대로, 기준 좌표계만 움직입니다.",u);return;
    }
    if(i==8){
     Vector3 o=new Vector3(2,1.4f,-3);float sx=1+u;
     Vector3 t=new Vector3(sx,-1,0).normalized,n=new Vector3(1/sx,1,0).normalized;
     Path(Muted,o-t*2.4f,o+t*2.4f);Mark(o,o+n*1.7f,"N′ · 여전히 수직",Green,-40,-65);
     Mark(o,o+new Vector3(sx,1,0).normalized*2.4f,"MN · 틀린 방향",Red,10,4,Ramp(u,.25f,.55f));
     SetText("늘어난 표면에 수직인 방향은?","N′ = normalize(M⁻ᵀ N)","비균일 확대에서 점과 법선에 같은 변환을 쓰면 수직이 깨집니다.",u);return;
    }
    if(i==13){DeformSleeve(180*u,false,true);Vector3 mid=armGroup.transform.TransformPoint(armMesh.vertices[12*16+12]);mid.z=-3;
     Dot(mid,Yellow,.16f);Tag(mid,"중앙 단면",Yellow,new Vector2(18,-55));SetText("비틀린 소매의 굵기는 유지될까?","선형 혼합 ≠ 순수 회전","서로 다른 회전을 평균내면 소매 가운데가 가늘어집니다.",u);return;}
   }
   if(i==16||i==19||i==20||i==21||i==23||i==24){
    plateGroup.SetActive(true);hero.SetActive(false);
    float turn=i==21?Mathf.Lerp(32,70,Ramp(u,.60f,1)):36;
    bool mirror=i==24&&u>=.50f;SetPatchUV(mirror);
    plateGroup.transform.rotation=Quaternion.Euler(-16,turn,0);var tr=plateGroup.transform;
    float r=(i==16||i==20)?Mathf.Lerp(.5f,.14f,Ramp(u,.29f,.88f)):.20f;
    Color32 texel=new Color(r,.5f,.86f,1);constantNormalData.SetPixel(0,0,texel);constantNormalData.Apply();
    surface.SetTexture("_NormalRGB",constantNormalData);surface.SetFloat("_ShowData",0);surface.SetVector("_LightDirectionWS",new Vector3(.55f,.5f,-1).normalized);
    var n=-tr.forward;var t=mirror?-tr.right:tr.right;var b=tr.up;
    Vector3 local=new Vector3(texel.r/255f*2-1,texel.g/255f*2-1,texel.b/255f*2-1).normalized;
    if(i==23){ // Show the actual oblique basis and both decompositions of v.
     plateGroup.SetActive(false);var o=new Vector3(1.2f,1,-3);var bx=new Vector3(.95f*Ramp(u,.18f,.85f),1);
     Mark(o,o+Vector3.right*2,"T",Teal,10,10);Mark(o,o+bx*1.85f,"B",Green,12,-50);
     var v=new Vector3(1.2f,1.4f,0);Mark(o,o+v*1.9f,"v",Yellow,-50,-58);
     SetText("같은 방향을 다른 좌표로 읽으려면?","vₜ = F⁻¹ v     ·     F = [T B N]","축이 정규직교일 때만 F의 전치가 역행렬과 같습니다.",u);return;
    }
    PatchBoundary();TeachingFrame(tr.position+(-tr.forward)*.08f,t,b,n,(t*local.x+b*local.y+n*local.z).normalized,u);
    string purpose=i==16?"텍스처에 방향을 어떻게 담을까?":i==20?"빨강 채널을 바꾸면 법선은 어디로 기울까?":i==24?"거울 UV에서 B의 방향은?":"이 면의 바깥쪽과 텍스처의 가로는 어디일까?";
    string f=i==16?"c = (nₜ + 1) / 2":i==20?"nₜ = normalize(2c − 1)":i==24?"B = h (N × T)":"n = xT + yB + zN";
    SetText(purpose,f,i==20?"빛은 고정하고 빨강 성분만 바꿉니다.":i==24?"h는 좌우 방향의 부호 · N은 그대로입니다.":"T: 가로   B: 세로   N: 표면 밖",u);
    if(i==20||i==16){Bar(r,"R · 낮음","R · 높음");}
    return;
   }
   if(i<25||i>33)return;
   {
   hero.SetActive(false);plateGroup.SetActive(false);
   Vector3 o=new Vector3(-5.8f,.45f,-2), q1=new Vector3(3f,.22f,0),q2=new Vector3(.48f,2.35f,0);
   float s1=i==29?-1:1, t2=i==30?1-Ramp(u,.12f,.9f):1;
   Vector3 uv=new Vector3(2.15f,.45f,-2),e1=Vector3.right*s1*2.5f,e2=Vector3.up*t2*2.35f;
   Path(Muted,o,o+q1,o+q2,o);Path(Yellow,uv,uv+e1,uv+e2,uv);
   Tag(o,"p₀",White,new Vector2(-95,15));Tag(o+q1,"p₁",Blue,new Vector2(12,8));Tag(o+q2,"p₂",Green,new Vector2(-70,-64));
   Mark(o,o+q1,"q₁",Teal,-120,25,Ramp(u,.06f,.26f));Mark(o,o+q2,"q₂",Green,10,-10,Ramp(u,.15f,.38f));
   Tag(uv,"UV₀",White,new Vector2(-60,26));Tag(uv+e1,"(s₁,t₁)",Teal,new Vector2(10,10));Tag(uv+e2,"(s₂,t₂)",Green,new Vector2(0,-58));
   float D=s1*t2;
   string purpose="텍스처에서 움직인 길은 모델 위의 어느 길일까?",f="q₁ = s₁ T + t₁ B     ·     q₂ = s₂ T + t₂ B",res="왼쪽은 모델의 변, 오른쪽은 같은 변의 UV 변화입니다.";
   if(i>=26&&i<=30&&Mathf.Abs(D)>.0001f){
    var T=q1/s1;var B=q2/t2;
    Mark(o,o+T.normalized*1.7f,"T",Yellow,-15,-62,Ramp(u,.28f,.6f));Mark(o,o+B.normalized*1.4f,"B",Blue,-85,4,Ramp(u,.55f,.85f));
    if(i==28){float x=Ramp(u,.12f,.45f)*.6f,y=Ramp(u,.56f,.86f)*.38f;Dot(o+q1*x+q2*y,Yellow,.22f);Dot(uv+e1*x+e2*y,Yellow,.22f);}
   }
   if(i==27||i==29||i==30){f="D = s₁ t₂ − s₂ t₁";res=i==30?"UV가 한 줄이 되면 두 방향을 따로 풀 수 없습니다.":i==29?"같은 모델에서 UV의 가로만 뒤집으면 T가 반대가 됩니다.":"D는 부호가 있는 UV 넓이의 두 배입니다.";
    if(i==27)f=u<.51f?f:u<.79f?"T = (t₂ q₁ − t₁ q₂) / D":"B = (s₁ q₂ − s₂ q₁) / D";
    purpose=i==30?"UV가 납작해지면 어떤 방향을 잃을까?":"두 변에서 T와 B를 어떻게 분리할까?";
   }else if(i==25)f="q₁ = p₁ − p₀    ·    (s₁, t₁) = UV₁ − UV₀";
   else if(i>=31){
    lineCursor=dotCursor=tagCursor=0;Vector3 root=new Vector3(.2f,1,-2);
    if(i==31){Vector3 a=new Vector3(2.2f,.15f,0),b=new Vector3(1.3f,1.1f,0);Path(Muted,root+Vector3.left*2,root+Vector3.up*1.65f,root,root+Vector3.left*2);Path(Muted,root,root+Vector3.up*1.65f,root+Vector3.right*3,root);
     Mark(root,root+a,"T₁",Teal,10,5);Mark(root+a,root+a+b,"T₂",Green,10,-62,Ramp(u,.28f,.68f));Dot(root,White,.22f);f="T = Σ Tᵢ    ·    B = Σ Bᵢ";purpose="공유 정점의 방향은 어디서 올까?";res="이웃한 면에서 온 접선들을 같은 정점에 모읍니다.";}
    if(i==32){Vector3 t=new Vector3(3,1.4f,0),n=Vector3.up;
     Mark(root,root+n*1.9f,"N",Blue,-80,-50);Mark(root,root+t,"T",Red,10,-52);Path(Muted,root+Vector3.right*3,root+t);
     Mark(root,root+Vector3.right*3,"T′",Teal,12,12,Ramp(u,.32f,.70f));f="T′ = normalize(T − N (N · T))";purpose="접선에서 수직 성분만 빼면?";res="법선 방향의 성분을 덜어내면 T′가 표면에 눕습니다.";}
    if(i==33){Mark(root,root+Vector3.left*2,"T 왼쪽",Teal,-155,-55);Mark(root,root+Vector3.right*2,"T 오른쪽",Green,10,-55);
     Dot(root+Vector3.left*Ramp(u,.42f,.80f)*.30f,Teal,.24f);Dot(root+Vector3.right*Ramp(u,.42f,.80f)*.30f,Green,.24f);
     f="한 위치 · 서로 다른 두 접선";purpose="이음선의 두 방향을 왜 분리할까?";res="반대 방향을 평균내지 않고 양쪽 정점에 따로 저장합니다.";}
   }
   SetText(purpose,f,res,u);
   }
  }
 }
}

