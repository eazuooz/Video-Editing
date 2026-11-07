"""Sample the exported genuine motion; local edits remain explicit and reversible."""
from pathlib import Path
import gzip,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'local/real-clips-v2/python-deps'))
import numpy as np
from scipy.spatial.transform import Rotation, Slerp

H=Path(__file__).resolve().parent
L=H.parent/'local/real-clips-v2'

class Motion:
    def __init__(self, key):
        self.data=json.load(gzip.open(L/'source-motion'/(key+'.json.gz'),'rt',encoding='utf-8'))
        self.bones=self.data['bones'];self.names=[b['name'] for b in self.bones]
        self.parents=[self.names.index(b['parent']) if b['parent'] in self.names else -1 for b in self.bones]
        self.seconds=self.data['seconds'];self.rate=self.data['sampleFps']
        self.p=np.array([[b['p'] for b in f] for f in self.data['frames']])
        self.q=np.array([[b['q'] for b in f] for f in self.data['frames']])
        self.s=np.array([[b['s'] for b in f] for f in self.data['frames']])

    def sample(self,time):
        x=np.clip(time,0,self.seconds)*self.rate;a=min(int(x),len(self.p)-1);b=min(a+1,len(self.p)-1);t=x-a
        qa=self.q[a];qb=self.q[b].copy();qb[np.sum(qa*qb,axis=1)<0]*=-1
        q=(1-t)*qa+t*qb;q/=np.linalg.norm(q,axis=1)[:,None]
        return {'p':(1-t)*self.p[a]+t*self.p[b],'q':q,'s':(1-t)*self.s[a]+t*self.s[b]}

    def world(self,pose):
        pp=np.zeros_like(pose['p']);qq=np.zeros_like(pose['q'])
        for i,parent in enumerate(self.parents):
            if parent<0:pp[i]=pose['p'][i];qq[i]=pose['q'][i]
            else:
                rot=Rotation.from_quat(qq[parent]);pp[i]=pp[parent]+rot.apply(pose['p'][i]);qq[i]=(rot*Rotation.from_quat(pose['q'][i])).as_quat()
        return pp,qq

def mix(a,b,w):
    q=b['q'].copy();q[np.sum(a['q']*q,axis=1)<0]*=-1
    qq=(1-w)*a['q']+w*q;qq/=np.linalg.norm(qq,axis=1)[:,None]
    return dict(p=(1-w)*a['p']+w*b['p'],q=qq,s=(1-w)*a['s']+w*b['s'])

def save_study(path,motion,poses,settings):
    result=dict(frames=len(poses),fps=60,sourceClip=motion.data['sourceClip'],mesh=motion.data['sourceMesh'],
                skeleton=motion.data['skeleton'],boneNames=motion.names,**settings)
    result['tracks']={name:{k:[pose[k][i].tolist() for pose in poses] for k in ('p','q','s')} for i,name in enumerate(motion.names)}
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,separators=(',',':')),'utf-8')
