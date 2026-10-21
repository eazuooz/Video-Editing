"""Record directly inspected repaired M06 output; human review remains pending."""
import datetime
from polish_common import *

e = Episode('M06')
e.authorized()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
digest = '5f843bb57ed7459901760bb40718ae8f915bad15b6787fcb9abfe308250d3235'
assert sha(e.D / f'{e.slug}.captioned.mp4') == digest
samples = read(e.H / 'final-pixel-samples.json')
assert samples['captionedMasterSha256'] == digest and len(samples['samples']) == 561
save(e.H / 'visual-review.json', {
    'status': 'passed', 'captionedSha256': digest, 'reviewedAt': now,
    'sampleManifest': rel(e.H / 'final-pixel-samples.json'),
    'directlyInspectedSheets': list(range(1, 48)),
    'directlyInspectedNativeImages': ['0074.png', '0209.png', '0358.png', '0405.png'],
    'coverage': 'All 561 current encoded samples on 47 sheets, with 375px-wide tiles: all 246 caption cues, scene/source joins, representative diagram states and dense QC20 guide states. Native 1920x1080 N06/N07/N08 formula and QC20 inset frames inspected. Sampled visual review and selected browser playback, not continuous whole-film viewing.',
    'findings': [
        {'scene': 'N06/N07/N08', 'status': 'passed-sampled', 'description': 'Nine word-preserving multiline beats now use 64px baseline advance. Cross product, log/exp and one-sided versus two-sided product labels are distinct and remain above fixed captions.'},
        {'scene': 'QC20', 'status': 'passed-sampled', 'description': 'Aspect-preserving 1600x900 inset keeps original rotation controls above the caption region. The red direction guide follows the visible component during the sampled rotation states.'},
        {'scene': 'Riders Republic / Trailmakers / Besiege examples', 'status': 'passed-sampled', 'description': 'Original observed body, wheel, wing and nose guides retained and cleared at source cuts. Editorial screen guides remain distinguished from unverified internal game coordinates and measurements.'},
        {'scene': 'explanations and delivery', 'status': 'passed-sampled', 'description': 'Original white palette, aircraft/axis diagrams, words, order, worked calculations, branding and member ending retained. Repaired subtitle/header divider and fixed two-line captions remain separated in inspected frames.'}
    ],
    'browserCheck': {
        'url': 'http://127.0.0.1:9248/projects/game-math-quaternion-calculations-v3/production/local/private-polish-v1/moving-review.html',
        'source': 'current captioned master', 'decodedDimensions': [1920, 1080],
        'browserContainerDurationSeconds': 1285.97, 'videoFrameDurationSeconds': 1285.916667,
        'displayWidths': ['large viewport', '375px'],
        'seekStartSeconds': [154.5, 261.6, 446.7],
        'observedAdvancingSeconds': [173.86, 282.01, 467.92, 175.46],
        'playbackAndSeek': 'passed', 'audio': 'muted; no listening claim', 'temporaryTabClosed': True
    },
    'wholeListening': 'pending-user; recovered AAC audio unchanged by decoded hash, original PCM was not recovered',
    'humanReview': 'pending', 'readyForHumanReview': True
})
qa = read(e.H / 'technical-qa.json')
qa['directVisualReview'] = rel(e.H / 'visual-review.json')
save(e.H / 'technical-qa.json', qa)
outputs = read(e.H / 'outputs.json')
outputs['technicalQa'] = rel(e.H / 'technical-qa.json')
outputs['visualQa'] = rel(e.H / 'visual-review.json')
save(e.H / 'outputs.json', outputs)
cp = read(B / 'checkpoint.json')
cp['updatedAt'] = now
cp['ready'] = sorted(set(cp.get('ready', []) + ['M06']))
cp['active'] = [x for x in cp['active'] if x != 'M06']
note = 'M06 master5f843bb57ed7: all561 final samples on47 sheets and4 native frames inspected. Large/mobile playback and3 seeks passed. Nine multiline beats and QC20 caption clearance repaired. Technical1080p60/full-decode/frame/audio/caption checks passed; four outputs locally ready for human review. Human approval pending; no upload.'
if note not in cp['completedJobs']:
    cp['completedJobs'].append(note)
cp['nextAction'] = 'M05/M06/M15 locally ready for user review. Preserve serialized queue: PID60248 M16, PID41764 M18, PID29088 M19, PID67440 M20, PID34688 M13/M14. Inspect current final encoded masters before marking ready. No duplicate jobs or forced termination. M07-M12/M17 await existing source decision; no upload or work beyondM20.'
for job in cp.get('jobs', []):
    path = R / job.get('statusFile', '')
    if path.is_file():
        job.update(read(path))
save(B / 'checkpoint.json', cp)
print('M06 final sampled review recorded; human approval pending')
