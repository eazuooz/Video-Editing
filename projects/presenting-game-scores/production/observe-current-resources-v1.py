"""Read real process identities/resources before a single owned CPU job.

Static preview servers are listed separately. This observer never controls a
process, GPU lease, research queue or pause file.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
ap = argparse.ArgumentParser()
ap.add_argument('--output', required=True)
args = ap.parse_args()
destination = (ROOT / args.output).resolve()
assert destination.parent == BASE and not destination.exists()
tracked = []
for name in ['narration-tts-execution-v1.json', 'current-whole-asr-execution-v1.json',
             'current-contexts-asr-execution-v1.json', 'current-targets-asr-execution-v1.json']:
    path = BASE / name
    if not path.exists():
        continue
    state = read(path)
    identity = state.get('processIdentity') or {}
    pid = state.get('actualPid', state.get('pid'))
    created = state.get('createTime', identity.get('createTime'))
    assert pid and created is not None, f'Actual creation time required for {name}'
    try:
        process = psutil.Process(pid)
        same = abs(process.create_time() - created) < .01
        alive = same and process.is_running()
        observation = dict(pid=pid, createTime=created, alive=alive,
                           pidReused=not same, command=process.cmdline() if same else None)
    except psutil.NoSuchProcess:
        observation = dict(pid=pid, createTime=created, alive=False, pidReused=False)
    tracked.append(dict(state=name, recordedExitCode=state.get('exitCode'), **observation))

inventory = []
unexpected_owned = []
for process in psutil.process_iter(['pid', 'name', 'create_time', 'cmdline']):
    try:
        data = process.info
        command = data['cmdline'] or []
        text = ' '.join(command).lower()
        name = (data['name'] or '').lower()
        if not any(part in name for part in ['python', 'ffmpeg', 'node']):
            continue
        preview = ('serve-native-review-v1.py' in text or
                   'vite.presenting-game-scores.black-preflight-v1.config.ts' in text)
        own = 'presenting-game-scores' in text
        row = dict(pid=data['pid'], name=data['name'], createTime=data['create_time'],
                   command=command, ownProject=own, staticPreview=preview)
        inventory.append(row)
        if own and not preview and data['pid'] != os.getpid() and not any(
                item['pid'] == data['pid'] and item['alive'] for item in tracked):
            unexpected_owned.append(row)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue
gpu = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.free,utilization.gpu',
                      '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True)
cpu = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory()
request = read(BASE / 'narration-tts-request-v1.json')
protected = []
for item in request['protectedInputs']:
    if item['path'].endswith('/project.json'):
        continue
    digest = hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
    assert digest == item['sha256'], item['path']
    protected.append(dict(path=item['path'], sha256=digest))
proof = dict(schemaVersion=1, slug='presenting-game-scores',
             observedAt=datetime.now(timezone.utc).isoformat(),
             ownHeavyJobs=sum(item['alive'] for item in tracked) + len(unexpected_owned),
             trackedJobs=tracked, unexpectedOwnedJobs=unexpected_owned,
             cpuLoadPercent=cpu, freePhysicalMemoryKiB=memory.available // 1024,
             gpuCsv=gpu.stdout.strip(), processInventory=inventory,
             protectedContentHashesMatched=protected, processOrControlChanges=0)
destination.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({key: proof[key] for key in ['observedAt', 'ownHeavyJobs',
                                           'cpuLoadPercent', 'freePhysicalMemoryKiB', 'gpuCsv']},
                 ensure_ascii=False))
