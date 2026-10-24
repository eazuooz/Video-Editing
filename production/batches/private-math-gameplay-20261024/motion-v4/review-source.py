"""Extract ordered native-source frames, never synthesize motion or holds."""
from pathlib import Path
import argparse,json,subprocess
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4]
O=R/'shared/output/private-math-gameplay-20261024/motion-v4/source-review'
def main():
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('source');p.add_argument('start',type=float);p.add_argument('end',type=float);p.add_argument('--step',type=float,default=1);a=p.parse_args()
 d=O/a.name;d.mkdir(parents=True,exist_ok=True)
 subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-ss',str(a.start),'-i',str(R/a.source),'-t',str(a.end-a.start),'-vf',f'fps=1/{a.step},scale=480:-2','-q:v','3',str(d/'%04d.jpg')],check=True)
 files=sorted(d.glob('[0-9]*.jpg'));sheets=[]
 for page in range((len(files)+23)//24):
  group=files[page*24:(page+1)*24];sheet=Image.new('RGB',(480*4,304*((len(group)+3)//4)),'#101412');draw=ImageDraw.Draw(sheet)
  for i,f in enumerate(group):
   im=Image.open(f);x=i%4*480;y=i//4*304;sheet.paste(im,(x,y+25));draw.text((x+8,y+6),f'{a.name} | {a.start+(page*24+i)*a.step:.2f}s',fill='white')
  dst=d/f'sheet-{page}.jpg';sheet.save(dst,quality=90);sheets.append(str(dst))
 print(json.dumps({'frames':len(files),'sheets':sheets}))
if __name__=='__main__':main()
