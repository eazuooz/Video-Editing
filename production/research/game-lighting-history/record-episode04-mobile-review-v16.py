"""Seal the completed 337-image direct sample review, without moving approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
P = ROOT/'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()
proof = lambda p: {'path': rel(p), 'sha256': sha(p)}
EP = ROOT/'production/research/game-lighting-history/local/episode04-mobile-encoded-v16/execution.json'
RP = P/'mobile-encoded-direct-review-v16.json'
assert not RP.exists(), 'Preserve earlier review'
e = read(EP)
assert e['status'] == 'encoded-samples-ready'
assert len(e['items']) == 337 and len(e['boards']) == 85
assert len(e['commands']) == 2 and all(c['exitCode'] == 0 for c in e['commands'])
session = read(EP.with_name('session.json'))
assert session['closed'] and session['exitCode'] == 0 and session['unifiedExecExitObserved']
boards = []
for b in e['boards']:
    assert sha(ROOT/b['path']) == b['sha256']
    boards.append({**b, 'directlyViewed': True, 'reviewedAt': stamp()})
items = []
for item in e['items']:
    assert sha(ROOT/item['path']) == item['sha256']
    items.append({**item, 'directlyViewedOnBoard': True})
assert sum(b['source'] == 'clean' for b in boards) == 15
assert sum(b['source'] == 'captioned' for b in boards) == 70
assert sum(i['source'] == 'clean' for i in items) == 60
assert sum(i['source'] == 'captioned' for i in items) == 277
gates = {k: False for k in ['allFinalPixelsReviewed', 'allMovingPixelsReviewed',
    'causalFlowApproved', 'finalMixedAsrApproved', 'wholeEpisode60to40Approved',
    'qaApproved', 'collected', 'uploaded']}
review = {
    'reviewedAt': stamp(),
    'scope': 'Mobile/visibility chapter encoded sample review only; continuous playback and final episode approval remain pending',
    'plan': proof(P/'mobile-chapter-review-plan-v16.json'),
    'build': proof(P/'mobile-chapter-review-build-v16.json'),
    'execution': proof(EP), 'session': proof(EP.with_name('session.json')),
    'boards': boards, 'items': items,
    'all337SamplesDirectlyRead': True, 'all85BoardsDirectlyRead': True,
    'cleanImages': 60, 'captionedImages': 277, 'captionCuesReviewed': list(range(74,124)),
    'sampledCaptionClearanceApproved': True, 'sourceConditionLabelApproved': True,
    'findings': [
        'Clean001-015 and captioned001-070 directly viewed across the continued task. G-buffer contents and triangle/instance identity are distinct; identification is not a completed lighting result.',
        'Triangle7 uses already perspective-corrected weights, followed by an explicitly independent equal-clip-w example: weights0.5/0.25/0.25 map UV(0,0),(1,0),(0,1) to(0.25,0.25). Differing-w correction and triangle-boundary derivatives remain qualified.',
        'Reconstruction introduces geometry/material reads and cache/layout/MSAA costs. Microsoft official sample/GDK2022 reference is not an invention date or independent benchmark.',
        'Forward/deferred computation order remains separate from tile hardware storage and Forward+ light lists. Producer/consumer and optional external-memory paths are spatially separated; no measured bandwidth count is invented.',
        'Supported Unreal paths, device/API/pass conditions and possible external-memory writes are retained. Transparency uses separate layered/forward treatment, followed by material/light/bandwidth/device-dependent coexistence.',
        'Native Rivalry2014 surface/camera samples retain their source identity and explicit limit: finished pixels do not reveal tile-memory round-trip counts or prove a later mobile deferred implementation. No presenter, desktop or title card in the sampled interval.',
        'All50 cue boundaries/middles and sampled17 cut boundaries checked. White boxed black narration text with forest shadow stays centered at960,970,48px,max2lines; source labels, projected faces, formula/limit footers and captions are clear in the337 sampled images.',
        'Original0.72s gaps and chapter PCM preserved; held gap imagery counts as explanation. This record certifies sampled pixels, not every moving frame or a final60:40 allocation.'
    ],
    **gates, 'newTts': 0, 'sourceModelsRerendered': 0, 'newGitImages': 0,
    'humanWholeListening': 'pending', 'normalSpeedContinuousPlayback': 'pending',
    'next': 'Review13 source samples10-26.933s and prepare the path tracing chapter using preserved12 KO/EN paragraphs and PCM.'
}
RP.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
CP = ROOT/'production/research/game-lighting-history/checkpoint.json'
cp = read(CP)
cp['episode04MobileEncodedDirectReviewV16'] = {'path': rel(RP), 'sha256': sha(RP),
    'samples': 337, 'boards': 85, 'captionCues': 50,
    'sampledCaptionClearanceApproved': True, 'sourceConditionLabelApproved': True, **gates}
cp['ownedActiveWork'] = {'status':'no-active-owned-media-worker','next':review['next']}
cp['updatedAt'] = stamp()
tmp = CP.with_suffix('.mobile-review-v16.tmp')
tmp.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8'); tmp.replace(CP)
print(json.dumps({'path':rel(RP),'sha256':sha(RP),'samples':337,'boards':85,'finalApproved':False}))
