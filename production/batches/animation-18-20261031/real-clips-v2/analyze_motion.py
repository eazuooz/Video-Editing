"""Measure source motion only to locate useful inspection intervals, never game statistics."""
import json,numpy as np
from motion import Motion,L
from scipy.spatial.transform import Rotation
def worlds(m):
    p=np.zeros_like(m.p);q=np.zeros_like(m.q)
    for i,parent in enumerate(m.parents):
        if parent<0:p[:,i]=0;q[:,i]=m.q[:,i]
        else:
            rotation=Rotation.from_quat(q[:,parent]);p[:,i]=p[:,parent]+rotation.apply(m.p[:,i]);q[:,i]=(rotation*Rotation.from_quat(m.q[:,i])).as_quat()
    return p,q
def main():
    result={}
    for f in (L/'source-motion').glob('*.gz'):
        key=f.name[:-8];m=Motion(key);p,q=worlds(m);joints={}
        for bone in ('hand_r','hand_l','foot_r','head','pelvis'):
            i=m.names.index(bone);speed=np.linalg.norm(np.diff(p[:,i],axis=0),axis=1)*m.rate
            peak=int(np.argmax(speed));joints[bone]={'speedPeakSeconds':round(peak/m.rate,4),'maxSpeedCmS':round(float(speed[peak]),2),'zMinMax':p[:,i,2][[np.argmin(p[:,i,2]),np.argmax(p[:,i,2])]].tolist()}
        result[key]={'seconds':m.seconds,'joints':joints}
        print(key,round(m.seconds,2),'hand',joints['hand_r']['speedPeakSeconds'],'head',joints['head']['speedPeakSeconds'],'foot',joints['foot_r']['speedPeakSeconds'],flush=True)
    (L/'source-motion-analysis.json').write_text(json.dumps(result,indent=2),'utf-8')
if __name__=='__main__':main()
