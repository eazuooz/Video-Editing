"""Bounded fresh intervals for comparison, never assumed useful from a game title."""
from pathlib import Path
import json,subprocess,hashlib,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/planes-extra-candidates';O.mkdir(parents=True,exist_ok=True);rows=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
for ident,source_id,begin,end in [('N01','igcymdI4XYM',686,736),('N02','igcymdI4XYM',920,963),('S01','4s7nMfXt8uQ',344,371)]:
 source=ROOT/f'shared/output/game-math-part2-full-series/sources/{source_id}.mp4';target=O/f'{ident}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(begin),'-i',str(source),'-t',str(end-begin),'-an','-vf','scale=800:450,fps=30','-c:v','libx264','-crf','19','-preset','fast','-threads','2','-movflags','+faststart',str(target)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 frames=[]
 for at in [*range(0,end-begin,2),end-begin-.1]:
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(at),'-i',str(target),'-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  if len(raw)==800*450*3:frames.append((at,Image.frombytes('RGB',(800,450),raw)))
 for page in range(math.ceil(len(frames)/8)):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for j,(at,im) in enumerate(frames[page*8:page*8+8]):
   x=j%2*800;y=j//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{ident} source{begin+at:.3f}s',font=font,fill='black')
  sheet.save(O/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
 rows.append({'id':ident,'file':target.name,'sourceId':source_id,'interval':[begin,end],'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'sourceFile':source.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'selected':False,'nativeCompared':False});print('Compared-candidate prepared',ident,flush=True)
(O/'inputs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(O/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>평면 추가 실제 게임 후보 비교</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1050px);display:block}button{padding:10px;margin:4px}</style><h1>추가 구간 후보 · 선택 전 정상 속도 비교</h1><button id="all">후보 전체 재생</button><div id="buttons"></div><video controls muted></video><p id="now"></p><pre id="proof"></pre><script>const rows='''+json.dumps(rows,ensure_ascii=False)+''';const v=document.querySelector('video');let queue=[],at=0,seen=[];function start(){const r=queue[at];if(!r)return;v.src=r.file+'?sha='+r.sha256;v.playbackRate=1;document.querySelector('#now').textContent=r.id+' / '+r.sha256;v.play()}document.querySelector('#all').onclick=()=>{queue=rows;at=0;start()};for(const r of rows){const b=document.createElement('button');b.textContent=r.id;b.onclick=()=>{queue=[r];at=0;start()};document.querySelector('#buttons').append(b)}v.onended=()=>{seen.push({id:queue[at].id,sha256:queue[at].sha256,seconds:v.duration,rate:v.playbackRate,ended:v.ended});document.querySelector('#proof').textContent=JSON.stringify(seen,null,2);at++;start()};</script>''',encoding='utf8')
