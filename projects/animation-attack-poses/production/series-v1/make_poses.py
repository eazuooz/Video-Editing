from pathlib import Path
import sys
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *
@functools.lru_cache(maxsize=1024)
def punch(amount,twist,depth,opposed):
 p=rig.pose_copy();pitch_torso(p,twist,-10*amount)
 arm(p,'r',[5+depth,16+30*amount,-17+24*amount])
 arm(p,'l',[5,20+(14 if not opposed else -14)*amount,-14+(12 if not opposed else -5)*amount])
 if opposed:
  local_rotation(p,'thigh_l','y',-13*amount);local_rotation(p,'calf_l','y',18*amount)
  local_rotation(p,'thigh_r','y',6*amount)
 return p
def swing(t):
 if t<15:return 0.
 if t<29:return -0.35*ease((t-15)/14)
 if t<38:return -0.35+1.35*ease((t-29)/9)
 if t<67:return 1.
 return 1.-ease((t-67)/25)
def clip(key):
 def pose(side,t):
  timing=min(t,(33,39)[side]) if key=='impact' and 33<=t<61 else t
  a=swing(timing)
  factor=(.48,1.)[side] if key=='size' else 1.
  w=(9,31)[side] if key=='twist' else 27
  return punch(round(a*factor,5),round(a*w*factor,4),round((23 if key=='plane' and not side else 0)*a,5),side==1 or key not in ('twist','size'))
 return pose
if __name__=='__main__':
 keys=['size','plane','top','twist','impact','camera','outline']
 funcs={k:clip('plane' if k=='top' else k) for k in keys}
 settings={'top':{'cameraView':'top'},'camera':{'cameraView':'perspective'}}
 export('A05',P,funcs,settings)
