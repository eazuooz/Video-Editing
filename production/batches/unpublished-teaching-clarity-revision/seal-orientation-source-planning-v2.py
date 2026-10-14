"""Seal inspected source planning and paired bridges; no final-pixel approval."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
B=ROOT/'production/batches/unpublished-teaching-clarity-revision'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
stamp=datetime.now(timezone.utc).isoformat()
base=read(R/'baseline-preservation-v1.json')
assert all(sha(ROOT/x['path'])==x['sha256'] for x in base['protectedFiles'])
old=read(R/'conservative-source-recut-proposal-v1.json')
assert sha(ROOT/old['source'])==old['sourceSha256']
plan=copy.deepcopy(old)
normal=read(R/'conservative-source-normal-playback-v2.json')
first=read(R/'first-recut-normal-playback-v1.json')
assert first['normalSpeedMutedPlayback'] and first['status']['paused']
assert first['status']['rate']==1 and first['status']['muted']
focus={
    '02':'몸통 관찰점의 화면 이동과 몸의 가시적 기울기를 따로 관찰',
    '05':'몸 기울기·건물 모서리·화면 기준을 구분; 이후 별도3D모델로 세 기준을 설명',
    '08':'몸에 붙인 관찰선과 화면 기준 비교; 고정 월드축은 영상에서 측정하지 않음',
    '11':'카메라 변화 속 몸과 배경의 가시적 관계; 내부 자세 수치 추정0',
    '14':'가시적 원근 크기와 몸 형태를 구분; 서로 다른 비행은 별도 예시',
    '17':'가시적 부드러운 움직임 관찰 뒤 별도 수학모델에서 축 길이 검사',
    '20':'화면 기준 좌우와 몸 기울기 비교; 월드축은 뒤의 개념모델로 설명',
    '23':'몸통 관찰점·가시적 기울기·카메라 영향 복습; 엔진 forward/up/roll 측정 아님'}
for w in plan['windows']:
    if w['scene']=='14' and w['segment']==2:
        w.update(firstNativeFrame=7320,endExclusiveNativeFrame=7800,sourcePtsIn=7320*256,sourcePtsOutExclusive=7800*256)
    if w['scene']=='02':
        evidence=dict(path=rel(R/'first-recut-normal-playback-v1.json'),actualEnd=first['status']['currentTime'])
    else:
        matches=[x for x in normal['records'] if str(x['scene']).zfill(2)==w['scene'] and x['segment']==w['segment']
                 and abs(x['plannedIn']-w['firstNativeFrame']/60)<1e-6 and abs(x['plannedOut']-w['endExclusiveNativeFrame']/60)<1e-6]
        assert len(matches)==1,(w['scene'],w['segment'])
        x=matches[0]
        assert x['observed']['paused'] and x['observed']['rate']==1 and x['observed']['muted'] and x['endpointPixelsDirectlyRead']
        play=[e for e in normal['events'] if e['event']=='play' and abs(e['t']-x['plannedIn'])<.01]
        assert play
        evidence=dict(path=rel(R/'conservative-source-normal-playback-v2.json'),actualStartSample=x.get('actualStart'),
                      actualPlayEvent=play[-1],actualEnd=x['observed']['currentTime'])
    w.update(focus=focus[w['scene']],normalPlaybackCompared=True,sourceAdopted=True,
             sourceAdoptionScope='Normal-speed native-boundary editorial selection only; guides hidden at occlusion/weak contrast, final encoded cue/UI review pending.',
             normalPlaybackEvidence=evidence,engineAxesMeasured=False)
assert sum(x['frames'] for x in plan['windows'])==21370
ordered=sorted(plan['windows'],key=lambda x:x['firstNativeFrame'])
assert all(a['endExclusiveNativeFrame']<=b['firstNativeFrame'] for a,b in zip(ordered,ordered[1:]))
assert len(plan['windows'])==16
plan.update(preparedAt=stamp,status='source-planning-selected-final-tracking-and-cues-pending',sourceAdoptionApproved=True,
    correction='Scene14 third window122–130 replaces123–131, avoiding the observed131s portal/map change; duration and unique total unchanged.',
    allNormalPlaybackWindowsExecuted=True,allIntermediatePixelsRead=False,newTtsStarted=False)
proposal=R/'conservative-source-recut-proposal-v2.json'
target=R/'source-selection-preflight-v2.json'
reviewTarget=R/'paired-additive-script-direct-review-v2.json'
assert not any(p.exists() for p in [proposal,target,reviewTarget])
proof=dict(schemaVersion=2,reviewedAt=stamp,sourceSelectionPreflightApproved=True,maximumUniqueFrames=21370,
    all16NormalPlaybackWindowsExecuted=True,source=plan['source'],sourceSha256=plan['sourceSha256'],nativeTimebase='1/15360',nativePtsStep=256,
    recutProposal=rel(proposal),normalPlaybackProof=rel(R/'conservative-source-normal-playback-v2.json'),
    firstWindowProof=rel(R/'first-recut-normal-playback-v1.json'),
    nativeReviews=[rel(R/'selected-native-direct-review-v1.json'),rel(R/'repair-candidate-direct-review-v1.json')],
    comparedAlternative=rel(R/'normal-playback-comparison-observation-v2.json'),
    readabilityDecision='NCR gray/white first flight has a clearer articulated torso/arms than the alternate pale/pink/yellow sequence. Crash/menu intervals were replaced by distinct flight. Weak/occluded body regions remain masked, not assigned an invented pose.',
    rights=dict(recordingPermission='Existing observed uploader free-use-for-videos permission; not a named CC license.',
                records=['projects/game-math-orientation-matrices/sources/SOURCES.md','projects/game-math-orientation-matrices/sources/game-candidates.json'],
                preserveRecorderCredit=True,sourceAudio=False,publicGameIpReviewApproved=False),
    sourceReuseDecision='Revision of the same lesson and approved source;16windows are internally disjoint. Existing series use is acknowledged, not labeled a new unused title.',
    maskedRegions=['scene02 source827–829/848–853','scene05 source155–156/172–173/190/198–200',
        'scene08 source259/263–265/299','scene11 source377–379/393–395','scene14 source137–143 partially occluded',
        'scene17 source623–624/640–641/645–648','scene20 source670/681–686','scene23 source879–883 mixed contrast'],
    annotationContract='Teal marked torso observation point; red observed screen displacement; gold image-up reference. No measured engine/world axes or physical center of mass. Hide uncertain guides; narrated projected models explain the world/body mathematics separately.',
    preservedBaselineFiles=38,entireFinalPixelsApproved=False,allIntermediatePixelsDirectlyRead=False,
    continuousAudioReview=False,finalCueUiAndCreditApproved=False,bodyRatioMeasured=False,additionalBridgeActualMeasured=False,
    currentPcmAsrApproved=False,newActualId=None,publicRightsApproved=False)
review=copy.deepcopy(read(R/'paired-additive-script-direct-review-v1.json'))
review.update(schemaVersion=2,reviewedAt=stamp,contentReadyForApprovedVoiceMeasurement=True,sourcePlanningApproval=True,
    sourcePlanningProof=rel(target),all22KoEnParagraphsWholeTextsDirectlyRead=True,
    scope='Paired additive wording and native source planning approved for single voice measurement. No current voice/ASR/final-animation approval.')
write(proposal,plan);write(target,proof);write(reviewTarget,review)
request=read(R/'narration-tts-request-v1.json');request.update(scriptReview=rel(reviewTarget),sourcePlanningApproved=True)
write(R/'narration-tts-request-v1.json',request)
cp=read(R/'latest-checkpoint.json');cp.update(observedAt=stamp,stage='six-bridges-source-planning-approved-single-voice-measurement-pending',
    sourcePlanning=rel(target),pairedScriptReview=rel(reviewTarget),newActualId=None,
    next='Single cooperative voice request after fresh resources; preserve foreign lease and verify own original-research restoration after actual outer exit.')
write(R/'latest-checkpoint.json',cp)
assert all(sha(ROOT/x['path'])==x['sha256'] for x in base['protectedFiles'])
print(json.dumps(dict(sourcePlanningApproved=True,normalWindows=16,uniqueFrames=21370,pairedNewParagraphs=22,baselineUnchanged=38,finalApproved=False)))
