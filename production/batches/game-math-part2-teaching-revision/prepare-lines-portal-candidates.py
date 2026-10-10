"""Native source candidates, not a selection or a rendered-lecture approval."""
from pathlib import Path
import json,hashlib,subprocess,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'shared/output/game-math-part2-teaching-revision/lines-portal-candidates';D.mkdir(parents=True,exist_ok=True)
source=ROOT/'shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='0d233cfcc3eb86b1e7722d257512ed6cfcc2b6276eac0b349fded54c516843bb'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
rows=[]
for ident,a,z in [('P01',16,35),('P02',40,60),('P03',60,80),('P04',80,99.5)]:
 target=D/(ident+'.mp4')
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-ss',str(a),'-i',str(source),'-t',str(z-a),'-an','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-movflags','+faststart',str(target)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 frames=[]
 for t in [*range(0,math.ceil(z-a),2),z-a-.2]:
  if t>=z-a:continue
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(target),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  frames.append((t,Image.frombytes('RGB',(800,450),raw)))
 for page in range(math.ceil(len(frames)/8)):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for i,(t,im) in enumerate(frames[page*8:page*8+8]):
   x=i%2*800;y=i//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{ident} source{a+t:.3f}s',font=font,fill='black')
  sheet.save(D/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
 rows.append({'id':ident,'interval':[a,z],'nativeSpeed':1,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'movingComparison':False})
buttons=''.join(f'<button data-src="{r["id"]}.mp4">{r["id"]} {r["interval"][0]}–{r["interval"][1]}초 재생</button>' for r in rows)
page='''<!doctype html><meta charset="utf-8"><title>직선 후보 비교 · Portal 2</title><style>body{background:#222;color:white;font:16px sans-serif}button{padding:6px;margin:4px}video{width:min(100%,1100px);max-height:70vh;display:block}</style><h1>Portal 2 · 2010 공식 역사 데모 · 직선 사례 후보</h1><p>네 구간을 실제 정상 속도로 비교 · 기존 카메라 투영 챕터 사용 기록 있음 · 엔진 측정 아님</p><button id="all">후보 전체 정상속도 재생</button>'''+buttons+'''<video controls muted id="v"></video><p id="s"></p><pre id="r"></pre><script>const v=document.querySelector('video'),s=document.querySelector('#s'),r=document.querySelector('#r');let sequence=[],done=[];function play(src){v.src=src;v.playbackRate=1;v.play();s.textContent=src}for(const b of document.querySelectorAll('button[data-src]'))b.onclick=()=>{sequence=[];play(b.dataset.src)};document.querySelector('#all').onclick=()=>{sequence=['P01.mp4','P02.mp4','P03.mp4','P04.mp4'];done=[];play(sequence.shift())};v.ontimeupdate=()=>s.textContent=v.getAttribute('src')+' | '+v.currentTime.toFixed(2)+' / '+v.duration.toFixed(2);v.onended=()=>{done.push({src:v.getAttribute('src'),duration:v.duration,ended:v.ended,rate:v.playbackRate});r.textContent=JSON.stringify(done,null,2);if(sequence.length)play(sequence.shift());else s.textContent+=' | all ended'};</script>'''
(D/'index.html').write_text(page,encoding='utf8')
(D/'candidate-records.json').write_text(json.dumps({'source':'https://www.youtube.com/watch?v=yFRbGppLaUI','sourceFile':source.relative_to(ROOT).as_posix(),'rightsPrimary':'https://store.steampowered.com/video_policy/','priorUse':'game-math-camera-projection:16–40 and40–99.5; re-use comparison recorded, not claimed fresh recording','requiredInternalCredit':'Portal 2 – Valve; 2010 pre-release historical demo','humanGameIPReview':'pending','selected':False,'candidates':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Prepared four native Portal 2 candidates; direct comparison pending',flush=True)
