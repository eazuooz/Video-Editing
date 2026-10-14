"""Adapt the already inspected exclusive worker for actual limited repairs only."""
from pathlib import Path
import ast
root=Path(__file__).resolve().parents[3]
old=root/'production/research/game-lighting-history/render-part1-guided-actions-v169.py'
target=root/'production/research/game-lighting-history/render-part1-scoped-repair-v176.py'
if target.exists():raise RuntimeError('Preserve prepared worker')
t=old.read_text('utf-8')
t=t.replace('source-reviewed37 additions','source-reviewed limited repairs')
t=t.replace('part1-guided-actions-tts-request-v169.json','part1-scoped-repair-tts-request-v176.json').replace('part1-guided-actions-tts-execution-v169.json','part1-scoped-repair-tts-execution-v176.json')
t=t.replace("if len(request['scenes'])!=37:raise RuntimeError('Only prepared37 independent additions are authorized')","if not 1<=len(request['scenes'])<=37 or [s['id'] for s in request['scenes']]!=request['repairIds']:raise RuntimeError('Only exact actual scoped repair IDs allowed')")
t=t.replace("'episode04Part1GuidedTtsV169'","'episode04Part1ScopedTtsV176'").replace("'.tts169.tmp'","'.tts176.tmp'")
t=t.replace("status='part1-new-guides-synthesizing'","status='part1-scoped-repairs-synthesizing'")
t=t.replace("status='part1-guides-generated-awaiting-ASR-and-restoration'","status='part1-scoped-repairs-generated-awaiting-selection-ASR-and-restoration'")
ast.parse(t);target.write_text(t,'utf-8')
print('Scoped worker prepared only; no model or GPU job started')
