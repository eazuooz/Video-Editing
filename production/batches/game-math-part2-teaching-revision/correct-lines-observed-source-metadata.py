"""Correct source UI/visibility notes without altering any supplied narration."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
files=[B/'lines-game-insertions.json',ROOT/'projects/game-math-lines-circles-v2/production/lesson.json',ROOT/'projects/game-math-bounds-transform-v2/production/lesson.json']
for path in files:
 data=json.loads(path.read_text(encoding='utf8'))
 for row in data['scenes']:
  ident=row['id']
  if ident=='LG01':
   row['selection']['UI']='Portal reticle, receiver indicators and retained source watermark; no health/ammunition/score HUD. Keep geometry labels clear of visible indicators and fixed bottom captions.'
  if ident=='LG05':
   row['selection']['UI']='Portal reticle and funnel/cube/receiver indicators; no health/ammunition/score HUD. Preserve visible platform edges, retained source identification and fixed bottom captions.'
  if ident=='LG06':
   row['selection']['visibleBeforeActionAfter']='665–675 gray body turns back to front;678–698 moving targets during attacks;731–739 nearby blue body crosses. In739–740 it is no longer visible: hide body contours and retain only the observed background.'
   row['selection']['occlusion']='Close crop669 and explosion684–687 hide parts. Reset at each source cut and hide unobservable extrema; the final739–740 second shows background after the body leaves.'
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Observed UI and final body visibility corrected; narration/formulas/cuts untouched.')
