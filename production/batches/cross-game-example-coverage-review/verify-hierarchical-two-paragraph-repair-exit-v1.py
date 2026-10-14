"""Verify actual outer exit, owned lease closure and exact preserved research status."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def live(x):
 try:return abs(psutil.Process(x['pid']).create_time()-x['createTime'])<.01
 except psutil.NoSuchProcess:return False
ap=argparse.ArgumentParser();ap.add_argument('--session',type=int,required=True);ap.add_argument('--outer-exit',type=int,required=True);ap.add_argument('--completion',required=True);a=ap.parse_args()
session=read(O/'narration-two-paragraph-repair-session-v1.json');assert session['sessionId']==a.session
assert not live(session) and all(not live(x) for x in session['launcherIdentities'])
statep=O/'narration-two-paragraph-repair-execution-v1.json';state=read(statep);assert not state.get('actualExitObserved')
assert state['actualPid']==session['pid'] and state['exitCode']==a.outer_exit and state['total']==2
if a.outer_exit==0:assert state['generationComplete'] and len(state['results'])==2
for x in state['protectedInputs']+state['results']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
hp=ROOT/'shared/output/gpu-handoff'/f"{state['leaseToken']}.json";history=read(hp)
assert history['project']=='hierarchical-game-outlines' and history['token']==state['leaseToken']
leasep=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(leasep) if leasep.exists() else None
assert not lease or lease['token']!=state['leaseToken'];assert not live(history['coordinator'])
resource=read(O/'resource-before-two-paragraph-repair-voice-v1.json');statusp=Path(resource['research']['statusPath']);status=read(statusp)
assert history.get('idleGpu') and history['state']=='tts_process_exiting','Active queue handoff requires its exact original-command/cwd restoration verifier; do not relabel it idle.'
assert sha(statusp)==resource['research']['statusSha256'] and status==resource['research']['status']
assert status['status']=='complete_pending_visual_review' and status['completed']==status['total']==1088
research_history=read(ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1/resource-and-annotation-handoff-v15.json')
assert sha(statusp)==research_history['currentResearchStatusSha256']
last_owner=research_history['currentOriginalResearchIdentity']
assert not live(dict(pid=last_owner['pid'],createTime=last_owner['createTime']))
assert 'owner_pid' not in status,'The completed queue writer clears its old owner; inspect a new owner if present.'
guard=read(O/'two-paragraph-repair-owned-idle-guard-v1.json');assert guard['leaseToken']==state['leaseToken'] and guard['stable20SecondsVerified']
cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={session["pid"]}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json'],text=True,encoding='utf-8',errors='replace');assert not cim.strip()
at=datetime.now(timezone.utc).isoformat();proof=dict(verifiedAt=at,actualOuterSession=a.session,actualOuterExitCode=a.outer_exit,actualCompletion=a.completion,ownedWorkerClosed=True,ownedLauncherClosed=True,cimAbsence=cim,leaseToken=state['leaseToken'],ownedIdleLeaseClosed=True,historyPath=hp.relative_to(ROOT).as_posix(),historySha256=sha(hp),currentForeignLease=lease,protectedInputCount=len(state['protectedInputs']),allProtectedShaMatched=True,newPcmCount=len(state['results']),allAvailableNewPcmShaMatched=True,researchWasPaused=False,researchRestarted=False,completedResearchStatusUnchanged=True,researchStatusPath=str(statusp),researchStatusSha256=sha(statusp),researchStatus=status,restorationVerified=True,restorationScope='Own idle lease released; previously completed queue preserved exactly, with no restart or optimizer/RNG claim.',processOrControlChanges=0,humanListeningApproved=False,currentMixedApproved=False)
out=O/'two-paragraph-repair-voice-closure-verification-v1.json';assert not out.exists();save(out,proof)
state.update(actualExitObserved=True,actualOuterExitCode=a.outer_exit,actualOuterSession=a.session,actualCompletion=a.completion,ownedClosureVerified=True,researchCompletePreserved=True);save(statep,state)
cp=read(O/'latest-checkpoint.json');cp.update(stage='two-candidates-voice-closed-awaiting-current-ASR',activeOwnedWorkers=0,ownedJob=None,crossGameVoiceClosure=out.relative_to(ROOT).as_posix(),next='Fresh CPU resource then wholetwo currentPCM ASR once; directly compare allfulltext and prepare18 complete independent contexts. Original12PCM unchanged;21r adoption remains false.');save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentHierarchicalReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,crossGameVoiceClosure=cp['crossGameVoiceClosure'],next=cp['next']);q['updatedAt']=at;assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(session=a.session,outerExit=a.outer_exit,newPcm=len(state['results']),protected=len(state['protectedInputs']),ownedClosed=True,researchCompletePreserved=True)))
