"""Bind directly read whole text/words and disclose exact-PCM sentence boundaries."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,wave,numpy as np
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
wholep=O/'cross-game-whole-asr-execution-v2.json';whole=read(wholep)
assert whole['actualExitObserved'] and whole['actualOuterSession']==56931 and whole['actualOuterExitCode']==0 and whole['completed']==5
gaps={'01b':[],'03b':[(2.86,3.06),(6.58,6.84),(10.8,11.06),(16.04,16.32)],'07b':[(3.86,4.3),(7.4,7.78),(12.08,12.38),(16.56,16.98),(20.96,21.18)],'10b':[(5.82,6.34),(10.54,10.78),(14.46,14.76),(21.26,21.8),(24.56,24.88)],'21r':[]}
notes={'01b':'Full overview sentence and its last 적용하겠습니다 recovered; source6s and original20.16s form26.16s overview before pauses/frame rounding.', '03b':'Allfive full paragraphs recovered, including cycling rules, position/lean, inverted/upright result and two directions; spacing alternatives only.', '07b':'Allsix contexts present, but 탈것/탈컷 and 움직이므로/움직임으로, 화면의 선은/화면에서는, 앞의/앞에 alternatives held for independentcomplete reading. No exact pronunciation or acoustic-failure claim.', '10b':'Allsix contexts and size-versus-rotation disclaimer recovered; 놓기 전의/놓기 전에 grammatical alternative held for independentcomplete reading.', '21r':'Wholecurrent candidate recovers initial 시작 and the complete original firstsentence. Independentcurrent diagnosis and splicedwhole/seam review required before finaladoption.'}
rp=O/'cross-game-whole-direct-review-v2.json';assert not rp.exists()
review=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),execution=wholep.relative_to(ROOT).as_posix(),executionSha256=sha(wholep),actualWholeSession=56931,actualExitCode=0,actualCompletion='c6d739',allWholeTextsDirectlyCompared=True,allCurrentWordLandmarksDirectlyCompared=True,actualFullReads=['678d6f03b/07b wholewords','b37614 10b/01b wholewords','5484e5 21r wholewords'],rows=[dict(id=r['id'],sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],expectedWholeText=' '.join(r['expectedKo']),recognizedWholeText=r['text'],note=notes[r['id']]) for r in whole['results']],wholeContentApprovalHeldForIndependentContexts=True,humanListeningApproved=False,humanPronunciationApproved=False,finalMixedAsrApproved=False,repairCandidateAdopted=False)
rp.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
contexts=[];energies={}
for row in whole['results']:
 source=ROOT/row['sourcePath'];assert sha(source)==row['sourceSha256']
 with wave.open(str(source),'rb') as wav:
  assert (wav.getframerate(),wav.getnchannels(),wav.getsampwidth())==(24000,1,2);frames=wav.getnframes();pcm=wav.readframes(frames)
 signal=np.frombuffer(pcm,dtype='<i2');bounds=[0];evidence=[]
 for a,b in gaps[row['id']]:
  # Bounds came from directly read current finalword/next-firstword landmarks.
  lo,hi=round(a*24000),round(b*24000);mid=(lo+hi)//2
  if hi-lo>=960:mid=min(range(lo+240,hi-239,120),key=lambda x:np.mean(signal[x-240:x+240].astype(float)**2))
  e=signal[mid-240:mid+240].astype(float);bounds.append(mid);evidence.append(dict(wordGapSeconds=[a,b],boundarySample=mid,boundarySeconds=mid/24000,windowSamples=480,rmsInt16=float(np.sqrt(np.mean(e**2))),peakInt16=int(np.max(np.abs(e))),humanListeningApproval=False))
 bounds.append(frames);assert len(bounds)==len(row['expectedKo'])+1;energies[row['id']]=evidence
 for i,line in enumerate(row['expectedKo']):
  a,b=bounds[i:i+2];assert 0<=a<b<=frames
  contexts.append(dict(id=f'{row["id"]}-p{i+1:02}',sceneId=row['id'],paragraphIndex=i,expectedKo=line,sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],startSample=a,endSample=b,sourceSampleRate=24000,startSeconds=a/24000,endSeconds=b/24000,zeroPaddingSamplesEachSide=7200,exactContextPcmSha256=hashlib.sha256(pcm[a*2:b*2]).hexdigest(),expectedWasRecognizerPrompt=False,boundaryEvidence=evidence))
assert len(contexts)==19
p=O/'cross-game-independent-context-proposal-v2.json';assert not p.exists();p.write_text(json.dumps(dict(createdAt=datetime.now(timezone.utc).isoformat(),wholeReview=rp.relative_to(ROOT).as_posix(),wholeReviewSha256=sha(rp),wholeExecution=wholep.relative_to(ROOT).as_posix(),wholeExecutionSha256=sha(wholep),contexts=contexts,boundariesDirectlyComparedWithCurrentWordsAndPCM=False,finalCueTimingApproved=False,humanListeningApproved=False,modelExecuted=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(contexts=len(contexts),energyEvidence=energies),ensure_ascii=False))
