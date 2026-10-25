from pathlib import Path
import json,urllib.request,io
from PIL import Image,ImageDraw
R=Path('D:/Github/VideoEditing');O=R/'shared/output/private-math-gameplay-20261024/m14-v5/source-research';O.mkdir(parents=True,exist_ok=True)
j=json.loads((R/'shared/output/private-math-gameplay-20261024/motion-v4/source-review/shapez-candidates/dep-ep01.info.json').read_text('utf8'))
f=next(x for x in j['formats'] if x['format_id']=='sb0');frames=[];t=0
for n,frag in enumerate(f['fragments']):
 p=O/f'storyboard-{n:02}.jpg'
 if not p.exists():p.write_bytes(urllib.request.urlopen(frag['url']).read())
 im=Image.open(p)
 for i in [0,3,6]:frames.append((t+i*frag['duration']/9,im.crop((i%3*320,i//3*180,(i%3+1)*320,(i//3+1)*180))))
 t+=frag['duration']
for page in range((len(frames)+23)//24):
 group=frames[page*24:(page+1)*24];s=Image.new('RGB',(1280,208*((len(group)+3)//4)),'#101412');d=ImageDraw.Draw(s)
 for i,(t,im) in enumerate(group):
  x=i%4*320;y=i//4*208;s.paste(im,(x,y+28));d.text((x+5,y+5),f'{t:.1f}s / {int(t)//60}:{int(t)%60:02}',fill='white')
 s.save(O/f'overview-{page}.jpg',quality=90)
print('Storyboard research contact sheets:',len(frames),'frames. Not production source.')
