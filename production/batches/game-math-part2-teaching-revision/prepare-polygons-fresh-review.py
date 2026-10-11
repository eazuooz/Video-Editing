"""Compare official new-title candidates before dependent gameplay narration."""
from pathlib import Path
import cv2,json,math,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates'
rows=json.loads((O/'inputs.json').read_text(encoding='utf8'));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15);cv2.setNumThreads(2)
for row in rows:
    source=O/row['file'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
    cap=cv2.VideoCapture(str(source));fps=cap.get(cv2.CAP_PROP_FPS);times=[*range(0,math.ceil(row['seconds']),2),row['seconds']-.1];images=[]
    for at in times:
        if at>=row['seconds']:continue
        frame=round(at*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,img=cap.read();assert ok,(row['id'],at)
        images.append((frame/fps,Image.fromarray(cv2.cvtColor(cv2.resize(img,(800,450)),cv2.COLOR_BGR2RGB))))
    cap.release();pages=[]
    for page in range(math.ceil(len(images)/8)):
        sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
        for cell,(at,im) in enumerate(images[page*8:page*8+8]):
            x=cell%2*800;y=cell//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{row["id"]} native{at:.3f}s',font=font,fill='black')
        file=O/f'{row["id"]}-{page+1:02}.jpg';sheet.save(file,quality=95);pages.append(file.name)
    row['comparisonPages']=pages;print('Fresh candidate',row['id'],row['seconds'],len(pages),'pages; not approved',flush=True)
(O/'inputs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
page='''<!doctype html><meta charset="utf-8"><title>다각형 새 게임 후보 비교</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1100px);display:block}button{padding:10px;margin:4px}</style><h1>다각형 후보 · 선택 전 정상속도 비교</h1><button id="all">후보 전체 재생</button><div id="buttons"></div><video controls muted></video><p id="now"></p><pre id="proof"></pre><script>const rows='''+json.dumps(rows,ensure_ascii=False)+''';const v=document.querySelector('video');let queue=[],at=0,seen=[];function start(){const r=queue[at];if(!r)return;v.src=r.file+'?sha='+r.sha256;v.playbackRate=1;document.querySelector('#now').textContent=r.id+' / '+r.sha256;v.play()}document.querySelector('#all').onclick=()=>{queue=rows;at=0;start()};for(const r of rows){const b=document.createElement('button');b.textContent=r.id;b.onclick=()=>{queue=[r];at=0;start()};document.querySelector('#buttons').append(b)}v.onended=()=>{seen.push({id:queue[at].id,sha256:queue[at].sha256,seconds:v.duration,rate:v.playbackRate,ended:v.ended});document.querySelector('#proof').textContent=JSON.stringify(seen,null,2);at++;start()};</script>'''
(O/'index.html').write_text(page,encoding='utf8')
