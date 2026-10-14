"""Verify the actual original session's pre-model GPU timeout and restoration."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib, psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def live(x):
    try:return abs(psutil.Process(x['pid']).create_time()-x['createTime'])<.01
    except psutil.NoSuchProcess:return False
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--outer-exit-code',required=True,type=int)
ap.add_argument('--session-id',required=True,type=int);a=ap.parse_args()
s=read(R/'narration-tts-session-v3.json');assert a.session_id==s['sessionId']==58747 and a.outer_exit_code==1
w=read(R/'narration-tts-waiting-v3.json')
assert not live(dict(pid=w['actualPid'],createTime=w['createTime']))
assert not (R/'narration-tts-execution-v3.json').exists()
request=read(R/'narration-tts-request-v1.json')
assert not any((ROOT/x['path']).exists() for x in request['scenes'])
for x in w['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
hp=ROOT/'shared/output/gpu-handoff/956228e6-e226-4c00-aa0a-c371c250af54.json';h=read(hp)
assert h['project']=='motion-sickness-games' and h['state']=='research_resume_verified'
assert not live(h['coordinator']) and not h.get('ttsOwner') and not h.get('ttsLog')
assert h.get('ttsStarted') is False and h['gpuWaitTimeoutSeconds']==600
assert h['resumedQueue']['command']==h['queueOwner']['command'] and h['resumedQueue']['cwd']==h['queueOwner']['cwd']
leasePath=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(leasePath) if leasePath.exists() else None
assert not lease or lease['token']!=h['token']
for name in h['ownedFiles']:
    p=Path(name);assert not p.exists() or read(p).get('token')!=h['token']
resumed=h['resumedQueue'];current=read(Path(h['queueDir'])/'status.json')
if live(resumed):
    p=psutil.Process(resumed['pid']);assert p.cmdline()==resumed['command'] and p.cwd()==resumed['cwd']
    assert current['owner_pid']==p.pid and current['status'] in ['running','waiting_for_resources']
    observation=dict(kind='actual-own-restored-queue-alive',identity=resumed,status=current)
else:
    assert lease and lease['queueOwner']==resumed and live(lease['coordinator'])
    observation=dict(kind='own-restoration-then-foreign-handoff',identity=resumed,
        currentForeignToken=lease['token'],foreignCoordinator=lease['coordinator'])
v=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),actualOuterSession=a.session_id,
    actualOuterExitCode=a.outer_exit_code,ownLeaseToken=h['token'],historySha256=sha(hp),
    reason=h['reason'],gpuWaitTimeoutSeconds=h['gpuWaitTimeoutSeconds'],lastGpuObservation=h['lastGpuObservation'],
    modelLoaded=False,newPcmCount=0,all68ProtectedInputsMatched=True,restorationVerified=True,
    historicalOwnResumedQueue=resumed,currentObservation=observation,processOrControlChangesByVerifier=0,
    original14PcmRegenerated=0,finalMixedAsrApproved=False)
proof=R/'research-handoff-premodel-timeout-verification-v3.json';assert not proof.exists();save(proof,v)
s.update(actualOuterExitCode=a.outer_exit_code,actualExitObserved=True,newPcmCount=0,modelLoaded=False,
    failureProof=proof.name);save(R/'narration-tts-session-v3.json',s)
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=v['observedAt'],
    stage='gpu-idle-timeout-before-model-original-research-restoration-verified',
    actualOuterSession=a.session_id,actualOuterExitCode=a.outer_exit_code,newPcmCount=0,researchResumeVerified=True,
    currentOwnedVoiceWorkerAlive=False,currentOwnedGpuJobs=0,
    portalStaticReview='portal-annotation-static-direct-review-v1.json',
    alyxObservationPlan='alyx-annotation-observation-plan-v1.json',
    next='No rapid duplicate request. Read current resources and actual history first. Retry one protected voice request only after stable idle GPU is available; pilot/ASR requires freeRAM>8millionKiB. Preserve all baselines and existing schedules.')
save(R/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/cross-game-example-coverage-review/queue.json';qraw=qp.read_text('utf-8-sig');q=json.loads(qraw)
q['currentMotionReview'].update(status=cp['stage'],ownedJob=dict(sessionId=a.session_id,
    actualOuterExitCode=1,state='closed-before-model',newPcmCount=0,restorationVerified=True,proof=str(proof.relative_to(ROOT))),
    next=cp['next']);assert qp.read_text('utf-8-sig')==qraw;save(qp,q)
print('Actual58747 exit1/600s stable-idle timeout/model0/68protectedSHA/actual own research restoration verified.')
