"""Observe the owned acquisition without restarting it or touching research."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil

ROOT = Path(__file__).resolve().parents[3]
read = lambda p: json.loads(p.read_text('utf-8-sig'))

def write(p, value):
    temp = p.with_name(p.name + '.writing-' + str(os.getpid()))
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    temp.replace(p)

execution = ROOT / 'production/research/game-lighting-history/local/episode04-additional-action-v47/execution.json'
state = read(execution)
worker = None
try:
    process = psutil.Process(state['parentPid'])
    command = process.cmdline()
    if any('acquire-episode04-additional-action-v47.cjs' in arg for arg in command):
        worker = {'pid': process.pid, 'createTime': process.create_time(), 'commandLine': command, 'cwd': process.cwd()}
except psutil.NoSuchProcess:
    pass
observation = {
    'observedAt': datetime.now(timezone.utc).isoformat(),
    'execution': execution.relative_to(ROOT).as_posix(),
    'executionSha256': hashlib.sha256(execution.read_bytes()).hexdigest(),
    'sessionId': 30231, 'status': state['status'], 'actualWorkerAlive': worker is not None,
    'worker': worker, 'current': state.get('current'), 'completed': len(state['completed']),
    'cpuThreads': 2, 'gpuJobs': 0, 'logDirectory': execution.parent.relative_to(ROOT).as_posix(),
    'sourceAudioAcquired': False, 'finalUseApproved': False, 'newTtsStarted': False,
    'next': 'Read acquired native candidates and approve exact normal-speed action ranges; finish current duplicate review and minimum-four-game comparison coverage, then synthesize only new guides/framing via cooperative GPU handoff.'
}
target = ROOT / 'projects/game-lighting-history-04/production/additional-action-progress-v47.json'
write(target, observation)
checkpoint = ROOT / 'production/research/game-lighting-history/checkpoint.json'
value = read(checkpoint)
value['episode04AdditionalActionV47'] = observation
value['ownedActiveWork'] = {**observation, 'type': 'single-CPU-source-acquisition' if worker else 'source-review', 'ownedMediaWorkersRunning': int(worker is not None), 'ownedGpuWorkersRunning': 0}
value['updatedAt'] = observation['observedAt']
value['nextAction'] = observation['next']
write(checkpoint, value)
print(json.dumps({'status': state['status'], 'pid': state['parentPid'], 'alive': worker is not None, 'completed': len(state['completed']), 'current': state.get('current', {}).get('label') if state.get('current') else None}))
