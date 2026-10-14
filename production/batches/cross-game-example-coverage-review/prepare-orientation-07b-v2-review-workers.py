"""Record real completed V2 session, then prepare closure and encoded QA workers."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
s=read(O/'07b-tracked-render-execution-v2.json');assert s['workerExitCode']==0
try:assert abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.001
except psutil.NoSuchProcess:pass
reg=O/'07b-tracked-render-execution-v2.session.json';assert not reg.exists()
reg.write_text(json.dumps(dict(registeredAt=datetime.now(timezone.utc).isoformat(),actualSession=11557,initialChunk='505ae4',actualCompletion='edffdb',actualOuterExitCode=0,pid=s['pid'],createTime=s['createTime'],command=s['commandLine'],cwd=s['cwd'],workerDead=True,liveRegistrationAttempt=dict(chunk='7746d5',exitCode=1,reason='Render completed before live registration; no worker restart.'),actualExitObserved=True),ensure_ascii=False,indent=2)+'\n','utf-8')
src=(B/'record-orientation-07b-worker-exit-v2.py').read_text('utf-8-sig').replace("{a.mode}-execution-v1.json","{a.mode}-execution-v2.json").replace("exitRecorderVersion=2","exitRecorderVersion=3").replace("priorRecorderFailure=dict(chunk='5724cd',actualExitCode=1,reason='V1 PID-only child absence assertion; no output or protected file mutation')","priorRecorderFailure=None")
out=B/'record-orientation-07b-worker-exit-v3.py';assert not out.exists();out.write_text(src,'utf-8')
src=(B/'extract-orientation-07b-tracked-pixels-v1.py').read_text('utf-8-sig').replace('pixels-execution-v1','pixels-execution-v2').replace('render-execution-v1','render-execution-v2')
out=B/'extract-orientation-07b-tracked-pixels-v2.py';assert not out.exists();out.write_text(src,'utf-8')
print(json.dumps(dict(actualSession=11557,outerExit=0,completion='edffdb',registrationAfterCompletion=True,newRenderStarted=False)))
