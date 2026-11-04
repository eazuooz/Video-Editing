"""Local contact sheets for actual-source review; never alters source media."""
from pathlib import Path
import subprocess,json,sys,io
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
LOCAL=HERE.parent/'local/fighters-v3'
def sheet(name,start,end,step,width=384,cols=4):
 source=LOCAL/'sources'/f'{name}.mp4'
 if name=='kirby':source=ROOT/'production/batches/animation-18-20261031/research/A02/candidates/kirby-needle-evolution.mp4'
 out=LOCAL/'source-review';out.mkdir(parents=True,exist_ok=True)
 times=[];t=start
 while t<end:times.append(t);t+=step
 h=int(width*9/16); rows=(len(times)+cols-1)//cols
 canvas=Image.new('RGB',(width*cols,(h+26)*rows),'#181818');draw=ImageDraw.Draw(canvas)
 capfont=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
 for i,t in enumerate(times):
  raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(source),'-frames:v','1','-vf',f'scale={width}:{h}','-f','image2pipe','-vcodec','png','-threads','1','-'])
  img=Image.open(io.BytesIO(raw)).convert('RGB')
  x=(i%cols)*width;y=(i//cols)*(h+26)
  canvas.paste(img,(x,y));draw.text((x+6,y+h+3),f'{name} {t:.2f}s',font=capfont,fill='white')
 dest=out/f'{name}-{start:g}-{end:g}-{step:g}.jpg';canvas.save(dest,quality=88)
 print(dest)
if __name__=='__main__':sheet(sys.argv[1],*map(float,sys.argv[2:5]))
