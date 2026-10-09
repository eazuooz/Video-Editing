"""Record four full directly read contexts without treating recognition as listening."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,d):
 t=p.with_name(p.name+'.recording');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--outer-exit-code',type=int,required=True);ap.add_argument('--session-id',type=int,required=True);args=ap.parse_args()
stamp=datetime.now(timezone.utc).isoformat();sp=BASE/'localized-voice-repair-contexts-asr-execution-v4.json';state=read(sp)
assert state['exitCode']==args.outer_exit_code==0 and state['completed']==state['total']==4
sessionp=sp.with_name(sp.stem+'.session.json');s=read(sessionp);assert s['sessionId']==args.session_id and s['pid']==state['pid']
try:assert abs(psutil.Process(state['pid']).create_time()-state['createTime'])>=.01
except psutil.NoSuchProcess:pass
state.update(actualExitObserved=True,actualOuterExitCode=0,actualOuterSessionId=args.session_id,actualWorkerAlive=False,actualExitObservedAt=stamp);save(sp,state)
s.update(actualExitObserved=True,exitCode=0,workerExpectedRunning=False,observedAt=stamp);save(sessionp,s)
data=read(BASE/'localized-voice-repair-contexts-asr-v4/asr.json');assert data['complete'] and len(data['results'])==4
notes=[
 'Full independent first candidate again starts with 점수를; 지금은 absent in recognized text. Complete clauses and final sound are represented; first timestamp includes padding. No audible omission is asserted.',
 'Full independent second candidate preserves 점수의 but transcribes 배점표 as 배전표. Entire paragraph and ending represented.',
 'Complete original first paragraph and full new guide represented, but 지금은 remains absent from the guide recognition. The semantic-lead result starts 점수를 at5.36s,0.445s after the exact guide boundary plus padding; inspect existing audio with a different unprompted decoding method before more synthesis.',
 'All three complete paragraphs and the new exact PCM join represented. 점수의 is preserved and 배점표 is again 배전표. T-Spin-Double and Back-to-Back reflect the expected action labels; no extra action or invented greeting.'
]
rows=[]
for d,note in zip(data['results'],notes):
 p=BASE/'localized-voice-repair-contexts-asr-v4'/(d['id']+'.json');assert read(p)==d and d['exactSourceSampleBytesMatched'] and not d['expectedWasRecognizerPrompt']
 assert sha(ROOT/d['sourcePath'])==d['sourceSha256'] and sha(ROOT/d['contextPath'])==d['contextSha256']==d['audioSha256']
 rows.append(dict(id=d['id'],path=rel(p),sha256=sha(p),expectedKo=d['expectedKo'],actualText=d['text'],
  allExpectedAndEntireActualTextDirectlyRead=True,wordsAndFinalSoundDirectlyRead=True,
  exactCurrentSourcePcmMatched=True,sourceSha256=d['sourceSha256'],contextSha256=d['contextSha256'],observation=note,
  noRecognizedWholeSentenceOmission=True,noRecognizedWholeSentenceRepetition=True,noRecognizedInventedGreeting=True))
proofp=BASE/'localized-voice-repair-contexts-direct-review-v4.json';assert not proofp.exists()
save(proofp,dict(schemaVersion=1,reviewedAt=stamp,rows=rows,completeContextCount=4,
 standaloneCompleteContexts=2,completeOriginalSemanticLeadContexts=2,allWholeTextsDirectlyCompared=True,
 allIndependentContextsDirectlyCompared=True,allNewV4WindowsDirectlyCompared=6,
 unresolvedRecognitionVariants=['22 지금은 absent from recognition','23 배점표/배전표'],
 currentVoiceApproved=False,finalMixedAsrApproved=False,actualSynthesisErrorConfirmed=False,
 candidateParagraphsAdopted=False,humanListening='pending',humanPronunciation='pending',
 endingHeuristicUsedForApproval=False,actualOuterExitCode=0,sessionId=args.session_id,
 nextAction='Compare existing complete PCM with a different unprompted decoding method; preserve original10 and candidate11 and both new localized takes.'))
cpp=BASE/'latest-checkpoint.json';cp=read(cpp);cp.update(recordedAt=stamp,stage='localized-contexts-direct-review-decoding-comparison-preparation-v5',
 ownedJob=None,currentVoiceApproved=False,asrApproved=False,narrationApproved=False,
 nextAction='SingleCPU2/GPU0 unprompted beam5 comparison of the unresolved complete current PCM. No new synthesis or research control; final measured timing and all downstream approvals remain false.');save(cpp,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
 raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores');item.update(stage=cp['stage'],currentExecution=None,nextAction=cp['nextAction']);q['updatedAt']=stamp;q['lastProgressAt']=stamp
 if qp.read_text('utf-8-sig')==raw:save(qp,q);break
else:raise RuntimeError('Concurrent queue change; preserve foreign work.')
print('All six localized-v4 full windows directly compared; onset and term uncertainty retained, no narration/final-mix approval.')
