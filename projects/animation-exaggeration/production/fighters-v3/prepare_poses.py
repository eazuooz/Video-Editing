"""Author sample-mannequin comparison variants in bone space, with measured IK.

Input poses are extracted by Unreal from the installed Epic sample. Every output
is an authored illustration, not an animation measured from a commercial game.
"""
from pathlib import Path
import json, math,functools
import numpy as np
from scipy.spatial.transform import Rotation as Rot

H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3'
D=json.loads((L/'unreal/asset-inspection.json').read_text())
B={b['name']:b for b in D['referenceBones'] if not b['name'].startswith('VB ')}
NAMES=list(B)
PARENTS={n:B[n]['parent'] for n in NAMES}
BASE={n:(np.array(B[n]['baseLocal']['p']),Rot.from_quat(B[n]['baseLocal']['q'])) for n in NAMES}
WORLD={n:(np.array(B[n]['baseWorld']['p']),Rot.from_quat(B[n]['baseWorld']['q'])) for n in NAMES}

def smooth(v):
    v=np.clip(v,0,1);return float(v*v*(3-2*v))
def pose_copy():return {n:(p.copy(),q) for n,(p,q) in BASE.items()}
def fk(local):
    w={}
    for n in NAMES:
        p,q=local[n];parent=PARENTS[n]
        if parent in w:
            a,r=w[parent];w[n]=(a+r.apply(p),r*q)
        else:w[n]=(p.copy(),q)
    return w
def set_world(local,n,p=None,q=None):
    w=fk(local);oldp,oldq=w[n];p=oldp if p is None else p;q=oldq if q is None else q
    parent=PARENTS[n]
    if parent in w:
        pp,pq=w[parent];local[n]=(pq.inv().apply(p-pp),pq.inv()*q)
    else:local[n]=(p.copy(),q)
def aim(local,bone,child,direction):
    w=fk(local);old=w[child][0]-w[bone][0];old/=np.linalg.norm(old)
    new=direction/np.linalg.norm(direction)
    axis=np.cross(old,new);dot=np.clip(np.dot(old,new),-1,1)
    if np.linalg.norm(axis)<1e-9:
        delta=Rot.identity() if dot>0 else Rot.from_rotvec(np.array([0,0,math.pi]))
    else:delta=Rot.from_rotvec(axis/np.linalg.norm(axis)*math.acos(dot))
    set_world(local,bone,q=delta*w[bone][1])
def ik(local,side,target):
    upper='upperarm_'+side;lower='lowerarm_'+side;hand='hand_'+side
    w=fk(local);root=w[upper][0];l1=np.linalg.norm(w[lower][0]-root);l2=np.linalg.norm(w[hand][0]-w[lower][0])
    v=target-root;d=np.linalg.norm(v)
    assert abs(l1-l2)+.05<d<l1+l2-.05,(side,d,l1,l2)
    f=v/d;pole=np.array([-1 if side=='r' else 1,-.35,-.55]);pole-=np.dot(pole,f)*f;pole/=np.linalg.norm(pole)
    a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-a*a))
    elbow=root+f*a+pole*h
    aim(local,upper,lower,elbow-root);w=fk(local);aim(local,lower,hand,target-w[lower][0])
    w=fk(local);return float(np.linalg.norm(w[hand][0]-target))

@functools.lru_cache(maxsize=4096)
def authored_pose(mode,phase,progress,variant):
    p=pose_copy();base_shoulder=WORLD['upperarm_r'][0]
    # The opposite hand stays in a recognizable guard pose.
    ik(p,'l',WORLD['upperarm_l'][0]+np.array([3.,22.,-12.]))
    amount=progress if variant else 0.
    if mode=='shoulder-control':
        if phase==0:
            target=base_shoulder+np.array([0.,25.,-15.])
        elif phase==1:
            target=base_shoulder+np.array([0.,18.+19.*amount,-24.+32.*amount])
        elif phase==2:
            # Move the anchor and the whole arm; its local joint angle is unchanged.
            shift=np.array([0.,22.*amount,8.*amount])
            set_world(p,'clavicle_r',WORLD['clavicle_r'][0]+shift)
            target=base_shoulder+shift+np.array([0.,35.,-12.])
        else:
            # Same hand target, while the right panel is allowed chest/shoulder motion.
            if variant:
                set_world(p,'spine_03',q=Rot.from_euler('z',-28.*amount,degrees=True)*WORLD['spine_03'][1])
                desired=base_shoulder+np.array([0.,22.*amount,8.*amount])
                current=fk(p)['upperarm_r'][0]
                set_world(p,'clavicle_r',fk(p)['clavicle_r'][0]+desired-current)
            target=base_shoulder+np.array([0.,45.,-2.])
        error=ik(p,'r',target)
    else:
        # One punch: preparation, strike and recovery are matched in time.
        strength=1.0 if variant and phase==2 else .35
        angle=-40*strength*progress
        set_world(p,'spine_03',q=Rot.from_euler('z',angle,degrees=True)*WORLD['spine_03'][1])
        w=fk(p);target=w['upperarm_r'][0]+np.array([0.,24.+19.*progress,-13.+15.*progress])
        error=ik(p,'r',target)
    w=fk(p)
    return p,{'shoulder':w['upperarm_r'][0].tolist(),'wrist':w['hand_r'][0].tolist(),
        'elbow':w['lowerarm_r'][0].tolist(),'target':target.tolist(),'endpointErrorCm':error}

def make(profile):
    frames=round(profile['duration']*60);mode=profile['mode'];animations=[];evidence=[]
    for variant in (0,1):
        allposes=[];stats=[]
        for frame in range(frames+1):
            t=min(frame/60,profile['duration']-1e-7)
            cue=next(c for c in profile['phases'] if c['start']<=t<c['end']);phase=cue['phase']
            elapsed=t-cue['start']-cue.get('motionStart',0)
            if mode=='shoulder-control':progress=smooth(elapsed/max(.001,cue.get('motionDuration',0))) if cue.get('motionDuration',0)>0 else 0
            else:
                # One visible stroke then hold the informative pose until the next cue.
                progress=smooth(elapsed/.75)
            p,s=authored_pose(mode,phase,progress,variant);s=dict(s);allposes.append(p)
            s.update(frame=frame,phase=phase,progress=progress);stats.append(s)
        tracks={}
        for n in NAMES:
            ps=np.array([p[n][0] for p in allposes]);qs=np.array([p[n][1].as_quat() for p in allposes])
            static=np.max(abs(ps-ps[0]))<1e-7 and np.max(abs(qs-qs[0]))<1e-7
            tracks[n]={'p':np.round(ps[:1] if static else ps,7).tolist(),
                       'q':np.round(qs[:1] if static else qs,8).tolist(),'s':B[n]['baseLocal']['s']}
        animations.append({'side':'left' if variant==0 else 'right','tracks':tracks});evidence.append(stats)
    if mode=='shoulder-control':
        fixed=[s for s in evidence[0] if s['phase']==3]
        if fixed:
            assert np.ptp(np.array([s['shoulder'] for s in fixed]),axis=0).max()<.001
        for a,b in zip(*evidence):
            if a['phase']==3:assert np.linalg.norm(np.array(a['target'])-b['target'])<.001
    assert max(s['endpointErrorCm'] for row in evidence for s in row)<.001
    result={'id':profile['id'],'mode':mode,'frames':frames,'fps':60,'sourcePose':D['sampleAnimation'],
        'mesh':D['mesh'],'skeleton':D['skeleton'],'animations':animations,'phases':profile['phases'],
        'evidence':{'left':evidence[0],'right':evidence[1]},'classification':'authored-explanation',
        'maximumRightShoulderTravelCm':23.4093998214,'handTargetPolicy':'same target in shoulder phase3'}
    out=L/'unreal/poses'/f"{profile['id']}.json";out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8');print(profile['id'],frames,len(tracks))

def main():
    profiles=json.loads((R/'unity/VideoEditing/Assets/VideoScenes/animation-series-v1/animation-exaggeration-presentations.json').read_text(encoding='utf-8-sig'))
    wanted={'A02-E004','A02-E005','A02-E011','A02-E013','A02-E014','A02-E015'}
    entries=next(v for v in profiles.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'phases' in v[0])
    for p in entries:
        if p['id'] in wanted:make(p)
    # Small representative first render before the full capture jobs.
    make({'id':'A02-prototype','mode':'shoulder-control','duration':3.,'phases':[
        {'phase':3,'start':0.,'end':3.,'motionStart':.3,'motionDuration':1.2}]})
if __name__=='__main__':main()
