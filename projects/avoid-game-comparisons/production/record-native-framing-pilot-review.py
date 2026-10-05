"""Record directly inspected local pixels and supersede one unsafe native edge."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
write = lambda p, d: p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
now = datetime.now(timezone.utc).isoformat()
pilot = BASE / 'measured-edit-v2/framing-pilot-local'
records = read(pilot / 'extraction.json')['records']
for c in records:
    assert sha(ROOT / c['image']) == c['sha256']
    c['directPixelReview'] = True
    if 'action-96' in c['cut'] or 'action-97' in c['cut']:
        c['finding'] = 'Avatar/terrain are visible in the full shot, but the large lower-left FINAL GAMEPLAY label intersects the wide caption. The trial1472x828 crop leaves a clipped label and moves the avatar toward the caption region; no blanket crop approval.'
    elif 'action-98' in c['cut']:
        c['finding'] = 'Actual fullscreen final breaking-VFX gameplay: avatar drills through a metal boat from water and rises beside a green enemy. It is not the earlier inset SINKING TEST. Caption intersects the lower-right annotation. Reject the inset-crop rationale and inspect new framing.'
    elif 'action-66' in c['cut']:
        c['finding'] = 'Cup/character ascent is visible. The1600x900 trial enlarges the cup and covers more of the lower cup with the fixed caption. Full shot is preferable at this sample; this is not a fuel-UI flight shot. Other times remain pending.'
    elif 'action-65' in c['cut']:
        c['finding'] = 'Both full and trial crop keep the blue printed-surface combat avatar above the fixed caption. Sample layout is readable; the new sentence pause and complete cut boundaries are still pending.'
    elif 'action-95' in c['cut']:
        c['finding'] = 'Fight avatar and red chest are visible, but fixed caption overlaps printed story text at the page bottom. Reframe/split cues before approval; later opened red chest/card must be checked at its actual word time.'
    c['finalApproved'] = False
edges = []
for k, native in enumerate(range(1571, 1575), 1):
    p = pilot / f'kwd-wipe-edge-{k:02d}.png'
    edges.append({'nativeFrame': native, 'path': rel(p), 'sha256': sha(p), 'directlyRead': True,
                  'finding': 'Clean active gameplay without the edit wipe.' if native < 1574 else 'First visible black wipe in the upper-left corner; exclude.'})
for k, native in enumerate([1530, 1556, 1574, 1575], 1):
    p = pilot / f'kwd-native-exact-{k:02d}.png'
    edges.append({'nativeFrame': native, 'path': rel(p), 'sha256': sha(p), 'directlyRead': True,
                  'finding': 'Fullscreen final breaking-VFX gameplay, not the earlier inset test.' if native < 1574 else 'Black transition wipe; excluded from the corrected action.'})
review = {'schemaVersion': 1, 'reviewedAt': now, 'pilotImages': records, 'exactNativeImages': edges,
    'nativeExtraction': {'source': 'KWDk-csu460', 'sourceSha256': '6ffdcb41a4a2b852d9b15ef8de726b09560d36f1ff8132f64dd2747ed0ed4efd',
        'nativeFps': 30, 'sourceStartTime': 0, 'method': 'Full raw input decode with select on native n; no output-time seek or offset.',
        'failedFilterAttempt': 'Initial unescaped between(n,1571,1574) filter exited1 before output. Escaped native selection exited0 and produced the four directly read frames.'},
    'correction': {'action': 'action-98', 'oldRange': [1530, 1575], 'newRange': [1530, 1574],
        'lastCleanNativeFrame': 1573, 'firstWipeNativeFrame': 1574,
        'earlierClaim': 'The prior52.5-second conservative endpoint included the first wipe frame. Bank action98 already described water-vehicle attack correctly; the compiler inset-test caution and pilot inset rationale were inaccurate.',
        'currentClaim': 'Water emergence/boat destruction is the observed action. Preserve the original source and earlier review as historical evidence; do not call this the earlier sinking test.'},
    'rejectedAdditionalMineInterval': {'nativeRange': [2578, 2788], 'source': 'CJ0_Xh59b98',
        'reason': 'All19 new samples directly inspected: mostly stationary framing/book turn/star effect, so do not add it as active-action quota.', 'addedActualSeconds': 0},
    'allPilotImagesDirectlyRead': True, 'newGitImages': 0, 'sourceAudioUsed': False,
    'finalFramingApproved': False, 'allFinalCuePixelsReviewed': False, 'bodyRatioApproved': False}
write(BASE / 'native-framing-pilot-direct-review.json', review)

bank = copy.deepcopy(read(PROOF / 'source-action-bank-v5.json'))
for c in bank['clips']:
    if c['id'] != 'action-98': continue
    assert c['startFrame'] == 1530 and c['endFrameExclusive'] == 1575
    c.update(endFrameExclusive=1574, outSeconds=1574 / 30, seconds=44 / 30,
             visibleAction='Drilling through a metal boat from water and rising beside a green enemy',
             insertionPoint='15p3 water-emergence contrast before the movement/target white comparison',
             caution='Fullscreen final breaking-VFX gameplay, not the earlier inset sinking test. Exclude first wipe native1574 and later. Preserve the development context and inspect the lower-right annotation against every fixed caption.',
             exactBoundaryReview=rel(BASE / 'native-framing-pilot-direct-review.json'))
bank.update(createdAt=now, previousBank=rel(PROOF / 'source-action-bank-v5.json'),
            status='93-native-planning-candidates-water-wipe-edge-corrected')
bank['uniqueSourceSeconds'] = sum(c['seconds'] for c in bank['clips'])
bank['bySourceSeconds'] = {i: sum(c['seconds'] for c in bank['clips'] if c['sourceVideoId'] == i) for i in bank['bySourceSeconds']}
assert not (PROOF / 'source-action-bank-v6.json').exists()
write(PROOF / 'source-action-bank-v6.json', bank)

proposal = copy.deepcopy(read(BASE / 'native-cue-proposal-v3.json'))
for g in proposal['groups']:
    for c in g['sourceCuts']:
        if c['id'] == 'action-98':
            replacement = next(c for c in bank['clips'] if c['id'] == 'action-98')
            c.update(replacement)
    g['sourceSeconds'] = sum(c['seconds'] for c in g['sourceCuts'])
proposal.update(schemaVersion=4, createdAt=now, supersedes=rel(BASE / 'native-cue-proposal-v3.json'),
    sourceActionBank=rel(PROOF / 'source-action-bank-v6.json'), directPixelReview=rel(BASE / 'native-framing-pilot-direct-review.json'))
proposal['sourceUniqueSeconds'] = sum(g['sourceSeconds'] for g in proposal['groups'])
assert not (BASE / 'native-cue-proposal-v4.json').exists()
write(BASE / 'native-cue-proposal-v4.json', proposal)
print(json.dumps({'bankIntervals': len(bank['clips']), 'nativeSeconds': bank['uniqueSourceSeconds'], 'newGitImages': 0}))
