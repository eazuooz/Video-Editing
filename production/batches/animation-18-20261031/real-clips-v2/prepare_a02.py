"""Genuine combat for the amplitude passage; preserve the exact separate rig tests."""
import json
from prepare_series import create,sample,amplitude
from motion import L
def pose(m,side,frame):
    t=min(m.seconds,max(0,(frame-12)/60));p=sample(m,t)
    return amplitude(m,p,sample(m,0),1.8 if side else 1.,('spine','clavicle'))
job=create('A02','combat','AS_ComboHands',pose,'Genuine combat; 1.0/1.8 rotation amplitude of spine and clavicle relative to the first source pose. Mesh scale, timing and camera unchanged.',observationFrames=[32,58])
(L/'a02-study-build-request.json').write_text(json.dumps([job],indent=2),'utf-8')
print('A02 native combat comparison prepared')
