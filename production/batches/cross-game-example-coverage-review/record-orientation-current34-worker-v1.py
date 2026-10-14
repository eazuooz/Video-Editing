"""Register a returned actual session, or seal the observed actual exit; never infer exit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,x):
 t=p.with_name(p.name+'.record-writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['mix','whole','contexts'],required=True);ap.add_argument('--session',type=int);ap.add_argument('--initial');ap.add_argument('--outer-exit',type=int);ap.add_argument('--completion');a=ap.parse_args()
name='current34-mix-execution-v2' if a.mode=='mix' else f'current34-mixed-{a.mode}-asr-execution-v1'
sp=O/(name+'.json');s=read(sp)
try:
 p=psutil.Process(s['pid']);same=abs(p.create_time()-s['createTime'])<.01
 if same:assert p.cmdline()==s['commandLine'] and p.cwd()==s['cwd']
 alive=same and p.is_running()
except psutil.NoSuchProcess:alive=False
cim=subprocess.check_output(['powershell','-NoProfile','-Command',f"Get-CimInstance Win32_Process | Where-Object {{ $_.ProcessId -eq {s['pid']} }} | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
sessionp=O/(name+'.session.json')
if a.outer_exit is None:
 assert a.session is not None and a.initial and not sessionp.exists()
 record=dict(recordedAt=now(),pid=s['pid'],createTime=s['createTime'],sessionId=a.session,initialChunk=a.initial,commandLine=s['commandLine'],cwd=s['cwd'],workerAliveAtRegistration=alive,cimActual=cim)
 save(sessionp,record);s['sessionId']=a.session
 print(json.dumps(dict(registered=True,session=a.session,workerAliveAtRegistration=alive,pid=s['pid'],createTime=s['createTime'])))
else:
 assert a.completion and not alive
 code=s.get('actualExitCode',s.get('exitCode'));assert code==a.outer_exit
 if sessionp.exists():assert read(sessionp)['sessionId']==a.session
 proof=read(O/'narration-07b-guide-repair-execution-v1.json')
 for r in proof['protectedInputs']+proof['results']:assert sha(ROOT/r['path'])==r['sha256']
 if a.outer_exit==0:
  if a.mode=='mix':
   assert s['all34RawPcmPlacementsExact'] and s['all24BaselineDistributedPcmExact']
   assert all(r['exitCode']==0 for r in s['subprocesses'])
   for r in s['files']:assert sha(ROOT/r['path'])==r['sha256']
  else:
   assert s['completed']==s['total'] and len(s['results'])==s['total']
 s.update(actualOuterExitCode=a.outer_exit,actualExitObserved=True,completionChunk=a.completion,actualSession=a.session,workerDead=True,closureObservedAt=now(),all79ProtectedInputsUnchanged=True,closureCimActual=cim)
 cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=now(),activeOwnedWorkers=0,ownedJob=None,stage=s['status']+'-actual-closed',next='Directly compare current34 mixed narration, then independent complete contexts and final caption/pixel review. No final delivery/settings approval.');save(O/'latest-checkpoint.json',cp)
 qp=B/'queue.json';old=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==old;save(qp,q)
 print(json.dumps(dict(actualExit=a.outer_exit,workerDead=True,protected79=True,session=a.session)))
save(sp,s)
