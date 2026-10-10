"""Native1x candidates at observed useful boundaries; selection requires playback."""
from pathlib import Path
import subprocess,json,shutil
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates'
src=ROOT/'shared/output/game-math-part2-teaching-revision/sources/TPkvx2W8CV8.mp4'
cuts={'IG01':[(54,74)],'IG02':[(109.5,140)],'IG03':[(210,247)],'IG04':[(157.3,174.3)],'IG05':[(459,470.8),(482.7,496)],'IG06':[(569,598)]}
for key,intervals in cuts.items():
    parts=[]
    for number,(a,b) in enumerate(intervals,1):
        target=D/f'{key}-part-{number}.mp4';parts.append(target)
        subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(a),'-i',str(src),'-t',str(b-a),'-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2',str(target)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    if len(parts)==1:shutil.copy2(parts[0],D/f'{key}.mp4')
    else:
        listing=D/f'{key}-concat.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts)+'\n',encoding='utf8')
        subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(D/f'{key}.mp4')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
buttons='<button id="all">여섯 구간을 정상 속도로 이어 보기</button>'+''.join(f'<button data-src="{key}.mp4">{key} '+', '.join(f'{a}–{b}' for a,b in intervals)+'초</button>' for key,intervals in cuts.items())
(D/'clean-cuts.html').write_text('<!doctype html><meta charset="utf-8"><title>보간 강의 최종 후보 구간</title><style>body{background:#222;color:#fff;font:18px sans-serif}button{padding:8px;margin:5px}video{display:block;width:min(100%,1100px);max-height:65vh}</style><h1>동작 전 → 방향 변화 → 다음 자세</h1>'+buttons+'<video id="v" controls muted></video><p id="s">후보 재생은 주석·최종 강의 승인과 별개</p><pre id="records"></pre><script>const v=document.querySelector("video"),s=document.querySelector("#s"),records=document.querySelector("#records");let sequence=[],done=[];function play(src){v.src=src;v.playbackRate=1;v.play();s.textContent=src;}for(const b of document.querySelectorAll("button[data-src]"))b.onclick=()=>{sequence=[];play(b.dataset.src)};document.querySelector("#all").onclick=()=>{sequence='+json.dumps([k+'.mp4' for k in cuts])+'.slice();done=[];play(sequence.shift())};v.ontimeupdate=()=>s.textContent=v.getAttribute("src")+" | "+v.currentTime.toFixed(2)+" / "+v.duration.toFixed(2);v.onended=()=>{done.push({src:v.getAttribute("src"),duration:v.duration,ended:v.ended,rate:v.playbackRate});records.textContent=JSON.stringify(done,null,2);if(sequence.length)play(sequence.shift());else s.textContent+=" | all ended"};</script>',encoding='utf8')
(D/'clean-proposed-cuts.json').write_text(json.dumps({'sourceId':'TPkvx2W8CV8','sourceNativeFps':'30000/1001','cuts':cuts,'movingPlaybackAndSelection':'pending'},indent=2)+'\n',encoding='utf8')
print('Six clean candidate sequences prepared, all at native speed, selection pending playback.')
