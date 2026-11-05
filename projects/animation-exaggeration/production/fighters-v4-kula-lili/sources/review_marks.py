"""Inspect editorial rectangles in source space with source-time labels."""
from pathlib import Path
import io
import json
import subprocess

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
records = json.loads((HERE / 'reviewed-footage.json').read_text(encoding='utf-8'))
sources = {s['id']: ROOT / s['file'] for s in records['sources']}
for motion in records['motions']:
    source = sources[motion['sourceId']]
    sheet = Image.new('RGB', (4*384, ((len(motion['keyframes'])+3)//4)*238), '#161b18')
    for index, key in enumerate(motion['keyframes']):
        t=key['sourceTime']
        data = subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=384:216','-threads','1','-f','image2pipe','-vcodec','png','-'])
        frame=Image.open(io.BytesIO(data)).convert('RGB')
        x,y,w,h=key['box']
        canvas = ImageDraw.Draw(frame)
        if not any(a < t < b for a,b in motion['hiddenSourceIntervals']):
            canvas.rectangle([x*384,y*216,(x+w)*384,(y+h)*216],outline='#F45B63',width=2)
        ox=index%4*384;oy=index//4*238
        sheet.paste(frame,(ox,oy))
        ImageDraw.Draw(sheet).text((ox+6,oy+219),f'{t:.3f}s',fill='white')
    sheet.save(source.parent / f"{motion['id']}-observed-boxes.jpg",quality=90)
