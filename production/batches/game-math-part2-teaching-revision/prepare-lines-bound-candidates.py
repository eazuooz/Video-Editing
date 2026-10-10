"""Prepare unused moving bound examples for direct comparison, not approval."""
from pathlib import Path
import json, hashlib, subprocess, math
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'shared/output/game-math-part2-teaching-revision/lines-bound-candidates';D.mkdir(parents=True,exist_ok=True)
source=ROOT/'shared/output/game-math-part2-full-series/sources/4s7nMfXt8uQ.mp4'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);rows=[]
for ident,a,z in [('S01',560,620),('S02',630,700),('S03',705,740)]:
 target=D/(ident+'.mp4')
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a),'-i',str(source),'-t',str(z-a),'-an','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-movflags','+faststart',str(target)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 frames=[]
 for local in [*range(0,math.ceil(z-a),3),z-a-.2]:
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(local),'-i',str(target),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  frames.append((local,Image.frombytes('RGB',(800,450),raw)))
 for page in range(math.ceil(len(frames)/8)):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for i,(local,im) in enumerate(frames[page*8:page*8+8]):
   x=i%2*800;y=i//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{ident} source{a+local:.3f}s',font=font,fill='black')
  sheet.save(D/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
 rows.append({'id':ident,'interval':[a,z],'nativeSpeed':1,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'movingComparison':False})
buttons=''.join(f'<button data-src="{r["id"]}.mp4">{r["id"]} {r["interval"]}</button>' for r in rows)
page='''<!doctype html><meta charset="utf-8"><title>물체 경계 후보 비교</title><style>body{background:#222;color:white;font:16px sans-serif}button{padding:6px;margin:4px}video{width:min(100%,1100px);max-height:70vh;display:block}</style><h1>움직이는 물체와 경계 · 정상 속도 후보 비교</h1><button id="all">전체 재생</button>'''+buttons+'''<video controls muted id="v"></video><p id="s"></p><pre id="r"></pre><script>const v=document.querySelector('video'),s=document.querySelector('#s'),r=document.querySelector('#r');let sequence=[],done=[];function play(src){v.src=src;v.playbackRate=1;v.play();s.textContent=src};for(const b of document.querySelectorAll('button[data-src]'))b.onclick=()=>{sequence=[];play(b.dataset.src)};document.querySelector('#all').onclick=()=>{sequence=['S01.mp4','S02.mp4','S03.mp4'];done=[];play(sequence.shift())};v.ontimeupdate=()=>s.textContent=v.getAttribute('src')+' | '+v.currentTime.toFixed(2)+' / '+v.duration.toFixed(2);v.onended=()=>{done.push({src:v.getAttribute('src'),duration:v.duration,ended:v.ended,rate:v.playbackRate});r.textContent=JSON.stringify(done,null,2);if(sequence.length)play(sequence.shift());else s.textContent+=' | all ended'};</script>'''
(D/'index.html').write_text(page,encoding='utf8');(D/'candidate-records.json').write_text(json.dumps({'sourceFile':source.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidates':rows,'selected':False,'worldOrEngineMeasurement':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Three bound candidates prepared; native comparison and selection pending',flush=True)
