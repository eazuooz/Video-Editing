"""Record observed replacement-board review and reuse exact identical pixels."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
W=P/'revision-balatro60-v2/final-v4';OLD=P/'revision-balatro60-v2/final-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--record-changed',action='store_true');a=ap.parse_args()
ex=read(W/'encoded-caption-qa-execution.json');assert ex['exitCode']==0 and (ex['newExtractedSamples'],ex['newBoards'])==(66,12)
try:assert abs(psutil.Process(ex['pid']).create_time()-ex['createTime'])>.01,'Worker still running'
except psutil.NoSuchProcess:pass
if a.record_changed:
 assert not (W/'corrected-cut-encoded-direct-review.json').exists()
 ex.update(actualOuterExitCode=0,outerExitCode=0,outerExitDirectlyObserved=True,actualExitObservedAt=now(),
  actualToolSessionId=None,actualToolChunkId='4d60c7',actualToolReturnedExitCode=0)
 save(W/'encoded-caption-qa-execution.json',ex)
 boards=[dict(x,directlyRead=True)for x in ex['boards']if not x['reusedIdenticalPixels']]
 assert [x['index']for x in boards]==list(range(30,42))
 for x in boards+[x for x in ex['samples']if not x['reusedIdenticalPixels']]:assert sha(ROOT/x['path'])==x['sha256']
 proof=dict(reviewedAt=now(),sourceSha256=ex['sourceSha256'],source=ex['source'],directlyReadBoards=boards,
  directlyReadChangedSamples=66,reviewedSampleIndices=list(range(177,243)),
  observations=['Boards30-31: native90 seconds begins9/11, then12/11 before the question finishes; equal12/12 is visible before the factual assertion.',
   'Boards32-33: all encoded cue33/34 first/mid/last states show both LINES012. Actual scores2500/1502,2502/1508,2508/1514,2514/1518 differ. Captions are clear below the board and numeric UI.',
   'Boards34-36: play continues13/12 then13/13 with separate progress/evaluation explanation. Guide begins while both show13; later14/13 and15/13 are changes, not a persistent equality assertion.',
   'Boards37-40: compare/find imperative guides the viewer to observe line count, scores and signed difference; later15/14. No menu, loop, slowdown or unrelated idle.',
   'Board41: last game frames and exact next black03 boundary are clean; projected top/side faces and labels retain readable fixed-caption space.'],
  historicalDefect=rel(OLD/'equality-claim-pixel-defect-v1.json'),historicalDefectPreserved=True,
  correctedFactualClaimApproved=True,captionUiCollisions=[],allCurrentFinalPixelsReviewed=False,humanListeningApproved=False,publicRightsApproved=False)
 save(W/'corrected-cut-encoded-direct-review.json',proof)
proof=read(W/'corrected-cut-encoded-direct-review.json');assert proof['correctedFactualClaimApproved'] and proof['sourceSha256']==ex['sourceSha256']
identity=read(W/'unchanged-pixel-identity.json');assert identity['all18848OutsideCutDecodedFramesIdentical']
old=read(OLD/'encoded-caption-qa-direct-progress.json');seen=set(old['directlyReadBoards'])
reviewed=[]
for b in ex['boards']:
 if not b['reusedIdenticalPixels'] or b['index']in seen:
  assert sha(ROOT/b['path'])==b['sha256'];reviewed.append(dict(b,directlyRead=True,reviewBasis='corrected direct read'if not b['reusedIdenticalPixels']else'previous direct read plus exact decoded pixel identity'))
sample_indices=sorted({i for b in reviewed for i in b['sampleIndices']})
j=dict(recordedAt=now(),source=ex['source'],sourceSha256=ex['sourceSha256'],directlyReadBoards=[b['index']for b in reviewed],
 reviewedSampleIndices=sample_indices,reviewedBoards=reviewed,correctedCutReview=rel(W/'corrected-cut-encoded-direct-review.json'),
 correctedCutReviewSha256=sha(W/'corrected-cut-encoded-direct-review.json'),unchangedPixelIdentity=rel(W/'unchanged-pixel-identity.json'),
 unchangedPixelIdentitySha256=sha(W/'unchanged-pixel-identity.json'),previousDirectProgress=rel(OLD/'encoded-caption-qa-direct-progress.json'),
 historicalDefectPreserved=True,unresolvedPixelDefects=[],allFinalPixels=False,qa=False,collected=False,uploaded=False)
save(W/'encoded-caption-qa-direct-progress.json',j)
print(json.dumps(dict(currentReviewedBoards=len(reviewed),currentReviewedSamples=len(sample_indices),allFinalPixels=False)))
