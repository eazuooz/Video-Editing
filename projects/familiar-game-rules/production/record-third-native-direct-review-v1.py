"""Record the 15 boards actually read; do not promote source capacity or audio gates."""
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

dest=PROOF/'additional-native-direct-review-v3.json'
assert not dest.exists(), 'Read existing completed review instead of repeating it'
closed=read(PROOF/'additional-source-execution-v3.json.session.json')
assert closed['exitObserved'] and closed['exitCode']==0
state=read(PROOF/'additional-source-execution-v3.json')
assert all(c['exitCode']==0 for c in state['children'])
native=read(PROOF/'additional-native-boards-v3.json')
assert native['boardCount']==15 and native['frameCount']==85
observation=('All15boards85 one-second native samples directly read. Exclude0–1 rating;2–5 large Facts/Gunbrella logo;6–7 creator-promo lower overlay;14–17 NPC dialogue;33–34 sepia/letterboxed story;44–46 stationary/automatic transport;47–48 area/promo overlay;49–51 dialogue;62–63 NPC dialogue;68–72 sepia house passage held for unclear concept connection;73–end title/release slate. '
 '8–9 rail-side traversal,10 city roof,11–12 rainy wall/umbrella ascent,13 cult-platform jump are candidate actions.18–19 swamp water leap likely repeats Day;20–21 roof umbrella likely repeats Reveal;22–25 junkyard and26–27 twin turrets likely repeat Multitool;28–30 beast likely repeats Day;31–32 articulated turret likely repeats Multitool;35 library and36–37 eye boss likely repeat Day. '
 '38–39 wire/container/spikes may repeat Reveal;40–41 cult airborne firing,42–43 letterboxed city dash need exact comparisons/crop;52–53 stationary firing held, not quota filler;54–57 library lower-floor jump/fire/traverse may extend or repeat Day;58 swamp/electrical airborne target,59–61 container walk/fire/jump,64–67 city wall umbrella/attack/roof are unapproved candidates. '
 'Native samples prove observed frames only. No exact edit edges, repeated-action removal, source duration, current input mapping, item efficacy, immunity or strategy approval.')
for b in native['boards']:
    assert sha(ROOT/b['board'])==b['sha256']
    for f in b['tiles']:assert sha(ROOT/f['path'])==f['sha256']
    b.update(directlyRead=True,reviewedAt=stamp)
native.update(allDirectlyRead=True,reviewedAt=stamp,exactCutApproval=False)
write(PROOF/'additional-native-boards-v3.json',native)
write(dest,dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=stamp,boards=15,frames=85,allBoardsDirectlyRead=True,sampleIntervalSeconds=1,observation=observation,manifestSha256=sha(PROOF/'additional-native-boards-v3.json'),exactCutApproval=False,crossSourceDuplicateSelectionApproved=False,finalPixelApproval=False,sourceAudioUsed=False,imagesGitPolicy='local-only'))
state.update(alive=False,exitCode=0,actualExitObserved=True,sessionId=13494,all15BoardsDirectlyRead=True,nativeDirectReview=rel(dest))
write(PROOF/'additional-source-execution-v3.json',state)
cpath=ROOT/'projects/familiar-game-rules/sources/game-candidates.json';candidates=read(cpath)
for version in [2,3]:
    pre=read(PROOF/f'source-expansion-preflight-v{version}.json')
    execution=read(PROOF/f'additional-source-execution-v{version}.json')
    direct=read(PROOF/f'additional-native-direct-review-v{version}.json')
    for src in pre['sources']:
        sid=src.get('videoId',src.get('id'))
        matching=[c for c in candidates['candidates'] if c.get('videoId')==sid]
        if matching:c=matching[0]
        else:c={**src,'videoId':sid};candidates['candidates'].append(c)
        media=next(x for x in execution['results'] if x['videoId']==sid)
        c.update(actualDownload=media,nativeReview=direct.get('observations',{}).get(sid,direct.get('observation')),nativeDirectReview=rel(PROOF/f'additional-native-direct-review-v{version}.json'),cutSelected=False,exactCutApproval=False,currentGameBindingOrDeviceClaimApproved=False,sourceAudioUsed=False)
candidates.update(newNarrationCreated=True,independentAuthoringReview='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/script-and-opening-direct-review-v1.json',additionalThirdNativeReview=rel(dest),updatedAt=stamp)
write(cpath,candidates)
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qpath)
item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(stage='current11-plus16-direct-reviewed-additional-v3-native-read-edges-pending',updatedAt=stamp,additionalSourceThirdExpansionExecution={**item['additionalSourceThirdExpansionExecution'],'alive':False,'exitCode':0,'actualExitObserved':True,'sessionId':13494,'all15BoardsDirectlyRead':True,'nativeDirectReview':rel(dest)},nextAction='Cross-source exact action/edge selection and further distinct official action if capacity remains short. Preserve all11currentPCM and147.2s white explanation. Whole11+independent16 structural read complete; ASR/narration approval false with phonetic/particle review pending. No final timing/render/upload approval.')
write(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','nextAction','additionalSourceThirdExpansionExecution']:d[k]=item[k]
    write(p,d)
print(json.dumps(dict(boardsRead=15,nativeFramesRead=85,parentExit0Observed=True,sourceEdgesApproved=False,audioApproved=False)))
