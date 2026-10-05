"""Persist directly read measured pixels, preserving input and final scopes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
WORK = BASE / 'measured-edit-v4'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = datetime.now(timezone.utc).isoformat()
def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

white = read(WORK / 'timed-white-cues-local-v4/execution.json')
assert white['exitCode'] == 0 and len(white['images']) == 173 and len(white['sheets']) == 29
for r in white['images'] + white['sheets']:
    assert sha(ROOT / r['path']) == r['sha256'], r['path']
notes = [
    ('01', 'Question, outcome, retained activity/changed choice/check order and first example are readable. Cards, comparison arrows, depth and moving emphasis stay clear of literal fixed narration boxes.'),
    ('03', 'Production reuse and player decisions are separate comparisons. Literal narration retains the limits on inferring internal code, cost or preferences from footage.'),
    ('04', 'The own-project question is a595-frame readable white comparison, classified as explanation. The initial594 UI recalculation was corrected before this measured render.'),
    ('05', 'Hypothetical routeA/B and intervening decisions are visibly differentiated. This is our design proposal, not proof of a measured game map or satisfaction.'),
    ('07', 'Retained promise and changed decision are independently readable; no unseen developer reuse or damage-effect claim is added.'),
    ('09', 'Preparation, card/choice and combat order are visible with comparisons and arrows. The narration does not assign an unseen effect to a selected device.'),
    ('11', 'Existing-player and first-player lanes separately converge on review. The diagrams do not claim an actual user study, success or sales guarantee.')
]
save(BASE / 'timed-white-caption-direct-review-v4.json', {
    'schemaVersion': 1, 'reviewedAt': now,
    'sourceExecution': 'projects/making-game-sequels/production/measured-edit-v4/timed-white-cues-local-v4/execution.json',
    'sourceExecutionSha256': sha(WORK / 'timed-white-cues-local-v4/execution.json'),
    'planSha256': sha(WORK / 'plan.json'),
    'captionTracksSha256': sha(WORK / 'caption-tracks-v4.json'),
    'captionLayoutSha256': sha(WORK / 'caption-layout-v4.json'),
    'whiteFrames': 13945, 'segments': white['cuts'], 'images': [{**r, 'directlyRead': True} for r in white['images']],
    'boards': [{**r, 'directlyRead': True} for r in white['sheets']],
    'imageCount': 173, 'boardCount': 29, 'allImagesDirectlyRead': True, 'allBoardsDirectlyRead': True,
    'observations': [{'scene': s, 'observation': t} for s, t in notes],
    'inputLiteralCaptionsAndDiagramsTechnicallyReviewed': True,
    'captionPosition': [960, 970], 'style': 'boxed-white-forest-v1',
    'observedClippingOrDiagramOverlap': False,
    'scope': 'Seven measured silent white cuts with every white caption intersection, paragraph edges and first/middle/last samples; final Nimbus/composite motion remains unreviewed.',
    'allFinalPixelsApproved': False, 'finalVideoApproved': False,
    'humanWholeListening': 'pending', 'allRasterLocalOnly': True, 'newGitImages': 0
})

edge = read(WORK / 'overhead-caption-edge-local-v5/execution.json')
assert edge['exitCode'] == 0 and len(edge['images']) == 14 and len(edge['sheets']) == 3
for r in edge['images'] + edge['sheets']:
    assert sha(ROOT / r['path']) == r['sha256'], r['path']
save(BASE / 'overhead-caption-raw-edge-direct-review-v5.json', {
    'schemaVersion': 1, 'reviewedAt': now,
    'images': [{**r, 'directlyRead': True} for r in edge['images']],
    'boards': [{**r, 'directlyRead': True} for r in edge['sheets']],
    'all14ImagesAnd3BoardsDirectlyRead': True,
    'captionTimingObservation': 'The overhead cue is absent from wall frames32174–32176 and present on overhead32177/32178 onward. The previous wall caption remains on32173 at the ASS centisecond edge.',
    'framingObservation': 'This extraction accidentally omitted the compiled composition crop, so the raw presenter/hotbar remain. Preserve these images as historical raw timing trials; they cannot approve the intended fullscreen framing.',
    'intendedCrop': [0, 0, 1472, 828],
    'framingApproved': False, 'correctedCropTargetRequired': True,
    'finalVideoApproved': False, 'allRasterLocalOnly': True, 'newGitImages': 0
})
print(json.dumps({'whiteImagesRead': 173, 'whiteBoardsRead': 29, 'rawEdgeImagesRead': 14, 'correctedCropRequired': True, 'finalApproved': False}))
