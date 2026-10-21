"""Sample original source geometry/footage before normalization; no final QA pass."""
import sys,math
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();kind=sys.argv[2];assert kind in ['explanation','actual']
out=e.O/('restored-source-review-'+kind);out.mkdir(exist_ok=True);records=[];tiles=[];source_hashes={}
restored=read(e.H/'explanation-restoration.json') if kind=='explanation' else None
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for slot in e.T['scenes']:
 if slot['classification']!=kind:continue
 times={min(slot['seconds']-.3,max(.2,f*slot['seconds'])) for f in [.12,.38,.64,.88]}
 if kind=='actual':
  at=0
  for s in slot['cut']['segments'][:-1]:at+=s['frames']/60;times.update([at-.15,at+.15])
 for k,t in enumerate(sorted(times)):
  if kind=='explanation':
   record=restored['scenes'][slot['id']];src=R/record['path'];ss=t;digest=record['sha256'];vf=''
  else:
   at=0;found=False
   for segment in slot['cut']['segments']:
    duration=segment['frames']/60
    if t<at+duration:
     src=R/segment.get('sourceFile',slot['cut']['sourceFile']);ss=segment['in']+t-at;found=True;break
    at+=duration
   assert found
   if src not in source_hashes:source_hashes[src]=sha(src)
   digest=source_hashes[src];vf='scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,'
   if slot['cut'].get('sourceFraming'):vf+=slot['cut']['sourceFraming']['filter']+','
  name=f'{slot["id"]}-{k:02d}';dst=out/(name+'.png');sig={'scene':slot['id'],'classification':kind,'source':rel(src),'sourceSha256':digest,'sourceSeconds':ss,'localSeconds':t,'globalSeconds':slot['start']+t,'captionSha256':sha(e.O/'captions.ko.ass')}
  receipt=dst.with_suffix('.json')
  if not(dst.exists() and receipt.exists() and read(receipt)==sig):
   e.ff(['-ss',ss,'-i',src,'-vf',vf+f"setpts=PTS+{slot['start']+t}/TB,ass=captions.ko.ass",'-frames:v','1','-threads','1',dst],'restored-source-preview.log',e.O);save(receipt,sig)
  records.append({**sig,'image':rel(dst)})
  tile=Image.new('RGB',(375,240),'#222222');im=Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS);tile.paste(im,(0,29));ImageDraw.Draw(tile).text((6,3),f'{e.id} {slot["id"]} +{t:.2f}s',font=font,fill='white');tiles.append(tile)
 print(e.id,slot['id'],kind,'source samples generated',flush=True)
for i in range(0,len(tiles),8):
 sheet=Image.new('RGB',(1500,480),'#222222')
 for j,tile in enumerate(tiles[i:i+8]):sheet.paste(tile,(j%4*375,j//4*240))
 sheet.save(out/f'sheet-{i//8+1:02d}.jpg',quality=94)
save(e.H/f'restored-source-review-{kind}.json',{'status':'samples-await-direct-inspection','samples':records,'sheets':math.ceil(len(tiles)/8),'finalMovingPixelReview':'pending','purpose':'Source-level preflight before normalization/final encode; never automatic delivery QA'})
