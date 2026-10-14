"""Bind the overview worker to its actual session and observed outer exit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,os,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,v):
 t=p.with_name(p.name+'.record-writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--session',type=int,required=True);ap.add_argument('--initial');ap.add_argument('--outer-exit',type=int);ap.add_argument('--completion');a=ap.parse_args()
sp=O/'current34-caption-clearance-render-execution-v2.json';ss=O/'current34-caption-clearance-render-execution-v2.session.json';s=rd(sp)
try:
 p=psutil.Process(s['pid']);same=abs(p.create_time()-s['createTime'])<.01
 if same:assert p.cmdline()==s['commandLine'] and p.cwd()==s['cwd']
 alive=same and p.is_running()
except psutil.NoSuchProcess:alive=False
cim=subprocess.check_output(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={s["pid"]}" | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],text=True,encoding='utf-8',errors='replace')
if a.outer_exit is None:
 assert not ss.exists() and a.initial
 save(ss,dict(recordedAt=now(),pid=s['pid'],createTime=s['createTime'],sessionId=a.session,initialChunk=a.initial,commandLine=s['commandLine'],cwd=s['cwd'],workerAliveAtRegistration=alive,cimActual=cim));s['sessionId']=a.session
else:
 assert not alive and s['exitCode']==a.outer_exit and a.completion and rd(ss)['sessionId']==a.session
 proof=rd(O/'narration-07b-guide-repair-execution-v1.json')
 for v in proof['protectedInputs']+proof['results']:assert sha(ROOT/v['path'])==v['sha256']
 if a.outer_exit==0:
  assert len(s['scenes'])==7
  for row in s['scenes']:
   assert row['renderExitCode']==row['wholeDecodeExitCode']==row['extractExitCode']==0 and sha(ROOT/row['output'])==row['outputSha256']
   for v in row['samples']+row['boards']:assert sha(ROOT/v['path'])==v['sha256']
 s.update(actualOuterExitCode=a.outer_exit,actualExitObserved=True,actualSession=a.session,completionChunk=a.completion,workerDead=True,closureObservedAt=now(),all79ProtectedUnchanged=True,closureCimActual=cim)
 cp=rd(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=s['status']+'-actual-closed',activeOwnedWorkers=0,ownedJob=None,next='Review all7 new caption-clearance scenes and current captioned bindings; preserve completed792-board finalV3 review. Resolve07b wing clearance before updated assembly/finalQA.');save(O/'latest-checkpoint.json',cp)
 qp=B/'queue.json';old=qp.read_bytes();q=rd(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==old;save(qp,q)
save(sp,s)
print(json.dumps(dict(session=a.session,alive=alive,outerExit=a.outer_exit,registered=a.outer_exit is None)))
