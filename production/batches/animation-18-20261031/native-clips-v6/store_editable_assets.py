"""Preserve only the five adopted native capture setups in the real project."""
from pathlib import Path
import shutil
from prepare import HERE,ROOT,WORK,read,save
from finish_episode import sha

def main():
    source=WORK/'unreal-worker/Content'
    destination=ROOT/'GameAnimationSample/Content/YamyamNativeClipsV6'
    rows=[]
    for key in ('AS_ComboHands','am_Ready_Fight_01_Knockdown_A','anim_GrabValve_R','anim_OpeningValve_R','A_Guard_idle'):
        build=read(WORK/(key+'-build.json'))
        for role in ('level','sequence','config'):
            package=build[role].split('.')[0]
            assert package.startswith('/Game/YamyamNativeClipsV6/')
            relative=Path(package.removeprefix('/Game/')).with_suffix('.umap' if role=='level' else '.uasset')
            original=source/relative;target=ROOT/'GameAnimationSample/Content'/relative
            assert target.resolve().is_relative_to(destination.resolve()) and original.is_file()
            if target.exists():assert sha(target)==sha(original),'Preserve an unrecognized changed setup: '+str(target)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(original,target)
            rows.append({'clip':key,'role':role,'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'bytes':target.stat().st_size})
    save(HERE/'editable-assets.json',{'project':'GameAnimationSample/GameAnimationSample.uproject','engine':'5.8.4',
         'sourceAnimationsBoundDirectly':True,'vendorContentModified':False,'files':rows})
    print(len(rows),'editable capture assets saved in the actual project.')

if __name__=='__main__':main()
