from common import *
from PIL import Image,ImageDraw,ImageFont
P=R/'projects/game-math-lines-circles-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2/preflight';O.mkdir(exist_ok=True)
r=read(H/'render-progress.json');t=read(H/'timeline.json');items=[]
for s in t['scenes']:
 if r['scenes'][s['id']]['origin']!='concept-matched own model':continue
 for ratio in [.25,.7]:
  stamp=round(s['seconds']*ratio,3);dst=O/f'{s["id"]}-{ratio}.jpg'
  run(['ffmpeg','-v','error','-ss',stamp,'-i',R/r['scenes'][s['id']]['path'],'-frames:v','1','-vf','scale=640:360','-y',dst]);items.append((s['id'],stamp,dst))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
for at in range(0,len(items),9):
 im=Image.new('RGB',(1920,1170),'#111');d=ImageDraw.Draw(im)
 for i,(sid,ts,p) in enumerate(items[at:at+9]):
  x=i%3*640;y=i//3*390;im.paste(Image.open(p),(x,y+30));d.text((x+5,y),f'{sid} / {ts}s',font=font,fill='white')
 im.save(O/f'sheet-{at//9+1}.jpg',quality=90)
print('Changed-scene preflight frames ready')
