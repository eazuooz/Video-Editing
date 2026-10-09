"""Record the directly read complete guide and two exact independent contexts."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,array,hashlib,json,math,os,psutil,wave
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
 t=p.with_name(p.name+'.recording');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def pcm(p):
 with wave.open(str(p),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
  return w.readframes(w.getnframes()),w.getparams()
ap=argparse.ArgumentParser();ap.add_argument('--outer-exit-code',type=int,required=True);ap.add_argument('--session-id',type=int,required=True);a=ap.parse_args();stamp=datetime.now(timezone.utc).isoformat()
sp=BASE/'named-guide-whole-asr-execution-v6.json';state=read(sp);assert state['exitCode']==a.outer_exit_code==0 and state['completed']==state['total']==1
sessionp=sp.with_name(sp.stem+'.session.json');s=read(sessionp);assert s['sessionId']==a.session_id and s['pid']==state['pid']
try:assert abs(psutil.Process(state['pid']).create_time()-state['createTime'])>=.01
except psutil.NoSuchProcess:pass
state.update(actualExitObserved=True,actualOuterExitCode=0,actualOuterSessionId=a.session_id,actualWorkerAlive=False,actualExitObservedAt=stamp);save(sp,state);s.update(actualExitObserved=True,exitCode=0,workerExpectedRunning=False,observedAt=stamp);save(sessionp,s)
data=read(BASE/'named-guide-whole-asr-v6/asr.json');assert data['complete'] and len(data['results'])==1;d=data['results'][0]
assert not d['expectedWasRecognizerPrompt'] and sha(ROOT/d['sourcePath'])==d['sourceSha256']==d['audioSha256']
proofp=BASE/'named-guide-whole-direct-review-v6.json';assert not proofp.exists()
save(proofp,dict(schemaVersion=1,reviewedAt=stamp,wholeCount=1,allWholeTextsDirectlyCompared=True,
 rows=[dict(id=d['id'],expectedKo=d['expectedKo'],actualText=d['text'],sourceSha256=d['sourceSha256'],
  path=rel(BASE/'named-guide-whole-asr-v6'/(d['id']+'.json')),allExpectedAndEntireActualTextDirectlyRead=True,
  wordsAndFinalSoundDirectlyRead=True,observation='먼저 and every word in both complete sentences are represented. Spacing/punctuation differences only; ending timestamp7.58s within actual7.6s PCM. No recognized omission, repetition or invented greeting.')],
 currentVoiceApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',
 endingHeuristicUsedForApproval=False,actualOuterExitCode=0,sessionId=a.session_id))
original=next(x for x in read(BASE/'narration-tts-execution-v1.json')['results'] if x['id']=='07-name-and-unit');assert sha(ROOT/original['path'])==original['sha256']
op,params=pcm(ROOT/original['path']);fp,fparams=pcm(ROOT/d['sourcePath']);assert params[:3]==fparams[:3]
headsamples=103560;head=op[:headsamples*2];quiet=array.array('h',head[-480:]);rms=math.sqrt(sum(x*x for x in quiet)/len(quiet));peak=max(map(abs,quiet));assert rms<64 and peak<256
directory=ROOT/'shared/output/presenting-game-scores/research/named-guide-review-join-v6';assert not directory.exists();directory.mkdir(parents=True)
destination=directory/'07-original-p1-and-complete-named-guide.wav';joined=head+fp
with wave.open(str(destination),'wb') as w:w.setparams(params);w.writeframes(joined)
actual,_=pcm(destination);assert actual==joined and actual[:len(head)]==head and actual[len(head):]==fp
joinp=BASE/'named-guide-complete-join-pcm-verification-v6.json';assert not joinp.exists()
save(joinp,dict(schemaVersion=1,verifiedAt=stamp,path=rel(destination),sha256=sha(destination),samples=len(joined)//2,
 originalPath=original['path'],originalSha256=original['sha256'],originalRetainedSamples=[0,headsamples],
 freshPath=d['sourcePath'],freshSha256=d['sourceSha256'],exactOriginalHeadBytesMatched=True,exactEntireFreshParagraphBytesMatched=True,
 observedLast10msRms=rms,observedLast10msPeak=peak,noFadeGainOrSpeechTrim=True,adopted=False,localOnly=True))
originalp1=next(x for x in read(ROOT/'projects/presenting-game-scores/script/narration.ko.json')['scenes'] if x['id']=='07-name-and-unit')['lines'][0]
contexts=[dict(id='24-complete-named-guide-independent',sourcePath=d['sourcePath'],sourceSha256=d['sourceSha256'],startSample=0,endSample=d['sourceSamples'],
 zeroPaddingSamplesEachSide=14400,expectedKo=d['expectedKo'],completeParagraphs=[1],boundaryEvidence=dict(entireCurrentParagraph=True,wholeWordsDirectlyRead=True)),
 dict(id='07-original-p1-and-complete-named-guide',sourcePath=rel(destination),sourceSha256=sha(destination),startSample=0,endSample=len(joined)//2,
 zeroPaddingSamplesEachSide=14400,expectedKo=[originalp1,*d['expectedKo']],completeParagraphs=[1,2],
 boundaryEvidence=dict(exactOriginalFirstParagraphAndCompleteNewGuideMatched=True,compositionProof=rel(joinp),compositionProofSha256=sha(joinp)))]
planp=BASE/'named-guide-independent-context-plan-v6.json';assert not planp.exists()
save(planp,dict(schemaVersion=1,createdAt=stamp,wholeReview=rel(proofp),wholeReviewSha256=sha(proofp),
 boundariesDirectlyComparedWithCurrentWordsAndPCM=True,contexts=contexts,expectedWasRecognizerPrompt=False,currentVoiceApproved=False))
print('One complete whole result directly read; two exact independent/semantic contexts prepared. Final mix and human listening remain pending.')
