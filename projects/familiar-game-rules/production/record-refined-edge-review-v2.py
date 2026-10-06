"""Lock all13 refined boards; keep framing/duplicate and final gates explicit."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix();stamp=datetime.now(timezone.utc).isoformat()
def write(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
dest=PROOF/'additional-cut-edge-direct-review-v2.json';assert not dest.exists()
state=read(PROOF/'additional-cut-edges-execution-v2.json');assert state['pid']==9844 and len(state['boards'])==13
assert all(c['exitCode']==0 for c in state['children'])
notes={
 'additional-08':'Pink door kick to pink corridor kick; FLASH promotional slate no longer included.',
 'additional-09':'Escalator firing to purple crate-door kick; FIRE promotional slate no longer included.',
 'additional-10':'Burning crossbow room to close flaming-target kick; FLOATIES slate no longer included.',
 'additional-11':'Floating target shots to roof-to-roof kick; UPPER CUTTERS slate no longer included.',
 'additional-12':'Bathroom target to upward corridor kick; RAGE slate no longer included.',
 'additional-13':'Lobby door kick to corridor explosion; THRUSTERS slate no longer included.',
 'additional-14':'Last included frame is a shield-group kick, outside-end begins a third-person shoe shot. However first edge itself is a third-person stationary platform framing; reserve the whole candidate rather than count it as clean first-person action.',
 'additional-15':'ACTION ADVENTURE title removed, but first frame shows empty rail scenery with character outside the visible first edge. Reserve pending action-only start rather than approve the whole interval.',
 'additional-17':'Forest-wire umbrella to rooftop firing; thick letterbox at old out-point no longer included.',
 'additional-22':'Rail-side traversal to rainy wall ascent; NPC dialogue at old end no longer included.',
 'additional-23':'Rainy wire jump to cult-room shots/projectiles; letterboxed city transition at old end no longer included.',
 'additional-25':'Swamp airborne enemy/projectile to container jump/fire; NPC dialogue at old end no longer included.',
 'additional-26':'City wall climb/fire starts clean. Last included frame is already darkening into a transition, so reserve whole candidate; no black/white promotional interval counted.',
}
reserved={'additional-14','additional-15','additional-26'}
for b in state['boards']:
    assert sha(ROOT/b['board'])==b['sha256']
    for t in b['tiles']:assert sha(ROOT/t['path'])==t['sha256']
    b.update(directlyRead=True,reviewedAt=stamp,observation=notes[b['actionId']],selectedSourceEdgeApproval=b['actionId'] not in reserved)
state.update(status='closed-all13-refined-edge-boards-read-cross-source-selection-pending',reviewedAt=stamp,allDirectlyRead=True,alive=False,sessionId=86251,actualExitObserved=True,exitCode=0,exactCutApproval=False)
write(PROOF/'additional-cut-edges-execution-v2.json',state)
sess=read(PROOF/'additional-cut-edges-execution-v2.session.json');sess.update(observedAt=stamp,alive=False,exitObserved=True,exitCode=0,status=state['status'],commandLine=['C:/Users/eazuo/miniconda3/envs/renderformer/python.exe','-X','utf8',rel(BASE/'extract-additional-edges-v2.py')]);write(PROOF/'additional-cut-edges-execution-v2.session.json',sess)
bank=read(PROOF/'additional-action-bank-candidates-v2.json');old=read(PROOF/'additional-cut-edges-execution-v1.json')
for c in bank['clips']:
    b=next(x for x in (state['boards'] if c['requiresNewBoundaryExtraction'] else old['boards']) if x['actionId']==c['id'])
    c.update(edgeBoard=b['board'],edgeBoardSha256=b['sha256'],edgeObservation=b['observation'],exactEdgeApproval=c['id'] not in reserved,sourceEdgeReviewedAt=stamp,crossSourceDuplicateSelectionApproved=False)
    if c['id'] in reserved:c['classification']='reserved-source-edge-not-approved'
bank.update(allEdgesDirectlyRead=True,reviewedAt=stamp,status='refined-edges-read; repeated actions not selected',reservedCandidateIds=sorted(reserved),edgeApprovedCandidateSeconds=sum(c['seconds'] for c in bank['clips'] if c['exactEdgeApproval']),approvedUniqueAdditionalSeconds=0,crossSourceDuplicateSelectionApproved=False,ratioApproved=False)
write(PROOF/'additional-action-bank-candidates-v2.json',bank)
write(dest,dict(schemaVersion=2,slug='familiar-game-rules',reviewedAt=stamp,all13RefinedBoardsDirectlyRead=True,frameSlots=78,observations=notes,reservedCandidateIds=sorted(reserved),manifestSha256=sha(PROOF/'additional-cut-edges-execution-v2.json'),bankSha256=sha(PROOF/'additional-action-bank-candidates-v2.json'),approvedUniqueAdditionalSeconds=0,crossSourceDuplicateSelectionApproved=False,finalPixelApproval=False,imagesGitPolicy='local-only'))
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
ex={**item['additionalCutEdgeExecution'],'status':state['status'],'sessionId':86251,'alive':False,'actualExitObserved':True,'exitCode':0,'activeTasks':[],'directReview':rel(dest),'all13RefinedBoardsDirectlyRead':True,'approvedUniqueAdditionalSeconds':0}
item.update(stage=state['status'],updatedAt=stamp,additionalCutEdgeExecution=ex,nextAction='Compare repeated actions in retained source-edge candidates against the37 previous intervals and each other. Preserve current11PCM and147.2s white explanation; acquire clean unique official action if still short. No ratio, narration, render or upload approval.')
q.update(updatedAt=stamp,lastProgressAt=stamp);write(qp,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','nextAction','additionalCutEdgeExecution']:d[k]=item[k]
    write(p,d)
print(json.dumps(dict(refinedBoardsRead=13,reserved=list(sorted(reserved)),edgeApprovedCandidateSeconds=bank['edgeApprovedCandidateSeconds'],uniqueSelectionApproved=False)))
