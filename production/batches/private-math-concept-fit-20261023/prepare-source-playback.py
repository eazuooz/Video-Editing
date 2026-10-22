from common import *
import html
sources=[
 dict(id='M05 bridge',source='projects/game-math-euler-axis-angle/production/local/revision-v3/sources/YNQ20CKbY8U-hls.mp4',start=418,end=436),
 dict(id='M05 copy and place',source='shared/output/private-math-concept-fit-20261023/sources/se2-official/vs1.2.mp4',start=101,end=112),
 dict(id='M05 house tile',source='shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm',start=35,end=44)]
out=R/'output/private-math-source-review';out.mkdir(exist_ok=True)
buttons=''.join(f'<button data-i="{i}">{html.escape(s["id"])} · {s["start"]}–{s["end"]}초</button>' for i,s in enumerate(sources))
(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>게임 장면 원속도 확인</title><style>body{background:#101512;color:white;font:18px system-ui}video{width:min(95vw,1100px)}button{padding:10px;margin:5px}</style><h1>장면 원속도 확인</h1>'''+buttons+'''<p id="state"></p><video controls></video><pre id="proof"></pre><script>const shots='''+json.dumps(sources)+''';const v=document.querySelector('video');let current=null,proof=[];document.querySelectorAll('button[data-i]').forEach(b=>b.onclick=()=>{current=shots[+b.dataset.i];v.src='/'+current.source;v.onloadedmetadata=()=>{v.currentTime=current.start;v.playbackRate=1;v.play()}});v.ontimeupdate=()=>{document.querySelector('#state').textContent=(current?.id||'')+' '+v.currentTime.toFixed(3)+' · '+v.playbackRate+'배속';if(current&&v.currentTime>=current.end){v.pause();proof.push({id:current.id,start:current.start,end:v.currentTime,rate:v.playbackRate});document.querySelector('#proof').textContent=JSON.stringify(proof,null,2);current=null}};</script>''',encoding='utf8')
save(B/'source-playback-shots.json',sources)
