"""Persist the completed direct comparisons; keep candidate/final scope separate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
now = datetime.now(timezone.utc).isoformat()
joins = read(BASE / 'guided-joins-asr-execution-v3.json')
assert joins['exitCode'] == 0 and len(joins['results']) == 6
notes = {
    '02-p4-p5-current-join': 'Both complete base sentences and the wall-side approach/turn/direct-attack guide retain meaning/order/end. Joined 벽장치 and 적어보세요 are spacing differences.',
    '06-p4-p6-current-join': 'The two complete base sentences and both complete guides retain meaning/order/end. 뒤의 was transcribed 뒤에; 미리보기 was split. Particle/pronunciation remains pending.',
    '13-p1-p2-current-join': 'The guide onset reads 적이 and its full sentence matches. The broad context writes an extra 자 at the unchanged base-clip onset and gives 같은 zero duration. Preserve that artifact; the earlier whole base PCM and independent padded guide comparisons support meaning. Do not copy the artifact into captions or approve human pronunciation.',
    '13-p3-p5-current-join': 'The complete base paragraph and both distance/close-purple/separate-distant guides retain all sentences in order; 옮겨 다니며 spacing differs.',
    '12-p2-p4-current-join': 'The complete preparation paragraph and selection/orientation plus separate-high-position combat guides retain order/end; 미리보기 spacing differs.',
    '12-p4-p6-current-join': 'The complete high-position guide and both original conclusion paragraphs retain meaning/order/end. 세 is transcribed 3 and 계속 하게 is joined. Numerical spelling and spacing do not change the three-question conclusion.'
}
rows = []
for r in joins['results']:
    assert sha(ROOT / r['audio']) == r['audioSha256']
    assert sha(ROOT / r['contextAudio']) == r['contextSha256']
    result = BASE / 'asr-guided-joins-local-v3' / (r['id'] + '.json')
    rows.append({**r, 'directReview': True, 'technicalReview': True,
                 'allTextAndWordTimestampsDirectlyCompared': True,
                 'resultPath': result.relative_to(ROOT).as_posix(),
                 'resultSha256': sha(result), 'comparison': notes[r['id']],
                 'scope': 'Unmixed lossless inspection PCM; final Nimbus mixed chapter remains unreviewed.'})
save(BASE / 'guided-joins-direct-review-v3.json', {
    'schemaVersion': 1, 'reviewedAt': now, 'executionSha256': sha(BASE / 'guided-joins-asr-execution-v3.json'),
    'rows': rows, 'allSixContextsDirectlyCompared': True,
    'allWordTimestampsDirectlyCompared': True, 'wordCount': sum(len(r['words']) for r in rows),
    'expectedWasRecognizerPrompt': False, 'technicalCandidateJoinReview': True,
    'baseOnsetRecognizerArtifactPreserved': True,
    'humanWholeListening': 'pending', 'humanPronunciation': 'pending',
    'finalMixBuilt': False, 'finalMixAsrApproved': False, 'newGitImages': 0})
save(BASE / 'guided-joins-asr-session-v3.json', {
    'schemaVersion': 1, 'sessionId': 34367, 'observedPid': 38132,
    'worker': 'projects/making-game-sequels/production/review-guided-joins-v3.py',
    'startedAt': joins['startedAt'], 'endedAt': joins['endedAt'],
    'exitCode': 0, 'sessionClosed': True, 'cpuJobs': 0, 'gpuJobs': 0,
    'directReview': 'projects/making-game-sequels/production/guided-joins-direct-review-v3.json',
    'doNotRepeatCompletedWorker': True})

pixels = read(BASE / 'measured-edit-v3/guided-cue-review-local-v3/execution.json')
assert pixels['exitCode'] == 0 and len(pixels['images']) == 528 and len(pixels['sheets']) == 88
assert sha(BASE / 'measured-edit-v3/plan.json') == pixels['planSha256']
assert sha(BASE / 'measured-edit-v3/caption-layout-v3.json') == pixels['captionLayoutSha256']
for row in pixels['images'] + pixels['sheets']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
ranges = [
    (1, 8, 'Wall preview/panel, floor-device selection and combat routes are visible above the fixed box. Sell/NotEnoughMoney are not sale/effect proof. Trimmed rail no longer obscures the onset. Source50 foreground beam does not hide all visible targets; do not approve unseen hits.'),
    (9, 16, '02-g1 starts on bridge/steps for about3.3s before the short wall-spray shot. This literal wall-side guide needs a source-placement correction. Preserve audio and total good explanation; no final alignment approval. Spike/Spring selections and blocked indications are distinct.'),
    (17, 24, 'Direct close combat and floor/wall effects remain visible. Device names/preview/Sell prompts do not prove a completed installation or sale. Short handoffs belong to the observed action.'),
    (25, 36, '06-g1 shows aiming/retreat/effects. 06-g2 rotates/moves a green preview; the blocked-indication sentence refers to the immediately preceding blocked preview, not a claim that the current green preview is blocked. Both preparation shots must retain their context.'),
    (37, 52, '49 zoom enlarges approaching targets/aim while retaining active projectiles; upper beam remains. 50 smoke/beam briefly obscures combat naturally; do not infer hidden hits. Separate near/far intervals remain explicitly separate.'),
    (53, 64, 'Near purple attacks, a following separate distant-route shot, body turn and far aim/crowd are visible above the box. Natural beam/smoke remains; no hidden-target or continuous-pursuit inference.'),
    (65, 72, '08 lowercrop keeps the resource counter visible through15000/13800/13000/11800/11000/9800/11000/10200 observations. No universal cost/effect claim. Blue ReadyUp paths remain preparation. 12 overhead caption begins roughly2 output frames before the overhead shot; preserve as a target boundary follow-up.'),
    (73, 80, 'Overhead orientation and floor/wall selection previews remain readable. 12-g1 selection follows the immediately preceding wall-orientation observation; the literal orientation clause needs its transition context retained. 12-g2 uses separate high-position combat, not ReadyUp enemies.'),
    (81, 88, 'High-position aiming, moving targets, firing effects and the general three-question conclusion remain readable. Brief normal-speed observation follows guidance; no final quota approval from active samples alone.')
]
save(BASE / 'guided-native-caption-direct-review-v3.json', {
    'schemaVersion': 1, 'reviewedAt': now, 'planSha256': pixels['planSha256'],
    'captionLayoutSha256': pixels['captionLayoutSha256'],
    'sourceExecution': 'projects/making-game-sequels/production/measured-edit-v3/guided-cue-review-local-v3/execution.json',
    'sourceExecutionSha256': sha(BASE / 'measured-edit-v3/guided-cue-review-local-v3/execution.json'),
    'imageCount': 528, 'boardCount': 88, 'cutCount': 61,
    'allImagesDirectlyRead': True, 'allBoardsDirectlyRead': True,
    'images': [{**r, 'directlyRead': True, 'finalApproved': False} for r in pixels['images']],
    'boards': [{**r, 'directlyRead': True} for r in pixels['sheets']],
    'observations': [{'boards': [a, b], 'observation': t} for a, b, t in ranges],
    'captionPosition': [960, 970], 'style': 'boxed-white-forest-v1',
    'allFinalCompositePixelsApproved': False, 'finalTimingApproved': False,
    'framingApproved': False, 'bodyRatioApproved': False,
    'requiredCorrection': '02-g1 wall-side approach guide starts about3.3s before its wall-spray shot. Review reassignment of existing unique wall combat and the recipient battle narration; do not duplicate intervals, change voice, move captions or silently approve the bridge.',
    'scope': 'Native/caption trials at selected word/cue/boundary/half-second anchors, not full final motion or final MC/Nimbus composition.',
    'allImagesLocalOnly': True, 'newGitImages': 0})
print(json.dumps({'joinContexts': 6, 'words': sum(len(r['words']) for r in rows), 'pixelImages': 528, 'boards': 88, 'requiredCorrection': '02 wall-side guide source placement', 'finalApproved': False}))
