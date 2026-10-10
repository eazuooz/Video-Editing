"""Extract final compositions including original identities; never grant approval."""
from pathlib import Path
import argparse, hashlib, json
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('slug',choices=['game-math-plane-distances-v2','game-math-triangle-addresses-v2']);a=p.parse_args()
P=ROOT/'projects'/a.slug
m=json.loads((P/'project.json').read_text(encoding='utf8'))
t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'))
src=ROOT/m['paths']['videoBurnedCaptions'];D=ROOT/'shared/output'/a.slug/'composition-review';D.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
cv2.setNumThreads(1);cap=cv2.VideoCapture(str(src));rows=[]
for ident,at in [('intro',.8),*[(s['id'],s['start']+s['seconds']*.55) for s in t['scenes']],('outro',t['seconds']-5)]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,round(at*60));ok,img=cap.read();assert ok,(ident,at)
    rows.append({'scene':ident,'time':at})
    im=Image.fromarray(cv2.cvtColor(cv2.resize(img,(960,540)),cv2.COLOR_BGR2RGB))
    rows[-1]['image']=im
cap.release();pages=[]
for start in range(0,len(rows),4):
    sheet=Image.new('RGB',(1920,1120),'#eef0ef');draw=ImageDraw.Draw(sheet)
    for j,r in enumerate(rows[start:start+4]):
        x=j%2*960;y=j//2*560;sheet.paste(r['image'],(x,y+20));draw.text((x+5,y),f'{r["scene"]} {r["time"]:.3f}s',font=font,fill='black')
    f=D/f'composition-{start//4+1:02}.jpg';sheet.save(f,quality=95);pages.append(f.relative_to(ROOT).as_posix())
for r in rows:r.pop('image')
(D/'index.json').write_text(json.dumps({'source':m['paths']['videoBurnedCaptions'],'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'records':rows,'pages':pages,'directReviewPassed':False,'imagesLocalOnly':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(a.slug,len(rows),'current final compositions extracted; review pending',flush=True)
