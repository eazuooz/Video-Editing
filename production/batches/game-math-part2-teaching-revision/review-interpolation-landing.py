"""Inspect source action endpoints without claiming render approval."""
from pathlib import Path
import subprocess,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation/landing-review';D.mkdir(parents=True,exist_ok=True)
src=ROOT/'shared/output/game-math-part2-teaching-revision/sources/TPkvx2W8CV8.mp4'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
images=[]
for n in range(32):
 t=196+n*.5
 raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
 images.append((t,Image.frombytes('RGB',(800,450),raw)))
for page in range(math.ceil(len(images)/8)):
 sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
 for i,(t,im) in enumerate(images[page*8:page*8+8]):
  x=i%2*800;y=i//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'Native source {t:.3f}s',font=font,fill='black')
 sheet.save(D/f'sheet-{page+1:02}.jpg',quality=95)
print(D)
