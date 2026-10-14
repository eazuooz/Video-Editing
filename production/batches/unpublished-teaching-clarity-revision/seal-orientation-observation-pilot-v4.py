"""Seal only the directly observed silent point-guide scope, not final video QA."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'production/batches/unpublished-teaching-clarity-revision'
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat();ex=read(R/'observation-pilot-execution-v4.json')
assert ex['workerExitCode']==ex['wholeDecodeExitCode']==ex['extractionExitCode']==0
assert len(ex['samples'])==25 and len(ex['boards'])==5
assert all(sha(ROOT/x['path'])==x['sha256'] for x in ex['samples']+ex['boards'])
assert all(sha(ROOT/x['path'])==x['sha256'] for x in read(R/'baseline-preservation-v1.json')['protectedFiles'])
play=read(R/'observation-pilot-normal-playback-v4.json');assert play['actual']['ended'] and play['actual']['rate']==1 and play['actual']['muted']
assert play['actual']['currentTime']==6
p=R/'observation-pilot-direct-review-v4.json';assert not p.exists()
write(p,dict(observedAt=now,actualSessionId=52560,actualOuterExitCode=0,outerExitObservedChunk='6bc423',
    workerGenerationAbsentObservedChunk='6b81f9',all25EncodedSamplesDirectlyRead=True,
    all5BoardsDirectlyRead=True,fullResolutionFormulaFrame105DirectlyRead=True,allHashesMatched=True,
    baseline38Unchanged=True,sourcePixelAnchorsMatched=True,wholeDecodeExitCode=0,
    nativeRange=[50400,50760],sourcePtsRange=[12902400,12994560],
    observations=['25 listed frames put the teal observation ring on the visible torso/back block, without a silhouette bounding box or principal-axis claim.',
        'The red arrow equals image-point(t) minus image-point(t-30frames); the text says camera motion also contributes. Gold denotes fixed image-up.',
        'Both minus signs now render visibly at full resolution; labels and geometry remain above910.',
        'Actual browser playback ran at1x from0 toended6s with muted audio. Start/end pixels and all listed encoded samples were directly inspected; intermediate360frames were not all directly read.'],
    listedSamplePointAndFormulaApproved=True,normalPlaybackExecuted=True,
    normalPlaybackEvidence=rel(R/'observation-pilot-normal-playback-v4.json'),
    allMovingPixelsApproved=False,sourceAdoptionApproved=False,
    timedNarrationApproved=False,finalCueApproved=False,finalTimingApproved=False,
    actualNewVideoId=None,uploaded=False,publicRightsApproved=False,
    samples=ex['samples'],boards=ex['boards']))
ex.update(sessionId=52560,actualOuterExitCode=0,outerExitObservedChunk='6bc423',
    status='completed-point-and-formula-listed-sample-review-normal-playback-done',directReview=rel(p))
write(R/'observation-pilot-execution-v4.json',ex)
cp=read(R/'latest-checkpoint.json');cp.update(observedAt=now,stage='observation-pilot-v4-listed-samples-approved-conservative-recut-playback-pending',
    observationPilot=rel(p),next='Finish actual normal-speed comparisons of the16 conservative source windows. Approve only source planning scope, then measure6 new KO bridges while preserving original24PCM and all final gates pending.')
write(R/'latest-checkpoint.json',cp)
q=read(B/'queue.json');q['execution'].update(stage=cp['stage'],ownedJob=None,next=cp['next'])
q['execution']['completedOwnedJobs'].append(dict(script=rel(B/'render-orientation-observation-pilot-v4.py'),sessionId=52560,pid=ex['pid'],createTime=ex['createTime'],actualOuterExitCode=0,outerExitObservedChunk='6bc423',directReview=rel(p),listedSamplesApproved=True,allFinalPixelsApproved=False))
q['updatedAt']=now;write(B/'queue.json',q)
print(json.dumps(dict(actualExit=0,listedSamplesApproved=25,boardsApproved=5,normalPlaybackExecuted=True,baselinePreserved=38,finalApproved=False)))
