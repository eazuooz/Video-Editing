"""Two fresh intervals for a causal first-episode closing observation."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision';D=O/'extra-source-candidates'
rows=[('X','shared/output/game-math-part2-full-series/sources/4Odvp_TIeQU.mp4',539,552,'입력 복원에서 중간 자세로')]
for ident,source,a,b,_ in rows:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-ss',str(a),'-i',str(ROOT/source),'-t',str(b-a),'-vf','scale=960:540','-an','-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(D/f'{ident}.mp4')],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 title='회전값 만들기·되돌리기에서 합성 질문으로'
 (D/f'{ident.lower()}.html').write_text(f'''<!doctype html><meta charset="utf-8"><title>마무리 사례 비교</title><style>body{{background:#222;color:white;font:20px sans-serif}}video{{width:960px;max-width:95vw}}</style><h1>{ident}: {a}–{b}초 · {title}</h1><button onclick="document.getElementById('{ident}').play()">{ident} 재생</button><video id="{ident}" controls muted src="{ident}.mp4"></video>''',encoding='utf8')
print(json.dumps({'candidates':2,'played':False,'finalSelected':False}))
