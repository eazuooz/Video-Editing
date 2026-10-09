"""Record actual decoder session/liveness/exit; never control processes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,psutil,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
ap=argparse.ArgumentParser();ap.add_argument('--session-id',type=int,required=True);ap.add_argument('--outer-exit-code',type=int);a=ap.parse_args()
sp=BASE/'voice-decoding-asr-execution-v2.json';state=json.loads(sp.read_text('utf-8-sig'));dest=sp.with_name(sp.stem+'.session.json')
if a.outer_exit_code is None:
 assert state['exitCode'] is None and not dest.exists()
 p=psutil.Process(state['pid']);assert abs(p.create_time()-state['createTime'])<.01 and p.cwd().lower()==str(ROOT).lower()
 assert 'review-revision-voice-decoding-v2.py' in ' '.join(p.cmdline())
 cim=subprocess.run(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={p.pid}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
 j=dict(schemaVersion=2,observedAt=datetime.now(timezone.utc).isoformat(),pid=p.pid,createTime=p.create_time(),sessionId=a.session_id,processIdentity=dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd()),cimObservation=json.loads(cim.stdout),cpuThreads=2,gpuJobs=0,workerExpectedRunning=True,actualExitObserved=False,exitCode=None,processOrControlChanges=0)
else:
 j=json.loads(dest.read_text('utf-8-sig'));assert j['sessionId']==a.session_id and state['exitCode']==a.outer_exit_code
 if psutil.pid_exists(state['pid']):assert abs(psutil.Process(state['pid']).create_time()-state['createTime'])>.01,'Actual decoder still alive'
 j.update(actualExitObserved=True,exitCode=a.outer_exit_code,workerExpectedRunning=False,closedAt=datetime.now(timezone.utc).isoformat())
 state.update(actualExitObserved=True,actualOuterExitCode=a.outer_exit_code,sessionId=a.session_id);sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
dest.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:j[k] for k in ['pid','createTime','sessionId','workerExpectedRunning','exitCode']}))
