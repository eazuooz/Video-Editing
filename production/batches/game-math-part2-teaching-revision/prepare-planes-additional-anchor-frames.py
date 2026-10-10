"""Resolve rejected draft seeds with exact current source pixels."""
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'shared/output/game-math-part2-teaching-revision/planes-track-authoring'
jobs=[('14-surface','shared/output/game-math-planes-barycentric/clips/14.mp4',[12,12.5,13]),('08-marker','shared/output/game-math-planes-barycentric/clips/08.mp4',[32.3,32.4,32.5]),('PG01-later','shared/output/game-math-part2-full-series/sources/portal2-steam-5791.mp4',[24,28,32]),('21-step','shared/output/game-math-planes-barycentric/clips/21.mp4',[47,47.25,47.5])]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
for ident,file,times in jobs:
 sheet=Image.new('RGB',(1600,960),'white');draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(ROOT/file),'-frames:v','1','-vf','scale=800:450','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  assert len(raw)==800*450*3
  im=Image.frombytes('RGB',(800,450),raw);im.save(O/f'{ident}-{t:.2f}.png');x=i%2*800;y=i//2*480;sheet.paste(im,(x,y+25));draw.text((x+8,y+3),f'{ident} native {t:.2f}s',font=font,fill='black')
 sheet.save(O/f'{ident}.jpg',quality=95)
 print(ident,flush=True)
