"""Copy the exact owned namespace into the user's project, never vendor content."""
from pathlib import Path
import json,shutil,hashlib
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=B/'local/real-clips-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
source=L/'unreal-worker/Content';dest=R/'GameAnimationSample/Content/YamyamRealClipsV2';files=[]
data=read(L/'active-native-packages.json')
previous=read(H/'editable-assets.json') if (H/'editable-assets.json').exists() else {'files':[]}
known={f['path']:f['sha256'] for f in previous['files']}
for package in data['packages']:
    assert package.startswith('/Game/YamyamRealClipsV2/')
    relative=Path(package.removeprefix('/Game/'));suffix='.umap' if '/Levels/' in package else '.uasset'
    f=source/relative.with_suffix(suffix);target=R/'GameAnimationSample/Content'/relative.with_suffix(suffix)
    assert f.is_file() and target.resolve().is_relative_to(dest.resolve())
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and sha(target)!=sha(f):
        assert known.get(target.relative_to(R).as_posix())==sha(target),'Refuse to replace an unrecognized editable asset: '+str(target)
        backup=L/'native-before-final-correction'/target.relative_to(dest);backup.parent.mkdir(parents=True,exist_ok=True)
        if not backup.exists():shutil.copy2(target,backup)
        shutil.copy2(f,target)
    else:shutil.copy2(f,target)
    files.append(dict(path=target.relative_to(R).as_posix(),sha256=sha(target),bytes=target.stat().st_size))
record=dict(engine='5.8',project='GameAnimationSample/GameAnimationSample.uproject',contentRoot='/Game/YamyamRealClipsV2',vendorAssetsModified=False,studies=data['studies'],files=files)
(H/'editable-assets.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Saved editable assets:',len(files),flush=True)
