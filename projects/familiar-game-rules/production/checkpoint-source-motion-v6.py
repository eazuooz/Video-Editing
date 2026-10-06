"""Persist observed source review; preparation/input evidence never approves final output."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat()
source_path=BASE/'word-action-source-candidate-v6.json'
review_path=PROOF/'moving-source-direct-review-v6.json'
proof_path=PROOF/'native-guide13-aim-reassignment-v6.json'
resource_path=PROOF/'resources-source-review-v6.json'
review,server,resources=read(review_path),read(PROOF/'browser-word-action-review-server-v1.json'),read(resource_path)
assert review['sourceCandidateSha256']==server['sourceCandidateSha256']==sha(source_path)
assert review['expectedCuts']==85
process=resources['ownReviewServer'][0]
assert process['ProcessId']==server['pid']==59504
assert '--source word-action-source-candidate-v6.json' in process['CommandLine']
changed=[r for r in review['cuts'] if r['cutId'].startswith('13-cut02-v6-')]
assert len(changed)==3 and all(r['decision']=='aligned' for r in changed)
observed=dict(**server,sessionId=26775,aliveObserved=True,aliveObservedAt=resources['observedAt'],
              cimObservedCreationDate=process['CreationDate'],cimObservedParentProcessId=process['ParentProcessId'],
              resourceEvidence=rel(resource_path),resourceEvidenceSha256=sha(resource_path),
              previousOwnServer=dict(pid=49360,sessionId=40823,
                commandLine='serve-word-action-review-v1.py --port9240 --source word-action-source-candidate-v5.json',
                creationDate='2026-10-06T22:32:33.777779+09:00',
                identityEvidence=rel(PROOF/'resources-before-source-review-v6.json'),
                stoppedAfterIdentityVerification=True,intentionalCtrlC=True,observedExitCode=1,aliveAfterStop=False),
              heavyCpuJobsStarted=0,gpuJobsStarted=0,renderJobsStarted=0,uploadJobsStarted=0,
              foreignTrainingVoiceReviewAndRenderJobsPreserved=True)
progress=dict(path=rel(review_path),sha256=sha(review_path),updatedAt=review['updatedAt'],
              currentSourceCandidateSha256=sha(source_path),expectedCuts=85,
              directlyReviewedCuts=review['directlyReviewedCuts'],unchangedCutInheritedReviews=47,
              currentV6DirectReviews=review['directlyReviewedCuts']-47,
              allSourceMotionReviewed=review['allSourceMotionReviewed'],allWordActionAligned=review['allWordActionAligned'],
              guide13ChangedCutsDirectlyAligned=True,newNativeFrames=89,newNativeEncodedInputPixelsPending=True,
              reassignmentEvidence=rel(proof_path),reassignmentEvidenceSha256=sha(proof_path),
              allFinalCaptionPixelsReviewed=False,finalTimelineAdopted=False,
              humanListeningPronunciation='pending',newGitImages=0,newGitMedia=0)
next_action=(f"Resume85cut source-v6/caption-v3 normal-speed review; actual{review['directlyReviewedCuts']}/85includes47whole-identical inherited aligned cuts. "
             'Guide12 all8v5changed cuts and guide13 all3v6changed cuts directly read/aligned; v5guide13-floating-debris mismatch remains preserved. '
             'v6addsF1591-1680exact89unique frames and removesF690-753/F790-816exact89, no other cut/PCM/caption/timing changes. '
             'New89native frames require current encoded input/final pixel checks; do not reuse old input approval for them. '
             'Ownlight UI port9240/PID59504/session26775; no heavy render/GPU/upload running. '
             'Preserve70paragraphs PCM373.680083333s/253KO118EN/white9140/actual13710/total23570 and completed input media. '
             'After all source-word checks resolve current mismatches, adopt timing then single mix/current mixed ASR/clean-captioned pair/all final pixels/QA/collection/private/Git. Final gates remain false.')
for path in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    cp=read(path)
    cp.update(updatedAt=now,stage='current-source-v6-caption-v3-guide13-aim-corrected-normal-speed-review',
      wordActionSourceCandidate=rel(source_path),wordActionSourceCandidateSha256=sha(source_path),
      browserReviewServer=observed,sourceMotionDirectReview=progress,nativeGuide13AimReassignment=rel(proof_path),
      allSourceMotionReviewed=False,finalTimingApproved=False,finalTimelineAdopted=False,
      allFinalCaptionPixelsReviewed=False,render=False,qa=False,collected=False,uploaded=False,nextAction=next_action)
    path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
queue=read(qpath)
item=next(i for i in queue['items'] if i['slug']=='familiar-game-rules')
item.update(stage='current-source-v6-caption-v3-guide13-aim-corrected-normal-speed-review',
  wordActionSourceCandidate=rel(source_path),wordActionSourceCandidateSha256=sha(source_path),
  browserReviewServer=observed,sourceMotionDirectReview=progress,nativeGuide13AimReassignment=rel(proof_path),
  allSourceMotionReviewed=False,finalTimingApproved=False,finalTimelineAdopted=False,
  allFinalCaptionPixelsReviewed=False,nextAction=next_action)
queue.update(updatedAt=now,lastProgressAt=now,currentSlug='familiar-game-rules')
qpath.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(reviewed=review['directlyReviewedCuts'],expected=85,serverPid=59504,sessionId=26775,finalApproved=False)))
