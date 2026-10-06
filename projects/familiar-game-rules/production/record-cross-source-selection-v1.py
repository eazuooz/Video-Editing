"""Lock the boards actually read and conservative editorial selections."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os, time, copy
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
dest=PROOF/'cross-source-selection-direct-review-v1.json'
assert not dest.exists(),'Preserve completed review'
comparison=read(PROOF/'cross-source-comparison-v1.json')
assert len(comparison['boards'])==22
notes={
1:'Corridor/door into pink hall with pistol, different from the old pizza/crossbow encounters.',
2:'Purple floating-brain hall, pink bathroom and window kick; retains a different action sequence.',
3:'Ascending escalator aim and explosion; distinct from the descending kick in additional09.',
4:'Pink shotgun corridor into dark stairs, distinct from the old selected rooms.',
5:'Dark door into green bathroom gunfire; keep this version and omit the repeated encounter variant08.',
6:'Close bathroom into purple stair ascent and aim; short active connector, no idle quota.',
7:'Classroom minigun and upward kick. Reread old Anger boards10/11: old minigun is in disco/living rooms, different from this classroom.',
8:'Editorial omission: pink door/green bathroom/pink hall repeats selected01/05 encounters with shoe/camera variants. No exact-pixel duplicate assertion.',
9:'Descending escalator feet/kick against a metal door, different action from additional03 ascent.',
10:'Flaming crossbow room and upward kick, different from old pizza/roof actions.',
11:'Purple floating-target hall fire into angled roof kick. Old06 uses a crossbow from a lower ledge at the water building; different action despite a related setting.',
12:'Editorial omission: bathroom-to-classroom upward kick repeats the selected07 classroom encounter with a variant camera/phase.',
13:'Purple lobby kick into tan checkered hall pistol/explosion; different selected action.',
16:'City market ground fire and umbrella movement toward roof/wire, distinct from the old cult rope pit.',
17:'Forest wire/parry-like visual effect into laundry roof with an enemy. Describe visible effects only; no unshown input binding.',
19:'Editorial omission after rereading old Gun boards07–10: cult jump into factory platform fight repeats retained old13 encounter phases. Trailer presentation can differ; no exact-pixel duplicate assertion.',
20:'Editorial omission after old Gun boards07–10 reread: factory floor/lift encounter repeats old13/14 in another phase.',
21:'Editorial omission: container/lift into eye sequence reuses the old17/18 eye encounter. Exclude whole candidate for freshness.',
22:'Train/mechanical rails, circular market machine fight and rainy roof umbrella movement; distinct from the old factory/eye encounters.',
23:'Keep only rainy-container overhead wire movement38–39.5s; remove subsequent cult-rope action because old13 already covers that encounter. New trim boundaries remain pending.',
24:'Editorial omission after old Gun boards12–14 reread: library floor/bookcase fight repeats the retained library encounter even though phases differ. Do not use its later swamp tail to fill quota.',
25:'Swamp airborne cult attack into rainy-container ground left/right aiming. Container ground action differs from retained23 overhead wire movement.',
}
omit={8,12,19,20,21,24}
decisions=[]
for b in comparison['boards']:
    n=int(b['actionId'].split('-')[-1]);assert n in notes
    assert sha(ROOT/b['board'])==b['sha256']
    for r in b['rows']:
        for t in r['tiles']:assert sha(ROOT/t['path'])==t['sha256']
    b.update(directlyRead=True,reviewedAt=stamp,editorialObservation=notes[n])
    decisions.append(dict(actionId=b['actionId'],decision='omit-editorial-repeated-encounter-variant' if n in omit else ('trim-new-boundaries-pending' if n==23 else 'retain-distinct-visible-action'),observation=notes[n]))
comparison.update(allDirectlyRead=True,reviewedAt=stamp,directReview=rel(dest),automatedScoreRole='Navigation only; direct source/body/action comparison decides selection. No exact-pixel or input inference.',crossSourceDuplicateSelectionApproved=True,finalCutAndCaptionApproval=False)
write(PROOF/'cross-source-comparison-v1.json',comparison)
reread=[]
for sid,nums in [('7kJo0miz08g',[10,11]),('zdqK0zC53CE',[7,8,9,10,12,13,14]),('YIVtT7SJrMM',[16,17])]:
    for n in nums:
        p=ROOT/f'shared/output/familiar-game-rules/research/native-v1/boards/{sid}-{n:02}.jpg'
        assert p.is_file();reread.append(dict(path=rel(p),sha256=sha(p),directlyReread=True,reviewedAt=stamp))
old=read(PROOF/'source-action-bank-v2.json');add=read(PROOF/'additional-action-bank-candidates-v2.json')
eligible=[c for c in add['clips'] if c['exactEdgeApproval']]
assert len(add['clips'])==25 and len(eligible)==22
retained=[];excluded=[]
for c0 in add['clips']:
    c=copy.deepcopy(c0);n=int(c['id'].split('-')[-1])
    if not c['exactEdgeApproval'] or n in omit:
        c.update(selectedForExpandedBank=False,countsTowardSelectedActualSeconds=False,selectionObservation=notes.get(n,'Reserved/non-action boundary remains excluded.'))
        excluded.append(c);continue
    c.update(crossSourceDuplicateSelectionApproved=True,selectionObservation=notes[n],selectedForExpandedBank=True,finalCutAndCaptionApproval=False)
    if n==23:
        c.update(previousOutFrameExclusive=c['outFrameExclusive'],outFrameExclusive=1185,outSeconds=39.5,seconds=1.5,exactEdgeApproval=False,requiresNewBoundaryExtraction=True,previousEdgeBoard=c.get('edgeBoard'))
    else:c['requiresNewBoundaryExtraction']=False
    retained.append(c)
assert len(retained)==16
hype=[]
for n,(start,end) in enumerate([(540,900),(900,1260),(1260,1620),(1620,1980),(1980,2340),(2340,2700),(2700,3060),(3060,3270),(3420,3660)],1):
    hype.append(dict(id=f'hype-{n:02}',sourceVideoId='q-AsYZCdpts',sourcePath='shared/output/familiar-game-rules/research/game-sources/q-AsYZCdpts.mp4',sourceSha256='69fb64174cf9981007f15d96cf9371fadee830602c35d566354c2eb1d6889327',sourceFrameRate='60/1',inFrameInclusive=start,outFrameExclusive=end,inSeconds=start/60,outSeconds=end/60,seconds=(end-start)/60,visibleAction='Train/crate/roof movement with independent left/right aiming and firing; exact source edges pending.',planningSection='03-function',viewerFocus='Track the body travel and one/two gun aim directions separately; do not infer keyboard/controller inputs.',diagramConnection='Action-to-input assignment differs from preserving an aiming function when the device changes.',insertionPosition='03-function between retained explanations',classification='candidate-existing-game-action',sourceAudio=False,loop=False,editorSlowdown=False,exactEdgeApproval=False,crossSourceDuplicateSelectionApproved=True,selectionObservation='Direct26 native boards and old Pedro16/17 reread: new open train/crate human-combat actions differ from old closed train boss encounter.',finalCutAndCaptionApproval=False,requiresNewBoundaryExtraction=True))
def seconds(c):
    num,den=map(int,c['sourceFrameRate'].split('/'));return (c['outFrameExclusive']-c['inFrameInclusive'])*den/num
bank=dict(schemaVersion=3,slug='familiar-game-rules',preparedAt=stamp,status='expanded-source-selection-reviewed-new-boundaries-pending',previousBank=rel(PROOF/'source-action-bank-v2.json'),additionalCandidateBank=rel(PROOF/'additional-action-bank-candidates-v2.json'),crossSourceReview=rel(dest),clips=old['clips']+retained+hype,excluded=old['excluded']+excluded,originalSelectedClipCount=37,refinedCandidateCountCorrection=dict(actualCandidates=25,actualEdgeApproved=22,previousTextCount21WasIncorrect=True),retainedAdditionalClipCount=16,newHypeClipCount=9,newBoundariesPending=10,clipCount=62,candidateSeconds=sum(map(seconds,old['clips']+retained+hype)),oldSeconds=sum(map(seconds,old['clips'])),additionalSeconds=sum(map(seconds,retained)),hypeSeconds=sum(map(seconds,hype)),allEdgesDirectlyRead=False,sourceAudioUsed=False,selfCreatedGameExamples=0,ratioApproved=False,fullScreenFramingApproved=False,finalCutAndCaptionApproval=False,imagesGitPolicy='local-only')
write(PROOF/'source-action-bank-v3.json',bank)
write(dest,dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=stamp,comparisonBoards=22,comparisonTiles=198,allComparisonBoardsDirectlyRead=True,additionalOldBoardsDirectlyReread=reread,decisions=decisions,editorialOmissions=6,retainedAdditionalCandidates=16,trimmedCandidate='additional-23:38–39.5s',newHypeCandidates=9,exactPixelDuplicateClaim=False,inputBindingInferred=False,newBoundaryApproval=False,fullScreenFramingApproved=False,finalCutAndCaptionApproval=False,ratioApproved=False,narrationApproved=False,imagesGitPolicy='local-only',expandedBank=rel(PROOF/'source-action-bank-v3.json'),expandedBankSha256=sha(PROOF/'source-action-bank-v3.json')))
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(stage=bank['status'],updatedAt=stamp,crossSourceSelection=dict(directReview=rel(dest),candidateBank=rel(PROOF/'source-action-bank-v3.json'),all22ComparisonBoardsDirectlyRead=True,all11TargetedOldBoardsDirectlyReread=True,retainedAdditionalCandidates=16,editorialOmissions=6,newHypeCandidates=9,newBoundariesPending=10,candidateSeconds=bank['candidateSeconds'],ratioApproved=False,finalPixelApproval=False),nextAction='Extract only9 Hype Train candidate boundaries and1 trimmed rainy-container interval; directly read10 new boards, then full-screen/caption framing. Preserve current11PCM and147.2s white explanation; final timing/narration/render/private remain unapproved.')
q.update(updatedAt=stamp,lastProgressAt=stamp);write(qp,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','crossSourceSelection','nextAction']:d[k]=item[k]
    write(p,d)
print(json.dumps({k:bank[k] for k in ['clipCount','oldSeconds','additionalSeconds','hypeSeconds','candidateSeconds','newBoundariesPending']}))
