"""Prepare truthful replacement metadata after the reviewed current pair is collected.

No browser actions, actual ID, upload or scheduling approval is inferred here.
Historical publishing files and the scheduled baseline remain unchanged.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/motion-sickness-games'
R=P/'production/revision-teaching-clarity-v1'
PUB=R/'publishing'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
pair=read(R/'final-pair-execution-v1.json')
session=read(R/'final-pair-execution-v1.session.json')
assert pair['exitCode']==0 and session['actualOuterExitCode']==0 and not session['workerCurrentlyAlive']
pixels=read(R/'final-pixel-direct-review-v1.json')
assert pixels['allListedSamplesDirectlyRead'] and pixels['allFinalCueCutPixelsApproved'] and not pixels['unresolved']
flow=read(R/'final-flow-playback-direct-review-v1.json')
assert flow['wholeNormalSpeedPlaybackReachedEnd'] and flow['sampledContinuousFlowApproved'] and not flow['unresolved']
assert flow['sourceSha256']==pixels['sourceSha256']==pair['pair'][1]['sha256']
audio=read(R/'current-mixed-complete-direct-review-v1.json')
assert audio['currentMixedContentReviewPassed'] and audio['all14WholeAnd66IndependentContextsDirectlyCompared']
plan=read(R/'measured-additive-plan-v1.json')
captions=read(R/'caption-alignment-v1.json')
delivery=read(P/'production/delivery-output.json')
assert delivery['cueCounts']=={'ko':179,'en':179} and len(delivery['files'])==4
for v in delivery['files']:
 assert sha(ROOT/v['source'])==v['sha256'] and sha(ROOT/delivery['directory']/v['name'])==v['sha256']
for v in pair['pair']:assert sha(ROOT/v['path'])==v['sha256']
assert abs(plan['ratioErrorFrames'])<=1 and captions['mixAacSha256']==audio['mixAacSha256']
assert not PUB.exists();PUB.mkdir()
old=read(P/'publishing/metadata-final.json')
defaults=read(ROOT/'shared/publishing/youtube-defaults.json')
koIntro=("게임의 목표를 따라가면서도 화면은 덜 돌릴 수 있을까요? 청소 게임의 조준과 시점, 퍼즐에서 방향이 바뀐 뒤 목표를 찾는 단서를 차례로 살펴보고, 카메라 설정과 되돌리기 기능의 설계로 연결합니다.\n\n"
 "파워워시 시뮬레이터의 에임 모드 개발 시연과 탈로스 프린서플2의 실제 플레이 장면을 보며, 화면에서 무엇이 움직이고 플레이어가 어떤 선택을 할 수 있는지 살펴봅니다. 빨간선으로 물줄기·조준 방향을, 다른 색의 짧은 표시로 기둥·바닥·목표 단서를 짚습니다. 이 선은 화면에서 보이는 관계를 설명하며 게임 엔진의 실측 좌표가 아닙니다.\n\n"
 "필요한 방향 전환과 부가 연출을 구분하고, 설정의 의미·현재 방향·목표를 알아보기 쉽게 설계하는 방법을 설명합니다. 개발 당시 자료와 설명용 제안을 구분하며 개인에게 같은 결과를 약속하지 않습니다.")
enIntro=("Can we follow a game's target while turning the whole view less? We examine aiming and viewing in a cleaning game, then the cues for recognizing a target after the view changes in a puzzle game. These observations lead to camera choices and a way to restore the original settings.\n\n"
 "We examine the PowerWash Simulator Aim Mode development demonstration and actual gameplay from The Talos Principle 2. Red lines identify the spray or aiming direction; other short colored markers identify posts, floor boundaries and target cues. These are explanations of visible screen relationships, not measured game-engine coordinates.\n\n"
 "The diagrams distinguish necessary changes in viewing direction from added presentation, and explain how to make settings, targets and current orientation understandable. Development-era footage and proposed interfaces are labelled separately. Individual responses can differ.")
english={'00a':'Overview: follow the target with less screen turning','06b':'After looking away, how do we find the target again?'}
oldEnglish=old['languages']['en']['chapters'][:-1]
for i in range(1,13):english[f'{i:02d}']=oldEnglish[i-1].split(' ',1)[1]
chapterRows=[]
for sc in plan['scenes']:
 sec=0 if sc['id']=='00a' else math.floor(sc['start'])
 chapterRows.append(dict(scene=sc['id'],startSeconds=sc['start'],startFrame=sc['startFrame'],platformStartSeconds=sec,
   ko='전체 안내: 목표를 따라가며 화면 움직임을 나누기' if sc['id']=='00a' else ('방향을 바꾼 뒤 목표를 다시 찾는 단서' if sc['id']=='06b' else sc['title']),en=english[sc['id']]))
chapterRows.append(dict(scene='membership',startSeconds=plan['bodyEnd'],startFrame=plan['totalFrames']-600,
 platformStartSeconds=math.floor(plan['bodyEnd']),ko='멤버쉽 후원 감사와 프로그래밍 과외',en='Membership thanks and programming coaching'))
clock=lambda n:f'{n//60:02d}:{n%60:02d}'
metadata={}
for lang,intro,heading in [('ko',koIntro,'챕터'),('en',enIntro,'Chapters')]:
 footer=(P/f'publishing/upload-description.{lang}.txt').read_text('utf-8-sig').split('🎮',1)
 assert len(footer)==2;footer='🎮'+footer[1].strip()
 body=intro+'\n\n'+heading+'\n'+'\n'.join(clock(v['platformStartSeconds'])+' '+v[lang] for v in chapterRows)
 description=body+'\n\n'+footer
 assert all(url in description for url in [defaults['coaching']['url'],defaults['membershipUrl'],'https://discord.gg/wZuqe7fqkR'])
 assert len(description)<=5000
 (PUB/f'upload-description.{lang}.txt').write_text(description+'\n','utf-8')
 metadata[lang]=dict(title=old['languages'][lang]['title'],description=description,descriptionBody=body)
comment=(P/'publishing/pinned-comment.ko.txt').read_text('utf-8-sig')
assert defaults['coaching']['url'] in comment
(PUB/'pinned-comment.ko.txt').write_text(comment,'utf-8')
thumbnail=P/'publishing/thumbnail-depth-v1.png'
baseline=read(P/'publishing/youtube-upload-depth-v1.json');assert baseline['videoId']=='c18rkesgBSw'
receipt=dict(schemaVersion=1,slug='motion-sickness-games',revision='teaching-clarity-v1',preparedAt=datetime.now(timezone.utc).isoformat(),
 status='reviewed-current-captioned-source-prepared; upload-and-platform-verification-pending',baselineVideoId='c18rkesgBSw',
 actualVideoId=None,url=None,source=rel(ROOT/delivery['directory']/'motion-sickness-games.captioned.mp4'),sourceSha256=pair['pair'][1]['sha256'],
 metadata=metadata,chapters=chapterRows,seconds=plan['seconds'],bodyEnd=plan['bodyEnd'],
 subtitleFiles=[dict(language=lang,path=rel(ROOT/delivery['directory']/f'motion-sickness-games.{lang}.srt'),
  sha256=sha(ROOT/delivery['directory']/f'motion-sickness-games.{lang}.srt'),cues=179,status='pending-manual-upload-with-timing') for lang in ['ko','en']],
 thumbnail=dict(path=rel(thumbnail),sha256=sha(thumbnail),reuseReviewedOriginal=True,savedOnNewUpload=False),
 initialPrivacy='private',uploaded=False,privateSaveVerified=False,fullSettingsVerified=False,automaticChecksPassed=False,
 burnedCaptionPixelsVerified=False,gitDelivered=False,scheduled=False,baselineScheduleChanged=False,
 coachingCard=dict(url=defaults['coaching']['url'],startSeconds=0,saved=False),
 endScreen=dict(startSeconds=plan['bodyEnd'],endSeconds=plan['seconds'],startFrame=plan['totalFrames']-600,
   endFrameExclusive=plan['totalFrames'],elements=defaults['endScreen']['elements'],saved=False),
 pinnedComment=dict(path=rel(PUB/'pinned-comment.ko.txt'),status='prepared-pending-comments-availability',commentId=None),
 humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 explicitWizardCompletionObserved=False,researchManipulations=0,newMediaRegenerated=False)
save(PUB/'youtube-upload-v1.json',receipt)
save(PUB/'publishing-text-direct-preparation-v1.json',dict(preparedAt=receipt['preparedAt'],metadata=metadata,
 chapters=chapterRows,allChapterTimesFromCurrentMeasuredPlan=True,oldDescriptionFooterAndCanonicalLinksRetained=True,
 actualId=None,uploaded=False,savedPlatformThumbnail=False,platformSettingsVerified=False))
print(json.dumps(dict(preparedOnly=True,chapters=len(chapterRows),koCues=179,enCues=179,actualId=None)))
