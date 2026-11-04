"""M26 exact source order: finite circle, exercises, and spoken calculations."""
from pathlib import Path
import copy,hashlib,json,math
P=Path(__file__).resolve().parent;project=P.parent.parent;R=P.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
script=read(project/'script/narration.ko.json');draft=read(project/'script/draft-narration.ko.json')
base=copy.deepcopy(read(R/'projects/game-math-velocity-derivatives/production/unity-staging/model-profiles.json')['profiles'][0]);base.pop('id');base.pop('bindingStatus')
v=lambda x=0,y=0,z=0:dict(x=x,y=y,z=z)
base.update(parameters=dict(kind=4,radius=2,omega=1,axis=v(0,0,1),radiusDirection=v(1)),startTime=0,endTime=math.pi*2,timeUnit='s',positionUnit='m',worldOrigin=v(-5,1.4),worldUnitsPerModelUnit=.65,velocityArrowScale=.45,accelerationArrowScale=.4,positionMin=-2.3,positionMax=2.3,velocityMin=-2.3,velocityMax=2.3,accelerationMin=-2.3,accelerationMax=2.3,showVelocity=True,showAcceleration=True,showRadius=True,showVelocityGraph=True,showAccelerationGraph=True,graphY=False,positiveYIsDown=False,axisConvention='+x 오른쪽 · +y 위 · +z 화면 밖 · 오른손 도식')
terms=[('', ''),('Uniform Circular Motion','등속 원운동'),('Velocity Difference','속도 벡터의 차이'),('Chord and Arc','현과 원호'),('Centripetal Acceleration','구심가속도'),('Speed and Radius','속력과 반지름'),('Angular Velocity','각속도'),('Differentiating Circular Motion','원운동의 미분'),('Period and Frequency','주기와 진동수'),('Earth Rotation Model','지구 자전 모형'),('Rotating Reference Frame','회전 좌표계'),('Angular Velocity Vector','각속도 벡터'),('Cross Product Convention','외적과 좌표 약속'),('Tangential Speed','접선 속력'),('Recovering Angular Velocity','각속도 성분 복원'),('Unobservable Rotation Component','한 점으로 구별할 수 없는 회전'),('Reference Point','기준점'),('Rigid Body Rotation','강체의 회전'),('Pressure Unit Conversion','압력 단위 환산'),('Dimensional Check','차원 검산'),('Piecewise Position','구간별 위치 함수'),('Continuous Position','연속인 위치'),('Average Velocity','평균속도'),('Average across Intervals','여러 구간의 평균속도'),('Piecewise Velocity','구간별 속도 함수'),('Instantaneous Velocity','순간속도'),('Chain Rule Evaluation','연쇄 법칙 값 대입'),('Piecewise Acceleration','구간별 가속도'),('Acceleration Evaluation','가속도 값 대입'),('Discriminant','판별식'),('Projectile Components','발사 속도 성분'),('Projectile Apex','발사체 정점'),('Return to Launch Height','출발 높이로 복귀'),('Vector Projection','벡터 투영'),('Arrival Time Candidates','도착 시간 후보'),('Complex Exponential Series','복소 지수 급수'),('Euler’s Formula','오일러 공식'),('Orbital Radius','궤도 반지름'),('Orbital Period and Acceleration','공전 주기와 구심가속도'),('Motion Models','운동 모형의 연결')]
C={
1:[('한 점만','r: 중심에서 입자까지 거리\ns=|v|: 원을 따라 움직이는 속력','물체의 크기·자체 회전을 제외한 입자 모형'),('서로 수직','v: 접선 방향\nr: 중심에서 입자 방향','r·v=0')],
2:[('같은 출발점','Δv=v₂−v₁','같은 길이여도 방향이 다릅니다'),('서로 닮았습니다','|Δv|/s=|Δr|/r','두 삼각형이 같은 각도로 벌어집니다')],
3:[('현이고','현: 두 점의 직선 거리\n호: 원을 따라간 거리','유한한 각도에서는 현이 더 짧습니다'),('영으로 줄이면','Δt→0일 때 |Δr|/Δt→s','현과 호를 같다고 놓지 않고 극한을 씁니다')],
4:[('극한을 취하면','|a|=lim |Δv|/Δt\n=(s/r)×s=s²/r','속도 벡터 차이를 시간으로 나눕니다'),('정확히 중심 방향','a=−ω²r⃗','구심가속도: 원의 중심을 향하는 가속도')],
5:[('초속 십','s=10 m/s, r=5 m\na=s²/r=20 m/s²','먼저 기본 조건'),('속력을 두 배','s=20 m/s, r=5 m\na=80 m/s²','속력 2배 → 가속도 4배'),('반지름을 두 배','s=10 m/s, r=10 m\na=10 m/s²','속력 고정 · 반지름 2배 → 가속도 절반')],
6:[('알 코사인','p=(r cosθ, r sinθ)\nθ=θ₀+ωt','각속도 ω의 단위는 rad/s'),('절댓값','s=r|ω|','회전 방향에는 부호 · 속력은 음수 아님')],
7:[('오메가를 곱해야','v=(−rω sinθ, rω cosθ)','θ(t)를 미분하는 연쇄 법칙'),('마이너스 오메가 제곱','a=(−rω² cosθ, −rω² sinθ)\n=−ω²r⃗','위치 반지름 벡터와 반대 방향')],
8:[('주기는','T=2πr/s=2π/|ω| [s]','한 바퀴 걸리는 시간'),('진동수는','f=1/T [Hz]\n|ω|=2πf [rad/s]','주기 · 바퀴 수 · 각도를 구별합니다')],
9:[('이십사 시간','R=6,371,000 m\nT=24×3600 s\na=R(2π/T)²≈0.0337 m/s²','24시간은 이 예제의 근삿값'),('수직 거리','원운동 반지름=회전축까지 거리','극으로 갈수록 자전축까지 거리가 줄어듭니다')],
10:[('지면 기준','관성계: 직진하려는 물체\n차·좌석이 안쪽 힘을 줌','한 좌표계 안에서 설명합니다'),('차와 함께 도는','회전계: 바깥쪽 원심 관성력 도입','실제 힘과 좌표계의 관성력을 구별합니다')],
11:[('축 방향 단위','ω⃗=ω n̂','화살표는 진행 방향이 아닌 회전축'),('외적이 접선','v=ω⃗×r⃗','같은 물체의 축·반지름·접선 속도')],
12:[('오른손 좌표계','+z=화면 밖\n(+z)×(+x)=+y','축 라벨과 외적 순서를 같이 확인'),('순서를 바꾸면','r⃗×ω⃗=−(ω⃗×r⃗)','바뀌는 것은 외적 방향입니다')],
13:[('사인이 일이','|ω⃗×r⃗|=|ω⃗||r⃗| sin90°\n=s','축에 수직인 반지름만 기여'),('수직인 성분','r⃗⊥=r⃗−(r⃗·n̂)n̂\nv=ω⃗×r⃗⊥','축 방향 위치 차이는 선속도를 바꾸지 않습니다')],
14:[('길이의 제곱','ω⃗⊥=(r⃗×v)/|r⃗|²\n|r⃗|≠0','분자는 반지름 × 속도 순서'),('속력이 육','r=2, s=6 → |ω|=3\nr=4, s=12 → |ω|=3','분자·분모가 함께 4배')],
15:[('평행한 축','(ω⃗+λr⃗)×r⃗=ω⃗×r⃗','한 점의 속도로 평행 회전 성분 구별 불가'),('수직인 각속도','복원값: r⃗에 수직인 ω⃗ 성분','임의 움직임에서는 접선 성분만 읽습니다')],
16:[('직선 이동','기준점에서 물체를 잇는 시선 r⃗','선속도는 일정해도 시선 방향은 바뀝니다'),('최대가 되고','|ω관측|=|r⃗×v|/|r⃗|²','기준점에 가까이 지날 때 크게 보입니다')],
17:[('축에서 먼 점','같은 ω\nr₁=1 → s₁=|ω|\nr₂=2 → s₂=2|ω|','날개 끝은 더 긴 원을 같은 시간에 돕니다'),('외적을 사용','v점=ω⃗×r⃗점','회전축 위에서 각 점의 원운동 중심을 선택')],
18:[('힘과 면적','1 Pa=1 N/m²\n1 psi=1 lbf/in²','힘과 넓이를 모두 환산합니다'),('제곱합니다','1 psi=4.448221615/0.0254² Pa\n≈6894.757 Pa','길이 환산값은 면적에서 제곱')],
19:[('역수를 취합니다','1 Pa=1/6894.757 psi\n≈0.000145038 psi','앞에서 구한 비율의 역수'),('식의 일부','N/m² → lbf/in²','힘만 또는 길이 한 번만 환산하면 실패')],
20:[('이 초 전까지','0≤t<2: x=2t−t²\n2≤t<4: x=0','현재 시각의 구간부터 고릅니다'),('사 초부터','4≤t<7: x=sin(πt)\nt≥7: x=7−t','하나의 위치 함수를 구간별로 정의')],
21:[('일 초에','x(0)=0 → x(1)=1 → x(2)=0','다음 2초 동안은 위치 0'),('사 점 오','x(4.5)=1, x(5.5)=−1\nx(6.5)=1','사인 곡선을 따라 왕복'),('기울기는 갑자기','x(7)=0 → x(9)=−2\n접합점: 위치 연속 · 속도는 미정의','연속성과 미분 가능성을 구별')],
22:[('영 초부터 일 초','v평균[0,1]=(1−0)/1=1','갈 때'),('일 초부터 이 초','v평균[1,2]=(0−1)/1=−1','돌아올 때'),('전체는','v평균[0,2]=(0−0)/2=0','움직인 거리와 변위는 다릅니다')],
23:[('오 점 오 초','v평균[5.5,6.5]=(1−(−1))/1=2','사인 구간의 두 끝점'),('구 초 전체','v평균[0,9]=(−2−0)/9=−2/9','중간 왕복과 관계없이 양 끝으로 계산')],
24:[('이 빼기 이 티','0<t<2: v=2−2t\n2<t<4: v=0','각 구간 내부에서 미분'),('도함수 파이','4<t<7: v=π cos(πt)\nt>7: v=−1','t=2,4,7에서는 보통 속도 미정의')],
25:[('영 점 일 초','v(0.1)=1.8','위치 곡선이 올라갑니다'),('일 초에서는','v(1)=0','위치 정점'),('일 점 구 초','v(1.9)=−1.8','위치는 양수지만 속도는 음수')],
26:[('사 점 일 초','v(4.1)=π cos(0.1π)≈2.988','라디안과 코사인 주기 확인'),('오 초에서는','v(5)=−π\nv(6.5)=0','같은 사인 위치 곡선의 다른 기울기'),('팔 초와 구 초','v(8)=v(9)=−1','마지막 직선의 일정 기울기')],
27:[('마이너스 이','0<t<2: a=−2\n2<t<4: a=0','속도를 한 번 더 미분'),('파이가 한 번 더','4<t<7: a=−π² sin(πt)\nt>7: a=0','이계 미분에도 연쇄 법칙 적용')],
28:[('모두 마이너스 이','a(0.1)=a(1)=a(1.9)=−2','속도는 달라도 가속도는 같습니다'),('사 점 일 초','a(4.1)≈−3.050','−π² sin(0.1π)'),('오 초에는','a(5)=0, a(6.5)=−π²\na(8)=a(9)=0','v=0과 a=0은 서로 다른 조건')],
29:[('음수라면','D<0 → 실수 시간 없음','도달 가능한 최고 높이보다 높은 목표'),('영이면','D=0 → 겹치는 한 해','포물선 정점에 접하는 목표 높이'),('양수면','D>0 → 두 시간 후보','t≥0 및 다른 좌표도 검사')],
30:[('초속 백오십','p₀=(0,10) ft, s₀=150 ft/s\nθ=40°, g=32 ft/s²','위를 양수 · 각도 단위 확인'),('약 백십사','v₀ₓ=150 cos40°≈114.91\nv₀ᵧ=150 sin40°≈96.42','초기 위치의 높이 10ft를 유지')],
31:[('약 삼 점 영일삼','t정점=v₀ᵧ/32≈3.013 s\nx정점≈346.22 ft','이 시각에 수직 속도=0'),('초기 십 피트','y정점=10+v₀ᵧ²/64\n≈155.26 ft','초기 높이 + 추가 상승 높이')],
32:[('십 피트입니다','도착 높이=10 ft\nT=2t정점≈6.026 s','지면 0ft와 구별'),('약 육백구십이','Δx=v₀ₓT≈692.44 ft','출발·도착 높이가 같을 때의 대칭')],
33:[('양쪽을 가속도','d⃗=v⃗₀t+½a⃗t²\na⃗·d⃗=(a⃗·v⃗₀)t+½|a⃗|²t²','내적하여 스칼라 방정식을 얻습니다'),('영입니다','A=|a⃗|², B=v⃗₀·a⃗, D=d⃗·a⃗\n½At²+Bt−D=0','A·B·D의 단위는 서로 다릅니다')],
34:[('근의 공식','t=(−B±√(B²+2AD))/A\na⃗≠0','가속도 방향을 맞추는 후보 시간'),('원래 벡터','각 t에서 v⃗₀t+½a⃗t²=d⃗ 확인','다른 방향의 목표 위치도 동시에 검사')],
35:[('제곱하면','i²=−1\neⁱˣ=1+ix+(ix)²/2!+…','지수 급수에 ix를 대입'),('거듭제곱','i⁰=1, i¹=i, i²=−1, i³=−i','짝수 항은 실수 · 홀수 항은 허수')],
36:[('실수 항끼리','실수: 1−x²/2!+x⁴/4!−…=cos x\n허수 계수: x−x³/3!+…=sin x','실수와 허수 항을 묶습니다'),('오일러 공식','eⁱˣ=cos x+i sin x','복소평면 단위원 · x는 라디안')],
37:[('삼백사십','r=(6371+340) km\n=6,711,000 m','높이 h와 중심까지 반지름 r 구별'),('초속 약','s=27,740 km/h\n≈7705.56 m/s','문제에서 지정한 원궤도 근삿값')],
38:[('약 오천사백','T=2πr/s≈5472 s\n≈91.2 min','같은 단위로 바꾼 뒤 계산'),('팔 점 팔오','a=s²/r≈8.85 m/s²','함께 자유낙하 · 중력이 0인 것이 아닙니다')],
39:[('속도 벡터 변화','|v| 일정이어도 Δv≠0\na=s²/r, v=ω⃗×r⃗','같은 운동을 극한·미분·외적으로 설명'),('어떤 기준점','물체 → 기준점 → 시간 → 단위\n그다음 식과 화면을 연결','다음 운동 문제에서도 같은 순서')]
}
rows=[]
for scene in script['scenes'][1:]:
 i=int(scene['id']);m=copy.deepcopy(base);diagram=''
 if i in {2,3,4}:m['showGraphs']=False;diagram='circle-difference'
 if i==5:m.update(parameters=dict(kind=4,radius=5,omega=2),endTime=math.pi,worldUnitsPerModelUnit=.35,velocityArrowScale=.08,accelerationArrowScale=.025,showGraphs=False);diagram='circle-values'
 if i==9:m.update(showGraphs=False);diagram='earth-latitude'
 if i==10:m.update(showGraphs=False);diagram='rotating-frame'
 if 11<=i<=15:m.update(showGraphs=False);diagram='rotation-axis'
 if i==11:m.update(displayEuler=v(25,-28),axisConvention='왼쪽: 비스듬한 관찰 시점 · 오른쪽: 정면 기준 도식')
 if i==14:m.update(parameters=dict(kind=4,radius=2,omega=3),endTime=2*math.pi/3,velocityArrowScale=.15,accelerationArrowScale=.05)
 if i==15:m.update(parameters=dict(kind=4,radius=2,omega=3),velocityArrowScale=.25,accelerationArrowScale=.05);diagram='unobserved-axis'
 if i==16:m.update(parameters=dict(kind=1,origin=v(-3,1),velocity=v(1)),endTime=6,showGraphs=False,showAcceleration=False,showRadius=False);diagram='viewpoint-angular'
 if i==17:m['showGraphs']=False;diagram='shared-angular'
 if i in {18,19}:m.update(showGraphs=False,showVelocity=False,showAcceleration=False,showRadius=False);diagram='pressure-units'
 if 20<=i<=28:m.update(parameters={'kind':5},startTime=0,endTime=9,positionMin=-2.3,positionMax=1.3,velocityMin=-3.5,velocityMax=3.5,accelerationMin=-10.5,accelerationMax=10.5,showRadius=False,worldUnitsPerModelUnit=1.4,velocityArrowScale=.45,accelerationArrowScale=.12)
 if i==29:m.update(showGraphs=False,showRadius=False);diagram='arrival-roots'
 if 30<=i<=32:
  vx=150*math.cos(math.radians(40));vy=150*math.sin(math.radians(40));m.update(parameters=dict(kind=2,origin=v(0,10),velocity=v(vx,vy),acceleration=v(0,-32)),endTime=2*vy/32,worldOrigin=v(-8,0),worldUnitsPerModelUnit=.008,velocityArrowScale=.008,accelerationArrowScale=.025,graphY=True,positionMin=0,positionMax=165,velocityMin=-105,velocityMax=105,accelerationMin=-36,accelerationMax=0,showRadius=False,positionUnit='ft')
 if i in {33,34}:m.update(showGraphs=False,showVelocity=False,showAcceleration=False,showRadius=False);diagram='gravity-projection'
 if i in {35,36}:m.update(parameters=dict(kind=4,radius=1,omega=1),worldUnitsPerModelUnit=2,showGraphs=False,showVelocity=False,showAcceleration=False);diagram='complex-unit-circle'
 if i in {37,38}:m.update(showGraphs=False);diagram='orbital-radius'
 m.update(beatId=scene['sourceBeatId'],englishTerm=terms[i][0],koreanTerm=terms[i][1],meaning=scene['title'])
 steps=[];text=' '.join(scene['lines'])
 for j,(anchor,formula,meaning) in enumerate(C[i]):
  assert anchor in text,(i,anchor)
  ov=copy.deepcopy(m);begin=m['startTime']+(m['endTime']-m['startTime'])*j/len(C[i]);end=m['startTime']+(m['endTime']-m['startTime'])*(j+1)/len(C[i]);secant=False;h=.5
  if i==5:ov['parameters']=dict(kind=4,radius=10 if j==2 else 5,omega=[2,4,1][j]);ov['worldUnitsPerModelUnit']=.18 if j==2 else .35;begin=0;end=math.pi/ov['parameters']['omega'];ov['endTime']=end
  if i==14:ov['parameters']=dict(kind=4,radius=2 if j==0 else 4,omega=3);ov['worldUnitsPerModelUnit']=1 if j==0 else .5
  if i==15:begin=end=0
  if i==20:begin=0 if j==0 else 4;end=4 if j==0 else 9
  if i==21:begin=[0,4,7][j];end=[4,7,9][j]
  if i==22:begin=end=[0,1,0][j];h=[1,1,2][j];secant=True
  if i==23:begin=end=5.5 if j==0 else 0;h=1 if j==0 else 9;secant=True
  if i in {24,27}:begin=0 if j==0 else 4;end=4 if j==0 else 9
  if i==25:begin=end=[.1,1,1.9][j]
  if i==26:begin=[4.1,5,8][j];end=[4.1,6.5,9][j]
  if i==28:begin=[.1,4.1,5][j];end=[1.9,4.1,9][j]
  if i==30:begin=0;end=m['endTime']/2
  if i==31:begin=end=m['endTime']/2
  if i==32:begin=m['endTime']/2;end=m['endTime']
  steps.append(dict(anchor=anchor,formula=formula,meaning=meaning,modelFrom=begin,modelTo=end,secantH=h,showSecant=secant,showTangent=25<=i<=28,motionOverride=ov,useMotionOverride=ov is not None))
 rows.append(dict(sourceBeatId=scene['sourceBeatId'],sceneId=scene['id'],sourceSection=scene['section'],sourceScreenPlan=draft['segments'][i]['screenPlan'],shot=dict(beatId=scene['sourceBeatId'],motion=m,diagramMode=diagram,steps=steps,durationSeconds=0,stepSeconds=[],stepPositions=[]),status='source-ordered-calculations-authored-runtime-pending',sceneSaved=False))
out=dict(episode='M26',scriptSha256=hashlib.sha256((project/'script/narration.ko.json').read_bytes()).hexdigest(),sourceOrderPreserved=True,actualSpeechTiming=False,runtimeQa=False,localReviewReady=False,shots=rows,limits=['Runtime diagrams, labels and actual speech bindings pending.','Current model time is a narrated teaching parameter, never real gameplay measurement.'])
(P/'circular-shots.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Authored',len(rows),'M26 configurations; no render or voice started.')
