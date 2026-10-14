"""Close the current header batch and bind one inspected repair representative."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1';R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1';B=Path(__file__).resolve().parent
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
sp=O/'current34-detailed-header-repair-render-execution-v2.json';s=rd(sp)
assert s['workerDead'] and s['actualOuterExitCode']==0 and len(s['scenes'])==11
r=next(x for x in s['scenes'] if x['id']=='03');x=r['samples'][4];assert x['path'].endswith('scene-03/frame-005.png') and sha(ROOT/x['path'])==x['sha256']
review=O/'detailed-header-repair-representative-direct-review-v2.json';assert not review.exists()
review.write_text(json.dumps(dict(reviewedAt=datetime.now(timezone.utc).isoformat(),execution=rel(sp),executionSha256=sha(sp),sample=x,observation='Full-resolution1920x1080 sample directly read: title/subtitle/rule now separated. Aircraft canopy, swept wings, tail, engine intakes and semantic axes remain visible. This one sample cannot approve every moving frame or final captions.',headerRepresentativePassed=True,whole11MovingSamplesApproved=False,normal11PlaybackApproved=False,final244CaptionPixelsApproved=False,newImageGit=0),ensure_ascii=False,indent=2)+'\n','utf-8')
out=R/'resource-and-annotation-handoff-v26.json';assert not out.exists()
previous=rd(R/'resource-and-annotation-handoff-v25.json');previous.update(recordedAt=datetime.now(timezone.utc).isoformat(),previousHandoff=rel(R/'resource-and-annotation-handoff-v25.json'),currentOwnedWorker=dict(state=rel(sp),stateSha256=sha(sp),sessionId=1557,actualCompletion='814e85',actualClosure='39e401',actualOuterExitCode=0,workerDead=True,all11RenderWholeDecodeExtractExit0=True,all79ProtectedUnchanged=True),headerRepresentativeReview=rel(review),activeOwnedWorkers=0,next='Read all11 header-repaired baselineV2 and six detailed revisionV1 moving samples and normal playback. Header03 one representative is corrected but whole approval is false. Complete remaining guide14/17/20/23 288samples74boards; normal8endpoints already verified. Build NEW assembly with detailed overviewV5/baselineV2/revisionV1 and genuine18storage/19code; generic assemblyV1 must not run. Then final244cue/cut/moving pixels and technical delivery workflow; no new TTS/ASR/mix.')
out.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=rd(O/'latest-checkpoint.json');cp.update(latestHandoff=rel(out),detailedHeaderRepresentativeReview=rel(review));(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
q=rd(B/'queue.json');q['currentOrientationReview'].update(latestHandoff=rel(out),detailedHeaderRepresentativeReview=rel(review));(B/'queue.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(handoff=rel(out),actualSession=1557,actualOuterExit=0,activeOwned=0,wholePixelApproved=False)))
