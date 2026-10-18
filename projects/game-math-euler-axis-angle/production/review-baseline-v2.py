from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v2';Q=O/'baseline-qa';Q.mkdir(parents=True,exist_ok=True)
timeline=json.loads((P/'production/timeline.json').read_text(encoding='utf8')); source=O/'baseline-studio-review-720p30.mp4'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
samples=[]
for s in timeline['scenes']:
 t=s['start']+min(4,s['seconds']/3);out=Q/(s['id']+'.jpg')
 if not out.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(source),'-frames:v','1','-q:v','2',str(out)],check=True)
 samples.append({'scene':s['id'],'title':s['title'],'at':t,'file':str(out.relative_to(R)).replace('\\','/')})
for k in range(0,len(samples),9):
 rows=samples[k:k+9];img=Image.new('RGB',(1280,855),'#dddddd');d=ImageDraw.Draw(img)
 for j,s in enumerate(rows):
  x=(j%3)*426;y=(j//3)*285;frame=Image.open(R/s['file']);frame.thumbnail((426,240));img.paste(frame,(x,y));d.text((x+5,y+242),s['scene']+' · '+s['title'],font=font,fill='#111111')
 img.save(Q/f'board-{k//9+1:02d}.jpg',quality=92)
(Q/'index.json').write_text(json.dumps({'reviewOnly':True,'restoredStudioFileSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceResolution':[1280,720],'notProductionSource':True,'samples':samples},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('26 baseline scene samples;3boards. Restored Studio720p used only to inspect prior output, never as new footage.')
