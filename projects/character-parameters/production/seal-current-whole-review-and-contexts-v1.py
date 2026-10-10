"""Seal explicitly reviewed full texts and manually selected intact PCM boundaries.

This does not grant voice, final mix, timing, pronunciation or pixel approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, wave
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
state = read(BASE / 'current-whole-asr-execution-v1.json')
assert state['exitCode'] == 0 and state['actualExitObserved'] and state['actualOuterExitCode'] == 0
assert state['completed'] == state['total'] == 12
review_path = BASE / 'current-whole-direct-review-v1.json'
plan_path = BASE / 'current-independent-context-plan-v1.json'
assert not review_path.exists() and not plan_path.exists(), 'Preserve actual reviews; never repeat them'
# Actual displayed word pairs and displayed 10ms PCM bins, manually read.
starts = [3.89, 8.19, 9.95, 8.80, 9.00, 8.83, 8.56, 9.57, 9.97, 7.72, 9.65, 9.67]
observations = [
    'All three overview sentences are represented, including question, ordered examples and benefit; only punctuation/spacing differ. Actual15.680041666667s, not reported as20–30s or padded.',
    'All three common-action/comparison/choice paragraphs are represented. Punctuation and spacing differ only.',
    'Fire/water/space rules, both named characters and complete design advice are represented; no recognized sentence loss/repetition.',
    'Two figures/smoke, opponent judgment and separate appearance/hit judgment/counterplay cautions are fully represented; spacing differs only.',
    'All ground/air/space and usable-strength advice is represented. 가까이 붙어 became 가까이부터 at19.00–19.66; retain lexical uncertainty for complete independent context and human pronunciation.',
    'All four role/weakness/counterplay/player-versus-enemy paragraphs are represented. ASR word clocks overlap 연결됩니다./플레이어 at28.24–28.42; this is not proof of overlapping audio. Independent context changes the recognizer window and preserves complete p2–p4.',
    'Full distinction among current damage, basic performance, effects and judgment, plus historical-source caution is represented. 퍼센트 is rendered as%; 한 순간의 became 한순간에; 뒤섞게 became 지석게. Retain lexical/particle uncertainty for complete independent context and human pronunciation.',
    'Named REACT/STEAL/STUN, separated shots and current-turn versus permanent-stat claims are represented. 맞힌/마친, 장면이므로/장면임으로, 읽지는/익지는, 영구/연구 remain lexical/particle uncertainties; do not silently approve them. Word clock26.58–26.70 overlap and recognizer warning are preserved without claiming audio truncation.',
    'SNIPE next-turn two-dice/not-immediate-six distinction, separate STRIKE and trigger/target/time advice are represented. 두/여섯 become2/6 equivalently; 구현 became구형 at24.48–24.90 and needs independent context/human pronunciation.',
    'All fairness/average/repeated-condition/role-preservation advice is represented. 경기의 became경기에; preserve particle uncertainty for independent context/human pronunciation.',
    'All condition/state/transition/test-question and role-sentence advice is represented. Punctuation/spacing differ only. ASR word clocks overlap있는가?/이 at27.24–27.30; not proof of audio overlap.',
    'All three complete conclusions preserve common rules, role/condition/time distinctions and the role sentence. 능력치 표 became능력 지표 at22.36–23.50; preserve lexical uncertainty for independent complete context and human pronunciation. Full original ending is represented.',
]
assert all(x is not None for x in starts) and 'PENDING_DIRECT_REVIEW' not in observations
asr = read(BASE / 'current-whole-asr-v1/asr.json')
assert asr['complete'] and len(asr['results']) == 12
stamp = datetime.now(timezone.utc).isoformat()
rows, contexts = [], []
for i, result in enumerate(asr['results']):
    source = ROOT / result['sourcePath']
    result_path = BASE / 'current-whole-asr-v1' / (result['id'] + '.json')
    assert sha(source) == result['sourceSha256'] and not result['expectedWasRecognizerPrompt']
    words = result['words']
    assert words
    with wave.open(str(source), 'rb') as wav:
        assert (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) == (24000, 1, 2)
        total = wav.getnframes()
        pcm = wav.readframes(total)
    assert total == result['sourceSamples']
    n = round(starts[i] * 24000)
    assert 0 < n < total
    bins = np.frombuffer(pcm[max(0,n-120)*2:(n+120)*2], dtype='<i2').astype(float)
    boundary = dict(startSample=n, startSeconds=n/24000, endSample=total,
                    endSeconds=total/24000, displayed10msPcmBinRead=True,
                    boundary10msRms=float(np.sqrt(np.mean(bins*bins))),
                    boundary10msPeak=int(np.max(np.abs(bins))),
                    fullOriginalEndingRetained=True,
                    selectedAfterCompleteParagraph=1,
                    wordTimestampsAreRecognizerEstimates=True)
    assert boundary['boundary10msRms'] < 100 and boundary['boundary10msPeak'] < 350
    overlaps = [dict(previous=a, following=b) for a,b in zip(words, words[1:])
                if a['timestamp'][1] is not None and b['timestamp'][0] is not None
                and a['timestamp'][1] > b['timestamp'][0] + .001]
    missing = [word for word in words if None in word['timestamp']]
    rows.append(dict(id=result['id'], resultPath=rel(result_path), resultSha256=sha(result_path),
                     sourcePath=result['sourcePath'], sourceSha256=result['sourceSha256'],
                     expectedKo=result['expectedKo'], actualText=result['text'],
                     directExpectedAndEntireActualRead=True, allWordTimestampsRead=True,
                     observation=observations[i], recognizedWholeSentenceOmission=False,
                     recognizedWholeSentenceRepetition=False, inventedGreeting=False,
                     estimatedWordClockOverlaps=overlaps, missingWordClockEndpoints=missing,
                     independentContextBoundary=boundary, humanPronunciation='pending'))
    contexts.append(dict(id=result['id']+'-complete-p2-to-end', sourcePath=result['sourcePath'],
                         sourceSha256=result['sourceSha256'], startSample=n, endSample=total,
                         zeroPaddingSamplesEachSide=6000, expectedKo=result['expectedKo'][1:],
                         completeParagraphs=list(range(2,len(result['expectedKo'])+1)),
                         boundaryEvidence=boundary,
                         purpose='Independent complete p2-through-ending; all original PCM bytes retained. Expected text is review metadata only.'))
review = dict(schemaVersion=1, slug='character-parameters', reviewedAt=stamp,
              actualOuterExitCode=0, actualOuterSession=57058,
              completeScenes=12, completeParagraphs=37, currentRawNarrationSeconds=347.600041666667,
              overviewSeconds=15.680041666667, overviewPlannedTargetSeconds=[20,30],
              overviewPreservesNaturalThreeSentences=True, overviewPaddedOrSlowed=False,
              allWholeTextsDirectlyCompared=True, rows=rows,
              independentContextsApproved=False, currentVoiceApproved=False,
              finalMixedAsrApproved=False, finalTimingApproved=False, allFinalPixels=False,
              humanListening='pending', humanPronunciation='pending',
              endingHeuristicUsedForApproval=False, currentPcmChanged=False,
              automaticApproval=False)
review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n','utf-8')
plan = dict(schemaVersion=1, createdAt=stamp, wholeReview=rel(review_path), wholeReviewSha256=sha(review_path),
            contextCount=12, contexts=contexts, boundariesDirectlyComparedWithCurrentWordsAndPCM=True,
            sourcePcmChanged=False, expectedWasRecognizerPrompt=False, automaticApproval=False,
            humanListening='pending', humanPronunciation='pending')
plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n','utf-8')
print(json.dumps(dict(wholeReview=rel(review_path), contexts=12, voiceApproved=False),ensure_ascii=False))
