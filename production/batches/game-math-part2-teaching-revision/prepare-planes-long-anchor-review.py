"""Dense source pixels for readable multi-second observed math annotations.

This is review material only. It does not approve tracking or invent world data.
"""
from pathlib import Path
import json, subprocess, math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'shared/output/game-math-part2-teaching-revision/planes-long-anchor-review'
O.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 15)
src = ROOT / 'shared/output/game-math-part2-full-series/sources'
jobs = [
    ('PG01-gel', '5791', 29, 37), ('PG01-cube', '5788', 24, 31),
    ('PG02-ramp', '5795', 31, 40), ('PG03-door', '5786', 79, 85),
    ('PG04-floor', '5790', 21, 30), ('PG04-wall', '5790', 49, 55),
    ('PG06-floor', '5790', 78, 84), ('PG06-turret', '5790', 56, 62),
    ('PG07-pad', '5791', 47, 59), ('PG07-wall', '5795', 75, 84),
    ('PG07-cube-continuation', '5795', 61, 74), ('PG04-coop-continuation', '5926', 34, 47),
]
records = []
for ident, suffix, start, end in jobs:
    file = src / f'portal2-steam-{suffix}.mp4'
    frames = []
    for k in range(round((end-start)*2)+1):
        t = start + k*.5
        path = O / f'{ident}-{t:06.2f}.png'
        if not path.exists():
            subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(file),'-frames:v','1','-vf','scale=800:450','-threads','1',str(path)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        frames.append((t,path))
    pages = []
    for page in range(math.ceil(len(frames)/9)):
        sheet = Image.new('RGB',(1920,1140),'white'); draw = ImageDraw.Draw(sheet)
        for cell,(t,path) in enumerate(frames[page*9:page*9+9]):
            x=cell%3*640; y=cell//3*380
            sheet.paste(Image.open(path).resize((640,360)),(x,y+20))
            draw.text((x+5,y),f'{ident} source {t:.2f}s',font=font,fill='black')
        path=O/f'{ident}-{page+1:02}.jpg';sheet.save(path,quality=95);pages.append(path.relative_to(ROOT).as_posix())
    records.append({'id':ident,'sourceFile':file.relative_to(ROOT).as_posix(),'interval':[start,end],'pages':pages,'directlyViewed':False})
    print(ident, len(pages), flush=True)
(O/'index.json').write_text(json.dumps({'records':records,'pixelApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
