from pathlib import Path
import functools,sys
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *
@functools.lru_cache(maxsize=2048)
def keyed(a,settle,step,lean):
 p=rig.pose_copy();pitch_torso(p,34*a+19*settle,-15*a-9*settle)
 arm(p,'r',[4,18+29*a,-15+12*a-17*settle]);arm(p,'l',[5,21-13*a,-15+9*a])
 if step:
  pp,rot=p['pelvis'];p['pelvis']=(pp+np.array([0.,19.*step,3*math.sin(step*math.pi)]),rot)
  local_rotation(p,'thigh_r','y',30*step);local_rotation(p,'thigh_l','y',-22*step);local_rotation(p,'calf_l','y',18*step)
 return p
def sample(key,side,t):
 frame=t%82
 if frame<10:a=-.45*ease(frame/10)
 elif frame<15:a=-.45+1.45*ease((frame-10)/5)
 elif frame<60:
  if (side==1 and key=='ending'):a=1.-ease((frame-24)/36)
  else:a=1.-ease((frame-15)/(24 if key=='ending' else 45))
 else:a=0.
 settle=(.5*np.sin(math.pi*np.clip((frame-15)/38,0,1))) if side and key=='ending' else 0.
 step=ease((frame-(42 if side else 60))/15) if key=='control' else 0.
 return keyed(round(a,5),round(float(settle),5),round(step,5),0)
if __name__=='__main__':
 keys=('timing','ending','control');export('A06',P,{k:(lambda i,t,k=k:sample(k,i,t)) for k in keys})
