"""Seal directly read reconstruction samples; continuous and final gates stay pending."""
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
EP = ROOT/'production/research/game-lighting-history/local/episode04-reconstruction-encoded-v23/execution.json'
RP = P/'reconstruction-encoded-direct-review-v23.json'
assert not RP.exists(), 'Preserve earlier review'
e = read(EP)
assert e['status'] == 'encoded-samples-ready'
assert len(e['items']) == 228 and len(e['boards']) == 58
assert len(e['commands']) == 2 and all(c['exitCode'] == 0 for c in e['commands'])
s = read(EP.with_name('session.json'))
assert s['closed'] and s['exitCode'] == 0 and s['unifiedExecExitObserved']
boards, items = [], []
for b in e['boards']:
    assert sha(ROOT/b['path']) == b['sha256']
    boards.append({**b, 'directlyViewed': True, 'reviewedAt': stamp()})
for i in e['items']:
    assert sha(ROOT/i['path']) == i['sha256']
    items.append({**i, 'directlyViewedOnBoard': True})
assert sum(b['source'] == 'clean' for b in boards) == 15
assert sum(b['source'] == 'captioned' for b in boards) == 43
assert sum(i['source'] == 'clean' for i in items) == 58
assert sum(i['source'] == 'captioned' for i in items) == 170
gates = {k: False for k in ['allFinalPixelsReviewed', 'allMovingPixelsReviewed',
    'causalFlowApproved', 'finalMixedAsrApproved', 'wholeEpisode60to40Approved',
    'qaApproved', 'collected', 'uploaded']}
r = {
    'reviewedAt': stamp(),
    'scope': 'Reconstruction chapter encoded samples only; continuous playback and final episode approval pending',
    'plan': proof(P/'reconstruction-chapter-review-plan-v23.json'),
    'build': proof(P/'reconstruction-chapter-review-build-v23.json'),
    'execution': proof(EP), 'session': proof(EP.with_name('session.json')),
    'boards': boards, 'items': items,
    'all228SamplesDirectlyRead': True, 'all58BoardsDirectlyRead': True,
    'cleanImages': 58, 'captionedImages': 170,
    'captionCuesReviewed': list(range(169, 195)),
    'sampledCaptionClearanceApproved': True, 'sourceConditionLabelApproved': True,
    'findings': [
        'Clean001-015 and captioned001-043 all directly read across the continuing task. All26 cue boundary/middle samples,12 cuts and both native intervals reviewed. Sampled diagram labels, footer, captions and source-condition labels are clear.',
        'Same-wall noise variation is separated from actual wall/window boundaries using depth/normal clues. Surface history is rejected after motion/disocclusion;2023 Ray Reconstruction roles are shown without inventing its proprietary architecture.',
        'SR restores output resolution, FG adds displayed frames and RR reconstructs noisy ray effects. Separate projected role blocks and captions preserve these distinctions rather than depicting a single undifferentiated pass.',
        'Cyberpunk33-37.5s split comparison shows moving camera, illuminated ceiling and wet floor. Corresponding red/teal reflected-detail boxes remain on the visible floor at sampled0-2.716667s. The annotation and cue188 are present at local f5471 and absent at f5472; the subsequent condition caveat has no lingering reflection box. Continuous tracking alignment is still pending.',
        'Cyberpunk46-50.62s retains DLSS Off Full RT On and DLSS3.5 Full RT On source FPS labels through the moving market/stair views. These are joint-feature source conditions, not an RR-only speed benchmark or input-latency measurement. Source titles30-32/44-45s and the already-used39-42.2s opening are excluded.',
        'Crop-top200 and black bottom padding preserve the original comparison labels above the fixed bottom-center captions. No sampled presenter, source desktop or caption collision was found.',
        'The guide changes to explanation when it defines comparison targets and a hypothetical matched camera/internal-resolution/exposure test. These diagrams are not counted as actual gameplay or claimed as completed measurements. Full original20-5 and20-6 explanation and all8 KO/EN paragraphs remain preserved.',
        'Black background, white text, warm yellow headings, restrained teal/orange accents and projected top/front/side faces remain visible. Captions stay boxed-white-forest-v1, center960,970,48px,max2lines. All2920321 original PCM samples and0.72s boundary silence preserved; this chapter review does not approve whole-video60:40 or final Nimbus mixed audio.'
    ], **gates,
    'newTts': 0, 'sourceModelsRerendered': 0, 'newGitImages': 0,
    'humanWholeListening': 'pending', 'normalSpeedContinuousPlayback': 'pending',
    'next': 'Read full original/additive MegaLights KO/EN chapter, inspect exact official market footage, then prepare one CPU2 chapter review pair without disturbing GPU research.'
}
RP.write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', 'utf-8')
CP = ROOT/'production/research/game-lighting-history/checkpoint.json'
cp = read(CP)
cp['episode04ReconstructionEncodedDirectReviewV23'] = {
    'path': rel(RP), 'sha256': sha(RP), 'samples': 228, 'boards': 58,
    'captionCues': 26, 'sampledCaptionClearanceApproved': True,
    'sourceConditionLabelApproved': True, **gates}
cp['ownedActiveWork'] = {'status': 'no-active-owned-media-worker', 'next': r['next']}
cp['updatedAt'] = stamp()
tmp = CP.with_suffix('.reconstruction-review-v23.tmp')
tmp.write_text(json.dumps(cp, ensure_ascii=False, indent=2)+'\n', 'utf-8')
tmp.replace(CP)
print(json.dumps({'path': rel(RP), 'sha256': sha(RP), 'samples': 228, 'boards': 58, 'finalApproved': False}))
