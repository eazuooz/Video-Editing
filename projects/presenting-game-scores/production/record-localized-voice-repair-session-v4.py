"""Record the existing two-item coordinator wait; never create another request."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, time, psutil
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    t=p.with_name(p.name+'.session-recording');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--session-id',type=int,required=True);args=ap.parse_args()
waitingp=BASE/'localized-voice-repair-tts-waiting-v4.json';waiting=read(waitingp)
lease=read(ROOT/'shared/output/GPU_HANDOFF.json');assert lease['project']=='presenting-game-scores'
outer=psutil.Process(waiting['actualPid']);assert abs(outer.create_time()-waiting['createTime'])<.01
coordinator=psutil.Process(lease['coordinator']['pid']);assert abs(coordinator.create_time()-lease['coordinator']['createTime'])<.01
assert any(p.pid==outer.pid for p in coordinator.parents()),'Do not claim another coordinator as owned'
assert 'render-localized-voice-repair-v4.py' in ' '.join(outer.cmdline())
request=read(BASE/'localized-voice-repair-tts-request-v4.json')
for row in request['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256']
stamp=datetime.now(timezone.utc).isoformat()
cim=subprocess.run(['powershell','-NoProfile','-Command',
    f'Get-CimInstance Win32_Process | Where-Object {{$_.ProcessId -in @({outer.pid},{coordinator.pid})}} | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],
    capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
observations=json.loads(cim.stdout);assert len(observations)==2
job=dict(pid=outer.pid,createTime=outer.create_time(),commandLine=outer.cmdline(),cwd=outer.cwd(),
    sessionId=args.session_id,coordinator=lease['coordinator'],leaseToken=lease['token'],
    state='projects/presenting-game-scores/production/localized-voice-repair-tts-execution-v4.json',
    waitingState='projects/presenting-game-scores/production/localized-voice-repair-tts-waiting-v4.json',
    log=None,gpu=0,cpuThreads=2,modelLoaded=False,workerExpectedRunning=True,exitCode=None)
sp=BASE/'localized-voice-repair-tts-session-v4.json';assert not sp.exists()
save(sp,dict(schemaVersion=1,recordedAt=stamp,sessionId=args.session_id,outerPid=outer.pid,
    outerCreateTime=outer.create_time(),outerCommandLine=outer.cmdline(),cwd=outer.cwd(),
    ownedCoordinator=lease['coordinator'],leaseToken=lease['token'],workerExpectedRunning=True,
    actualExitObserved=False,exitCode=None,modelLoaded=False,gpuJobs=0,cimObservation=observations,
    state=job['state'],waitingState=job['waitingState'],protectedInputsMatched=True))
waiting.update(sessionId=args.session_id,ownedLeaseToken=lease['token'],ownedCoordinator=lease['coordinator']);save(waitingp,waiting)
cp_path=BASE/'latest-checkpoint.json';cp=read(cp_path)
action='Observe actual localized-v4 successor first. Finish current research checkpoint/validation/done; coordinator runs only two exact-text takes and restores original command/cwd on success/failure. After actual outer exit verify own research resume, fresh resources, whole2 and independent complete contexts/joins. Preserve all completed10+11 PCM and26 new ASR windows; no candidate adoption or final approval yet.'
cp.update(recordedAt=stamp,stage='localized-two-voice-cooperative-boundary-wait-v4',ownedJob=job,
    currentVoiceApproved=False,asrApproved=False,narrationApproved=False,
    localizedRepairRequest='projects/presenting-game-scores/production/localized-voice-repair-tts-request-v4.json',
    completedCandidateWholeReview='projects/presenting-game-scores/production/observation-candidates-whole-direct-review-v3.json',
    completedCandidateContextsReview='projects/presenting-game-scores/production/observation-candidates-contexts-direct-review-v3.json',
    completedCandidateTargetsReview='projects/presenting-game-scores/production/observation-candidates-targets-direct-review-v3.json',
    candidateVoiceResearchResume='projects/presenting-game-scores/production/observation-candidates-research-resume-verification-v3.json',
    nextAction=action);save(cp_path,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
    raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
    item.update(stage=cp['stage'],currentExecution=job,nextAction=action)
    item['checkpoints']['narration']=False;q.update(updatedAt=stamp,lastProgressAt=stamp)
    if qp.read_text('utf-8-sig')==raw:save(qp,q);break
    time.sleep(.15)
else:raise RuntimeError('Concurrent batch change; preserve foreign data')
print(json.dumps(dict(sessionId=args.session_id,outerPid=outer.pid,coordinatorPid=coordinator.pid,
    leaseToken=lease['token'],state=lease['state'],modelLoaded=False)))
