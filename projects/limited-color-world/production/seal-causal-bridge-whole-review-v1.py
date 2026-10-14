"""Record the three whole transcripts directly compared; prepare complete contexts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
 t=p.with_name(p.name+'.sealing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
sp=BASE/'causal-bridge-whole-asr-execution-v1.json';state=read(sp)
sessionPath=sp.with_name(sp.stem+'.session.json');session=read(sessionPath)
assert state['exitCode']==0 and state['completed']==state['total']==3 and session['sessionId']==31431
assert not psutil.pid_exists(state['pid']) or abs(psutil.Process(state['pid']).create_time()-state['createTime'])>.01
stamp=datetime.now(timezone.utc).isoformat()
state.update(actualExitObserved=True,actualOuterSession=31431,actualOuterExitCode=0,actualToolExitObservation='7fce94',actualExitObservedAt=stamp);save(sp,state)
session.update(actualExitObserved=True,actualExitCode=0,actualToolExitObservation='7fce94');save(sessionPath,session)
asrp=BASE/'causal-bridge-whole-asr-v1/asr.json';asr=read(asrp);assert asr['complete'] and len(asr['results'])==3
ko=read(ROOT/'projects/limited-color-world/script/causal-bridges.v1.ko.json')
en=read(ROOT/'projects/limited-color-world/script/causal-bridges.v1.en.json')
notes=[
 ('All static structure, changing platform height, next motion and character movement sentences recognized in order. Spacing/punctuation only; full final 함께 보겠습니다 retained.',[]),
 ('All tops/destination/background, boundary lost in darkness and contrast-check sentences recognized. 밝고→밟고 is an unresolved recognition/pronunciation alternative, not a confirmed script omission. Full final 확인해 보겠습니다 retained.',['밝고→밟고']),
 ('Full cue set, changed-color conditions and broader checks recognized. Initial 지금까지→끝까지 and 무늬→문이 are unresolved recognition/pronunciation alternatives. Full final 다시 살펴봐야 합니다 retained.',['지금까지→끝까지','무늬→문이'])]
rows=[];contexts=[]
for k,e,r,(note,alts) in zip(ko['scenes'],en['scenes'],asr['results'],notes):
 assert k['id']==e['id']==r['id'] and r['expectedKo']==k['lines'] and sha(ROOT/r['sourcePath'])==r['sourceSha256']
 with wave.open(str(ROOT/r['sourcePath']),'rb') as w:
  assert w.getframerate()==24000 and w.getnchannels()==1 and w.getsampwidth()==2 and w.getnframes()==r['sourceSamples']
  pcm=w.readframes(w.getnframes())
 rows.append(dict(id=k['id'],expectedKo=k['lines'],expectedEn=e['lines'],actualWholeText=r['text'],
  currentPcmPath=r['sourcePath'],currentPcmSha256=r['sourceSha256'],seconds=r['seconds'],wholeCompleteParagraphDirectlyCompared=True,
  confirmedOmittedOrRepeatedSentence=False,recognitionAlternatives=alts,comparison=note,wholeWords=r['words'],humanPronunciation='pending'))
 contexts.append(dict(id=k['id']+'-p01',sceneId=k['id'],paragraph=1,sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],
  startSample=0,endSample=r['sourceSamples'],startSeconds=0,endSeconds=r['seconds'],seconds=r['seconds'],
  expectedKo=k['lines'],expectedEn=e['lines'],wholeRecognizedContext=r['text'],wholeFirstWord=r['words'][0],wholeLastWord=r['words'][-1],
  zeroPaddingSamplesEachSide=4800,partitionPcmSha256=hashlib.sha256(pcm).hexdigest(),completeOriginalParagraph=True,
  preservesEveryOriginalPcmSample=True,boundaryScope='One complete causal paragraph, all original samples including start and final decay; 200ms silence each side for independent recognition.'))
rp=BASE/'causal-bridge-whole-voice-direct-review-v1.json';assert not rp.exists()
review=dict(schemaVersion=1,reviewedAt=stamp,wholeAsr=rel(asrp),wholeAsrSha256=sha(asrp),actualSession=31431,actualExitCode=0,
 actualToolExitObservation='7fce94',allWholeTextsDirectlyCompared=True,currentPcmHashesMatched=True,
 expectedWasRecognizerPrompt=False,heuristicIsApproval=False,endingOnlyApproval=False,rows=rows,
 independentContextsApproved=False,narrationApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending')
save(rp,review)
pp=BASE/'causal-bridge-independent-context-plan-v1.json';assert not pp.exists()
save(pp,dict(schemaVersion=1,preparedAt=stamp,wholeReview=rel(rp),wholeReviewSha256=sha(rp),currentWholeAsrSha256=sha(asrp),
 boundariesDirectlyComparedWithCurrentWordsAndPCM=True,exactSamplePartitionPreservesAll3Pcm=True,contexts=contexts,total=3,
 independentRecognitionCompleted=False,automaticApproval=False,humanPronunciation='pending'))
print('Whole3 full texts/current PCM compared; 3 complete independent contexts prepared; recognition alternatives and final-mix gates pending.')
