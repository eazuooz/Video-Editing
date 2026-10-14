"""Seal the directly read changed quaternion manifest and current Studio."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
report_path = ROOT / 'production/batches/sakurai-planning-game-design/preflight/limited-color-world.json'
report = read(report_path)
old = read(BASE / 'duplicate-history-approved55-v3.json')
old_hash = {x['path']: x['sha256'] for x in old['inputFiles']}
changed = [x for x in report['inputFiles'] if old_hash.get(x['path']) != x['sha256']]
assert len(changed) == 1
assert changed[0]['path'] == 'projects/game-math-quaternion-teaching-additions-v2/project.json'
assert changed[0]['sha256'] == '9694832db296d5af53129dff00423ed33b3ecbf0468ddf0bebb0a0624c704347'
assert report['inputsDigest'] == '176082991351a51cef66607e137ab02342f865315e10ba627406f021721a9411'
for x in report['inputFiles']:
    assert sha(ROOT / x['path']) == x['sha256'], x['path']
previous = read(BASE / 'content-studio-change-review-v3.json')
for x in previous['changedFilesFullBodiesDirectlyRead']:
    if '/script/' in x['path']:
        assert sha(ROOT / x['path']) == x['sha256'], x['path']
manifest = read(ROOT / changed[0]['path'])
assert manifest['contract']['angles'] == 'radians in formulas'
assert manifest['contract']['vectorRotation'] == 'q [0,v] q^-1'
assert manifest['contract']['worldDelta'] == 'delta q'
assert manifest['contract']['bodyDelta'] == 'q delta'
ax = BASE / 'studio-quaternion-current-v4.ax.txt'
ax_text = ax.read_text(encoding='utf-8')
assert all(s in ax_text for s in ['03OXtik2nes', '예약됨', '표준 화질 완료', '고화질 완료', '19:18', '쿼터니언의 원리와 계산'])
out = BASE / 'content-studio-change-review-v4.json'
assert not out.exists()
record = dict(
    schemaVersion=4, slug='limited-color-world', reviewedAt=datetime.now(timezone.utc).isoformat(),
    previousFullRelatedReview='content-studio-direct-review-v2.json',
    previousNew33SceneWholeKoEnReview='content-studio-change-review-v3.json',
    preservedPreviousReport='duplicate-history-approved55-v3.json',
    projects=55, inputs=384, inputsDigest=report['inputsDigest'],
    changedFilesFullBodiesDirectlyRead=changed, unchanged33SceneKoEnShaVerified=True,
    actualWholeManifestReadObservation='8e5e22',
    comparison='The current additive quaternion manifest preserves the 26-scene rotation baseline and defines right-handed column-vector local-to-world Hamilton wxyz calculations, radians in formulas, q[0,v]q^-1 vector rotation and body/world delta order. Its unchanged 33 paired teaching/bridge scenes teach orientation algebra. This differs from limited-color-world: preserving essential gameplay cues through outline, pattern, height, motion and lightness when hues are difficult to distinguish. Axis colors remain mathematical diagram notation, not perceptual or color-accessibility instruction.',
    currentStudio=dict(actualId='03OXtik2nes', url='https://studio.youtube.com/video/03OXtik2nes/edit',
                       fullTitleDescriptionAnd19ChaptersDirectlyRead=True, observedStatus='예약됨',
                       sdHdObserved=True, ax=rel(ax), axSha256=sha(ax), settingsChanged=False),
    standaloneUploadAllowed=manifest['standaloneUploadAllowed'],
    absenceFromChannelNotInferred=True, foreignFilesOrSettingsModified=0,
    decision='distinct', currentProductionApprovalSeparate=True)
out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
reason = 'Full related KOEN/body/outline/manifest and current Studio reviews remain in v2/v3; changed quaternion manifest read whole plus unchanged33 KOEN scenes verified and current Studio03OXtik2nes whole19 chapters reread in v4. Quaternion orientation algebra and radian/body/world convention differ from hue-independent gameplay cues, pattern/height/motion/lightness and perceptual inspection.'
decision = subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', 'limited-color-world', '--decision', 'distinct', '--reason', reason, '--studio-evidence', rel(out)], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
assert decision.returncode == 0, decision.stdout + decision.stderr
check = subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', 'limited-color-world', '--check'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
assert check.returncode == 0, check.stdout + check.stderr
print(json.dumps(dict(projects=55, inputs=384, digest=report['inputsDigest'], decisionExit=decision.returncode, checkExit=check.returncode)))
