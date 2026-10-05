"""Lock the direct read of65 new raw-context samples and correct two native ends.

No current narration sample or completed media is changed. Raster evidence stays
local; this records sampled observations rather than rendered-final approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
write = lambda p,d: p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
now = datetime.now(timezone.utc).isoformat()
state_path = BASE / 'measured-edit-v3/flagged-native-context-local/execution.json'
state = read(state_path)
assert state['exitCode'] == 0 and len(state['images']) == 65 and len(state['sheets']) == 11
for r in state['images'] + state['sheets']:
    assert sha(ROOT / r['path']) == r['sha256']
    r.update(directlyRead=True, directlyReadAt=now)
state.update(status='closed-all65-raw-context-images-directly-read-two-native-end-corrections',
             sessionId=78822, allDirectlyRead=True, updatedAt=now)
write(state_path,state)
review = {'schemaVersion':1,'reviewedAt':now,'status':'raw-context-direct-review-corrections-required',
    'execution':rel(state_path),'executionSha256':sha(state_path),'images':state['images'],'sheets':state['sheets'],
    'sourceMethod':'Full original input decode; select actual native n, with no time seek or downloaded-source retry.',
    'findings':[
      {'action':'action-83','source':'CJ0_Xh59b98','reviewedNativeRange':[1220,1275],
       'lastCleanFrame':1269,'firstEditorialDissolveFrame':1270,'oldEndExclusive':1276,'newEndExclusive':1270,
       'finding':'At1270 a different map scene first becomes faintly superimposed;1271–1275 strengthen that editorial dissolve. The preceding combat remains visible at1269. Remove all six transition samples.'},
      {'action':'action-73','source':'o3Fomp9HdHs','reviewedNativeRange':[720,785],
       'lastSampledCleanFrame':784,'firstDialogueFrame':785,'oldEndExclusive':786,'newEndExclusive':785,
       'finding':'720–784 sampled movement through the curved terrain is actual gameplay.785 opens a large source dialogue box with the first Y, so exclude that frame rather than hiding the dialogue.'},
      {'action':'action-94','source':'CJ0_Xh59b98','reviewedNativeRange':[8990,9188],
       'finding':'The desk character approaches the same green entry, rises into a white entry effect, becomes flat on the same printed surface, and fights there while the book geometry/camera remains continuous.',
       'interpretation':'The layered representation here is an observed in-game2D/3D entry/camera effect, unlike the different-map editorial dissolve in action83. This is an inference from visible spatial/character continuity, not a claim about a specific button or universal entry rule.',
       'remainingReview':'Reframing and every final caption/transition pixel are still pending.'},
      {'action':'action-71','source':'h27ZF-hKKYM','reviewedNativeRange':[9690,9989],
       'finding':'9690–9910 samples show desk movement/combat.9930 shows the beginning of a flame-powered launch, followed by ascent at9950/9970/9989. The current12p1 rocket phrase starts over combat and is not approved.',
       'nextAction':'Reallocate a distinct already-reviewed flight interval to the rocket words, preserving all PCM and normal source speed; do not describe desk combat as ascent.'}],
    'sampledImagesDirectlyRead':65,'sheetsDirectlyRead':11,'newGitImages':0,'sourceAudioStreams':0,
    'allCurrent15PcmPreserved':True,'finalWordAlignmentApproved':False,'finalFramingApproved':False,
    'finalCaptionPixelsApproved':False,'bodyRatioApproved':False,'humanWholeListening':'pending'}
review_path = BASE / 'flagged-native-context-direct-review.json'
write(review_path,review)
bank = copy.deepcopy(read(PROOF / 'source-action-bank-v6.json'))
for c in bank['clips']:
    if c['id'] not in ['action-83','action-73']:continue
    old=c['endFrameExclusive']; new=1270 if c['id']=='action-83' else 785
    assert old == (1276 if c['id']=='action-83' else 786)
    c.update(endFrameExclusive=new,outSeconds=new/c['nativeFps'],seconds=(new-c['startFrame'])/c['nativeFps'],
             exactBoundaryReview=rel(review_path),
             excludedTail={'oldEndExclusive':old,'newEndExclusive':new,'reason':'Editorial dissolve' if c['id']=='action-83' else 'Source dialogue first frame'})
bank.update(createdAt=now,previousBank=rel(PROOF/'source-action-bank-v6.json'),status='93-native-candidates-water-wipe-mine-dissolve-drill-dialogue-ends-corrected')
bank['uniqueSourceSeconds']=sum(c['seconds'] for c in bank['clips'])
bank['bySourceSeconds']={i:sum(c['seconds'] for c in bank['clips'] if c['sourceVideoId']==i) for i in bank['bySourceSeconds']}
bank_path=PROOF/'source-action-bank-v7.json';assert not bank_path.exists();write(bank_path,bank)
proposal=copy.deepcopy(read(BASE/'native-cue-proposal-v4.json'))
for g in proposal['groups']:
    for c in g['sourceCuts']:
        if c['id'] in ['action-83','action-73']:c.update(next(x for x in bank['clips'] if x['id']==c['id']))
    if g['sceneId']=='15' and g['paragraph']==3:
        assert [c['id'] for c in g['sourceCuts']]==['action-98','action-24','action-07']
        g['sourceCuts']=[g['sourceCuts'][0],g['sourceCuts'][2],g['sourceCuts'][1]]
        g['wordOrderCorrection']='Water emergence → lava emergence → firing toward enemy, matching retained narration; no native interval or PCM repeats.'
    g['sourceSeconds']=sum(c['seconds'] for c in g['sourceCuts'])
proposal.update(schemaVersion=5,createdAt=now,supersedes=rel(BASE/'native-cue-proposal-v4.json'),
                sourceActionBank=rel(bank_path),directPixelReview=rel(review_path))
proposal['sourceUniqueSeconds']=sum(g['sourceSeconds'] for g in proposal['groups'])
proposal_path=BASE/'native-cue-proposal-v5.json';assert not proposal_path.exists();write(proposal_path,proposal)
print(json.dumps({'rawImagesRead':65,'correctedNativeEnds':2,'bankIntervals':len(bank['clips']),
                 'nativeSeconds':bank['uniqueSourceSeconds'],'newGitImages':0,'finalApproved':False}))
