"""Reuse previously inspected pixels only on exact PNG hash equality.

Produces a manual-review queue; never grants a visual pass.
"""
from PIL import Image, ImageDraw, ImageFont
from polish_common import *

e = Episode('M08')
e.authorized()
current = read(e.H / 'final-pixel-samples.json')
old = read(e.H / 'initial-final-pixel-image-hashes.json')
findings = read(e.H / 'initial-final-visual-findings.json')
assert old['priorSampleManifestSha256'] == sha(e.H / 'initial-final-pixel-samples.json')
assert findings['sampleManifestSha256'] == old['priorSampleManifestSha256']
assert findings['directlyInspectedSampleCount'] == 1056
assert current['captionedMasterSha256'] == sha(e.D / f'{e.slug}.captioned.mp4')
assert current['captionedMasterSha256'] != old['priorCaptionedSha256']
lookup = {r['seconds']: r for r in old['samples']}
unchanged, changed = [], []
for index, row in enumerate(current['samples']):
    p = R / row['image']
    receipt = read(p.with_suffix('.json'))
    assert receipt == {k: row[k] for k in ['masterSha256', 'seconds', 'reasons']}
    record = {**row, 'index': index, 'imageSha256': sha(p)}
    prior = lookup.get(row['seconds'])
    defect_nearby = any(a - 1 <= row['seconds'] <= z + 1
                        for a, z in (f['globalSeconds'] for f in findings['findings']))
    if prior and prior['imageSha256'] == record['imageSha256'] and not defect_nearby:
        unchanged.append(record)
    else:
        record['requiresReinspectionReason'] = 'prior-defect-neighborhood' if defect_nearby else 'changed-or-unavailable-old-pixel'
        changed.append(record)
out = e.O / 'final-repair-difference-review'
out.mkdir(exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 15)
for i in range(0, len(changed), 12):
    sheet = Image.new('RGB', (1500, 720), '#222222')
    for j, row in enumerate(changed[i:i+12]):
        tile = Image.new('RGB', (375, 240), '#222222')
        im = Image.open(R / row['image']).convert('RGB').resize((375, 211), Image.Resampling.LANCZOS)
        tile.paste(im, (0, 29))
        ImageDraw.Draw(tile).text((4, 2), f"{row['index']:04d} {row['seconds']:.2f}s", fill='white', font=font)
        sheet.paste(tile, (j % 4 * 375, j // 4 * 240))
    sheet.save(out / f'sheet-{i//12+1:03d}.jpg', quality=94)
save(e.H / 'final-pixel-difference-review.json', {
    'status': 'await-direct-changed-pixel-inspection',
    'captionedMasterSha256': current['captionedMasterSha256'],
    'currentSampleManifestSha256': sha(e.H / 'final-pixel-samples.json'),
    'priorPixelHashRecord': rel(e.H / 'initial-final-pixel-image-hashes.json'),
    'priorPixelHashRecordSha256': sha(e.H / 'initial-final-pixel-image-hashes.json'),
    'priorReview': rel(e.H / 'initial-final-visual-findings.json'),
    'unchanged': unchanged, 'changed': changed,
    'changedSheetCount': (len(changed) + 11) // 12,
    'changedSheetDirectory': rel(out),
    'limitations': 'Exact unchanged encoded PNG pixels reuse prior actual inspection. Every nonmatching/unavailable prior pixel is queued for new direct inspection. Not full-film human viewing/listening.',
})
print('Identical reviewed pixels:', len(unchanged), 'new inspection:', len(changed), flush=True)
