using System;
using UnityEngine;

namespace Yamyam.PipelineTeaching {
 public sealed partial class PipelineTeachingStage {
  void ApplyExercises(int b,float u){
   if(b==52){kind.text="현재 화면\n학습 경로 해설";string[] books={"Fundamentals of Computer Graphics","Principles of Digital Image Synthesis","Physically Based Rendering","Real-Time Rendering","OpenGL / DirectX 문서"};int i=Step(u,books.Length);Code(C("이론 ↔ 동작하는 구현",Yellow),books[i],i==4?"시맨틱 · 입력 형식 · 상태 확인":"원리를 실제 코드의 선택과 연결");readout.text="기초 → 합성 이론 → 광선 추적 → 실시간 → API";meaning.text="제목과 학습 역할을 소개하며 표지 이미지는 사용하지 않습니다.";return;}
   if(b>=53&&b<=58){ProjectionExercise(b,u);return;}
   if(b==59||b==60){UVExercise(b,u);return;}
   if(b==61||b==62){MaterialExercise(b,u);return;}
   if(b>=63&&b<=67){NormalExercise(b,u);return;}
   if(b==68){int s=Step(u,3);ShowTriangle(u,true);heroMaterial.SetFloat("_Mode",s==0?0:s==1?1:3);readout.text=new[]{"정점: 어디에 놓을까?","깊이: 어느 표면이 앞일까?","셰이더: 어떤 색으로 남길까?"}[s];meaning.text="위치 → 앞뒤 판정 → 표면 색, 하나의 화면으로 이어집니다.";Code(C("위치와 속성 준비",Teal),C("보이는 샘플 판정",Blue),C("재질과 빛으로 색 완성",Yellow));}
  }
  void ProjectionExercise(int b,float u){
   kind.text="현재 화면\n투영 비율 수치 실험";double aspect=b==58?8.0/9:2.0/3;var m=PMatrix.Projection(aspect,60,1,256,false);double sx=m[0,0],sy=m[1,1],fovy=360/Math.PI*Math.Atan(1/sy);
   Vector3 center=new Vector3(3,1.8f,-.5f);float h=3.5f,w=(float)aspect*h;Box(center,w,h,Teal);Path(Muted,center+Vector3.down*h/2,center+Vector3.up*h/2);Tag(center+new Vector3(0,h/2,0),"한 플레이어의 창",White,-160,-80);
   if(b==53){bool wide=Step(u,2)==1;double dar=wide?16.0/9:4.0/3,par=dar/(640.0/480);Box(new Vector3(3,1.8f,-.6f),(float)dar*3.2f,3.2f,Yellow);Code("프레임 버퍼 640 × 480 가정",C("PAR = DAR ÷ (640 / 480)",Teal),wide?"16:9 → 4/3":"4:3 → 1");readout.text=wide?"같은 저장 격자 · 가로로 더 넓은 표시 픽셀":"저장 비율과 표시 비율이 같으면 정사각 픽셀";meaning.text="연습문제의 설정이며 모든 Wii 출력 규격을 뜻하지 않습니다.";}
   else if(b==54){Code(C("A = 320 / 480 = 2/3",Teal),"수평 시야각 = 60°",C("sx = cot(30°) = √3",Yellow),"sy = A × sx = 2√3 / 3");readout.text="가로가 반으로 좁아진 창 · 수평 시야는 60° 유지";meaning.text="sy를 창 비율에 맞춰야 화면이 찌그러지지 않습니다.";}
   else if(b==55||b==58){Code("A = "+N(aspect),"sx = "+N(sx),"sy = A × sx = "+N(sy),C("vertical FOV = "+N(fovy)+"°",Yellow));readout.text="수직 시야각 = 2 × atan(1 / sy)";meaning.text=b==58?"표시 픽셀의 가로 길이까지 반영하면 A = 8/9":"창이 세로로 길어져 수직 방향을 더 넓게 봅니다.";}
   else if(b==56){bool gl=Step(u,2)==0;Code(C(gl?"GL · RH · 앞 −Z":"D3D · LH · 앞 +Z",Teal),gl?"zclip = −257z/255 − 512/255":"zclip = 256z/255 − 256/255",gl?"wclip = −z":"wclip = z",C("이 표시는 열벡터 행렬",Yellow));readout.text="near 1 · far 256 · 가로/세로 확대는 sx, sy";meaning.text="코드가 행벡터라면 여기의 행렬을 전치해 사용합니다.";}
   else if(b==57){bool gl=Step(u,2)==0;PMatrix p=PMatrix.Projection(aspect,60,1,256,gl);double a=PipelineMath.Divide(p.Transform(new P4(0,0,gl?-1:1))).z,d=PipelineMath.Divide(p.Transform(new P4(0,0,gl?-256:256))).z;Code(gl?"z = −1, −256":"z = 1, 256",C("near → z/w = "+N(a),Green),C("far → z/w = "+N(d),Blue),"벡터 관례와 깊이 범위를 함께 표시");readout.text="양 끝을 실제로 대입해 투영행렬을 검산";meaning.text="이 좌표계 선택은 API가 강제하는 유일한 구성은 아닙니다.";}
  }
  void UVExercise(int b,float u){
   int idx=b==59?1:Step(u,6);var uv=PipelineMath.ExerciseUV[idx];currentBuffer.Clear();var p=new[]{new PVertex(new P4(-.88,.88,.4),uv[0],new P3(1,1,1)),new PVertex(new P4(.88,.88,.4),uv[1],new P3(1,1,1)),new PVertex(new P4(.88,-.88,.4),uv[2],new P3(1,1,1)),new PVertex(new P4(-.88,-.88,.4),uv[3],new P3(1,1,1))};var options=new PRasterOptions{shade=(q,n,c)=>PipelineMath.Checker(q)};PipelineMath.Draw(currentBuffer,p,options);Present(currentBuffer);
   string[] rows=new string[4];for(int i=0;i<4;i++)rows[i]=C("v"+i+": ",i==0?Yellow:White)+"("+N(uv[i].x)+", "+N(uv[i].y)+")";Code(rows);readout.text="UV 집합 "+(char)('A'+idx)+" · 직접 그린 비대칭 반복 무늬";meaning.text=b==59?"정수만큼 옮겨도 Repeat에서는 같은 무늬가 됩니다.":"모서리 번호를 유지하며 확대·회전·전단을 확인합니다.";
  }
  void MaterialExercise(int b,float u){
   int idx=b==61?Step(u,3)==0?0:Step(u,3)==1?7:8:Step(u,10);P3 cd=new P3(PipelineMath.Materials[idx,0]/255.0,PipelineMath.Materials[idx,1]/255.0,PipelineMath.Materials[idx,2]/255.0),cs=new P3(PipelineMath.Materials[idx,3]/255.0,PipelineMath.Materials[idx,4]/255.0,PipelineMath.Materials[idx,5]/255.0);int exponent=PipelineMath.Materials[idx,6];
   // Numeric table components are normalized linear coefficients in this controlled demonstration.
   heroMaterial.SetTexture("_BaseMap",Texture2D.whiteTexture);heroMaterial.SetColor("_BaseColor",ColorOf(cd));heroMaterial.SetColor("_SpecColor",ColorOf(cs));heroMaterial.SetFloat("_Exponent",exponent);heroMaterial.SetFloat("_Ambient",0);heroMaterial.SetVector("_LightPosition",new Vector4(-4.6f,3,-3.5f,1));heroMaterial.SetFloat("_LightRange",20);
   currentBuffer.Clear();for(int y=0;y<currentBuffer.height;y++)for(int x=0;x<currentBuffer.width;x++){double px=2*(x+.5)/currentBuffer.width-1,py=2*(y+.5)/currentBuffer.height-1;px*=currentBuffer.width/(double)currentBuffer.height;double z2=1-px*px-py*py;if(z2>=0){P3 n=new P3(px,py,Math.Sqrt(z2));currentBuffer.color[y*currentBuffer.width+x]=PipelineMath.BlinnPhong(n,new P3(-.3,.4,1),new P3(0,0,1),cd,cs,exponent,new P3(.85,.85,.85),new P3());}}Present(currentBuffer);kind.text="현재 화면\n우리 Blinn–Phong 구현";readout.text="재질 "+(char)('A'+idx)+" · 난반사 "+F(cd)+" · 지수 "+exponent;meaning.text="같은 형상과 빛에서 표면색·반사색·범위만 비교합니다.";objectLabel.text="같은 기사 + 수치 확인 표면 · 재질 "+(char)('A'+idx);
   // Keep hero readable; numeric values sit by the controlled sample instead of over the character.
   Tag(new Vector3(1.4f,3.9f,-.5f),"정반사 "+F(cs),Yellow,-20,-20);
  }
  void NormalExercise(int b,float u){
   triangleObject.SetActive(true);triangleMaterial.SetFloat("_Mode",3);Vector3 p=triangleObject.transform.position;kind.text="현재 화면\n노멀 복원 수치 실험";
   if(b==63||b==64){P3[] normals={new P3(-1,0,0),new P3(0,0,1),new P3(.267,-.535,.805),new P3(0,.857,.514)};int i=b==63?Step(u,2):2+Step(u,2);P3 n=normals[i];int r=PipelineMath.Encode(n.x),g=PipelineMath.Encode(n.y),bl=PipelineMath.Encode(n.z);Arrow(p,p+new Vector3((float)n.x,(float)n.y,(float)-n.z)*1.3f,Blue);Code(C("n = "+F(n),Blue),"rgb = round(255 × (n+1) / 2)",C("= ("+r+", "+g+", "+bl+")",Yellow));readout.text="방향 −1..1 → 저장 채널 0..255";meaning.text="반올림한 입력과 8비트 양자화 오차를 구분합니다.";}
   else {int i=b==66?1:b==67?Step(u,4):0;P3 n=PipelineMath.Normal8(PipelineMath.NormalRGB[i,0],PipelineMath.NormalRGB[i,1],PipelineMath.NormalRGB[i,2]);P3 Nn=PipelineMath.NormalN[i].Unit(),T=(PipelineMath.NormalT[i]-Nn*P3.Dot(Nn,PipelineMath.NormalT[i])).Unit(),B=P3.Cross(Nn,T)*PipelineMath.NormalH[i],world=PipelineMath.ToModel(n,PipelineMath.NormalN[i],PipelineMath.NormalT[i],PipelineMath.NormalH[i]);Func<P3,Vector3> f=q=>new Vector3((float)q.x,(float)q.y,(float)-q.z);Arrow(p,p+f(T)*1.1f,Teal);Arrow(p,p+f(B)*1.1f,Green);Arrow(p,p+f(Nn)*1.1f,Blue);Arrow(p,p+f(world)*1.5f,Yellow);
    Code(C("RGB "+PipelineMath.NormalRGB[i,0]+", "+PipelineMath.NormalRGB[i,1]+", "+PipelineMath.NormalRGB[i,2],Teal),"normalize(2 × rgb / 255 − 1)","B = "+PipelineMath.NormalH[i]+" × cross(N, T)",C("n모델 = xT + yB + zN",Yellow));readout.text="예제 "+(char)('A'+i)+" · 모델 법선 "+F(world);meaning.text=b==66?"이 기저에서는 접선 성분 y와 z가 모델 축에서 자리를 바꿉니다.":"반올림된 N·T를 정규화하고 직교화한 뒤 합칩니다.";lastNumericVertices=new[]{T,B,Nn,n,world};
   }
  }
 }
}
