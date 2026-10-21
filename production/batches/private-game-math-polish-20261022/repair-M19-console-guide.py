"""Candidate screen anchors from the actual normalized scene; requires review.

Yellow button pixels only locate an editorial attention ring. They are not
engine measurements or a viewer-facing detector output.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from polish_common import *

e = Episode('M19')
e.authorized()
out = e.O / 'console-guide-repair'
out.mkdir(exist_ok=True)
src = e.O / 'clips/10.mp4'
plan_path = e.H / 'observed-guides.json'
plan = read(plan_path)
save(out / 'previous-plan.json', plan)
guide = next(g for g in plan['guides'] if g['scene'] == '10')
keys, records, tiles = [], [], []
for i in range(16):
    t = round(.4 + i * .1, 3)
    path = out / f'{i:02d}.png'
    e.ff(['-ss', t, '-i', src, '-vf', 'scale=640:360', '-frames:v', '1', '-threads', '1', path], 'console-guide-repair.log')
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(float)
    rr, gg, bb = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    yy, xx = np.indices(rr.shape)
    mask = (xx > 120) & (xx < 350) & (yy > 60) & (yy < 190)
    mask &= (rr > 130) & (gg > 100) & (bb < gg * .45) & (rr < gg * 1.8)
    y, x = np.where(mask)
    assert len(x) > 80, (t, len(x))
    x0, x1 = np.quantile(x, [.02, .98])
    y0, y1 = np.quantile(y, [.02, .98])
    key = [t, round((x0 + x1) / 2, 2), round((y0 + y1) / 2, 2), round((x1 - x0) / 2 + 9, 2), round((y1 - y0) / 2 + 7, 2)]
    keys.append(key)
    draw = ImageDraw.Draw(im)
    cx, cy, rx, ry = key[1:]
    draw.ellipse((cx-rx, cy-ry, cx+rx, cy+ry), outline='#F0D379', width=3)
    tile = Image.new('RGB', (640, 390), '#222222')
    tile.paste(im, (0, 30))
    ImageDraw.Draw(tile).text((8, 5), f'scene10 +{t:.2f}s; candidate screen guide', fill='white')
    tiles.append(tile)
    records.append({'localSeconds': t, 'sourceFrame': rel(path), 'sourceFrameSha256': sha(path), 'candidateKeyframe': key})
guide['keyframes'] = keys
guide['reason'] = 'Button face followed on normalized original scene at0.1s intervals, replacing sparse raw-source anchors that drifted in final encode. Editorial screen region only; no recovered normal or angle.'
save(plan_path, plan)
sheet = Image.new('RGB', (2560, 1560), '#222222')
for i, tile in enumerate(tiles):
    sheet.paste(tile, ((i % 4) * 640, (i // 4) * 390))
sheet.save(out / 'candidates.jpg', quality=95)
save(e.H / 'console-guide-repair.json', {'status': 'candidate-await-direct-review', 'source': rel(src), 'sourceSha256': sha(src), 'failedCaptionedMaster': '998a54ed193feb66226357f7c07fb914e272afb06bb0cda47410edab99916790', 'reason': 'Final samples236 and245 expose ring drift onto deck/front wall instead of the button face.', 'samples': records, 'planSha256': sha(plan_path), 'newTts': False})
print('M19 candidate anchors prepared; not approved')
