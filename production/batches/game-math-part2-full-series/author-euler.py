"""Original bilingual teaching script, written after source and footage inspection."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
slug='game-math-euler-axis-angle';candidate=next(x for x in read(B/'queue.json')['items'] if x['slug']==slug)
write(B/'candidates'/f'{slug}.json',{k:candidate[k] for k in ['slug','titleKo','titleEn','viewerQuestion','sourceNotion','sections']})
fp=B/'footage-index.json';sources=read(fp);file=ROOT/'shared/output/game-math-part2-full-series/sources/FvSgGn941U0.mp4';metadata=ROOT/'tmp/game-math-superflight-metadata.json'
sources['FvSgGn941U0']={
 'id':'FvSgGn941U0','game':'Superflight','uploader':'Morkala','url':'https://www.youtube.com/watch?v=FvSgGn941U0','file':file.relative_to(ROOT).as_posix(),'sha256':sha(file),
 'reviewedBeforeNarration':True,'recordingPermissionObserved':'Uploader description explicitly states Free to use gameplay of Superflight. Metadata inspected2026-10-05. No named CC license. Recording permission only; public game-IP review pending.',
 'licenseLabel':'uploader free-to-use permission','metadataProof':metadata.relative_to(ROOT).as_posix(),'metadataSha256':sha(metadata),'sourceAudioUsed':False,
 'priorUse':'Different recording from the prior orientation lecture, with nonrepeated intervals. Same game revisited because its visible body bank and forward direction directly match this linked chapter. Fresh games and source permission reviewed rather than automatically recycling a clip.',
 'visibleAction':'Existing-game wingsuit flight: body banks, forward direction changes and the following camera moves around structures. Visible motion illustrates a question; it does not prove the game uses Euler angles or has gimbal lock.',
 'inspection':'Directly reviewed all10 contact sheets at3-second intervals plus end frames. Excluded portal/fade effects around27–31,47–50,105–109,127–131,184–188,213–217,225–229,242–246,267–271,290–294,339–342,370–373,424–427,453–456,485–489,526–529,555–560,575–581,615–end. Use only the bounded approved sourceSegments.',
 'inspectionSheets':[f'shared/output/game-math-part2-full-series/inspection/euler-morkala/window-{i:02d}-1.jpg' for i in range(1,11)]+['shared/output/game-math-part2-full-series/inspection/euler-morkala-extra/window-01-1.jpg'],
 'extraInspection':'Directly reviewed54–100s at3-second intervals; exclude fade/portal65–70 and77–81. Only54–65 and81–100 added, with no repeated intervals.','publicGameIpReview':'pending'}
write(fp,sources)
scenes=[]
def explanation(sid,title,mode,ko,en,beats,**extra):
 assert len(ko)==len(en)==len(beats),(sid,len(ko),len(en),len(beats))
 scenes.append(dict(id=f'{sid:02d}',kind='explanation',title=title,mode=mode,ko=ko,en=en,beats=beats,**extra))
def actual(sid,title,ko,en,segments,focus,claim):
 assert len(ko)==len(en)
 scenes.append(dict(id=f'{sid:02d}',kind='actual',title=title,ko=ko,en=en,sourceId='FvSgGn941U0',sourceSegments=[{'in':a,'maxSeconds':b-a} for a,b in segments],**{'in':segments[0][0]},maxSeconds=sum(b-a for a,b in segments),focus=focus,claim=claim))
explanation(1,'이번 강의에서 배울 것','overview',[
 '같은 각도를 넣었는데 회전 순서를 바꾸면 왜 다른 자세가 나올까요?',
 '이번 시간에는 비행 장면을 보며 오일러 각의 세 회전과 움직이는 축을 구분합니다.',
 '직접 순서를 바꾸고, 짐벌락과 각도 보간이 어려워지는 이유를 확인합니다.',
 '마지막으로 하나의 축과 각도로 회전을 표현하고, 회전벡터의 계산과 주의점을 두 문제로 정리하겠습니다.'
],[
 'Why do the same angles produce different orientations when their order changes?',
 'We will observe flight and distinguish the three Euler rotations and their moving axes.',
 'Then we will change the order and examine gimbal lock and angle interpolation.',
 'Finally, we will describe a rotation with one axis and angle, and solve two problems about rotation vectors and their limits.'
],['같은 각도 / 다른 순서?','비행 관찰 → 세 각과 움직이는 축','순서 비교 → 짐벌락 → 보간','축·각 → 회전벡터 → 두 문제'])
actual(2,'비행 자세를 세 가지 변화로 보기',[
 '슈퍼플라이트에서 몸이 장애물 사이를 지나갑니다. 몸통이 향하는 쪽부터 보세요.',
 '진행 방향이 옆으로 바뀌는 모습과, 앞쪽이 위아래를 향하는 모습을 나눠 봅니다.',
 '팔을 이은 선이 기울어지는 것도 보입니다. 몸의 앞쪽을 중심으로 비트는 변화와 연결해 생각하세요.',
 '이런 변화를 헤딩, 피치, 뱅크라는 세 각도로 정리할 수 있습니다.',
 '화면의 왼쪽이나 위쪽만 보고 각도 부호를 판단하면 카메라 움직임과 섞입니다.',
 '이 게임의 내부 구현을 추측하지 않고, 다음 그림에서 축과 회전 규칙을 직접 정하겠습니다.'
],[
 'The body passes between obstacles in Superflight. Start by watching where its torso points.',
 'Distinguish turning sideways from pointing upward or downward.',
 'The line joining the arms also tilts. Connect this to twisting around the body forward direction.',
 'We can organize these changes using heading, pitch, and bank.',
 'Screen left or up alone cannot determine angle signs because the camera also moves.',
 'We will define the axes and rotation rules in our own diagram without guessing the game implementation.'
],[(3,26),(31,46),(54,65)],'진행 방향, 몸 앞쪽의 상하 변화, 팔의 기울기; 카메라 투영과 구분','세 각의 직관적 관찰이며 게임 내부 좌표나 구현의 증거는 아니다')
explanation(3,'오일러 각은 순서가 있는 세 회전','euler',[
 '오일러 각은 숫자 세 개로 자세를 표현합니다. 중요한 것은 각도와 함께 축과 순서도 정한다는 점입니다.',
 '이 강의에서는 앞 편과 같은 오른손 규칙, 열벡터, 로컬에서 월드로 가는 회전 행렬을 씁니다.',
 '헤딩은 와이축, 피치는 움직이는 엑스축, 뱅크는 움직이는 제트축으로 정합니다.',
 '서로 다른 세 축을 쓰는 와이, 엑스, 제트 순서입니다. 모든 임의의 축 선택이 같은 것은 아닙니다.',
 '책은 왼손 좌표계와 행벡터를 쓰므로, 식을 옮길 때 전치만 하지 말고 축과 부호까지 확인해야 합니다.',
 '양의 회전은 오른손 엄지가 양의 축을 가리킬 때 손가락이 감기는 방향으로 판단하겠습니다.'
],[
 'Euler angles represent orientation with three numbers, together with a defined axis convention and order.',
 'We retain the right-hand rule, column vectors, and a local-to-world rotation matrix from the previous lecture.',
 'Heading uses y, pitch uses the moving x axis, and bank uses the moving z axis.',
 'This is the Y-X-Z order with three different axes. Arbitrary axis choices are not all equivalent.',
 'The book uses a left-handed frame and row vectors; converting its formulas requires checking axes and signs as well as transposition.',
 'Positive rotation follows the curled fingers when the right thumb points along the positive axis.'
],['세 숫자 + 축 + 순서','오른손 / 열벡터 / 로컬 → 월드','heading: y / pitch: x / bank: z','몸체 축 Y → X → Z','책과 축·부호·행/열 규약 비교','양의 회전: 오른손 규칙'])
explanation(4,'몸에 붙은 축도 함께 돌아간다','intrinsic',[
 '처음에는 몸체 축과 월드 축이 나란합니다. 먼저 와이축을 중심으로 헤딩을 적용합니다.',
 '몸이 돌아가면 몸에 붙은 엑스축도 같이 돌아갑니다. 피치는 이 바뀐 엑스축을 중심으로 적용합니다.',
 '마지막 뱅크는 두 회전을 거친 몸의 제트축, 즉 앞쪽 축을 중심으로 적용합니다.',
 '이처럼 몸체 축을 따라가는 회전을 내재적 회전이라고 부릅니다.',
 '우리 규약에서는 양의 피치가 앞쪽 제트를 음의 와이 쪽으로 보냅니다. 위로 든다는 이름만 믿으면 안 됩니다.',
 '헤딩과 피치로 앞쪽 방향을 정하고, 뱅크로 그 앞쪽 주위의 비틀림을 정한다고 생각해 보세요.'
],[
 'Initially the body and world axes are aligned. Apply heading around y first.',
 'The attached x axis moves with the body. Apply pitch around this new x axis.',
 'Apply bank around the body z axis after the first two rotations: its forward axis.',
 'Rotations that follow the body axes are called intrinsic rotations.',
 'With our signs, positive pitch sends forward z toward negative y. The name alone does not specify the sign.',
 'Think of heading and pitch as setting the forward direction, and bank as twisting around that direction.'
],['heading: 처음 y축 회전','pitch: 바뀐 몸체 x축','bank: 바뀐 몸체 z축','내재적: 몸체 축을 따라가는 회전','+pitch: +z → -y','앞쪽 방향 + 앞쪽 주위 비틀림'])
actual(5,'몸체 축과 화면 축은 다릅니다',[
 '몸이 옆으로 돌고 기울어지는 모습을 다시 보세요. 팔과 몸통을 따라가면 몸에 붙은 방향을 생각할 수 있습니다.',
 '몸에 붙은 축은 회전할 때 같이 돌아갑니다. 화면 아래쪽이 항상 몸의 아래쪽은 아닙니다.',
 '주변 구조물을 기준으로 본 회전과, 몸에 붙은 축을 기준으로 본 회전은 기준이 다릅니다.',
 '따라오는 카메라 때문에 화면에서 보이는 기울기도 함께 달라집니다.',
 '그래서 코드에 피치라는 이름 하나만 적으면 충분하지 않습니다.',
 '어느 좌표계의 어느 축인지 적어 두면, 다음 회전이 어디를 중심으로 적용되는지 확인하기 쉬워집니다.'
],[
 'Watch the body turn and tilt again. Its arms and torso help us imagine attached directions.',
 'Attached axes rotate with the body. Screen down is not always body down.',
 'Rotations measured against the structures and rotations measured against attached axes use different references.',
 'The following camera also changes the tilt visible on screen.',
 'A variable named pitch therefore does not specify enough by itself.',
 'Writing down the frame and axis makes it easier to check which axis the next rotation uses.'
],[(81,100),(109,126),(131,148),(152,159),(160,183),(229,241)],'몸통·팔의 방향과 화면/주변 구조물을 따로 관찰','몸체 축과 고정 기준 축을 구분해야 하며 화면만으로 내부 수치를 알 수 없다')
explanation(6,'고정축에서는 순서를 뒤집는다','extrinsic',[
 '같은 자세에 도착하는 또 다른 방법은 월드에 고정된 축만 사용하는 것입니다. 외재적 회전이라고 부릅니다.',
 '몸체 축에서 헤딩, 피치, 뱅크 순서로 돌린 결과는 고정축에서 뱅크, 피치, 헤딩 순서로 돌린 결과와 같습니다.',
 '열벡터의 행렬은 와이 회전, 엑스 회전, 제트 회전을 왼쪽부터 곱한 형태입니다.',
 '벡터에 행렬을 적용할 때는 오른쪽부터 계산하므로, 고정축 제트 회전이 먼저 작용합니다.',
 '요, 피치, 롤이라는 이름도 쓰지만 요가 고정된 수직축인지 몸체 축인지 문맥을 확인해야 합니다.',
 '내재적 와이, 엑스, 제트와 외재적 제트, 엑스, 와이는 여기서 같은 최종 행렬을 만드는 두 설명입니다.'
],[
 'Another route to the same orientation uses axes fixed in the world. These are extrinsic rotations.',
 'Intrinsic heading-pitch-bank is equivalent to extrinsic bank-pitch-heading in reverse order.',
 'For column vectors, the product is the y rotation, x rotation, and z rotation written from left to right.',
 'Matrices act on the vector from the right, so the fixed z rotation acts first.',
 'The names yaw, pitch, and roll are also common, but check whether yaw uses fixed vertical or a body axis.',
 'Intrinsic Y-X-Z and extrinsic Z-X-Y are two descriptions of the same final matrix here.'
],['고정 월드 축: 외재적 회전','몸체 Y-X-Z = 고정 Z-X-Y','R = Ry(h) Rx(p) Rz(b)','열벡터에는 오른쪽부터 적용','yaw라는 이름만으로 축을 추측하지 않기','같은 최종 자세 / 다른 설명'])
explanation(7,'90도 두 번도 순서에 따라 다르다','order',[
 '앞쪽 벡터를 영, 영, 일로 두고, 고정 엑스축과 고정 와이축으로 각각 구십 도 회전해 보겠습니다.',
 '엑스 회전을 먼저 하면 앞쪽이 음의 와이 방향이 됩니다.',
 '그다음 와이축으로 돌려도 와이 방향의 벡터는 그대로입니다. 결과는 영, 마이너스 일, 영입니다.',
 '이번에는 와이 회전을 먼저 합니다. 앞쪽 벡터가 양의 엑스 방향으로 갑니다.',
 '그다음 엑스축으로 돌리면 엑스 방향은 그대로입니다. 결과는 일, 영, 영입니다.',
 '같은 두 각도를 썼지만 결과가 다릅니다. 삼차원 회전은 보통 순서를 바꿀 수 없습니다.'
],[
 'Start with forward vector zero, zero, one, and use ninety-degree rotations about fixed x and y.',
 'Apply the x rotation first. Forward points along negative y.',
 'The following y rotation leaves a vector on the y axis unchanged, giving zero, minus one, zero.',
 'Now apply the y rotation first. Forward points along positive x.',
 'The following x rotation leaves that direction unchanged, giving one, zero, zero.',
 'The angles are identical but the results differ. Three-dimensional rotations generally do not commute.'
],['v = (0,0,1)','먼저 Rx(90°): (0,-1,0)','Ry Rx v = (0,-1,0)','먼저 Ry(90°): (1,0,0)','Rx Ry v = (1,0,0)','Ry Rx ≠ Rx Ry'])
actual(8,'방향이 바뀐 뒤 기울기를 보세요',[
 '몸이 구조물 사이를 돌아 들어간 뒤 팔이 기울어지는 장면을 보세요.',
 '앞쪽이 달라지면 그 앞쪽 주위로 비트는 축도 월드에서 다른 방향을 가리킵니다.',
 '처음의 고정축으로 돌리는 것과, 돌아간 몸의 축으로 돌리는 것을 나눠 생각해야 합니다.',
 '그래서 같은 회전량이라도 적용 순서와 축 기준이 중요합니다.',
 '이 화면에서 정확한 각도를 측정하는 것은 아닙니다. 몸에 붙은 방향이 계속 달라진다는 점을 관찰하는 것입니다.',
 '이제 숫자 세 개가 직관적이면서도, 한 자세를 여러 숫자로 나타낼 수 있는 이유를 보겠습니다.'
],[
 'Watch the arms tilt after the body turns between structures.',
 'When forward changes, the axis of a forward twist points in a different world direction.',
 'Distinguish rotating around an original fixed axis from rotating around an already moved body axis.',
 'Order and axis reference therefore matter even for identical rotation amounts.',
 'We are not measuring exact angles from these pixels; observe that attached directions keep changing.',
 'Next we will see why three intuitive angles can describe the same orientation in several ways.'
],[(188,212),(246,264)],'방향이 바뀐 후의 팔 기울기, 움직이는 앞쪽 축','관찰을 몸체 축 개념에 연결; 고정축과 이동축을 섞지 않는다')
explanation(9,'같은 자세를 여러 각도로 표현한다','aliases',[
 '오일러 각은 사람이 읽고 편집하기 쉽습니다. 세 개의 실수만 저장하는 것도 장점입니다.',
 '하지만 헤딩 영 도와 삼백육십 도는 같은 자세입니다. 같은 회전축에 한 바퀴를 더해도 끝 자세는 같습니다.',
 '우리 순서에서는 헤딩 영, 피치 백삼십오, 뱅크 영도 다른 세 각으로 바꿀 수 있습니다.',
 '헤딩 백팔십, 피치 사십오, 뱅크 백팔십은 바로 같은 자세입니다. 세 값을 각각 비교하면 놓칩니다.',
 '보통 헤딩과 뱅크는 마이너스 백팔십보다 크고 백팔십 이하로, 피치는 마이너스 구십부터 구십까지 정리합니다.',
 '피치가 양이나 음의 구십 도인 특수한 경우에는 뱅크를 영으로 정하는 추가 규칙이 필요합니다.'
],[
 'Euler angles are easy for people to read and edit, and require only three real components.',
 'Heading zero and three hundred sixty degrees describe the same orientation: an extra full turn preserves the endpoint.',
 'For our order, heading zero, pitch one hundred thirty-five, and bank zero have an alternative representation.',
 'Heading one hundred eighty, pitch forty-five, and bank one hundred eighty give exactly the same orientation.',
 'A common canonical range is minus one hundred eighty exclusive to plus one hundred eighty inclusive for heading and bank, and minus ninety to ninety for pitch.',
 'At pitch plus or minus ninety, we need an additional rule such as setting bank to zero.'
],['장점: 사람이 편집하기 쉬운 세 숫자','0°와 360°: 같은 끝 자세','(h,p,b) = (0°,135°,0°)','= (180°,45°,180°)','h,b ∈ (-180°,180°] / p ∈ [-90°,90°]','p = ±90°이면 b = 0으로 정리'])
explanation(10,'짐벌락: 두 회전축이 겹치는 순간','gimbal',[
 '이제 피치가 양의 구십 도가 될 때까지 몸체 엑스축으로 기울여 보겠습니다.',
 '마지막 뱅크에 쓰는 몸체 제트축이 첫 헤딩에 쓰는 월드 와이축과 같은 직선 위에 놓입니다.',
 '우리 양의 구십 도에서는 두 축의 양의 방향이 반대입니다. 같은 축 선을 다른 방향으로 가리킵니다.',
 '헤딩과 뱅크를 따로 바꾸던 두 손잡이가 같은 회전 방향에 영향을 주게 됩니다.',
 '이 순간 오일러 매개변수의 변화가 만드는 독립적인 회전 방향이 하나 줄어듭니다. 이것이 짐벌락입니다.',
 '물체가 실제로 회전할 능력을 잃었다는 뜻은 아닙니다. 자세를 조절하는 이 좌표 표현이 특이해진 것입니다.'
],[
 'Tilt around body x until pitch reaches positive ninety degrees.',
 'The final body z axis used for bank lies on the same line as the initial world y axis used for heading.',
 'At positive ninety under our signs, the positive directions are opposite along that line.',
 'Two controls that previously changed distinct axes now affect the same rotational direction.',
 'The Euler parameter changes lose one independent instantaneous rotation direction. This is gimbal lock.',
 'The object does not physically lose its ability to rotate; this coordinate parameterization becomes singular.'
],['p → +90°','첫 heading 축과 마지막 bank 축','+y 와 몸체 +z: 반대 방향, 같은 직선','두 손잡이가 같은 축에 영향','매개변수 변화의 독립 방향 감소','물체의 물리적 회전 능력은 그대로'])
actual(11,'화면에서 세운 자세와 짐벌락은 다릅니다',[
 '몸이 급하게 기울고 앞쪽이 위아래를 향하는 비행을 관찰해 보세요.',
 '화면에서 세로로 보인다는 이유만으로 짐벌락이라고 말할 수는 없습니다.',
 '카메라 각도도 영향을 주고, 게임이 어떤 회전 표현을 쓰는지도 이 화면만으로 알 수 없습니다.',
 '이 사례는 급격히 자세가 달라질 때도 제어가 자연스러워야 한다는 요구를 보여 줍니다.',
 '짐벌락은 다음 계산처럼 정해 둔 오일러 순서에서 축이 겹치는 조건을 검사해야 합니다.',
 '실제 움직임에서 생긴 질문과, 그 질문을 설명하는 수학 모델을 연결하되 증거를 섞지 마세요.'
],[
 'Observe steep tilts and changes in where the body points during flight.',
 'An object appearing vertical on screen is not enough to diagnose gimbal lock.',
 'The camera affects that appearance, and the pixels do not reveal the game rotation representation.',
 'This example illustrates the need for natural control through large orientation changes.',
 'Gimbal lock must be checked using the overlapping-axis condition for a defined Euler order.',
 'Connect the question raised by real motion to its mathematical model while keeping their evidence distinct.'
],[(272,289),(294,334)],'급격한 기울기와 카메라의 영향; 짐벌락 발생 증거로 과장하지 않음','실제 화면과 정해진 오일러 매개화의 수학적 조건을 구분한다')
explanation(12,'90도에서는 헤딩과 뱅크가 합쳐진다','gimbal-values',[
 '우리 와이, 엑스, 제트 순서에서 피치가 양의 구십 도이면, 자세는 헤딩에서 뱅크를 뺀 값에 달려 있습니다.',
 '헤딩 삼십, 피치 구십, 뱅크 십 도를 넣어 봅시다. 차이는 이십 도입니다.',
 '헤딩 이십, 피치 구십, 뱅크 영도 같은 행렬을 만듭니다. 그림의 두 몸체 축이 정확히 겹칩니다.',
 '피치가 음의 구십 도일 때는 우리 규약에서 헤딩과 뱅크의 합으로 정리됩니다.',
 '이처럼 모든 자세는 표현할 수 있지만, 주변 자세 변화가 개별 각도에서는 크게 튈 수 있습니다.',
 '특수한 자세에서 뱅크를 영으로 정해 한 표현을 택해도, 경계의 불연속과 보간 문제까지 사라지지는 않습니다.'
],[
 'For our Y-X-Z order at positive ninety pitch, the orientation depends on heading minus bank.',
 'Try heading thirty, pitch ninety, and bank ten degrees. Their difference is twenty.',
 'Heading twenty, pitch ninety, and bank zero give the same matrix. The two body frames coincide.',
 'At negative ninety pitch, our convention instead combines heading plus bank.',
 'All orientations remain representable, but nearby orientation changes can cause large jumps in individual angles.',
 'Choosing bank zero at the singular pose selects a representation without removing boundary discontinuities or interpolation problems.'
],['p = +90° → h - b','(30°,90°,10°)','= (20°,90°,0°)','p = -90° → h + b','모든 자세 표현 가능 / 각도는 크게 튈 수 있음','표준형으로 경계의 불연속을 없애지는 못함'])
explanation(13,'각도 보간은 짧은 차이를 골라야 한다','wrap',[
 '헤딩 마이너스 백칠십 도에서 플러스 백칠십 도로 바꾼다고 합시다.',
 '끝 값에서 시작 값을 그대로 빼면 플러스 삼백사십 도입니다. 거의 한 바퀴를 돌아갑니다.',
 '원 위에서 두 방향은 사실 이십 도만 떨어져 있습니다. 음의 이십 도로 가면 짧은 길입니다.',
 '각도 차이를 한 바퀴 단위로 감싸는 함수가 랩 파이입니다. 우리는 마이너스 파이 초과, 파이 이하를 택합니다.',
 '감싼 차이에 보간 비율을 곱하고 시작 각도에 더하면, 이 한 축에서는 짧은 방향으로 이동합니다.',
 '정확히 백팔십 도 떨어진 두 방향은 두 길의 길이가 같습니다. 같은 끝점 규칙으로 한 방향을 정해야 합니다.'
],[
 'Suppose heading changes from minus one hundred seventy to plus one hundred seventy degrees.',
 'Subtracting start from end gives positive three hundred forty, almost a full turn.',
 'On the circle the directions are only twenty degrees apart. Negative twenty is the short route.',
 'wrapPi removes full turns from the difference. We choose the interval greater than minus pi and at most pi.',
 'Multiply that wrapped difference by the interpolation fraction and add it to the start angle for the short route on this one axis.',
 'Exactly one hundred eighty degrees apart, both routes are equally long. Apply a consistent endpoint rule.'
],['start = -170° / end = +170°','그대로 빼기: +340°','짧은 차이: -20°','Δ = wrapPi(end - start)','θ(t) = start + t Δ','180° 동률: 끝점 규칙을 일관되게'])
actual(14,'자연스러운 회전 경로가 필요합니다',[
 '장애물 가까이에서 몸이 방향을 바꾸는 장면을 보세요. 끝 방향만 맞는 것으로는 충분하지 않습니다.',
 '그 방향까지 어떤 경로로 돌아가는지도 시청자와 플레이어가 느끼게 됩니다.',
 '가까운 두 방향을 이동하려는데 불필요하게 한 바퀴 가까이 돌아가면 어색하겠죠.',
 '앞의 각도 감싸기는 한 축의 이런 긴 경로를 줄이는 데 도움이 됩니다.',
 '하지만 이 게임이 그 함수를 사용한다는 뜻은 아닙니다. 자연스러운 제어가 필요한 이유를 관찰하는 사례입니다.',
 '삼차원에서 세 각을 따로 보간할 때는 또 다른 문제가 남습니다. 코드 다음에 그 차이를 보겠습니다.'
],[
 'Watch the body change direction near obstacles. A correct endpoint is not enough.',
 'Viewers and players also notice the route taken to reach that endpoint.',
 'An unnecessary near-full turn between nearby directions would feel awkward.',
 'Wrapping the angular difference helps avoid that long route on one axis.',
 'This does not claim the game uses that function; it illustrates why natural control matters.',
 'Interpolating three angles separately still has additional problems. We will examine them after the code.'
],[(342,369),(373,394)],'장애물 옆의 방향 전환과 몸의 회전 경로','회전 보간은 끝 자세와 중간 경로 모두 다뤄야 한다')
explanation(15,'라디안과 끝점까지 정한 wrap 코드','wrap-code',[
 '입력은 유한한 실수 라디안이라고 가정합니다. 파이와 이 파이를 상수로 둡니다.',
 '표준 라이브러리의 리메인더로 한 바퀴의 배수를 제거합니다.',
 '결과가 마이너스 파이이면 한 바퀴를 더해 플러스 파이로 옮깁니다. 선택한 끝점 규칙을 지킵니다.',
 '제공된 원문 코드의 범위 검사 부등호는 반대로 적혀 있습니다. 그대로 복사하지 말고 정정된 동작을 확인하세요.',
 '보간할 때는 끝 값 자체가 아니라 끝에서 시작을 뺀 차이를 감쌉니다.',
 '도 단위 숫자를 이 함수에 바로 넣으면 안 됩니다. 입력과 출력 단위를 함께 기록하세요.'
],[
 'Assume finite real-valued radians and define pi and two pi as constants.',
 'Use the standard remainder function to remove complete turns.',
 'Map a result of minus pi to plus pi by adding a full turn, matching our endpoint convention.',
 'The supplied original code has its range-test inequality reversed. Check the corrected behavior instead of copying it unchanged.',
 'For interpolation, wrap end minus start, rather than wrapping only the endpoint.',
 'Do not pass degree values directly to this function. Record both input and output units.'
],['전제: finite input / radians','한 바퀴 배수 제거','(-π, π] 끝점 규칙','원문 부등호 오타를 정정','wrapPi(end - start)','도 ↔ 라디안 변환 확인'],code=[
 'double wrapPi(double angle) {','  constexpr double pi = 3.141592653589793;','  constexpr double tau = 2.0 * pi;','  double w = std::remainder(angle, tau);','  if (w <= -pi) w += tau;','  return w;','}','double delta = wrapPi(end - start);','double value = start + t * delta;'])
explanation(16,'세 각을 따로 보간하면 남는 문제','interpolation',[
 '각도 차이를 잘 감싸도, 세 각을 따로 직선 보간한 경로가 항상 삼차원에서 가장 짧은 회전은 아닙니다.',
 '중간에 피치가 구십 도 근처로 가면 헤딩과 뱅크가 비슷한 축에 영향을 줍니다.',
 '각 숫자가 일정한 속도로 바뀌어도 몸의 실제 회전 속도는 일정하지 않을 수 있습니다.',
 '같은 시작과 끝 자세를 다른 오일러 표현으로 넣으면 중간 경로도 달라질 수 있습니다.',
 '사람이 각도를 편집하는 화면에는 오일러 각이 편하지만, 회전 보간에서는 다른 표현을 함께 검토해야 합니다.',
 '다음 편에서 쿼터니언을 배우고 그다음 편에서 보간을 계산합니다. 쿼터니언도 단위 길이와 부호 규칙을 지켜야 합니다.'
],[
 'Even after wrapping differences, linear interpolation of three separate angles is not always the shortest three-dimensional rotation.',
 'Near ninety pitch, heading and bank affect nearly the same axis.',
 'Constant rates of change in each number need not produce constant physical angular speed.',
 'Alternative Euler representations of the same endpoints can also produce different intermediate routes.',
 'Euler angles are convenient for editing, but rotation interpolation calls for considering other representations.',
 'The next lectures introduce quaternions and interpolation. Quaternions still require unit-length and sign conventions.'
],['wrap로 한 축의 긴 경로는 줄일 수 있음','±90° 근처: 두 축이 거의 겹침','각 숫자의 일정 속도 ≠ 몸의 일정 회전 속도','같은 끝 자세 / 다른 중간 경로','편집용 표현과 계산용 표현을 구분','쿼터니언에서도 단위 길이·부호 관리'])
actual(17,'끝 자세와 이동 과정은 따로 봅니다',[
 '몸이 방향을 바꾸고 구조물 곁을 지나가는 과정을 보세요.',
 '처음과 마지막 화면 두 장만으로는 중간에 어느 쪽으로 얼마나 돌았는지 알기 어렵습니다.',
 '회전 표현으로 끝 자세를 저장하는 일과, 움직임의 경로를 제어하는 일은 서로 연결되지만 다릅니다.',
 '자연스러운 카메라나 캐릭터 회전을 만들려면 중간 자세도 함께 설계해야 합니다.',
 '세 축으로 나누는 대신 한 축을 골라 한 번에 도는 표현도 있습니다.',
 '이번에는 축 자체를 자유롭게 골라, 같은 회전을 더 간단하게 설명해 보겠습니다.'
],[
 'Watch the body change direction and pass beside structures.',
 'Two endpoint images cannot reveal the direction or total amount of turning in between.',
 'Storing an endpoint orientation and controlling its motion path are related but different tasks.',
 'Natural camera or character rotation also requires designing intermediate orientations.',
 'Another representation selects one axis and rotates around it once.',
 'Let us choose that axis freely and describe the rotation in a simpler way.'
],[(400,423),(427,452)],'연속적인 몸의 방향·기울기 변화; 시작·끝과 경로 구분','끝 자세와 중간 경로는 같은 정보가 아니며 축·각 표현으로 전환')
explanation(18,'축 하나와 각도 하나로 표현','axis-angle',[
 '오일러의 회전 정리에 따르면, 두 삼차원 자세 사이의 변화는 적절한 한 축 주위의 회전으로 나타낼 수 있습니다.',
 '축은 길이가 일인 단위벡터 엔으로, 회전량은 각도 세타로 기록합니다. 이것이 축, 각 표현입니다.',
 '예를 들어 축을 영, 일, 영으로 두고 구십 도 돌리면, 양의 제트 방향이 양의 엑스로 갑니다.',
 '앞쪽 방향만 움직이는 것이 아니라, 몸에 붙은 세 축 전체가 그 축을 중심으로 같이 돌아갑니다.',
 '단위축은 세 성분을 쓰지만 길이 제약이 있습니다. 각도까지 네 성분을 저장해도 자유도가 네 개인 것은 아닙니다.',
 '정해 둔 한 축에서 회전량을 절반으로 만들려면 각도를 절반으로 하면 됩니다. 임의의 두 회전을 더하는 문제와는 다릅니다.'
],[
 'Euler rotation theorem says a change between two three-dimensional orientations can be expressed as rotation about one suitable axis.',
 'Store a unit axis n and angle theta. This is the axis-angle representation.',
 'For example, axis zero, one, zero and ninety degrees send positive z toward positive x.',
 'The entire attached frame rotates around that axis, not just its forward vector.',
 'The axis has three components with a unit-length constraint. Four stored components do not mean four degrees of freedom.',
 'For a selected axis, halving the angle halves the rotation amount. This is different from combining two arbitrary rotations.'
],['두 자세 사이 변화 → 적절한 한 축 회전','unit n + θ','n = (0,1,0), θ = 90°','몸체의 세 축 전체가 함께 회전','저장 성분 4 / 회전 자유도 3','같은 축: θ/2 → 절반의 회전량'])
explanation(19,'회전벡터의 길이가 각도','rotation-vector',[
 '축 벡터에 각도를 곱한 벡터 이, 즉 세타 엔을 만들 수 있습니다. 회전벡터라고 부릅니다.',
 '책에서는 이 표현을 지수 사상이라고 부릅니다. 엄밀한 수학에서 지수 사상은 이 벡터를 회전으로 보내는 연산의 이름입니다.',
 '라디안을 쓰고 축이 영, 일, 영이며 각도가 파이의 절반이면, 회전벡터는 영, 파이의 절반, 영입니다.',
 '벡터의 길이에서 영 이상의 각도를 얻고, 길이가 영보다 크면 정규화해서 축을 얻습니다.',
 '영 벡터는 회전이 없는 항등 자세입니다. 이때 영으로 나누어 축을 만들면 안 됩니다.',
 '축과 각도의 부호를 동시에 바꿔도 같은 벡터가 됩니다. 다만 최종 자세의 다른 중복까지 모두 없어지지는 않습니다.'
],[
 'Multiply the axis by the angle to obtain e equals theta n, a rotation vector.',
 'The book calls this an exponential-map representation. In formal mathematics, the exponential map is the operation sending this vector to a rotation.',
 'Using radians, axis zero, one, zero and angle pi over two give vector zero, pi over two, zero.',
 'Its length gives a nonnegative angle; for nonzero length, normalization gives the axis.',
 'The zero vector represents identity. Do not divide by zero to recover an axis there.',
 'Negating both axis and angle gives the same vector, but does not eliminate every alternative representation of the final orientation.'
],['e = θ n','회전벡터 / exponential-map 표현','e = (0, π/2, 0) [rad]','θ = ||e|| / n = e / ||e||','e = 0: 항등 / 축 정규화 금지','(-θ)(-n) = θ n'])
actual(20,'움직인 거리와 돌린 양을 구분하세요',[
 '이번에도 몸이 구조물 사이를 이동합니다. 화면에서 이동한 거리와 몸이 돌아간 양을 나눠 보세요.',
 '회전벡터는 공간에서 물체가 이동한 경로를 가리키는 화살표가 아닙니다.',
 '그 방향은 회전축이고, 길이는 선택한 단위의 회전각입니다.',
 '카메라가 함께 움직이므로 화면의 기울기만으로 그 벡터를 정확하게 복원할 수는 없습니다.',
 '실제 움직임을 이해할 때 위치 벡터, 앞쪽 방향벡터, 회전벡터의 뜻을 구분하는 것이 중요합니다.',
 '다음 그림에서는 같은 최종 자세를 만드는 서로 다른 회전벡터를 비교하겠습니다.'
],[
 'The body moves between structures again. Distinguish travel distance from the amount of turning.',
 'A rotation vector is not an arrow tracing the object translation through space.',
 'Its direction specifies the rotation axis, and its length specifies the angle in the chosen units.',
 'A moving camera prevents exact reconstruction of that vector from apparent screen tilt alone.',
 'Keep position vectors, forward direction vectors, and rotation vectors conceptually distinct.',
 'The next diagram compares different rotation vectors that yield the same final orientation.'
],[(460,483),(489,514),(515,523),(529,554)],'중심 이동, 몸 앞쪽 방향, 몸의 기울기 구분','회전벡터의 방향은 이동 방향이 아니라 회전축, 길이는 각도이다')
explanation(21,'한 바퀴 미만이어도 표현은 중복된다','axis-aliases',[
 '한 축 주위로 플러스 구십 도 돌린 결과와 마이너스 이백칠십 도 돌린 결과는 같습니다.',
 '각도를 길이로 표현하면, 같은 축의 구십 도 벡터와 반대 축의 이백칠십 도 벡터가 같은 끝 자세를 만듭니다.',
 '두 벡터의 길이는 모두 삼백육십 도보다 작습니다. 따라서 길이가 한 바퀴 미만이라는 조건만으로 유일하지 않습니다.',
 '보통 회전각을 영부터 백팔십 도까지로 정하고, 백팔십 도에서 축 부호를 고르는 별도 규칙을 둡니다.',
 '백팔십 도에서는 축을 뒤집어도 같은 회전입니다. 이 경계에 중복과 불연속이 남습니다.',
 '항등 자세에서는 각도가 영이므로 축이 무엇이든 결과가 같습니다. 회전벡터 영으로 다루면 축을 억지로 고를 필요가 없습니다.'
],[
 'Positive ninety degrees and negative two hundred seventy degrees around one axis have the same endpoint.',
 'With nonnegative angle lengths, a ninety-degree vector along an axis and a two-hundred-seventy-degree vector along its opposite axis yield the same orientation.',
 'Both lengths are below a full turn, so that bound alone does not make the representation unique.',
 'A common choice limits the angle to zero through one hundred eighty and adds an axis-sign rule at one hundred eighty.',
 'At one hundred eighty, opposite axes still yield the same rotation. Boundary duplication and discontinuity remain.',
 'At identity the angle is zero and every axis gives the same result. The zero rotation vector avoids choosing an arbitrary axis.'
],['+90°와 -270°: 같은 끝 자세','e₁ = 90° n / e₂ = 270° (-n)','둘 다 ||e|| < 360° → 유일하지 않음','보통 0 ≤ θ ≤ 180° + 경계 축 부호 규칙','180°: n과 -n이 같은 회전','0°: 축 임의 / e = 0'])
explanation(22,'회전벡터는 보통 더할 수 없다','nonadd',[
 '회전벡터라는 이름 때문에 두 회전을 성분별로 더하고 싶을 수 있습니다. 유한한 회전에서는 보통 틀립니다.',
 '엑스축 구십 도 회전 뒤 와이축 구십 도 회전은, 두 회전벡터를 더해 한 번 도는 것과 다릅니다.',
 '벡터 덧셈은 순서를 바꿔도 같습니다. 하지만 앞에서 본 회전은 순서를 바꾸면 자세가 달라집니다.',
 '따라서 두 연산이 일반적으로 같을 수 없습니다. 합성은 회전 행렬이나 뒤에서 배울 쿼터니언 곱으로 계산합니다.',
 '각도가 아주 작으면 합이 근사값이 될 수 있지만, 유한한 각도에서 정확한 공식이라고 쓰면 안 됩니다.',
 '회전량 벡터와 순간적인 회전 변화율 벡터는 용도가 다릅니다. 다음 장면 뒤에 각속도와도 구분하겠습니다.'
],[
 'The name rotation vector may tempt us to add components. That generally fails for finite rotations.',
 'An x ninety-degree rotation followed by y ninety degrees differs from one rotation using their summed vectors.',
 'Vector addition commutes, whereas the rotations we observed change the result when reordered.',
 'These operations therefore cannot generally be equal. Compose using rotation matrices or the quaternion product introduced later.',
 'For very small angles, addition may provide an approximation, but it is not an exact finite-angle formula.',
 'A vector describing rotation amount and a vector describing instantaneous rotational rate serve different purposes. We will distinguish angular velocity next.'
],['유한 회전: e₂ 뒤/앞 순서를 보존','Rx(90°) 후 Ry(90°) ≠ Exp(eₓ + eᵧ)','벡터 합은 교환 / 회전 합성은 비가환','정확한 합성: 행렬곱 또는 쿼터니언곱','작은 각도에서만 1차 근사 가능','회전량과 순간 변화율을 구분'])
actual(23,'세 축의 변화가 섞인 실제 움직임',[
 '몸이 계속 방향을 바꾸고 기울어지는 비행을 마지막으로 보겠습니다.',
 '복잡한 움직임도 각 순간의 자세와 그 사이의 변화로 나눠 생각할 수 있습니다.',
 '헤딩과 기울기가 동시에 바뀌는 듯 보여도, 화면만 보고 내부에서 각도를 더한다고 결론 내릴 수는 없습니다.',
 '수학 모델에서는 축 기준과 합성 순서를 정하고 결과를 확인해야 합니다.',
 '회전벡터의 성분을 더하는 간단한 방법이 맞는지, 작은 각도 근사인지, 정확한 합성인지 구분하세요.',
 '이제 회전량과 초당 회전량을 구분하고, 배운 내용을 두 문제로 확인하겠습니다.'
],[
 'Watch the body keep changing direction and tilt one last time.',
 'Even complex motion can be considered as orientations at each instant and changes between them.',
 'Simultaneous-looking changes in heading and tilt do not reveal whether the implementation adds angles.',
 'Our mathematical model must define axis references and composition order before checking the result.',
 'Distinguish component addition, a small-angle approximation, and exact rotation composition.',
 'Now we will separate rotation amount from rotation per second and check the lesson with two problems.'
],[(560,574),(581,614)],'팔의 기울기와 전진 방향이 함께 변하는 연속 비행','관찰만으로 구현을 단정하지 않고 합성 규칙과 근사/정확 계산을 구분')
explanation(24,'각속도와 여러 바퀴의 회전 기록','angular-rate',[
 '각속도 벡터의 방향은 순간적인 회전축이고, 길이는 초당 라디안 같은 회전 변화율입니다.',
 '초당 칠백이십 도와 초당 천팔십 도는 각각 두 바퀴와 세 바퀴입니다. 서로 다른 움직임입니다.',
 '하지만 일 초 뒤의 최종 자세만 보면 둘 다 시작 자세로 돌아옵니다. 끝 자세만으로 회전 이력을 구별할 수 없습니다.',
 '여러 바퀴의 동작이 필요하면 누적 각도나 시간에 따른 각속도를 별도로 기록해야 합니다.',
 '순간적인 각속도를 더할 때에도 같은 좌표계로 표현해야 합니다. 몸체 기준과 월드 기준 벡터를 바로 더하면 안 됩니다.',
 '이 단위와 좌표계 구분은 뒤의 원운동과 강체 역학에서 다시 이어집니다. 지금은 자세, 회전량, 회전속도를 나눠 기억하세요.'
],[
 'An angular velocity vector points along an instantaneous rotation axis, and its magnitude is a rate such as radians per second.',
 'Seven hundred twenty and one thousand eighty degrees per second are two and three turns: different motions.',
 'After one second, however, both endpoint orientations match the start. Endpoint orientation cannot distinguish their histories.',
 'Track accumulated angle or time-varying angular velocity separately when multiple turns matter.',
 'Instantaneous angular velocities must use a common frame before addition. Do not directly add body-frame and world-frame components.',
 'These unit and frame distinctions return in circular motion and rigid-body dynamics. Keep orientation, rotation amount, and rotation rate separate.'
],['ω: 순간 축 × 회전 변화율 [rad/s]','720°/s = 2회전 / 1080°/s = 3회전','1초 후 끝 자세는 같아도 움직임은 다름','누적 회전량·시간 이력은 별도 기록','각속도 합: 먼저 같은 좌표계로 변환','자세 / 회전량 / 회전속도'])
explanation(25,'직접 풀어 보는 두 문제','practice',[
 '첫 문제입니다. 시작 헤딩이 백칠십 도, 끝 헤딩이 마이너스 백칠십 도일 때 짧은 차이는 얼마일까요?',
 '그대로 빼면 마이너스 삼백사십 도입니다. 한 바퀴를 더하면 플러스 이십 도가 됩니다.',
 '따라서 중간 비율이 절반이면 백팔십 도를 거칩니다. 끝점 규칙까지 일관되게 적용하세요.',
 '두 번째입니다. 회전벡터가 영, 파이의 절반, 영이고 단위가 라디안일 때 축과 각도는 무엇일까요?',
 '길이는 파이의 절반, 즉 구십 도이고 축은 영, 일, 영입니다. 우리 오른손 규칙에서 앞쪽 제트는 양의 엑스로 갑니다.',
 '여기에 엑스축 구십 도 회전을 더 합성하려면 벡터 성분을 그냥 더하지 말고, 어느 회전을 먼저 적용하는지부터 정해야 합니다.'
],[
 'First problem: from heading one hundred seventy to minus one hundred seventy degrees, what is the short difference?',
 'Direct subtraction gives minus three hundred forty. Add a full turn to obtain positive twenty.',
 'At halfway we pass one hundred eighty degrees. Apply the chosen endpoint convention consistently.',
 'Second problem: for rotation vector zero, pi over two, zero in radians, what are the axis and angle?',
 'The length is pi over two, or ninety degrees, and the axis is zero, one, zero. Our right-hand rule sends forward z toward positive x.',
 'To additionally compose an x ninety-degree rotation, do not simply add vector components: decide the application order first.'
],['문제 1: +170° → -170°','Δ = wrapPi(-340°) = +20°','절반: 180° / 끝점 규칙 유지','문제 2: e = (0,π/2,0) [rad]','θ = π/2 / n = (0,1,0) / +z → +x','추가 회전: 성분합보다 순서와 합성 규칙 먼저'])
explanation(26,'축·순서·단위를 함께 기억하세요','summary',[
 '오일러 각은 사람이 다루기 쉬운 세 숫자지만, 축과 순서가 빠지면 뜻이 정해지지 않습니다.',
 '짐벌락은 정해진 매개화에서 두 축이 겹치는 현상이며, 물체의 회전 능력이 사라지는 것은 아닙니다.',
 '축, 각과 회전벡터는 한 축 주위의 회전을 표현합니다. 단위와 영 벡터, 중복 표현, 합성의 한계를 함께 확인하세요.',
 '다음 시간에는 쿼터니언이 어떻게 같은 회전을 네 성분으로 표현하는지, 곱과 역회전을 실제 숫자로 계산해 보겠습니다.'
],[
 'Euler angles are three convenient numbers for people, but their meaning requires defined axes and order.',
 'Gimbal lock aligns two axes in a chosen parameterization; it does not remove the object ability to rotate.',
 'Axis-angle and rotation vectors describe rotation about one axis. Check units, zero vectors, alternative representations, and composition limits.',
 'Next we will represent rotations with four quaternion components and calculate products and inverses with actual numbers.'
],['오일러 각: 세 숫자 + 축 + 순서','짐벌락: 좌표 표현의 특이점','축·각 / 회전벡터: 단위·중복·합성 주의','다음: 쿼터니언 성분·곱·역회전'])
data={'slug':slug,'chapter':8,'part':2,'totalParts':4,'renderModule':'euler','sourceSections':['8.3.1','8.3.2','8.3.3','8.3.4 with corrected wrap condition/endpoints','8.3.5','8.4 with corrected nonuniqueness bound'],
 'contract':{'handedness':'right','vector':'column','transform':'local-to-world','axes':'Positive axes are defined by arrows, x cross y = z. y drawing-up, body z forward; screen/anatomical directions do not define handedness.','order':'Intrinsic body Y-X-Z; R=Ry(h)Rx(p)Rz(b), equivalent extrinsic fixed Z-X-Y.','bookDifference':'Left-handed/row-vector book conventions adapted explicitly; signs and basis must be checked independently of transpose.','units':'Narrative examples in degrees; code and rotation vectors explicitly radians.'},
 'scenes':scenes,'coverage':{'8.3.1':['03','04'],'8.3.2':['05','06','07','08'],'8.3.3':['09','16'],'8.3.4':['09','10','11','12','13','14','15','16'],'8.3.5':['25','26'],'8.4':['17','18','19','20','21','22','23','24','25']},
 'gameCandidates':{'reviewedAt':'2026-10-05','selected':[{'game':'Superflight','sourceId':'FvSgGn941U0','reason':'Fresh recording and nonrepeated source intervals illustrating body axes, tilt and forward direction in this connected chapter. Explicit free-use recording permission observed. Same-game reuse considered explicitly.'}],
 'rejected':[{'game':'Ace Combat7','sourceId':'t3QYpA_-Iss','reason':'Uploader requests public description credit, conflicting with user publishing defaults. Do not ignore the condition.'},{'game':'Distance','sourceId':'eUjG48VFk44','reason':'No explicit recording reuse permission observed.'},{'game':'Trailmakers','reason':'Candidate official overview did not establish permission for inspected concept-matched recording.'},{'game':'NCR Superflight','sourceId':'-Hpr1dqRzIk','reason':'Already used in immediately preceding lecture; choose different recording and intervals.'}],
 'historyReview':'Reviewed existing project source inventory and first orientation lecture; no previously used Morkala intervals. Exclude all original audio and OST.'}}
assert [s['id'] for s in scenes]==[f'{i:02d}' for i in range(1,27)]
write(B/'lessons'/f'{slug}.json',data)
evidence=read(B/'preflight/studio-rotation-review.json');evidence['candidate']=slug;evidence['distinctReason']='The previous PART1 matrix lecture includes rotation matrices/Rodrigues but not a full intrinsic-versus-extrinsic Euler convention, gimbal parameter singularity, corrected wrap implementation, or rotation-vector aliases/nonadditivity. The new orientation lecture covers8.1–8.2 and uses Rz90 as a prerequisite; this lecture covers8.3–8.4 with different viewer question, worked calculations and source intervals. Actual Studio Euler title search had zero results, and nearest full transcripts were read.'
write(B/'preflight/studio-euler-review.json',evidence)
print(json.dumps({'slug':slug,'scenes':len(scenes),'koLines':sum(len(s['ko']) for s in scenes),'koChars':sum(sum(map(len,s['ko'])) for s in scenes),'actualCapacity':sum(s.get('maxSeconds',0) for s in scenes)},ensure_ascii=False))
