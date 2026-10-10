"""Record bounded still-layout review; hold scene08's cropped jump endpoint."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
now=datetime.now(timezone.utc).isoformat()
prep=read('remaining-editorial-annotation-preparation-v3.json')
rows=[]
for job in prep['jobs']:
    assert sha(ROOT/job['plan'])==job['planSha256']
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in job['samples']+job['boards'])
    rows.append({'scene':job['scene'],'plan':job['plan'],'planSha256':job['planSha256'],
      'samplesDirectlyRead':job['samples'],'boardsDirectlyRead':job['boards'],
      'boundedStillLayoutApproved':job['scene']!='08','movingPixelsApproved':False})
assert sum(len(j['samplesDirectlyRead']) for j in rows)==143
assert sum(len(j['boardsDirectlyRead']) for j in rows)==26
assert all(sha(ROOT/r['path'])==r['sha256'] for r in read('baseline-protected-sha-v1.json')['files'])
proof={'reviewedAt':now,'jobs':rows,'fiveUnchangedSourceSceneLayoutsApproved':True,
  'scene08ReframeApproved':False,
  'scene08Hold':{'frame':2069,'sourceNativeFrame':23009,
    'finding':'Jump-end helmet extends above the180px crop; attention bracket also stays too low at this endpoint.',
    'repairPlan':'Shorten raw375–383.5 to375–382.5; extend raw389–394.883333 to389–395.883333. Preserve3743frames and re-key the moved source cut after inspecting its exact pixels.',
    'repairExecuted':False},
  'notes':[
    'All26 boards and143 selected stills were directly read. Scene08 credit-clear v3 retains a source-crop defect and is held.',
    'Scene05 horizontal projection/height triangle is illustrative, explicitly separated from terrain clearance.',
    'Scenes11/16 distinguish camera placement from the opposite look vector; original source credits remain clear below the labels.',
    'Scene14 separates canonical representation from camera smoothing; footage is not an engine pole-singularity experiment.',
    'Scene18 separates position, attitude and view; colored lines explain roles rather than recovered game coordinates.',
    'Attention brackets use manually inspected screen regions. They are not precise helmet tracking or world measurements.',
    'Original fixed boxed captions require encoded cue/cut review. These stills do not approve moving or final pixels.'],
  'protectedBaselineUnchanged':True,'allMovingPixelsApproved':False,'allFinalPixelsApproved':False,
  'currentWholeMixedAsrApproved':False,'wholeVideoApproved':False,'humanListeningApproved':False,
  'publicRightsApproved':False,'newUpload':False,'gitDelivered':False}
p=OUT/'remaining-annotation-sampled-review-v1.json';assert not p.exists()
p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json'
q=json.loads(qpath.read_text(encoding='utf-8'));e=q['execution']
assert e['heavyJob']['sessionId']==20597
s=read('selected-scene08-execution-v1.json');assert s['status']=='completed' and s['exitCode']==0
assert s['pid']==73324
assert not any(j['sessionId']==20597 for j in e['completedJobs'])
e['completedJobs'].append({'sessionId':20597,'pid':s['pid'],'createTime':s['createTime'],
  'state':'projects/game-math-polar-3d/revision-teaching-clarity-v1/selected-scene08-execution-v1.json',
  'actualOuterExitCode':0,'exitObservedChunk':'fa31e0','sourceSamplesRead':69,'boardsRead':12,
  'reframedPixelsApproved':False})
e.update(stage='polar-five-still-layouts-reviewed-scene08-held',heavyJob=None,
  next='Render five unchanged-source annotated pilots. Repair only scene08 source endpoint, then current whole audio/pair/QA/collect/private/Git/schedule.')
q['updatedAt']=now;qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'stillsRead':143,'boardsRead':26,'fiveLayoutsApproved':True,'scene08Held':True,'baselineUnchanged':True}),flush=True)
