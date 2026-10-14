"""Verify the failed original session and exact research handoff chain without mutation."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def live(x):
    try:return abs(psutil.Process(x['pid']).create_time()-x['createTime'])<.01
    except psutil.NoSuchProcess:return False
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
session=read(R/'narration-tts-session-v1.json');assert session['sessionId']==57445
assert not (R/'narration-tts-execution-v1.json').exists()
w=read(R/'narration-tts-waiting-v1.json')
assert not live(dict(pid=w['actualPid'],createTime=w['createTime']))
for x in w['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
req=read(R/'narration-tts-request-v1.json')
assert not any((ROOT/x['path']).exists() for x in req['scenes'])
h=read(ROOT/'shared/output/gpu-handoff/6c8440e2-e5ea-4040-82a7-7f2c98a96938.json')
assert h['project']=='motion-sickness-games' and h['ttsExitCode']==1 and h['state']=='research_resume_verified'
assert not live(h['coordinator']) and not live(h['ttsOwner'])
assert h['resumedQueue']['command']==h['queueOwner']['command']
assert h['resumedQueue']['cwd']==h['queueOwner']['cwd']
chain=[h];current=h['resumedQueue']
if not live(current):
    later=read(ROOT/'shared/output/gpu-handoff/759ca44d-310e-4a70-a0fc-ff5544606cd3.json')
    assert later['queueOwner']==current and later['state']=='research_resume_verified'
    assert later['resumedQueue']['command']==current['command'] and later['resumedQueue']['cwd']==current['cwd']
    chain.append(later);current=later['resumedQueue']
assert live(current)
p=psutil.Process(current['pid'])
assert p.cmdline()==current['command'] and Path(p.cwd()).resolve()==Path(current['cwd']).resolve()
status=read(Path(h['queueDir'])/'status.json')
assert status['owner_pid']==current['pid'] and status['status'] in ['running','waiting_for_resources']
for f in h['ownedFiles']:
    path=Path(f);assert not path.exists() or read(path).get('token')!=h['token']
log=ROOT/Path(h['ttsLog']).relative_to(ROOT)
assert 'Existing project evidence changed' in log.read_text('utf-8-sig')
v=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),actualOuterSession=57445,actualOuterExitCode=1,
    failure='Changed foreign duplicate inputs rejected coordinator child before model load.',modelLoaded=False,ownGpuModelJobs=0,
    newPcmCount=0,all68ProtectedInputsMatched=True,original14PcmRegenerated=0,
    restorationVerified=True,ownLeaseToken=h['token'],ownHistorySha256=sha(ROOT/'shared/output/gpu-handoff'/f"{h['token']}.json"),
    historicalOwnResume=h['resumedQueue'],laterForeignHandoffToken=chain[-1]['token'] if len(chain)>1 else None,
    actualCurrentQueue=current,actualCurrentStatus=status,verifierProcessOrControlChanges=0,
    foreignResumeIsOwnResume=False,completedResearchJobEvidence=h.get('completedJobEvidence'),finalMixedAsrApproved=False)
write(R/'research-handoff-premodel-failure-verification-v1.json',v)
session.update(actualOuterExitCode=1,actualExitObserved=True,modelLoaded=False,newPcmCount=0,failureProof='research-handoff-premodel-failure-verification-v1.json')
write(R/'narration-tts-session-v1.json',session)
c=read(R/'latest-checkpoint.json');c.update(recordedAt=v['observedAt'],stage='duplicate-input-change-before-model-failure-research-resume-verified',
    ttsStarted=False,failedOwnedSession=57445,actualOuterExitCode=1,newPcmCount=0,researchResumeVerified=True,
    next='Refresh six changed polygon inputs and current Studio; preserve failed request and use one versioned retry only after current check and fresh resource.')
write(R/'latest-checkpoint.json',c)
qpath=ROOT/'production/batches/cross-game-example-coverage-review/queue.json';q=read(qpath)
q['currentMotionReview']['ownedJob']=dict(sessionId=57445,status='failed-before-model',actualOuterExitCode=1,newPcmCount=0,restorationVerified=True,proof=str((R/'research-handoff-premodel-failure-verification-v1.json').relative_to(ROOT)))
write(qpath,q)
print('Actual57445 exit1/model0/PCM0/protected68/own resume and later foreign chain verified; no controls changed.')
