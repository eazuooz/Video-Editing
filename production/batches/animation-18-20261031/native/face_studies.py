"""Animate the Epic sample's actual face controls in reference-space axes."""
from pathlib import Path
import sys,json
import numpy as np
from scipy.spatial.transform import Rotation
B=Path(__file__).resolve().parent.parent; R=B.parents[2]
REFERENCE=R/'projects/animation-facial-animations/production/local/series-v1/reference-pose.json'
def author(ep,project,settings,evaluate):
    data=json.loads(REFERENCE.read_text('utf-8'));bones=data['bones']
    local=project/'production/local/series-v1';out=local/'poses';out.mkdir(parents=True,exist_ok=True)
    evidence={}
    for key,profile in settings.items():
        clips=[];evidence[key]=[]
        for side in range(2):
            samples=[evaluate(key,side,t) for t in range(121)]
            evidence[key].append(samples)
            names=set(bones)
            tracks={}
            for name in names:
                ref=bones[name];parent=bones.get(ref['parent']);par=Rotation.from_quat(parent['world']['q']) if parent else Rotation.identity()
                r0=Rotation.from_quat(ref['local']['q']);p0=np.array(ref['local']['p'])
                positions=[];rotations=[]
                for pose in samples:
                    delta,angles=pose.get(name,([0,0,0],[0,0,0]))
                    positions.append((p0+par.inv().apply(delta)).round(6).tolist())
                    r=par.inv()*Rotation.from_euler('xyz',angles,degrees=True)*par*r0
                    rotations.append(r.as_quat().round(7).tolist())
                if all(a==positions[0] for a in positions) and all(a==rotations[0] for a in rotations):
                    positions,rotations=positions[:1],rotations[:1]
                tracks[name]=dict(p=positions,q=rotations,s=ref['local']['s'])
            clips.append({'side':('left','right')[side],'tracks':tracks})
        (out/(key+'.json')).write_text(json.dumps(dict(frames=120,animations=clips,**profile),separators=(',',':')),'utf-8')
    (project/'production/series-v1/motion-evidence.json').write_text(json.dumps(evidence,separators=(',',':')),'utf-8')
    (local/'study-job.json').write_text(json.dumps(dict(episode=ep,keys=list(settings),mesh=data['mesh'],skeleton=data['skeleton'])),'utf-8')

def smooth(t,start,end):
    x=min(1,max(0,(t-start)/(end-start)));return x*x*(3-2*x)

def face(p,bone,z=0,xyz=(0,0,0)):
    p[bone]=([0,0,z],list(xyz))
