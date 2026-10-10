"""Inspect the existing annotations at quarter-second intervals before narrowing."""
from pathlib import Path
import json, cv2, numpy as np, importlib.util
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
spec=importlib.util.spec_from_file_location('overlay',B/'create-lines-overlay.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
W=ROOT/'shared/output/game-math-bounds-transform-v2/track-fine-review';W.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
windows={'13':[(25.5,27),(33,34)],'16':[(0,.5),(13.5,17),(27.5,33.5)]}
records=[]
for ident,ranges in windows.items():
 track=o.read(B/'lines-tracks'/f'{ident}.json');cap=cv2.VideoCapture(str(ROOT/track['sourceFile']));frames=[]
 for a,z in ranges:
  for t in np.arange(a,z+.01,.25):
   cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000);ok,frame=cap.read();assert ok
   frame=cv2.resize(frame,(800,450));points=o.observation(track,float(t))
   if points:
    for key,color in [('red',(80,80,240)),('blue',(245,165,66))]:
     if key in points:cv2.polylines(frame,[np.round(points[key]).astype(np.int32)],True,color,2)
   image=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));frames.append((float(t),image))
 cap.release();sheets=[]
 for page in range((len(frames)+7)//8):
  sheet=Image.new('RGB',(1600,1880),'white');d=ImageDraw.Draw(sheet)
  for n,(t,image) in enumerate(frames[page*8:page*8+8]):
   x=n%2*800;y=n//2*470;d.text((x+5,y),f'{ident} source local {t:.2f}s; existing selected points',fill='black',font=font);sheet.paste(image,(x,y+20))
  file=f'{ident}-fine-{page+1:02}.jpg';sheet.save(W/file,quality=94);sheets.append(file)
 records.append({'scene':ident,'windows':ranges,'sheets':sheets,'sourceSha256':track['sourceSha256'],'directPixelReview':False});print(ident,len(frames),flush=True)
o.write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
o.write(W/'index.json',{'records':records,'notAutomaticApproval':True})
