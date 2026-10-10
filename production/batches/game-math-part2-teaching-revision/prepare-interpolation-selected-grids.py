"""Dense observations of proposed intervals, preserving the native 29.97 timebase."""
from pathlib import Path
import subprocess,math,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates'
src=ROOT/'shared/output/game-math-part2-teaching-revision/sources/TPkvx2W8CV8.mp4'
records=[]
for ident,intervals in [('S6-selected',[(155,174)]),('S8-selected',[(458,482),(482,494)]),('S9-selected',[(568,598)])]:
    times=[t for a,b in intervals for t in range(a,b)]
    sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*250),'white');draw=ImageDraw.Draw(sheet)
    for i,time in enumerate(times):
        raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(time),'-i',str(src),'-frames:v','1','-vf','scale=400:225','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
        x=i%4*400;y=i//4*250;sheet.paste(Image.frombytes('RGB',(400,225),raw),(x,y));draw.text((x+6,y+228),f'{ident} requested source {time}s',fill='black')
    sheet.save(D/f'{ident}-fine.jpg',quality=95)
    records.append({'candidate':ident,'proposedIntervals':intervals,'requestedSeconds':times,'sampling':'native seek; no assumed60fps stride','decision':'pending pixel inspection'})
(D/'extra-fine-sampling.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
print('Dense proposed-interval grids ready; no selection approval implied.')
