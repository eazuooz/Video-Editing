"""Silent native Skate3 intervals; explicit comparison with existing candidates."""
from pathlib import Path
import subprocess,json,html
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates';src=ROOT/'shared/output/game-math-part2-teaching-revision/sources/TPkvx2W8CV8.mp4'
windows=[('S1',105,140),('S2',392,442),('S3',332,363)]
for key,a,b in windows:
 subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(a),'-i',str(src),'-t',str(b-a),'-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2',str(D/f'{key}.mp4')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
records=json.loads((D/'candidates.json').read_text(encoding='utf8'));records=[x for x in records if not x['candidate'].startswith('S')]
records.extend({'candidate':key,'sourceId':'TPkvx2W8CV8','interval':[a,b],'playbackSpeed':1,'referenceAlreadyUsed':False,'chosen':False,'nativePlaybackReview':False} for key,a,b in windows)
(D/'candidates.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
buttons=''.join(f'<button data-src="{x["candidate"]}.mp4">{x["candidate"]} 원본{x["interval"][0]}–{x["interval"][1]}초 재생</button>' for x in records)
(D/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>회전 보간 실제 동작 후보</title><style>body{background:#222;color:#fff;font:18px sans-serif}button{padding:8px;margin:5px}video{display:block;width:min(100%,1100px);max-height:62vh}</style><h1>입력 자세 → 연속 방향 변화 → 다음 자세</h1>'+buttons+'<video id="v" controls muted></video><p id="s">가림·카메라·대상·UI를 비교</p><script>const v=document.querySelector("video"),s=document.querySelector("#s");for(const b of document.querySelectorAll("button"))b.onclick=()=>{v.src=b.dataset.src;v.play();s.textContent=b.textContent};v.ontimeupdate=()=>s.textContent=s.textContent.split(" | ")[0]+" | "+v.currentTime.toFixed(2)+" / "+v.duration.toFixed(2);v.onended=()=>s.textContent+=" | ended";</script>',encoding='utf8')
print('Three native Skate candidates prepared; all selections pending play/compare.')
