"""Record directly inspected partial frames; do not certify a whole master."""
import datetime
from polish_common import *

e = Episode('M09'); e.authorized()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
still = read(e.H/'observed-guide-preflight.json')
moving = read(e.H/'moving-available-guide-preflight.json')
sample = read(e.H/'remaining-encoded-guide-samples.json')
guide = read(e.H/'observed-guide-composition.json')
assert still['planSha256'] == moving['planSha256'] == guide['planSha256'] == sha(R/guide['plan'])
assert still['assSha256'] == moving['assSha256'] == guide['globalAssSha256'] == sha(R/guide['globalAss'])
assert len(still['samples']) == 29 and len(sample['samples']) == 43
assert len(moving['clips']) == 7
for frame in still['samples']:
    assert sha(R/frame['image']) == frame['imageSha256']
for frame in sample['samples']:
    assert sha(R/frame['path']) == frame['sha256']
    clip = next(c for c in moving['clips'] if c['name'] == frame['clip'])
    assert frame['clipSha256'] == clip['sha256'] == sha(R/clip['path'])
still.update(status='passed-still-preflight', reviewedAt=now,
    directInspection='All29 composited states inspected at375px on4 sheets; native1920x1080 frames05@6.5,08@3,LG02@4.46,LG03@2.38 also inspected. Fixed captions and native controls remain clear. Partial scenes only.',
    fullMasterReady=False, finalMovingReview='whole-master-pending')
save(e.H/'observed-guide-preflight.json', still)
for clip in moving['clips']:
    if clip['scene'] != '02':
        clip['currentPixels'] = 'Native-speed browser start/end states observed; current intermediate encoded frames inspected at375px. Guide hidden outside verified cue windows. Not continuous listening or whole-master approval.'
moving.update(status='selected-playback-and-temporal-samples-inspected', reviewedAt=now,
    temporalSampleEvidence=rel(e.H/'remaining-encoded-guide-samples.json'),
    limitations='Seven short windows only; five new windows sampled at quarter-second steps. Original narration preserved, but complete encoded episode audiovisual QA is still pending.',
    fullMasterApproval=False)
save(e.H/'moving-available-guide-preflight.json', moving)
sample.update(status='passed-partial-encoded-frame-inspection', reviewedAt=now,
    manifestSha256=sha(e.H/'moving-available-guide-preflight.json'),
    inspected='All43 encoded states on4 sheets directly inspected at375px. Endpoints follow observed hand/rock positions; screen-space straight guides are editorial, not measured world axes or forces.',
    fullMasterApproval=False)
save(e.H/'remaining-encoded-guide-samples.json', sample)
review = read(e.H/'available-guides-review.json')
review.update(reviewedAt=now, sampleCount=29, sheetCount=4,
    preflightSha256=sha(e.H/'observed-guide-preflight.json'),
    selectedPlaybackSha256=sha(e.H/'moving-available-guide-preflight.json'),
    restoredSceneCount=5, encodedSamples=rel(e.H/'remaining-encoded-guide-samples.json'),
    encodedSamplesSha256=sha(e.H/'remaining-encoded-guide-samples.json'),
    additionalSourceReviews=[rel(e.H/f'uncle-remaining-source-review-{sid}.json') for sid in ['05','08','LG02','LG03']],
    findings=[
        'Current five available FHD gameplay slots preserve exact original scene frames, baseline narration and sequence.',
        'Four new cuts:183 one-second captioned source states and52 dense source target states directly inspected before adoption; unsuitable dark/reset intervals rejected.',
        'All29 current composited states and43 additional encoded temporal samples inspected. Five new short playback windows observed at native-speed start/end; no continuous full listening claim.',
        '05 marks the two endpoints; LG02/LG03 show a labeled screen connection;08 shows changing screen slope. No fabricated world length, axis or collision implementation.',
        'LG02 hand extension is separately tracked. Guides clear before cuts or when verified target visibility ends. Fixed captions and game UI remain clear.',
        'LG01 Portal2 official-demo native FHD and whole-master QA remain unresolved.'
    ], fullMasterReady=False, humanReview='pending', newTts=False, timelineChanged=False)
save(e.H/'available-guides-review.json', review)
print('M09 partial review recorded:5 restored slots,29 stills,43 additional encoded states; no full-master approval.')
