"""Render observed first/middle/last points, with no approval inference."""
from pathlib import Path
import json,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-track-check';O.mkdir(parents=True,exist_ok=True)
cv2.setNumThreads(2);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
items=[]
for spec in json.loads((B/'polygons-observed-track-seeds.json').read_text(encoding='utf8')):
 r=json.loads((B/'polygons-tracks'/f'{spec["id"]}.json').read_text(encoding='utf8'));keys=r['keyframes']
 if not keys:continue
 cap=cv2.VideoCapture(str(ROOT/r['sourceFile']))
 for k in [keys[0],keys[len(keys)//2],keys[-1]]:
  cap.set(cv2.CAP_PROP_POS_FRAMES,k['nativeFrame']);ok,frame=cap.read();assert ok
  im=Image.fromarray(cv2.cvtColor(cv2.resize(frame,(800,450)),cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(im)
  for colour,hexcode in [('red','#ef5350'),('blue','#42a5f5'),('yellow','#ffd54f')]:
   if colour not in k:continue
   p=k[colour];d.line([tuple(x) for x in (p+[p[0]] if r.get('closed') or colour in ['blue','yellow'] else p)],fill=hexcode,width=3)
  items.append((f'{spec["id"]} source {k["t"]:.3f}s / {len(keys)} native observed frames',im))
 cap.release()
pages=[]
for page in range((len(items)+5)//6):
 sheet=Image.new('RGB',(1600,1416),'white');d=ImageDraw.Draw(sheet)
 for cell,(label,im) in enumerate(items[page*6:page*6+6]):
  x=cell%2*800;y=cell//2*472;sheet.paste(im,(x,y+22));d.text((x+5,y+2),label,font=font,fill='black')
 p=O/f'check-{page+1:02}.jpg';sheet.save(p,quality=96);pages.append(p.relative_to(ROOT).as_posix())
(O/'index.json').write_text(json.dumps({'pages':pages,'observations':len(items),'finalMovingApproval':False},indent=2)+'\n',encoding='utf8')
print(len(items),'draft point checks; moving review remains pending')
