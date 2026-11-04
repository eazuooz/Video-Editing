"""M25 source-ordered visual calculations. Authoring only, no invented timing."""
from pathlib import Path
import copy,hashlib,json,math
P=Path(__file__).resolve().parent; project=P.parent.parent;R=P.parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
script=read(project/'script/narration.ko.json');draft=read(project/'script/draft-narration.ko.json')
base=copy.deepcopy(read(R/'projects/game-math-velocity-derivatives/production/unity-staging/model-profiles.json')['profiles'][0]);base.pop('id');base.pop('bindingStatus')
base.update(startTime=0,endTime=2.4,timeUnit='s',positionUnit='ft',worldOrigin={'x':-5,'y':3.4,'z':0},worldUnitsPerModelUnit=.04,velocityArrowScale=.025,accelerationArrowScale=.04,graphY=True,positiveYIsDown=True,axisConvention='아래쪽 +y · 낙하 예제',parameters={'kind':2,'velocity':{'x':0,'y':0,'z':0},'acceleration':{'x':0,'y':32,'z':0}},showVelocity=True,showAcceleration=True,showVelocityGraph=True,showAccelerationGraph=True,positionMin=0,positionMax=100,velocityMin=0,velocityMax=80,accelerationMin=0,accelerationMax=36)
terms=[('', ''),('Acceleration','가속도'),('Acceleration Units','가속도 단위'),('Constant Acceleration','등가속도 운동'),('Position, Velocity, Acceleration','위치·속도·가속도'),('Discontinuity and Jerk','불연속과 저크'),('Accumulated Displacement','누적 변위'),('Left Riemann Sum','왼쪽 리만 합'),('Refining the Partition','분할 세분화'),('Area under Velocity','속도 그래프 아래의 넓이'),('Initial Conditions','초기 조건'),('Arrival Time','도착 시각'),('Free Fall','자유낙하'),('Required Initial Velocity','필요한 초기 속도'),('Apex and Return Time','정점과 복귀 시각'),('Required Acceleration','필요한 가속도'),('Vector Kinematics','벡터 운동학'),('Full Target Verification','전체 목표 위치 확인'),('Projectile Motion','포물선 운동'),('Apex and Range','정점과 도달 거리'),('Launch Speed and Angle','발사 속력과 각도'),('Range Scaling','도달 거리의 변화'),('Arbitrary Gravity Direction','임의 중력 방향'),('Designed Jump','설계한 점프'),('Integration','적분'),('Riemann Sum','리만 합'),('Definite Integral','정적분'),('Signed Area','부호 있는 넓이'),('Power and Energy','전력과 에너지'),('Rates and Accumulation','변화율과 누적량'),('Antiderivative','원시함수'),('Power Rule for Integration','거듭제곱 적분법'),('Constant of Integration','적분 상수'),('Fundamental Theorem of Calculus','미적분학의 기본 정리'),('Evaluating a Definite Integral','정적분 계산'),('Derivative of an Accumulation','누적 함수의 미분'),('Definite and Indefinite Integrals','정적분과 부정적분'),('Differentiation and Integration','미분과 적분'),('Centripetal Acceleration','구심가속도')]
content={
1:[('시간 변화율','p′(t)=v(t)\nv′(t)=a(t)','가속도는 속도 벡터의 변화율'),('방향만 바뀌어도','|v| 일정이어도 방향이 바뀌면\nΔv ≠ 0 → 가속도 존재','다음 편에서 원운동으로 확장합니다')],
2:[('초당 사 미터씩','a=4 m/s², v₀=0\nv(1)=4 m/s, v(2)=8 m/s','같은 1초마다 속도에 4 m/s가 더해집니다'),('피트 단위로 삼십이','이후 낙하 예제: a=32 ft/s²\n아래 방향을 양수로 정합니다','단위와 좌표 약속을 함께 바꿉니다')],
3:[('아래쪽을 양수','v(t)=v₀+at\nv₀=0, a=32 ft/s²','아래쪽 +y · 공기 저항 없는 모형'),('이 점 사 초','v(2.4)=32×2.4=76.8 ft/s','가속도가 일정할 때 속도는 직선입니다')],
4:[('가속도가 영이면','a=0 → v 일정 → p 직선','위치·속도·가속도를 같은 시각에 읽습니다'),('가속도가 양수면','a>0 → v의 기울기 양수','위치의 기울기도 점점 커집니다'),('음수면 반대로','a<0 → v의 기울기 음수','속도는 감소합니다'),('앞뒤 부호','a=0만으로 극값 판단 불가\na: + → −이면 v의 극대 후보','주변 부호 변화를 함께 확인합니다')],
5:[('수직 점프','속도 v의 순간 점프\n그 시각의 보통 가속도는 정의 불가','점프 양쪽을 연결하지 않습니다'),('가속도만 계단','a: 0 → 2\nv는 연속 · 기울기만 바뀜','가속도의 변화율: 저크 Jerk')],
6:[('속도가 일정하다면','Δp=vΔt','수평인 속도 그래프 아래의 직사각형'),('마지막 속도','76.8×2.4=184.32 ft\n마지막 속도를 처음부터 적용한 과대값','실제 쌓인 양은 이 직사각형보다 작습니다')],
7:[('여섯 구간','Δt=2.4/6=0.4 s\nvᵢ=32(i−1)Δt','각 조각의 왼쪽 끝에서 속도를 읽습니다'),('칠십육 점 팔','Σ vᵢΔt = 76.8 ft\n정확한 변위보다 작은 근삿값','각 조각에서 아직 빠진 작은 삼각형을 봅니다')],
8:[('열두 구간','n=12, Δt=0.2 s\n왼쪽 합=84.48 ft','직사각형 위의 빈틈이 작아집니다'),('스물네 구간','n=24, Δt=0.1 s\n왼쪽 합=88.32 ft','같은 속도 곡선을 더 잘게 나눕니다')],
9:[('밑변은','Δp=½×2.4 s×76.8 ft/s\n=92.16 ft','속도×시간의 단위는 위치 변화입니다'),('일반적인 시간','Δp=½at²\nt가 2배 → Δp가 4배','정지 출발 · 일정 가속도 조건')],
10:[('직사각형이 하나','Δp=v₀t+½at²','초기 속도의 직사각형 + 가속도의 삼각형'),('초기 위치','p(t)=p₀+v₀t+½at²','그래프 넓이는 변위 · 출발 위치는 별도')],
11:[('이차방정식','½at²+v₀t−d=0\nt=(−v₀±√(v₀²+2ad))/a','a≠0, 제곱근 안≥0일 때 실근'),('두 실근','시간 t≥0 확인\n각 성분의 목표 위치도 확인','한 축의 해는 전체 충돌 판정이 아닙니다')],
12:[('천삼백오십삼 피트','d=1353 ft, v₀=0, a=32 ft/s²\nt=√(2d/a)≈9.196 s','아래쪽 양수 · 양의 시간 해'),('그때 속도','v=at≈294.27 ft/s','공기 저항·지형 충돌을 제외한 모형')],
13:[('십이 초 뒤','v₀=d/t−½at\n=1353/12−½×32×12','같은 아래쪽 목표에 더 늦게 도착시키기'),('마이너스 칠십구','v₀=112.75−192\n=−79.25 ft/s','음수이므로 처음에는 위로 던집니다')],
14:[('수직 속도가 영','−79.25+32t=0\nt정점≈2.477 s','위로 가던 속도가 0을 지나 바뀝니다'),('두 해가','t(−79.25+16t)=0\nt=0 또는 약 4.953 s','복귀 속도 +79.25 ft/s · 출발과 반대 부호')],
15:[('나머지에 이를 곱한','a=2(d−v₀t)/t²','초기 속도로 갈 몫을 먼저 뺍니다'),('십오 미터','a=2(15−2×3)/3²\n=2 m/s²','15m 중 6m + 가속도로 9m')],
16:[('벡터로 바꾸고','p⃗(t)=p⃗₀+v⃗₀t+½a⃗t²','x·y·z 각각에 같은 시간 t를 넣습니다'),('한 축의 후보','t 후보 → p⃗(t) 계산\np⃗(t)=목표 벡터인지 확인','벡터 나눗셈이나 벡터 제곱근을 쓰지 않습니다')],
17:[('두 번일 수','y(t)=목표 높이 → 두 시간 후보','높이와 같아지는 두 지점을 표시합니다'),('수평 위치가','x(t)도 목표 x와 같아야 함','같은 높이와 같은 위치는 다릅니다')],
18:[('위쪽을 양수','x(t)=v₀ₓt\ny(t)=v₀ᵧt−½gt²','이제 +y는 위쪽 · aᵧ=−g'),('같은 시간을','vₓ=v₀ₓ, vᵧ=v₀ᵧ−gt','수평·수직이 하나의 시간선을 공유합니다')],
19:[('정점 시간','t정점=v₀ᵧ/g\nH=v₀ᵧ²/(2g)','정점에서는 수직 속도만 0'),('같을 때의 식','T=2v₀ᵧ/g\nR=v₀ₓT','출발·착지 높이가 같을 때')],
20:[('코사인 세타','v₀ₓ=s₀ cosθ\nv₀ᵧ=s₀ sinθ','수평에서 잰 각도 · 직교 성분'),('사인 이 세타','R=s₀² sin(2θ)/g','같은 높이 · 일정한 아래쪽 중력')],
21:[('속력만 두 배','s₀ → 2s₀\n공중 시간 T → 2T\n도달 거리 R → 4R','같은 각도·중력·출발 및 착지 높이'),('높이가 다른 곳','착지 높이 y목표를 위치 식에 대입','경사면 실제 예시는 같은 높이 조건이 아닙니다')],
22:[('단위 벡터','ĝ=a⃗/|a⃗|\nd∥=d⃗·ĝ, v∥=v⃗₀·ĝ','가속도 방향으로 먼저 투영합니다'),('전체 목표 위치','d∥=v∥t+½|a⃗|t²\n후보 t를 전체 벡터 식에 대입','a⃗=0이면 일정 속도 문제로 분리')],
23:[('최고 높이를','H=2 m, T정점=1 s\ng=2H/T정점²=4 m/s²','먼저 원하는 높이와 시간을 정합니다'),('초속 사 미터','v₀ᵧ=2H/T정점=4 m/s\nT왕복=2 s','지구 중력을 복제하지 않은 설계 모형'),('육 미터','v₀ₓ=3 m/s\nR=3×2=6 m','같은 높이의 발판을 6m 간격으로 배치')],
24:[('복잡한 곡선','각 조각: 변화율 × 구간 폭','직선 대신 곡선에도 같은 원리'),('적분이라고','조각 폭 → 0\n변화율의 합 → 누적량','현재 변화율과 누적 변위를 나란히 읽습니다')],
25:[('같은 폭으로','Δx=(b−a)/n\nxᵢ₋₁=a+(i−1)Δx','i=1의 왼쪽 끝은 a'),('직사각형 하나','조각 넓이=f(xᵢ₋₁)Δx','높이와 폭의 단위도 함께 곱합니다')],
26:[('리만 합','Sₙ=Σ[i=1..n] f(xᵢ₋₁)Δx','모든 조각의 부호 있는 넓이'),('정적분으로','∫ₐᵇ f(x) dx = lim[n→∞] Sₙ','수렴 조건 아래 구간 전체의 한 값')],
27:[('왼쪽 끝','왼쪽·오른쪽·가운데 표본','유한 분할에서는 근삿값이 서로 다릅니다'),('오른쪽 끝','표본 위치를 오른쪽 끝으로','곡선과 같은 좌표축에서 비교'),('가운데 중','표본 위치를 가운데로','분할 수와 구간은 그대로 유지'),('함수가 축 아래','∫v dt = 변위\n∫|v| dt = 총 이동 거리','축 아래의 음수 조각은 반대 이동입니다')],
28:[('전력을 시간에','E=∫P(t)dt\nW×s=J','전력은 에너지의 시간 변화율'),('백 와트','P=100 W, Δt=2 s\nE=200 J','같은 100W가 2초 동안 쌓입니다'),('단가를 곱한','비용=∫ P(t)×단가(t) dt','단가의 에너지 단위를 먼저 맞춥니다')],
29:[('천의 길이','천 속도 [m/s] → 길이 [m]','화살표는 공급 속도 · 막대는 누적 길이'),('물의 부피','유량 [L/s] → 부피 [L]','일정 유량의 물이 통에 쌓이는 해설 모형'),('연료량','소모율 [L/s] → 사용량 [L]','잔량과 사용 누적량의 방향을 구별합니다')],
30:[('원시함수','F′(t)=f(t)\nF는 f의 원시함수','미분한 결과에서 그 이전 함수를 찾기'),('초기 위치','a → v₀+at\n→ p₀+v₀t+½at²','되돌릴 때마다 초기 조건이 필요합니다')],
31:[('지수를 하나 올리고','∫tⁿdt=tⁿ⁺¹/(n+1)+C\nn≠−1','미분해서 원래 함수가 되는지 확인'),('로그 티의 절댓값','∫(1/t)dt=ln|t|+C\nt=0을 포함하지 않는 구간','n=−1에는 다른 공식이 필요합니다')],
32:[('삼을 더해도','d(t²+3)/dt=2t\nd(t²+10)/dt=2t','위치가 달라도 속도는 같습니다'),('함수 묶음','∫2t dt=t²+C','초기 위치로 C를 하나 고릅니다')],
33:[('미적분학의 기본 정리','F′=f, f 연속\n∫ₐᵇ f(t)dt=F(b)−F(a)','끝 값에서 시작 값을 뺍니다'),('변위가 됩니다','∫ₐᵇ v(t)dt=p(b)−p(a)','속도 아래 넓이와 위치 차이가 같은 값')],
34:[('일 초부터 삼 초','∫₁³ 2t dt=[t²]₁³\n=9−1=8 m','현재 곡선과 누적 변위의 실제 계산'),('삼십 미터','(9+30)−(1+30)=8 m','같은 출발 위치 차이는 빼면서 사라집니다')],
35:[('끝 시각을 움직여','A(t)=∫ₐᵗ f(u)du','a는 고정 · t는 움직이는 오른쪽 끝'),('현재 함수 값','[A(t+h)−A(t)]/h → f(t)','얇게 더한 넓이를 폭으로 나누면 현재 높이')],
36:[('정적분은','정적분: 고정 구간의 한 누적값\n부정적분: 원시함수의 묶음','부정적분에는 독립적인 상수 C'),('영을 적분하면','∫ₐᵇ 0 dt=0\n∫0 dt=C','시작점을 바꾸는 것만으로 모든 C가 나오지 않음')],
37:[('위치를 미분','p → 미분 → v → 미분 → a','같은 점프를 변화율 방향으로 읽기'),('초기 위치에서','a → 적분+v₀ → v\nv → 적분+p₀ → p','높이와 시간을 정하는 설계에도 같은 관계')],
38:[('방향만 계속','빠르기 일정 · 방향은 변화\n→ 속도 벡터 변화 → 가속도','다음: 원운동의 중심 방향 가속도')]
}
def vector(x=0,y=0,z=0):return dict(x=x,y=y,z=z)
def update(m,**k):m.update(k);return m
def linear(v=3,a=2,end=3):
    m=copy.deepcopy(base);m.update(parameters=dict(kind=2,velocity=vector(v),acceleration=vector(a)),startTime=0,endTime=end,graphY=False,positiveYIsDown=False,axisConvention='오른쪽 +x',worldOrigin=vector(-8,1),worldUnitsPerModelUnit=.32,velocityArrowScale=.15,accelerationArrowScale=.25,positionMin=0,positionMax=20,velocityMin=-3,velocityMax=10,accelerationMin=-3,accelerationMax=5,positionUnit='m');return m
def jump():
    m=linear();m.update(parameters=dict(kind=3,jumpHeight=2,timeToApex=1,horizontalSpeed=3),endTime=2,graphY=True,axisConvention='+x 오른쪽 · +y 위 · aᵧ=−g',worldUnitsPerModelUnit=.8,worldOrigin=vector(-8,0),positionMin=0,positionMax=2.3,velocityMin=-4.5,velocityMax=4.5,accelerationMin=-4.5,accelerationMax=1);return m
def rect(m,n=6,sample=0):m.update(showRiemann=True,riemannFromModel=True,riemannCount=n,riemannSample=sample);return m
rows=[]
for scene in script['scenes'][1:]:
    i=int(scene['id']);m=copy.deepcopy(base);m.update(beatId=scene['sourceBeatId'],englishTerm=terms[i][0],koreanTerm=terms[i][1],meaning=scene['title']);diagram=''
    if i in {1,2,4,5,15}:m=linear()
    if i==15:m=linear(2,2,3)
    if i in {6,7,8,9,10,24,25,26,27,33,34,35}:rect(m)
    if i==10:m['parameters']['velocity']['y']=8;m['positionMax']=120;m['velocityMax']=90
    if i==12:m.update(endTime=math.sqrt(2*1353/32),worldUnitsPerModelUnit=.0035,velocityArrowScale=.006,positionMax=1400,velocityMax=310)
    if i in {13,14}:m.update(endTime=12 if i==13 else 79.25/16,parameters=dict(kind=2,velocity=vector(0,-79.25),acceleration=vector(0,32)),worldUnitsPerModelUnit=.003 if i==13 else .022,worldOrigin=vector(-5,0),positionMin=-110,positionMax=1400 if i==13 else 10,velocityMin=-90,velocityMax=320 if i==13 else 90,velocityArrowScale=.007 if i==13 else .022)
    if 16<=i<=23 or i==37:m=jump()
    if i in {17,20,21,22}:diagram={17:'jump-target',20:'launch-components',21:'range-comparison',22:'gravity-projection'}[i];m['showGraphs']=False
    if i in {24,25,26}:m=rect(linear(),6);m.update(parameters={'kind':15,'powers':[3,1],'coefficients':[1/3,1]},endTime=3,positionMax=13,velocityMax=11,accelerationMax=7)
    if i==27:m=rect(linear(),6);m.update(parameters={'kind':2,'velocity':vector(3),'acceleration':vector(-1)},endTime=4,positionMax=5,velocityMin=-2,velocityMax=4)
    if i in {28,29}:m=linear(100,0,2);m.update(positionMax=220,velocityMax=110,showAccelerationGraph=False,showAcceleration=False,showVelocity=False,worldUnitsPerModelUnit=.02,valueLabel='누적 에너지',derivativeLabel='전력',positionUnit='J',axisConvention='시간에 쌓이는 에너지 · 전력은 에너지의 변화율');rect(m);diagram='flow-accumulation' if i==29 else ''
    if i in {30,31,32,33,34,35,36}:m=linear(0,2,3);m.update(parameters={'kind':15,'powers':[2],'coefficients':[1]},positionMax=11,velocityMin=0,velocityMax=7,showAccelerationGraph=False,showAcceleration=False)
    if i in {33,34,35}:rect(m,12)
    if i==32:m.update(showComparison=True,comparisonParameters={'kind':15,'powers':[2,0],'coefficients':[1,10]},comparisonLabel='노랑: t²+3 · 청록: t²+10',parameters={'kind':15,'powers':[2,0],'coefficients':[1,3]},positionMax=21,showVelocityGraph=False,worldUnitsPerModelUnit=.2)
    if i==34:m.update(startTime=1,endTime=3)
    if i==36:m.update(parameters={'kind':1,'velocity':vector()},positionMin=-1,positionMax=5,velocityMin=-1,velocityMax=1,showComparison=True,comparisonParameters={'kind':1,'origin':vector(3),'velocity':vector()},comparisonLabel='노랑: 0 · 청록: 3\n둘의 도함수는 0',showVelocityGraph=False)
    if i in {1,38}:m=linear();m.update(parameters={'kind':4,'radius':2,'omega':1},endTime=math.pi,worldOrigin=vector(-5,1),worldUnitsPerModelUnit=1,positionMin=-2.3,positionMax=2.3,velocityMin=-2.3,velocityMax=2.3,accelerationMin=-2.3,accelerationMax=2.3,showRadius=True)
    m.update(beatId=scene['sourceBeatId'],englishTerm=terms[i][0],koreanTerm=terms[i][1],meaning=scene['title'])
    steps=[];text=' '.join(scene['lines'])
    for j,(anchor,formula,meaning) in enumerate(content[i]):
        assert anchor in text,(i,anchor)
        ov=copy.deepcopy(m);begin=m['startTime']+(m['endTime']-m['startTime'])*j/len(content[i]);end=m['startTime']+(m['endTime']-m['startTime'])*(j+1)/len(content[i])
        if i==2:
            if j==0:ov.update(parameters={'kind':2,'velocity':vector(),'acceleration':vector(4)},endTime=2,positionMax=9,velocityMax=9)
            else:ov=copy.deepcopy(base)
            begin=ov['startTime'];end=ov['endTime']
        if i==4:
            ov.update(parameters={'kind':2,'velocity':vector(3),'acceleration':vector([0,2,-1,0][j])});begin=0;end=3
        if i==5:
            ov.update(parameters={'kind':7 if j==0 else 17},endTime=4 if j==0 else 2,positionMax=7,velocityMin=-4,velocityMax=5,accelerationMax=3);begin=0;end=ov['endTime']
        if i==6:
            rect(ov,1,1 if j else 0)
            if j==0:ov.update(parameters={'kind':2,'velocity':vector(0,32),'acceleration':vector()},accelerationMin=-1,accelerationMax=1)
        if i==8:rect(ov,12 if j==0 else 24);begin=0;end=2.4
        if i==9:rect(ov,96)
        if i==14:begin=0 if j==0 else 79.25/32;end=79.25/32 if j==0 else 79.25/16
        if i==23:begin=0 if j<2 else 1;end=1 if j<2 else 2
        if i==26:rect(ov,6 if j==0 else 96)
        if i==27:rect(ov,6,[0,1,.5,.5][j]);begin=0;end=4
        if i==31:
            ov.update(parameters={'kind':15,'powers':[3],'coefficients':[1/3]},positionMax=10,velocityMax=10)
            if j==1:ov.update(parameters={'kind':18},startTime=.5,endTime=3,positionMin=-1,positionMax=1.2,velocityMax=2.2)
            begin=ov['startTime'];end=ov['endTime']
        if i==34 and j==1:ov['parameters']={'kind':15,'powers':[2,0],'coefficients':[1,30]};ov.update(positionMin=30,positionMax=40,worldOrigin=vector(-8,1),worldUnitsPerModelUnit=.12);begin=1;end=3
        if i==35:ov.update(endTime=3,riemannMovingEnd=True,riemannCount=24);begin=.1 if j==0 else 2;end=2 if j==0 else 3
        ov.update(beatId=m['beatId'],englishTerm=m['englishTerm'],koreanTerm=m['koreanTerm'],meaning=m['meaning'])
        steps.append(dict(anchor=anchor,formula=formula,meaning=meaning,modelFrom=begin,modelTo=end,secantH=.1,showSecant=False,showTangent=False,motionOverride=ov,useMotionOverride=ov is not None))
    rows.append({'sourceBeatId':scene['sourceBeatId'],'sceneId':scene['id'],'sourceSection':scene['section'],'sourceScreenPlan':draft['segments'][i]['screenPlan'],'shot':dict(beatId=scene['sourceBeatId'],motion=m,diagramMode=diagram,steps=steps,durationSeconds=0,stepSeconds=[],stepPositions=[]),'status':'source-ordered-calculations-authored-runtime-pending','sceneSaved':False})
out=dict(episode='M25',scriptSha256=hashlib.sha256((project/'script/narration.ko.json').read_bytes()).hexdigest(),sourceOrderPreserved=True,actualSpeechTiming=False,runtimeQa=False,localReviewReady=False,shots=rows,limits=['Runtime/layout, full canonical-source QA and actual speech bindings remain pending.','Analytic model values never purport to be measured commercial-game data.'])
(P/'integration-shots.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Authored',len(rows),'source-ordered M25 configurations; no voice or render started.')
