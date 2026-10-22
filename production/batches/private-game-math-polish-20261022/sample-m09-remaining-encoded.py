"""Sample encoded guide windows between authored keyframes and at their boundaries."""
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M09');e.authorized();mp=e.H/'moving-available-guide-preflight.json';manifest=read(mp)
out=e.O/'moving-available-preflight/remaining-samples';out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);records=[];tiles=[]
for c in manifest['clips']:
 if c['scene']=='02':continue
 assert sha(R/c['path'])==c['sha256'];duration=c['frames']/60
 times=[.05,*[.325+k*.25 for k in range(int((duration-.325)/.25)+1)],duration-.05]
 for t in times:
  p=out/f"{c['name']}-{t:.3f}.png"
  e.ff(['-ss',t,'-i',R/c['path'],'-frames:v',1,'-vf','scale=750:422:flags=lanczos','-threads',1,p],'m09-encoded-samples.log')
  tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(p).resize((375,211),Image.Resampling.LANCZOS),(0,29));ImageDraw.Draw(tile).text((5,3),f"{c['name']} +{c['start']+t:.3f}s",font=font,fill='white');tiles.append(tile)
  records.append({'clip':c['name'],'localSeconds':c['start']+t,'path':rel(p),'sha256':sha(p),'clipSha256':c['sha256']})
sheets=[]
for i in range(0,len(tiles),12):
 sheet=Image.new('RGB',(1500,720),'#222222')
 for j,tile in enumerate(tiles[i:i+12]):sheet.paste(tile,(j%4*375,j//4*240))
 p=out/f'sheet-{i//12+1:02d}.jpg';sheet.save(p,quality=95);sheets.append(rel(p))
save(e.H/'remaining-encoded-guide-samples.json',{'status':'await-direct-inspection','manifestSha256':sha(mp),'samples':records,'sheets':sheets,'method':'Exact encoded-frame seeks between authored tracking times, plus start/end no-guide checks. Temporal samples, not full continuous listening.','fullMasterApproval':False})
print(len(records),'encoded states',len(sheets),'sheets')
