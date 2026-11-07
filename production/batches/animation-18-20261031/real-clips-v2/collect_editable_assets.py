"""List only active study levels, sequences, settings and referenced animation copies."""
from pathlib import Path
import json,unreal as u
H=Path(__file__).resolve().parent;L=H.parent/'local/real-clips-v2';root='/Game/YamyamRealClipsV2/'
items=set();studies=[]
for p in sorted((L/'studies').glob('A*.json')):
    key=p.stem
    if key in ('A04-jab','A11-upper'):continue
    d=json.loads(p.read_text('utf-8'));ep=d['episode'];base=root+ep+'/'
    seq=u.load_asset(base+'Sequences/'+key)
    if not seq:continue
    packages=[base+'Levels/'+key,base+'Sequences/'+key,base+'Capture/'+key]
    for binding in seq.get_bindings():
        for track in binding.get_tracks():
            if isinstance(track,u.MovieSceneSkeletalAnimationTrack):
                for section in track.get_sections():
                    asset=section.params.animation
                    if asset and asset.get_path_name().startswith(root):packages.append(asset.get_path_name().split('.')[0])
    items.update(packages);studies.append(dict(key=key,packages=packages))
(L/'active-native-packages.json').write_text(json.dumps(dict(packages=sorted(items),studies=studies),indent=2),'utf-8')
