"""Review corrected, burned moving pixels at tenth-second observations."""
from pathlib import Path
import json,hashlib,subprocess,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
P=ROOT/'projects/game-math-bounds-transform-v2';W=ROOT/'shared/output/game-math-bounds-transform-v2'
m=json.loads((P/'project.json').read_text(encoding='utf8'));t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'))
src=ROOT/m['paths']['videoBurnedCaptions'];digest=hashlib.sha256(src.read_bytes()).hexdigest()
qa=json.loads((P/'production/qa.json').read_text(encoding='utf8'))
assert digest==qa['videos']['videoBurnedCaptions']['sha256'] and qa['fullDecodePassed']
assert digest!='33acbad6b7980c3d56f952e66cb9f7614f683e1e4fcc315b2d852a9067c1e29f'
D=W/'corrected-annotation-pixels';D.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
windows={'13':[(25.8,26.8),(33.4,34.2)],'16':[(27.8,29.5),(29.8,30.8)]}
hidden={'13':[0,10,25.5,27,33,35],'16':[0,2,13.5,27.5,31.5,33,38]}
records=[]
for ident,ranges in windows.items():
 slot=next(s for s in t['scenes'] if s['id']==ident);times=sorted(set(hidden[ident]+[round(a+i*.1,3) for a,z in ranges for i in range(round((z-a)*10)+1)]));frames=[]
 for local in times:
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(slot['start']+local),'-i',str(src),'-frames:v','1','-vf','scale=960:540','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  assert len(raw)==960*540*3
  frames.append((local,Image.frombytes('RGB',(960,540),raw)))
 sheets=[]
 for page in range(math.ceil(len(frames)/8)):
  sheet=Image.new('RGB',(1920,2240),'white');draw=ImageDraw.Draw(sheet)
  for i,(local,im) in enumerate(frames[page*8:page*8+8]):
   x=i%2*960;y=i//2*560;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'CURRENT {digest[:10]} scene {ident} local {local:.2f}s',fill='black',font=font)
  name=f'{ident}-corrected-{page+1:02}.jpg';sheet.save(D/name,quality=95);sheets.append(name)
 records.append({'scene':ident,'localTimes':times,'badSpansRequiredHidden':hidden[ident],'sheets':sheets,'directMovingPixelReview':False})
 print(ident,len(frames),flush=True)
(D/'index.json').write_text(json.dumps({'source':m['paths']['videoBurnedCaptions'],'sha256':digest,'records':records,'automaticApproval':False,'imagesLocalOnly':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
