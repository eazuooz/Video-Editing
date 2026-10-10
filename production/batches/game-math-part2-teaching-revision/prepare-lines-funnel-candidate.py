"""Direct official Steam movie candidate, not a footage selection."""
from pathlib import Path
import json,hashlib,subprocess,math,shutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'shared/output/game-math-part2-teaching-revision/lines-funnel-candidates';D.mkdir(exist_ok=True)
source=ROOT/'shared/output/game-math-part2-full-series/sources/portal2-steam-5787.mp4';shutil.copy2(source,D/'F01.mp4')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);frames=[]
for t in [*range(0,105,2),105.4]:
 raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
 frames.append((t,Image.frombytes('RGB',(800,450),raw)))
for page in range(math.ceil(len(frames)/8)):
 sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
 for i,(t,im) in enumerate(frames[page*8:page*8+8]):
  x=i%2*800;y=i//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'Portal2 Steam5787 source{t:.3f}s',font=font,fill='black')
 sheet.save(D/f'F01-sheet-{page+1:02}.jpg',quality=95)
page='''<!doctype html><meta charset="utf-8"><title>공식 데모 · 큐브와 이동 범위 비교</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1100px);max-height:70vh;display:block}</style><h1>Portal2 공식 Steam 데모 · 새로운 기록 비교</h1><p>2010 공개 데모 · 원래 최고 화질940×528 · 화면 기하와 내부 판정은 구분</p><button id="all">전체 정상 속도 재생</button><video id="v" src="F01.mp4" controls muted></video><p id="s"></p><pre id="r"></pre><script>const v=document.querySelector('video'),s=document.querySelector('#s'),r=document.querySelector('#r');document.querySelector('#all').onclick=()=>{v.currentTime=0;v.playbackRate=1;v.play()};v.ontimeupdate=()=>s.textContent=v.currentTime.toFixed(3)+' / '+v.duration.toFixed(3);v.onended=()=>{s.textContent+=' | all ended';r.textContent=JSON.stringify([{src:'F01.mp4',ended:v.ended,rate:v.playbackRate,duration:v.duration}],null,2)};</script>'''
(D/'index.html').write_text(page,encoding='utf8');(D/'candidate-records.json').write_text(json.dumps(dict(source='https://store.steampowered.com/app/620/Portal_2/',metadata='shared/output/game-math-part2-full-series/sources/portal2-steam-5787.info.json',id='portal2-steam-5787',sourceFile=source.relative_to(ROOT).as_posix(),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),nativeHighestSourceResolution=[940,528],historicalPreview=True,rightsPolicy='https://store.steampowered.com/video_policy/',nativeReview=False,selection=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Official Steam candidate dense sheets ready; moving comparison pending',flush=True)
