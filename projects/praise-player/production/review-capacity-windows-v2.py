"""Inspect fresh spare windows before extending any selected actual-gameplay cut."""
import json, subprocess, io, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
WORK=Path(__file__).parent/'final-v2'; DEST=WORK/'source-proof'
mapping=json.loads((WORK/'example-map.json').read_text(encoding='utf8'))
windows=[('sports',199.8,203)]
points=[]
for key,a,b in windows:
 for n in range(math.ceil((b-a)*5)):
  points.append({'key':key,'seconds':a+n*.2,'file':mapping['sources'][key]['file']})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);records=[]
for page in range(math.ceil(len(points)/24)):
 batch=points[page*24:(page+1)*24];sheet=Image.new('RGB',(1600,math.ceil(len(batch)/4)*256),'white');draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(batch):
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(p['seconds']),'-i',str(ROOT/p['file']),'-frames:v','1','-vf','scale=400:225','-f','image2pipe','-vcodec','mjpeg','-'])
  x=i%4*400;y=i//4*256;sheet.paste(Image.open(io.BytesIO(data)).convert('RGB'),(x,y+28));draw.text((x+5,y+3),f"{p['key']} {p['seconds']:.3f}s",font=font,fill='black')
 target=DEST/f'capacity-bowling-actions-{page+1:02}.jpg';sheet.save(target,quality=92);records.append({'sheet':str(target.relative_to(ROOT)).replace('\\','/'),'points':batch})
(DEST/'capacity-bowling-actions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'pages':len(records),'samples':len(points)}))
