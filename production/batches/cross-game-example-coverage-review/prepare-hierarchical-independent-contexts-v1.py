"""Bind four fully read results and fourteen real word gaps to exact PCM proposals."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave,numpy as np
ROOT=Path(__file__).resolve().parents[3];V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
whole_path=V/'additions-whole-asr-execution-v1.json';whole=read(whole_path)
assert whole['actualExitObserved'] and whole['actualOuterSession']==58603 and whole['actualOuterExitCode']==0 and whole['completed']==4
gaps={'01b':[(4.6,4.86),(14.9,15.12)],'04a':[(9.76,9.94),(19.94,20.18),(29.62,30),(40.82,40.98)],
      '08a':[(11.42,11.62),(23.76,24),(35.02,35.6),(45.72,46.1)],
      '10a':[(12.3,12.58),(24.1,24.38),(35.06,35.5),(47.68,48.22)]}
notes={
 '01b':'All3paragraphs/4natural sentences and the final first-example connection recovered;23.84s within20–30s. No overview rerender/TTS needed.',
 '04a':'All5paragraphs and final confirmation sentence read. 표식의/표시계 and 아래의/아래에 alternatives held for independent complete contexts; no human pronunciation approval.',
 '08a':'All5paragraphs read. 주민에게 일을/주민의 기일 and 맞는 가지/만능가지 remain unrecovered in this whole result and are held for independent diagnosis. Raw extra greeting 다음 영상에서 만나요 spans only57.20..57.26 with two zero-duration words; preserve raw result and verify the full final paragraph independently before excluding it from exact-script timing.',
 '10a':'All5paragraphs and conclusion read. 표식의/표시계, source-name 배드타이드/Bedtide and 선로/설로 held for complete independent contexts. Units1m/2m and Off/On are numeric/language renderings of expected source UI. Warning about an ending timestamp is preserved; full ending text alone is not phonetic/word timing approval.'}
review_path=V/'additions-whole-direct-review-v1.json';proposal_path=V/'additions-independent-context-proposal-v1.json'
assert not review_path.exists() and not proposal_path.exists()
review=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),execution=whole_path.relative_to(ROOT).as_posix(),
 executionSha256=sha(whole_path),actualWholeSession=58603,actualExitCode=0,actualCompletion='31951f',actualClosure='38a4e8 exit0',
 actualWholeAndAllWordsRead='b220dd exit0,all4full expected/current texts and all455 current word rows',
 allWholeTextsDirectlyCompared=True,allCurrentWordLandmarksDirectlyCompared=True,
 rows=[dict(id=r['id'],sourcePath=r['sourcePath'],sourceSha256=r['sourceSha256'],
  expectedWholeText=' '.join(r['expectedKo']),recognizedWholeText=r['text'],note=notes[r['id']]) for r in whole['results']],
 wholeContentApprovalHeldForIndependentContexts=True,allFourNewPcmContentApproved=False,
 finalMixedAsrApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False)
contexts=[];energies={}
for row in whole['results']:
 p=ROOT/row['sourcePath'];assert sha(p)==row['sourceSha256']
 with wave.open(str(p),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
  n=w.getnframes();pcm=w.readframes(n)
 signal=np.frombuffer(pcm,dtype='<i2');bounds=[0];evidence=[]
 for lo_s,hi_s in gaps[row['id']]:
  lo,hi=round(lo_s*24000),round(hi_s*24000)
  candidates=range(lo+240,hi-239,120);assert len(candidates)>0
  mid=min(candidates,key=lambda x:np.mean(signal[x-240:x+240].astype(float)**2))
  e=signal[mid-240:mid+240].astype(float);bounds.append(mid)
  evidence.append(dict(observedWholeWordGap=[lo_s,hi_s],boundarySample=mid,boundarySeconds=mid/24000,
   windowSamples=480,rmsInt16=float(np.sqrt(np.mean(e**2))),peakInt16=int(np.max(np.abs(e))),
   windowPcmSha256=hashlib.sha256(pcm[(mid-240)*2:(mid+240)*2]).hexdigest(),humanListeningApproval=False))
 bounds.append(n);assert len(bounds)==len(row['expectedKo'])+1;energies[row['id']]=evidence
 for i,text in enumerate(row['expectedKo']):
  a,b=bounds[i:i+2];assert 0<=a<b<=n
  contexts.append(dict(id=f'{row["id"]}-p{i+1:02}',sceneId=row['id'],paragraphIndex=i,expectedKo=text,
   sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],startSample=a,endSample=b,
   sourceSampleRate=24000,startSeconds=a/24000,endSeconds=b/24000,zeroPaddingSamplesEachSide=7200,
   exactContextPcmSha256=hashlib.sha256(pcm[a*2:b*2]).hexdigest(),expectedWasRecognizerPrompt=False,boundaryEvidence=evidence))
assert len(contexts)==18
review_path.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf8')
proposal=dict(createdAt=datetime.now(timezone.utc).isoformat(),wholeReview=review_path.relative_to(ROOT).as_posix(),
 wholeReviewSha256=sha(review_path),contexts=contexts,energyEvidence=energies,
 boundariesDirectlyComparedWithCurrentWordsAndPCM=False,finalCueTimingApproved=False,modelExecuted=False,humanListeningApproved=False)
proposal_path.write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n','utf8')
# Keep the protected original review immutable. Correct a documentation count
# in an explicitly separate version after the actual voice closure.
tts=read(V/'narration-additions-execution-v1.json');assert tts['ownedClosureVerified']
old=V/'causal-paired-script-direct-review-v1.json';current=read(old)
current['previousReview']=dict(path=old.relative_to(ROOT).as_posix(),sha256=sha(old),preserved=True)
current['recordedAt']=datetime.now(timezone.utc).isoformat();current['pairedReviews'][0]['overviewSentenceCount']=4
current['pairedReviews'][0]['measuredSeconds']=23.84;current['pairedReviews'][0]['measuredLengthPending']=False
current['sentenceCountCorrectionOnly']=True;current['voiceOrMediaRepeatedForCount']=False
v2=V/'causal-paired-script-direct-review-v2.json';assert not v2.exists();v2.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(contexts=18,wholeReviewHeldForIndependent=True,energyEvidence=energies,overviewActualSentences=4,overviewSeconds=23.84),ensure_ascii=False))
