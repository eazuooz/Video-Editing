"""Keep the original8 gameplay cuts editable; compare their current moving pixels."""
from pathlib import Path
import json,hashlib,shutil,subprocess,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision/planes-baseline-review';O.mkdir(parents=True,exist_ok=True)
t=json.loads((B/'baselines/game-math-planes-barycentric/production/timeline.json').read_text(encoding='utf8'));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15);rows=[]
for s in t['scenes']:
 if s['classification']!='actual':continue
 source=ROOT/f'shared/output/game-math-planes-barycentric/clips/{s["id"]}.mp4';target=O/source.name;shutil.copy2(source,target)
 rows.append({'id':s['id'],'file':target.name,'seconds':s['seconds'],'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cut':s['cut']})
 frames=[]
 for at in [*range(0,math.floor(s['seconds']),2),s['seconds']-.15]:
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(at),'-i',str(source),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  if len(raw)==800*450*3:frames.append((at,Image.frombytes('RGB',(800,450),raw)))
 for page in range(math.ceil(len(frames)/8)):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for j,(at,im) in enumerate(frames[page*8:page*8+8]):
   x=j%2*800;y=j//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'Original{s["id"]} local{at:.3f}s',font=font,fill='black')
  sheet.save(O/f'{s["id"]}-sheet-{page+1:02}.jpg',quality=95)
 print('Prepared retained gameplay',s['id'],flush=True)
(O/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>평면 원본 게임 예시 검수</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1050px);display:block}button{padding:9px;margin:4px}#proof{white-space:pre-wrap}</style><h1>평면·삼각형 원본8개 예시 정상 속도 재검수</h1><button id="all">원본 전체 연속 재생</button><div id="buttons"></div><video controls muted></video><p id="now"></p><pre id="proof"></pre><script>const rows='''+json.dumps(rows,ensure_ascii=False)+''';const v=document.querySelector('video');let queue=[],at=0,seen=[];function start(){const r=queue[at];if(!r)return;v.src=r.file+'?sha='+r.sha256;v.playbackRate=1;document.querySelector('#now').textContent=r.id+' / '+r.sha256;v.play()}document.querySelector('#all').onclick=()=>{queue=rows;at=0;start()};for(const r of rows){const b=document.createElement('button');b.textContent=r.id;b.onclick=()=>{queue=[r];at=0;start()};document.querySelector('#buttons').append(b)}v.onended=()=>{seen.push({id:queue[at].id,sha256:queue[at].sha256,seconds:v.duration,rate:v.playbackRate,ended:v.ended});document.querySelector('#proof').textContent=JSON.stringify(seen,null,2);at++;start()};</script>''',encoding='utf8')
(O/'inputs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
