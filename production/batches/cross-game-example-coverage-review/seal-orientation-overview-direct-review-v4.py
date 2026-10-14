"""Seal110 directly inspected overview samples and normal1x endpoint observations."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=O/'current34-overview-render-execution-v4.json';out=O/'current34-overview-direct-review-v4.json'
assert not out.exists();state=read(sp)
assert state['actualOuterExitCode']==0 and state['actualExitObserved'] and state['workerDead']
proof=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
rows=[]
starts={'01':.192251,'01b':.178977,'24':.164864}
ends={'01':20.75,'01b':6.0,'24':21.95}
observations={
    '01':'Projected top/front/side faces show the same forward direction with distinct tilt, then three colored axes, inverse return and input/calculation/output connection. Labels and legend sit above the reserved bottom caption area.',
    '01b':'Four distinct games are named in the actual order. Flight, bicycle, aircraft and placed block have projected faces and separate motion. The common frame question and bottom explanatory note are readable above the fixed-caption region.',
    '24':'Tilt comparison, three matrix columns and R-transposeR=I/detR=+1 reveal in retained narration order; later rotation motivates the next lesson. Lower note remains above the reserved bottom region.'}
for s in state['scenes']:
    assert sha(ROOT/s['output'])==s['outputSha256']
    assert s['renderExitCode']==s['wholeDecodeExitCode']==s['extractExitCode']==0
    for x in s['samples']+s['boards']:assert sha(ROOT/x['path'])==x['sha256']
    rows.append(dict(scene=s['id'],video=s['output'],videoSha256=s['outputSha256'],
        samples=s['samples'],boards=s['boards'],allSamplesDirectlyRead=True,
        fullResolutionLowerNoteAlsoRead=True,observation=observations[s['id']],
        normalPlayback=dict(tabId='106',url='http://127.0.0.1:9250/orientation-current34-overview-v4-review.html',
            startTime=starts[s['id']],endTime=ends[s['id']],duration=ends[s['id']],rate=1,muted=True,
            runningAtStart=True,endedAtEnd=True,scope='Actual UI start/end plus sampled moving pixels; not every intervening frame or continuous listening.')))
assert sum(len(x['samples']) for x in rows)==110 and sum(len(x['boards']) for x in rows)==20
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),executionSha256=sha(sp),
    actualSession=63635,actualOuterExitCode=0,actualCompletion='447494',actualClosure='f32686',rows=rows,
    all110SamplesDirectlyRead=True,all20BoardsDirectlyRead=True,normalPlaybackReviewed=True,
    captionReservedAreaClear=True,projectedFacesAndNarrationOrderedMotionSampled=True,
    allIntermediateFramesReviewed=False,final244CaptionPixelsApproved=False,
    humanContinuousListeningApproved=False,currentMixedNarrationReview='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/current34-mixed-complete-direct-review-v1.json',
    all79ProtectedUnchanged=True,repairCandidateUnchanged=True,newImageGit=0,newTts=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(scenes=3,samples=110,boards=20,normalEndpoints=True,finalCaptionPixels=False)))
