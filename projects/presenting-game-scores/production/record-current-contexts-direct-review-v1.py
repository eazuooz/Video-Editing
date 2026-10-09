"""Record all independently read context texts; prepare two full-paragraph targets."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
    for i in range(40):
        try: os.replace(t,p);return
        except OSError:
            if i==39:raise
            time.sleep(.15)
now=datetime.now(timezone.utc).isoformat()
sp=BASE/'current-contexts-asr-execution-v1.json';state=read(sp)
assert state['completed']==state['total']==10 and state['exitCode']==0
try:
    p=psutil.Process(state['pid']);assert abs(p.create_time()-state['createTime'])>=.01
except psutil.NoSuchProcess:pass
state.update(actualExitObserved=True,actualOuterExitCode=0,actualOuterSessionId=83640,actualWorkerAlive=False,actualExitObservedAt=now)
save(sp,state)
sessionp=BASE/'current-contexts-asr-execution-v1.session.json';s=read(sessionp)
s.update(actualExitObserved=True,exitCode=0,workerExpectedRunning=False,observedAt=now);save(sessionp,s)
notes=[
 '지운 줄 수 now recognized as 지운 줄수, resolving the prior context-dependent 지훈 transcription. All second/third paragraphs and final sound words are represented.',
 'Both complete paragraphs represented; spacing/punctuation differences only.',
 'Both complete paragraphs represented; no omitted comparison or final advice.',
 'Tspindable and Back to Back are spelling variants for the device/action label. 배점표 remains 배전표; do not automatically claim either correct pronunciation or confirmed synthesis error.',
 'Action notice/retained total and the complete final advice are represented.',
 '27줄을 now represented, resolving the whole-scene 주를 transcription; 2920 and141 remain correct. 중의/중에 uncertainty remains for human pronunciation.',
 'Both complete paragraphs, units and better-value direction represented.',
 '기여 remains 기어 in this context; preserve the uncertainty and examine a separate complete third paragraph.',
 '행동의 now represented, resolving the whole-scene 행동에 transcription; both complete paragraphs and ending represented.',
 'Complete recap and original coaching ending represented; no invented greeting or repeated ending.'
]
rows=[]
for i,p in enumerate(sorted((BASE/'current-contexts-asr-v1').glob('[0-9]*.json'))):
 d=read(p);assert d['exactSourceSampleBytesMatched'] and not d['expectedWasRecognizerPrompt'];assert sha(ROOT/d['contextPath'])==d['contextSha256'];assert sha(ROOT/d['sourcePath'])==d['sourceSha256']
 rows.append(dict(id=d['id'],path=rel(p),sha256=sha(p),expectedKo=d['expectedKo'],actualText=d['text'],
   wordsDirectlyRead=True,allExpectedAndEntireActualTextDirectlyRead=True,exactCurrentSourcePcmMatched=True,
   currentSourceSha256=d['sourceSha256'],contextSha256=d['contextSha256'],observation=notes[i],
   noRecognizedWholeSentenceOmission=True,noRecognizedWholeSentenceRepetition=True,noRecognizedInventedGreeting=True))
assert len(rows)==10
reviewp=BASE/'current-contexts-direct-review-v1.json';assert not reviewp.exists()
save(reviewp,dict(schemaVersion=1,reviewedAt=now,allWholeTextsDirectlyCompared=True,
 wholeReview=rel(BASE/'current-whole-direct-review-v1.json'),wholeReviewSha256=sha(BASE/'current-whole-direct-review-v1.json'),
 allIndependentContextsDirectlyCompared=True,contextCount=10,rows=rows,
 currentVoiceApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',
 unresolvedRecognitionVariants=['04 배점표/배전표','08 기여/기어','06 중의/중에'],
 endingHeuristicUsedForApproval=False,sourcePcmChanged=False,actualOuterExitCode=0,sessionId=83640))
contexts=[]
for scene,start,gap,rms,peak in [('04-evaluation-weights',14.14,[13.86,14.16],5.5,14),('08-scoring-feedback',14.68,[14.38,14.7],14.6,31)]:
 d=read(BASE/'current-whole-asr-v1'/(scene+'.json'))
 contexts.append(dict(id=scene+'-complete-p3-leading-pad',sourcePath=d['sourcePath'],sourceSha256=d['sourceSha256'],
 startSample=round(start*24000),endSample=d['sourceSamples'],zeroPaddingSamplesEachSide=14400,
 expectedKo=d['expectedKo'][2:],completeParagraphs=[3],boundaryEvidence=dict(startSeconds=start,
 wholeWordsGap=gap,inspected10msPcmBins=True,boundaryBinRms=rms,boundaryBinPeak=peak,fullOriginalEndPreserved=True),
 purpose='Separate complete third paragraph with .6-second zero lead/tail. No isolated word or truncated sentence; expected text is review-only.'))
planp=BASE/'current-targeted-leading-context-plan-v1.json';assert not planp.exists()
save(planp,dict(schemaVersion=1,createdAt=now,wholeReview=rel(reviewp),wholeReviewSha256=sha(reviewp),
 boundariesDirectlyComparedWithCurrentWordsAndPCM=True,contexts=contexts,expectedWasRecognizerPrompt=False,automaticApproval=False))
print(json.dumps({'contextsDirectlyRead':10,'remainingTargets':2,'currentVoiceApproved':False}))
