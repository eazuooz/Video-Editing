"""Inspect retained Townscaper action windows before any retiming decision."""
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M17');e.authorized();src=e.O/'clips/14.mp4';out=e.O/'camera-cue-repair';out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);tiles=[];samples=[];source_sha=sha(src)
for t in range(0,103,3):
 p=out/f'{t:03d}.jpg';e.ff(['-ss',t,'-i',src,'-frames:v',1,'-vf','scale=480:270:flags=lanczos','-q:v',2,p],'camera-cue-samples.log')
 tile=Image.new('RGB',(480,300),'#222222');tile.paste(Image.open(p),(0,30));ImageDraw.Draw(tile).text((6,4),f'M17 14 +{t}s / source{626+t}s',font=font,fill='white');tiles.append(tile);samples.append({'localTime':t,'sourceTime':626+t,'path':rel(p),'sha256':sha(p)})
sheets=[]
for i in range(0,len(tiles),8):
 sheet=Image.new('RGB',(1920,600),'#222222')
 for j,tile in enumerate(tiles[i:i+8]):sheet.paste(tile,(j%4*480,j//4*300))
 p=out/f'sheet-{i//8+1:02d}.jpg';sheet.save(p,quality=95);sheets.append(rel(p))
save(e.H/'camera-cue-repair-samples.json',{'sourceClip':rel(src),'sourceSha256':source_sha,'samples':samples,'sheets':sheets,'status':'await-direct-action-inspection','fullMasterReady':False})
print(len(samples),'camera candidate states')
