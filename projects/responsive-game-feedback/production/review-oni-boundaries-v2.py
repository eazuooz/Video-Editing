"""Resolve visible confirmation/blocked/processing transitions before writing narration."""
import json,subprocess,io,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
DEST=Path(__file__).parent/'expanded-source-review-v2'
FILE='shared/assets/responsive-game-feedback/expanded-v2/oni-gameplay-preview.mp4'
points=[('embark',t) for t in range(322,341,2)]+[('print confirm',1535+n*.5) for n in range(22)]
points += [('native reason',t) for t in [498,510,516,518,621,684,884,900,928,1100,1125,1134,3088]]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);records=[]
for page in range(math.ceil(len(points)/24)):
 batch=points[page*24:(page+1)*24];sheet=Image.new('RGB',(1600,math.ceil(len(batch)/4)*256),'white');draw=ImageDraw.Draw(sheet)
 for i,(label,t) in enumerate(batch):
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(ROOT/FILE),'-frames:v','1','-vf','crop=1548:864:372:216,scale=400:225','-f','image2pipe','-vcodec','mjpeg','-'])
  x=i%4*400;y=i//4*256;sheet.paste(Image.open(io.BytesIO(data)).convert('RGB'),(x,y+28));draw.text((x+5,y+3),f'{label} {t:.2f}s',font=font,fill='black')
  if label=='native reason':
   subprocess.check_call(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(ROOT/FILE),'-frames:v','1','-vf','crop=1548:864:372:216',str(DEST/f'native-reason-{t}.png')])
 target=DEST/f'oni-boundaries-{page+1:02}.jpg';sheet.save(target,quality=94);records.append({'sheet':str(target.relative_to(ROOT)).replace('\\','/'),'points':batch})
(DEST/'oni-boundaries.json').write_text(json.dumps({'file':FILE,'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'pages':len(records),'samples':len(points)}))
