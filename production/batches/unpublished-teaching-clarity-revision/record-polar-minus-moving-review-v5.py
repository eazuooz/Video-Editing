"""Seal the directly read two moving glyph repairs; preserve final gates."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
state=read(OUT/'minus-glyph-moving-pilots-execution-v5.json')
assert state['exitCode']==0 and state['status']=='completed'
assert not psutil.pid_exists(state['pid']) or psutil.Process(state['pid']).create_time()!=state['createTime']
now=datetime.now(timezone.utc).isoformat()
notes={
 '11':'All181 samples/31 boards directly read, including changed subtraction stage24.086667–30s and all following stages/cues/native cut. Full sample0076/f1446 clearly shows ASCII subtraction: camera position minus target position. Blue target-to-camera and red camera-to-target are opposite explanatory relation vectors, not measured engine coordinates. The later blue rectangle is explicitly a game-image centre reference and is removed before component decomposition. Horizontal/relative-height model is labelled illustrative. Fixed bottom captions, original credit, rider and numeric UI remain clear. No unresolved glyph/layout defect found in the listed moving samples.',
 '16':'All205 samples/35 boards directly read, including both minus signs16.82–25.94s, every cue/stage/native cut and all later obstruction/control-policy discussion. Full sample0065/f1200 clearly shows placement=camera-centre and look=centre-camera with readable minus glyphs. The blue/red/yellow relation diagram is explicitly explanatory, distinct from measured game-world geometry. Different riding interval is announced at41.12s; no falsely continuous event is implied. Normal riding, turns and jumps remain visible, with brief natural foliage occlusion in source action. Caption boxes, original source credit, speed/score UI and all listed annotation labels remain readable.'}
jobs=[]
for j in state['jobs']:
    assert (len(j['samples']),len(j['boards']))==({'11':(181,31),'16':(205,35)}[j['scene']])
    for r in j['samples']+j['boards']:assert sha(ROOT/r['path'])==r['sha256']
    for key in [f"scene{j['scene']}.annotated.clean",f"scene{j['scene']}.annotated.captioned"]:
        r=j[key];assert sha(ROOT/r['path'])==r['sha256'] and r['wholeDecodeExitCode']==0 and r['allPts1500Verified']
    jobs.append({'scene':j['scene'],'samples':j['samples'],'boards':j['boards'],
      'directReview':notes[j['scene']],'allListedPixelsDirectlyRead':True,
      'boundedMovingPixelsApproved':True,'unresolved':[]})
dest=OUT/'minus-glyph-moving-direct-review-v5.json';assert not dest.exists()
dest.write_text(json.dumps({'reviewedAt':now,'sessionId':62331,'actualOuterExitCode':0,
 'exitObservedChunk':'bab914','cimAbsenceObservedChunk':'59791f',
 'bothMovingPilotsAllListedPixelsDirectlyRead':True,'bothMovingGlyphRepairsApproved':True,
 'samplesDirectlyRead':386,'boardsDirectlyRead':66,'jobs':jobs,
 'narrationCuesGeometryChanged':False,'baselineProtectedUnchanged':state['protectedBaselineUnchanged'],
 'allFinalPixelsApproved':False,'wholeVideoApproved':False,
 'humanListeningApproved':False,'pronunciationApproved':False,'publicRightsApproved':False,
 'mediaGitAdded':0,'imageGitAdded':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qfile=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qfile)
assert not any(j['sessionId']==62331 for j in q['execution']['completedJobs'])
q['execution']['completedJobs'].append({'sessionId':62331,'pid':state['pid'],'createTime':state['createTime'],
 'state':statefile if (statefile:='projects/game-math-polar-3d/revision-teaching-clarity-v1/minus-glyph-moving-pilots-execution-v5.json') else '',
 'actualOuterExitCode':0,'exitObservedChunk':'bab914','allListedOutputsDirectlyRead':True,
 'boundedMovingPixelReviewApproved':True,'wholeVideoApproval':False})
q['execution'].update(stage='polar-seven-reviewed-action-slots-await-guarded-final-pair',heavyJob=None,
 next='Fresh CIM/CPU/GPU resource, one CPU2/GPU0 whole54115f pair with originalAAC copy; then every final cue/cut/Manim/intro/member pixel and technical QA. Do not regenerate approved narration or prior samples.')
q['updatedAt']=now;qfile.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'samples':386,'boards':66,'bothMovingGlyphRepairsApproved':True,'allFinalPixelsApproved':False}))
