"""Current compositor pixels for source movement/caption-safe region review."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3';sys.path.insert(0,str(O/'deps'))
import cv2
from PIL import Image,ImageDraw,ImageFont
plan=json.loads((P/'sources/annotation-plan-v3.json').read_text(encoding='utf8'));out=O/'annotation-contact';out.mkdir(exist_ok=True);rows=[];font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
for w in plan['windows']:
 f=O/'annotation-preview'/(w['id']+'.mp4');cap=cv2.VideoCapture(str(f));n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));assert n>1
 for fraction in [.15,.5,.85]:
  frame=round((n-1)*fraction);cap.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,a=cap.read();assert ok
  im=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB)).resize((640,360));rows.append((w['id'],w['sourceIn']+frame/60,im))
 cap.release()
for offset in range(0,len(rows),12):
 chunk=rows[offset:offset+12];board=Image.new('RGB',(1920,390*((len(chunk)+2)//3)),(12,12,12));d=ImageDraw.Draw(board)
 for j,(name,t,im) in enumerate(chunk):
  x=j%3*640;y=j//3*390;board.paste(im,(x,y));d.text((x+5,y+362),f'{name} source {t:.2f}s',font=font,fill='white')
 board.save(out/f'board-{offset//12+1:02}.jpg',quality=93)
(out/'index.json').write_text(json.dumps([dict(id=name,sourceTime=t) for name,t,_ in rows],indent=2))
print('Current annotation composites:',len(rows),'frames')
