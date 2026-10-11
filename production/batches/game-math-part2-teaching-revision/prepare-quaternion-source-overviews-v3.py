"""Local candidate frames and normal-speed player; generation is not approval."""
import cv2
import hashlib
import json
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3'
OUT.mkdir(parents=True,exist_ok=True)
cv2.setNumThreads(2)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
inputs=[
 ('tiny-glade-256965562',ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-256965562.mp4',5),
 ('tiny-glade-257046593',ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-257046593.mp4',5),
 ('trailmakers-257325554',OUT/'sources/trailmakers-257325554.mp4',8),
 ('space-engineers-XvpNC9lkLwQ',OUT/'sources/space-engineers-XvpNC9lkLwQ.mp4',15),
 ('besiege-2036907',OUT/'sources/besiege-2036907.mp4',5),
 ('portal2-steam-80739',OUT/'sources/portal2-steam-80739.mp4',4),
 ('trailmakers-JvTCVUEc1ZE',OUT/'sources/trailmakers-JvTCVUEc1ZE.mp4',20),
 ('besiege-uWKEJ92486U',OUT/'sources/besiege-uWKEJ92486U.mp4',5),
]
rows=[]
for ident,source,stride in inputs:
 if not source.exists():continue
 cap=cv2.VideoCapture(str(source));fps=cap.get(cv2.CAP_PROP_FPS);count=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));seconds=count/fps
 assert fps>0 and count>0
 h=hashlib.sha256()
 with source.open('rb') as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 digest=h.hexdigest();folder=OUT/'overviews'/ident;folder.mkdir(parents=True,exist_ok=True)
 times=[*range(0,math.ceil(seconds),stride),max(0,seconds-0.2)];pages=[]
 for page in range(math.ceil(len(times)/8)):
  sheet=Image.new('RGB',(1280,1568),'white');draw=ImageDraw.Draw(sheet)
  for cell,at in enumerate(times[page*8:page*8+8]):
   if at>=seconds:continue
   cap.set(cv2.CAP_PROP_POS_FRAMES,round(at*fps));ok,img=cap.read();assert ok,(ident,at)
   frame=Image.fromarray(cv2.cvtColor(cv2.resize(img,(640,360)),cv2.COLOR_BGR2RGB))
   x=cell%2*640;y=cell//2*392;sheet.paste(frame,(x,y+32));draw.text((x+5,y+4),f'{ident} {at:.2f}s / native {fps:g}fps',font=font,fill='black')
  file=folder/f'page-{page+1:02}.jpg';sheet.save(file,quality=95);pages.append(file.relative_to(ROOT).as_posix())
 cap.release()
 relative=source.relative_to(OUT.parent).as_posix()
 rows.append({'id':ident,'file':'../'+relative,'sourceFile':source.relative_to(ROOT).as_posix(),'sha256':digest,
              'seconds':seconds,'fps':fps,'frames':count,'overviewStride':stride,'overviewPages':pages,'reviewed':False})
 print(ident,round(seconds,3),len(pages),'pages; selection and normal-speed review pending',flush=True)
(OUT/'source-overviews.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
html='''<!doctype html><meta charset="utf-8"><title>쿼터니언 게임 후보 · 정상속도 검수</title><style>body{background:#202020;color:white;font:16px sans-serif}video{width:min(100%,900px);display:block}button{padding:10px;margin:4px}input{width:100px;padding:8px}</style><h1>쿼터니언 후보 · 실제 동작 비교</h1><div id="choices"></div><label>시작(초)<input id="start" type="number" value="0"></label><label>끝(초)<input id="end" type="number"></label><button id="play">구간 정상속도 재생</button><video controls muted></video><p id="now"></p><pre id="proof"></pre><script>const rows='''+json.dumps(rows,ensure_ascii=False)+''';const v=document.querySelector('video'),start=document.querySelector('#start'),end=document.querySelector('#end');let current=null,seen=[],active=false,began=0;for(const r of rows){const b=document.createElement('button');b.textContent=r.id;b.onclick=()=>{current=r;active=false;v.src=r.file+'?sha='+r.sha256;start.value=0;end.value=r.seconds;document.querySelector('#now').textContent=r.id+' / '+r.sha256};document.querySelector('#choices').append(b)}document.querySelector('#play').onclick=()=>{if(!current)return;v.currentTime=Number(start.value);v.playbackRate=1;began=v.currentTime;active=true;v.play()};function done(){if(!active)return;active=false;v.pause();seen.push({id:current.id,sha256:current.sha256,in:began,out:v.currentTime,requestedOut:Number(end.value),rate:v.playbackRate,normalSpeedReachedEnd:v.currentTime>=Number(end.value)-.1});document.querySelector('#proof').textContent=JSON.stringify(seen,null,2)}v.ontimeupdate=()=>{if(active&&v.currentTime>=Number(end.value))done()};v.onended=done;</script>'''
(OUT/'index.html').write_text(html,encoding='utf-8')
