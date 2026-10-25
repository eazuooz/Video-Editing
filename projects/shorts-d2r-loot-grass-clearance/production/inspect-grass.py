"""CPU-only source selection, restricted to official Act III B-roll."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'local/act3-review';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'production/batches/distinctive-ten-shorts-20261025/local/d2r-official/D2R_Launch_Broll_.mp4'
subprocess.run(['ffmpeg','-v','error','-n','-threads','2','-ss','535','-i',str(SOURCE),'-t','110','-vf','fps=1,scale=960:540','-q:v','2','-threads','1',str(OUT/'%03d.jpg')],check=True)
frames=sorted(OUT.glob('[0-9][0-9][0-9].jpg'))
for base in range(0,len(frames),12):
 canvas=Image.new('RGB',(1920,870),'black');draw=ImageDraw.Draw(canvas)
 for i,p in enumerate(frames[base:base+12]):
  im=Image.open(p);im.thumbnail((480,270));x=i%4*480;y=i//4*290
  canvas.paste(im,(x,y));draw.text((x+8,y+270),f'original {535+base+i}s',fill='white')
 canvas.save(OUT/f'sheet-{base//12+1:02}.jpg',quality=94)
(OUT/'index.json').write_text(json.dumps({'source':str(SOURCE),'range':[535,645],'samplingFps':1,'actualViewed':False,'scope':'source selection frames, not full-speed playback/audio listening'},indent=2),encoding='utf8')
print(json.dumps({'frames':len(frames),'output':str(OUT)}))
