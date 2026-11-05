"""Keep an attacker's reference fixed while comparing silhouette, recoil height and root travel."""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *

def react(key,i,t):
    pose=rig.pose_copy()
    v=ease((t-11)/6)*(1-ease((t-46)/30))
    amount=v*(.20 if key=='recoil' and i==0 else 1)
    high=key!='height' or i==0
    pitch_torso(pose,amount*(9+33*i),amount*(29 if high else -19))
    local_rotation(pose,'neck_01','x',amount*(-18 if high else 11))
    arm(pose,'r',[8+amount*(18+5*i),16,-29+amount*(56 if high else 12)])
    arm(pose,'l',[-3-18*i*amount,12+8*amount,-25+amount*(32 if high else 4)])
    local_rotation(pose,'thigh_l','y',20*amount if high else 38*amount)
    local_rotation(pose,'calf_l','x',-28*amount)
    if key=='root' and i:
        xyz,q=pose['root'];pose['root']=(xyz+np.array([0,37*v,0]),q)
    if key=='turn':
        hip,q=pose['pelvis'];pose['pelvis']=(hip+np.array([0,0,25*v]),q)
    return pose
if __name__=='__main__':
    keys=('recoil','root','height','turn')
    export('A10',P,{k:lambda i,t,k=k:react(k,i,t) for k in keys})
