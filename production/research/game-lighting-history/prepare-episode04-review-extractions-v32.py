"""Prepare the next two sequential CPU review jobs without regenerating media."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[3]
D=R/'production/research/game-lighting-history'
src=(D/'extract-episode04-hair-encoded-v29.py').read_text('utf-8')
b=src.replace('hair','dlss').replace('Hair','Dlss').replace('v29','v31').replace('V29','V31')
b=b.replace('all34','all24').replace('len(metrics)==34','len(metrics)==24').replace('N==8577','N==6970')
b=b.replace('Read all34 cues and every cut/annotation board; then remaining38 paragraphs','Read24 DLSS cues, every cut and both actual controls before postprocess')
b=b.replace('for localSeconds in [0,.1,.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,(native[\'frames\']-1)/60]:',"for localSeconds in [0,.1]+[n/2 for n in range(1,27)]+[(native['frames']-1)/60]:")
dest=D/'extract-episode04-dlss-encoded-v31.py'
assert not dest.exists();compile(b,str(dest),'exec');dest.write_text(b,'utf-8')
b=(D/'extract-episode04-megalights-native-v25.py').read_text('utf-8')
b=b.replace('megalights','postprocess').replace('MegaLights','Postprocess').replace('v25','v32').replace('V25','V32')
a=b.index('sources = {');z=b.index('\nfor path,digest,crop,times',a)
source='production/research/game-lighting-history/local/epic-post-processing.mp4'
digest='d4c422af11f1242fb9d1ac8fd233ddd5638dbfc4be6a93417e50d826f92ea723'
b=b[:a]+f"sources = {{\n 'exposure': ({source!r}, {digest!r}, None, [1570,1572,1574,1576,1578,1580,1582,1584,1586,1588,1590,1592,1594,1596,1598,1600,1602,1604,1606,1608,1610,1612,1614,1616,1618]),\n 'focus-debug': ({source!r}, {digest!r}, None, [2330,2331,2332,2333,2334,2335,2336]),\n 'focus-normal': ({source!r}, {digest!r}, None, [2369,2370,2371,2372,2373,2374,2375,2376,2377,2378,2379,2380,2381]),\n}}"+b[z:]
b=b.replace('Read8 exact supplementary market49.8-55.79s samples; reject stationary34-49s as a long actual-action guide','Read exact exposure and depth-of-field windows; preserve source chronology and distinguish debug regions from normal blur')
dest=D/'extract-episode04-postprocess-native-v32.py'
assert not dest.exists();compile(b,str(dest),'exec');dest.write_text(b,'utf-8')
print('Prepared DLSS24-cue encoded review and45 native postprocess samples; execution pending.')
