"""Evaluate authored animation assets through UE 5.8 itself at strike-start and strike-end."""
from pathlib import Path
import math,json,unreal as u
H=Path(__file__).resolve().parent;L=H.parents[1]/'local/fighters-v4-kula-lili/unreal'
def position(anim,sec,bone):
    options=u.AnimPoseEvaluationOptions()
    options.set_editor_property('evaluation_type',u.AnimDataEvalType.COMPRESSED)
    pose=u.AnimPoseExtensions.get_anim_pose_at_time(anim,sec,options)
    t=u.AnimPoseExtensions.get_bone_pose(pose,bone,u.AnimPoseSpaces.WORLD).translation
    return (t.x,t.y,t.z)
report=[]
for f in sorted(L.glob('A02-E*-build.json')):
    build=json.loads(f.read_text());poses=json.loads((L/'poses'/(build['id']+'.json')).read_text())
    clips=[u.load_asset(p) for p in build['animationAssets']]
    for phase in poses['phases']:
        frame0=round(phase['start']*60);frame1=next(k for k in range(frame0,poses['frames']) if poses['evidence']['left'][k]['progress']>=.99999 and poses['evidence']['left'][k]['phase']==phase['phase'])
        movement=[];shoulder=[];ends=[]
        for clip in clips:
            start=position(clip,frame0/60,'hand_r');end=position(clip,frame1/60,'hand_r')
            movement.append(math.dist(start,end));ends.append(end)
            shoulder.append(math.dist(position(clip,frame0/60,'upperarm_r'),position(clip,frame1/60,'upperarm_r')))
        report.append(dict(clip=build['id'],first=frame0,peak=frame1,wristCm=movement,engineRatio=movement[1]/movement[0],shoulderCm=shoulder,
            commonEndSeparationCm=math.dist(*ends) if poses['mode']=='shoulder-control' and phase['phase']==3 else None))
result={'engine':u.SystemLibrary.get_engine_version(),'method':'UE AnimPoseExtensions.get_anim_pose_at_time using the saved left and right AnimSequences, then component-space hand_r displacement in centimetres. One sample pair per narrated phase.','phases':report}
(H/'ue-evaluated-amplitude.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
assert all(abs(r['wristCm'][0]-30)<1 and abs(r['wristCm'][1]-54)<1 and abs(r['engineRatio']-1.8)<.06 for r in report),report
