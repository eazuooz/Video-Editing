"""Scoped existing action preservation review; actual viewing is recorded separately."""
from pathlib import Path
import sys,json,hashlib,shutil,subprocess,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug=sys.argv[1]
assert slug in [x['slug'] for x in json.loads((B/'queue.json').read_text(encoding='utf8'))['items'][2:]]
base=json.loads((B/f'baselines/{slug}/production/timeline.json').read_text(encoding='utf8'))
D=ROOT/f'shared/output/game-math-part2-teaching-revision/remaining-native-review/{slug}';D.mkdir(parents=True,exist_ok=True)
records=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
for slot in base['scenes']:
    if slot['classification']!='actual':continue
    ident=slot['id'];source=ROOT/f'shared/output/{slug}/clips/{ident}.mp4';target=D/f'O{ident}.mp4'
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest()!=sha:shutil.copy2(source,target)
    times=[*range(0,math.ceil(slot['seconds']),2),slot['seconds']-.04];frames=[]
    for i,t in enumerate(times):
        if t>=slot['seconds']:continue
        raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
        image=Image.frombytes('RGB',(800,450),raw);image.save(D/f'O{ident}-{i:03}.png');frames.append((t,image))
    for page in range(math.ceil(len(frames)/8)):
        sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
        for i,(t,image) in enumerate(frames[page*8:page*8+8]):
            x=(i%2)*800;y=(i//2)*470;sheet.paste(image,(x,y+20));draw.text((x+5,y),f'O{ident} local{t:.3f}s',font=font,fill='black')
        sheet.save(D/f'O{ident}-sheet-{page+1:02}.jpg',quality=95)
    records.append({'id':ident,'seconds':slot['seconds'],'baselineClip':source.relative_to(ROOT).as_posix(),'sha256':sha,'cut':slot['cut'],'movingReview':False})
    print('Prepared preserved native action',slug,ident,flush=True)
buttons='<button id="all">원본 동작 전체 정상속도 재생</button>'+''.join(f'<button data-src="O{r["id"]}.mp4">O{r["id"]} 재생</button>' for r in records)
page='''<!doctype html><meta charset="utf-8"><title>기존 동작과 주석 대상 확인</title><style>body{background:#222;color:white;font:16px sans-serif}button{margin:4px;padding:6px}video{display:block;width:min(100%,1100px);max-height:70vh}</style><h1>기존 동작 보존 · 움직이는 주석 대상 확인</h1>'''+buttons+'''<video controls muted id="v"></video><p id="s"></p><pre id="records"></pre><script>const v=document.querySelector('video'),s=document.querySelector('#s'),r=document.querySelector('#records');let sequence=[],done=[];function play(src){v.src=src;v.playbackRate=1;v.play();s.textContent=src}for(const b of document.querySelectorAll('button[data-src]'))b.onclick=()=>{sequence=[];play(b.dataset.src)};document.querySelector('#all').onclick=()=>{sequence='''+json.dumps([f'O{r["id"]}.mp4' for r in records])+'''.slice();done=[];play(sequence.shift())};v.ontimeupdate=()=>s.textContent=v.getAttribute('src')+' | '+v.currentTime.toFixed(2)+' / '+v.duration.toFixed(2);v.onended=()=>{done.push({src:v.getAttribute('src'),duration:v.duration,ended:v.ended,rate:v.playbackRate});r.textContent=JSON.stringify(done,null,2);if(sequence.length)play(sequence.shift());else s.textContent+=' | all ended'};</script>'''
(D/'index.html').write_text(page,encoding='utf8');(D/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
