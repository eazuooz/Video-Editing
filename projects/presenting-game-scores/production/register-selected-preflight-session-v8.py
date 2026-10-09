from pathlib import Path
from datetime import datetime,timezone
import json,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
p=BASE/'selected-input-preflight-execution-v8.json';j=json.loads(p.read_text('utf-8'));proc=psutil.Process(j['pid'])
assert proc.is_running() and abs(proc.create_time()-j['createTime'])<.01
assert 'build-selected-input-preflight-v8.py' in ' '.join(proc.cmdline()) and proc.cwd().lower()==str(ROOT).lower()
dst=BASE/'selected-input-preflight-execution-v8.session.json';assert not dst.exists()
record=dict(pid=proc.pid,createTime=proc.create_time(),sessionId=38215,recordedAt=datetime.now(timezone.utc).isoformat(),processIdentity=dict(command=proc.cmdline(),cwd=proc.cwd()),liveIdentityObserved=True,exitCode=None,actualExitObserved=False)
dst.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(pid=proc.pid,createTime=proc.create_time(),sessionId=38215,alive=True)))
