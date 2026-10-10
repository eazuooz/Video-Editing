"""Author only footage-dependent additions after native playback and pixel comparison."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not any((ROOT/'shared/output/narration/game-math-interpolation-teaching-additions-v2').rglob('*.wav'))
proofs=[];played={}
for name in ['native-clean-cut-playback.json','native-reserve-cut-playback.json']:
    p=D/name;record=read(p);records=json.loads(record['observed']['records'])
    assert all(r['ended'] and r['rate']==1 for r in records)
    played.update({r['src'].removesuffix('.mp4'):r for r in records})
    proofs.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'observedAt':record['observedAt']})
assert all(f'IG{i:02}' in played for i in range(1,12))
cuts={**read(D/'clean-proposed-cuts.json')['cuts'],**read(D/'reserve-proposed-cuts.json')['cuts']}
content={
 'IG01':('절반 자세는 움직임 중간에 있습니다',[
 '스케이트 삼에서 자세가 이어지는 모습을 보겠습니다. 빨간 선은 몸체 방향입니다.',
 '파란 선은 보이는 보드의 긴 방향입니다. 출발, 공중, 착지를 따로 따라가세요.',
 '그 사이를 만들 비율이 티입니다. 앞의 사십오 도는 계산 예시이며 이 장면의 측정 각도가 아닙니다.'
 ],[
 'Observe connected poses in Skate 3. Red follows the body direction.',
 'Blue follows the visible board length. Follow takeoff, the airborne pose and landing separately.',
 'The fraction for constructing intermediate poses is t. The previous forty-five degrees was a worked example, not an angle measured here.'
 ],'54 upright/pushing →61–64 airborne body turn/land →68–72 board flip and upright73','The complete body/board actions are separated in silhouette; no menu or ragdoll interrupts the result.'),
 'IG02':('방향의 변화와 지나가는 속도 나누기',[
 '이번에는 빨간 몸체 선과 파란 보드 선이 바뀌는 순서를 보세요.',
 '움직인 거리와 중간 자세의 비율은 서로 다른 값입니다. 같은 장면에서도 카메라가 따라 움직입니다.',
 '화면에서 빨라 보인다고 일정한 각속도라고 단정할 수는 없습니다. 다음 계산에서는 시간 조건을 따로 고정합니다.'
 ],[
 'Watch the order in which the red body line and blue board line change.',
 'Travel distance and the fraction between orientations are different values. The camera also follows the action.',
 'Fast-looking screen motion does not establish constant angular speed. We will state the timing conditions separately in the calculation.'
 ],'109.5 pushing →117–120 jump/turn →127–131 flip →upright travel139','Compared with the reset-heavy392–442 cut, the same visible rider proceeds through readable actions and outcomes.'),
 'IG03':('보이는 방향에서 각도 읽기로 이어가기',[
 '같은 몸체가 기울었다가 서는 과정을 보겠습니다. 빨간 선은 몸체, 파란 선은 보드입니다.',
 '방향을 숫자로 바꾸려면 기준축을 먼저 정해야 합니다. 화면의 선은 카메라로 투영된 관찰값입니다.',
 '다음 삼각형은 축을 고정한 계산 예시입니다. 그 가로와 세로에서 길이와 방향각을 읽겠습니다.'
 ],[
 'Observe the same body lean and become upright. Red follows the body; blue follows the board.',
 'Turning a direction into numbers first requires axes. These screen lines are projected observations through the camera.',
 'The next triangle is a worked example with fixed axes. Read its length and direction angle from its horizontal and vertical components.'
 ],'210 pushing red bowl →216–234 airborne rotations and landings →240–242 road jump/land →upright247','The body remains identifiable against red ground, allowing observation to lead into the fixed-axis hypot/atan2 example.'),
 'IG04':('몸체와 보드에는 다른 방향이 붙어 있습니다',[
 '빨간 선은 몸체 방향입니다. 파란 선은 보드의 긴 방향입니다.',
 '몸과 보드의 방향이 따로 바뀌었다가 다시 이어집니다.',
 '각 대상을 구분해야 같은 방향 벡터로 계산 결과를 비교할 수 있습니다.'
 ],[
 'Red follows the body. Blue follows the visible board length.',
 'Their directions change separately and then reconnect.',
 'Distinguish the objects before comparing calculated results for the same direction vector.'
 ],'157.3 walking/boarding →159–172 flips and grind →upright173–174','A short close silhouette provides a clear object distinction without the later ragdoll188–190.'),
 'IG05':('같은 자세를 바꿔 적는 것과 실제로 돌리는 것',[
 '몸체의 빨간 방향을 보세요. 카메라가 따라와도 지금 몸체의 자세는 하나입니다.',
 '행렬을 쿼터니언으로 바꿔 적는다고 몸체가 추가로 도는 것은 아닙니다.',
 '이어서 다른 발췌입니다. 파란 보드 방향이 변하고 다시 착지합니다.',
 '자세가 실제로 바뀌는 동작과, 같은 자세를 다른 숫자로 옮기는 계산을 나누겠습니다.'
 ],[
 'Follow the red body direction. Even with a following camera, the body has one orientation at each instant.',
 'Converting a matrix to a quaternion does not add another physical rotation.',
 'This is a different excerpt. The blue board direction changes before another landing.',
 'Separate an action that changes the pose from a conversion that writes the same pose in different numbers.'
 ],'459–470.8 road body banking → next independent482.7–496 board jump/flip/land','Cuts exclude the obscured quarterpipe471–475, ragdoll476–478 and loading479–481. Separate excerpts are explicitly narrated.'),
 'IG06':('끝 자세와 검산의 목적 연결하기',[
 '마지막으로 몸체와 보드가 움직이는 방향을 함께 따라가겠습니다.',
 '빨간 몸체 선과 파란 보드 선은 다른 대상입니다. 같은 대상의 입력 방향과 결과를 비교해야 합니다.',
 '앞의 작은 수 예제는 카메라와 축을 고정해 그 비교를 검산한 것입니다.',
 '이 게임의 내부 회전값을 얻은 것은 아닙니다. 다음에는 움직인 점을 선과 경계로 정의하겠습니다.'
 ],[
 'Finally follow the body and board directions together through the action.',
 'The red body line and blue board line represent different objects. Compare the input and output direction of the same object.',
 'The worked numerical example fixed the camera and axes to verify that comparison.',
 'We have not extracted the game internal rotation values. Next define moving points as lines and bounds.'
 ],'569 boarding →573–582 banking →585–594 jumps/flips/landings →595–598 upright travel','The continuous rider survives each readable action; excludes earlier resets539–543 and562–568.'),
 'IG07':('지나온 회전의 기록과 현재 자세 나누기',[
 '빨간 몸체 방향이 바뀌고 다시 섭니다.',
 '현재 자세와 지나온 회전 과정은 다른 정보입니다.',
 '이어서 다른 발췌입니다. 파란 보드 방향도 따로 따라가세요.',
 '끝 자세 하나를 넘겨도 몇 바퀴 돌았는지까지 기록되지는 않습니다.'
 ],[
 'The red body direction changes and becomes upright again.',
 'The current pose and the rotation history are different information.',
 'This is a different excerpt. Follow the blue board direction separately as well.',
 'Passing the final orientation does not also store how many turns occurred.'
 ],'144 crouch →145 flip/146 land →149 grind/152 upright; independent193–208.5 hops/flips/landings','Two clean action extracts retain before/result without the ragdoll188–190. The discontinuity is stated rather than claimed as one rotation history.'),
 'IG08':('카메라의 그림과 몸체의 자세 구분하기',[
 '몸체의 빨간 선을 따라가세요. 카메라도 함께 따라 움직입니다.',
 '화면에 보이는 기울기는 몸체의 세 차원 각도와 같지 않습니다.',
 '다른 발췌에서도 같은 대상을 계속 보겠습니다.',
 '각도를 다시 찾는 검산에는 카메라 관찰과 별도로 정한 축과 회전값이 필요합니다.'
 ],[
 'Follow the red body line while the camera also moves with it.',
 'The tilt projected on screen is not the body three-dimensional angle.',
 'Continue observing the same object in a different excerpt.',
 'Verifying recovered angles requires declared axes and rotation data in addition to the camera observation.'
 ],'344.5 board/jump →346–355 crouched road banking; independent525 boarding →526–536 banking','Trims the earlier332–356 candidate loading341–342 and excludes537.7+ collision/reset; keeps follow-camera projection comparison.'),
 'IG09':('정보가 부족하면 각도를 추측하지 않습니다',[
 '몸체의 빨간 방향은 보이지만, 그 선만으로 회전축 전체가 정해지지는 않습니다.',
 '이어서 다른 발췌의 파란 보드 방향입니다.',
 '가려진 정보는 추측하지 않겠습니다.',
 '계산에서는 앞에서 정한 입력과 예외 규칙으로 같은 자세인지 검사합니다.'
 ],[
 'The red body direction is visible, but that line alone does not determine the complete rotation axis.',
 'This is the blue board direction in a different excerpt.',
 'We will not guess information that is hidden.',
 'The calculation uses the declared inputs and exceptional-case rules to verify the same orientation.'
 ],'442–449.5 road lean before quarterpipe collision; independent543.5–555.8 boarding/flip/land/road bank','Rejects collision450–452, static453, loading454–455 and542. End555.8 precedes the close quarterpipe occlusion556.'),
 'IG10':('움직이는 몸체와 단위 방향의 길이',[
 '빨간 선은 몸체, 파란 선은 보드 방향입니다.',
 '공중에서 몸과 보드가 바뀌고 다시 착지합니다.',
 '계산의 단위 길이는 저장한 방향값의 조건입니다.',
 '게임 속 이동 거리나 화면에서 보이는 선 길이를 일로 만든다는 뜻은 아닙니다.'
 ],[
 'Red follows the body; blue follows the board direction.',
 'Their directions change in the air before another landing.',
 'Unit length in the calculation is a condition on the stored direction values.',
 'It does not set the game travel distance or the displayed line length to one.'
 ],'89 crouch →90–96 flips/landings →100–104 airborne board/body changes →upright107','Close red-ground silhouettes reveal the two moving directions and clarify norm versus physical/screen length.'),
 'IG11':('한 자세를 여러 작업에 넘겨 쓰기',[
 '몸체를 나타내는 빨간 선과 보드의 파란 선을 비교해 보세요.',
 '물체가 움직여도 한 순간의 자세는 한 번 정해집니다.',
 '그 자세를 편집할 각도, 보간할 쿼터니언, 벡터에 적용할 행렬로 옮길 수 있습니다.',
 '바꿔 적은 숫자가 같은 방향을 만드는지 다음 왕복 계산에서 확인하겠습니다.'
 ],[
 'Compare the red body line and blue board line.',
 'The moving object has one orientation at a particular instant.',
 'That pose can be expressed as angles for editing, a quaternion for interpolation or a matrix for applying it to vectors.',
 'The next round trip checks whether the converted numbers produce the same direction.'
 ],'4 boarding →8–14 airborne turns/landing →16–22 jump/land →24–34 push/turn/upright','The long continuous red-bowl sequence supplies readable body and board changes without menus; end34.8 precedes the next airborne pose. Temporary hidden board anchors must be hidden rather than guessed.')
}
scenes=[]
for ident,(title,ko,en,action,reason) in content.items():
    intervals=cuts[ident];maximum=sum(b-a for a,b in intervals)
    assert len(ko)==len(en)
    row={'id':ident,'kind':'actual','sourceType':'actual-footage','title':title,'sourceId':'TPkvx2W8CV8','intervals':intervals,'maximumSeconds':maximum,'ko':ko,'en':en,'annotation':{'red':'visible body direction, anchored to torso','blue':'visible board length direction, not world axis','teal':'explicitly projected screen reference when useful; never implied world axis','illustrativeVsMeasured':'No game-world angle/quaternion/SLERP or engine internal measurements asserted. Fixed-axis numerical examples are explanation scenes.','reveal':'narration order with current-hash cues','tracking':'native29.97 times; hide board/body anchors during occlusion; independent cut reset','captionClearance':'fixed bottom960,970; gameplay HUD cleared by shot layout/labels above band','movingPixelApproval':False},'selection':{'sourceIntervals':intervals,'nativePlayback':played[ident],'visibleBeforeActionAfter':action,'camera':'following camera changes projection; preserve full-screen moving footage','occlusion':'body/board can overlap in airborne poses; hide unobservable anchors instead of guessing','UI':'score bottom-left, radar top-right; semantic lines remain over object and notes away from these and fixed captions','chosenReason':reason,'finalAnnotationReview':'pending'}}
    if len(intervals)==2:row['sourceGroupStartsAtLines']=[0,1 if ident=='IG09' else 2]
    scenes.append(row)
review={'allSelectedNativePlaybackCompared':True,'denseActionPixelsCompared':True,'playbackProofs':proofs,'classification':'Action-led full-screen moving gameplay with brief narrated tracked direction annotations; diagrams/frozen analysis remain explanation and are not counted twice','priorUse':'No previous Skate title found in scoped recent production manifests/source records. Selected native intervals are nonoverlapping with one another and with baseline Forza/Riders sources; this is not a claim of exhaustive channel history.','rejected':[{'source':'Skate3','interval':[332,356],'reason':'Original broad candidate includes loading341–342. Use344.5–356 only.'},{'source':'Skate3','interval':[442,459],'reason':'Collision450–452, static453/loading454–455. Keep442–449.5.'},{'source':'Skate3','interval':[542,557],'reason':'542 loading and556 close-camera occlusion. Keep543.5–555.8.'},{'source':'Skate3','interval':[392,442],'reason':'Resets, ragdoll and loading repeatedly break before/action/result.'},{'source':'RidersRepublic','interval':[440,510],'reason':'Results/menu/intro dominate; unavailable as teaching action quota.'},{'source':'RidersRepublic','interval':[244,292],'reason':'Results first, then occluded crowd and already-used baseline tail.'},{'source':'ForzaHorizon4','interval':[42,55],'reason':'Already used within retained baseline42–95; not a new footage insertion.'}], 'rights':'Uploader recording reuse statement verified in existing source record; game-IP/human review pending','narration':'authored only after the above actual comparisons','annotationsAndFinalRender':'pending'}
write(B/'interpolation-game-insertions.json',{'revisionOf':'game-math-rotation-interpolation','scenes':scenes,'review':review})
source=read(B/'interpolation-skate-source.json');source.update(candidateSelected=True,selectionEvidence=(B/'interpolation-game-insertions.json').relative_to(ROOT).as_posix(),finalMovingAnnotationApproval=False);write(B/'interpolation-skate-source.json',source)
print('11 nonoverlapping selected cuts; bilingual narration authored after comparison, final tracks and pixels pending.')
