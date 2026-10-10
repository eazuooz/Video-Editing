from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'shared/output/game-math-part2-teaching-revision/extra-source-candidates'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss','506','-i',str(ROOT/'shared/output/game-math-part2-full-series/sources/4Odvp_TIeQU.mp4'),'-t','16','-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(D/'T.mp4')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
(D/'t.html').write_text('''<!doctype html><meta charset="utf-8"><title>자전거 벡터 예시 비교</title><style>body{background:#222;color:white;font:20px sans-serif}video{width:960px;max-width:95vw}</style><h1>T: 506–522초 · 원본 게임 대사 자막 이후의 점프</h1><button onclick="document.getElementById('T').play()">T 재생</button><video id="T" controls muted src="T.mp4"></video>''',encoding='utf8')
print('T prepared; candidate playback pending')
