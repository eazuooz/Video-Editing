"""Use the sample's real metacarpals and finger joints, keeping the hand and grip socket fixed."""
from pathlib import Path
import sys,functools
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *
@functools.lru_cache(maxsize=1)
def base():
    p=rig.pose_copy();arm(p,'r',[-19,37,-8]);return p
def sample(key,i,t):
    p={n:(v.copy(),q) for n,(v,q) in base().items()}
    v=ease((t-10)/37);natural=bool(i or key in ('scale','count'))
    if key=='keys' and not i:v=float(t>=30)
    for j,finger in enumerate(('index','middle','ring','pinky','thumb')):
        for segment in range(1,4):
            name=f'{finger}_{segment:02}_r'
            bend=(26+6*j) if finger!='thumb' else 23
            spread=(j-1)*8*v if natural and segment==1 else 0
            local_rotation(p,name,'yz',[(-1 if finger=='thumb' else 1)*bend*v,spread])
    return p
if __name__=='__main__':
    keys=('grip','keys','scale','count');world=rig.fk(base())['hand_r'][0];x,y,z=world
    profiles={k:dict(yaw=0,cameraWidth=70,cameraHeight=z-5,
                      actorLocations=[[-18-x,0,0],[18-x,0,0]]) for k in ('grip','keys')}
    profiles['grip']['handSockets']=['hand_r','hand_r']
    profiles['scale']=dict(yaw=0,cameraDistance=90+y,cameraHeight=z-5,fov=43,
                           actorLocations=[[-18-x,0,0],[60-x,-210,0]])
    profiles['count']=dict(yaw=0,cameraWidth=510,actorSpacing=125)
    export('A15',P,{k:lambda i,t,k=k:sample(k,i,t) for k in keys},profiles)
