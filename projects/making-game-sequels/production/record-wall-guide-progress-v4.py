"""Adopt reviewed source reassignment metadata; production gates remain closed."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
PROJECT=BASE.parent; WORK=BASE/'measured-edit-v4'
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stamp=datetime.now(timezone.utc).isoformat()
plan=read(WORK/'plan.json'); pixels=read(WORK/'wall-guide-target-local-v4/execution.json')
compile_state=read(WORK/'native-review-v4/execution.json')
assert compile_state['exitCode']==pixels['exitCode']==0
assert compile_state['reusedCuts']==85 and compile_state['newEncodedCuts']==0
assert len(pixels['images'])==77 and len(pixels['sheets'])==13 and pixels['completedCuts']==6
assert pixels['planSha256']==sha(WORK/'plan.json')
for r in pixels['images']+pixels['sheets']:assert sha(ROOT/r['path'])==r['sha256']
pixel_review={'schemaVersion':1,'reviewedAt':stamp,'planSha256':sha(WORK/'plan.json'),
 'captionLayoutSha256':sha(WORK/'caption-layout-v4.json'),'images':[{**r,'directlyRead':True,'finalApproved':False} for r in pixels['images']],
 'boards':[{**r,'directlyRead':True} for r in pixels['sheets']],
 'all77ImagesAnd13BoardsDirectlyRead':True,'cutCount':6,'allRasterLocalOnly':True,'newGitImages':0,
 'observations':[
  {'boards':[1,6],'observation':'The complete02-g1 now plays on one continuous seven-second wall-side fight. The fixed-box onset at output frame approximately3843 is already on wall devices, then approaching orcs, aim/body direction changes and purple/blue direct attacks. Earlier bridge/step mismatch is resolved for these selected word/cue/native samples. The prior short wall fight remains a separate excerpt before this guide.'},
  {'boards':[7,13],'observation':'06p2 starts with direct close combat, then floor-device/effect observations, then the separate bridge fight while the narration distinguishes preparation from combat. The last effect cue extends across the first bridge frames; visible electric attack effects continue, but no attribution of every projectile to a floor device is made. Brief remaining normal-speed attack/followthrough is observation, not a claim that active pixels alone approve the final quota.'}],
 'changedWordSourceAlignmentTechnicallySupported':True,'captionCenter':[960,970],
 'style':'boxed-white-forest-v1','finalFullMotionApproved':False,'allFinalPixelsReviewed':False,
 'finalTimingApproved':False,'bodyRatioApproved':False}
save(BASE/'wall-guide-target-direct-review-v4.json',pixel_review)
# Current inspection contexts are byte-identical to the six already read contexts.
old_join=read(BASE/'guided-joins-direct-review-v3.json')
new_request=read(BASE/'guided-joins-readback-request-v4.json'); joins=[]
for c in new_request['contexts']:
    old=next(r for r in old_join['rows'] if r['id']==c['id'])
    audio,rate=sf.read(ROOT/c['audio'],dtype='int16'); expected,er=sf.read(ROOT/old['contextAudio'],dtype='int16')
    assert rate==er==24000 and np.array_equal(audio[c['fromSample']:c['toSample']],expected)
    assert c['expectedKo']==old['expectedKo'] and sha(ROOT/c['audio'])==c['audioSha256']
    joins.append({**c,'byteIdenticalReviewedContext':True,'priorDirectReview':'projects/making-game-sequels/production/guided-joins-direct-review-v3.json',
      'priorContextAudioSha256':old['contextSha256'],'priorResultSha256':old['resultSha256'],
      'technicalReview':True,'comparison':old['comparison'],'finalNimbusMixReview':False})
save(BASE/'guided-joins-byte-preservation-review-v4.json',{'schemaVersion':1,'reviewedAt':stamp,
 'contexts':joins,'allSixContextsSampleIdentical':True,'all60ScriptParagraphsPreserved':True,
 'currentInspectionIndexSha256':sha(WORK/'inspection-pcm-index-v4.json'),
 'candidateOnly':True,'recognizerOnsetArtifactPreserved':True,'newAsrWorkerNeededForTheseIdenticalContexts':False,
 'finalMixAsrApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending'})
# Derive current joins from authoritative placements, rather than inheriting the
# v3 two-frame offsets still present in its informational quietJoins rollup.
current_joins=[]
for s in plan['scenes']:
    voiced=[p for p in s['pcmPlacement'] if p['kind']!='inserted-silence']
    for a,z in zip(voiced,voiced[1:]):
        current_joins.append({'scene':s['id'],'afterParagraph':a['paragraph'],'beforeParagraph':z['paragraph'],
         'outputSamples':[a['outputToSample'],z['outputFromSample']],
         'insertedSilenceSamples':z['outputFromSample']-a['outputToSample'],
         'fromAudio':a['audio'],'fromSourceEndSample':a['toSample'],
         'toAudio':z['audio'],'toSourceStartSample':z['fromSample'],
         'newGuideJoin':bool(a.get('guideId') or z.get('guideId')),
         'finalMixJoinAsrApproved':False})
save(WORK/'current-quiet-joins-v4.json',{'schemaVersion':1,'reviewedAt':stamp,
 'planSha256':sha(WORK/'plan.json'),'authoritativeBasis':'Current pcmPlacement sample positions.',
 'joins':current_joins,'inheritedPlanQuietJoins':'Historical v3 informational offsets; this current derivation is authoritative.',
 'finalMixApproved':False})
for folder,session,pid in [('native-review-v4',7051,13152),('wall-guide-target-local-v4',41159,15532)]:
    state=read(WORK/folder/'execution.json'); record=read(WORK/folder/'session.json')
    record.update(sessionId=session,pid=pid,endedAt=state['endedAt'],exitCode=0,sessionClosed=True,doNotRepeatCompletedWorker=True)
    save(WORK/folder/'session.json',record)

bindings={'schemaVersion':1,'reviewedAt':stamp,'currentCandidate':'projects/making-game-sequels/production/measured-edit-v4/plan.json',
 'sourceReassignment':plan['sourceReassignment'],'directPixelReview':'projects/making-game-sequels/production/wall-guide-target-direct-review-v4.json',
 'quietJoins':'projects/making-game-sequels/production/measured-edit-v4/current-quiet-joins-v4.json',
 'all554_584SpeechSecondsPreserved':True,'nativeIntervalsUnique':True,'finalApproved':False}
save(PROJECT/'planning/guided-source-alignment-v4.json',bindings)
outline=PROJECT/'planning/outline.md'
outline.write_text(outline.read_text('utf-8-sig')+'\n## 현재 v4 벽 장치 안내 정렬 — '+stamp+'\n\n'
 '02의 벽 장치 안내가 다리 화면에서 시작하던 약3.3초 불일치를 고쳤습니다. 기존633–640초의 연속 벽 옆 전투를02안내에 옮기고,595.5–602.5333초의 별도 다리 전투는06의 일반 전투·준비 구분 문장 뒤로 옮겼습니다. 원래13장52문단과 새8문단, 모든554.584초 PCM을 그대로 보존합니다. 고유 인아웃은 중복 없이 유지했고85기존 컴파일을 byte동일로 재사용했습니다. 두 프레임은02말미 무음에서06문단 앞 무음으로만 옮겼습니다.\n\n'
 '현재308KO/173EN·60문단과 v4 표적77화면/13판을 직접 읽었습니다. 현재6접합은 이미 직접 읽은 ASR 문맥과 모든 PCM샘플이 동일함을 대조해 기술 근거를 재사용하며 새 ASR을 반복하지 않습니다. 넓은13문맥의 자/같은 zero-duration 및 조사·숫자 ASR차이는 유지합니다. 사람청취·발음, 최종Nimbus믹스/전체13장ASR·접합, 흰도식과 모든 최종자막 모션·정수비율·렌더·QA·4파일수집·새비공개는 아직 미완료입니다. 다음은 실제 timing의 흰 도식·literal자막 픽셀과 남은2프레임 overhead 경계 검토입니다.\n',encoding='utf-8')
chapter=read(PROJECT/'planning/chapter-plan.json')
for c in chapter['chapters']:
    s=next(x for x in plan['scenes'] if x['id']==c['id'])
    c.update(candidateStartFrame=s['startFrame'],candidateEndExclusive=s['endFrameExclusive'],
       sourceActionIds=sorted(set(x['bankCutId'] for x in s['segments'] if x['classification']=='actual-existing-game')),
       candidatePlan=bindings['currentCandidate'],finalTimingApproved=False)
chapter.update(updatedAt=stamp,guidedSourceAlignment='projects/making-game-sequels/planning/guided-source-alignment-v4.json')
save(PROJECT/'planning/chapter-plan.json',chapter)
action=read(PROJECT/'sources/action-map.json');action.update(updatedAt=stamp,
    currentMeasuredCandidate=bindings['currentCandidate'],guidedSourceAlignment=bindings,
    status='Current13/60 component voice and six byte-identical candidate joins technically reviewed; wall guide target corrected. Final white/caption motion and Nimbus mix pending.')
save(PROJECT/'sources/action-map.json',action)
manifest=read(PROJECT/'project.json');manifest['paths']['timeline']=bindings['currentCandidate']
manifest['status']='current13-guided60-wall-source-aligned-final-white-cues-and-mix-pending'
edit=manifest['editing'];edit.setdefault('historicalMeasuredCandidateV3',copy.deepcopy(edit['measuredCandidate']))
edit.update(timingStatus='guided60-v4-candidate-final-white-pixels-and-mix-pending',measuredSpeechSeconds=554.584)
edit['measuredCandidate'].update(candidatePlan=bindings['currentCandidate'],nativeCompile='projects/making-game-sequels/production/measured-edit-v4/native-review-v4/compiled.json',
    captionTracks='projects/making-game-sequels/production/measured-edit-v4/caption-tracks-v4.json',
    captionLayout='projects/making-game-sequels/production/measured-edit-v4/caption-layout-v4.json',
    candidateJoinTechnicalReview='projects/making-game-sequels/production/guided-joins-byte-preservation-review-v4.json',
    changedWallGuidePixelReview=bindings['directPixelReview'],allFinalPixelsReviewed=False,newJoinAsrApproved=False)
save(PROJECT/'project.json',manifest)
# Refresh measured independent scene metadata while retaining diagrams and all gates.
mcpath=ROOT/'motion-canvas/src/projects/making-game-sequels/scene-plan.json';mc=read(mcpath)
for s in mc['scenes']:
    measured=next(x for x in plan['scenes'] if x['id']==s['id'])
    s['durationFrames']=measured['frames']
    s['segments']=[{'role':c['classification'],'frames':c['frames'],'segmentId':c['id'],
        'diagramId':c.get('diagramId'),'mediaPixelsReviewed':False,'diagramPixelsReviewed':False,
        'sourceAudioStreams':0} for c in measured['segments']]
mc.update(finalTimingApproved=False,allFinalCaptionPixelsReviewed=False,allSourceSegmentPixelsReviewed=False,
    measuredCandidate=bindings['currentCandidate'])
save(mcpath,mc)
sr=read(BASE/'script-source-review.json');sr.update(reviewedAt=stamp,
    status='current13-guided60-source-and-component-voice-reviewed-wall-guide-target-corrected-final-white-mix-pending',
    candidateJoinReview='projects/making-game-sequels/production/guided-joins-byte-preservation-review-v4.json',
    guidedSourceAlignment='projects/making-game-sequels/planning/guided-source-alignment-v4.json')
next(s for s in sr['scenes'] if s['id']=='02')['paragraphs'][4]['sourceActionIds']=[17]
for x in sr['inputs']:
    if x['path'].endswith('measured-edit-v3/plan.json'):x['path']=bindings['currentCandidate']
    x['sha256']=sha(ROOT/x['path'])
save(BASE/'script-source-review.json',sr)

queuepath=PROOF.parent/'queue.json';queue=read(queuepath);item=next(i for i in queue['items'] if i['slug']=='making-game-sequels')
stage=manifest['status'];next_action='Review literal fixed captions on seven measured white diagram segments and the2-frame overhead boundary; then finalize integer timing and update mix/scenes/KOEN/chapter/outro together. Final Nimbus13 whole/context ASR, full composite pixels, two decode/loudness/identical AAC, collection/private/Git remain required.'
item.update(stage=stage,updatedAt=stamp,nextAction=next_action)
item['execution'].update(status='all-guidance-and-wall-target-workers-closed',phase=stage,observedAt=stamp,
    pid=None,sessionId=None,commandLine=None,alive=False,activeTasks=[],cpuProductionJobs=0,
    primaryCpuProductionJobs=0,gpuSynthesisJobs=0,renderJobs=0,uploads=0)
item['guidedObservation'].update(currentIndex='projects/making-game-sequels/production/narration-guided60-index-v3.json',
    currentCandidate=bindings['currentCandidate'],candidateJoinReview='projects/making-game-sequels/production/guided-joins-byte-preservation-review-v4.json',
    sourcePixelTrialReview='projects/making-game-sequels/production/guided-native-caption-direct-review-v3.json',
    wallGuideTargetReview=bindings['directPixelReview'],newGuides=8,allCurrentComponentSeconds=554.584,
    technicalReviewComplete=True,finalMixBuilt=False)
item['measuredEditCandidate'].update(path=bindings['currentCandidate'],actualFrames=20918,
    explanationFrames=13945,finalFrames=35583,ratioErrorFrames=.2,paragraphs=60,
    nativeCuts=85,koCues=308,enCues=173,finalTimingApproved=False,bodyRatioApproved=False,
    allFinalPixelsReviewed=False)
item.setdefault('historicalCurrent13BeforeGuidance',copy.deepcopy(item.get('currentNarrationReview')))
item['currentNarrationReview']={'index':'projects/making-game-sequels/production/narration-guided60-index-v3.json',
 'componentSeconds':554.584,'paragraphs':60,'scenes':13,'base52Preserved':True,
 'allComponentsTechnicallyReviewed':True,'candidateSixJoinsSampleIdentical':True,'finalMixAsrApproved':False,
 'humanWholeListening':'pending','humanPronunciation':'pending'}
queue.update(updatedAt=stamp,lastProgressAt=stamp);save(queuepath,queue)
for path in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    cp=read(path)
    cp.setdefault('historicalCurrent13BeforeGuidance',{'paragraphs':cp.get('paragraphs'),
        'narrationMeasurement':cp.get('narrationMeasurement'),'currentMeasuredSpeechSeconds':cp.get('currentMeasuredSpeechSeconds')})
    for k in ['stage','updatedAt','execution','guidedObservation','measuredEditCandidate','nextAction']:cp[k]=item[k]
    cp.update(scenes=13,paragraphs=60,currentMeasuredSpeechSeconds=554.584,
      currentVoiceIndex='projects/making-game-sequels/production/narration-guided60-index-v3.json',
      narrationApprovalScope='Current component voice and byte-identical unmixed six contexts only; final Nimbus mix and human whole listening/pronunciation pending.',
      narrationMeasurement=item['currentNarrationReview'],allCaptionPixelsReviewed=False,
      finalTimingApproved=False,bodyRatioApproved=False,finalMixBuilt=False,rendered=False,
      qaApproved=False,collected=False,privateUploaded=False,newGitImages=0,
      actualCuePixelTrials={'guidedV3Images':528,'guidedV3Boards':88,'wallV4Images':77,'wallV4Boards':13,
       'allTheseTrialsDirectlyRead':True,'finalFullCompositeApproved':False})
    save(path,cp)
print(json.dumps({'paragraphs':60,'componentVoiceSeconds':554.584,'wallGuideTargetCorrected':True,
 'sixReviewedContextsSampleIdentical':True,'nativeEncodeReused':85,'newNativeEncodes':0,'workers':0,'finalComplete':False}))
