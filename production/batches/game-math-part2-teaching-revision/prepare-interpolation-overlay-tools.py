"""Scope the proven editable overlay renderer to this revision only."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
source=(B/'create-game-overlay.py').read_text(encoding='utf8')
source=source.replace("quaternion-annotation-tracks.json","interpolation-annotation-tracks.json").replace("quaternion-on-footage-math.json","interpolation-on-footage-math.json")
source=source.replace("def source_at(slot,elapsed):\n offset=0", "def source_at(slot,elapsed):\n if slot.get('preservedOriginal'):return slot['baselineClip'],elapsed\n offset=0")
source=source.replace("source_files={x.get('sourceFile',slot['cut']['sourceFile']) for x in slot['cut']['segments']}","source_files=({slot['baselineClip']} if slot.get('preservedOriginal') else {x.get('sourceFile',slot['cut']['sourceFile']) for x in slot['cut']['segments']})")
source=source.replace("'날개 방향','#ef5350'","spec.get('redLabel','보이는 몸체 가로방향'),'#ef5350'")
source=source.replace("'몸체 방향','#ef5350'","spec.get('redLabel','몸체 방향'),'#ef5350'")
source=source.replace("'sourceMap':'native1x real-time source segments'","'sourceMap':('preserved native60fps baseline clip local time' if slot.get('preservedOriginal') else 'native1x real-time source segments')")
target=B/'create-interpolation-overlay.py'
target.write_text(source,encoding='utf8')
print('Created independently scoped editable overlay tools; pixel review remains pending.')
