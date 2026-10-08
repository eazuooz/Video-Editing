"""Derive a bounded, local-only pixel check from the established extractor."""
from pathlib import Path
root=Path(__file__).resolve().parents[3]
base=Path(__file__).resolve().parent
p=base/'extract-action-repaired-pixels-v2.py'
assert not p.exists(), 'Preserve existing extraction code and state.'
t=(base/'extract-selected-candidate-pixels-v1.py').read_text('utf-8-sig')
t=t.replace('selected-pixels-v1','action-repaired-pixels-v2').replace('selected-pixels-execution-v1','action-repaired-pixels-execution-v2').replace('selected-inputs-execution-v1','selected-inputs-execution-v2')
t=t.replace("plan=read(planPath);cap=read(capPath);video=ROOT/build['captionedSilentVideo'];assert sha(video)==build['captionedSilentSha256']", "plan=read(planPath);cap=read(capPath);video=ROOT/build['captionedSilentVideo'];assert sha(video)==build['captionedSilentSha256']\nchanged=[c for c in plan['cuts'] if c.get('repairNativeOnly')]\nassert len(changed)==10\nspans=[(c['outputStartFrame']-120,c['outputStartFrame']-120+c['frames']) for c in changed]\nwindows=[(max(0,a-120),min(35321,b+120)) for a,b in spans]\ndef in_window(n):return any(a<=n<b for a,b in windows)")
t=t.replace('if 0<=n<35321:points.setdefault(n,[]).append(why)', 'if 0<=n<35321 and in_window(n):points.setdefault(n,[]).append(why)')
t=t.replace("for c in plan['cuts']:\n start=", "for c in plan['cuts']:\n start=")
t=t.replace("add(start,'cut-first');add(end-1,'cut-last')", "add(start,'cut-first');add(end-1,'cut-last');add(start-1,'before-cut');add(end,'after-cut')")
t=t.replace("for n in range(start,end,30):add(n,'action-every-half-second')", "for n in range(start,end,15):add(n,'action-every-quarter-second')")
t=t.replace('totalCuts=136', 'totalCuts=139,changedCuts=10,repairWindows=windows,reviewScope="Five changed action/caption regions with two-second adjacent context; baseline355boards retained; final full-pair pixels pending"')
t=t.replace("nextAction='Read every local candidate board in chronological order, compare64whole paragraphs/action clauses and changed crops, keep actual defects, then adopt approved inputs only. Final mix/current mixed ASR/final pair/QA/collection/private/Git pending.'", "nextAction='Read every focused repair board and affected full action/caption clause. Preserve baseline355board review and all five historical defects. Adopt current inputs only after zero unresolved defects; final mix/current mixed ASR/final full-pair pixels/QA/collection/private/Git pending.'")
t=t.replace('selectedPixelExecution=rel(STATE)', 'actionRepairedPixelExecution=rel(STATE)')
p.write_text(t,'utf-8')
print('Prepared focused repair extractor; no media job or approval started.')
