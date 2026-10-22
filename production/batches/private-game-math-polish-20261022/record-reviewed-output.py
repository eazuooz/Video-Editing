"""Bind an explicit manual review record to unchanged current outputs.

This does not inspect video or generate a pass. A reviewer must supply actual
observations in a version-bound JSON record after inspecting the encoded master.
"""
import datetime
import sys
from polish_common import *

e = Episode(sys.argv[1])
e.authorized()
review = read(Path(sys.argv[2]))
assert review['status'] == 'passed' and review['humanReview'] == 'pending'
assert review['readyForHumanReview'] is True
assert review['captionedSha256'] == sha(e.D / f'{e.slug}.captioned.mp4')
samples = read(e.H / 'final-pixel-samples.json')
assert samples['captionedMasterSha256'] == review['captionedSha256']
assert review['sampleCount'] == len(samples['samples'])
if review.get('pixelReviewMethod') == 'exact-pixel-reuse-plus-direct-difference-review':
    difference = read(R / review['pixelDifferenceEvidence'])
    assert difference['status'] == 'passed-direct-changed-pixel-inspection'
    assert difference['captionedMasterSha256'] == review['captionedSha256']
    assert difference['currentSampleManifestSha256'] == sha(e.H / 'final-pixel-samples.json')
    assert difference['directlyInspectedChangedSheets'] == list(range(1, difference['changedSheetCount'] + 1))
    assert review['directlyInspectedSampleCount'] == len(difference['changed'])
    assert review['reusedIdenticalPixelCount'] == len(difference['unchanged'])
    prior = read(R / difference['priorPixelHashRecord'])
    assert sha(R / difference['priorPixelHashRecord']) == difference['priorPixelHashRecordSha256']
    prior_manifest = read(e.H / 'initial-final-pixel-samples.json')
    prior_review = read(R / difference['priorReview'])
    assert prior_review['sampleManifestSha256'] == sha(e.H / 'initial-final-pixel-samples.json')
    assert prior_review['directlyInspectedSheets'] == list(range(1, prior_manifest['sheets'] + 1))
    old = {x['seconds']: x for x in prior['samples']}
    for row in difference['unchanged']:
        assert old[row['seconds']]['imageSha256'] == row['imageSha256'] == sha(R / row['image'])
    combined = difference['unchanged'] + difference['changed']
    assert sorted(x['index'] for x in combined) == list(range(len(samples['samples'])))
    for row in combined:
        assert sha(R / row['image']) == row['imageSha256']
        assert row['seconds'] == samples['samples'][row['index']]['seconds']
    pixel_note = f"{len(difference['changed'])} newly inspected pixels plus {len(difference['unchanged'])} exactly unchanged previously inspected pixels"
else:
    assert review['directlyInspectedSheets'] == list(range(1, samples['sheets'] + 1))
    pixel_note = f"all {review['sampleCount']} final samples on {samples['sheets']} sheets"
qa = read(e.H / 'technical-qa.json')
assert all(x['fullDecode'] and x['frames'] > 0 for x in qa['outputs'])
assert next(x['sha256'] for x in qa['outputs'] if x['kind'] == 'captioned') == review['captionedSha256']
save(e.H / 'visual-review.json', review)
qa['directVisualReview'] = rel(e.H / 'visual-review.json')
save(e.H / 'technical-qa.json', qa)
outputs = read(e.H / 'outputs.json')
outputs['technicalQa'] = rel(e.H / 'technical-qa.json')
outputs['visualQa'] = rel(e.H / 'visual-review.json')
save(e.H / 'outputs.json', outputs)
cp = read(B / 'checkpoint.json')
cp['updatedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
cp['ready'] = sorted(set(cp.get('ready', []) + [e.id]))
cp['active'] = [x for x in cp['active'] if x != e.id]
note = f"{e.id} master {review['captionedSha256'][:12]}: {pixel_note}; native frames and browser playback inspected. Technical checks passed; four local outputs ready for human review. No new voice or upload."
if note not in cp['completedJobs']:
    cp['completedJobs'].append(note)
cp['nextAction'] = 'Ready: ' + '/'.join(cp['ready']) + '. Preserve existing serialized workers and inspect remaining encoded masters. M07-M12/M17 await the existing source decision. No duplicate/forced-killed jobs, upload, deletion or work beyond M20.'
for job in cp.get('jobs', []):
    path = R / job.get('statusFile', '')
    if path.is_file():
        job.update(read(path))
save(B / 'checkpoint.json', cp)
print(e.id, 'manual final review recorded; human approval pending')
