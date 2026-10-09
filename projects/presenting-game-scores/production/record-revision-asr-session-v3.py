from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
ap=argparse.ArgumentParser();ap.add_argument('--mode',required=True);ap.add_argument('--session-id',type=int,required=True);ap.add_argument('--outer-exit-code',type=int);a=ap.parse_args()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,j):
 t=p.with_name(p.name+'.session-writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
sp=BASE/f'voice-{a.mode}-asr-execution-v3.json';s=read(sp);p=None
try:
 candidate=psutil.Process(s['actualPid'])
 if abs(candidate.create_time()-s['createTime'])<.01:p=candidate
except psutil.NoSuchProcess:pass
target=BASE/f'voice-{a.mode}-asr-session-v3.json';stamp=datetime.now(timezone.utc).isoformat()
if a.outer_exit_code is None:
 assert p and s['exitCode'] is None and not target.exists()
 j=dict(schemaVersion=1,observedAt=stamp,mode=a.mode,sessionId=a.session_id,pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),state=sp.relative_to(ROOT).as_posix(),workerExpectedRunning=True,actualOuterExitCode=None,cpuThreads=2,gpuJobs=0)
else:
 assert a.outer_exit_code==s['exitCode'] and not p
 j=read(target) if target.exists() else dict(schemaVersion=1,mode=a.mode,sessionId=a.session_id,pid=s['actualPid'],createTime=s['createTime'],command=s['commandLine'],cwd=s['cwd'],state=sp.relative_to(ROOT).as_posix(),cpuThreads=2,gpuJobs=0)
 assert j['sessionId']==a.session_id;j.update(workerExpectedRunning=False,actualOuterExitCode=a.outer_exit_code,actualExitObservedAt=stamp)
 s.update(actualExitObserved=True,actualOuterExitCode=a.outer_exit_code,actualOuterSession=a.session_id,actualExitObservedAt=stamp);save(sp,s)
save(target,j);print(json.dumps(dict(mode=a.mode,sessionId=a.session_id,pid=j['pid'],actualOuterExitCode=a.outer_exit_code,workerExpectedRunning=j['workerExpectedRunning'])))
