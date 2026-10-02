from pathlib import Path
import json,subprocess,hashlib,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];WORK=Path(__file__).parent/'final-v1';OUT=WORK/'actual-review';OUT.mkdir(exist_ok=True)
r=json.loads((WORK/'capture-final.json').read_text(encoding='utf-8'));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22);selected=set(sys.argv[1:]);index=json.loads((OUT/'index.json').read_text(encoding='utf-8')) if selected and (OUT/'index.json').exists() else []
for t in r['takes']:
    if t['status']!='finished' or t.get('supersededReason') or (selected and t['id'] not in selected):continue
    index=[v for v in index if v['scene']!=t['id']]
    stamps=[]
    for pi in range(1,5):
        acts=[a for a in t['actions'] if a['paragraph']==pi];begin=min(a['actual'] for a in acts);end=min(t['seconds']-.1,max(a['finished'] for a in acts)+.3);stamps.append((pi,max(begin+.05,end)))
    row=Image.new('RGB',(1920,580),'white');evidence=[]
    for i,(pi,sec) in enumerate(stamps):
        p=OUT/f"{t['id']}-p{pi}.png"
        subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(sec),'-i',str(ROOT/t['finalVideo']),'-frames:v','1','-threads','1',str(p)],check=True,creationflags=0x08000000)
        im=Image.open(p);im.thumbnail((960,540));x=i%2*960;y=i//2*290;im=im.resize((480,270));row.paste(im,(i*480,40));ImageDraw.Draw(row).text((i*480+8,8),f"{t['id']} / P{pi} / {sec:.2f}s",font=font,fill='#202020');evidence.append({'paragraph':pi,'seconds':sec,'path':p.relative_to(ROOT).as_posix()})
    row=row.crop((0,0,1920,310));row.save(OUT/f"{t['id']}-contact.jpg",quality=94)
    index.append({'scene':t['id'],'voiceSha256':t['voiceSha256'],'videoSha256':t['finalSha256'],'maxActionLateness':t['maxActionLateness'],'sampled':evidence,'visualReview':'pending'})
(OUT/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Final narrated-action review images:',len(index))
