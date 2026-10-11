"""Add prerequisite/causal narration beside the unchanged22 approved scenes."""
from pathlib import Path
import json,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
comparison=read(B/'polygons-candidate-comparison.json')
assert comparison['review']['allSelectedNativePlaybackCompared'] and comparison['review']['denseActionPixelsCompared']
base=read(B/'baselines/game-math-polygons-triangulation/lesson.json');old={s['id']:s for s in base['scenes']}
extra=[]
def ex(ident,title,ko,en,beats,visual,question):
 assert len(ko)==len(en)
 extra.append(dict(id=ident,title=title,kind='explanation',mode=ident,ko=ko,en=en,beats=beats,visual=visual,
  causalConnection=question,originalReplacement=False))
ex('QF01','찾은 위치에서 기준점 선택으로',
 ['앞 편에서는 삼각형 안의 위치를 세 꼭짓점의 비율로 나타냈습니다. 그런데 표시를 놓을 기준점은 어디로 정할까요? 무엇을 같게 만들고 싶은지에 따라 답이 달라집니다.'],
 ['The previous lecture described a triangle position by vertex weights. Where should we place a reference marker? The answer changes with what we want to make equal.'],
 ['삼각형 안의 주소 → 기준점 선택','무엇을 같게 만들까요?'],
 'Carry the previous finite triangular surface and weighted point into this lecture. Retain the original01 overview immediately after this question, as the rest of the opening overview.',
 'Previous address gives a position; choosing a useful reference remains unresolved.')
ex('QB01','같은 비율은 좌표의 평균입니다',
 ['세 꼭짓점을 똑같이 삼분의 일씩 섞으면 좌표의 평균입니다. 종이 삼각형을 균일하게 잘랐을 때 균형을 잡을 위치와 연결됩니다. 변이나 꼭짓점까지의 거리가 같다는 조건은 아직 넣지 않았습니다.'],
 ['Equal one-third vertex weights give the coordinate average. For a uniformly dense paper triangle, this connects to its balance point. We have not imposed equal distances to edges or vertices.'],
 ['wA=wB=wC=1/3','좌표 평균 ≠ 거리 조건'],
 'Use A(0,0), B(4,0), C(0,3), explicitly smaller new triangle than the previous6-by4 example. Animate three equal contributions; then introduce original03 three questions.',
 'Carry the known weighted sum into the three different center definitions; uniform density is the analogy limit.')
ex('QB02','각을 반으로 나누면 왜 변에서 같은 거리일까요?',
 ['내부의 점에서 두 변에 수직선을 내려 거리를 잽니다. 각을 반으로 가르는 선 위라면 두 직각삼각형이 같은 모양이라서 이 거리가 같습니다.',
  '세 변에서 거리가 같은 점을 꼭짓점과 연결해 보세요. 세 작은 삼각형은 높이가 같은 반지름입니다. 넓이는 밑변 길이에 비례하므로, 앞 편의 넓이 비율도 반대편 변의 길이에 비례합니다.'],
 ['Drop perpendiculars from an interior point to two sides. On the angle bisector, the two right triangles are congruent, giving equal perpendicular distances.',
  'Join a point equally distant from all three sides to the vertices. The three small triangles share the same radius as height. Their areas, and hence the barycentric area weights from the previous lecture, are proportional to their opposite side lengths.'],
 ['각의 이등분: 수직 거리 같음','같은 높이r → 작은 넓이=변×r/2','넓이 비율 → 반대편 변의 가중치'],
 'Animate a bisected angle, equal hypotenuse/right angles and perpendicular feet. On the same3-4-5 triangle draw IA,IB,IC; reveal opposite-side area colors with heights r. Do not introduce I(1,1) as an unproved answer before original06 calculation.',
 'Mean does not equalize edge clearance. Equal perpendicular distance motivates bisectors and explains the upcoming opposite-side weights.')
ex('QB03','변의 중점에서 직각으로 세우는 이유',
 ['변에서 같은 거리가 필요한 문제는 풀었습니다. 이번에는 세 꼭짓점까지의 거리를 같게 만듭니다. 두 점의 중간에서 선을 직각으로 세우면, 그 선 위의 위치는 두 점에서 같은 거리입니다. 이 선이 수직이등분선입니다.'],
 ['We have solved equal distances to sides. Now require equal distances to vertices. A perpendicular line through the midpoint of two points consists of positions equally distant from them. This is the perpendicular bisector.'],
 ['변까지 거리 → 꼭짓점까지 거리','중점 + 직각 → 두 꼭짓점 거리 같음'],
 'Keep the same3-4-5 triangle. Contrast perpendicular edge clearance with vertex-to-center segments. Animate midpoint and equal right-triangle legs before original07 intersection. Show an exterior point can remain equally distant; no claim that all centers lie inside.',
 'Incenter solves edge clearance; circumcenter answers a different enclosing-circle question.')
ex('QB04','선을 이어서 남겨야 할 땅을 정합니다',
 ['중심 하나로는 땅의 모양을 기록할 수 없습니다. 경계점을 순서대로 잇고 마지막에 처음으로 돌아와야, 남길 영역과 빈 공간을 구분합니다. 이제 중심을 고르는 문제에서 경계를 지키는 문제로 넘어갑니다.'],
 ['A single center cannot describe the land shape. Connect boundary points in order and close the path to distinguish retained area from empty space. We now move from choosing a center to preserving a boundary.'],
 ['중심 한 점 ≠ 영역 전체','순서대로 연결 → 닫기 → 땅과 빈 공간'],
 'Carry the previous center onto a larger L-shaped surface; reveal ordered numbered vertices and return edge. Keep the missing upper-right notch empty. Original09 then specifies and validates the exact boundary.',
 'Three center conditions are established; a complete shape requires its ordered boundary before partition.')
ex('QB05','회전의 부호는 어느 쪽으로 꺾였는지입니다',
 ['선분이 빈 곳을 지나갔으니 엘자는 오목했습니다. 경계를 돌며 같은 사실을 계산할 수도 있습니다. 엘자의 홈에서는 왼쪽으로 삼만큼 간 뒤 위로 삼만큼 갑니다. 두 방향의 외적은 마이너스 구로, 다른 꼭짓점과 반대 회전입니다.'],
 ['The segment crossing empty space showed that the L is concave. Turning along its boundary checks the same property numerically. At its notch, travel three left and then three up: the2D cross product is minus nine, the opposite turn from the other vertices.'],
 ['v2→v3=(-3,0)','v3→v4=(0,3)','uxvy−uyvx=(-3)×3−0×0=-9'],
 'Use ordered CCW L vertices and the existing coordinate frame. Animate incoming and outgoing arrows at v3(1,1), then each component product. Respect y-up mathematics, not raw screen y-down. Validity already checked in09; signed result is area units, not angle degrees.',
 'The segment definition is already understood; signed turns compute that concavity. Original12 distinguishes angle sum from a convexity proof.')
ex('QF02','경계를 정했으니 안쪽을 나눌 차례입니다',
 ['무엇을 같게 할지 정해 중심을 골랐고, 순서대로 이어진 경계에서 홈도 확인했습니다. 경계는 땅의 바깥을 정하지만 아직 안쪽을 삼각형으로 채우지는 않았습니다. 다음 편에서는 이 엘자의 빈 부분을 지키며 나누겠습니다.'],
 ['We chose centers by their purpose and found the notch in an ordered boundary. A boundary defines the outside, but does not yet partition the interior. The next episode divides this L while preserving its empty region.'],
 ['목적 → 중심','입력 검증 → 경계·홈','다음 질문: 빈 공간을 지키며 삼각형으로 나누기'],
 'Retain all original12 content before this conclusion. Hold the same L and show only its boundary; reveal the missing interior partition as the precise next question without previewing a false filled notch.',
 'Conclude a complete center/boundary question; the unresolved interior partition makes the episode boundary necessary.')
ex('QF03','땅은 남기고 빈 공간은 채우지 않는 분할',
 ['앞 편에서 중심의 목적과 경계의 순서를 구분하고, 엘자의 홈을 확인했습니다. 이번에는 그 땅을 겹침 없는 삼각형으로 나누겠습니다.',
  '볼록한 모양의 간단한 방법부터 시작해, 같은 방법이 홈에서 왜 실패하는지 보겠습니다. 이어서 귀를 하나씩 떼고, 원래 영역과 좁은 통로가 남았는지 검사합니다.'],
 ['The previous episode separated center purposes and boundary order, then found the L-shaped notch. We now partition that land into triangles with disjoint interiors.',
  'Start with a simple convex method and see why it can fail at a notch. Remove ears one by one, then verify the original area and narrow openings remain.'],
 ['앞 편: 유효한 경계와 홈','부채꼴 → 실패 원인 → 귀 제거','겹침·누락·빈 공간·품질 검사'],
 'Independent narrated overview directly after preserved2-second branding. Keep the same six-vertex L beside a convex hexagon; preserve the notch, vertex indices and semantic colors throughout.',
 'Carry the validated boundary into a partition task; promise the exact original13–22 order.')
ex('QB06','넓이 합은 덮은 모양을 알려주지 않습니다',
 ['부채꼴은 잘라 놓은 조각의 수가 맞아도 홈을 덮을 수 있습니다. 더한 넓이에서 겹친 곳을 뺀 결과는 장부의 합계와 비슷합니다. 합계가 같아도 돈이 어디에 쓰였는지는 모르듯, 넓이 합만으로 어느 위치를 덮었는지는 모릅니다.'],
 ['A fan can cover the notch despite giving the expected number of triangles. A signed area sum is like a ledger total: matching totals do not reveal where each amount went. Similarly, an equal area sum does not establish coverage at each location.'],
 ['삼각형 수 일치 ≠ 같은 영역','부호 있는 넓이 합 ≠ 위치별 덮기'],
 'Show the existing v2-anchored wrong fan over the same L, with separate red excess and striped overlap. Animate signed cancellation in a ledger while keeping spatial error visible. The ledger is an analogy for totals only, not a monetary claim.',
 'Observed empty notch demands a location-by-location test. Original15 calculates signed cancellation without mistaking it for valid coverage.')
ex('QB07','빼도 되는 작은 조각을 먼저 찾습니다',
 ['한 번에 전부 연결하려다가 빈 곳을 덮었습니다. 이번에는 세 이웃 점으로 만든 작은 조각 하나만 확인합니다. 볼록한 모서리여도 조각이 다른 경계를 가르거나 남은 점을 품으면 뗄 수 없습니다. 안쪽에 놓이고 방해하는 점이 없을 때만 귀로 저장합니다.'],
 ['Joining everything at once covered empty space. Instead, test one small triangle from three neighboring points. Even a convex corner cannot be removed if its diagonal crosses the boundary or the triangle contains another remaining point. Store it as an ear only when its interior and vertex checks pass.'],
 ['한꺼번에 연결 → 작은 후보 하나 검사','볼록 후보 + 내부 대각선 + 다른 점 검사','유효한 귀만 출력하고 가운데 점 제거'],
 'Keep the same wrong-fan result, retract only new error annotations, and spotlight candidate0,1,2. Reveal diagonal-inside and remaining-vertex tests before removing1. Do not erase original vertex storage.',
 'The wrong fan motivates local validity checks rather than a disconnected new algorithm name.')
ex('QB08','사라진 것은 점의 번호가 아니라 연결입니다',
 ['첫 귀를 저장한 뒤에도 원래 점의 번호는 그대로입니다. 남은 경계에서는 영번의 다음 이웃이 이번이 됩니다. 삼각형을 하나 뗄 때마다 이 연결을 갱신해야 다음 귀를 올바르게 찾습니다.'],
 ['Original vertex IDs remain after saving the first ear. In the remaining boundary, vertex zero now connects to vertex two. Update adjacency after each removal to find the next valid ear.'],
 ['출력: (0,1,2)','남은 연결: 0→2→3→4→5→0','원본 번호 유지 / 이웃 갱신'],
 'Carry the first2-area ear as a completed colored piece, leave v1 in immutable data with detached status, and replace active0→1→2 with0→2. Original18 then uses0,2,3 and0,3,4 in that same diagram.',
 'A stored ear changes the active boundary; updating neighbors explains why the next candidate differs.')
ex('QB09','길이 눈금이 두 배면 넓이는 네 배입니다',
 ['영역을 올바르게 덮은 다음에야 조각의 모양을 개선합니다. 길이 단위를 바꾸어 좌표가 두 배가 되면, 밑변과 높이가 모두 두 배라 넓이는 네 배입니다. 길이 오차와 넓이 오차에 같은 기준을 쓰면 안 됩니다.',
  '가느다란 조각은 높이가 작아서 같은 위치 오차도 상대적으로 크게 작용합니다. 통로를 지우는 대신 유효한 후보 안에서 모양을 비교하겠습니다.'],
 ['Improve triangle shape only after validating coverage. Doubling coordinate scale doubles both base and height, so area quadruples. Length and area tolerances must therefore use different units and scales.',
  'A thin triangle has a small altitude, making the same position error relatively larger. Compare valid candidates rather than erasing the passage.'],
 ['좌표×2 → 길이×2 / 넓이×4','작은 높이 → 같은 오차의 상대적 영향 증가','유효성 먼저 → 품질 비교'],
 'Retain the completed four-triangle L; add a scale comparison with labeled unit versus unit squared. Use same-base triangles with heights1 and0.01 and a small illustrative perturbation0.001; explicitly numerical illustrations, not measured Noita units. Original20 preserves its full validity/quality comparison.',
 'Coverage is correct; numerical sensitivity motivates quality and tolerance checks without changing the original boundary.')
ex('QB10','중심부터 분할까지 같은 질문으로 돌아갑니다',
 ['삼각형마다 넓이가 다르면 균일한 판의 중심을 낼 때도 같은 비율로 섞을 수 없습니다. 넓이 이와 일 점 오인 조각은 각각 그 넓이만큼 반영합니다. 분할한 이유가 위치와 표면 값을 올바르게 계산하기 위해서였음을 기억하며 마지막 문제를 확인하세요.'],
 ['Different triangle areas also mean different weights for a uniformly dense plate center. Pieces of area two and one point five contribute in those proportions. Return to the final problems remembering that valid partition lets us calculate positions and surface values correctly.'],
 ['삼각형별 중심 → 넓이 가중 평균','2,1.5,1.5,2 / 총넓이7','유효한 분할 → 위치·속성 계산의 바탕'],
 'Carry all four ears with areas2,1.5,1.5,2; mark each triangle centroid, then show area-weighted composite center, not a mean of polygon vertices. Original22 full worked review follows unchanged, including the original rendering chapter promise.',
 'Connect original04 area-weighted polygon center to the completed partition and original22 end-to-end audit.')

game=[]
def actual(ident,title,segments,ko,en,connection):
 assert len(ko)==len(en)==len(segments)
 records=[]
 for key,a,z in segments:
  selected=next(r for r in comparison['candidates'] if r['source']==key)
  assert any(x<=a and z<=y for x,y in selected['chosen'])
  records.append(dict(sourceId=key,sourceFile=comparison['sourcePaths'][key],sourceSha256=comparison['sourceSha256'][key],
   **{'in':a,'maxSeconds':z-a}))
 game.append(dict(id=ident,title=title,kind='actual',sourceType='actual-footage',sourceId=segments[0][0],
  sourceFile=records[0]['sourceFile'],sourceSegments=records,intervals=[[a,z] for _,a,z in segments],
  maximumSeconds=sum(z-a for _,a,z in segments),segmentSourceIds=[k for k,_,_ in segments],
  sourceGroupStartsAtLines=list(range(len(segments))),ko=ko,en=en,
  causalConnection=connection,selection=dict(comparedBeforeNarration=True,record='polygons-candidate-comparison.json',
  chosenReason=connection,priorUse=[r for r in comparison['review']['overlaps'] if r['source'] in [k for k,_,_ in segments]],
  finalAnnotatedPixels='pending'),annotation=dict(red='observed boundary/connection',blue='chosen observed reference',
  teal='retained region/path',yellow='missing region or candidate cut',
  reveal='in narration order with separate source-group resets',tracking='editable observed camera/object landmarks; hide during occlusion, banners and source cuts',
  classification='full-screen action-led existing footage; diagram/frozen analysis separately explanation',worldMeasurement=False,
  engineInternalsAsserted=False,movingPixelApproval=False)))
actual('QG01','움직이는 건물의 기준점과 외곽',
 [('tiny-glade-257046593',10,24),('tiny-glade-256965562',33,46.5)],
 ['타이니 글레이드에서는 건물을 놓고 크기와 위치를 바꿉니다. 파란 점은 관찰용 기준입니다. 기준점을 정해도 바깥선 전체가 사라지는 것은 아닙니다.',
  '별도 장면에서는 건물을 돌리고 높이도 바꿉니다. 같은 가운데 표시를 쓰더라도 모양은 달라집니다. 화면의 기준점과 실제 게임 내부 계산은 구분합니다.'],
 ['In Tiny Glade, place a building and change its size and position. Blue marks an observed reference; choosing one reference does not replace its complete outline.',
  'In a separate shot, rotate a building and change its height. Its outline changes even with a similar center marker. This is an observed screen reference, not a claim about internal game calculations.'],
 'Coordinate averaging supplies a reference, while full geometry still matters; observable placement and resize prepare the following edge-clearance question.')
actual('QG02','벽을 바꾸면 안과 밖의 경계도 바뀝니다',
 [('tiny-glade-257046593',0,8.8),('tiny-glade-256965562',0,18.7)],
 ['이 장면은 벽을 그리다가 열린 아치를 만듭니다. 빨간 윤곽은 보이는 벽의 경계입니다.',
  '별도 장면에서는 벽을 지우고 다시 그린 뒤 길이 벽을 지나갑니다. 남은 벽과 빈 통로를 함께 보세요. 중심 하나보다 경계 전체가 필요한 이유입니다.'],
 ['A wall stroke creates an open arch. Red follows the observed wall boundary.',
  'In a separate shot, erase and redraw a wall, then run a path through it. Watch both the remaining wall and empty opening: the full boundary conveys more than one center point.'],
 'After three center conditions, actual wall editing exposes the unresolved whole-boundary problem before original08/09.')
actual('QG03','높이 변화와 평면의 홈을 구분합니다',
 [('tiny-glade-256965562',23,31.7),('noita-e',79,99)],
 ['타이니 글레이드에서는 땅의 높이를 바꿉니다. 높이가 다른 곳을 한 평면의 경계로 바로 계산할 수는 없습니다.',
  '노이타의 별도 동굴 장면입니다. 캐릭터가 좁은 틈을 지나 오른쪽 발판으로 이동합니다. 지형과 빈 공간의 빨간 경계를 보세요. 홈을 건너 잇는 선은 원래 없는 땅을 만들 수 있습니다.'],
 ['Tiny Glade changes terrain height. Different heights cannot automatically be treated as one planar boundary.',
  'In a separate Noita cave, pass through a narrow opening and move toward the right ledge. Red follows visible land versus empty space. Bridging a notch could create land outside the original shape.'],
 'Original convexity requires a valid planar input; distinguish elevation from a planar notch, then pass the same concave-union question to original11.')
actual('QG04','호수와 동굴의 빈 부분을 남깁니다',
 [('tiny-glade-257046593',30.5,40.3),('noita-outline-b',451,469)],
 ['호수를 그리면 남은 땅의 경계도 바뀝니다. 물 쪽으로 파인 부분은 땅에 포함되지 않습니다.',
  '별도 노이타 장면에서는 꺾인 지형 옆 빈 공간을 따라 내려갑니다. 빨간 경계와 노란 빈 부분을 보세요. 앞 강의의 거리 대신, 이번에는 분할이 이 빈 공간을 채우지 않는지 묻습니다.'],
 ['Drawing a lake changes the remaining land boundary. The water-side notch is excluded from the land.',
  'In a separate Noita shot, descend through empty space beside a stepped outline. Watch red edges and yellow empty space. This familiar source now asks about partition coverage rather than the preceding lecture’s distance.'],
 'Convex fan works only under its conditions; observed water/notch exclusions motivate the original concave fan failure. Familiar Noita interval reuse disclosed, with a different mathematical viewer question.')
actual('QG05','조각을 떼어도 통로의 모양은 남습니다',
 [('noita-outline-d',788,802)],
 ['이 노이타 구간에서도 내려온 뒤 발판 사이로 다시 올라갑니다. 빨간 선은 보이는 경계입니다. 귀를 저장한 뒤에도 원래의 빈 통로를 남겨야 한다는 조건을 이 움직임과 비교해 보세요.'],
 ['Descend and return upward between platforms in this Noita interval. Red follows visible boundaries. Compare the movement with the requirement that removing an ear preserves the original empty passage.'],
 'First ear is saved; visible movement through an opening checks what must remain, then original17 continues that same preservation question. Earlier plane interval reused for this distinct boundary question, recorded.')
actual('QG06','잘라 낸 조각이 무엇을 남기는지 확인합니다',
 [('shapez2-257294952',0,4),('shapez2-257312662',39.5,46.8)],
 ['셰이프즈 투입니다. 원이 두 조각으로 나옵니다.',
  '별도 장면은 사각형도 자릅니다. 결과를 보세요. 삼각형 분할의 증거는 아닙니다.'],
 ['Shapez2 cuts a disk and sends out two pieces.',
  'A separate shot also cuts a square. Watch where the pieces emerge. This is not evidence of a triangulation implementation.'],
 'After all ears, complete input/action/output cutting visibly motivates checking retained pieces. This is a factory-item analogy, not an assertion about the renderer.')
actual('QG07','좁은 통로를 지우지 않고 경계를 따라갑니다',
 [('noita-f',258,277.3),('shapez2-257312662',30,34)],
 ['노이타에서 좁은 복도를 올라갔다가 아래 공간으로 내려옵니다. 긴 변과 가까운 모서리가 함께 있습니다. 안내창이 지나가면 같은 통로를 다시 보세요. 모양을 단순하게 만들겠다고 이 빈 틈을 지우면 안 됩니다.',
  '별도 공장 장면입니다. 꺾인 길의 순서를 보세요.'],
 ['Climb a narrow Noita corridor, then descend to a wider area. Long edges meet nearby corners. Once the area banner passes, look at the same passage again. Simplification must not erase this opening.',
  'A separate factory shot: follow the bent path in order.'],
 'Validity precedes shape improvement. Observe close boundaries and ordered connections before original21/22 end-to-end review; reset annotations at the game change.')
orders=[['QF01','01','02','QB01','03','04','QG01','05','QB02','06','QB03','07','QG02','08','QB04','09','10','QG03','11','QB05','12','QF02'],
 ['QF03','13','QG04','14','QB06','15','QB07','16','QG05','17','QB08','18','QG06','19','QB09','20','QG07','21','QB10','22']]
episodes=[dict(slug='game-math-polygon-centers-v2',titleKo='게임수학 Part 2 · 다각형 ① 목적에 맞는 중심과 경계',titleEn='Game Math Part 2 · Polygons1: Centers and Boundaries',question='기준점은 어떤 목적에 맞게 고르고, 땅의 경계와 홈은 어떻게 기록할까?',originalIds=[f'{i:02}' for i in range(1,13)]),
 dict(slug='game-math-polygon-partition-v2',titleKo='게임수학 Part 2 · 다각형 ② 빈 공간을 지키는 삼각형 분할',titleEn='Game Math Part 2 · Polygons2: Partition Without Filling Empty Space',question='오목한 땅을 삼각형으로 나눠도 빈 공간과 원래 영역은 어떻게 보존할까?',originalIds=[f'{i:02}' for i in range(13,23)])]
assert [i for order in orders for i in order if i in old]==list(old)
allnew={s['id']:s for s in extra+game};assert len(allnew)==len(extra)+len(game)
audit=[]
for episode,order in zip(episodes,orders):
 for index,ident in enumerate(order):
  scene=old.get(ident,allnew.get(ident));assert scene
  audit.append(dict(episode=episode['slug'],id=ident,previousScene=order[index-1] if index else 'preserved-branding',
   nextScene=order[index+1] if index+1<len(order) else 'preserved-membership-ending',
   retainedOriginal=ident in old,whyHere=scene.get('causalConnection','Preserve approved original question/action/calculation/result and its exact bilingual sequence.'),
   unchangedDictionary=ident in old,finalContinuousReview=False))
flow=dict(baseline=base['slug'],status='additive draft; narration, original dense footage and current moving pixels pending',
 preservation='All22 original scene dictionaries, bilingual lines, formulas/order, PCM and explanation clips remain exact.',
 causalSpine=['앞 강의의 삼각형 안의 위치 → 목적에 맞는 기준점','좌표 평균 → 변까지 거리 → 꼭짓점까지 거리','중심으로 모양을 기록할 수 없음 → 순서대로 연결한 경계와 홈','유효한 평면 경계 → 볼록성 → 안전한 분할 조건','잘못된 부채꼴의 영역 덮기 → 작은 귀의 유효성 검사','남은 이웃 관계 갱신 → 영역 보존 → 수치 품질'],
 episodes=episodes,orders=orders,additions=extra,completeBoundary='After original12: validated boundary and convexity concluded; original13 starts a separate complete partition problem. Never split a derivation.',
 sceneConnections=audit,actualRatio=.4,explanationRatio=.6,backgroundMusic=False,sourceAudioUsed=False,
 palette='preserved research-paper-white-v1 for this already-started chapter',draftReviewedAt=datetime.datetime.now().astimezone().isoformat())
write(B/'polygons-flow-draft.json',flow)
write(B/'polygons-game-insertions.json',dict(revisionOf=base['slug'],scenes=game,review=comparison['review'],
 sourceComparison='polygons-candidate-comparison.json',rights=comparison['rights']))
for episode,order in zip(episodes,orders):
 print(episode['slug'],dict(newExplanationCharacters=sum(sum(len(t) for t in allnew[i]['ko']) for i in order if i in allnew and allnew[i]['kind']=='explanation'),
  newActualCapacity=sum(allnew[i].get('maximumSeconds',0) for i in order if i in allnew),
  originalCount=sum(i in old for i in order)))
print('Draft saved; no voice/render/publishing approval claimed.')
