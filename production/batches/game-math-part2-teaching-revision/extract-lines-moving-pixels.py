"""Rendered, captioned action samples; no automatic pixel approval."""
from pathlib import Path
import json,sys,hashlib,subprocess,math,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1]
assert slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']
P=ROOT/'projects'/slug;m=json.loads((P/'project.json').read_text(encoding='utf8'));t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'))
src=ROOT/m['paths']['videoBurnedCaptions'];D=ROOT/f'shared/output/{slug}/moving-pixel-review';D.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);rows=[s for s in t['scenes'] if s['classification']=='actual']
def extract(s):
 times=[*range(0,math.ceil(s['seconds']),2),s['seconds']-.15];images=[]
 for local in times:
  if local>=s['seconds']:continue
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(s['start']+local),'-i',str(src),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  images.append((local,Image.frombytes('RGB',(800,450),raw)))
 paths=[]
 for page in range(math.ceil(len(images)/8)):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for i,(local,im) in enumerate(images[page*8:page*8+8]):
   x=i%2*800;y=i//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{s["id"]} local{local:.3f}s final{local+s["start"]:.3f}s',font=font,fill='black')
  path=D/f'{s["id"]}-sheet-{page+1:02}.jpg';sheet.save(path,quality=95);paths.append(path.name)
 print('Actual final moving samples',slug,s['id'],flush=True)
 return {'scene':s['id'],'localTimes':[x[0] for x in images],'sheets':paths,'movingPixelAndCaptionReview':False}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(extract,rows))
(D/'index.json').write_text(json.dumps({'source':m['paths']['videoBurnedCaptions'],'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'samples':records,'automaticApproval':False,'imagesLocalOnly':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
