"""Lock the 26 directly read Code Yellow boards without approving quota filler."""
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
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(tmp,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
dest=PROOF/'additional-native-direct-review-v4.json'
assert not dest.exists(), 'Preserve completed review'
closed=read(PROOF/'additional-source-execution-v4.json.session.json')
assert closed['exitObserved'] and closed['exitCode']==0
state=read(PROOF/'additional-source-execution-v4.json')
assert all(c['exitCode']==0 for c in state['children'])
native=read(PROOF/'additional-native-boards-v4.json')
assert native['boardCount']==26 and native['frameCount']==153
notes=[
    {'seconds':'0–11.5','observation':'Rating, animated banana/TV introduction, static and Code Yellow logo; excluded.'},
    {'seconds':'12–20.5','observation':'Hook/shaft rotation, cinematic-camera promotion, banana overlay and window firing. Same shaft route appears in Full Throttle; no new ordinary-control capacity approval.'},
    {'seconds':'21–31.5','observation':'Big-head and tiny-player modifications; repeated shaft route and large bottom banners. Excluded from this ordinary-control narration.'},
    {'seconds':'32–46.5','observation':'Adjustable focus speed then adjustable player speed in shaft and blue-bar rooms, with promotional labels. Excluded from ordinary-action quota rather than counting intentionally altered action speed.'},
    {'seconds':'47–54.5','observation':'City stair route, radial weapon menu at49/49.5 and51/51.5, Unlock All Weapons plus Adjustable Focus Speed promotion. Menu is visible but this does not establish normal input bindings or selection availability; research-only.'},
    {'seconds':'55–58.5','observation':'Tiny player plus big head in sewer chamber and repeated close targets; modifier banners. Excluded.'},
    {'seconds':'59–65','observation':'Cinematic camera skateboard upward fire then hook-side room firing; changed viewpoint does not prove a new route and has no exact source/crop approval.'},
    {'seconds':'65.5–76','observation':'Static price/platform/update release slate through75.5 then static transition; excluded.'},
]
for b in native['boards']:
    assert sha(ROOT/b['board'])==b['sha256']
    for f in b['tiles']:assert sha(ROOT/f['path'])==f['sha256']
    b.update(directlyRead=True,reviewedAt=stamp)
native.update(allDirectlyRead=True,reviewedAt=stamp,exactCutApproval=False)
write(PROOF/'additional-native-boards-v4.json',native)
write(dest,dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=stamp,boards=26,frames=153,allBoardsDirectlyRead=True,sampleIntervalSeconds=.5,observations=notes,manifestSha256=sha(PROOF/'additional-native-boards-v4.json'),decision='research-only-modifier-promotional-and-repeated-actions',newQuotaSecondsApproved=0,exactCutApproval=False,crossSourceDuplicateSelectionApproved=False,finalPixelApproval=False,sourceAudioUsed=False,imagesGitPolicy='local-only'))
state.update(status='closed-native-direct-review-complete-research-only',alive=False,exitCode=0,actualExitObserved=True,sessionId=80852,all26BoardsDirectlyRead=True,nativeDirectReview=rel(dest),newQuotaSecondsApproved=0)
write(PROOF/'additional-source-execution-v4.json',state)
cpath=ROOT/'projects/familiar-game-rules/sources/game-candidates.json';candidates=read(cpath)
src=read(PROOF/'source-expansion-preflight-v4.json')['sources'][0]
existing=next((c for c in candidates['candidates'] if c.get('videoId')==src['videoId']),None)
if existing is None:existing={**src};candidates['candidates'].append(existing)
existing.update(actualDownload=state['results'][0],nativeReview=notes,nativeDirectReview=rel(dest),cutSelected=False,exactCutApproval=False,newQuotaSecondsApproved=0,selectionDecision='research-only-modifier-promotional-and-repeated-actions',sourceAudioUsed=False)
candidates.update(additionalFourthNativeReview=rel(dest),updatedAt=stamp);write(cpath,candidates)
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qpath)
item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(stage='current11-plus16-reviewed-all-additional-native-read-exact-edges-pending',updatedAt=stamp,additionalSourceFourthExpansionExecution=state,nextAction='Review exact boundaries and cross-source repeated actions from the already acquired Anger Foot/Gunbrella candidates. Code Yellow contributes0approved seconds. Preserve current11PCM and147.2s useful white explanation; no render, ratio, narration or upload approval.')
q.update(updatedAt=stamp,lastProgressAt=stamp);write(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','nextAction','additionalSourceFourthExpansionExecution']:d[k]=item[k]
    write(p,d)
print(json.dumps(dict(boardsRead=26,nativeFramesRead=153,parentExit0Observed=True,newQuotaSecondsApproved=0)))
