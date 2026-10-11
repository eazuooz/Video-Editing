"""Report only scene renders invalidated by measured addition timing."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
pending={}
for ep in ['centers','partition']:
 for slot in read(ROOT/f'projects/game-math-polygon-{ep}-v2/production/timeline.json')['scenes']:
  if slot['preservedOriginal'] or slot['classification']!='explanation':continue
  kind=slot.get('sceneSourceModule','polygons_additions');path=O/f'caption-safe-{kind}-receipts.json';receipt=read(path).get(slot['id'],{}) if path.exists() else {}
  if receipt.get('voiceSha256')!=slot['voiceSha256'] or receipt.get('lineStarts')!=slot['lineStarts'] or not 0<=slot['frames']-receipt.get('frames',-99)<=3:
   pending.setdefault(kind,[]).append(slot['id'])
print(json.dumps(pending))
