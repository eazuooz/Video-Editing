"""Whole-source overview of official 2016 development gameplay, not a script."""
import json, subprocess, io, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
DEST=Path(__file__).parent/'expanded-source-review-v2';DEST.mkdir(parents=True,exist_ok=True)
FILE='shared/assets/responsive-game-feedback/expanded-v2/oni-gameplay-preview.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(ROOT/FILE)]))
duration=float(probe['format']['duration']);points=[min(n*45+.1,duration-.1) for n in range(math.ceil(duration/45))]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);records=[]
for page in range(math.ceil(len(points)/24)):
 batch=points[page*24:(page+1)*24];sheet=Image.new('RGB',(1600,math.ceil(len(batch)/4)*256),'white');draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(batch):
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(ROOT/FILE),'-frames:v','1','-vf','scale=400:225','-f','image2pipe','-vcodec','mjpeg','-'])
  x=i%4*400;y=i//4*256;sheet.paste(Image.open(io.BytesIO(data)).convert('RGB'),(x,y+28));draw.text((x+5,y+3),f'ONI official 2016 preview {t:.2f}s',font=font,fill='black')
 target=DEST/f'oni-preview-coarse-{page+1:02}.jpg';sheet.save(target,quality=92);records.append({'sheet':str(target.relative_to(ROOT)).replace('\\','/'),'seconds':batch})
(DEST/'oni-preview-coarse.json').write_text(json.dumps({'file':FILE,'sourceDate':'2016-09-07','version':'in-development preview, not current release','probe':probe,'records':records,'scriptPrepared':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'pages':len(records),'samples':len(points),'seconds':duration}))
