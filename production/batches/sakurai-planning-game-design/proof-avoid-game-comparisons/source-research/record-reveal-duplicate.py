"""Record the directly inspected duplicate trailer; keep all image/media files local."""
import json, hashlib, datetime
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[5]
BASE = 'production/batches/sakurai-planning-game-design'
PROOF = BASE + '/proof-avoid-game-comparisons'
SR = PROOF + '/source-research'
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads((ROOT / p).read_text(encoding='utf-8-sig'))
def write(p, value): (ROOT / p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()

discovery = read(SR + '/discovery-pepper-reveal.json')
new_dir = ROOT / PROOF / 'research-local/game-discovery-pepper-reveal/dkxNejWRGsA'
old_dir = ROOT / PROOF / 'research-local/game-discovery/z4utn4Sm6SY'
assert old_dir.exists(), old_dir
rows = []
for i in range(1, 73):
    name = f'frame-{i:04d}.jpg'
    a = np.asarray(Image.open(new_dir / name).convert('RGB'), dtype=np.float64)
    b = np.asarray(Image.open(old_dir / name).convert('RGB'), dtype=np.float64)
    assert a.shape == b.shape
    rows.append({'seconds': i - 1, 'meanAbsoluteRgbDifference': round(float(np.abs(a-b).mean()), 6)})
write(SR + '/pepper-reveal-sampled-comparison.json', {
    'schemaVersion': 1, 'comparedAt': NOW,
    'sourceIds': ['dkxNejWRGsA', 'z4utn4Sm6SY'],
    'sampling': '72 directly reviewed one-second discovery frames at matching PTS; supplemental pixel comparison, not a full-frame identity claim',
    'rows': rows, 'duplicateDecisionMethod': 'Direct visual reading of all five sheets for each source, supported by matching action/cut sequence and sampled RGB differences. Not a numeric-threshold-only decision.'
})
sheet_paths = discovery['sources'][0]['sheets'] + [str(p.relative_to(ROOT)).replace('\\', '/') for p in sorted(old_dir.glob('sheet-*.jpg'))]
review = {
    'schemaVersion': 1, 'reviewedAt': NOW, 'newSourceId': 'dkxNejWRGsA',
    'existingSourceId': 'z4utn4Sm6SY',
    'status': 'excluded-duplicate-gameplay-different-end-card',
    'directlyReadSheets': [{'path': p, 'sha256': sha(p)} for p in sheet_paths],
    'observations': [
        'Both five-sheet sequences show the same yellow-terrain curves/columns, water, lava launches, separated yellow islands, crab introduction, gun/cart montage, large machine, saw/rope terrain, cannon and boss flashes at matching seconds.',
        '0-4 publisher/intro; 30-31 marketing text; 32 black; 33-37 staged idle; 54-59 title cards; 60 black; 61-68 giant-face/avatar staging do not provide fresh quota actions.',
        '69-71 differs in platform/date end-card text: historical Grinding in2023 versus the later console announcement. A different source ID/date/title is not a new gameplay sequence.',
        'All new72 and existing72 sampled frames were visually read, with small image-encoding differences at0-68 and substantial end-card text differences at69-71. Native re-extraction would not add concept-matched unique footage.'
    ],
    'approvedNewUniqueActualSeconds': 0, 'approvedIntervals': [],
    'nativeExtractionNeeded': False, 'sourceAudioUsed': False,
    'sourceFileSha256': 'abd96cc86e6705df93007fba4ef22b9840ac56c0b1667b6c8f99e9f7122171d6',
    'uiDate': '2022-11-10', 'metadataUploadDate': '20221109',
    'dateCaution': 'UI/local-date and metadata-date observations preserved independently; no current release claim.',
    'sampleComparison': SR + '/pepper-reveal-sampled-comparison.json',
    'localMediaAndImagesPreserved': True, 'newGitImages': 0
}
write(SR + '/direct-pepper-reveal-review.json', review)
for p in [PROOF + '/source-candidates-and-usage-review.json', 'projects/avoid-game-comparisons/sources/game-candidates.json']:
    d = read(p)
    d['additionalSourceReviews'] = [x for x in d.get('additionalSourceReviews', []) if x.get('videoId') != 'dkxNejWRGsA'] + [{
        'videoId': 'dkxNejWRGsA', 'game': 'Pepper Grinder',
        'status': review['status'], 'reason': 'Same gameplay/action sequence as already reviewed z4utn4Sm6SY; only end-card announcement differs.',
        'directReview': SR + '/direct-pepper-reveal-review.json',
        'newUniqueActualSeconds': 0, 'sourceAudioUsed': False
    }]
    d['updatedAt'] = NOW
    write(p, d)
acq = read(SR + '/acquisition-pepper-reveal.json')
acq['directActionReview'] = SR + '/direct-pepper-reveal-review.json'
acq['uniqueFootageDecision'] = review['status']
for result in acq['results']: result['directActionReview'] = review['status']
write(SR + '/acquisition-pepper-reveal.json', acq)
print(json.dumps({'review': SR + '/direct-pepper-reveal-review.json', 'sheets': len(sheet_paths), 'framesCompared': len(rows), 'newUniqueActualSeconds': 0, 'newGitImages': 0}))
