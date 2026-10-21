"""Record the directly inspected current M15 final master; human review remains pending."""
import datetime
from polish_common import *

e = Episode('M15')
e.authorized()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
digest = 'a32c846993c01f575ed1601bbf14e5abc04f34ec5407aa3dffe9d280be552b9f'
assert sha(e.D / f'{e.slug}.captioned.mp4') == digest
samples = read(e.H / 'final-pixel-samples.json')
assert samples['captionedMasterSha256'] == digest and len(samples['samples']) == 568
save(e.H / 'visual-review.json', {
    'status': 'passed', 'captionedSha256': digest, 'reviewedAt': now,
    'sampleManifest': rel(e.H / 'final-pixel-samples.json'),
    'directlyInspectedSheets': list(range(1, 49)),
    'directlyInspectedNativeImages': ['0173.png', '0343.png', '0558.png'],
    'coverage': 'All 568 current encoded samples on 48 sheets, with 375px-wide tiles: all 234 caption cues, scene/source joins, representative diagram states and dense observed-guide sequences. Native 1920x1080 vector convention, surface annotation and Lambert worked-example frames inspected. Sampled/dense visual review, not continuous whole-film viewing.',
    'findings': [
        {'scene': '02/05', 'status': 'passed-sampled', 'description': 'Front-surface and wall/background guides track the visible targets, reveal progressively and clear before cuts. No fabricated depth or engine data.'},
        {'scene': '08/14/17', 'status': 'passed-sampled', 'description': 'Aspect-preserving 1600x900 game insets retain native controls above fixed captions. Construction preview and lit-rock guides match visible objects without covering the taught surface.'},
        {'scene': '11/19/21', 'status': 'passed-sampled', 'description': 'Bright/shaded-surface guides follow observed screen motion, preserve the actual tonal difference and clear at their recorded bounds.'},
        {'scene': 'explanations and delivery', 'status': 'passed-sampled', 'description': 'Original white palette, narration order, formulas, direction conventions, worked numeric example, branding and member ending retained. Two-line captions have separate lines and stay within bounds. No new issue found in reviewed frames.'}
    ],
    'browserCheck': {
        'url': 'http://127.0.0.1:9248/projects/game-math-rendering-light/production/local/private-polish-v1/moving-review.html',
        'source': 'current captioned master', 'decodedDimensions': [1920, 1080],
        'browserContainerDurationSeconds': 1142.38, 'videoFrameDurationSeconds': 1142.333333,
        'displayWidths': ['large viewport', '375px'],
        'seekStartSeconds': [194.0, 685.5, 848.0],
        'observedAdvancingSeconds': [202.18, 213.08, 694.50, 703.54, 859.90],
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
cp['ready'] = sorted(set(cp.get('ready', []) + ['M15']))
cp['active'] = [x for x in cp['active'] if x != 'M15']
note = 'M15 master a32c846993c0: all568 encoded samples on48 sheets plus3 native frames inspected. Large/mobile browser playback and3 seeks checked. Technical1080p60/full-decode/frame/audio/caption checks passed; four outputs locally ready for human review. Human approval pending; no upload.'
if note not in cp['completedJobs']:
    cp['completedJobs'].append(note)
cp['nextAction'] = 'M05 and M15 are locally ready for user review. Preserve the existing serialized queue: PID43600 M06, PID60248 M16, PID41764 M18, PID29088 M19, PID67440 M20, PID34688 M13/M14. Inspect each final encoded master before marking ready; do not duplicate or terminate jobs. Polygon legibility source and header-clearance preflight is complete and queued. M07-M12/M17 await the existing source decision. No upload or work beyondM20.'
for job in cp.get('jobs', []):
    path = R / job.get('statusFile', '')
    if path.is_file():
        job.update(read(path))
save(B / 'checkpoint.json', cp)
print('M15 final sampled review recorded; human approval pending')
