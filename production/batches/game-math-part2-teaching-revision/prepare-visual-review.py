from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision';V=O/'visual-previews-v2/videos/supplements/480p15'
sheet=Image.new('RGB',(1280,8*205),'white');draw=ImageDraw.Draw(sheet);records=[]
html='<!doctype html><meta charset="utf-8"><title>쿼터니언 추가 설명 화면 검수</title><style>body{background:#222;color:white;font:20px sans-serif}video{width:960px;max-width:95vw}article{margin:30px}</style><h1>보충 설명8장면 · 무음 화면 초안 · 최종 강의 아님</h1>'
for row in range(8):
 key=f'N{row+1:02d}';file=O/f'visual-previews-v3/videos/supplements/480p15/{key}.mp4'
 if not file.exists():file=V/f'{key}.mp4'
 assert file.exists()
 raw=subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)],creationflags=subprocess.CREATE_NO_WINDOW);meta=json.loads(raw);seconds=float(meta['format']['duration'])
 html+=f'<article><h2>{key} 보충 설명</h2><button onclick="document.getElementById(\'{key}\').play()">{key} 재생</button><video id="{key}" controls muted src="{file.relative_to(O).as_posix()}"></video></article>'
 for col,t in enumerate([.5,seconds*.4,seconds*.7,seconds-.2]):
  frame=O/f'qa/{key}-{col}.png';frame.parent.mkdir(exist_ok=True)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(t),'-i',str(file),'-frames:v','1','-vf','scale=320:180',str(frame)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  sheet.paste(Image.open(frame),(col*320,row*205));draw.text((col*320+5,row*205+183),f'{key} / {t:.2f}s',fill='black')
 records.append({'scene':key,'file':file.relative_to(ROOT).as_posix(),'seconds':seconds,'resolution':[854,480],'fps':15,'status':'preview-only-before-measured-narration','narratedRenderComplete':False})
(O/'visual-review.html').write_text(html,encoding='utf8');sheet.save(O/'qa/eight-supplements-moving-review.jpg');(O/'qa/supplement-preview-inventory.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
print(json.dumps({'scenes':len(records),'sheet':str(O/'qa/eight-supplements-moving-review.jpg'),'finalLectureComplete':False}))
