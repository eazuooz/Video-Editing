"""Native damage-height and real-weapon collision comparisons."""
import json,numpy as np
from prepare_series import motion,sample,tracks,N,create
from motion import L
from scipy.spatial.transform import Rotation
def main():
    jobs=json.loads((L/'series-study-build-request.json').read_text('utf-8'))
    for job in jobs:
        p=__import__('pathlib').Path(job['file']);d=json.loads(p.read_text('utf-8'))
        if job['key'] in ('A04-weight','A06-timing','A06-ending','A06-control'):
            d.update(weapon=True,weaponAxisInHand=[-.190522,-.123159,.973927])
        if job['key']=='A13-tool':d['handSockets']=['hand_r','hand_l']
        p.write_text(json.dumps(d,separators=(',',':')),'utf-8')
    high=motion('am_Ready_Fight_01_Knockdown_A');low=motion('am_Ready_Fight_02_Kickdown_A');rows=[];evidence=[]
    for i,m in enumerate((high,low)):
        poses=[sample(m,(21.4 if not i else 8.6)+np.clip((f-12)/60,0,2.5)) for f in range(N)]
        rows.append(dict(mesh=m.data['sourceMesh'],skeleton=m.data['skeleton'],tracks=tracks(m,poses),location=[-145 if not i else 145,0,0]))
    d=dict(episode='A10',study='height',frames=N,fps=60,mesh=high.data['sourceMesh'],skeleton=high.data['skeleton'],sourceClip=[high.data['sourceClip'],low.data['sourceClip']],animations=rows,cameraWidth=690,cameraHeight=65,yaw=-65,sourceModified=False,observationFrames=[40,80],changes='Compare the two imported high/low knockdown performances')
    p=L/'studies/A10-height.json';p.write_text(json.dumps(d,separators=(',',':')),'utf-8');jobs.append(dict(key='A10-height',file=str(p)))
    m=motion('AS_Spear_Attack_04');hand=m.names.index('hand_r');axis=np.array([-.190522,-.123159,.973927]);orientation=Rotation.from_euler('z',-65,degrees=True)
    def pose(f):return sample(m,np.interp(f,[0,17,32,60,110,179],[1.1,1.55,1.9,3.4,5.1,5.1]))
    def segment(p,side):
        w,q=m.world(p);v=Rotation.from_quat(q[hand]).apply(axis);offset=np.array([-145 if not side else 145,0,0])
        return orientation.apply(w[hand]+v*6)+offset,orientation.apply(w[hand]+v*91)+offset
    for key in ('range','path','overhead','active'):
        rows=[];traces=[];targets=[]
        for side in (0,1):
            poses=[pose(f) for f in range(N)];a,b=segment(poses[32],side);delta=b-a
            normal=np.cross(delta,[0,0,1]);normal/=np.linalg.norm(normal)
            target=a+.7*delta+(normal*13 if key=='range' else 0);targets.append(target.tolist());trace=[]
            for f,p in enumerate(poses):
                a,b=segment(p,side);v=b-a;near=a+np.clip(np.dot(target-a,v)/np.dot(v,v),0,1)*v
                distance=float(np.linalg.norm(near-target));radius=(1.5 if not side else 10) if key=='range' else 5
                active=(17<=f<21 if not side else 32<=f<36) if key=='active' else 17<=f<60
                trace.append(dict(start=a.tolist(),end=b.tolist(),target=target.tolist(),distance=distance,radius=radius,hurt=8,enabled=active,hit=active and distance<=radius+8))
            rows.append(dict(tracks=tracks(m,poses),location=[-145 if not side else 145,0,0]));traces.append(trace)
        d=dict(episode='A16',study=key,frames=N,fps=60,mesh=m.data['sourceMesh'],skeleton=m.data['skeleton'],sourceClip=m.data['sourceClip'],animations=rows,cameraWidth=720,cameraHeight=100,yaw=-65,sourceModified=False,observationFrames=[18,34],changes='Genuine spear swing with authored capsule/radius/active-window comparison',weapon=True,weaponAxisInHand=axis.tolist(),sphereTargets=targets,targetRadius=8,collisionEvidence=traces)
        if key=='overhead':d['cameraView']='top'
        p=L/'studies'/('A16-'+key+'.json');p.write_text(json.dumps(d,separators=(',',':')),'utf-8');jobs.append(dict(key='A16-'+key,file=str(p)))
    (L/'series-study-build-request.json').write_text(json.dumps(jobs,indent=2),'utf-8')
    print('Complete native batch studies',len(jobs),flush=True)
if __name__=='__main__':main()
