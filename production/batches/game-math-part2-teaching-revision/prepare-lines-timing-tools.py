"""Create scoped timing/planning tools from the already reviewed episode method.

No baseline/voice changes. Source-group boundaries announce each actual cut.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
src=(B/'prepare-interpolation-timing.py').read_text(encoding='utf8')
old="for slug,name in [('game-math-interpolation-teaching-additions-v2','interpolation-addition-tts-map.json'),('game-math-interpolation-worked-checks-v3','interpolation-worked-tts-map-v3.json'),('game-math-interpolation-numeric-retakes-v4','interpolation-numeric-tts-map-v4.json')]:"
assert old in src
src=src.replace(old,"for slug,name in [('game-math-lines-bounds-teaching-additions-v2','lines-addition-tts-map.json')]:")
src=src.replace('game-math-interpolation-teaching-additions-v2','game-math-lines-bounds-teaching-additions-v2').replace('game-math-part2-teaching-revision/interpolation','game-math-part2-teaching-revision/lines').replace('interpolation-alignment-progress','lines-alignment-progress')
(B/'prepare-lines-timing.py').write_text(src,encoding='utf8')
src=(B/'plan-interpolation-episodes.py').read_text(encoding='utf8')
src=src.replace('game-math-part2-teaching-revision/interpolation','game-math-part2-teaching-revision/lines').replace('interpolation-episode-flow-audit','lines-episode-flow-audit').replace('game-math-rotation-interpolation','game-math-lines-bounds').replace('interpolation-measured-episode-plan','lines-measured-episode-plan')
(B/'plan-lines-episodes.py').write_text(src,encoding='utf8')
groups={'LG01':[0,1],'LG02':[0,3],'LG03':[0,2],'LG06':[0,1,2],'LG07':[0,1,2]}
sources=read(B/'lines-game-insertions.json')
for s in sources['scenes']:
 if s['id'] in groups:s['sourceGroupStartsAtLines']=groups[s['id']]
write(B/'lines-game-insertions.json',sources)
for slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']:
 p=ROOT/'projects'/slug/'production/lesson.json';lesson=read(p)
 for s in lesson['scenes']:
  if s['id'] in groups:s['sourceGroupStartsAtLines']=groups[s['id']]
 write(p,lesson)
print('Lines timing tools prepared; original dictionaries and frozen TTS manifest/scripts retained.')
