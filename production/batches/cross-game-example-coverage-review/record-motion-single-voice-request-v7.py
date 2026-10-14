"""Record actual observer completion and the single live serialized request."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil,os
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
B=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):
    tmp=p.with_name(p.name+'.'+str(os.getpid())+'.writing');tmp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
now=datetime.now(timezone.utc).isoformat()
resource=read(R/'voice-retry-resource-verification-v14.json')
assert resource['voiceRequestEligible'] and resource['all68ProtectedHashesMatched']
waiting=read(R/'narration-tts-waiting-v7.json')
p=psutil.Process(waiting['actualPid']);assert abs(p.create_time()-waiting['createTime'])<.01
assert p.cmdline()==waiting['commandLine'] and p.cwd()==waiting['cwd']
sp=R/'narration-tts-session-v7.json';assert not sp.exists()
session=dict(schemaVersion=1,version=7,sessionId=62462,startedAt=waiting['recordedAt'],recordedAt=now,
    pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),state='serialized-owned-handoff-active',
    resource='voice-retry-resource-verification-v14.json',resourceSha256=sha(R/'voice-retry-resource-verification-v14.json'),
    duplicateProof='duplicate-content-and-studio-direct-review-v9.json',duplicateCheckChunk='fa77cd',duplicateCheckExitCode=0,
    actualOuterExitCode=None,original14PcmRegenerated=0)
save(sp,session)
dp=R/'duplicate-current-check-verification-v9.json';assert not dp.exists()
save(dp,dict(schemaVersion=1,verifiedAt=now,decisionChunk='22fc85',decisionExitCode=0,checkChunk='fa77cd',checkExitCode=0,
    proof='duplicate-content-and-studio-direct-review-v9.json',proofSha256=sha(R/'duplicate-content-and-studio-direct-review-v9.json'),
    reportSha256=sha(ROOT/'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'),currentCheckPassed=True))
cp=read(R/'latest-checkpoint.json')
cp.update(recordedAt=now,stage='single-v7-request-owned-research-boundary-and-idle-guard',userPaused=False,
    currentDuplicateCheckPassed=True,currentDuplicateReview='duplicate-content-and-studio-direct-review-v9.json',
    currentDuplicateCheckVerification='duplicate-current-check-verification-v9.json',
    currentResourceVerification='voice-retry-resource-verification-v14.json',preparedVoiceVersion=7,
    ownedJob=dict(sessionId=62462,pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),
        state='narration-tts-session-v7.json',gpuJobs=0,modelLoaded=False,actualOuterExitCode=None),
    next='Reuse actual62462/live identity; no second request. Observe actual outer completion, then verify own lease closure/exact original research restoration for success or failure. If three PCM exist, run current whole3 and independent15 CPU ASR once, followed by narration-timed annotations/ratio/mix/final QA/private/Git/schedule replacement.')
save(R/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
q['status']='active';q['userPauseActive']=False;q['resumeUserEvidence']='계속 끝날때까지 재게해줘';q['updatedAt']=now
q['currentMotionReview'].update(status=cp['stage'],stage=cp['stage'],ownedJob=cp['ownedJob'],
    currentResourceVerification=str((R/'voice-retry-resource-verification-v14.json').relative_to(ROOT)).replace('\\','/'),
    currentDuplicateReview=str((R/'duplicate-content-and-studio-direct-review-v9.json').relative_to(ROOT)).replace('\\','/'),
    currentDuplicateCheckPassed=True,preparedVoiceVersion=7,currentReadOnlyObserver=dict(version=14,actualSession=80003,exitCode=0,completionChunk='3e0f5e'),next=cp['next'])
assert qp.read_text('utf-8-sig')==raw;save(qp,q)
save(ROOT/'production/resume-until-part2-boundary-20261012.json',dict(recordedAt=now,userEvidence='계속 끝날때까지 재게해줘',
    userPauseActive=False,automation24ExpectedStatus='ACTIVE',authorizedBoundary='game-math-normal-transform-uv',
    boundaryRequires='production/review/four outputs/private settings/Git/actual schedule replacement',
    stopOnlyAfterBoundaryCompleted=True,startSubsequentNewLectures=False,startNewSakuraiSix=False,
    preserveSeparateOwnerQueues=True,currentOwnedRequestSession=62462))
print('Recorded actual62462 single request/current duplicate pass/observer80003 exit0; no extra worker or foreign mutation.')
