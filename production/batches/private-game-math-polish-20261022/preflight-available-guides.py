"""Inspect actual restored game pixels with retained tracked contours and captions."""
import sys,math,datetime
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode(sys.argv[1]);assert e.id in ['M10','M11','M12'];e.authorized()
p=e.H/'restored-available-guides.json';plan=read(p);out=e.O/'available-guide-preflight';out.mkdir(exist_ok=True)
points={};records=[];tiles=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for run in plan['visibleIntervals']:
 a,z=run['start'],run['end'];times=[a+.04,*[a+.5*k for k in range(1,math.ceil((z-a)*2))],z-.04]
 for t in times:points[(run['scene'],round(t,3))]=True
for (sid,t) in sorted(points):
 slot=next(s for s in e.T['scenes'] if s['id']==sid);src=e.O/f'clips/{sid}.mp4';dst=out/f'{sid}-{t:.3f}.png'
 vf='scale=1600:900:flags=lanczos,pad=1920:1080:160:0:black,setsar=1,' if sid in plan['captionClearanceScenes'] else ''
 e.ff(['-ss',t,'-i',src,'-vf',vf+f"setpts=PTS+{slot['start']+t}/TB,ass=composition-polish.ass,ass=captions.ko.ass",'-frames:v','1','-threads','1',dst],'available-guide-preflight.log',e.O)
 records.append({'scene':sid,'localSeconds':t,'image':rel(dst),'imageSha256':sha(dst),'sourceSha256':sha(src)})
 tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS),(0,29));ImageDraw.Draw(tile).text((5,3),f'{e.id} {sid} +{t:.3f}s',font=font,fill='white');tiles.append(tile)
for i in range(0,len(tiles),8):
 sheet=Image.new('RGB',(1500,480),'#222222')
 for j,tile in enumerate(tiles[i:i+8]):sheet.paste(tile,(j%4*375,j//4*240))
 sheet.save(out/f'sheet-{i//8+1:02d}.jpg',quality=94)
save(e.H/'observed-guide-preflight.json',{'status':'await-direct-still-inspection','partial':True,'fullMasterReady':False,'planSha256':sha(p),'assSha256':sha(e.O/'composition-polish.ass'),'captionSha256':sha(e.O/'captions.ko.ass'),'samples':records,'sheets':math.ceil(len(tiles)/8),'finalMovingReview':'pending','reviewScope':'Current restored original source clips with original editable contours; byte-changed sources require direct pixel/track equivalence inspection'})
print(e.id,len(records),'restored annotation states await direct inspection',flush=True)
