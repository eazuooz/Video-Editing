"""Seal direct boundary review; preserve all earlier trials and native media."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[4]
P=Path(__file__).resolve().parent
def read(n): return json.loads((P/n).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d):
 p=P/n
 assert not p.exists(), f'Preserve existing {n}'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
e=read('trim-boundary-execution-v1.json')
session=read('trim-boundary-execution-v1.json.session.json')
assert e['totalSamples']==238 and e['totalBoards']==42
for source in e['sources']:
 for s in source['samples']:
  assert sha(ROOT/s['path'])==s['sha256']
  assert sha(ROOT/s['trialPath'])==s['trialSha256']
 for b in source['boards']: assert sha(ROOT/b['path'])==b['sha256']
plan=read('native-trim-plan-v3.json')
win=next(w for w in plan['windows'] if w['key']=='rivals-match-06')
win.update(priorBoundaryReviewStartFrame=5520,startFrame=5523,startPts=5523*3000,durationSeconds=(6480-5523)/30,
 boundaryCorrection='Native timer1:58 at5517–5521 abruptly becomes1:51 at5522. Exclude the pre-jump frames and start5523. Constant native CFR/PTS is preserved; no VFR diagnosis or continuous8-second action claim.')
for w in plan['windows']:w['boundaryDirectReviewApproved']=True
plan.update(recordedAt=datetime.now(timezone.utc).isoformat(),status='native-boundaries-directly-reviewed',
 totalUniqueSeconds=sum(w['durationSeconds'] for w in plan['windows']),nativeExactSelectionApproved=True,
 sourceAdoptionApproved=False,finalCueUiApproved=False,
 notes='Half-open native PTS intervals. Boundary samples and full native trial samples directly reviewed; not a claim of every intervening frame or whole continuous listening. Source adoption awaits the separate bank, rights and current duplicate gate.')
put('native-trim-plan-v4.json',plan)
notes={
 'zetterburn-gameplay1':'Start action retained; late277–279 fire-hit aftermath only, exclude isolated later idle. Do not claim burn damage formula.',
 'zetterburn-gameplay2':'Airborne upward fire hit and brief landing/ghost aftermath; exclude isolated tail after129.',
 'orcane-gameplay1':'Water/rolling movement remains visible at152–154. Original top-edge opponent extent preserved, not artificially repaired.',
 'orcane-gameplay2':'Water swirl remains at207–209; exclude later alone/idle tail.',
 'forsburn-gameplay1':'Smoke obscuration is the visible mechanic, not unrelated idle; end255 excludes source ending.',
 'forsburn-gameplay2':'Clone/burst and airborne action end before isolated tail after153.',
 'rivals-match-01':'On-stage approach/close hit. Both damage HUDs, players and broadcast credit preserved.',
 'rivals-match-02':'Movement/platform/close pressure; end at44 with98%/45% observed, not base stats.',
 'rivals-match-03':'Left off-stage exchange, stock change and continuing movement; not winner/result menu.',
 'rivals-match-04':'Respawn into on-stage/aerial exchange; native off-stage heights remain uncropped.',
 'rivals-match-05':'On-stage to left off-stage pressure; changing damage is current match state, not guaranteed damage or matchup strength.',
 'rivals-match-06':win['boundaryCorrection']+' Later aerial interaction103%/83% observed; historical separate game, not continuity with prior stage.',
 'rivals-match-07':'Armor-like Etalus state and subsequent pressure; do not infer a universal numerical armor multiplier.',
 'rivals-match-08':'Close exchange and accumulated damage; no victory/optimal strategy claim.',
 'slade-steal':'STEAL contact and coin106→111, opponent−2HP observed. End1783 excludes subsequent extended defeated state. Not dodge evidence.',
 'hamir-react':'Selected REACT, DEF3→6 and STA7→6 seen in reviewed native action; then BLOCKED/+1STA. Later rolled stats are a new turn, not base parameters.',
 'artemis-stun':'Selected STUN changes opposing die state, followed by separate STRONG/BLOCKED interaction. No claim that this action demonstrates regeneration. Cut ends before extended new draft.',
 'fleet-snipe':'Selected SNIPE, hit then two yellow+3 die indicators. Full-resolution native2418 tooltip directly read: deals1HP damage and grants two3STA dice ON THE NEXT TURN. Do not describe immediate+6 current stamina; displayed current STA3 is unchanged.',
 'fleet-strike':'Separate boss STRIKE with−1HP visible by4611; end4612 excludes defeat/result aftermath. Not continuous with SNIPE window.'}
review={'schemaVersion':1,'slug':'character-parameters','reviewedAt':datetime.now(timezone.utc).isoformat(),
 'execution':'production/batches/sakurai-planning-game-design/proof-character-parameters/trim-boundary-execution-v1.json',
 'executionSha256':sha(P/'trim-boundary-execution-v1.json'),'actualSessionEvidence':session,
 'directlyReadSamples':238,'directlyReadBoards':42,'allBoundaryBoardsDirectlyRead':True,'allBoundaryHashesMatch':True,
 'additionalCriticalFullResolutionRead':{'nativeFrame':2418,'path':'shared/output/character-parameters/preflight/native-actions-v2/a8nwpiCqyTQ/native/pts-619008.png','observation':notes['fleet-snipe']},
 'sourceObservations':notes,'selectedPlan':'production/batches/sakurai-planning-game-design/proof-character-parameters/native-trim-plan-v4.json',
 'selectedPlanSha256':sha(P/'native-trim-plan-v4.json'),'nativeBoundarySelectionApproved':True,
 'scope':'19 half-open candidate windows and their boundary pixels only. Actual narration cues are not created. Full-screen sample layout approval is separate; all final pixels/cues/native frames/continuous listening remain unapproved.',
 'sourceAdoptionApproved':False,'allNativeFramesReviewed':False,'wholeContinuousListeningApproved':False,
 'allFinalCueUiApproved':False,'publicRightsApproved':False,'humanListeningApproved':False,
 'newExtractionCount':0,'externalResearchChanges':0,'rasterGitAdditions':0}
put('trim-boundary-direct-review-v4.json',review)
print(json.dumps({'boundarySamples':238,'boards':42,'uniqueSeconds':plan['totalUniqueSeconds'],'sourceAdoptionApproved':False}))
