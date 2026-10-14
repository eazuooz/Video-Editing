"""Associate the observed ASR tool session with its actual process identity."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, psutil
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--mode',choices=['whole','contexts','targets'],required=True)
ap.add_argument('--session-id',type=int,required=True)
args=ap.parse_args()
sp=BASE/f'causal-bridge-{args.mode}-asr-execution-v1.json'
state=json.loads(sp.read_text('utf-8-sig')); p=psutil.Process(state['pid'])
assert abs(p.create_time()-state['createTime'])<.01
assert 'review-causal-bridge-voice-v1.py' in ' '.join(p.cmdline()) and args.mode in p.cmdline()
assert Path(p.cwd()).resolve()==ROOT
dest=sp.with_name(sp.stem+'.session.json'); assert not dest.exists()
data=dict(recordedAt=datetime.now(timezone.utc).isoformat(),sessionId=args.session_id,pid=p.pid,
 processIdentity=dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd()),proxyPid=p.ppid(),
 state=sp.relative_to(ROOT).as_posix(),sourceWorkerSha256=hashlib.sha256((BASE/'review-causal-bridge-voice-v1.py').read_bytes()).hexdigest(),actualExitObserved=False)
tmp=dest.with_name(dest.name+f'.{os.getpid()}.writing')
tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8'); os.replace(tmp,dest)
print(json.dumps(data,ensure_ascii=False))
