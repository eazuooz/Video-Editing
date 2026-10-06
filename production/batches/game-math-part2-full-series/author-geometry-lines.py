"""Bilingual geometry lecture, authored after direct source-footage inspection."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-lines-bounds';scenes=[]
def E(i,title,mode,ko,en,beats,**kw):
 assert len(ko)==len(en)==len(beats),(i,len(ko),len(en),len(beats))
 scenes.append(dict(id=f'{i:02}',title=title,kind='explanation',mode=mode,ko=ko,en=en,beats=beats,**kw))
def A(i,title,vid,segments,ko,en,focus,claim):
 assert len(ko)==len(en)
 scenes.append(dict(id=f'{i:02}',title=title,kind='actual',sourceId=vid,sourceSegments=[{'in':a,'maxSeconds':b-a} for a,b in segments],**{'in':segments[0][0]},maxSeconds=sum(b-a for a,b in segments),ko=ko,en=en,focus=focus,claim=claim))
U='SSekdYTL4Ck';S='4s7nMfXt8uQ'
E(1,'형태를 계산으로 바꾸는 첫걸음','overview',[
 '게임 화면에서 조준하는 선과 물체의 크기를, 프로그램은 어떤 숫자로 다룰까요?',
 '먼저 그래플이 연결되는 장면에서 출발점과 방향을 찾고, 직선과 선분, 레이를 구분합니다.',
 '이어서 둥근 물체를 구로 표현하고, 여러 점을 감싸는 경계 상자를 직접 계산하겠습니다.',
 '마지막으로 상자를 회전시키며 흔한 오류를 확인하고, 안전하게 변환하는 식까지 정리합니다.'
],[
 'What numbers let a program describe a targeting line or an object size?',
 'We will find origins and directions in grappling footage, then distinguish lines, segments and rays.',
 'Next we will represent round objects with spheres and calculate a box enclosing a set of points.',
 'Finally we will rotate a box, expose a common error, and derive a safe transformation formula.'
],['화면의 형태 → 계산 가능한 데이터','그래플 관찰 → 직선·선분·레이','둥근 형태 → 구 → 점들의 경계 상자','회전 오류 → 여덟 꼭짓점 → 빠른 식'])
A(2,'그래플에서 출발점과 연결점을 찾기',U,[(482,510),(559,576)],[
 '어 스토리 어바웃 마이 엉클에서 바위 사이를 이동합니다. 손에서 뻗는 밝은 연결선을 보세요.',
 '연결선이 나타날 때 손 쪽의 출발과 바위 쪽의 도착을 나눠 생각할 수 있습니다.',
 '조준점을 다른 바위로 옮기면 연결되는 방향도 바뀝니다. 시작점 하나만으로 선 전체가 정해지지는 않습니다.',
 '화면에서 보이는 길이는 카메라와 원근의 영향을 받습니다. 픽셀 길이를 곧바로 게임 속 거리로 읽지는 마세요.',
 '이동하면서 두 끝점 사이의 관계가 바뀌는 모습을 기억하세요. 다음 그림에서는 우리가 정한 좌표로 그 관계를 계산합니다.',
 '보이는 그래플은 계산의 출발점입니다. 이 장면만으로 게임 내부의 레이 판정이나 물리 구현을 확인한 것은 아닙니다.'
],[
 'We travel among rocks in A Story About My Uncle. Watch the bright connection extending from the hand.',
 'When it appears, distinguish its origin near the hand from its attachment on a rock.',
 'Aiming at another rock changes the connection direction. One starting point alone does not determine a line.',
 'Its screen length depends on the camera and perspective; pixels are not automatically world distance.',
 'Remember how the endpoints relate as we move. Our diagram will calculate that relation in explicitly chosen coordinates.',
 'The visible grapple motivates the mathematics; it does not reveal this game ray tests or physics implementation.'
],'손·바위의 연결점과 조준 방향; 화면 길이와 월드 거리 구분','관찰을 직접 정의한 좌표 계산으로 연결하며 내부 구현을 단정하지 않는다')
E(3,'같은 원을 설명하는 세 가지 방법','forms',[
 '같은 원도, 무엇을 계산하느냐에 따라 표현을 바꿉니다. 중심과 반지름을 저장하면 형태의 데이터를 직접 갖게 됩니다.',
 '둘째는 매개변수 표현입니다. 각도를 넣으면 중심에 반지름 곱하기 코사인과 사인을 더해 원 위의 점을 만들 수 있습니다.',
 '셋째는 암시적 표현입니다. 주어진 점에서 중심을 뺀 벡터의 길이 제곱과 반지름 제곱을 비교합니다.',
 '두 값이 같으면 원 위이고, 길이 제곱이 작으면 안쪽입니다. 그림의 점을 움직이며 판정이 바뀌는 것을 보세요.',
 '매개변수식은 점을 만드는 데, 암시적 식은 점을 검사하는 데 편리합니다. 하나가 항상 더 좋은 표현은 아닙니다.',
 '각도 매개변수를 넣었다고 시간이 생기는 것은 아닙니다. 각도, 시간, 거리 중 어떤 뜻인지 우리가 먼저 정해야 합니다.'
],[
 'We can describe the same circle differently depending on the calculation. Storing its center and radius gives direct shape data.',
 'A parametric representation constructs a point by adding radius times cosine and sine of an angle to the center.',
 'An implicit representation compares squared distance from a candidate point to the center with squared radius.',
 'Equality means the boundary; a smaller squared distance means the interior. Watch the classification change as the point moves.',
 'Parametric equations conveniently construct points; implicit equations conveniently test them. Neither is always better.',
 'An angle parameter does not automatically represent time. Define whether a parameter means angle, time or distance.'
],['직접 데이터: 중심 c / 반지름 r','점 만들기: p(θ)=c+r(cosθ,sinθ)','점 검사: F(p)=‖p-c‖²-r²','F=0: 경계 / F<0: 내부','생성 / 검사 / 저장: 목적에 맞는 표현','θ: 각도 / 시간·거리와 자동으로 같지 않음'])
E(4,'중심을 옮기면 일차항도 필요합니다','conic',[
 '중심이 원점인 원은 엑스 제곱 더하기 와이 제곱이 반지름 제곱입니다. 중심을 옮기면 식도 달라집니다.',
 '중심이 이, 삼이고 반지름이 일인 원입니다. 엑스 좌표에서는 중심 좌표 이만큼을 뺍니다. 와이 좌표에서는 중심 좌표 삼만큼을 빼고, 각각 제곱합니다.',
 '전개하면 엑스 제곱 더하기 와이 제곱, 마이너스 사 엑스, 마이너스 육 와이, 더하기 십이가 영입니다.',
 '따라서 일반적인 이차 곡선 식에는 제곱항과 교차항뿐 아니라 일차항과 상수항도 들어갑니다.',
 '원은 중심 두 성분과 반지름 하나로 정해집니다. 구는 중심 세 성분과 반지름 하나를 사용합니다.',
 '축마다 다른 반지름을 주면 타원이나 타원체를 표현할 수 있습니다. 구를 비균일하게 늘린 뒤에도 구라고 취급하면 판정이 달라집니다.'
],[
 'For a circle at the origin, x squared plus y squared equals radius squared. Translating its center changes the equation.',
 'Take center two, three and radius one. Subtract two from x and three from y before squaring.',
 'Expansion gives x squared plus y squared minus four x minus six y plus twelve equal to zero.',
 'A general conic therefore includes linear and constant terms as well as squared and cross terms.',
 'A circle needs two center components and one radius. A sphere needs three center components and one radius.',
 'Different radii along the axes describe an ellipse or ellipsoid. Nonuniformly stretching a sphere generally changes it into an ellipsoid.'
],['원점의 원: x²+y²=r²','(x-2)²+(y-3)²=1','x²+y²-4x-6y+12=0','Ax²+Bxy+Cy²+Dx+Ey+F=0','원: 3개 / 구: 4개 형상 매개변수','비균일 스케일: 구 → 타원체'])
A(5,'연결 방향과 이동 거리 구분하기',U,[(598,613),(632,669)],[
 '다른 바위에 연결하고 공중을 이동하는 장면입니다. 연결선이 생기는 순간 두 끝을 다시 찾아보세요.',
 '출발점에서 연결점으로 가는 차이 벡터는 방향과 길이를 함께 담습니다.',
 '같은 쪽을 가리켜도 가까운 바위와 먼 바위까지의 차이 벡터는 길이가 다릅니다.',
 '방향만 필요하면 그 차이를 길이로 나눕니다. 그러면 길이가 일인 방향벡터와 별도의 거리를 갖게 됩니다.',
 '손에서 바위까지의 연결과 캐릭터가 실제로 움직인 경로는 같은 질문이 아닙니다. 이동에 쓰인 힘과 궤적은 뒤의 역학에서 다루겠습니다.',
 '지금은 두 위치를 잇는 기하 표현에 집중하세요. 식의 매개변수가 전체 길이의 비율인지 거리인지에 따라 계산 결과의 뜻이 달라집니다.'
],[
 'We connect to another rock and travel through the air. Find both endpoints whenever the beam appears.',
 'Subtracting origin from attachment gives a displacement vector containing direction and length.',
 'Even when two rocks lie in the same direction, their displacement lengths differ.',
 'For direction alone, divide displacement by its length. Store a unit direction and distance separately.',
 'The hand-to-rock connection and the character actual path are different questions. Forces and trajectories belong to later dynamics lessons.',
 'Focus here on geometric descriptions between positions. A fractional parameter and a distance parameter have different meanings.'
],' 연결점 차이 벡터·거리와 캐릭터 이동 경로의 차이','레이 매개변수와 정규화를 관찰에 연결; 게임 속 힘/궤적 공식은 추정하지 않는다')
E(6,'직선·선분·레이는 범위가 다릅니다','domains',[
 '출발점을 알파벳 오, 차이 벡터를 델타라고 부르겠습니다. 위치는 출발점에 티 곱하기 델타를 더해 구합니다.',
 '티가 영이면 출발점이고, 일이면 도착점입니다. 영부터 일까지만 허용하면 두 점 사이의 선분입니다.',
 '티를 모든 실수로 허용하면 양쪽으로 끝없이 이어지는 직선입니다. 음수는 반대쪽으로 연장합니다.',
 '보통 수학의 레이는 티가 영 이상인 반직선입니다. 앞쪽으로 끝없이 이어집니다.',
 '책에서는 레이라는 이름을 유한한 방향 선분에도 사용합니다. 엔진에서도 최대 거리를 받는 레이 검사가 흔하므로 실제 허용 범위를 확인해야 합니다.',
 '이름만 외우기보다 출발점, 방향과 매개변수의 범위를 함께 기록하세요. 그래야 선분 밖의 점을 잘못 포함하지 않습니다.'
],[
 'Call the origin the letter o and displacement delta. Position is the origin plus t times delta.',
 'Zero gives the origin and one gives the endpoint. Restricting t to zero through one defines the segment.',
 'Allowing every real t produces an infinite line. Negative t extends in the opposite direction.',
 'A mathematical ray usually restricts t to nonnegative values and extends infinitely forward.',
 'The book also calls a finite directed segment a ray. Engine ray queries may have a maximum distance, so inspect the actual allowed domain.',
 'Record the origin, direction and parameter range together, rather than relying on a name.'
],['p(t)=o+tδ','선분: 0≤t≤1','직선: t∈ℝ','무한 레이: t≥0','책의 유한 레이 / 엔진의 최대 거리 확인','데이터 + 매개변수 범위를 함께 기록'])
E(7,'비율과 거리의 단위 확인하기','ray-units',[
 '출발점이 이, 일이고 차이 벡터가 육, 삼이라고 합시다. 절반 지점은 어디일까요?',
 '티에 영 점 오를 넣으면 출발점에 삼, 일 점 오를 더합니다. 결과는 오, 이 점 오입니다.',
 '이 영 점 오는 선분 길이의 절반이라는 비율입니다. 영 점 오 초나 영 점 오 미터가 아닙니다.',
 '차이 벡터의 길이는 루트 사십오입니다. 단위 방향은 차이 벡터를 루트 사십오로 나눠 만듭니다.',
 '이 단위 방향에 거리 에스를 곱하면 에스가 공간의 거리 단위를 갖습니다. 같은 절반 지점에는 루트 사십오의 절반을 넣습니다.',
 '두 끝점이 같으면 차이 벡터가 영입니다. 길이로 나누기 전에 검사하고, 퇴화한 점으로 처리할지 오류로 거절할지 정하세요.'
],[
 'Let the origin be two, one and displacement six, three. Where is the midpoint?',
 'At t equal to one half, add three, one point five. The point is five, two point five.',
 'This one half is a fraction of the segment, not half a second or half a meter.',
 'The displacement length is square root of forty-five. Divide displacement by that length to obtain a unit direction.',
 'Multiplying that unit direction by s makes s a distance. The same midpoint uses s equal to half of square root forty-five.',
 'Identical endpoints give zero displacement. Check before normalization and define whether to treat the degenerate input as a point or reject it.'
],['o=(2,1) / δ=(6,3)','p(.5)=(5,2.5)','t=.5: 길이 비율 / 시간·거리 아님','L=√45 / u=δ/L','p(s)=o+su / 중간: s=L/2','δ=0이면 정규화 금지'])
A(8,'화면에서 수직인 선도 표현할 수 있을까요?',U,[(714,768)],[
 '이번에는 위아래에 있는 바위를 번갈아 조준합니다. 연결선이 화면에서 세워지기도 하고 비스듬해지기도 합니다.',
 '우리의 눈에는 모두 자연스러운 선입니다. 그런데 기울기만으로 저장하면 수직선에서 문제가 생깁니다.',
 '엑스 방향 변화가 영인 선은 와이 변화량을 엑스 변화량으로 나눌 수 없습니다.',
 '다음 그림에서는 같은 선을 법선과 위치로 표현해 이 문제를 피하겠습니다. 법선은 선을 따라가는 방향과 직각입니다.',
 '화면의 수직 방향은 카메라가 만든 방향입니다. 실제 계산에서는 어떤 좌표계의 엑스와 와이인지 먼저 정해야 합니다.',
 '또 두 지점에서 거리가 같은 위치를 찾는 문제도 보겠습니다. 두 지점을 잇는 선과 그 수직이등분선은 서로 다른 선입니다.'
],[
 'We aim at rocks above and below us. The beam looks vertical in some views and diagonal in others.',
 'Both are ordinary lines, yet a slope-only representation has a problem at vertical lines.',
 'When the x change is zero, we cannot divide the y change by it.',
 'Our diagram will use a normal and offset instead. A normal is perpendicular to the line direction.',
 'Screen vertical comes from the camera. For calculation, first choose the coordinate frame defining x and y.',
 'We will also find points equidistant from two sites. Their connecting line and perpendicular bisector are different lines.'
],'변하는 조준 방향·세로/사선 투영과 고정 좌표계 구분','수직선의 기울기 문제와 법선 표현으로 이어지는 직관; 월드축 추정 금지')
E(9,'법선 표현과 수직이등분선','line-normal',[
 '와이는 기울기 곱하기 엑스 더하기 절편이라는 식이 익숙합니다. 하지만 수직선은 엑스가 상수라는 다른 형태가 필요합니다.',
 '법선을 엔이라고 하고, 점과의 내적이 디라는 식을 쓰면 수직선과 수평선도 같은 틀로 표현할 수 있습니다.',
 '법선의 방향은 선에 직각입니다. 법선이 영이면 유효한 직선을 정할 수 없습니다.',
 '영, 영과 이, 영에서 같은 거리인 점들을 찾읍시다. 두 점의 차이인 이, 영을 법선으로 쓰고, 중점 일, 영을 통과시킵니다.',
 '식은 이 엑스가 이, 즉 엑스가 일입니다. 세로선이 두 점 사이를 정확히 이등분합니다.',
 '법선을 단위 길이로 바꾸면 디도 같은 길이로 나눕니다. 법선만 바꾸면 선의 위치가 달라집니다. 식의 값과 실제 거리도 법선 길이가 일일 때만 바로 같습니다.'
],[
 'The familiar slope-intercept equation needs a different form, x equal to a constant, for a vertical line.',
 'Using normal n dotted with a point equal to offset d represents vertical and horizontal lines in one form.',
 'The normal is perpendicular to the line. A zero normal does not define a valid line.',
 'For points equidistant from zero, zero and two, zero, use displacement two, zero as normal and midpoint one, zero on the bisector.',
 'The equation is two x equals two, or x equals one. This vertical line bisects the two sites.',
 'When normalizing n, divide d by the same length. Scaling only n moves the line; the residual is directly a signed distance only for a unit normal.'
],['y=mx+b / 수직선: x=k','n·p=d / n⊥선 방향','‖n‖>0 확인','n=r-q / d=n·((q+r)/2)','q=(0,0), r=(2,0) → 2x=2 → x=1','n′=n/‖n‖ / d′=d/‖n‖'])
A(10,'둥근 모습과 실제 판정 범위','%s'%S,[(64,86.5),(96.5,122)],[
 '시리어스 샘 투에서 둥근 물체가 다가오고, 주변에 밝은 폭발 효과가 나타납니다. 둥근 윤곽부터 찾아보세요.',
 '이런 형태를 단순하게 계산하려면 중심과 반지름이 좋은 출발점입니다. 모든 방향으로 같은 거리라는 조건을 만들 수 있기 때문입니다.',
 '다만 둥글게 보이는 화면 효과가 곧 구의 표면이나 실제 피해 범위라는 뜻은 아닙니다. 반지름은 우리가 정의한 계산 데이터입니다.',
 '중심에서 표적까지의 거리가 반지름보다 작으면 내부에 있고, 같으면 경계에 있습니다. 다음 그림에서 세 경우를 나눠 보겠습니다.',
 '화면에서 가까워져 크게 보이는 것과 물체 자체의 반지름이 커지는 것도 다릅니다. 원근에 따른 픽셀 크기를 실제 크기로 혼동하지 마세요.',
 '구의 판정은 복잡한 둥근 모양을 다루는 첫 근사입니다. 어떤 부분을 감싸야 하는지와 근사의 오차를 함께 정해야 합니다.'
],[
 'In Serious Sam2, round objects approach and bright explosions appear. First find the rounded outlines.',
 'A center and radius offer a simple calculation model: the same distance in every direction.',
 'A rounded visual effect is not proof of a spherical surface or damage region. Radius belongs to explicitly defined calculation data.',
 'A target closer than the radius is inside; equal distance is on the boundary. Our diagram will distinguish three cases.',
 'Growing screen size as an object approaches is different from changing its actual radius. Perspective pixels do not establish world size.',
 'A sphere is an initial approximation for a complex rounded object. Specify what must be enclosed and the acceptable approximation error.'
],'둥근 투사체 모습·폭발의 시각 효과; 원근 크기와 실제 반지름 구분','구의 정의를 동기화하며 실제 피해/충돌 반경을 단정하지 않는다')
E(11,'구의 표면과 내부를 구분하기','sphere-test',[
 '구는 중심 세 성분과 반지름으로 정합니다. 점에서 중심을 뺀 벡터의 길이 제곱을 계산하세요.',
 '중심이 일, 이, 삼이고 반지름이 이인 예제를 보겠습니다. 반지름 제곱은 사입니다.',
 '첫 점이 중심 자체라면 거리 제곱은 영입니다. 사보다 작으므로 내부입니다.',
 '두 번째 점이 삼, 이, 삼이면 중심에서 엑스 방향으로 이만큼 떨어집니다. 거리 제곱이 사이므로 표면입니다.',
 '세 번째 점이 사, 이, 삼이면 거리 제곱은 구입니다. 사보다 크므로 바깥입니다. 제곱근 없이도 세 경우를 구분할 수 있습니다.',
 '표면만 뜻할 때는 등호를, 채워진 구 전체를 뜻할 때는 작거나 같음을 씁니다. 유한한 좌표와 영 이상인 반지름을 확인하고, 경계 오차의 허용 단위도 정하세요.'
],[
 'A sphere has three center components and a radius. Compute squared length of point minus center.',
 'Take center one, two, three and radius two. Squared radius is four.',
 'At the center, squared distance is zero: inside because it is smaller than four.',
 'At three, two, three, the x displacement is two. Squared distance four puts the point on the surface.',
 'At four, two, three, squared distance is nine: outside. No square root is needed for this comparison.',
 'Equality defines the surface; less than or equal defines the solid. Validate finite coordinates, a nonnegative radius and a tolerance with defined units.'
],['구: c=(cx,cy,cz) / r≥0','c=(1,2,3), r=2 → r²=4','p=(1,2,3) → 거리²=0 / 내부','p=(3,2,3) → 거리²=4 / 표면','p=(4,2,3) → 거리²=9 / 외부','표면: = / 채운 구: ≤ / 유한·오차 검사'])
E(12,'반지름 두 배가 크기 두 배일까요?','sphere-measures',[
 '반지름을 두 배로 바꾸면 지름은 두 배가 됩니다. 하지만 넓이와 부피는 다르게 커집니다.',
 '원을 가로지르는 지름은 이 알이고, 원주는 이 파이 알입니다. 둘 다 길이 단위를 갖습니다.',
 '원 넓이는 파이 알 제곱입니다. 구의 표면적은 사 파이 알 제곱이고, 둘 다 길이의 제곱 단위입니다.',
 '구의 부피는 삼분의 사 파이 알 세제곱입니다. 길이의 세제곱 단위이므로 반지름 두 배에서 부피는 여덟 배가 됩니다.',
 '표면적은 네 배입니다. 길이, 넓이, 부피를 모두 크기라는 말로 묶으면 비용이나 범위를 잘못 비교하기 쉽습니다.',
 '게임에서 반경을 바꿀 때에도 무엇을 일정하게 유지할지 구분하세요. 시각 효과, 판정 범위와 입자 수의 관계는 설계에 달려 있으며 이 공식만으로 게임의 비용을 확정할 수는 없습니다.'
],[
 'Doubling radius doubles diameter, but area and volume grow differently.',
 'Diameter is two r and circumference is two pi r. Both have length units.',
 'Circle area is pi r squared; sphere surface area is four pi r squared. Both use squared length units.',
 'Sphere volume is four thirds pi r cubed. Cubic units make volume grow eightfold when radius doubles.',
 'Surface area grows fourfold. Calling length, area and volume simply size can cause incorrect comparisons.',
 'When changing a game radius, distinguish what remains constant. Effects, tests and particle counts are design choices; these formulas alone do not determine game performance.'
],['r → 2r: 어떤 크기를 비교할까?','지름 2r / 원주 2πr [L]','원 πr² / 구 표면 4πr² [L²]','구 부피 (4/3)πr³ [L³]','길이 ×2 / 넓이 ×4 / 부피 ×8','효과·판정·성능은 별도의 설계 조건'])
A(13,'복잡한 몸을 간단한 형태로 감싸기',S,[(494,542)],[
 '마을 안에서 작은 적과 큰 적이 움직입니다. 머리, 팔과 몸통의 윤곽을 하나씩 모두 검사한다고 생각해 보세요.',
 '모든 자세에서 상세한 모양을 비교하면 계산할 데이터가 많아집니다. 먼저 단순한 경계 형태로 후보를 거를 수 있습니다.',
 '둥근 머리에는 구를, 길쭉한 몸에는 상자를 떠올려 봅니다. 여기서는 실제 게임의 충돌체가 아니라 우리가 비교할 근사 형태입니다.',
 '물체 방향을 따라가는 상자와 월드 축에 나란한 상자도 구분해야 합니다. 같은 몸을 감싸도 빈 공간의 크기가 달라집니다.',
 '팔을 벌리거나 돌아서면 감싸야 할 윤곽이 바뀝니다. 정지한 한 자세에서 만든 경계가 모든 애니메이션을 포함하는지도 확인해야 합니다.',
 '다음 그림에서는 모양을 점들의 집합으로 단순화하고, 세 축의 최소와 최대를 독립적으로 찾겠습니다.'
],[
 'Small and large enemies move through the village. Imagine checking every head, arm and torso detail.',
 'Detailed comparisons across poses involve many data points. Simple bounding shapes can first filter candidates.',
 'Think of a sphere around a round head or a box around a tall body. These are our illustrative proxies, not verified game colliders.',
 'Distinguish a box following object orientation from a box parallel to world axes. They can enclose different amounts of empty space.',
 'Turning or extending arms changes what must be enclosed. A bound built for one static pose may not contain every animation pose.',
 'Our diagram will simplify the shape to a point set and independently find minimum and maximum along three axes.'
],'몸통·팔의 자세와 둥근 머리; 감싸는 형태의 빈 공간','구/OBB/AABB와 애니메이션 범위 선택의 관찰; 실제 collider데이터 추정 금지')
E(14,'축에 나란한 상자의 데이터','box-data',[
 '축 정렬 경계 상자, 즉 에이 에이 비 비는 엑스, 와이, 제트 축에 나란한 여섯 면으로 점들을 감쌉니다.',
 '각 축의 최소 좌표와 최대 좌표를 저장하면 상자가 정해집니다. 최소 좌표 세 개가 한 실제 입력점에서 나올 필요는 없습니다.',
 '중심은 최소와 최대의 평균입니다. 반크기는 최대에서 최소를 뺀 값의 절반이며, 전체 크기와 혼동하지 마세요.',
 '점이 내부에 있는지 보려면 엑스를 엑스 범위에, 와이를 와이 범위에, 제트를 제트 범위에 각각 비교합니다.',
 '세 검사가 모두 참이어야 안쪽입니다. 와이를 엑스 최소값과 비교하는 복사 오류가 있어도 코드가 실행되므로 특히 주의하세요.',
 '물체 축을 따라 회전하는 상자는 오 비 비입니다. 방향 정보를 더 저장하는 대신 길쭉한 물체 주변의 빈 공간을 줄일 수 있습니다.'
],[
 'An axis-aligned bounding box, or AABB, encloses points with six faces parallel to x, y and z.',
 'Store each axis minimum and maximum. The three minima need not belong to one actual input point.',
 'Center is the average of minimum and maximum. Half-extents are half their difference; distinguish them from full size.',
 'For membership, compare x with its x interval, y with its y interval and z with its z interval.',
 'All three tests must pass. A copy error comparing y against x bounds can compile while giving incorrect results.',
 'An oriented bounding box, or OBB, follows object orientation. Extra orientation data can reduce empty space around a slender shape.'
],['AABB: 세 기준축에 평행한 면','min=(min x,min y,min z) / max도 독립','c=(min+max)/2 / e=(max-min)/2','min.x≤p.x≤max.x / y,y / z,z','세 축 모두 통과 / 복사 오류 주의','OBB: 방향도 저장 / 빈 공간 비교'])
E(15,'다섯 점으로 상자 만들기','point-bounds',[
 '책의 다섯 점을 그대로 사용하되, 좌표를 축별로 비교하겠습니다. 첫 점으로 최소와 최대를 초기화합니다.',
 '다음 점마다 엑스, 와이, 제트를 각각 비교합니다. 더 작으면 최소를, 더 크면 최대를 바꿉니다. 활성 코드 줄과 표의 색을 함께 보세요.',
 '모든 점을 읽으면 최소는 마이너스 오, 마이너스 칠, 마이너스 오이고, 최대는 칠, 십일, 팔입니다.',
 '엑스 중심은 일입니다. 와이 중심은 이입니다. 제트 중심은 일 점 오입니다. 전체 크기는 십이, 십팔, 십삼이고 반크기는 육, 구, 육 점 오입니다.',
 '모든 좌표를 영으로 초기화하면 실제 점들이 원점의 한쪽에 있을 때 원점까지 잘못 포함할 수 있습니다. 첫 유효한 점이나 명시적인 빈 상자 상태를 쓰세요.',
 '입력이 비었거나 좌표에 무한대와 비수가 있으면 먼저 처리해야 합니다. 점 개수와 반복 범위도 실제 배열에 맞춰야 안전한 경계를 얻습니다.'
],[
 'Use the book five points and compare one coordinate axis at a time. Initialize both extrema from the first point.',
 'For each next point, update each component minimum or maximum. Follow the highlighted code and matching table colors.',
 'The final minimum is minus five, minus seven, minus five; maximum is seven, eleven, eight.',
 'Center is one, two, one point five. Full size is twelve, eighteen, thirteen; half-extents are six, nine, six point five.',
 'Initializing at zero can wrongly include the origin when every point lies on one side. Use a first valid point or an explicit empty-box state.',
 'Handle empty input, infinity and NaN first. Match the iteration bounds to the actual array length.'
],['5점 / 첫 유효한 점으로 min=max','각 점: min=min_component / max=max_component','min=(-5,-7,-5) / max=(7,11,8)','c=(1,2,1.5) / size=(12,18,13) / e=(6,9,6.5)','원점 초기화 오류 / empty 상태 명시','empty / isfinite / 실제 점 개수 검사'],points=[[7,11,-5],[2,3,8],[-3,3,1],[-5,-7,0],[6,3,4]])
A(16,'경계가 겹쳐도 몸이 닿았다는 뜻은 아닙니다',S,[(578,632)],[
 '팔을 가진 큰 적과 작은 적이 화면을 가로질러 움직입니다. 각 몸을 간단한 상자로 감싸는 모습을 떠올려 보세요.',
 '상자의 모서리에는 실제 몸이 차지하지 않는 빈 공간이 남습니다. 두 상자가 겹쳐도 실제 몸은 떨어져 있을 수 있습니다.',
 '특히 길쭉하거나 기울어진 형태를 월드 축 상자로 감싸면 빈 공간이 커집니다. 윤곽과 경계의 차이를 보는 것이 핵심입니다.',
 '기존 강의에서 배운 이차원 상자 겹침은 빠르게 후보를 찾는 검사로 사용할 수 있습니다. 이제는 그 결과의 한계를 같이 기억하세요.',
 '후보를 찾은 뒤 필요한 정확도의 검사로 넘어갑니다. 복잡한 모양을 어떤 단순한 형태로 대신할지는 게임의 규칙과 비용에 맞춰 정합니다.',
 '다음 그림은 서로 떨어진 두 길쭉한 사각형입니다. 경계 상자만 겹치는 반례를 직접 확인하고, 실제 모양과의 충돌을 구분하겠습니다.'
],[
 'Large and small enemies with extended arms move across the scene. Imagine enclosing each body with a simple box.',
 'Box corners contain space outside the body. The boxes can overlap while the actual bodies remain apart.',
 'World-axis boxes around slender or tilted shapes can contain substantial empty space. Focus on outline versus enclosure.',
 'The earlier2D box-overlap lecture supplies a fast candidate test. Remember the limit of its result.',
 'After filtering, use a test accurate enough for the game rule and cost. Choose proxies deliberately.',
 'Our next diagram gives two separated slender rectangles whose bounding boxes overlap, distinguishing candidates from actual shape contact.'
],'불규칙한 팔·몸의 윤곽과 단순한 상자가 남기는 빈 공간','기존2D충돌을 재제작하지 않고 경계 후보 판정의 오탐 한계를 설명')
E(17,'후보 판정과 정밀 판정','proxy-overlap',[
 '두 가느다란 사각형을 같은 방향으로 기울였습니다. 실제 사각형 사이에는 빈 틈이 있습니다.',
 '하지만 축 정렬 상자는 각각의 엑스와 와이 범위를 조합하므로 두 상자의 영역은 겹칩니다.',
 '상자 겹침이 뜻하는 것은 이 둘을 더 검사하자는 후보입니다. 상세 모양이 닿았다는 결론은 아닙니다.',
 '올바른 경계가 겹치지 않으면 그 안의 모양도 겹칠 수 없습니다. 단, 경계가 실제 현재 모양을 빠짐없이 감싼다는 조건이 필요합니다.',
 '구는 회전해도 모양이 유지되고, 방향 상자는 길쭉한 모양에 더 맞을 수 있습니다. 더 꽉 맞는 경계가 항상 전체 비용을 줄인다고 단정할 수는 없습니다.',
 '경계를 갱신하는 비용, 후보 수와 다음 단계의 비용을 함께 비교하세요. 이 예제는 전체 충돌 엔진이 아니라 경계의 역할을 보여주는 반례입니다.'
],[
 'Tilt two slender rectangles in the same direction. A visible gap separates their actual shapes.',
 'Their axis-aligned boxes combine independent x and y ranges, producing overlapping enclosures.',
 'Box overlap means a candidate for further testing, not confirmed contact of detailed shapes.',
 'Nonoverlapping valid bounds rule out overlap of contained shapes. This requires each bound to contain the entire current shape.',
 'Spheres retain their shape under rotation; oriented boxes may fit slender shapes better. A tighter bound is not automatically cheaper overall.',
 'Compare update cost, candidate count and subsequent test cost. This counterexample explains the role of bounds rather than an entire collision engine.'
],['실제 사각형: 떨어져 있음','AABB: 겹침 / 빈 공간 포함','겹침 → 후보 / 실제 충돌 확정 아님','올바른 경계가 분리됨 → 포함된 모양도 분리','구 / AABB / OBB: 데이터·빈 공간 비교','갱신 + 후보 수 + 정밀 검사 비용'])
E(18,'최소·최대 두 점만 돌리면 틀립니다','rotated-minmax',[
 '상자를 회전시킨 뒤에도 경계를 구하려면 어떻게 해야 할까요? 최소점과 최대점만 돌리는 방법을 먼저 시험해 보겠습니다.',
 '엑스와 와이가 마이너스 일부터 일인 정사각형을 사십오 도 돌립니다. 두 대각 끝점은 엑스가 영인 세로선으로 이동합니다.',
 '이 두 점만 보고 새 경계를 만들면 폭이 영이라고 계산됩니다. 하지만 나머지 두 꼭짓점은 좌우로 루트 이만큼 뻗습니다.',
 '회전 뒤 어느 점이 최소와 최대가 되는지 바뀌었기 때문입니다. 최소라는 이름이 회전 뒤에도 유지되는 것은 아닙니다.',
 '삼차원 상자에서는 여덟 꼭짓점을 모두 변환하고, 변환된 점들의 축별 최소와 최대를 다시 구하면 됩니다.',
 '이 상자는 변환된 원래 상자를 감쌉니다. 원래 물체의 실제 점들만 변환해 만든 경계와는 크기가 다를 수 있다는 점도 곧 비교하겠습니다.'
],[
 'How do we rebuild bounds after rotating a box? First try transforming only its minimum and maximum.',
 'Rotate a square with x and y from minus one to one by forty-five degrees. The two diagonal endpoints move to a vertical line at x zero.',
 'Using only those points falsely gives zero width. The other corners extend to plus and minus square root two.',
 'Rotation changes which corner supplies each extremum. An old minimum does not necessarily remain a minimum.',
 'For a3D box, transform all eight corners and recompute each coordinate minimum and maximum.',
 'This encloses the transformed input box. It can differ from bounds constructed by transforming only the original object points.'
],['잘못된 시도: min,max 두 점만 변환','정사각형 Rz(45°): 두 점 x=0','실제 x 범위: [-√2,+√2]','회전 뒤 극값을 주는 꼭짓점이 달라짐','3D 상자: 8꼭짓점 변환 → 축별 min/max','변환한 상자 / 변환한 실제 점들의 경계 구분'])
A(19,'시점 변화와 물체 경계의 기준축',U,[(1205,1269)],[
 '나무 기둥과 난간이 있는 마을을 걸어갑니다. 같은 구조물을 다른 쪽에서 보며 화면의 가로세로 범위를 비교하세요.',
 '비스듬히 보면 긴 변이 짧게 보이고 다른 면이 드러납니다. 화면 경계가 달라지는 것은 카메라 투영의 영향입니다.',
 '월드 좌표의 경계를 구할 때는 화면 픽셀과 다른 고정 기준축을 사용합니다. 카메라만 바뀌었다면 월드에서 정지한 물체의 경계가 자동으로 바뀌는 것은 아닙니다.',
 '반대로 물체 자체를 월드에서 돌리면 어느 꼭짓점이 엑스 최소를 주는지 바뀔 수 있습니다. 바로 앞 정사각형 실험이 그 경우였습니다.',
 '물체에 붙은 상자와 월드 축에 붙은 상자를 나누어 생각하세요. 지금 움직이는 것은 카메라인지 물체인지부터 확인하는 습관이 도움이 됩니다.',
 '다음 식에서는 카메라 원근을 섞지 않고, 물체의 회전과 크기 변경, 이동으로 이루어진 아핀 변환만 다루겠습니다.'
],[
 'We walk through wooden posts and rails, comparing screen extents of the same structures from different sides.',
 'An oblique view shortens a long edge and reveals another face. These screen changes come from camera projection.',
 'World bounds use fixed coordinate axes rather than screen pixels. Changing only the camera does not automatically change a stationary object world bounds.',
 'Rotating the object itself in the world can change which corner supplies minimum x, as in our square experiment.',
 'Separate an object-attached box from world-axis bounds. First identify whether the camera or the object is moving.',
 'Our next formula handles affine rotation, scale and translation, without combining them with perspective projection.'
],'동일한 나무 기둥을 다른 시점에서 관찰; 카메라 변화와 물체 회전 분리','화면윤곽이 월드AABB증거가 아님을 관찰로 설명; affine계산으로 연결')
E(20,'중심과 반크기로 빠르게 변환하기','affine-bounds',[
 '열벡터 규약에서 아핀 변환은 행렬 에이 곱하기 점, 더하기 이동 벡터입니다. 중심은 같은 식으로 변환하면 됩니다.',
 '반크기는 다릅니다. 중심 주위로 각 성분이 플러스와 마이너스 범위에 있으므로, 새 축의 최대 퍼짐은 각 기여의 절댓값을 더해 얻습니다.',
 '새 반크기는 행렬 에이의 성분별 절댓값에 원래 반크기를 곱한 값입니다. 여기서 절댓값은 행렬식이나 벡터 길이가 아닙니다.',
 '엑스 반크기가 이, 와이 반크기가 일인 상자를 제트축으로 사십오 도 돌리면, 새 엑스와 와이 반크기는 모두 삼을 루트 이로 나눈 값입니다.',
 '새 최소는 새 중심 빼기 새 반크기이고, 새 최대는 둘을 더한 값입니다. 여덟 꼭짓점을 변환하는 방법과 같은 상자 경계를 얻습니다.',
 '이 식은 원래 상자의 아핀 변환에 적용됩니다. 원근 나눗셈이 있는 투영에 그대로 쓰거나, 실제 물체에 항상 가장 작은 경계라고 주장하면 안 됩니다.'
],[
 'With column vectors, an affine transformation is A times a point plus translation. Transform the center with that expression.',
 'Half-extents require a different rule. Signed offsets around the center can combine, so maximum spread sums absolute contributions.',
 'New half-extents are componentwise absolute A times original half-extents. This absolute value is not a determinant or vector norm.',
 'Rotating half-extents two, one around z by forty-five degrees gives both new x and y half-extents three over square root two.',
 'New minimum is transformed center minus new half-extents, and maximum is their sum. This matches transforming all eight box corners.',
 'The formula applies to an affine image of the input box. Do not apply it unchanged to perspective division or claim the tightest bounds of every contained object.'
],['p′=Ap+t / c′=Ac+t','새 축의 최대 퍼짐: 기여 절댓값의 합','e′=|A|e / 성분별 abs','e=(2,1,.5), Rz45° → e′=(3/√2,3/√2,.5)','min′=c′-e′ / max′=c′+e′','아핀 상자 변환 / 원근 투영·최소 mesh 경계 아님'])
A(21,'무엇을 감싸는지 먼저 정하세요',S,[(374,430)],[
 '긴 다리와 큰 적이 함께 보입니다. 다리의 긴 변을 따라가는 상자와 적의 움직이는 몸을 감싸는 상자를 나눠 떠올려 보세요.',
 '상자를 먼저 만들고 그 상자를 변환하면, 상자 안의 빈 공간까지 함께 변환됩니다.',
 '물체의 실제 점들을 먼저 변환하고 경계를 다시 만들면, 빈 공간이 다른 방식으로 줄어들 수 있습니다. 두 방법은 입력 대상이 다릅니다.',
 '어떤 방법이 필요한지 결정하려면 감쌀 대상이 정지한 다리인지, 특정 자세의 몸인지, 여러 자세 전체인지부터 정해야 합니다.',
 '잘못 작은 경계는 실제 물체를 놓치고, 지나치게 큰 경계는 다음 검사 후보를 늘립니다. 정확성과 계산 비용을 함께 보세요.',
 '끝으로 같은 좌표 예제를 두 방법으로 비교하겠습니다. 출발점과 끝점의 계산, 점들의 경계, 변환된 상자의 경계가 연결되는지 직접 확인하세요.'
],[
 'A long bridge and large enemies share the scene. Imagine separate bounds following the bridge and enclosing moving bodies.',
 'Building a box first and then transforming it also transforms the box empty space.',
 'Transforming actual object points first and rebuilding bounds can exclude different empty regions. The methods have different inputs.',
 'Define whether you enclose a stationary bridge, one body pose or all poses before choosing a method.',
 'An undersized bound can miss real geometry; an oversized bound increases subsequent candidates. Compare accuracy and calculation cost.',
 'We will finish by comparing both constructions using the same coordinates, connecting endpoints, point bounds and transformed-box bounds.'
],'긴 다리와 불규칙한 움직이는 몸; 경계가 포함할 대상 구분','실제점 경계와 기존상자 변환의 입력 차이를 연결; 내부mesh/code추정 금지')
E(22,'두 문제로 계산을 이어 보기','bounds-practice',[
 '첫 문제입니다. 출발점이 오, 삼이고 차이 벡터가 마이너스 칠, 오라면 티가 일일 때 끝점은 어디일까요?',
 '두 벡터를 더하면 마이너스 이, 팔입니다. 기울기는 마이너스 칠분의 오이고, 직선식의 절편은 칠분의 사십육입니다.',
 '둘째는 아까의 다섯 점입니다. 점들을 제트축으로 사십오 도 돌린 뒤 직접 경계를 만들면, 엑스는 마이너스 육에서 삼까지 루트 이로 나눈 범위가 됩니다.',
 '와이는 마이너스 십이부터 십팔까지 루트 이로 나눈 범위이고, 제트는 마이너스 오부터 팔입니다. 원래 상자를 변환한 경계는 이보다 넓습니다.',
 '점 집합의 경계와 상자의 경계가 다를 수 있는 이유는 빈 공간입니다. 계산에서 무엇을 입력했는지 확인하면 결과의 차이를 설명할 수 있습니다.',
 '오늘은 형태의 표현, 매개변수 범위와 단위, 구의 판정, 상자의 생성과 변환을 연결했습니다. 다음 편에서는 평면의 거리와 삼각형 안의 위치를 계산하겠습니다.'
],[
 'First problem: origin five, three and displacement minus seven, five. What is the endpoint at t one?',
 'Adding gives minus two, eight. Slope is minus five over seven and intercept is forty-six over seven.',
 'For the second problem, rotate the five points around z by forty-five degrees and build their bounds directly. The x range is minus six to three, each divided by square root two.',
 'The y range is minus twelve to eighteen, divided by square root two; z remains minus five to eight. Transforming the original box produces a wider enclosure.',
 'Empty space explains why point-set bounds can differ from transformed-box bounds. Check the input before interpreting the result.',
 'We connected shape representations, parameter domains and units, sphere tests, and box construction and transformation. Next we will calculate plane distances and positions within triangles.'
],['o=(5,3), δ=(-7,5): p(1)=?','p(1)=(-2,8) / y=(-5/7)x+46/7','변환한 5점: x∈[-6/√2,3/√2]','y∈[-12/√2,18/√2], z∈[-5,8]','점 집합의 경계 ⊆ 변환한 기존 상자의 경계','표현·범위·단위·경계 / 다음: 평면과 삼각형'])
assert [s['id'] for s in scenes]==[f'{i:02}' for i in range(1,23)]
data={'slug':slug,'chapter':9,'part':1,'totalParts':3,'renderModule':'geometry','sourceSections':['9.1','9.2','9.3','9.4'],
 'contract':{'handedness':'right','vector':'column','transform':'Affine p′=Ap+t; axes explicitly defined. Screen perspective is not world coordinates.',
  'parameter':'Dimensionless segment t; infinite ray t≥0; normalized direction distance s has length units.',
  'bookCorrections':'Include conic linear terms; fix perpendicular bisector; componentwise min/max and actual array count; adapt row to column affine formula.',
  'bounds':'abs(A)*e is exact for transformed input box enclosure; not necessarily tight for the enclosed point set; no perspective division.'},
 'scenes':scenes,'coverage':{'9.1':['03','04'],'9.2':['02','05','06','07','08','09','22'],'9.3':['10','11','12'],'9.4':['13','14','15','16','17','18','19','20','21','22']},
 'gameCandidates':{'reviewedAt':'2026-10-06','selected':[{'game':'A Story About My Uncle','sourceId':U,'reason':'Fresh existing-game recording; visible grappling endpoints and wooden geometry viewed from changing camera angles.'},{'game':'Serious Sam2','sourceId':S,'reason':'Fresh recording with round objects/effects, tall creatures and a long bridge. Illustrative proxies do not assert hidden colliders.'}],
 'rejected':[{'game':'Slime Rancher2','reason':'Observed fan policy required public notice and restricted unrelated promotion; does not match publishing defaults.'},{'game':'Portal2 Royalty Free Gameplay','reason':'Uploader requests Like/Subscribe; permission condition unresolved. No account engagement performed.'},{'game':'SUPERHOT','reason':'Short candidate recording alone insufficient for full chapter; fresh bounded sources chosen.'}],
 'historyReview':'Both chosen games and recordings absent from project SOURCES.md before selection. Direct dense-frame review and actual permission description precede this script. All source audio excluded.'}}
out=B/'lessons'/f'{slug}.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'slug':slug,'scenes':len(scenes),'koLines':sum(len(s['ko']) for s in scenes),'koChars':sum(sum(map(len,s['ko'])) for s in scenes),'actualCapacitySeconds':sum(s.get('maxSeconds',0) for s in scenes)}))
