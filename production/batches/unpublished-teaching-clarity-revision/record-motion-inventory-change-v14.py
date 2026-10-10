from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
REV = 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read = lambda p: json.loads((ROOT / p).read_text('utf-8-sig'))
report = read('production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
prior = read(REV + '/duplicate-history-current78-v13.json')
old = {e['path']: e['sha256'] for e in prior['inputFiles']}
changed = [dict(e) for e in report['inputFiles'] if old.get(e['path']) != e['sha256']]
assert {e['path'] for e in changed} == {
    'projects/game-math-plane-distances-v2/publishing/youtube-upload.json',
    'projects/game-math-triangle-addresses-v2/project.json',
    'projects/game-math-triangle-addresses-v2/publishing/youtube-upload.json'}
for e in changed:
    assert hashlib.sha256((ROOT / e['path']).read_bytes()).hexdigest() == e['sha256']
    e['fullCurrentBodyDirectlyRead'] = True
studio = read(REV + '/plane-current-studio-v14.json')
assert studio['readOnly'] and studio['platformMutations'] == 0
assert 'Rzrt47-u4G0' in studio['url'] and '비공개' in studio['ax'] and '검토 중...' in studio['ax']
reason = ('All three changed records were directly read in full. Plane-distance receipt now records actual new Rzrt47-u4G0 upload started; current read-only Studio whole title and20-chapter description show private, SD/HD completed and review in progress, not complete publishing. Triangle-address manifest records local technical/direct-pixel completion while its prepared receipt actual videoId remains null. Its23-chapter KO/EN descriptions develop plane membership versus finite triangle membership, area, weighted vertex address, signed area weights, independent coplanarity and affine surface-value interpolation. These mathematics claims differ from camera comfort, visible movement versus body feedback, reversible options and task readability in motion-sickness. The new plane title/entire metadata were compared with the preserved previous full source/script reviews; baseline wsxSYEEj8aQ and W5UkJkep7yo earlier current observations are retained as dated history. No foreign file or publishing setting was modified.')
proof = dict(schemaVersion=1, recordedAt=datetime.now(timezone.utc).isoformat(), inputsDigest=report['inputsDigest'],
    projectCount=len(report['existingProjects']), inputCount=len(report['inputFiles']), changedFiles=changed,
    priorFullContentReviewRetained=REV + '/inventory-change-direct-review-v13.json',
    previousReportPreserved=REV + '/duplicate-history-current78-v13.json', comparison=reason,
    currentStudioEvidence=REV + '/plane-current-studio-v14.json', foreignFilesModified=0, foreignPublishingModified=0,
    earlierCurrentCheckExit1='9207a0: new input changes require full rereview', decisionExitCode=None, checkExitCode=None)
target = ROOT / REV / 'inventory-change-direct-review-v14.json'
assert not target.exists()
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for key, args in [('decisionExitCode', ['--decision', 'distinct', '--reason', reason, '--studio-evidence', target.relative_to(ROOT).as_posix()]), ('checkExitCode', ['--check'])]:
    target.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    result = subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'motion-sickness-games', *args], cwd=ROOT)
    proof[key] = result.returncode
    target.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    assert result.returncode == 0
for f in [REV + '/latest-checkpoint.json', 'production/batches/unpublished-teaching-clarity-revision/queue.json']:
    data = read(f)
    current = data if f.endswith('latest-checkpoint.json') else next(e for e in data['items'] if e['slug'] == 'motion-sickness-games')
    current.update(currentDuplicateReview=target.relative_to(ROOT).as_posix(), currentDuplicateCheckExitCode=0)
    (ROOT / f).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
