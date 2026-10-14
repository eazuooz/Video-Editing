"""Prepare the single CPU extraction; no render or media mutation here."""
from pathlib import Path
R=Path(__file__).resolve().parents[3]
s=R/'production/research/game-lighting-history/extract-episode04-megalights-encoded-v28.py'
t=s.with_name('extract-episode04-hair-encoded-v29.py')
b=s.read_text('utf-8').replace('megalights','hair').replace('MegaLights','Hair').replace('v28','v29').replace('V28','V29')
b=b.replace('all22','all34').replace('remaining48 paragraphs','remaining38 paragraphs')
b=b.replace('N==6456','N==8577').replace('len(metrics)==22','len(metrics)==34')
b=b.replace('0,.1,.5,1,1.2,1.5,2,2.5,3,3.5,4,4.5,3.983333333,4,4.016666667,4.49,4.5,4.516666667,5,5.5', '0,.1,.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9')
assert not t.exists()
compile(b,str(t),'exec')
t.write_text(b,'utf-8')
print(t.relative_to(R))
