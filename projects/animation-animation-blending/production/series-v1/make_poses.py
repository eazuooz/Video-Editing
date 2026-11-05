"""Blend clips in joint space and solve an ankle target on an actual measured incline."""
from pathlib import Path
import sys,math,functools
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *
@functools.lru_cache(maxsize=1)
def attacking():
    p=rig.pose_copy();pitch_torso(p,31,18)
    arm(p,'r',[7,42,4]);arm(p,'l',[4,21,-12]);local_rotation(p,'thigh_l','x',18)
    return p
@functools.lru_cache(maxsize=128)
def walking(t):
    p=rig.pose_copy();phase=(t-17)*2*math.pi/49
    for i,side in enumerate(('l','r')):
        v=math.sin(phase+i*math.pi)
        local_rotation(p,'thigh_'+side,'x',24*v);local_rotation(p,'calf_'+side,'x',-25*max(v,0))
        arm(p,side,[4,13-12*v,-36])
    return p
def blend(a,b,w):
    return {n:((1-w)*a[n][0]+w*b[n][0],a[n][1]*Rotation.from_rotvec((a[n][1].inv()*b[n][1]).as_rotvec()*w)) for n in rig.NAMES}
def ankle(p,side,target):
    upper='thigh_'+side;lower='calf_'+side;foot='foot_'+side;world=rig.fk(p)
    start=world[upper][0];mid=world[lower][0];end=world[foot][0]
    a=np.linalg.norm(mid-start);b=np.linalg.norm(end-mid);delta=target-start
    distance=np.clip(np.linalg.norm(delta),abs(a-b)+.01,a+b-.01);f=delta/np.linalg.norm(delta)
    pole=np.array([0.,1.,0.]);pole-=pole.dot(f)*f;pole/=np.linalg.norm(pole)
    along=(a*a-b*b+distance*distance)/(2*distance)
    knee=start+along*f+np.sqrt(max(0,a*a-along*along))*pole
    rig.aim(p,upper,lower,knee-start);rig.aim(p,lower,foot,target-rig.fk(p)[lower][0])
def study(key,side,t):
    if key in ('blend','duration'):
        length=(1 if not side else 14) if key=='blend' else (6 if not side else 24)
        return blend(attacking(),walking(t),ease((t-18)/length))
    if key=='guard':
        p=rig.pose_copy();r=side*ease((t-8)/30);theta=(t-8)*np.pi/65
        pitch_torso(p,23*r*np.cos(theta),21*r*np.sin(theta))
        arm(p,'r',[4,21,19]);arm(p,'l',[-4,20,19]);return p
    p=rig.pose_copy();v=ease((t-9)/31);root,q=p['root'];p['root']=(root+np.array([0,23*v,0]),q)
    arm(p,'r',[8,25,2]);arm(p,'l',[-8,23,2])
    for limb in ('l','r'):
        if side:
            w=rig.fk(p)[('foot_'+limb)][0];target=w.copy()
            angle=np.radians(-72);x=w[0]*np.cos(angle)-w[1]*np.sin(angle)
            target[2]=rig.WORLD['foot_'+limb][0][2]+5+np.tan(np.radians(9))*x
            ankle(p,limb,target)
    return p
if __name__=='__main__':
    keys=('blend','duration','guard','slope')
    export('A14',P,{k:lambda i,t,k=k:study(k,i,t) for k in keys},
           {'slope':{'rampPitch':9,'yaw':-72},'guard':{'yaw':-15}})
