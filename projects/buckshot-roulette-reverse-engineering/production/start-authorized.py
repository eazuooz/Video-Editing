"""Record the user's explicit start without changing unrelated production scopes."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/buckshot-roulette-reverse-engineering'
now = datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

p = read(PROJECT / 'project.json')
p['status'] = 'active-local-analysis-and-capture'
p['startGate'].update(productionAllowedNow=True, satisfiedBy='응 진행해줘~', satisfiedOn='2026-10-29', scheduled=False)
write(PROJECT / 'project.json', p)
c = read(PROJECT / 'production/checkpoint.json')
c.update(updatedAt=now, stage='active-local-analysis-and-capture')
c['startGate'].update(productionAllowedNow=True, reason='2026-10-29 explicit user: 응 진행해줘~')
c['inProgress'] = ['OBS short recording verification', 'REA read-only package inspection and timestamped evidence']
write(PROJECT / 'production/checkpoint.json', c)
control_path = ROOT / 'shared/publishing/video-production-control.json'
control = read(control_path)
control.setdefault('scopedSetupAuthorizations', {})[p['slug']] = {
    'scope': p['scope'], 'status': p['status'], 'userEvidence': '응 진행해줘~',
    'authorizedOn': '2026-10-29', 'productionAllowedNow': True,
    'automaticStart': False, 'automationCreated': False, 'projectPath': str(PROJECT.relative_to(ROOT)).replace('\\', '/'),
    'boundary': 'One local documentary review; no uploads, publishing, schedules, original install/save changes or unrelated work.'
}
write(control_path, control)
print('Explicit start recorded for ' + p['slug'])
