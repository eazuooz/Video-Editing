"""Independently adjust brow, sclera exposure, jaw opening and camera distance."""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from face_studies import *
def pose(key,side,t):
    w=smooth(t,8,36)*(1-smooth(t,65,100));e=w*((.22 if not side else 1.) if key!='distance' else .82);p={}
    if key!='mouth':
        for lr in ('L','R'):
            face(p,lr+'_brow_mid',1.15*e);face(p,lr+'_brow_outer',.8*e)
            face(p,lr+'_eye_lid_upper_mid',.52*e);face(p,lr+'_eye_lid_lower_mid',-.21*e)
        face(p,'C_brow_mid',.65*e)
    if key!='eyes':
        face(p,'C_jaw',-.20*e,(-15*e,0,0))
        face(p,'C_lip_upper_mid',.2*e)
        face(p,'C_lip_lower_mid',-.12*e)
    return p
if __name__=='__main__':
    settings={s:dict(cameraWidth=96,actorSpacing=23,cameraHeight=172,yaw=-3) for s in ('expression','eyes','mouth')}
    settings['distance']=dict(cameraDistance=76,fov=74,cameraHeight=173,yaw=-3,actorLocations=[[-28,0,0],[105,-210,0]])
    author('A12',P,settings,pose)
