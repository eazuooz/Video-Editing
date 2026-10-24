"""Capture actual encoded captions, moving-game phases and return-to-model joins.

This generates evidence only; human/pixel review is recorded separately.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json,sys,subprocess,hashlib
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent
O=R/'shared/output/private-math-gameplay-20261024/motion-v4/final-review'
def read(p):return json.loads(p.read_text('utf-8-sig'))
for ep in sys.argv[1:]:
 p=read(V/(ep+'-plan.json'));H=R/'projects'/p['slug']/'production'/p['revision']
 out=read(H/'outputs.json');patches=read(H/'patches.json')['patches']
 master=next(x for x in out['outputs'] if x['path'].endswith('.captioned.mp4'));d=O/ep;d.mkdir(parents=True,exist_ok=True)
 marker=d/'frames.json'
 if marker.exists() and read(marker).get('masterSha256')==master['sha256']:
  print(ep,'frames already captured',flush=True);continue
 records=[]
 for i,patch in enumerate(patches):
  start=patch['start'];duration=patch['duration']
  cues=[('start',start+.35),('action',start+duration*.55),('result',start+duration-.35),('return',min(out['seconds']-.1,start+duration+.4))]
  for label,t in cues:
   f=d/f'{i:02d}-{label}.jpg'
   subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-ss',str(t),'-i',str(R/master['path']),'-frames:v','1','-q:v','2',str(f)],check=True)
   records.append(dict(patch=patch['key'],stage=label,time=t,path=f.relative_to(R).as_posix()))
 for page in range((len(patches)+3)//4):
  group=records[page*16:(page+1)*16];sheet=Image.new('RGB',(1920,386*((len(group)+2)//3)),'#101412');draw=ImageDraw.Draw(sheet)
  for i,row in enumerate(group):
   x=i%3*640;y=i//3*386;im=Image.open(R/row['path']).resize((640,360));sheet.paste(im,(x,y+26));draw.text((x+8,y+7),f"{ep} {row['patch']} {row['stage']} {row['time']:.2f}s",fill='white')
  sheet.save(d/f'sheet-{page}.jpg',quality=92)
 mobile=Image.new('RGB',(375*3,235*((len(patches)+2)//3)),'#101412');draw=ImageDraw.Draw(mobile)
 for i,patch in enumerate(patches):
  x=i%3*375;y=i//3*235;im=Image.open(d/f'{i:02d}-action.jpg').resize((375,211));mobile.paste(im,(x,y+24));draw.text((x+7,y+5),f'{ep} {patch["key"]}',fill='white')
 mobile.save(d/'mobile.jpg',quality=95)
 marker.write_text(json.dumps(dict(master=master['path'],masterSha256=master['sha256'],frames=records,pixelReview='pending',nativePlayback='pending'),indent=2)+'\n',encoding='utf8')
 print(ep,'captured',len(records),'frames',flush=True)
