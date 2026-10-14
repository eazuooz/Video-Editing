"""Record the observed shell session without rewriting the live render state."""
from pathlib import Path
from datetime import datetime, timezone
import json, os, psutil, subprocess
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
s=read(O/'07b-tracked-render-execution-v2.json');p=psutil.Process(s['pid'])
assert abs(p.create_time()-s['createTime'])<.001 and p.cmdline()==s['commandLine'] and p.cwd()==s['cwd']
cim=subprocess.check_output(['powershell','-NoProfile','-Command',f"Get-CimInstance Win32_Process -Filter 'ProcessId={p.pid}' | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json"],text=True,encoding='utf-8',errors='replace')
reg=O/'07b-tracked-render-execution-v2.session.json';assert not reg.exists()
save(reg,dict(registeredAt=datetime.now(timezone.utc).isoformat(),actualSession=11557,initialChunk='505ae4',pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),cimActual=cim,actualExitObserved=False))
qp=B/'queue.json';before=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(actualSession=11557,activeOwnedWorkers=1,ownedJob=dict(actualSession=11557,pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),state='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/07b-tracked-render-execution-v2.json',next='Observe actual outer exit, then verify exact worker death and encoded samples.'))
assert before==qp.read_bytes();save(qp,q)
print(json.dumps(dict(actualSession=11557,pid=p.pid,exactIdentityVerified=True)))
