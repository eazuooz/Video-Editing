"""Seal the directly read whole texts and complete, sample-exact contexts.

This records agent text/word/PCM-boundary review, not human listening or
pronunciation approval. The recognizer is never given the expected text.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time, wave
import numpy as np
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def save(p, d):
    temp = p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    for i in range(40):
        try: os.replace(temp, p); return
        except OSError:
            if i == 39: raise
            time.sleep(.15)
now = datetime.now(timezone.utc).isoformat()
state_path = BASE/'current-whole-asr-execution-v1.json'
state = read(state_path)
assert state['exitCode'] == 0 and state['completed'] == state['total'] == 10
try:
    p = psutil.Process(state['pid'])
    assert abs(p.create_time()-state['createTime']) >= .01, 'Owned recognizer still alive.'
    reused = True
except psutil.NoSuchProcess:
    reused = False
completion = dict(observedAt=now, sessionId=53793, pid=state['pid'], createTime=state['createTime'],
    actualWorkerAlive=False, pidReused=reused, completedResults=10,
    workerReportedExitCode=0, workerFinishedAt=state['finishedAt'],
    sessionClosureObserved=True, outerShellExitCodeObserved=None,
    observation='write_stdin drained all ten results; a subsequent read returned Unknown process id. CIM found no matching worker. The worker completion state reports exitCode 0; no separate shell exit value was returned.')
session_path = BASE/'current-whole-asr-execution-v1.session.json'
session = read(session_path)
session.update(workerExpectedRunning=False, actualExitObserved=True, exitCode=0,
               exitCodeEvidence='worker completion state plus closed session and matching worker absence',
               outerShellExitCodeObserved=None, completionObservation=completion)
save(session_path, session)
state.update(actualExitObserved=True, actualWorkerAlive=False, completionObservation=completion)
save(state_path, state)

starts = [3.395, 4.735, 2.835, 5.485, 4.945, 3.775, 4.315, 6.695, 4.46, 5.69]
gaps = [(3.3,3.5),(4.52,5.04),(2.66,2.88),(5.2,5.56),(4.64,4.96),
        (3.64,3.82),(4.2,4.36),(6.48,6.72),(4.24,4.52),(5.54,5.74)]
observations = [
    'All three overview sentences are represented. 지운 줄 수 became 지훈줄수 at 5.06–5.82; preserve this phonetic recognition difference for independent context and human pronunciation review.',
    'All three paragraphs are represented; punctuation and 줄 수 spacing differ only. No missing or repeated sentence is indicated.',
    'The question, equal-count/different-evaluation distinction and final design advice are represented; spacing differs.',
    '티 스핀 더블/백 투 백 are recognized in English spelling. 배점표 became 배전표 at 14.44–15.04; independent complete context is needed before interpreting this as a voice error.',
    'Both current-action and retained-total roles, and the complete concluding sentence, are represented.',
    '스물일곱/이천구백이십/백사십일 are recognized as 27/2920/141. 줄을 became 주를 and 중의 became 중에; keep number correctness separate from particle/phonetic uncertainty.',
    'Names, quantity versus overall evaluation, units and direction of better values are represented; spacing differs.',
    'The two calculation observations and full cautions are represented. 기여를 became 기어를 at 15.90–16.20; preserve it for independent context and human pronunciation review.',
    'Persistent quantities and transient notices, their reading roles, and the full final advice are represented. 행동의 became 행동에 at 7.82–8.24; preserve particle uncertainty.',
    'All three closing questions, the actual-example recap and complete coaching sentence are represented. No invented greeting or replacement ending is indicated.'
]
whole_rows, contexts = [], []
result_paths = sorted((BASE/'current-whole-asr-v1').glob('[0-9]*.json'))
assert len(result_paths) == 10
for i, path in enumerate(result_paths):
    d = read(path); source = ROOT/d['sourcePath']; assert sha(source) == d['sourceSha256']
    assert not d['expectedWasRecognizerPrompt']
    words = d['words']; assert words and all(w['timestamp'][0] is not None and w['timestamp'][1] is not None for w in words)
    assert all(a['timestamp'][1] <= z['timestamp'][0]+.001 for a,z in zip(words, words[1:]))
    a = round(starts[i]*24000)
    with wave.open(str(source), 'rb') as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (24000,1,2)
        end = w.getnframes(); pcm = w.readframes(end)
    assert end == d['sourceSamples']
    samples = np.frombuffer(pcm, dtype='<i2')
    near = samples[a-120:a+120].astype(float)
    boundary = dict(startSample=a, startSeconds=a/24000, endSample=end, endSeconds=end/24000,
        firstSentenceAsrEnd=gaps[i][0], nextCompleteParagraphAsrStart=gaps[i][1],
        boundary20msRms=round(float(np.sqrt(np.mean(near*near))),3),
        boundary20msPeak=int(np.max(np.abs(near))),
        inspected10msPcmBins=True, fullFinalWordPreserved=True,
        finalRecognizedWord=words[-1], sourceSampleCount=end)
    whole_rows.append(dict(id=d['id'], path=rel(path), sha256=sha(path), expectedKo=d['expectedKo'],
        actualText=d['text'], sourceSha256=d['sourceSha256'], directExpectedAndEntireActualRead=True,
        allWordTimestampsRead=True, observation=observations[i], boundary=boundary,
        noRecognizedWholeSentenceOmission=True, noRecognizedWholeSentenceRepetition=True,
        noRecognizedInventedGreeting=True, humanPronunciation='pending'))
    contexts.append(dict(id=d['id']+'-complete-p2-p3', sourcePath=d['sourcePath'],
        sourceSha256=d['sourceSha256'], startSample=a, endSample=end,
        zeroPaddingSamplesEachSide=6000, expectedKo=d['expectedKo'][1:],
        completeParagraphs=[2,3], boundaryEvidence=boundary,
        purpose='Independent complete second/third paragraphs and original ending; expected text is review metadata only.'))
review_path = BASE/'current-whole-direct-review-v1.json'
assert not review_path.exists()
review = dict(schemaVersion=1, slug='presenting-game-scores', reviewedAt=now,
    completionObservation=completion, currentRawNarrationSeconds=195.2,
    overviewSeconds=16.96, overviewPlannedTargetSeconds=[20,30],
    overview='Three complete natural sentences preserve question, ordered examples and viewer benefit. Actual voice is 16.96 seconds; it is not padded, slowed, trimmed or reported as 20–30 seconds.',
    allWholeTextsDirectlyCompared=True, completeScenes=10, completeParagraphs=30, rows=whole_rows,
    independentContextsApproved=False, currentVoiceApproved=False, finalMixedAsrApproved=False,
    humanListening='pending', humanPronunciation='pending', endingHeuristicUsedForApproval=False,
    currentPcmChanged=False, finalTimingApproved=False, privateSaved=False)
save(review_path, review)
plan_path = BASE/'current-independent-context-plan-v1.json'
assert not plan_path.exists()
save(plan_path, dict(schemaVersion=1, createdAt=now, wholeReview=rel(review_path),
    wholeReviewSha256=sha(review_path), boundariesDirectlyComparedWithCurrentWordsAndPCM=True,
    contextCount=10, contexts=contexts, sourcePcmChanged=False, expectedWasRecognizerPrompt=False,
    humanListening='pending', humanPronunciation='pending', automaticApproval=False))
print(json.dumps(dict(wholeReview=rel(review_path), contextPlan=rel(plan_path), count=len(contexts)),ensure_ascii=False))
