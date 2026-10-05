"""Generate local per-beat QA sheets; generation is not visual approval."""
from pathlib import Path
import sys,json,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];slug=sys.argv[1]
d=json.loads((Path(__file__).parent/'lessons'/f'{slug}.json').read_text(encoding='utf8'))
work=R/'shared/output'/slug/'lookdev';folder=work/'inspection';folder.mkdir(parents=True,exist_ok=True)
records=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
for scene in d['scenes']:
 if scene['kind']!='explanation':continue
 sid=scene['id'];source=work/f'videos/scene/480p15/Scene{sid}.mp4';count=len(scene['beats']);page=Image.new('RGB',(1710,510*((count+1)//2)),(238,240,243));draw=ImageDraw.Draw(page);times=[]
 for i in range(count):
  t=i*2.2+1.65;target=folder/f'scene{sid}-beat{i+1:02d}.jpg'
  subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(source),'-frames:v','1','-q:v','2',str(target)],check=True)
  im=Image.open(target).convert('RGB');im.thumbnail((854,480));x=(i%2)*855;y=(i//2)*510;page.paste(im,(x,y+30));draw.text((x+8,y+3),f'{sid} / beat{i+1} / {t:.2f}s',font=font,fill='black');times.append(t)
 out=folder/f'scene{sid}-all-beats.jpg';page.save(out,quality=95)
 records.append({'scene':sid,'path':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'sampleTimes':times,'review':'pending-direct-view'})
(folder/'generated-samples.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
print('Generated',len(records),'per-beat sheets; direct visual review still required.')
