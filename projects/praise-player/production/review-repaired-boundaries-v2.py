from pathlib import Path
import json, subprocess, io, math
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3];W=Path(__file__).parent/'final-v2';D=W/'source-proof'
m=json.loads((W/'example-map.json').read_text(encoding='utf8'))
r=json.loads((W/'source-boundary-repairs.json').read_text(encoding='utf8'))
points=[]
for key,a,b,x,y,reason in r['repairs']:
 for t in [x,(x+y)/2,y-1/60]:points.append((key,t,m['sources'][key]['file']))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for p in range(math.ceil(len(points)/24)):
 batch=points[p*24:(p+1)*24];im=Image.new('RGB',(1600,math.ceil(len(batch)/4)*256),'white');d=ImageDraw.Draw(im)
 for i,(k,t,f) in enumerate(batch):
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(ROOT/f),'-frames:v','1','-vf','scale=400:225','-f','image2pipe','-vcodec','mjpeg','-'])
  x=i%4*400;y=i//4*256;im.paste(Image.open(io.BytesIO(data)).convert('RGB'),(x,y+28));d.text((x+5,y+3),f'{k} {t:.3f}s',font=font,fill='black')
 im.save(D/f'repaired-boundaries-{p+1:02}.jpg',quality=92)
print(json.dumps({'pages':math.ceil(len(points)/24),'samples':len(points)}))
