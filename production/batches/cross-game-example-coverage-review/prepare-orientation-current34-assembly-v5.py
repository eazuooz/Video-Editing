"""Bind reviewed06a only; preserve36 prepared V4 inputs byte-exact."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,py_compile
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
priorp=O/'current34-assembly-inputs-v4.json';prior=rd(priorp)
pairp=O/'current34-final-pair-execution-v4.json';pair=rd(pairp);assert pair['workerDead'] and pair['actualOuterExitCode']==0
sp=O/'current34-06a-caption-clearance-execution-v1.json';s=rd(sp);assert s['workerDead'] and s['actualOuterExitCode']==0
rp=O/'current34-06a-caption-clearance-sampled-direct-review-v1.json';r=rd(rp);assert r['executionSha256']==sha(sp) and r['all32SamplesDirectlyRead'] and r['targetedCaptionClearanceApproved']
np=O/'06a-current-caption-clearance-normal-direct-review-v1.json';n=rd(np);assert n['executionSha256']==sha(sp) and n['normal1xMutedStartEndActuallyObserved']
oldrp=O/'current34-final-v4-pixels-partial-direct-review-v1.json';oldr=rd(oldrp);assert oldr['allNewDirectPixelsRead'] and oldr['samplesDirectlyRead']==818
pieces=[];offset=0;x=s['scenes'][0]
for old in pair['pieces']:
 assert sha(ROOT/old['path'])==old['sha256']
 row=copy.deepcopy(old);row.update(absoluteStartFrame=offset,clearanceRepaired=old['id']=='06a',reusedPreparedV4ByteExact=old['id']!='06a',reencodeRequired=old['id']=='06a',explanationTailPadFrames=0);offset+=row['frames']
 if row['id']=='06a':
  assert row['frames']==x['plannedFrames']==759 and row['absoluteStartFrame']==x['absoluteStartFrame']==14232
  assert sha(ROOT/x['source'])==x['sourceSha256'] and sha(ROOT/x['output'])==x['outputSha256']
  row.update(replacesPath=old['path'],replacesSha256=old['sha256'],path=x['source'],sha256=x['sourceSha256'],explanationTailPadFrames=x['explanationTailPadFrames'],currentCaptionBinding=x['output'],currentCaptionBindingSha256=x['outputSha256'])
  for key in ['preparedFromPath','preparedFromSha256','reencoded']:row.pop(key,None)
 pieces.append(row)
assert offset==65917 and len(pieces)==37
data={k:v for k,v in prior.items() if k!='pieces'}
data.update(preparedAt=datetime.now(timezone.utc).isoformat(),pieces=pieces,priorV4Inputs=priorp.relative_to(ROOT).as_posix(),priorV4InputsSha256=sha(priorp),priorPairExecution=pairp.relative_to(ROOT).as_posix(),priorPairExecutionSha256=sha(pairp),
 additionalClearanceExecution=sp.relative_to(ROOT).as_posix(),additionalClearanceExecutionSha256=sha(sp),additionalClearanceSampleReview=rp.relative_to(ROOT).as_posix(),additionalClearanceSampleReviewSha256=sha(rp),additionalClearanceNormalReview=np.relative_to(ROOT).as_posix(),additionalClearanceNormalReviewSha256=sha(np),priorV4PixelReview=oldrp.relative_to(ROOT).as_posix(),priorV4PixelReviewSha256=sha(oldrp),changedPieceCount=1,reusedPreparedByteExactPieces=36,finalRatioApproved=False,allFinalPixelsApproved=False)
out=O/'current34-assembly-inputs-v5.json';assert not out.exists();out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
w=(B/'assemble-orientation-current34-pair-v4.py').read_text('utf-8')
for a,b in [('current34-final-pair-v4','current34-final-pair-v5'),('current34-final-pair-execution-v4','current34-final-pair-execution-v5'),('current34-assembly-inputs-v4','current34-assembly-inputs-v5'),("inputs['changedPieceCount']==8 and inputs['reusedPreparedByteExactPieces']==29","inputs['changedPieceCount']==1 and inputs['reusedPreparedByteExactPieces']==36"),("sum(x['reencodeRequired'] for x in inputs['pieces'])==7","sum(x['reencodeRequired'] for x in inputs['pieces'])==1"),('changedPieceCount=8, reusedPreparedByteExactPieces=29','changedPieceCount=1, reusedPreparedByteExactPieces=36'),('changed eight-scene final pixels and cut boundaries; reuse reviewed unchanged29 input evidence','changed06a final pixels and cut boundaries; reuse reviewed unchanged36 input evidence')]:
 assert a in w,a;w=w.replace(a,b)
needle="    assert sum(x['reencodeRequired'] for x in inputs['pieces'])==1\n";assert w.count(needle)==1
w=w.replace(needle,needle+"""    for pk,hk in [('additionalClearanceExecution','additionalClearanceExecutionSha256'),('additionalClearanceSampleReview','additionalClearanceSampleReviewSha256'),('additionalClearanceNormalReview','additionalClearanceNormalReviewSha256'),('priorV4PixelReview','priorV4PixelReviewSha256')]:
        assert sha(ROOT/inputs[pk])==inputs[hk]
    assert read(ROOT/inputs['additionalClearanceSampleReview'])['all32SamplesDirectlyRead']
    assert read(ROOT/inputs['additionalClearanceNormalReview'])['normal1xMutedStartEndActuallyObserved']
    assert read(ROOT/inputs['priorV4PixelReview'])['allNewDirectPixelsRead']
""")
wp=B/'assemble-orientation-current34-pair-v5.py';assert not wp.exists();wp.write_text(w,'utf-8');py_compile.compile(str(wp),doraise=True)
w=(B/'record-orientation-current34-pair-worker-v4.py').read_text('utf-8').replace('current34-final-pair-execution-v4','current34-final-pair-execution-v5').replace('changed eight-scene samples','changed06a samples').replace('unchanged29 evidence','unchanged36 evidence')
wp=B/'record-orientation-current34-pair-worker-v5.py';assert not wp.exists();wp.write_text(w,'utf-8');py_compile.compile(str(wp),doraise=True)
print(json.dumps(dict(inputs=out.relative_to(ROOT).as_posix(),sha256=sha(out),changed=1,reusedPreparedByteExact=36,frames=offset)))
