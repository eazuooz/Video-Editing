"""Record direct comparison of all24 complete current PCM paragraphs.

This seals actual execution and byte checks, not human pronunciation approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil, wave

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
def save(p, d):
    t = p.with_name(p.name+'.sealing')
    t.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(t, p)

sp = BASE/'current-contexts-asr-execution-v1.json'
state = read(sp)
session_path = BASE/'current-contexts-asr-execution-v1.session.json'
session = read(session_path)
assert state['exitCode'] == 0 and state['completed'] == state['total'] == 24
assert session['sessionId'] == state['sessionId'] == 77115
assert not psutil.pid_exists(state['pid']) or abs(psutil.Process(state['pid']).create_time()-state['createTime']) > .01
asrp = BASE/'current-contexts-asr-v1/asr.json'
asr = read(asrp)
planp = BASE/'current-independent-context-plan-v1.json'
plan = read(planp)
whole = read(BASE/'current-whole-asr-v1/asr.json')
assert asr['complete'] and len(asr['results']) == len(plan['contexts']) == 24
whole_map = {r['id']: r for r in whole['results']}
specific = {
    '03-pattern-and-erasing-p01': dict(alternatives=['빗금→빗급', '화면의→화면에'], comparison='Full roof paint/erase/hatching and retained house structure clauses are present. 빗급 is a repeated recognition alternative in both whole and independent complete context; pronunciation remains unresolved. 집의 is correctly recognized in the independent context, resolving only that whole-text spelling alternative.'),
    '05-state-not-hue-p02': dict(alternatives=['영구히→연구히'], comparison='Both current-height and nonpermanent-path clauses are complete, including the negative instruction 읽으면 안 됩니다. Independent context recognizes 높아지므로 as expected, while 영구히→연구히 differs from the correct whole-text 영구히; human articulation review remains pending.'),
    '06-route-information-p01': dict(alternatives=[], comparison='Complete flower/platform-top/destination-boundary and foreground-priority clauses are recognized. Independent first word 꽃 resolves the whole-text initial 가스꽃 recognition alternative; this is text comparison, not human articulation approval.'),
    '06-route-information-p03': dict(alternatives=['차이에→차이의'], comparison='The full distinguish-first, outlines/shapes and decoration-order claims are present. The particle alternative 차이에→차이의 occurs in both contexts and remains a pronunciation-review item.'),
    '08-check-and-conclusion-p01': dict(alternatives=['놓친→놓침'], comparison='Both the preview-help and not-universal-readability clauses are complete. Independent 놓침 differs from correct whole-text 놓친; 색 인지/색인지 and 미리보기/미리 보기 spacing do not introduce a new device. Human pronunciation remains pending.'),
}
rows = []
for r, c in zip(asr['results'], plan['contexts']):
    assert r['id'] == c['id'] and r['expectedKo'] == c['expectedKo'] and r['expectedEn'] == c['expectedEn']
    source = ROOT/r['sourcePath']
    assert sha(source) == c['sourceSha256'] == r['sourceSha256']
    with wave.open(str(source), 'rb') as w:
        assert w.getframerate() == 24000 and w.getnchannels() == 1 and w.getsampwidth() == 2
        w.setpos(c['startSample'])
        pcm = w.readframes(c['endSample']-c['startSample'])
    assert hashlib.sha256(pcm).hexdigest() == c['partitionPcmSha256'] == r['pcmSha256']
    context = ROOT/r['contextPath']
    assert sha(context) == r['contextSha256'] == r['audioSha256']
    with wave.open(str(context), 'rb') as w:
        padded = w.readframes(w.getnframes())
    pad = c['zeroPaddingSamplesEachSide']*2
    assert padded == b'\0'*pad+pcm+b'\0'*pad
    assert r['expectedWasRecognizerPrompt'] is False and r['words']
    note = specific.get(r['id'], dict(alternatives=[], comparison='All expected complete clauses are recognized in original order. Only spacing/punctuation variations were observed; no omitted or repeated sentence was detected.'))
    rows.append(dict(id=r['id'], expectedKo=c['expectedKo'], expectedEn=c['expectedEn'],
        actualIndependentFullText=r['text'], actualWholeParagraphText=c['wholeRecognizedContext'],
        sourcePath=r['sourcePath'], currentPcmSha256=r['sourceSha256'], exactSampleRange=[c['startSample'],c['endSample']],
        partitionPcmSha256=r['pcmSha256'], contextPath=r['contextPath'], contextSha256=r['contextSha256'],
        fullWords=r['words'], firstWord=r['words'][0], lastWords=r['words'][-4:],
        completeContextDirectlyCompared=True, exactOriginalPcmAndZeroPaddingMatched=True,
        omissionOrRepeatedSentenceDetected=False, recognitionAlternatives=note['alternatives'],
        comparison=note['comparison'], humanListening='pending', humanPronunciation='pending'))
observed = datetime.now(timezone.utc).isoformat()
state.update(actualExitObserved=True, actualOuterSession=77115, actualOuterExitCode=0,
             actualToolExitObservation='63b6db', actualExitObservedAt=observed, directReview=True)
session.update(actualExitObserved=True, actualExitCode=0, actualToolExitObservation='63b6db')
save(sp,state); save(session_path,session)
proof = dict(schemaVersion=1, reviewedAt=observed, actualSession=77115, actualExitCode=0,
    actualToolExitObservation='63b6db', whole8PreviouslyDirectlyRead=True,
    independent24CompleteTextsDirectlyRead=True, fullExpectedKoEnDirectlyCompared=True,
    currentPcmHashesAndAllExactSamplePartitionsMatched=True, recognizerReceivedExpectedPrompt=False,
    wholeAsrSha256=sha(BASE/'current-whole-asr-v1/asr.json'), independentAsr=rel(asrp), independentAsrSha256=sha(asrp),
    contextPlan=rel(planp), contextPlanSha256=sha(planp), rows=rows,
    detectedSentenceOmissionsOrRepeats=0, humanListening='pending', humanPronunciation='pending',
    unresolvedPronunciationItems=['03: 빗금/빗급, 화면의/화면에', '05: 영구히/연구히', '06: 차이에/차이의', '08: 놓친/놓침'],
    boundedCurrent8VoiceTextReviewComplete=True, narrationApproved=False, finalMixedAsrApproved=False,
    finalTimingApproved=False, finalPixelApproved=False, privateUploaded=False, actualVideoId=None,
    nextAction='Preserve all8 PCM. Measure and independently review additive causal narration after its source mapping is secured; native extra-action, measured60:40, continuous animations, current Nimbus mix/full mixed ASR and final caption/pixel QA remain pending.')
dest = BASE/'current-independent-voice-direct-review-v1.json'
assert not dest.exists()
save(dest,proof)
print(json.dumps(dict(actualSession=77115, actualExitCode=0, completeContexts=24, allPcmPartitionsMatched=True,
                     current8BoundedTextReviewComplete=True, humanPronunciation='pending', finalMix=False)))
