"""Sample encoded M08 replacements with current captions; no delivery pass."""
import datetime
import math
from PIL import Image, ImageDraw, ImageFont
from polish_common import *

e = Episode('M08')
e.authorized()
rendered = read(e.H/'conversions-legibility-render.json')
assert len(rendered['scenes']) == sum(s['classification']=='explanation' for s in e.T['scenes'])
out = e.O/'conversions-legibility-review'
out.mkdir(exist_ok=True)
records, tiles = [], []
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 16)
for slot in e.T['scenes']:
    if slot['classification'] != 'explanation':
        continue
    sid = slot['id']
    item = rendered['scenes'][sid]
    src = R/item['path']
    assert sha(src) == item['sha256']
    times = {min(slot['seconds']-.2, max(.2, f*slot['seconds'])) for f in [.12,.38,.64,.88]}
    times.update(min(slot['seconds']-.2, t+1.5) for t in slot['lineStarts'])
    for k, t in enumerate(sorted(times)):
        dst = out/f'{sid}-{k:02d}.png'
        e.ff(['-ss', t, '-i', src, '-vf', f"setpts=PTS+{slot['start']+t}/TB,ass=captions.ko.ass",
              '-frames:v', '1', '-threads', '1', dst], 'interpolation-review-sample.log', e.O)
        records.append({'scene':sid, 'source':rel(src), 'sourceSha256':item['sha256'],
                        'localSeconds':t, 'globalSeconds':slot['start']+t,
                        'image':rel(dst), 'imageSha256':sha(dst)})
        tile = Image.new('RGB',(375,240),'#222222')
        tile.paste(Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS),(0,29))
        ImageDraw.Draw(tile).text((5,3),f'M08 {sid} +{t:.2f}s',font=font,fill='white')
        tiles.append(tile)
    print('M08',sid,'encoded source samples generated',flush=True)
for i in range(0,len(tiles),8):
    sheet = Image.new('RGB',(1500,480),'#222222')
    for j,tile in enumerate(tiles[i:i+8]):
        sheet.paste(tile,(j%4*375,j//4*240))
    sheet.save(out/f'sheet-{i//8+1:02d}.jpg',quality=94)
save(e.H/'conversions-legibility-samples.json',{
    'status':'await-direct-inspection','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'samples':records,'sheets':math.ceil(len(tiles)/8),'sourceCode':rendered['sourceCode'],
    'timelineSha256':rendered['timelineSha256'],'captionSha256':sha(e.O/'captions.ko.ass'),
    'scope':'16 encoded explanation replacements only; not a final assembled master',
    'readyForHumanReview':False,'gameplaySourceBlocker':'unchanged'})
