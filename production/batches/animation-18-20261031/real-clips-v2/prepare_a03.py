"""A03 uses the observed overhead strike from voxel vision's real Spear 02 clip."""
from pathlib import Path
import json, numpy as np
from motion import Motion, save_study, L
from scipy.spatial.transform import Rotation

attack=Motion('AS_Spear_Attack_02')
walk=Motion('MM_Walk_Fwd')
origin=attack.sample(1.62)
root=attack.names.index('root')
base_position=origin['p'][root].copy()
walk_lookup={n:i for i,n in enumerate(walk.names)}
settings={'episode':'A03','cameraWidth':510,'cameraHeight':140,'yaw':-65,
          'sourceInterval':[1.62,6.45],'controlRule':{'fps':60,'attackFrames':48,'earlyCancel':36,'lateCancel':48},
          'changes':['source interval of a genuine overhead weapon swing','piecewise timing to 48 frames','root translation locked for comparison'],
          'sourceModified':False}
cal=attack.sample(2.2);wp,wq=attack.world(cal)
r=attack.names.index('hand_r');left=attack.names.index('hand_l')
axis=wp[r]-wp[left];axis/=np.linalg.norm(axis)
local_axis=Rotation.from_quat(wq[r]).inv().apply(axis)
settings['weaponAxisInHand']=local_axis.tolist()
settings['weaponLength']=108

def sample(frame):
    t=np.interp(min(48,max(0,frame)),[0,5,12,18,48],[1.62,2.2,3.25,3.65,6.45])
    pose=attack.sample(t);pose['p'][root]=[0,0,0]
    return pose

yaw=Rotation.from_euler('z',settings['yaw'],degrees=True)
def blade(pose):
    p,q=attack.world(pose);direction=Rotation.from_quat(q[r]).apply(local_axis)
    return yaw.apply(p[r]+direction*6),yaw.apply(p[r]+direction*91)
start,end=blade(sample(17));target=start+(end-start)*.65
def distance(frame):
    a,b=blade(sample(frame));delta=b-a
    near=a+np.clip(np.dot(target-a,delta)/np.dot(delta,delta),0,1)*delta
    return float(np.linalg.norm(near-target))
contact=next(f for f in range(12,19) if distance(f)<=13)
settings['contactEvidence']={'target':target.tolist(),'targetRadius':12,'bladeRadius':1,'firstContactFrame':contact,
    'distances':[distance(f) for f in range(49)],'classification':'computed capsule-to-sphere contact in our demonstration'}
settings['targetLocation']=[float(target[0]),float(target[1]),float(target[2]-132)]
settings['cameraWidth']=550
jobs=[]
for key,cancel in [('attack',None),('cancel36',36),('cancel48',48),('noinput',None)]:
    poses=[];trace=[]
    for f in range(108):
        clock=max(0,f-18)
        # The extra two frames are an explicitly authored hit-stop in this demonstration.
        sim=min(48,clock if clock<contact+1 else max(contact,clock-2))
        pose=sample(sim);accepted=cancel is not None and sim>=cancel
        if accepted:
            walk_time=max(0,(clock-cancel)/60)
            source=walk.sample(walk_time%walk.seconds)
            for i,name in enumerate(attack.names):
                if name in walk_lookup:
                    j=walk_lookup[name]
                    for k in ('p','q','s'):pose[k][i]=source[k][j]
            pose['p'][root]=[0,0,0]
        poses.append(pose)
        state='standby' if f<18 else 'run' if accepted else 'idle' if sim>=48 else 'lead-in' if sim<12 else 'attack' if sim<18 else 'follow-through'
        a,b=blade(pose)
        trace.append(dict(outputFrame=f,simulationFrame=sim,state=state,freezeLeft=1 if clock in (contact+1,contact+2) else 0,
                          transitionAccepted=accepted,contactFrame=contact if clock>=contact else -1,
                          hit=clock>=contact,bladeStart=a.tolist(),bladeEnd=b.tolist(),target=target.tolist(),
                          classification='computed contact and authored input timing in our demonstration'))
    dest=L/'studies'/('A03-'+key+'.json')
    save_study(dest,attack,poses,dict(settings,kind=key,trace=trace,weapon=True))
    jobs.append(dict(key='A03-'+key,file=str(dest)))
(L/'study-build-request.json').write_text(json.dumps(jobs,indent=2),'utf-8')
print('A03 genuine motion studies',len(jobs))
