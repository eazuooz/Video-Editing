from pathlib import Path
import hashlib, json, subprocess, sys, re
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
version=sys.argv[1] if len(sys.argv)>1 else 'v1'
assert re.fullmatch(r'v\d+',version)
source=ROOT/f'shared/output/motion-canvas/motion-sickness-games-lookdev-{version}.mp4'
dest=ROOT/f'projects/motion-sickness-games/production/lookdev-{version}'
requests=[]
for i,sid in enumerate(['02','04','06','08','10','12']):
 for phase,offset in [('early',1.5),('middle',4.7),('late',7.3)]:
  seconds=8*i+offset;file=dest/f'{sid}-{phase}.png'
  subprocess.run(['ffmpeg','-y','-v','error','-ss',str(seconds),'-i',str(source),'-frames:v','1',str(file)],check=True)
  requests.append({'scene':sid,'phase':phase,'seconds':seconds,'path':file.relative_to(ROOT).as_posix()})
for page in range(3):
 canvas=Image.new('RGB',(1920,3*564),'#e8ece9');draw=ImageDraw.Draw(canvas)
 for n,item in enumerate(requests[page*6:(page+1)*6]):
  x=n%2*960;y=n//2*564
  frame=Image.open(ROOT/item['path']).convert('RGB').resize((960,540))
  canvas.paste(frame,(x,y+24));draw.text((x+12,y+5),f"Scene {item['scene']} | {item['phase']} | {item['seconds']:.1f}s",fill='black')
 canvas.save(dest/f'contact-{page+1}.png')
(dest/'inspection.json').write_text(json.dumps({'source':source.relative_to(ROOT).as_posix(),
 'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frames':requests,
 'silentLookdev':True,'finalNarratedVideo':False,'directVisualReview':'pending'},indent=2)+'\n')
print('18 early/middle/late views prepared; inspection is not approval.')
