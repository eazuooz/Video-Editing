"""Bind eight reviewed clearance repairs and reuse 29 prepared V3 inputs byte-exact."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
priorp=O/'current34-assembly-inputs-v3.json';prior=rd(priorp)
v3p=O/'current34-final-pair-execution-v3.json';v3=rd(v3p)
assert v3['workerDead'] and v3['actualOuterExitCode']==0 and len(v3['pieces'])==37
sp=O/'current34-clearance-caption-bindings-execution-v1.json';s=rd(sp)
assert s['workerDead'] and s['actualOuterExitCode']==0
reviewp=O/'current34-clearance-caption-pixels-partial-direct-review-v1.json';review=rd(reviewp)
assert review['executionSha256']==sha(sp) and review['allSelectedPixelsDirectlyRead'] and review['samplesDirectlyRead']==557 and review['boardsDirectlyRead']==143
normalp=O/'07b-current-caption-clearance-normal-direct-review-v1.json';normal=rd(normalp)
assert normal['executionSha256']==sha(sp) and normal['normal1xMutedStartEndActuallyObserved']
exnormalp=O/'current34-caption-clearance-normal-direct-review-v2.json';exnormal=rd(exnormalp)
assert exnormal['all7NormalStartEndObserved']
oldreviewp=O/'current34-final-pixels-complete-held-direct-review-v1.json';oldreview=rd(oldreviewp)
assert oldreview['all3168PlannedSamplesDirectlyRead']
changed={x['id']:x for x in s['scenes']};assert set(changed)=={'07b','09a','12','13a','16a','16','18','21a'}
pieces=[];offset=0
for old in v3['pieces']:
 assert sha(ROOT/old['path'])==old['sha256']
 row=copy.deepcopy(old);row['absoluteStartFrame']=offset;offset+=row['frames']
 if row['id'] in changed:
  x=changed[row['id']];assert row['frames']==x['plannedFrames'] and row['absoluteStartFrame']==x['absoluteStartFrame']
  assert sha(ROOT/x['source'])==x['sourceSha256'] and sha(ROOT/x['output'])==x['outputSha256']
  row.update(replacesPath=old['path'],replacesSha256=old['sha256'],path=x['source'],sha256=x['sourceSha256'],reencodeRequired=row['id']!='07b',explanationTailPadFrames=x['explanationTailPadFrames'],clearanceRepaired=True,currentCaptionBinding=x['output'],currentCaptionBindingSha256=x['outputSha256'])
  for k in ['preparedFromPath','preparedFromSha256','reencoded']:row.pop(k,None)
 else:
  row.update(reencodeRequired=False,explanationTailPadFrames=0,reusedPreparedV3ByteExact=True,clearanceRepaired=False)
 pieces.append(row)
assert len(pieces)==37 and offset==65917 and sum(x['clearanceRepaired'] for x in pieces)==8
data={k:v for k,v in prior.items() if k!='pieces'}
data.update(preparedAt=datetime.now(timezone.utc).isoformat(),pieces=pieces,priorInputs=priorp.relative_to(ROOT).as_posix(),priorInputsSha256=sha(priorp),priorPairExecution=v3p.relative_to(ROOT).as_posix(),priorPairExecutionSha256=sha(v3p),
 clearanceExecution=sp.relative_to(ROOT).as_posix(),clearanceExecutionSha256=sha(sp),clearanceCaptionReview=reviewp.relative_to(ROOT).as_posix(),clearanceCaptionReviewSha256=sha(reviewp),clearance07bNormalReview=normalp.relative_to(ROOT).as_posix(),clearance07bNormalReviewSha256=sha(normalp),clearanceExplanationNormalReview=exnormalp.relative_to(ROOT).as_posix(),clearanceExplanationNormalReviewSha256=sha(exnormalp),priorCompleteHeldPixelReview=oldreviewp.relative_to(ROOT).as_posix(),priorCompleteHeldPixelReviewSha256=sha(oldreviewp),changedPieceCount=8,reusedPreparedByteExactPieces=29,finalRatioApproved=False,allFinalPixelsApproved=False)
out=O/'current34-assembly-inputs-v4.json';assert not out.exists();save(out,data)
print(json.dumps(dict(inputs=out.relative_to(ROOT).as_posix(),sha256=sha(out),changedPieces=8,reusedByteExactPieces=29,frames=65917,finalApproval=False)))
