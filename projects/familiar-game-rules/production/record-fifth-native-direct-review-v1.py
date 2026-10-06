"""Record the directly read Hype Train samples; exact cuts stay pending."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=datetime.now(timezone.utc).isoformat()
def write(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing')
    t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
dest=PROOF/'additional-native-direct-review-v5.json'
assert not dest.exists(),'Preserve completed review'
state=read(PROOF/'additional-source-execution-v5.json')
assert state['pid']==2688 and all(c['exitCode']==0 for c in state['children'])
session=read(PROOF/'additional-source-execution-v5.json.session.json')
assert session['pid']==2688 and session['sessionId']==37507
native=read(PROOF/'additional-native-boards-v5.json')
assert native['boardCount']==26 and native['frameCount']==152
notes=[
 {'seconds':'0–6','observation':'Rating, dark introduction and white flash. Exclude.'},
 {'seconds':'6.5–8.5','observation':'Close train-car firing with angled source camera and blood/head impact. Actual gameplay, but omit this opening close impact from proposed editorial selection. No normal input-binding claim.'},
 {'seconds':'9–20.5','observation':'Run through train doors, jump and fire over crates, explosion and airborne kick. Relevant body movement and aiming, no keyboard/controller demonstration.'},
 {'seconds':'21–29.5','observation':'Shoot right then airborne left/right gun directions at24.5; land on crates, face left and fire, advance into an open car.'},
 {'seconds':'30–38.5','observation':'Airborne aiming at targets on several crate heights, explosions, climb and move onto the car roof.'},
 {'seconds':'39–50.5','observation':'Jump over roof and aim at targets below on both sides, then advance across another open car. Source camera tilt/slow-motion belongs to original footage; no artificial retiming is authorized.'},
 {'seconds':'51–61','observation':'Roof jump, land in car and fire left/right; closer head-impact frames around55 require editorial consideration. Exact start/end and full-screen crop remain unapproved.'},
 {'seconds':'61.5–75.5','observation':'Game view shrinks into a TV, animated banana, release calendar and platform slate. Exclude entire TV/promotion section from actual-game quota.'},
]
for b in native['boards']:
    assert sha(ROOT/b['board'])==b['sha256']
    for f in b['tiles']:assert sha(ROOT/f['path'])==f['sha256']
    b.update(directlyRead=True,reviewedAt=stamp)
native.update(allDirectlyRead=True,reviewedAt=stamp,exactCutApproval=False)
write(PROOF/'additional-native-boards-v5.json',native)
write(dest,dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=stamp,boards=26,frames=152,allBoardsDirectlyRead=True,sampleIntervalSeconds=.5,observations=notes,manifestSha256=sha(PROOF/'additional-native-boards-v5.json'),decision='new-train-action-candidate-exact-edges-and-framing-pending',newQuotaSecondsApproved=0,exactCutApproval=False,crossSourceDuplicateSelectionApproved=False,finalPixelApproval=False,sourceAudioUsed=False,imagesGitPolicy='local-only'))
session.update(alive=False,exitObserved=True,exitCode=0,closedAt=stamp,closureEvidence='Unified exec session37507 returned exit0; subsequent CIM check found parent2688 and download40340/full-decode55148/native46924 absent. Command/creation identity preserved.')
write(PROOF/'additional-source-execution-v5.json.session.json',session)
state.update(status='closed-all26-native-boards-read-exact-edges-pending',alive=False,exitCode=0,actualExitObserved=True,sessionId=37507,all26BoardsDirectlyRead=True,nativeDirectReview=rel(dest),newQuotaSecondsApproved=0,updatedAt=stamp)
write(PROOF/'additional-source-execution-v5.json',state)
cp=ROOT/'projects/familiar-game-rules/sources/game-candidates.json';candidates=read(cp)
source={k:v for k,v in state['results'][0].items() if k!='nativeFrames'}
assert not any(c.get('videoId')==source['videoId'] for c in candidates['candidates'])
candidates['candidates'].append({**source,'game':'My Friend Pedro','officialEvidence':rel(PROOF/'official-pedro-hype-train-watch.ax.txt'),'permissionEvidence':rel(PROOF/'devolver-yamyamcoding-permission-full-v2.ax.txt'),'permission':'Directly read personalized DevolverDigital commercial video/broadcast permission, including My Friend Pedro; final public rights pending.','nativeReview':notes,'nativeDirectReview':rel(dest),'selectedForAcquisition':True,'cutSelected':False,'exactCutApproval':False,'newQuotaSecondsApproved':0,'sourceAudioUsed':False})
candidates['rejected'].append({'videoId':'zaPBAKg3VT4','game':'My Friend Pedro','decision':'Public watch page requires adult phone verification; reserve without downloading or bypassing.','evidence':rel(PROOF/'official-pedro-bananas-age-limit.ax.txt'),'selectedForAcquisition':False,'newQuotaSecondsApproved':0})
candidates.update(additionalFifthNativeReview=rel(dest),updatedAt=stamp);write(cp,candidates)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
ex={**item['additionalSourceFifthExpansionExecution'],'status':state['status'],'alive':False,'actualExitObserved':True,'exitCode':0,'activeTasks':[],'nativeDirectReview':rel(dest)}
item.update(stage=state['status'],updatedAt=stamp,additionalSourceFifthExpansionExecution=ex,nextAction='Compare21 refined additions against37 old actions; extract only new Hype Train boundaries and full-screen framing candidates. Preserve current11PCM and147.2s white explanation. No narration, ratio, render or upload approval.')
q.update(updatedAt=stamp,lastProgressAt=stamp);write(qp,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','nextAction','additionalSourceFifthExpansionExecution']:d[k]=item[k]
    write(p,d)
print(json.dumps(dict(boardsRead=26,nativeFramesRead=152,parentExit0Observed=True,newQuotaSecondsApproved=0)))
