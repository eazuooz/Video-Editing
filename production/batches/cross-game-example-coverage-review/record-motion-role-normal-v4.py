"""Record actual eight CUA normal-speed start/end observations, bounded only."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
plan=read(R/'remaining-action-normal-playback-plan-v4.json')
starts=[.246577,.272591,.264060,.268273,.266716,.263103,.274746,.263991]
ends=[23.183333,12,15.8,4,3.966667,2.983333,14.983333,5]
rows=[]
for i,p in enumerate(plan['items']):
 assert sha(ROOT/p['path'])==p['sha256']
 assert abs(ends[i]-p['frames']/60)<.000001
 rows.append(dict(p,start=dict(time=starts[i],paused=False,ended=False,rate=1,muted=True),end=dict(time=ends[i],duration=ends[i],paused=True,ended=True,rate=1,muted=True),actualUiTab=96))
out=R/'remaining-action-normal-playback-observation-v4.json';assert not out.exists()
stamp=datetime.now(timezone.utc).isoformat()
save(out,dict(schemaVersion=1,observedAt=stamp,items=rows,allEightNormalSpeedStartEndsObserved=True,
 boardFirstAttempt=dict(start=.267777,nearEnd=14.612981,duration=14.983333,ended=False,reason='Changed selected clip before ended observation; repeated this one unfinished observation and then saw actual ended14.983333.'),
 observations=['Portal cube remains a distinct red manipulation target; ray/status and button-result shots remain different native intervals.',
 'Laser status mark disappears before uncertain fast view change; original HUD/status and final caption region are clear in reviewed samples.',
 'Alyx destination transition hides its mark; board mark disappears after first certain plank interval. Subsequent hands/action remain unmarked; no fictitious world-path interpolation.',
 'Room/device and locker observations preserve original camera movement; credit/HUD remain visible.'],
 sampledEvidence=['remaining-action-roles-sampled-direct-review-v1.json','remaining-action-roles-sampled-direct-review-v4.json'],
 approvalScope='Encoded samples and normal1x silent playback start/end only',allIntermediateFramesApproved=False,continuousListeningApproved=False,currentMixedAudioApproved=False,finalNarrationTimedCueApproved=False,finalVideoApproved=False,localOnly=True))
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=stamp,stage='eight-normal-role-windows-reviewed-current17-mix-pending',remainingActionNormalPlayback=out.name,activeOwnedWorkers=0,currentDuplicateCheckPassed=False,next='Read five changed lighting04-3 inputs and actual Studio, refresh strict duplicate check; then fresh resources and single current17 mix. No new TTS/source/render duplication.')
save(R/'latest-checkpoint.json',cp)
qpath=ROOT/'production/batches/cross-game-example-coverage-review/queue.json';raw=qpath.read_text('utf-8-sig');q=json.loads(raw)
q.update(recordedAt=stamp,next=cp['next'])
for v in q.values():
 if isinstance(v,dict) and str(v.get('currentCheckpoint','')).endswith('revision-cross-game-four-v1/latest-checkpoint.json'):v.update(activeOwnedWorkers=0,remainingActionNormalPlayback=out.relative_to(ROOT).as_posix())
assert qpath.read_text('utf-8-sig')==raw;save(qpath,q)
print(json.dumps(dict(eightNormalStartEnds=True,finalVideoApproved=False,newRender=0)))
