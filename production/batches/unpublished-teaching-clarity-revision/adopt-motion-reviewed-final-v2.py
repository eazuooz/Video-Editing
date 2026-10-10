"""Adopt reviewed local motion revision; preserve historical delivery records.

Prepared until current whole/context audio, final pixels and normal1x playback
are directly approved. This cannot upload or alter the baseline schedule.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/motion-sickness-games'
R=P/'production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
pair=read(R/'final-pair-execution-v2.json');session=read(R/'final-pair-execution-v2.session.json')
assert pair['exitCode']==0 and session['actualOuterExitCode']==0 and not session['workerCurrentlyAlive']
pixels=read(R/'final-pixel-direct-review-v2.json')
flow=read(R/'final-flow-playback-direct-review-v2.json')
audio=read(R/'current-mixed-complete-direct-review-v1.json')
assert pixels['allListedPixelsDirectlyReviewedCurrentOrByteIdenticalPrior'] and pixels['allFinalCueCutPixelsApproved'] and not pixels['unresolved']
assert flow['wholeNormalSpeedPlaybackReachedEnd'] and flow['sampledContinuousFlowApproved'] and not flow['unresolved']
assert pixels['sourceSha256']==flow['sourceSha256']==pair['pair'][1]['sha256']
assert audio['currentMixedContentReviewPassed'] and audio['all14WholeAnd66IndependentContextsDirectlyCompared']
assert pair['all26ProtectedInputsUnchanged']
mix=read(R/'current-mix-execution-v1.json');plan=read(R/'measured-additive-plan-v1.json')
assert audio['mixAacSha256']==mix['mixAacSha256'] and sha(ROOT/mix['mixAac'])==mix['mixAacSha256']
for v in pair['pair']:assert sha(ROOT/v['path'])==v['sha256'] and v['allPts1500Verified'] and v['wholeDecodeExitCode']==0 and v['identicalReviewedWholeAacPackets']
assert pair['frames']==plan['totalFrames']==40193 and abs(plan['ratioErrorFrames'])<=1
assert sha(R/'captions.ko.ass')==read(R/'caption-layout-v1.json')['assSha256']
alignment=read(R/'caption-alignment-v1.json');assert len(alignment['entries'])==179 and alignment['originalCueTextsAndWrapsPreserved']
protected=read(R/'narration-tts-waiting-v1.json')['protectedInputs']
for v in protected:assert sha(ROOT/v['path'])==v['sha256'],v['path']
receipt=R/'final-media-adoption-v2.json';history=R/'baseline-records-before-adoption-v2'
assert not receipt.exists() and not history.exists();history.mkdir()
saved=[]
for name in ['project.json','production/timeline.json','production/qa.json','production/delivery-output.json','rebuild.json','planning/outline.md']:
 src=P/name
 if not src.exists():continue
 dst=history/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 assert sha(dst)==sha(src);saved.append(dict(original=rel(src),preserved=rel(dst),sha256=sha(src)))
manifest=read(P/'project.json')
priorPublishing=manifest['publishing']
assert priorPublishing['videoId']=='c18rkesgBSw'
manifest.setdefault('publishingHistory',[]).append(dict(reason='Preserve completed visual-depth baseline before the user-authorized unpublished teaching revision; its actual schedule is unchanged.',publishing=priorPublishing))
manifest.update(status='teaching-clarity-current-local-reviewed; collection-private-Git-schedule-pending',publishReady=False)
manifest['video']['durationSeconds']=plan['seconds']
manifest['paths'].update(script=rel(R/'script/narration.ko.json'),scriptEn=rel(R/'script/narration.en.json'),
 audioMix=mix['mixAac'],editorAudioMix=mix['mixWav'],audioReport=rel(R/'current-mix-execution-v1.json'),
 captionsKo=rel(R/'captions.ko.srt'),captionsEn=rel(R/'captions.en.srt'),
 videoClean=pair['pair'][0]['path'],videoBurnedCaptions=pair['pair'][1]['path'],renderReport=rel(P/'production/qa.json'),
 currentAssemblyBuilder='production/batches/unpublished-teaching-clarity-revision/assemble-motion-current-pair-v2.py',
 currentMeasuredScenePlan=rel(R/'measured-additive-plan-v1.json'),currentTeachingRevision=rel(receipt))
e=manifest['editing']
e.update(actualGameplaySeconds=plan['actualFrames']/60,actualExplanationSeconds=plan['explanationFrames']/60,
 actualCommercialGameplaySeconds=plan['actualFrames']/60,actualDevelopmentFootageSeconds=0,actualPrototypeExplanationSeconds=0,
 actualGameplayShare=plan['actualFrames']/plan['bodyFrames'],plannedGameplaySeconds=plan['actualFrames']/60,
 plannedExplanationSeconds=plan['explanationFrames']/60,scenePlan=rel(R/'measured-additive-plan-v1.json'),
 timingStatus='current14 measured audio, captions, chapters and original member ending retimed together; final pair directly reviewed')
e['finalBodyFrames']=dict(total=plan['bodyFrames'],actual=plan['actualFrames'],explanation=plan['explanationFrames'],ratioErrorFrames=plan['ratioErrorFrames'])
e['openingOverview']=dict(required=True,scene='00a',seconds=1507/60,narrationSeconds=22.4,
 question='게임의 목표를 따라가면서도 화면은 덜 돌릴 수 있을까요?',
 orderedExamples=['청소 게임의 조준과 시점','방향 변경 뒤 퍼즐 목표의 단서','카메라 설정과 되돌리기 설계'],
 reviewedBeforeTts=rel(R/'paired-script-direct-review-v1.json'),currentFinalFlow=rel(R/'final-flow-playback-direct-review-v2.json'),
 classification='selected projected explanation and unique normal-speed action classified separately')
e['teachingClarityRevision']=dict(version='teaching-clarity-v1',baselineVideoId='c18rkesgBSw',baselineRecords=rel(history),
 baselineOrderAndUsefulExplanationsRetained=True,original12PcmByteIdentical=True,newPcmCount=2,
 sceneCount=14,paragraphCount=66,retainedCaptionCount=166,newCaptionCount=13,sourceSelection=rel(R/'sources/source-action-bank-v1.json'),
 scriptAndPrimaryReferenceReview=rel(R/'paired-script-direct-review-v1.json'),
 retainedAnnotations=rel(R/'retained-encoded-sample-direct-review-v1.json'),newOpening=rel(R/'opening-overlay-pilot-sampled-direct-review-v3.json'),
 additiveExplanation=rel(R/'additive-mc-direct-review-v3.json'),finalPixels=rel(R/'final-pixel-direct-review-v2.json'),visualRepairs=rel(R/'two-target-repair-direct-review-v3.json'),
 finalFlow=rel(R/'final-flow-playback-direct-review-v2.json'),currentMixedAudio=rel(R/'current-mixed-complete-direct-review-v1.json'),
 onFootageSemanticLinesAndLabels=True,gameWorldValuesMeasured=False,
 claimScope='Visible projected relations only; distinct source excerpts and a proposed interface are labelled; no promised individual comfort result.')
manifest['audio']['mixStatus']='current14 decoded AAC whole14 and independent66 directly compared; human whole hearing and pronunciation pending'
manifest['publishing']={**priorPublishing,'baselineVideoId':'c18rkesgBSw','baselinePreserved':True,
 'status':'reviewed-local-replacement-prepared; platform-settings-pending','videoId':None,'actualVideoId':None,'videoUrl':None,
 'privacyStatus':'private','scheduled':False,'scheduledPublishAt':None,'uploaded':False,'fullSettingsVerified':False,
 'ccOffPixelVerification':'pending-new-actual-upload','receipt':rel(R/'publishing/youtube-upload-v1.json'),'baselineScheduleChanged':False}
manifest['approvals'].update(script='Original60 KOEN paragraphs retained with independent4-paragraph overview and2-paragraph bridge; source/action/causal audit directly reviewed.',
 final='Current mixed80 contexts and all listed final cue/cut/annotation pixels directly reviewed; human hearing, pronunciation and public rights pending.',
 publication='Reviewed private replacement and daily alternating09KST schedule authorized; actual settings/Git/schedule verification pending.')
manifest['finalRender'].update(revision='teaching-clarity-v1',durationSeconds=plan['seconds'],frames=plan['totalFrames'],
 status='reviewed-current-local-pair',qa=rel(P/'production/qa.json'),videoClean=pair['pair'][0]['path'],
 videoBurnedCaptions=pair['pair'][1]['path'],pixelReview=rel(R/'final-pixel-direct-review-v2.json'),
 technicalQa=rel(R/'final-pair-execution-v2.json'),allFinalPixelsReviewed=True)
save(P/'project.json',manifest)
outline=P/'planning/outline.md'
retainedOutline=outline.read_text('utf-8-sig')
assert '## 공개 전 이해도 수정본' not in retainedOutline
addition=read(R/'script/additions.ko.json')
overview=next(s for s in addition['scenes'] if s['id']=='00a')['lines']
outline.write_text(retainedOutline.rstrip()+'\n\n## 공개 전 이해도 수정본 — teaching-clarity-v1\n\n'
 '기존 12씬의 모든 설명·순서·승인 PCM은 보존했다. 아래 개론과 연결 문단은 음성 제작 전에 `production/revision-teaching-clarity-v1/paired-script-direct-review-v1.json`에서 독립 KO/EN으로 검토했으며, 이 기획 문서는 검수된 수정본을 채택하는 시점에 해당 기록을 합쳐 보존한다.\n\n'
 '고양이 2초 다음 개론: '+ ' '.join(overview)+'\n\n'
 '개론 음성은 실측 22.4초, 도입 씬은 고유 정상속도 행동과 입체 설명을 합해 25.116667초다. 빨간 표시를 보기 전에 물줄기로 때를 지우는 목표를 말한다. 파란 기둥과 노란 바닥 표시는 물줄기와 배경의 움직임을 따로 읽는 데 쓰며, 실측 게임 세계 좌표·각도나 개인의 멀미 개선 효과를 주장하지 않는다.\n\n'
 '청소 목표와 조준/시점 관찰 → 보이는 움직임과 개인 반응 구분 → 필요한 조작과 부가 연출 분리 → 위치·표면을 바꿀 때 필요한 방향 전환 → 이해 가능하고 되돌릴 수 있는 옵션 → 방향을 바꾼 뒤 목표를 다시 찾는 단서 → 퍼즐의 서로 다른 발췌와 도착 방향 비교 → 목표 가독성과 옵션의 저장/복구 → 다른 방향에서 같은 작업을 다시 읽고 역할·선택·피드백으로 결론을 맺는다. 06과 07 사이 새 06b는 조준을 나눠도 목표를 다시 알아봐야 한다는 질문으로 게임 변경의 이유를 설명한다.\n\n'
 '참고 OS4CZkBBbW4의 개인차 → 관찰 가능한 화면 움직임/고정 기준 → 개발자 선택 → 옵션/피드백 흐름과 대조했다. 우리의 도입은 과제부터 보여 주며 약물·임상 조언은 포함하지 않는다. 처음 보는 사람에게 청소의 전후 변화가 더 명료하여 PowerWash를 먼저 사용했고, Talos의 짧은 서로 다른 장면은 연속 퍼즐 성공이나 통제된 비교로 제시하지 않는다. 선택/제외·정확 native PTS·권리 범위는 현재 source-action-bank와 직접검수 기록을 따른다.\n\n'
 '원래 실제 게임60:설명40 분류를 유지하며 본편 '+str(plan['bodyFrames'])+'프레임 중 실제 '+str(plan['actualFrames'])+' / 설명 '+str(plan['explanationFrames'])+'프레임, 반올림 오차 '+str(plan['ratioErrorFrames'])+'프레임이다. 고양이120/회원600프레임은 제외한다. 최종179 KO/EN큐, 표시·컷·입체 설명 픽셀과 정상1배속 선택 흐름은 현재 final-pixel/direct-flow 기록으로 확인했다. 사람 전체청취·발음·공개권리는 별도 pending이며 채택은 플랫폼 게시/예약 완료가 아니다.\n','utf-8')
qa=dict(reviewedAt=now,frames=plan['totalFrames'],seconds=plan['seconds'],videos=pair['pair'],
 twoWholeDecodeExitZero=True,allPts1500Verified=True,identicalReviewedWholeAacPackets=True,
 bodyFrames=plan['bodyFrames'],actualFrames=plan['actualFrames'],explanationFrames=plan['explanationFrames'],ratioErrorFrames=plan['ratioErrorFrames'],
 originalIntroFrames=120,originalMembershipFrames=600,captionCount=179,captionCounts={'ko':179,'en':179},
 allListedFinalPixelsDirectlyReviewedCurrentOrByteIdenticalPrior=True,pixelEvidence=rel(R/'final-pixel-direct-review-v2.json'),
 flowEvidence=rel(R/'final-flow-playback-direct-review-v2.json'),mixedAudioEvidence=rel(R/'current-mixed-complete-direct-review-v1.json'),
 currentMixMeasurements=dict(wavLufs=-16.05,wavDbtp=-2.31,decodedAacLufs=-16.10,decodedAacDbtp=-2.05),
 original12PcmPreserved=True,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 actualNewVideoId=None,privateSettingsVerified=False,gitDelivered=False,scheduled=False)
save(P/'production/qa.json',qa)
intended={rel(P/'project.json'),rel(P/'production/qa.json'),rel(P/'planning/outline.md')}
assert all(sha(ROOT/v['path'])==v['sha256'] for v in protected if v['path'] not in intended)
save(receipt,dict(adoptedAt=now,status='reviewed-local-media-adopted; collection-platform-Git-schedule-pending',
 baselineRecords=saved,intentionallyChangedProtectedRecords=sorted(intended),allOtherProtectedInputsUnchanged=True,
 currentClean=pair['pair'][0],currentCaptioned=pair['pair'][1],baselineScheduleChanged=False,
 uploaded=False,actualId=None,gitDelivered=False,scheduled=False,humanListeningApproved=False,publicRightsApproved=False))
print(json.dumps(dict(reviewedLocalMediaAdopted=True,frames=40193,oldPcmPreserved=True,collectionPending=True,actualId=None)))
