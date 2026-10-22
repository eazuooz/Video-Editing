"""Record completed direct visual review of the corrected M08 master."""
import datetime
from polish_common import *

e = Episode('M08')
e.authorized()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
p = e.H / 'final-pixel-difference-review.json'
d = read(p)
assert len(d['changed']) == 122 and len(d['unchanged']) == 934
assert d['changedSheetCount'] == 11
d.update(
    status='passed-direct-changed-pixel-inspection',
    reviewedAt=now,
    directlyInspectedChangedSheets=list(range(1, 12)),
    nativeFrameIndices=[505, 599, 993],
    findings=[
        'All122 changed/unavailable or prior-defect-neighborhood encoded samples on11 sheets directly viewed. Every prior defect neighborhood was re-inspected even if a pixel hash was unchanged.',
        'IG05 landing board line follows the actual deck through landing; IG08 torso line follows waist-to-shoulder during rail approach; IG06 intermediate anchors follow the pushing torso instead of drifting above the head.',
        'Three native1920x1080 repaired states inspected. Labels and fixed captions remain clear; affected labels/lines clear at their planned interval boundaries.',
        'First five current intro/overview samples lacked old hash receipts, so they were directly inspected instead of reused.',
    ],
)
save(p, d)
review = {
    'status': 'passed', 'reviewedAt': now, 'humanReview': 'pending',
    'readyForHumanReview': True,
    'captionedSha256': d['captionedMasterSha256'],
    'sampleCount': 1056,
    'pixelReviewMethod': 'exact-pixel-reuse-plus-direct-difference-review',
    'pixelDifferenceEvidence': rel(p),
    'directlyInspectedSampleCount': 122,
    'reusedIdenticalPixelCount': 934,
    'directlyInspectedDifferenceSheets': list(range(1, 12)),
    'nativeFrameIndices': [505, 599, 993],
    'findings': d['findings'] + [
        '934 current final PNGs exactly match previously directly inspected pixels by SHA256. Previous88-sheet inspection covered all original1056 sample states; only identical unaffected pixels reuse that evidence.',
        'Original detailed lesson, script, caption words/cues, recovered compressed audio, original frame counts and white explanation palette are preserved.',
        'Gameplay direction marks are editorial screen-space guides rather than measured internal3D axes.',
    ],
    'browserPlayback': {
        'status': 'passed-selected-native-playback',
        'page': rel(e.O / 'final-playback-check.html'),
        'masterQuery': d['captionedMasterSha256'][:16],
        'checks': [
            'Current corrected final file played at451.8–454.3s and506.5–509.2s with start/end observations.',
            '375px playback at755.4–757.4s, and actual Atan2/hypot formula scene from145s with captions observed.',
            'Large-size matrix-to-quaternion explanation and its next gameplay transition observed from402s.',
            'Final summary-to-membership ending checked from824s.',
        ],
        'scope': 'Selected native playback and start/end states only; not every-frame or whole-film listening.',
    },
    'limitations': [
        'Internal visual review is not human final approval.',
        'Original uncompressed recording unavailable. Recovered baseline compressed audio and its decodedPCM are unchanged; this is not an originalPCM identity claim.',
        'No new TTS, lesson rewrite, platform upload or public action.',
    ],
}
save(e.H / 'visual-review.json', review)
print('M08 corrected visual review recorded; human review pending.')
