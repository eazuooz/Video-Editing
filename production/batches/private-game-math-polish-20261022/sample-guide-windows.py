"""Observe source motion for narrow editorial guides; no final-review approval."""
import sys
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();plan=read(e.H/'guide-windows.json')
out=e.O/'guide-source-windows';out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18);hashes={};records=[]
for w in plan['windows']:
 s=next(x for x in e.T['scenes'] if x['id']==w['scene']);tiles=[]
 for k in range(round((w['end']-w['start'])*2)+1):
  t=w['start']+k/2;at=0
  for segment in s['cut']['segments']:
   duration=segment['frames']/60
   if t<at+duration:
    src=R/segment.get('sourceFile',s['cut']['sourceFile']);ss=segment['in']+t-at;break
   at+=duration
  else:raise ValueError('Sample outside source slot')
  if src not in hashes:hashes[src]=sha(src)
  dst=out/f'{s["id"]}-{k:02d}.png'
  sig={'scene':s['id'],'localSeconds':t,'sourceSeconds':ss,'source':rel(src),'sourceSha256':hashes[src]}
  vf='scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1'
  if s['cut'].get('sourceFraming'):vf+=','+s['cut']['sourceFraming']['filter']
  receipt=dst.with_suffix('.json')
  if not(dst.exists() and receipt.exists() and read(receipt)==sig):
   e.ff(['-ss',ss,'-i',src,'-vf',vf,'-frames:v','1','-threads','1',dst],'guide-source-preview.log');save(receipt,sig)
  tile=Image.new('RGB',(640,390),'#222222');tile.paste(Image.open(dst).convert('RGB').resize((640,360),Image.Resampling.LANCZOS),(0,30))
  ImageDraw.Draw(tile).text((8,3),f'{e.id} {s["id"]} +{t:.2f}s',font=font,fill='white');tiles.append(tile)
  records.append({**sig,'image':rel(dst)})
 sheet=Image.new('RGB',(1920,390*((len(tiles)+2)//3)),'#222222')
 for k,tile in enumerate(tiles):sheet.paste(tile,((k%3)*640,(k//3)*390))
 sheet.save(out/f'{s["id"]}-motion.jpg',quality=94)
 print(e.id,s['id'],'source window sampled',flush=True)
save(e.H/'guide-source-samples.json',{'status':'awaiting-direct-observation','samples':records,'finalEncodedMotionReview':'pending'})
