from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision'
D=O/'wing-manual';D.mkdir(exist_ok=True)
source=O/'sources/_dw9jjRpanA.mp4'
times=[34+i/4 for i in range(33)]
for page in range(3):
    sheet=Image.new('RGB',(1200,4*245),'white');draw=ImageDraw.Draw(sheet)
    for idx,t in enumerate(times[page*12:(page+1)*12]):
        f=D/f'{t:.2f}.png'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=800:450',str(f)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        im=Image.open(f).crop((150,170,530,390));x=idx%3*400;y=idx//3*245
        sheet.paste(im,(x+10,y+10));draw.text((x+10,y+232),f'{t:.2f}s; crop x150..530 y170..390',fill='black')
        for value in [200,250,300,350,400,450,500]:
            px=x+10+value-150;draw.line((px,y+10,px,y+15),fill='cyan');draw.text((px-10,y),str(value),fill='white',stroke_width=1,stroke_fill='black')
        for value in [200,250,300,350]:
            py=y+10+value-170;draw.line((x+10,py,x+17,py),fill='cyan');draw.text((x+10,py),str(value),fill='white',stroke_width=1,stroke_fill='black')
    sheet.save(D/f'page-{page+1}.jpg')
print('33 manual tracking correction frames prepared')
