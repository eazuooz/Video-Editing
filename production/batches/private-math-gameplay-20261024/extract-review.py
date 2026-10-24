"""Extract final-composition frames for visual inspection; extraction is not approval."""
from pathlib import Path
import json, subprocess, sys
from PIL import Image, ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[2]
def rd(p):return json.loads(p.read_text('utf-8-sig'))
mode=sys.argv[1]
dest=R/'shared/output/private-math-gameplay-20261024'/('final-review' if mode=='final' else 'patch-review-current');dest.mkdir(exist_ok=True)
for eid in sys.argv[2:]:
 p=rd(B/f'{eid.lower()}-gameplay-plan.json');h=R/'projects'/p['slug']/'production/gameplay-v3';receipts=rd(h/'patches.json')['patches'];frames=[]
 if mode=='final':master=R/next(x['path'] for x in rd(h/'outputs.json')['outputs'] if x['path'].endswith('.captioned.mp4'))
 for i,(x,q) in enumerate(zip(p['patches'],receipts)):
  at=max(g.get('from',0) for g in x.get('guides',[]))+1.8 if x.get('guides') else x['duration']/2
  at=min(at,x['duration']-.35)
  src=master if mode=='final' else R/q['path'];time=q['start']+at if mode=='final' else at
  f=dest/f'{eid}-{i}.jpg'
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(time),'-i',str(src),'-frames:v','1','-q:v','2',str(f)],check=True)
  im=Image.open(f);im.resize((375,211)).save(dest/f'{eid}-{i}-mobile.png')
  tile=Image.new('RGB',(960,566),'#171717');tile.paste(im.resize((960,540)),(0,26));ImageDraw.Draw(tile).text((10,6),f'{eid} {x.get("key",x["scene"])} / {time:.3f}s / {p["patchSet"]}',fill='white');frames.append(tile)
 for j in range(0,len(frames),4):
  sheet=Image.new('RGB',(1920,566*((min(4,len(frames)-j)+1)//2)),'black')
  for k,im in enumerate(frames[j:j+4]):sheet.paste(im,((k%2)*960,(k//2)*566))
  f=dest/f'{eid}-sheet{j//4}.jpg';sheet.save(f,quality=92);print(f,flush=True)
