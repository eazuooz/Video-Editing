"""Seal the four changed manifests and read-only Studio review already read."""
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
old = read(PROOF / 'duplicate-history-before-change-v4.json')
report = read(report_path)
previous = {row['path']: row['sha256'] for row in old['inputFiles']}
changes = [row for row in report['inputFiles'] if previous.get(row['path']) != row['sha256']]
expected = {
 'projects/game-lighting-history-01/project.json': '671e27e531693599650f3f7f7bb0a8ad2f9d14742a1a250a3903262ab92822b2',
 'projects/game-lighting-history-02/project.json': 'fac2463c360103e6451d1abb9403448267283a3fc71039b4f4811d1941b56047',
 'projects/game-lighting-history-03/project.json': '3bd90a93c3a277faad7248321f74f1b815c68cf368d30044707103379c31372a',
 'projects/game-lighting-history-04/project.json': '565476debfda075c8a8755ab8209cb9bb4445e90ccaaf827c68da669e8891c03',
}
assert {row['path']: row['sha256'] for row in changes} == expected
assert all(sha(ROOT / path) == digest for path, digest in expected.items())
assert report['inputsDigest'] == '0c14251257f1731e098a98fadf6cc6ecfb27058153aec15b24cd3c9cc6f720ac'
assert not any('narration.' in row['path'] for row in changes)
assert not (BASE / 'current-whole-asr-execution-v1.json').exists()
assert not (BASE / 'current-whole-asr-v1.log').exists()
reason = ('The full four changed lighting manifests were directly reread. They update generated narration, '
          'measured voice lengths, provisional SRT paths and research restoration; all final video/upload gates '
          'remain false. Their unchanged paired scripts address sector brightness/lightmaps/forward and deferred '
          'shading; stored indirect light, SSR, refraction and volumes; BVH, samples, ReSTIR, Nanite and Lumen; '
          'virtual shadows, path tracing, reconstruction and postprocessing. These are rendering information and '
          'computation topics, distinct from achieved game performance, quantity versus evaluation, names/units, '
          'opponent differences and readable score calculation. Prior complete KO/EN comparisons remain valid. '
          'No approval is based on an empty exact-match list.')
studio = ('2026-10-09 read-only CUA tab134 reloaded nalAZHtEtw0/edit and directly read the complete title and '
          'description/chapters: normal perpendicularity/inverse transpose, pixel/texel and UV correspondence, '
          'repeat/clamp, interpolate-before-wrap. Private, SD/HD complete, notification dash, Save disabled. '
          'Then the channel date-descending latest30 rows (about489 total) were read: existing math/Sakurai '
          'videos, no new lighting row in that observed page. User-scheduled rotation/polar/picking-sides and '
          'published praise-player were preserved; these status changes are not new score-design claims. '
          'No full-channel absence claim and no platform changes.')
subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'presenting-game-scores',
                '--decision', 'distinct', '--reason', reason, '--studio-evidence', studio], cwd=ROOT, check=True)
subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'presenting-game-scores', '--check'], cwd=ROOT, check=True)
current = read(report_path)
assert current['inputsDigest'] == report['inputsDigest']
stamp = datetime.now(timezone.utc).isoformat()
proof = dict(schemaVersion=4, slug='presenting-game-scores', reviewedAt=stamp,
             previousReview='content-studio-change-review-v3.json',
             previousReportPreserved='duplicate-history-before-change-v4.json',
             changedFiles=[{**row, 'wholeTextDirectlyRead': True} for row in changes],
             newOrChangedScriptInputs=0, fullChangedContentsDirectlyRead=True,
             reason=reason, studioEvidence=studio, currentStudio=dict(tabId='134',
             detailVideoId='nalAZHtEtw0', completeTitleAndDescriptionRead=True,
             latestPageRows=30, observedTotalApproximate=489, edits=0),
             foreignFilesModified=0, foreignPublishingChanges=0,
             decision='distinct', inputsDigest=current['inputsDigest'], currentCheckExit=0,
             existingProjects=len(current['existingProjects']), inputs=len(current['inputFiles']),
             reportSha256=sha(report_path))
destination = PROOF / 'content-studio-change-review-v4.json'
assert not destination.exists()
destination.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', 'utf-8')
failure = dict(observedAt=stamp, worker='review-current-voice-v1.py', mode='whole',
               actualExitCode=1, reason='Current inventory changed; duplicate gate refused before state/model.',
               stateCreated=False, modelLoaded=False, gpuJobs=0, currentPcmPreserved=True,
               recoveryReview=destination.relative_to(ROOT).as_posix(), recoveryCheckExit=0)
(BASE / 'current-whole-asr-pre-model-refusal-v1.json').write_text(
    json.dumps(failure, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('Four complete lighting manifest changes and current read-only Studio compared; current distinct check passed.')
