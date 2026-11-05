"""Use the sample's real metacarpals and finger joints, keeping the hand and grip socket fixed."""
from pathlib import Path
import sys,functools
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *
@functools.lru_cache(maxsize=1)
def base():
    p=rig.pose_copy();arm(p,'r',[-19,37,-8]);return p
@functools.lru_cache(maxsize=1)
def resting_axes():
    world=rig.fk(base())
    return world,world['hand_r'][1].apply([0.,0.,1.])
def sample(key,i,t):
    p={n:(v.copy(),q) for n,(v,q) in base().items()}
    v=ease((t-10)/37);natural=bool(i or key in ('scale','count'))
    if key=='keys' and not i:v=float(t>=30)
    world,axis=resting_axes()
    palm_normal=np.cross([0.,1.,0.],axis);palm_normal/=np.linalg.norm(palm_normal)
    for j,finger in enumerate(('index','middle','ring','pinky','thumb')):
        for segment in range(1,4):
            name=f'{finger}_{segment:02}_r'
            curl=(22.,36.,22.)[segment-1] + (j*2.5 if natural else 0.)
            tilt=((19.-2.*j) if natural and segment==1 else 0.)
            if finger=='thumb':curl=-curl*.6;tilt=-tilt
            rotation=Rotation.from_rotvec(np.deg2rad(-curl*v)*axis)*Rotation.from_rotvec(np.deg2rad(tilt*v)*palm_normal)
            reference=world[name][1];position,local=p[name]
            p[name]=position,local*reference.inv()*rotation*reference
    return p
if __name__=='__main__':
    keys=('grip','keys','scale','count');world=rig.fk(base())['hand_r'][0];x,y,z=world
    profiles={k:dict(yaw=0,cameraWidth=70,cameraHeight=z-5,
                      actorLocations=[[-18-x,0,0],[18-x,0,0]]) for k in ('grip','keys')}
    profiles['grip'].update(handSockets=['hand_r','hand_r'],handOffset=[-9.05,2.51,-.35],handScale=[.044,.044,.22])
    profiles['scale']=dict(yaw=0,cameraDistance=365+y,cameraHeight=z-5,fov=43,
                           actorLocations=[[-18-x,275,0],[63-x,35,30]])
    profiles['count']=dict(yaw=0,cameraWidth=510,actorSpacing=125)
    export('A15',P,{k:lambda i,t,k=k:sample(k,i,t) for k in keys},profiles)
