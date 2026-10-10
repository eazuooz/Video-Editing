"""Adopt only the reviewed native action bank for independent editorial planning."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
put=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=P/'source-action-bank-v1.json'
assert not out.exists(),'Preserve completed adoption; inspect it instead.'
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
b=read(P/'trim-boundary-direct-review-v4.json');n=read(P/'native-trial-direct-review-v3.json')
assert b['allBoundaryBoardsDirectlyRead'] and b['allBoundaryHashesMatch']
layout=read(P/'fullscreen-ui-direct-review-v5.json');assert layout['sampleFullscreenLayoutApproved']
play=read(P/'native-playback-observation-v1.json');assert play['actualStartEvents']==19 and play['actualEndEvents']==18
plan=read(P/'native-trim-plan-v4.json');assert plan['nativeExactSelectionApproved']
native=read(P/'native-action-execution-v2.json'); sources=[]
for s in native['sources']:
 assert sha(ROOT/s['sourcePath'])==s['sourceSha256']
 sources.append({k:s[k] for k in ['sourceKey','sourcePath','sourceSha256','nativeVideo','nativePtsPath']})
recentFiles=sorted(set([*ROOT.glob('projects/*/project.json'),*ROOT.glob('projects/*/sources/*.json'),*ROOT.glob('projects/*/sources/*.md')]))
patterns=['rivals of aether','dungeons of aether','gbbkfyzyvbc','a8nwpicqytq','zetterburn','forsburn']
hits=[]
for p in recentFiles:
 text=p.read_text(encoding='utf-8-sig').lower()
 found=[x for x in patterns if x in text]
 if found:hits.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'matches':found})
rights=read(P/'dungeons-coarse-direct-review-v1.json')['rights']
links={
 'zetterburn-gameplay1':('03-rule-not-scale','Burning effect','Persistent state versus one hit'),
 'zetterburn-gameplay2':('03-rule-not-scale','Airborne fire hit','Attack/condition branch'),
 'orcane-gameplay1':('03-rule-not-scale','Water/bubbles and movement','Location-dependent option'),
 'orcane-gameplay2':('03-rule-not-scale','Water/bubbles during combat','Different action grammar'),
 'forsburn-gameplay1':('04-information-rule','Two figures and smoke obscuration','Opponent information changes'),
 'forsburn-gameplay2':('04-information-rule','Smoke/charged-looking burst','State and readability; no invulnerability claim'),
 'rivals-match-01':('01-overview','Ground/aerial approach','Shared baseline possibilities'),
 'rivals-match-02':('02-common-baseline','Ground/aerial exchanges and platform pressure','Same game grammar; distinct choices'),
 'rivals-match-03':('05-useful-strength','Off-stage pressure/return','Strength depends on situation'),
 'rivals-match-04':('05-useful-strength','Aerial and ledge interactions','Space and recovery options'),
 'rivals-match-05':('06-role-and-limitation','Close/on-stage to off-stage exchanges','Pressure plus counterplay'),
 'rivals-match-06':('07-state-not-base','Historical armor-like state and aerial exchanges','Current state versus base specification'),
 'rivals-match-07':('10-balance-preserves-role','Armor-like appearance and opponent pressure','Condition and answer, no numerical tier ranking'),
 'rivals-match-08':('11-cost-and-summary','Spacing and close exchange','Concise role and testable interactions'),
 'slade-steal':('08-resources-and-actions','STEAL hit and106→111 coins','Actions affect resources; not evasion'),
 'hamir-react':('08-resources-and-actions','REACT and DEF3→6 then BLOCKED','Parameter as result of action'),
 'artemis-stun':('08-resources-and-actions','STUN opposing die change','Opponent state, not just own attack scaling'),
 'fleet-snipe':('09-condition-and-time','SNIPE and next-turn die indicators','When/what the effect grants'),
 'fleet-strike':('09-condition-and-time','Separate boss STRIKE−1HP','Immediate damage contrasted with a delayed effect')}
for w in plan['windows']:
 chapter,action,diagram=links[w['key']]
 w.update(provisionalInsertion=chapter,visibleAction=action,viewerFocus=diagram,diagramConnection=diagram,
  normalPlaybackRate=1,sourceAudioUse=False,loop=False,slowdown=False,
  observation=b['sourceObservations'][w['key']],selectedForNarrationPlanning=True,
  finalUseDurationSeconds=None,allFinalCueUiApproved=False)
evidenceNames=['content-studio-direct-review-v1.json','source-research-direct-review-v1.json','native-trial-direct-review-v3.json','trim-boundary-direct-review-v4.json','fullscreen-ui-direct-review-v5.json','native-playback-observation-v1.json','native-trim-plan-v4.json']
d={'schemaVersion':1,'slug':'character-parameters','recordedAt':datetime.now(timezone.utc).isoformat(),
 'status':'reviewed-action-bank-ready-for-independent-narration','sourceAdoptionApproved':True,
 'adoptionScope':'Reviewed normal-speed native action candidates only; measured allocation and final narration-cue/UI review remain pending. All19 windows need not be used in full.',
 'sources':sources,'windows':plan['windows'],'maximumUniqueSeconds':plan['totalUniqueSeconds'],
 'proofs':[{'path':(P/x).relative_to(ROOT).as_posix(),'sha256':sha(P/x)} for x in evidenceNames],
 'rights':rights,'sourceOwners':'Aether Studios official character website and official YouTube channel, including its historical RCS broadcast.',
 'recentUseReview':{'method':'Complete current project manifests and source JSON/Markdown scanned for chosen title/character/source identifiers after an initial rg search; content duplicate review is separate.',
 'filesScanned':len(recentFiles),'matches':hits,'earlierCompletedTitleUseObserved':bool(hits),'inputHashes':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in recentFiles]},
 'candidates':[
 {'game':'Rivals of Aether','selected':True,'reason':'Actual shared combat rules, character-specific fire/water/smoke and historical Etalus/Ori match interactions; fresh current source review.', 'rightsUrl':'https://aetherstudios.com/press-releases/'},
 {'game':'Dungeons of Aether','selected':True,'reason':'Actual dice-modified stat rows and distinct named actions; only five brief combat windows, no promotion or dialogue quota.', 'rightsUrl':'https://aetherstudios.com/press-releases/'},
 {'game':'Balatro/Tetris','selected':False,'directlyObservedForThisProject':False,'reason':'Recently used score episode; scoring identity does not demonstrate a character roster here.'},
 {'game':'Super Smash Bros.','selected':False,'directlyObservedForThisProject':False,'reason':'Original lecture examples are research only; its footage/audio cannot substitute independently secured examples.'}],
 'exclusions':['Official source promotion, menu, tooltip-only, journal/map/dialogue, countdown/commentators, repeated montage, long defeat/result and isolated idle tails.','No source audio, web loop or slowdown.','Rivals06 pre-jump frames excluded; separate games and montage actions are not one continuous effect or proof of victory.'],
 'gameCaptionConstraint':{'style':'boxed-white-forest-v1','center':[960,970],'lines':1,'maximumHangulCharacters':18,'alsoRequireMeasuredPixelWidth':True},
 'sourceFraming':layout['selectedLayout'],'actualBodyRatioApproved':False,'allFinalPixelsApproved':False,'allNativeFramesReviewed':False,
 'wholeContinuousViewingOrListeningApproved':False,'humanListeningApproved':False,'publicRightsApproved':False,
 'newSourceAcquisitionOrDecodeOrExtraction':0,'externalResearchChanges':0,'rasterGitAdditions':0}
put(out,d)
print(json.dumps({'sourceAdoptionApproved':True,'windows':19,'maximumUniqueSeconds':d['maximumUniqueSeconds'],'recentFiles':len(recentFiles),'previousMatches':len(hits),'finalPixelsApproved':False}))
