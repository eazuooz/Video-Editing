"""Bind actual tool session and close only after observed outer exit and dead worker."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,subprocess
import psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['register','close'],required=True);ap.add_argument('--session',type=int,required=True);ap.add_argument('--completion',required=True);ap.add_argument('--outer-exit',type=int);a=ap.parse_args()
sp=O/'current34-mixed-detailed-render-execution-v1.json';s=rd(sp)
exact=[]
for job in [s]+s['jobs']:
 try:
  p=psutil.Process(job['pid']);alive=p.is_running() and abs(p.create_time()-job['createTime'])<.01
  if alive:assert p.cmdline()==job.get('commandLine',job.get('command')) and Path(p.cwd()).resolve()==ROOT
  exact.append(dict(pid=p.pid,createTime=job['createTime'],exactIdentityAlive=alive,pidAbsent=False))
 except psutil.NoSuchProcess:exact.append(dict(pid=job['pid'],createTime=job['createTime'],exactIdentityAlive=False,pidAbsent=True))
if a.mode=='register':
 ss=sp.with_name(sp.stem+'.session.json');assert not ss.exists()
 cim=subprocess.check_output(['powershell','-NoProfile','-Command',f"Get-CimInstance Win32_Process | Where-Object {{ $_.ProcessId -eq {s['pid']} }} | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json"],text=True,encoding='utf-8',errors='replace')
 write(ss,dict(recordedAt=datetime.now(timezone.utc).isoformat(),sessionId=a.session,pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],cwd=s['cwd'],actualInitialCompletion=a.completion,cimActual=cim,exactIdentityObservations=exact))
 # Live state writer reads this sidecar, preventing concurrent state overwrite.
 cp=rd(O/'latest-checkpoint.json');cp['actualSession']=a.session;cp['ownedJob']['sessionId']=a.session;write(O/'latest-checkpoint.json',cp)
 q=rd(B/'queue.json');q['currentOrientationReview']['actualSession']=a.session;q['currentOrientationReview']['ownedJob']['sessionId']=a.session;write(B/'queue.json',q)
else:
 assert a.outer_exit is not None and not any(x['exactIdentityAlive'] for x in exact)
 s.update(actualOuterExitCode=a.outer_exit,actualSession=a.session,sessionId=a.session,actualCompletion=a.completion,actualExitObserved=True,workerDead=True,exactProcessIdentityObservations=exact,closedAt=datetime.now(timezone.utc).isoformat())
 if a.outer_exit==0:
  assert s['workerExitCode']==0 and len(s['results'])==3
  for row in s['results']:
   assert sha(ROOT/row['output'])==row['outputSha256'] and row['wholeDecodeExitCode']==row['extractExitCode']==0
   for x in row['samples']+row['boards']:assert sha(ROOT/x['path'])==x['sha256']
 proof=rd(O/'narration-07b-guide-repair-execution-v1.json')
 for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
 write(sp,s);cp=rd(O/'latest-checkpoint.json');cp.update(stage=s['status']+'-actual-closed',mixedDetailedExecution=sp.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None,next='Directly inspect all new EX/cut encoded samples and normal1x endpoints; bind reviewed mixed3 to assemblyV3 before pair.')
 write(O/'latest-checkpoint.json',cp);q=rd(B/'queue.json');q['currentOrientationReview'].update(stage=cp['stage'],mixedDetailedExecution=cp['mixedDetailedExecution'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);write(B/'queue.json',q)
print(json.dumps(dict(mode=a.mode,session=a.session,exactWorkerAlive=exact[0]['exactIdentityAlive'],outerExit=a.outer_exit)))
