"""Run only after the actual outer exec session reports completion.

Verify recorded process identities and the current original research queue.
This verifier does not start, stop or remove any process/control file.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):
 temp=p.with_name(p.name+'.verification-writing');temp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');temp.replace(p)
def same_live(i):
 try:
  p=psutil.Process(i['pid'])
  return abs(p.create_time()-i['createTime'])<.01
 except psutil.NoSuchProcess:return False
ap=argparse.ArgumentParser();ap.add_argument('--outer-exit-code',type=int,required=True);ap.add_argument('--session-id',type=int,required=True);args=ap.parse_args()
assert args.session_id==read(BASE/'observation-candidates-tts-session-v3.json')['sessionId'],'Require the actual observation-candidates serialized request session'
statePath=BASE/'observation-candidates-tts-execution-v3.json';state=read(statePath)
assert args.outer_exit_code==state['exitCode']==0 and state['generationComplete']
assert len(state['results'])==state['total']==11
assert not same_live({'pid':state['actualPid'],'createTime':state['createTime']}),'Voice worker still alive'
historyPath=ROOT/'shared/output/gpu-handoff'/f"{state['leaseToken']}.json";history=read(historyPath)
assert history['token']==state['leaseToken'] and history['project']=='presenting-game-scores'
assert not same_live(history['coordinator']),'Own coordinator still alive'
currentLeasePath=ROOT/'shared/output/GPU_HANDOFF.json'
currentLease=read(currentLeasePath) if currentLeasePath.exists() else None
assert not currentLease or currentLease['token']!=state['leaseToken'],'Own lease not closed'
for r in state['results']:assert sha(ROOT/r['path'])==r['sha256']
stamp=datetime.now(timezone.utc).isoformat()
proof=dict(schemaVersion=1,observedAt=stamp,ttsLeaseToken=state['leaseToken'],historyPath=historyPath.relative_to(ROOT).as_posix(),
 historySha256=sha(historyPath),actualOuterSession=args.session_id,actualOuterExitCode=args.outer_exit_code,
 ownedVoiceWorkerClosed=True,ownedCoordinatorClosed=True,foreignLeasePreserved=currentLease,
 processOrControlChangesByVerifier=0,allElevenCandidatePcmHashesMatched=True,restorationVerified=False)
if history.get('idleGpu'):
 assert history['state']=='tts_process_exiting'
 proof.update(restorationVerified=True,researchWasPaused=False,researchRestartedByOwnJob=False,
  restorationScope='Owned idle lease closed at process exit; no research was paused by this voice job')
else:
 assert history['ttsExitCode']==0 and history['state']=='research_resume_verified',history['state']
 original=history['queueOwner'];resumed=history['resumedQueue'];recordedStatus=history['resumedStatus']
 assert resumed['command']==original['command'] and Path(resumed['cwd']).resolve()==Path(original['cwd']).resolve()
 assert recordedStatus['owner_pid']==resumed['pid'] and recordedStatus['status'] in ['running','waiting_for_resources']
 assert same_live(resumed),'Resumed identity must be observed alive; inspect later handoff if it has since ended'
 resumedProcess=psutil.Process(resumed['pid']);assert resumedProcess.cmdline()==resumed['command'] and Path(resumedProcess.cwd()).resolve()==Path(original['cwd']).resolve()
 currentStatus=read(Path(history['queueDir'])/'status.json')
 assert currentStatus['owner_pid']==resumed['pid'] and currentStatus['status'] in ['running','waiting_for_resources']
 completed=history.get('completedJobEvidence')
 if completed:
  marker=Path(completed['marker']);assert sha(marker)==completed['markerSha256']
  validation=completed['validation'];assert validation.get('numerically_finite') is not False
  assert validation.get('checkpoint_finite') is not False
  assert all(Path(p).exists() for p in completed['outputs'])
 for path in history.get('ownedFiles',[]):
  p=Path(path)
  assert not p.exists() or read(p).get('token')!=state['leaseToken'],'Own cooperative control remains'
 proof.update(restorationVerified=True,researchWasPaused=True,researchRestartedByOwnJob=True,
  originalResearchIdentity=original,observedResumedIdentity=dict(pid=resumedProcess.pid,createTime=resumedProcess.create_time(),command=resumedProcess.cmdline(),cwd=resumedProcess.cwd()),
  recordedResumedStatus=recordedStatus,currentResumedStatus=currentStatus,completedResearchJobEvidence=completed,
  restorationScope='Exact original command/cwd and fresh running/waiting queue ownership observed; no optimizer/RNG recovery claim')
save(BASE/'observation-candidates-research-resume-verification-v3.json',proof)
state.update(actualExitObserved=True,actualOuterExitCode=args.outer_exit_code,actualOuterSession=args.session_id,
 actualExitObservedAt=stamp,researchResumeVerified=True);save(statePath,state)
print('Actual eleven-item candidate voice exit0 and own lease closure verified; original research resume verified without process/control mutation.')
