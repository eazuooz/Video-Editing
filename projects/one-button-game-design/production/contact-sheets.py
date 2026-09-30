from pathlib import Path
from PIL import Image, ImageDraw
import io, subprocess
ROOT=Path(__file__).resolve().parents[3]
dest=Path(__file__).parent/'footage-review'
dest.mkdir(exist_ok=True)
for name,offset in [('super-star-minigames',1980),('adventure-egg-2',2637)]:
    path=ROOT/'shared/assets/one-button-game-design/raw'/f'{name}.mp4'
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)]))
    points=list(range(2,int(duration),5))
    sheet=Image.new('RGB',(1800,((len(points)+5)//6)*288),'white')
    draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(points):
        data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(path),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
        pic=Image.open(io.BytesIO(data));pic.thumbnail((294,252))
        x=(i%6)*300+(300-pic.width)//2;y=(i//6)*288
        sheet.paste(pic,(x,y));draw.text(((i%6)*300+12,y+260),f'file {t}s / original {offset+t}s',fill='black')
    sheet.save(dest/f'{name}.jpg')
