from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,io
ROOT=Path(__file__).resolve().parents[3]
DEST=Path(__file__).parent
files=['raw/super-meat-boy.mp4','raw/hollow-knight-new.mp4','raw/portal.mp4','playtests/landing-sound.mp4','playtests/retry-sound.mp4','playtests/variants-sound.mp4']
sheet=Image.new('RGB',(1920,6*312),'white');draw=ImageDraw.Draw(sheet)
for i,file in enumerate(files):
    source=ROOT/'shared/assets/deconstruct-analyze-rebuild'/file
    for j,time in enumerate([3,9,18,29]):
        data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(time),'-i',str(source),'-frames:v','1','-vf','scale=480:270','-f','image2pipe','-c:v','mjpeg','-'])
        sheet.paste(Image.open(io.BytesIO(data)),(j*480,i*312));draw.text((j*480+8,i*312+280),f'{file} / {time}s',fill='black')
sheet.save(DEST/'source-review.jpg')
