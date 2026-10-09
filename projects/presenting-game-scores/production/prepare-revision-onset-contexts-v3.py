"""Record direct whole2 review and five complete, padded current-PCM contexts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
def fresh(p,j):
 assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
s=read(B/'voice-whole-asr-execution-v3.json');assert s['exitCode']==0 and s['actualExitObserved']
j=read(B/'voice-whole-asr-v3/asr.json');assert j['complete'] and len(j['results'])==2
req=read(B/'narration-tts-request-v3.json');script=read(ROOT/read(ROOT/req['manifestOverride'])['paths']['script'])
byid={x['id']:x for x in script['scenes']}
points={'r01-overview':[4.24,12.62],'r10-audit-and-close-p2':[5.36]}
metrics=[];inputs=[];bounds={}
for r in j['results']:
 assert sha(ROOT/r['sourcePath'])==r['sourceSha256'] and r['expectedWasRecognizerPrompt'] is False
 with wave.open(str(ROOT/r['sourcePath']),'rb') as w:
  assert (w.getframerate(),w.getsampwidth(),w.getnchannels(),w.getnframes())==(24000,2,1,r['samples'])
  pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
 mids=[]
 for t in points[r['id']]:
  n=round(t*24000);v=pcm[n-120:n+120].astype(float)
  metric=dict(id=r['id'],sourceSha256=r['sourceSha256'],sample=n,seconds=t,rms=float(np.sqrt(np.mean(v*v))),peak=int(np.max(np.abs(v))),windowSamples=240,completeSentenceEndingRead=True,nextSentenceOnsetRead=True,noRemovedSamples=True)
  metrics.append(metric);assert metric['rms']<100 and metric['peak']<350,metric;mids.append(n)
 boundaries=[0]+mids+[r['samples']];bounds[r['id']]=boundaries
 lines=byid[r['id']]['lines'] if r['id']=='r01-overview' else [byid[r['id']]['lines'][0].split('. ',1)[0]+'.',byid[r['id']]['lines'][0].split('. ',1)[1]]
 assert len(lines)==len(boundaries)-1
 for i,(a,b,text) in enumerate(zip(boundaries,boundaries[1:],lines),1):
  inputs.append(dict(id=r['id']+'-complete-sentence-'+str(i),sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],startSample=a,endSample=b,samples=b-a,zeroPaddingSamplesEachSide=9600,expectedKo=text,boundaryMethod='Complete expected/recognized sentence and actual 10ms PCM quiet bin directly compared; no spoken samples removed'))
 r['directReview']=True;r['allCompleteClausesAndEndingsPresent']=True
 r['finding']='All overview question/order/outcome clauses exactly present; new card-scoring wording removes the old 기어가 alternative.' if r['id']=='r01-overview' else '앞서 본 테트리스 onset present without former 스 onset. All two sentences/endings present. 카드의/카드에 is preserved as a particle pronunciation/recognizer alternative for human review, not a changed substantive claim.'
reviewp=B/'voice-whole-direct-review-v3.json'
fresh(reviewp,dict(schemaVersion=3,reviewedAt=datetime.now(timezone.utc).isoformat(),allWholeTextsDirectlyCompared=True,allCurrentWordsAndEndingsDirectlyRead=True,results=j['results'],quietBoundaries=metrics,currentCompleteVoiceApproved=False,contentReadyForIndependentContexts=True,humanListening='pending',humanPronunciation='pending',finalMixedAsrApproved=False))
fresh(B/'voice-repair-boundaries-v3.json',dict(boundaries=bounds,metrics=metrics,allSourceSamplesPreserved=True,overviewMeasuredSeconds=21.36,finalTimingApproved=False))
fresh(B/'voice-contexts-asr-plan-v3.json',dict(schemaVersion=3,preparedAt=datetime.now(timezone.utc).isoformat(),wholeDirectReview=rel(reviewp),wholeDirectReviewSha256=sha(reviewp),boundariesDirectlyComparedWithCurrentWordsAndPcm=True,inputs=inputs,automaticApproval=False,modelsStarted=0))
print(json.dumps(dict(wholeTextsDirectlyCompared=2,completeContextsPrepared=len(inputs),quietBoundaries=metrics,contextAsrStarted=False),ensure_ascii=False))
