"""Create a new final pair worker for reviewed targeted repairs; never rerun V3."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
s=(B/'assemble-orientation-current34-pair-v3.py').read_text('utf-8')
for a,b in [('current34-final-pair-v3','current34-final-pair-v4'),('current34-final-pair-execution-v3','current34-final-pair-execution-v4'),('current34-assembly-inputs-v3','current34-assembly-inputs-v4')]:s=s.replace(a,b)
needle="    assert inputs['detailedExplanationPieceCount']==17 and inputs['detailedMixedPieceCount']==3 and inputs['retainedByteIdenticalPieces']==3\n"
assert s.count(needle)==1
s=s.replace(needle,needle+"""    for pk,hk in [('clearanceExecution','clearanceExecutionSha256'),('clearanceCaptionReview','clearanceCaptionReviewSha256'),('clearance07bNormalReview','clearance07bNormalReviewSha256'),('clearanceExplanationNormalReview','clearanceExplanationNormalReviewSha256'),('priorPairExecution','priorPairExecutionSha256'),('priorCompleteHeldPixelReview','priorCompleteHeldPixelReviewSha256')]:
        assert sha(ROOT/inputs[pk])==inputs[hk]
    cr=read(ROOT/inputs['clearanceCaptionReview']); assert cr['allSelectedPixelsDirectlyRead'] and cr['samplesDirectlyRead']==557
    assert read(ROOT/inputs['clearance07bNormalReview'])['normal1xMutedStartEndActuallyObserved']
    assert read(ROOT/inputs['clearanceExplanationNormalReview'])['all7NormalStartEndObserved']
    assert inputs['changedPieceCount']==8 and inputs['reusedPreparedByteExactPieces']==29
    assert sum(x['reencodeRequired'] for x in inputs['pieces'])==7
""")
s=s.replace("            bodyMeasured={k:inputs[k] for k in ['bodyFrames','actualFrames','explanationFrames','ratioErrorFrames']})", "            changedPieceCount=8, reusedPreparedByteExactPieces=29, assemblyInputs=rel(O/'current34-assembly-inputs-v4.json'), assemblyInputsSha256=sha(O/'current34-assembly-inputs-v4.json'),\n            bodyMeasured={k:inputs[k] for k in ['bodyFrames','actualFrames','explanationFrames','ratioErrorFrames']})")
s=s.replace('Observe actual pair exit and all244 final cue/cut/annotation/UI pixels;', 'Observe actual new pair exit, changed eight-scene final pixels and cut boundaries; reuse reviewed unchanged29 input evidence without source re-review;')
p=B/'assemble-orientation-current34-pair-v4.py';assert not p.exists();p.write_text(s,'utf-8')
s=(B/'record-orientation-current34-pair-worker-v3.py').read_text('utf-8').replace('current34-final-pair-execution-v3','current34-final-pair-execution-v4')
s=s.replace('Fresh resource, then inspect every current244 cue and37 cut boundary with moving guides/UI/cat/member;', 'Fresh resource, then inspect new final changed eight-scene samples and37 cut boundaries; preserve approved unchanged29 evidence;')
p=B/'record-orientation-current34-pair-worker-v4.py';assert not p.exists();p.write_text(s,'utf-8')
print('Prepared new pairV4/recorderV4; eight repairs plus29 prepared byte-exact inputs; no execution.')
