"""Read-only verification of actual66238 exit1 and restored original queue."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def live(x):
    try:return abs(psutil.Process(x['pid']).create_time()-x['createTime'])<.01
    except psutil.NoSuchProcess:return False
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
s=read(R/'narration-tts-session-v4.json');assert s['sessionId']==66238
w=read(R/'narration-tts-waiting-v4.json');assert not live(dict(pid=w['actualPid'],createTime=w['createTime']))
assert not (R/'narration-tts-execution-v4.json').exists()
request=read(R/'narration-tts-request-v1.json');assert not any((ROOT/x['path']).exists() for x in request['scenes'])
for x in w['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
hp=ROOT/'shared/output/gpu-handoff/a5373dcb-af59-4431-b6b9-41eb1b89f07a.json';h=read(hp)
assert h['state']=='research_resume_verified' and h['ttsExitCode']==1 and not live(h['coordinator'])
log=Path(h['ttsLog']);txt=log.read_text('utf-8-sig');assert 'Existing project evidence changed' in txt
assert h['resumedQueue']['command']==h['queueOwner']['command'] and h['resumedQueue']['cwd']==h['queueOwner']['cwd']
lp=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(lp) if lp.exists() else None;assert not lease or lease['token']!=h['token']
for name in h['ownedFiles']:
    p=Path(name);assert not p.exists() or read(p).get('token')!=h['token']
resumed=h['resumedQueue'];current=read(Path(h['queueDir'])/'status.json')
if live(resumed):
    p=psutil.Process(resumed['pid']);assert p.cmdline()==resumed['command'] and p.cwd()==resumed['cwd']
    assert current['owner_pid']==p.pid and current['status'] in ['running','waiting_for_resources']
    obs=dict(kind='actual-own-restored-queue-alive',identity=resumed,status=current)
else:
    assert lease and lease['queueOwner']==resumed and live(lease['coordinator'])
    obs=dict(kind='own-restoration-then-foreign-handoff',identity=resumed,currentForeignToken=lease['token'],coordinator=lease['coordinator'])
v=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),actualOuterSession=66238,actualOuterExitCode=1,
    ownLeaseToken=h['token'],historySha256=sha(hp),ttsLogSha256=sha(log),failure='foreign duplicate inputs changed during owned stable-GPU wait',
    modelLoaded=False,newPcmCount=0,all68ProtectedInputsMatched=True,restorationVerified=True,
    historicalOwnResumedQueue=resumed,currentObservation=obs,processOrControlChangesByVerifier=0,original14PcmRegenerated=0)
proof=R/'research-handoff-premodel-failure-verification-v4.json';assert not proof.exists();save(proof,v)
s.update(actualOuterExitCode=1,actualExitObserved=True,newPcmCount=0,modelLoaded=False,failureProof=proof.name);save(R/'narration-tts-session-v4.json',s)
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=v['observedAt'],stage='foreign-input-change-before-model-original-research-restoration-verified-v4',
    actualOuterSession=66238,actualOuterExitCode=1,newPcmCount=0,researchResumeVerified=True,currentOwnedVoiceWorkerAlive=False,currentOwnedGpuJobs=0,
    currentOwnedHandoff=None,ownedJob=dict(sessionId=66238,actualOuterExitCode=1,state='closed-before-model',proof=proof.relative_to(ROOT).as_posix()),
    next='Read all changed duplicate contents/current Studio before a new request. Keep stable GPU guard and foreign work intact. Preserve baseline schedule until replacement reviewed.')
save(R/'latest-checkpoint.json',cp)
qp=Path(__file__).parent/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw);q['currentMotionReview'].update(status=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next']);assert qp.read_text('utf-8-sig')==raw;save(qp,q)
print('Actual66238exit1/model0/PCM0/68SHA/ownlease closure/originalresearch74836 restored verified.')
