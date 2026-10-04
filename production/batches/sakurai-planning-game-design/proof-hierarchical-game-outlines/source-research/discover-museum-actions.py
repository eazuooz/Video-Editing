"""Sequential read-only discovery. Frames are not final cut approvals."""
import argparse, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--pass-name', choices=['discovery', 'action'], default='discovery')
args = parser.parse_args()
state_path = BASE / ('museum-' + args.pass_name + '.json')
windows = [
    ('drop-ride', 2135, 2210, 3),
    ('coaster-first', 2580, 2950, 5),
    ('coaster-followup', 2970, 3335, 5),
    ('staff-route', 3440, 3560, 3),
    ('new-ride-queue', 4600, 4880, 4),
]
if args.pass_name == 'action':
    windows = [
        ('segment-action-a', 2594, 2692, 1),
        ('segment-action-b', 2692, 2824, 1),
        ('segment-action-c', 2996, 3078, 1),
        ('segment-action-d', 3136, 3284, 1),
        ('ride-placement-action', 2177, 2206, 1),
        ('queue-decoration-action', 4600, 4758, 2),
    ]
stamp = lambda: datetime.now(timezone.utc).isoformat()
state = {'pid': os.getpid(), 'startedAt': stamp(), 'status': 'running', 'gpuJobs': 0, 'children': [], 'finalCutApproval': False}
def save():
    state['updatedAt'] = stamp()
    state_path.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')

print('discovery PID', os.getpid(), flush=True)
save()
try:
    for label, start, end, step in windows:
        output = BASE / 'frames' / ('I-ccSZ5J1Bo-' + label) / 'index.json'
        if output.exists():
            old = json.loads(output.read_text(encoding='utf-8'))
            if old.get('exitCode') != 0: raise RuntimeError('Existing failed extraction requires review')
            state['children'].append({'label': label, 'status': 'reused-finished-extraction', 'index': str(output), 'frameCount': old['frameCount']})
            save()
            continue
        command = [sys.executable, str(BASE / 'inspect-source-actions.py'), 'I-ccSZ5J1Bo', '--step', str(step), '--start', str(start), '--end', str(end), '--label', label, '--seek-overview']
        child = subprocess.Popen(command)
        record = {'label': label, 'pid': child.pid, 'startedAt': stamp(), 'status': 'running', 'start': start, 'end': end, 'step': step}
        state['children'].append(record)
        save()
        code = child.wait()
        record.update(exitCode=code, endedAt=stamp(), status='finished' if code == 0 else 'failed')
        save()
        if code: raise RuntimeError('Discovery failed: ' + label)
    state['status'] = 'finished-awaiting-direct-review'
    state['endedAt'] = stamp()
    save()
except Exception as error:
    state.update(status='failed', error=str(error), endedAt=stamp())
    save()
    raise
