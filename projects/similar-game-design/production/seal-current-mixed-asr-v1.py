"""Seal only the manually compared, current mixed windows and their exact PCM."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time, wave

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
read = lambda path: json.loads(path.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda path: path.relative_to(ROOT).as_posix()


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    temp = path.with_name(path.name + f'.{os.getpid()}.writing')
    for attempt in range(60):
        try:
            temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
            os.replace(temp, path)
            return
        except OSError:
            if attempt == 59:
                raise
            time.sleep(.15)


target = W / 'full-mix-asr-review.json'
assert not target.exists(), 'Read the actual seal; do not repeat a completed review.'
execution_path = W / 'mixed-asr-execution.json'
execution = read(execution_path)
assert execution['exitCode'] == 0 and execution['completed'] == 48
assert read(W / 'mixed-asr-tool-exit-observation-v1.json')['actualToolExitCode'] == 0
result = read(W / 'mixed-asr-v1/asr.json')
progress_path = W / 'mixed-asr-direct-progress.json'
progress = read(progress_path)
decisions_path = W / 'mixed-asr-resolution-direct-review-v1.json'
decisions = read(decisions_path)
mix = read(W / 'mix-settings.json')
assert result['complete'] and len(result['results']) == 48
assert len(progress['windows']) == progress['directlyReadWindowCount'] == 48
assert progress['all48WindowsDirectlyCompared']
assert len({row['label'] for row in progress['windows']}) == 48
assert all(row['expectedFullTextDirectlyRead'] and row['actualFullTextDirectlyRead'] and row['endWordsDirectlyRead'] for row in progress['windows'])
assert decisions['allCurrentWholeAndIndependentTextsDirectlyCompared']
assert not decisions['unresolvedActualContentDefects'] and not decisions['unresolvedTimestampAnomalies']
assert decisions['humanWholeListening'] == decisions['humanPronunciation'] == 'pending'
assert decisions['endingHeuristicUsedForApproval'] is False
assert decisions['priorUnmixedApprovalUsedAsFinalMixApproval'] is False
assert sha(W / 'plan.json') == result['planSha256'] == progress['planSha256'] == mix['planSha256']
assert sha(W / 'final-mix.wav') == result['mixSha256'] == progress['currentMixedAudioSha256'] == mix['wavSha256']
assert sha(W / 'final-mix.m4a') == mix['aacSha256']
assert decisions['currentMixedAudioSha256'] == mix['wavSha256']
compared = {row['label']: row for row in progress['windows']}
windows = []
with wave.open(str(W / 'final-mix.wav'), 'rb') as source:
    assert source.getframerate() == 48000 and source.getnchannels() == 2 and source.getsampwidth() == 2
    assert source.getnframes() == 37098 * 800
    for row in result['results']:
        proof = compared[row['label']]
        path = ROOT / proof['path']
        assert sha(path) == proof['sha256']
        assert read(path) == row and row['expectedWasRecognizerPrompt'] is False
        source.setpos(row['fromSample'])
        pcm = source.readframes(row['toSample'] - row['fromSample'])
        assert len(pcm) == (row['toSample'] - row['fromSample']) * 4
        assert hashlib.sha256(pcm).hexdigest() == row['mixPcmSliceSha256']
        pad = bytes(row['padSamplesEachSide'] * 4)
        padded = pad + pcm + pad
        assert hashlib.sha256(padded).hexdigest() == row['paddedPcmSha256']
        window_path = ROOT / row['windowPath']
        assert sha(window_path) == row['windowSha256']
        with wave.open(str(window_path), 'rb') as window:
            assert window.getframerate() == 48000 and window.getnchannels() == 2 and window.getsampwidth() == 2
            assert window.readframes(window.getnframes()) == padded
        windows.append(dict(label=row['label'], path=proof['path'], sha256=proof['sha256'],
                            expectedKo=row['expectedKo'], actualText=row['text'], directlyCompared=True,
                            entireExpectedAndActualTextDirectlyRead=True, currentMixedPcmSliceSha256=row['mixPcmSliceSha256'],
                            exactCurrentMixedPcmSliceVerified=True, notes=proof['notes'], humanPronunciation='pending'))
assert sum(row['label'].startswith('whole-') for row in windows) == 24
assert sum(row['label'].startswith('context-') for row in windows) == 24
review = dict(schemaVersion=1, slug='similar-game-design', reviewedAt=now(),
              status='approved-current-mixed-content-with-human-listening-pronunciation-pending',
              currentMixedAudioSha256=mix['wavSha256'], currentMixedAacSha256=mix['aacSha256'], planSha256=mix['planSha256'],
              executionPath=rel(execution_path), executionSha256=sha(execution_path),
              directProgress=rel(progress_path), directProgressSha256=sha(progress_path),
              resolutionReview=rel(decisions_path), resolutionReviewSha256=sha(decisions_path),
              all48WindowsDirectlyCompared=True, wholeWindowsDirectlyCompared=24, independentWindowsDirectlyCompared=24,
              all48CurrentMixedPcmSlicesReverified=True, windows=windows,
              observedRecognitionDifferences=decisions['observedRecognitionDifferences'],
              resolvedTimestampArtifacts=decisions['resolvedTimestampArtifacts'], timestampAnomalies=[], unresolvedContentDefects=[],
              technicallyApproved=True,
              approvalScope='Current mixed clause completeness/order/endings and exact sample provenance; pronunciation and human listening remain pending.',
              priorUnmixedApprovalUsedAsFinalMixApproval=False, endingHeuristicUsedForApproval=False,
              expectedWasRecognizerPrompt=False, automaticApproval=False,
              humanWholeListening='pending', humanPronunciation='pending', allFinalPixels=False, qaApproved=False, collected=False, uploaded=False)
save(target, review)
mix.update(currentFinalMixedWindowAsr=rel(target), finalMixedAsrApproved=True)
save(W / 'mix-settings.json', mix)
manifest_path = BASE.parent / 'project.json'
manifest = read(manifest_path)
manifest['paths']['finalMixedAsrReview'] = rel(target)
manifest['approvals']['finalMixedAsr'] = True
manifest['updatedAt'] = now()
save(manifest_path, manifest)
cp_path = BASE / 'latest-checkpoint.json'
cp = read(cp_path)
cp.update(stage='current-mixed-48-directly-compared-awaiting-guarded-pair', recordedAt=now(), finalMixedAsrReview=rel(target),
          finalMixedAsrApproved=True, allFinalPixels=False, qaApproved=False, collected=False, uploaded=False,
          nextAction='One guarded current clean/captioned pair, exact PTS/two decodes/AAC, then all final pixels/QA/collection/private/Git.')
save(cp_path, cp)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
queue = read(qp)
item = next(row for row in queue['items'] if row['slug'] == 'similar-game-design')
item.update(stage=cp['stage'], finalMixedAsrReview=rel(target), finalMixedAsrApproved=True, allFinalPixels=False,
            qaApproved=False, collected=False, uploaded=False, nextAction=cp['nextAction'])
queue['updatedAt'] = now()
save(qp, queue)
print(json.dumps(dict(directWhole=24, directIndependent=24, exactCurrentPcmSlices=48, technicallyApproved=True, humanPronunciation='pending', allFinalPixels=False)))
