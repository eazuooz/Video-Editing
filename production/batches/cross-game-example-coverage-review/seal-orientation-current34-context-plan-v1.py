"""Seal reviewed diagnostic boundaries, without approving phonetics or captions."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, wave
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
proposal=O/'current34-mixed-independent-context-proposal-v1.json'
review=O/'current34-mixed-whole-direct-review-v1.json'
out=O/'current34-mixed-independent-context-plan-v1.json'
assert not out.exists()
p=rd(proposal);w=rd(review);mix=rd(O/'current34-mix-execution-v2.json')
assert w['all34WholeTextsDirectlyCompared'] and not w['currentMixedAudioApproved']
assert sha(ROOT/p['wholeExecution'])==p['wholeExecutionSha256']==w['wholeExecutionSha256']
assert p['sourceSha256']==mix['decodedAacSha256']==w['decodedAacSha256']==sha(ROOT/p['sourcePath'])
assert len(p['contexts'])==180 and len(p['boundaries'])==146
scripts={s['id']:s['lines'] for s in rd(O/'script/current34-combined-v1.ko.json')['scenes']}
assert len(scripts)==34
for sid,lines in scripts.items():
 rows=[v for v in p['contexts'] if v['scene']==sid]
 assert len(rows)==len(lines)
 assert [v['paragraph'] for v in rows]==list(range(1,len(lines)+1))
 assert [v['expectedKo'] for v in rows]==lines
 assert all(a['coreEndSample']==b['coreStartSample'] for a,b in zip(rows,rows[1:]))
 for row in rows:
  assert row['startSample']<=row['coreStartSample']<row['coreEndSample']<=row['endSample']
  assert row['coreStartSample']-row['startSample']<=7200 and row['endSample']-row['coreEndSample']<=7200
  assert row['zeroPaddingSamplesEachSide']==14400 and not row['expectedWasRecognizerPrompt']
  assert sha(ROOT/row['wholeResult'])==row['wholeResultSha256']
  assert sha(ROOT/row['originalPcmPath'])==row['originalPcmSha256']
 bounds=[v for v in p['boundaries'] if v['scene']==sid]
 assert len(bounds)==len(rows)-1
 for i,b in enumerate(bounds):
  assert b['currentAacBoundarySample']==rows[i]['coreEndSample']==rows[i+1]['coreStartSample']
  assert b['previousExpected']==lines[i] and b['followingExpected']==lines[i+1]
  b.update(directlyReviewed=True,exactPhoneticBoundaryApproved=False)
with wave.open(str(ROOT/p['sourcePath']),'rb') as f:
 assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(48000,2,2)
 assert all(0<=r['startSample']<r['endSample']<=f.getnframes() for r in p['contexts'])
for v in mix['protectedInputs']:assert sha(ROOT/v['path'])==v['sha256']
p.update(sealedAt=datetime.now(timezone.utc).isoformat(),proposal=rel(proposal),proposalSha256=sha(proposal),wholeReview=rel(review),wholeReviewSha256=sha(review),all34WholeTextsDirectlyCompared=True,currentWholeWordsAndPcmBoundariesDirectlyCompared=True,all146BoundaryRowsDirectlyRead=True,boundaryDirectReadChunks=['2c0ad6','d326b0','a2551f','815871'],all79ProtectedUnchanged=True,coreCoverageContinuousWithinEachScene=True,contextEdgeOverlapIsDiagnostic=True,modelExecuted=False,currentMixedAudioApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,finalCaptionTimingApproved=False)
p['boundaryReviewNotes']=[
 'All146 rows compared previous/following complete expected paragraphs, nearby current whole words, exact8ms AAC RMS/peak and source24k mapping when applicable.',
 'Baseline24 use original distributed cue midpoints. Added10 use approved source diagnostic junctions mapped through current76 PCM placements; two images at an insertion junction identify its intentional observation gap.',
 '03b last boundary maps5 source samples after the allocation junction.07b last boundary lies in an intentional quiet gap; whole word timestamps stretched across it do not identify caption timing.',
 '04p03,07p04/p05 and24p01 contain nonzero edge energy or recognizer endpoints crossing the core split. Disclosed150ms adjoining context protects diagnostic comparison; this seal does not assert exact phonetic boundaries.',
 '180 independent complete contexts must still be recognized and directly compared. Adjacent words at overlapping edges are diagnostic context, not proof of a repeated sentence in the mix.'
]
out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(contexts=180,boundaries=146,sealedDiagnosticPlan=True,modelRun=False,captionApproved=False)))
