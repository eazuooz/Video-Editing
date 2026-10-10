"""Draft only additive causal teaching; original chapter remains unchanged."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
extra=[]
def scene(i,title,mode,ko,en,beats,previous,question,visual):
 extra.append(dict(id=i,kind='explanation',title=title,mode=mode,ko=ko,en=en,beats=beats,retainedResult=previous,nextQuestion=question,visual=visual))
scene('LF01','자세를 구한 물체에 연결선과 범위를 붙입니다','lecture-overview',
 ['앞 편에서 물체의 방향을 구했습니다. 이제 그 물체에서 다른 곳으로 잇는 선을 계산하겠습니다.','이번 챕터는 두 편입니다. 먼저 원과 선의 표현을 골라 점을 만들고 검사합니다. 이어지는 편에서는 선에 닿을 대상의 크기를 감싸고, 회전한 뒤의 범위를 다시 구합니다.'],
 ['The previous lesson found an object orientation. We now calculate a connection from that object to another location.','This chapter has two episodes. First, choose circle and line representations to generate and test points. Next, enclose the target size and rebuild its bounds after rotation.'],
 ['앞 결과: 물체의 자세','이번 질문: 어디로 연결하고 무엇에 닿는가?','① 원·선의 표현 / ② 대상의 범위·변환'],
 'Previous rotation conversion checks the same orientation','How do we calculate its connections and occupied range?',
 'Carry the same projected object and axes from rotation; reveal an attached endpoint, target and connection. Preview two ordered tasks beside this object, not unrelated topic cards.')
scene('LC04','옮긴 원에서 두 점을 잇는 선으로','circle-to-line',
 ['원에서는 중심과 반지름으로 모양을 저장하고, 각도로 점을 만들고, 거리로 안팎을 검사했습니다. 이제 원 대신 두 연결점을 주고, 같은 세 질문을 직선에 적용하겠습니다.'],
 ['For the circle, center and radius store the shape, angle generates a point, and distance tests inside or outside. Replace the circle with two connection points and apply the same three questions to a line.'],
 ['원: 저장 / 생성 / 검사','두 점을 주면 선에서는?'],
 'Translated circle has explicit storage, generation and test roles','How do the same tasks work for a two-point connection?',
 'Keep the translated circle, make two sample points, and join them; preserve their semantic colors while returning to the actual grapple.')
scene('LP01','비율과 미터를 같은 지점에서 비교합니다','parameter-distance',
 ['방금의 출발점은 이, 일이고 끝점은 팔, 사입니다. 차이 벡터 육, 삼의 길이는 루트 사십오입니다. 좌표 단위를 미터라고 정해 보겠습니다.','절반인 티 영 점 오를 곱하면 세 미터와 일 점 오 미터를 더해, 오 미터와 이 점 오 미터에 도착합니다. 티에는 미터 단위가 없습니다.','같은 차이 벡터를 루트 사십오로 나누면 단위 방향입니다. 여기에 거리인 루트 사십오 나누기 이를 곱해도 똑같은 절반 지점입니다.','비율로 찾든 거리로 찾든 결과는 같습니다. 다음에는 기울기로 표현할 때 모든 방향의 선을 다룰 수 있는지 확인하겠습니다.'],
 ['Our origin is two, one and endpoint eight, four. Displacement six, three has length square root forty-five. Define the coordinate unit as meters.','Multiplying by t one half adds three meters and one point five meters, reaching five meters, two point five meters. The parameter t has no meter unit.','Divide the same displacement by square root forty-five for a unit direction. Multiply it by distance square root forty-five over two to reach the identical midpoint.','Fraction and distance give the same point. Next, check whether slope can represent every line direction.'],
 ['o=(2,1)m / δ=(6,3)m / |δ|=√45m','t=.5 → o+.5δ=(5,2.5)m','d=δ/√45 / s=√45/2 m','o+sd=(5,2.5)m / 같은 결과'],
 'Original07 computes the midpoint and explains dimensionless versus distance parameters','Can we compare the two forms at the identical point?',
 'One fixed coordinate plane, same endpoints and midpoint. Animate fraction and distance expressions into the same colored point; distinguish t from s without switching examples.')
scene('LF02','연결선을 만들었으니 대상의 범위가 남았습니다','episode-recap',
 ['원과 선은 어떤 계산을 할지에 따라 표현을 골랐습니다. 선분의 비율과 광선의 거리도 같은 점에서 비교했습니다.','이제 연결선은 만들 수 있습니다. 그런데 무엇에 닿았는지는 대상의 크기를 알아야 판단합니다. 다음 편에서는 그 물체를 구와 상자로 감싸고, 회전하면 그 범위가 어떻게 바뀌는지 계산하겠습니다.'],
 ['Choose a circle or line representation for the task, and compare a segment fraction with a ray distance at the same point.','We can now construct the connection. Contact also needs the target size. The next episode encloses that object in spheres and boxes and calculates how its bounds change under rotation.'],
 ['표현 선택 → 점 생성·검사','비율 t / 거리 s','다음 질문: 연결선이 닿을 대상의 크기'],
 'Line and perpendicular-bisector representations are established','What occupied range must a connection reach?',
 'Retain the same connection and target, reveal its extent only as the next question; do not start an unfinished collision algorithm before the ending.')
scene('LF03','선에 닿을 크기를 계산하고 회전 뒤까지 이어갑니다','bounds-overview',
 ['연결선만 알아서는 물체를 맞혔는지 판단할 수 없습니다. 이번에는 대상이 차지하는 범위를 구와 상자로 표현하겠습니다.','먼저 거리로 구의 안팎을 검사합니다. 다음에는 점들의 최소와 최대로 상자를 만들고 겹침을 비교합니다. 마지막에는 같은 상자를 돌려, 바뀐 범위를 다시 계산하겠습니다.'],
 ['A connection line alone cannot decide whether it reaches an object. Represent the target occupied range with spheres and boxes.','First, use distance to test a sphere. Next, build a box from point minima and maxima and compare overlap. Finally, rotate the same box and calculate its changed bounds.'],
 ['선은 구함 → 대상의 크기는?','거리·구 → min/max·상자 → 회전 뒤 경계'],
 'Episode1 establishes the connection line','How do we represent and update the target extent?',
 'Independent overview immediately after branding: same connection reaches projected target; animate sphere, spatial box and rotation in the narrated order.')
scene('LP02','구의 안팎은 중심까지의 거리입니다','sphere-prerequisite',
 ['원에서 했던 거리 검사를 공간으로 옮기겠습니다. 공간의 점은 엑스, 와이, 제트 세 좌표로 위치를 적습니다.','중심에서 옆으로 이만큼 떨어지고 나머지 차이가 영이면 거리의 제곱은 사입니다. 반지름이 이인 구의 경계에 놓입니다.','차이가 삼이면 거리의 제곱은 구여서 사보다 큽니다. 바깥입니다. 세 축의 차이를 각각 제곱해 더하면 어느 방향에서도 같은 검사를 할 수 있습니다.'],
 ['Move the circle distance test into space. A spatial point uses three coordinates, x, y and z.','An offset of two along one axis and zero along the others has squared distance four. It lies on a sphere of radius two.','An offset of three has squared distance nine, greater than four: outside. Square and sum all three offsets to apply the identical test in every direction.'],
 ['P−C=(2,0,0) → 거리²=4 = r²','P−C=(3,0,0) → 거리²=9 > r²','각 축 차이 제곱의 합'],
 'Visible round gameplay range suggests a distance-based proxy','What calculation distinguishes inside, boundary and outside?',
 'Keep the target and a declared teaching sphere. Three orthogonal axes and moving offset point, projections with occlusion. Mark numerical positions as a fixed example, not world measurements.')
scene('LC13','둥근 범위가 길쭉한 몸을 감싸면','sphere-to-box',
 ['구의 거리 검사와 크기 변경을 확인했습니다. 하지만 길쭉한 다리를 큰 구로 감싸면 옆의 빈 공간까지 많이 포함됩니다.','빈 공간을 줄이려면 물체가 축마다 어디까지 뻗는지 따로 기록할 수 있습니다. 다음 몸과 다리를 보며 세 방향의 범위를 떠올려 보세요.'],
 ['We tested sphere distance and size changes. A large sphere around a long bridge also includes substantial empty space beside it.','Record the object extent separately along each axis to reduce that space. Look for these three ranges in the next bodies and bridge.'],
 ['구의 검사·크기 변화 확인','긴 물체 → 둥근 경계의 빈 공간','축별 범위로 감싸기'],
 'Sphere scaling preserves the distinction between length, area and volume','Can a bound follow a long or irregular target more efficiently?',
 'Use the same projected long object with a translucent teaching sphere; show the empty space before replacing it with a box. Preserve object dimensions and axes.')
scene('LP03','최소와 최대는 한 축씩 고릅니다','minmax-prerequisite',
 ['최소와 최대를 세 좌표에서 한꺼번에 찾기 전에, 한 축에 놓인 이, 사, 칠을 보겠습니다.','최소는 이, 최대는 칠입니다. 중심은 둘의 평균인 사 점 오이고, 전체 길이는 오, 반크기는 이 점 오입니다.','공간에서는 이 비교를 엑스, 와이, 제트마다 반복합니다. 축마다 선택된 최소가 서로 다른 점에서 나올 수 있습니다. 이 원리로 원래의 다섯 점을 읽겠습니다.'],
 ['Before comparing three coordinates, place two, four and seven on one axis.','Minimum is two and maximum seven. Their average is center four point five, the full extent five, and half-extent two point five.','Repeat this comparison independently for x, y and z. Each minimum can come from a different point. Use this principle to read the original five points.'],
 ['한 축: 2,4,7 → min=2 / max=7','c=(2+7)/2=4.5 / e=(7−2)/2=2.5','같은 비교를 x,y,z에 반복'],
 'Original14 defines axis-aligned six-face storage','How do we actually find its values from points?',
 'Show one number line then extend it into three spatial axes. Reveal one min/max comparison at a time before the original five-point table and syntax-colored code.')
scene('LC18','겹침을 검사했으니 회전 뒤 값도 갱신해야 합니다','overlap-to-rotation',
 ['상자가 겹쳐도 실제 몸은 떨어질 수 있다는 반례를 확인했습니다. 그래도 상자는 물체를 빠뜨리지 않게 감싸야 합니다.','물체를 돌렸는데 이전 최소와 최대를 그대로 쓰면 이 조건을 지킬까요? 같은 사각형을 돌려 어느 꼭짓점이 가장 왼쪽으로 가는지 확인하겠습니다.'],
 ['The counterexample showed overlapping boxes with separated bodies. A useful bound must still enclose the entire object.','Does keeping old minima and maxima after rotation preserve that condition? Rotate the same rectangle and see which corner becomes leftmost.'],
 ['상자 겹침은 후보 / 실제 접촉은 다음 검사','회전 뒤에도 물체를 빠뜨리지 않는가?','극값을 주는 꼭짓점이 바뀜'],
 'Original17 separates broad-phase overlap from body contact','Does rotation invalidate the stored extrema?',
 'Keep the thin separated rectangles from the counterexample, then focus on one, label its corners and rotate it into the original square calculation.')
scene('LP04','부호를 지우는 이유를 같은 구간에서 봅니다','affine-absolute-intuition',
 ['중심과 반크기로 상자를 옮기는 식을 배웠습니다. 마이너스는 위치의 방향을 바꾸지만, 퍼진 크기를 마이너스로 만들지는 않습니다.','앞의 구간은 중심 오, 반크기 이였습니다. 엑스를 마이너스 이 배하고 일을 더하면, 양 끝은 마이너스 오와 마이너스 십삼으로 서로 순서가 바뀝니다.','최소부터 다시 정렬하면 마이너스 십삼부터 마이너스 오입니다. 중심은 마이너스 구, 반크기는 사입니다. 마이너스 이의 절댓값에 원래 반크기 이를 곱한 결과와 같습니다.','세 축에서는 새 축으로 들어오는 모든 최대 퍼짐을 더합니다. 그래서 행렬의 각 성분에 절댓값을 적용합니다. 물체의 점들을 옮기는 것과, 빈 공간이 있는 상자 전체를 옮기는 것은 다음 장면에서 구별하겠습니다.'],
 ['The center and half-extents transform a box. A negative sign reverses position direction without giving a negative spread.','The earlier interval had center five and half-extent two. Transform x by minus two x plus one. Its endpoints become minus five and minus thirteen, reversing their order.','Sorting gives minus thirteen to minus five, center minus nine and half-extent four. This equals the absolute value of minus two times the original half-extent two.','In three dimensions, add each maximum contribution into a new axis. That is why each matrix entry uses its absolute value. Next, distinguish transforming actual points from transforming their box, including its empty space.'],
 ['입력 [3,7], c=5,e=2 / x′=−2x+1','끝점 −5,−13 → 정렬 [−13,−5]','c′=−9 / e′=|−2|·2=4','위치에는 부호 / 퍼짐에는 절댓값'],
 'Original20 gives exact affine enclosure of the input box','Why do absolute matrix entries preserve spread under sign reversal?',
 'Reuse LB05 interval and transformation with no new coordinates; flip its two colored endpoints, then sort labels while leaving physical positions fixed. Extend same reasoning to 2.5D box axes.')
scene('LF04','같은 입력을 끝까지 따라가며 검산합니다','chapter-conclusion',
 ['연결점 두 개로 선을 만들고, 대상의 크기를 구와 상자로 감쌌습니다. 회전 뒤에는 극값을 주는 점이 바뀌어서 경계도 다시 계산했습니다.','계산할 때는 선의 비율인지 거리인지, 실제 점들의 경계인지 상자 전체의 경계인지 먼저 정하세요. 다음 평면과 삼각형 강의는 이렇게 좁힌 후보 안에서 거리를 재고 위치를 더 정확히 찾는 단계입니다.'],
 ['Two endpoints defined a line; spheres and boxes enclosed the target. Rotation changed which points supplied the extrema, requiring rebuilt bounds.','First decide whether a parameter is fraction or distance, and whether the bound encloses actual points or an entire box. The next plane and triangle lesson measures distances and locates positions more precisely within these narrowed candidates.'],
 ['연결선 → 대상 범위 → 회전 뒤 갱신','같은 입력·단위로 결과 비교','다음: 평면 거리 / 삼각형 안 위치'],
 'Original22 connects endpoint arithmetic with transformed-point versus transformed-box bounds','What finer test follows candidate filtering?',
 'Carry the same line, target, bound and spatial axes through the recap; reveal its plane and triangle only as the next complete question.')
draft=read(B/'lines-bounds-additive-draft.json')
# This prerequisite is drafted but not approved/audio-recorded yet; distinguish its new task explicitly.
lb=next(s for s in draft['additions'] if s['id']=='LB02')
lb['ko'][0]='수직선에서 기울기 나눗셈이 막혔죠. 두 점을 잇는 선과 별개로, 이번에는 영, 영과 이, 영에서 같은 거리인 점들을 찾겠습니다. 같은 거리라는 질문이 수직 이등분선을 만드는 이유를 보겠습니다.'
lb['en'][0]='The slope division failed for a vertical line. In a separate task from joining the two sites, find points equally distant from zero, zero and two, zero. Equal distance is the question that produces a perpendicular bisector.'
orders=[['LF01','01','02','LB01','03','04','LC04','LG01','05','LG02','06','07','LP01','LG03','08','LB02','09','LF02'],['LF03','10','LG04','LP02','11','12','LC13','13','14','LP03','15','LB04','LG05','16','17','LC18','18','LG06','19','LB05','20','LG07','21','22']]
episodes=[dict(slug='game-math-lines-circles-v2',titleKo='게임수학 Part 2 · 직선과 경계 ① 두 점으로 연결선을 계산하기',titleEn='Game Math Part 2 · Lines and Bounds 1: Calculate a Connection from Two Points',question='두 점에서 연결선을 만들고, 그 위의 점과 같은 거리인 위치를 어떻게 구할까?'),dict(slug='game-math-bounds-transform-v2',titleKo='게임수학 Part 2 · 직선과 경계 ② 물체의 범위와 회전 뒤 경계',titleEn='Game Math Part 2 · Lines and Bounds 2: Object Extents and Bounds after Rotation',question='선이 닿을 대상의 크기를 감싸고 회전 뒤 경계를 어떻게 갱신할까?')]
out={**draft,'status':'causal/additive text draft; final game selections and narration timing pending','additions':draft['additions']+extra,'omitUnrecorded':['LB03','LP04','LF04'],'omitReason':'LF03 already motivates target extent; LB05 supplies the same 1D absolute-value prerequisite before original20; original22 already supplies the full chapter conclusion. Avoid repeating those purposes. All supplied scenes preserved.','episodes':episodes,'orders':orders,'completeBoundary':'After original09: point generation, parameter domains and line/bisector representations complete. Original10–22 sphere/box tests and affine bounds remain in episode2.','noPadding':True,'mathBaseline':'high school; symbols introduced before use; numerical unit contracts retained','preservedOriginalSceneDictionaries':22}
(B/'lines-bounds-flow-draft.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'newExplanationScenes':len(out['additions']),'newKoLines':sum(len(s['ko']) for s in out['additions']),'episodes':len(episodes),'audioGenerated':False},ensure_ascii=False))
