"""Current pixels at unchanged speech cues; no altered timeline or audio."""
from PIL import Image, ImageDraw, ImageFont
from polish_common import *
cases=[('M11','02',4,8,.5),('M11','02',37.5,40,.5),
       ('M12','21',0,8,.5),('M12','21',38.5,42,.5)]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
records=[]; sheets=[]
for ident,sid,a,z,step in cases:
 e=Episode(ident);e.authorized();out=e.O/'remaining-guide-cues';out.mkdir(exist_ok=True)
 src=e.O/f'clips/{sid}.mp4'; source_hash=sha(src); tiles=[]
 for i in range(round((z-a)/step)+1):
  t=a+i*step;dst=out/f'{sid}-{t:.1f}.png'
  e.ff(['-ss',t,'-i',src,'-vf','scale=640:360:flags=lanczos','-frames:v',1,'-threads',1,dst],'remaining-guide-cues.log')
  tile=Image.new('RGB',(640,390),'#222222');tile.paste(Image.open(dst).convert('RGB'),(0,30))
  ImageDraw.Draw(tile).text((6,4),f'{ident} {sid} +{t:.1f}s',font=font,fill='white');tiles.append(tile)
  records.append({'episode':ident,'scene':sid,'time':t,'path':rel(dst),'sha256':sha(dst),'sourceClip':rel(src),'sourceSha256':source_hash})
 for i in range(0,len(tiles),6):
  sheet=Image.new('RGB',(1920,780),'#222222')
  for j,tile in enumerate(tiles[i:i+6]):sheet.paste(tile,(j%3*640,j//3*390))
  dst=out/f'{sid}-{a:.1f}-sheet-{i//6+1}.jpg';sheet.save(dst,quality=95);sheets.append(rel(dst))
save(B/'remaining-guide-cues.json',{'status':'await-direct-pixel-inspection','samples':records,'sheets':sheets})
print(len(records),'source states',len(sheets),'sheets',flush=True)
