"""Dense, timestamped source evidence for short property-matched guide windows."""
import math,subprocess,sys
from PIL import Image,ImageDraw
from polish_common import *
e=Episode('M08' if 'M08' in sys.argv else 'M07');e.authorized();plan=read(e.H/'fhd-replacement-cuts.json')
windows={'IG01':[(3,11.5)],'IG10':[(0,8)],'IG02':[(0,5)],'IG07':[(0,7),(8.3,13.3)]}
if '--flight' in sys.argv:windows={'14':[(5,9),(37,40),(51,54)]}
if e.id=='M08':
 windows={'IG03':[(0,5)],'IG04':[(0,5)],'IG11':[(0,4)],'IG05':[(0,4),(11.8,15.8)],'IG08':[(0,4),(10.5,13.5)],'IG09':[(0,4),(7.5,10.5)],'IG06':[(0,8)]}
 if '--regions' in sys.argv:windows={'17':[(3,7)],'20':[(0,4),(27,31)],'23':[(0,4),(29,33),(53,57)]}
out=e.O/'guide-targets';out.mkdir(exist_ok=True)
records=[]
for sid,ranges in windows.items():
 for n,(start,end) in enumerate(ranges):
  at=0
  cut=plan['scenes'].get(sid) or next(s['cut'] for s in e.T['scenes'] if s['id']==sid)
  for seg in cut['segments']:
   if at<=start<at+seg['frames']/60:break
   at+=seg['frames']/60
  source_in=seg['in']+start-at
  folder=out/f'{sid}-{n}';folder.mkdir(exist_ok=True)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(source_in),'-i',str(R/seg.get('sourceFile',cut['sourceFile'])),'-vf',"select='not(mod(n,30))',scale=480:270",'-frames:v',str(round((end-start)*2)+1),'-fps_mode','vfr','-q:v','2','-y',str(folder/'%03d.jpg')],check=True)
  frames=sorted(folder.glob('*.jpg'))
  for i in range(0,len(frames),12):
   sheet=Image.new('RGB',(1440,1184),'#151515');d=ImageDraw.Draw(sheet)
   for k,p in enumerate(frames[i:i+12]):
    x=k%3*480;y=k//3*296;t=start+(i+k)/2
    sheet.paste(Image.open(p),(x,y+26));d.text((x+5,y+6),f'{sid} local {t:.2f} / source {source_in+(i+k)/2:.2f}',fill='white')
    records.append({'scene':sid,'localSeconds':t,'sourceSeconds':source_in+(i+k)/2,'image':rel(p)})
   sheet.save(out/f'{sid}-{n}-sheet-{i//12+1:02}.jpg',quality=95)
  print(sid,start,end,'dense target evidence',flush=True)
target=e.H/'guide-target-samples.json';previous=read(target)['samples'] if target.exists() else []
records=[x for x in previous if x['scene'] not in windows]+records
save(target,{'samples':records,'status':'await-target-trace','sourceCutMapSha256':sha(e.H/'fhd-replacement-cuts.json')})
