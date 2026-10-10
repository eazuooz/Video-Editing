import json, hashlib, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
P = ROOT / 'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'
EXPECTED = '2f9d041ade512576400f379671b4c31d2585fa511813e6cd7bc806d56bdd4088'
changed = {'projects/game-math-bounds-transform-v2/publishing/youtube-upload.json': '18abd35a8514f13fb8a430d1f577a33fbe46f1d00f867e3fee3f8c487912095e'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = json.loads(P.read_text('utf-8-sig'))
old = json.loads((R / 'duplicate-history-current77-v7.json').read_text('utf-8-sig'))
assert report['inputsDigest'] == EXPECTED and len(report['existingProjects']) == 77 and len(report['inputFiles']) == 461
previous = {x['path']: x['sha256'] for x in old['inputFiles']}
delta = {x['path']: x['sha256'] for x in report['inputFiles'] if previous.get(x['path']) != x['sha256']}
assert delta == changed
for path, digest in changed.items():
    assert sha(ROOT / path) == digest, path
e = {
    'schemaVersion': 1, 'recordedAt': datetime.now(timezone.utc).isoformat(),
    'inputsDigest': EXPECTED, 'projectCount': 77, 'inputCount': 461,
    'previousReportPreserved': 'duplicate-history-current77-v7.json',
    'priorFullContentReviewRetained': 'inventory-change-direct-review-v7.json',
    'changedFiles': [{'path': p, 'sha256': s, 'fullCurrentBodyDirectlyRead': True} for p, s in changed.items()],
    'comparison': 'The entire changed bounds publishing receipt, including full Korean/English descriptions, all 25 measured chapters, all settings and pending records, was read. It still teaches spheres, axis-aligned enclosure, axis interval overlap, broad candidates versus actual contact, and updating rotated extents using center and half-size. The motion revision teaches following a target with less camera rotation, separating aim from view movement, recognizing orientation landmarks and offering accessible reversible camera controls. The questions and worked claims remain distinct. The receipt now records transfer complete and no copyright issues, ad suitability in progress, both 216-cue language tracks and English metadata published, and saved/reopened beginning card and member end screen. Preparation-era fields remain historical and incomplete. No foreign content or settings changed. Earlier full comparisons of the 77-project inventory and the three new plane projects remain retained.',
    'currentStudio': [{
        'url': 'https://studio.youtube.com/video/W5UkJkep7yo/edit', 'cuaTabId': '58',
        'title': '게임수학 Part 2 · 직선과 경계 ② 물체의 범위와 회전 뒤 경계',
        'fullDescriptionDirectlyRead': True, 'allChapterLabelsDirectlyRead': 25,
        'draftBannerObserved': '이 동영상은 임시본 상태입니다.',
        'sdComplete': True, 'hdComplete': True,
        'privacyBadgeObserved': False, 'saveButtonDisabled': True, 'settingsModified': False,
        'observation': 'Current DOM shows SD and HD complete, superseding earlier HD processing observations. Draft banner remains visible; no complete-publishing or current visibility approval is inferred.'
    }],
    'foreignFilesModified': 0, 'foreignPublishingModified': 0,
    'previousPairAttempt': {'exitCode': 1, 'reason': 'Fresh duplicate check detected the changed receipt before any pair state/media was created.', 'workerOrMediaCreated': False}
}
target = R / 'inventory-change-direct-review-v8.json'
assert not target.exists()
target.write_text(json.dumps(e, ensure_ascii=False, indent=2) + '\n', 'utf-8')
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason = e['comparison'] + ' Evidence: ' + target.relative_to(ROOT).as_posix()
studio = 'CUA58 full W5UkJkep7yo title, description, all25 chapters and footer read. Current SDHD complete, draft banner, Save disabled. Read-only. ' + target.relative_to(ROOT).as_posix()
for name, args in [('decision', ['--decision', 'distinct', '--reason', reason, '--studio-evidence', studio]), ('check', ['--check'])]:
    p = subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'motion-sickness-games', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    print(p.stdout, end=''); print(p.stderr, end=''); assert p.returncode == 0
    e[name + 'ExitCode'] = p.returncode
assert json.loads(P.read_text('utf-8-sig'))['inputsDigest'] == EXPECTED
target.write_text(json.dumps(e, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'digest': EXPECTED, 'evidence': target.relative_to(ROOT).as_posix()}))
