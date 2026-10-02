import json, pathlib, subprocess, math
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[4]
WORK=pathlib.Path(__file__).parent
RAW=ROOT/'shared/assets/blank-project-coding/original-restored-v2/raw'
OUT=WORK/'source-review';OUT.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
report=[]
for file in RAW.glob('*.mp4'):
 if '.f' in file.stem:continue
 p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(file)]))
 duration=float(p['format']['duration'])
 step=25 if duration>300 else 12
 times=list(range(3,int(duration)-2,step))
 frames=[]
 for i,t in enumerate(times):
  dest=OUT/f'{file.stem}-{i:03}.jpg'
  if not dest.exists():subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-ss',str(t),'-i',str(file),'-frames:v','1','-vf','scale=480:270',str(dest)],check=True)
  im=Image.open(dest).convert('RGB');draw=ImageDraw.Draw(im);draw.rectangle((0,0,480,28),fill='#202733');draw.text((8,3),f'{file.stem}  {t:04}s',font=font,fill='white');frames.append(im)
 for k in range(0,len(frames),12):
  chunk=frames[k:k+12];page=Image.new('RGB',(1440,math.ceil(len(chunk)/3)*270),'white')
  for j,im in enumerate(chunk):page.paste(im,((j%3)*480,(j//3)*270))
  page.save(OUT/f'{file.stem}-contact-{k//12+1}.jpg',quality=90)
 report.append({'file':str(file.relative_to(ROOT)).replace('\\','/'),'duration':duration,'sampleTimes':times,'directlyReviewed':False})
(OUT/'index.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('Contact sheets ready',len(report))
