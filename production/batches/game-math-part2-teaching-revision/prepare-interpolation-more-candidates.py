"""Additional native Skate intervals: observations, never selection approval."""
from pathlib import Path
import subprocess,json,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-candidates'
src=ROOT/'shared/output/game-math-part2-teaching-revision/sources/TPkvx2W8CV8.mp4'
windows=[('S6',144,210),('S7',250,320),('S8',442,520),('S9',520,590)]
records=json.loads((D/'candidates.json').read_text(encoding='utf8'))
for key,start,end in windows:
    if not (D/f'{key}.mp4').exists():
        subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-ss',str(start),'-i',str(src),'-t',str(end-start),'-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2',str(D/f'{key}.mp4')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    times=list(range(start,end,5));sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*250),'white');draw=ImageDraw.Draw(sheet)
    for i,time in enumerate(times):
        raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(time),'-i',str(src),'-frames:v','1','-vf','scale=400:225','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
        x=i%4*400;y=i//4*250;sheet.paste(Image.frombytes('RGB',(400,225),raw),(x,y));draw.text((x+6,y+228),f'{key} requested source {time}s',fill='black')
    sheet.save(D/f'{key}-native-grid.jpg',quality=95)
    if not any(r['candidate']==key for r in records):records.append({'candidate':key,'sourceId':'TPkvx2W8CV8','interval':[start,end],'playbackSpeed':1,'referenceAlreadyUsed':False,'chosen':False,'nativePlaybackReview':False})
(D/'candidates.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
buttons=''.join(f'<button data-src="{x["candidate"]}.mp4">{x["candidate"]} 원본{x["interval"][0]}–{x["interval"][1]}초 재생</button>' for x in records)
(D/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>회전 보간 실제 동작 후보</title><style>body{background:#222;color:#fff;font:18px sans-serif}button{padding:8px;margin:5px}video{display:block;width:min(100%,1100px);max-height:62vh}</style><h1>입력 자세 → 연속 방향 변화 → 다음 자세</h1>'+buttons+'<video id="v" controls muted></video><p id="s">가림·카메라·대상·UI를 비교</p><script>const v=document.querySelector("video"),s=document.querySelector("#s");for(const b of document.querySelectorAll("button"))b.onclick=()=>{v.src=b.dataset.src;v.play();s.textContent=b.textContent};v.ontimeupdate=()=>s.textContent=s.textContent.split(" | ")[0]+" | "+v.currentTime.toFixed(2)+" / "+v.duration.toFixed(2);v.onended=()=>s.textContent+=" | ended";</script>',encoding='utf8')
print('Prepared four more native candidates; playback and comparative selection pending.')
