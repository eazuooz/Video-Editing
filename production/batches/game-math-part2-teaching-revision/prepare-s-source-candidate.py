from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'shared/output/game-math-part2-teaching-revision/extra-source-candidates'
source=ROOT/'shared/output/game-math-part2-teaching-revision/sources/_dw9jjRpanA.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss','121','-i',str(source),'-t','9','-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(D/'S.mp4')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
(D/'s.html').write_text('''<!doctype html><meta charset="utf-8"><title>비행 다음 구간 검토</title><style>body{background:#222;color:white;font:20px sans-serif}video{width:960px;max-width:95vw}</style><h1>S: 121–130초 · 장비 변화와 착지 여부</h1><button onclick="document.getElementById('S').play()">S 재생</button><video id="S" controls muted src="S.mp4"></video>''',encoding='utf8')
print('S prepared; full playback review pending')
