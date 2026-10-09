"""Persist the completed direct text review and its limited technical scope.

Current mixed recognition variants are preserved as pronunciation questions,
not converted to claims of audible correctness or audible synthesis failure.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def pcm(path,start,end):
 with wave.open(str(path),'rb')as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(48000,2,2)
  w.setpos(start);return w.readframes(end-start)
ex=read(W/'mixed-asr-execution.json');progress=read(W/'mixed-asr-direct-progress.json');data=read(W/'mixed-asr-v1/asr.json')
assert ex['outerExitCode']==ex['exitCode']==0 and ex['outerExitDirectlyObserved']
assert progress['directlyRead']==31 and data['complete'] and len(data['results'])==31
settings=read(W/'mix-settings.json');mix=W/'final-mix.wav';plan=read(W/'plan.json')
assert sha(mix)==settings['wavSha256']==data['mixSha256'] and sha(W/'plan.json')==data['planSha256']
rx=W/'mixed-resolution-execution-v3.json';r=read(rx);assert r['exitCode']==0 and r['completed']==3
r.update(outerExitCode=0,outerExitDirectlyObserved=True,sessionId=11999,outerClosedObservedAt=now());save(rx,r)
rows=[]
observations={
 'whole-03':'Recognizer chunk duplicates guide12 tail/p3 with29.80→20.00s reversal. Current complete guide12+p3 diagnostic contains each once in actual timeline order; exact PCM placements contain each once. Raw repeated text preserved; no actual speech repetition claimed.',
 'whole-08':'All three full paragraphs/order/endings present. 기여/기어 and 읽게/잃게 remain in current independent and beam5 contexts. These lexical/pronunciation questions are not claimed resolved. No verified sentence omission or new speech; human listening required.',
 'context-08-complete-p3':'Both full sentences/endings present. Same unresolved 기여/기어 and 읽게/잃게 recognition alternatives in the unchanged current mixed PCM; human pronunciation/listening pending.',
 'context-06-complete-p2-clause-1':'27주를 versus expected27줄을 in independent window; whole06 reads27줄 and exact same source samples/current mix slice preserved. Keep unit-consonant pronunciation question pending.'}
for row in progress['windows']:
 p=ROOT/row['path'];x=read(p);assert sha(p)==row['sha256'] and row['directlyCompared']
 b=pcm(mix,x['fromSample'],x['toSample']);assert hashlib.sha256(b).hexdigest()==x['mixPcmSliceSha256']
 with wave.open(str(ROOT/x['windowPath']),'rb')as w:
  padded=w.readframes(w.getnframes())
 assert padded==bytes(x['padSamplesEachSide']*4)+b+bytes(x['padSamplesEachSide']*4)
 rows.append({**row,'expectedKo':x['expectedKo'],'actualText':x['text'],'exactCurrentMixedPcmSliceReverified':True,
  'observation':observations.get(x['label'],row['observation']),'humanPronunciation':'pending'})
targetrows=[]
for p in sorted((W/'mixed-resolution-contexts-v3').glob('*.json')):
 if p.name=='request.json':continue
 x=read(p);b=pcm(mix,x['start'],x['end']);assert hashlib.sha256(b).hexdigest()==x['mixPcmSliceSha256']
 targetrows.append(dict(label=x['label'],path=p.relative_to(ROOT).as_posix(),sha256=sha(p),expectedKo=x['expectedKo'],actualText=x['text'],
  directlyCompared=True,allWordsAndCompleteEndingsRead=True,exactCurrentMixedPcmSliceReverified=True,
  expectedWasRecognizerPrompt=False,pronunciationResolved=False if x['label'].startswith('08') else None))
assert len(targetrows)==3
voice=W/'voice-normalized.wav';premix=W/'final-mix-before-master-level.wav';checks=[]
whole08=next(x for x in data['results']if x['label']=='whole-08')
gain=10**(settings['masterGainDb']/20)
for name,a,b in [('기여/기어',16.74,17.20),('읽게/잃게',18.78,19.28)]:
 start=whole08['fromSample']+round(a*48000);end=whole08['fromSample']+round(b*48000)
 v=np.frombuffer(pcm(voice,start,end),dtype='<i2').astype(float);pre=np.frombuffer(pcm(premix,start,end),dtype='<i2').astype(float)
 m=np.frombuffer(pcm(mix,start,end),dtype='<i2').astype(float)
 corr=float(np.corrcoef(v,m)[0,1]);residual=m-gain*v
 checks.append(dict(word=name,startSample48k=start,endSample48k=end,normalisedVoiceCurrentMixCorrelation=corr,
  masterGainReconstructionMaximumErrorLsb=float(np.max(np.abs(m-pre*gain))),
  residualToVoiceRmsDb=float(20*np.log10(np.sqrt(np.mean(residual**2))/np.sqrt(np.mean((v*gain)**2)))),
  maxAbsoluteFinalInt16=float(np.max(np.abs(m))),clippedAtInt16Limit=bool(np.any(np.abs(m)>=32767)),
  interpretation='Current normalized speech remains at the exact intended interval under continuous BGM. Correlation verifies mix provenance, not phoneme correctness or intelligibility.'))
 assert checks[-1]['masterGainReconstructionMaximumErrorLsb']<2 and not checks[-1]['clippedAtInt16Limit']
resolution=dict(reviewedAt=now(),targets=targetrows,currentMixedAudioSha256=sha(mix),currentPlanSha256=sha(W/'plan.json'),
 allThreeEntireActualTextsAndTimestampsDirectlyRead=True,
 target03ExpectedOrderMetadataCorrection='The saved target expectedKo list follows caption-storage order (p3 before guide12), not timeline. Literal texts unchanged; actual timeline/recognition correctly orders guide12 then p3. No ASR prompt used; preserve the raw diagnostic JSON.',
 whole03ChunkRepetitionResolvedAsRecognitionArtifact=True,actualSpeechRepetitionClaimed=False,
 current08LexicalRecognitionResolved=False,current08HumanPronunciationRequired=True,
 currentWordWaveformChecks=checks,unmixedApprovalUsedAsFinalMixApproval=False,endingHeuristicUsedForApproval=False,
 newAudioCreated=0,newTts=0,automaticApproval=False,humanWholeListening='pending',humanPronunciation='pending')
rp=W/'mixed-asr-resolution-direct-review-v2.json';save(rp,resolution)
review=dict(schemaVersion=1,slug='presenting-game-scores',reviewedAt=now(),status='approved-current-mixed-clause-completeness-with-explicit-pronunciation-questions',
 currentMixedAudioSha256=settings['wavSha256'],currentAacSha256=settings['aacSha256'],planSha256=sha(W/'plan.json'),
 windows=rows,all31WindowsDirectlyCompared=True,wholeWindowCount=10,independentWindowCount=21,
 all31CurrentMixedPcmSlicesReverified=True,resolutionReview=rp.relative_to(ROOT).as_posix(),resolutionReviewSha256=sha(rp),
 resolvedTimestampArtifacts=['Whole03 duplicate guide tail/p3 maps back to the same20–29.8sec; complete current leading context contains both exactly once.'],
 unresolvedHumanPronunciationQuestions=['08 기여/기어 and 읽게/잃게 persist in all current mixed contexts; not resolved by previous unmixed recognition.',
  '06 independent27주를/whole27줄; intended unit 줄 requires human pronunciation review.',
  'Overview 지훈/지운 and 의/에 particle variants in04/06/09/10 remain human pronunciation questions.'],
 unresolvedContentDefects=[],actualSynthesisErrorConfirmed=False,technicallyApproved=True,
 approvalScope='Direct current mixed review confirms full clause coverage/order/endings, numeric comparisons, exact PCM provenance and no verified sentence-level omission/repetition/invented greeting. It does not approve lexical pronunciation, full human listening or public release. Persistent08 recognition alternatives remain explicitly pending.',
 priorUnmixedApprovalUsedAsFinalMixApproval=False,endingHeuristicUsedForApproval=False,expectedWasRecognizerPrompt=False,automaticApproval=False,
 humanWholeListening='pending',humanPronunciation='pending',allFinalPixels=False,qaApproved=False,collected=False,uploaded=False)
save(W/'full-mix-asr-review.json',review)
print(json.dumps(dict(windows=31,targetContexts=3,technicalScope=review['approvalScope'],waveformChecks=checks),ensure_ascii=False))
