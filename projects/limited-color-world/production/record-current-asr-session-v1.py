"""Record an observed tool session against its actual worker identity."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, psutil
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--mode', choices=['whole','contexts','targets'], required=True)
ap.add_argument('--session-id', type=int, required=True)
ap.add_argument('--pid', type=int, required=True)
ap.add_argument('--create-time', type=float, required=True)
args = ap.parse_args()
state_path = BASE/f'current-{args.mode}-asr-execution-v1.json'
state = json.loads(state_path.read_text('utf-8-sig'))
assert state['pid'] == args.pid and abs(state['createTime']-args.create_time) < .01
p = psutil.Process(args.pid)
assert abs(p.create_time()-args.create_time) < .01
assert 'review-current-voice-v1.py' in ' '.join(p.cmdline()) and args.mode in p.cmdline()
assert Path(p.cwd()).resolve() == ROOT.resolve()
dest = state_path.with_name(state_path.stem+'.session.json')
assert not dest.exists()
data = dict(recordedAt=datetime.now(timezone.utc).isoformat(),sessionId=args.session_id,pid=p.pid,
    processIdentity=dict(pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd()),
    proxyPid=p.ppid(),state=state_path.relative_to(ROOT).as_posix(),
    sourceWorkerSha256=hashlib.sha256((BASE/'review-current-voice-v1.py').read_bytes()).hexdigest(),
    actualExitObserved=False)
tmp=dest.with_name(dest.name+f'.{os.getpid()}.writing')
tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8'); os.replace(tmp,dest)
print(json.dumps(data,ensure_ascii=False))
