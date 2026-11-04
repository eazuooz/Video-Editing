"""Source-ordered M27 model cases; not actual speech timing or runtime approval."""
from pathlib import Path
import copy,hashlib,json,math
S=Path(__file__).resolve().parent;P=S.parents[1]
script=json.loads((P/'script/narration.ko.json').read_text(encoding='utf-8'))
base=dict(id='UNBOUND',mass=2,gravity=9.8,forceX=6,opposingForce=2,muStatic=.5,muKinetic=.3,timeStart=0,timeEnd=2,initialVelocity=0,worldScale=.35,forceScale=.12,velocityScale=.3,accelerationScale=.15,showSupport=True,showFriction=False,showNet=True,showVelocity=True,showAcceleration=True,showEquation=True,subjectKind='box',secondaryKind='box')
def step(anchor,formula,meaning,picture=0,**kw):return dict(anchor=anchor,formula=formula,meaning=meaning,model=dict(base,picture=picture,**kw))
def m(anchor,formula,meaning,picture=0,**kw):
 d=copy.deepcopy(base);d.update(picture=picture,**kw);return dict(anchor=anchor,formula=formula,meaning=meaning,model=d)
content={
1:('Newtonian Mechanics','뉴턴 역학',[
 m('무엇이 그 변화','ΣF → a → v → p','원인을 더해 움직임을 계산합니다',10,forceX=4,opposingForce=0),
 m('질량이 일정','ΣF = ma','일상적 크기·속도 · 일정한 질량 · 관성 기준계',10,forceX=4,opposingForce=0)]),
2:('Inertia','관성',[
 m('질량은','같은 F: m ↑ → a ↓','질량은 가속에 대한 관성을 나타냅니다',10,forceX=4,opposingForce=0,mass=2),
 m('알짜힘이 없으면','ΣF=0 → a=0 → v 일정','정지하거나 등속 직선 운동합니다',10,forceX=0,opposingForce=0,initialVelocity=3,worldScale=.55)]),
3:('Friction and Inertia','마찰과 관성',[
 m('같은 속도로','v₀ = 4 m/s · a마찰 = −0.5 m/s²','매끄러운 바닥 · 같은 출발 속도',1,initialVelocity=4,slideDeceleration=.5,worldScale=.45),
 m('거친 바닥','v₀ = 4 m/s · a마찰 = −2 m/s²','거친 바닥 · 더 빨리 멈춤',1,initialVelocity=4,slideDeceleration=2,worldScale=.45)]),
4:('Newton’s Second Law','뉴턴의 제2법칙',[
 m('알짜힘이 질량','F=4 N, m=2 kg → a=2 m/s²','알짜힘과 가속도는 같은 방향',10,forceX=4,opposingForce=0),
 m('힘이 두 배','F=8 N, m=2 kg → a=4 m/s²','질량 고정 · 힘만 두 배',10,forceX=8,opposingForce=0),
 m('질량이 두 배','F=8 N, m=4 kg → a=2 m/s²','힘 고정 · 질량만 두 배',10,forceX=8,opposingForce=0,mass=4)]),
5:('Net Force','알짜힘',[
 m('반대 방향으로 지탱','ΣF_y = N − mg = 0','힘이 존재해도 합이 0이면 가속하지 않습니다',forceX=0,opposingForce=0),
 m('오른쪽 육 뉴턴','ΣF_x = +6 − 2 = +4 N','방향 부호를 포함해 더합니다',forceX=6,opposingForce=2)]),
6:('Newton and Vector Force','뉴턴 · 힘 벡터',[
 m('일 뉴턴','1 N = 1 kg·m/s²','질량 1kg의 가속도를 1m/s²로 만드는 힘',10,mass=1,forceX=1,opposingForce=0),
 m('각 방향에','F⃗ = m a⃗\nFₓ=maₓ, Fᵧ=maᵧ, F_z=ma_z','힘·가속도는 벡터 · 질량은 스칼라',forceX=6,opposingForce=2)]),
7:('Acceleration Time','속도를 바꾸는 시간',[
 m('이 초라면','a=(4−0)/2=2 m/s²\nF=2×2=4 N','2초 동안 가속해 4m/s 도달',10,forceX=4,opposingForce=0,timeEnd=2),
 m('한 초라면','a=(4−0)/1=4 m/s²\nF=2×4=8 N','1초 동안 같은 속도에 도달',10,forceX=8,opposingForce=0,timeEnd=1)]),
8:('Free-Body Diagram','자유 물체도',[
 m('힘마다 이름','선택한 물체가 받는 힘만 표시','중력 · 수직항력 · 미는 힘 · 반대 힘'),
 m('질량으로 나누어','a = ΣF/m = 4/2 = 2 m/s²','방향까지 합친 뒤 질량으로 나눕니다'),
 m('속도와 위치','v ← v + aΔt\np ← p + vΔt','이 식은 반암시적 오일러 갱신의 예입니다',10,forceX=4,opposingForce=0)]),
9:('Inertial Reference Frame','관성 기준계',[
 m('기준으로 움직임','a상대 = a물체 − a기준계','기준계의 가속도도 구분합니다',12,subjectKind='robot',secondaryKind='sandwich',bodyLabel='관찰자',otherLabel='낙하 물체',frameAcceleration=0,timeEnd=.65,worldScale=.8),
 m('가상의 힘','가속 기준: F가상 = −m a기준계','관성계에서는 가상 힘 없이 뉴턴 법칙 적용',12,subjectKind='robot',secondaryKind='sandwich',bodyLabel='관찰자',otherLabel='낙하 물체',frameAcceleration=-9.8,showObserverFrame=True,timeEnd=.65,worldScale=.8)]),
10:('Free-Fall Frame','자유 낙하 기준계',[
 m('함께 자유 낙하','a엘리베이터 = a샌드위치 = −g','지면에서 보면 함께 낙하합니다',12,subjectKind='robot',secondaryKind='sandwich',bodyLabel='로봇',otherLabel='샌드위치',frameAcceleration=-9.8,timeEnd=.65,worldScale=.8),
 m('서로의 위치','a상대 = −g − (−g) = 0','같이 내려가는 기준에서는 상대 위치 유지',12,subjectKind='robot',secondaryKind='sandwich',bodyLabel='로봇',otherLabel='샌드위치',frameAcceleration=-9.8,timeEnd=.65,worldScale=.8,showObserverFrame=True)]),
11:('Galilean Reference Frames','등속 이동 기준계',[
 m('지면에서 보면','x=0, y=−½gt²','지면 기준에서는 수직 낙하',12,frameVelocity=3,subjectKind='robot',secondaryKind='sandwich',timeEnd=.7,worldScale=.7),
 m('포물선처럼','x상대=−v기준t\ny상대=−½gt²','일정한 속도 차이 · 가속도는 그대로',12,frameVelocity=3,showObserverFrame=True,subjectKind='robot',secondaryKind='sandwich',timeEnd=.7,worldScale=.7)]),
12:('Action and Reaction','작용·반작용',[
 m('에이가 비를','F_A←B = −F_B←A','서로 다른 물체가 받는 같은 크기의 힘',11,forceX=4,mass=4,secondaryMass=2,bodyLabel='A',otherLabel='B',timeEnd=1.2),
 m('동시에 서로 다른','두 힘은 동시에 작용\n각 물체에서 따로 합산','같은 힘이어도 질량에 따라 가속도는 다름',11,forceX=4,mass=4,secondaryMass=2,bodyLabel='A',otherLabel='B',timeEnd=1.2)]),
13:('Contact Force Pair','접촉력의 짝',[
 m('책에는','책: N위 − mg아래 = 0','책의 자유 물체도 · 지구와 책상이 미는 힘',subjectKind='book',forceX=0,opposingForce=0,mass=1),
 m('책상 쪽 그림','F책←책상 = −F책상←책','반작용은 책상이 받습니다 · 같은 합에 넣지 않음',subjectKind='book',forceX=0,opposingForce=0,mass=1)]),
14:('External Support','지면의 버팀',[
 m('같은 힘으로','상자와 사람의 접촉력은 크기가 같습니다','미끄러운 지면에서 두 물체만 비교',11,subjectKind='robot',secondaryKind='box',bodyLabel='사람',otherLabel='두 배 질량 상자',forceX=4,mass=2,secondaryMass=4,timeEnd=1.2),
 m('땅에서 받는 힘','사람의 ΣF = F지면 − F상자','예: 6−4=2 N → 앞쪽 가속',10,subjectKind='robot',forceX=6,opposingForce=4,mass=2,worldScale=.6)]),
15:('Internal and External Forces','내력과 외력',[
 m('내부 힘은','F_A←B + F_B←A = 0','계 전체에서 내력은 쌍으로 상쇄됩니다',11,forceX=4,mass=2,secondaryMass=4,timeEnd=1),
 m('질량중심','M a_CM = ΣF외력','회색 선: 외력 없는 계의 고정 질량중심',11,forceX=4,mass=2,secondaryMass=4,timeEnd=1.5)]),
16:('Normal Contact Force','수직항력',[
 m('바닥을 뚫고','바닥이 물체를 받칩니다','접촉면의 수직 방향 성분',forceX=0,opposingForce=0),
 m('중력과 마찰','ΣF = F중력 + F접촉 + F외부','법선 방향과 접선 방향을 나눕니다',forceX=3,opposingForce=0,showFriction=True)]),
17:('Universal Gravitation','만유인력',[
 m('거리의 제곱','F=Gm₁m₂/r²','점질량 또는 구대칭 분포 근사',3,gravityMassA=3,gravityMassB=5,gravityDistance=1,worldScale=1.2),
 m('거리를 두 배','r → 2r\nF → F/4','거리만 두 배 · 두 힘은 서로를 향함',3,gravityMassA=3,gravityMassB=5,gravityDistance=2,worldScale=1.2)]),
18:('Uniform Gravity','일정한 중력 가속도',[
 m('질량에 일정한','F중력 = m g⃗','지표 가까운 작은 공간 · 일정한 아래 방향',5,timeEnd=.7,worldScale=.7),
 m('가속도는 지 자체','a⃗ = (m g⃗)/m = g⃗','공기 저항을 뺀 비교 · 질량과 무관한 g',5,timeEnd=.7,worldScale=.7)]),
19:('Standard Gravity','표준 중력',[
 m('약 구점팔삼','GM/R² ≈ 9.83 m/s²','질량·평균 반지름을 넣은 구형 근사',5,gravity=9.83,timeEnd=.7,worldScale=.7),
 m('정확한 값은','구형 근사 − 자전 ≈ 9.796\n실제: 적도 약 9.78, 극 약 9.83','편평한 실제 지구와 단순 구형 모형은 다릅니다',5,gravity=9.796,timeEnd=.7,worldScale=.7),
 m('표준 중력','g₀ = 9.80665 m/s²','정의된 관례값 · 모든 장소의 실측값이 아님',5,gravity=9.80665,timeEnd=.7,worldScale=.7)]),
20:('Jump Design','점프 설계',[
 m('일정한 중력','y = v₀t − ½gt²','같은 높이 H=2m · 지구 중력 기준',4,jumpHeight=2,apexSeconds=math.sqrt(4/9.8),timeEnd=2*math.sqrt(4/9.8),worldScale=1),
 m('공중에 머무는','같은 H=2m · 정점까지 0.4s','모형 중력을 키워 빠르게 올라갔다 내려옵니다',4,jumpHeight=2,apexSeconds=.4,timeEnd=.8,worldScale=1)]),
21:('Perceived Weight','움직임의 무게감',[
 m('낙하를 빠르게','높이 일정 · 짧은 비행 시간','게임 의도에 맞게 가속도를 선택합니다',4,subjectKind='robot',jumpHeight=2,apexSeconds=.4,timeEnd=.8,worldScale=1),
 m('더 긴 도약','높이 일정 · 긴 비행 시간','감쇠가 원인인 문제와는 구분합니다',4,subjectKind='robot',jumpHeight=2,apexSeconds=.8,timeEnd=1.6,worldScale=1)]),
22:('Apex-Constrained Jump','정점 조건 점프',[
 m('최고점의 속도','H=2 m, T=0.4 s\nv(T)=0','위쪽을 양수로 정의합니다',4,subjectKind='robot',jumpHeight=2,apexSeconds=.4,timeEnd=.4,worldScale=1),
 m('초속 십 미터','v₀=2H/T=10 m/s\na=−2H/T²=−25 m/s²','정점의 높이와 시간을 함께 맞춘 값',4,subjectKind='robot',jumpHeight=2,apexSeconds=.4,timeEnd=.8,worldScale=1)]),
23:('Coulomb Friction','쿨롱 마찰',[
 m('바로 미끄러지지','약한 경사: 정지 마찰로 버팀','접촉 표면 사이의 미끄럼을 따집니다',2,subjectKind='pot',showFriction=True,forceX=0,opposingForce=0,angleRadians=.2),
 m('움직이다 멈춥니다','운동 중: 미끄럼 반대의 마찰','이 모델에서는 정지할 때 역방향으로 튀지 않음',1,subjectKind='pot',initialVelocity=3,slideDeceleration=2,timeEnd=2,worldScale=.9)]),
24:('Static and Kinetic Friction','정지 마찰 · 운동 마찰',[
 m('한도까지','|F_s| ≤ μ_s N','접촉 표면이 미끄러지지 않는 상태',subjectKind='pot',showFriction=True,forceX=3,opposingForce=0),
 m('한도를 넘어','|F_k| = μ_k N','미끄럼 방향과 반대 · 세계 좌표의 정지와 다름',subjectKind='pot',showFriction=True,forceX=12,opposingForce=0,kineticContact=True,initialVelocity=1)]),
25:('Static Friction Limit','정지 마찰의 최대값',[
 m('최대 오 뉴턴','N=10 N, μ_s=0.5\n|F_s|max=5 N','최대값은 현재 값과 다릅니다',subjectKind='pot',showFriction=True,mass=1,gravity=10,forceX=5,opposingForce=0),
 m('이 뉴턴만','F외부=+2 N → F_s=−2 N\nΣF=0','한도 5N 안에서 필요한 2N만 작용',subjectKind='pot',showFriction=True,mass=1,gravity=10,forceX=2,opposingForce=0)]),
26:('Friction Coefficient','마찰 계수',[
 m('두 표면의 조합','μ_s=0.61 → 한도 6.1 N','예시: 알루미늄/강철 · N=10N',subjectKind='pot',showFriction=True,mass=1,gravity=10,forceX=2,opposingForce=0,muStatic=.61),
 m('영점영사','μ_s=0.04 → 한도 0.4 N','예시: 강철/테플론 · 표면 조건에 따라 달라짐',subjectKind='pot',showFriction=True,mass=1,gravity=10,forceX=2,opposingForce=0,muStatic=.04,muKinetic=.03)]),
27:('Normal Force on an Incline','경사면의 수직항력',[
 m('평평하고','θ=0 → N=mg','바닥 법선 위쪽 · 평행 성분 0',2,subjectKind='pot',showFriction=True,forceX=0,opposingForce=0,angleRadians=0),
 m('내적을 이용해','N=−F중력·n̂=mg cosθ\nF평행=mg sinθ','법선 방향 성분을 분리합니다',2,subjectKind='pot',showFriction=True,forceX=0,opposingForce=0,angleRadians=math.pi/6)]),
28:('Incline Stability','경사면의 미끄럼 조건',[
 m('탁자를 더 기울이면','mg sinθ ≤ μ_s mg cosθ','θ=20°: tanθ≈0.364 < 0.5',2,subjectKind='pot',showFriction=True,forceX=0,opposingForce=0,angleRadians=math.radians(20)),
 m('탄젠트 세타','tanθ ≤ μ_s\nθ=35°: tanθ≈0.700 > 0.5','한도를 넘으면 미끄럼 시작',2,subjectKind='pot',showFriction=True,forceX=0,opposingForce=0,angleRadians=math.radians(35))]),
29:('Kinetic Friction','운동 마찰',[
 m('방향은 상대','F⃗_k = −μ_k N v̂미끄럼','접촉면을 따라 아래로 움직이는 경우',2,subjectKind='pot',showFriction=True,forceX=0,opposingForce=0,angleRadians=math.pi/6,kineticContact=True,initialVelocity=-1),
 m('속력이 달라도','속력 1 → 3 m/s\n같은 μ_k,N → 같은 마찰 크기','이상적인 쿨롱 마찰 모형의 조건',2,subjectKind='pot',showFriction=True,forceX=0,opposingForce=0,angleRadians=math.pi/6,kineticContact=True,initialVelocity=-3)]),
30:('Contact Area and Pressure','접촉 면적과 압력',[
 m('면적이 직접','N=10 N, A=1 m²\nP=10 Pa, 미끄럼 한도=5 N','압력과 마찰 한도는 서로 다른 양',13,subjectKind='pot',mass=1,gravity=10,contactArea=1),
 m('더 작은 면적','N=10 N, A=0.25 m²\nP=40 Pa, 미끄럼 한도=5 N','면적이 줄면 압력 증가 · 넘어짐은 토크로 분석',13,subjectKind='pot',mass=1,gravity=10,contactArea=.25)]),
31:('From Forces to Motion','힘에서 움직임으로',[
 m('방향까지 합친','누가 받는 힘인가? → ΣF','중력 · 접촉력 · 마찰을 구분합니다',showFriction=True,forceX=12,opposingForce=0),
 m('가속도로 다음','a=ΣF/m → v → p','다음에는 목표로 돌아가는 복원력을 더합니다',10,forceX=4,opposingForce=0)])
}
rows=[]
for scene in script['scenes']:
 i=int(scene['id'])
 if not i:continue
 english,korean,steps=content[i];text=' '.join(scene['lines'])
 for item in steps:
  assert item['anchor'] in text,(i,item['anchor'])
  item['model'].update(id=scene['sourceBeatId'],english=english,korean=korean,meaning=scene['title'])
 rows.append(dict(sceneId=scene['id'],sourceBeatId=scene['sourceBeatId'],shot=dict(beatId=scene['sourceBeatId'],steps=steps,durationSeconds=0,stepSeconds=[],stepPositions=[]),runtimeQa=False,sceneSaved=False))
out=dict(episode='M27',sourceOrderPreserved=True,scriptSha256=hashlib.sha256((P/'script/narration.ko.json').read_bytes()).hexdigest(),shots=rows,actualSpeechTiming=False,runtimeQa=False,localReviewReady=False,remaining=['Inspect context-specific licensed props, observed native output and final caption clearance.','Force pairs, contact arrows and frame transformations require actual moving-output inspection.'])
(S/'force-shots.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Authored',len(rows),'source-ordered M27 scenes; no voice or renderer started.')
