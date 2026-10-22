from common import *
P=R/'projects/game-math-orientation-matrices';H=P/'production/concept-fit-v2';p=P/'project.json';d=read(p)
d['activeConceptFitRevision']=dict(id='concept-fit-v2',scope='Original15:03 private orientation/matrix lecture',authorization=rel(B/'authorization.json'),timeline=rel(H/'timeline.json'),script=rel(P/'script/concept-fit-v2/narration.ko.json'),outputs=rel(H/'outputs.json'),reviewLedger=rel(H/'review-ledger.json'),renderer=rel(B/'m03-scenes.py'),humanReview='pending',oldPathsPreserved=True)
save(p,d)
paths=[]
for folder in [B,H,P/'script/concept-fit-v2',P/'publishing/revisions/concept-fit-v2']:
 paths += [rel(x) for x in folder.rglob('*') if x.is_file() and x.suffix in ['.py','.json','.md','.txt','.srt'] and '__pycache__' not in x.parts and x.name!='m03-complete-commit.json']
shared=['shared/publishing/video-production-control.json','shared/publishing/video-worklist.json','docs/VIDEO_WORKFLOW.md','docs/GAME_MATH_PRIVATE_POLISH.md',rel(p)]
paths +=shared+['docs/GAME_MATH_PRIVATE_POLISH.md',rel(P/'rebuild.json')]
save(B/'m03-complete-commit.json',dict(paths=sorted(set(paths)),sharedPaths=shared,message='Restore original matrix lecture and audit concept-matched math footage'))
print(len(set(paths)),'owned paths prepared')
