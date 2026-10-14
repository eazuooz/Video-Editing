"""Lightweight preparation only: no model, decoding, source adoption or UI."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;P=BASE.parent;PUB=P/'publishing'
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-limited-color-world'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=datetime.now(timezone.utc).isoformat()
req=read(BASE/'narration-tts-request-v1.json')
for x in req['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
def write(p,s):
 assert not p.exists(),f'Preserve existing prepared file: {p}'
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def save(p,d):write(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
defaults=read(ROOT/'shared/publishing/youtube-defaults.json')
ko=read(P/'script/narration.ko.json');en=read(P/'script/narration.en.json')
coaching=defaults['coaching']['url'];membership=defaults['membershipUrl']
originalFooter=(ROOT/defaults['description']['channelDefaultSnapshot']).read_text('utf-8-sig')
footer=originalFooter.split('📚 수업 노트')[0].rstrip()
# The separator preceding omitted, unfilled notes/GitHub is also omitted.
if footer.endswith('━━━━━━━━━━━━━━━━━━'):footer=footer[:-len('━━━━━━━━━━━━━━━━━━')].rstrip()
discord='https://discord.gg/wZuqe7fqkR'
assert all(link in footer for link in [coaching,membership,discord])
bodies={
 'ko':'색을 구별하기 어려워도 어디로 가고 무엇을 눌러야 할지 읽을 수 있는 화면은 어떻게 만들까요? 치커리의 실제 플레이에서 집의 윤곽, 식물의 높이와 움직임, 어두운 공간의 대비를 차례로 살펴봅니다.\n\n색과 구조를 나누고, 무늬와 형태를 더하고, 현재 상태와 중요한 경계를 보여 주는 방법을 입체 도식에 연결합니다. 흑백·색 인지 미리보기로 문제를 찾은 뒤 실제 플레이에서 대상과 상태, 다음 행동이 읽히는지 확인하는 순서도 정리합니다.\n\n장치의 손잡이와 배경 가림 비교는 설계 예시입니다. 미리보기나 한 장면만으로 모든 플레이어의 접근성을 보장한다고 판단하지 않습니다.',
 'en':'How can a screen communicate where to go and what to interact with when colors are difficult to distinguish? We examine house outlines, plant height and motion, and contrast in dark spaces through actual Chicory gameplay.\n\nSpatial diagrams connect these observations to separating fill from structure, adding pattern and shape, communicating current state, and keeping important boundaries readable. We also connect grayscale and color-perception previews to actual play checks of targets, states and the next action.\n\nThe device handles and background-occlusion comparisons are design examples. A preview or a single scene does not establish accessibility for every player.'}
englishFooter='🎮 YamYamCoding helps you build practical game-programming skills through design and implementation.\n\n🚀 Premium one-to-one coaching\nDirectX 11/12, Unity, Unreal Engine, computer graphics, PBR, shaders, rendering, game engines, and graphics research implementation.\n'+coaching+'\n\n💬 Community: questions, code reviews, feedback, and study materials\nDiscord\n'+discord+'\n\nYouTube membership\n'+membership
preparedFiles=[]
for lang,tail,tags in [('ko',footer,'#게임개발 #게임디자인 #게임접근성'),('en',englishFooter,'#GameDevelopment #GameDesign #GameAccessibility')]:
 for name,text in [('description-body.'+lang+'.txt',bodies[lang]),('description-prepared.'+lang+'.txt',bodies[lang]+'\n\n'+tail+'\n\n'+tags)]:
  path=PUB/name;write(path,text+'\n');preparedFiles.append(path)
comment='내 화면의 중요한 정보가 색 하나에만 의존하는지, 윤곽·무늬·움직임·밝기 차이로 다시 살펴보세요. 게임 프로그래밍을 함께 설계하고 구현하는 1:1 과외 안내: '+coaching
write(PUB/'pinned-comment.ko.txt',comment+'\n');preparedFiles.append(PUB/'pinned-comment.ko.txt')
enChapters=['Read the Next Action','Separate Fill from Outline','Patterns Retain Information','Read Height and Motion','Show the Current State','Prioritize Route Information','Retain Contrast in Darkness','Check the Cues in Actual Play']
prep=dict(schemaVersion=1,slug='limited-color-world',preparedAt=stamp,status='prepared-only-before-measured-voice-and-final-media',
 titles={'ko':ko['title'],'en':en['title']},plannedChapters=[dict(scene=s['id'],titleKo=s['title'],titleEn=e,startSeconds=None) for s,e in zip(ko['scenes'],enChapters)],
 measuredChaptersPrepared=False,exactCanonicalLinks=dict(coaching=coaching,discord=discord,membership=membership),
 channelIntroductionPreserved=True,unfilledChannelPlaceholdersOmitted=True,publicSourceCredits=False,
 thumbnail=rel(PUB/'thumbnail-upload-v1.jpg'),thumbnailOriginal=rel(PUB/'thumbnail-v1.png'),
 thumbnailPackaging=dict(jpegEncodingOnly=True,semanticImageEdits=False,geometryAndDimensionsPreserved=True,sameDecodedPixelsVerified=False,lossless=False,bytes=(PUB/'thumbnail-upload-v1.jpg').stat().st_size,dimensions=[1672,941]),
 card=dict(startSeconds=0,url=coaching,saved=False),endScreen=dict(durationSeconds=10,startSeconds=None,elements=defaults['endScreen']['elements'],saved=False),
 pinnedComment=dict(path=rel(PUB/'pinned-comment.ko.txt'),exactPreparedText=comment,status='pending-video-publication',posted=False,pinned=False),
 actualVideoId=None,uploaded=False,scheduled=False,targetDate='2026-11-01',targetTime='09:00',timezone='Asia/Seoul',targetIsPlatformReservation=False,
 platformSettingsVerified=False,savedPlatformThumbnailVerified=False,manualSrtPublished=False,englishMetadataPublished=False,uploadedCcOffPixelsVerified=False,actualAdChecksComplete=False,
 humanListening='pending',humanPronunciation='pending',finalPublicRights='pending',localOnly=True,imagesGitAdded=0,
 defaultsSha256=sha(ROOT/'shared/publishing/youtube-defaults.json'),channelSnapshotSha256=sha(ROOT/defaults['description']['channelDefaultSnapshot']),
 files=[dict(path=rel(x),sha256=sha(x)) for x in preparedFiles])
save(PUB/'publishing-text-preparation-v1.json',prep)
bank=read(PROOF/'source-action-bank-v1.json')
proposals=[
 ('room-to-corridor',1,99,111,'02-contours','Move through outline-defined floor, door and portrait corridor; compare structure with painted rooms.','Split door/area-title transition and reject any dialogue/static title. This interval is not claimed to be continuously clean.'),
 ('town-outline-route',1,172,177,'02-contours','Character navigation along path/fence/tree landmarks whose outlines and hatching distinguish the route.','Exclude171 transition and178 sign; choose only active travel where its route is clear.'),
 ('palette-before-current',1,234,238.5,'02-contours','Earlier unique palette/painting actions preceding the selected changing-fill sequence.','No source-frame overlap; reject color-menu waiting and any obstructing UI. Combine adjacent actions once, never replay.'),
 ('room-paint-continuation',1,159,168.5,'02-contours','Continue unique active painting of room/outside structure after the preserved4s interval.','Reject off-object wandering/idle; only visible action with clear surviving contour is eligible.'),
 ('flower-before-paint',1,532,535,'05-state-not-hue','Show current tall flower and beginning of actual interaction before the selected shrinking interval.','Reject any tutorial/sign/static waiting; observe exact state and action before claiming a causal change.'),
 ('mushroom-arrival',2,27,29.5,'04-height-and-motion','Unique continuation of bouncing/arrival after the selected raised mushroom sequence.','Exclude transition30; verify contact, compression and landing, without claiming the best route.'),
 ('four-mushroom-ledged-arrival',2,110,111.5,'04-height-and-motion','Unique final jump toward the outlined destination after the preserved four-mushroom sequence.','Reject transition/fade; exact destination arrival must be visible before inclusion.'),
 ('flower-stack-state-continuation',2,56,61,'05-state-not-hue','Unique plant operation and movement after the selected stack action, comparing the state while moving.','Reject repetitive paint/idle and litter overlay62; do not infer permanent unlock.'),
 ('flower-route-arrival',2,95.5,97.5,'06-route-information','Finish the unique route action after the selected second route portion.','Reject any wait/wipe before98; show player, platform top and destination boundary clearly.'),
 ('tree-outline-paint',1,594,598,'02-contours','Different object: actual tree painting while trunk/leaves contours remain.','Explicitly announce changing from house to tree if used; requires observed action and a matching additive narration, not the house-specific sentence.')]
rows=[]
for key,num,a,b,scene,action,caution in proposals:
 sourceKey=f'chicory-b-roll-{num}';f0=round(a*60);f1=round(b*60)
 assert not any(w['sourceKey']==sourceKey and max(f0,w['startFrame'])<min(f1,w['endFrameExclusive']) for w in bank['windows'])
 rows.append(dict(key=key,sourceKey=sourceKey,plannedStartFrame=f0,plannedEndFrameExclusive=f1,plannedStartPts=f0*256,plannedEndPtsExclusive=f1*256,
  timeBase='1/15360',frameRate='60/1',candidateSeconds=b-a,provisionalInsertion=scene,visibleActionToVerify=action,
  caution=caution,basis='Previously directly reviewed coarse observations; candidate labels are not native-boundary/action/continuous-playback approval.',
  nativeBoundaryReviewed=False,normalPlaybackReviewed=False,finalCueUiReviewed=False,sourceAdoptionApproved=False,selected=False,
  normalSpeedOnly=True,loop=False,slowdown=False,sourceAudio=False))
plan=dict(schemaVersion=1,slug='limited-color-world',preparedAt=stamp,status='unadopted-additional-action-candidates-awaiting-voice-measurement-and-native-review',
 protectedOriginalBank=dict(path=rel(PROOF/'source-action-bank-v1.json'),sha256=sha(PROOF/'source-action-bank-v1.json'),maximumApprovedPlanningSeconds=101.5),
 candidates=rows,proposedCandidateSeconds=sum(x['candidateSeconds'] for x in rows),potentialTimeIsNotApprovedFootage=True,
 allCandidatesDisjointFromProtectedSelectedFrames=True,additionalMediaCreated=False,additionalDecodeStarted=False,additionalFramesExtracted=False,
 sourceAdoptionApproved=False,actualRatioApproved=False,
 nextAction='After actual voice measurement determine need, compare candidate normal playback/before-action-after and exact nativePTS, reject transitions/idle and inspect fixed-caption framing. Reuse existing native/coarse PNGs; extract only missing new PTS once under CPU2/GPU0 and adequate fresh resources. Preserve protected original source bank while activeTTS is running.')
save(PROOF/'additional-action-candidates-v2.json',plan)
for x in req['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
# Correct packaging wording: JPEG changes sample values, never claim identical decoded pixels.
trPath=PUB/'prepared-thumbnail-direct-review-v1.json';tr=read(trPath)
tr['serialization']='Single JPEG delivery encoding with unchanged composition, dimensions and geometry; decoded values are lossy and are not claimed identical to PNG. Original PNG and generated source preserved.'
tr['jpegEncodingOnly']=True;tr['semanticImageEdits']=False;tr['sameDecodedPixelsVerified']=False;tr['lossless']=False
trPath.write_text(json.dumps(tr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared exact KOEN publishing text/comment/8 untimed chapters and10 unadopted disjoint candidates49.5s. Original10 voice inputs/101.5s bank unchanged; extra decode/extraction/model/UI/Git0.')
