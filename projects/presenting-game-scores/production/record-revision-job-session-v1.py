"""Bind a real tool session to actual PID/creation/cmd, or seal its observed exit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,psutil,os
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('--state',required=True);ap.add_argument('--record-path',required=True);ap.add_argument('--session-id',required=True,type=int);ap.add_argument('--outer-exit-code',type=int);a=ap.parse_args()
p=ROOT/a.state;dst=ROOT/a.record_path;s=json.loads(p.read_text('utf-8-sig'));pid=s.get('pid',s.get('actualPid'));ctime=s['createTime']
try:
 q=psutil.Process(pid);alive=abs(q.create_time()-ctime)<.01
except psutil.NoSuchProcess:q=None;alive=False
stamp=datetime.now(timezone.utc).isoformat()
if a.outer_exit_code is None:
 assert alive and s['exitCode'] is None and not dst.exists()
 j=dict(pid=pid,createTime=ctime,sessionId=a.session_id,recordedAt=stamp,command=q.cmdline(),cwd=q.cwd(),liveIdentityObserved=True,workerExpectedRunning=True,exitCode=None,actualOuterExitCode=None)
else:
 assert not alive and s['exitCode']==a.outer_exit_code
 j=json.loads(dst.read_text('utf-8-sig')) if dst.exists() else dict(pid=pid,createTime=ctime,sessionId=a.session_id)
 assert j['sessionId']==a.session_id
 j.update(exitCode=a.outer_exit_code,actualOuterExitCode=a.outer_exit_code,workerExpectedRunning=False,actualExitObserved=True,actualExitObservedAt=stamp)
 s.update(sessionId=a.session_id,outerExitCode=a.outer_exit_code,actualOuterExitCode=a.outer_exit_code,outerExitDirectlyObserved=True,actualExitObserved=True,actualExitObservedAt=stamp)
 tmp=p.with_suffix('.session-writing');tmp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
dst.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(pid=pid,sessionId=a.session_id,alive=alive,actualOuterExitCode=a.outer_exit_code)))
