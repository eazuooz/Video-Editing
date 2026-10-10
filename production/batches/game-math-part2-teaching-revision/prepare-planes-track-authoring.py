"""Exact native source samples for manual, conservative surface observations."""
from pathlib import Path
import json, hashlib, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision/planes-track-authoring'; O.mkdir(parents=True,exist_ok=True)
baseline='shared/output/game-math-planes-barycentric/clips/'
source='shared/output/game-math-part2-full-series/sources/'
jobs=[
 ('02',baseline+'02.mp4',[10,10.5,11]),('05',baseline+'05.mp4',[8,8.5,9]),
 ('08',baseline+'08.mp4',[32,32.5,33]),('11',baseline+'11.mp4',[16,16.5,17]),
 ('14',baseline+'14.mp4',[26,26.5,27]),('17',baseline+'17.mp4',[18,18.5,19]),
 ('19',baseline+'19.mp4',[24,24.5,25]),('21',baseline+'21.mp4',[46,46.5,47]),
 ('PG01-gel',source+'portal2-steam-5791.mp4',[17,17.5,18]),
 ('PG01-cube',source+'portal2-steam-5788.mp4',[20,20.5,21]),
 ('PG02-slope',source+'portal2-steam-5795.mp4',[36,36.5,37]),
 ('PG03-panel',source+'portal2-steam-80739.mp4',[18,18.5,19]),
 ('PG03-door',source+'portal2-steam-5786.mp4',[81,81.5,82]),
 ('PG04-floor',source+'portal2-steam-5790.mp4',[28,28.5,29]),
 ('PG04-wall',source+'portal2-steam-5790.mp4',[50,50.5,51]),
 ('PG06-tile',source+'portal2-steam-5790.mp4',[85.5,86,86.5]),
 ('PG06-turret',source+'portal2-steam-5790.mp4',[58,58.5,59]),
 ('PG07-pad',source+'portal2-steam-5791.mp4',[45,45.5,46]),
 ('PG07-wall',source+'portal2-steam-5795.mp4',[80,80.5,81]),
]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15); records=[]
for ident,file,times in jobs:
 pictures=[]
 for t in times:
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(ROOT/file),'-frames:v','1','-vf','scale=800:450','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  assert len(raw)==800*450*3
  im=Image.frombytes('RGB',(800,450),raw); path=O/f'{ident}-{t:.2f}.png'; im.save(path)
  pictures.append((t,im,path.relative_to(ROOT).as_posix()))
 sheet=Image.new('RGB',(1600,960),'white');draw=ImageDraw.Draw(sheet)
 for i,(t,im,path) in enumerate(pictures):
  x=i%2*800;y=i//2*480;sheet.paste(im,(x,y+25));draw.text((x+8,y+3),f'{ident} native source {t:.2f}s; 800x450',font=font,fill='black')
 page=O/f'{ident}.jpg';sheet.save(page,quality=95)
 records.append({'id':ident,'sourceFile':file,'sourceSha256':hashlib.sha256((ROOT/file).read_bytes()).hexdigest(),'times':times,'frames':[p[2] for p in pictures],'page':page.relative_to(ROOT).as_posix(),'directManualReview':False,'movingPixelApproval':False})
 print(ident,flush=True)
(O/'index.json').write_text(json.dumps({'records':records,'approval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
