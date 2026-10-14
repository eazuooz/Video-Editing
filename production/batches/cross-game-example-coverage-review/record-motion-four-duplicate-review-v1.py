"""Record the actually read changed contents and current read-only Studio evidence."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = read(ROOT / 'production/batches/sakurai-planning-game-design/preflight/motion-sickness-games.json')
previous = read(R / 'duplicate-before-refresh-v1.json')
old = {x['path']: x['sha256'] for x in previous['inputFiles']}
changes = [x for x in report['inputFiles'] if old.get(x['path']) != x['sha256']]
expected = set(read(R / 'duplicate-changed-inputs-v1.json')['changedPaths']) | {
    'projects/game-math-polygons-cross-game-additions-v4/project.json',
    'projects/game-math-polygons-cross-game-additions-v4/script/narration.ko.json',
    'projects/game-math-polygons-cross-game-additions-v4/script/narration.en.json',
}
assert {x['path'] for x in changes} == expected, 'Read any newly changed content before recording it'
for x in changes:
    assert sha(ROOT / x['path']) == x['sha256'], x['path']
evidence = [R / ('current-studio-' + k + '-metadata-v1.json') for k in ['normal', 'frustum', 'projection']]
evidence += [R / 'current-studio-list-v1.dom.txt',
             ROOT / 'production/batches/cross-game-example-coverage-review/motion-current-studio-v1.dom.txt']
for p in evidence:
    assert p.exists()
out = R / 'duplicate-content-and-studio-direct-review-v1.json'
assert not out.exists()
value = {
    'schemaVersion': 1, 'reviewedAt': datetime.now(timezone.utc).isoformat(),
    'candidate': 'motion-sickness-games', 'baselineVideoId': 'mBDd9VzSTkA',
    'inputsDigest': report['inputsDigest'], 'existingProjects': len(report['existingProjects']),
    'inputCount': len(report['inputFiles']), 'changedInputs': changes,
    'reviewScope': {
        'allChangedKoEnScriptBodiesDirectlyRead': True,
        'changedManifestViewerQuestionsContractsAndPreservationDirectlyRead': True,
        'changedReceiptKoEnDescriptionsChaptersVisibilityScheduleSemanticsDirectlyRead': True,
        'allForeignRawTechnicalReceiptFieldsClaimedRead': False,
        'currentScheduledListRowsDirectlyRead': 27,
        'currentFullStudioTitleDescriptionRead': ['nalAZHtEtw0', 'CbX6KQ-_zsc', 'c96qTnlHBVU'],
        'baselineWhole14PairedScenesReadInContinuingTask': True,
        'foreignPlatformChanges': 0, 'foreignFileChanges': 0,
    },
    'findings': [
        'Polygon centers use coordinate averages, incenter/circumcenter and weighted areas; valid polygon boundaries and ears partition regions. The new four-game addition compares placement references, terrain boundaries, factory paths and retained regions. These do not teach camera-input separation or individual motion sensitivity.',
        'Frustum Studio teaches FOV/zoom, clip planes, camera displacement, orthographic projection and viewport sizing. Projection Studio follows one 3D point through local/world/view/clip/w/pixel coordinates. This revision teaches visible tool/camera/locomotion responsibilities and understandable reversible player choices; it does not reproduce those calculations.',
        'Normal/UV Studio teaches perpendicular normals, inverse transpose, interpolation and addressing. Portal/Alyx source reuse is separately disclosed; a shared game title or source is not a shared viewer question.',
        'Current motion overview, all original wording/order and 14 approved PCM remain protected. New Portal2 and Alyx footage will supply two additional beginner-explained comparisons, not another copy of an existing mathematical lecture.',
    ],
    'studioEvidence': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in evidence],
    'verdict': 'distinct', 'inventoryAloneIsApproval': False,
    'finalFourGamePixelsApproved': False, 'newUploadComplete': False,
}
out.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'recorded': str(out.relative_to(ROOT)), 'changedInputs': len(changes), 'digest': report['inputsDigest']}))
