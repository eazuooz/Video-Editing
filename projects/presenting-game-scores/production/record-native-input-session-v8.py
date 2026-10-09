from pathlib import Path
from datetime import datetime,timezone
import argparse,json,psutil,subprocess
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--session-id',type=int,required=True);a=ap.parse_args()
p=BASE/'measured-native-inputs-execution-v8.json';d=json.loads(p.read_text('utf-8-sig'))
w=psutil.Process(d['pid']);assert abs(w.create_time()-d['createTime'])<.01
assert 'build-measured-native-inputs-v8.py' in ' '.join(w.cmdline()) and w.cwd().lower()==str(ROOT).lower()
cim=subprocess.run(['powershell','-NoProfile','-Command',
 f'Get-CimInstance Win32_Process -Filter "ProcessId={w.pid}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json'],
 capture_output=True,text=True,encoding='utf-8',check=True)
record=dict(observedAt=datetime.now(timezone.utc).isoformat(),sessionId=a.session_id,
 pid=w.pid,createTime=w.create_time(),processIdentity=dict(pid=w.pid,createTime=w.create_time(),commandLine=w.cmdline(),cwd=w.cwd()),
 cimObservation=json.loads(cim.stdout),state=p.relative_to(ROOT).as_posix(),actualExitObserved=False,
 exitCode=None,workerExpectedRunning=True,cpuThreads=2,gpuJobs=0,processOrControlChanges=0)
target=p.with_name(p.stem+'.session.json');assert not target.exists()
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(pid=w.pid,createTime=w.create_time(),sessionId=a.session_id,completed=d['completed'])))
