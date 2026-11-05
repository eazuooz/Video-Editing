"""Author clip data for the installed human-proportioned UE sample without editing its assets."""
from pathlib import Path
import json,sys,math,functools
import numpy as np
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'projects/animation-exaggeration/production/fighters-v3'))
import prepare_poses as rig
def ease(x):
 x=float(np.clip(x,0,1));return x*x*(3-2*x)
def local_rotation(pose,bone,axis,angle):
 p,q=pose[bone];pose[bone]=(p,q*Rotation.from_euler(axis,angle,degrees=True))
def arm(pose,side,offset):
 w=rig.fk(pose);pivot=w['upperarm_'+side][0];off=np.array(offset,dtype=float);length=np.linalg.norm(off)
 off*=np.clip(length,10,48)/max(.001,length);rig.ik(pose,side,pivot+off)
def pitch_torso(pose,yaw,bend):
 rig.set_world(pose,'spine_01',q=Rotation.from_euler('xz',[bend,yaw],degrees=True)*rig.WORLD['spine_01'][1])
def export(ep,p,functions,settings=None):
 l=p/'production/local/series-v1';h=p/'production/series-v1';out=l/'poses';out.mkdir(parents=True,exist_ok=True)
 count=120;receipt={}
 for key,fn in functions.items():
  clips=[];evidence=[];profile=(settings or {}).get(key,{})
  for side in range(2):
   frames=[];trace=[]
   for t in range(count+1):
    pose=fn(side,t)
    frames.append(pose);world=rig.fk(pose)
    trace.append({n:world[n][0].round(3).tolist() for n in ('head','pelvis','hand_r','hand_l','foot_r','foot_l')})
   tracks={}
   for bone in rig.NAMES:
    pos=np.stack([x[bone][0] for x in frames]);rot=np.stack([x[bone][1].as_quat() for x in frames])
    if np.max(np.abs(pos-pos[0]))<1e-6 and np.max(np.abs(rot-rot[0]))<1e-6:pos=pos[:1];rot=rot[:1]
    tracks[bone]={'p':pos.round(6).tolist(),'q':rot.round(7).tolist(),'s':rig.B[bone]['baseLocal']['s']}
   clips.append({'side':['left','right'][side],'tracks':tracks});evidence.append(trace)
  (out/(key+'.json')).write_text(json.dumps(dict(frames=count,animations=clips,**profile),separators=(',',':')),encoding='utf-8')
  receipt[key]=evidence
 (h/'motion-evidence.json').write_text(json.dumps(receipt,separators=(',',':')),encoding='utf-8')
 (l/'study-job.json').write_text(json.dumps(dict(episode=ep,keys=list(functions),mesh=rig.D['mesh'],skeleton=rig.D['skeleton'])),encoding='utf-8')
