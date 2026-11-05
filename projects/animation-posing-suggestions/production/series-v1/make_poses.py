"""Pose the same articulated body with visible changes to posture, wrists and foot support."""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent; P=H.parents[1]; R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *

def make(key,side,t):
    pose=rig.pose_copy()
    strength=side*ease((t-8)/30)
    pitch_torso(pose,24*strength,-9*strength)
    local_rotation(pose,'neck_01','yz',[11*strength,-20*strength])
    local_rotation(pose,'spine_02','y',-11*strength)
    if key in ('flow','edge'):
        arm(pose,'l',[4-16*strength,12+14*strength,-28+4*strength])
        arm(pose,'r',[6+24*strength,14+8*strength,-27+37*strength])
        local_rotation(pose,'hand_r','xz',[19*strength,-12*strength])
        local_rotation(pose,'clavicle_r','x',10*strength)
    if key in ('stance','flow'):
        hip,q=pose['pelvis'];pose['pelvis']=(hip+np.array([12*strength,0,-4*strength]),q)
        local_rotation(pose,'thigh_r','yz',[13*strength,7*strength])
        local_rotation(pose,'thigh_l','yz',[-12*strength,-5*strength])
        local_rotation(pose,'calf_l','x',-18*strength)
        local_rotation(pose,'foot_l','z',-13*strength)
    return pose
if __name__=='__main__':
    keys=('flow','edge','stance')
    export('A08',P,{k:lambda side,t,k=k:make(k,side,t) for k in keys},
           {k:dict(yaw=-21,cameraWidth=450,actorSpacing=95) for k in keys})
