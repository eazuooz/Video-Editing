"""Bind seven visual-only repairs to the completed current34 final review."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os, py_compile

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
M = ROOT / 'manim/projects/game-math-orientation-matrices/teaching_caption_clearance_v2.py'
T = O / 'current34-caption-clearance-timing-v2.json'
WORKER = B / 'render-orientation-caption-clearance-v2.py'
rd = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()

def save(p, value):
    temporary = p.with_name(p.name + '.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temporary, p)

assert not T.exists() and not WORKER.exists()
review_path = O / 'current34-final-pixels-partial-direct-review-v1.json'
review = rd(review_path)
assert (review['boardsDirectlyRead'], review['samplesDirectlyRead']) == (792, 3168)
findings_path = O / 'current34-final-pixel-clearance-findings-v1.json'
findings = rd(findings_path)
ids = ['09a', '12', '13a', '16a', '16', '18', '21a']
assert set(ids) == {f['scene'] for f in findings['findings'] if f['severity'] == 'requires_repair'}
for f in findings['findings']:
    if 'proof' in f:
        assert sha(ROOT / f['proof']['path']) == f['proof']['sha256']
plan1 = rd(O / 'current34-detailed-explanation-timing-v1.json')
plan2 = rd(O / 'current34-detailed-header-repair-timing-v2.json')
storage = rd(O / 'measured-manim-timing-v2.json')
assembly = rd(O / 'current34-assembly-inputs-v3.json')
scenes = []
for sid in ids:
    source = storage if sid == '18' else plan2 if sid == '16' else plan1
    slot = copy.deepcopy(next(s for s in source['scenes'] if s['id'] == sid))
    piece = next(p for p in assembly['pieces'] if p['id'] == sid)
    assert slot['frames'] == piece['frames']
    assert sha(ROOT / piece['path']) == piece['sha256']
    if 'voice' not in slot:
        slot['voice'] = 'shared/output/narration/game-math-orientation-matrices/qwen3-1.7b-balanced-v1/chunks/18-scene.wav'
        slot['voiceSha256'] = sha(ROOT / slot['voice'])
    assert sha(ROOT / slot['voice']) == slot['voiceSha256']
    slot['retainedVideo'] = piece['path']
    slot['retainedVideoSha256'] = piece['sha256']
    slot['onlyFixedExplanationLabelPositionsChanged'] = True
    scenes.append(slot)
assets = [M, *[ROOT / 'manim/projects/game-math-orientation-matrices' / name for name in
    ['teaching_revision_detailed_v1.py', 'teaching_revision_v2.py',
     'teaching_baseline_detailed_v1.py', 'teaching_baseline_detailed_v2.py',
     'detailed_subjects_v1.py', 'detailed_camera_subject_v1.py']]]
plan = dict(preparedAt=now(), visualOnly=True, code=rel(M), codeSha256=sha(M),
    assets=[dict(path=rel(p), sha256=sha(p)) for p in assets], scenes=scenes,
    findings=rel(findings_path), findingsSha256=sha(findings_path),
    finalReview=rel(review_path), finalReviewSha256=sha(review_path),
    bodyRatioAndTimingPreserved=True, fixedCaptionCenter=[960, 970],
    newTts=0, newAsr=0, newMix=0, finalMovingPixelsApproved=False,
    finalCaptionPixelsApproved=False, normalPlaybackApproved=False,
    pendingGameplayClearanceScene='07b', mainPromotion=False)
worker = (B / 'render-orientation-detailed-header-repair-v2.py').read_text('utf-8')
replacements = {
    'current34-detailed-header-repair-v2': 'current34-caption-clearance-v2',
    'teaching_detailed_header_repair_v2.py': M.name,
    'current34-detailed-header-repair-timing-v2.json': T.name,
    'current34-detailed-header-repair-render-execution-v2.json': 'current34-caption-clearance-render-execution-v2.json',
    "assert len(plan['scenes'])==11": "assert len(plan['scenes'])==7",
    'rendering-eleven-detailed-current34-explanations': 'rendering-seven-caption-clearance-current34-explanations',
    'Directly inspect all11 detailed explanation renders and normal1x playback; preserve current AAC/cues and remaining guide review. Only update assembly after detailed visual approvals.':
    'Review all7 newly repaired moving scenes and captioned bindings; retain completed792-board review, current AAC/cues and original renders. Assess07b wing clearance; no main promotion before all final QA.',
    'rendered-current34-detailed-explanations-awaiting-direct-pixel-review': 'rendered-current34-caption-clearance-awaiting-direct-pixel-review',
    'failed-current34-detailed-render-preserve-history': 'failed-current34-caption-clearance-preserve-history',
}
for before, after in replacements.items():
    assert before in worker, before
    worker = worker.replace(before, after)
worker = worker.replace('"""Single CPU2 render for three overview/conclusion depth repairs; no main promotion."""',
    '"""Single CPU2/GPU0 batch for seven evidenced caption-clearance repairs."""')
WORKER.write_text(worker, 'utf-8')
py_compile.compile(str(WORKER), doraise=True)
py_compile.compile(str(M), doraise=True)
save(T, plan)
for f in findings['findings']:
    if f['severity'] == 'requires_repair':
        f['currentPreparedCode'] = dict(path=rel(M), sha256=sha(M), className='DetailedScene' + f['scene'],
            timing=rel(T), preparationOnly=True, renderExecuted=False, repairedPixelsReviewed=False)
findings.update(updatedAt=now(), allPlannedFinalSamplesDirectlyRead=True,
    sampleCount=3168, boardCount=792, next='Render and directly review only the seven evidenced explanation-label repairs; assess07b wing framing. Preserve completed source/audio/render QA.')
save(findings_path, findings)
complete = dict(recordedAt=now(), review=rel(review_path), reviewSha256=sha(review_path),
    all3168PlannedSamplesDirectlyRead=True, all792BoardsDirectlyRead=True,
    findings=rel(findings_path), findingsSha256=sha(findings_path),
    sevenExplanationScenesHeld=True, gameplayClearancePending='07b',
    all244CuePixelsApproved=False, allFinalSelectedSamplesApproved=False,
    allIntermediateFramesApproved=False, humanListeningApproved=False,
    mainPromotion=False, newTts=0, newAsr=0, newMix=0,
    next='Only targeted visual repairs and their new moving/captioned review; completed finalV3 review is not repeated.')
save(O / 'current34-final-pixels-complete-held-direct-review-v1.json', complete)
cp_path = O / 'latest-checkpoint.json'
cp = rd(cp_path)
assert cp['activeOwnedWorkers'] == 0
cp.update(recordedAt=now(), stage='current34-final-pixels-complete-held-targeted-clearance',
    finalPixelCompleteHeldReview=rel(O / 'current34-final-pixels-complete-held-direct-review-v1.json'),
    finalPixelClearanceFindings=rel(findings_path), captionClearanceTiming=rel(T),
    next=complete['next'])
save(cp_path, cp)
qp = B / 'queue.json'
old = qp.read_bytes()
q = rd(qp)
q['currentOrientationReview'].update(stage=cp['stage'],
    finalPixelCompleteHeldReview=cp['finalPixelCompleteHeldReview'],
    finalPixelClearanceFindings=rel(findings_path), captionClearanceTiming=rel(T), next=cp['next'])
q['updatedAt'] = now()
assert qp.read_bytes() == old
save(qp, q)
print(json.dumps(dict(preparedScenes=ids, worker=rel(WORKER), timing=rel(T),
    allFinalPixelsApproved=False, newAudio=0)))
