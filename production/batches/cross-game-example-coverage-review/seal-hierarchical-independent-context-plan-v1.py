"""Seal the14 directly read quiet-gap diagnostics with disclosed120ms overlap."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave
ROOT=Path(__file__).resolve().parents[3];V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=V/'additions-independent-context-proposal-v1.json';proposal=read(p)
assert len(proposal['contexts'])==18 and sha(ROOT/proposal['wholeReview'])==proposal['wholeReviewSha256']
execution=read(V/'additions-whole-asr-execution-v1.json')
count=sum(len(x['words']) for x in execution['results']);assert count==413
old_review=ROOT/proposal['wholeReview'];review=read(old_review)
review['previousReview']=dict(path=old_review.relative_to(ROOT).as_posix(),sha256=sha(old_review),preserved=True)
review['recordedAt']=datetime.now(timezone.utc).isoformat()
review['actualWholeAndAllWordsRead']=f'b220dd exit0,all4full expected/current texts and all{count} current word rows'
review['actualCurrentWordRowCount']=count;review['countFieldCorrectionOnly']=True;review['recognitionOrPcmRepeated']=False
review_path=V/'additions-whole-direct-review-v2.json';assert not review_path.exists()
review_path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf8')
contexts=[]
for row in proposal['contexts']:
 source=ROOT/row['sourcePath'];assert sha(source)==row['sourceSha256']
 with wave.open(str(source),'rb') as w:n=w.getnframes();pcm=w.readframes(n)
 r=dict(row)
 if r['startSample']>0:r['startSample']=max(0,r['startSample']-2880)
 if r['endSample']<n:r['endSample']=min(n,r['endSample']+2880)
 a,b=r['startSample'],r['endSample']
 r.update(startSeconds=a/24000,endSeconds=b/24000,exactContextPcmSha256=hashlib.sha256(pcm[a*2:b*2]).hexdigest(),
  boundaryContextOverlapSamples=2880,boundaryScope='120ms overlap around directly read current word gaps/PCM energy; diagnostic only; no finalcue or human acoustic approval.')
 contexts.append(r)
out=V/'additions-independent-context-plan-v1.json';assert not out.exists()
plan=dict(createdAt=datetime.now(timezone.utc).isoformat(),proposal=p.relative_to(ROOT).as_posix(),proposalSha256=sha(p),
 wholeReview=review_path.relative_to(ROOT).as_posix(),wholeReviewSha256=sha(review_path),contexts=contexts,contextCount=18,
 boundariesDirectlyComparedWithCurrentWordsAndPCM=True,actualEnergyEvidenceRead='ee0fb3 exit0,all14 word-gap/20ms PCM windows',
 actualWholeWordsRead='b220dd exit0',zeroPaddingSamplesEachSide=7200,expectedWasRecognizerPrompt=False,
 wholeReadbackStillHeldForIndependent=True,finalCueTimingApproved=False,humanListeningApproved=False,modelExecuted=False)
out.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf8')
normal_out=V/'candidate-normal-playback-observation-v3.json';assert not normal_out.exists()
proofs=[]
for point,name in [('start','timber-signal-normal-start-v1.ax.txt'),('end','timber-signal-normal-end-v2.ax.txt')]:
 path=V/'ui-proof-v1'/name;text=path.read_text('utf8')
 states=[json.loads(line[line.index('{'):]) for line in text.splitlines() if 'text {"source"' in line]
 assert states;state=states[-1]
 assert '6TNjosDftog' in state['source'] and state['intervalStart']==2416 and state['intervalEnd']==2456
 assert state['muted'] and state['playbackRate']==1 and (state['videoWidth'],state['videoHeight'])==(1920,1080)
 assert (not state['paused'] and 2416<=state['currentTime']<2417) if point=='start' else (state['paused'] and 2456<=state['currentTime']<2457)
 proofs.append(dict(point=point,evidence=path.relative_to(ROOT).as_posix(),sha256=sha(path),actualState=state))
normal=dict(recordedAt=datetime.now(timezone.utc).isoformat(),previous=dict(path='candidate-normal-playback-observation-v2.json',sha256=sha(V/'candidate-normal-playback-observation-v2.json')),
 newSignalSourceObservation=dict(sourceId='6TNjosDftog',actualCuaTab=127,normalStartEnd=proofs,
  savedEndV1WasDiffOnlyAndNotUsedAsFullStateEvidence=True,endV2CapturedFullPausedStateWithoutReplay=True,
  observedMeaning='Floodgate Badtide field assignment and separate lever Off-to-On state; no different-map/physical-flow success claim'),
 additionalEarlySourceObservation=dict(sourceId='6TNjosDftog',actualCuaTab=124,
  visibleStartSeconds=672,visibleEndSeconds=864,sourceRate=1,muted=True,
  evidence=[dict(path=(V/'ui-proof-v1'/name).relative_to(ROOT).as_posix(),sha256=sha(V/'ui-proof-v1'/name)) for name in ['timber-early-normal-start-v1.ax.txt','timber-early-normal-end-v1.ax.txt']],
  preciseSecondsNotPresentInSavedAx=True,allContinuousFramesDirectlyViewed=False,
  finding='Lodge/path placement and later LumberMill invalid-red preview are source observations; no completed plank output'),
 sourceWholePlaybackRepeated=False,allContinuousFramesApproved=False,finalNarratedCutApproved=False,
 humanWholeListeningApproved=False,publicRightsApproved=False)
normal_out.write_text(json.dumps(normal,ensure_ascii=False,indent=2)+'\n','utf8')
cp_path=V/'latest-checkpoint.json';cp=read(cp_path)
cp.update(recordedAt=plan['createdAt'],currentWholeDirectReview=review_path.relative_to(ROOT).as_posix(),
 independentContextPlan=out.relative_to(ROOT).as_posix(),causalScriptReview=(V/'causal-paired-script-direct-review-v2.json').relative_to(ROOT).as_posix(),
 candidateNormalReview=normal_out.relative_to(ROOT).as_posix(),newVoiceGenerationComplete=True,
 next='Fresh CPU resource then one18complete independent currentPCM ASR; directly compare resident-work/matching-branch/marker/game-name/ending alternatives. Preserve all4newPCM/12originalPCM. No TTS/source/native repeats.')
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(contexts=18,wordGaps=14,wholeWordRows=count,zeroPaddingMs=300,overlapMs=120,sourceNormalNew=1,wholeContentHeld=True)))
