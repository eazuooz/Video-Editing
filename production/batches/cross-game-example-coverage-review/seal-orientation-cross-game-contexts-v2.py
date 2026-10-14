"""Seal reviewed14 word gaps with disclosed diagnostic overlap; not caption timing."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,wave
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=O/'cross-game-independent-context-proposal-v2.json';proposal=read(p)
assert len(proposal['contexts'])==19 and sha(ROOT/proposal['wholeReview'])==proposal['wholeReviewSha256']
contexts=[]
for row in proposal['contexts']:
 source=ROOT/row['sourcePath'];assert sha(source)==row['sourceSha256']
 with wave.open(str(source),'rb') as wav:frames=wav.getnframes();pcm=wav.readframes(frames)
 r=dict(row)
 # Preserve phonetic onset/end context at each observed sentence gap, including
 # gaps where the quietest20ms window sits near the next word landmark.
 if r['startSample']>0:r['startSample']=max(0,r['startSample']-2880)
 if r['endSample']<frames:r['endSample']=min(frames,r['endSample']+2880)
 a,b=r['startSample'],r['endSample'];r.update(startSeconds=a/24000,endSeconds=b/24000,exactContextPcmSha256=hashlib.sha256(pcm[a*2:b*2]).hexdigest(),boundaryContextOverlapSamples=2880,boundaryScope='120ms overlap around directly read current word gaps plus exactPCM energy windows; independent diagnostic only, no finalcue or human acoustic approval.')
 contexts.append(r)
out=O/'cross-game-independent-context-plan-v2.json';assert not out.exists();out.write_text(json.dumps(dict(createdAt=datetime.now(timezone.utc).isoformat(),proposal=p.relative_to(ROOT).as_posix(),proposalSha256=sha(p),wholeReview=proposal['wholeReview'],wholeReviewSha256=proposal['wholeReviewSha256'],contexts=contexts,contextCount=19,boundariesDirectlyComparedWithCurrentWordsAndPCM=True,actualEnergyEvidenceRead='7f1277 exit0,all14 boundaries',allExpectedWholeTextsRead=True,zeroPaddingSamplesEachSide=7200,expectedWasRecognizerPrompt=False,finalCueTimingApproved=False,modelExecuted=False,humanListeningApproved=False,repairCandidateAdopted=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(contexts=19,wordGaps=14,diagnosticOverlapMs=120,originalAndNewPcmUnchanged=True)))
