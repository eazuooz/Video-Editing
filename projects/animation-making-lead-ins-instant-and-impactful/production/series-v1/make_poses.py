"""A04. Same rig and contact pose; change only the distribution of the windup."""
from pathlib import Path
import json,sys,math,functools
import numpy as np
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/series-v1';L.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'projects/animation-exaggeration/production/fighters-v3'))
import prepare_poses as rig
keys=('anticipation','charge','jab','weight')
N=120
def lerp(a,b,p):return a+(b-a)*max(0.,min(1.,p))
def state(key,side,t):
 t=t-15
 if key=='anticipation':
  if t<0:return 0.,0.
  if t<9:return ((t/9)**(2.2 if side==0 else .22)),0.
  if t<=12:return 1.,(t-9)/3
  return 1-lerp(0,1,(t-25)/18),1-lerp(0,1,(t-25)/18)
 pre,hold,strike=(10,30,8) if key=='charge' else ((0,0,1) if side==0 else (10,0,2)) if key=='jab' else ((5,3,3) if side==0 else (22,12,6))
 if t<0:return 0.,0.
 if key=='charge' and side==0:return 0.,0.
 if pre and t<pre:return t/pre,0.
 if t<pre+hold:return 1.+(.035*math.sin(t*1.5) if key=='charge' else 0.),0.
 if t<=pre+hold+strike:return (1. if pre else 0.),min(1.,(t-pre-hold+1)/strike) if not pre else (t-pre-hold)/strike
 if t<pre+hold+strike+10:return (1. if pre else 0.),1.
 p=max(0.,1.-(t-pre-hold-strike-10)/22.)
 return (p if pre else 0.),p
@functools.lru_cache(maxsize=512)
def make(w,s):
 local=rig.pose_copy();twist=(-34*w+50*s)
 rig.set_world(local,'spine_01',q=Rotation.from_euler('xz',[12*w-14*s,twist],degrees=True)*rig.WORLD['spine_01'][1])
 world=rig.fk(local)
 for side in ('l','r'):
  pivot=world['upperarm_'+side][0]
  direction=np.array([8.,21.,-16.]) if side=='l' else np.array([5.+10*w-12*s,19.-30*w+59*s,-16.+33*w-12*s])
  reach=np.linalg.norm(direction)
  if reach>48:direction*=48/reach
  # Always within reachable arm length. Hand and sleeve retain native scale.
  rig.ik(local,side,pivot+direction)
 return local
def bake(key):
 sides=[];traces=[];(L/'poses').mkdir(exist_ok=True)
 for side in (0,1):
  samples=[];trace=[]
  for t in range(N+1):
   w,s=state(key,side,t);local=make(round(w,5),round(s,5));samples.append(local)
   pts=rig.fk(local);trace.append({'frame':t,'wrist':pts['hand_r'][0].round(3).tolist(),'windup':round(w,4),'strike':round(s,4)})
  tracks={}
  for bone in rig.NAMES:
   pos=np.stack([p[bone][0] for p in samples]);rots=np.stack([p[bone][1].as_quat() for p in samples])
   if np.max(np.abs(pos-pos[0]))<1e-6 and np.max(np.abs(rots-rots[0]))<1e-6:pos=pos[:1];rots=rots[:1]
   tracks[bone]={'p':pos.round(6).tolist(),'q':rots.round(7).tolist(),'s':rig.B[bone]['baseLocal']['s']}
  sides.append({'side':('left','right')[side],'tracks':tracks});traces.append(trace)
 data={'frames':N,'yaw':-87,'animations':sides}
 (L/'poses'/f'{key}.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
 return traces
if __name__=='__main__':
 result={k:bake(k) for k in keys};a,b=result['anticipation']
 assert a[27]['strike']==b[27]['strike']==1 and a[27]['wrist']==b[27]['wrist'] and a[16]['windup']<b[16]['windup']
 (H/'motion-evidence.json').write_text(json.dumps(result,separators=(',',':')),encoding='utf-8')
 (L/'study-job.json').write_text(json.dumps(dict(episode='A04',keys=keys,mesh=rig.D['mesh'],skeleton=rig.D['skeleton'])),encoding='utf-8')
