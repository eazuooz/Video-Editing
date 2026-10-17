"""Inspect annotation geometry only; actual-caption/moving review stays pending."""
from pathlib import Path
import json,subprocess,importlib.util,copy
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent;L=R/'projects/making-game-sequels/production/local/reference-preserving-v2';O=L/'preflight'
spec=importlib.util.spec_from_file_location('footage_marks',V/'render-footage.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
sources={x['id']:x for x in json.loads((V/'source-selection.json').read_text(encoding='utf8'))['sources']}
marks=json.loads((V/'source-annotations.json').read_text(encoding='utf8'))['marks']
for i,m in enumerate(marks):
 t=(m['from']+m['to'])/2;c={'frames':60,'sourceStart':t,'marks':[m],'credit':'독립 게임 영상 · 설명용 표식','showGameTitle':False}
 ass=O/f'mark-{i:02}.ass';ass.write_text(mod.annotations(c),encoding='utf8');vf='scale=1600:900:flags=lanczos,pad=1920:1080:160:0:black,setsar=1,ass='+ass.relative_to(R).as_posix()
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(R/sources[m['source']]['file']),'-vf',vf,'-frames:v','1',str(O/f'mark-{i:02}.png')],cwd=R,check=True)
print('Five marked source frames generated; this does not certify moving final captions.')
