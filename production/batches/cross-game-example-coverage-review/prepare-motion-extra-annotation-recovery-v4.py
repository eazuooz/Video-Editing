"""Seal the actual held V3, then prepare only the changed PowerWash role anchors."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent; R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
e=read(R/'extra-annotation-pieces-execution-v3.json')
try:
 p=psutil.Process(e['pid']); assert abs(p.create_time()-e['createTime'])>=.01
except psutil.NoSuchProcess:pass
assert e['exitCode']==0 and len(e['pieces'])==1 and e['encodedSampleCount']==53 and e['boardCount']==14
checked={}
for p in e['pieces']:
 assert all(p[k]==0 for k in ['decodeExitCode','encodeExitCode','wholeDecodeExitCode','extractionExitCode'])
 for x in [p]+p['samples']+p['boards']:
  assert sha(ROOT/x['path'])==x['sha256']; checked[x['path']]=x['sha256']
e.update(actualOuterSession=96628,actualOuterExitCode=0,actualOuterCompletion='3d276a',originalWorkerAlive=False)
(R/'extra-annotation-pieces-execution-v3.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n','utf-8')
proof=dict(schemaVersion=1,reviewedAt=stamp,actualSession=96628,actualCompletion='3d276a',actualExitCode=0,actualPieceCount=1,
 directlyReadEncodedSamples=53,directlyReadBoards=14,sha256RecheckedFiles=checked,
 findings='All53 encoded samples read. V3 still held: red leader points below the visible tool onto ground at435–585 and at390/405 near the lower edge. Later750/765 points differ from nozzle onto barrel. Cyan contextual hut and HUD/caption preview generally remain visible. Do not adopt these inconsistent tool-tip points.',
 sampledRoleApproval=False,allIntermediateFramesRead=False,normalPlaybackApproved=False,narrationTimed=False,finalCueApproval=False,localOnly=True)
assert not (R/'extra-annotation-pieces-sampled-direct-review-v3.json').exists()
(R/'extra-annotation-pieces-sampled-direct-review-v3.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
plan=read(R/'extra-annotation-observation-plan-v2.json')
plan.update(schemaVersion=3,preparedAt=stamp,previous='extra-annotation-observation-plan-v2.json',repairEvidence='extra-annotation-pieces-sampled-direct-review-v3.json',
 pointPrecision='Manual visible broad decorated tool-body region from V3 images, distinct from nozzle tip or physical centroid. Contact-sheet coordinates explicitly subtract the40pixel header and column/row offset before1920x1080 inversion. Requires new encoded review.',
 semanticChange='Label identifies tool body, not exact nozzle tip. Do not infer world position, movement magnitude or comfort.')
pw=[x for x in plan['observations'] if x['sourceId']=='powerwash-independent-nozzle-aim']; assert len(pw)==53
half_points=[[650,410],[660,410],[660,410],[670,410],[650,410],[650,410],[665,410],[665,410],[650,410],[650,410],[630,420],[635,420],[635,420],[635,420],[635,420],[635,420],[635,420],[635,420],[635,425],[635,425],[635,425],[635,425],[635,425],[635,425],[670,425],[680,425],[695,425],[695,425],[680,425],[685,420],[685,420],[685,420],[685,420],[685,420],[675,420],[675,420],[675,420],[675,420],[675,420],[675,420],[675,420],[675,420],[675,420],[675,420],[675,420],[675,420],[685,420],[685,420],[660,420],[660,420],[660,420],[660,420],[660,420]]
for row,(x,y) in zip(pw,half_points):
 # x/y above are local960wide image coordinates with the40pixel board header.
 full=[2*x,2*(y-40)]
 row['redObservedSamplePoint']=[round((full[0]-160)/1.25),round(full[1]/1.25)]
 row['redLabel']='조작 대상: 도구 몸통'
(R/'extra-annotation-observation-plan-v3.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
src=(B/'render-motion-extra-annotation-pieces-v3.py').read_text('utf-8')
src=src.replace('extra-annotation-pieces-v3','extra-annotation-pieces-v4').replace('extra-annotation-pieces-execution-v3','extra-annotation-pieces-execution-v4').replace('extra-annotation-pieces-current-cim-v3','extra-annotation-pieces-current-cim-v4').replace('render-motion-extra-annotation-pieces-v3.py','render-motion-extra-annotation-pieces-v4.py')
src=src.replace("plan=read(R/'extra-annotation-observation-plan-v2.json')","plan=read(R/'extra-annotation-observation-plan-v3.json')")
src=src.replace('all84 encoded anchors/21boards','all53 encoded anchors/14boards').replace('dict(pieces=2,frames=','dict(pieces=len(state[\'pieces\']),frames=')
assert not (B/'render-motion-extra-annotation-pieces-v4.py').exists()
(B/'render-motion-extra-annotation-pieces-v4.py').write_text(src,'utf-8')
cp_path=R/'latest-checkpoint.json';cp=read(cp_path)
cp.update(ownedJob=dict(active=False,status='completed-held-powerwash-v3',sessionId=96628,exitCode=0,completion='3d276a'),activeOwnedWorkers=0,extraAnnotationSampledReview='extra-annotation-pieces-sampled-direct-review-v3.json',
 next='Retain Portal V2. Only PowerWash V4 prepared: broad visible tool-body anchor and explicit board-header conversion. Run after fresh resource verification; review53 new encoded samples14boards then normal1x. Finalratio/mix/private/schedule false.')
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(samples=53,boards=14,hashes=len(checked),heldV3=True,powerwashOnlyV4Prepared=True)))
