"""One owned GPU batch; restore complete lines with the approved voice."""
from pathlib import Path
import sys,subprocess,json
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-mesh-uv';device=sys.argv[sys.argv.index('--device')+1]
record=json.loads((R/f'projects/{slug}/production/narration-number-correction.json').read_text(encoding='utf8'))
assert record['retakeScenes']==['04','13']
selected=sys.argv[sys.argv.index('--scenes')+1].split(',') if '--scenes' in sys.argv else record['retakeScenes']
assert selected and set(selected)<=set(record['retakeScenes'])
for sid in selected:
 subprocess.run([sys.executable,'-X','utf8',str(B/'repair-scene-by-lines.py'),slug,sid,'--device',device,'--defer-assembly'],cwd=R,check=True)
print('Required full-line takes generated; current ASR,meaning,numbers and final assembly remain pending.',flush=True)
