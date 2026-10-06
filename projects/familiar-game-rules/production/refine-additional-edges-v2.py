"""Record directly observed coarse-edge defects, then prepare new edges only."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os, time
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
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
dest=PROOF/'additional-cut-edge-direct-review-v1.json'
assert not dest.exists(),'Preserve completed direct review'
state=read(PROOF/'additional-cut-edges-execution-v1.json')
closed=read(PROOF/'additional-cut-edges-execution-v1.session.json')
assert closed['exitObserved'] and closed['exitCode']==0
assert len(state['boards'])==26 and all(c['exitCode']==0 for c in state['children'])
notes=[
 'Corridor, pink doorway firing and purple floating enemies; action at both boundaries.',
 'Purple room to door kick and escalator close kick; edited montage, no single-encounter claim.',
 'Escalator close kick to pink corridor shotgun firing.',
 'Pink corridor firing to dark stair room. Correct the coarse sewer/weapon-throw description.',
 'Dark doorway kick to bathroom purple close target.',
 'Bathroom shot to purple tentacle above. Do not describe the entire interval as a bathroom kick.',
 'Upward kick/flying furniture to living-room minigun against green armor.',
 'Pink door action at start, FLASH sneaker promotion included before last: shorten out point.',
 'Escalator action at start, FIRE sneaker promotion included before last: shorten out point.',
 'Crossbow firing at start, FLOATIES sneaker promotion included before last: shorten out point.',
 'Floating firing at start, UPPER CUTTERS sneaker promotion included before last: shorten out point.',
 'Bathroom upward kick at start, RAGE sneaker promotion included before last: shorten out point.',
 'Lobby doorway firing at start, THRUSTERS sneaker promotion included before last: shorten out point.',
 'Upper platform at start, third-person shoe showroom included before last: shorten out point.',
 'Train traversal but faint ACTION ADVENTURE title at first edge: conservatively move start.',
 'City roof umbrella leap to forest wire. Both boundaries action; cross-source repetition unapproved.',
 'Forest wire to laundry roof; last frame acquires thick internal letterbox: shorten out point.',
 'City firing is internally letterboxed at start, cult action at end. Reserve whole candidate pending framing, count zero.',
 'Cult chamber airborne action to industrial ground shooting. Edited montage, not a continuous encounter.',
 'Industrial ground firing to vertical lift movement; real action boundaries but cross-source comparison pending.',
 'Wire-container traversal to eye-arena umbrella/airborne firing; likely reused action, compare before selection.',
 'Train action at start but NPC dialogue included before last; conservatively shorten out point.',
 'Rainy wire-container action to internally letterboxed city transition; conservatively shorten out point.',
 'Library lower-floor firing to swamp bridge airborne target. Edited action montage at boundaries.',
 'Swamp airborne target at start, NPC dialogue before last: shorten out point.',
 'City wall ascent at start, black/white transition at end: shorten out point.',
]
for b,note in zip(state['boards'],notes):
    assert sha(ROOT/b['board'])==b['sha256']
    for t in b['tiles']:assert sha(ROOT/t['path'])==t['sha256']
    b.update(directlyRead=True,reviewedAt=stamp,observation=note)
state.update(allDirectlyRead=True,reviewedAt=stamp,status='closed-all26-coarse-edges-read-refinements-required',alive=False,sessionId=95748,actualExitObserved=True,exitCode=0,exactCutApproval=False)
write(PROOF/'additional-cut-edges-execution-v1.json',state)
write(dest,dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=stamp,all26BoardsDirectlyRead=True,frameSlots=156,observations=notes,manifestSha256=sha(PROOF/'additional-cut-edges-execution-v1.json'),sourceEdgeApproval=False,crossSourceDuplicateSelectionApproved=False,finalPixelApproval=False,imagesGitPolicy='local-only'))
bank=read(PROOF/'additional-action-bank-candidates-v1.json')
updates={8:(None,1141),9:(None,1471),10:(None,1891),11:(None,2251),12:(None,2521),13:(None,2791),14:(None,3121),15:(960,None),17:(None,1440),22:(None,360),23:(None,1230),25:(None,1830),26:(None,1980)}
refined=[]
for i,c in enumerate(bank['clips'],1):
    if i==18:continue
    c={**c,'previousCandidateId':c['id'],'coarseEdgeObservation':notes[i-1]}
    if i in updates:
        start,end=updates[i]
        if start is not None:c['inFrameInclusive']=start
        if end is not None:c['outFrameExclusive']=end
        c['refinementReason']='Conservative boundary inside a previously read action sample; not a claim about the exact source montage transition.'
    num,den=map(int,c['sourceFrameRate'].split('/'))
    c.update(inSeconds=c['inFrameInclusive']*den/num,outSeconds=c['outFrameExclusive']*den/num,seconds=(c['outFrameExclusive']-c['inFrameInclusive'])*den/num,requiresNewBoundaryExtraction=i in updates,exactEdgeApproval=False)
    if i==4:c['visibleAction']='Pink corridor gunfire to dark stair room'
    if i==6:c['visibleAction']='Bathroom shot to upward purple-tentacle encounter'
    refined.append(c)
new={**bank,'schemaVersion':2,'preparedAt':stamp,'previousCandidateBank':rel(PROOF/'additional-action-bank-candidates-v1.json'),'clipCount':len(refined),'candidateSeconds':sum(c['seconds'] for c in refined),'clips':refined,'excluded':[dict(id='additional-18',reason=notes[17],approvedQuotaSeconds=0)],'allEdgesDirectlyRead':False,'crossSourceDuplicateSelectionApproved':False,'ratioApproved':False}
write(PROOF/'additional-action-bank-candidates-v2.json',new)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
ex={**item['additionalCutEdgeExecution'],'status':state['status'],'sessionId':95748,'alive':False,'actualExitObserved':True,'exitCode':0,'activeTasks':[],'directReview':rel(dest),'refinedBank':rel(PROOF/'additional-action-bank-candidates-v2.json')}
item.update(stage='all26-coarse-edges-read-13-refinements-pending',updatedAt=stamp,additionalCutEdgeExecution=ex,nextAction='Extract only13 changed candidate boundaries, directly read them, and compare all retained actions with the previous bank. Preserve current11PCM. Source duration, ratio, narration, render and upload not approved.')
q.update(updatedAt=stamp,lastProgressAt=stamp);write(qp,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','nextAction','additionalCutEdgeExecution']:d[k]=item[k]
    write(p,d)
print(json.dumps(dict(coarseBoardsRead=26,refinedCandidates=len(refined),changedBoundaries=len(updates),candidateSeconds=new['candidateSeconds'],allApproval=False)))
