"""Seal observed chapter work; prepare remaining pixel review and measured additive allocation.

No synthesis, source acquisition, final approval or platform action is performed here.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, psutil

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'projects/game-lighting-history-04/production'
B = ROOT / 'production/research/game-lighting-history'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()
def write(p, value):
    assert not p.exists(), f'Preserve existing record: {p}'
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
def ref(p): return {'path': rel(p), 'sha256': sha(p)}

ep = B / 'local/episode04-postprocess-encoded-v37/execution.json'
ex = read(ep)
assert ex['status'] == 'encoded-samples-ready'
assert len(ex['items']) == 68 and len(ex['boards']) == 18
reviewed = []
for board in ex['boards']:
    assert sha(ROOT / board['path']) == board['sha256']
    reviewed.append({**board, 'directlyViewed': True, 'reviewedAt': stamp(),
                     'readContinuity': 'All five clean and thirteen captioned boards directly read across preceding/current contexts.'})
record = {
    'reviewedAt': stamp(), 'extraction': ref(ep), 'boards': reviewed,
    'samples': 68, 'allScopedBoardsDirectlyRead': True,
    'scope': 'Only corrected original-22p-1/2 encoded math and their cue/cut boundaries, including neighboring cut samples.',
    'findings': [
        'Input HDR 0–16 and output 0–1 axes are independent and labelled; intermediate values match f(x)=x/(1+x).',
        'Exposure multiplier changes outputs for original x=.25/1/4; tone outputs remain .20/.50/.80 with opacity-only revelation.',
        'At exposure ×2, outputs are .50/2/8. These are independent transformations of the same x, not sequential processing or an Unreal ACES implementation claim.',
        'All reviewed cues remain boxed-white-forest-v1 at 960,970, at most two lines, clear of input labels, values and model geometry.',
    ],
    'unchangedEncodedSampleEvidence': ref(P / 'postprocess-unchanged-sample-review-v38.json'),
    'historicalMathRejectionPreserved': True, 'scopedEncodedSampleClearance': True,
    'allMovingPixelsReviewed': False, 'allFinalPixelsReviewed': False,
    'humanListening': 'pending', 'humanPronunciation': 'pending', 'localOnly': True, 'newGitImages': 0,
}
write(P / 'postprocess-corrected-encoded-direct-review-v39.json', record)
write(B / 'local/episode04-postprocess-encoded-v37/session-resume-v39.json', {
    'observedAt': stamp(), 'sessionId': 82550, 'exitCode': 0, 'terminalCompletionObserved': True,
    'earlierSession': {'sessionId': 56002, 'exitCode': 1, 'error': "KeyError('entryId')", 'cleanImagesPreserved': 18},
    'execution': ref(ep), 'images': 68, 'boards': 18, 'renderRegenerated': False,
})
build = read(P / 'inspection-chapter-review-build-v38.json')
execution = read(P / 'inspection-chapter-review-execution-v38.json')
assert execution['status'] == 'technical-review-pair-ready'
assert build['identicalAacPayloadAndPtsAndDuration']
assert all(x['wholeDecode']['exitCode'] == 0 for x in build['outputs'])
worker = execution['worker']
alive = psutil.pid_exists(worker['pid']) and abs(psutil.Process(worker['pid']).create_time() - worker['createTime']) < .01
assert not alive, 'Wait for actual matching worker exit before extraction.'
write(B / 'local/episode04-inspection-chapter-v38/session.json', {
    'observedAt': stamp(), 'sessionId': 5431, 'exitCode': 0,
    'terminalCompletionObserved': True, 'matchingWorkerAlive': False, 'worker': worker,
    'build': ref(P / 'inspection-chapter-review-build-v38.json'),
    'finalApproved': False,
})

src = (B / 'extract-episode04-postprocess-encoded-v34.py').read_text('utf-8')
src = src.replace('all24 current chapter', 'all69 current inspection chapter')
src = src.replace('postprocess', 'inspection').replace('v34', 'v38')
src = src.replace('N==7637', 'N==20032').replace('len(metrics)==31', 'len(metrics)==69')
start = src.index(' # Both disjoint source intervals:')
end = src.index(' return points', start)
src = src[:start] + ''' # Native interval transitions, code/input annotation starts and tracked UI clearance.
 for native in [c for c in plan['cuts'] if c['kind']=='actual']:
  for localSeconds in [0,.1,.5,1,2,3,4,5,6,6.46,6.48,6.5,7,8,9,10,12,14,(native['frames']-1)/60]:
   frame=native['fromFrame']+round(localSeconds*60)
   if frame<native['toFrame']:add(frame,f"RenderDoc source{native['sourceStart']+localSeconds:.3f}s")
''' + src[end:]
src = src.replace("'next':'Read all24 cues and every cut/annotation board; then remaining38 paragraphs'", "'next':'Directly read all69 cues, every cut and native annotation; preserve final/moving approval false'")
target = B / 'extract-episode04-inspection-encoded-v38.py'
assert not target.exists()
compile(src, str(target), 'exec')
target.write_text(src, 'utf-8')

names = [
    'first-chapter-review-plan-v10', 'upscaling-chapter-review-plan-v13',
    'mobile-chapter-review-plan-v16', 'path-chapter-review-plan-v18',
    'reconstruction-chapter-review-plan-v23', 'megalights-chapter-review-plan-v28',
    'hair-chapter-review-plan-v30', 'dlss-chapter-review-plan-v33',
    'postprocess-chapter-review-plan-v37', 'inspection-chapter-review-plan-v38',
]
rows = []
for name in names:
    path = P / (name + '.json'); plan = read(path)
    totals = plan['totals']
    assert totals['frames'] == totals['actualFrames'] + totals['explanationFrames']
    rows.append({'name': name, 'plan': ref(path), **totals})
N = sum(x['frames'] for x in rows)
A = sum(x['actualFrames'] for x in rows)
E = sum(x['explanationFrames'] for x in rows)
assert (N, A, E) == (100826, 11204, 89622)
parts = []
for i, (lo, hi, title, question) in enumerate([
    (0, 3, '그림자·업스케일링·모바일의 프레임 예산', '부족한 픽셀과 제한된 하드웨어에서 무엇을 계산하고 재사용하는가?'),
    (3, 7, '패스 트레이싱·광원·머리카락의 표본 계산', '경로·광원·가는 기하의 비용과 표본 부족을 어떻게 다루는가?'),
    (7, 10, 'DLSS 5·후처리·프레임 검사', '재구성과 화면 변환 뒤에 어떤 입력·출력과 검증 한계가 남는가?'),
], 1):
    subset = rows[lo:hi]; e = sum(x['explanationFrames'] for x in subset); a = sum(x['actualFrames'] for x in subset)
    parts.append({
        'logicalEpisode': 4, 'physicalPart': i, 'proposedSlug': f'game-lighting-history-04-{i}',
        'titleKo': title, 'viewerQuestion': question, 'preservedChapters': [x['name'] for x in subset],
        'preservedActualFrames': a, 'preservedExplanationFrames': e,
        'minimumAdditionalActualFramesBeforeNewOverviewAndConclusion': round(1.5 * e - a),
        'minimumBodySecondsBeforeNewOverviewAndConclusion': e / 60 / .4,
        'boundary': 'Complete original chapter; no algorithm, existing paragraph or approved PCM is cut.',
        'independentOverviewRequired': i != 1, 'independentConclusionRequired': i != 3,
        'catIntroFrames': 120, 'membershipEndingFrames': 600,
        'independentKoEnCaptionsRequired': True, 'finalTimingApproved': False,
        'actualVideoId': None, 'uploaded': False,
    })
allocation = {
    'preparedAt': stamp(), 'status': 'measured-additive-allocation-not-final-cut-plan',
    'plans': rows, 'preservedFrames': N, 'preservedActualFrames': A, 'preservedExplanationFrames': E,
    'preservedBodySeconds': N / 60, 'currentActualFraction': A / N,
    'minimumAdditionalActualFrames': round(1.5 * E - A),
    'minimumAdditionalActualSeconds': (1.5 * E - A) / 60,
    'minimumTotalBodySecondsBeforeNewOverviewAndConclusion': E / 60 / .4,
    'reason': 'Preserve all accepted explanations and PCM. Add distinct, narrated, concept-matched real game/engine action; never loops, slow-down or unrelated quota.',
    'parts': parts, 'logicalFourEpisodeCoveragePreserved': True,
    'user20MinuteConceptBoundaryInstructionApplied': True,
    'newNativeSelectionComplete': False, 'newNarrationPrepared': False, 'newTtsStarted': False,
    'bodyRatioApproved': False, 'allFinalPixelsReviewed': False, 'uploadReady': False,
}
write(P / 'measured-additive-physical-split-v39.json', allocation)
cp = read(B / 'checkpoint.json')
cp.update({'updatedAt': stamp(), 'stage': 'episode04-all-ten-chapter-pairs-produced-awaiting-inspection-pixels-and-measured-action-expansion'})
cp['episode04PostprocessCorrectedSamplesV39'] = {'record': ref(P / 'postprocess-corrected-encoded-direct-review-v39.json'), 'scopedSampleClearance': True, 'allMovingPixelsReviewed': False, 'allFinalPixelsReviewed': False}
cp['episode04MeasuredPhysicalSplitV39'] = {'record': ref(P / 'measured-additive-physical-split-v39.json'), 'status': allocation['status'], 'bodyRatioApproved': False, 'uploadReady': False}
cp['ownedActiveWork'] = {'status': 'no-active-owned-media-worker', 'next': 'One CPU2 inspection extraction, direct pixels, select new action intervals/paired observation narration, guarded TTS, final measured three-part delivery.'}
tmp = B / 'checkpoint.v39.tmp'
tmp.write_text(json.dumps(cp, ensure_ascii=False, indent=2) + '\n', 'utf-8'); tmp.replace(B / 'checkpoint.json')
print(json.dumps({'postprocessReviewedSamples': 68, 'inspectionWorkerExited': True, 'preservedSeconds': N / 60, 'minimumAdditionalActualSeconds': allocation['minimumAdditionalActualSeconds'], 'physicalParts': len(parts), 'finalApproved': False}))
