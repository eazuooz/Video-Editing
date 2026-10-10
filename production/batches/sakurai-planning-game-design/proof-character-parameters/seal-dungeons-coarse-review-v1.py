"""Seal all193 directly read official-source samples, without adopting cuts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT=Path(__file__).resolve().parents[4]
PROOF=Path(__file__).resolve().parent
STATE=PROOF/'dungeons-source-execution-v2.json'
TARGET=PROOF/'dungeons-coarse-direct-review-v1.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
if TARGET.exists():raise SystemExit('Completed review exists; do not repeat.')
d=json.loads(STATE.read_text(encoding='utf-8-sig'))
assert d['totalSamples']==193 and d['totalBoards']==33 and d['wholeDecodeExitCode']==0
assert all(c['exitCode']==0 for c in d['children'])
assert sha(ROOT/d['source']['localPath'])==d['source']['sha256']
for s in d['samples']:assert sha(ROOT/s['path'])==s['sha256'] and s['pts']==s['nativeFrame']*256
notes=[
'0–2.5s: Nintendo/Aether logos; excluded from actual-game time.',
'3–5.5s: publisher/music-credit cards; excluded, source music not used.',
'6–8.5s: music credit and Steam praise promotional text; excluded.',
'9–11.5s: promotional text followed by Fleet moving through a mine room10–11.5; map movement not a combat-stat example.',
'12–14.5s: exploration, black transition, room, Fleet dialogue. Held; not combat quota.',
'15–17.5s: Kohler dialogue, black transition, map/swimming; held.',
'18–20.5s: map movement then black and NPC inventory interaction. Not core combat example.',
'21–23.5s: NPC thirst, Potion of Might tooltip, Give selection; unrelated item exchange excluded.',
'24–26.5s: Give and Bless you exchange; excluded.',
'27–29.5s: thank-you promotion then Slade battle with frog from28.5. STEAL animation and coin count111 visible; exact start/end and cause need native review.',
'30–32.5s: Slade aftermath with enemy−2HP, black30.5; Hamir battle31–32.5. REACT tooltip says1DMG and instantly+3DEF on connect. Initial Hamir ATK5/DEF3/ACC2/SPD4/STA7 against6/4/5/2/1; these are the displayed draft state, not universal base stats.',
'33–35.5s: Hamir gains3DEF to6, following attack is BLOCKED with+1STA; new draft state34.5; black35; Artemis STUN against Lava Digger35.5.',
'36–38.5s: Artemis STUN strike−1HP, text about discarding opponent dice, opposing ATK8 becomes3; subsequent STRONG attack blocked with+5 displayed. No health regeneration demonstrated.',
'39–41.5s: Artemis aftermath and next dice pool39.5, black40; Fleet SNIPE starts40.5. Exact tooltip and action require native review.',
'42–44.5s: Fleet SNIPE hit−1HP and two+3STA indicators, transition43 then announcement text. Not a numerical base-stat comparison.',
'45–47.5s: Fleet map movement then journal menu. Journal excluded.',
'48–50.5s: journal followed by Hamir key use and opening gate. Not selected combat quota.',
'51–53.5s: map, black51.5, Hamir NPC geode interaction and tooltip; held.',
'54–56.5s: geode Give/quest dialogue then black; excluded.',
'57–59.5s: Slade map and dialogue portrait; excluded.',
'60–62.5s: Slade dialogue about Drop of Nourishment; excluded.',
'63–65.5s: dialogue and fade; excluded.',
'66–68.5s: quest-complete map animation then Switch announcement; excluded.',
'69–71.5s: Switch promotional text; excluded.',
'72–74.5s: Hamir/Digger dialogue over battle; excluded.',
'75–77.5s: transition then Fleet STRIKE tooltip1DMG, battle versus Foreman Kohler, attack−1HP. Action is a different shot from the earlier SNIPE.',
'78–80.5s: boss falls then result idle and dialogue. Do not use aftermath/dialogue to fill quota.',
'81–83.5s: Kohler/Fleet dialogue; excluded.',
'84–86.5s: dialogue/fade then rapid Fleet/Slade/Hamir attack montage. Earlier Slade shot reappears, and fleeting new QUAKE shot is too brief for an inferred continuous cause.',
'87–89.5s: repeated Artemis STUN, four-way inset montage, fade, release card. Exclude repeated shots/inset/promotion.',
'90–92.5s: April6 Nintendo Switch release card; historical2023 promotion, excluded.',
'93–95.5s: release card fading to black; excluded.',
'95.75s: final native frame5745 black; excluded.'
]
boards=[]
for b,n in zip(d['boards'],notes):
 assert sha(ROOT/b['path'])==b['sha256']
 boards.append({**b,'directlyRead':True,'observations':n})
r={'schemaVersion':1,'slug':'character-parameters','recordedAt':stamp(),'executionState':str(STATE.relative_to(ROOT)).replace('\\','/'),'executionSha256':sha(STATE),'actualOuterSessionId':3660,'actualOuterExitCode':0,'outerExitObservation':'write_stdin returned actual exit0; session is already closed, not polled again.','source':d['source'],'nativeVideo':d['video'],'wholeDecodeExitCode':0,'samples':d['samples'],'boards':boards,'totalSamplesDirectlyRead':193,'totalBoardsDirectlyRead':33,'coarseSamplePixelReviewApproved':True,'allNativeFramesReviewed':False,'wholeContinuousViewingOrListeningApproved':False,'exactInOutApproved':False,'sourceAdoptionApproved':False,'finalCueUiApproved':False,'newScriptTtsOrRender':False,'humanListeningApproved':False,'publicRightsApproved':False,'sourceAudioUse':False,'loopOrSlowdownUse':False,'rasterGitAdditions':0,'rights':{'primaryUrl':'https://aetherstudios.com/press-releases/','directlyRead':True,'observedScope':'Aether games content may be broadcast for commercial or noncommercial purposes and monetized.','sourceOwner':'Aether Studios','attributionRequirementObserved':False,'finalHumanRightsReviewPending':True},'primaryConcepts':{'url':'https://dungeonsofaether.com/','directlyRead':True,'observedOfficialEmbed':'https://www.youtube.com/embed/a8nwpiCqyTQ','diceDraftPoolPerTurn':True,'fleet':'jack of all trades; learning baseline','hamir':'sturdy, weather blows and wait to strike','slade':'dodges attacks when speed is sufficiently high','artemis':'heals wounds through regeneration; not demonstrated by selected trailer samples'},'actualYouTubeObservation':{'tabId':'148','url':d['sourceUrl'],'title':d['source']['title'],'channel':'Aether Studios @RivalsofAetherOfficial','publishedLocalDate':'2023-04-01','visibilityObserved':'unlisted','expandedDescription':'Get ready to brave the mines below Julesvale on the go when Dungeons of Aether releases on Switch! Available April6th on the Nintendo Store.','pausedTimeSeconds':28.057675,'muted':True,'durationSeconds':95.781},'limitations':['Five brief combat sequences are candidates only; establish exact native boundaries before adoption.','Do not claim montage shots are one continuous battle or optimal strategy.','Draft values are temporary states, not permanent base character statistics.','Promotion, dialogue, inventory, journal, map idle, result and repeated montage are excluded from actual gameplay quota.'],'nextAction':'Review exact native combat windows and fixed-caption-safe framing alongside Rivals clips/match.'}
TARGET.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sp=STATE.with_name(STATE.name+'.session.json')
before=sp.read_bytes();s=json.loads(before)
assert s['pid']==46436 and s['sessionId']==3660
s.update(outerExitCode=0,exitObservation=r['outerExitObservation'],exitRecordedAt=stamp())
assert sp.read_bytes()==before
sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';before=qpath.read_bytes();q=json.loads(before)
item=next(x for x in q['items'] if x['slug']=='character-parameters')
assert not item.get('videoId') and not any(item['checkpoints'].values())
item.update(stage='official-source-native-action-and-framing-review-pending',updatedAt=stamp())
item['sourcePreflightReview']={'rivalsReview':'production/batches/sakurai-planning-game-design/proof-character-parameters/official-coarse-direct-review-v1.json','dungeonsReview':str(TARGET.relative_to(ROOT)).replace('\\','/'),'sources':8,'samplesDirectlyRead':479,'boardsDirectlyRead':83,'coarseApproved':True,'nativeActionAdoptionApproved':False}
item['execution']={'status':'completed','phase':'official-source-coarse-review','pid':46436,'processCreateTime':d['processCreateTime'],'sessionId':3660,'outerExitCode':0,'state':str(STATE.relative_to(ROOT)).replace('\\','/'),'cpuThreads':2,'gpuJobs':0}
item['nextAction']=r['nextAction'];q['updatedAt']=q['lastProgressAt']=stamp()
assert qpath.read_bytes()==before
tmp=qpath.with_name(qpath.name+f'.{os.getpid()}.tmp');tmp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,qpath)
print(json.dumps({'sealed':str(TARGET),'samples':193,'boards':33,'nativeAdoption':False,'queueUpdated':True}))
