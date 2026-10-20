"""Arrange already-extracted current final frames in temporal order; no re-decode."""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parents[3]
P = R / 'projects/vampire-survivors-d2-copyright'
L = P / 'production/local'
Q = L / 'final-qa'
rd = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
plan = rd(P / 'production/edit-plan.json')
selection = rd(Q / 'frame-selection.json')
mapping = {x['frame']: Q/'frames'/x['file'] for x in selection['mapping']}
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 21)
items = [c for c in plan['cuts'] if c['kind']=='explanation' or c.get('annotation')]
for page in range(math.ceil(len(items)/6)):
    sheet = Image.new('RGB', (1920, 6*300), '#171717')
    draw = ImageDraw.Draw(sheet)
    for row, c in enumerate(items[page*6:page*6+6]):
        start = c['startFrame']+120
        valid = [f for f in mapping if start <= f < start+c['frames']]
        seconds = [.4, 2, 4, 6] if c['kind']=='explanation' else [max(0,c['annotation']['cue']-.1), c['annotation']['cue']+.5, c['annotation']['cue']+1.5, min(c['frames']/60-.02,c['annotation']['cue']+c['annotation']['seconds']+.3)]
        for col, seconds in enumerate(seconds):
            target = start+min(seconds*60,c['frames']-1)
            frame = min(valid,key=lambda f:abs(f-target))
            x = col*480; y = row*300
            sheet.paste(Image.open(mapping[frame]).resize((480,270)),(x,y+27))
            draw.text((x+4,y),f'{c["id"]} +{(frame-start)/60:.2f}s',font=font,fill='white')
    sheet.save(Q/f'motion-order-{page+1:02}.jpg',quality=95)
print('Ordered temporal boards from existing extraction:',len(items),'scenes')
