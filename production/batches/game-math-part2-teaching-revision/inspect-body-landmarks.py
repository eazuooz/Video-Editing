from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/source-review';SRC=ROOT/'shared/output/game-math-part2-full-series/sources/4Odvp_TIeQU.mp4'
times=[3,6,9,10,11,12,13,14,15,16,17,18]
sheet=Image.new('RGB',(1600,4*320),'white');draw=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
 p=O/f'landmark-{t}.png'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(t),'-i',str(SRC),'-frames:v','1','-vf','scale=800:450',str(p)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 im=Image.open(p);im.thumbnail((533,300));x=(i%3)*533;y=(i//3)*320;sheet.paste(im,(x,y));draw.text((x+5,y+303),f'original {t}s / 800x450 landmark source',fill='black')
sheet.save(O/'landmark-comparison.jpg')
print(str(O/'landmark-comparison.jpg'))
