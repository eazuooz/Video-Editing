"""Prepare final binding version for three newly detailed mixed EX clips; do not run."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
p=B/'prepare-orientation-current34-assembly-v2.py';s=p.read_text('utf-8')
s=s.replace('current34-assembly-inputs-v2.json','current34-assembly-inputs-v3.json')
needle='pieces = []\n'
assert s.count(needle)==1
s=s.replace(needle,"""mdreviewp=O/'current34-mixed-detailed-direct-review-v1.json'
mdreview=read(mdreviewp)
assert mdreview['allNewEncodedSamplesDirectlyRead'] and mdreview['all3NormalStartEndObserved']
mdstatep=O/'current34-mixed-detailed-render-execution-v2.json';mdstate=read(mdstatep)
assert mdstate['workerDead'] and mdstate['actualOuterExitCode']==0
assert mdreview['executionSha256']==sha(mdstatep)
mixed_details={x['id']:x for x in mdstate['results']}
assert set(mixed_details)=={'03b','07b','10b'}
for x in mixed_details.values():assert sha(ROOT/x['output'])==x['outputSha256']
pieces = []
""")
needle="    elif s['visual']:\n"
assert s.count(needle)==1
s=s.replace(needle,"""    elif sid in mixed_details:
        x=mixed_details[sid];assert n==x['frames']
        add(sid,x['output'],n,s['actualFrames'],s['explanationFrames'],source_sha=x['outputSha256'],note='Detailed EX subjects; prior reviewed gameplay/frozen decoder input RGB bytes preserved; selected current encoded EX/cuts and normal endpoints directly reviewed.')
    elif s['visual']:
""")
s=s.replace("    detailedExplanationPieceCount=17,originalByteIdenticalIds=", "    mixedDetailReview=rel(mdreviewp),mixedDetailReviewSha256=sha(mdreviewp),\n    detailedMixedPieceCount=3,\n    detailedExplanationPieceCount=17,originalByteIdenticalIds=")
out=B/'prepare-orientation-current34-assembly-v3.py';assert not out.exists();out.write_text(s,'utf-8')
p=B/'assemble-orientation-current34-pair-v2.py';s=p.read_text('utf-8')
for a,b in [('current34-final-pair-v2','current34-final-pair-v3'),('current34-final-pair-execution-v2','current34-final-pair-execution-v3'),('current34-assembly-inputs-v2','current34-assembly-inputs-v3')]:s=s.replace(a,b)
s=s.replace("('subjectPolicy','subjectPolicySha256')]:","('subjectPolicy','subjectPolicySha256'),('mixedDetailReview','mixedDetailReviewSha256')]:")
s=s.replace("inputs['detailedExplanationPieceCount']==17 and inputs['retainedByteIdenticalPieces']==3", "inputs['detailedExplanationPieceCount']==17 and inputs['detailedMixedPieceCount']==3 and inputs['retainedByteIdenticalPieces']==3")
out=B/'assemble-orientation-current34-pair-v3.py';assert not out.exists();out.write_text(s,'utf-8')
p=B/'record-orientation-current34-pair-worker-v2.py';s=p.read_text('utf-8').replace('current34-final-pair-execution-v2','current34-final-pair-execution-v3')
out=B/'record-orientation-current34-pair-worker-v3.py';assert not out.exists();out.write_text(s,'utf-8')
print('Prepared assemblyV3/pairV3/recorderV3; execution0, awaiting mixed3 direct review.')
