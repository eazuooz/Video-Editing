"""Explicitly collect this revision's sources/records; no broad staging."""
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
slugs=json.loads((B/'authorization.json').read_text('utf8'))['slugs']
paths=[]
def add(p):
 if p.is_file():paths.append(p.relative_to(R).as_posix())
def tree(p):
 for f in p.rglob('*'):
  if '__pycache__' not in f.parts and f.suffix.lower() in ['.py','.cjs','.md','.json','.txt','.diff','.cs','.meta','.mat','.unity','.asset']:add(f)
tree(B)
common=R/'unity/VideoEditing/Assets/VideoScenes/design-25-30-unity-v2'
tree(common);add(common.with_suffix('.meta'))
for s in slugs:
 p=R/'projects'/s;tree(p/'production/unity-visual-v2')
 for f in ['project.json','rebuild.json','production/delivery-output.json']:add(p/f)
 scene=R/'unity/VideoEditing/Assets/VideoScenes'/s
 tree(scene/'unity-visual-v2');add(scene/'unity-visual-v2.meta');add(scene.with_suffix('.meta'))
for f in ['shared/publishing/video-production-control.json','shared/publishing/video-worklist.json','docs/VIDEO_WORKLIST.md']:add(R/f)
paths=sorted(set(paths));assert all('/production/local/' not in p for p in paths)
assert all(not any(x in p for x in ['.mp4','.wav','.mp3','.fbx','.FBX','.prefab']) for p in paths)
out=B/'commit-paths.json';paths=sorted(set(paths+[out.relative_to(R).as_posix()]))
out.write_text(json.dumps(paths,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'paths':len(paths),'list':out.relative_to(R).as_posix()}))
