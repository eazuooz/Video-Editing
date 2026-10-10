"""Seal the directly read v4/v5 sample layouts, without adopting source cuts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT=Path(__file__).resolve().parents[4]; P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
target=P/'fullscreen-ui-direct-review-v5.json'
assert not target.exists(), 'Preserve completed review.'
v4=json.loads((P/'fullscreen-ui-trial-v4.json').read_text(encoding='utf-8-sig'))
v5=json.loads((P/'fullscreen-ui-trial-v5.json').read_text(encoding='utf-8-sig'))
for v,n,b in [(v4,26,5),(v5,13,3)]:
 assert len(v['samples'])==n and len(v['boards'])==b
 for s in v['samples']:
  assert sha(ROOT/s['path'])==s['sha256']
  assert sha(ROOT/s['trialPath'])==s['trialSha256']
 for x in v['boards']:assert sha(ROOT/x['path'])==x['sha256']
d={'schemaVersion':1,'slug':'character-parameters','recordedAt':datetime.now(timezone.utc).isoformat(),
 'v4':{'evidence':'production/batches/sakurai-planning-game-design/proof-character-parameters/fullscreen-ui-trial-v4.json','sha256':sha(P/'fullscreen-ui-trial-v4.json'),
 'directlyReadSamples':26,'directlyReadBoards':5,'rivalsSampleLayoutApproved':True,'dungeonsSampleLayoutApproved':False,
 'observedFailures':['Dungeons inventory covers REACT at native2034.','Dungeons inventory covers STRONG at2265.','Dungeons inventory covers boss upper body at4533/4605.']},
 'v5':{'evidence':'production/batches/sakurai-planning-game-design/proof-character-parameters/fullscreen-ui-trial-v5.json','sha256':sha(P/'fullscreen-ui-trial-v5.json'),
 'directlyReadSamples':13,'directlyReadBoards':3,'extraFullResolutionSample':2034,'dungeonsSampleLayoutApproved':True,
 'observations':'Original full-frame action/stat dice/STA/hearts/skill names unchanged. Same-frame complete inventory and coins at1490,135 with424x55 size is below enemy name and right of stat dice. REACT/STRONG headers and boss upper body clear; full-resolution2034 coin291 readable. Left-clipped character-name reveal is native source content, not removed by this layout.'},
 'rivalsObservations':'Whole native action y0:657 remains full-width at original aspect, including high aerial1515/1530 and offstage7605/7650. Original bottom HUD split to corners; original commentator credit remains below fixed caption. All13 target samples clear with the demonstrated one-line cue.',
 'scope':'Target-sample full-screen layout approval only. Actual narration cues must be single-line, measured width, at960970. No approval of every native frame, exact boundaries, final cues, continuous whole viewing/listening or source adoption.',
 'selectedLayout':{'gBbKFYZYvbc':'fullscreen-ui-trial-v4','a8nwpiCqyTQ':'fullscreen-ui-trial-v5','officialShorts':'Preserved full-width1920x960 native2:1, same-frame lower extension.'},
 'sampleFullscreenLayoutApproved':True,'allNativeFramesReviewed':False,'nativeExactSelectionApproved':False,'sourceAdoptionApproved':False,'allFinalCueUiApproved':False,'publicRightsApproved':False,'humanListeningApproved':False,
 'newNativeExtractionCount':0,'externalResearchChanges':0,'rasterGitAdditions':0}
target.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sampleFullscreenLayoutApproved':True,'sourceAdoptionApproved':False,'v4Samples':26,'v5Samples':13}))
