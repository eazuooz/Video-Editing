from pathlib import Path
import subprocess,json,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'projects/picking-sides/production/visual-depth-v1/outro-boundary-local'
folder.mkdir(exist_ok=True)
src=ROOT/'projects/picking-sides/production/final-v1/outro.mp4'
frames=[0,1,2,15,30,60]
ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
subprocess.run([ff,'-v','error','-threads','2','-i',str(src),'-vf','select='+ '+'.join(f'eq(n\\,{n})' for n in frames),'-fps_mode','vfr','-frames:v','6',str(folder/'frame-%02d.png')],check=True)
board=Image.new('RGB',(1920,1722),'#e8edef');d=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
for i,n in enumerate(frames):
 x=(i%2)*960;y=(i//2)*574
 d.text((x+10,y+3),'Original membership clip frame '+str(n),font=font,fill='black')
 board.paste(Image.open(folder/f'frame-{i+1:02d}.png').resize((960,540)),(x,y+34))
board.save(folder/'boundary.jpg',quality=95)
print(folder/'boundary.jpg')
