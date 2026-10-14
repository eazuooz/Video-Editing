"""Prepare additive paired text and source-bound causal mapping, no synthesis."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
kp=O/'script/cross-game-additions.ko.json';ep=O/'script/cross-game-additions.en.json'
assert not kp.exists() and not ep.exists()
rows=[
 dict(id='01b',title='새 비교 예시의 순서',afterScene='01',game=None,
 ko=['비행과 자전거의 자세를 비교한 뒤, 조립 비행기와 부품 배치에 같은 기준을 적용하겠습니다.'],
 en=['After comparing the orientations of a flying character and a bicycle, we will apply the same frame-based reasoning to a assembled aircraft and component placement.']),
 dict(id='03b',title='자전거에서도 위치와 자세를 나눕니다',afterScene='03',game='Descenders',
 ko=['방향과 자세의 차이는 자전거에서도 보입니다.','디센더스는 산길을 달리고 점프하는 자전거 게임입니다.','먼저 굽은 길에서 이동하는 위치와 기울어진 자전거를 나누어 보세요.','다음 점프에서는 바퀴가 위로 뒤집혔다가 착지 전에 다시 아래로 돌아옵니다.','이동 방향만으로 이 뒤집힘을 표현할 수 없으니, 자전거의 앞과 위를 함께 기록해야 합니다.'],
 en=['We can also see the distinction between direction and orientation on a bicycle.','Descenders is a cycling game about riding mountain trails and making jumps.','First separate the changing position on a winding trail from the bicycle leaning.','In the next jump, the wheels turn upside down and then face downward again before landing.','Travel direction alone cannot describe that inversion, so we need to record both the front and the top of the bicycle.']),
 dict(id='07b',title='앞과 날개를 함께 읽는 비행 자세',afterScene='07',game='Trailmakers',
 ko=['이제 트레일메이커스의 조립 비행기로 축의 의미를 확인하겠습니다.','이 게임은 부품으로 만든 탈것을 직접 움직입니다.','활주로를 떠난 뒤 날개가 기울고, 다음 시점에서는 거의 수평으로 돌아옵니다.','붉은 선은 기체의 앞, 파란 선은 날개 양쪽을 잇는 방향입니다.','두 선을 함께 보면 앞쪽 방향만 볼 때 놓친 기울기를 구분할 수 있습니다.','카메라도 움직이므로 화면의 선은 관찰 표시이며, 앞의 구십 도 계산은 따로 정한 수학 예입니다.'],
 en=['Now we will use an assembled aircraft in Trailmakers to see what the axes mean.','In this game, you build vehicles from parts and drive or fly them.','After takeoff the wings tilt; from the next viewpoint they return to nearly level.','The red line marks the front of the aircraft, and the blue line connects the two sides of its wings.','Reading both lines helps us distinguish inclination that the forward direction alone misses.','The camera also moves, so these screen lines are observation guides; our earlier ninety-degree calculation is a separately defined mathematical example.']),
 dict(id='10b',title='비행 자세에서 부품 배치 자세로',afterScene='10',game='Space Engineers',
 ko=['날아가는 물체의 자세를 기록했다면, 배치할 부품의 자세도 같은 방식으로 생각할 수 있습니다.','스페이스 엔지니어스에서는 부품을 조립해 우주선을 만듭니다.','초록 상자 속 흐릿한 부품은 아직 놓기 전의 미리보기입니다.','작은 부품이 세로에서 가로로 바뀌고, 다시 돌아온 뒤 실제 부품으로 놓이는 모습을 보세요.','크기 선택이 바뀌는 장면은 회전과 구분합니다.','비행 중인 기체와 달리 배치 자세를 고르는 상황이지만, 물체의 축을 같은 기준에서 기록한다는 원리는 같습니다.'],
 en=['Once we can record the orientation of a flying object, we can reason in the same way about a component we are about to place.','In Space Engineers, parts are assembled to build spacecraft.','The translucent component inside the green box is a preview that has not yet been placed.','Watch the small component change from upright to sideways, turn back, and then appear as a placed solid component.','A change of size selection is separate from rotation.','Here we choose a placement orientation rather than fly an aircraft, but the shared principle is to record the object axes in one reference frame.'])]
for lang,p in [('ko',kp),('en',ep)]:
    p.write_text(json.dumps(dict(title='방향과 회전 행렬 · 네 게임 연결 비교',status='prepared-direct-paired-review-pending',scenes=[dict(id=r['id'],title=r['title'],lines=r[lang]) for r in rows]),ensure_ascii=False,indent=2)+'\n','utf-8')
addKo=read(O/'script/additions.ko.json');addEn=read(O/'script/additions.en.json')
repairKo=next(s for s in addKo['scenes'] if s['id']=='21a')['lines'][0]
repairEn=next(s for s in addEn['scenes'] if s['id']=='21a')['lines'][0]
for lang,text in [('ko',repairKo),('en',repairEn)]:
    p=O/f'script/cross-game-repair-batch.{lang}.json';assert not p.exists()
    scenes=[dict(id=r['id'],title=r['title'],lines=r[lang]) for r in rows]+[dict(id='21r',title='21a 첫 원문 보정 후보',lines=[text])]
    p.write_text(json.dumps(dict(title='방향과 회전 행렬 · 추가 비교와 첫 원문 후보',status='voice-measurement-only',scenes=scenes),ensure_ascii=False,indent=2)+'\n','utf-8')
mp=O/'tts-cross-game-repair-manifest-v1.json';assert not mp.exists();m=read(O/'tts-manifest-v1.json')
m['paths']['script']=(O/'script/cross-game-repair-batch.ko.json').relative_to(ROOT).as_posix()
m['paths']['scriptEn']=(O/'script/cross-game-repair-batch.en.json').relative_to(ROOT).as_posix()
m['tts'].update(outputDir='shared/output/narration/game-math-orientation-matrices/cross-game-repair-batch-v1',filenameStem='orientation-cross-game-repair-v1')
m['scope']='Four additive scenes and one verbatim21a-p01 candidate only. Original24PCM and six additions remain unchanged. Final placement, ratio, currentmixedASR, captions/pixels are not approved.'
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf-8')
plan=O/'cross-game-causal-and-source-plan-v1.json';assert not plan.exists()
source=read(O/'cross-game-native-direct-review-v1.json')
data=dict(preparedAt=now,pairedKoScript=kp.relative_to(ROOT).as_posix(),pairedEnScript=ep.relative_to(ROOT).as_posix(),newScenes=rows,
 originalOverviewRetainedSeconds=20.16,overviewExtension='01b follows01 and names actual comparison order before02a/02; measured combined overview duration is pending.',
 retainedOriginal24ScenesAnd140ParagraphsEach=True,retainedOriginal6AdditionsAnd22ParagraphsEach=True,
 insertions=[dict(id='01b',after='01',before='02a',reason='New examples in their real order, one central orientation question.'),dict(id='03b',after='03',before='04',reason='Direction alone misses bicycle inversion; motivates full body axes.'),dict(id='07b',after='07',before='08',reason='Numerical axes lead to visible front/wing comparison; view and object frames remain distinct.'),dict(id='10b',after='10',before='11',reason='Same reference-frame representation transfers from flying body to component placement; parent/camera frames follow.')],
 sourceNativePlanning=source['observations'],spaceStaticReview='space-enlarged-static-direct-review-v3.json',
 geometry=dict(mathematicalAxes='Separate explicit model: xred/ygreen/zblue, right-handed column local→worldR. Actualguide colors label observed object roles; never call them engine-world axes.',descenders='Red guide follows rigid bicycle frame/front, not articulated rider; mark wheel/top relation only when visible. Hide guides at occlusion/camera cuts.',trailmakers='Red front guide and blue left-right wing guide; hide endpoints under bridge/at camera cuts. No continuity interpolation across viewpoint jumps.',spaceEngineers='Green native preview box remains identifiable; red part-direction guide reveals with narration. Show full-source rotation-key context before enlargement. Hide preview guide once placed; label resulting solid part separately.',fixedCaptions=[960,970],allMovingPixelsApproved=False),
 ratio=dict(baselineActualFrames=21370,baselineExplanationFrames=32055,actualShare=.4,explanationShare=.6,toleranceFrames=1,measurementPending=True,additionalActualFormula='max(0,(2/3)*addedExplanationFrames-addedActualFrames)',sourceCapacity='Native clear windows are a conditional bank, not finalduration. If currentmeasured speech requires more relevant unique action, secure clearer additional cuts; preserve all useful explanation and PCM, no loops/slowdown/unrelated idle.'),
 scopedRepair=dict(id='21r',originalScene='21a',paragraph=1,text=repairKo,reason='Both whole and independent currentASR omit 시작. Single exact original paragraph candidate; humanacoustic judgment remains pending.',candidateAdopted=False,retainOriginal6Pcm=True,preserveP2OnwardBytes=True),
 duplicateFullComparisonPending=True,wholePairedTextReviewed=False,finalFourGameTeachingApproved=False,newTtsStarted=False,originalLessonChanged=False)
plan.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(scenes=5,paragraphs=sum(len(r['ko']) for r in rows)+1,sourcePlanningOnly=True,newModel=0,newPcm=0)))
