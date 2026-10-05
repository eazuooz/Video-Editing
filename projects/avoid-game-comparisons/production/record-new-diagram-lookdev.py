"""Record direct CUA lookdev inspection; this does not approve final cues/timing."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
MC = ROOT / 'motion-canvas/src/projects/avoid-game-comparisons'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
names = ['13', '14', '06-2', '06-4', '10-2', '10-4', '12-2', '15-3']
observations = {
    '13': 'Movement target, changed direction and an unresolved condition are separate white cards; both arrowheads explicitly compare them.',
    '14': 'Observed red chest/card result is separated from the undecided connection condition and listener readback; this is our explanation, not a developer rule.',
    '06-2': 'Curve/surface and ice/support are compared without claiming identical controls or all terrain rules.',
    '06-4': 'Descending/contact space and ascending/direction now match the actual fourth paragraph about movement on the printed mug surface.',
    '10-2': 'Two different vehicle excerpts are compared; the diagram does not join them into one continuous pursuit.',
    '10-4': 'Accessibility demonstration context is separated from default difficulty and universal portal visibility.',
    '12-2': 'Visible device entry/firing is separated from unconfirmed entry cost and win conditions.',
    '15-3': 'Movement and an attack target are compared as separate actions; edited excerpts do not establish universal combat rules.',
}
result = {
    'schemaVersion': 1, 'reviewedAt': datetime.now(timezone.utc).isoformat(),
    'status': 'eight-new-diagram-layouts-directly-reviewed-final-timing-captions-pending',
    'method': 'CUA screenshots of own Motion Canvas lookdev and own documented Player/Stage review UI; visible pixels read directly.',
    'fixedCaptionGuide': {'style': 'boxed-white-forest-v1', 'centerPx': [960, 970], 'mcCenter': [0, 430], 'maximumGuideLines': 2},
    'observed': [{'id': n, 'localOnlyScreenshot': str((BASE / 'lookdev-local/new-diagrams' / (n + '.png')).relative_to(ROOT)).replace('\\', '/'),
                  'screenshotSha256': sha(BASE / 'lookdev-local/new-diagrams' / (n + '.png')),
                  'visibleReading': observations[n], 'guideOverlapObserved': False,
                  'whiteCardsDepthShadowArrowsAndLabelsReadable': True} for n in names],
    'codeHashes': {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in
                   [MC / 'scenes/cue-diagrams.tsx', MC / 'scenes/concept-diagrams.tsx', MC / 'cue-lookdev-project.ts', MC / 'cue-lookdev-review.html']},
    'corrections': ['Changed the cue comparison arrow to two heads and added the comparison label to avoid implied causality.',
                    'Replaced unrelated cost/time/fuel labels in06-4 with ascent/descent/contact-space labels matching its preserved narration.'],
    'originalSixLookdevPreserved': True, 'sourceOrPcmChanged': False,
    'silentLookdevIsFinalVideo': False, 'newGitImages': 0,
    'finalTimingApproved': False, 'allActualCuePixelsReviewed': False,
    'finalDiagramCaptionPixelsReviewed': False, 'finalMixApproved': False,
    'humanWholeListening': 'pending', 'humanPronunciationApproval': 'pending',
}
(BASE / 'new-diagram-lookdev-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'reviewed': len(names), 'newGitImages': 0, 'finalApproval': False}))
