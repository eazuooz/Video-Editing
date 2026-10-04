"""Preview a fullscreen avatar crop against the current fixed captions."""
from pathlib import Path
import json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
WORK=BASE/'measured-edit-v2';version='v2' if '--v2' in sys.argv else 'v1';crop=[770,260,896,504] if version=='v2' else [1010,130,896,504]
DEST=WORK/('appearance-crop-review' if version=='v1' else 'appearance-crop-review-v2');DEST.mkdir(exist_ok=False)
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
plan=json.loads((WORK/'plan.json').read_text(encoding='utf8'));caps=json.loads((WORK/'captions.json').read_text(encoding='utf8'))['rows']
shot=next(c for s in plan['scenes'] for c in s['segments'] if c['id']=='appearance-01')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
rows=[]
for i,t in enumerate([27,28,29,30,31]):
 p=DEST/f'crop-{i+1}.png';vf=f'crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]},scale=1920:1080,setsar=1'
 subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',str(ROOT/'shared/assets/game-footage/game-reward-planning/mRkJ2uWFWYw.mp4'),'-vf',vf,'-frames:v','1',str(p)],check=True)
 im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);timeline=shot['startFrame']/60+t-shot['sourceInSeconds'];c=next((r for r in caps if r['startSeconds']<=timeline<r['endSeconds']),None)
 if c:
  text=c['ko'];width=round(d.textlength(text,font=font))+44;left=round(960-width/2);top=928
  d.rectangle((left+14,top+14,left+width+14,top+84+14),fill='#073c32');d.rectangle((left,top,left+width,top+84),fill='white',outline='#161b18',width=3)
  d.text((960,970),text,font=font,fill='black',anchor='mm')
 im.save(DEST/f'captioned-{i+1}.png');rows.append({'sourceSecond':t,'timelineSecond':timeline,'cue':c['index'] if c else None,'ko':c['ko'] if c else None,'crop':crop})
page=Image.new('RGB',(1440,3*430),'#eeeeee');d=ImageDraw.Draw(page)
for i,r in enumerate(rows):
 x=i%2*720;y=i//2*430;page.paste(Image.open(DEST/f'captioned-{i+1}.png').resize((720,405)),(x,y));d.text((x+6,y+405),f"{r['sourceSecond']}s · cue {r['cue']}",font=small,fill='black')
page.save(DEST/'contact.png');(DEST/'index.json').write_text(json.dumps({'status':'pending-direct-crop-and-action-review','rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'frames':len(rows),'contact':str(DEST/'contact.png')}))
