"""Inspect finite surface visibility before authoring dependent narration."""
from pathlib import Path
import json, hashlib, subprocess, math
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'shared/output/game-math-part2-teaching-revision/planes-chosen-fine'
D.mkdir(parents=True,exist_ok=True)
S=ROOT/'shared/output/game-math-part2-full-series/sources'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
windows={5786:[(86,104)],5790:[(74,91)],80739:[(18,30.5)]}
records=[]
for ident,ranges in windows.items():
 source=S/f'portal2-steam-{ident}.mp4'; frames=[]
 for a,z in ranges:
  for i in range(math.ceil((z-a)/.5)):
   t=a+i*.5
   raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
   assert len(raw)==800*450*3
   frames.append((t,Image.frombytes('RGB',(800,450),raw)))
 sheets=[]
 for page in range(math.ceil(len(frames)/8)):
  im=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(im)
  for i,(t,frame) in enumerate(frames[page*8:page*8+8]):
   x=i%2*800;y=i//2*470;im.paste(frame,(x,y+20));draw.text((x+5,y),f'Steam {ident} actual source {t:.2f}s',font=font,fill='black')
  name=f'{ident}-fine-{page+1:02}.jpg';im.save(D/name,quality=95);sheets.append(name)
 records.append({'id':ident,'source':source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'windows':ranges,'sheets':sheets,'directlyViewed':False})
 print(ident,len(frames),flush=True)
(D/'index.json').write_text(json.dumps({'records':records,'automaticApproval':False,'imagesLocalOnly':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
