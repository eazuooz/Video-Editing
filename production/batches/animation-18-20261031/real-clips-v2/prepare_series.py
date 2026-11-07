"""Topic-specific comparisons grounded in the installed motion clips.

Each variation is explicit: time distribution, amplitude, mirroring or clip blending.
Specialised face/finger/IK/shape controls are retained separately rather than replaced
by body mocap that cannot show those quantities.
"""
from pathlib import Path
import json,sys,numpy as np
from functools import lru_cache
from motion import Motion,mix,save_study,L
from scipy.spatial.transform import Rotation
H=Path(__file__).resolve().parent
N=180
@lru_cache(None)
def motion(key):return Motion(key)
def smooth(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)
def sample(m,t,root=True):
    p=m.sample(t)
    if root:p['p'][m.names.index('root')]=[0,0,0]
    return p
def amplitude(m,pose,origin,factor,bones=None):
    out={k:v.copy() for k,v in pose.items()}
    ids=[i for i,n in enumerate(m.names) if (bones is None or any(n.startswith(b) for b in bones)) and n!='root']
    a=Rotation.from_quat(origin['q'][ids]);b=Rotation.from_quat(pose['q'][ids])
    out['q'][ids]=(a*Rotation.from_rotvec((a.inv()*b).as_rotvec()*factor)).as_quat()
    out['p'][ids]=origin['p'][ids]+(pose['p'][ids]-origin['p'][ids])*factor
    return out
def bone_rotation(m,p,bone,xyz):
    i=m.names.index(bone);p['q'][i]=(Rotation.from_quat(p['q'][i])*Rotation.from_euler('xyz',xyz,degrees=True)).as_quat()
def world_rotation(m,p,bone,xyz):
    i=m.names.index(bone);w,q=m.world(p);target=Rotation.from_euler('xyz',xyz,degrees=True)*Rotation.from_quat(q[i]);parent=m.parents[i]
    p['q'][i]=(Rotation.from_quat(q[parent]).inv()*target).as_quat() if parent>=0 else target.as_quat()
def tracks(m,poses):
    return {name:{k:[p[k][i].tolist() for p in poses] for k in ('p','q','s')} for i,name in enumerate(m.names)}
def mapped(m,other,p):
    out=sample(m,0)
    for i,n in enumerate(m.names):
        if n in other.names:
            j=other.names.index(n)
            for k in out:out[k][i]=p[k][j]
    return out
def mirror(m,p):
    # Reflect component-space transforms in the sagittal plane, swapping paired bones.
    wp,wq=m.world(p);reflection=np.diag([-1.,1.,1.]);out={k:v.copy() for k,v in p.items()};worldp=[];worldq=[]
    reference={k:np.array([b['reference'][k] for b in m.bones]) for k in ('p','q','s')}
    rp,rq=m.world(reference)
    for i,name in enumerate(m.names):
        partner=name[:-2]+('_l' if name.endswith('_r') else '_r') if name.endswith(('_l','_r')) else name
        j=m.names.index(partner) if partner in m.names else i
        # Mirrored bones have different local bind axes. Reflect their motion
        # relative to the bind pose, then restore the destination bone's basis.
        delta=(Rotation.from_quat(wq[j])*Rotation.from_quat(rq[j]).inv()).as_matrix()
        worldp.append(reflection@wp[j]);worldq.append(Rotation.from_matrix(reflection@delta@reflection)*Rotation.from_quat(rq[i]))
    for i,parent in enumerate(m.parents):
        if parent<0:out['p'][i]=worldp[i];out['q'][i]=worldq[i].as_quat()
        else:
            out['p'][i]=worldq[parent].inv().apply(worldp[i]-worldp[parent]);out['q'][i]=(worldq[parent].inv()*worldq[i]).as_quat()
    return out

def create(ep,key,source,fn,reason,**settings):
    m=motion(source);rows=[];evidence=[]
    for side in (0,1):
        poses=[];points=[]
        for frame in range(N):
            p=fn(m,side,frame);poses.append(p)
            w,q=m.world(p);points.append({name:w[m.names.index(name)].tolist() for name in ('head','pelvis','hand_r','hand_l','foot_r','foot_l','upperarm_r','upperarm_l')})
        rows.append(dict(tracks=tracks(m,poses),location=[-145 if side==0 else 145,0,0]))
        evidence.append(points)
    data=dict(episode=ep,study=key,frames=N,fps=60,sourceClip=m.data['sourceClip'],mesh=m.data['sourceMesh'],skeleton=m.data['skeleton'],
              animations=rows,cameraWidth=620,cameraHeight=77,yaw=-65,changes=reason,sourceModified=False,
              observationFrames=[42,84],sourcePlayback='source-derived teaching comparison; original assets preserved',motionEvidence=evidence)
    data.update(settings);dest=L/'studies'/(ep+'-'+key+'.json');dest.write_text(json.dumps(data,separators=(',',':')),'utf-8')
    return dict(key=ep+'-'+key,file=str(dest))

def run():
    jobs=[]
    selected=set(sys.argv[1:])
    def add(*a,**k):
        if not selected or a[0]+'-'+a[1] in selected:jobs.append(create(*a,**k))
    combo='AS_ComboHands';kick='AS_RightLegKick2'
    # A04: one observed first punch, with only the approach to its windup retimed.
    def a04(key):
        def f(m,side,n):
            t=max(0,(n-12)/60)
            if key=='anticipation':
                c=max(0,n-12)
                t=.77*((c/12)**(2.2 if not side else .22)) if c<12 else .77+(c-12)/60
            elif key=='jab':t=np.interp(t,[0,.2,.45,.75,2.5],[.45 if not side else 0,.55,.76,1.,1.2])
            elif key=='weight':t=np.interp(t,[0,.35 if not side else 1.1,1.5,2.5],[1.62,3.25,3.65,6.45])
            elif key=='charge':t=0 if not side else min(4.,t*1.6)
            return sample(m,t)
        return f
    for key in ('anticipation','jab'):add('A04',key,combo,a04(key),'Same genuine first punch; both reach the extended striking pose at exactly 12 authored frames',observationFrames=[13,24] if key=='anticipation' else [24,58])
    add('A04','charge','AS_LevitatingFireballCharge2',a04('charge'),'Idle versus observed charging gesture',cameraWidth=680,cameraHeight=100)
    add('A04','weight','AS_Spear_Attack_02',a04('weight'),'Short versus sustained windup of the observed overhead attack',cameraWidth=680,cameraHeight=100)
    # A05: retain the actual body mechanics, isolate the visible arm/torso contributions.
    def a05(key):
        def f(m,side,n):
            t=min(1.05,max(0,(n-12)/90));p=sample(m,t);base=sample(m,0)
            if key=='size' and not side:
                for i,b in enumerate(m.names):
                    if not any(b.startswith(x) for x in ('upperarm_r','lowerarm_r','hand_r','index','middle','ring','pinky','thumb')):p['q'][i]=base['q'][i];p['p'][i]=base['p'][i]
                p=amplitude(m,p,base,.55,('upperarm_r','lowerarm_r','hand_r'))
            if key in ('plane','top') and not side:world_rotation(m,p,'spine_01',[0,0,30*smooth((n-12)/36)])
            if key=='twist' and not side:
                reflected=mirror(m,p)
                for i,b in enumerate(m.names):
                    if b.endswith('_l') and any(x in b for x in ('arm','hand','clavicle')):p['q'][i]=reflected['q'][i]
            if key=='impact':p=sample(m,min(t,.60 if not side else .77))
            return p
        return f
    for key in ('size','plane','top','twist','impact','camera','outline'):
        settings={'observationFrames':[42,81]}
        if key=='top':settings.update(cameraView='top',cameraWidth=620)
        if key in ('plane','top'):settings['yaw']=-95.4554
        if key=='camera':settings.update(sideYaws=[-110,-30])
        add('A05',key,combo,a05(key),'Genuine combat motion; isolate '+key+' variable',**settings)
    # A06: preserve its explicit 60-frame clock, using an actual swing for each comparison.
    def a06(key):
        def f(m,side,n):
            c=np.clip(n-12,0,60);t=np.interp(min(c,15) if key=='timing' and not side else c,[0,15,60],[.45,1.42,2.4]);p=sample(m,t)
            if key=='ending' and not side and c>15:p=mix(p,sample(m,0),smooth((c-15)/8))
            if key=='control' and c>=(42 if side else 60):
                w=motion('MM_Walk_Fwd');p=mapped(m,w,sample(w,((c-(42 if side else 60))/60)%w.seconds))
            return p
        return f
    for key in ('timing','ending','control'):add('A06',key,'AS_Spear_Attack_06',a06(key),'Observed swing; recovery and input transition isolated',observationFrames=[27,58],secondaryClips=[motion('MM_Walk_Fwd').data['sourceClip']] if key=='control' else [])
    # A07: a real startled/excited reaction carries the information-loss comparison.
    def a07(key):
        def f(m,side,n):
            p=sample(m,min(2.5,max(0,(n-12)/60)));base=sample(m,0)
            return amplitude(m,p,base,.22 if key=='gesture' and not side else 1.)
        return f
    for key in ('gesture','near','far'):
        add('A07',key,'am_Stand_React_Excited_01',a07(key),'Same observed reaction; gesture amplitude or camera distance',cameraWidth=620 if key!='far' else 1000,cameraHeight=77 if key!='far' else 150)
    # A08: character-specific resting and sad poses, with the compared controls isolated.
    def a08(key):
        def f(m,side,n):
            t=min(m.seconds,max(0,(n-12)/60));p=sample(m,t)
            if key=='stance' and not side:return mix(p,mirror(m,p),.5)
            if not side:
                reference=sample(m,0)
                for i,b in enumerate(m.names):
                    if key=='flow' and b.startswith(('spine','neck','head')):p['q'][i]=reference['q'][i]
                    if key=='edge' and b.startswith(('clavicle','upperarm','lowerarm')):p['q'][i]=reference['q'][i]
                    if key=='stance' and b.startswith(('pelvis','thigh','calf','foot')):p['q'][i]=reference['q'][i];p['p'][i]=reference['p'][i]
            return p
        return f
    for key in ('flow','edge','stance'):add('A08',key,'am_Stand_Wave_02_LHand' if key=='edge' else 'am_HandsHips_Dance_LookToSide_01_Loop',a08(key),'Actual standing/waving pose; '+key+' control isolated',yaw=-20)
    # A10: source reactions occur late in the performance takes, not at frame zero.
    def a10(key):
        def f(m,side,n):
            t=21.4+np.clip((n-12)/60,0,2.5);p=sample(m,t);origin=sample(m,21.4)
            if key=='recoil' and not side:p=amplitude(m,p,origin,.25)
            if key=='root' and side:
                # Preserve the take's actual ~105 cm root displacement; the
                # left comparison locks that same root at the initial point.
                i=m.names.index('root');p['p'][i]=m.sample(t)['p'][i]-m.sample(21.4)['p'][i]
            if key=='turn' and side:world_rotation(m,p,'spine_01',[0,0,35])
            if key=='recoil' and not side:
                # Rotation isolation must not leave the comparison hovering.
                wp,_=m.world(p);op,_=m.world(origin);feet=[m.names.index('foot_l'),m.names.index('foot_r')]
                p['p'][m.names.index('root')][2]+=min(op[i,2] for i in feet)-min(wp[i,2] for i in feet)
            return p
        return f
    for key in ('recoil','root','turn'):add('A10',key,'am_Ready_Fight_01_Knockdown_A',a10(key),'Actual struck participant; isolate '+key+'; root compares genuine translation with locked root; turn preserves pelvis/legs and changes only upper-torso orientation',cameraWidth=780,cameraHeight=75,observationFrames=[35,85])
    # A11: a kick is finally demonstrated with the imported kicking action.
    def a11(key):
        def f(m,side,n):
            u=np.clip((n-12)/100,0,1)
            if key=='kick':
                if n>20:return sample(m,min(m.seconds,.76+(n-20)/60))
                u=np.clip((n-12)/8,0,1)
                keys=[sample(m,t) for t in (0,.53,.76)];times=[0,.5,1] if not side else [0,.85,1]
                j=0 if u<times[1] else 1
                return mix(keys[j],keys[j+1],np.clip((u-times[j])/(times[j+1]-times[j]),0,1))
            if key=='upper':
                keys=[sample(m,t) for t in (0,.45,.77)];times=[0,.5,1] if not side else [0,.85,1]
                j=0 if u<times[1] else 1
                return mix(keys[j],keys[j+1],np.clip((u-times[j])/(times[j+1]-times[j]),0,1))
            t=np.interp(u,[0,.32,.5,1],[0,.45,.77,1.2])
            if key=='upper' and side:t=np.interp(u,[0,.42,.5,1],[0,.45,.77,1.2])
            if key=='returning' and not side and u>.5:t=np.interp(u,[.5,1],[.77,0])
            return sample(m,t)
        return f
    for key in ('kick','upper','returning'):add('A11',key,kick if key=='kick' else combo,a11(key),'Genuine '+('kick' if key=='kick' else 'combat')+' motion; compare timing/return interpolation',observationFrames=[12,20] if key=='kick' else [55,70])
    # A13: mirror a true walk and an asymmetric held-flashlight pose.
    def a13(key):
        def f(m,side,n):
            p=sample(m,min(m.seconds,(n/60)))
            return mirror(m,p) if side and key in ('mirror','tool') else p
        return f
    for key in ('mirror','tool','direction'):
        add('A13',key,'A_Flashlight_Idle_01_R' if key=='tool' else 'M_Neutral_Walk_Loop_F',a13(key),'Genuine asymmetric motion; component-space sagittal reflection',sideYaws=[-65,65] if key!='direction' else [-65,-65])
    # A14: blend two actual clips with independent duration controls.
    def a14(key):
        def f(m,side,n):
            attack=sample(m,min(.8,n/60));walk=motion('MM_Walk_Fwd');walking=mapped(m,walk,sample(walk,max(0,(n-42)/60)%walk.seconds))
            length=(1 if not side else 14) if key=='blend' else (6 if not side else 24)
            return mix(attack,walking,smooth((n-42)/length))
        return f
    for key in ('blend','duration'):add('A14',key,combo,a14(key),'Actual combat and walk clips; '+key+' controls, both compatible Manny hierarchies',observationFrames=[45,66],secondaryClips=[motion('MM_Walk_Fwd').data['sourceClip']])
    (L/'series-study-build-request.json').write_text(json.dumps(jobs,indent=2),'utf-8')
    print('Prepared distinct genuine-motion studies',len(jobs),flush=True)
if __name__=='__main__':run()
