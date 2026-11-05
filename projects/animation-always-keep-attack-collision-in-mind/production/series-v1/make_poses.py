"""Compute and compare collision on an actual attached weapon sampled from UE joint space."""
from pathlib import Path
import sys,functools,math,json
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/series-v1'
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import np,rig,Rotation,ease,pitch_torso,arm,export
@functools.lru_cache(maxsize=1536)
def swing(key,i,t):
    p=rig.pose_copy();v=ease((t-10)/25)*(1-ease((t-59)/35))
    sideway=9*(1-ease((t-20)/13)) if key in ('path','overhead') else 0
    pitch_torso(p,-24+49*v,9-15*v)
    arm(p,'r',[8+30*v,21+sideway,7+3*v]);arm(p,'l',[-7,20,-12])
    # Point the cube's long local axis along the authored blade direction.
    a=np.array([.62*np.cos(v*math.pi),1,.65-v]);a/=np.linalg.norm(a)
    q,_=Rotation.align_vectors([a],[[0,0,1]])
    rig.set_world(p,'hand_r',q=q);return p
def world(key,i,t):
    w=rig.fk(swing(key,i,t));ori=Rotation.from_euler('z',-72,degrees=True)
    pos,q=w['hand_r'];base=ori.apply(pos)+[(-125,125)[i],0,0];tip=ori.apply(pos+q.apply([0,0,52]))+[(-125,125)[i],0,0]
    return base,tip
if __name__=='__main__':
    keys=('range','path','overhead','active');profiles={};measure={}
    for k in keys:
        radii=(1.5,10.) if k=='range' else (5.,5.);targets=[];traces=[];hurt=8.
        for side in range(2):
            base,tip=world(k,side,29);target=tip+np.array([0,13 if k=='range' else 3,0])
            if k=='active':
                early=np.mean(world(k,side,18),axis=0);late=np.mean(world(k,side,33),axis=0)
                target=(early+late)/2
                hurt=float(np.linalg.norm(late-early)/2)+1
            targets.append(target.tolist())
            trace=[]
            for t in range(120):
                start,end=world(k,side,t);delta=end-start
                nearest=start+np.clip(np.dot(target-start,delta)/np.dot(delta,delta),0,1)*delta
                distance=np.linalg.norm(nearest-target)
                enabled=(17<=t<21 if side==0 else 32<=t<36) if k=='active' else 10<=t<58
                trace.append(dict(start=start.round(4).tolist(),end=end.round(4).tolist(),target=target.round(4).tolist(),
                                  distance=round(float(distance),3),radius=radii[side],hurt=hurt,enabled=enabled,hit=bool(enabled and distance<=radii[side]+hurt)))
            traces.append(trace)
        profiles[k]=dict(cameraWidth=500,yaw=-72,handSockets=['hand_r','hand_r'],handShape='Cube',handScale=[.06,.025,.52],handOffset=[0,0,26],
                         sphereTargets=targets,targetRadius=hurt)
        if k=='overhead':profiles[k]['cameraView']='top'
        measure[k]=traces
    (H/'collision-samples.json').write_text(json.dumps(measure,separators=(',',':')),'utf-8')
    export('A16',P,{k:lambda i,t,k=k:swing(k,i,t) for k in keys},profiles)
