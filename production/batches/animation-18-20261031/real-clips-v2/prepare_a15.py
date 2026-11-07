"""Isolate genuine finger poses from the imported valve-grasp animation."""
import json,numpy as np
from prepare_series import create,sample
from motion import L
def pose(m,side,frame):
    base=sample(m,.6);t=min(m.seconds,max(0,(frame-12)/60))
    source=sample(m,t if side else (0 if frame<65 else m.seconds))
    for i,name in enumerate(m.names):
        if name.endswith('_r') and any(name.startswith(f) for f in ('index','middle','ring','pinky','thumb')):
            base['q'][i]=source['q'][i];base['p'][i]=source['p'][i]
    return base
job=create('A15','keys','anim_GrabValve_R',pose,'Actual imported finger tracks: compare two held source poses with continuous finger motion. Hold wrist/body identically to isolate the fingers.',cameraWidth=110,cameraHeight=79,yaw=0,actorLocations=[[9.6,0,0],[59.6,0,0]],observationFrames=[30,90])
(L/'a15-study-build-request.json').write_text(json.dumps([job],indent=2),'utf-8')
print('A15 source finger study prepared')
