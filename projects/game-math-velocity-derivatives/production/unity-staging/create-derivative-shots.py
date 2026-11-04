"""Author source-ordered M24 calculations; no invented speech timing or render."""
from pathlib import Path
import copy,hashlib,json
P=Path(__file__).resolve().parent; project=P.parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
script=read(project/'script/narration.ko.json'); draft=read(project/'script/draft-narration.ko.json')
profiles=read(P/'model-profiles.json')['profiles']; base=copy.deepcopy(profiles[0]);base.pop('bindingStatus');base.pop('id')
base.update(timeUnit='s',positionUnit='m',startTime=0,endTime=4,worldOrigin={'x':-7,'y':1,'z':0},worldUnitsPerModelUnit=.65,positionMin=-1,positionMax=10,velocityMin=-3,velocityMax=7)
terms=[
('Actual Game Abstract','움직임에서 변화율로'),('Kinematics','운동학'),('Model Assumptions','모형의 가정'),('Continuous Motion','연속 운동'),('Particle Model','입자 모형'),('Physical Dimensions','물리량과 단위'),('Dimensional Analysis','차원 분석'),('Frequency','진동수'),('Dimensional Analysis','차원 분석'),('Unit Conversion','단위 변환'),('Compound Unit Conversion','복합 단위 변환'),('Position–Time Graph','위치–시간 그래프'),('Average Velocity','평균속도'),('Secant Slope','할선의 기울기'),('Average Speed','평균속력'),('Instantaneous Velocity','순간속도'),('Position Function','위치 함수'),('Difference Quotient','차분 몫'),('Limit and Tangent','극한과 접선'),('Derivative Function','도함수'),('Signed Velocity','부호 있는 속도'),('Rate of Change','변화율'),('Independent Variable','독립변수'),('Signed Rate of Change','변화율의 부호'),('Derivative Definition','미분의 정의'),('Difference Quotient Substitution','차분 몫에 대입'),('Limit Simplification','극한 계산'),('Derivative Evaluation','도함수의 값'),('Differentiability','미분 가능성'),('Integration Constant','적분 상수'),('Derivative Notation','미분 표기'),('Constant Rule','상수 함수의 미분'),('Sum Rule','합의 미분'),('Linearity','선형성'),('Power Rule','거듭제곱 미분법'),('Power Rule Examples','거듭제곱 미분 예제'),('Maclaurin Series','맥클로린 급수'),('Truncation Error','절단 오차'),('Trigonometric Derivatives','삼각함수의 미분'),('Exponential Derivative','지수함수의 미분'),('Proportional Growth','비례 성장'),('Composite Function','합성 함수'),('Chain Rule','연쇄 법칙'),('Chain Rule Units','연쇄 법칙의 단위'),('Nested Sine Functions','사인의 합성함수'),('Nested Exponential Functions','지수함수의 합성'),('Motion and Derivatives','움직임과 미분')]
# Each entry follows the existing paragraph; anchors are exact substrings of
# the narration. Colors distinguish the current result, not decorative text.
content={
1:[('언제 어디에','p(t) → 위치\nv(t) → 위치의 변화율','운동학: 어떻게 움직이는가'),('왜 움직였는지','위치·시간 → 운동학\n힘·질량 → 동역학','이번 단계에서는 위치 하나를 추적합니다')],
2:[('에너지 보존','같은 조건 → 같은 에너지 기준\n오차가 누적되면 운동도 달라짐','모형의 가정과 계산 오차를 구분합니다'),('위치와 시간','p(t) → v(t) → a(t)','먼저 위치에서 변화율로 이어갑니다')],
3:[('연속적으로','연속 모형: p(t)\n프레임 표본: p(0), p(Δt), p(2Δt)','계산 시각 사이에도 수학적 경로는 이어집니다'),('계산 간격','Δt : 컴퓨터의 계산 간격\n수학 모형 ≠ 수치 구현','같은 경로에서 표본을 더 촘촘히 읽습니다')],
4:[('크기와 자세는 없는 점','추적할 정보: 위치 p\n이번에는 제외: 자세·표면 모양','로봇 가운데의 한 점을 추적합니다'),('가로·세로·깊이','p(t) = (x(t), y(t), z(t))','한 성분에서 배운 계산을 각 성분에 적용합니다')],
5:[('미터, 초, 킬로그램','길이 L → m\n시간 T → s\n질량 M → kg','계산 전에 기준 단위를 맞춥니다'),('무게는 중력','질량 m : kg\n무게 W = mg : N','질량은 같아도 중력에 따라 무게가 바뀝니다')],
6:[('제곱미터','넓이: m × m = m²','두 길이를 곱합니다'),('세제곱미터','부피: m × m × m = m³','세 길이를 곱합니다'),('초당 미터','속도: m/s\n가속도: (m/s)/s = m/s²','차원: 속도 L/T, 가속도 L/T²')],
7:[('진동수','1 Hz = 1/s\n1000 Hz = 1 kHz','k는 소문자 · Hz는 진동수 단위'),('힘은','힘: kg·m/s² = N\n에너지: N·m = J\n일률: J/s = W','에너지는 N·m입니다')],
8:[('십육 밀리초','16 ms = 0.016 s\nΔx = v Δt','밀리초를 초로 바꾼 뒤 곱합니다'),('영 점 영사팔','3 m/s × 0.016 s\n= 0.048 m','단위 s가 약분되어 위치 변화 m만 남습니다')],
9:[('삼 점 이팔공팔사','14.57 m × (3.28084 ft / 1 m)','같은 길이를 뜻하는 비를 곱합니다'),('사십칠 점 팔영','14.57 × 3.28084\n≈ 47.80 ft','m이 약분되고 ft가 남습니다')],
10:[('삼천육백 초','188 km/h × (1 h / 3600 s)\n× (1000 m / 1 km)','h와 km를 차례로 약분합니다'),('백칠십일 점 삼삼','× (3.28084 ft / 1 m)\n≈ 171.33 ft/s','같은 빠르기를 다른 단위로 나타냅니다')],
11:[('가로축은 시간','가로축: 시간 t\n세로축: 위치 x(t)','높이는 앞선 정도, 기울기는 움직이는 빠르기'),('가파르다는','기울기 = 세로 변화 / 가로 변화','일찍 앞서 있는 것과 빨리 움직이는 것은 다릅니다')],
12:[('변위입니다','Δx = x₂ − x₁ = 8 − 2 = 6 m\nΔt = t₂ − t₁ = 2 s','Δ는 두 값 사이의 변화를 뜻합니다'),('초속 삼 미터','평균속도 = Δx / Δt\n= 6 m / 2 s = 3 m/s','시작과 끝을 함께 표시합니다')],
13:[('기울기와 같습니다','할선: 두 표본점을 잇는 직선\n기울기 = Δx / Δt','곡선 전체를 한 구간의 평균으로 요약합니다'),('중간에 무슨','같은 두 끝점 → 같은 평균속도','중간 움직임은 별도로 살펴봐야 합니다')],
14:[('앞으로 육 미터','앞으로 6 m → 뒤로 6 m\n이동거리 = 12 m\n변위 = 0 m','왕복 움직임과 정지는 평균속도만으로 구분되지 않습니다'),('평균속력은','평균속력 = 12 / 4 = 3 m/s\n평균속도 = 0 / 4 = 0 m/s','이동거리와 변위를 구분합니다')],
15:[('영 나누기 영','Δt = 0을 먼저 넣으면 0/0','영이 아닌 짧은 구간으로 접근합니다'),('구간을 짧게','Δt를 줄이면 할선이 접선에 접근','실제 차의 계기판과 해설용 함수는 별개입니다')],
16:[('마이너스 티 제곱','x(t) = −t² + 6t − 1\nx(1) = 4,  x(3) = 8','설명 모형의 단위: 분과 펄롱'),('칠 점 칠오','x(2.5) = −6.25 + 15 − 1\n= 7.75 fur','현재 위치에서 조금 뒤의 위치를 비교합니다')],
17:[('영 점 오 분 뒤','h = 0.5 → (8 − 7.75)/0.5 = 0.5','t=2.5분을 고정하고 간격만 줄입니다'),('영 점 일 분','h = 0.1 → 0.09/0.1 = 0.9','분당 펄롱 단위의 평균속도'),('영 점 영일 분','h = 0.01 → 0.99','두 점의 간격이 더 작아집니다'),('영 점 영영일 분','h = 0.001 → 0.999','평균속도는 1에 가까워집니다')],
18:[('수렴값을 극한','h ≠ 0에서 계산한 비율\nh → 0일 때의 수렴값','0으로 나누는 계산이 아닙니다'),('접선의 기울기','v(2.5) = 1 fur/min','접선의 기울기가 순간속도입니다')],
19:[('새 함수를','x(t) = −t² + 6t − 1\nv(t) = x′(t) = −2t + 6','미분 결과는 먼저 함수입니다'),('구체적인 시각','v(2.5) = −5 + 6 = 1','함수에 시각을 넣으면 그 순간의 값이 됩니다')],
20:[('삼 초에','x(t) = 3t − 0.5t²\nv(t) = 3 − t\nv(3) = 0','위치는 양수여도 속도는 0이 될 수 있습니다'),('이동거리는 오','x(4) − x(0) = 4 m\n이동거리 = 4.5 + 0.5 = 5 m','3초 뒤에는 속도가 음수로 바뀝니다')],
21:[('우량계','쌓인 물 높이 h(t)\nh′(t) → 지금 쌓이는 빠르기','변화율은 이동 외의 양에도 적용됩니다'),('온도와 부피가 일정','PV = nRT\nT,V 일정 → P′ ∝ n′','비례 관계에는 조건이 필요합니다')],
22:[('지형의 높이','높이 y = f(x)\nf′(x) > 0 : 오르막\nf′(x) < 0 : 내리막','입력은 시간이 아니라 가로 위치입니다'),('비율은 줄어드니','높이 ↑ → 남은 비율 ↓\n도함수 < 0','매끄럽게 근사한 비율 곡선의 기울기')],
23:[('마이너스 십에서','−10 → −2\n음의 변화율이 0에 가까워짐','값은 증가하지만 감소하는 빠르기는 줄어듭니다'),('한계효용','만족도 U(소득)\nU′ → 추가 소득 한 단위의 효과','설명용 가상 곡선입니다')],
24:[('티 더하기 에이치','평균 변화율\n[x(t+h) − x(t)] / h','h는 두 시각 사이의 간격입니다'),('극한을 현재','x′(t) = lim[h→0]\n              [x(t+h)−x(t)]/h','영이 아닌 간격에서 만든 비율의 극한')],
25:[('전부 티 더하기','x(t+h) = −(t+h)² + 6(t+h) − 1','함수 안의 t를 빠짐없이 바꿉니다'),('위치 전체를','[−(t+h)²+6(t+h)−1]\n−[−t²+6t−1]','두 번째 괄호 전체에 마이너스를 적용합니다')],
26:[('분자에는','−2th − h² + 6h\n= h(−2t − h + 6)','아직 h는 0이 아닙니다'),('약분할 수','h(−2t−h+6) / h\n= −2t − h + 6','h ≠ 0에서 약분합니다'),('마이너스 이 티 더하기','h → 0\nv(t) = −2t + 6','일반 시각에 쓸 속도 함수가 남습니다')],
27:[('이 점 오','v(2.5) = 1','짧은 구간의 수치 계산과 같은 답'),('이 분에서는','v(2)=2,  v(2.4)=1.2\nv(2.6)=0.8,  v(3)=0','시간이 갈수록 접선이 평평해집니다'),('음수가 되면서','t > 3 → v(t) < 0','이제 위치가 줄어드는 방향으로 움직입니다')],
28:[('수평이면','수평: v=0\n오르막: v>0\n내리막: v<0','위치 곡선의 기울기를 읽습니다'),('날카롭게 꺾인','왼쪽 기울기 ≠ 오른쪽 기울기\n→ 그 점에서 미분 불가','왕복 모형의 급격한 방향 전환점을 봅니다')],
29:[('위로 옮겨도','d[x(t)+10]/dt = dx(t)/dt','일정한 위치 차이는 미분하면 사라집니다'),('출발 위치가','속도만으로는 출발 위치를 모름\n위치 복원에는 초기값 필요','다음 적분 강의로 이어지는 정보입니다')],
30:[('디 엑스 디 티','dx/dt = x′(t) = ẋ(t)','같은 시간 미분의 서로 다른 표기'),('분모의 글자','d/dt : 시간 t에 대해 미분\ndy/dx : 입력 x에 대한 y의 변화율','무엇에 대한 변화인지 확인합니다')],
31:[('상수 함수','f(t)=k\nf′(t)=0','수평선의 기울기는 0입니다'),('삼이든 백이든','d(3)/dt=0\nd(100)/dt=0','상수의 크기와 관계없습니다')],
32:[('각각 미분한','x사람,지면 = x기차,지면 + x사람,기차\nv사람,지면 = v기차,지면 + v사람,기차','회전하지 않는 같은 방향의 기준축'),('초속 십 미터','10 m/s + 2 m/s = 12 m/s','뗏목 관찰에서 지면·상대 운동 모형으로 연결')],
33:[('이백일 점 일육팔','x미터 = 201.168 × x펄롱\nv미터 = 201.168 × v펄롱','같은 상수배가 도함수에도 붙습니다'),('선형성','(af + bg)′ = af′ + bg′','합과 상수배를 보존합니다')],
34:[('지수 엔을','d(tⁿ)/dt = n tⁿ⁻¹','지수를 앞으로 곱하고 하나 낮춥니다'),('티의 삼 제곱','d(t³)/dt = 3t²\nd(t²)/dt = 2t','상수 항의 도함수는 0입니다'),('음의 정수','d(t⁻¹)/dt = −t⁻²,  t ≠ 0','함수의 정의역도 확인합니다')],
35:[('삼 티의 오 제곱','d(3t⁵−4t)/dt = 15t⁴−4','각 항에 따로 규칙을 적용합니다'),('티의 백 제곱','d(t¹⁰⁰/100 + √π)/dt\n= t⁹⁹','상수 √π는 사라집니다'),('마이너스 삼 제곱','d(t⁻¹)/dt = −t⁻²\nd(4t⁻³)/dt = −12t⁻⁴','역수는 음의 지수로 바꿔 계산합니다')],
36:[('맥클로린 급수','sin x = x − x³/3! + x⁵/5! − …','x의 단위는 라디안입니다'),('팩토리얼','3! = 1×2×3 = 6\n5! = 1×2×3×4×5 = 120','0 근처에서 항을 차례로 더합니다')],
37:[('앞 네 항','sin x ≈ x − x³/6 + x⁵/120 − x⁷/5040','|x| ≤ 1에서 다음 항으로 오차 상한 확인'),('백만분의 삼','|오차| ≤ 1/9! ≈ 0.00000276','이 입력 범위의 교대급수 오차 상한'),('영 점 오라면','x=0.5 → 0.479425533','설명용 다항 근사와 실제 사인을 비교합니다')],
38:[('각 항을 미분','1 − x²/2! + x⁴/4! − …\n= cos x','사인 급수의 항을 하나씩 미분합니다'),('마이너스 사인','(sin x)′ = cos x\n(cos x)′ = −sin x','각도 단위는 라디안입니다')],
39:[('지수 함수의 급수','eˣ = 1 + x + x²/2! + x³/3! + …','e는 자연상수입니다'),('한 칸씩 앞으로','(eˣ)′ = 1 + x + x²/2! + …\n         = eˣ','미분한 뒤에도 같은 함수가 남습니다')],
40:[('처음 양에','P(t)=P₀ eʳᵗ\nP′(t)=r P(t)','현재 양에 비례하는 연속 성장 모형'),('처음 값을','y′=y → y=C eˣ\ny(0)=C','초기값으로 하나의 함수를 고릅니다')],
41:[('좌표를 에스','t → s(t) → y(s(t))','시간이 경로 좌표를, 경로 좌표가 높이를 바꿉니다'),('합성 함수','바깥 함수 y(s)\n안쪽 함수 s(t)','같은 언덕에서 두 관계를 연결합니다')],
42:[('두 가지가','dy/dt = (dy/ds) × (ds/dt)','경로에 따른 높이 변화 × 경로를 가는 속도'),('절댓값은','s가 경로 길이 좌표이면\n|dy/ds| ≤ 1','경로 길이보다 높이 변화가 클 수 없습니다')],
43:[('영 점 이오','(0.25 m/m) × (4 m/s)\n= 1 m/s','경로 1m마다 높이 0.25m 증가'),('마이너스 일','(0.25 m/m) × (−4 m/s)\n= −1 m/s','뒤로 움직이면 높이 변화의 부호가 바뀝니다')],
44:[('사인 삼 엑스','d[sin(3x)]/dx = cos(3x) × 3','바깥을 미분하고 안쪽 변화율을 곱합니다'),('사인 엑스 제곱','d[sin(x²)]/dx = cos(x²) × 2x','안쪽이 x²이면 변화율은 2x입니다'),('시간 변화율도','d[sin(x(t)²)]/dt\n= cos(x²) × 2x × dx/dt','시간 미분에는 x 자체의 변화율도 필요합니다')],
45:[('코사인 엑스 더하기','d[e^(cos x+3x)]/dx\n= e^(cos x+3x) × (−sin x+3)','지수 안쪽을 빠짐없이 미분합니다'),('사인 삼 엑스 더하기','d[e^(sin 3x+sin x²)]/dx\n= e^(sin 3x+sin x²)\n  × (3cos 3x+2x cos x²)','겹이 늘어나도 같은 연쇄 법칙입니다')],
46:[('두 시점의','두 위치 → 평균속도\n한 점의 접선 → 순간속도\n기울기를 함수로 → 도함수','실제 움직임과 수학적 변화율을 연결했습니다'),('속도 자체가','위치 → 속도 → 가속도\n위치 ← 속도 누적','다음 질문: 속도는 얼마나 빨리 바뀌는가?')]
}
rows=[]
for i,scene in enumerate(script['scenes']):
    if i==0:continue
    model=copy.deepcopy(base);en,ko=terms[i];model.update(beatId=scene['sourceBeatId'],englishTerm=en,koreanTerm=ko,meaning=scene['title'])
    model['showGraphs']=i not in set(range(1,11))|{21,22,23,30,32,33}
    if i==11:model.update(parameters={'kind':16},startTime=0,endTime=6,positionMin=0,positionMax=13,showVelocityGraph=False,showComparison=True,comparisonParameters={'kind':1,'velocity':{'x':2,'y':0,'z':0}},comparisonLabel='노랑: 토끼의 위치\n청록: 거북이의 위치',worldUnitsPerModelUnit=.38)
    if i in {12,13}:model.update(parameters={'kind':1,'origin':{'x':2,'y':0,'z':0},'velocity':{'x':3,'y':0,'z':0}},startTime=0,endTime=2,positionMin=0,positionMax=9,velocityMin=0,velocityMax=4)
    if i in {14,28}:model.update(parameters={'kind':7},startTime=0,endTime=4,positionMin=-1,positionMax=7,velocityMin=-4,velocityMax=4)
    if 15<=i<=19 or 24<=i<=27:model.update(timeUnit='min',positionUnit='fur',startTime=1,endTime=3.5,positionMin=3,positionMax=9,velocityMin=-2,velocityMax=5)
    if i==20:model.update(parameters={'kind':2,'origin':{'x':0,'y':0,'z':0},'velocity':{'x':3,'y':0,'z':0},'acceleration':{'x':-1,'y':0,'z':0}},startTime=0,endTime=4,positionMin=-1,positionMax=5,velocityMin=-2,velocityMax=4)
    if i==31:model.update(parameters={'kind':1,'origin':{'x':3,'y':0,'z':0},'velocity':{'x':0,'y':0,'z':0}},positionMin=0,positionMax=5,velocityMin=-1,velocityMax=1)
    if i in {34,35}:model.update(parameters={'kind':11,'power':3},startTime=.1,endTime=2,positionMin=0,positionMax=9,velocityMin=0,velocityMax=13)
    if 36<=i<=38:model.update(parameters={'kind':8,'amplitude':1,'frequency':1},startTime=-1,endTime=1,positionMin=-1.1,positionMax=1.1,velocityMin=-.1,velocityMax=1.1)
    if i in {39,40}:model.update(parameters={'kind':10,'amplitude':1,'rate':1},startTime=0,endTime=2,positionMin=0,positionMax=8,velocityMin=0,velocityMax=8)
    if 41<=i<=43:model=copy.deepcopy(profiles[1]);model.pop('id');model.pop('bindingStatus');model.update(beatId=scene['sourceBeatId'],englishTerm=en,koreanTerm=ko,meaning=scene['title'])
    if i==44:model.update(parameters={'kind':12},startTime=0,endTime=2,positionMin=-1.1,positionMax=1.1,velocityMin=-4,velocityMax=3)
    if i==45:model.update(parameters={'kind':14},startTime=0,endTime=1.5,positionMin=0,positionMax=5,velocityMin=-6,velocityMax=7)
    if 34<=i<=40 or i in {44,45}:model.update(scalarFunction=True,inputLabel='입력 x',valueLabel='함수',derivativeLabel='도함수',secondDerivativeLabel='이계도함수',timeUnit='rad' if i in range(36,39) else '입력',positionUnit='값',showVelocity=False)
    steps=[];text=' '.join(scene['lines'])
    for j,(anchor,formula,meaning) in enumerate(content[i]):
        if anchor not in text:raise ValueError(f'{i:03}: anchor absent: {anchor}')
        begin=model['startTime']+(model['endTime']-model['startTime'])*j/len(content[i]);end=model['startTime']+(model['endTime']-model['startTime'])*(j+1)/len(content[i])
        h=.5;secant=i in {12,13,15,17,24};tangent=i in {18,19,20,27,28,34,36,38,39,40,44,45}
        if i in {17,18}:begin=end=2.5;h=[.5,.1,.01,.001][min(j,3)]
        if i==16 and j==0:begin=1;end=3
        if i==16 and j==1:begin=end=2.5
        if i==27 and j==0:begin=end=2.5
        if i in {12,13}:begin=end=0;h=2
        item={'anchor':anchor,'formula':formula,'meaning':meaning,'modelFrom':begin,'modelTo':end,'secantH':h,'showSecant':secant,'showTangent':tangent}
        if i in {34,35,44,45}:
            override=copy.deepcopy(model)
            if i==34:
                override.update(parameters={'kind':11,'power':3 if j<2 else -1},startTime=.3,endTime=1.6,positionMin=0,positionMax=5,velocityMin=-12,velocityMax=9)
            elif i==35:
                candidates=[{'kind':15,'powers':[5,1],'coefficients':[3,-4]},{'kind':15,'powers':[100,0],'coefficients':[.01,3.141592653589793**.5]},{'kind':15,'powers':[-1,-3],'coefficients':[1,4]}]
                override.update(parameters=candidates[j],startTime=.8 if j==2 else .2,endTime=1,positionMin=-3 if j==0 else 0,positionMax=10 if j==2 else 3,velocityMin=-34 if j==2 else -5,velocityMax=12)
                if j==2:item['meaning']='그래프: t⁻¹ + 4t⁻³의 합과 도함수'
            elif i==44:override['parameters']={'kind':8,'frequency':3} if j==0 else {'kind':12}
            elif i==45:override.update(parameters={'kind':13 if j==0 else 14},startTime=0,endTime=.6 if j==0 else 1.5,positionMin=0,positionMax=15 if j==0 else 5,velocityMin=0 if j==0 else -6,velocityMax=40 if j==0 else 7)
            item.update(motionOverride=override,modelFrom=override['startTime'],modelTo=override['endTime'])
        steps.append(item)
    diagrams={1:'point-coordinate',2:'point-coordinate',3:'sampled-path',4:'point-coordinate',5:'mass-weight',6:'units',7:'frequency',8:'unit-dimensions',9:'length-conversion',10:'speed-conversion',21:'accumulation',22:'slope',23:'signed-slope',30:'function-flow',32:'relative-motion',33:'function-flow'}
    rows.append({'sourceBeatId':scene['sourceBeatId'],'sceneId':scene['id'],'sourceSection':scene['section'],'sourceScreenPlan':draft['segments'][i]['screenPlan'],'shot':{'beatId':scene['sourceBeatId'],'motion':model,'diagramMode':diagrams.get(i,''),'steps':steps,'durationSeconds':0,'stepSeconds':[],'stepPositions':[]},'status':'source-ordered-calculations-authored-runtime-pending','remainingVisuals':('Complete and inspect concept-specific measurement diagram; generic motion graph deliberately hidden.' if not model.get('showGraphs',True) else 'Inspect plotted numeric range, moving target and actual caption layout.'),'sceneSaved':False})
plan={'episode':'M24','scriptSha256':hashlib.sha256((project/'script/narration.ko.json').read_bytes()).hexdigest(),'sourceOrderPreserved':True,'actualSpeechTiming':False,'runtimeQa':False,'localReviewReady':False,'shots':rows,'limits':['No voice or runtime generated by this authoring step.','Formula boards are editable supporting calculations; concrete diagrams remain required for unit/general-change paragraphs.','A formula-example graph must identify the exact current example when several different functions are discussed.']}
(P/'derivative-shots.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Authored {len(rows)} source-ordered shot configurations; runtime/timing and listed diagrams pending.')
