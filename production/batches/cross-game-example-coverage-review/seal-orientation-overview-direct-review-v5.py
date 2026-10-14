"""Bind directly read detailed subjects and actual normal playback endpoints."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=O/'current34-overview-render-execution-v5.json'
out=O/'current34-overview-direct-review-v5.json'
assert not out.exists()
state=rd(sp)
assert state['actualOuterExitCode']==0 and state['actualExitObserved'] and state['workerDead']
proof=rd(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
starts={'01':.1709,'01b':.17517,'24':.160822}
ends={'01':20.75,'01b':6.0,'24':21.95}
observations={
 '01':'Two wing-suit people have helmets/visors, harnesses, articulated limbs, gloves and boots; same forward direction with distinct body tilt. Axis reveal, inverse return and input/calculation/output follow retained narration. Edge-on pose naturally narrows the silhouette. Labels remain above the reserved fixed-caption region.',
 '01b':'Four original conceptual illustrations connect the named game examples: wing-suit person, rider and bicycle with rims/spokes/frame/crank/seat/handlebar, aircraft with canopy/wings/tail/engine intakes, and machinery with dock/vents/bolts/connector/antenna. Projected depth and ordered motion are visible. These are illustrative subjects, not copies or measurements of game internals.',
 '24':'Detailed wing-suit person, three matrix columns and R-transposeR=I/detR=+1 reveal in retained narration order. Rotation motivates the next lesson; lower annotation remains above the reserved caption region in inspected samples.'}
rows=[]
for s in state['scenes']:
 assert sha(ROOT/s['output'])==s['outputSha256']
 assert s['renderExitCode']==s['wholeDecodeExitCode']==s['extractExitCode']==0
 for x in s['samples']+s['boards']:assert sha(ROOT/x['path'])==x['sha256']
 rows.append(dict(scene=s['id'],video=s['output'],videoSha256=s['outputSha256'],samples=s['samples'],boards=s['boards'],allSamplesDirectlyRead=True,
  fullResolutionRepresentativeRead=True,fullResolutionLowerNoteAlsoRead=False,observation=observations[s['id']],
  normalPlayback=dict(tabId='109',url='http://127.0.0.1:9250/orientation-current34-overview-v5-review.html',startTime=starts[s['id']],endTime=ends[s['id']],duration=ends[s['id']],rate=1,muted=True,runningAtStart=True,endedAtEnd=True,scope='Actual normal UI start/end and all selected moving samples; not every intervening frame or continuous listening.')))
assert sum(len(x['samples']) for x in rows)==110 and sum(len(x['boards']) for x in rows)==20
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),executionSha256=sha(sp),actualSession=65738,actualOuterExitCode=0,actualCompletion='b7972f',actualClosure='1d4da6',rows=rows,all110SamplesDirectlyRead=True,all20BoardsDirectlyRead=True,normalPlaybackReviewed=True,recognizableDetailedSubjectsReviewed=True,captionReservedAreaClear=True,projectedFacesAndNarrationOrderedMotionSampled=True,allIntermediateFramesReviewed=False,final244CaptionPixelsApproved=False,humanContinuousListeningApproved=False,currentMixedNarrationReview='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/current34-mixed-complete-direct-review-v1.json',all79ProtectedUnchanged=True,repairCandidateUnchanged=True,newImageGit=0,newTts=0),ensure_ascii=False,indent=2)+'\n','utf-8')
transition=rd(O/'detailed-subject-visual-transition-v1.json')
transition.update(overviewV5MovingReviewPassed=True,overviewDirectReview=out.relative_to(ROOT).as_posix(),overviewDirectReviewSha256=sha(out),renderPreparedOnly=False,renderStarted=True,actualDetailedRenderSession=64072,finalAssemblyMayUseOlderSubjectVisuals=False,all17DetailedExplanationsApproved=False)
(O/'detailed-subject-visual-transition-v1.json').write_text(json.dumps(transition,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(scenes=3,samples=110,boards=20,normalEndpoints=True,detailedSubjects=True,finalCaptionPixels=False)))
