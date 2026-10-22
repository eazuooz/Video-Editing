"""Unmarked, decoded frame evidence for three observed interpolation defects."""
from PIL import Image, ImageDraw, ImageFont
from polish_common import *
e=Episode('M08');e.authorized();out=e.O/'tracking-repair';out.mkdir(exist_ok=True)
spec={'IG05':[11.8,11.9,12,12.1,12.2,12.3,12.4,12.5],
      'IG08':[2.5,2.75,3,3.25,3.5],
      'IG06':[5,5.25,5.5,5.75,6]}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);items=[]
for sid,times in spec.items():
 src=e.O/'clips'/f'{sid}.mp4'
 for t in times:
  p=out/f'{sid}-{t:.2f}.png';e.ff(['-ss',t,'-i',src,'-frames:v','1','-threads','1',p],'sample-repair.log')
  items.append({'scene':sid,'localSeconds':t,'path':rel(p),'sha256':sha(p)})
 for j in range(0,len(times),4):
  sheet=Image.new('RGB',(960,600),'#222222');d=ImageDraw.Draw(sheet)
  for k,t in enumerate(times[j:j+4]):
   x=k%2*480;y=k//2*300
   sheet.paste(Image.open(out/f'{sid}-{t:.2f}.png').resize((480,270)),(x,y+30));d.text((x+5,y+3),f'{sid} +{t:.2f} (480 x 270 coordinates)',font=font,fill='white')
  sheet.save(out/f'{sid}-sheet-{j//4+1}.jpg',quality=97)
save(e.H/'tracking-repair-evidence.json',{'status':'await-observed-keyframe-correction','source':'Original selected FHD cut without overlays','frames':items,'finalApproval':False})
