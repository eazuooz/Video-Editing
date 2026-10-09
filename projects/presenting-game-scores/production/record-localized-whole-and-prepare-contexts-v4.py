"""Record two directly read full results and prepare four exact PCM contexts.

These are review material. No production narration/timing/final-mix approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, array, hashlib, json, math, os, psutil, wave

BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
 t=p.with_name(p.name+'.recording'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8'); os.replace(t,p)
def pcm(p):
 with wave.open(str(p),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
  return w.readframes(w.getnframes()),w.getparams()
ap=argparse.ArgumentParser(); ap.add_argument('--outer-exit-code',type=int,required=True); ap.add_argument('--session-id',type=int,required=True); args=ap.parse_args()
stamp=datetime.now(timezone.utc).isoformat()
sp=BASE/'localized-voice-repair-whole-asr-execution-v4.json'; state=read(sp)
assert args.outer_exit_code==state['exitCode']==0 and state['completed']==state['total']==2
sessionp=sp.with_name(sp.stem+'.session.json'); session=read(sessionp)
assert session['sessionId']==args.session_id and session['pid']==state['pid']
try: assert abs(psutil.Process(state['pid']).create_time()-state['createTime'])>=.01
except psutil.NoSuchProcess: pass
state.update(actualExitObserved=True,actualOuterExitCode=0,actualOuterSessionId=args.session_id,actualWorkerAlive=False,actualExitObservedAt=stamp)
save(sp,state); session.update(actualExitObserved=True,exitCode=0,workerExpectedRunning=False,observedAt=stamp); save(sessionp,session)
data=read(BASE/'localized-voice-repair-whole-asr-v4/asr.json'); assert data['complete'] and len(data['results'])==2
notes=[
 'The whole first result again begins with 점수를. 지금은 is absent from recognition, with the first returned token spanning0–0.92s. Both complete instruction clauses and the ending are represented; do not infer an audible omission from this result alone.',
 '점수의 is now represented correctly. 배점표 is transcribed 배전표 in this whole result. The entire complete paragraph and ending are represented; compare the new PCM in independent and original-head contexts.'
]
rows=[]
for d,note in zip(data['results'],notes):
 p=BASE/'localized-voice-repair-whole-asr-v4'/(d['id']+'.json'); assert read(p)==d and not d['expectedWasRecognizerPrompt']
 assert sha(ROOT/d['sourcePath'])==d['sourceSha256']==d['audioSha256']
 rows.append(dict(id=d['id'],path=rel(p),sha256=sha(p),expectedKo=d['expectedKo'],actualText=d['text'],
  allExpectedAndEntireActualTextDirectlyRead=True,wordsAndFinalSoundDirectlyRead=True,
  exactCurrentSourcePcmMatched=True,sourceSha256=d['sourceSha256'],observation=note,
  noRecognizedWholeSentenceOmission=True,noRecognizedWholeSentenceRepetition=True,noRecognizedInventedGreeting=True))
reviewp=BASE/'localized-voice-repair-whole-direct-review-v4.json'; assert not reviewp.exists()
save(reviewp,dict(schemaVersion=1,reviewedAt=stamp,wholeCount=2,allWholeTextsDirectlyCompared=True,rows=rows,
 currentVoiceApproved=False,finalMixedAsrApproved=False,actualSynthesisErrorConfirmed=False,
 candidateParagraphsAdopted=False,humanListening='pending',humanPronunciation='pending',
 unresolvedRecognitionVariants=['22 지금은 absent from recognition','23 배점표/배전표'],
 resolvedRecognitionVariant='23 점수의 represented correctly in the whole result',
 endingHeuristicUsedForApproval=False,actualOuterExitCode=0,sessionId=args.session_id))
script=read(ROOT/'projects/presenting-game-scores/script/narration.ko.json')
freshscript=read(ROOT/'projects/presenting-game-scores/script/localized-voice-repair-v4.ko.json')
tts=read(BASE/'localized-voice-repair-tts-execution-v4.json'); assert tts['actualExitObserved'] and tts['exitCode']==0
contexts=[]
for d in data['results']:
 contexts.append(dict(id=d['id']+'-complete-independent',sourcePath=d['sourcePath'],sourceSha256=d['sourceSha256'],
  startSample=0,endSample=d['sourceSamples'],zeroPaddingSamplesEachSide=14400,expectedKo=d['expectedKo'],
  completeParagraphs=[1],boundaryEvidence=dict(entireCurrentParagraph=True,wholeWordsRead=True,wholeReview=rel(reviewp)),
  purpose='Independently recognize the entire unchanged paragraph with0.6s zero padding on each side; expected text is not supplied to the recognizer.'))
joins=[]
originaltts=read(BASE/'narration-tts-execution-v1.json')
directory=ROOT/'shared/output/presenting-game-scores/research/localized-review-joins-v4'; assert not directory.exists(); directory.mkdir(parents=True)
for originalid,freshid,headsamples,outid,paragraphcount in [
 ('07-name-and-unit','22-named-fields-guide-repair',103560,'07-first-paragraph-and-complete-named-guide',1),
 ('04-evaluation-weights','23-evaluation-p3-particle-candidate',339360,'04-complete-original-head-new-p3',2)]:
 original=next(x for x in originaltts['results'] if x['id']==originalid)
 fresh=next(x for x in tts['results'] if x['id']==freshid)
 assert sha(ROOT/original['path'])==original['sha256'] and sha(ROOT/fresh['path'])==fresh['sha256']
 op,params=pcm(ROOT/original['path']); fp,fparams=pcm(ROOT/fresh['path']); assert params[:3]==fparams[:3]
 head=op[:headsamples*2]; quiet=array.array('h',head[-480:]); rms=math.sqrt(sum(x*x for x in quiet)/len(quiet)); peak=max(map(abs,quiet)); assert rms<64 and peak<256
 destination=directory/(outid+'.wav'); joined=head+fp
 with wave.open(str(destination),'wb') as w: w.setparams(params); w.writeframes(joined)
 actual,_=pcm(destination); assert actual==joined and actual[:len(head)]==head and actual[len(head):]==fp
 expected=next(x for x in script['scenes'] if x['id']==originalid)['lines'][:paragraphcount]+next(x for x in freshscript['scenes'] if x['id']==freshid)['lines']
 proof=dict(id=outid,path=rel(destination),sha256=sha(destination),samples=len(joined)//2,seconds=len(joined)/48000,
  originalPath=original['path'],originalSha256=original['sha256'],originalRetainedSamples=[0,headsamples],
  freshPath=fresh['path'],freshSha256=fresh['sha256'],exactOriginalHeadBytesMatched=True,exactEntireFreshParagraphBytesMatched=True,
  observedLast10msRms=rms,observedLast10msPeak=peak,noFadeGainOrSpeechTrim=True,adopted=False,localOnly=True)
 joins.append(proof)
 contexts.append(dict(id=outid,sourcePath=rel(destination),sourceSha256=sha(destination),startSample=0,endSample=len(joined)//2,
  zeroPaddingSamplesEachSide=14400,expectedKo=expected,completeParagraphs=list(range(1,paragraphcount+2)),
  boundaryEvidence=dict(exactCompleteOriginalHeadAndEntireFreshParagraph=True,originalQuietEndSample=headsamples,
   observedLast10msRms=rms,observedLast10msPeak=peak),
  purpose='Complete semantic original lead and exact new paragraph; preserve every retained sample and the entire ending.'))
joinp=BASE/'localized-complete-review-joins-pcm-verification-v4.json'; assert not joinp.exists()
save(joinp,dict(schemaVersion=1,verifiedAt=stamp,joins=joins,productionAdopted=False,allOriginalTenAndCandidateElevenPreserved=True))
for c in contexts[2:]: c['boundaryEvidence'].update(compositionProof=rel(joinp),compositionProofSha256=sha(joinp))
planp=BASE/'localized-voice-repair-independent-context-plan-v4.json'; assert not planp.exists()
save(planp,dict(schemaVersion=1,createdAt=stamp,wholeReview=rel(reviewp),wholeReviewSha256=sha(reviewp),
 boundariesDirectlyComparedWithCurrentWordsAndPCM=True,contexts=contexts,expectedWasRecognizerPrompt=False,
 automaticApproval=False,currentVoiceApproved=False))
cpp=BASE/'latest-checkpoint.json'; cp=read(cpp); cp.update(recordedAt=stamp,stage='localized-whole-direct-review-contexts-prepared-v4',
 ownedJob=None,currentVoiceApproved=False,asrApproved=False,narrationApproved=False,
 nextAction='Fresh resources and current duplicate gate, then one CPU2/GPU0 recognition of four complete independent/semantic PCM contexts. Read every whole text and word; preserve onset/term uncertainty until resolved.')
save(cpp,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
 raw=qp.read_text('utf-8-sig'); q=json.loads(raw); item=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
 item.update(stage=cp['stage'],currentExecution=None,nextAction=cp['nextAction']); item['checkpoints']['narration']=False; q['updatedAt']=stamp; q['lastProgressAt']=stamp
 if qp.read_text('utf-8-sig')==raw: save(qp,q); break
else: raise RuntimeError('Concurrent queue change; preserve foreign work.')
print(json.dumps(dict(wholeTextsDirectlyRead=2,completeContextsPrepared=4,currentVoiceApproved=False)))
