"""Record direct inspection of every five-pilot board, without final approval."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
five=read(OUT/'five-moving-pilots-execution-v1.json')
assert five['status']=='completed' and five['exitCode']==0
notes={
 '05':['All22 boards/128 encoded samples directly read. Formula-component glyphs and source credit/captions remain readable.','Yellow whole-rider bracket misses the upper body during jumps, e.g.f1350 andf2010. Retain narrated component glyph; remove the inaccurate whole-object bracket.'],
 '11':['All31 boards/181 encoded samples directly read. Narration distinguishes observed framing from unrecovered engine coordinates.','Close-camera/fakie framesf510–930 put the rider far from interpolated bracket. Later jumps also exceed its fixed height. Replace ambiguous target-tracking presentation with a labelled explanatory camera/target relation, avoiding claims of recovered positions.'],
 '14':['All22 boards/132 encoded samples directly read. Tracking-policy versus canonical-representation labels match the spoken limitations.','Upper body extends beyond bracket during early backflip and later ramps. Remove inaccurate whole-rider bracket while retaining meaningful camera-policy diagram.'],
 '16':['All35 boards/205 encoded samples directly read, including all cut/cue/stage boundaries. Opposite subtraction arrows/formula match the narrated distinction.','Several jump/turn frames put the rider outside the bracket. At61s the actual tree occludes the rider: useful obstruction evidence, not proof of an internal camera algorithm. Remove false whole-object tracker, retain bounded explanation.'],
 '18':['All17 boards/102 encoded samples directly read. Position/attitude/viewpoint text follows the concluding narration.','The bracket drifts during turns and flips. Add separate simple position/attitude/viewpoint explanatory shapes beside the action; do not infer engine values or claim one coordinate controls every behaviour.']}
jobs=[]
for job in five['jobs']:
    sid=str(job['scene']);assert job['status']=='completed'
    assert len(job['samples'])=={'05':128,'11':181,'14':132,'16':205,'18':102}[sid]
    for row in job['samples']+job['boards']:assert sha(ROOT/row['path'])==row['sha256']
    jobs.append({'scene':sid,'allEncodedSamplesDirectlyRead':job['samples'],
      'allBoardsDirectlyRead':job['boards'],'observations':notes[sid],
      'sampledCaptionAndCreditSpacingClear':True,'annotationRepairRequired':True,
      'movingAnnotationApproved':False,'allContinuousFramesApproved':False})
save(OUT/'five-pilot-direct-review-v1.json',{'reviewedAt':now,'actualOuterExitCode':0,
 'sessionId':42240,'exitObservedChunk':'7db7a3','samplesRead':748,'boardsRead':127,
 'jobs':jobs,'next':'Separate v4 annotation repair; preserve every original pilot and all narration.',
 'currentWholeMixedAsrApproved':False,'wholeVideoApproved':False,'allFinalPixelsApproved':False,
 'humanListeningApproved':False,'publicRightsApproved':False,'newImageGitAdded':0})
eight=read(OUT/'selected-scene08-execution-v2.json');assert eight['status']=='completed' and eight['exitCode']==0
for row in eight['changedRegionSamples']+eight['changedRegionBoards']:assert sha(ROOT/row['path'])==row['sha256']
save(OUT/'scene08-selected-source-direct-review-v2.json',{'reviewedAt':now,
 'actualOuterExitCode':0,'sessionId':69328,'exitObservedChunk':'03c8a8',
 'all25ChangedRegionSamplesDirectlyRead':eight['changedRegionSamples'],
 'all5ChangedRegionBoardsDirectlyRead':eight['changedRegionBoards'],
 'sourceCandidate':eight['sourceCandidate'],'sourceCandidateSha256':eight['sourceCandidateSha256'],
 'allNativePtsVerified':all(c['allNativePtsVerified'] for c in eight['cuts']),
 'observations':['Source375–382.5s ends before the problematic upper crop; final frame2009 visibly retains rider/head.',
  'Source389–395.883333s extends the normal-speed turn by60 native frames, preserving3743 frames total.',
  'The repaired middle boundaries are separate source actions; no continuous race/score/strategy result is claimed.'],
 'sampledSourceClarityApproved':True,'reframedFinalPixelsApproved':False,
 'allContinuousFramesApproved':False,'currentFinalCuePixelsApproved':False,'publicRightsApproved':False})
queuefile=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(queuefile)
for session,pid,create,state,chunk in [(42240,76592,1791626777.0563855,'five-moving-pilots-execution-v1.json','7db7a3'),(69328,59024,1791628237.6603613,'selected-scene08-execution-v2.json','03c8a8')]:
    assert not any(j['sessionId']==session for j in q['execution']['completedJobs'])
    q['execution']['completedJobs'].append({'sessionId':session,'pid':pid,'createTime':create,
      'state':str((OUT/state).relative_to(ROOT)).replace('\\','/'),'actualOuterExitCode':0,
      'exitObservedChunk':chunk,'wholeVideoApproval':False})
asr=read(OUT/'current-whole-audio-asr-execution-v1.json')
q['execution'].update(stage='polar-current-whole-aac-asr-running-v4-annotation-repair-preparation',
 heavyJob={'sessionId':15271,'pid':asr['pid'],'createTime':asr['createTime'],
  'state':str((OUT/'current-whole-audio-asr-execution-v1.json').relative_to(ROOT)).replace('\\','/'),
  'cpuThreads':2,'gpuJobs':0,'runningExpected':asr['exitCode'] is None,
  'next':'Actual exit/full19 chapters+19 independent contexts direct comparison; six v4 annotation repairs.'},
 next='Prepare v4 annotation fixes without changing PCM. Review all repaired moving cues, preserve whole original AAC in final pair, then full QA/collection/private/Git/schedule.')
q['updatedAt']=now;save(queuefile,q)
print(json.dumps({'fiveSamples':748,'fiveBoards':127,'scene08ChangedSamples':25,'scene08ChangedBoards':5,'wholeVideoApproval':False,'asrSession':15271}))
