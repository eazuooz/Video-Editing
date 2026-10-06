"""Save current observed v5 review progress without promoting final gates."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = datetime.now(timezone.utc).isoformat()
source_path = BASE / 'word-action-source-candidate-v5.json'
review_path = PROOF / 'moving-source-direct-review-v5.json'
proof_path = PROOF / 'native-guide12-boundary-reassignment-v5.json'
server_path = PROOF / 'browser-word-action-review-server-v1.json'
review = read(review_path)
server = read(server_path)
assert review['sourceCandidateSha256'] == server['sourceCandidateSha256'] == sha(source_path)
assert server['pid'] == 49360 and server['port'] == 9240
resource_path = PROOF / 'resources-source-review-v5.json'
resources = read(resource_path)
process = resources['ownReviewServer'][0]
assert process['ProcessId'] == server['pid']
assert '--source word-action-source-candidate-v5.json' in process['CommandLine']
observed = dict(**server, sessionId=40823, aliveObserved=True,
                cimObservedCreationDate=process['CreationDate'],
                cimObservedParentProcessId=process['ParentProcessId'], aliveObservedAt=resources['observedAt'],
                resourceEvidence=rel(resource_path),resourceEvidenceSha256=sha(resource_path),
                previousOwnServer=dict(pid=10404, sessionId=29080,
                                       commandLine='serve-word-action-review-v1.py --port 9240 --source word-action-source-candidate-v4.json',
                                       creationDate='2026-10-06T21:30:01.536353+09:00',
                                       stoppedAfterIdentityVerification=True, intentionalCtrlC=True,
                                       observedExitCode=1, aliveAfterStop=False),
                heavyCpuJobsStarted=0,gpuJobsStarted=0,renderJobsStarted=0,uploadJobsStarted=0,
                otherGameMathVoiceReviewAndRenderJobsPreserved=True)
progress = dict(path=rel(review_path),sha256=sha(review_path),updatedAt=review['updatedAt'],
                currentSourceCandidateSha256=sha(source_path),expectedCuts=83,
                directlyReviewedCuts=review['directlyReviewedCuts'],
                unchangedCutInheritedReviews=26,
                currentV5DirectReviews=review['directlyReviewedCuts']-26,
                allSourceMotionReviewed=review['allSourceMotionReviewed'],
                allWordActionAligned=review['allWordActionAligned'],
                reassignmentEvidence=rel(proof_path),reassignmentEvidenceSha256=sha(proof_path),
                allFinalCaptionPixelsReviewed=False,finalTimelineAdopted=False,
                humanListeningPronunciation='pending',newGitImages=0,newGitMedia=0)
next_action = ('Resume source-v5/caption-v3 normal-speed word/action review in current port9240/PID49360/session40823. '
               f"Current direct observations {review['directlyReviewedCuts']}/83 include exactly26 complete identical inherited cuts; "
               'eight guide12 source-only reassigned cuts require current direct playback/gallery checks. '
               'Native pink/grey F540/541 and corridor/stair F1238/1239 boundaries are preserved as observed corrections, not approvals. '
               'All selected native frame unions,70 paragraphs,current PCM373.680083333s,253KO/118EN,piece timing,white9140 input and23570 total are unchanged. '
               'Do not rerender/extract completed input trials or redo TTS/ASR. After all current motion checks adopt timing, then single mix/current mixed ASR/clean-captioned pair/all encoded pixels/QA/collection/private/Git. Final gates remain false.')
for path in [BASE/'latest-checkpoint.json', PROOF/'latest-checkpoint.json']:
    cp=read(path)
    cp.update(updatedAt=now,stage='current-source-v5-caption-v3-native-boundary-corrected-normal-speed-review',
              wordActionSourceCandidate=rel(source_path),wordActionSourceCandidateSha256=sha(source_path),
              browserReviewServer=observed,sourceMotionDirectReview=progress,
              nativeGuide12BoundaryReassignment=rel(proof_path),
              allSourceMotionReviewed=False,finalTimingApproved=False,finalTimelineAdopted=False,
              allFinalCaptionPixelsReviewed=False,render=False,qa=False,collected=False,uploaded=False,
              nextAction=next_action)
    path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
queue_path=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
queue=read(queue_path)
item=next(i for i in queue['items'] if i['slug']=='familiar-game-rules')
item.update(stage='current-source-v5-caption-v3-native-boundary-corrected-normal-speed-review',
            wordActionSourceCandidate=rel(source_path),wordActionSourceCandidateSha256=sha(source_path),
            browserReviewServer=observed,sourceMotionDirectReview=progress,
            nativeGuide12BoundaryReassignment=rel(proof_path),
            allSourceMotionReviewed=False,finalTimingApproved=False,finalTimelineAdopted=False,
            allFinalCaptionPixelsReviewed=False,nextAction=next_action)
queue.update(updatedAt=now,lastProgressAt=now,currentSlug='familiar-game-rules')
queue_path.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(currentCuts=83,directlyReviewed=review['directlyReviewedCuts'],serverPid=49360,
                      sessionId=40823,finalApproved=False)))
