"""Record actual direct text/native review; keep all approval gates distinct."""
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

dest=BASE/'current-whole-direct-review-v1.json'
assert not dest.exists(), 'Read existing review instead of overwriting/repeating it'
state=read(BASE/'current-whole-asr-execution-v1.json')
assert state['completed']==11 and state['exitCode']==0
asr=read(BASE/'current-whole-asr-v1/asr.json')
assert asr['complete'] and len(asr['results'])==11
notes={
 '01':'All4 paragraphs/49 words directly read. Complete question, ordered3games, promised distinctions and first-example bridge present. 맡는 recognized 맞는 at16.20–16.52; game-name spacing differs. Independent complete role/bridge and names contexts pending.',
 '02':'All4 paragraphs/57 words directly read. First-person direction, added kick, input-evidence caution and connection all present. 조준에 recognized 조준의 at9.18–9.54; complete addition context and final paragraph pending.',
 '03':'All4 paragraphs directly read, including new-user caveat and complete 합니다 ending. No substantive missing/repeated sentence or arbitrary greeting observed in whole result. Independent final paragraph pending.',
 '04':'All4 paragraphs directly read. 둘지뿐 recognized 둘짓뿐 at13.86–14.36; keep particle/pronunciation issue. Montage/continuous-encounter caveat and 않습니다 ending present. Complete last2paragraph context pending.',
 '05':'All4 paragraphs directly read, including contextual mapping/prompts and simultaneous-action test. No substantive missing/repeated sentence or greeting observed. Complete final paragraph pending.',
 '06':'All5 paragraphs directly read. 건브렐라 recognized 검브렐라 and 맡는 recognized 맞는. Final2sentences present; reported boundary29.12 then28.94 retreats0.18s; missing-ending timestamp warning retained. Independent complete first2paragraphs and final paragraph pending. Do not treat timestamp defect as actual PCM overlap or approve ending by heuristic.',
 '07':'All4 paragraphs directly read. Press/release versus continuous direction distinction and final selection-range instruction present. No substantive missing/repeated sentence or greeting observed. Independent final paragraph pending.',
 '08':'All5 paragraphs directly read. 페드로 recognized 패드로 at0.84–1.50. Whole content/device-evidence caution/final decision all present; boundary28.44 then28.04 retreats0.40s and missing-ending timestamp warning retained. Independent complete first paragraph and last2paragraphs pending; not an actual repeated PCM assertion.',
 '09':'All4 paragraphs directly read. All3hypothetical methods, different selection processes, combined-action test and decision preservation present. Spacing 지키는 데/지키는데 alone not semantic omission. Independent final paragraph pending.',
 '10':'All5 paragraphs directly read. Continuous segment, left/right then up/down aim, simultaneous test and fresh-path/no-repeat statement present. Boundary26.18 then26.04 retreats0.14s; complete last2paragraph context pending; no substantive repetition inferred.',
 '11':'All3 paragraphs directly read. 맡는 recognized 맞는 at2.58–2.78. Full remapping/device/function/final other-path conclusion present, without arbitrary greeting. Independent role and final-paragraph contexts pending.'
}
rows=[]
for r in asr['results']:
    m=next(x for x in state['audioInputs'] if x['scene']==r['scene'])
    assert sha(ROOT/m['path'])==r['audioSha256']==m['sha256']
    rows.append(dict(scene=r['scene'],audioSha256=r['audioSha256'],resultSha256=sha(BASE/'current-whole-asr-v1'/(r['scene']+'.json')),expectedKo=r['expectedKo'],actual=r['text'],wordCount=len(r['words']),allExpectedAndRecognizedWordsDirectlyRead=True,observation=notes[r['scene']],independentContextReviewed=False,approved=False))
write(dest,dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=stamp,sceneCount=11,paragraphCount=46,wholeDirectReview=True,asrSha256=sha(BASE/'current-whole-asr-v1/asr.json'),rows=rows,independentContextReview=False,asrApproved=False,narrationApproved=False,automaticApproval=False,humanWholeListening='pending',pronunciation='pending'))
ctx=[('01-role-tail','01',12.82,24.32,[2,3]),('01-game-names','01',5.44,13.08,[1]),('02-addition','02',5.08,11.06,[1]),('02-tail','02',17.12,23.44,[3]),('03-tail','03',18.22,24.64,[3]),('04-complete-tail','04',11.70,25.68,[2,3]),('05-tail','05',20.24,26.32,[3]),('06-name-role','06',0,12.72,[0,1]),('06-complete-tail','06',24.72,32.16,[4]),('07-tail','07',17.36,23.60,[3]),('08-name','08',0,6.40,[0]),('08-complete-tail','08',20.20,35.04,[3,4]),('09-tail','09',21.88,27.28,[3]),('10-complete-tail','10',19.48,33.20,[3,4]),('11-role','11',0,6.58,[0]),('11-tail','11',14.06,21.04,[2])]
contexts=[]
for cid,sid,a,b,paras in ctx:
    r=next(x for x in asr['results'] if x['scene']==sid)
    m=next(x for x in state['audioInputs'] if x['scene']==sid)
    contexts.append(dict(id=cid,scene=sid,startSample=round(a*24000),endSample=round(b*24000),sampleRate=24000,startSeconds=a,endSeconds=b,sourcePath=m['path'],sourceSha256=m['sha256'],expectedKo=[r['expectedKo'][i] for i in paras],boundaryBasis='Directly read current whole ASR word timestamps and complete sentence/paragraph pauses, plus current PCM sample limits; never TTS estimated paragraph timing',reviewed=False,approved=False))
write(BASE/'current-independent-context-plan-v1.json',dict(schemaVersion=1,slug='familiar-game-rules',createdAt=stamp,wholeReview=rel(dest),wholeReviewSha256=sha(dest),contexts=contexts,contextCount=16,expectedWasRecognizerPrompt=False,automaticApproval=False))
session=read(BASE/'current-whole-asr-execution-v1.session.json')
session.update(alive=False,exitObserved=True,exitCode=0,exitObservedAt=stamp,observedBy='Actual exec session99335 returned exit0; CIM matched53612/30688 absent after completion')
write(BASE/'current-whole-asr-execution-v1.session.json',session)
state.update(wholeDirectReview=True,directReview=rel(dest),alive=False,actualExitObserved=True,exitObservedAt=stamp)
write(BASE/'current-whole-asr-execution-v1.json',state)

native=read(PROOF/'additional-native-boards-v2.json')
assert native['boardCount']==39 and native['frameCount']==226
observations={
 'q8iWixSvfsI':'All18boards105native frames directly read.0–1.5rating;2–6train cinematic/creator promo;6.5–13dark corpse-room/stationary/publisher sequence;13.5–15ACTIONADVENTURE overlay excluded.15.515–18.018railcar jump/traverse;18.518–21.021street-to-upper-platform umbrella jump;21.521–22.523wire/forest glide;23.023–24.024laundry-roof traverse;24.525–26.026letterboxed firing at left target;26.526–27.027cult jump/fire;27.528–28.529industrial spill jump/fire;29.029–30.030cult airborne targets;30.531–33.033factory catwalk umbrella/fire/jump;33.533–34.535cage ride reserved, not passive filler;35.035–37.538dialogue excluded;38.038–39.039hanging container/wire above spikes;39.540–40.540vertical factory umbrella/fire;41.041–41.541eye encounter;42.042–43.043boar/speechbubble reserved;43.544–45blackwipe/WHEN;45.545–end title/release slate excluded. Cross-source wire/eye/cult/rail action overlap and letterbox crop must be reviewed before selecting exact edges. These approximate samples are not approved source duration.',
 'XbW4873OPZo':'All21boards121native frames directly read.0–2rating and2.5–15shoe-vault cinematic excluded.15.5–17door kick/pink room/ceiling targets;17.5green corridor fire;18electrical room/tentacles;18.5–19corridor kick/fire.19.5–21.5FlashKickers promo excluded.22–23escalator high/nearby targets and double-foot action;23.5–24.5crate/door kick and purple target.25–27FireFighters promo excluded.27.5room crossbow fire;28–29.5downward rocket/fire-grate/blast and upward target view;30–31.5fire hall kick/fire/crossbow.32–34Floaties promo excluded.34.5–36blasted room/floating targets with aim;36.5–37.5rooftop shield-target kick and upward movement.38–39UpperCutters promo excluded.39.5–40bathroom kick launches target upward;40.5–42corridor upper-target kick.42.5–43.5RageRunners promo excluded.44–46.5lobby door kick, corridor aim/fire/kick and explosion.47–48.5Thrusters promo excluded.49–50upper-platform traverse/kick;50.5–52stair/shaft ascent and shield group kick.52.5–54shoe-vault cinematic;54.5–end logos/release slates excluded. Aim/target changes directly visible; exact input, item effects/immunity and optimal strategy not inferred. All chosen cuts still require exact edge and cross-source review.'
}
for b in native['boards']:
    assert sha(ROOT/b['board'])==b['sha256']
    for f in b['tiles']:assert sha(ROOT/f['path'])==f['sha256']
    b.update(directlyRead=True,reviewedAt=stamp,observation=observations[b['sourceId']])
native.update(allDirectlyRead=True,reviewedAt=stamp,exactCutApproval=False)
write(PROOF/'additional-native-boards-v2.json',native)
write(PROOF/'additional-native-direct-review-v2.json',dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=stamp,boards=39,frames=226,allBoardsDirectlyRead=True,observations=observations,manifestSha256=sha(PROOF/'additional-native-boards-v2.json'),exactCutApproval=False,crossSourceDuplicateSelectionApproved=False,finalPixelApproval=False,sourceAudioUsed=False,imagesGitPolicy='local-only'))
extra=read(PROOF/'additional-source-execution-v2.json')
closed=read(PROOF/'additional-source-execution-v2.json.session.json')
assert closed['exitObserved'] and closed['exitCode']==0 and all(c['exitCode']==0 for c in extra['children'])
extra.update(alive=False,exitCode=0,actualExitObserved=True,sessionId=31781,all39BoardsDirectlyRead=True,nativeDirectReview=rel(PROOF/'additional-native-direct-review-v2.json'))
write(PROOF/'additional-source-execution-v2.json',extra)
candidates=read(ROOT/'projects/familiar-game-rules/sources/game-candidates.json')
for c in candidates['candidates']:
    if c.get('videoId') in observations:
        c.update(nativeReview=observations[c['videoId']],nativeDirectReview=rel(PROOF/'additional-native-direct-review-v2.json'),cutSelected=False,currentGameBindingOrDeviceClaimApproved=False)
write(ROOT/'projects/familiar-game-rules/sources/game-candidates.json',candidates)
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qpath)
item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(stage='current11-whole-direct-reviewed-awaiting16-independent-contexts-and-source-edges',updatedAt=stamp,wholeNarrationDirectReview=rel(dest),independentContextPlan=rel(BASE/'current-independent-context-plan-v1.json'),additionalSourceExpansionExecution={**item['additionalSourceExpansionExecution'],'alive':False,'exitCode':0,'actualExitObserved':True,'sessionId':31781,'all39BoardsDirectlyRead':True},nextAction='One CPU worker for16complete independent contexts; directly compare every whole/independent result and current PCM. Then precise additional source edges/cross-source comparison and further distinct source expansion if needed. Preserve all11PCM/147.2s explanation; no final ratio/pixel/audio approval yet.')
item['execution'].update(alive=False,exitCode=0,exitObserved=True,wholeDirectReview=True)
if 'narrationExecution' in item:item['narrationExecution'].update(alive=False,exitObserved=True,exitCode=0,sessionId=71573)
for h in item.get('executionHistory',[]):
    if h.get('pid')==35872:h.update(alive=False,exitObserved=True,exitCode=0,sessionId=71573)
write(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','execution','nextAction','wholeNarrationDirectReview','independentContextPlan','additionalSourceExpansionExecution']:d[k]=item[k]
    write(p,d)
print(json.dumps(dict(wholeScenesRead=11,contextPlan=16,nativeBoardsRead=39,nativeFramesRead=226,audioApproval=False,cutApproval=False)))
