"""Identical start/end poses with independently controlled in-betweens and hand return paths."""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *
def sample(key,i,t):
    p=rig.pose_copy()
    start,end=14,22
    u=float(np.clip((t-start)/(end-start),0,1))
    if key=='kick':
        w=(max(0,(u-.625)/.375) if i else u)*(1-ease((t-43)/24))
        pitch_torso(p,-13+24*w,-5-13*w)
        local_rotation(p,'thigh_r','xz',[28+59*w,-15*w])
        local_rotation(p,'calf_r','x',-85+79*w)
        local_rotation(p,'foot_r','y',15*w)
        arm(p,'r',[8,17,-9+19*w]);arm(p,'l',[-7,14,9-13*w])
    else:
        peak=26
        rise=float(np.clip((t-11)/(peak-11),0,1))
        if i and key=='upper':rise=ease((t-22)/4)
        return_v=ease((t-peak-5)/26)
        s=rise*(1-return_v)
        hip,q=p['pelvis'];p['pelvis']=(hip+np.array([0,0,-14*(1-s)]),q)
        pitch_torso(p,-29+51*s,16-24*s)
        arch=np.sin(np.pi*return_v) if i and key=='returning' else 0
        arm(p,'r',[7+13*s-16*arch,18+7*s-13*arch,-27+65*s])
        arm(p,'l',[6,15,-12])
    return p
if __name__=='__main__':
    keys=('kick','upper','returning')
    export('A11',P,{k:lambda i,t,k=k:sample(k,i,t) for k in keys},
           {k:dict(cameraWidth=505,yaw=-65) for k in keys})
