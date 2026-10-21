"""Finite, frame-indexed actual-captioned sample proof; no approximate seek."""
from pathlib import Path
import argparse,importlib.util,subprocess
from PIL import Image,ImageDraw
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_sample_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
a=argparse.ArgumentParser();a.add_argument('file');a.add_argument('--frames',required=True);x=a.parse_args()
file=c.R/x.file;frames=sorted(set(map(int,x.frames.split(','))));sig=c.sha(file)
d=c.O/'qa/samples'/sig[:12];d.mkdir(parents=True,exist_ok=True)
receipt=d/'proof.json'
if not receipt.exists():
 args=['ffmpeg','-v','error','-nostdin','-n','-threads','2','-i',str(file),'-vf','select='+ '+'.join(f'eq(n\\,{f})'for f in frames),'-fps_mode','vfr','-frames:v',str(len(frames)),str(d/'frame-%03d.png')]
 subprocess.run(args,check=True,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
 rows=[]
 for i,f in enumerate(frames):
  p=d/f'frame-{i+1:03}.png';im=Image.open(p);assert im.size==(1920,1080)
  mobile=d/f'frame-{i+1:03}.mobile.png';im.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
  rows.append(dict(frame=f,file=c.rel(p),sha256=c.sha(p),mobile=c.rel(mobile)))
 c.save(receipt,dict(source=c.rel(file),sourceSha256=sig,method='Sequential software decode select by decoded frame ordinal',rows=rows))
r=c.read(receipt);contact=Image.new('RGB',(1500,240*((len(frames)+3)//4)),'#242424');dr=ImageDraw.Draw(contact)
for i,row in enumerate(r['rows']):
 xx=i%4*375;yy=i//4*240;contact.paste(Image.open(c.R/row['mobile']),(xx,yy+25));dr.text((xx+4,yy+4),f'frame {row["frame"]}',fill='white')
contact.save(d/'contact.jpg');print(d)
