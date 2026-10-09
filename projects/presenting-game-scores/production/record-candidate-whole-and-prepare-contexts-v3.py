"""Record directly read eleven whole texts; prepare complete, unadopted joins.

Run after the actual whole exec exit0. No model, GPU, production adoption,
retiming, approval or process/control operation occurs here.
"""
from pathlib import Path
from datetime import datetime, timezone
import array, hashlib, json, math, os, psutil, wave

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
def save(p, value):
    t = p.with_name(p.name + '.recording')
    t.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(t, p)
def pcm(p):
    with wave.open(str(p), 'rb') as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (24000, 1, 2)
        return w.readframes(w.getnframes()), w.getparams()

stamp = datetime.now(timezone.utc).isoformat()
state_path = BASE / 'observation-candidates-whole-asr-execution-v3.json'
state = read(state_path)
assert state['exitCode'] == 0 and state['completed'] == state['total'] == 11
session_path = state_path.with_name(state_path.stem + '.session.json')
session = read(session_path)
assert session['sessionId'] == 61870 and session['pid'] == state['pid']
try:
    p = psutil.Process(state['pid'])
    assert abs(p.create_time() - state['createTime']) >= .01, 'Worker still alive'
except psutil.NoSuchProcess:
    pass
state.update(actualExitObserved=True, actualOuterExitCode=0,
             actualOuterSessionId=61870, actualWorkerAlive=False, actualExitObservedAt=stamp)
save(state_path, state)
session.update(actualExitObserved=True, exitCode=0, workerExpectedRunning=False, observedAt=stamp)
save(session_path, session)
notes = [
 'Both complete sentences and final sound represented; whitespace differences only.',
 'Complete two-stage comparison and final instruction represented.',
 'Both sentences distinguish action notice and retained result; complete ending represented.',
 'Both notice/timing and continuing-total sentences represented.',
 '27, 14096 and17016 are represented correctly; numeric spellings are notation variants.',
 'Both complete sentences represented; 왼쪽의/왼쪽에 recognition variant retained for independent context and human pronunciation.',
 'Opening 지금은 is absent in this whole transcription, although the remaining two sentences are represented. Preserve the complete PCM and inspect padded independent context; no audible omission is asserted.',
 'Both stable-location/transient-notice sentences and ending represented.',
 'Both complete audit sentences represented; punctuation differences only.',
 '배점표 is now represented as 배점표; 점수의/점수 remains a particle recognition variation. Unadopted same-text candidate requires independent and complete join comparison.',
 '기여 is now represented as 기여; 읽게 is transcribed 잃게. Preserve the uncertainty and inspect full independent/join contexts before adoption.'
]
data = read(BASE / 'observation-candidates-whole-asr-v3/asr.json')
assert data['complete'] and len(data['results']) == 11
rows = []
contexts = []
for d, note in zip(data['results'], notes):
    p = BASE / 'observation-candidates-whole-asr-v3' / (d['id'] + '.json')
    assert sha(ROOT / d['sourcePath']) == d['sourceSha256']
    assert not d['expectedWasRecognizerPrompt'] and read(p) == d
    raw, _ = pcm(ROOT / d['sourcePath'])
    assert len(raw) // 2 == d['sourceSamples']
    rows.append(dict(id=d['id'], path=rel(p), sha256=sha(p), expectedKo=d['expectedKo'],
        actualText=d['text'], allExpectedAndEntireActualTextDirectlyRead=True,
        wordsAndFinalSoundDirectlyRead=True, currentSourceSha256=d['sourceSha256'],
        observation=note, noRecognizedWholeSentenceOmission=True,
        noRecognizedWholeSentenceRepetition=True, noRecognizedInventedGreeting=True))
    contexts.append(dict(id=d['id'] + '-complete-independent', sourcePath=d['sourcePath'],
        sourceSha256=d['sourceSha256'], startSample=0, endSample=d['sourceSamples'],
        zeroPaddingSamplesEachSide=14400, expectedKo=d['expectedKo'], completeParagraphs=[1],
        boundaryEvidence=dict(entireSourceIncludingOnsetAndFinalSoundPreserved=True,
            wholeWordsFirst=d['words'][0], wholeWordsLast=d['words'][-1],
            sourceSampleCountVerified=True, noSpeechTrim=True),
        purpose='Whole complete one-paragraph independent window with .6s zero lead/tail; expected text is review-only.'))
review_path = BASE / 'observation-candidates-whole-direct-review-v3.json'
assert not review_path.exists()
save(review_path, dict(schemaVersion=1, reviewedAt=stamp, allWholeTextsDirectlyCompared=True,
    wholeCount=11, rows=rows, actualOuterExitCode=0, sessionId=61870,
    unresolvedRecognitionVariants=['16 왼쪽의/왼쪽에', '17 missing 지금은 in whole transcription',
        '20 점수의/점수', '21 읽게/잃게'], candidateParagraphsAdopted=False,
    currentVoiceApproved=False, finalMixedAsrApproved=False, actualSynthesisErrorConfirmed=False,
    humanListening='pending', humanPronunciation='pending', endingHeuristicUsedForApproval=False))

join_dir = ROOT / 'shared/output/presenting-game-scores/research/candidate-joins-v3'
assert not join_dir.exists(), 'Preserve existing review joins'
join_dir.mkdir(parents=True)
main_script = read(ROOT / 'projects/presenting-game-scores/script/narration.ko.json')
target_plan = read(BASE / 'current-targeted-leading-context-plan-v1.json')
assert target_plan['boundariesDirectlyComparedWithCurrentWordsAndPCM']
join_rows = []
for original_id, candidate_id in [('04-evaluation-weights', '20-candidate-evaluation-p3'),
                                  ('08-scoring-feedback', '21-candidate-contribution-p3')]:
    boundary = next(c for c in target_plan['contexts'] if c['id'].startswith(original_id))
    original_path = ROOT / boundary['sourcePath']
    assert sha(original_path) == boundary['sourceSha256']
    original, params = pcm(original_path)
    d = next(x for x in data['results'] if x['id'] == candidate_id)
    fresh, fresh_params = pcm(ROOT / d['sourcePath'])
    assert params[:3] == fresh_params[:3]
    count = boundary['startSample']
    head = original[:count * 2]
    assert len(head) == count * 2
    tailbin = array.array('h', head[-480:])
    peak = max(map(abs, tailbin))
    rms = math.sqrt(sum(v*v for v in tailbin) / len(tailbin))
    assert peak < 256 and rms < 64, 'Reinspect a non-quiet join; never force a cut'
    joined = head + fresh
    destination = join_dir / (original_id + '-complete-review-join.wav')
    with wave.open(str(destination), 'wb') as w:
        w.setparams(params)
        w.writeframes(joined)
    actual, _ = pcm(destination)
    assert actual == joined and actual[:count*2] == original[:count*2] and actual[count*2:] == fresh
    scene = next(s for s in main_script['scenes'] if s['id'] == original_id)
    assert scene['lines'][2] == d['expectedKo'][0]
    audit = dict(id=original_id, path=rel(destination), sha256=sha(destination),
        samples=len(actual)//2, seconds=len(actual)/48000, originalPath=rel(original_path),
        originalSha256=sha(original_path), originalRetainedSamples=[0, count],
        exactOriginalHeadPcmMatched=True, candidatePath=d['sourcePath'], candidateSha256=d['sourceSha256'],
        exactCompleteCandidatePcmMatched=True, endingPcmTrimmed=False, alteredPcmSamples=0,
        reusedQuietBoundaryEvidence=boundary['boundaryEvidence'], observedLast10msRms=rms,
        observedLast10msPeak=peak, allThreeOriginalParagraphTextsPreserved=True,
        expectedKo=scene['lines'], adopted=False, humanListening='pending')
    join_rows.append(audit)
    contexts.append(dict(id=original_id + '-complete-candidate-join', sourcePath=rel(destination),
        sourceSha256=sha(destination), startSample=0, endSample=len(actual)//2,
        zeroPaddingSamplesEachSide=14400, expectedKo=scene['lines'], completeParagraphs=[1,2,3],
        boundaryEvidence=dict(entireSourceIncludingOnsetAndFinalSoundPreserved=True,
            fullOriginalHeadAndFullCandidatePcmMatched=True, joinAudit=audit),
        purpose='Complete review-only three-paragraph join; original first two paragraphs and exact-text candidate last paragraph. No production adoption.'))
join_audit_path = BASE / 'candidate-complete-joins-pcm-verification-v3.json'
assert not join_audit_path.exists()
save(join_audit_path, dict(schemaVersion=1, preparedAt=stamp, joins=join_rows,
    newTtsJobs=0, newAsrJobs=0, newGpuJobs=0, originalTenChunksChanged=False,
    exactPcmCompositionVerified=True, candidateParagraphsAdopted=False, localOnly=True))
plan_path = BASE / 'observation-candidates-independent-context-plan-v3.json'
assert not plan_path.exists()
save(plan_path, dict(schemaVersion=1, createdAt=stamp, wholeReview=rel(review_path),
    wholeReviewSha256=sha(review_path), joinAudit=rel(join_audit_path), joinAuditSha256=sha(join_audit_path),
    boundariesDirectlyComparedWithCurrentWordsAndPCM=True, contexts=contexts,
    expectedWasRecognizerPrompt=False, automaticApproval=False, candidateParagraphsAdopted=False))
print(json.dumps(dict(wholeTextsDirectlyRead=11, completeIndependentContexts=11,
                     additionalCompleteReviewJoins=2, currentVoiceApproved=False)))
