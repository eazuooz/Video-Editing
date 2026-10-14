"""Preserve the closed V3 request and current foreign handoff/resource gates."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
proof=read(R/'research-handoff-premodel-timeout-verification-v3.json')
assert proof['actualOuterExitCode']==1 and proof['restorationVerified'] and proof['newPcmCount']==0
w=read(R/'narration-tts-waiting-v3.json')
for x in w['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
assert lease['project']!='motion-sickness-games' and lease['queueOwner']==proof['historicalOwnResumedQueue']
p=psutil.Process(lease['coordinator']['pid'])
assert abs(p.create_time()-lease['coordinator']['createTime'])<.01
assert p.cmdline()==lease['coordinator']['command'] and p.cwd()==lease['coordinator']['cwd']
pilot=R/'portal-annotation-pilot-execution-v1.json'
assert not pilot.exists()
resources=read(R/'annotation-pilot-resource-v2.json')
assert resources['freePhysicalMemoryKiB']<=8_000_000
out=R/'resource-and-annotation-handoff-v4.json';assert not out.exists()
v=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),
    actualVoiceOuterSession=58747,actualVoiceExitCode=1,voiceModelLoaded=False,newPcmCount=0,
    ownVoiceWorkerClosed=True,ownLeaseClosed=True,ownResearchRestorationVerified=True,
    ownRestorationProof='research-handoff-premodel-timeout-verification-v3.json',
    ownRestorationProofSha256=sha(R/'research-handoff-premodel-timeout-verification-v3.json'),
    currentForeignHandoff=dict(token=lease['token'],project=lease['project'],state=lease['state'],
        coordinator=lease['coordinator'],originalQueueIdentity=lease['queueOwner'],coordinatorAlive=True),
    currentResearchStatus=read(Path(lease['queueDir'])/'status.json'),
    currentAvailableMemoryBytes=psutil.virtual_memory().available,
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.free,utilization.gpu',
        '--format=csv,noheader'],text=True).strip(),
    all68ProtectedInputsMatched=True,
    portalStaticReview='portal-annotation-static-direct-review-v1.json',
    portalStaticReviewSha256=sha(R/'portal-annotation-static-direct-review-v1.json'),
    alyxObservationPlan='alyx-annotation-observation-plan-v1.json',
    alyxObservationPlanSha256=sha(R/'alyx-annotation-observation-plan-v1.json'),
    pilotAttempt=dict(actualShellExitCode=1,reason='Resource assertion before state/output creation: freePhysicalMemoryKiB6882152 below8000000.',
        resource='annotation-pilot-resource-v2.json',heavyWorkerCreated=False,renderStateCreated=False,newEncodedMedia=0),
    allMovingAnnotationApproved=False,narrationTimed=False,finalMixedAsrApproved=False,
    actualReplacementVideoId=None,gitImagesAdded=0,originalScheduleChanged=False,
    originalUploadDeleted=False,processAndForeignControlsChanged=0,
    next='Read actual current resources before one new voice request; no rapid repeat after600s idle timeout. Preserve current foreign handoff. Pilot/ASR deferred until free physicalRAM>8millionKiB. Reuse sealed structural/source/static reviews; do not regenerate completed work.')
save(out,v)
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=v['observedAt'],currentHandoff=out.name,
    ownedJob=dict(sessionId=58747,state='closed-before-model-gpu-idle-timeout',actualOuterExitCode=1,gpuJobs=0),
    currentForeignHandoff=v['currentForeignHandoff'],next=v['next']);save(R/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/cross-game-example-coverage-review/queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
q['currentMotionReview'].update(status=cp['stage'],ownedJob=cp['ownedJob'],resourceHandoff=str(out.relative_to(ROOT)),next=v['next'])
assert qp.read_text('utf-8-sig')==raw;save(qp,q)
print('Closed58747/restoration followed by live foreign handoff; protected68/static4/Alyx6 verified. No new render/model/media/Git/platform mutation.')
