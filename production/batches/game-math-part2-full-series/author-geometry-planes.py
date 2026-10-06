"""Full complementary chapter9 lecture after bounded real-game pixel review."""
from pathlib import Path
import json
B=Path(__file__).parent;slug='game-math-planes-barycentric';scenes=[]
def E(i,title,mode,ko,en,beats):
 assert len(ko)==len(en)==len(beats),(i,len(ko),len(en),len(beats))
 scenes.append(dict(id=f'{i:02}',title=title,kind='explanation',mode=mode,ko=ko,en=en,beats=beats))
def A(i,title,vid,segments,ko,en,focus,claim):
 assert len(ko)==len(en)
 scenes.append(dict(id=f'{i:02}',title=title,kind='actual',sourceId=vid,sourceSegments=[{'in':a,'maxSeconds':b-a} for a,b in segments],**{'in':segments[0][0]},maxSeconds=sum(b-a for a,b in segments),ko=ko,en=en,focus=focus,claim=claim))
U='SSekdYTL4Ck';N='igcymdI4XYM';S='4s7nMfXt8uQ'
E(1,'바닥까지의 거리와 삼각형 안의 위치','overview',[
 '점이 바닥에서 얼마나 떨어져 있는지, 삼각형 안에서는 어디에 있는지 어떻게 계산할까요?',
 '먼저 실제 게임의 발판과 지형을 관찰하고, 평면의 법선과 부호 있는 거리를 구합니다.',
 '이어서 세 점으로 삼각형을 만들고, 넓이와 무게중심 좌표를 숫자로 계산하겠습니다.',
 '마지막에는 평면 밖의 점을 잘못 포함하는 오류를 확인하고, 같은 좌표로 색을 보간합니다.'
],[
 'How do we calculate a point distance from a floor and its location within a triangle?',
 'We will observe game platforms and terrain, then calculate plane normals and signed distances.',
 'Next we will build a triangle from three points and work out its area and barycentric coordinates.',
 'Finally we will reject an off-plane query and use the same coordinates to interpolate color.'
],['높이와 삼각형 안의 위치를 계산하기','발판 관찰 → 평면·법선·거리','세 점 → 넓이 → 무게중심 좌표','평면 밖 판정 → 속성 보간'])
A(2,'발판의 표면을 기준으로 보기',S,[(297,342)],[
 '시리어스 샘 투의 해안에서 길과 다리를 따라 이동합니다. 발밑의 바닥과 다리의 윗면을 보세요.',
 '캐릭터가 표면 위로 떠 있는지, 그 표면에 가까워지는지 구분할 기준이 필요합니다.',
 '그 기준을 수학에서는 평면으로 단순하게 만들 수 있습니다. 실제 발판에는 두께와 끝이 있지만 평면은 무한히 이어집니다.',
 '따라서 표면까지의 거리와 발판 위의 허용 범위는 다른 검사입니다. 거리만 맞아도 옆으로 벗어나 있을 수 있습니다.',
 '카메라가 돌아가면 윗면의 화면 모양도 바뀝니다. 계산은 같은 좌표계에서 정의한 점과 법선을 사용해야 합니다.',
 '이 장면은 기준 표면을 찾는 연습입니다. 게임 내부에서 무한 평면 충돌을 쓰는지는 화면만으로 알 수 없습니다.'
],[
 'We travel along paths and bridges on a Serious Sam2 shoreline. Watch the floor and bridge top surfaces.',
 'A reference lets us distinguish floating above that surface from approaching it.',
 'Mathematics can simplify that reference to a plane. A real platform has thickness and edges; a plane extends infinitely.',
 'Distance to the surface and remaining within the platform footprint are separate tests.',
 'Camera motion changes its screen appearance. Calculations must use points and normals defined in one coordinate frame.',
 'This footage motivates a reference surface; it does not reveal the game internal collision representation.'
],'해안 바닥·다리 윗면·이동; 무한 평면과 유한 다리 구분','평면 거리와 표면 내 범위가 다른 질문임을 실제 표면 관찰에 연결')
E(3,'평면의 방향과 위치를 나누기','affine-plane',[
 '평면은 법선 벡터와 위치를 나타내는 숫자로 표현합니다. 법선은 평면을 따라가는 방향이 아니라 수직인 방향입니다.',
 '평면 위의 점과 법선을 내적하면 일정한 값이 나옵니다. 그 값을 알파벳 디라고 쓰겠습니다.',
 '법선이 영, 일, 영이고 디가 이라면 와이가 이인 모든 점이 평면 위에 있습니다.',
 '와이가 영인 평면은 원점을 지나지만, 와이가 이인 평면은 원점을 지나지 않습니다. 일반 평면은 원점을 지나는 선형 부분공간일 필요가 없습니다.',
 '평면 위의 두 점을 빼면 평면을 따라가는 벡터가 됩니다. 그 차이와 법선의 내적은 영입니다.',
 '법선의 방향을 뒤집으면 앞과 뒤가 바뀝니다. 식을 그대로 유지하려면 디의 부호도 함께 뒤집어야 합니다.'
],[
 'Describe a plane with a normal and a location coefficient. The normal points perpendicular to the surface.',
 'Every point on the plane has the same dot product with its normal. Call that coefficient d.',
 'Normal zero, one, zero and d two describe all points with y equal to two.',
 'The y zero plane contains the origin; the y two plane does not. A general plane is an affine set, not necessarily a linear subspace.',
 'Subtracting two plane points gives a direction along the plane. Its dot product with the normal is zero.',
 'Reversing the normal swaps front and back. Reverse d as well to preserve the same plane.'
],['평면 법선 n: 표면에 수직','n·p=d / 위치 계수 d','n=(0,1,0), d=2 → y=2','원점을 지나는 평면 / 이동한 아핀 평면','n·(p-q)=0','(n,d) → (-n,-d): 같은 평면·반대 앞면'])
E(4,'식의 값과 실제 거리를 구분하기','plane-distance',[
 '점에서 평면 식의 값을 구하려면 법선과 점을 내적하고 디를 뺍니다. 양수는 법선 쪽, 음수는 반대쪽입니다.',
 '법선이 영, 이, 영이고 디가 사인 평면도 와이가 이인 평면입니다. 법선 길이는 이입니다.',
 '점이 사, 오, 마이너스 삼이면 내적은 십입니다. 사를 빼면 육이지만 실제 거리는 육이 아닙니다.',
 '법선의 길이 이로 나누면 부호 있는 거리는 삼입니다. 단위 법선일 때만 식의 값 자체가 거리가 됩니다.',
 '같은 평면을 단위 법선으로 바꾸려면 법선과 디를 둘 다 이로 나눕니다. 법선만 줄이면 평면 위치가 바뀝니다.',
 '법선 길이가 영인 입력은 평면 방향을 정하지 못합니다. 나누기 전에 유효성을 확인하세요.'
],[
 'Evaluate the normal dot point minus d. A positive value lies on the normal side; a negative value lies on the opposite side.',
 'Normal zero, two, zero with d four also defines y two. The normal length is two.',
 'At point four, five, minus three, the dot product is ten. Subtracting four gives six, but six is not the distance.',
 'Divide by normal length two to get signed distance three. Only a unit normal makes the raw residual a distance.',
 'Normalize both the normal and d by two. Normalizing only the normal changes the plane location.',
 'A zero-length normal cannot define a plane direction. Validate before division.'
],['F(p)=n·p-d / 부호로 앞·뒤 판정','n=(0,2,0), d=4 → y=2','p=(4,5,-3): F=10-4=6','signedDistance=F/‖n‖=3','n̂=n/‖n‖, d̂=d/‖n‖','n=0: 유효한 평면 방향 없음'])
A(5,'지형의 높이와 기준선',N,[(96,122),(404,423)],[
 '노이타에서는 캐릭터가 층층이 놓인 지형 사이로 움직입니다. 물의 수평선과 나무 바닥을 기준으로 보세요.',
 '캐릭터가 같은 기준선보다 위에 있는지 아래에 있는지는 높이 차이의 부호로 구분할 수 있습니다.',
 '화면이 따라 움직여도 기준을 함께 보면 상대적인 위치를 찾을 수 있습니다. 화면 맨 아래를 고정된 월드 바닥으로 생각하면 안 됩니다.',
 '단순한 수평면 예제에서는 와이 좌표에서 기준 높이를 빼면 됩니다. 기울어진 표면에서는 수직 높이 대신 법선 방향 거리를 써야 합니다.',
 '여러 층의 바닥을 하나의 무한 평면으로 바꾸면 구멍과 가장자리 정보가 사라집니다. 표면 위치와 경계는 따로 확인해야 합니다.',
 '다음 그림에서는 직접 정의한 평면으로 가장 가까운 점까지 구합니다. 게임의 픽셀 지형이 그 식으로 구현됐다는 뜻은 아닙니다.'
],[
 'In Noita, the character moves through layered terrain. Use the waterline and wooden floor as visible references.',
 'The sign of a height difference distinguishes positions above or below the same reference.',
 'Following camera motion does not prevent relative comparison. The screen bottom is not a fixed world floor.',
 'For a horizontal reference, subtract its height from y. A tilted surface instead needs distance along its normal.',
 'Replacing layered floors with one infinite plane loses holes and edges. Surface distance and boundary checks are separate.',
 'Our next diagram calculates the closest point on an explicitly defined plane; it does not claim to reproduce the pixel terrain implementation.'
],'물 수평선·나무 바닥·캐릭터 높이와 카메라 추적','부호 있는 거리의 기준과 유한 지형 경계의 차이')
E(6,'평면 위의 가장 가까운 점','plane-projection',[
 '아까 점 사, 오, 마이너스 삼에서 와이가 이인 평면까지의 부호 있는 거리는 삼이었습니다.',
 '가장 가까운 점으로 가려면 법선 방향으로 삼만큼 내려갑니다. 결과는 사, 이, 마이너스 삼입니다.',
 '단위 법선이라면 원래 점에서 부호 있는 거리 곱하기 단위 법선을 빼면 됩니다.',
 '정규화하지 않은 법선을 그대로 쓰려면 식의 값을 법선 길이의 제곱으로 나누고, 그 결과를 법선에 곱해 뺍니다.',
 '평면 뒤쪽에 있는 점에서는 거리가 음수라서 법선 방향으로 올라갑니다. 앞뒤 모두 같은 식을 씁니다.',
 '이 투영은 무한 평면의 가장 가까운 점입니다. 삼각형이나 발판의 끝을 넘어가면 유한 표면의 가장 가까운 점은 다시 검사해야 합니다.'
],[
 'Point four, five, minus three has signed distance three from the y two plane.',
 'Move three units opposite its normal. The closest plane point is four, two, minus three.',
 'With a unit normal, subtract signed distance times that normal from the query.',
 'With an unnormalized normal, multiply it by the residual divided by its squared length, then subtract.',
 'Behind the plane, negative signed distance moves the point toward the normal. One formula handles both sides.',
 'This is the closest point on an infinite plane. A finite triangle or platform needs additional edge tests.'
],['p=(4,5,-3), y=2: 거리 +3','p₀=(4,2,-3)','p₀=p-signedDistance·n̂','p₀=p-[(n·p-d)/(n·n)]n','뒤쪽의 음수 거리도 같은 식','무한 평면 투영 / 유한 표면 경계는 별도'])
E(7,'세 점으로 법선 만들기','plane-three-points',[
 '한 직선 위에 있지 않은 세 점은 하나의 평면을 정합니다. 한 꼭짓점에서 다른 두 꼭짓점으로 향하는 변 벡터를 만듭니다.',
 '첫 변이 육, 영, 영이고 둘째 변이 영, 사, 영이면 외적은 영, 영, 이십사입니다.',
 '이 강의는 오른손 좌표계에서 첫 변 외적 둘째 변을 씁니다. 단위 법선은 영, 영, 일입니다.',
 '두 변의 순서를 바꾸면 외적과 법선이 반대로 향합니다. 점 순서와 앞면 규칙을 함께 정하세요.',
 '점 하나와 법선을 내적하면 디를 구할 수 있습니다. 지금은 세 점의 제트가 모두 영이므로 디도 영입니다.',
 '세 점이 한 직선에 있으면 외적이 영입니다. 거의 한 직선에 있는 경우도 오차가 커질 수 있으므로 정규화 전에 검사해야 합니다.'
],[
 'Three noncollinear points determine a plane. Form two edge vectors from the same vertex.',
 'Edges six, zero, zero and zero, four, zero have cross product zero, zero, twenty-four.',
 'Using our right-handed first-edge cross second-edge convention gives unit normal zero, zero, one.',
 'Swapping the edge order reverses the normal. Define winding and front-face conventions together.',
 'Dot any one vertex with the normal to obtain d. All three z coordinates are zero here, so d is zero.',
 'Collinear points yield a zero cross product. Nearly collinear inputs may also be poorly conditioned; check before normalization.'
],['세 점 → 같은 시작점의 두 변 e₁,e₂','e₁=(6,0,0), e₂=(0,4,0)','e₁×e₂=(0,0,24) / n̂=(0,0,1)','오른손 규칙 / 순서 반전 → 법선 반전','d=n·v₁ / 이 예제: z=0','공선·거의 공선 검사 → 정규화'])
A(8,'눈에 보이는 삼각형 표식을 관찰하기',U,[(1320,1366)],[
 '바위의 밝은 삼각형 표식과 그쪽으로 연결되는 그래플을 보세요. 세 꼭짓점과 그 안의 위치를 나눠 생각할 수 있습니다.',
 '카메라가 움직이면 삼각형이 기울고 화면에서 납작해 보입니다. 원래 표면의 형태와 화면 투영은 구분해야 합니다.',
 '세 점의 순서를 정해 둘레를 따라가면 앞면 방향을 정의할 수 있습니다. 순서를 뒤집으면 법선도 반대로 정해집니다.',
 '삼각형 표식이 보인다고 바위 전체의 실제 메시 구성을 알 수 있는 것은 아닙니다. 지금은 눈에 보이는 표식을 수학 예제와 연결합니다.',
 '그래플의 연결 위치가 표식의 어느 꼭짓점에 가까운지 관찰해 보세요. 세 기준점 사이의 위치를 숫자로 표현하는 방법이 뒤에 나옵니다.',
 '먼저 점이 더 많은 표면의 법선을 정리하고, 삼각형의 길이와 넓이부터 계산하겠습니다.'
],[
 'Watch a bright triangular rock marking and the grapple attached nearby. Separate its three vertices from locations within it.',
 'Camera motion tilts and compresses its screen appearance. Distinguish a surface shape from its projection.',
 'Ordering three points around the boundary defines a front-face direction. Reversing that order reverses the chosen normal.',
 'A triangular marking does not reveal the entire rock mesh. We connect visible features to an explicitly defined mathematical example.',
 'Observe which reference vertex lies closest to the attachment. We will express relative locations using three weights.',
 'First we will handle more than three ordered vertices, then calculate triangle lengths and area.'
],'실제 바위 삼각형 표식·연결점·카메라에 따른 화면 투영','삼각형 꼭짓점과 위치의 관찰; 숨은 메시 인덱스 추정 금지')
E(9,'여러 꼭짓점에는 순서가 필요합니다','newell-ordered',[
 '다각형의 꼭짓점이 여러 개라면 아무 세 점만 고르는 방법은 불안정할 수 있습니다. 그 세 점이 거의 한 직선에 있거나 오목한 부분일 수 있기 때문입니다.',
 '뉴웰 방식은 둘레 순서대로 이웃한 점의 기여를 누적합니다. 마지막 점 다음에는 첫 점을 연결합니다.',
 '제트 성분에서는 이웃한 두 점의 엑스 차이와 와이 합을 곱해 더합니다. 다른 성분도 좌표를 순환해서 계산합니다.',
 '둘레 순서를 뒤집으면 법선 방향이 뒤집힙니다. 임의로 섞인 점들을 그대로 넣는 방식이 아닙니다.',
 '법선을 정한 뒤 디는 각 점과 법선의 내적을 평균해서 구할 수 있습니다. 이것은 평균점과 법선의 내적과 같습니다.',
 '원문은 가장 잘 맞는 평면이라고 부르지만, 순서 없는 점군의 최소제곱 평면과 일반적으로 같지는 않습니다. 점의 수와 퇴화 여부도 별도로 확인하세요.'
],[
 'Choosing any three polygon vertices can be unstable when they are nearly collinear or lie at a concave corner.',
 'Newell method accumulates contributions from adjacent vertices in boundary order, including the closing edge.',
 'Its z component sums each neighboring x difference times their y sum. Cycle the coordinates for the other components.',
 'Reversing boundary order reverses the normal. Arbitrarily shuffled points are not valid ordered input.',
 'Once the normal is chosen, average its dot products with vertices to obtain d, equivalently dot the mean point with the normal.',
 'The source calls this best fit, but it is not generally the least-squares plane of an unordered point cloud. Validate point count and degeneracy separately.'
],['임의 세 점: 공선·오목 부분에 주의','둘레 순서 + 마지막→첫 점의 닫힌 변','n_z=Σ(xᵢ-xᵢ₊₁)(yᵢ+yᵢ₊₁)','순서 반전 → 법선 반전 / 점 섞기 금지','d=평균(n·vᵢ)=n·평균(vᵢ)','Newell: 순서 있는 다각형 / 일반 점군 최소제곱 아님'])
E(10,'변의 길이와 각을 연결하기','triangle-laws',[
 '삼각형의 각 꼭짓점 반대편 변을 같은 번호로 부르겠습니다. 세 변의 길이를 더하면 둘레입니다.',
 '변의 길이가 삼, 사, 오인 직각삼각형의 둘레는 십이이고, 그 절반은 육입니다.',
 '한 각과 마주 보는 변의 길이를 사인값으로 나눈 비율은 세 꼭짓점에서 같습니다. 이것이 사인 법칙입니다.',
 '두 변과 그 사이의 각을 알면 코사인 법칙으로 나머지 변을 구합니다. 길이의 제곱을 다룬다는 점을 기억하세요.',
 '지금은 삼 제곱 더하기 사 제곱이 오 제곱입니다. 두 변 사이가 직각이라 코사인 항은 영입니다.',
 '각도 함수의 라디안과 도 단위를 섞지 마세요. 각이나 변을 구한 뒤에도 양의 길이와 삼각형 성립 조건을 확인해야 합니다.'
],[
 'Give each edge the same index as its opposite vertex. Adding the three edge lengths gives the perimeter.',
 'A three-four-five right triangle has perimeter twelve and semiperimeter six.',
 'Edge length divided by the sine of its opposite angle is the same at all three vertices: the sine law.',
 'Given two edges and their included angle, the cosine law finds the remaining edge using squared lengths.',
 'Here three squared plus four squared equals five squared. The right angle makes the cosine term zero.',
 'Do not mix degrees and radians. Validate positive lengths and triangle feasibility after solving.'
],['vᵢ 반대편 변의 길이 aᵢ / 둘레 P','3·4·5: P=12, s=P/2=6','a₁/sinθ₁=a₂/sinθ₂=a₃/sinθ₃','a₁²=a₂²+a₃²-2a₂a₃cosθ₁','3²+4²=5² / cos90°=0','각도 단위 / 길이>0 / 삼각부등식'])
A(11,'세 기준점 사이에서 위치 찾기',N,[(423,442),(446,472)],[
 '노이타의 나무 발판 끝과 바위의 모서리를 보세요. 가까이 보이는 세 위치를 기준점으로 선택할 수 있습니다.',
 '캐릭터가 한 기준점에서 다른 기준점 쪽으로 이동하면, 어느 점에 가까운지가 바뀝니다.',
 '엑스와 와이 좌표로 설명할 수도 있지만, 세 기준점의 가중치를 쓰면 삼각형과 함께 움직이는 설명이 가능합니다.',
 '카메라가 이동할 때는 세 기준점도 같이 추적해야 합니다. 서로 다른 화면에서 읽은 픽셀 좌표를 섞으면 위치 관계가 틀어집니다.',
 '또한 기준점을 골랐다는 사실만으로 실제 바닥 전체가 하나의 삼각형이 되지는 않습니다. 사이에 빈 공간이 있을 수도 있습니다.',
 '다음 예제는 우리가 직접 정한 삼각형입니다. 넓이를 먼저 구하고, 그 안과 밖의 위치를 세 숫자로 나타내겠습니다.'
],[
 'Observe platform ends and rock corners in Noita. We can choose three visible locations as reference points.',
 'Movement from one reference toward another changes which point the character is nearer.',
 'Cartesian coordinates describe the location; three weights describe it relative to a triangle that moves with its references.',
 'Track all three references when the camera moves. Do not combine pixels from incompatible screen frames.',
 'Choosing three points does not make the entire ground a triangle; gaps may lie between them.',
 'Our next example defines its own triangle, calculates area, and expresses inside and outside positions with three numbers.'
],'발판 끝·바위 모서리 세 기준과 상대 위치; 빈 공간도 확인','직접 정의한 삼각형 좌표의 동기; 실제 지형을 삼각형으로 단정하지 않음')
E(12,'같은 넓이를 세 방법으로 구하기','triangle-area',[
 '꼭짓점이 영, 영과 사, 영과 영, 삼인 삼각형입니다. 밑변 사에 높이 삼을 곱하고 이로 나누면 넓이는 육입니다.',
 '세 변 삼, 사, 오를 알면 헤론 공식을 쓸 수 있습니다. 둘레의 절반 육에서 각 변을 뺀 값을 곱합니다.',
 '루트 안은 육 곱하기 삼 곱하기 이 곱하기 일, 즉 삼십육입니다. 제곱근은 육입니다.',
 '두 변 벡터의 외적 길이는 평행사변형 넓이입니다. 절반을 취하면 삼각형 넓이가 되고, 이 예제에서는 십이를 이로 나눕니다.',
 '이차원에서는 외적에 해당하는 행렬식에 부호가 있습니다. 꼭짓점 순서를 뒤집으면 부호가 바뀌지만 넓이의 크기는 같습니다.',
 '삼차원에서 외적의 길이를 쓰면 방향의 부호는 사라집니다. 넓이와 앞면 방향을 같은 숫자라고 생각하지 마세요.'
],[
 'Use vertices zero, zero; four, zero; and zero, three. Base four times height three divided by two gives area six.',
 'With side lengths three, four and five, Heron formula uses semiperimeter six and its differences from each edge.',
 'The radicand is six times three times two times one, or thirty-six. Its square root is six.',
 'Edge cross-product magnitude gives parallelogram area; half gives triangle area. Here divide twelve by two.',
 'In2D, the corresponding determinant has a sign. Reversing winding changes the sign but not area magnitude.',
 'Taking a3D cross-product magnitude discards direction. Distinguish area from front-face orientation.'
],['A=bh/2=4×3/2=6','Heron: A=√[s(s-a)(s-b)(s-c)]','√(6×3×2×1)=√36=6','A=‖e₁×e₂‖/2=12/2=6','2D signedArea=det(e₁,e₂)/2','3D 넓이: 외적 길이 / 방향은 법선'])
E(13,'세 숫자로 삼각형 위치 표현하기','barycentric-basis',[
 '무게중심 좌표는 세 꼭짓점의 가중치를 나타냅니다. 세 가중치의 합은 일이어야 합니다.',
 '각 꼭짓점에 가중치를 곱해서 더하면 위치가 나옵니다. 첫 꼭짓점 자체는 일, 영, 영입니다.',
 '첫째와 둘째 꼭짓점의 중간은 영 점 오, 영 점 오, 영입니다. 세 값이 모두 삼분의 일이면 꼭짓점 평균 위치입니다.',
 '세 숫자를 쓰지만 합이 일이라 독립적으로 고를 수 있는 값은 두 개입니다. 삼각형의 표면이 이차원이기 때문입니다.',
 '셋째 꼭짓점을 기준으로 쓰면 다른 두 꼭짓점에서 셋째를 뺀 변이 두 축이 됩니다. 이 축이 직각이거나 단위 길이일 필요는 없습니다.',
 '퇴화하지 않은 삼각형의 평면 위에서 가중치가 모두 영 이상이면 내부나 경계입니다. 음수 가중치도 의미가 있으며, 그때는 삼각형 밖의 점입니다.'
],[
 'Barycentric coordinates give weights for three vertices. Their sum must be one.',
 'Multiply each vertex by its weight and add. The first vertex has coordinates one, zero, zero.',
 'The midpoint of the first two vertices is one half, one half, zero. Equal one-third weights give the vertex average.',
 'Although written as three numbers, only two are independent because their sum is fixed. A triangle surface is two-dimensional.',
 'Using the third vertex as origin gives axes first-minus-third and second-minus-third. They need not be orthogonal or unit length.',
 'On a nondegenerate triangle plane, nonnegative weights describe its interior and boundary. Negative weights meaningfully describe outside points.'
],['λ₁+λ₂+λ₃=1','p=λ₁v₁+λ₂v₂+λ₃v₃','꼭짓점 / 변의 중간 / 꼭짓점 평균','세 숫자·독립 값 두 개','p=v₃+λ₁(v₁-v₃)+λ₂(v₂-v₃)','모두 λ≥0: 내부·경계 / 음수: 바깥'])
A(14,'삼각형의 기준을 함께 옮기기',U,[(1519,1577)],[
 '다른 바위로 연결되며 표식의 화면 위치가 바뀝니다. 연결 표식과 그 주변에서 세 기준점을 골라 보세요.',
 '표면과 카메라가 움직여도, 같은 세 꼭짓점으로 정의한 상대 가중치는 위치를 설명할 기준이 될 수 있습니다.',
 '꼭짓점 하나를 향해 다가가면 그 꼭짓점의 가중치는 일을 향합니다. 변 위의 위치는 반대편 꼭짓점의 가중치가 영입니다.',
 '다만 화면에서 가깝게 보이는 정도와 삼차원 공간에서의 가중치는 같다고 단정할 수 없습니다. 원근 투영이 모양을 바꾸기 때문입니다.',
 '지금 보이는 그래플 연결점의 실제 좌표를 추출한 것은 아닙니다. 표식은 다음 수치 예제가 무엇을 계산하는지 보여주는 기준입니다.',
 '이제 세 좌표에 가중치를 곱해 직접 더해 보고, 음수가 들어갔을 때 왜 삼각형 밖으로 나가는지 확인하겠습니다.'
],[
 'Connecting to another rock changes the marking screen position. Choose three reference points around the attachment marking.',
 'Weights relative to the same three vertices provide a location reference even as a surface or camera moves.',
 'Approaching a vertex makes its weight approach one. A point on its opposite edge has zero weight for it.',
 'Screen proximity is not automatically the3D barycentric relationship because perspective changes the projection.',
 'We have not extracted the real attachment coordinates. Visible markings motivate the explicitly defined numerical example.',
 'Now we will multiply vertices by weights and see how a negative weight places a point outside.'
],'표식·연결 위치의 상대 관계와 원근 변화','무게중심 좌표의 기준점 의존성과 화면 원근의 차이')
E(15,'안쪽과 바깥쪽을 직접 계산하기','barycentric-worked',[
 '삼차원 꼭짓점을 영, 영, 영과 육, 영, 영과 영, 사, 영으로 정하겠습니다. 모두 제트가 영인 같은 평면에 있습니다.',
 '가중치 영 점 이, 영 점 삼, 영 점 오는 합이 일입니다. 엑스는 육 곱하기 영 점 삼, 와이는 사 곱하기 영 점 오입니다.',
 '결과는 일 점 팔, 이, 영입니다. 세 가중치가 영 이상이므로 삼각형 내부입니다.',
 '이번에는 마이너스 영 점 이, 영 점 칠, 영 점 오를 넣겠습니다. 합은 여전히 일이지만 첫 가중치가 음수입니다.',
 '엑스는 사 점 이, 와이는 이이고 제트는 영입니다. 첫 꼭짓점 반대편 변을 넘어 바깥으로 나갑니다.',
 '좌표의 단위는 공간의 길이이고, 가중치는 비율입니다. 음수 가중치를 무조건 잘못된 계산으로 버리면 바깥 위치 정보를 잃습니다.'
],[
 'Define3D vertices zero, zero, zero; six, zero, zero; and zero, four, zero. All lie in the z zero plane.',
 'Weights point two, point three and point five sum to one. Compute x as six times point three and y as four times point five.',
 'The result is one point eight, two, zero. All weights are nonnegative, so it lies inside.',
 'Now use minus point two, point seven and point five. Their sum is still one, but the first weight is negative.',
 'The result four point two, two, zero lies beyond the edge opposite the first vertex.',
 'Position has length units; weights are dimensionless ratios. Rejecting every negative weight loses valid outside-location information.'
],['v₁=(0,0,0), v₂=(6,0,0), v₃=(0,4,0)','λ=(.2,.3,.5), 합=1','p=(1.8,2,0): 내부','λ=(-.2,.7,.5), 합=1','p=(4.2,2,0): v₁ 반대편 바깥','좌표: 길이 / 가중치: 비율'])
E(16,'넓이 비율에서 가중치 구하기','barycentric-areas',[
 '반대로 점의 위치를 알고 가중치를 구할 수도 있습니다. 점과 두 꼭짓점이 만드는 부분 삼각형 넓이를 전체 넓이로 나눕니다.',
 '가중치 영 점 이, 영 점 삼, 영 점 오인 내부 점에서는 세 부분의 넓이가 전체의 이십, 삼십, 오십 퍼센트입니다.',
 '중요한 것은 같은 꼭짓점 순서로 구한 부호 있는 넓이를 쓰는 것입니다. 절댓값만 쓰면 바깥쪽의 음수를 잃습니다.',
 '점이 첫 꼭짓점 반대편으로 넘어가면 그 부분의 부호가 뒤집히며 첫 가중치가 음수가 됩니다.',
 '전체 삼각형의 부호를 뒤집어도 분자와 분모가 함께 뒤집혀 같은 가중치가 나옵니다. 순서를 일관되게 쓰세요.',
 '전체 넓이가 영이면 나눌 수 없습니다. 너무 가느다란 삼각형도 작은 좌표 오차를 큰 가중치 오차로 키울 수 있습니다.'
],[
 'Given a position, obtain each weight from a signed subtriangle area divided by the whole signed area.',
 'For the inside example, the subareas are twenty, thirty and fifty percent of the total.',
 'Keep consistent vertex order and signed areas. Absolute areas discard the negative weight of an outside point.',
 'Crossing the edge opposite the first vertex reverses that subarea sign and makes its weight negative.',
 'Reversing all winding reverses numerator and denominator together, preserving weights. Be consistent.',
 'A zero whole area cannot be divided by. Very thin triangles may amplify small coordinate errors.'
],['λᵢ=signedArea(부분)/signedArea(전체)','내부: .2 / .3 / .5','부호 보존: 절댓값만 사용하면 바깥 정보 손실','반대편 변 넘어가기 → 해당 λ<0','일관된 순서: 분자·분모 부호 함께 반전','퇴화·가느다란 삼각형: 분모·오차 검사'])
A(17,'높이가 다른 표면을 한 그림으로 보면',N,[(472,487),(525,558)],[
 '캐릭터가 다른 높이의 발판을 오가고, 멀리 있는 발판도 같은 화면에 들어옵니다. 보이는 겹침과 실제 같은 표면은 구분하세요.',
 '이차원 게임 화면에서는 위치가 두 성분으로 보이지만, 삼차원 게임이라면 깊이가 다른 점이 화면에서 겹칠 수도 있습니다.',
 '삼각형 안처럼 보이는 투영 위치만으로 삼차원 표면 위에 있다고 판단하면 오류가 납니다.',
 '평면까지의 거리 검사와 그 평면 안에서의 가중치 검사를 따로 하면 이 두 질문을 나눌 수 있습니다.',
 '또한 물체가 발판의 경계를 지나가면 같은 평면 높이더라도 발판 밖입니다. 넓이 비율의 음수 가중치를 기억하세요.',
 '다음 그림에서는 투영 위치는 똑같고 깊이만 다른 두 점을 나란히 놓아 이 오류를 확인합니다.'
],[
 'The character moves among ledges at different heights. Distinguish visual overlap from occupying the same surface.',
 'This2D footage exposes two position components; in3D, different depths may project to the same screen location.',
 'An apparently inside projected location alone does not prove that a3D query lies on a triangle surface.',
 'Separate distance-to-plane validation from within-plane barycentric tests.',
 'Passing a platform edge can also leave its finite footprint while keeping the same reference height. Remember negative outside weights.',
 'Our diagram will compare two points with identical projection and different depths.'
],'다른 높이 발판·공중 이동·유한 끝; 깊이 오류는 별도3D그림에서 검증','실제2D관찰의 제한을 밝히고 공면성·경계 판정을 분리')
E(18,'투영은 평면 위 검사까지 해주지 않습니다','barycentric-coplanarity',[
 '아까 내부 점은 일 점 팔, 이, 영입니다. 이번에는 엑스와 와이는 그대로 두고 제트만 칠로 바꿉니다.',
 '엑스 와이 평면으로 보면 두 점은 같은 위치입니다. 하지만 제트가 칠인 점은 삼각형 평면에서 칠만큼 떨어져 있습니다.',
 '투영해서 가중치를 계산할 때는 법선의 절댓값이 가장 큰 성분의 좌표를 버리면 안정적인 면을 고르기 쉽습니다.',
 '그렇다고 버린 좌표가 중요하지 않은 것은 아닙니다. 먼저 평면까지의 거리를 검사하고, 투영한 좌표로 내부 여부를 검사하세요.',
 '평면과 충분히 가깝다고 볼 허용 오차는 공간의 단위와 크기에 맞춰 정합니다. 무게중심 가중치의 오차는 별도의 비율 단위입니다.',
 '입력 좌표가 유한한지, 법선과 넓이 분모가 유효한지도 확인합니다. 내부 판정 하나가 모든 입력 검증을 대신하지 않습니다.'
],[
 'Our inside point was one point eight, two, zero. Keep x and y but change z to seven.',
 'Both points have the same XY projection, but the new point is seven units off the triangle plane.',
 'For a projected solve, dropping the axis with largest absolute normal component helps choose a well-conditioned projection.',
 'The discarded coordinate still matters. Check plane distance separately before testing projected weights.',
 'Plane proximity tolerance has spatial units and scale; barycentric tolerance uses dimensionless ratios.',
 'Also validate finite inputs, normal length and the area denominator. An inside test is not complete input validation.'
],['p=(1.8,2,0) / q=(1.8,2,7)','XY 투영 같음 / 평면 거리 0 대 7','|nᵢ| 최대 축을 버리고 투영 계산','공면성 검사 + 삼각형 내부 검사','거리 오차: 길이 / λ 오차: 비율','finite / normal / denominator 검증'])
A(19,'가까운 모서리 세 개를 함께 추적하기',N,[(787,821),(825,840)],[
 '노이타에서 좁은 발판과 기울어진 지형 사이로 이동합니다. 가까운 세 모서리를 골라 같이 추적해 보세요.',
 '세 점을 연결한 삼각형이 가늘어지면, 작은 이동도 가중치의 큰 변화로 나타날 수 있습니다.',
 '넓이가 거의 영인 기준을 쓰면 세 숫자가 계산돼도 안정적이라는 보장은 없습니다. 수치와 입력 모양을 함께 봐야 합니다.',
 '지형이 바뀌거나 기준점이 다른 곳으로 바뀌면 같은 가중치도 다른 위치를 뜻합니다. 위치와 기준 삼각형은 한 쌍입니다.',
 '실제 화면의 경계에는 오목한 부분과 빈 공간이 있습니다. 세 기준점 사이를 채운 수학 삼각형이 지형 전체를 대신하지 않습니다.',
 '오늘의 계산은 한 평면과 한 삼각형에 관한 것입니다. 더 복잡한 경계를 여러 삼각형으로 나누는 문제는 다음 편에서 다룹니다.'
],[
 'We move among narrow ledges and slanted terrain in Noita. Track three nearby corners together.',
 'A thin reference triangle can turn a small position change into a large weight change.',
 'Producing three numbers does not guarantee numerical stability for nearly zero area. Inspect the input shape as well.',
 'Changing reference vertices changes the position represented by the same weights. Coordinates and their triangle form one description.',
 'Real boundaries contain notches and gaps; filling a mathematical triangle between references does not reproduce the terrain.',
 'Today concerns one plane and triangle. The next lecture partitions more complex boundaries into triangles.'
],'좁은 발판·모서리·오목 빈 공간의 실제 관찰','삼각형 기준의 퇴화와 다음 다각형 분할 주제로 연결')
E(20,'같은 가중치로 색도 보간하기','barycentric-attributes',[
 '무게중심 좌표는 위치만 만들지 않습니다. 세 꼭짓점에 다른 값을 주면 같은 가중치로 그 값도 섞을 수 있습니다.',
 '첫 꼭짓점에 빨강, 둘째에 초록, 셋째에 파랑을 주겠습니다. 단순한 선형 색 예제입니다.',
 '가중치 영 점 이, 영 점 삼, 영 점 오를 쓰면 색 세 성분도 영 점 이, 영 점 삼, 영 점 오가 됩니다.',
 '변의 중간에서는 두 꼭짓점의 값을 반씩 섞고, 꼭짓점에서는 그 꼭짓점의 값이 그대로 나옵니다.',
 '높이, 텍스처 좌표처럼 꼭짓점마다 정의한 다른 속성도 같은 방식으로 보간할 수 있습니다. 정규화가 필요한 방향은 보간 뒤 다시 확인합니다.',
 '지금은 삼각형 표면의 아핀 보간입니다. 원근 투영된 화면의 가중치를 그대로 쓰는 문제는 뒤의 렌더링에서 따로 다룹니다.'
],[
 'Barycentric coordinates combine attributes as well as positions. Assign different values to the three vertices.',
 'Give the vertices red, green and blue in an explicitly linear color example.',
 'Weights point two, point three and point five produce those same three color components.',
 'An edge midpoint averages its endpoints; a vertex reproduces its own attribute.',
 'The same construction interpolates defined heights or texture coordinates. Direction attributes that require normalization need a further check.',
 'This is affine interpolation on a triangle surface. Perspective-correct interpolation in screen space belongs to the rendering chapter.'
],['속성 a(p)=Σλᵢaᵢ','예제: 선형 RGB의 빨강·초록·파랑','λ=(.2,.3,.5) → RGB=(.2,.3,.5)','꼭짓점 그대로 / 변 중간 평균','높이·UV·방향 / 필요한 후처리 확인','표면 아핀 보간 / 원근 보정은 렌더링에서'])
A(21,'표면의 위치와 색을 함께 보기',S,[(678,740)],[
 '시리어스 샘 투의 색이 다른 지붕과 벽을 보세요. 같은 물체 표면에서도 위치에 따라 눈에 들어오는 색과 밝기가 다릅니다.',
 '표면 위의 위치를 구한 뒤 그 위치의 속성을 구한다는 두 단계가 그래픽스의 중요한 질문입니다.',
 '삼각형의 꼭짓점마다 값을 저장했다면 아까의 가중치로 중간 값을 만들 수 있습니다. 이것은 우리가 정의한 수학적 예제입니다.',
 '실제 화면의 색은 텍스처와 조명, 효과 등 여러 요인의 결과일 수 있습니다. 이 영상만으로 꼭짓점 색 보간을 쓴다고 확인한 것은 아닙니다.',
 '카메라가 움직여도 같은 표면의 기준 위치를 유지해야 합니다. 화면 좌표와 물체 표면 좌표를 섞지 않는 것이 중요합니다.',
 '마지막 문제에서는 평면의 거리와 삼각형 가중치를 함께 검증합니다. 어디에 있는지를 먼저 확인하고, 그 위치의 속성을 계산하세요.'
],[
 'Observe differently colored roofs and walls in Serious Sam2. Appearance varies with surface location.',
 'Finding a surface position and then finding its attributes are two connected graphics questions.',
 'If values are stored per triangle vertex, our weights construct intermediate values. This is the mathematical model we explicitly defined.',
 'The real image may involve textures, lighting and effects. Footage alone does not confirm vertex-color interpolation.',
 'Preserve surface references as the camera moves. Do not mix screen coordinates with object-surface coordinates.',
 'Our final problems validate plane distance and triangle weights together: locate the point, then calculate its attributes.'
],'색이 다른 실제 지붕·벽·표면과 이동하는 카메라','표면 위치→속성 질문의 연결; 게임 내부 셰이더 방식은 추정하지 않음')
E(22,'거리·평면·가중치를 함께 확인하기','planes-practice',[
 '첫 문제입니다. 법선 영, 이, 영과 디 사인 평면에서 점 사, 오, 마이너스 삼까지의 거리는 얼마일까요?',
 '식의 값은 육이지만 법선 길이 이로 나누어 거리는 삼입니다. 가장 가까운 평면 점은 사, 이, 마이너스 삼입니다.',
 '둘째는 제트가 영인 삼각형입니다. 가중치 영 점 이, 영 점 삼, 영 점 오가 만드는 점은 일 점 팔, 이, 영입니다.',
 '엑스와 와이는 같고 제트가 칠인 점은 투영 위치만 같습니다. 평면 밖이므로 표면 내부라는 판정을 하면 안 됩니다.',
 '계산 순서는 유효한 입력, 평면까지의 거리, 삼각형의 가중치, 원하는 속성입니다. 단계마다 단위와 허용 오차도 확인하세요.',
 '오늘은 평면의 방향과 위치, 거리와 투영, 삼각형 넓이와 무게중심 좌표를 연결했습니다. 다음 편에서는 서로 다른 중심과 다각형 분할을 설명하겠습니다.'
],[
 'First: find the distance from four, five, minus three to the plane with normal zero, two, zero and d four.',
 'Residual six divided by normal length two gives distance three. The closest plane point is four, two, minus three.',
 'Second: on our z zero triangle, weights point two, point three and point five construct one point eight, two, zero.',
 'Changing only z to seven preserves the projection but leaves the plane. It must not pass a triangle-surface membership test.',
 'Check valid inputs, plane distance, triangle weights and desired attributes in that order, with appropriate units and tolerances.',
 'We connected plane orientation and location, distance and projection, triangle area and barycentric coordinates. Next we will compare centers and partition polygons.'
],['n=(0,2,0), d=4, p=(4,5,-3): 거리?','거리=3 / 투영=(4,2,-3)','λ=(.2,.3,.5) → p=(1.8,2,0)','q=(1.8,2,7): 투영 같음·평면 밖','유효 입력 → 공면성 → 가중치 → 속성','다음: 세 중심의 차이와 다각형 분할'])
assert [s['id'] for s in scenes]==[f'{i:02}' for i in range(1,23)]
data={'slug':slug,'chapter':9,'part':2,'totalParts':3,'renderModule':'geometry_planes','sourceDependencies':['manim/projects/game-math-part2-full-series/geometry.py'],
 'sourceSections':['9.5','9.6.1–9.6.4'],'contract':{'handedness':'right','vector':'column','plane':'n·p=d; normalize n and d together; nonzero finite normal. Plane residual is distance only for a unit normal.',
 'normal':'Right-handed e1×e2 with both edges at one vertex. Winding and front-face convention explicitly stated.',
 'newell':'Ordered closed polygon method; not generic unordered point-cloud least squares. Mean d after normal selection.',
 'barycentric':'Sum1; nonnegative inside a nondegenerate triangle; signed subareas; independent coplanarity check; largest-normal-component projection.',
 'attributes':'Defined linear RGB/affine surface interpolation, not assumed proprietary implementation; perspective-correct screen interpolation deferred to chapter10.'},
 'coverage':{'9.5':['02','03','04','05','06','07','08','09','22'],'9.6.1':['10'],'9.6.2':['12'],'9.6.3':['11','13','14','15','19','20','21'],'9.6.4':['16','17','18','22']},'scenes':scenes,
 'gameCandidates':{'reviewedAt':'2026-10-06','selected':[{'game':'Noita','sourceId':N,'reason':'Different recording from prior use; layered terrain, ledges and reference water heights directly illustrate side, footprint and reference-point questions.'},{'game':'A Story About My Uncle','sourceId':U,'reason':'Fresh nonoverlapping intervals from chapter9 first source: wooden surfaces, cyan triangle markings and relative attachment positions.'},{'game':'Serious Sam2','sourceId':S,'reason':'Fresh night interval with colored surfaces for position-to-attribute observation; shader implementation not inferred.'}],
 'rejected':[{'game':'Slime Rancher2','reason':'Observed notice/promotion conditions do not match publishing defaults.'},{'game':'Portal2 Royalty Free Gameplay','reason':'Uploader engagement condition unresolved; no engagement performed.'}],
 'historyReview':'Full source history reviewed. Noita title has prior use but this NCR recording is new. All chosen intervals are directly reviewed and do not overlap the first geometry lecture. Source audio excluded.'}}
out=B/'lessons'/f'{slug}.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'slug':slug,'scenes':len(scenes),'koLines':sum(len(s['ko']) for s in scenes),'koChars':sum(sum(map(len,s['ko'])) for s in scenes),'actualCapacitySeconds':sum(s.get('maxSeconds',0) for s in scenes)}))
