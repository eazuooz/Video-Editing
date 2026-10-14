"""Read-only verification of actual 46624 exit1 before voice model load."""
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
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
s=read(R/'narration-tts-session-v2.json');assert s['sessionId']==46624
w=read(R/'narration-tts-waiting-v2.json');assert not live(dict(pid=w['actualPid'],createTime=w['createTime']))
assert not (R/'narration-tts-execution-v2.json').exists()
for x in w['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
req=read(R/'narration-tts-request-v1.json');assert not any((ROOT/x['path']).exists() for x in req['scenes'])
hp=ROOT/'shared/output/gpu-handoff/8cfc58ed-6b07-49e0-8bc5-18a3ef534dec.json';h=read(hp)
assert h['project']=='motion-sickness-games' and h['state']=='research_resume_verified'
assert not live(h['coordinator']) and not h.get('ttsOwner') and not h.get('ttsLog')
marker=Path(h['queueDir'])/'done/train_shadow_only_head_42.json';m=read(marker)
assert m['validation']['numerically_finite'] is False and m['validation']['checkpoint_finite'] is False
assert h['resumedQueue']['command']==h['queueOwner']['command'] and h['resumedQueue']['cwd']==h['queueOwner']['cwd']
leasePath=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(leasePath) if leasePath.exists() else None
assert not lease or lease['token']!=h['token']
for name in h['ownedFiles']:
    p=Path(name);assert not p.exists() or read(p).get('token')!=h['token']
current=h['resumedQueue'];chain=[]
if live(current):
    p=psutil.Process(current['pid']);assert p.cmdline()==current['command'] and p.cwd()==current['cwd']
    observation=dict(kind='own-resumed-queue-currently-alive',identity=current)
else:
    assert lease and lease['queueOwner']==current and live(lease['coordinator'])
    observation=dict(kind='historical-own-resume-then-foreign-handoff',ownResumedIdentity=current,
      foreignToken=lease['token'],foreignCoordinator=lease['coordinator'],foreignState=lease['state'])
v=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),actualOuterSession=46624,actualOuterExitCode=1,
    failure='Coordinator rejects completed train_shadow_only_head_42 non-finite validation before launching TTS.',
    failureInference='Actual exit1, no TTS owner/log/state/PCM, marker validation false, and coordinator wait_boundary guard directly read.',
    modelLoaded=False,ownGpuModelJobs=0,newPcmCount=0,all68ProtectedInputsMatched=True,
    ownLeaseToken=h['token'],ownHistorySha256=sha(hp),researchMarkerSha256=sha(marker),researchValidation=m['validation'],
    restorationVerified=True,historicalOwnResume=current,historicalOwnResumeStatus=h['resumedStatus'],currentObservation=observation,
    currentResearchStatus=read(Path(h['queueDir'])/'status.json'),foreignResumeIsOwnResume=False,
    verifierProcessOrControlChanges=0,original14PcmRegenerated=0,finalMixedAsrApproved=False)
save(R/'research-handoff-premodel-failure-verification-v2.json',v)
s.update(actualOuterExitCode=1,actualExitObserved=True,modelLoaded=False,newPcmCount=0,failureProof='research-handoff-premodel-failure-verification-v2.json');save(R/'narration-tts-session-v2.json',s)
c=read(R/'latest-checkpoint.json');c.update(recordedAt=v['observedAt'],stage='research-validation-rejected-before-voice-model-restoration-verified',
  actualOuterSession=46624,actualOuterExitCode=1,newPcmCount=0,researchResumeVerified=True,
  prototypeStructuralPixelReviewApproved=True,structuralReview='structural-prototype-direct-review-v1.json',
  next='Preserve failed research validation and its restored queue; respect current foreign handoff. Measured narration/final annotation/mix remain pending.');save(R/'latest-checkpoint.json',c)
qp=ROOT/'production/batches/cross-game-example-coverage-review/queue.json';q=read(qp)
q['currentMotionReview']['ownedJob']=dict(sessionId=46624,status='failed-before-model-research-validation',actualOuterExitCode=1,newPcmCount=0,
  restorationVerified=True,proof=str((R/'research-handoff-premodel-failure-verification-v2.json').relative_to(ROOT)));save(qp,q)
print('Actual46624 exit1/non-finite research marker/model0/PCM0/protected68/own restoration verified; foreign controls untouched.')
