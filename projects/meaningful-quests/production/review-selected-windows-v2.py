"""Direct source-window sampling; clips remain normal speed and are never looped."""
from pathlib import Path
import json, subprocess, io, math
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
WORK=Path(__file__).parent/'final-v2';DEST=WORK/'source-proof';DEST.mkdir(parents=True,exist_ok=True)
mapping=json.loads((WORK/'example-map.json').read_text(encoding='utf8'))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
points=[];seen=set()
for chapter in mapping['chapters']:
 for group in chapter['groups']:
  for key,a,b in group['windows']:
   # Dense sampling across edited official trailers; every B-roll boundary/middle too.
   times=[a,(a+b)/2,b-1/60]
   if key.startswith('spirit'): times+=[a+n*.5 for n in range(math.ceil((b-a)*2))]
   for t in sorted(set(times)):
    item=(key,round(t,4))
    if item in seen:continue
    seen.add(item);points.append({'key':key,'seconds':t,'file':mapping['sources'][key]['file']})
records=[]
for page in range(math.ceil(len(points)/24)):
 batch=points[page*24:(page+1)*24];sheet=Image.new('RGB',(1600,math.ceil(len(batch)/4)*256),'white');draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(batch):
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(p['seconds']),'-i',str(ROOT/p['file']),'-frames:v','1','-vf','scale=400:225','-f','image2pipe','-vcodec','mjpeg','-'])
  x=i%4*400;y=i//4*256;sheet.paste(Image.open(io.BytesIO(data)).convert('RGB'),(x,y+28));draw.text((x+5,y+3),f"{p['key']} {p['seconds']:.3f}s",font=font,fill='black')
 target=DEST/f'selected-windows-{page+1:02}.jpg';sheet.save(target,quality=92);records.append({'sheet':str(target.relative_to(ROOT)).replace('\\','/'),'points':batch})
(DEST/'selected-windows.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'pages':len(records),'samples':len(points)}))
