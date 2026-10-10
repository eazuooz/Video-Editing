"""Prepare an explicit own-source path inventory after actual private delivery.

Does not stage, commit, push, change any index or add a raster automatically.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
receipt=read(BASE.parent/'publishing/youtube-upload-v1.json')
assert receipt.get('savedPrivateVerified') and receipt.get('uploadedCcOffPixelsVerified') and receipt.get('actualVideoId'),'Finish actual reviewed private delivery first'
assert read(BASE/'final-v1/final-pixel-direct-review-v1.json')['qaApproved']
extensions={'.md','.json','.cjs','.py','.ps1','.ts','.tsx','.meta','.txt','.srt','.ass','.csv','.html'}
roots=['projects/character-parameters','motion-canvas/src/projects/character-parameters','manim/projects/character-parameters','production/batches/sakurai-planning-game-design/proof-character-parameters']
excludedDirs={'__pycache__','raw','assets','frames','boards','delivery-history','media-archives'}
paths=[];excluded=[]
for directory in roots:
 base=ROOT/directory
 if not base.exists():continue
 for p in base.rglob('*'):
  if not p.is_file()or p.is_symlink():continue
  relative=p.relative_to(ROOT).as_posix();parts=p.relative_to(base).parts
  reject=any(x in excludedDirs or x.startswith('delivery-stage-')for x in parts)or p.name.endswith(('.ax.txt','.info.json'))or 'source-zwiS1L6QVY0-ja-research' in p.name
  if reject or p.suffix.lower()not in extensions:excluded.append(relative);continue
  paths.append(relative)
paths.extend(['motion-canvas/vite.character-parameters.black-preflight-v1.config.ts','motion-canvas/tsconfig.character-parameters.json','production/batches/sakurai-planning-game-design/preflight/character-parameters.json'])
paths=[x for x in paths if (ROOT/x).is_file()]
followup=ROOT/'projects/picking-sides/publishing/postpublication-20261010'
paths.extend(p.relative_to(ROOT).as_posix()for p in followup.iterdir()if p.suffix in {'.py','.json'} and not p.name.endswith('.ax.txt'))
paths=sorted(set(paths));dest=BASE.parent/'publishing/git-delivery-paths-v1.json'
assert not dest.exists(),'Read actual prepared selection rather than regenerate it'
shared=['.gitignore','shared/git-essential-images.json','motion-canvas/projects.json','projects/rebuild-index.json','production/batches/sakurai-planning-game-design/queue.json','production/batches/sakurai-planning-game-design/README.md']
record=dict(schemaVersion=1,slug='character-parameters',actualVideoId=receipt['actualVideoId'],createdAt=datetime.now(timezone.utc).isoformat(),
 sourcePaths=paths,sourceSha256={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest()for x in paths},
 sharedPathsRequireOwnOnlyHeadMerge=shared,excludedLocalPaths=sorted(excluded),rasterPaths=[],rasterSelectionMustBeExplicitIndividuallyReviewed=True,
 externalIndexMustRemainByteIdentical=True,staged=False,committed=False,pushed=False)
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(explicitSourcePaths=len(paths),rasterAutomaticallySelected=0,staged=False,committed=False)))
