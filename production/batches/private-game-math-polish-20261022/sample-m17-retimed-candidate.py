"""Find a same-source action offset matching the immutable camera narration."""
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M17');e.authorized();s=next(s for s in e.T['scenes'] if s['id']=='14');src=R/s['cut']['sourceFile']
out=e.O/'camera-cue-candidate-647';out.mkdir(exist_ok=True);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
groups={'orbit':[12+i*.5 for i in range(13)],'higher':[26+i*.5 for i in range(11)],'end':[81.5+i for i in range(9)]+[93,96,99,102]}
records=[];sheets=[]
for name,times in groups.items():
 tiles=[]
 for t in times:
  p=out/f'{name}-{t:.1f}.jpg';e.ff(['-ss',647+t,'-i',src,'-vf','scale=640:360:flags=lanczos','-frames:v',1,'-q:v',2,p],'camera-cue-candidate.log')
  tile=Image.new('RGB',(640,390),'#222222');tile.paste(Image.open(p),(0,30));ImageDraw.Draw(tile).text((6,4),f'M17 14 new+{t:.1f}s / source{647+t:.1f}s',font=font,fill='white');tiles.append(tile);records.append({'group':name,'localTime':t,'sourceTime':647+t,'path':rel(p),'sha256':sha(p)})
 for i in range(0,len(tiles),6):
  sheet=Image.new('RGB',(1920,780),'#222222')
  for j,tile in enumerate(tiles[i:i+6]):sheet.paste(tile,(j%3*640,j//3*390))
  p=out/f'{name}-sheet-{i//6+1:02d}.jpg';sheet.save(p,quality=95);sheets.append(rel(p))
save(e.H/'camera-cue-candidate-647.json',{'status':'candidate-await-direct-action-review','sourceFile':rel(src),'sourceSha256':sha(src),'sourceIn':647,'frames':s['frames'],'samples':records,'sheets':sheets,'originalSceneOrderAndDurationPreserved':True,'fullMasterReady':False})
print(len(records),'source states await direct review')
