"""Inspect stable visible wood before selecting a short editorial contour."""
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M10');e.authorized();d=read(e.H/'village-cue-review.json')
src=R/d['rawClip'];assert sha(src)==d['rawClipSha256']
out=e.O/'village-stable-targets';out.mkdir(exist_ok=True);records=[]
times=[n/4 for n in range(12,23)]+[n/4 for n in range(96,113)]+[46.75,47,47.25,47.5]
for t in times:
 p=out/f'{t:.2f}.png';e.ff(['-ss',t,'-i',src,'-frames:v','1','-vf','scale=800:450','-threads','1',p],'village-stable-targets.log')
 records.append({'t':t,'path':rel(p),'sha256':sha(p)})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);sheets=[]
for start in range(0,len(records),6):
 im=Image.new('RGB',(1600,1452),'#222222');dr=ImageDraw.Draw(im)
 for i,r in enumerate(records[start:start+6]):
  x=i%2*800;y=i//2*484;im.paste(Image.open(R/r['path']),(x,y+34));dr.text((x+8,y+5),f'M10 +{r["t"]:.2f}s',font=font,fill='white')
 p=out/f'sheet-{start//6+1:02}.jpg';im.save(p,quality=94);sheets.append(rel(p))
save(e.H/'village-stable-targets.json',{'status':'await-direct-inspection','sourceSha256':sha(src),'samples':records,'sheets':sheets})
print(len(records),'stable target states',flush=True)
