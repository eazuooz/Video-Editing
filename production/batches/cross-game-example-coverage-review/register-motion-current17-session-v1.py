"""Register an actual live session with exact worker command/create/cwd identity."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os
import psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
ap=argparse.ArgumentParser();ap.add_argument('--state',required=True);ap.add_argument('--session',type=int,required=True);ap.add_argument('--initial',required=True);a=ap.parse_args()
sp=ROOT/a.state;state=json.loads(sp.read_text('utf-8-sig'));p=psutil.Process(state['pid'])
assert abs(p.create_time()-state['createTime'])<.01 and p.cmdline()==state['commandLine'] and p.cwd()==state['cwd']
ss=sp.with_name(sp.stem+'.session.json');assert not ss.exists()
v=dict(pid=p.pid,createTime=p.create_time(),sessionId=a.session,actualInitialChunk=a.initial,actualOuterExitCode=None,workerCurrentlyAlive=True,registeredAt=datetime.now(timezone.utc).isoformat(),commandLine=p.cmdline(),cwd=p.cwd())
t=ss.with_name(ss.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,ss)
print(json.dumps(dict(pid=p.pid,createTime=p.create_time(),sessionId=a.session,actualCurrentlyAlive=True)))
