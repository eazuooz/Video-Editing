"""Record direct whole-text comparison and six bounded current-PCM contexts.

This records the observed ASR session exit and preserves the exact input bytes.
It grants no human listening, pronunciation, final-mix or publication approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, wave
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()
def save(p, value):
    temp = p.with_name(p.name + '.writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(temp, p)
def rel(p): return p.relative_to(ROOT).as_posix()

statepath = R/'additions-whole-asr-execution-v1.json'
s = read(statepath)
assert s['pid'] == 32300 and s['createTime'] == 1791650397.0102296
assert s['exitCode'] == 0 and s['completed'] == s['total'] == 2
assert s['cwd'] == str(ROOT) and 'review-motion-additive-voice-v1.py' in s['commandLine'][3]
# Actual unified session92351 was polled once and returned exit0 (d744a5).
s.update(sessionId=92351, actualExitObserved=True, actualExitCode=0,
         actualExitToolChunk='d744a5', actualExitRecordedAt=now())
save(statepath, s)
save(statepath.with_name(statepath.stem+'.session.json'), dict(
    pid=s['pid'], createTime=s['createTime'], commandLine=s['commandLine'], cwd=s['cwd'],
    sessionId=92351, actualExitCode=0, workerCurrentlyAlive=False,
    identitySource='Worker state plus actual completed session; CIM PID32300 absent', recordedAt=now()))

boundaries = {'00a':[0,89040,248160,373560,537600], '06b':[0,119160,263040]}
gaps = {'00a':[(3.54,3.78),(10.14,10.36),(15.38,15.60)], '06b':[(4.72,5.02)]}
rows, contexts = [], []
for result in s['results']:
    sid = result['id']; source = ROOT/result['sourcePath']
    assert sha(source) == result['sourceSha256']
    with wave.open(str(source), 'rb') as wav:
        assert (wav.getnchannels(),wav.getsampwidth(),wav.getframerate()) == (1,2,24000)
        pcm = wav.readframes(wav.getnframes())
    samples = np.frombuffer(pcm, dtype='<i2').astype(float)
    cuts = boundaries[sid]
    assert cuts[-1] == len(samples)
    energy = []
    for i, (lo, hi) in enumerate(gaps[sid]):
        n = cuts[i+1]; t = n/24000
        assert lo < t < hi
        energy.append(dict(sample=n,seconds=t,precedingWordEnd=lo,followingWordStart=hi,
                           rms20ms=float(np.sqrt(np.mean(samples[n-240:n+240]**2)))))
    # All whole words, sentence endings and these quiet source-sample boundaries
    # were directly read. Difference is spacing/punctuation only.
    rows.append(dict(id=sid, expectedWhole=' '.join(result['expectedKo']),
                     recognizedWhole=result['text'], currentAudioSha256=result['sourceSha256'],
                     allWordsDirectlyRead=True, wholeMeaningComplete=True,
                     missingWords=[], repeatedWords=[], differingMeaning=[],
                     spacingOnly=['빨간선 → 빨간 선','연결해 보죠 → 연결해보죠'] if sid=='00a' else [],
                     fullSentenceEndingsPresent=True, quietBoundaries=energy,
                     tail20msRms=float(np.sqrt(np.mean(samples[-480:]**2))),
                     last10msMax=float(np.max(np.abs(samples[-240:]))),
                     humanListeningApproved=False, humanPronunciationApproved=False))
    for i, text in enumerate(result['expectedKo']):
        contexts.append(dict(id=f'{sid}-p{i+1:02d}', sceneId=sid, paragraphIndex=i,
            sourcePath=result['sourcePath'],sourceSha256=result['sourceSha256'],
            startSample=cuts[i],endSample=cuts[i+1],startSeconds=cuts[i]/24000,
            endSeconds=cuts[i+1]/24000,zeroPaddingSamplesEachSide=7200,
            expectedKo=text, independentCompleteSentence=True,
            boundaryReason='Actual whole word boundaries and quiet current PCM interval; no words clipped'))
reviewpath = R/'additions-whole-asr-direct-review-v1.json'
planpath = R/'additions-independent-context-plan-v1.json'
assert not reviewpath.exists() and not planpath.exists(), 'Preserve completed preparation.'
save(reviewpath, dict(schemaVersion=1,recordedAt=now(),sourceExecution=rel(statepath),
    sourceExecutionSha256=sha(statepath),actualSession=92351,actualOuterExitCode=0,
    allWholeTextsDirectlyCompared=True,expectedWasRecognizerPrompt=False,rows=rows,
    wholeCurrentTextComplete=True,independentContextsApproved=False,
    allCurrentUnmixedVoiceApproved=False,finalMixedVoiceApproved=False,
    humanListeningApproved=False,humanPronunciationApproved=False,
    baselinePcmRegenerated=0))
save(planpath, dict(schemaVersion=1,recordedAt=now(),wholeReview=rel(reviewpath),
    wholeReviewSha256=sha(reviewpath),boundariesDirectlyComparedWithCurrentWordsAndPCM=True,
    sourceBytesPreserved=True,contexts=contexts,automaticApproval=False,
    finalMixedAsrApproved=False,humanListeningApproved=False))
print(json.dumps(dict(wholeDirectlyCompared=2,completeContextsPrepared=6,
    contextsApproved=False,sourcePcmModified=0),ensure_ascii=False))
