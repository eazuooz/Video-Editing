from common import *
from PIL import Image,ImageDraw,ImageFont
import math,html
P=R/'projects/game-math-camera-frustum';H=P/'production/concept-fit-v2';Q=R/'shared/output/private-math-concept-fit-20261023/candidates/m16';Q.mkdir(parents=True,exist_ok=True)
sources=read(P/'sources/gameplay-cuts.json')['sources']
windows=[('splitA', '8RZ1nPWzWtg', 30, 42, 2), ('townA', 'FRfnXAIbA-M', 175, 246, 3), ('townB', 'FRfnXAIbA-M', 399, 469, 3), ('splitB', '8RZ1nPWzWtg', 293, 307, 2), ('townC', 'FRfnXAIbA-M', 759, 798, 3), ('townD', 'FRfnXAIbA-M', 1429, 1459, 2), ('townE', 'FRfnXAIbA-M', 936, 978, 3), ('townF', 'FRfnXAIbA-M', 1097, 1139, 3)]
rows=[];meta={};font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
for key,s in sources.items():
 p=R/s['file'];v=probe(p);video=next(x for x in v['streams'] if x['codec_type']=='video');assert video['height']>=1080
 meta[key]=dict(path=s['file'],sha256=sha(p),width=video['width'],height=video['height'],fps=video['r_frame_rate'],url=s['url'],rights=s['recordingPermissionObserved'])
for name,key,a,b,step in windows:
 for i in range(math.floor((b-a)/step)+1):
  t=a+i*step;p=Q/f'{name}-{t:09.3f}.jpg'
  if not p.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(R/sources[key]['file']),'-frames:v','1','-q:v','2','-y',str(p)],capture_output=True,check=True)
  rows.append(dict(window=name,source=key,time=t,path=rel(p)))
sheets=[]
for start in range(0,len(rows),12):
 im=Image.new('RGB',(1920,1560),'#111');d=ImageDraw.Draw(im)
 for n,r in enumerate(rows[start:start+12]):
  l=n%3*640;t=n//3*390;im.paste(Image.open(R/r['path']).resize((640,360)),(l,t+30));d.text((l+4,t+4),r['window']+' '+str(r['time']),font=font,fill='white')
 p=Q/f'sheet-{start//12+1:02}.jpg';im.save(p,quality=91);sheets.append(rel(p))
save(Q/'inspection.json',dict(sources=meta,windows=windows,frames=rows,sheets=sheets,directReview='pending'))
D=R/'output/m16-source-review';D.mkdir(exist_ok=True)
buttons=''.join(f'<button data-src="/{sources[key]["file"]}" data-a="{a}" data-b="{b}">{html.escape(name)} {a}–{b}</button>' for name,key,a,b,_ in windows)
(D/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>M16 원본 조작 검수</title><style>body{background:#111;color:white;font:18px system-ui}video{width:min(95vw,1440px)}button{padding:8px;margin:4px}</style><h1>M16 실제 장면</h1><div>'''+buttons+'''</div><p id="state"></p><video controls></video><pre id="proof"></pre><script>const v=document.querySelector('video');let b=Infinity,a=0,records=[];document.querySelectorAll('button').forEach(x=>x.onclick=()=>{v.src=x.dataset.src;a=+x.dataset.a;b=+x.dataset.b;v.onloadedmetadata=()=>{v.currentTime=a;v.playbackRate=1;v.play()}});v.ontimeupdate=()=>{document.querySelector('#state').textContent=v.currentTime+' / '+b+' · '+v.playbackRate+'배속';if(v.currentTime>=b){v.pause();records.push({start:a,end:v.currentTime,rate:v.playbackRate});b=Infinity;document.querySelector('#proof').textContent=JSON.stringify(records,null,2)}};</script>''',encoding='utf8')
print(len(rows),'frames',len(sheets),'sheets',flush=True)
