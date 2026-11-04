from pathlib import Path
import shutil,json
import audio_pipeline as ap
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3'
source=L/'unreal-worker/Content/YamyamA02/fighters_v3_final';dest=R/'GameAnimationSample/Content/YamyamA02/fighters_v3_final'
assert dest.resolve().is_relative_to((R/'GameAnimationSample/Content/YamyamA02').resolve())
records=[]
for f in source.rglob('*'):
 if not f.is_file():continue
 assert f.suffix in {'.umap','.uasset'}
 target=dest/f.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert ap.sha(target)==ap.sha(f),'Preserve a separately modified editor asset'
 else:shutil.copy2(f,target)
 records.append(ap.artifact(target))
ap.save(H/'editable-unreal-scenes.json',{'engine':'Unreal Engine5.8.4','project':'GameAnimationSample/GameAnimationSample.uproject','ownedContentRoot':'/Game/YamyamA02/fighters_v3_final','sourceAssetsModified':False,'vendorDependency':'User-installed Epic Game Animation Sample; original UEFN mannequin mesh/skeleton/idle remain in place. Only owned derived levels, sequences, animations, materials and MRQ configs copied.','files':records,'generator':ap.artifact(H/'build_unreal_stage.py'),'poseGenerator':ap.artifact(H/'prepare_poses.py'),'requiredNativeInspectionScript':ap.artifact(H/'inspect_unreal.py')})
print('Saved editable owned Unreal assets:',len(records))
