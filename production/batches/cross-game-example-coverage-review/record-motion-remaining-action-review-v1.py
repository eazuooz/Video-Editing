"""Seal the directly read eight-piece samples with two explicit held tracks."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
B=ROOT/'production/batches/cross-game-example-coverage-review'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
sp=R/'remaining-action-roles-execution-v1.json';s=read(sp)
assert s['exitCode']==0 and s['encodedSampleCount']==159 and s['boardCount']==44
assert not psutil.pid_exists(s['pid'])
proofpath=R/'remaining-action-roles-sampled-direct-review-v1.json';assert not proofpath.exists()
bound=[]
for p in s['pieces']:
 for row in [dict(path=p['path'],sha256=p['sha256'])]+p['samples']+p['boards']:
  assert sha(ROOT/row['path'])==row['sha256'],row['path']
  bound.append(dict(path=row['path'],sha256=row['sha256']))
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']
assert len(protected)==71
for row in protected:assert sha(ROOT/row['path'])==row['sha256']
held=[dict(piece='07b-laser-target',track='portal-target-status',reason='Cyan line points at floor instead of wall connection/status display in encoded509..660. Red cube bounded samples are aligned. Correct target anchors before adoption.'),dict(piece='08b-board-removal',track='alyx-board-object',reason='Red point hits background door/window at encoded129..181 and299..300;239..241 on plank. Sparse wrong anchors interpolate across changing view. Correct foreground plank anchor or hide uncertain intervals before adoption.')]
proof=dict(schemaVersion=1,recordedAt=stamp,actualSession=44852,actualCompletion='42a366',actualOuterExitCode=0,actualWorkerAbsent=True,encodedSamplesDirectlyRead=159,boardsDirectlyRead=44,
 shaBoundFiles=bound,held=held,otherSixPiecesSampledRolesAndCaptionClearance=True,
 observations=['Prerequisite cube red bracket aligned in bounded1312..1390 samples.','Button original blue/yellow state preserved; no added misleading target track.','Room and locker observations have no fabricated object trajectory.','Device cyan touches left receiver edge in bounded samples; no world-centroid claim.','Alyx destination hidden at uncertainty and black transition; arrival-wall cyan remains separate.'],
 normalSpeedPlaybackApproved=False,allIntermediateFramesApproved=False,continuousListeningApproved=False,allNarrationTimedMovingPixelsApproved=False,finalCaptionsBurned=False,finalVideoApproved=False,localOnly=True)
proofpath.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
s.update(actualOuterExitCode=0,actualSession=44852,actualCompletion='42a366',actualWorkerAbsent=True,directReview=proofpath.name,status='completed-two-tracks-held-for-narrow-repair')
sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n','utf-8')
next_step='Preserve actual44852 completed8pieces/159samples44boards. Two tracks held: laser cyan floor instead of wall status; Alyx red background instead of foreground board. Narrowly correct only these anchors/pieces, directly review new encoded pixels and normal1x. Other six pieces/source/TTS/ASR/prototypes are not rerendered. Then current17mix/captions/chapters/end/currentmixedASR/allfinalpixels/4files/private/settings/Git/actual09replacement. Pause after normal-transform-UV; no Sakurai6.'
cp_path=R/'latest-checkpoint.json';cp=read(cp_path);cp.update(recordedAt=stamp,activeOwnedWorkers=0,ownedJob=dict(active=False,status='completed-two-tracks-held',sessionId=44852,exitCode=0,completion='42a366'),remainingActionSampledReview=proofpath.name,stage='remaining-action-samples-read-two-tracks-held',next=next_step);cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
qp=B/'queue.json';q=read(qp)
matches=[v for v in q.values() if isinstance(v,dict) and v.get('currentCheckpoint','').endswith('revision-cross-game-four-v1/latest-checkpoint.json')];assert len(matches)==1
matches[0].update(activeOwnedWorkers=0,remainingActionSampledReview=proofpath.relative_to(ROOT).as_posix())
q.update(status='active',recordedAt=stamp,next=next_step);qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(actualExit=0,samples=159,boards=44,shaBoundFiles=len(bound),heldTracks=2,activeOwnedWorkers=0)))
