from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
OUT=ROOT/'shared/output'/SLUG;P=ROOT/'motion-canvas/src/projects'/SLUG
data={'unity':{},'footage':{}}
for d in (OUT/'unity-production').iterdir():
 if not d.is_dir():continue
 movie=d/'unity.mp4';capture=d/('render-capture.json' if movie.exists() else 'preflight-capture.json')
 if not capture.exists():continue
 c=json.loads(capture.read_text());posters=sorted(d.glob('frame-*.png'))
 data['unity'][d.name]={'frames':c['frames'],'video':movie.relative_to(ROOT).as_posix() if movie.exists() else None,'capture':capture.relative_to(ROOT).as_posix(),'posters':[{'frame':int(p.stem.split('-')[-1]),'path':p.relative_to(ROOT).as_posix()} for p in posters]}
selection=OUT/'selected-footage/selection.json'
if selection.exists():
 records=json.loads(selection.read_text(encoding='utf-8'))
 data['footage']={'16':records[:2],'22':records[2:]}
(P/'media.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
from revision_paths import workroot
actual=workroot(ROOT)/'actual-footage/selection.json'
if actual.exists():(P/'actual-footage.json').write_text(actual.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps({'unity':list(data['unity']),'footage':list(data['footage'])}))
