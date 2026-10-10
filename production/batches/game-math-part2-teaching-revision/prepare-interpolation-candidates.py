"""Native candidate playback, including a retained car example for comparison."""
from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates';D.mkdir(parents=True,exist_ok=True)
windows=[('CAR','ZFGdubPhasM',42,55),('R1','_dw9jjRpanA',196,244),('R2','_dw9jjRpanA',244,292),('R3','_dw9jjRpanA',440,510)]
sheet=Image.new('RGB',(1600,4*250),'white');draw=ImageDraw.Draw(sheet);records=[]
for row,(key,source,a,b) in enumerate(windows):
 folder='game-math-part2-teaching-revision' if source=='_dw9jjRpanA' else 'game-math-part2-full-series';src=ROOT/f'shared/output/{folder}/sources/{source}.mp4';clip=D/f'{key}.mp4'
 if not clip.exists():subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(a),'-i',str(src),'-t',str(b-a),'-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2',str(clip)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 for i,time in enumerate([0,(b-a)/3,2*(b-a)/3,b-a-.1]):
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(time),'-i',str(clip),'-frames:v','1','-vf','scale=400:225','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  sheet.paste(Image.frombytes('RGB',(400,225),raw),(400*i,250*row));draw.text((400*i+8,250*row+230),f'{key} native source {a+time:.2f}',fill='black')
 records.append({'candidate':key,'sourceId':source,'interval':[a,b],'playbackSpeed':1,'referenceAlreadyUsed':key=='CAR','chosen':False,'nativePlaybackReview':False})
sheet.save(D/'comparison.jpg',quality=95);(D/'candidates.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
buttons=''.join(f'<button data-src="{key}.mp4">{key} 원본 {a}–{b}초 전체 재생</button>' for key,source,a,b in windows)
(D/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>회전 보간 · 실제 동작 후보 비교</title><style>body{background:#222;color:#fff;font:18px sans-serif}button{padding:8px;margin:5px}video{display:block;width:min(100%,1100px);max-height:65vh}</style><h1>입력 자세 → 연속 방향 변화 → 다음 자세</h1>'+buttons+'<video id="v" controls muted></video><p id="s">대상·카메라·가림·UI를 나누어 비교</p><script>const v=document.querySelector("video"),s=document.querySelector("#s");for(const b of document.querySelectorAll("button"))b.onclick=()=>{v.src=b.dataset.src;v.play();s.textContent=b.textContent};v.ontimeupdate=()=>s.textContent=s.textContent.split(" | ")[0]+" | "+v.currentTime.toFixed(2)+" / "+v.duration.toFixed(2);v.onended=()=>s.textContent+=" | ended";</script>',encoding='utf8')
print('Four native1x comparison candidates prepared; none selected or approved.')
