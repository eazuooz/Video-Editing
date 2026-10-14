"""Repair the actually observed missing minus glyph; preserve v3 evidence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'production/batches/unpublished-teaching-clarity-revision'
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat()
ex=read(R/'observation-pilot-execution-v3.json')
assert ex['workerExitCode']==ex['wholeDecodeExitCode']==ex['extractionExitCode']==0
assert len(ex['samples'])==25 and len(ex['boards'])==5
assert all(sha(ROOT/x['path'])==x['sha256'] for x in ex['samples']+ex['boards'])
assert all(sha(ROOT/x['path'])==x['sha256'] for x in read(R/'baseline-preservation-v1.json')['protectedFiles'])
review=R/'observation-pilot-direct-review-v3.json';script=B/'render-orientation-observation-pilot-v4.py'
assert not review.exists() and not script.exists()
write(review,dict(observedAt=now,actualSessionId=94586,actualOuterExitCode=0,outerExitObservedChunk='935ec9',
    workerGenerationAbsentObservedChunk='651c0e',all25ListedEncodedSamplesDirectlyRead=True,
    all5BoardsDirectlyRead=True,fullResolutionReadFrames=[105,135,270],allHashesMatched=True,
    baseline38Unchanged=True,authoredTorsoPointsStayOnVisibleTorsoInListedSamples=True,
    observations=['The manually authored point remains on the visible torso/back block in listed samples, including former f90/135/150 segmentation failures.',
        'The math formula has missing U+2212 minus glyphs: f105/135/270 full-resolution pixels show two empty boxes. Correct this before approving the prototype.',
        'The dot and red arrow describe image point displacement, including camera effects; there is no claim of world-space velocity or torso rotation.'],
    prototypeApproved=False,allMovingPixelsApproved=False,sourceAdoptionApproved=False,
    timedNarrationApproved=False,finalCueApproved=False,samples=ex['samples'],boards=ex['boards']))
ex.update(sessionId=94586,actualOuterExitCode=0,outerExitObservedChunk='935ec9',status='completed-point-samples-reviewed-held-for-formula-glyph',directReview=rel(review))
write(R/'observation-pilot-execution-v3.json',ex)
s=(B/'render-orientation-observation-pilot-v3.py').read_text('utf8')
s=s.replace('observation-pilot-v3','observation-pilot-v4').replace('observation-pilot-execution-v3','observation-pilot-execution-v4')
s=s.replace('observation-point-track-v3','observation-point-track-v4')
s=s.replace('Δp = p(t) − p(t − 0.5s)','Δp = p(t) - p(t - 0.5s)')
assert '−' not in s
script.write_text(s,'utf8')
q=read(B/'queue.json');q['execution']['ownedJob']=None
q['execution']['completedOwnedJobs'].append(dict(script=rel(B/'render-orientation-observation-pilot-v3.py'),sessionId=94586,pid=ex['pid'],createTime=ex['createTime'],actualOuterExitCode=0,outerExitObservedChunk='935ec9',directReview=rel(review),approved=False))
q['execution']['stage']='manual-point-pilot-v4-formula-glyph-repair-prepared';q['updatedAt']=now;write(B/'queue.json',q)
print(json.dumps(dict(actualV3Exit=0,pointsListedSampleReview=True,v3Approved=False,v4PreparedOnly=True)))
