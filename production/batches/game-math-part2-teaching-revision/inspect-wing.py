from pathlib import Path
import subprocess
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'shared/output/game-math-part2-teaching-revision'
D=O/'wing-inspection';D.mkdir(exist_ok=True)
SRC=O/'sources/_dw9jjRpanA.mp4'
times=list(range(28,50))
sheet=Image.new('RGB',(1600,6*245),'white');draw=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
    f=D/f'{t}.png'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(t),'-i',str(SRC),'-frames:v','1','-vf','scale=800:450',str(f)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    sheet.paste(Image.open(f).resize((400,225)),(i%4*400,i//4*245))
    draw.text((i%4*400+5,i//4*245+228),f'source {t}s',fill='black')
sheet.save(D/'contact.jpg')
print('22 observed-frame inspection samples prepared; no tracking approval')
