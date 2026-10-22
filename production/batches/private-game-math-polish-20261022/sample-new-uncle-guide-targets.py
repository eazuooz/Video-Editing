"""Dense visible-target samples for the reviewed village/grapple proposals."""
import sys
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
for ident in sys.argv[1:]:
 e=Episode(ident);e.authorized()
 manifest='village-cue-review.json' if ident=='M10' else 'uncle-cut-review-v3.json'
 d=read(e.H/manifest);src=R/d['rawClip'];assert sha(src)==d['rawClipSha256']
 ranges=[(.5,2.5),(9,10.75),(45,46.5)] if ident=='M10' else [(12,13.25),(24.25,26.25)]
 out=e.O/'new-uncle-guide-targets';out.mkdir(exist_ok=True);records=[]
 for a,z in ranges:
  for n in range(round(a*4),round(z*4)+1):
   t=n/4;p=out/f'{t:.2f}.png';e.ff(['-ss',t,'-i',src,'-frames:v','1','-vf','scale=800:450','-threads','1',p],'new-uncle-guide-targets.log')
   records.append({'localSeconds':t,'path':rel(p),'sha256':sha(p)})
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',19);sheets=[]
 for start in range(0,len(records),6):
  sheet=Image.new('RGB',(1600,1452),'#222222');draw=ImageDraw.Draw(sheet)
  for i,s in enumerate(records[start:start+6]):
   x=i%2*800;y=i//2*484;sheet.paste(Image.open(R/s['path']),(x,y+34));draw.text((x+6,y+5),f'{ident} +{s["localSeconds"]:.2f}s',font=font,fill='white')
  p=out/f'sheet-{start//6+1:02}.jpg';sheet.save(p,quality=94);sheets.append(rel(p))
 save(e.H/'new-uncle-guide-targets.json',{'status':'await-direct-target-inspection','candidate':rel(e.H/manifest),'candidateSha256':sha(e.H/manifest),'sourceSha256':sha(src),'samples':records,'sheets':sheets,'fullMasterReady':False})
 print(ident,len(records),'target states generated',flush=True)
