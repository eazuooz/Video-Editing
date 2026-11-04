"""Finite CPU-only temporal samples of the actual encoded gameplay and joins.

This is sampled sequence evidence, never a claim of continuous human playback.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib,math
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];R=P.parents[1];Q=P/'production/local/render-v4'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
q=read(Q/'queue.json');rep=read(Q/'final-qa/report.json');master=Path(rep['files']['captioned']['path'])
assert hashlib.sha256(master.read_bytes()).hexdigest()==rep['files']['captioned']['sha256']
ff=read(Path(q['jobs'][0]))['ffmpeg'];out=Q/'temporal-samples';out.mkdir(exist_ok=True)
records=[]
for cut in q['cuts']:
 if cut['kind']!='actual-gameplay':continue
 sid=cut['scene'];start=2+cut['globalStartFrame']/60;duration=cut['frames']/60
 folder=out/sid;folder.mkdir(exist_ok=True)
 if not (folder/'extract.ok').exists():
  with (folder/'extract.log').open('w',encoding='utf-8') as log:
   subprocess.run([ff,'-v','error','-nostdin','-y','-threads','2','-ss',str(max(0,start-.5)),'-i',str(master),'-t',str(duration+1.5),'-vf','fps=2,scale=750:-2','-q:v','3','-threads','1',str(folder/'frame-%04d.jpg')],stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=0x08000000)
  (folder/'extract.ok').write_text('bounded final-file extraction complete',encoding='utf-8')
 frames=sorted(folder.glob('frame-*.jpg'));sheets=[]
 for page,a in enumerate(range(0,len(frames),16)):
  sheet=Image.new('RGB',(1500,944),'#080808');draw=ImageDraw.Draw(sheet)
  for j,f in enumerate(frames[a:a+16]):
   im=Image.open(f).convert('RGB');im.thumbnail((375,211));x=j%4*375;y=j//4*236;sheet.paste(im,(x,y));draw.text((x+5,y+214),f'{sid} master {max(0,start-.5)+(a+j)/2:.2f}s',fill='white')
  path=folder/f'contact-{page:02}.png';sheet.save(path);sheets.append(str(path))
 records.append(dict(scene=sid,masterStart=start,gameSeconds=duration,sampleFps=2,frames=len(frames),sheets=sheets,viewed=False))
(out/'manifest.json').write_text(json.dumps(dict(masterSha256=rep['files']['captioned']['sha256'],createdAt=datetime.now(timezone.utc).isoformat(),method='2fps complete actual-game segments plus adjacent boundaries. CPU-only extraction, source master unchanged.',continuousPlaybackViewed=False,humanListening=False,records=records),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(segments=len(records),frames=sum(x['frames'] for x in records),sheets=sum(len(x['sheets']) for x in records))))
