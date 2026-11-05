"""Same target and final pose; animate head, clavicle, eye and wrist on independent curves."""
from pathlib import Path
import sys,math,json
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from face_studies import *
def values(key,i,t):
    turn=smooth(t,9 if key!='curves' or not i else 18,50)
    transient=lambda a,b:math.sin(math.pi*smooth(t,a,b))
    nod=10*transient(8 if key!='curves' or not i else 1,50) if i or key=='curves' else 0
    tilt=0
    if key=='tilt':tilt=nod;nod=0
    yaw=60*turn;eye=0
    if key=='gaze':
        nod=0;eye=16*turn*i;yaw=(60-16*i)*turn
    return [round(v,5) for v in (yaw,nod,tilt,eye)]
def sample(key,i,t):
    yaw,nod,tilt,eye=values(key,i,t);p={}
    if key=='wrist':
        a=smooth(t,8,49);b=math.sin(math.pi*a)
        face(p,'hand_r',0,(0,26*i*b,68*a))
        if i:
            face(p,'clavicle_r',1.5*b,(0,6*b,4*b))
            face(p,'upperarm_r',0,(8*b,-7*b,0))
        return p
    face(p,'neck_01',0,(-nod*.35,tilt*.35,yaw*.34))
    face(p,'head',0,(-nod*.65,tilt*.65,yaw*.66))
    for lr in ('L','R'):face(p,lr+'_eye',0,(0,0,eye))
    return p
if __name__=='__main__':
    keys=('head','tilt','wrist','curves','gaze')
    settings={k:dict(cameraWidth=122,cameraHeight=173,yaw=0,actorSpacing=30) for k in keys}
    settings['wrist']=dict(cameraWidth=184,cameraHeight=129,yaw=0,actorLocations=[[10,0,0],[101,0,0]],handSockets=['hand_r','hand_r'])
    author('A18',P,settings,sample)
    curves={key:[[values(key,i,t) for t in range(120)] for i in range(2)] for key in keys}
    (H/'degrees-by-frame.json').write_text(json.dumps(curves,separators=(',',':')),'utf-8')
