"""Source-ordered M31–M33 models. Bind speech time only after actual voice alignment."""
from pathlib import Path
from copy import deepcopy
import json, hashlib
R=Path(__file__).resolve().parents[3]
V=lambda x,y=0,z=0:dict(x=x,y=y,z=z)
B=[V(0,0),V(1,2),V(3,2),V(4,0)]
H=[V(0,0),V(0,1),V(2,1),V(2,0)]
E=[V(3,5),V(6,1),V(0,3),V(5,5)]
L=[V(0,0),V(4/3,0),V(8/3,0),V(4,0)]
S=[V(0,0),V(0,0),V(4,0),V(4,0)]
PC=[V(0,0),V(0,3),V(6,-3),V(-4,0)]
EC=[V(3,5),V(9,-12),V(-27,18),V(20,-6)]
K=[V(0,0),V(1,2),V(4,0),V(5,2)]
def fixed(t):return dict(parameterFixed=True,displayT=t)
def config(mode,term,ko,meaning,formula='',**kw):
 d=dict(mode=mode,englishTerm=term,koreanTerm=ko,meaning=meaning,formula=formula,
        animation='Travel',basis='Bernstein',controls=deepcopy(B),coefficients=deepcopy(PC),knots=deepcopy(K),tangent=False,
        showDerivative=False,showCurvature=False,modelScale=1.4,worldOffset=V(-7.6,.7),termExpanded=True)
 d.update(kw);return d

M31=[
 config('Power','Parametric Curve','매개변수 곡선','숫자 하나를 넣어 경로 위 위치를 구합니다','t → p(t) = (x(t), y(t), z(t))\nt 범위와 실제 시간은 구분'),
 config('Circle','Parametric Circle','원의 매개변수 표현','한 바퀴를 0부터 1로 셉니다','x = cos(2πt)\ny = sin(2πt)',modelScale=1.65,worldOffset=V(-4.7,2.6)),
 config('Power','Power Basis','단항식 기저','거듭제곱별 계수로 곡선을 정리합니다','p(t) = c₀ + c₁t + c₂t² + c₃t³'),
 config('Circle','Polynomial versus Parametric','다항식과 매개변수 표현','사인·코사인 곡선은 다항식이 아닙니다','원: cos(2πt), sin(2πt)\n유한 다항식과 구분',modelScale=1.65,worldOffset=V(-4.7,2.6)),
 config('Power','Curve Evaluation','곡선 평가','현재 진행도를 위치로 바꿉니다','t 갱신 → p(t) → 물체 위치\n화면 경로: 표본을 선분으로 연결'),
 config('Power','Coefficient Matrix','계수 행렬','좌표별 다항식 계수를 나란히 둡니다','C = [c₀ c₁ c₂ c₃] : 3×4\np(t) = C [1 t t² t³]ᵀ\n공간 변환 행렬과 구분'),
 config('Power','Linear Path','직선 경로','변위에 진행도를 곱합니다','d = p₁−p₀\np(t) = p₀+td\nc₂=c₃=0',coefficients=[V(0),V(4),V(0),V(0)]),
 config('Power','Endpoint Conditions','끝점 조건','0과 1을 넣어 출발·도착을 확인합니다','p(0) = c₀\np(1) = c₀+c₁+c₂+c₃'),
 config('Power','Curve Derivatives','곡선의 도함수','접선과 변화량을 계산합니다','p′ = c₁+2c₂t+3c₃t²\np″ = 2c₂+6c₃t',tangent=True,showDerivative=True,acceleration=True),
 config('Power','Chain Rule','연쇄 법칙','진행도의 속도까지 곱해야 실제 속도입니다','실제 시간: τ\ndp/dτ = (dp/dt)(dt/dτ)',tangent=True,showDerivative=True),
 config('LineSpeed','Path and Speed','경로와 속력','같은 직선에서도 시간 간격은 달라집니다','p(t)=(4t,0) → p′=(4,0)\nq(t)=(4t²,0) → q′=(8t,0)',worldOffset=V(-7.6,2.8),showDerivative=True,tangent=True),
 config('Power','Unit Tangent','단위 접선 벡터','도함수에서 길이를 빼고 방향을 얻습니다','T = p′ / |p′|\np′=0: 별도 방향 처리',tangent=True,showDerivative=True),
 config('Circle','Curvature','곡률','작은 반지름일수록 더 급하게 꺾입니다','κ = |p′ × p″| / |p′|³\n원: κ = 1/r\np′ ≠ 0에서 사용',radius=2,animation='Radius',modelScale=.95,worldOffset=V(-4.7,2.6),showCurvature=True,tangent=True,arrowScale=.06),
 config('Lagrange','Interpolation','보간','정해진 점을 정해진 순서로 지납니다','(0,2) → (1,3) → (2,2) → (3,3)',modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Lagrange','Parameter Nodes','매개변수 절점','지날 위치와 지날 매개변수를 함께 정합니다','t = 0, 1/3, 2/3, 1\ny = 2, 3, 2, 3',modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Lagrange','Coordinate-Wise Interpolation','좌표별 보간','같은 시각 목록으로 각 좌표를 계산합니다','x(t), y(t), z(t)\n동일한 매개변수 절점 사용',modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Aitken','Aitken Interpolation','에이트켄 보간','이웃한 결과를 다시 섞습니다','직선 두 개 → 이차\n이차 두 개 → 삼차',triangle=True,modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Aitken','Recursive Interpolation','재귀 보간','양 끝 시각에 맞춰 두 결과의 몫을 정합니다','[(tⱼ−t)P앞+(t−tᵢ)P뒤]\n÷ (tⱼ−tᵢ)',triangle=True,modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Lagrange','Interpolation Overshoot','보간의 지나침','점을 지나는 조건은 모양의 보장이 아닙니다','y(t)=18t³−27t²+10t+2\n점 사이에서 y>3 또는 y<2',modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Lagrange','Lagrange Interpolation','라그랑주 보간','각 점마다 전용 가중치를 만듭니다','p(t) = Σ pᵢ Lᵢ(t)',basis='Lagrange',basisGraph=True,modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Lagrange','Lagrange Basis','라그랑주 기저','자기 시각에서만 1이 됩니다','Lᵢ(tᵢ)=1\nLᵢ(tⱼ)=0   (i≠j)',basis='Lagrange',basisGraph=True,modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Lagrange','Lagrange Basis Construction','기저 함수 구성','다른 시각들을 빼서 영점을 만듭니다','Lᵢ(t)=∏ⱼ≠ᵢ (t−tⱼ)/(tᵢ−tⱼ)\n모든 절점은 서로 달라야 함',basis='Lagrange',basisGraph=True,modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Lagrange','Signed Weights','부호가 있는 가중치','음수 가중치 때문에 밖으로 나갈 수 있습니다','Lᵢ(t) < 0 또는 Lᵢ(t) > 1 가능',basis='Lagrange',basisGraph=True,modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Lagrange','Worked Interpolation','보간 계산 예','서로 다른 계산법이 같은 곡선을 만듭니다','y(t)=18t³−27t²+10t+2\ny(1/2)=2.5',basis='Lagrange',basisGraph=True,modelScale=1.7,worldOffset=V(-7.6,-.8),**fixed(.5)),
 config('Lagrange','Affine versus Convex Combination','아핀 결합과 볼록 결합','합이 1이어도 음수가 있으면 밖으로 나갑니다','Σ Lᵢ(t)=1\n음수 허용 → 볼록 껍질 보장 없음',basis='Lagrange',basisGraph=True,modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Lagrange','Uniqueness of Interpolation','보간 다항식의 유일성','조건을 그대로 두면 계산법만 바꿔도 같습니다','최대 삼차인 두 해의 차이\n서로 다른 영점 4개 → 영다항식',modelScale=1.7,worldOffset=V(-7.6,-.8)),
 config('Bezier','Cubic Hermite Curve','삼차 에르미트 곡선','양 끝 위치와 도함수로 모양을 정합니다','입력 순서: p₀, v₀, v₁, p₁\n도함수는 방향과 크기를 모두 가짐',controls=H,tangent=True,showDerivative=True,modelScale=2,worldOffset=V(-6.9,1.4)),
 config('Power','Hermite Endpoint Constraints','에르미트 끝점 조건','네 조건을 다항식에 넣습니다','c₀=p₀, c₁=v₀\nc₀+c₁+c₂+c₃=p₁\nc₁+2c₂+3c₃=v₁',tangent=True,showDerivative=True,modelScale=2,worldOffset=V(-6.9,1.4)),
 config('Power','Hermite Coefficients','에르미트 계수','남은 두 미지수를 연립해서 풉니다','c₂=3(p₁−p₀)−2v₀−v₁\nc₃=2(p₀−p₁)+v₀+v₁',tangent=True,showDerivative=True,modelScale=2,worldOffset=V(-6.9,1.4)),
 config('Bezier','Hermite Basis Matrix','에르미트 기저 행렬','입력을 계수 또는 가중치로 바꿉니다','[p₀ v₀ v₁ p₁] M [1 t t² t³]ᵀ\nM의 각 행:\n1 0 −3 2\n0 1 −2 1\n0 0 −1 1\n0 0 3 −2',controls=H,modelScale=2,worldOffset=V(-6.9,1.4)),
 config('Bezier','Hermite Basis Functions','에르미트 기저 함수','점의 가중치와 도함수의 가중치를 구분합니다','위치 두 가중치의 합 = 1\n도함수 가중치는 방향·크기 조절',controls=H,basis='Hermite',basisGraph=True,modelScale=2,worldOffset=V(-6.9,1.4)),
 config('Bezier','Hermite Worked Example','에르미트 계산 예','네 가중치의 실제 합을 확인합니다','p₀=(0,0), p₁=(2,0)\nv₀=(0,3), v₁=(0,−3)\np(1/2)=(1,0.75)',controls=H,basis='Hermite',basisGraph=True,modelScale=2,worldOffset=V(-6.9,1.4),**fixed(.5)),
 config('Power','Equivalent Curve Representations','같은 곡선의 다른 표현','입력만 달라지고 경로는 같습니다','단항식 계수 ↔ 위치·도함수\n동일한 삼차 다항식',modelScale=2,worldOffset=V(-6.9,1.4)),
 config('Smoothstep','Smoothstep','스무스스텝','양 끝 속도를 0으로 만듭니다','s(t)=3t²−2t³\ns′(0)=s′(1)=0',worldOffset=V(-7.6,2.8),showDerivative=True),
 config('Smoothstep','Clamped Smoothstep','범위를 제한한 스무스스텝','밖에서는 멈추지만 가속도는 이어지지 않습니다','u=clamp((x−a)/(b−a),0,1)\ns=3u²−2u³\n바깥 상수값과 C1 연결 · C2 아님',worldOffset=V(-7.6,2.8),showDerivative=True),
 config('Power','Quintic Hermite Interpolation','5차 에르미트 보간','위치·속도·가속도 조건 여섯 개를 맞춥니다','p₀,v₀,a₀,p₁,v₁,a₁\n6개 조건 → 최대 5차\n다음: 손잡이 점으로 조절',coefficients=[V(0),V(0),V(0),V(40),V(-60),V(24)],tangent=True,showDerivative=True),
]

M32=[
 config('Bezier','Cubic Bézier Curve','삼차 베지에 곡선','내부 두 점은 모양을 잡는 손잡이입니다','b₀,b₃: 지나는 끝점\nb₁,b₂: 모양을 잡는 제어점'),
 config('Bezier','Repeated Linear Interpolation','반복 선형 보간','같은 비율로 이웃 점들을 섞습니다','lerp(a,b,t)=(1−t)a+tb\n4개 → 3개 → 2개 → 1개',triangle=True),
 config('Bezier','De Casteljau Algorithm','드 카스텔조 알고리즘','마지막 한 점이 곡선을 그립니다','p(t): 반복 보간의 마지막 점',triangle=True),
 config('Bezier','In-Place De Casteljau','배열 안에서 드 카스텔조 계산','앞에서부터 덮어 쓰고 유효 길이를 줄입니다','n = 점 개수\n빈 배열 먼저 확인\n원본 보존하려면 복사',triangle=True,codeVisible=True,code='<color=#CEA7DB>while</color> (n > <color=#E8CF83>1</color>) {\n  <color=#CEA7DB>for</color> (i = 0; i < n-1; ++i)\n    p[i] = <color=#73C7C2>lerp</color>(p[i],p[i+1],t);\n  --n;\n}\n<color=#CEA7DB>return</color> p[0];'),
 config('Bezier','Polynomial Expansion','다항식 전개','반복 보간을 거듭제곱별로 모읍니다','이차: c₀=b₀\nc₁=2(b₁−b₀)\nc₂=b₀−2b₁+b₂',controls=[V(0),V(2,2),V(4)]),
 config('Bezier','Basis Conversion','기저 변환','제어점과 다항식 계수는 같은 곡선을 나타냅니다','C = BM\np(t)=BM[1 t t² t³]ᵀ'),
 config('Bezier','Cubic Bézier Coefficients','삼차 베지에 계수','제어점의 차이가 도함수 조건을 만듭니다','c₀=b₀\nc₁=3(b₁−b₀)\nc₂=3b₀−6b₁+3b₂\nc₃=−b₀+3b₁−3b₂+b₃'),
 config('Bezier','Inverse Basis Conversion','역 기저 변환','계수에서 손잡이를 복원합니다','b₀=c₀\nb₁=c₀+c₁/3\nb₂=c₀+2c₁/3+c₂/3\nb₃=c₀+c₁+c₂+c₃'),
 config('Bezier','De Casteljau Worked Example','드 카스텔조 계산 예','손잡이 높이와 경로 높이는 다릅니다','t=1/2\n1차: (0.5,1),(2,2),(3.5,1)\n2차: (1.25,1.5),(2.75,1.5)\np=(2,1.5)',triangle=True,**fixed(.5)),
 config('Bezier','Control-Point Influence','제어점의 영향','진행도를 고정하고 손잡이 하나만 바꿉니다','t=1/2 고정\nb₁ 높이만 변경',animation='HandleY',triangle=True,**fixed(.5)),
 config('Bezier','Bernstein Coefficients','베른슈타인 계수','같은 제어점으로 가는 경로 수를 셉니다','이차: 1,2,1\n삼차: 1,3,3,1',basisGraph=True),
 config('Pascal','Pascal’s Triangle','파스칼의 삼각형','바로 위 두 수를 더합니다','사차: 1,4,6,4,1\n이항계수 C(n,i)',worldOffset=V(-7.6,.5),modelScale=1.3),
 config('Bezier','Bernstein Basis Functions','베른슈타인 기저 함수','가중치로 네 제어점을 섞습니다','Bᵢⁿ(t)=C(n,i)tⁱ(1−t)ⁿ⁻ⁱ\nt=1/2: 1/8,3/8,3/8,1/8',basisGraph=True,**fixed(.5)),
 config('Bezier','Convex Hull Property','볼록 껍질 성질','0 이상인 가중치의 합은 1입니다','Σ Bᵢⁿ(t)=(t+(1−t))ⁿ=1\n0≤t≤1 → 모든 가중치≥0',convexHull=True),
 config('Bezier','Global Support','전역 지지','손잡이 하나가 열린 구간 전체에 영향을 줍니다','0<t<1 → 모든 가중치>0\n국소 수정에는 여러 조각 사용',animation='HandleY'),
 config('Bezier','Maximum Basis Weight','가중치가 가장 큰 곳','공간 거리와 매개변수 순서를 구분합니다','Bᵢⁿ 최대: t=i/n\n삼차 첫 내부점: t=1/3',basisGraph=True,**fixed(1/3)),
 config('Bezier','Endpoint Derivatives','끝점 도함수','양 끝 손잡이가 출발·도착 방향을 정합니다','p′(0)=3(b₁−b₀)\np′(1)=3(b₃−b₂)',showDerivative=True,tangent=True),
 config('Bezier','Bézier–Hermite Conversion','베지에·에르미트 변환','위치와 도함수로 같은 곡선을 표현합니다','b₁=p₀+v₀/3\nb₂=p₁−v₁/3',showDerivative=True,tangent=True),
 config('Bezier','Endpoint Second Derivatives','끝점 이차 도함수','연속한 두 변의 차이를 계산합니다','p″(0)=6(b₀−2b₁+b₂)\np″(1)=6(b₁−2b₂+b₃)',showDerivative=True,tangent=True,acceleration=True),
 config('Bezier','Control Spacing and Speed','손잡이 간격과 속력','같은 직선도 시간 배치가 달라집니다','등간격 제어점 → 등속\n시작,시작,끝,끝 → smoothstep',controls=L,equalTimeMarkers=True,showDerivative=True,tangent=True,worldOffset=V(-7.6,2.4)),
 config('LineSpeed','Acceleration versus Curvature','가속도와 곡률','직선 위 가속은 곡률을 만들지 않습니다','κ=|p′×p″|/|p′|³\n직선: κ=0, 가속도는 가능',worldOffset=V(-7.6,2.8),showDerivative=True,showCurvature=True,tangent=True),
 config('Split','Curve Subdivision','곡선 분할','같은 경로를 독립적인 손잡이 묶음으로 만듭니다','원래 모양 보존\n각 조각에 새 제어점'),
 config('Extract','Reparameterization','재매개변수화','원래 구간을 새 0~1 범위로 옮깁니다','t=a+(b−a)s\ns=0 → a\ns=1 → b'),
 config('Power','Subinterval Worked Example','부분 구간 계산 예','구간 폭도 도함수에 곱해집니다','t²=(0.2+0.3s)²\n=0.04+0.12s+0.09s²',coefficients=[V(.04),V(.12),V(.09),V(0)],modelScale=12,worldOffset=V(-8,2.6)),
 config('Split','Left Subcurve','왼쪽 부분 곡선','삼각형의 첫 점들을 차례로 모읍니다','분할 t=0.75\n각 줄 첫 점 → 왼쪽 제어점',splitAt=.75,triangle=True,**fixed(.75)),
 config('Split','Subcurve Derivative Scale','부분 곡선의 도함수 비율','구간 폭만큼 손잡이가 줄어듭니다','t=0.75s\ndp/ds=0.75 dp/dt',splitAt=.75,triangle=True,showDerivative=True),
 config('Split','Midpoint Subdivision','중점 분할','왼쪽 끝과 오른쪽 시작은 같습니다','왼쪽 끝 = 오른쪽 시작\n(2,1.5)\n두 조각의 합 = 원래 경로',triangle=True,**fixed(.5)),
 config('Blossom','Blossoming','블로서밍','보간 비율의 대칭성으로 구간을 꺼냅니다','q₀=b[a,a,a], q₁=b[a,a,b]\nq₂=b[a,b,b], q₃=b[b,b,b]',blossomParameters=[.2,.2,.2]),
 config('Split','Shape-Preserving Subdivision','모양을 보존하는 분할','손잡이를 늘려도 원래 경로를 유지합니다','제어점 → 가중치 → 도함수\n분할 → 다음은 연결 조건'),
]

a=-.9683; z=4.2253; width=z-a
fitco=[V(a,-.364*a*a+1.145*a+2.110),V(width,(-.728*a+1.145)*width),V(0,-.364*width*width),V(0)]
def add(a,b):return V(*(a[k]+b[k] for k in ('x','y','z')))
def mul(a,t):return V(*(a[k]*t for k in ('x','y','z')))
fitb=[fitco[0],add(fitco[0],mul(fitco[1],1/3)),add(add(fitco[0],mul(fitco[1],2/3)),mul(fitco[2],1/3)),add(add(fitco[0],fitco[1]),fitco[2])]
M33=[
 config('Elevation','Degree Elevation','차수 올리기','모양을 보존하며 제어점을 늘립니다','삼차 4점 → 사차 5점\n변환 직후 경로는 동일'),
 config('Elevation','Piecewise Curves','조각별 곡선','높은 차수 대신 작은 조각을 이어 조절합니다','qᵢ=(i/4)bᵢ₋₁+(1−i/4)bᵢ\n스플라인: 낮은 차수 조각의 연결'),
 config('Spline','Global and Local Parameters','전체·국소 매개변수','정수 부분은 구간, 소수 부분은 진행도입니다','s=2.3 → i=2, u=0.3\ns=N → i=N−1, u=1',modelScale=1.2,**fixed(2.3/3)),
 config('Spline','Time Mapping','시간 배치','시간에서 구간과 진행도를 찾습니다','실제 시간 → s → (i,u) → qᵢ(u)\ns 등속 ≠ 이동 거리 등속',modelScale=1.2),
 config('Join','Knot Position','매듭점 위치','앞 조각의 끝과 다음 조각의 시작을 맞춥니다','qᵢ(1)=qᵢ₊₁(0)=kᵢ₊₁'),
 config('Join','Incoming and Outgoing Tangents','들어오는·나가는 접선','매듭점에 두 도함수를 둡니다','위치 k · 들어오는 v⁻ · 나가는 v⁺',tangent=True,showDerivative=True),
 config('Join','Hermite Handles','에르미트 손잡이','손잡이는 도함수의 3분의 1 거리입니다','v⁻=3(k−f)\nv⁺=3(a−k)\n매듭 배열: 0,3,6,…',tangent=True,showDerivative=True),
 config('Join','Shape versus Motion Continuity','모양과 움직임의 연결','방향이 같아도 속력이 뛸 수 있습니다','같은 방향 · 다른 길이\nG1이어도 C1은 아닐 수 있음',animation='UnequalHandles',tangent=True,showDerivative=True),
 config('Join','Parametric Continuity','매개변수 연속성','위치·도함수·이차 도함수를 차례로 맞춥니다','C0: 위치\nC1: +일차 도함수\nC2: +이차 도함수',tangent=True,showDerivative=True),
 config('Join','C1 Continuity','C1 연속성','속도가 변해도 갑자기 뛰지는 않습니다','C1 ≠ 일정한 속도\n연결점 좌우 도함수 일치',tangent=True,showDerivative=True),
 config('Join','Equal Opposite Handles','길이가 같은 반대쪽 손잡이','매듭점이 두 손잡이의 중점입니다','k−f = a−k\nk=(a+f)/2',tangent=True,showDerivative=True),
 config('Join','C2 Handle Condition','C2 손잡이 조건','이웃 변을 한 번 더 연장해 맞춥니다','왼쪽 2차 도함수 = 오른쪽 2차 도함수\nC1 조건도 함께 만족',animation='C2Match',tangent=True,showDerivative=True,acceleration=True),
 config('Join','Duration-Scaled Derivatives','재생 시간을 반영한 도함수','속도는 시간, 가속도는 시간 제곱으로 나눕니다','왼쪽 2초 · 오른쪽 1초\nv=q′/Δτ, a=q″/Δτ²',leftDuration=2,rightDuration=1,tangent=True,showDerivative=True),
 config('Join','Geometric Continuity','기하 연속성','진행 방향을 맞추되 속력은 따로 정합니다','G1: 0이 아닌 접선이 같은 방향\n길이는 달라도 가능',animation='UnequalHandles',tangent=True,showDerivative=True),
 config('Join','Curvature-Vector Continuity','곡률 벡터 연속성','휘는 정도와 휘는 방향을 함께 봅니다','3D의 G2: 곡률 벡터까지 일치\n같은 κ · 다른 휨 평면 → 불충분',animation='DifferentBendPlanes',modelEuler=V(20,-35),modelScale=3,worldOffset=V(-7,2),tangent=True,showDerivative=True,showCurvature=True),
 config('Join','Continuity and Degrees of Freedom','연속성과 자유도','조건 하나마다 제어점 하나가 정해집니다','C0 → 첫 점\nC1 → 두 번째\nC2 → 세 번째\nC3 → 네 번째',animation='C2Match'),
 config('Spline','Automatic Tangents','자동 접선','지날 점들로 출발·도착 도함수를 정합니다','에르미트 곡선은 그대로\n그 입력인 접선을 자동 선택',modelScale=1.2,tangent=True),
 config('TCB','Uniform Catmull–Rom Spline','균일 캐트멀–롬 스플라인','이전 점에서 다음 점까지의 절반을 씁니다','vᵢ=(kᵢ₊₁−kᵢ₋₁)/2\nv⁻=v⁺',modelScale=1.2,tangent=True,showDerivative=True),
 config('TCB','Catmull–Rom Worked Example','캐트멀–롬 계산 예','이웃 점만으로 같은 접선을 만듭니다','이전 (0,0), 현재 (1,2), 다음 (4,0)\nv=(2,0)',modelScale=1.2,tangent=True,showDerivative=True,**fixed(1/3)),
 config('TCB','Kochanek–Bartels Spline','코차넥–바텔스 스플라인','장력·연속성·편향으로 접선을 조절합니다','TCB: Tension / Continuity / Bias\nT=C=B=0 → 균일 Catmull–Rom',modelScale=1.2),
 config('TCB','Tension','장력','접선 전체에 1−T를 곱합니다','T=1 → 접선 0\nT=−1 → 기본 접선 2배',modelScale=1.2,tension=1,tangent=True,showDerivative=True),
 config('TCB','Continuity Parameter','연속성 매개변수','같은 직선 모양도 움직임은 다릅니다','C=−1, T=B=0\n구간 안에서 등속 직선',modelScale=1.2,continuity=-1,tangent=True,showDerivative=True),
 config('TCB','Incoming/Outgoing Weights','들어오는·나가는 가중치','이전 변과 다음 변의 비중을 맞바꿉니다','들어옴: (1−C)/2, (1+C)/2\n나감: (1+C)/2, (1−C)/2',modelScale=1.2,animation='Continuity',tangent=True),
 config('TCB','Bias','편향','두 접선을 함께 한쪽 변으로 돌립니다','이전 변: (1+B)/2\n다음 변: (1−B)/2',modelScale=1.2,animation='Bias',tangent=True),
 config('TCB','Combined TCB Weights','TCB 가중치 결합','세 다이얼의 인수를 함께 곱합니다','v⁻=(1−T)/2 ×\n[(1−C)(1+B)d이전\n +(1+C)(1−B)d다음]',modelScale=1.2,tension=.4,continuity=.3,bias=-.3,tangent=True),
 config('TCB','Endpoint Boundary Conditions','끝점 경계 조건','이웃이 없는 끝에서는 별도 규칙을 정합니다','정지: v끝=0\n가상점=다음 점 → 시작 접선 0',modelScale=1.2,stopAtEnds=True,tangent=True),
 config('TCB','Quadratic Endpoint Tangent','이차 곡선의 끝점 접선','처음 세 점에서 도함수를 가져옵니다','v시작=(−3k₀+4k₁−k₂)/2\n균일한 시각 간격',modelScale=1.2,endpointRule='quadratic',tangent=True),
 config('Lagrange','Three-Node Lagrange Basis','세 절점의 라그랑주 기저','자기 시각에서만 1인지 대입합니다','L₀=(t−1)(t−2)/2\nL₁=−t(t−2)\nL₂=t(t−1)/2',parameterNodes=[0,1,2],interpolationPoints=[V(0),V(1,2),V(2)],domainMax=2,basis='Lagrange',basisGraph=True,modelScale=2,worldOffset=V(-6.9,1.4)),
 config('Power','Projectile Parabola','포물선 경로','높이와 도착 시간을 조건으로 풉니다','x=0, y=2ht−ht², z=dt/2\n예: h=1, d=4\n0≤t≤2',coefficients=[V(0),V(0,2,2),V(0,-1),V(0)],domainMax=2,modelEuler=V(10,-75),modelScale=1.2,worldOffset=V(-7.6,1.2)),
 config('Bezier','Numeric De Casteljau','드 카스텔조 수치 예','같은 비율로 세 번 섞습니다','t=0.4 → 0.6:0.4\np=(3.56,2.696)',controls=E,triangle=True,modelScale=.95,worldOffset=V(-8,-.3),**fixed(.4)),
 config('Power','Equivalent Coefficients','같은 곡선의 계수','끝점·도함수·다항식이 같은 경로를 가리킵니다','x=3+9t−27t²+20t³\ny=5−12t+18t²−6t³\nv₀=(9,−12), v₁=(15,6)',coefficients=EC,tangent=True,showDerivative=True,arrowScale=.08,modelScale=.95,worldOffset=V(-8,-.3)),
 config('Power','Numeric Curve Derivative','곡선 도함수 수치 예','그 지점에서 어느 쪽으로 나아가는지 구합니다','t=0.4\np=(3.56,2.696)\np′=(−3,−0.48)',coefficients=EC,tangent=True,showDerivative=True,modelScale=.95,worldOffset=V(-8,-.3),**fixed(.4)),
 config('Bezier','Partition of Unity','가중치 합 1','전개하면 t 항들이 사라집니다','(1−t)²+2t(1−t)+t²\n=1',controls=[V(0),V(2,2),V(4)],basisGraph=True,convexHull=True),
 config('Bezier','Control Layout and Timing','제어점 배치와 시간','같은 경로에서 출발·정지 방식을 고릅니다','모두 동일 → 한 점\n등간격 → 등속\n시작,시작,끝,끝 → 양 끝 정지',controls=[V(0)]*4,worldOffset=V(-7.6,2.4),equalTimeMarkers=True,showDerivative=True),
 config('Bezier','Alternating Collinear Controls','번갈아 놓은 일직선 제어점','제어점 순서만 보고 왕복을 단정하지 않습니다','b = 시작,끝,시작,끝\ns′(t)=3(2t−1)² ≥ 0\n가운데에서만 순간 정지',controls=[V(0),V(4),V(0),V(4)],worldOffset=V(-7.6,2.4),equalTimeMarkers=True,tangent=True,showDerivative=True),
 config('Bezier','Projectile Bézier Controls','포물선의 베지에 제어점','시간 범위를 바꾸고 계수를 변환합니다','y=4hu(1−u), z=du\n내부점 높이 4h/3\nz 위치 d/3, 2d/3',controls=[V(0),V(0,4/3,4/3),V(0,4/3,8/3),V(0,0,4)],modelEuler=V(10,-75),modelScale=1.2,worldOffset=V(-7.6,1.2)),
 config('Power','Fitted Parabola Conversion','맞춘 포물선 변환','x 범위를 새 매개변수로 바꿉니다','y=−0.364x²+1.145x+2.110\nx=−0.9683+5.1936u',coefficients=fitco,modelScale=1.25,worldOffset=V(-7.2,.6)),
 config('Bezier','Fitted Parabola Handles','맞춘 포물선의 손잡이','내부점은 경로 표본이 아니라 접선 손잡이입니다','\n'.join(f'b{i}=({p["x"]:.4f},{p["y"]:.4f})' for i,p in enumerate(fitb)),controls=fitb,modelScale=1.25,worldOffset=V(-7.2,.6)),
 config('Extract','Numeric Subcurve','부분 곡선 계산 예','새 도함수에는 구간 폭이 곱해집니다','t=0.2+0.3u\nq₀=(3.88,3.272), q₁=(3.94,2.72)\nq₂=(3.55,2.6), q₃=(3.25,2.75)',controls=E,modelScale=.95,worldOffset=V(-8,-.3)),
 config('Split','Numeric Midpoint Split','중점 분할 계산 예','두 조각의 공통 끝점을 확인합니다','분할 t=0.5\n공통점 (3.25,2.75)',controls=E,triangle=True,modelScale=.95,worldOffset=V(-8,-.3),**fixed(.5)),
 config('Elevation','Numeric Degree Elevation','차수 올리기 계산 예','제어 다각형은 달라도 경로는 같습니다','새 내부점:\n(5.25,2), (3,2), (1.25,3.5)',controls=E,modelScale=.95,worldOffset=V(-8,-.3)),
 config('Spline','Piecewise Path Design','조각별 경로 설계','필요한 연결 조건을 먼저 정합니다','위치 → 진행 방향 → 속도·가속도\n모양과 시간 배치를 함께 확인',modelScale=1.2,tangent=True),
]

EXTRA={
 31:{2:[('티가 사분의',fixed(.25),'p(1/4)=(0,1)'),('이분의 일이면',fixed(.5),'p(1/2)=(−1,0)')],7:[('디까지 영이면',dict(coefficients=[V(0)]*4),'d=0 → 점 하나')],8:[('티가 일이면',fixed(1),'p(1)=c₀+c₁+c₂+c₃')],24:[('티가 이분의',fixed(.5),'y(1/2)=2.5')],27:[('손잡이 화살표를',dict(animation='HandleRotate'),'손잡이 방향 변경'),('길게 늘리면',dict(animation='HandleY'),'손잡이 길이 변경')],35:[('구간 밖에서는',dict(domainMin=-.25,domainMax=1.25),'구간 밖: 0 또는 1 유지')]},
 32:{5:[('세 점에서는',{},'c₀=b₀\nc₁=2(b₁−b₀)\nc₂=b₀−2b₁+b₂')],14:[('처음과 끝에서는',fixed(1),'t=1: 마지막 가중치만 1')],17:[('끝 도함수는',fixed(1),'p′(1)=3(b₃−b₂)')],20:[('가운데 두 점을',dict(controls=S),'양 끝 손잡이 겹침 → smoothstep')],21:[('반대로 원을',dict(mode='Circle',radius=1,modelScale=1.65,worldOffset=V(-4.7,2.6),arrowScale=.06),'등속 원: 방향 변화로 가속도 발생')],28:[('다음은 에이 두 번',dict(blossomParameters=[.2,.2,.5]),'q₁=b[a,a,b]'),('그다음은 에이 한 번',dict(blossomParameters=[.2,.5,.5]),'q₂=b[a,b,b]'),('마지막은 비 세 번',dict(blossomParameters=[.5,.5,.5]),'q₃=b[b,b,b]')]},
 33:{3:[('마지막 끝점에서는',fixed(1),'s=N → (N−1,1)')],8:[('반대로 양쪽 도함수를',dict(animation='StoppedCorner'),'양쪽 도함수 0 → 멈춰 방향 전환')],13:[('왼쪽 손잡이를',dict(animation='UnequalHandles'),'왼쪽 손잡이 = 오른쪽 2배\n2초와 1초에서 실제 속도 일치')],21:[('장력이 마이너스 일이면',dict(tension=-1),'T=−1 → 접선 2배'),('일을 넘기면',dict(tension=1.5),'T>1 → 접선 반전')],34:[('등속 직선이라면',dict(controls=L),'등간격 → 등속 직선'),('부드럽게 출발하고',dict(controls=S),'시작,시작,끝,끝 → 양 끝 속도 0')]}
}
def main():
 for episode,slug,models in [(31,'game-math-parametric-hermite',M31),(32,'game-math-bezier-subdivision',M32),(33,'game-math-splines-continuity',M33)]:
  P=R/'projects'/slug;path=P/'script/narration.ko.json';data=json.loads(path.read_text(encoding='utf-8-sig'));scenes=[s for s in data['scenes'] if int(s['id'])];assert len(scenes)==len(models),(episode,len(scenes),len(models));rows=[]
  for scene,raw in zip(scenes,models):
   n=int(scene['id']);words=' '.join(scene['lines']);m=deepcopy(raw);formula=m.pop('formula');m.update(episodeId=f'M{episode}',beatId=scene['sourceBeatId'],sourceParagraphs=scene['sourceBeatId'],screenIntent=words)
   steps=[dict(anchor=words.split('.')[0],formula=formula,meaning=m['meaning'],model=m)]
   for anchor,opts,f in EXTRA.get(episode,{}).get(n,[]):
    assert words.find(anchor)>0,(episode,n,anchor)
    nextmodel=deepcopy(m);nextmodel.update(opts);steps.append(dict(anchor=anchor,formula=f,meaning=m['meaning'],model=nextmodel))
   positions=[words.find(s['anchor']) for s in steps];assert positions==sorted(positions)
   rows.append(dict(sceneId=scene['id'],sourceBeatId=scene['sourceBeatId'],shot=dict(beatId=scene['sourceBeatId'],durationSeconds=0,stepSeconds=[],stepPositions=[],steps=steps),actualSpeechTiming=False))
  out=P/'production/unity-staging/curve-shots.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(dict(project=slug,scriptSha256=hashlib.sha256(path.read_bytes()).hexdigest(),shots=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(episode,len(rows),'source scenes',sum(len(x['shot']['steps']) for x in rows),'verified speech anchors')
if __name__=='__main__':main()
