"""Bounded village traversal evidence; not source adoption."""
from PIL import Image, ImageDraw
from polish_common import *
e=Episode('M10');e.authorized();ident='oU__wsOyeiY'
r=read(B/'fhd-candidate-acquisition.json')[ident];src=R/r['path'];assert sha(src)==r['sha256']
out=e.O/'village-source-review';out.mkdir(exist_ok=True)
times=list(range(228,309))+list(range(391,412));samples=[]
for t in times:
 p=out/f'{t}.jpg';e.ff(['-ss',t,'-i',src,'-frames:v','1','-vf','scale=480:270','-threads','1',p],'village-window.log')
 samples.append(dict(seconds=t,image=rel(p),sha256=sha(p)))
for start in range(0,len(samples),12):
 sheet=Image.new('RGB',(1440,1184),'#171717');d=ImageDraw.Draw(sheet)
 for i,r in enumerate(samples[start:start+12]):
  x=i%3*480;y=i//3*296;sheet.paste(Image.open(R/r['image']),(x,y+26));d.text((x+5,y+5),str(r['seconds'])+'s',fill='white')
 sheet.save(out/f'sheet-{start//12+1:02}.jpg',quality=94)
save(e.H/'village-source-review.json',dict(status='await-direct-inspection',source=rel(src),sourceSha256=sha(src),samples=samples,sheets=9,cutApproved=False))
print(len(samples),'village states generated; no production adoption')
