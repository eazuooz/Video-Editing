"""Promote reviewed current34;retain exact baseline and78 other protected inputs."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(p,v):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
stamp=datetime.now(timezone.utc).isoformat()
record=O/'current34-main-promotion-v1.json';assert not record.exists()
main=ROOT/'projects/game-math-orientation-matrices/project.json'
before=main.read_bytes();before_sha=hashlib.sha256(before).hexdigest()
assert before_sha=='0f6146cd968e9d7a471124abcedea8a5ee0490cd9616f2a4b6d92368ad3a5d03'
qa_path=O/'current34-final-technical-and-pixel-direct-review-v5.json';qa=rd(qa_path)
assert qa['technicalQaPassed'] and qa['finalRatioApproved'] and qa['all244CueFirstMidLastPixelsReviewed']
assert qa['normal1xMutedActualStartEndObserved'] and qa['all3170SelectedFinalSamplesReviewed']
pair=rd(ROOT/qa['pairExecution']);assert sha(ROOT/qa['pairExecution'])==qa['pairExecutionSha256']
assert pair['workerDead'] and pair['actualOuterExitCode']==0
mix=rd(O/'current34-mix-execution-v2.json')
source_proof=rd(O/'narration-07b-guide-repair-execution-v1.json')
for x in source_proof['protectedInputs']+source_proof['results']:assert sha(ROOT/x['path'])==x['sha256']
others=[x for x in source_proof['protectedInputs'] if (ROOT/x['path']).resolve()!=main.resolve()]
assert len(others)==78
backup=O/'baseline-main-before-current34-promotion-v1.json';assert not backup.exists()
backup.write_bytes(before);assert sha(backup)==before_sha
v=json.loads(before.decode('utf-8-sig'));e=v['editing'];b=qa['bodyMeasured'];prefix=rel(O)+'/'
e.update(actualGameplaySeconds=b['actualFrames']/60,actualExplanationSeconds=b['explanationFrames']/60,
    actualGameplayShare=b['actualFrames']/b['bodyFrames'],actualCommercialGameplaySeconds=b['actualFrames']/60,
    finalBodyFrames=dict(total=b['bodyFrames'],actual=b['actualFrames'],explanation=b['explanationFrames'],ratioErrorFrames=b['ratioErrorFrames']),
    timingStatus='current34 finalV5:34 approved voices,76 measured placements,244 KOEN cues,34 chapters and original600-frame ending preserved together',
    scenePlan=prefix+'current34-measured-timing-plan-v1.json')
e['exampleInterleaving']['reviewStatus']='Four distinct game examples linked through narration and detailed subjects;current3170 selected final pixels and actual normal1x muted endpoints reviewed. Human listening/pronunciation pending.'
e['openingOverview']['currentFinalFlow']=prefix+'current34-final-normal-direct-review-v5.json'
e['crossGameRevision']=dict(version='teaching-clarity-current34-v5',baselineVideoId='6-kP65hrZcI',
    original24PcmPreserved=True,originalWordingOrderPreserved=True,voiceCount=34,paragraphCount=180,
    retainedCaptionCount=200,newCaptionCount=44,distinctGames=['Superflight','Descenders','Trailmakers','Space Engineers'],
    detailedSubjectPolicy='shared/publishing/illustrative-subject-detail-policy.json',
    finalPixels=rel(qa_path),currentMixedContentReview=prefix+'current34-mixed-complete-direct-review-v1.json',
    claimScope='Visible gameplay states and projected illustrative geometry;no measured game-world axes,positions or engine internals.')
v['video']['durationSeconds']=pair['seconds']
v['audio']['mixStatus']='current34 narration-only PCM placement and whole34/independent180 AAC content review passed;human listening/pronunciation pending'
p=v['paths'];p.update(script=prefix+'script/current34-combined-v1.ko.json',scriptEn=prefix+'script/current34-combined-v1.en.json',
    audioReport=prefix+'current34-mix-execution-v2.json',audioMix=mix['mixAac'],editorAudioMix=mix['mixWav'],narration=mix['mixWav'],
    captionsKo=prefix+'current34.captions.ko.srt',captionsEn=prefix+'current34.captions.en.srt',captionsAss=prefix+'current34.captions.ko.ass',
    videoClean=pair['pair'][0]['path'],videoBurnedCaptions=pair['pair'][1]['path'],renderReport=rel(qa_path),
    timeline=prefix+'current34-measured-timing-plan-v1.json',currentMeasuredScenePlan=prefix+'current34-measured-timing-plan-v1.json',
    currentAssemblyBuilder='production/batches/cross-game-example-coverage-review/assemble-orientation-current34-pair-v5.py',
    currentAssemblyInputs=prefix+'current34-assembly-inputs-v5.json',currentTeachingRevision=rel(record),
    publishingKo=prefix+'publishing/upload-description.ko.txt',publishingEn=prefix+'publishing/upload-description.en.txt')
for k in ['script','scriptEn','audioMix','editorAudioMix','captionsKo','captionsEn','captionsAss','videoClean','videoBurnedCaptions','renderReport','timeline']:
    assert (ROOT/p[k]).is_file()
old=copy.deepcopy(v['publishing'])
v.setdefault('publishingHistory',[]).append(dict(reason='Preserve baseline completed upload and original main;actual Studio116 reads Oct13 09:00 GMT+0900 scheduled. No platform change during local promotion.',publishing=old))
v['publishing'].update(videoId=None,actualVideoId=None,videoUrl=None,privateUploadComplete=False,fullSettingsComplete=False,
    fullSettingsVerified=False,uploaded=False,scheduled=False,privacyStatus='private',scheduledPublishAt=None,
    baselineVideoId='6-kP65hrZcI',baselinePreserved=True,baselineScheduleChanged=False,
    receipt=prefix+'publishing/youtube-upload-v1.json',status='current34-reviewed-local-awaiting-single-private-upload',
    productionGitEvidence=None,scheduleEvidence=None)
v['status']='current34-detailed-four-game-local-reviewed;delivery-publishing-Git-schedule-pending'
v['publishReady']=False
v['approvals'].update(visualPixelReview='current34 finalV5 all3170 planned samples reviewed;bounded scope,not every intermediate frame',
    final='Current whole34 and180 independent AAC content review;detail/moving/244-caption samples and actual normal1x muted endpoints passed. Human listening/pronunciation/rights pending.')
v['finalRender'].update(revision='teaching-clarity-current34-v5',durationSeconds=pair['seconds'],frames=65917,
    status='reviewed-current34-local-pair',qa=rel(qa_path),pixelReview=rel(qa_path),technicalQa=qa['pairExecution'],
    videoClean=p['videoClean'],videoBurnedCaptions=p['videoBurnedCaptions'],allFinalPixelsReviewed=True,
    pixelReviewScope='All3170 planned samples;118 new directly read plus3052 prior exact RGB inherited. Every intervening frame not approved.')
assert main.read_bytes()==before
save(main,v)
for x in others+source_proof['results']:assert sha(ROOT/x['path'])==x['sha256']
proof=dict(schemaVersion=1,promotedAt=stamp,intentionalProtectedMainTransition=True,
    baselineMain=dict(path=rel(backup),sha256=before_sha,exactOriginalBytesPreserved=True),
    currentMain=dict(path=rel(main),sha256=sha(main)),other78ProtectedInputsUnchanged=True,otherProtectedInputs=others,
    repairCandidateUnchanged=True,repairCandidates=source_proof['results'],sourceReview=rel(qa_path),sourceReviewSha256=sha(qa_path),
    baselinePlatformModified=False,newActualVideoId=None,fourOutputsCollected=False,
    humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,newGitMedia=0)
save(record,proof)
cp=rd(O/'latest-checkpoint.json');cp.update(recordedAt=stamp,stage='current34-main-promoted-awaiting-four-output-collection',
    mainPromoted=True,mainPromotion=rel(record),next='Collect exact current root4outputs with shared/foreign index preservation;one privatecaptioned upload;available settings/reopen;selectGit;actual09slot replacement.')
save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_bytes();q=rd(qp);q['currentOrientationReview'].update(stage=cp['stage'],mainPromoted=True,
    mainPromotion=rel(record),activeOwnedWorkers=0,ownedJob=None,next=cp['next']);q['updatedAt']=stamp;assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(mainPromoted=True,currentMainSha256=sha(main),otherProtected=78,backupSha256=sha(backup),fourOutputsCollected=False)))
