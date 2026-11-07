"""One genuine walking step, simultaneous side and front-observer cameras."""
import json,numpy as np
from prepare_series import create,sample
from motion import L
from scipy.spatial.transform import Rotation
def pose(m,side,frame):
    time=np.clip((frame-12)/60,0,.65);p=sample(m,time);i=m.names.index('root')
    original=m.sample(time)['p'][i]-m.sample(0)['p'][i]
    # This explicitly authored travel vector is independent of the body's facing.
    p['p'][i]=Rotation.from_euler('z',-65,degrees=True).inv().apply([original[1],0,0])
    return p
job=create('A13','direction','M_Neutral_Walk_Loop_F',pose,'An actual native-rate walking step, then held for spatial analysis. Travel direction is X; body faces 25 degrees away to demonstrate presentation adjustment.',actorLocations=[[-205,0,0],[85,0,0]],observationFrames=[12,51])
d=json.loads(__import__('pathlib').Path(job['file']).read_text('utf-8'))
d.update(study='observer',cameraWidth=760,cameraLocation=[800,0,595],cameraYaw=180,cameraPitch=-35,actorLocations=[[0,-145,0],[0,145,0]])
p=L/'studies/A13-observer.json';p.write_text(json.dumps(d,separators=(',',':')),'utf-8')
(L/'a13-direction-build-request.json').write_text(json.dumps([job,dict(key='A13-observer',file=str(p))],indent=2),'utf-8')
print('Native two-camera walking study prepared')
