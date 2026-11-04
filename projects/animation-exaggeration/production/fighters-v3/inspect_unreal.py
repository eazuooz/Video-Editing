"""Run inside the isolated Unreal Python commandlet; read asset data only."""
from pathlib import Path
import json, traceback
import unreal as u

H=Path(__file__).resolve().parent
OUT=H.parent/'local/fighters-v3/unreal/asset-inspection.json'

def main():
    registry=u.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    assets=registry.get_assets_by_path('/Game/Characters/UEFN_Mannequin',recursive=True)
    rows=[{'path':str(a.package_name),'class':str(a.asset_class_path.asset_name)} for a in assets]
    mesh=u.load_asset('/Game/Characters/UEFN_Mannequin/Meshes/SKM_UEFN_Mannequin')
    assert mesh is not None
    animations=[x['path'] for x in rows if x['class']=='AnimSequence']
    idle=[x for x in animations if 'Idle' in x or 'Stand' in x]
    candidate=next((x for x in idle if x.endswith('/M_Neutral_Stand_Idle_Loop')),idle[0] if idle else animations[0])
    clip=u.load_asset(candidate)
    pose=u.AnimPoseExtensions.get_anim_pose_at_time(clip,0.0,u.AnimPoseEvaluationOptions())
    names=u.AnimPoseExtensions.get_bone_names(pose)
    component=u.SkeletalMeshComponent()
    component.set_skeletal_mesh(mesh)
    bones=[]
    for name in names:
        local=u.AnimPoseExtensions.get_ref_bone_pose(pose,name,u.AnimPoseSpaces.LOCAL)
        world=u.AnimPoseExtensions.get_ref_bone_pose(pose,name,u.AnimPoseSpaces.WORLD)
        def val(t):
            p=t.translation;q=t.rotation;s=t.scale3d
            return {'p':[p.x,p.y,p.z],'q':[q.x,q.y,q.z,q.w],'s':[s.x,s.y,s.z]}
        bones.append({'name':str(name),'parent':str(component.get_parent_bone(name)),
            'local':val(local),'world':val(world),
            'baseLocal':val(u.AnimPoseExtensions.get_bone_pose(pose,name,u.AnimPoseSpaces.LOCAL)),
            'baseWorld':val(u.AnimPoseExtensions.get_bone_pose(pose,name,u.AnimPoseSpaces.WORLD))})
    result={'engine':u.SystemLibrary.get_engine_version(),'mesh':mesh.get_path_name(),
        'skeleton':mesh.get_editor_property('skeleton').get_path_name(),'animationCount':len(animations),
        'idleCandidates':idle,'sampleAnimation':candidate,'assets':rows,'referenceBones':bones,
        'clipMethods':[n for n in dir(clip) if any(k in n for k in ('bone','frame','model','controller','skeleton'))],
        'controllerMethods':[n for n in dir(u.AnimDataController) if any(k in n for k in ('bone','frame','model','bracket'))],
        'meshMethods':[n for n in dir(mesh) if any(k in n for k in ('bone','skeleton','reference'))],
        'sampleAnimationSeconds':float(clip.sequence_length),'sourceAssetsModified':False}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    u.log('A02_INSPECT_OK '+str(OUT))

try:main()
except Exception:
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.with_suffix('.error.txt').write_text(traceback.format_exc(),encoding='utf-8')
    raise
