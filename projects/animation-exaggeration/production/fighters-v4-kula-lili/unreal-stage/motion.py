"""Bake the dual-arm comparison from the inspected Unreal sample pose (centimetres).
The measured scalar is the distance from each wrist's strike-start to strike-end.
The common-target reach starts from a deeper windup on the right. This preserves
both the 1.8 travel ratio and the scripted shared final target. No mesh scaling.
"""
from pathlib import Path
import functools, hashlib, json, sys, math
import numpy as np
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent; R=H.parents[4]; L=H.parents[1]/'local/fighters-v4-kula-lili/unreal'
BASE_TOOLS=H.parents[1]/'fighters-v3'
sys.path.insert(0,str(BASE_TOOLS))
import prepare_poses as rig
PROFILES=R/'unity/VideoEditing/Assets/VideoScenes/animation-series-v1/animation-exaggeration-presentations.json'
IDS={'A02-E004','A02-E005','A02-E011','A02-E013','A02-E014','A02-E015'}
DIRECTION=np.array([0.,24.,18.]) # exact 30cm reference and 54cm treatment
ORIGIN=rig.WORLD['upperarm_r'][0]
SCALES=(1.,1.8)
def ease(t):
    t=np.clip(t,0,1)
    return round(float(t*t*(3-2*t)),6)
@functools.lru_cache(maxsize=4096)
def pose(mode,phase,progress,side):
    local=rig.pose_copy()
    scale=SCALES[side]
    shared_target=mode=='shoulder-control' and phase==3
    rotary=mode=='shoulder-control' and phase==1
    offset=DIRECTION*scale
    end=ORIGIN+np.array([0.,43.,0.])
    start=end-offset if shared_target else ORIGIN+np.array([0.,1.,-24.])
    desired=start+offset*progress
    if side and not rotary:
        # Lean from the waist and twist the chest so the shoulder travels on
        # the articulated torso. No stretched clavicle and no displaced feet.
        spine='spine_01'
        base=rig.WORLD[spine][1]
        motion=Rotation.from_euler('xz',[-28*progress,-27*progress],degrees=True)
        rig.set_world(local,spine,q=motion*base)
        # Open the opposite shoulder into a readable guarding stance.
    guard=rig.fk(local)['upperarm_l'][0]+np.array([3.,17.,-12.])
    rig.ik(local,'l',guard)
    err=rig.ik(local,'r',desired)
    world=rig.fk(local)
    measured={key:world[n][0].tolist() for key,n in [('shoulder','upperarm_r'),('wrist','hand_r'),('elbow','lowerarm_r')]}
    measured.update(target=desired.tolist(),origin=start.tolist(),peak=(start+offset).tolist(),endpointErrorCm=err)
    return local,measured
def bake(profile):
    mode=profile['mode'];count=round(profile['duration']*60)
    sides=[];evidence={}
    for side,label in enumerate(('left','right')):
        poses=[];stats=[]
        for frame in range(count+1):
            t=min(frame/60,profile['duration']-1e-7)
            cue=next(c for c in profile['phases'] if c['start']<=t<c['end'])
            phase=cue['phase'];elapsed=t-cue['start']-cue.get('motionStart',0)
            span=cue.get('motionDuration') or (1.35 if mode=='shoulder-control' else 0.78)
            q=ease(elapsed/span)
            p,record=pose(mode,phase,q,side)
            poses.append(p);stats.append(dict(record,frame=frame,phase=phase,progress=q))
        tracks={}
        for n in rig.NAMES:
            pp=np.stack([p[n][0] for p in poses]);qq=np.stack([p[n][1].as_quat() for p in poses])
            if np.max(np.abs(pp-pp[0]))<1e-7 and np.max(np.abs(qq-qq[0]))<1e-7:pp=pp[:1];qq=qq[:1]
            tracks[n]={'p':pp.round(7).tolist(),'q':qq.round(8).tolist(),'s':rig.B[n]['baseLocal']['s']}
        sides.append({'side':label,'tracks':tracks});evidence[label]=stats
    error=max(x['endpointErrorCm'] for arr in evidence.values() for x in arr)
    assert error<.001
    trials=[]
    for cue in profile['phases']:
        rr=[[x for x in evidence[k] if cue['start']<=x['frame']/60<cue['end']] for k in ('left','right')]
        distance=[max(float(np.linalg.norm(np.array(x['wrist'])-x['origin'])) for x in arr) for arr in rr]
        assert np.allclose(distance,[30,54],atol=.003),(profile['id'],distance)
        shoulders=[max(float(np.linalg.norm(np.array(x['shoulder'])-arr[0]['shoulder'])) for x in arr) for arr in rr]
        assert shoulders[0]<.001
        if mode=='shoulder-control' and cue['phase']==3:
            assert np.allclose(rr[0][-1]['wrist'],rr[1][-1]['wrist'],atol=.001)
        trials.append({'start':cue['start'],'phase':cue['phase'],'wristTravelCm':distance,'rightOverLeft':distance[1]/distance[0],'shoulderTravelCm':shoulders})
    d={'id':profile['id'],'mode':mode,'frames':count,'fps':60,'sourcePose':rig.D['sampleAnimation'],'mesh':rig.D['mesh'],'skeleton':rig.D['skeleton'],'phases':profile['phases'],'animations':sides,'evidence':evidence,'class':'authored native Unreal illustration','trials':trials,'maxEndpointErrorCm':error}
    f=L/'poses'/f"{profile['id']}.json";f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(d,separators=(',',':')),encoding='utf-8')
    return {'id':d['id'],'frames':count,'sameModelScale':[1,1,1],'samePlayback':1,'trials':trials,'poseSha256':hashlib.sha256(f.read_bytes()).hexdigest()}
if __name__=='__main__':
    groups=json.loads(PROFILES.read_text(encoding='utf-8-sig'))
    profiles=next(v for v in groups.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'phases' in v[0])
    report=[]
    for entry in profiles:
        if entry['id'] in IDS:
            report.append(bake(entry));print('Verified pose',entry['id'],flush=True)
    (H/'motion-measurements.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
