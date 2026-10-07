"""Record the observed serial correction owner without promoting review gates."""
from pathlib import Path
import datetime, json, psutil

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / 'production/batches/visual-depth-revision'
state = json.loads((BATCH / 'caption-safe-pipeline-hierarchical-game-outlines.json').read_text('utf-8-sig'))
owner = psutil.Process(state['pid'])
command = owner.cmdline()
expected = ['production/batches/visual-depth-revision/run-caption-safe-local.py', *state['scope']]
if command[1:] != expected:
    raise RuntimeError('Current command identity must match the authorized five-video scope')
record = dict(sessionId=34487, pid=owner.pid, createTime=owner.create_time(), command=command,
              checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              execution='production/batches/visual-depth-revision/caption-safe-pipeline-hierarchical-game-outlines.json')
queue_path = BATCH / 'queue.json'
queue = json.loads(queue_path.read_text('utf-8-sig'))
queue['remainingCaptionSafeSession'] = record
for item in queue['items']:
    if item['slug'] in state['scope']:
        item['pipelineSessionRecord'] = record
queue['historicalResourceObservation'] = queue.pop('currentResourceObservation', None)
queue['currentResourceObservation'] = state['resourceObservation']
queue['updatedAt'] = record['checkedAt']
queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('Observed five-video serial CPU owner/session recorded; no final review or upload approved')
