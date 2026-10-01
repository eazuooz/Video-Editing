"""Inspect new request/menu/placement/processing candidates from the actual demo."""
import json, subprocess, io, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
DEST=Path(__file__).parent/'expanded-source-review-v2';DEST.mkdir(parents=True,exist_ok=True)
FILE='shared/assets/responsive-game-feedback/expanded-v2/oni-gameplay-preview.mp4'
windows=[('crew selection',264,322),('placement',436,474),('resource status',1098,1148),('jobs menu',1018,1086),('selection confirmation',1490,1540),('construction',608,688),('pending work',880,958),('context overlay',488,522),('state controls',3080,3140)]
points=[]
for label,a,b in windows:
 for t in sorted(set([a,(a+b)/2,b-1/30]+[a+n*2 for n in range(math.ceil((b-a)/2))])):
  points.append({'label':label,'seconds':t})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);records=[]
for page in range(math.ceil(len(points)/24)):
 batch=points[page*24:(page+1)*24];sheet=Image.new('RGB',(1600,math.ceil(len(batch)/4)*256),'white');draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(batch):
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(p['seconds']),'-i',str(ROOT/FILE),'-frames:v','1','-vf','crop=1548:864:372:216,scale=400:225','-f','image2pipe','-vcodec','mjpeg','-'])
  x=i%4*400;y=i//4*256;sheet.paste(Image.open(io.BytesIO(data)).convert('RGB'),(x,y+28));draw.text((x+5,y+3),f"{p['label']} {p['seconds']:.2f}s",font=font,fill='black')
 target=DEST/f'oni-actions-{page+1:02}.jpg';sheet.save(target,quality=93);records.append({'sheet':str(target.relative_to(ROOT)).replace('\\','/'),'points':batch})
(DEST/'oni-actions.json').write_text(json.dumps({'file':FILE,'crop':[372,216,1548,864],'cropPurpose':'Remove publisher stream face/brand border, preserve complete native game UI; source title/version remains documented and will be labeled.','records':records,'scriptPrepared':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'pages':len(records),'samples':len(points)}))
