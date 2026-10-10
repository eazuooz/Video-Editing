"""Sample real moving render frames to locate problems, never grant approval."""
from pathlib import Path
import json,subprocess,concurrent.futures,argparse,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/track-pixel-review';O.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
records=[]
parser=argparse.ArgumentParser();parser.add_argument('--scenes');args=parser.parse_args();selected=set(args.scenes.split(',')) if args.scenes else None
for slug in ['game-math-quaternion-foundations-v2','game-math-quaternion-calculations-v2']:
 t=json.loads((ROOT/f'projects/{slug}/production/timeline.json').read_text(encoding='utf8'))
 for s in t['scenes']:
  if s['classification']!='actual':continue
  if selected and s['id'] not in selected:continue
  source=ROOT/f'shared/output/{slug}/clips/{s["id"]}.mp4'
  annotation=json.loads((ROOT/f'shared/output/{slug}/overlays/{s["id"]}.json').read_text(encoding='utf8'))
  start=min(s['seconds']-.1,annotation['revealAt']['red']+.3)
  times=[start+(s['seconds']-.1-start)*i/8 for i in range(9)]
  records.append((slug,s,source,times))
def sample(job):
 slug,s,source,times=job;sheet=Image.new('RGB',(1500,1050),'white');draw=ImageDraw.Draw(sheet)
 for i,time in enumerate(times):
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(time),'-i',str(source),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  im=Image.frombytes('RGB',(800,450),raw);x=i%3*500;y=i//3*350
  sheet.paste(im.crop((125,100,600,420)),(x+10,y+22));draw.text((x+10,y+2),f'{s["id"]} {time:.2f}s (native1x clip)',font=font,fill='black')
 sheet.save(O/f'{slug}-{s["id"]}.jpg',quality=95)
 return {'slug':slug,'scene':s['id'],'times':times,'clipSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'movingReviewPassed':False}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 result=list(pool.map(sample,records))
if selected and (O/'index.json').exists():
 previous=json.loads((O/'index.json').read_text(encoding='utf8'));changed={(r['slug'],r['scene']) for r in result};result=[r for r in previous if (r['slug'],r['scene']) not in changed]+result
(O/'index.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print('Extracted',len(result),'actual rendered annotation sheets. Sampling is diagnostic, not continuous moving approval.')
