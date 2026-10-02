from pathlib import Path
import json, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3];WORK=Path(__file__).parent;OUT=WORK/'capture-review';OUT.mkdir(exist_ok=True)
report=json.loads((WORK/'capture-report.json').read_text(encoding='utf-8'));takes={}
for t in report['takes']:
 if t['status']=='finished' and not t.get('supersededReason'):takes[t['id']]=t
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
all_rows=[]
for sid,t in sorted(takes.items()):
 actions=t['actions'];chosen=[]
 for a in actions:
  if a['action'] in ('run','step','input','type') and a['after']<t['seconds']:
   chosen.append(min(t['seconds']-.1,a['after']-.4))
 if not chosen:chosen=[.1,t['seconds']/2,t['seconds']-.2]
 sample=[chosen[0],chosen[len(chosen)//2],chosen[-1]]
 row=Image.new('RGB',(1920,396),'white');files=[]
 for i,sec in enumerate(sample):
  file=OUT/f'{sid}-{i+1}.png'
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(sec),'-i',str(ROOT/t['path']),'-frames:v','1',str(file)],check=True,creationflags=0x08000000)
  im=Image.open(file);im.thumbnail((640,360));row.paste(im,(i*640,36));ImageDraw.Draw(row).text((i*640+12,5),f'{sid}  |  {sec:.2f}s',fill='#202020',font=font);files.append(str(file.relative_to(ROOT)))
 row.save(OUT/f'{sid}-contact.jpg',quality=93);all_rows.append((sid,row))
for j in range(0,len(all_rows),4):
 sheet=Image.new('RGB',(1920,396*len(all_rows[j:j+4])),'white')
 for i,(_,row) in enumerate(all_rows[j:j+4]):sheet.paste(row,(0,i*396))
 sheet.save(OUT/f'contact-{j//4+1}.jpg',quality=92)
(OUT/'inventory.json').write_text(json.dumps({'sampledScenes':list(takes),'status':'screenshots-extracted-awaiting-visual-review','source':'capture-report.json'},indent=2)+'\n',encoding='utf-8')
print('Extracted',len(takes),'actual-development scenes.')
