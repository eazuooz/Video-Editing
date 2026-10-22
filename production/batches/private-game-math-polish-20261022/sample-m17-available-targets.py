"""Sample source pixels beside unchanged sentence times for M17 guides."""
import math
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M17');e.authorized();out=e.O/'available-targets';out.mkdir(exist_ok=True)
windows={'05':(0,4),'08':(0,7),'14':(13.5,17)}
tiles=[];records=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
for sid,(a,z) in windows.items():
 src=e.O/f'clips/{sid}.mp4'
 for n in range(round((z-a)*2)+1):
  t=a+n*.5;dst=out/f'{sid}-{t:.1f}.png'
  e.ff(['-ss',t,'-i',src,'-vf','scale=480:270:flags=lanczos','-frames:v',1,'-threads',1,dst],'available-targets.log')
  tile=Image.new('RGB',(480,300),'#222222');tile.paste(Image.open(dst).convert('RGB'),(0,30));ImageDraw.Draw(tile).text((5,4),f'M17 {sid} +{t:.1f}s',font=font,fill='white');tiles.append(tile)
  records.append({'scene':sid,'localSeconds':t,'path':rel(dst),'sha256':sha(dst),'sourceSha256':sha(src)})
for i in range(0,len(tiles),8):
 sheet=Image.new('RGB',(1920,600),'#222222')
 for j,tile in enumerate(tiles[i:i+8]):sheet.paste(tile,(j%4*480,j//4*300))
 sheet.save(out/f'sheet-{i//8+1:02d}.jpg',quality=95)
save(e.H/'available-guide-targets.json',{'samples':records,'sheets':math.ceil(len(records)/8),'windows':windows,'status':'await-direct-source-target-inspection','fullMasterApproval':False})
print(len(records),'M17 source target states',flush=True)
