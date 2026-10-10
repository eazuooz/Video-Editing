"""Recheck preserved action clips and native per-cut pixel time bases."""
from pathlib import Path
import subprocess,json,math,shutil,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-baseline-review';D.mkdir(exist_ok=True)
p=json.loads((B/'baselines/game-math-rotation-interpolation/production/timeline.json').read_text(encoding='utf8'))
records=[]
for row in p['scenes']:
    if row['classification']!='actual':continue
    ident=row['id'];source=ROOT/f'shared/output/game-math-rotation-interpolation/clips/{ident}.mp4'
    shutil.copy2(source,D/f'O{ident}.mp4')
    points=sorted(set([0.,row['seconds']-.05,*[float(i) for i in range(0,math.ceil(row['seconds']),2) if i<row['seconds']]]))
    sheet=Image.new('RGB',(1600,math.ceil(len(points)/4)*250),'white');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(points):
        raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=400:225','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
        x=i%4*400;y=i//4*250;sheet.paste(Image.frombytes('RGB',(400,225),raw),(x,y));draw.text((x+6,y+228),f'O{ident} local {t:.2f}s / actual native clip',fill='black')
    sheet.save(D/f'O{ident}-pixels.jpg',quality=95)
    records.append({'id':ident,'seconds':row['seconds'],'baselineClip':source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cut':row['cut'],'review':'pending actual moving playback and dense pixels'})
buttons='<button id="all">원본 동작 여덟 장면 정상 속도 검토</button>'+''.join(f'<button data-src="O{r["id"]}.mp4">O{r["id"]} {r["seconds"]}초</button>' for r in records)
html='<!doctype html><meta charset="utf-8"><title>보간 원본 동작 연속 검토</title><style>body{background:#222;color:white;font:18px sans-serif}button{padding:8px;margin:5px}video{display:block;width:min(100%,1100px);max-height:65vh}</style><h1>원본 동작 유지 · 주석 대상 확인</h1>'+buttons+'<video id="v" controls muted></video><p id="s">원본 음성·설명·동작 순서 보존</p><pre id="records"></pre><script>const v=document.querySelector("video"),s=document.querySelector("#s"),records=document.querySelector("#records");let sequence=[],done=[];function play(src){v.src=src;v.playbackRate=1;v.play();s.textContent=src}for(const b of document.querySelectorAll("button[data-src]"))b.onclick=()=>{sequence=[];play(b.dataset.src)};document.querySelector("#all").onclick=()=>{sequence='+json.dumps([f'O{r["id"]}.mp4' for r in records])+'.slice();done=[];play(sequence.shift())};v.ontimeupdate=()=>s.textContent=v.getAttribute("src")+" | "+v.currentTime.toFixed(2)+" / "+v.duration.toFixed(2);v.onended=()=>{done.push({src:v.getAttribute("src"),duration:v.duration,ended:v.ended,rate:v.playbackRate});records.textContent=JSON.stringify(done,null,2);if(sequence.length)play(sequence.shift());else s.textContent+=" | all ended"};</script>'
(D/'index.html').write_text(html,encoding='utf8');(D/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Eight original gameplay clips copied exactly for review; no source/voice changed.')
