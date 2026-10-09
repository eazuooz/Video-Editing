"""Seal13 directly compared complete windows; inspect two remaining uncertainties."""
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
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (24000,1,2)
        return w.readframes(w.getnframes()), w.getparams()
stamp = datetime.now(timezone.utc).isoformat()
sp = BASE / 'observation-candidates-contexts-asr-execution-v3.json'
state = read(sp)
assert state['completed'] == state['total'] == 13 and state['exitCode'] == 0
try:
    assert abs(psutil.Process(state['pid']).create_time() - state['createTime']) >= .01
except psutil.NoSuchProcess:
    pass
state.update(actualExitObserved=True, actualOuterExitCode=0, actualOuterSessionId=17846,
             actualWorkerAlive=False, actualExitObservedAt=stamp)
save(sp,state)
sessionp = sp.with_name(sp.stem + '.session.json')
s = read(sessionp)
assert s['sessionId'] == 17846 and s['pid'] == state['pid']
s.update(actualExitObserved=True, exitCode=0, workerExpectedRunning=False, observedAt=stamp)
save(sessionp,s)
notes = [
 'Complete source-guide content and final sound represented; spacing differences only.',
 'Both complete comparison instructions and ending represented.',
 'Both action-notice and retained-result sentences represented.',
 'Both complete sentences, final sound and source comparison represented.',
 '27/14096/17016 correctly represented as digits; not additional speech or altered script.',
 '왼쪽의 is again transcribed 왼쪽에; both full statements and final sound represented. Preserve the particle/pronunciation uncertainty for human review.',
 '지금은 remains absent at the recognition onset. Do not assert audible omission; compare the full guide after a complete preceding semantic paragraph.',
 'Both stable-location/transient-notice sentences and endings represented.',
 'Both audit sentences represented; punctuation variation only.',
 '배점표 is represented correctly; 점수의/점수 variation persists in this complete candidate paragraph.',
 '기여 and 읽게 are now both represented correctly in the complete independent context; the prior 잃게 recognition differs with context.',
 'All original three paragraphs and complete join represented. 배점표 is correct; 점수의/점수 variation retained. T-Spin-Double/Back-to-Back spellings correspond to action labels, not different actions.',
 'All original three paragraphs and complete joined ending represented. 기여 and 읽게 are represented correctly in the full original-head/candidate context.'
]
data = read(BASE / 'observation-candidates-contexts-asr-v3/asr.json')
assert data['complete'] and len(data['results']) == 13
rows=[]
for d,note in zip(data['results'],notes):
    p=BASE/'observation-candidates-contexts-asr-v3'/(d['id']+'.json')
    assert read(p)==d and d['exactSourceSampleBytesMatched'] and not d['expectedWasRecognizerPrompt']
    assert sha(ROOT/d['contextPath']) == d['contextSha256'] and sha(ROOT/d['sourcePath']) == d['sourceSha256']
    rows.append(dict(id=d['id'],path=rel(p),sha256=sha(p),expectedKo=d['expectedKo'],actualText=d['text'],
       wordsAndFinalSoundDirectlyRead=True,allExpectedAndEntireActualTextDirectlyRead=True,
       exactCurrentSourcePcmMatched=True,sourceSha256=d['sourceSha256'],contextSha256=d['contextSha256'],
       observation=note,noRecognizedWholeSentenceOmission=True,noRecognizedWholeSentenceRepetition=True,
       noRecognizedInventedGreeting=True))
reviewp=BASE/'observation-candidates-contexts-direct-review-v3.json'
assert not reviewp.exists()
save(reviewp,dict(schemaVersion=1,reviewedAt=stamp,allWholeTextsDirectlyCompared=True,
   allIndependentContextsDirectlyCompared=True,contextCount=13,standaloneCompleteContexts=11,
   additionalCompleteJoinContexts=2,rows=rows,currentVoiceApproved=False,finalMixedAsrApproved=False,
   resolvedRecognitionVariants=['04 배점표/배전표 in new candidate', '08 기여/기어 in new candidate',
      '21 읽게/잃게 resolved in independent paragraph and complete join'],
   unresolvedRecognitionVariants=['17 지금은 missing from recognition', '16 왼쪽의/왼쪽에', '20 점수의/점수'],
   actualSynthesisErrorConfirmed=False,candidateParagraphsAdopted=False,humanListening='pending',
   humanPronunciation='pending',endingHeuristicUsedForApproval=False,actualOuterExitCode=0,sessionId=17846))

original_script=read(ROOT/'projects/presenting-game-scores/script/narration.ko.json')
guides=read(ROOT/'projects/presenting-game-scores/script/observation-candidates-v3.ko.json')
boundary=next(c for c in read(BASE/'current-independent-context-plan-v1.json')['contexts']
    if c['id'].startswith('07-name-and-unit'))
original_path=ROOT/boundary['sourcePath']
assert sha(original_path)==boundary['sourceSha256']
original,params=pcm(original_path)
head=original[:boundary['startSample']*2]
quiet=array.array('h',head[-480:]);rms=math.sqrt(sum(x*x for x in quiet)/len(quiet));peak=max(map(abs,quiet))
assert peak<256 and rms<64, 'Reinspect the full-paragraph boundary'
guide=next(r for r in read(BASE/'observation-candidates-tts-execution-v3.json')['results'] if r['id']=='17-observe-named-fields')
assert sha(ROOT/guide['path'])==guide['sha256']
fresh,freshparams=pcm(ROOT/guide['path']);assert params[:3]==freshparams[:3]
joined=head+fresh
destination=ROOT/'shared/output/presenting-game-scores/research/candidate-joins-v3/17-named-fields-complete-leading-context.wav'
assert not destination.exists()
with wave.open(str(destination),'wb') as w:w.setparams(params);w.writeframes(joined)
actual,_=pcm(destination);assert actual==joined and actual[:len(head)]==head and actual[len(head):]==fresh
expected=[next(x for x in original_script['scenes'] if x['id']=='07-name-and-unit')['lines'][0],
          next(x for x in guides['scenes'] if x['id']=='17-observe-named-fields')['lines'][0]]
proofp=BASE/'named-fields-leading-context-pcm-verification-v3.json'
assert not proofp.exists()
save(proofp,dict(schemaVersion=1,preparedAt=stamp,path=rel(destination),sha256=sha(destination),
   originalPath=rel(original_path),originalSha256=sha(original_path),originalRetainedSamples=[0,boundary['startSample']],
   guidePath=guide['path'],guideSha256=guide['sha256'],exactCompleteOriginalFirstParagraphMatched=True,
   exactCompleteGuidePcmMatched=True,observedLast10msRms=rms,observedLast10msPeak=peak,
   boundaryEvidence=boundary['boundaryEvidence'],noSpeechTrim=True,adopted=False,localOnly=True))
joined04=next(r for r in read(BASE/'candidate-complete-joins-pcm-verification-v3.json')['joins'] if r['id']=='04-evaluation-weights')
assert sha(ROOT/joined04['path'])==joined04['sha256']
start04=next(c['startSample'] for c in read(BASE/'current-independent-context-plan-v1.json')['contexts']
    if c['id'].startswith('04-evaluation-weights'))
targets=[dict(id='17-named-fields-complete-leading-context',sourcePath=rel(destination),sourceSha256=sha(destination),
    startSample=0,endSample=len(actual)//2,zeroPaddingSamplesEachSide=14400,expectedKo=expected,
    completeParagraphs=[1,2],boundaryEvidence=dict(exactOriginalFirstParagraphAndCompleteGuideMatched=True,
        compositionProof=rel(proofp),compositionProofSha256=sha(proofp)),
    purpose='Complete semantic lead and unchanged entire guide. Inspect whether recognition preserves 지금은 inside a natural preceding context; no isolated-word prompt.'),
 dict(id='04-complete-p2-candidate-p3-leading-context',sourcePath=joined04['path'],sourceSha256=joined04['sha256'],
    startSample=start04,endSample=joined04['samples'],zeroPaddingSamplesEachSide=14400,
    expectedKo=next(x for x in original_script['scenes'] if x['id']=='04-evaluation-weights')['lines'][1:],
    completeParagraphs=[2,3],boundaryEvidence=dict(exactOriginalSecondParagraphAndCompleteCandidateMatched=True,
        originalQuietStartSample=start04,compositionProof=rel(BASE/'candidate-complete-joins-pcm-verification-v3.json')),
    purpose='Complete original second paragraph and complete exact-text candidate third paragraph; inspect 점수의 variation without shortening either sentence.')]
planp=BASE/'observation-candidates-targeted-context-plan-v3.json';assert not planp.exists()
save(planp,dict(schemaVersion=1,createdAt=stamp,wholeReview=rel(reviewp),wholeReviewSha256=sha(reviewp),
   boundariesDirectlyComparedWithCurrentWordsAndPCM=True,contexts=targets,expectedWasRecognizerPrompt=False,
   automaticApproval=False,currentVoiceApproved=False))
print(json.dumps(dict(contextsDirectlyRead=13,remainingCompleteTargets=2,currentVoiceApproved=False)))
