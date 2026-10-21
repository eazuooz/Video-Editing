"""Generate version-bound pixel evidence; never grants a review pass."""
import sys, math
from PIL import Image, ImageDraw, ImageFont
from polish_common import *

e=Episode(sys.argv[1]);kind=sys.argv[2] if len(sys.argv)>2 else 'actual'
folder=e.O/f'pixel-review-{kind}';folder.mkdir(exist_ok=True)
records=[];tiles=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
for s in e.T['scenes']:
 if s['classification']!=kind:continue
 clip=e.O/f'clips/{s["id"]}.mp4'
 if not clip.exists():continue
 try:e.verify(clip,s['frames'])
 except Exception:continue
 digest=sha(clip)
 # Discrete temporal samples plus every cut's two sides, using actual captions.
 times={min(s['seconds']-.2,max(.1,x*s['seconds'])) for x in [.12,.36,.62,.88]}
 boundary=0
 for seg in s.get('cut',{}).get('segments',[])[:-1]:
  boundary+=seg['frames']/60
  times.update([max(.1,boundary-.15),min(s['seconds']-.1,boundary+.15)])
 for k,t in enumerate(sorted(times)):
  dst=folder/f'{s["id"]}-{k:02d}.png';receipt=dst.with_suffix('.json')
  sig={'clipSha256':digest,'captionSha256':sha(e.O/'captions.ko.ass'),'scene':s['id'],'localSeconds':t,'globalSeconds':s['start']+t}
  if not (dst.exists() and receipt.exists() and read(receipt)==sig):
   vf=f"setpts=PTS+{s['start']+t}/TB,ass=captions.ko.ass"
   e.ff(['-ss',t,'-i',clip,'-vf',vf,'-frames:v','1','-threads','1',dst],f'review-{kind}.log',e.O)
   save(receipt,sig)
  records.append({**sig,'image':rel(dst)})
  im=Image.open(dst).convert('RGB').resize((375,211),Image.Resampling.LANCZOS)
  tile=Image.new('RGB',(375,240),'#222222');tile.paste(im,(0,29));ImageDraw.Draw(tile).text((6,3),f'{s["id"]} +{t:.2f}s',font=font,fill='white');tiles.append(tile)
for i in range(0,len(tiles),8):
 sheet=Image.new('RGB',(1500,480),'#222222')
 for j,tile in enumerate(tiles[i:i+8]):sheet.paste(tile,((j%4)*375,(j//4)*240))
 sheet.save(folder/f'mobile-{i//8+1:02d}.jpg',quality=94)
save(e.H/f'pixel-review-{kind}-samples.json',{'status':'unreviewed-samples-not-complete-playback','samples':records,'sheets':math.ceil(len(tiles)/8),'existingNarrationUnchanged':True})
print(e.id,kind,len(records),'samples prepared; visual decisions pending',flush=True)
