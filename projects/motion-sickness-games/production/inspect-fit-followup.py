"""Research unused intervals at normal source clock; no final cuts or approval."""
from pathlib import Path
import json, subprocess, hashlib
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/motion-sickness-games/production/source-fit-followup'
SOURCE=ROOT/'shared/assets/game-footage/motion-sickness-games/PF5L_2g9UVQ.mp4'
assert SOURCE.exists()
groups={'aim-transition':[69+2*n for n in range(16)],
        'roundabout':[169+2*n for n in range(10)],
        'overhead':[227+2*n for n in range(11)],
        'lower-post-transition':[339+n for n in range(7)],
        'boards-to-slide':[383+2*n for n in range(13)]}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
items=[]
for name,times in groups.items():
    for t in times:
        dest=BASE/f'pws-{t:03}.jpg'
        if not dest.exists():
            subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(SOURCE),'-frames:v','1','-q:v','2',str(dest)],check=True,stdout=subprocess.DEVNULL)
        items.append({'group':name,'sourceSeconds':t,'file':dest.relative_to(ROOT).as_posix()})
contacts=[]
for offset in range(0,len(items),12):
    sheet=Image.new('RGB',(1920,936),'#ffffff')
    draw=ImageDraw.Draw(sheet)
    for k,row in enumerate(items[offset:offset+12]):
        x,y=(k%4)*480,(k//4)*312
        frame=Image.open(ROOT/row['file']).convert('RGB').resize((480,270))
        sheet.paste(frame,(x,y));draw.text((x+8,y+275),f"{row['sourceSeconds']:03}s  {row['group']}",font=font,fill='#073c32')
    dest=BASE/f'contact-{offset//12+1}.jpg';sheet.save(dest,quality=93);contacts.append(dest.relative_to(ROOT).as_posix())
report={'sourceId':'PF5L_2g9UVQ','sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'kind':'Research unused action intervals for pending voice fit; not final cut approval.',
        'frames':items,'contactSheets':contacts,'directReview':'pending','finalTimingApproved':False,
        'lockedInputsModified':False}
(BASE/'research-images.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'images':len(items),'contacts':contacts,'finalApproval':False}))
