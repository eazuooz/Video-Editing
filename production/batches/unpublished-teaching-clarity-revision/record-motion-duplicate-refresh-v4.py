import json, hashlib, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
P = ROOT / 'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json'
EXPECTED = '96d850927446925597b94e3bde1c1236ab4bbb4e072c895a5a0b3f13da9b0f22'
reviewed = {
 'projects/game-math-bounds-transform-v2/project.json': '253eaf47dde59e2149f6efd0394ea6e23c79f9baf129fa9fb7fcd67fcc465abe',
 'projects/game-math-lines-circles-v2/project.json': 'db945f2e9bc07a1ece8f2737765571bc68e6164165ffa707d43ea350757a31b1',
 'projects/game-math-bounds-transform-v2/script/narration.ko.json': '9c18040dcb71cccd9ff6a86cfb9ad945599a62697123522c1cf305ed648620ee',
 'projects/game-math-bounds-transform-v2/script/narration.en.json': '0cc7e7d05417c4dfd16bf09a63d4690c3872b993bf13c06ce580547bb8e03192',
 'projects/game-math-lines-numeric-retakes-v5/project.json': '54e18b6be2d8b4e92630de75f7b5fb86d79ee4359879ff0fd9a8267d8a5faf82',
 'projects/game-math-lines-numeric-retakes-v5/script/narration.ko.json': '054d98cf61e66d700995674014215bdb2bb789da90509674883aed3e5685caab',
 'projects/game-math-lines-numeric-retakes-v5/script/narration.en.json': '4786a6db2bb59dc13e14c2f26e2b61b0301d70e4514211ebcc22c3532fac4945',
 'projects/game-math-lines-unit-retake-v6/project.json': '585277291c60f3ee0d53d955b212f67f002ef732cfcc91c8f256040c66042df0',
 'projects/game-math-lines-unit-retake-v6/script/narration.ko.json': 'a8d0d97fdda6110da44e1ef1a9d3199740271cc4179383ba1b2045a3fbca30cc',
 'projects/game-math-lines-unit-retake-v6/script/narration.en.json': '9fbc566b317fd1b3f3fe4da52c22cdfb92cc506204ccf407020134c4f6966f2c',
}
report = json.loads(P.read_text(encoding='utf-8'))
assert report['inputsDigest'] == EXPECTED
assert len(report['existingProjects']) == 74 and len(report['inputFiles']) == 450
for path, sha in reviewed.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == sha, path
stamp = datetime.now(timezone.utc).isoformat()
evidence = {
 'schemaVersion': 1, 'recordedAt': stamp, 'inputsDigest': EXPECTED,
 'previousReportPreserved': str((R/'duplicate-history-current72-v3.json').relative_to(ROOT)).replace('\\','/'),
 'projectCount': 74, 'inputCount': 450,
 'allCurrentTitlesDirectlyRead': True,
 'changedFiles': [{'path': p, 'sha256': s, 'fullCurrentBodyDirectlyRead': True} for p,s in reviewed.items()],
 'comparison': {
  'bounds': 'Full paired 26-scene sphere/AABB/affine enclosure material addresses squared-distance inclusion, axis-aligned ranges, overlap candidates, eight-corner rotation and abs(A) half-extents. This differs from player comfort, camera motion, free aim and restoring a goal after a view change.',
  'numericRetakes': 'Full paired 20-scene v5 and v6 are narration-only revisions of the lines/bounds teaching material. They clarify dimensionless t versus metre distance and the final scalar addition; standalone upload is disabled. No camera-comfort duplicate. The additionally changed lines/circles manifest retains its two-point connection, parameter/range and circle question; measured episode timing is preparation, not a new platform ID.',
  'currentMotionQuestion': 'How can a player follow a goal while reducing unnecessary camera movement, choose comfort settings and restore those settings?',
  'foreignLanguageIssuePreserved': 'The previously observed LC13 English long-bridge versus Korean long-legs alternative remains foreign material; no correction or approval of its accuracy is asserted.'
 },
 'currentStudio': {
  'url': 'https://studio.youtube.com/video/avLKKfQBV_U/edit',
  'cuaTabId': '58',
  'title': '게임수학 Part 2 · 기하 기본 요소 ① 직선·구·경계 상자',
  'fullDescriptionDirectlyRead': True,
  'descriptionClaims': '그래플 출발점과 방향; 직선·선분·레이 범위; 구; 여러 점의 경계 상자; 상자 회전 오류와 안전한 변환식. 15 measured chapter labels through 17:31 membership.',
  'visibilityObserved': '예약됨', 'sdCompleteObserved': True, 'hdCompleteObserved': True,
  'saveButtonDisabledObserved': True, 'settingsModified': False,
  'newRetakeOrBoundsIdObserved': None
 },
 'priorContentStudioReviewRetained': 'current-content-studio-review-v2.json',
 'foreignFilesModified': 0, 'foreignPublishingModified': 0
}
target = R/'inventory-change-direct-review-v4.json'
assert not target.exists()
target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
reason = 'Preserved full previous topic review and directly reread all ten changed manifest/KO/EN bodies plus all 74 titles. Sphere/AABB/affine bounds and numeric/unit narration retakes concern geometric representations, while motion-sickness concerns player-camera comfort, aim separation and recoverable settings. Current Studio full lines/bounds metadata is distinct. Exact IDs/titles alone were not used. Evidence: '+str(target.relative_to(ROOT)).replace('\\','/')
studio = 'Current CUA58 avLKKfQBV_U edit: entire title/description/15 chapters, scheduled visibility, completed SD/HD and disabled Save directly read; no settings change. Prior related five Studio reviews preserved. '+str(target.relative_to(ROOT)).replace('\\','/')
a = subprocess.run([node, 'scripts/review-video-duplicates.cjs','motion-sickness-games','--decision','distinct','--reason',reason,'--studio-evidence',studio], cwd=ROOT, check=False, text=True, capture_output=True, encoding='utf-8')
print(a.stdout, end=''); print(a.stderr, end=''); assert a.returncode == 0
b = subprocess.run([node, 'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'], cwd=ROOT, check=False, text=True, capture_output=True, encoding='utf-8')
print(b.stdout, end=''); print(b.stderr, end=''); assert b.returncode == 0
evidence['actualDecisionExitCode'] = a.returncode
evidence['actualCheckExitCode'] = b.returncode
evidence['checkedInputsDigest'] = json.loads(P.read_text(encoding='utf-8'))['inputsDigest']
target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
assert evidence['checkedInputsDigest'] == EXPECTED
print(json.dumps({'evidence':str(target.relative_to(ROOT)), 'digest':EXPECTED,'checkExit':b.returncode}))
