"""Record the actual direct read of all461 framing trial images, without final approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = datetime.now(timezone.utc).isoformat()
state_path = BASE / 'measured-edit-v3/cue-review-local-v1/execution.json'
state = read(state_path)
assert state['exitCode'] == 0 and state['completedCuts'] == 108
assert len(state['images']) == 461 and len(state['sheets']) == 77
# Each entry below was read in the rendered contact sheets. The complete sheet
# inventory locks the unflagged sampled observations as well. These samples do
# not approve unsampled motion, final composite pixels or the full audio mix.
issues = [
 ([20], 'focus-occlusion', 'Falling Pepper avatar is behind the fixed caption; reframe this source shot.'),
 ([70], 'focus-occlusion', 'The hanging/falling red enemy crosses the caption; retain both the avatar and named enemy above it.'),
 ([113], 'focus-occlusion', 'The entry/glow reaches the caption area; reframe without hiding the entry action.'),
 ([131], 'source-text-overlap', 'The printed book footer intersects the two-line caption.'),
 ([165], 'source-dialogue', 'A source dialogue box is visible at the sampled opening. Inspect the exact boundary or crop the underlying shot.'),
 ([172,173], 'focus-occlusion', 'Pepper lies behind the two-line caption at the bottom center.'),
 ([178,182], 'focus-occlusion', 'Rocket avatar/boots touch or pass under the caption and the top crop clips the lower action.'),
 ([189,190,191], 'source-UI-overlap', 'Rocket fuel/puck UI is behind the fixed caption; reframe the underlying cup shot.'),
 ([203], 'focus-occlusion', 'Mine entry ring extends into the caption area.'),
 (list(range(210,224)), 'source-text-overlap', 'Mine printed book footer overlaps multiple narration cues. Inspect a stronger framing while retaining key/tilt movement.'),
 ([258,259,260,261], 'focus-and-UI-occlusion', 'The colored-ball launcher and some health UI are behind the caption; keep the observed launcher visible.'),
 ([268,269], 'word-action-alignment', 'A cue naming Pepper water vehicles begins while the Plucky boat is still visible. Align the actual spoken game-name boundary.'),
 ([277,278], 'focus-occlusion', 'The rocket avatar is clipped or covered near the bottom. A top crop is unsuitable here.'),
 ([319,320], 'focus-occlusion', 'The dark-path avatar is partly or entirely behind the fixed caption.'),
 ([350,351], 'focus-occlusion', 'The desk avatar feet/action enter the caption box.'),
 ([367,368], 'focus-occlusion', 'The lava movement is hidden by a wide two-line caption.'),
 ([375], 'focus-occlusion', 'The mine fight reaches the caption area.'),
 ([376], 'source-editorial-transition', 'The last encoded image contains two different scenes blended. Inspect exact native transition and remove editorial dissolve frames.'),
 ([400,401], 'word-action-alignment', 'The rocket-ascent cue currently overlays desk combat before ascent appears at the end of action71. Reallocate distinct active intervals to the spoken word time.'),
 ([452,453], 'focus-occlusion', 'The cave avatar crosses behind the fixed caption at the bottom.'),
 ([458,459,460], 'transition-context-pending', 'The mine book/desk/flat-surface representation blends during entry. Inspect raw continuity to distinguish in-game transition from source edit; do not assume either.'),
]
observed = []
for indices, kind, finding in issues:
    observed.append({'kind': kind, 'finding': finding, 'status': 'repair-or-exact-context-review-required',
        'samples': [{**state['images'][i-1], 'imageIndex': i} for i in indices]})
for record in state['images']:
    assert sha(ROOT / record['path']) == record['sha256']
    record.update(directlyRead=True, directlyReadAt=now, finalApproved=False)
for record in state['sheets']:
    assert sha(ROOT / record['path']) == record['sha256']
    record.update(directlyRead=True, directlyReadAt=now)
state.update(status='closed-all461-trial-images-directly-read-corrections-required',
             allTrialImagesDirectlyRead=True, allCaptionPixelsReviewed=False, framingApproved=False,
             sessionId=32587, updatedAt=now)
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
review = {'schemaVersion': 1, 'reviewedAt': now,
    'status': 'all-sampled-cue-and-encoded-boundary-images-read-with-explicit-corrections',
    'execution': rel(state_path), 'executionSha256': sha(state_path),
    'plan': 'projects/avoid-game-comparisons/production/measured-edit-v3/plan.json',
    'planSha256': state['planSha256'], 'captionLayoutSha256': state['captionLayoutSha256'],
    'cuts': 108, 'sampledImages': 461, 'sheets': 77,
    'sheetsRead': state['sheets'], 'imagesRead': state['images'], 'issues': observed,
    'additionalWordAlignmentCorrection': {'scene': '15', 'paragraph': 3,
        'finding': 'Retained narration names water/lava movement before enemy firing, whereas candidate v3 orders water/boss/lava.',
        'plannedCorrection': 'Reorder distinct water/lava/boss excerpts, preserving all current PCM and all native frames.'},
    'sampledGeneralObservations': [
        'Fixed bottom-center white forest captions remain legible in one/two lines; no narration was moved to the top or side.',
        'Source context labels distinguish development footage and accessibility demonstrations, including the two ON settings.',
        'The chest/card image is visibly present in14p1 at the retained source boundary.',
        'Many sampled actions have clear avatar/target visibility, but the listed occlusions prevent a final approval.',
        'KWD action98 is full-screen active final breaking VFX; the earlier inset claim is rejected in the pilot review.',
    ],
    'scope': 'Directly read all77 local contact sheets and their461 tiles. This is a sampled framing/word-alignment review, not every-frame or rendered-final approval.',
    'allCurrentPcmPreserved': True, 'sourceAudioStreams': 0, 'newGitImages': 0,
    'finalTimingApproved': False, 'allFinalCaptionPixelsApproved': False,
    'finalVideoRendered': False, 'humanWholeListening': 'pending'}
(BASE / 'all-actual-cue-trial-direct-review-v3.json').write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'readImages':461,'readSheets':77,'issueGroups':len(issues),'finalApproved':False,'newGitImages':0}))
