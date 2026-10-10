"""Inspect earlier unselected actions before authoring dependent narration."""
from pathlib import Path
import subprocess, math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates'
src=ROOT/'shared/output/game-math-part2-teaching-revision/sources/TPkvx2W8CV8.mp4'
for name,a,b,step in [('early',0,54,2),('before-first',76,109,1),('road',282,332,1)]:
    times=list(range(a,b,step));sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*250),'white');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=400:225','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
        x=i%4*400;y=i//4*250;sheet.paste(Image.frombytes('RGB',(400,225),raw),(x,y));draw.text((x+6,y+228),f'{name} source {t}s native',fill='black')
    sheet.save(D/f'{name}-additional-native.jpg',quality=95)
print('Earlier unused dense action grids prepared; comparison still required.')
