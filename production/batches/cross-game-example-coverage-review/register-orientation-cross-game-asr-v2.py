"""Register the actual outer session against the current worker identity."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib, subprocess, psutil, os
ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
R = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
ap = argparse.ArgumentParser()
ap.add_argument('--mode', choices=['whole','contexts'], required=True)
ap.add_argument('--session', type=int, required=True)
args = ap.parse_args()
read = lambda p: json.loads(p.read_text('utf-8-sig'))
statepath = R / f'cross-game-{args.mode}-asr-execution-v2.json'
state = read(statepath)
proc = psutil.Process(state['pid'])
assert abs(proc.create_time() - state['createTime']) < .01
assert proc.cmdline() == state['commandLine'] and proc.cwd() == state['cwd']
assert 'review-orientation-cross-game-voice-v2.py' in ' '.join(proc.cmdline())
sessionpath = statepath.with_name(statepath.stem + '.session.json')
assert not sessionpath.exists()
now = datetime.now(timezone.utc).isoformat()
cim = subprocess.check_output(['powershell', '-NoProfile', '-Command',
    f'Get-CimInstance Win32_Process -Filter "ProcessId={proc.pid}" | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],
    text=True, encoding='utf-8', errors='replace')
record = dict(registeredAt=now, sessionId=args.session, mode=args.mode,
    pid=proc.pid, createTime=proc.create_time(), commandLine=proc.cmdline(),
    cwd=proc.cwd(), actualCim=cim, cpuThreads=2, gpuJobs=0,
    state=statepath.relative_to(ROOT).as_posix(),
    log=(R / f'cross-game-{args.mode}-asr-v2.log').relative_to(ROOT).as_posix(),
    exitCode=None, processControlChanges=0)
sessionpath.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
qp = B / 'queue.json'
raw = qp.read_bytes()
queue = read(qp)
queue['currentOrientationReview'].update(stage=f'cross-game5PCM-{args.mode}-ASR-running',
    actualSession=args.session, ownedJob=record, activeOwnedWorkers=1,
    next='Reuse current actual session/PID/create. After outer exit record closure; directly compare full current text. No duplicate model worker.')
queue['updatedAt'] = now
assert qp.read_bytes() == raw
temp = qp.with_name(qp.name + f'.orientation-register-{os.getpid()}.writing')
temp.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + '\n', 'utf-8')
os.replace(temp, qp)
print(json.dumps(dict(session=args.session, pid=proc.pid, createTime=proc.create_time(),
    mode=args.mode, cpuThreads=2, gpuJobs=0, currentIdentityVerified=True)))
