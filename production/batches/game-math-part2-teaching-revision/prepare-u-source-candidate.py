from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'shared/output/game-math-part2-teaching-revision/extra-source-candidates'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss','610','-i',str(ROOT/'shared/output/game-math-part2-full-series/sources/4Odvp_TIeQU.mp4'),'-t','32','-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(D/'U.mp4')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
(D/'u.html').write_text('''<!doctype html><meta charset="utf-8"><title>합성의 질문을 만드는 주행</title><style>body{background:#222;color:white;font:20px sans-serif}video{width:960px;max-width:95vw}</style><h1>U: 610–642초 · 기울기와 진행 방향을 함께 읽기</h1><button onclick="document.getElementById('U').play()">U 재생</button><video id="U" controls muted src="U.mp4"></video>''',encoding='utf8')
print('U prepared; normal-speed playback pending')
