"""Record the actual live beam diagnostic exec session, without process control."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,psutil,subprocess
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--session-id',type=int,required=True);a=ap.parse_args()
sp=BASE/'localized-decoding-asr-execution-v5.json';state=json.loads(sp.read_text('utf-8-sig'));assert state['exitCode'] is None
p=psutil.Process(state['pid']);assert abs(p.create_time()-state['createTime'])<.01 and p.cwd().lower()==str(ROOT).lower()
assert 'review-localized-decoding-v5.py' in ' '.join(p.cmdline())
dest=sp.with_name(sp.stem+'.session.json');assert not dest.exists()
cim=subprocess.run(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={p.pid}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
dest.write_text(json.dumps(dict(schemaVersion=1,observedAt=datetime.now(timezone.utc).isoformat(),pid=p.pid,createTime=p.create_time(),sessionId=a.session_id,
 processIdentity=dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd()),cimObservation=json.loads(cim.stdout),
 cpuThreads=2,gpuJobs=0,workerExpectedRunning=True,actualExitObserved=False,exitCode=None,processOrControlChanges=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(pid=p.pid,createTime=p.create_time(),sessionId=a.session_id)))
