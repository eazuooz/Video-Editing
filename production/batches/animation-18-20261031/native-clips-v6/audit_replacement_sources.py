"""Validate the unchanged native side reused from earlier engine captures."""
import sys
import numpy as np

from prepare import BATCH,WORK,read,save
from audit_native_bases import check_rotation
sys.path.insert(0,str(BATCH/'real-clips-v2'))
from motion import Motion,L


def main():
    checks=[]
    for ep,keys in {'A05':['impact','plane','top','twist'],'A07':['gesture'],
                    'A08':['flow','edge'],'A10':['recoil']}.items():
        for key in keys:
            definition=read(L/'studies'/(ep+'-'+key+'.json'))
            motion=Motion(definition['sourceClip'].split('/')[-1])
            for f in range(180):
                if ep=='A05':
                    t=min(1.05,max(0,(f-12)/90))
                    if key=='impact':t=min(t,.77)
                elif ep in ('A07','A08'):
                    t=min(motion.seconds if ep=='A08' else 2.5,max(0,(f-12)/60))
                else:t=21.4+float(np.clip((f-12)/60,0,2.5))
                check_rotation(definition,1,f,motion,t)
            checks.append({'episode':ep,'key':key,'sourceClip':definition['sourceClip'],
                           'nativeSide':1,'rotationFramesChecked':180,
                           'rootTranslation': 'In-place extraction in the saved comparison capture',
                           'manualJointRotationsAdopted':False})
    save(WORK/'replacement-native-source-audit.json',{'checks':checks,'humanReviewed':False,
         'rule':'Use only the verified unchanged side; do not reuse hand-posed comparison variants.'})
    print('Verified unchanged source motion for',len(checks),'replacement inputs.',flush=True)


if __name__=='__main__':main()
