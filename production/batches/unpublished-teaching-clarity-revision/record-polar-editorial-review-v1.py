"""Record directly inspected, bounded source/layout evidence; never final approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def write(name,obj):
 p=OUT/name;assert not p.exists();p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verified(records):
 assert all(sha(ROOT/r['path'])==r['sha256'] for r in records)
 return records
now=datetime.now(timezone.utc).isoformat()
v5=read('unused-native-execution-v5.json');assert v5['exitCode']==0
selected=read('selected-scene02-execution-v1.json');assert selected['exitCode']==0
prep1=read('scene02-editorial-annotation-preparation-v1.json')
prep2=read('scene02-editorial-annotation-preparation-v2.json')
write('scene02-selected-source-direct-review-v1.json',{
 'reviewedAt':now,'selectedCandidateSha256':selected['sourceCandidateSha256'],
 'actualOuterExitCode':0,'exitObservedChunk':'5d6a28','sessionId':94349,
 'allSelectedSourceBoardsDirectlyRead':verified(selected['boards']),
 'all63SamplesDirectlyRead':verified(selected['samples']),
 'unselectedV5ExitObservedChunk':'47f46d','unselectedV5SessionId':27299,
 'unselectedV5Samples':verified(v5['records']),'unselectedV5Boards':verified(v5['boards']),
 'selectionReason':'The first interval contains ramp/air/landing immediately, replacing a ground-heavy start. The third contains a second jump/landing at the existing landing paragraph. Later crash and results/menu intervals are excluded.',
 'cuts':selected['cuts'],'frames':3403,'normalSpeed':True,'loop':False,'sourceAudio':False,
 'sameRunClaim':False,'worldCoordinatesRecovered':False,
 'boundedSourceSampleApproval':True,'allContinuousNativeFramesApproved':False,
 'annotationApproval':False,'finalVideoApproval':False,'humanListeningApproved':False,'publicRightsApproved':False})
write('scene02-automatic-track-held-review-v1.json',{
 'reviewedAt':now,'v1':{'execution':'scene02-visible-track-execution-v1.json','sessionId':86587,'actualOuterExitCode':0,'exitObservedChunk':'23aaa9','directReviewScope':'All63 samples/11boards','approved':False,'reason':'Nearest purple HSV component moved from helmet to jersey/bike/wheels during flips. A detector result is not moving pixel approval.'},
 'v2':{'execution':'scene02-visible-track-execution-v2.json','sessionId':36098,'actualOuterExitCode':0,'exitObservedChunk':'1a5edf','directReviewScope':'First18 samples/3boards; remaining8boards not approved/read for this rejection','approved':False,'reason':'Changed HSV threshold still drifted into background and wheels. First attempt missing selected execution-v2 was corrected before state creation; the original error remains history.'},
 'replacementApproach':'Manually keyed whole-rider observation brackets; separate explicitly illustrative component/camera glyphs. Interpolated motion remains unapproved until actual moving pilot review.',
 'baselineChanged':False,'researchManipulation':False})
write('scene02-editorial-layout-direct-review-v2.json',{
 'reviewedAt':now,'historicalV1Boards':verified(prep1['boards']),
 'historicalV1HeldReason':'The headline at y150 overlapped the original player-name UI in later daytime cuts; do not use this version.',
 'selectedPlan':prep2['plan'],'selectedPlanSha256':prep2['planSha256'],
 'selectedBoardsAllDirectlyRead':verified(prep2['boards']),
 'selected63SamplesAllDirectlyRead':verified(prep2['samples']),
 'sampledLayoutApprovedForPilot':True,'headlinesMovedToY240':True,
 'colors':'Original explanation roles retained: red horizontal, green height, blue radius/relative vector; yellow observation bracket.',
 'narrationOrder':[0,7.98,15,22.72,29.08,34.78,42.5],
 'interpretation':'Bracket selects a visible rider region, not an exact helmet/world point. Floating component glyph and camera icon are labelled explanatory diagrams, not game engine measurements.',
 'actualCaptionPixelsApproved':False,'movingTrackApproved':False,'wholeVideoApproved':False})
qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json'
q=json.loads(qpath.read_text(encoding='utf-8'))
jobs=[(27299,71804,'unused-native-execution-v5.json','47f46d'),(94349,55484,'selected-scene02-execution-v1.json','5d6a28'),(86587,73292,'scene02-visible-track-execution-v1.json','23aaa9'),(36098,50188,'scene02-visible-track-execution-v2.json','1a5edf')]
for session,pid,name,chunk in jobs:
 assert read(name)['exitCode']==0
 if not any(j['sessionId']==session for j in q['execution']['completedJobs']):
  q['execution']['completedJobs'].append({'sessionId':session,'pid':pid,'state':f'projects/game-math-polar-3d/revision-teaching-clarity-v1/{name}','actualOuterExitCode':0,'exitObservedChunk':chunk})
pilot=read('scene02-moving-pilot-execution-v1.json')
q['execution'].update(stage='polar-first-gameplay-moving-annotation-pilot',heavyJob={
 'sessionId':79707,'pid':pilot['pid'],'createTime':pilot['createTime'],
 'state':'projects/game-math-polar-3d/revision-teaching-clarity-v1/scene02-moving-pilot-execution-v1.json',
 'cpuThreads':2,'gpuJobs':0,'runningExpected':pilot['status']=='running',
 'next':'Actual exit and moving pilot/caption/cue/fast-flip pixel review; other6gameplay annotations and whole current final ASR/pair/QA/settings/Git/schedule still pending'})
q['updatedAt']=now
qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selectedSourceSamples':63,'layoutSamples':63,'allVideoApproval':False,'currentJobSession':79707}),flush=True)
