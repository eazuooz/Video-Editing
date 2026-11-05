"""Store editable UE stages without replacing an existing asset of different contents."""
from pathlib import Path
import json, shutil,hashlib
H=Path(__file__).resolve().parent; R=H.parents[4]
src=H.parents[1]/'local/fighters-v4-kula-lili/unreal-worker/Content/YamyamA02/fighters_v4_motion18'
dest=R/'GameAnimationSample/Content/YamyamA02/fighters_v4_motion18'
def sha(f):
    with f.open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
files=[]
for f in sorted(src.rglob('*')):
    if not f.is_file():continue
    assert f.suffix in {'.umap','.uasset'}
    target=dest/f.relative_to(src);target.parent.mkdir(parents=True,exist_ok=True)
    assert target.resolve().is_relative_to(dest.resolve())
    if target.exists():assert sha(f)==sha(target)
    else:shutil.copy2(f,target)
    files.append({'path':target.relative_to(R).as_posix(),'sha256':sha(target)})
assert sum(i['path'].endswith('.umap') for i in files)==6
(H/'editable-stages.json').write_text(json.dumps({'engine':'5.8','project':'GameAnimationSample/GameAnimationSample.uproject','contentRoot':'/Game/YamyamA02/fighters_v4_motion18','sourceMesh':'SKM_UEFN_Mannequin','cameraOrthoWidthCm':500,'characterScale':[1,1,1],'files':files},indent=2)+'\n',encoding='utf-8')
print('Editable Unreal assets:',len(files))
