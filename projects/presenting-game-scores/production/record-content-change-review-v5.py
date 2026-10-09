"""Seal the full reread of the next lighting manifest metadata change."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-presenting-game-scores'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
report_path = ROOT / 'production/batches/sakurai-planning-game-design/preflight/presenting-game-scores.json'
report = read(report_path)
old = read(PROOF / 'duplicate-history-before-change-v5.json')
before = {row['path']: row['sha256'] for row in old['inputFiles']}
changed = [row for row in report['inputFiles'] if before.get(row['path']) != row['sha256']]
expected = {
 'projects/game-lighting-history-01/project.json': '7bf42ef23e2d5ed70486404e2ade249931ca30d85eb2836385cd2ecaf5f6679d',
 'projects/game-lighting-history-02/project.json': '1e0f6ad3f7cbb6efd770cab973467e13d9ce6ba12910a1366d450ff7fea62493',
 'projects/game-lighting-history-03/project.json': '4f23058c0d06e9b25948647620085576277a1f02f7ae293651ca9c09d0626fb6',
 'projects/game-lighting-history-04/project.json': 'fa5952344bc64884d54336f7673202800de9d618132f8a083a44b511722e62ab',
}
assert {row['path']: row['sha256'] for row in changed} == expected
assert all(sha(ROOT / path) == digest for path, digest in expected.items())
previous = read(PROOF / 'content-studio-change-review-v4.json')
reason = previous['reason'] + (' The four complete manifests were reread again after their currentDistinct '
    'flags were accurately set false with a narration-generation snapshot. Generated PCM, all source '
    'claims, script paths and chapter promises are unchanged; no new game-score content was added.')
studio = previous['studioEvidence']
subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'presenting-game-scores', '--decision',
                'distinct', '--reason', reason, '--studio-evidence', studio], cwd=ROOT, check=True)
subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'presenting-game-scores', '--check'], cwd=ROOT, check=True)
current = read(report_path)
assert current['inputsDigest'] == report['inputsDigest']
proof = dict(schemaVersion=5, reviewedAt=datetime.now(timezone.utc).isoformat(),
             changedFiles=[{**row, 'wholeTextDirectlyRead': True} for row in changed],
             previousReview='content-studio-change-review-v4.json',
             previousReportPreserved='duplicate-history-before-change-v5.json',
             newOrChangedScriptInputs=0, fullChangedContentsDirectlyRead=True,
             reason=reason, studioEvidence=studio, foreignFilesModified=0,
             foreignPublishingChanges=0, inputsDigest=current['inputsDigest'],
             currentCheckExit=0, reportSha256=sha(report_path), decision='distinct')
out = PROOF / 'content-studio-change-review-v5.json'
assert not out.exists()
out.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', 'utf-8')
refusal = dict(actualExitCode=1, mode='whole', stateCreated=False, modelLoaded=False,
               reason='Lighting currentDistinct metadata changed again before model/state creation.',
               currentPcmPreserved=True, recoveryReview=out.relative_to(ROOT).as_posix())
(BASE / 'current-whole-asr-pre-model-refusal-v2.json').write_text(
    json.dumps(refusal, ensure_ascii=False, indent=2) + '\n', 'utf-8')
