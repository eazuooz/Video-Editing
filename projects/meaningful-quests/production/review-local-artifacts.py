from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,io
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent
def sheet(points,target):
    result=Image.new('RGB',(1920,((len(points)+2)//3)*390),'white');d=ImageDraw.Draw(result)
    for i,(file,t,label) in enumerate(points):
        data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(file),'-frames:v','1','-vf','scale=640:360','-f','image2pipe','-c:v','mjpeg','-']);result.paste(Image.open(io.BytesIO(data)),(i%3*640,i//3*390));d.text((i%3*640+10,i//3*390+365),label,fill='black')
    result.save(BASE/target)
reel=ROOT/'shared/output/motion-canvas/meaningful-quests-lookdev.mp4'
sheet([(reel,i*10+3,f'diagram {i+1} early') for i in range(6)]+[(reel,i*10+7,f'diagram {i+1} late') for i in range(6)],'lookdev-review.jpg')
raw=ROOT/'shared/assets/meaningful-quests/playtests-v2'
sheet([(raw/(mode+'.mp4'),t,f'{mode} at {t}s') for mode in ['comparison','delivery','shortcut'] for t in [5.5,14.8,18.5,23.5]],'playtest-review.jpg')
