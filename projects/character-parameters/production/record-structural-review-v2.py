"""Seal actual prototype observations while retaining unresolved transitions."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+'.review.writing'); t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8'); os.replace(t,p)
qa=read(BASE/'black-structural-qa-v2.json')
assert len(qa['samples'])==32 and len(qa['boards'])==6
for row in qa['samples']+qa['boards']: assert sha(ROOT/row['path'])==row['sha256']
assert sha(ROOT/qa['videoPath'])==qa['videoSha256']
review=dict(reviewedAt=now(),scope='All 32 exact-PTS prototype samples/six boards; not measured narration or final cues.',videoPath=qa['videoPath'],videoSha256=qa['videoSha256'],allBoardsDirectlyRead=True,boards=qa['boards'],samples=qa['samples'],projectedFacesDepthOcclusionAndMotionObserved=True,captionReserveCounts=[x['captionReservePixelsAboveThreshold'] for x in qa['samples']],resolvedScenes={
 '05-useful-strength':'Raised-platform label remains clear of the token throughout the sampled flight and landing.',
 '06-role-and-limitation':'Two red enemies appear above/alongside the projected corridor walls in p4; return route and hypothetical framing remain visible.',
 '07-state-not-base':'Fixed criterion, changing state and play judgment remain distinct; elevated comparison label clears the orange token.',
 '11-cost-and-summary':'Condition/test-path summary stays above the moving tokens; projected nodes and paths remain legible.'},unresolvedIssues=[dict(scene='09-condition-and-time',frame=2430,observation='The outgoing current-effect label and incoming separate-STRIKE label overlap during their opacity crossfade.',repair='Fade out the former completely before fading in the latter, preserving their common clear position.')],prototypeStructuralPixelReviewApproved=False,continuousWholeAnimationReviewed=False,finalCuePixelsApproved=False,timingMeasured=False,localOnly=True,imagesGitAdded=0)
save(BASE/'black-structural-direct-review-v2.json',review)
execution=read(BASE/'black-structural-qa-execution-v2.json');execution.update(actualOuterExitObserved=True,actualOuterExitCode=0,sessionId=None,outerExecution='exec_command completed directly with exit_code 0')
save(BASE/'black-structural-qa-execution-v2.json',execution)
render=read(BASE/'black-structural-render-execution-v2.json');render.update(status='completed-output-probed-and-decoded',completionObservedAt=now(),frames=3601,seconds=60.016667,decodeExitCode=0,extractionExitCode=0,actualFfmpegExitObserved=False,actualFfmpegExitCode=None)
save(BASE/'black-structural-render-completion-v2.json',render)
source=ROOT/'motion-canvas/src/projects/character-parameters/spatial-character-explanation.tsx'
assert sha(BASE/'spatial-character-explanation-preserved-v2.tsx')==read(BASE/'prepared-structural-targeted-v2.json')['sourceSha256']
save(BASE/'prepared-structural-targeted-v3.json',dict(preparedAt=now(),historicalReview=rel(BASE/'black-structural-direct-review-v2.json'),targetScenes=['09-condition-and-time'],source=rel(source),sourceSha256=sha(source),preservedSource=rel(BASE/'spatial-character-explanation-preserved-v2.tsx'),scope='Only the remaining label transition, silent 12-second structural prototype.',scopedTypecheckExitCode=0,renderStartedThroughCua=True,finalMediaApproved=False))
for row in read(BASE/'narration-tts-request-v1.json')['protectedInputs']:assert sha(ROOT/row['path'])==row['sha256']
print('All six v2 boards directly read and hashes sealed; one remaining label crossfade held for v3. Protected narration inputs unchanged.')
