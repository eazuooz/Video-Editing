"""Prepare a local-only extraction of the changed native cut and cue229."""
from pathlib import Path
R=Path(__file__).resolve().parents[3]
s=R/'production/research/game-lighting-history/extract-episode04-hair-encoded-v29.py'
t=s.with_name('extract-episode04-hair-scoped-v30.py')
b=s.read_text('utf-8').replace('v29','v30').replace('V29','V30')
b=b.replace('for c in metrics:', "for c in [m for m in metrics if m['id']==229]:")
b=b.replace("for c in plan['cuts']:", "for c in [c for c in plan['cuts'] if c['kind']=='actual']:")
b=b.replace('One CPU2 extraction of all34 current chapter cue/cut/annotation samples.', 'One CPU2 local-only extraction of changed native annotation and cue229.')
b=b.replace('Read all34 cues and every cut/annotation board; then remaining38 paragraphs', 'Read changed native-cut and cue229 boards; retain prior rejection and sampled-review scope')
assert not t.exists()
compile(b,str(t),'exec')
t.write_text(b,'utf-8')
print(t.relative_to(R))
