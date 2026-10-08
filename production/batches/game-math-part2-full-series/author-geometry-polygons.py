"""Chapter9 final lecture, authored after fresh bounded game pixel review."""
from pathlib import Path
import json
B=Path(__file__).parent;slug='game-math-polygons-triangulation';scenes=[]
def E(i,title,mode,ko,en,beats):
 assert len(ko)==len(en)==len(beats)
 scenes.append(dict(id=f'{i:02}',title=title,kind='explanation',mode=mode,ko=ko,en=en,beats=beats))
def A(i,title,vid,segments,ko,en,focus,claim):
 assert len(ko)==len(en)
 scenes.append(dict(id=f'{i:02}',title=title,kind='actual',sourceId=vid,sourceSegments=[{'in':a,'maxSeconds':b-a} for a,b in segments],**{'in':segments[0][0]},maxSeconds=sum(b-a for a,b in segments),ko=ko,en=en,focus=focus,claim=claim))
D='dorfromantik-official-trailer';N='igcymdI4XYM';S='4s7nMfXt8uQ';U='SSekdYTL4Ck'
E(1,'어떤 중심을 쓰고, 어떻게 나눌까요?','overview',[
 '삼각형의 중심은 하나일까요? 안으로 움푹 들어간 지형은 어떻게 삼각형으로 나눌까요?',
 '먼저 실제 게임의 타일과 지형을 보며, 무게중심과 내심, 외심이 답하는 질문을 구분합니다.',
 '이어서 다각형의 경계와 볼록성을 확인하고, 한 점에서 부채꼴로 나누는 방법의 한계를 보겠습니다.',
 '마지막에는 오목한 예제를 귀 잘라내기로 분할하고, 빠진 영역과 가느다란 삼각형을 검사하겠습니다.'
],[
 'Does a triangle have just one center, and how can we partition terrain with an inward notch?',
 'We will observe real game tiles and terrain, then distinguish the questions answered by centroid, incenter and circumcenter.',
 'Next we will validate polygon boundaries and convexity, and examine the limits of a triangle fan.',
 'Finally we will partition a concave example by ear clipping and check coverage and thin triangles.'
],['중심 선택과 안전한 삼각형 분할','실제 타일·지형 → 무게중심·내심·외심','경계·볼록성 → 부채꼴 분할의 한계','귀 잘라내기 → 영역·품질 검사'])
A(2,'타일을 놓을 때 필요한 기준',D,[(21,56),(67,79.5)],[
 '도르프로만틱에서 육각형 타일을 돌려 빈자리에 놓습니다. 타일의 가운데와 바깥쪽 변을 함께 보세요.',
 '가운데에 표시를 놓는 일과, 안쪽에 원을 넣는 일은 서로 다른 질문입니다.',
 '타일을 둘러싸는 원의 중심을 찾는 질문도 있습니다. 모양에 따라 세 질문의 답이 달라집니다.',
 '정육각형처럼 대칭이 좋은 모양에서는 중심들이 겹쳐 보입니다. 일반 삼각형에서도 같다고 생각하면 안 됩니다.',
 '타일이 연결되면 전체 땅의 윤곽도 바뀝니다. 타일 하나의 중심과 연결된 영역의 중심을 구분하세요.',
 '이제 변의 길이가 삼, 사, 오인 삼각형으로 비교합니다. 게임이 그 중심 계산을 쓴다고 추정하지 않고, 우리가 정의한 예제를 풉니다.'
],[
 'In Dorfromantik, hexagonal tiles rotate and enter empty positions. Observe each tile center and outer edges together.',
 'Placing a central marker and fitting an interior circle ask different questions.',
 'The center of a circle through the corners answers another question. Shape can change all three answers.',
 'Symmetric regular hexagons make centers appear coincident; an arbitrary triangle need not do so.',
 'Connected tiles change the entire land outline. Distinguish one tile from the combined region.',
 'We will compare a three-four-five triangle in our own defined example, without inferring the game implementation.'
],'실제 타일 회전·배치, 가운데·변·연결된 영역','중심이라는 말의 목적을 구분하는 질문')
E(3,'세 중심이 답하는 세 질문','center-questions',[
 '삼각형에서 무게중심은 세 꼭짓점 좌표의 평균입니다. 세 중선이 만나는 점이기도 합니다.',
 '내심은 세 변까지의 거리가 같은 점입니다. 그 점을 중심으로 안에 닿는 원을 그릴 수 있습니다.',
 '외심은 세 꼭짓점까지의 거리가 같은 점입니다. 그 점을 중심으로 꼭짓점을 지나는 원을 그립니다.',
 '좌표 평균, 변까지의 거리, 꼭짓점까지의 거리입니다. 무엇이 같아야 하는지 먼저 정하세요.',
 '세 꼭짓점이 영, 영과 사, 영과 영, 삼인 직각삼각형을 같은 그림에서 비교하겠습니다.',
 '이 예제에서는 세 중심이 서로 다릅니다. 모두 중심이라고 부르지만 역할을 바꾸어 쓸 수는 없습니다.'
],[
 'The centroid is the average of three triangle vertices and the intersection of the medians.',
 'The incenter is equally distant from the three sides and centers a circle tangent inside them.',
 'The circumcenter is equally distant from the three vertices and centers a circle through them.',
 'Coordinate average, distance to sides, and distance to vertices: decide what should be equal first.',
 'Compare the right triangle with vertices zero-zero, four-zero and zero-three on the same diagram.',
 'The three centers differ here. Their shared name does not make their roles interchangeable.'
],['G: 꼭짓점 평균·중선 교점','I: 세 변까지 같은 거리','O: 세 꼭짓점까지 같은 거리','평균 / 변 거리 / 꼭짓점 거리','v₀=(0,0), v₁=(4,0), v₂=(0,3)','목적이 다른 세 중심'])
E(4,'무게중심은 무엇의 평균일까요?','centroid',[
 '무게중심은 세 꼭짓점을 더해서 삼으로 나눕니다. 지금은 사 나누기 삼, 일입니다.',
 '첫 꼭짓점에서 반대편 변의 중점으로 중선을 그리면, 무게중심은 꼭짓점 쪽에서 삼분의 이 지점입니다.',
 '나머지 두 중선도 같은 점을 지납니다. 가중치는 세 꼭짓점에 각각 삼분의 일입니다.',
 '밀도가 일정한 삼각형 판의 질량 중심도 이 점입니다. 밀도가 달라지면 같은 결론을 그대로 쓸 수 없습니다.',
 '여러 삼각형으로 나눈 다각형에서는 각 삼각형의 넓이로 가중 평균을 내야 합니다. 꼭짓점만 평균하면 일반적으로 틀립니다.',
 '세 점이 일직선이면 좌표 평균은 계산되지만, 넓이 있는 삼각형 판은 아닙니다. 계산 결과와 입력의 유효성을 구분하세요.'
],[
 'Add the three vertices and divide by three. Our centroid is four thirds, one.',
 'A median joins a vertex to the opposite midpoint; the centroid lies two thirds along it from the vertex.',
 'The other medians meet the same point. Each vertex has barycentric weight one third.',
 'It is also the mass center of a uniform triangular lamina. Nonuniform density requires a different calculation.',
 'For a polygon partition, weight triangle centroids by area. Averaging polygon vertices generally gives the wrong area centroid.',
 'Collinear vertices still have a coordinate average but no nonzero-area triangular lamina. Validate the input separately.'
],['G=(v₀+v₁+v₂)/3=(4/3,1)','중선: 꼭짓점 → 반대편 중점','중선 비율 2:1 / λ=(1/3,1/3,1/3)','일정 밀도의 삼각형 판만 동일 질량 중심','다각형: G=ΣAᵢGᵢ/ΣAᵢ','일직선 입력: 넓이 0 검사'])
A(5,'가운데 표시와 안전한 여유 공간',S,[(342,367),(632,658)],[
 '시리어스 샘 투에서 길과 다리 사이를 이동합니다. 발밑의 표면과 옆으로 벗어나는 가장자리를 보세요.',
 '발판의 어느 곳에 표시를 놓을지와, 가장자리에서 여유 거리를 확보할지는 다른 문제입니다.',
 '삼각형 발판이라면 세 꼭짓점의 평균을 가운데 표시의 한 기준으로 쓸 수 있습니다.',
 '하지만 평균점에서 모든 변까지의 거리가 같지는 않습니다. 원형 여유 공간을 생각할 때는 변까지의 거리가 필요합니다.',
 '실제 길은 복잡한 모양일 수 있습니다. 화면의 발판을 마음대로 삼각형 하나로 바꾸어 경계를 없애지 마세요.',
 '다음 예제의 내심은 세 변까지 같은 거리를 만듭니다. 현실 게임의 이동 판정 대신, 그 조건을 직접 숫자로 확인하겠습니다.'
],[
 'In Serious Sam2, observe the walkable surface and edges while moving between paths and bridges.',
 'A marker location and clearance from boundaries are different geometric problems.',
 'For a defined triangular platform, the vertex average can be one marker reference.',
 'It does not have equal distances to all sides. Circular clearance needs side distances.',
 'Actual paths can have complex outlines. Replacing them with one triangle loses boundaries.',
 'Our next incenter example verifies equal side distances numerically rather than claiming the game collision method.'
],'이동하는 발밑 표면·길의 끝·다리 경계','평균 위치와 변까지의 여유 거리의 차이')
E(6,'내심과 내접원의 반지름','incenter',[
 '내심은 각을 반으로 나누는 선들이 만나는 점입니다. 각 꼭짓점에는 반대편 변의 길이를 가중치로 줍니다.',
 '지금 첫 꼭짓점의 반대편은 오, 둘째의 반대편은 삼, 셋째의 반대편은 사입니다. 둘레는 십이입니다.',
 '가중 합을 십이로 나누면 내심은 일, 일입니다. 엑스축과 와이축까지의 거리가 각각 일입니다.',
 '빗변의 식은 삼 엑스 더하기 사 와이 빼기 십이는 영입니다. 내심을 넣고 법선 길이 오로 나누면 거리도 일입니다.',
 '내접원 반지름은 넓이의 두 배를 둘레로 나눕니다. 넓이 육, 둘레 십이이므로 반지름은 일입니다.',
 '반둘레를 쓰면 넓이 나누기 반둘레입니다. 둘레와 반둘레를 혼동하면 반지름이 절반으로 잘못 나옵니다.'
],[
 'Angle bisectors meet at the incenter. Weight each vertex by the length of its opposite side.',
 'The opposite lengths are five, three and four, with perimeter twelve.',
 'Divide the weighted sum by twelve to obtain one-one, at distance one from both coordinate axes.',
 'The hypotenuse is three x plus four y minus twelve equals zero. At the incenter, its absolute residual divided by five is also one.',
 'The inradius is twice area divided by perimeter: twice six divided by twelve equals one.',
 'Equivalently divide area by semiperimeter. Confusing perimeter with semiperimeter produces half the correct radius.'
],['I=(a₀v₀+a₁v₁+a₂v₂)/(a₀+a₁+a₂)','반대편 길이 (5,3,4), P=12','I=(1,1): 두 축까지 거리 1','|3x+4y-12|/5=1','r=2A/P=12/12=1','r=A/s, s=P/2=6'])
E(7,'외심은 삼각형 밖에 있을 수도 있습니다','circumcenter',[
 '외심은 두 변의 수직이등분선이 만나는 점으로 구할 수 있습니다. 세 꼭짓점까지의 거리가 같습니다.',
 '가로 변의 중점은 이, 영이고 세로 변의 중점은 영, 일 점 오입니다. 수직이등분선의 교점은 이, 일 점 오입니다.',
 '그 점에서 원점까지의 거리는 이 점 오입니다. 나머지 두 꼭짓점까지도 같으므로 외접원 반지름입니다.',
 '직각삼각형의 외심은 빗변의 중점입니다. 예각삼각형에서는 안에 있고, 둔각삼각형에서는 밖에 있을 수 있습니다.',
 '영, 영과 사, 영과 일, 일인 둔각 예제의 외심은 이, 마이너스 일입니다. 바깥에 있어도 외심 조건을 만족합니다.',
 '세 점이 일직선이면 유일한 유한 외접원을 정할 수 없습니다. 거의 일직선인 입력도 계산을 불안정하게 만듭니다.'
],[
 'Intersect perpendicular bisectors of two sides to find a center equally distant from the vertices.',
 'Midpoints two-zero and zero-one point five give intersecting bisectors at two-one point five.',
 'Its distance from the origin is two point five, equal to the other vertex distances: the circumradius.',
 'A right triangle places the center at the hypotenuse midpoint; an acute triangle places it inside and an obtuse triangle outside.',
 'The obtuse triangle zero-zero, four-zero, one-one has circumcenter two-minus one, outside but still satisfying the condition.',
 'Collinear points do not determine a unique finite circumcircle; nearly collinear inputs are numerically unstable.'
],['외심: 두 수직이등분선의 교점','O=(2,1.5)','R=√(2²+1.5²)=2.5','예각: 내부 / 직각: 빗변 중점 / 둔각: 외부','둔각 예제 (0,0),(4,0),(1,1): O=(2,-1)','일직선·거의 일직선 입력 검사'])
A(8,'지형 윤곽은 점의 순서가 중요합니다',N,[(132,168),(729,754)],[
 '노이타의 굴곡진 지형 사이를 움직입니다. 앞으로 튀어나온 부분과 안으로 들어간 홈을 보세요.',
 '윤곽을 점으로 기록한다면, 경계를 따라 순서대로 이어야 합니다. 점 목록만 같고 연결 순서가 다르면 다른 모양이 됩니다.',
 '움푹 들어간 구간을 가로질러 직선으로 연결하면 통로와 빈 공간이 메워질 수 있습니다.',
 '중간에 같은 점을 반복하거나 너무 짧은 변을 만들면 방향과 넓이 계산도 불안정해질 수 있습니다.',
 '이 게임의 픽셀 지형을 삼각형 메시라고 단정하지 않습니다. 보이는 윤곽으로 올바른 입력이 왜 필요한지 관찰합니다.',
 '다음 그림은 점 여섯 개로 정의한 단순한 오목 다각형입니다. 경계 순서와 빠진 영역을 눈으로 확인하겠습니다.'
],[
 'In Noita, observe protrusions and inward notches while moving through irregular terrain.',
 'A polygon records vertices in boundary order. Reordering the same points changes the shape.',
 'A shortcut across an inward boundary can incorrectly fill a passage or empty region.',
 'Repeated points and tiny edges can destabilize direction and area calculations.',
 'We use visible contours to motivate valid input, without asserting a triangle mesh implementation for pixel terrain.',
 'Our next diagram defines a simple six-vertex concave polygon and checks its ordered boundary and missing region.'
],'노이타 실제 이동·굴곡진 경계·안쪽 홈','순서 있는 경계와 단순한 다각형 입력의 필요성')
E(9,'분할 전에 경계부터 검증하기','polygon-boundary',[
 '다각형은 마지막 점에서 첫 점으로 돌아오는 닫힌 경계입니다. 꼭짓점은 경계를 따라 순서대로 저장합니다.',
 '지금은 영, 영에서 시작해 사, 영과 사, 일, 일, 일, 일, 사, 영, 사로 돌아오는 엘자입니다.',
 '오른쪽 위의 빈 영역은 다각형에 포함되지 않습니다. 오목한 꼭짓점은 일, 일입니다.',
 '먼저 유한한 좌표와 중복점, 길이가 영인 변, 넓이가 영인 입력을 검사합니다.',
 '삼차원 점이라면 같은 평면에 있는지도 확인하고, 인접하지 않은 변이 서로 가로지르는지 검사해야 합니다.',
 '오늘 분할은 구멍과 자기 교차가 없는 단순 다각형을 대상으로 합니다. 구멍이 있는 입력은 별도의 경계와 알고리즘이 필요합니다.'
],[
 'A polygon boundary closes from its last vertex to its first; store vertices in boundary order.',
 'Our L runs through zero-zero, four-zero, four-one, one-one, one-four, zero-four.',
 'The upper-right missing region is outside; one-one is the concave vertex.',
 'Check finite coordinates, duplicate points, zero-length edges and zero-area input first.',
 'For3D vertices, check coplanarity and intersections of nonadjacent edges as well.',
 'We partition a simple polygon without holes or self-intersections. Holes require additional contours and a suitable algorithm.'
],['닫힌 경계: v₀→v₁→…→vₙ₋₁→v₀','L: (0,0),(4,0),(4,1),(1,1),(1,4),(0,4)','(1,1)의 오목한 홈 / 오른쪽 위는 외부','유한 좌표·중복·0길이 변·0넓이','3D 공면성 / 비인접 변 교차','오늘 범위: 단순 경계·구멍 없음'])
E(10,'볼록성은 선분으로 생각하세요','convexity',[
 '볼록한 영역은 안의 두 점을 골라 연결한 선분이 모두 안에 남습니다. 직관적으로 움푹 파인 곳이 없습니다.',
 '정육각형과 삼각형은 볼록합니다. 그 안의 두 점을 연결해도 바깥으로 빠져나가지 않습니다.',
 '엘자에서는 왼쪽 위와 오른쪽 아래의 점을 연결하면 일부가 오른쪽 위 빈 영역을 통과합니다.',
 '그 두 점은 안에 있어도 선분 전체는 안에 있지 않습니다. 따라서 엘자는 오목한 다각형입니다.',
 '단순한 평면 경계에서는 같은 순서로 돌며 방향 전환이 한쪽으로 일관적인지도 볼 수 있습니다.',
 '한쪽 회전 판정을 자기 교차 경계에 무조건 적용하면 안 됩니다. 먼저 입력의 순서와 교차 여부를 검증하세요.'
],[
 'A convex region contains the entire segment between every two of its points; it has no inward notch.',
 'A regular hexagon and a triangle are convex: interior point pairs stay inside when connected.',
 'In our L, a segment from upper-left to lower-right crosses the missing upper-right region.',
 'Its endpoints are inside but part of the segment is outside, proving concavity.',
 'For a valid simple planar boundary, consistent turn orientation provides another check.',
 'Do not apply a turn test blindly to a self-intersecting contour. Validate order and intersections first.'
],['볼록: 내부 두 점의 선분 전체가 내부','삼각형·정육각형: 볼록','L 내부 두 점 연결 → 빈 영역 통과','내부 끝점 두 개만으로 충분하지 않음','유효한 단순 경계: 회전 부호 일관성','자기 교차 검증이 선행'])
A(11,'타일 하나와 연결된 땅은 다릅니다',D,[(90,123),(154,157),(173,190)],[
 '도르프로만틱의 육각형 타일이 추가되며 땅의 경계가 바뀝니다. 새 타일 하나와 전체 연결 영역을 나누어 보세요.',
 '타일 하나는 볼록하지만 여러 개를 합친 윤곽에는 안쪽 홈이 생길 수 있습니다.',
 '같은 바깥 경계 안에 있다고 생각한 두 위치를 연결해도, 선분이 빈 타일 자리 위를 통과할 수 있습니다.',
 '볼록한 조각들의 합집합이 언제나 볼록한 것은 아닙니다. 전체 윤곽을 별도로 검사해야 합니다.',
 '구멍이 있는 영역이라면 바깥 윤곽만 기록해도 충분하지 않습니다. 제외할 내부 경계가 필요합니다.',
 '다음 계산에서는 모양 전체가 볼록한지 살피는 방법과, 각도의 합만으로 구분할 수 없는 이유를 보겠습니다.'
],[
 'Adding Dorfromantik hexagons changes the land boundary. Distinguish one tile from the entire connected region.',
 'An individual tile is convex while its union can contain inward notches.',
 'Connecting two land positions can cross an empty tile location.',
 'A union of convex pieces is not necessarily convex; test its complete boundary separately.',
 'An area with holes needs inner exclusion contours in addition to the outer boundary.',
 'We will examine whole-shape convexity and why an angle sum alone cannot distinguish it.'
],'실제 타일 배치로 변하는 전체 윤곽·빈 타일 자리','볼록한 부분의 합집합과 오목한 전체 경계 구분')
E(12,'회전 부호와 각도의 합','polygon-turns',[
 '연속된 세 꼭짓점에서 두 변의 이차원 외적 부호를 봅니다. 경계를 시계 반대 방향으로 정했다면, 볼록한 곳은 왼쪽으로 돕니다.',
 '엘자의 오목한 꼭짓점에서는 반대로 돕니다. 이 예제는 왼쪽 회전과 오른쪽 회전이 섞여 있습니다.',
 '일직선인 세 점은 외적이 영입니다. 엄격한 볼록성인지, 일직선 점을 허용하는지 규칙을 정해야 합니다.',
 '단순한 다각형의 내각 합은 꼭짓점의 개수에서 두 개를 뺀 뒤, 백팔십 도를 곱합니다. 볼록과 오목 모두 같습니다.',
 '여섯 꼭짓점이면 칠백이십 도입니다. 각도 합이 맞는다는 이유만으로 볼록하다고 판정할 수 없습니다.',
 '역코사인으로 각도를 구할 때는 영인 변을 거르고 입력을 마이너스 일과 일 사이로 제한합니다. 작은 끼인각만으로 오목한 내각을 구별하지 마세요.'
],[
 'Inspect the2D cross sign of consecutive edges. With counterclockwise winding, convex vertices turn left.',
 'The L notch turns right, mixing turn signs in this valid simple example.',
 'Collinear triples have zero cross product. Define strict convexity or a policy allowing collinear points.',
 'Every simple polygon has interior-angle sum n minus two times180 degrees, whether convex or concave.',
 'Six vertices give720 degrees. A correct angle sum alone does not prove convexity.',
 'For acos, reject zero edges and clamp its input to minus one through one. The smaller unsigned angle does not identify a reflex interior angle.'
],['cross₂(eᵢ,eᵢ₊₁): CCW에서 볼록은 +','L의 (1,1)에서 회전 부호 −','cross=0: 일직선 처리 규칙','단순 다각형: Σθ=(n−2)·180°','볼록·오목 모두 n=6 → 720°','acos: 0변 검사·[-1,1] 제한·오목각 구분'])
E(13,'볼록한 다각형은 부채꼴로 나누기','convex-fan',[
 '볼록한 다각형에서는 첫 꼭짓점에서 나머지 꼭짓점으로 대각선을 그을 수 있습니다.',
 '첫 삼각형은 영, 일, 이이고 다음은 영, 이, 삼입니다. 같은 첫 꼭짓점을 공유하며 앞으로 진행합니다.',
 '꼭짓점이 여섯 개면 삼각형은 네 개입니다. 일반적으로 꼭짓점의 개수에서 두 개를 뺀 개수입니다.',
 '볼록하기 때문에 대각선과 삼각형이 바깥으로 빠져나가지 않습니다. 바로 이 조건이 단순한 방법을 안전하게 만듭니다.',
 '각 삼각형은 같은 경계 방향으로 저장하고, 원래 꼭짓점의 인덱스로 위치와 속성을 참조할 수 있습니다.',
 '삼각형 개수가 맞는 것만으로 올바른 분할이 되지는 않습니다. 영역을 겹치거나 빠짐없이 덮는지도 확인하세요.'
],[
 'For a convex polygon, diagonals from the first vertex can connect to the remaining vertices.',
 'Emit triangles zero-one-two, then zero-two-three, advancing while sharing the first vertex.',
 'Six vertices produce four triangles, generally n minus two.',
 'Convexity keeps the diagonals and triangles inside. This condition makes the simple fan safe.',
 'Keep consistent winding and reference original vertex indices for positions and attributes.',
 'The correct triangle count alone does not prove a valid partition; verify coverage without overlap or gaps.'
],['볼록한 경계에서 v₀를 고정','(0,1,2) → (0,2,3) → …','n=6 → n−2=4개','안쪽 대각선 / 바깥 영역을 채우지 않음','같은 winding·원래 인덱스·속성 유지','개수 + 겹침 없음 + 빠짐 없음'])
A(14,'안쪽 홈을 가로지르면 생기는 문제',N,[(843,856),(870,899)],[
 '노이타에서 캐릭터가 파인 통로와 지형의 끝을 지납니다. 바깥으로 열린 빈 공간을 보세요.',
 '경계의 한 점에서 모든 다른 점으로 직선을 잇는다면, 일부 선은 빈 공간을 가로지를 수 있습니다.',
 '그 선을 삼각형 변으로 사용하면 원래 없던 땅을 채웠다고 계산할 수 있습니다.',
 '반대로 어떤 부분은 여러 삼각형이 겹칠 수도 있습니다. 총 개수만 맞추어서는 이 문제를 발견하지 못합니다.',
 '실제 게임이 그런 오류를 낸다는 뜻이 아닙니다. 보이는 통로를 통해 잘못된 분할의 결과를 상상해 보는 것입니다.',
 '이제 같은 엘자에서 시작점을 바꾸어, 부채꼴이 실패하는 경우를 직접 그려 보겠습니다.'
],[
 'Observe the open notches and terrain edges as the Noita character traverses them.',
 'Segments from one boundary vertex to every other vertex may cross empty space.',
 'Using such segments as triangle edges can fill land that did not exist.',
 'Other triangles may overlap. Triangle count alone misses both errors.',
 'This illustrates a faulty geometric construction, not an observed bug in the game.',
 'We will change the fan anchor on our L to draw a concrete failure.'
],'실제 이동·파인 통로·열린 빈 공간','오목한 경계 밖을 채우는 잘못된 분할의 결과')
E(15,'오목한 예제에서 부채꼴의 실패','concave-fan',[
 '엘자의 한 꼭짓점을 부채꼴의 기준으로 고릅니다. 이 점의 엑스 좌표는 사이고, 와이 좌표는 숫자 일입니다. 경계 순서를 따라 네 개의 삼각형을 만듭니다.',
 '기준점에서 일, 사와 영, 사 쪽으로 이어지는 삼각형의 일부는 빈 영역으로 나갑니다.',
 '경계 방향에 따른 넓이를 더하면 칠이 나올 수 있습니다. 잘못 덮은 부분이 부호로 상쇄되기 때문입니다.',
 '원래 엘자의 넓이도 칠이지만, 같은 합이 올바른 영역을 보장하지는 않습니다.',
 '반대로 영, 영을 기준으로 하면 이 특정 엘자에서는 유효한 부채꼴이 됩니다. 오목한 모양이 모두 같은 결과를 내는 것은 아닙니다.',
 '중요한 것은 입력 조건을 확인한 알고리즘입니다. 임의의 시작점으로 오목 다각형을 안전하게 나눌 수 있다고 일반화하지 마세요.'
],[
 'Choose four-one as the L fan anchor and emit four triangles in boundary order.',
 'Some triangles toward one-four and zero-four extend into the missing region.',
 'Signed triangle areas can still sum to seven because erroneous contributions cancel.',
 'The L area is also seven, but matching totals do not guarantee matching coverage.',
 'Anchoring at zero-zero happens to give a valid fan for this particular L. Concave shapes and anchor choices differ.',
 'Use an algorithm with validated input conditions; an arbitrary fan anchor is not safe for general concave polygons.'
],['오목 L의 기준점 v₂=(4,1)','바깥 삼각형 영역을 빨강으로 표시','부호 있는 넓이 합은 7일 수 있음','면적 합 일치 ≠ 같은 영역','v₀=(0,0)는 이 L에서만 유효한 예','오목 다각형의 임의 fan은 일반 해법 아님'])
E(16,'귀 잘라내기의 첫 단계','ear-first',[
 '귀는 경계의 연속된 세 꼭짓점으로 만드는, 안쪽에 놓인 삼각형입니다. 가운데 꼭짓점이 볼록한 후보여야 합니다.',
 '단순 경계에서 대각선이 내부에 있어야 하고, 다른 남은 꼭짓점이 그 삼각형 안이나 허용하지 않은 경계 위에 없어야 합니다.',
 '엘자에서 영, 영과 사, 영과 사, 일인 삼각형을 첫 귀로 고릅니다. 넓이는 이입니다.',
 '그 삼각형을 결과에 저장하고 가운데 꼭짓점인 사, 영을 남은 경계에서 제거합니다.',
 '새 경계는 영, 영에서 사, 일로 바로 이어집니다. 제거한 삼각형과 남은 영역이 원래 엘자를 함께 덮습니다.',
 '꼭짓점을 제거했다고 원래 데이터의 인덱스를 덮어쓰지 마세요. 남은 연결 관계와 출력 삼각형을 따로 유지합니다.'
],[
 'An ear is an interior triangle formed by three consecutive boundary vertices, with a convex middle candidate.',
 'Its diagonal must lie inside and other remaining vertices must not occupy its interior or disallowed boundary.',
 'Our first L ear is zero-zero, four-zero, four-one, of area two.',
 'Store that triangle and remove its middle vertex four-zero from the remaining contour.',
 'The new edge runs from zero-zero to four-one; the removed ear and remainder together cover the original L.',
 'Preserve original vertex indices while updating contour links and output triangles separately.'
],['귀 후보: 연속된 prev, current, next','볼록·내부 대각선·다른 꼭짓점 제외','첫 귀 (0,1,2), A=2','v₁ 제거 / 출력 인덱스 유지','남은 경계: 0→2→3→4→5→0','연결 관계와 원래 꼭짓점 데이터 분리'])
A(17,'빠진 통로 없이 영역을 보존하기',N,[(951,995),(1001,1013)],[
 '노이타의 얼음 지형과 좁은 통로를 따라 움직입니다. 어디가 지형이고 어디가 지나갈 빈 공간인지 구분하세요.',
 '분할 결과를 볼 때도 같은 질문이 필요합니다. 원래 지형에 있던 영역은 남고, 빈 통로는 채워지지 않아야 합니다.',
 '삼각형을 하나씩 추가할 때마다 주변 경계를 다시 보아야 합니다. 처음의 이웃 관계가 끝까지 같지는 않습니다.',
 '형태가 복잡해져도 지켜야 할 것은 겹침 없는 덮기와 같은 바깥 윤곽입니다.',
 '여기서는 게임의 실제 이동을 관찰할 뿐, 픽셀 데이터를 직접 삼각형으로 바꾸었다고 말하지 않습니다.',
 '다음 그림에서는 남은 귀를 차례로 제거하고 네 삼각형이 넓이 칠의 엘자를 정확하게 덮는지 확인합니다.'
],[
 'Observe ice terrain and narrow empty passages during real Noita movement.',
 'A partition should preserve land while leaving empty passages unfilled.',
 'Recheck neighbors after every added triangle; the original adjacency does not remain unchanged.',
 'Complexity does not change the requirements: nonoverlapping coverage and the same outer contour.',
 'We observe actual motion without claiming to convert the pixel terrain into a mesh.',
 'Our next diagram removes the remaining ears and verifies four triangles covering the L of area seven.'
],'실제 얼음 지형 이동·좁은 빈 통로·바깥 윤곽','분할에서 보존할 영역과 갱신되는 이웃 관계')
E(18,'남은 귀를 제거하고 결과 검사하기','ear-sequence',[
 '첫 귀를 뗀 뒤 다음 귀는 영, 이, 삼입니다. 그 넓이는 일 점 오입니다.',
 '이 꼭짓점을 제거하면 영, 삼, 사가 다음 귀가 됩니다. 넓이는 다시 일 점 오입니다.',
 '마지막에는 영, 사, 오 삼각형이 남고 넓이는 이입니다. 네 넓이를 더하면 칠입니다.',
 '각 삼각형의 내부가 겹치지 않고 빈 영역을 채우지 않으며, 원래 경계를 덮는 것도 확인합니다.',
 '귀를 찾지 못하면 유효하지 않은 입력이나 퇴화, 허용 오차 문제를 의심해야 합니다. 무한 반복하거나 임의의 삼각형을 출력하지 마세요.',
 '구멍 있는 다각형을 연결하는 기법은 추가 규칙이 필요합니다. 오늘의 단순 예제가 모든 구멍과 교차 입력까지 해결했다고 확장하지 않습니다.'
],[
 'After the first ear, triangle zero-two-three has area one point five.',
 'Remove vertex two; zero-three-four becomes the next ear, again of area one point five.',
 'The final triangle zero-four-five has area two; the four areas sum to seven.',
 'Also verify nonoverlapping interiors, unfilled empty space, and coverage of the original boundary.',
 'Failure to find an ear can indicate invalid input, degeneracy or tolerance trouble. Do not loop forever or emit arbitrary triangles.',
 'Bridging holes needs additional rules; our simple example does not establish a solution for all holes or intersections.'
],['다음 귀: (0,2,3), A=1.5','다음 귀: (0,3,4), A=1.5','마지막 (0,4,5), A=2 / 합=7','겹침 없음·외부 없음·경계 보존','귀 없음: 중단·입력·퇴화·오차 점검','구멍 연결은 별도 알고리즘 조건'])
A(19,'좁은 곳과 가느다란 조각',N,[(30,44),(49,63),(511,522),(1017,1022),(1026,1040)],[
 '노이타에서 넓은 공간과 좁은 틈을 지납니다. 실제 윤곽에는 서로 가까운 점과 긴 경계가 함께 나타납니다.',
 '그런 모양을 삼각형으로 표현하면 아주 가느다란 조각이 생길 수 있습니다.',
 '가느다란 삼각형은 꼭 틀린 삼각형은 아닙니다. 하지만 작은 넓이에 비해 긴 변을 가져 계산이 민감해질 수 있습니다.',
 '좌표 단위와 해상도가 다른 입력에 같은 숫자의 허용 오차를 그대로 적용하는 것도 조심해야 합니다.',
 '모양을 단순하게 만들기 위해 점을 지우면 통로의 폭이나 경계가 달라질 수 있습니다. 필요한 정보부터 보존하세요.',
 '다음 비교는 유효한 분할과 품질 좋은 분할을 구분합니다. 원래 영역을 지키는 것이 먼저이고 모양 개선은 그다음입니다.'
],[
 'Noita traversal alternates wide areas and narrow gaps, where close points coexist with long boundaries.',
 'A triangle representation of such outlines can produce very thin elements.',
 'A thin triangle is not automatically invalid, but long edges with small area can increase numerical sensitivity.',
 'A fixed tolerance does not fit every coordinate scale or resolution.',
 'Removing vertices for simplification can change passage width and boundaries; preserve required information.',
 'We will distinguish a valid partition from a higher-quality one. Preserve the region before improving element shapes.'
],'실제 이동·넓은 공간과 좁은 틈·짧고 긴 윤곽','입력 단위와 삼각형 품질을 구분')
E(20,'유효성 검사 뒤에 품질 개선하기','triangle-quality',[
 '넓이가 거의 영인 삼각형과 넓이가 충분한 삼각형을 나란히 보겠습니다. 작은 각도를 가진 조각은 계산에 민감합니다.',
 '귀가 여러 개라면 작은 각도가 더 큰 후보를 선호하는 등 품질 기준을 둘 수 있습니다.',
 '하지만 좋은 각도만 보고 경계 밖의 삼각형을 고르면 안 됩니다. 귀의 유효성 조건이 먼저입니다.',
 '같은 네 삼각형 개수라도 내부 대각선을 어떻게 선택하느냐에 따라 모양이 달라집니다.',
 '분할 후에는 방향과 인덱스, 넓이, 영역 덮기, 필요한 속성 연결을 다시 확인합니다.',
 '오차 기준은 길이와 넓이를 구분하고 입력 크기에 맞추세요. 삼각형을 더 좋게 만들겠다고 원래 경계와 구멍을 지워서는 안 됩니다.'
],[
 'Compare a nearly zero-area thin triangle with a well-shaped one; small angles can amplify sensitivity.',
 'Among valid ears, quality heuristics may prefer a larger minimum angle.',
 'A favorable angle does not justify a triangle outside the boundary. Ear validity comes first.',
 'The same triangle count can have different shapes depending on diagonal choices.',
 'Recheck winding, indices, area, coverage and required attribute connectivity after partitioning.',
 'Use scale-aware length and area tolerances without deleting required boundaries or holes to improve appearance.'
],['가느다란 삼각형 / 충분한 넓이·각도','유효 귀 사이에서 최소각 등 품질 비교','귀 유효성 → 품질 선호','삼각형 개수 같아도 대각선 선택은 다름','방향·인덱스·넓이·영역·속성 점검','길이 ε와 넓이 ε 구분·경계 보존'])
A(21,'타일과 발판으로 다시 질문하기',D,[(0,17),(82,89.5)],[
 '도르프로만틱의 연결된 타일을 보세요. 타일 하나와 전체 땅의 윤곽은 다릅니다.',
 '먼저 중심의 목적을 정하고, 경계 순서와 볼록성, 홈과 구멍을 확인합니다.',
 '조건에 맞게 분할한 다음, 빈 공간과 원래 영역이 보존되었는지 검사하세요.',
 '마지막 문제에서는 세 중심과 엘자의 네 삼각형을 직접 확인하겠습니다.'
],[
 'Observe connected Dorfromantik tiles: one tile and the whole land have different outlines.',
 'Define the center purpose, then check boundary order, convexity, notches and holes.',
 'Partition under suitable conditions and verify that empty space and the original region are preserved.',
 'Our final practice checks the three centers and four L triangles.'
],'실제 게임 내 카메라 이동·연결된 타일 영역·타일 회전','중심 선택→경계 검증→분할→검사의 전체 연결')
E(22,'세 중심과 네 삼각형을 직접 확인하기','polygon-practice',[
 '첫 문제입니다. 영, 영과 사, 영과 영, 삼인 삼각형의 무게중심, 내심, 외심을 구분해 보세요.',
 '무게중심은 사 나누기 삼, 일입니다. 내심은 일, 일이고 외심은 이, 일 점 오입니다.',
 '내접원 반지름은 일, 외접원 반지름은 이 점 오입니다. 같은 중심이나 같은 반지름이 아닙니다.',
 '둘째는 여섯 꼭짓점의 엘자입니다. 유효한 삼각형은 네 개입니다. 첫째와 마지막 삼각형의 넓이는 각각 숫자 이입니다. 둘째와 셋째의 넓이는 각각 일 점 오입니다. 네 넓이를 더하면 칠입니다.',
 '같은 넓이 합만 확인하지 말고 겹침과 빈 영역, 경계도 검사하세요. 처음 조건부터 결과까지 한 흐름으로 확인합니다.',
 '기하 장에서는 표현과 경계, 평면과 좌표, 중심과 분할을 연결했습니다. 다음 렌더링 장에서는 이 삼차원 정보를 화면의 픽셀로 만드는 과정을 설명하겠습니다.'
],[
 'First, distinguish centroid, incenter and circumcenter for zero-zero, four-zero, zero-three.',
 'The centroid is four thirds-one, incenter one-one, circumcenter two-one point five.',
 'The inradius is one and circumradius two point five; neither their centers nor their radii coincide.',
 'Second, the six-vertex L has four valid triangles with areas two, one point five, one point five and two, totaling seven.',
 'Also check overlap, empty regions and boundaries. Validate the complete path from input conditions to output.',
 'Geometry connected representations, bounds, planes, coordinates, centers and partitions. Rendering next converts this3D information into screen pixels.'
],['직각삼각형 (0,0),(4,0),(0,3)','G=(4/3,1), I=(1,1), O=(2,1.5)','내접원 r=1 / 외접원 R=2.5','L: 4개 삼각형 / 2+1.5+1.5+2=7','입력 조건 → 분할 → 영역·경계·품질','다음: 렌더링 · 3D 정보에서 픽셀로'])
assert [s['id'] for s in scenes]==[f'{i:02}' for i in range(1,23)]
data={'slug':slug,'chapter':9,'part':3,'totalParts':3,'renderModule':'geometry_polygons','sourceDependencies':['manim/projects/game-math-part2-full-series/geometry.py'],
 'sourceSections':['9.6.5','9.7','9.8'],'contract':{'centers':'Centroid coordinate average and uniform triangular lamina; incenter opposite-side weights with r=2A/P=A/s; circumcenter equal vertex distances, possibly outside an obtuse triangle. Nondegenerate finite inputs.',
 'polygon':'Ordered closed finite planar simple boundary; zero/duplicate edges, signed area, nonadjacent intersections and holes inspected separately. Simple here means no self-intersections and no holes for the demonstrated algorithm.',
 'convexity':'Segment definition; consistent turn test only after valid simple planar boundary; angle sum alone cannot distinguish concavity.',
 'partition':'Convex fan n-2; concave arbitrary-anchor fan can fail even with matching signed-area sum. Verified six-vertex L ears1,2,3 then final triangle. Validity precedes quality; no universal hole-bridging implementation asserted.'},
 'coverage':{'9.6.5':['02','03','04','05','06','07','22'],'9.7':['08','09','10','11','12'],'9.8':['13','14','15','16','17','18','19','20','21','22']},'scenes':scenes,
 'gameCandidates':{'reviewedAt':'2026-10-06','selected':[{'game':'Dorfromantik','sourceId':D,'reason':'New title, official developer presskit and explicit content-creation permission; actual tile placement shows convex individual tiles versus concave connected land.'},{'game':'Noita','sourceId':N,'reason':'Fresh nonoverlapping reviewed intervals show inward terrain notches, narrow passages and preserved empty regions.'},{'game':'Serious Sam2','sourceId':S,'reason':'Fresh bridge/path intervals compare central marker and boundary-clearance questions.'}],
 'rejected':[{'game':'Dorfromantik Cherry Blossom Update','reason':'Nearly static scenic camera with moving boats does not sufficiently demonstrate the selected tile-placement questions.'},{'game':'Dorfromantik Undo Button Update','reason':'Promotional montage includes office/esports/live-action scenes unrelated to this math lecture.'},{'game':'Unlicensed Dorfromantik commentary uploads','reason':'No clear recording reuse permission; official developer-supplied source selected instead.'}],
 'historyReview':'Full history inspected. Dorfromantik is fresh; Noita and Serious Sam2 use reviewed source intervals not used in the two preceding geometry lectures. Source sound and BGM excluded.'}}
out=B/'lessons'/f'{slug}.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'slug':slug,'scenes':len(scenes),'koLines':sum(len(s['ko']) for s in scenes),'koChars':sum(sum(map(len,s['ko'])) for s in scenes),'actualCapacitySeconds':sum(s.get('maxSeconds',0) for s in scenes)}))
