"""Export genuine clip poses for controlled, reversible timing/amplitude studies."""
from pathlib import Path
import gzip, json, math, traceback
import unreal as u

H=Path(__file__).resolve().parent
L=H.parent/'local/real-clips-v2'
assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()==(L/'unreal-worker').resolve()
OUT=L/'source-motion';OUT.mkdir(exist_ok=True)
request=json.loads((L/'motion-export-request.json').read_text('utf-8'))

def transform(t):
    p=t.translation;q=t.rotation;s=t.scale3d
    return dict(p=[p.x,p.y,p.z],q=[q.x,q.y,q.z,q.w],s=[s.x,s.y,s.z])

def export(row):
    target=OUT/(row['id']+'.json.gz')
    if target.exists():return
    clip=u.load_asset(row['clip']);mesh=u.load_asset(row['mesh'])
    assert isinstance(clip,u.AnimSequence) and isinstance(mesh,u.SkeletalMesh)
    assert clip.get_editor_property('skeleton')==mesh.get_editor_property('skeleton')
    opt=u.AnimPoseEvaluationOptions()
    base=u.AnimPoseExtensions.get_anim_pose_at_time(clip,0.,opt)
    names=[n for n in u.AnimPoseExtensions.get_bone_names(base) if not str(n).startswith('VB ')]
    component=u.SkeletalMeshComponent();component.set_skeletal_mesh(mesh)
    bones=[dict(name=str(n),parent=str(component.get_parent_bone(n)),
                reference=transform(u.AnimPoseExtensions.get_ref_bone_pose(base,n,u.AnimPoseSpaces.LOCAL))) for n in names]
    duration=clip.get_play_length();nframes=math.ceil(duration*30)+1
    frames=[]
    for i in range(nframes):
        t=min(duration,i/30.)
        pose=u.AnimPoseExtensions.get_anim_pose_at_time(clip,t,opt)
        frames.append([transform(u.AnimPoseExtensions.get_bone_pose(pose,n,u.AnimPoseSpaces.LOCAL)) for n in names])
    result=dict(id=row['id'],sourceClip=row['clip'],sourceMesh=row['mesh'],skeleton=clip.get_editor_property('skeleton').get_path_name(),
                seconds=duration,sourceFrames=u.AnimationLibrary.get_num_frames(clip),sampleFps=30,
                bones=bones,frames=frames,sourceModified=False,additiveType=str(clip.get_editor_property('additive_anim_type')))
    with gzip.open(target,'wt',encoding='utf-8') as out:json.dump(result,out,separators=(',',':'))
    u.log('REAL_MOTION_EXPORTED '+row['id']+' '+str(nframes))

try:
    for row in request:export(row)
except Exception:
    (L/'motion-export-error.txt').write_text(traceback.format_exc(),'utf-8');raise
