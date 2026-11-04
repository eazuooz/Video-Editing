"""M28 full ordered source-beat animations, before measured speech timing."""
from pathlib import Path
import json,copy,math,hashlib
S=Path(__file__).resolve().parent;P=S.parents[1]
script=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8-sig'))
base=dict(mass=1,k=16,c=0,x0=1,v0=0,timeStart=0,timeEnd=3,worldScale=1.6,forceScale=.06,subjectKind='box',secondaryKind='box',showEquation=True,showSupport=False,gravity=0)
def m(anchor,formula,meaning,picture=6,**kw):
 model=copy.deepcopy(base);model.update(picture=picture,**kw);return dict(anchor=anchor,formula=formula,meaning=meaning,model=model)
C={
1:('Spring and Rest Length','용수철과 정지 길이',[
 m('한쪽 끝을 고정','x = 현재 길이 − 정지 길이','정지 길이에서의 위치를 x=0으로 정의',x0=1,timeEnd=.3),
 m('눌러 짧게','x<0 → F>0','누르면 반대로 밀어내는 복원력',x0=-1,timeEnd=.3)]),
2:('Hooke’s Law','훅의 법칙',[
 m('벗어난 만큼','F = −k x','변형과 반대 방향 · k 단위 N/m',k=20,x0=.2,timeEnd=.05),
 m('영점일 미터','k=20 N/m, x=0.1 m\nF=−2 N','탄성 한계 안의 선형 모형',k=20,x0=.1,timeEnd=.01,worldScale=5)]),
3:('Spring Acceleration','복원 가속도',[
 m('마이너스 케이 엑스','F = −k x\na = −(k/m)x','F를 m으로 나누어 가속도',14,k=4,mass=1),
 m('무거운 물체','같은 k=4: m=4 → K=k/m=1','같은 힘 · 더 작은 가속도',14,k=4,mass=4)]),
4:('Differential Equation','미분방정식',[
 m('미분인 속도','x → v=dx/dt → a=d²x/dt²','세 그래프가 같은 시각을 가리킵니다',14,k=4),
 m('두 번 미분','x″ = −Kx','후보를 미분해 원래 관계에 대입',14,k=4)]),
5:('Cosine Candidate','코사인 후보 검산',[
 m('코사인 티','x=cos t\nx′=−sin t','위치에서 첫 번째 미분',14,k=1,timeEnd=6.28),
 m('두 번이면','x″=−cos t=−x','K=1인 특별한 경우',14,k=1,timeEnd=6.28)]),
6:('Natural Angular Frequency','고유 각진동수',[
 m('시간축을 바꿉니다','x=cos(√K t)','시간축의 배율 변화',14,k=1),
 m('루트 케이가 두 번','x″=−Kcos(√K t)=−Kx','연쇄 법칙의 √K가 두 번 등장',14,k=4),
 m('각진동수','ω₀=√(k/m)','단위 rad/s · 같은 질량과 초기 위치',14,k=16)]),
7:('Amplitude and Phase','진폭과 위상',[
 m('최대한 당긴','x=Acos(ωt+φ₀)\nx₀=1, v₀=0','끝에서 정지 상태로 출발',15,k=4),
 m('중간에서 이미','x₀=0, v₀=2\nA=1, φ₀=−π/2','중간에서 오른쪽으로 출발',15,k=4,x0=0,v0=2)]),
8:('Initial Conditions','초기 위치와 속도',[
 m('처음에 오른쪽','ω=2, x₀=0, v₀=+2\nA=1, φ₀=−π/2','처음 속도가 출발 방향을 결정',15,k=4,x0=0,v0=2,timeEnd=1),
 m('속도를 반대로','ω=2, x₀=0, v₀=−2\nA=1, φ₀=+π/2','같은 진폭 · 반대 출발 방향',15,k=4,x0=0,v0=-2,timeEnd=1),
 m('위치와 속도가 모두 영','x₀=0, v₀=0 → 정지','진폭이 0이면 위상 의미 없음',15,k=4,x0=0,v0=0)]),
9:('Frequency in Hertz','헤르츠와 각진동수',[
 m('헤르츠는','f=ω/(2π)','한 왕복: 2π rad',15,k=4),
 m('상수를 네 배','k: 4→16 → ω: 2→4','질량 고정 · 진동수 두 배',15,k=16),
 m('질량을 네 배','m: 1→4 → ω: 4→2','k=16 고정 · 진동수 절반',15,k=16,mass=4),
 m('진폭만 커집니다','x₀: 1→2 · ω=2 유지','선형 탄성 모형의 진폭 독립성',15,k=16,mass=4,x0=2,worldScale=1.1)]),
10:('Viscous Damping','점성 감쇠',[
 m('영원히 왕복','c=0: 에너지 일정','복원력만 있는 이상적 모형'),
 m('속도에 비례','F_d = −cv','속도와 반대 방향 · 크기는 속도에 비례',c=4)]),
11:('Spring and Damper Forces','복원력과 감쇠력',[
 m('알짜힘','ΣF=−kx−cv\na=ΣF/m','위치와 속도에 따라 두 화살표의 방향 변화',c=4),
 m('평형점을 지날','x=0 → F_s=0\nv≠0 → F_d≠0','평형점에서도 속도가 남을 수 있습니다',c=4,x0=0,v0=4,timeEnd=.5)]),
12:('Damping Ratio','감쇠비',[
 m('이 곱하기','ω₀=√(k/m)\nζ=c/(2mω₀)','c의 단위와 무차원 비율 ζ는 다릅니다',c=4),
 m('질량 일','m=1, k=16, c=4\nω₀=4, ζ=0.5','x″=−ω₀²x−2ζω₀x′',c=4)]),
13:('Underdamping','부족 감쇠',[
 m('영보다 크고 일보다','0<ζ<1\nx=e^(−ζω₀t)(Acosω_dt+Bsinω_dt)','작아지는 진폭과 반복 왕복',c=4),
 m('실제 각진동수','ω_d=ω₀√(1−ζ²)\nω₀=4, ζ=.5 → ω_d≈3.464','두 상수는 초기 위치와 속도로 결정',c=4),
 m('영으로 놓으면','ζ=0 → e⁰=1','감쇠 없는 같은 모형으로 연결',c=0)]),
14:('Critical and Overdamping','임계 감쇠와 과감쇠',[
 m('임계 감쇠','ζ=1\nx=(A+Bt)e^(−ω₀t)','초기 x=1, v=0인 동일 조건 비교',7,c=4),
 m('과감쇠','ζ>1: 두 감소 지수의 합','같은 초기 정지 조건: 과감쇠가 더 늦게 복귀',7,c=4)]),
15:('Critical Damping and Overshoot','임계 감쇠의 초기 조건',[
 m('초기 속도','x₀=1, v₀=−10, ω₀=4\nx=(1−6t)e^(−4t)','반복 진동 없음 ≠ 모든 초기 속도에서 통과 없음',c=8,x0=1,v0=-10,timeEnd=.5),
 m('육분의 일 초','t=1/6 s → x=0\nt>1/6 s → x<0','이 초기 조건에서는 목표를 한 번 통과',c=8,x0=1,v0=-10,timeStart=.16,timeEnd=.5)]),
16:('Setpoint and Output','설정값과 출력',[
 m('목표값이 될 수','target=1 · value=0','초록 선: 목표 · 물체: 출력',8,c=4,x0=0,target=1,dt=.02,worldScale=3),
 m('둘의 차이','error=value−target','목표 자체를 힘으로 취급하지 않습니다',16,c=4,x0=0,target=1,codeStage=0,worldScale=3)]),
17:('PD Controller','비례·미분 제어',[
 m('오차에 비례','a=−K(value−target)−Cvelocity','복원 P · 속도에 대한 감쇠 D',8,c=4,x0=0,target=1,dt=.02,worldScale=3),
 m('적분 항','PID의 I: 시간에 따른 오차 누적','여기서 구현하는 것은 P와 D 두 항입니다',16,c=4,x0=0,target=1,codeStage=1,worldScale=3)]),
18:('Controller State','제어기의 상태',[
 m('현재 값','value, target, velocity','한 프레임에서 사용할 세 상태',16,c=4,x0=0,target=1,codeStage=0,worldScale=3),
 m('가속도를 만듭니다','a=−Kerror−Cvelocity','질량을 K,C에 흡수한 구현',16,c=4,x0=0,target=1,codeStage=1,worldScale=3)]),
19:('Semi-Implicit Euler','반암시적 오일러 방법',[
 m('가속도에','a=16, Δt=.1','오차 −1 → 가속도 16',16,c=4,x0=0,target=1,codeStage=1,dt=.1,worldScale=3),
 m('새 속도 일점육','v_new=0+16×.1=1.6','속도를 먼저 갱신',16,c=4,x0=0,target=1,codeStage=2,dt=.1,worldScale=3),
 m('새 위치 영점일육','x_new=0+1.6×.1=.16','새 속도로 위치 갱신',16,c=4,x0=0,target=1,codeStage=3,dt=.1,worldScale=3)]),
20:('Response Parameters','반응의 조절 값',[
 m('케이가 오메가','K=ω₀², C=2ζω₀','질량을 흡수한 계수',8,k=4,c=4,x0=0,target=1,dt=.02,worldScale=3),
 m('큰 값은 빠르게','ζ=1, ω₀=4 → K=16,C=8','반복 진동 없이 더 빠른 반응',8,k=16,c=8,x0=0,target=1,dt=.02,worldScale=3)]),
21:('Time-Step Stability','시간 간격과 수치 안정성',[
 m('어떤 계산 간격','같은 K=16,C=4 · 다른 Δt','두 선은 같은 연속 시간 조건을 수치 적분',17,c=4,x0=0,target=1,timeEnd=2),
 m('여러 시간 간격','Δt=.05 s ↔ Δt=.5 s','그래프 범위 밖의 값도 숫자로 표시',17,c=4,x0=0,target=1,timeEnd=2)]),
22:('First-Order Lag','일차 지연',[
 m('일차 지연','value=target+(old−target)e^(−λΔt)','목표가 구간 동안 고정된 경우의 정확한 해',9,x0=0,target=1,lambda_=2,timeEnd=2,worldScale=3),
 m('반 초 뒤','1−e^(−2×.5)≈.632','λ=2, target=1, old=0, Δt=.5s',9,x0=0,target=1,lambda_=2,timeEnd=.5,worldScale=3)]),
23:('Choosing the Response','반응 모형의 선택',[
 m('일정한 속도','같은 목표·시간 · 서로 다른 상태 모형','용수철 · 일차 지연 · 일정 속도',18,c=4,x0=0,target=1,lambda_=2,worldScale=2.5),
 m('관성을 남겨야','속도 상태 유지 여부를 기준으로 선택','목표를 따라가는 방식의 차이를 직접 비교',18,c=4,x0=0,target=1,lambda_=2,worldScale=2.5)]),
24:('Restoration and Damping','되돌림과 가라앉힘',[
 m('두 역할','F복원=−kx\nF감쇠=−cv','위치와 속도라는 서로 다른 원인',c=4),
 m('다음에는 힘이','계속 작용하는 힘 → 짧은 충격','다음 질문: 힘과 충격량의 관계',c=4)])}
rows=[]
for scene in script['scenes']:
 sid=int(scene['id'])
 if sid==0:continue
 english,korean,steps=C[sid]
 for step in steps:
  assert step['anchor'] in ''.join(scene['lines']),(sid,step['anchor'])
  model=step['model'];model.update(id=scene['id'],english=english,korean=korean,meaning=step['meaning'],equation=step['formula'],condition=step['meaning'])
  if 'lambda_' in model:model['lambda']=model.pop('lambda_')
 rows.append(dict(sceneId=scene['id'],sourceBeatId=scene['sourceBeatId'],shot=dict(beatId=scene['sourceBeatId'],durationSeconds=0,stepSeconds=[],stepPositions=[],steps=steps),actualSpeechTiming=False))
out=dict(project='game-math-springs-damping',scriptSha256=hashlib.sha256((P/'script/narration.ko.json').read_bytes()).hexdigest(),shots=rows,sourceOrderPreserved=True,runtimeReviewed=False)
(S/'spring-shots.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Prepared',len(rows),'source-ordered spring scenes')
