"""Research actual-action/cinematic boundaries without changing frozen TTS inputs."""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/motion-sickness-games/production/source-fit-followup/talos-action-edges'
BASE.mkdir(parents=True,exist_ok=True)
source=ROOT/'shared/assets/game-footage/motion-sickness-games/6slinvkF0Rs.mp4'
times=[15.5,15.8,15.9,16,40.5,40.8,41,41.3,41.6,41.9,42,42.1,42.2,47,47.5,48,48.5,49,49.5,50,50.5,51,51.5,52,52.4]
indices=sorted(set(round(t*30) for t in times))
vf='select='+'+'.join(f'eq(n\\,{n})' for n in indices)
result=subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',str(source),'-filter_threads','1','-vf',vf,'-fps_mode','vfr','-frames:v',str(len(indices)),'-q:v','2',str(BASE/'frame-%02d.jpg')],capture_output=True,text=True)
if result.returncode or result.stderr:raise RuntimeError(result.stderr)
rows=[{'sourceSeconds':frame/30,'nativeFrame':frame,'file':(BASE/f'frame-{i+1:02d}.jpg').relative_to(ROOT).as_posix()} for i,frame in enumerate(indices)]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21);contacts=[]
for offset in range(0,len(rows),12):
    sheet=Image.new('RGB',(1920,936),'white');draw=ImageDraw.Draw(sheet)
    for k,row in enumerate(rows[offset:offset+12]):
        x,y=k%4*480,k//4*312;sheet.paste(Image.open(ROOT/row['file']).resize((480,270)),(x,y))
        draw.text((x+6,y+276),f"Talos2 {row['sourceSeconds']:.4f}s",font=font,fill='#073c32')
    dest=BASE/f'contact-{offset//12+1}.jpg';sheet.save(dest,quality=93);contacts.append(dest.relative_to(ROOT).as_posix())
report={'sourceId':'6slinvkF0Rs','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'images':rows,'contacts':contacts,'decodeMethod':'Full linear decode/native-frame select; no stderr and exit0.','directReview':'pending','finalTimingApproved':False,'frozenInputsChanged':False}
(BASE/'images.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'images':len(rows),'contacts':contacts}))
