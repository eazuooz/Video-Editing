"""Attach an actual exec session to the already-running owned CPU worker."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, subprocess, psutil

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
ap = argparse.ArgumentParser()
ap.add_argument('--mode', choices=['whole', 'contexts', 'targets'], required=True)
ap.add_argument('--session-id', type=int, required=True)
args = ap.parse_args()
state_path = BASE / f'localized-voice-repair-{args.mode}-asr-execution-v4.json'
state = json.loads(state_path.read_text('utf-8-sig'))
assert state['exitCode'] is None and state['mode'] == args.mode
process = psutil.Process(state['pid'])
assert abs(process.create_time() - state['createTime']) < .01
assert 'review-localized-voice-repair-v4.py' in ' '.join(process.cmdline())
assert process.cwd().lower() == str(ROOT).lower()
session_path = state_path.with_name(state_path.stem + '.session.json')
assert not session_path.exists(), 'Preserve the recorded session; inspect it instead.'
cim = subprocess.run(['powershell', '-NoProfile', '-Command',
    f'Get-CimInstance Win32_Process -Filter "ProcessId={process.pid}" | '
    'Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],
    capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
assert cim.stdout.strip()
record = dict(schemaVersion=1, observedAt=datetime.now(timezone.utc).isoformat(),
    pid=process.pid, createTime=process.create_time(), sessionId=args.session_id,
    processIdentity=dict(pid=process.pid, createTime=process.create_time(),
                         commandLine=process.cmdline(), cwd=process.cwd()),
    cimObservation=json.loads(cim.stdout), state=state_path.relative_to(ROOT).as_posix(),
    mode=args.mode, cpuThreads=2, gpuJobs=0, workerExpectedRunning=True,
    actualExitObserved=False, exitCode=None, processOrControlChanges=0)
session_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps(dict(pid=process.pid, createTime=process.create_time(),
                     sessionId=args.session_id, mode=args.mode)))
