"""Keep geometry demonstrations and replace only the generic fist motion."""
import json,numpy as np
from prepare_series import create,sample,L

def pose(m,side,n):
    t=np.interp(n,[0,12,54,80,130,179],[0,0,.45,.77,1.2,1.2])
    p=sample(m,t)
    if side:
        envelope=max(0.,1.-abs(n-80)/35)
        p['s'][m.names.index('hand_r')]*=1.+.8*envelope
    return p

row=create('A09','fist','AS_ComboHands',pose,'Genuine combat clip; only right hand scale differs, same camera/body/hand position',observationFrames=[54,80])
(L/'a09-study-build-request.json').write_text(json.dumps([row],indent=2),'utf-8')
