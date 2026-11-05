from pathlib import Path
import sys,functools
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *
@functools.lru_cache(maxsize=320)
def flinch(amount):
 p=rig.pose_copy();pitch_torso(p,24*amount,17*amount)
 local_rotation(p,'neck_01','z',-21*amount)
 arm(p,'r',[4+14*amount,14+10*amount,-21+42*amount]);arm(p,'l',[5,15,-19+27*amount])
 hip,q=p['pelvis'];p['pelvis']=(hip+np.array([0.,-11*amount,-4*amount]),q)
 local_rotation(p,'thigh_l','y',14*amount)
 return p
def study(key,i,t):
 v=ease((t-10)/14)*(1-ease((t-48)/35))
 return flinch(round(v*((.19 if i==0 else 1.) if key=='gesture' else .5),5))
if __name__=='__main__':
 settings={'near':{'cameraDistance':720,'fov':40},'far':{'cameraDistance':1310,'fov':40}}
 keys=('gesture','near','far');export('A07',P,{k:lambda i,t,k=k:study(k,i,t) for k in keys},settings)
