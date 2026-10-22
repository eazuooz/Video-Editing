"""Sample only the new grapple target windows, without rewriting narration."""
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M11');e.authorized();candidate=read(e.H/'uncle-cut-review-v2.json')
src=R/candidate['rawClip'];assert sha(src)==candidate['rawClipSha256']
out=e.O/'uncle-guide-source';out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);records=[];tiles=[]
for a,z in [(12.5,15.5),(38,39.5)]:
 for i in range(round((z-a)*4)+1):
  t=a+i/4;p=out/f'{t:.2f}.png'
  e.ff(['-ss',t,'-i',src,'-vf','scale=640:360','-frames:v',1,'-threads',1,p],'uncle-guide-source.log')
  tile=Image.new('RGB',(640,390),'#222222');tile.paste(Image.open(p),(0,30));ImageDraw.Draw(tile).text((5,4),f'M11 08 +{t:.2f}s',font=font,fill='white');tiles.append(tile)
  records.append({'localSeconds':t,'image':rel(p),'sha256':sha(p)})
sheets=[]
for i in range(0,len(tiles),6):
 sheet=Image.new('RGB',(1920,780),'#222222')
 for j,tile in enumerate(tiles[i:i+6]):sheet.paste(tile,(j%3*640,j//3*390))
 p=out/f'sheet-{i//6+1:02d}.jpg';sheet.save(p,quality=94);sheets.append(rel(p))
save(e.H/'uncle-guide-source.json',{'sourceClip':rel(src),'sourceSha256':sha(src),'samples':records,'sheets':sheets,'status':'await-direct-inspection'})
