"""Seal held V3 pixels and prepare only two narrow V4 repairs."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
B=Path(__file__).parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
stamp=datetime.now(timezone.utc).isoformat()
s=read(R/'remaining-action-roles-execution-v3.json')
assert s['exitCode']==0 and s['encodedSampleCount']==83 and s['boardCount']==22
assert not psutil.pid_exists(s['pid'])
proofpath=R/'remaining-action-roles-sampled-direct-review-v3.json'
assert not proofpath.exists()
bound=[]
for p in s['pieces']:
 for row in [dict(path=p['path'],sha256=p['sha256'])]+p['samples']+p['boards']:
  assert sha(ROOT/row['path'])==row['sha256']
  bound.append(dict(path=row['path'],sha256=row['sha256']))
protected=read(R/'narration-first-paragraph-repair-execution-v1.json')['protectedInputs']
assert len(protected)==71
for row in protected:assert sha(ROOT/row['path'])==row['sha256']
save(proofpath,dict(schemaVersion=1,recordedAt=stamp,actualSession=56509,actualCompletion='e4f53b',actualOuterExitCode=0,actualWorkerAbsent=True,encodedSamplesDirectlyRead=83,boardsDirectlyRead=22,shaBoundFiles=bound,
 held=[dict(piece='07b-laser-target',reason='Top-right red label covers blue-X status in encoded509..540. Cyan misses wall status during fast view shift at584/614. Stable2352..2383 contains original blue-to-yellow state change; hide afterward.'),dict(piece='08b-board-removal',reason='First3357..3418 segment follows foreground plank. Second3477..3537 hits below/outside plank or rubble at255/285; hide entire uncertain second segment.299/300 are on plank but do not validate preceding interval.')],
 finalVideoApproved=False,allIntermediateFramesApproved=False,normalSpeedPlaybackApproved=False,continuousListeningApproved=False,allNarrationTimedMovingPixelsApproved=False,localOnly=True))
s.update(actualSession=56509,actualOuterExitCode=0,actualCompletion='e4f53b',actualWorkerAbsent=True,status='completed-two-pieces-held-clearance-and-fast-view',directReview=proofpath.name)
save(R/'remaining-action-roles-execution-v3.json',s)
a=read(R/'remaining-action-annotation-anchors-v2.json')
a.update(preparedAt=stamp,previous='remaining-action-annotation-anchors-v2.json',boundedCorrectionEvidence=proofpath.name)
for tr in a['tracks']:
 if tr['id']=='portal-target-status':
  tr['rangeEndExclusive']=2383
  tr['rule']='Show only stable native2352..2382; preserve blue-X to yellow-check change. Hide after2383 during fast camera motion.'
 if tr['id']=='alyx-board-object':
  tr['segments']=[dict(start=3357,endExclusive=3418)]
  tr['rangeEndExclusive']=3418
  tr['rule']='Identify visible foreground plank only3365..3417; hide afterward through lower-frame exit and uncertain returning view. Actual hand removal remains visible without fabricated tracking.'
ap=R/'remaining-action-annotation-anchors-v3.json';assert not ap.exists();save(ap,a)
src=(B/'render-motion-remaining-action-roles-v3.py').read_text('utf-8')
src=src.replace('remaining-action-roles-v3','remaining-action-roles-v4').replace('remaining-action-roles-execution-v3','remaining-action-roles-execution-v4').replace('remaining-action-roles-current-cim-v3','remaining-action-roles-current-cim-v4').replace('remaining-action-annotation-anchors-v2.json','remaining-action-annotation-anchors-v3.json')
old="d.rectangle((left,133,right,190),fill='white',outline=color,width=3);d.text((left+12,141),label,font=font,fill=color)\n     origin=(left+40,190);d.line([origin,(origin[0]-25,224),tuple(pt)],fill=color,width=5);x,y=pt"
new="top=720 if red and piece['id']=='07b-laser-target' else 133\n     d.rectangle((left,top,right,top+57),fill='white',outline=color,width=3);d.text((left+12,top+8),label,font=font,fill=color)\n     origin=(left+40,top if top==720 else top+57);elbow=(origin[0]-25,top-34 if top==720 else top+91)\n     d.line([origin,elbow,tuple(pt)],fill=color,width=5);x,y=pt"
assert old in src;src=src.replace(old,new).replace('2352,1932,3365','2352,2383,1932,3365')
worker=B/'render-motion-remaining-action-roles-v4.py';assert not worker.exists();worker.write_text(src,'utf-8')
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=stamp,activeOwnedWorkers=0,ownedJob=dict(active=False,status='completed-two-pieces-held',sessionId=56509,exitCode=0,completion='e4f53b'),remainingActionSampledReview=proofpath.name,correctedRoleAnchors=ap.name,stage='two-role-clearance-repair-v4-prepared',next='Run only fresh-resource guarded V4 two-piece repair, then direct encoded review and normal1x. Preserve other six V1 pieces, PCM and all completed sources/QA. Final video remains unapproved.')
save(R/'latest-checkpoint.json',cp)
q=read(B/'queue.json')
for v in q.values():
 if isinstance(v,dict) and str(v.get('currentCheckpoint','')).endswith('revision-cross-game-four-v1/latest-checkpoint.json'):v.update(activeOwnedWorkers=0,remainingActionSampledReview=proofpath.relative_to(ROOT).as_posix())
q.update(status='active',recordedAt=stamp,next=cp['next']);save(B/'queue.json',q)
print(json.dumps(dict(actualV3Exit=0,samples=83,boards=22,heldPieces=2,preparedV4=True,protected71=True)))
