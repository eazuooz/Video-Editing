"""Reassign unique battle footage to the wall guide without altering any voice."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
dest = BASE / 'measured-edit-v4'
assert not dest.exists(), 'Preserve earlier candidates.'
old = read(BASE / 'measured-edit-v3/plan.json')
review = read(BASE / 'guided-native-caption-direct-review-v3.json')
assert review['allImagesDirectlyRead'] and not review['framingApproved']
plan = copy.deepcopy(old)
by = {s['id']: s for s in plan['scenes']}
two, six = by['02'], by['06']
bridge = next(c for c in two['segments'] if c.get('bankCutId') == 12)
wall = next(c for c in six['segments'] if c.get('bankCutId') == 17)
assert bridge['frames'] == 422 and wall['frames'] == 420
two['segments'] = [c for c in two['segments'] if c.get('bankCutId') not in [12, 13]] + [
    next(c for c in old['scenes'][1]['segments'] if c.get('bankCutId') == 13),
    {**wall, 'sceneId': '02', 'paragraph': 4, 'parentOriginalParagraph': 4,
     'id': '02-p4-action-17-18990-19200',
     'insertion': 'After the short wall-spray excerpt, one continuous seven-second wall-side fight spans the new wall/approach/turn/direct-attack guide.',
     'claim': 'Observe approaching enemies beside wall devices and player aim/body direction/direct attack. Separate excerpts do not prove a continuous fight or trap causation.'}]
six['segments'] = [c for c in six['segments'] if c.get('bankCutId') != 17]
at = next(i for i,c in enumerate(six['segments']) if c['paragraph'] == 3)
six['segments'].insert(at, {**bridge, 'sceneId': '06', 'paragraph': 2,
    'parentOriginalParagraph': 2, 'id': '06-p2-action-12-17865-18076',
    'insertion': 'After short direct combat/floor-effect excerpts, the bridge fight illustrates the instruction to distinguish preparation from combat.',
    'claim': 'Direct attack and a separate battle observation; do not identify the player projectile as a floor-device effect or infer a single continuous sequence.'})
assert [c['bankCutId'] for c in six['segments'] if c['paragraph']==2] == [18,20,12]
# Two output frames transfer with the same unique source interval. Only silence
# changes: remove800 samples from02's final silence and add800 before06p3.
last = two['pcmPlacement'][-1]
assert last['kind'] == 'inserted-silence' and last['samples'] > 800
last['samples'] -= 800; last['outputToSample'] -= 800
boundary = next(p['outputSpeechFromSample'] for p in six['speechEvidence'] if p['paragraph']==3)
pad = next(p for p in six['pcmPlacement'] if p['kind']=='inserted-silence' and p['outputToSample']==boundary)
pad['samples'] += 800; pad['outputToSample'] += 800
for p in six['pcmPlacement']:
    if p is pad: continue
    if p['outputFromSample'] >= boundary:
        p['outputFromSample'] += 800; p['outputToSample'] += 800
for p in six['speechEvidence']:
    if p['paragraph'] >= 3:
        p['outputSpeechFromSample'] += 800; p['outputSpeechToSample'] += 800
cursor = 120
for s in plan['scenes']:
    local = 0
    for c in s['segments']:
        c.update(sceneId=s['id'], localFromFrame=local, startFrame=cursor+local,
                 endFrameExclusive=cursor+local+c['frames'], seconds=c['frames']/60,
                 finalApproved=False, captionPixelsApproved=False, mediaCompiled=False)
        local += c['frames']
    s.update(startFrame=cursor,endFrameExclusive=cursor+local,frames=local)
    assert s['pcmPlacement'][-1]['outputToSample']==local*400
    cursor += local
actual = [c for s in plan['scenes'] for c in s['segments'] if c['classification']=='actual-existing-game']
white = [c for s in plan['scenes'] for c in s['segments'] if c['classification']=='explanation']
assert sum(c['frames'] for c in actual)==20918 and sum(c['frames'] for c in white)==13945
for asset in plan['assets']:
    spans=sorted((c['sourceStartFrame'],c['sourceEndFrameExclusive']) for c in actual if c['assetId']==asset['assetId'])
    assert all(a[1]<=z[0] for a,z in zip(spans,spans[1:]))
for s in plan['scenes']:
    before = next(x for x in old['scenes'] if x['id']==s['id'])
    kept = [(p['audio'],p['audioSha256'],p['fromSample'],p['toSample']) for p in s['pcmPlacement'] if p['kind']!='inserted-silence']
    inherited = [(p['audio'],p['audioSha256'],p['fromSample'],p['toSample']) for p in before['pcmPlacement'] if p['kind']!='inserted-silence']
    assert kept==inherited and [p['ko'] for p in s['speechEvidence']]==[p['ko'] for p in before['speechEvidence']]
plan.update(createdAt=datetime.now(timezone.utc).isoformat(),
    status='guided60-v4-wall-source-reassignment-candidate-final-gates-pending',
    historicalV3Plan={'path':'projects/making-game-sequels/production/measured-edit-v3/plan.json','sha256':sha(BASE/'measured-edit-v3/plan.json')},
    sourceAndCaptionTrialReview='projects/making-game-sequels/production/guided-native-caption-direct-review-v3.json',
    candidateJoinDirectReview='projects/making-game-sequels/production/guided-joins-direct-review-v3.json',
    sourceReassignment={'wallGuide':'02-g1','continuousWallNativeFrames':[18990,19200],
        'wallGuideNativeOnsetApprox':19040,'recipientBridgeScene':'06','recipientBridgeNativeFrames':[17865,18076],
        'why':'The earlier guide began about3.3s before wall devices appeared. Existing wall combat moves to that guide; bridge combat moves to a general separate-combat observation after the floor-effect words.',
        'scene02FrameChange':-2,'scene06FrameChange':2,'bodyFramesChange':0,
        'allNativeIntervalsUnique':True,'all554_584ComponentPcmSamplesPreserved':True,
        'changedTargetPixelsApproved':False},
    finalTimingApproved=False,bodyRatioApproved=False,allCaptionPixelsReviewed=False,
    finalMixBuilt=False,rendered=False,qaApproved=False,collected=False,privateUploaded=False)
plan['inputs']['projects/making-game-sequels/production/guided-native-caption-direct-review-v3.json']=sha(BASE/'guided-native-caption-direct-review-v3.json')
plan['inputs']['projects/making-game-sequels/production/guided-joins-direct-review-v3.json']=sha(BASE/'guided-joins-direct-review-v3.json')
dest.mkdir(); save(dest/'plan.json',plan)
print(json.dumps({'nativeCuts':len(actual),'actualFrames':20918,'whiteFrames':13945,'allPcmPreserved':True,'wallGuidePixelsPending':True}))
