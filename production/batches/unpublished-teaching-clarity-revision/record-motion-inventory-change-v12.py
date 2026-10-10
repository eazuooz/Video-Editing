from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
report = read(ROOT / 'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
assert report['inputsDigest'] == 'daf8146d0dc1f9e52c07ecfca23fd5562b745f83f1e6c449b13d40bd71327898'
prior = read(R / 'duplicate-history-current78-v11.json')
old = {v['path']: v['sha256'] for v in prior['inputFiles']}
changed = [v for v in report['inputFiles'] if old.get(v['path']) != v['sha256']]
assert {v['path'] for v in changed} == {
    'projects/game-math-plane-distances-v2/project.json',
    'projects/game-math-triangle-addresses-v2/project.json',
}
for v in changed:
    assert hashlib.sha256((ROOT / v['path']).read_bytes()).hexdigest() == v['sha256']
    v['fullCurrentBodyDirectlyRead'] = True
studio = read(R / 'neighbor-current-studio-v12.json')
assert studio['readOnly'] and studio['platformMutations'] == 0
reason = ('Both changed full manifests were directly reread. Their Manim project paths now point to '
          'planes_additions.py rather than the shared geometry wrapper. Their narration-final.wav paths, '
          'whole chapter contracts, measured 40:60 totals (42595 and 50995 body frames), preserved baseline '
          'wsxSYEEj8aQ and incomplete new private/pixel/flow states remain explicit. Distance to a plane, '
          'normalization and nearest point, Newell boundaries, finite triangle inclusion and defined affine '
          'attributes remain the mathematical questions previously compared in full KO/EN content. '
          'They do not reproduce this video’s camera/view/aim responsibility, task readability, orientation '
          'cues or reversible settings. Current W5UkJkep7yo Studio title, entire 25-chapter description, '
          'private status, SD/HD completion, no alerts and disabled Save were reread without mutation. '
          'Retain all earlier full source/script/content comparisons; shared game imagery does not '
          'establish duplicated teaching claims.')
o = dict(schemaVersion=1, recordedAt=datetime.now(timezone.utc).isoformat(),
         inputsDigest=report['inputsDigest'], projectCount=len(report['existingProjects']),
         inputCount=len(report['inputFiles']), previousReportPreserved='duplicate-history-current78-v11.json',
         priorFullContentReviewRetained='inventory-change-direct-review-v11.json', changedFiles=changed,
         comparison=reason, currentStudioEvidence='neighbor-current-studio-v12.json',
         foreignFilesModified=0, foreignPublishingModified=0, decisionExitCode=None, checkExitCode=None)
p = R / 'inventory-change-direct-review-v12.json'
assert not p.exists()
p.write_text(json.dumps(o, ensure_ascii=False, indent=2) + '\n', 'utf-8')
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
c = subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'motion-sickness-games', '--decision',
                    'distinct', '--reason', reason, '--studio-evidence', p.relative_to(ROOT).as_posix()], cwd=ROOT)
o['decisionExitCode'] = c.returncode
assert c.returncode == 0
assert read(ROOT / 'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')['inputsDigest'] == o['inputsDigest']
c = subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'motion-sickness-games', '--check'], cwd=ROOT)
o['checkExitCode'] = c.returncode
p.write_text(json.dumps(o, ensure_ascii=False, indent=2) + '\n', 'utf-8')
assert c.returncode == 0
cp = read(R / 'latest-checkpoint.json')
cp.update(currentDuplicateReview=p.relative_to(ROOT).as_posix(), currentDuplicateCheckExitCode=0)
(R / 'latest-checkpoint.json').write_text(json.dumps(cp, ensure_ascii=False, indent=2) + '\n', 'utf-8')
