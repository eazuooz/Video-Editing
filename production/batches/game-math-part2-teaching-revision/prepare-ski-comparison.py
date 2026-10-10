"""Unused native-speed ski excerpts, compared against crash-heavy I350–405."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'shared/output/game-math-part2-teaching-revision/extra-source-candidates'
cuts=[('4Odvp_TIeQU',147,159),('4Odvp_TIeQU',169.25,187),('_dw9jjRpanA',372,394)]
parts=[]
for n,(source,a,b) in enumerate(cuts):
 file=ROOT/(('shared/output/game-math-part2-teaching-revision/sources/' if source=='_dw9jjRpanA' else 'shared/output/game-math-part2-full-series/sources/')+source+'.mp4')
 p=D/f'AG-ski-{n}.mp4';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(a),'-i',str(file),'-t',str(b-a),'-vf','scale=960:540,fps=60','-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(p)],check=True,creationflags=subprocess.CREATE_NO_WINDOW);parts.append(p)
listing=D/'ag-ski.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts)+'\n',encoding='utf8')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy','-an',str(D/'AG-ski.mp4')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
(D/'ag-ski.html').write_text('''<!doctype html><meta charset="utf-8"><title>점프와 착지의 비교 발췌</title><style>body{background:#222;color:white;font:20px sans-serif}video{width:960px;max-width:95vw}</style><h1>AG: 충돌 화면을 제외한 서로 다른 스키 발췌</h1><p>원본147–159 →169.25–187 → 별도 기록372–394. 장면 전환을 한 순간의 전후로 해석하지 않는다.</p><button onclick="document.getElementById('AG').play()">AG 재생</button><video id="AG" controls muted src="AG-ski.mp4"></video>''',encoding='utf8')
print(json.dumps({'candidate':'AG','seconds':sum(b-a for _,a,b in cuts),'normalPlaybackAndSelectionPending':True}))
