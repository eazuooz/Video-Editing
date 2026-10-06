"""Record ten read boundary boards without treating candidate capacity as QA."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,time,copy
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=datetime.now(timezone.utc).isoformat()
def write(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
dest=PROOF/'additional-cut-edge-direct-review-v3.json';assert not dest.exists()
state=read(PROOF/'additional-cut-edges-execution-v3.json');assert state['pid']==27756 and len(state['boards'])==10 and all(c['exitCode']==0 for c in state['children'])
notes={
'additional-23':'REJECT current trim: rainy overhead wire at38/39 changes into an already-used cult-rope encounter by39.433. Do not approve38–39.5. Omit the whole short candidate; the retained bank has sufficient planning capacity without this unsafe mixed interval.',
'hype-01':'9–15: train interior aimed firing, traversal through doors and crates. Both edges contain ordinary action; source camera tilt preserved.',
'hype-02':'15–21: aim/fire toward targets at different crate heights and traverse the train. Both edges active; no external slate.',
'hype-03':'21–27: jump, independent left/right aiming in native middle samples, land and fire across the next car. Active source edges.',
'hype-04':'27–33: continue through car with shooting and crate-height changes into explosion. Active edges; do not infer unshown buttons.',
'hype-05':'33–39: crate/roof traverse and airborne downward fire into another train car. Active source edges.',
'hype-06':'39–45: airborne body movement with downward/side aim and spinning action; source speed/camera retained, no editor slowdown.',
'hype-07':'45–51: airborne fire into roof traversal, body and targets visible at both edges.',
'hype-08':'51–54.5: roof movement down into car and firing; end precedes the closer head impact around55. Player/targets retained at boundaries.',
'hype-09':'RESERVE: at57 first frames the player is partly outside the original top edge. Additional full-screen crop could worsen it. Omit all4seconds for conservative framing;61.5TV/promo is also excluded.',
}
by={}
for b in state['boards']:
    assert sha(ROOT/b['board'])==b['sha256']
    for t in b['tiles']:assert sha(ROOT/t['path'])==t['sha256']
    b.update(directlyRead=True,reviewedAt=stamp,observation=notes[b['actionId']],sourceEdgeApproved=b['actionId'] not in ['additional-23','hype-09'])
    by[b['actionId']]=b
state.update(status='closed-all10-new-edge-boards-read-eight-Hype-retained',allDirectlyRead=True,alive=False,actualExitObserved=True,exitCode=0,finishedProcessObservation='Unified exec returned0; subsequent CIM found parent27756 and children60712/46980 absent. No process was terminated.',exactCutApproval=False,finalPixelApproval=False,directReview=rel(dest),updatedAt=stamp)
write(PROOF/'additional-cut-edges-execution-v3.json',state)
bank=copy.deepcopy(read(PROOF/'source-action-bank-v3.json'));kept=[]
for c in bank['clips']:
    if c['id'] in ['additional-23','hype-09']:
        c.update(selectedForExpandedBank=False,countsTowardSelectedActualSeconds=False,exactEdgeApproval=False,selectionObservation=notes[c['id']]);bank['excluded'].append(c);continue
    if c['id'] in by:
        b=by[c['id']];c.update(exactEdgeApproval=True,requiresNewBoundaryExtraction=False,edgeBoard=b['board'],edgeBoardSha256=b['sha256'],edgeObservation=notes[c['id']],sourceEdgeReviewedAt=stamp,classification='actual-existing-game-action')
    kept.append(c)
assert len(kept)==60 and all(c['exactEdgeApproval'] for c in kept)
numsecs=lambda c:(c['outFrameExclusive']-c['inFrameInclusive'])*int(c['sourceFrameRate'].split('/')[1])/int(c['sourceFrameRate'].split('/')[0])
bank.update(schemaVersion=4,createdAt=stamp,previousBank=rel(PROOF/'source-action-bank-v3.json'),clips=kept,clipCount=60,retainedAdditionalClipCount=15,newHypeClipCount=8,newBoundariesPending=0,candidateSeconds=sum(map(numsecs,kept)),additionalSeconds=sum(numsecs(c) for c in kept if c['id'].startswith('additional-')),hypeSeconds=sum(numsecs(c) for c in kept if c['id'].startswith('hype-')),status='60-distinct-source-edge-intervals-reviewed-framing-captions-timing-pending',allEdgesDirectlyRead=True,newEdgeReview=rel(dest))
write(PROOF/'source-action-bank-v4.json',bank)
write(dest,dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=stamp,boardsRead=10,frameSlotsRead=60,all10DirectlyRead=True,sourceEdgesRetained=8,omitted=['additional-23','hype-09'],notes=notes,previousPreStateFailure=dict(log=rel(BASE/'additional-cut-edges-v3.log'),reason='Missing optional requiresNewBoundaryExtraction key on old preserved intervals; failed before output/state. Changed to get(defaultFalse); one actual extraction then completed0.'),expandedBank=rel(PROOF/'source-action-bank-v4.json'),expandedBankSha256=sha(PROOF/'source-action-bank-v4.json'),candidateSeconds=bank['candidateSeconds'],sourceCapacityIsFinalTiming=False,fullScreenFramingApproved=False,finalCutAndCaptionApproval=False,ratioApproved=False,narrationApproved=False,imagesGitPolicy='local-only'))
cp=ROOT/'projects/familiar-game-rules/sources/game-candidates.json';d=read(cp)
d.update(expandedActionBank=rel(PROOF/'source-action-bank-v4.json'),crossSourceSelectionReview=rel(PROOF/'cross-source-selection-direct-review-v1.json'),newEdgeReview=rel(dest),selectedIntervalCount=60,selectedSourceCapacitySeconds=bank['candidateSeconds'],finalCutAndCaptionApproval=False,updatedAt=stamp);write(cp,d)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
ex=dict(pid=27756,commandLine=[os.sys.executable,'projects/familiar-game-rules/production/extract-additional-edges-v3.py'],alive=False,actualExitObserved=True,exitCode=0,sessionId=None,executionReturnedSynchronously=True,state=rel(PROOF/'additional-cut-edges-execution-v3.json'),log=rel(BASE/'additional-cut-edges-v3-retry.log'),children=state['children'],activeTasks=[],cpuThreads=2,gpuJobs=0,all10NewBoardsDirectlyRead=True,directReview=rel(dest),foreignWorkPreserved=True)
item.update(stage=bank['status'],updatedAt=stamp,additionalNewCutEdgeExecution=ex,expandedSourceBank=dict(path=rel(PROOF/'source-action-bank-v4.json'),clipCount=60,sourceCandidateSeconds=bank['candidateSeconds'],allSourceEdgesReviewed=True,ratioApproved=False,fullScreenFramingApproved=False,finalPixelApproval=False),nextAction='Review current duplicate-input changes; full-screen/caption framing of60 source intervals; then new independent KOEN commentary and MC scene wrappers preserving all11PCM/147.2s explanation. Source capacity233.467s is planning only; final ratio/narration/render/QA/collection/private remain false.')
q.update(updatedAt=stamp,lastProgressAt=stamp);write(qp,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','additionalNewCutEdgeExecution','expandedSourceBank','nextAction']:d[k]=item[k]
    write(p,d)
print(json.dumps({k:bank[k] for k in ['clipCount','oldSeconds','additionalSeconds','hypeSeconds','candidateSeconds']}))
