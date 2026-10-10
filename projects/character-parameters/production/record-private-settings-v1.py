"""Record the actually reopened Studio settings and two CC-off upload samples.

This records observations already made through CUA; it performs no platform action.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/character-parameters'
PUB=BASE/'publishing'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
receipt=read(PUB/'youtube-upload-v1.json')
assert receipt['actualVideoId']=='nic5Sp6dylQ' and receipt['uploadSelectedFiles']==1
qa=read(BASE/'production/final-v1/final-pixel-direct-review-v1.json')
collection=read(BASE/'production/collection-private-preflight-v1.json')
assert qa['qaApproved'] and qa['allFinalPixelsReviewed'] and collection['allFourSourceOutputSha256Identical']
assert qa['sourceSha256']==receipt['video']['sha256']
proofs={p.name:dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))for p in (PUB/'ui-proof-v1').glob('*.ax.txt')}
for name,required in {
 'private-details-reopened.ax.txt':['nic5Sp6dylQ','비공개','표준 화질 완료','고화질 완료','Planning & Game Design & Tech'],
 'automatic-checks-complete.ax.txt':['저작권 검사 완료 발견된 문제 없음 광고 적합성 검사 완료 발견된 문제 없음'],
 'advanced-settings-reopened.ax.txt':['AI가 사용되었습니다., Value: 1','유료 프로모션이 포함되어 있지 않습니다., Value: 1'],
 'en-metadata-reopened.ax.txt':['How Do Abilities Give a Character Its Identity?','수동 자막','게시됨'],
 'card-reopened.ax.txt':['0분 0초 0프레임','프로그래밍 코칭 · 과외','1430b1ff-a61e-8040-a542-d672d5d25328'],
 'end-subscribe-reopened.ax.txt':['6:19:57','6:29:57'],
 'end-playlist-reopened.ax.txt':['6:19:57','6:29:57','Planning & Game Design & Tech'],
 'end-link-reopened.ax.txt':['6:19:57','6:29:57','1430b1ff-a61e-8040-a542-d672d5d25328'],
 'monetization-reopened.ax.txt':['사용','8분을 초과하는 동영상만'],
 'claims-reopened.ax.txt':['소유권 주장이 발견되지 않았습니다','설정에 따라 수익을 창출'],
 'upload-game-settings.ax.txt':['자막 사용 안함','화질 1080p60 HD'],
 'en-reopened.ax.txt':['Does changing attack power and speed','sentence about the situation and choice you want players to remember.'],
}.items():
 text=(PUB/'ui-proof-v1'/name).read_text('utf-8')
 assert all(s in text for s in required),(name,required)
entries=[]
for file,purpose,reason in [
 ('thumbnail-upload-v1.png','delivery-thumbnail','Individually reviewed natural cat, yellow header, white illustrated ground and readable black/red Korean concept headline; actual saved Studio preview matches.'),
 ('private-details-proof-v1.png','minimal-publishing-proof','Actual reopened Studio shows this single ID private, completed SD/HD, correct uploaded thumbnail and title/description; required minimum private-delivery proof.'),
 ('upload-game-cc-off-proof-v1.png','minimal-publishing-proof','Actual uploaded 10-second 1080p60 Rivals frame shows burned bottom-center Korean caption, separated two-player HUD and original broadcast recorder credit with CC off.'),
 ('upload-black-cc-off-proof-v1.png','minimal-publishing-proof','Actual uploaded 5-second 1080p60 black explanation shows projected top/front/side faces, spatial floor and fixed Korean box with CC off; minimum explanation-upload proof.'),
]:
 p=PUB/file
 entries.append(dict(path=p.relative_to(ROOT).as_posix(),purpose=purpose,reason=reason,sha256=sha(p),reviewedAt=now,project='character-parameters'))
review=dict(schemaVersion=1,slug='character-parameters',actualVideoId='nic5Sp6dylQ',reviewedAt=now,
 savedPrivateVerified=True,fullSettingsVerified=True,platformAutomaticChecksComplete=True,
 thumbnailSavedAndReopened=True,manualKoCues=201,manualEnCues=95,manualKoSavedAndReopened=True,manualEnPublishedAndReopened=True,
 enAll95LiteralCueTextsDirectlyRead=True,englishMetadataPublishedAndReopened=True,measuredChapters=13,
 card=dict(timecode='0:00:00',url=receipt['card']['url'],title='프로그래밍 코칭 · 과외',callToAction='프로그래밍 코칭 안내',teaser='얌얌코딩 코칭 · 과외',originalCatImage=True,savedAndReopened=True),
 endScreen=dict(elements=receipt['endScreen']['elements'],savedAndReopened=True,uiTimecodes=dict(start='6:19:57',end='6:29:57'),uiTimecodeFrameRate=60,actualStartSeconds=379.95,actualEndSeconds=389.95,allThreeWithinOriginalMemberOutro=True,originalTwelveIdentitiesAndTitleClear=True,
  historicalPreprocessing30fpsQuantization=dict(start='6:19:29',end='6:29:28',supersededByActual60fpsSave=True)),
 checks=dict(sd=True,hd=True,copyright=True,adSuitability=True,observedResults='No problems found; no ownership claims; video earns according to its settings.'),
 monetization=dict(enabled=True,midrollEligible=False,selfCertification=receipt['monetization']['selfCertification'],submittedLocked=True),
 uploadedCcOffPixelsVerified=True,platformSamples=[dict(seconds=10,role='actual-existing-game',width=1920,height=1080,paused=True,muted=True,ccOff=True,observation='Visible action, bottom-center literal Korean box, both damage/stock HUDs and full original recorder credit remain separate.'),dict(seconds=5,role='explanation',width=1920,height=1080,paused=True,muted=True,ccOff=True,observation='Black background; teal/yellow/orange spatial cuboids with front/side/top faces and floor depth, readable gray footer and fixed Korean caption.')],
 allContinuousPlatformFramesReviewed=False,humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 wizardCompletionModalDirectlyObserved=False,automaticChecksCompletionBadgeDirectlyObserved=True,
 subtitleDownloadAttempt=dict(language='en',format='srt',attempts=1,outcome='CUA download event timed out; no completion or hash claimed. Saved manual status and all95 actual timeline texts were directly reopened instead.'),
 autoDubbing=dict(englishUS='processing',indonesian='processing',reviewApproved=False),minimalReviewedImages=entries,localOnlyAxProofs=proofs,
 pending=receipt['pending'],scheduled=False,gitDelivered=False,mediaOrQaImagesAdded=0)
save(PUB/'private-settings-direct-review-v1.json',review)
receipt.update(status='reviewed-private-settings-complete-awaiting-selective-git-and-schedule',updatedAt=now,uploaded=True,privateSaved=True,savedPrivateVerified=True,
 uploadProgressDirectlyObservedPercent=100,transferCompletionScope='Actual upload entered SD processing, then reopened details showed SD and HD complete.',
 chaptersVerified=True,englishMetadataPublished=True,manualSrtPublished=True,fullSettingsVerified=True,uploadedCcOffPixelsVerified=True,platformAutomaticChecksComplete=True,
 privateSettingsDirectReview='projects/character-parameters/publishing/private-settings-direct-review-v1.json')
receipt['thumbnail'].update(saved=True,verified=True)
for x in receipt['subtitles'].values():x.update(published=True,savedAndReopened=True)
receipt['card'].update(saved=True,verified=True)
receipt['endScreen'].update(saved=True,verified=True,uiTimecodes=dict(start='6:19:57',end='6:29:57'),uiTimecodeFrameRate=60,actualPlatformStartSeconds=379.95,actualPlatformEndSeconds=389.95,historicalPreprocessingQuantization=review['endScreen']['historicalPreprocessing30fpsQuantization'])
receipt['monetization'].update(actualAdChecksComplete=True)
receipt['checks'].update(sd=True,hd=True,copyrightComplete=True,adSuitabilityComplete=True)
save(PUB/'youtube-upload-v1.json',receipt)
project=read(BASE/'project.json')
project.update(status='reviewed-private-awaiting-selective-git-and-schedule',updatedAt=now)
project['publishing'].update(actualId=receipt['actualVideoId'],uploaded=True,fullSettingsVerified=True,receipt='projects/character-parameters/publishing/youtube-upload-v1.json')
project['approvals']['uploaded']=True
project['review']['narrationApprovalScope']='Whole current PCM and final mix plus independent complete contexts compared; all planned encoded pixels reviewed. Human whole listening/pronunciation and final public rights remain pending.'
save(BASE/'project.json',project)
checkpoint=read(BASE/'production/latest-checkpoint.json')
checkpoint.update(stage=project['status'],uploaded=True,actualId=receipt['actualVideoId'],private=True,fullSettingsVerified=True,nextAction='Selective own-source Git gate/normal push and actual remote blobs; then current Studio matching future09KST schedule and reopen.',recordedAt=now)
checkpoint['ownedJob']['status']='closed-completed-final-pixel-review-and-collection'
save(BASE/'production/latest-checkpoint.json',checkpoint)
queuePath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';queue=read(queuePath)
item=next(x for x in queue['items']if x['slug']=='character-parameters')
item.update(stage=project['status'],uploaded=True,videoId=receipt['actualVideoId'],fullSettingsVerified=True,privateSavedVerified=True,updatedAt=now,nextAction=checkpoint['nextAction'],measuredMotionCanvasCreated=True,
 publishingPreparation='projects/character-parameters/publishing/publishing-text-preparation-v2.json',selectedInputDirectReview='projects/character-parameters/production/selected-input-direct-review-v4.json')
item['checkpoints'].update(uploaded=True,privateSettings=True)
for key in ['currentExecution','currentJob','ownedJob']:
 if key in item:item[key]['status']='closed-completed-final-pixel-review-and-collection'
queue.update(lastProgressAt=now,updatedAt=now)
save(queuePath,queue)
registryPath=ROOT/'shared/git-essential-images.json';registry=read(registryPath)
for e in entries:
 old=next((x for x in registry['entries']if x['path']==e['path']),None)
 if old:assert old['sha256']==e['sha256']
 else:registry['entries'].append(e)
save(registryPath,registry)
ignore=ROOT/'.gitignore';text=ignore.read_text('utf-8-sig')
for e in entries:
 if '!'+e['path'] not in text.splitlines():text=text.rstrip()+'\n!'+e['path']+'\n'
ignore.write_text(text,'utf-8')
readme=BASE/'README.md';text=readme.read_text('utf-8-sig')
start=text.index('한영 실측13챕터');end=text.index('\n\n이번 CPU',start)
text=text[:start]+'실제 새 ID `nic5Sp6dylQ`는 검수된 captioned MP4 한 번 선택 뒤 비공개로 저장·재열람했다. SD·HD와 저작권·광고 검사가 문제없이 완료됐고 한영 수동201/95큐, 별도 영어 정보,13실측챕터, 썸네일,00초 코칭 카드와379.95–389.95초 회원 구간의 세 요소를 저장·재열람했다. 처리 후 실제60fps UI의6:19:57–6:29:57로 원래10초 구간에 정확히 맞췄다. 1080p60/CCoff 업로드5초 검정 입체와10초 실제게임에서 고정 자막·UI·원래 방송 크레딧을 직접 읽었다. `publishing/private-settings-direct-review-v1.json`과 실제 receipt를 따른다. 선택Git·실제 공개예약은 아직 미완료이며10/30 오전09시 Asia/Seoul은 목표일이다. 사람 전체청취·발음·최종 공개권리·자동더빙·optionalCC·게시후 댓글은 pending이다. 전달 썸네일1+최소 게시 증거3 PNG만 개별 검수/registry/정확ignore예외로 준비했고 QA·원본·미디어는 local-only다.'+text[end:]
readme.write_text(text,'utf-8')
print(json.dumps(dict(actualVideoId=receipt['actualVideoId'],private=True,fullSettingsVerified=True,automaticChecks=True,minimalImages=len(entries),gitDelivered=False,scheduled=False)))
