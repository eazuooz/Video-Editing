using UnityEngine;
using UnityEngine.UI;

namespace Yamyam.GameMath.LightLab {
 public sealed partial class LightLabIllustrations {
  [SerializeField] Text[] mathLines;
  [SerializeField] Image[] mathBars;
  [SerializeField] Text mathHeading;
  [SerializeField] string[] mathSteps;
  [SerializeField] string mathMode;
  void BuildMath(Font font){
   mathMode=Cue.diagram.Substring(5);
   result.gameObject.SetActive(false);
   detail.gameObject.SetActive(false);
   mathHeading=Text(font,"",46,1010,265,820,100,Yellow);
   mathLines=new Text[5];
   for(int i=0;i<5;i++)mathLines[i]=Text(font,"",44,1010,370+i*91,820,90,Color.white);
   if(mathMode=="rgb"){
    mathHeading.text="R · G · B는 같은 채널끼리 곱합니다";
    mathSteps=new[]{"광원   (1.0, 0.5, 0.2)","재질   (0.8, 0.4, 0.1)","R: 1.0 × 0.8 = 0.8","G: 0.5 × 0.4 = 0.2","B: 0.2 × 0.1 = 0.02"};
    mathBars=new Image[3];Color[] c={Rose,Green,Cyan};
    for(int i=0;i<3;i++)mathBars[i]=Panel(c[i],980,566+i*76,12,48);
   } else if(mathMode=="reflect"){
    mathHeading.text="법선 성분을 두 배로 → 원래 L을 빼기";
    mathSteps=new[]{"N=(0,1,0),  L=(0.6,0.8,0)","N·L = 0.8","2(N·L)N = (0,1.6,0)","R = (−0.6,0.8,0)","<color=#45DEE6>reflect</color>(−L, N)"};
   } else if(mathMode=="diffuse"){
    mathHeading.text="60°에서 코사인은 0.5";
    mathSteps=new[]{"표면색: (0.8,0.4,0.2)","정면: N·L = 1.0","60°: N·L = 0.5","결과: (0.4,0.2,0.1)","색의 비율은 그대로, 기여는 절반"};
   } else if(mathMode=="nonlinear"){
    mathHeading.text="평균과 제곱의 순서를 바꾸면?";
    mathSteps=new[]{"두 값: 0 과 1","평균 후 제곱: ((0+1)/2)²","결과: 0.25","각각 제곱 후 평균: (0²+1²)/2","결과: 0.50"};
   } else if(mathMode=="factor"){
    mathHeading.text="재질값은 광원의 합 밖으로 묶기";
    mathSteps=new[]{"광원 기여 0.2, 0.3 / 재질 0.8","0.2 × 0.8 + 0.3 × 0.8","= 0.16 + 0.24 = 0.40","(0.2 + 0.3) × 0.8","= 0.5 × 0.8 = 0.40"};
   } else if(mathMode=="units"){
    mathHeading.text="전체 출력과 표면에 도착한 양";
    mathSteps=new[]{"복사속 Φ: 전체 출력 [W]","복사조도 E: 면적당 입사량 [W/m²]","구면 넓이 A = 4πr²","같은 Φ, 거리 r → 2r","넓이 4배 → E는 1/4"};
   } else if(mathMode=="spaces"){
    mathHeading.text="같은 좌표 공간의 방향끼리 비교";
    mathSteps=new[]{"월드 N = (0,1,0)","월드 L = (0,1,0) → N·L = 1","회전된 로컬에서 L = (1,0,0)","다른 공간끼리 내적: 0  ✕","L을 월드로 변환: 1  ✓"};
   } else if(mathMode=="gobo-product"){
    mathHeading.text="두 텍스처에서 읽은 값을 곱하기";
    mathSteps=new[]{"표면 위치 → 광원 좌표","고보: G(x/w, y/w) = 0.8","깊이 감쇠: F(z) = 0.5","G × F = 0.4","이 지점의 광원 기여에 적용"};
   } else if(mathMode=="uv"){
    mathHeading.text="폭 4인 상자를 0…1로 옮기기";
    mathSteps=new[]{"u = x/4 + 0.5","왼쪽 x = −2 → u = 0","중심 x = 0 → u = 0.5","오른쪽 x = 2 → u = 1","월드 → 광원 로컬 → 텍스처"};
   } else if(mathMode=="gloss"){
    mathHeading.text="지수는 반짝임의 폭을 바꿉니다";
    mathSteps=new[]{"정렬된 방향: 1ⁿ = 1","조금 벗어난 방향: R·V = 0.8","0.8² = 0.64","0.8⁸ ≈ 0.17","큰 지수 → 좁은 하이라이트"};
   } else if(mathMode=="half-lambert"){
    mathHeading.text="밝기가 0인 옆면을 읽을 수 있게";
    mathSteps=new[]{"옆면: N·L = 0","Lambert: max(0, 0) = 0","Half Lambert: (0.5×0 + 0.5)²","= 0.25","간접광 계산 대신 응답을 조절"};
   } else if(mathMode=="lambert-brdf"){
    mathHeading.text="반사율 ρ를 전체 방향에 나누기";
    mathSteps=new[]{"ρ: 들어온 빛 중 반사하는 비율","램버트 BRDF: fᵣ = ρ/π","코사인 가중 반구 적분 = π","(ρ/π) × π = ρ","광원 · 재질 · 코사인의 단위를 맞춤"};
   } else if(mathMode=="falloff"){
    mathHeading.text="안쪽 2m · 바깥쪽 6m";
    mathSteps=new[]{"d ≤ 2: 세기 1","d ≥ 6: 세기 0","중간: (6−d)/(6−2)","d=4: (6−4)/4 = 0.5","거리 범위를 직접 제어"};
   } else if(mathMode=="point"){
    mathHeading.text="광원 위치 − 표면 위치";
    mathSteps=new[]{"표면 P / 광원 Q","방향 벡터: Q−P","거리: d = |Q−P|","단위 방향: L = (Q−P)/d","위치 하나에서 모든 방향으로"};
   } else if(mathMode=="gouraud"){
    mathHeading.text="정점에서 계산 → 색을 보간";
    mathSteps=new[]{"세 정점 밝기: 0.2, 0.4, 0.6","중심에서 각각 1/3 비중","(0.2 + 0.4 + 0.6) / 3","= 0.4","최댓값 0.6보다 밝아질 수 없음"};
   } else if(mathMode=="radiometry"){
    mathHeading.text="표면에 들어오는 양과 나가는 양";
    mathSteps=new[]{"복사조도 E: 면적당 입사량","복사발산도 M: 면적당 출사량","라디오시티 B: 반사·발광을 합친 출사량","색 하나에는 방향별 차이가 없음","방향을 남기려면 여러 성분 저장"};
   } else {
    mathHeading.text=Cue.plainMeaning;
    mathSteps=Cue.explanationSteps!=null&&Cue.explanationSteps.Length>0?Cue.explanationSteps:new[]{Cue.formula};
   }
   for(int i=0;i<mathLines.Length;i++)mathLines[i].text=i<mathSteps.Length?mathSteps[i]:"";
  }
  void ApplyMath(float seconds){
   if(mathLines==null||mathSteps==null)return;
   // Preview timing only. Production cues replace these equal phase times
   // with actual spoken sentence onsets before a final capture is authorized.
   float u=Mathf.Clamp01(seconds/Mathf.Max(.01f,Cue.duration));
   int active=Mathf.Min(mathSteps.Length-1,(int)(u*mathSteps.Length));
   if(Cue.stepTimes!=null && Cue.stepTimes.Length>0){active=-1;for(int i=0;i<Cue.stepTimes.Length;i++)if(seconds>=Cue.stepTimes[i])active=i;active=Mathf.Min(active,mathSteps.Length-1);}
   for(int i=0;i<mathLines.Length;i++){
    mathLines[i].gameObject.SetActive(i<mathSteps.Length && i<=active);
    mathLines[i].color=i==active?Yellow:Color.white;
   }
   if(mathMode=="rgb"&&mathBars!=null){
    float[] values={.8f,.2f,.02f};
    for(int i=0;i<3;i++){
     mathBars[i].gameObject.SetActive(active>=i+2);
     mathBars[i].rectTransform.sizeDelta=new Vector2(12+values[i]*80,48);
     mathBars[i].rectTransform.anchoredPosition=new Vector2(870,-(552+i*91));
    }
   }
  }
 }
}
