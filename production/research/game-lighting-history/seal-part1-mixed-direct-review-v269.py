"""Seal review only from manually recorded complete contexts and exact current PCM."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, psutil
R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(R).as_posix()
binding = lambda p: {'path': rel(p), 'sha256': sha(p)}
plan = P / 'part1-final-input-plan-v240.json'
settings = read(P / 'part1-final-mix-settings-v242.json')
mix = settings['wavSha256']
assert sha(R / settings['wav']) == mix and sha(plan) == settings['planSha256']
progressPath = P / 'part1-final-mixed-asr-direct-progress-v251.json'
progress = read(progressPath)
assert progress['currentMixSha256'] == mix and progress['planSha256'] == sha(plan)
assert progress['allWholeAndIndependentTextsDirectlyCompared'] and progress['allWordEndingsAndTimestampsCompared']
reviewed = {r['label']: r for r in progress['manuallyReadResults']}
main = read(P / 'part1-final-mixed-asr-execution-v243.json')
extra = read(P / 'part1-artifact-context-execution-v255.json')
extraRequest = read(P / 'part1-artifact-context-request-v255.json')
for s in [main, extra]:
    assert s['status'] == 'complete' and s['exitCode'] == 0
    w = s['worker']
    if psutil.pid_exists(w['pid']):
        assert abs(psutil.Process(w['pid']).create_time() - w['createTime']) > .01
assert len(main['results']) == len(reviewed) == 30
for r in main['results']:
    q = reviewed[r['label']]
    assert sha(R / r['path']) == r['sha256'] == q['sha256']
    assert q['expectedParagraphsAndFullActualTextDirectlyRead'] and q['allWordTimestampsDirectlyRead']
extraPath = P / 'part1-artifact-context-direct-review-v270.json'
extraReview = read(extraPath)
assert extraReview['currentMixSha256'] == mix and extraReview['planSha256'] == sha(plan)
assert extraReview['allFullTextsAndTimestampsDirectlyCompared'] and extraReview['allObservedRecognitionConcernsResolved']
assert len(extra['results']) == len(extraRequest['windows']) == len(extraReview['records'])
for r in extra['results']:
    q = next(q for q in extraReview['records'] if q['label'] == r['label'])
    assert sha(R / r['path']) == r['sha256'] == q['sha256']
    assert q['expectedParagraphsAndFullActualTextDirectlyRead'] and q['allWordTimestampsDirectlyRead'] and q['contentApproved']
    assert q['observedResolution'].strip()
pcmPath = P / 'part1-final-mixed-pcm-corroboration-v254.json'
pcm = read(pcmPath)
assert pcm['currentMixSha256'] == mix and pcm['planSha256'] == sha(plan)
assert pcm['allOriginalChapterSamplesPartitionedOnce'] and pcm['allSelectedPcmValuesExact']
assert pcm['all30RecognitionWindowsCurrentMixExact'] and pcm['allAdditionalArtifactContextsCurrentMixExact']
assert pcm['additionalWindowCount'] == len(extra['results'])
resolved = [
    {'main': 'whole-03', 'independent': ['artifact-context-texture-streaming-input'], 'concern': 'Chunk-edge news ending and backward repeat'},
    {'main': 'whole-04', 'independent': ['artifact-context-ordinary-streaming-budget', 'context-texture-scene-return'], 'concern': 'Chunk-edge goodbye/backward repeat and editing/scene lexical variants'},
    {'main': 'whole-05', 'independent': ['context-tsr-silhouette-history', 'context-tsr-rotation-vectors', 'artifact-context-original-18t-3'], 'concern': 'Silhouette chunk-edge repeat and quarter-pixel numerical meaning'},
    {'main': 'whole-06', 'independent': ['artifact-context-outer-comparison-before'], 'concern': 'Boundary-start 자수의 first-syllable recognition'},
    {'main': 'whole-07', 'independent': ['context-geometry-barrier-views', 'artifact-context-07-pre-visibility-interpolation'], 'concern': 'Road-mask goodbye/backward repeat and weighted interpolation values'},
    {'main': 'whole-10', 'independent': ['context-rivalry-mobile-history', 'context-rivalry-surface-observation'], 'concern': 'Zero-duration word insertion, news ending and backward repeat'},
    {'main': 'context-runtime-texture-size', 'independent': ['artifact-context-runtime-texture-consumer'], 'concern': '정보 형식 recognition conflict'}
]
known = set(reviewed) | {r['label'] for r in extraReview['records']}
assert all(all(label in known for label in r['independent']) for r in resolved)
record = {'reviewedAt': datetime.now(timezone.utc).isoformat(), 'currentMixSha256': mix, 'planSha256': sha(plan),
          'directProgress': binding(progressPath), 'artifactContextReview': binding(extraPath), 'pcmCorroboration': binding(pcmPath),
          'mainWindows': 30, 'additionalCompleteContexts': len(extra['results']), 'recognitionConcernResolutions': resolved,
          'allWholeAndIndependentTextsDirectlyCompared': True, 'allWordEndingsAndTimestampsCompared': True,
          'allObservedRecognitionConcernsResolved': True, 'noRemainingContentFailures': True, 'finalMixedAsrApproved': True,
          'approvalScope': 'Current mixed-ASR sentence coverage, independent chunk/semantic checks and exact PCM preservation for private technical review. This is not human listening or pronunciation approval.',
          'remainingPronunciationVariants': [
              {'label': r['label'], 'variants': r.get('recognitionVariants', []), 'humanConcern': r.get('humanPronunciationConcern')}
              for r in progress['manuallyReadResults'] if r.get('recognitionVariants') or r.get('humanPronunciationConcern')],
          'humanWholeListening': 'pending', 'humanPronunciation': 'pending', 'rightsApproved': False,
          'originalNimbusFileVerified': False, 'allFinalPixelsReviewed': False, 'qaApproved': False, 'uploaded': False}
dest = P / 'part1-final-mixed-asr-direct-review-v254.json'
assert not dest.exists(), 'Preserve sealed review; new input needs a new version.'
dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'currentMixedAsrApproved': True, 'mainWindows': 30, 'additionalContexts': len(extra['results']), 'humanListening': 'pending', 'finalPixels': False}))
