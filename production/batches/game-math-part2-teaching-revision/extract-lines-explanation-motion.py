"""Spoken-beat samples from the final captioned episode, no automatic approval."""
from pathlib import Path
import json,subprocess,math,hashlib,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1]
assert slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']
P=ROOT/'projects'/slug;m=json.loads((P/'project.json').read_text(encoding='utf8'));t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'))
video=ROOT/m['paths']['videoBurnedCaptions'];D=ROOT/f'shared/output/{slug}/explanation-motion-review';D.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);records=[]
for s in t['scenes']:
 if s['preservedOriginal'] or s['classification']!='explanation':continue
 times=sorted({round(min(s['seconds']-.05,x),3) for x in [.2,s['seconds']-.15,*[y+z for y in s['lineStarts'] for z in [.25,1.65]],*[c['start']+.25 for c in s['sentenceCues']]]})
 frames=[]
 for i,local in enumerate(times):
  path=D/f'{s["id"]}-{i:02}.jpg'
  subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-ss',str(s['start']+local),'-i',str(video),'-frames:v','1','-vf','scale=960:540','-q:v','2',str(path)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  frames.append({'local':local,'final':s['start']+local,'file':path.name})
 sheets=[]
 for page in range(math.ceil(len(frames)/4)):
  sheet=Image.new('RGB',(1920,1120),'white');draw=ImageDraw.Draw(sheet)
  for i,frame in enumerate(frames[page*4:page*4+4]):
   x=i%2*960;y=i//2*560;sheet.paste(Image.open(D/frame['file']),(x,y+20));draw.text((x+5,y),f'{s["id"]} local{frame["local"]} final{frame["final"]:.3f}',font=font,fill='black')
  name=f'{s["id"]}-sheet-{page+1:02}.jpg';sheet.save(D/name,quality=95);sheets.append(name)
 records.append({'scene':s['id'],'samples':frames,'sheets':sheets,'directMovingPixelReviewPassed':False})
 print('Final explanation motion samples',s['id'],flush=True)
(D/'index.json').write_text(json.dumps({'source':m['paths']['videoBurnedCaptions'],'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'records':records,'imagesLocalOnly':True,'automaticApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
