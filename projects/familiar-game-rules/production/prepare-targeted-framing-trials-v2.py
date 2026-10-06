"""Compare targeted source compositions using already extracted native pixels.

This does not adopt a crop, change any narration, or approve source motion.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
SOURCE = PROOF / 'word-cue-input-trials-v1.json'
REVIEW = PROOF / 'word-cue-input-direct-progress-v1.json'
OUT = ROOT / 'shared/output/familiar-game-rules/research/targeted-framing-trials-v2'
DEST = PROOF / 'targeted-framing-trials-v2.json'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()

parser = argparse.ArgumentParser()
parser.add_argument('--resource', required=True)
args = parser.parse_args()
resource = read(ROOT / args.resource)
assert resource['ownHeavyJobs'] == 0 and resource['cpuLoadPercent'] < 85
assert (datetime.now(timezone.utc) - datetime.fromisoformat(resource['observedAt'].replace('Z', '+00:00'))).total_seconds() < 240
source = read(SOURCE)
review = read(REVIEW)
assert review['evidenceSha256'] == sha(SOURCE) and review['allInputBoardsDirectlyRead']
assert not DEST.exists() and not OUT.exists()
(OUT / 'boards').mkdir(parents=True)
(OUT / 'captioned').mkdir()

targets = {
    'q8iWixSvfsI': [1110, 1139, 1168, 1199, 1285],
    'zdqK0zC53CE': [1663, 1686, 1709, 1756, 1777, 1816, 2820],
    'BW0uTZ6-dsM': [1470, 1477, 1530, 1596, 2220, 2279, 2386, 3480, 3510, 3540],
    'zxzPcsI8l2o': [300, 310, 319],
    'YIVtT7SJrMM': [1217, 1335, 2261, 2340, 2548, 2641, 2700, 4395, 4614, 5658, 5707, 5880, 6216, 6251],
    'q-AsYZCdpts': [2256, 2466, 3045, 3075, 1865, 1943],
}
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)
label = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
tiles = []
chosen = []
for video_id, frames in targets.items():
    for frame in frames:
        matches = [s for s in source['samples'] if s['sourceVideoId'] == video_id and s['literalKo']]
        sample = min(matches, key=lambda s: abs(s['sourceFrame'] - frame))
        assert abs(sample['sourceFrame'] - frame) <= 15, (video_id, frame)
        if sample['index'] not in [s['index'] for s in chosen]:
            chosen.append(sample)

for sample in chosen:
    native_path = ROOT / sample['nativePath']
    assert sha(native_path) == sample['nativeSha256']
    for mode, crop in [('native-full-frame', [0, 0, 1920, 1080]), ('bottom120-trial', [160, 180, 1600, 900])]:
        with Image.open(native_path) as raw:
            assert raw.size == (1920, 1080)
            x, y, width, height = crop
            im = raw.crop((x, y, x + width, y + height)).resize((1920, 1080), Image.Resampling.LANCZOS).convert('RGB')
        caption_width = round(font.getlength(sample['literalKo']) + 44)
        left = 960 - caption_width / 2
        top = 928
        draw = ImageDraw.Draw(im)
        draw.rectangle((left + 14, top + 14, left + caption_width + 14, top + 98), fill='#073c32')
        draw.rectangle((left, top, left + caption_width, top + 84), fill='white', outline='#161b18', width=3)
        draw.text((960, top + 11), sample['literalKo'], font=font, fill='#080b09', anchor='mt')
        dest = OUT / 'captioned' / f'{sample["index"]:05}-{mode}.jpg'
        im.save(dest, quality=95)
        tiles.append(dict(index=len(tiles)+1, sampleIndex=sample['index'], cutId=sample['cutId'],
                          outputFrame=sample['outputFrame'], sourceVideoId=sample['sourceVideoId'], sourceFrame=sample['sourceFrame'],
                          nativePath=sample['nativePath'], nativeSha256=sample['nativeSha256'], mode=mode, sourceCrop=crop,
                          literalKo=sample['literalKo'], captionIndex=sample['captionIndex'], captionBox=[left, top, caption_width, 84],
                          path=rel(dest), sha256=sha(dest), directlyRead=False))
boards = []
for start in range(0, len(tiles), 6):
    board = Image.new('RGB', (1920, 1710), 'white')
    draw = ImageDraw.Draw(board)
    group = tiles[start:start + 6]
    for i, tile in enumerate(group):
        x, y = i % 2 * 960, i // 2 * 570
        draw.text((x+6, y+1), f'{tile["sampleIndex"]} {tile["sourceVideoId"]}@{tile["sourceFrame"]} {tile["mode"]} cue{tile["captionIndex"]}', font=label, fill='black')
        with Image.open(ROOT / tile['path']) as im:
            board.paste(im.resize((960, 540)), (x, y+30))
    dest = OUT / 'boards' / f'{len(boards)+1:02}.jpg'
    board.save(dest, quality=95)
    boards.append(dict(index=len(boards)+1, path=rel(dest), sha256=sha(dest), tileIndices=[t['index'] for t in group], directlyRead=False))

evidence = dict(schemaVersion=1, slug='familiar-game-rules', createdAt=now(), pid=os.getpid(),
                commandLine=[os.sys.executable, *os.sys.argv], cpuThreads=1, gpuJobs=0, resourceObservation=resource,
                inputEvidence=rel(SOURCE), inputEvidenceSha256=sha(SOURCE), inputReview=rel(REVIEW), inputReviewSha256=sha(REVIEW),
                samplesCompared=len(chosen), imageCount=len(tiles), boardCount=len(boards), tiles=tiles, boards=boards,
                captionCenter=[960,970], fontPx=48, newSourceExtraction=0, sourceAudioUsed=False, narrationChanged=False,
                adoptedCrops=False, allDirectlyRead=False, allSourceMotionReviewed=False, allFinalCaptionPixelsReviewed=False,
                finalTimelineAdopted=False, humanListeningPronunciation='pending', imagesGitPolicy='local-only', newGitImages=0,
                scope='Targeted still composition trials. Check active player/tool/target and retained upper/lower paths; compare prospective or peripheral feet separately. No blanket crop or final approval.')
DEST.write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(samples=len(chosen), images=len(tiles), boards=len(boards), newSourceExtraction=0, adopted=False)))
