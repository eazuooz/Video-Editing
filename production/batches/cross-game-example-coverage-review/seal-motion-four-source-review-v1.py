"""Seal the directly read source samples; never infer final-pixel approval."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(name, value):
    path = R / name
    assert not path.exists(), f'Preserve existing proof: {path}'
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def entries(value):
    if isinstance(value, dict):
        if 'path' in value and 'sha256' in value:
            yield value
        for v in value.values():
            yield from entries(v)
    elif isinstance(value, list):
        for v in value:
            yield from entries(v)


pre = read(R / 'source-preflight-v1.json')
native = read(R / 'native-preflight-execution-v1.json')
clear = read(R / 'source-clearance-execution-v1.json')
assert native['exitCode'] == clear['exitCode'] == 0
assert native['totalSamples'] == 122 and native['totalSheets'] == 23
assert len(clear['transition']['samples']) == 51
assert sum(len(w['samples']) for w in clear['reframed']) == 95
checked = []
for e in entries([native, clear, pre['protectedBaseline']]):
    actual = sha(ROOT / e['path'])
    assert actual == e['sha256'], e['path']
    checked.append({'path': e['path'], 'sha256': actual})
now = datetime.now(timezone.utc).isoformat()
notes = {
    'portal-aim': '16–32 viewpoint turns around cube/beam and fixed room clues; 33 wall portal, 35 floor portal, 36 cube appears; 37–40 held cube moves with viewpoint. No player portal traversal observed.',
    'portal-traverse': 'Historical filename only. Semantic name: portal-direction-and-cube. 58–61 room/beam, 62–63 ceiling, 64–67 device, 68–69 upward beam, 70–72 floor/wall portal, 74–80 cube aiming and blue-X to yellow-check, 81–82 stairs. Not player traversal.',
    'portal-cube': '84–86 stairs and button; 87–90 turns toward floor portal/beam; 91–93 cube emerges; 94–99 carried cube reaches button and dotted indicator changes blue to yellow.',
    'alyx-platform': '48 dark held. 49–52 yellow destination feet/arc followed by changed viewpoint near doorway; fine samples bracket transitions but do not identify their exact first frames. 52–54 weapon inspection excluded. 54–59 boards and doorway; 60–65 hands grip/remove boards; 67 clear path; 68 destination, 69 nearer door.',
    'alyx-hand': '108 cartridge; 109 locker orientation; 110 destination; 111–113 nearer locker; 114 turns toward room. Later alien-organ/jar interaction held as less approachable.',
    'alyx-locomotion': '164–173 dark and complex travel; later target/combat held. Not adopted for this beginner comparison.'
}
save('native-and-clearance-direct-review-v1.json', {
    'schemaVersion': 1, 'reviewedAt': now,
    'reviewMethod': 'Every board and its displayed samples read directly through view_image in this continuing task; hashes rechecked by this sealer.',
    'native': {'sessionId': 67533, 'actualOuterExitCode': 0, 'samples': 122, 'boards': 23, 'allDisplayedSamplesDirectlyRead': True},
    'transition': {'sessionId': 19810, 'actualOuterExitCode': 0, 'newSampleFiles': 51, 'boards': 9, 'allDisplayedSamplesDirectlyRead': True},
    'clearanceMock': {'reusedSourceSamples': 95, 'boards': 19, 'allDisplayedSamplesDirectlyRead': True, 'framing': clear['framing'],
        'findings': 'Top120 crop/upshift and same-frame bottom120 blur leave cube lens/beam, destination marker and working hands visible above fixed mock caption. Some lower cube base/wrist is covered; final moving annotations and actual cues must be checked separately.'},
    'observations': notes, 'checkedFileHashes': checked,
    'protectedBaselineFiles': len(pre['protectedBaseline']), 'protectedBaselineUnchanged': True,
    'countsAreNotUniqueNativeFrameCount': True,
    'allContinuousNativeFramesApproved': False, 'wholeContinuousListeningApproved': False,
    'narrationTimedAnnotationsApproved': False, 'allFinalCuePixelsApproved': False,
    'sourceAudioAdopted': False, 'finalPublicRightsReview': False,
    'newMediaOrGitImagesCreatedBySealer': 0
})

pts_dir = ROOT / 'shared/output/cross-game-example-coverage/motion/native-preflight-v1'
for k in ['portal2', 'alyx']:
    d = read(pts_dir / (k + '-native-pts.json'))
    print(k, 'native PTS keys', list(d.keys()))

queue_path = ROOT / 'production/batches/cross-game-example-coverage-review/queue.json'
q = read(queue_path)
current = q['currentMotionReview']
assert current['baselineVideoId'] == 'mBDd9VzSTkA'
current['ownedJob'].update(status='complete', actualOuterExitCode=0)
current['sourceDirectReview'] = str((R / 'native-and-clearance-direct-review-v1.json').relative_to(ROOT)).replace('\\', '/')
current['sourceClearanceReview'] = {'samples': 51, 'reframedSamples': 95, 'boards': 28, 'allDisplayedSamplesDirectlyRead': True, 'finalCueApproval': False}
q['updatedAt'] = now
queue_path.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'sealed': True, 'hashedFiles': len(checked), 'protected': 44, 'finalApproval': False}))
