"""Prepare exact reviewed detail/guide bindings and a new final-pair worker."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
def new(name,text):
 p=B/name;assert not p.exists();p.write_text(text,'utf-8')
text=(B/'prepare-orientation-current34-assembly-v1.py').read_text('utf-8-sig')
text=text.replace('current34-assembly-inputs-v1.json','current34-assembly-inputs-v2.json')
text=text.replace('current34-overview-render-execution-v4.json','current34-overview-render-execution-v5.json').replace('current34-overview-direct-review-v4.json','current34-overview-direct-review-v5.json')
text=text.replace("gs = {x['id']: x for x in guides['results']}","""gs = {x['id']: x for x in guides['results']}
dsreviewp=O/'current34-detailed-explanations-sampled-direct-review-v1.json'
dnreviewp=O/'current34-detailed-explanations-normal-direct-review-v1.json'
dsreview=read(dsreviewp);dnreview=read(dnreviewp)
assert dsreview['all605SamplesDirectlyRead'] and dnreview['all17NormalStartEndObserved']
assert dnreview['sampledReviewSha256']==sha(dsreviewp)
details={x['scene']:x for x in dsreview['rows']}
assert set(details)=={x['scene'] for x in dnreview['rows']}
for x in dsreview['executions']:
 assert sha(ROOT/x['path'])==x['sha256']
for x in details.values():assert sha(ROOT/x['video'])==x['videoSha256']""")
text=text.replace("    elif s['visual']:\n", """    elif sid in details:
        x=details[sid]; assert s['actualFrames']==0
        add(sid,x['video'],n,0,n,source_sha=x['videoSha256'],note='Detailed illustrative aircraft/mounted camera; retained math/narration/timing, selected moving samples and normal endpoints reviewed.')
    elif s['visual']:
""")
text=text.replace('retainedByteIdenticalPieces=14','retainedByteIdenticalPieces=3').replace("== 14\nout.write_text", "== 3\nout.write_text").replace('inputs=37, retained=14','inputs=37, retained=3')
text=text.replace("    pieces=pieces,", """    detailedSampleReview=rel(dsreviewp),detailedSampleReviewSha256=sha(dsreviewp),
    detailedNormalReview=rel(dnreviewp),detailedNormalReviewSha256=sha(dnreviewp),
    overviewReview=rel(O/'current34-overview-direct-review-v5.json'),overviewReviewSha256=sha(O/'current34-overview-direct-review-v5.json'),
    guideReview=rel(O/'current34-baseline-guides-direct-review-v1.json'),guideReviewSha256=sha(O/'current34-baseline-guides-direct-review-v1.json'),
    subjectPolicy='shared/publishing/illustrative-subject-detail-policy.json',subjectPolicySha256=sha(ROOT/'shared/publishing/illustrative-subject-detail-policy.json'),
    detailedExplanationPieceCount=17,originalByteIdenticalIds=['intro','19','outro'],
    genuineStorage18Preserved=True,genuineSyntax19Preserved=True,
    pieces=pieces,""")
new('prepare-orientation-current34-assembly-v2.py',text)
text=(B/'assemble-orientation-current34-pair-v1.py').read_text('utf-8-sig')
text=text.replace('current34-final-pair-v1','current34-final-pair-v2').replace('current34-final-pair-execution-v1.json','current34-final-pair-execution-v2.json').replace('current34-assembly-inputs-v1.json','current34-assembly-inputs-v2.json').replace('retainedByteIdenticalPieceCount=14','retainedByteIdenticalPieceCount=3')
needle="    layout = read(O/'current34-caption-layout-v1.json');"
text=text.replace(needle,"""    for pathkey,hashkey in [('detailedSampleReview','detailedSampleReviewSha256'),('detailedNormalReview','detailedNormalReviewSha256'),('overviewReview','overviewReviewSha256'),('guideReview','guideReviewSha256'),('subjectPolicy','subjectPolicySha256')]:
        assert sha(ROOT/inputs[pathkey])==inputs[hashkey]
    assert inputs['detailedExplanationPieceCount']==17 and inputs['retainedByteIdenticalPieces']==3
"""+needle)
new('assemble-orientation-current34-pair-v2.py',text)
text=(B/'record-orientation-current34-pair-worker-v1.py').read_text('utf-8-sig').replace('current34-final-pair-execution-v1.json','current34-final-pair-execution-v2.json').replace("s['retainedByteIdenticalPieceCount'] == 14", "s['retainedByteIdenticalPieceCount'] == 3")
new('record-orientation-current34-pair-worker-v2.py',text)
print('Prepared detailed assemblyV2/pairV2/recorderV2 only; no media executed.')
