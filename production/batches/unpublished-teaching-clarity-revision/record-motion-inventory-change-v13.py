"""Retain full earlier comparisons and review only actual changed foreign records."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
report = read(ROOT / 'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
prior = read(R / 'duplicate-history-current78-v12.json')
old = {v['path']: v['sha256'] for v in prior['inputFiles']}
changed = [v for v in report['inputFiles'] if old.get(v['path']) != v['sha256']]
assert {v['path'] for v in changed} == {'projects/game-math-plane-distances-v2/project.json', 'projects/game-math-plane-distances-v2/publishing/youtube-upload.json'}
assert report['inputsDigest'] == '4364f74809fffde71a6b76f0fef5684bc9ba547f8f059ea29e5e2343fc72532c'
for v in changed:
    assert hashlib.sha256((ROOT / v['path']).read_bytes()).hexdigest() == v['sha256']
    v['fullCurrentBodyDirectlyRead'] = True
studio = read(R / 'plane-current-studio-v13.json')
assert studio['readOnly'] and studio['platformMutations'] == 0 and '예약됨' in studio['ax']
reason = ('Both full changed records were directly read: the plane-distance manifest now records local technical/pixel completion and the prepared receipt contains the full independent KO/EN explanation and20 measured chapters, source hashes and pending platform fields. Its actual videoId is null; no new plane upload is inferred. The claims remain normalized plane residual versus distance, closest point, three-point/Newell normal and the finite-triangle next question, distinct from motion comfort, camera/aim responsibility, task readability and reversible options. Current baseline wsxSYEEj8aQ Studio entire15-chapter description/title and scheduled/SDHD/no-alert state were reread; its plane/barycentric teaching remains distinct. Current W5UkJkep7yo whole25-chapter bounds/rotation description and private/SDHD were also reread. Preserve all prior full KO/EN/source comparisons and historical reports; no foreign files or publishing settings modified.')
o = dict(schemaVersion=1, recordedAt=datetime.now(timezone.utc).isoformat(), inputsDigest=report['inputsDigest'],
         projectCount=len(report['existingProjects']), inputCount=len(report['inputFiles']), changedFiles=changed,
         previousReportPreserved='duplicate-history-current78-v12.json', priorFullContentReviewRetained='inventory-change-direct-review-v12.json',
         comparison=reason, currentStudioEvidence=['plane-current-studio-v13.json', 'neighbor-current-studio-v13.json'],
         foreignFilesModified=0, foreignPublishingModified=0, earlierCurrentCheckExit1='744d2c: input changes required rereview',
         decisionExitCode=None, checkExitCode=None)
p = R / 'inventory-change-direct-review-v13.json'
assert not p.exists()
p.write_text(json.dumps(o, ensure_ascii=False, indent=2) + '\n', 'utf-8')
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for label, args in [('decisionExitCode', ['--decision', 'distinct', '--reason', reason, '--studio-evidence', p.relative_to(ROOT).as_posix()]), ('checkExitCode', ['--check'])]:
    c = subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'motion-sickness-games', *args], cwd=ROOT)
    o[label] = c.returncode
    p.write_text(json.dumps(o, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    assert c.returncode == 0
cp = read(R / 'latest-checkpoint.json')
cp.update(currentDuplicateReview=p.relative_to(ROOT).as_posix(), currentDuplicateCheckExitCode=0)
(R / 'latest-checkpoint.json').write_text(json.dumps(cp, ensure_ascii=False, indent=2) + '\n', 'utf-8')
