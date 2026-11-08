from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'projects/ai-2d-game-assets'
src=P/'assets/local/room-v2/map-open-eight-source.png';sheet=Image.open(src).convert('RGBA');base=P/'production/local/room-v2/map-open-eight';report=json.loads((base/'map-open-slice-sheet.json').read_text());s=report['factor'];out=ROOT/'sites/yamyam-cartographers-room/dist/assets/motions';records=[]
for i in range(8):
 cell=sheet.crop((i%4*384,i//4*512,(i%4+1)*384,(i//4+1)*512));bb=cell.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();dx=round(((bb[0]+bb[2])/2-192)*s);dy=round((bb[3]-480)*s)
 frame=Image.new('RGBA',(128,176));frame.alpha_composite(Image.open(base/f'map-open-{i:02}.png').convert('RGBA'),(dx,dy));dest=out/f'map-open-{i:02}.png';frame.save(dest);records.append({'frame':i,'translation':[dx,dy],'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
manifest=out.parent/'motions.json';data=json.loads(manifest.read_text(encoding='utf8'));data['clips']['map-open']={'frames':[f'motions/map-open-{i:02}.png' for i in range(8)],'canvas':[128,176],'anchor':[64,166],'gameScale':.75,'fps':5.333333,'loop':False};manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
(P/'production/room-v2/map-open-execution.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'spriteGenFactor':s,'frames':records},indent=2),encoding='utf8');print('map-open replaced; other clips preserved')
