"""Preview observed guides, current captions and intended UI clearance together."""
import sys,math
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();plan=read(e.H/'observed-guides.json');out=e.O/'observed-guide-preflight';out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);tiles=[];records=[];samples={};hashes={}
replacement=read(e.H/'fhd-replacement-cuts.json') if (e.H/'fhd-replacement-cuts.json').exists() else None
if replacement:
 assert replacement['status']=='approved-source-cuts'
 assert replacement['originalTimelineSha256']==sha(e.P/'production/timeline.json')
for guide in plan['guides']:
 for key in guide['keyframes']:
  # Avoid the exact end frame, when the guide is intentionally cleared.
  t=min(key[0],guide['keyframes'][-1][0]-.04)
  samples.setdefault(guide['scene'],set()).add(round(t,3))
for sid,times in samples.items():
 slot=next(x for x in e.T['scenes'] if x['id']==sid)
 cut=replacement['scenes'].get(sid,slot['cut']) if replacement else slot['cut']
 for k,t in enumerate(sorted(times)):
  at=0
  for segment in cut['segments']:
   duration=segment['frames']/60
   if t<at+duration:
    src=R/segment.get('sourceFile',cut['sourceFile']);ss=segment['in']+t-at;break
   at+=duration
  else:raise ValueError('Sample outside cut')
  if src not in hashes:hashes[src]=sha(src)
  vf='scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1'
  if cut.get('sourceFraming'):vf+=','+cut['sourceFraming']['filter']
  if sid in plan['captionClearanceScenes']:vf+=',scale=1600:900:flags=lanczos,pad=1920:1080:160:0:black'
  vf+=f",setpts=PTS+{slot['start']+t}/TB,ass=composition-polish.ass,ass=captions.ko.ass"
  dst=out/f'{sid}-{k:02d}.png';e.ff(['-ss',ss,'-i',src,'-vf',vf,'-frames:v','1','-threads','1',dst],'observed-guide-preflight.log',e.O)
  records.append({'scene':sid,'localSeconds':t,'source':rel(src),'sourceSha256':hashes[src],'sourceSeconds':ss,'image':rel(dst),'imageSha256':sha(dst)})
  tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS),(0,29));ImageDraw.Draw(tile).text((6,3),f'{e.id} {sid} +{t:.2f}s',font=font,fill='white');tiles.append(tile)
 print(e.id,sid,'composited guide states sampled',flush=True)
for i in range(0,len(tiles),8):
 sheet=Image.new('RGB',(1500,480),'#222222')
 for j,tile in enumerate(tiles[i:i+8]):sheet.paste(tile,((j%4)*375,(j//4)*240))
 sheet.save(out/f'sheet-{i//8+1:02d}.jpg',quality=94)
save(e.H/'observed-guide-preflight.json',{'status':'await-direct-still-inspection','planSha256':sha(e.H/'observed-guides.json'),'assSha256':sha(e.O/'composition-polish.ass'),'captionSha256':sha(e.O/'captions.ko.ass'),'samples':records,'sheets':math.ceil(len(tiles)/8),'finalMovingReview':'pending'})
