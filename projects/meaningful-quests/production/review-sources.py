from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,io,sys
ROOT=Path(__file__).resolve().parents[3]
name=sys.argv[1]
times=[float(v) for v in sys.argv[2:]]
sheet=Image.new('RGB',(1920,((len(times)+4)//5)*254),'white')
draw=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(ROOT/'shared/assets/meaningful-quests/raw'/f'{name}.mp4'),'-frames:v','1','-vf','scale=384:216','-f','image2pipe','-c:v','mjpeg','-'])
    sheet.paste(Image.open(io.BytesIO(data)),((i%5)*384,(i//5)*254))
    draw.text(((i%5)*384+8,(i//5)*254+220),f'{name} / {t}s',fill='black')
sheet.save(Path(__file__).parent/f'{name}-source-review.jpg')
