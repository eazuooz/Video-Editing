"""Register an actual live wrapper session and process identity without relaunch."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--session',type=int,required=True);ap.add_argument('--initial',required=True);a=ap.parse_args()
s=read(O/'02aext-tracked-render-execution-v1.json');p=psutil.Process(s['pid']);assert abs(p.create_time()-s['createTime'])<.001 and p.cmdline()==s['commandLine'] and p.cwd()==s['cwd']
cim=subprocess.check_output(['powershell','-NoProfile','-Command',f"Get-CimInstance Win32_Process -Filter 'ProcessId={p.pid}' | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json"],text=True,encoding='utf-8',errors='replace')
reg=O/'02aext-tracked-render-execution-v1.session.json';assert not reg.exists();save(reg,dict(registeredAt=datetime.now(timezone.utc).isoformat(),actualSession=a.session,initialChunk=a.initial,pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),cimActual=cim,actualExitObserved=False))
qp=B/'queue.json';before=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(actualSession=a.session,activeOwnedWorkers=1,ownedJob=dict(actualSession=a.session,pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),state='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/02aext-tracked-render-execution-v1.json',next='Actual outer exit, exact worker death and all encoded samples before mix.'));assert before==qp.read_bytes();save(qp,q)
print(json.dumps(dict(actualSession=a.session,pid=p.pid,createTime=p.create_time(),exactIdentityVerified=True)))
