"""Prepare a bounded native review outside the already-used overview interval."""
from pathlib import Path
R=Path(__file__).resolve().parents[3]
src=R/'production/research/game-lighting-history/extract-episode04-postprocess-native-v32.py'
s=src.read_text('utf-8').replace('postprocess','renderdoc').replace('Postprocess','Renderdoc').replace('v32','v35').replace('V32','V35')
start=s.index('sources = {'); end=s.index('\nfor path,digest,crop,times',start)
s=s[:start]+'''sources = {
 'mesh': ('production/research/game-lighting-history/local/episode04-native-v1/own-renderdoc-capture.mp4','4dd745b1f29bee29b351d9e1e605b9092215a1b4ffeeaecaa43206c4735c02c8',(244,123,1570,923),[64,66,68,70,72,74]),
 'shader': ('production/research/game-lighting-history/local/episode04-native-v1/own-renderdoc-capture.mp4','4dd745b1f29bee29b351d9e1e605b9092215a1b4ffeeaecaa43206c4735c02c8',(244,123,1570,923),[100,102,104,106,108,110,112,114,116,118,120,122,124]),
}
'''+s[end:]
s=s.replace('Read exact exposure and depth-of-field windows; preserve source chronology and distinguish debug regions from normal blur','Read exact mesh/input/return locations; avoid repeating overview125–132.5s and distinguish code inspection from completed debug return.')
dest=src.with_name('extract-episode04-renderdoc-native-v35.py');assert not dest.exists();compile(s,str(dest),'exec');dest.write_text(s,'utf-8')
print(str(dest.relative_to(R)))
