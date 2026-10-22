from common import *
from PIL import Image,ImageDraw,ImageFont
O=R/'shared/output/private-math-concept-fit-20261023';d=read(B/'scene-audit.json')
master=R/'projects/game-math-orientation-matrices/production/local/concept-fit-v2/original-upload-recovered.mp4'
folder=O/'current-samples/M03-original';folder.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);items=[]
for row in d['scenes']:
 if row['episode']!='M03-original':continue
 paths=[]
 for n,f in enumerate([.08,.33,.66,.92]):
  sec=row['start']+row['seconds']*f;dst=folder/f'{row["scene"]}-{n}.jpg'
  if not dst.exists():run(['ffmpeg','-v','error','-threads','2','-ss',sec,'-i',master,'-vf','scale=640:360','-frames:v','1','-q:v','3','-y',dst])
  x=dict(path=rel(dst),masterSeconds=sec,localSeconds=row['seconds']*f);paths.append(x);items.append((row,x))
 row.update(samples=paths,sampledMaster=rel(master),sampleStatus='sampled-not-reviewed',sampleSourceResolution='1280x720 review only; not production source')
sheets=[]
for idx in range(0,len(items),12):
 group=items[idx:idx+12];im=Image.new('RGB',(1920,1560),'#121512');draw=ImageDraw.Draw(im)
 for j,(row,x) in enumerate(group):
  left=j%3*640;top=j//3*390;im.paste(Image.open(R/x['path']),(left,top+30));draw.text((left+6,top+4),f'M03/{row["scene"]} +{x["localSeconds"]:.1f}s {row["title"][:30]}',font=font,fill='white')
 dest=O/f'current-M03-original-{idx//12+1:02}.jpg';im.save(dest,quality=88);sheets.append(dict(episode='M03-original',path=rel(dest),items=[dict(scene=r['scene'],**x) for r,x in group]))
d['currentSampleSheets']=[s for s in d['currentSampleSheets'] if s['episode']!='M03-original']+sheets;save(B/'scene-audit.json',d)
print(json.dumps(dict(samples=len(items),sheets=[s['path'] for s in sheets])))
