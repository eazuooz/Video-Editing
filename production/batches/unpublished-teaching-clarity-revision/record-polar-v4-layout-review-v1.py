"""Seal bounded direct review of all six v4 layouts; moving/final gates stay false."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=read(OUT/'remaining-editorial-annotation-preparation-v4.json')
notes={
 '05':'All12 samples/2 boards read. Horizontal component and height are separate; yellow whole-rider bracket is removed. World-plane height is distinguished from ground clearance.',
 '08':'All76 samples/13 boards read, including repaired frame2009/2010/2011 and2363–2423. Direction arrow and rotation arc are labelled explanatory roles. Normal-speed turns, jumps and flips illustrate direction versus attitude; blue screen-vertical reference is distinct from world height. Head remains visible in the selected repaired source samples. No camera/engine reconstruction is claimed.',
 '11':'All19 samples/4 boards read. Separate blue placement and red look directions join camera and target symbols in a labelled relation model; neither symbol claims a recovered image/world location.',
 '14':'All12 samples/2 boards read. Relative-vector model remains legible beside climbing and descending action. Canonical coordinates and following policy stay separate.',
 '16':'All21 samples/4 boards read. Opposite subtraction directions and formula agree with narration. Real tree occlusion illustrates an obstruction, without inferring an internal engine algorithm.',
 '18':'All10 samples/2 boards read. Yellow position axes, red attitude arc and blue camera cone visibly separate the three quantities and preserve the original concluding narration.'}
jobs=[]
for job in proof['jobs']:
    assert sha(ROOT/job['plan'])==job['planSha256']
    for row in job['samples']+job['boards']:assert sha(ROOT/row['path'])==row['sha256']
    jobs.append({**job,'directReview':notes[job['scene']],
      'boundedPreparedLayoutApproved':True,'movingAnnotationApproved':False,
      'fixedCaptionedEncodedPixelsApproved':False,'allContinuousFramesApproved':False})
assert sum(len(j['samples']) for j in jobs)==150
assert sum(len(j['boards']) for j in jobs)==27
dest=OUT/'remaining-editorial-annotation-direct-review-v4.json';assert not dest.exists()
dest.write_text(json.dumps({'reviewedAt':datetime.now(timezone.utc).isoformat(),
 'preparationSha256':sha(OUT/'remaining-editorial-annotation-preparation-v4.json'),
 'jobs':jobs,'all150PreparedSamplesAnd27BoardsDirectlyRead':True,
 'sixBoundedPreparedLayoutsApproved':True,'narrationChanged':False,
 'movingReviewApproved':False,'wholeVideoApproved':False,'allFinalPixelsApproved':False,
 'currentWholeMixedAsrApproved':False,'newImageGitAdded':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'layouts':6,'samples':150,'boards':27,'boundedPreparedLayoutApproved':True,'finalApproval':False}))
