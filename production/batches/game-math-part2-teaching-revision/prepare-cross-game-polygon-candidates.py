"""Exact supplementary intervals for normal-speed comparison; no approval."""
from pathlib import Path
import hashlib,json,subprocess,cv2,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'shared/output/game-math-part2-teaching-revision/cross-game-review-20261011/candidates'
O.mkdir(parents=True,exist_ok=True)
dorf=ROOT/'shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm'
fresh=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates'
noita=ROOT/'shared/output/game-math-part2-full-series/sources/igcymdI4XYM.mp4'
plans=[('dorf-placement',dorf,0,17),('dorf-connected-edge',dorf,82,89.5),('dorf-convex-versus-union',dorf,90,123),('shapez-square-cut',fresh/'shapez2-257312662.mp4',39.5,46.8),('noita-center-gap',noita,451,469),('noita-center-return',noita,788,802),('shapez-square-aligned',fresh/'shapez2-257312662.mp4',41.9,49.2)]
rows=[];cv2.setNumThreads(1);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
for ident,source,lo,hi in plans:
 dest=O/(ident+'.mp4')
 if not dest.exists():
  subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(lo),'-i',str(source),'-t',str(hi-lo),'-map','0:v:0','-an','-vf','scale=1920:1080,setsar=1,fps=60','-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-y',str(dest)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 cap=cv2.VideoCapture(str(dest));times=[.1,*range(1,math.ceil(hi-lo)),hi-lo-.1];pictures=[]
 for t in times:
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,im=cap.read();assert ok,(ident,t)
  pictures.append((t,Image.fromarray(cv2.cvtColor(cv2.resize(im,(800,450)),cv2.COLOR_BGR2RGB))))
 cap.release();pages=[]
 for p in range(math.ceil(len(pictures)/6)):
  sheet=Image.new('RGB',(1600,1410),'white');d=ImageDraw.Draw(sheet)
  for cell,(t,im) in enumerate(pictures[p*6:p*6+6]):
   x=cell%2*800;y=cell//2*470;sheet.paste(im,(x,y+20));d.text((x+4,y),f'{ident}: source{lo+t:.2f}s',font=font,fill='black')
  path=O/f'{ident}-{p+1:02}.jpg';sheet.save(path,quality=95);pages.append(path.relative_to(ROOT).as_posix())
 rows.append({'id':ident,'file':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'sourceFile':source.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'interval':[lo,hi],'seconds':hi-lo,'pages':pages,'selected':False})
 print(ident,len(pages),'pages',flush=True)
(O/'inputs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
html='''<!doctype html><meta charset="utf-8"><title>게임 간 비교용 추가 구간 검수</title><style>body{background:#222;color:white;font:18px sans-serif}video{width:min(100%,1100px)}button{padding:12px;margin:5px}</style><h1>추가 구간 · 1배속 비교</h1><button id="all">전체 재생</button><div id="buttons"></div><video controls muted></video><p id="now"></p><pre id="proof"></pre><script>const rows=ROWS;const v=document.querySelector('video');let queue=[],at=0,proof=[];function play(){let r=queue[at];if(!r)return;v.src=r.file+'?sha='+r.sha256;v.playbackRate=1;v.play()}document.querySelector('#all').onclick=()=>{queue=rows;at=0;play()};rows.forEach(r=>{let b=document.createElement('button');b.textContent=r.id;b.onclick=()=>{queue=[r];at=0;play()};document.querySelector('#buttons').append(b)});v.ontimeupdate=()=>{document.querySelector('#now').textContent=queue[at]?.id+' '+v.currentTime.toFixed(2)+'/'+v.duration};v.onended=()=>{proof.push({id:queue[at].id,sha256:queue[at].sha256,seconds:v.duration,rate:v.playbackRate,ended:v.ended});document.querySelector('#proof').textContent=JSON.stringify(proof,null,2);at++;play()};</script>'''
(O/'index.html').write_text(html.replace('ROWS',json.dumps(rows,ensure_ascii=False)),encoding='utf8')
