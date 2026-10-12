"""Resolve an explicit metadata/source delivery list, without staging foreign changes."""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
O = 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
B = 'production/batches/cross-game-example-coverage-review'
EXTENSIONS = {'.json', '.py', '.cjs', '.ts', '.tsx', '.meta', '.md', '.txt', '.srt', '.ass', '.svg'}

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def own(path):
    f = path.replace('\\', '/')
    p = Path(f)
    return (p.suffix in EXTENSIONS and '/ui-proof-v1/' not in f
            and not f.endswith(('.ax.txt', '.dom.txt')) and not p.name.startswith('local-original-')
            and not f.endswith('info.json')
            and (f.startswith('projects/game-math-orientation-matrices/')
                 or f.startswith('manim/projects/game-math-orientation-matrices/')
                 or f.startswith('motion-canvas/src/projects/game-math-orientation-matrices/')
                 or (f.startswith(B + '/') and 'orientation' in p.name)))

selected = set()
todo = [
    'projects/game-math-orientation-matrices/project.json',
    'projects/game-math-orientation-matrices/rebuild.json',
    'projects/game-math-orientation-matrices/production/delivery-output.json',
    O + '/latest-checkpoint.json', O + '/current34-main-private-update-v1.json',
    O + '/current34-main-promotion-v1.json', O + '/current34-final-technical-and-pixel-direct-review-v5.json',
    O + '/current34-four-output-collection-verification-v1.json',
    O + '/publishing/private-settings-direct-review-v1.json', O + '/publishing/youtube-upload-v1.json',
    O + '/publishing/metadata-text-plan-v1.json', O + '/publishing/upload-description.ko.txt',
    O + '/publishing/upload-description.en.txt', O + '/publishing/pinned-comment.ko.txt',
    O + '/publishing/git-preflight-rebuild-v1.json',
    B + '/seal-orientation-current34-private-v1.py', B + '/plan-orientation-current34-git-v1.py',
    B + '/deliver-orientation-current34-private-v1.cjs',
]
missing = [f for f in todo if not (ROOT / f).is_file()]
if missing:
    raise SystemExit('Missing explicit core inputs: ' + str(missing))
todo.extend(f for f in [O + '/publishing/git-preflight-rebuild-v2.json',
                       O + '/publishing/git-precommit-failure-v1.json'] if (ROOT / f).is_file())
while todo:
    f = todo.pop()
    absolute = (ROOT / f).resolve()
    if not absolute.is_relative_to(ROOT):
        continue
    f = absolute.relative_to(ROOT).as_posix()
    if f in selected or not own(f) or not (ROOT / f).is_file():
        continue
    selected.add(f)
    content = (ROOT / f).read_text(encoding='utf-8-sig')
    for reference in re.findall(r'(?:projects|production|manim|motion-canvas)/[^\s"\'`,;()<>]+', content):
        candidate = reference.replace('\\', '/').rstrip('/.:]}')
        if own(candidate) and (ROOT / candidate).is_file():
            todo.append(candidate)
for p in (ROOT / 'manim/projects/game-math-orientation-matrices').glob('*.py'):
    selected.add(p.relative_to(ROOT).as_posix())
# The batch queue is an explicitly owned shared control record, not a folder stage.
selected.add(B + '/queue.json')
selected.add('shared/publishing/illustrative-subject-detail-policy.json')

def head_text(name):
    return subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT).decode('utf-8-sig').replace('\r\n', '\n')

agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8-sig').replace('\r\n', '\n')
agent_rules = [p for p in agents.split('\n\n') if p.startswith(('- Detailed-subject rule reaffirmed', '- Detailed illustrative subjects'))]
assert len(agent_rules) == 2
visual = (ROOT / 'docs/VIDEO_VISUAL_STYLE.md').read_text(encoding='utf-8-sig').replace('\r\n', '\n')
start = visual.index('## 사람과 물건을 알아볼 수 있는 상세 삽화로 표현')
end = visual.find('\n## ', start + 3)
visual_section = visual[start:end if end != -1 else len(visual)].split('\n\n2026-10-10 최신 적용 범위:')[0].strip()
workflow = (ROOT / 'docs/VIDEO_WORKFLOW.md').read_text(encoding='utf-8-sig').replace('\r\n', '\n')
workflow_paragraphs = [p for p in workflow.split('\n\n') if p.startswith(('설명 화면의 사람과 물건', '2026-10-13 재확인:'))]
assert len(workflow_paragraphs) == 2
insertions = {
    'AGENTS.md': '\n\n'.join(agent_rules),
    'docs/VIDEO_VISUAL_STYLE.md': visual_section,
    'docs/VIDEO_WORKFLOW.md': '## 사람과 물건의 상세 표현 — 2026-10-12 승인\n\n' + '\n\n'.join(workflow_paragraphs),
}
shared = []
for name, insertion in insertions.items():
    base = head_text(name)
    if insertion in base:
        rendered = base
    else:
        title, remainder = base.split('\n\n', 1)
        rendered = title + '\n\n' + insertion + '\n\n' + remainder
    shared.append({'path': name, 'content': rendered,
        'sha256': hashlib.sha256(rendered.encode()).hexdigest(),
        'purpose': 'Only the explicitly requested detailed-subject rules; other working-tree edits excluded.'})
    selected.add(name)
rows = []
for name in sorted(selected):
    p = ROOT / name
    rows.append({'path': name, 'bytes': p.stat().st_size,
                 'workingSha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                 'purpose': 'Current orientation editable source or review/rebuild/publishing metadata; no media.'})
plan = {'schemaVersion': 1, 'preparedAt': datetime.now(timezone.utc).isoformat(),
        'parent': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'actualVideoId': 'orq0TMVkFts', 'selectedFiles': rows, 'sharedSubsetBlobs': shared,
        'newImages': 0, 'newMedia': 0, 'foreignPathsSelected': 0,
        'excluded': ['UI screenshots/raw UI proofs', 'media/source frames/audio/video/archives',
                     'research subtitles', 'foreign projects and index entries'],
        'automaticAdReviewPending': True, 'scheduleReplacementVerified': False}
target = ROOT / O / 'publishing/production-git-selection-v1.json'
target.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'explicitFiles': len(rows), 'sourceBytes': sum(r['bytes'] for r in rows),
                  'sharedSubsetBlobs': len(shared), 'media': 0, 'newImages': 0}))
