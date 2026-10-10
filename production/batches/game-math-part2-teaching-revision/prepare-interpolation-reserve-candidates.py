"""Additional action-only intervals for measured narration; no quota padding."""
from pathlib import Path
import subprocess, json, math
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates'
src=ROOT/'shared/output/game-math-part2-teaching-revision/sources/TPkvx2W8CV8.mp4'
cuts={'IG07':[(144,152.6),(193,208.5)],'IG08':[(344.5,356),(525,537.7)],'IG09':[(442,449.5),(543.5,555.8)],'IG10':[(89,107.5)],'IG11':[(4,34.8)]}
for ident,intervals in cuts.items():
    times=[t for a,b in intervals for t in range(math.floor(a),math.ceil(b))]
    sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*250),'white');draw=ImageDraw.Draw(sheet)
    parts=[]
    for i,t in enumerate(times):
        raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=400:225','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
        x=i%4*400;y=i//4*250;sheet.paste(Image.frombytes('RGB',(400,225),raw),(x,y));draw.text((x+6,y+228),f'{ident} source {t}s native seek',fill='black')
    sheet.save(D/f'{ident}-reserve-fine.jpg',quality=95)
    for i,(a,b) in enumerate(intervals,1):
        p=D/f'{ident}-part-{i}.mp4';parts.append(p)
        subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(a),'-i',str(src),'-t',str(b-a),'-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2',str(p)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    listing=D/f'{ident}-concat.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts)+'\n',encoding='utf8')
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(D/f'{ident}.mp4')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
buttons='<button id="all">수정한 다섯 구간 정상 속도 비교</button>'+''.join(f'<button data-src="{k}.mp4">{k} '+', '.join(f'{a}–{b}' for a,b in intervals)+'초</button>' for k,intervals in cuts.items())
html='<!doctype html><meta charset="utf-8"><title>보간 추가 동작 비교</title><style>body{background:#222;color:white;font:18px sans-serif}button{padding:8px;margin:5px}video{display:block;width:min(100%,1100px);max-height:65vh}</style><h1>서로 다른 발췌의 동작과 결과 비교</h1>'+buttons+'<video id="v" controls muted></video><p id="s">추가 후보: 재생과 픽셀 확인 전 승인 없음</p><pre id="records"></pre><script>const v=document.querySelector("video"),s=document.querySelector("#s"),records=document.querySelector("#records");let sequence=[],done=[];function play(src){v.src=src;v.playbackRate=1;v.play();s.textContent=src}for(const b of document.querySelectorAll("button[data-src]"))b.onclick=()=>{sequence=[];play(b.dataset.src)};document.querySelector("#all").onclick=()=>{sequence='+json.dumps([k+'.mp4' for k in cuts])+'.slice();done=[];play(sequence.shift())};v.ontimeupdate=()=>s.textContent=v.getAttribute("src")+" | "+v.currentTime.toFixed(2)+" / "+v.duration.toFixed(2);v.onended=()=>{done.push({src:v.getAttribute("src"),duration:v.duration,ended:v.ended,rate:v.playbackRate});records.textContent=JSON.stringify(done,null,2);if(sequence.length)play(sequence.shift());else s.textContent+=" | all ended"};</script>'
(D/'reserve-cuts.html').write_text(html,encoding='utf8')
(D/'reserve-proposed-cuts.json').write_text(json.dumps({'cuts':cuts,'decision':'pending moving playback and dense pixel comparison'},indent=2)+'\n',encoding='utf8')
print('Five native-speed comparisons prepared; selection remains pending.')
