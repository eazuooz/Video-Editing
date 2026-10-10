from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision';D=O/'extra-source-candidates'
source=ROOT/'shared/output/game-math-part2-full-series/sources/4Odvp_TIeQU.mp4'
target=D/'Q.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss','460','-i',str(source),'-t','40','-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(target)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
sheet=Image.new('RGB',(1600,2*245),'white');draw=ImageDraw.Draw(sheet)
for i,t in enumerate([0,5,10,15,20,25,30,39.8]):
    f=D/f'Q-{i}.png';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(t),'-i',str(target),'-frames:v','1','-vf','scale=400:225',str(f)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    x=i%4*400;y=i//4*245;sheet.paste(Image.open(f),(x,y));draw.text((x+5,y+228),f'Q source {460+t:.2f}s',fill='black')
sheet.save(D/'Q-comparison.jpg')
(D/'q.html').write_text('''<!doctype html><meta charset="utf-8"><title>별도 비행 구간 비교</title><style>body{background:#222;color:white;font:20px sans-serif}video{width:960px;max-width:95vw}</style><h1>Q: 원래 기록의 미사용 구간460–500초</h1><button onclick="document.getElementById('Q').play()">Q 재생</button><video id="Q" controls muted src="Q.mp4"></video>''',encoding='utf8')
print('Q prepared; playback and fit not yet approved')
