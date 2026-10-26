"""Derive existing measured QA helpers for only the current six episodes."""
from pathlib import Path
import ast
R=Path(__file__).resolve().parents[3]
BASE=R/'projects/similar-game-design/production/reference-preserving-v2'
SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time']
for slug in SLUGS:
 for name in ['review_audio.py','extract-final-review.py']:
  text=(BASE/name).read_text('utf-8-sig')
  text=text.replace('NARRATION = ROOT / "shared/output/narration" / PROJECT.name / REVISION','NARRATION = LOCAL / "voice"')
  text=text.replace('edit-plan-final.json','edit-plan.json')
  ast.parse(text);dest=R/'projects'/slug/'production/batch-v1'/name
  if dest.exists():raise ValueError('Preserve existing QA helper '+str(dest))
  dest.write_text(text,'utf8')
print('Added12 measured QA helpers; no media jobs started')
