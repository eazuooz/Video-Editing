"""Seal all complete independent bridge texts; retain alternatives and prepare targeted full sentences."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
 t=p.with_name(p.name+'.sealing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
sp=BASE/'causal-bridge-contexts-asr-execution-v1.json';state=read(sp);sessionPath=sp.with_name(sp.stem+'.session.json');session=read(sessionPath)
assert state['exitCode']==0 and state['completed']==state['total']==3 and session['sessionId']==13857
assert not psutil.pid_exists(state['pid']) or abs(psutil.Process(state['pid']).create_time()-state['createTime'])>.01
stamp=datetime.now(timezone.utc).isoformat()
state.update(actualExitObserved=True,actualOuterSession=13857,actualOuterExitCode=0,actualToolExitObservation='08b0b4',actualExitObservedAt=stamp);save(sp,state)
session.update(actualExitObserved=True,actualExitCode=0,actualToolExitObservation='08b0b4');save(sessionPath,session)
asrp=BASE/'causal-bridge-contexts-asr-v1/asr.json';asr=read(asrp);assert asr['complete'] and len(asr['results'])==3
wholep=BASE/'causal-bridge-whole-voice-direct-review-v1.json';whole=read(wholep)
notes=[('Full three-sentence causal paragraph agrees with expected wording apart from spacing/punctuation. All current PCM samples retained.',[]),
 ('Full three sentences agree except 밝고→밟고 persists. This is a pronunciation/recognition alternative; full last sentence ends 확인해보겠습니다.',['밝고→밟고']),
 ('Full two sentences agree except 지금까지→끝까지 persists at the start. 무늬 is correctly recognized in the independent context, unlike whole 문이. Complete final condition/check sentence and ending retained.',['지금까지→끝까지'])]
rows=[]
for r,w,(note,alts) in zip(asr['results'],whole['rows'],notes):
 assert r['sceneId']==w['id'] and r['expectedKo']==w['expectedKo'] and r['expectedEn']==w['expectedEn']
 assert sha(ROOT/r['sourcePath'])==r['sourceSha256']==w['currentPcmSha256']
 assert sha(ROOT/r['contextPath'])==r['contextSha256'] and r['exactSourceSampleBytesMatched']
 rows.append(dict(id=r['id'],sceneId=r['sceneId'],expectedKo=r['expectedKo'],expectedEn=r['expectedEn'],actualWholeText=w['actualWholeText'],actualIndependentCompleteText=r['text'],
  currentPcmSha256=r['sourceSha256'],independentContextSha256=r['contextSha256'],allOriginalSamplesPreserved=True,wholeAndIndependentFullTextsDirectlyCompared=True,
  recognitionAlternatives=alts,comparison=note,words=r['words'],humanPronunciation='pending'))
rp=BASE/'causal-bridge-independent-voice-direct-review-v1.json';assert not rp.exists()
save(rp,dict(schemaVersion=1,reviewedAt=stamp,wholeReview=rel(wholep),wholeReviewSha256=sha(wholep),independentAsr=rel(asrp),independentAsrSha256=sha(asrp),
 actualSession=13857,actualExitCode=0,actualToolExitObservation='08b0b4',allThreeWholeAndIndependentFullTextsDirectlyCompared=True,
 currentPcmHashesMatched=True,allOriginalPcmSamplesPreserved=True,rows=rows,expectedWasRecognizerPrompt=False,heuristicIsApproval=False,
 boundedCurrentVoiceTextReviewComplete=True,narrationApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',
 nextAction='Recognize two complete targeted sentences with 800ms silence padding to inspect persistent beginning/밝고 alternatives. Never silently correct ASR text or regenerate successful PCM.'))
wa=read(BASE/'causal-bridge-whole-asr-v1/asr.json')['results']
targets=[]
for sceneId,start,end,text,en in [
 ('06b-outline-to-contrast',9.51,12.160041666666666,'이 문제를 밝고 어두운 차이로 확인해 보겠습니다.','We will examine that problem through lightness differences.'),
 ('07b-cues-to-check',0,4.46,'지금까지 윤곽과 무늬, 높이와 움직임, 밝기 차이를 연결했습니다.','We have connected outlines, patterns, height, motion and lightness differences.')]:
 r=next(x for x in wa if x['id']==sceneId)
 a=round(start*24000);b=round(end*24000);assert 0<=a<b<=r['sourceSamples']
 with wave.open(str(ROOT/r['sourcePath']),'rb') as f:f.setpos(a);pcm=f.readframes(b-a)
 words=[x for x in r['words'] if start-.01<=x['timestamp'][0]<end-.001]
 assert words and words[-1]['timestamp'][1]<=end+.001
 targets.append(dict(id=sceneId+'-target-complete-sentence',sceneId=sceneId,sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],
  startSample=a,endSample=b,startSeconds=a/24000,endSeconds=b/24000,seconds=(b-a)/24000,expectedKo=[text],expectedEn=[en],
  wholeRecognizedContext=''.join(x['text'] for x in words),wholeFirstWord=words[0],wholeLastWord=words[-1],zeroPaddingSamplesEachSide=19200,
  partitionPcmSha256=hashlib.sha256(pcm).hexdigest(),completeOriginalSentence=True,boundaryScope='Current complete-word gap; full sentence, not an ending-only approval.'))
tp=BASE/'causal-bridge-targeted-leading-context-plan-v1.json';assert not tp.exists()
save(tp,dict(schemaVersion=1,preparedAt=stamp,wholeReview=rel(wholep),wholeReviewSha256=sha(wholep),boundariesDirectlyComparedWithCurrentWordsAndPCM=True,
 contexts=targets,total=2,reason='Persistent lexical alternatives in two complete sentences; meaningful adaptive check after 3whole+3complete independent contexts.',automaticApproval=False))
print('Complete3 bridge contexts directly compared; all samples intact; two persistent alternatives retained with targeted complete-sentence plan.')
