"""Read-only verification after the actual eleven-item outer session exits."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
 t=p.with_name(p.name+'.verifying');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def live(i):
 try:return abs(psutil.Process(i['pid']).create_time()-i['createTime'])<.01
 except psutil.NoSuchProcess:return False
ap=argparse.ArgumentParser();ap.add_argument('--outer-exit-code',type=int,required=True);ap.add_argument('--session-id',type=int,required=True);a=ap.parse_args()
launch=read(BASE/'narration-tts-session-v1.json');assert a.session_id==launch['sessionId']
s=read(BASE/'narration-tts-execution-v1.json');assert a.outer_exit_code==s['exitCode']==0 and s['generationComplete'] and len(s['results'])==11
assert not live(launch['actualOuterIdentity']) and not live(dict(pid=s['actualPid'],createTime=s['createTime']))
hp=ROOT/'shared/output/gpu-handoff'/f"{s['leaseToken']}.json";h=read(hp)
assert h['token']==launch['leaseToken']==s['leaseToken'] and h['project']=='presenting-game-scores'
assert not live(h['coordinator']);lp=ROOT/'shared/output/GPU_HANDOFF.json';current=read(lp) if lp.exists() else None
assert not current or current['token']!=s['leaseToken']
for r in s['results']:assert sha(ROOT/r['path'])==r['sha256']
proof=dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),ttsLeaseToken=s['leaseToken'],historyPath=hp.relative_to(ROOT).as_posix(),historySha256=sha(hp),actualOuterSession=a.session_id,actualOuterExitCode=a.outer_exit_code,ownedVoiceWorkerClosed=True,ownedCoordinatorClosed=True,foreignLeasePreserved=current,processOrControlChangesByVerifier=0,allElevenCurrentPcmHashesMatched=True,restorationVerified=False)
if h.get('idleGpu'):
 assert h['state']=='tts_process_exiting';proof.update(restorationVerified=True,researchWasPaused=False,researchRestartedByOwnJob=False)
else:
 assert h['ttsExitCode']==0 and h['state']=='research_resume_verified',h['state']
 original=h['queueOwner'];resumed=h['resumedQueue'];recorded=h['resumedStatus']
 assert resumed['command']==original['command'] and Path(resumed['cwd']).resolve()==Path(original['cwd']).resolve()
 assert recorded['owner_pid']==resumed['pid'] and recorded['status'] in ['running','waiting_for_resources']
 assert live(resumed),'Inspect any later handoff history; never blindly start research'
 p=psutil.Process(resumed['pid']);assert p.cmdline()==resumed['command'] and Path(p.cwd()).resolve()==Path(original['cwd']).resolve()
 status=read(Path(h['queueDir'])/'status.json');assert status['owner_pid']==resumed['pid'] and status['status'] in ['running','waiting_for_resources']
 completed=h.get('completedJobEvidence')
 if completed:
  assert sha(Path(completed['marker']))==completed['markerSha256']
  assert completed['validation'].get('numerically_finite') is not False
  assert completed['validation'].get('checkpoint_finite') is not False
  assert all(Path(x).exists() for x in completed['outputs'])
 for x in h.get('ownedFiles',[]):
  pth=Path(x);assert not pth.exists() or read(pth).get('token')!=s['leaseToken']
 child=None
 if status.get('child_pid') and psutil.pid_exists(status['child_pid']):
  c=psutil.Process(status['child_pid']);child=dict(pid=c.pid,createTime=c.create_time(),command=c.cmdline(),cwd=c.cwd())
 proof.update(restorationVerified=True,researchWasPaused=True,researchRestartedByOwnJob=True,originalResearchIdentity=original,observedResumedIdentity=resumed,recordedResumedStatus=recorded,currentResumedStatus=status,observedResumedChild=child,completedResearchJobEvidence=completed,restorationScope='Exact original command/cwd and fresh running/waiting queue ownership observed; GPU training status distinguished from queue waiting; no optimizer/RNG recovery claim')
out=BASE/'research-handoff-verification-v1.json';assert not out.exists();save(out,proof)
s.update(actualExitObserved=True,actualOuterExitCode=a.outer_exit_code,actualOuterSession=a.session_id,actualExitObservedAt=proof['observedAt'],researchResumeVerified=True);save(BASE/'narration-tts-execution-v1.json',s)
launch.update(workerExpectedRunning=False,actualOuterExitCode=a.outer_exit_code,actualExitObservedAt=proof['observedAt']);save(BASE/'narration-tts-session-v1.json',launch)
print('Actual11-item voice outer exit0 and original research command/cwd/queue restoration verified without mutation.')
