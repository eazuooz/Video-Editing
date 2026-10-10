"""CPU-only playable candidate intervals for direct comparison, not final footage approval."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'shared/output/game-math-part2-teaching-revision/source-review'
OUT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'shared/output/game-math-part2-full-series/sources/4Odvp_TIeQU.mp4'
windows=[('A',3,15),('B',51,63),('C',99,111),('D',734,746)]
rows=[];sheet=Image.new('RGB',(1280,4*200),'#ffffff');draw=ImageDraw.Draw(sheet)
for row,(key,start,end) in enumerate(windows):
 clip=OUT/f'{key}.mp4'
 if not clip.exists():
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(start),'-i',str(SRC),'-t',str(end-start),'-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','22','-threads','2',str(clip)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 for j,t in enumerate([0,3,6,9]):
  p=OUT/f'{key}-{j}.png'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(t),'-i',str(clip),'-frames:v','1','-vf','scale=320:180',str(p)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  sheet.paste(Image.open(p),(j*320,row*200));draw.text((j*320+8,row*200+182),f'{key} / source {start+t}s',fill='black')
 rows.append({'candidate':key,'sourceId':'4Odvp_TIeQU','sourceIn':start,'sourceOut':end,'clip':clip.relative_to(ROOT).as_posix(),'playedAndCompared':False})
sheet.save(OUT/'candidate-comparison.jpg')
(OUT/'candidates.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
html='<!doctype html><meta charset="utf-8"><title>쿼터니언 실제 동작 비교</title><style>body{background:#181818;color:white;font:20px sans-serif}article{margin:30px}video{width:960px;max-width:95vw}p{max-width:1000px}</style><h1>기존 게임 동작 비교 · Riders Republic</h1><p>현재 상태 → 회전하는 동작 → 결과가 보이는지, 카메라와 가림을 구분해 실제 재생으로 확인한다. 숫자·게임 내부 구현을 추정하지 않는다.</p>'
for key,start,end in windows:html+=f'<article><h2>후보 {key}: 원본 {start}–{end}초</h2><button onclick="document.getElementById(\'video-{key}\').play()">후보 {key} 재생</button><video id="video-{key}" controls muted preload="metadata" src="{key}.mp4"></video></article>'
(OUT/'index.html').write_text(html,encoding='utf8')
print(json.dumps({'candidateClips':len(rows),'sheet':str(OUT/'candidate-comparison.jpg'),'actualPlaybackReviewPending':True}))
