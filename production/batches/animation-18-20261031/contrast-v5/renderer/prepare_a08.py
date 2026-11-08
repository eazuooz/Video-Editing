"""Actual same-rig cumulative posing, derived from the saved A08 final pose.

No vendor asset is edited. CPU authors editable tracks for an isolated UE worker.
"""
from sources import *
import importlib.util,shutil
from scipy.spatial.transform import Slerp
LOCAL=B/'local/contrast-v5/a08-cumulative'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
def main():
    ctrl=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert ctrl['fullLocalProductionAuthorized'] and 'A08'in ctrl['episodes']
    sys.path.insert(0,str(B/'native'))
    original=project('A08')/'production/series-v1/make_poses.py';m=load('a08_original_pose_definition',original);rig=m.rig
    base=rig.pose_copy();final=m.make('flow',1,40)
    groups=[['neck_01'],['spine_01','spine_02'],['clavicle_r','upperarm_r','lowerarm_r','upperarm_l','lowerarm_l'],['hand_r'],['pelvis'],['thigh_r','thigh_l','calf_l','foot_l']]
    states=[base]
    for group in groups:
        nxt={k:(p.copy(),q)for k,(p,q)in states[-1].items()}
        for name in group:nxt[name]=final[name]
        states.append(nxt)
    assert all(np.allclose(states[-1][k][0],final[k][0])and np.allclose(states[-1][k][1].as_quat(),final[k][1].as_quat())for k in final),'Full final pose must equal existing A08 flow final pose'
    paths={'flow':([0,12,48,88,179],[0,0,1,2,2]),'edge':([0,12,48,88,179],[2,2,3,4,4]),'stance':([0,12,48,88,179],[4,4,5,6,6]),'overview':([0,12,38,65,92,119,145,171,179],[0,0,1,2,3,4,5,6,6])}
    definitions={}
    calibration=read(H/'a08-ground-calibration.json')['keys']if(H/'a08-ground-calibration.json').exists()else{}
    def blend(a,b,u):
        u=float(u);return {k:((1-u)*a[k][0]+u*b[k][0],Slerp([0,1],Rotation.from_quat([a[k][1].as_quat(),b[k][1].as_quat()]))([u])[0])for k in a}
    for key,(times,stages)in paths.items():
        recordings=[];evidence=[]
        for side in (0,1):
            poses=[];trace=[]
            for n in range(181):
                if side==0:pose=states[stages[0]]
                else:
                    j=min(len(times)-2,max(0,int(np.searchsorted(times,n,side='right')-1)))
                    u=float(np.clip((n-times[j])/(times[j+1]-times[j]),0,1));u=u*u*(3-2*u)
                    pose=blend(states[stages[j]],states[stages[j+1]],u)
                if side==1 and key in calibration:
                    # Exact old joint rotations/relative locations are retained.
                    # Root height only follows the visible actual support sole.
                    pose={k:(p.copy(),q)for k,(p,q)in pose.items()}
                    rp,rq=pose['root'];rp[2]+=calibration[key][min(n,179)]['rootDeltaZCm'];pose['root']=(rp,rq)
                poses.append(pose);world=rig.fk(pose);trace.append({k:world[k][0].round(5).tolist()for k in ('head','pelvis','upperarm_r','lowerarm_r','hand_r','hand_l','foot_r','foot_l')})
            tracks={}
            for name in rig.NAMES:
                pp=np.stack([p[name][0]for p in poses]);qq=np.stack([p[name][1].as_quat()for p in poses])
                if np.max(abs(pp-pp[0]))<1e-6 and np.max(abs(qq-qq[0]))<1e-6:pp=pp[:1];qq=qq[:1]
                tracks[name]={'p':pp.round(6).tolist(),'q':qq.round(7).tolist(),'s':rig.B[name]['baseLocal']['s']}
            recordings.append({'side':('left','right')[side],'tracks':tracks});evidence.append(trace)
        d={'frames':180,'fps':60,'animations':recordings,'motionEvidence':evidence,'yaw':-21,'cameraWidth':450,'cameraHeight':85,'actorSpacing':95,
           'authoring':'Same original A08 articulated mannequin, fixed source mesh/light/camera, cumulative actual joint edits. Not a commercial-game motion capture.',
           'sourceDefinition':str(original.relative_to(R)).replace('\\','/'),'sourceDefinitionSha256':sha(original),
           'stageTimes':times,'stageIndices':stages,'stages':['original','head','torso','arms','wrist','pelvis','legs and feet'],'observationFrames':[12,88]}
        if key in calibration:d['rootGroundCorrection']={'basis':'Actual first UE-render support sole pixels','calibration':str((H/'a08-ground-calibration.json').relative_to(R)).replace('\\','/'),'sha256':sha(H/'a08-ground-calibration.json'),'noMassOrForceClaim':True}
        save(LOCAL/'poses'/(key+'.json'),d);definitions[key]={'file':str(LOCAL/'poses'/(key+'.json')),'sha256':sha(LOCAL/'poses'/(key+'.json'))}
    job={'episode':'A08ContrastV5','keys':list(paths),'mesh':rig.D['mesh'],'skeleton':rig.D['skeleton'],'local':str(LOCAL)}
    save(LOCAL/'study-job.json',job)
    save(H/'a08-capture-plan.json',{'status':'editable-pose-data-authored-actual-capture-pending','scope':'A08 alone, cumulative correction under current explicit 17-episode authorization','local':str(LOCAL),'job':job,'definitions':definitions,
         'originalFinalJointRotationsExactlyReused':True,'rootGroundCorrectionApplied':bool(calibration),'firstToFinalOrder':['original','head','torso','arms','wrist','pelvis','legs/feet'],
         'forbiddenSubstitution':'Do not use the unrelated dance/waving source clips as the one cumulative pose.','humanReviewed':False,'platformChanged':False})
    print('Authored four 180-frame actual pose sequences; no GPU started')
if __name__=='__main__':main()
