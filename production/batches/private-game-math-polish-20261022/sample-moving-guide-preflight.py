"""Inspect intermediate encoded states, not just authored tracking anchors."""
import sys,math
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();manifest=read(e.H/'moving-observed-guide-preflight.json')
out=e.O/'moving-observed-preflight/samples';out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);records=[];tiles=[]
for clip in manifest['clips']:
 sid=clip['scene'];src=R/clip['path'];folder=out/sid;folder.mkdir(exist_ok=True)
 e.ff(['-ss',.25,'-i',src,'-vf','fps=2,scale=750:422','-threads','1',folder/'%04d.png'],'moving-guide-samples-'+sid+'.log')
 count=math.floor((clip['end']-clip['start']-.25)*2+.5)
 for i,p in enumerate(sorted(folder.glob('*.png'))[:count]):
  local=clip['start']+.25+i*.5
  tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(p).convert('RGB').resize((375,211),Image.Resampling.LANCZOS),(0,29))
  ImageDraw.Draw(tile).text((5,3),f'{e.id} {sid} +{local:.2f}s',font=font,fill='white');tiles.append(tile)
  records.append({'scene':sid,'localSecondsApprox':local,'image':rel(p),'imageSha256':sha(p),'videoSha256':clip['sha256']})
sheets=[]
for i in range(0,len(tiles),12):
 sheet=Image.new('RGB',(1500,720),'#222222')
 for j,tile in enumerate(tiles[i:i+12]):sheet.paste(tile,((j%4)*375,(j//4)*240))
 p=out/f'sheet-{i//12+1:02d}.jpg';sheet.save(p,quality=94);sheets.append(rel(p))
save(e.H/'moving-guide-intermediate-samples.json',{'status':'await-direct-inspection','method':'Encoded native-speed preview at2fps offset0.25s; images are temporal samples, not continuous human playback','manifestSha256':sha(e.H/'moving-observed-guide-preflight.json'),'samples':records,'sheets':sheets,'fullMasterApproval':False})
print(e.id,len(records),'encoded intermediate states',len(sheets),'sheets',flush=True)
