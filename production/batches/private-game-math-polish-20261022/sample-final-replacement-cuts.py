"""Supplement an existing final review with exact current replacement cut joins."""
import sys,math
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();cutmap=read(e.H/'fhd-replacement-cuts.json')
assert cutmap['status']=='approved-source-cuts'
assert cutmap['originalTimelineSha256']==sha(e.P/'production/timeline.json')
movie=e.D/f'{e.slug}.captioned.mp4';digest=sha(movie)
assert read(e.H/'final-pixel-samples.json')['captionedMasterSha256']==digest
out=e.O/'final-replacement-cuts';out.mkdir(exist_ok=True);records=[];tiles=[]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
for sid,cut in cutmap['scenes'].items():
 s=next(s for s in e.T['scenes'] if s['id']==sid);boundary=round(s['start']*60)
 for j,segment in enumerate(cut['segments'][:-1]):
  boundary+=segment['frames']
  for offset in [-1,1,15]:
   t=(boundary+offset)/60;dst=out/f'{sid}-{j}-{offset}.png'
   e.ff(['-ss',t,'-i',movie,'-frames:v','1','-threads','1',dst],'final-replacement-sampling.log')
   records.append({'scene':sid,'seconds':t,'image':rel(dst),'imageSha256':sha(dst)})
   tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS),(0,29));ImageDraw.Draw(tile).text((5,3),f'{sid} {t:.3f}s',font=font,fill='white');tiles.append(tile)
for i in range(0,len(tiles),12):
 sheet=Image.new('RGB',(1500,720),'#222222')
 for j,tile in enumerate(tiles[i:i+12]):sheet.paste(tile,((j%4)*375,(j//4)*240))
 sheet.save(out/f'sheet-{i//12+1:02d}.jpg',quality=94)
save(e.H/'final-replacement-cut-samples.json',{'status':'await-direct-inspection','captionedMasterSha256':digest,'cutMapSha256':sha(e.H/'fhd-replacement-cuts.json'),'samples':records,'sheets':math.ceil(len(tiles)/12)})
print(e.id,len(records),'current replacement-cut states; direct review pending',flush=True)
