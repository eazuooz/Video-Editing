"""Seal the explicitly completed text comparison and verify current mix slices.

This records a human-directed technical content decision, not an automatic ASR
or pronunciation approval. The original recognizer results remain unchanged.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time, wave

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, data):
    temporary = p.with_name(p.name + f'.{os.getpid()}.writing')
    for attempt in range(60):
        try:
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
            os.replace(temporary, p)
            return
        except OSError:
            if attempt == 59: raise
            time.sleep(.15)

assert not (W / 'full-mix-asr-review.json').exists(), 'Do not repeat a sealed review.'
execution = read(W / 'mixed-asr-execution.json')
settings = read(W / 'mix-settings.json')
asr = read(W / 'mixed-asr-v1/asr.json')
assert execution['exitCode'] == 0 and execution['completed'] == 32 and asr['complete']
assert len(asr['results']) == 32 and len({x['label'] for x in asr['results']}) == 32
assert settings['wavSha256'] == sha(W / 'final-mix.wav') == asr['mixSha256']
assert settings['planSha256'] == sha(W / 'plan.json') == asr['planSha256']

# The expected and entire actual strings for all32 were directly read before
# this recorder was written. Keep every observed recognition difference.
differences = [
    dict(scene='01-overview', difference='Independent context 가우스→가오스; current whole mix reads 가우스.', resolution='Whole/context recognizer disagreement; name pronunciation remains pending.'),
    dict(scene='02-visible-effects', difference='경로의→경로에, 바닥에→바닥의 in whole/context.', resolution='Full movement/area/selection clauses retained; particle pronunciation pending.'),
    dict(scene='10-origin-effect-target-guide', difference='Whole 단테→단태, 내 게임의→내 게임에; context reads 내 게임의.', resolution='Action and origin/direction/target clauses retained. Context does not cover p1 name; do not claim it resolves that pronunciation.'),
    dict(scene='11-jade-ground-and-height-guide', difference='바닥에→바닥의, 앞의→앞에 in whole/context.', resolution='Ground/height/target distinction and unsupported-equipment caveat retained; particles pending.'),
    dict(scene='12-nearby-space-guide', difference='화면의→화면에 in whole/context.', resolution='Moving centre/nearby target/spatial relationship and no-ranking caveat retained; particle pending.'),
    dict(scene='13-doorway-comparison-guide', difference='Whole 단테→단태; 같게→갖게 in whole/context.', resolution='Condition-controlled comparison and no-performance-ranking caveat retained; name/word pronunciation pending.'),
    dict(scene='14-purpose-before-options-guide', difference='Whole 단테→단태; independent p3-4 excludes name.', resolution='Purpose/action/options/test flow and missing-before-after caveat retained; name pronunciation pending.'),
    dict(scene='06-quick-trial', difference='Context 부활→도할; whole reads 부활. 닿는→닫는 in both; whole 앞의→앞에.', resolution='Current whole/context agree on approach/progress/recovered ally and complete trial/return flow; 부활 recognizer disagreement preserved, pronunciation pending.'),
    dict(scene='15-task-and-result-guide', difference='Whole 단테→단태 and 뒤의→뒤에; context reads 단테 and 뒤의. Whole 닿는→닫는.', resolution='Current context resolves name/particle readback, supporting/attack target and completion distinction intact; human pronunciation pending.'),
    dict(scene='16-action-versus-expression-guide', difference='앞에서→앞에 in both; context 대상 쪽으로→대상적으로; whole reads 대상 쪽으로; whole 앞의→앞에.', resolution='Current whole/context recognizer disagreement preserved; full action/direction/expression distinction and complete transition retained. Same contextual disagreement existed in repaired unmixed PCM; not treated as a new audio edit.'),
]
windows = []
timestamp_anomalies = []
with wave.open(str(W / 'final-mix.wav'), 'rb') as mix:
    assert mix.getframerate() == 48000 and mix.getnchannels() == 2 and mix.getsampwidth() == 2
    for result in asr['results']:
        path = W / 'mixed-asr-v1' / (result['label'] + '.json')
        assert read(path) == result and not result['expectedWasRecognizerPrompt']
        mix.setpos(result['fromSample'])
        current_pcm = mix.readframes(result['toSample'] - result['fromSample'])
        with wave.open(str(ROOT / result['windowPath']), 'rb') as window:
            window_pcm = window.readframes(window.getnframes())
        assert window_pcm == current_pcm
        assert hashlib.sha256(current_pcm).hexdigest() == result['mixPcmSliceSha256']
        assert sha(ROOT / result['windowPath']) == result['windowSha256']
        previous_end = 0
        for word in result['words']:
            start, end = word['timestamp']
            if start is None or end is None or end < start or start < previous_end - .3:
                timestamp_anomalies.append(dict(label=result['label'], word=word, previousEnd=previous_end))
            if end is not None: previous_end = end
        windows.append(dict(label=result['label'], path=path.relative_to(ROOT).as_posix(), sha256=sha(path),
            expectedKo=result['expectedKo'], actualText=result['text'], directlyCompared=True,
            entireExpectedAndActualTextDirectlyRead=True, exactCurrentMixedPcmSliceVerified=True,
            currentMixedPcmSliceSha256=result['mixPcmSliceSha256'], fullClausesAndEndingRetained=True,
            noConfirmedOmissionRepetitionOrInventedGreeting=True, humanPronunciation='pending'))
assert not timestamp_anomalies
review = dict(schemaVersion=1, slug='player-customization', reviewedAt=now(),
    status='approved-current-mixed-content-with-human-listening-pronunciation-pending',
    currentMixedAudioSha256=settings['wavSha256'], currentMixedAacSha256=settings['aacSha256'],
    planSha256=settings['planSha256'], executionPath='projects/player-customization/production/final-v1/mixed-asr-execution.json',
    executionSha256=sha(W / 'mixed-asr-execution.json'), all32WindowsDirectlyCompared=True,
    wholeWindowsDirectlyCompared=16, independentWindowsDirectlyCompared=16,
    all32CurrentMixedPcmSlicesReverified=True, windows=windows, observedRecognitionDifferences=differences,
    timestampAnomalies=timestamp_anomalies, unresolvedContentDefects=[], technicallyApproved=True,
    approvalScope='Current mixed content completeness/ordering/ending and exact sample provenance. Pronunciation and human listening are separate pending reviews.',
    priorUnmixedApprovalUsedAsFinalMixApproval=False, endingHeuristicUsedForApproval=False,
    expectedWasRecognizerPrompt=False, automaticApproval=False, humanWholeListening='pending',
    humanPronunciation='pending', allFinalPixels=False, qaApproved=False, collected=False, uploaded=False)
save(W / 'full-mix-asr-review.json', review)
progress = read(W / 'mixed-asr-direct-progress.json')
progress.update(updatedAt=now(), windows=windows, readCount=32, wholeReadCount=16, contextReadCount=16,
    all32WindowsDirectlyCompared=True, technicallyApproved=True, finalMixedAsrApproved=True,
    currentObservedDifferences=differences, sealedReview='projects/player-customization/production/final-v1/full-mix-asr-review.json')
save(W / 'mixed-asr-direct-progress.json', progress)
cp_path = BASE / 'latest-checkpoint.json'; cp = read(cp_path)
cp.update(recordedAt=now(), stage='current-final-mixed-content-reviewed-awaiting-pair',
    finalMixedAsrApproved=True, finalMixedAsrReview='projects/player-customization/production/final-v1/full-mix-asr-review.json',
    nextAction='Fresh resource check, guarded current clean/captioned pair once; then all final cue/cut/spatial pixels and QA before collect/private/Git.')
save(cp_path, cp)
queue_path = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'; queue = read(queue_path)
item = next(x for x in queue['items'] if x['slug'] == 'player-customization')
item.update(stage=cp['stage'], finalMixedAsrApproved=True, finalMixedAsrReview=cp['finalMixedAsrReview'], nextAction=cp['nextAction'])
queue['updatedAt'] = now(); save(queue_path, queue)
print(json.dumps(dict(all32DirectlyCompared=True, exactCurrentPcmSlices=32, technicalContentApproved=True,
    humanListening='pending', humanPronunciation='pending', finalPixels=False)))
