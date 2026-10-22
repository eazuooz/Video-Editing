"""Dense pixel evidence for manual connection guides; no automatic tracking claims."""
import sys
from PIL import Image, ImageDraw, ImageFont
from polish_common import *
e=Episode('M09'); e.authorized()
windows={'05':[(5.5,7),(31.5,32.5)], '08':[(2,4),(19.5,20.5)],
         'LG02':[(3.5,5.5),(7,8)], 'LG03':[(1,2.5),(32,33)]}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
for sid in sys.argv[1:]:
 d=read(e.H/f'uncle-remaining-candidate-{sid}.json'); src=R/d['rawClip']
 assert sha(src)==d['rawClipSha256']
 out=src.parent/'targets'; out.mkdir(exist_ok=True); samples=[];tiles=[]
 for a,z in windows[sid]:
  for k in range(round((z-a)*4)+1):
   t=a+k/4; p=out/f'{t:.2f}.png'
   e.ff(['-ss',t,'-i',src,'-frames:v',1,'-vf','scale=800:450:flags=lanczos','-threads',1,p],f'm09-{sid}-targets.log')
   im=Image.open(p).convert('RGB')
   tile=Image.new('RGB',(800,480),'#222222');tile.paste(im,(0,30));ImageDraw.Draw(tile).text((7,3),f'{sid} +{t:.2f}s',font=font,fill='white');tiles.append(tile)
   samples.append({'time':t,'frame':round(t*60),'path':rel(p),'sha256':sha(p)})
 sheets=[]
 for i in range(0,len(tiles),6):
  sheet=Image.new('RGB',(2400,960),'#222222')
  for j,tile in enumerate(tiles[i:i+6]):sheet.paste(tile,(j%3*800,j//3*480))
  p=out/f'sheet-{i//6+1:02d}.jpg';sheet.save(p,quality=95);sheets.append(rel(p))
 save(e.H/f'uncle-remaining-targets-{sid}.json',{'status':'await-direct-pixel-inspection','sourceSha256':sha(src),'candidateSha256':sha(e.H/f'uncle-remaining-candidate-{sid}.json'),'samples':samples,'sheets':sheets,'coordinatePixels':[800,450]})
 print(sid,len(samples),'target states',flush=True)
