"""Seal bounded direct pixel review; keep unresolved final approval false."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def verify(records):
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in records)
    return records
now=datetime.now(timezone.utc).isoformat()
pilot=read('scene02-moving-pilot-execution-v1.json')
prep=read('scene02-editorial-annotation-preparation-v3.json')
assert pilot['exitCode']==0 and len(pilot['samples'])==304 and len(pilot['boards'])==51
assert len(prep['samples'])==63 and len(prep['boards'])==11
proof={'reviewedAt':now,'pilot':{
    'execution':'scene02-moving-pilot-execution-v1.json','sessionId':79707,
    'actualOuterExitCode':0,'exitObservedChunk':'ff090c',
    'all304SamplePixelsDirectlyRead':verify(pilot['samples']),
    'all51BoardsDirectlyRead':verify(pilot['boards']),
    'frames':3403,'wholeDecodeBothExitCode':0,'allFramePts1500Verified':True,
    'approved':False,'heldIssues':[
        'Original bottom-center score is obscured by fixed two-line narration captions. Reframe the source; preserve caption position960,970.',
        'Component glyph starts7.98s after the second jump. Reveal it at the existing ground/air caption transition3.35s.',
        'Whole-rider brackets are image-space attention regions, not precise helmet tracking or measured world coordinates. Fast rotation needs actual moving playback review.'],
    'fullContinuousPlaybackApproved':False,'wholeVideoApproved':False},
    'reframedEditorialV3':{'plan':prep['plan'],'planSha256':prep['planSha256'],
        'all63StillPixelsDirectlyRead':verify(prep['samples']),
        'all11BoardsDirectlyRead':verify(prep['boards']),
        'sampledLayoutApprovedForMovingPilot':True,
        'change':'Crop unrelated top180 source pixels; full-width active action900px and bottom180 same-frame blur. Score/speed and original CC remain above captions. Target keys shift by exactly-180y. Header100; component glyph3.35s; red horizontal/green height/blue radius roles retained.',
        'currentCaptionedMovingPixelsApproved':False},
    'v2FirstLaunch':{'actualExitCode':1,'observedChunk':'9de1a2',
        'reason':'Derived worker still referenced the historical execution-v1 filename; protected existence assertion stopped it before state creation or media rendering. Corrected to execution-v2 before the next launch.',
        'baselineOverwrite':False},
    'protectedBaselineUnchanged':all(sha(ROOT/r['path'])==r['sha256'] for r in read('baseline-protected-sha-v1.json')['files']),
    'researchManipulation':False,'newUpload':False,'newSchedule':False,
    'allFinalPixelsApproved':False,'currentMixedAsrApproved':False,'privateDeliveryApproved':False}
p=OUT/'scene02-pilot-held-and-reframe-direct-review-v1.json';assert not p.exists()
p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json'
q=json.loads(qpath.read_text(encoding='utf-8'))
if not any(j['sessionId']==79707 for j in q['execution']['completedJobs']):
    q['execution']['completedJobs'].append({'sessionId':79707,'pid':61756,
        'state':'projects/game-math-polar-3d/revision-teaching-clarity-v1/scene02-moving-pilot-execution-v1.json',
        'actualOuterExitCode':0,'exitObservedChunk':'ff090c','sampledPixelApproval':False})
current=read('scene02-moving-pilot-execution-v2.json')
q['execution'].update(stage='polar-reframed-first-gameplay-moving-pilot-v2',heavyJob={
    'sessionId':84633,'pid':current['pid'],'createTime':current['createTime'],
    'state':'projects/game-math-polar-3d/revision-teaching-clarity-v1/scene02-moving-pilot-execution-v2.json',
    'cpuThreads':2,'gpuJobs':0,'runningExpected':current['status']=='running',
    'next':'Actual exit, all changed caption/transition/fast-flip samples and normal-speed playback; six other gameplay annotations and whole current audio/pair/QA/collect/private/Git/schedule pending'})
q['updatedAt']=now
qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pilotV1SamplesRead':304,'pilotV1Held':True,'v3StillSamplesRead':63,'currentSession':84633,'allFinalApproval':False}),flush=True)
