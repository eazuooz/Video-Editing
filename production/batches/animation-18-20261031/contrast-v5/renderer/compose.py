"""1920x1080 CPU compositor. Actual poses first, an explanatory guide second.

frame(episode, key, source_frame, mode='compare') returns a PIL RGB image.
No UI, network, GPU, audio, source edits or A03 access. Pixel guides use exactly
the saved camera and bone tracks. Their interpretation is editorial, not CV.
"""
from pathlib import Path
from functools import lru_cache
import math,argparse,json
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from sources import *
from config import EPISODES,OVERRIDES
from scipy.ndimage import binary_closing,binary_fill_holes,binary_erosion
BG='#080c0a';WHITE='#f3f5ef';YELLOW='#f2d787';TEAL='#257d78';RED='#cb392f';GREEN='#247343';BLUE='#2666b2';MUTED='#abb9af'
@lru_cache(None)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size)
def txt(d,xy,s,size=44,c=WHITE,maxwidth=None):
    while maxwidth and d.textlength(s,font=font(size))>maxwidth and size>30:size-=1
    d.text(xy,s,font=font(size),fill=c,anchor='lt')
def line(d,pts,color,width=6):
    if len(pts)<2:return
    pts=[tuple(map(float,p)) for p in pts]
    d.line(pts,fill='#0e241d',width=width+4,joint='curve');d.line(pts,fill=color,width=width,joint='curve')
def ring(d,p,c,r=11):
    x,y=p;d.ellipse((x-r,y-r,x+r,y+r),outline='#13261e',width=7);d.ellipse((x-r,y-r,x+r,y+r),outline=c,width=4)
def arrow(d,a,b,c,w=6):
    a=np.array(a);b=np.array(b);v=b-a
    if np.linalg.norm(v)<1:return
    v/=np.linalg.norm(v);perp=np.array([-v[1],v[0]])
    line(d,[a,b],c,w);d.polygon([tuple(b),tuple(b-18*v+9*perp),tuple(b-18*v-9*perp)],fill=c)

def contract(ep,key):
    if ep+'-'+key in OVERRIDES:
        heading,labels,samples,phases,guide,kind=OVERRIDES[ep+'-'+key]
    else:
        visual=read(project(ep)/'production/series-v1/visual-plan.json')
        heading=EPISODES[ep][0];labels=visual['studyLabels'][key]
        n=source(ep,key)['definition']['frames'];samples=[min(n-1,i) for i in (8,40,70)]
        phases=['처음 상태','변화 중','결과 상태'];guide='none';kind='authored-diagram'
    return dict(heading=heading,labels=labels,samples=samples,phases=phases,guide=guide,comparisonKind=kind)

def raw(ep,key,n,side):
    # These are separately rendered camera / isolation plates of the same instant.
    alternate={('A13','direction',1):'observer',('A16','path',1):'overhead',('A18','wrist',1):'wristIsolated'}
    use=alternate.get((ep,key,side),key)
    return image(ep,use,n).copy(),use

def guide_plate(ep,key,n,side,enabled=True):
    im,use=raw(ep,key,n,side)
    c=contract(ep,key);guide=c['guide'];s=source(ep,use);d=s['definition'];pen=ImageDraw.Draw(im)
    if guide=='silhouette'and side==1:
        a=np.array(im);region=a[:,960:];mask=region.mean(axis=2)<155
        mask=binary_fill_holes(binary_closing(mask,iterations=4));lab,count=components(mask);sizes=np.bincount(lab.ravel());sizes[0]=0
        keep=lab==sizes.argmax();region[keep]=[22,33,27];im=Image.fromarray(a);pen=ImageDraw.Draw(im)
    if not enabled:return im
    w=points(ep,use,n,side);col=TEAL if side==0 else RED
    def pt(name):return projected(d,w[name],side)
    def chain(names,color=col):
        names=[name for name in names if name in w]
        if len(names)>1:line(pen,[pt(name) for name in names],color)
        for name in names:ring(pen,pt(name),color,8)
    def trail(bone,color='#c49a24',start=None,end=None):
        lo=max(0,n-32) if start is None else start;hi=n if end is None else end;pts=[]
        for j in range(lo,hi+1,2):
            q=points(ep,use,j,side)
            if bone in q:pts.append(projected(d,q[bone],side))
        line(pen,pts,color,5)
    if guide in ('arm','hands','posture','foot','ik','fingers'):
        if guide=='foot':chain(['thigh_r','calf_r','foot_r']);trail('foot_r')
        elif guide=='posture':chain(['head','neck_01','spine_03','pelvis']);chain(['upperarm_l','upperarm_r'],BLUE)
        elif guide=='fingers':
            for finger in ('thumb','index'):chain([f'{finger}_{i:02}_r'for i in (1,2,3)],col)
            if 'hand_r' in w:ring(pen,pt('hand_r'),BLUE,14)
            if ep=='A15' and key=='keys':
                first=points(ep,use,0,side)
                for finger in ('thumb','index'):
                    names=[f'{finger}_{i:02}_r'for i in (1,2,3)]
                    line(pen,[projected(d,first[a],side)for a in names if a in first],BLUE,3)
        else:
            chain(['clavicle_r','upperarm_r','lowerarm_r','hand_r']);trail('hand_r')
            if guide in ('arm','hands'):chain(['clavicle_l','upperarm_l','lowerarm_l','hand_l'],col)
        # Only the previous actual pose's relevant joint chain, not an invented silhouette.
        prev=max(0,int(n)-14);pw=points(ep,use,prev,side)
        names=['upperarm_r','lowerarm_r','hand_r'] if guide!='foot' else ['thigh_r','calf_r','foot_r']
        names=[a for a in names if a in pw]
        if len(names)>1:line(pen,[projected(d,pw[a],side)for a in names],BLUE,3)
        if guide=='ik' and 'hand_r' in w:
            ring(pen,pt('hand_r'),GREEN,21)
            if key=='hint':chain(['upperarm_r','lowerarm_r','hand_r'],col)
    if guide=='support':
        for f in ('foot_r','foot_l'):
            if f in w:
                p=pt(f);line(pen,[p+[-20,17],p+[20,17]],GREEN,7);ring(pen,p,GREEN,10)
        if 'pelvis' in w:chain(['head','pelvis'],BLUE)
        if not w and ep=='A01':
            # Visible silhouette bounds, not an invented support force or bone.
            a=np.array(im)[:,side*960:(side+1)*960].astype('int16')
            mask=(a[:,:,0]>a[:,:,1]+22)&(a[:,:,1]>a[:,:,2]+12)&(a[:,:,0]>120)
            ys,xs=np.nonzero(mask)
            if len(xs)>100:
                x0,x1=int(np.quantile(xs,.02))+960*side,int(np.quantile(xs,.98))+960*side
                y0,y1=int(np.quantile(ys,.01)),int(np.quantile(ys,.99))
                if key=='walk':line(pen,[(x0-20,y0-12),(x1+20,y0-12)],BLUE,5)
                else:line(pen,[(x0,y1-8),(x0,y1+10),(x1,y1+10),(x1,y1-8)],GREEN,5)
    if guide=='root' and 'pelvis' in w:
        trail('pelvis');ring(pen,pt('pelvis'),col,13)
        for foot in ('foot_r','foot_l'):
            if foot in w:ring(pen,pt(foot),GREEN,10)
    if guide in ('face','mouth'):
        names=['C_jaw','C_lip_upper_mid','C_lip_lower_mid'] if guide=='mouth' else ['L_brow_mid','R_brow_mid','L_eye_lid_upper_mid','R_eye_lid_upper_mid']
        for name in names:
            if name in w:ring(pen,pt(name),col,12)
    if guide=='gaze':
        # The authoring curves rotate about world Z. A skeleton's local X is
        # NOT assumed to be an eye-forward axis. Project the recorded control
        # direction from the actual eye locations, with actor yaw applied once.
        deg=read(project(ep)/'production/series-v1/degrees-by-frame.json')[key][side][n]
        yaw,_,_,eye=deg
        for name,angle,color in (('C_nose_bridge',yaw,BLUE),('L_eye',yaw+eye,col),('R_eye',yaw+eye,col)):
            if name in w:
                p=w[name];direction=Rotation.from_euler('z',angle,degrees=True).apply([0,14,0])
                arrow(pen,projected(d,p,side),projected(d,p+direction,side),color,4)
    if guide=='curves':
        # Trace a real facial point; do not invent a measured gaze axis.
        name='C_nose_bridge';initial=points(ep,use,9,side)
        if name in w and name in initial:
            a=projected(d,initial[name],side);b=pt(name)
            ring(pen,a,BLUE,14);trail(name,start=9);ring(pen,b,col,14)
            arrow(pen,a,b,col,4)
    if guide=='collision':
        collision=d['collisionEvidence'][side][min(n,d['frames']-1)]
        a,b,target=[projected(d,collision[k],side,True)for k in ('start','end','target')]
        scale=1920/d['cameraWidth'];r=max(5,collision['hurt']*scale)
        ring(pen,target,GREEN,r)
        if collision['enabled']:line(pen,[a,b],RED if collision['hit'] else '#b58217',max(5,round(2*collision['radius']*scale)))
    return im

def paste_panel(out,ep,key,n,side,box,guides=True,crop=None,scale_factor=1):
    plate=guide_plate(ep,key,n,side,guides)
    crop=crop or bounds(ep,key);x0,y0,x1,y1=crop;offset=panel_offset(ep,key,side);x0+=offset;x1+=offset
    part=plate.crop((x0,y0,x1,y1));x,y,w,h=box
    scale=min(w/part.width,h/part.height)*scale_factor
    dim=(max(1,round(part.width*scale)),max(1,round(part.height*scale)))
    part=part.resize(dim,Image.Resampling.LANCZOS)
    dx=x+(w-part.width)//2;dy=y+(h-part.height)//2;out.paste(part,(dx,dy))
    return (dx,dy,part.width,part.height)

def contextual_strip(im,ep,key,n,c):
    d=ImageDraw.Draw(im);guide=c['guide'];definition=source(ep,key)['definition']
    if guide=='curves':
        deg=read(project(ep)/'production/series-v1/degrees-by-frame.json')[key]
        for side in (0,1):
            x=95+930*side;y=865;seq=deg[side][:61]
            for axis,col,name in ((0,'#e1bb56','좌우'),(2 if key=='tilt' else 1,'#80d2c2','기울임' if key=='tilt' else '숙임')):
                points=[(x+100+i*9,y-v[axis]*1.1)for i,v in enumerate(seq)];line(d,points,col,4)
                txt(d,(x,790 if axis==0 else 835),name,30,col)
            px=x+100+min(n,60)*9;d.line((px,785,px,885),fill=WHITE,width=3)
        return
    if guide=='blend' and key in ('blend','duration'):
        for side in (0,1):
            frames=(1 if side==0 else 14)if key=='blend' else (6 if side==0 else 24)
            u=np.clip((n-42)/frames,0,1);w=u*u*(3-2*u);x=90+930*side
            txt(d,(x,775),'공격',31,'#e1bb56');txt(d,(x,825),'걷기',31,'#80d2c2')
            for y,width,col in ((798,1-w,'#e1bb56'),(849,w,'#80d2c2')):
                d.line((x+120,y,x+720,y),fill='#39463e',width=12);d.line((x+120,y,x+120+600*float(width),y),fill=col,width=12)
            txt(d,(x+745,782),f'{1-w:.2f}',30);txt(d,(x+745,832),f'{w:.2f}',30)
        return
    if guide=='collision':
        for side in (0,1):
            use='overhead'if key=='path'and side else key;q=source(ep,use)['definition']['collisionEvidence'][side][n]
            text='명중'if q['hit']else'활성 · 미접촉'if q['enabled']else'판정 꺼짐'
            txt(d,(85+930*side,815),text,43,'#ff9f95'if q['hit']else WHITE)
        return
    if ep=='A06' and key=='control':
        clock=max(0,n-12)
        for side,threshold in ((0,60),(1,42)):
            txt(d,(80+930*side,810),'다음 행동 가능'if clock>=threshold else'후속 동작 중 · 입력 대기',40,'#a4d987'if clock>=threshold else WHITE)
        return
    txt(d,(80,825),EPISODES[ep][1],40,WHITE,1760)

def frame(ep,key,source_frame,mode='compare',pass_index=None,caption=None,legend=False):
    assert ep in EPISODES and ep!='A03'
    s=source(ep,key);n=min(s['definition']['frames']-1,max(0,int(source_frame)))
    c=contract(ep,key)
    if mode=='screen-size':c={**c,'heading':'같은 동작, 화면 크기만 변경','labels':['큰 화면에서 관찰','작은 화면에서 관찰'],'guide':'distance'}
    im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
    txt(d,(64,40),c['heading'],64,YELLOW,1550)
    txt(d,(64,112),'UE 실제 시연'if s['kind'].startswith('actual-UE')else'설명용 도식',30,MUTED)
    txt(d,(1620,58),'단계 비교'if mode=='stages'else'1× 관찰'if mode=='native'else'느린 분석',32,WHITE)
    if mode=='stages':
        # Three different actual instants, not three copies of the same current pose.
        width=(1810-30*(len(c['samples'])-1))//len(c['samples'])
        for j,(sample,label) in enumerate(zip(c['samples'],c['phases'])):
            x=55+j*(width+30);col=('#81cfc5','#f2d787','#f18b81','#a4d987')[j]
            txt(d,(x,165),label,45,col,width)
            side=0 if ep=='A16'and key=='active'and j==0 else 1
            paste_panel(im,ep,key,sample,side,(x,227,width,545),True)
            d=ImageDraw.Draw(im);d.line((x,796,x+width,796),fill=col,width=7)
            txt(d,(x,821),f'시연 {sample}F',32,MUTED)
        # The phase labels and actual frame indices already convey this relation.
        # Keep the fixed caption-safe area clear; no redundant footer at y880.
    elif c['guide']=='distance':
        # The comparison is screen occupancy, explicitly not altered animation.
        use='near'if ep=='A07'else key
        for side,x in enumerate((55,985)):
            txt(d,(x,165),c['labels'][side],44,'#81cfc5'if not side else'#f18b81',875)
            paste_panel(im,ep,use,n,0,(x,220,875,555),False,scale_factor=1 if side==0 else .38)
        if ep=='A02':txt(ImageDraw.Draw(im),(80,825),'동작과 자세는 동일 · 화면에서 차지하는 크기만 변경',40,WHITE,1760)
        else:contextual_strip(im,ep,key,n,c)
    else:
        for side,x in enumerate((55,985)):
            txt(d,(x,165),c['labels'][side],44,'#81cfc5'if not side else'#f18b81',875)
            actualside=1 if ep=='A05'and key=='impact'else side
            actualn=max(0,n-1)if ep=='A05'and key=='impact'and side==0 else n
            paste_panel(im,ep,key,actualn,actualside,(x,220,875,540),mode!='native')
        contextual_strip(im,ep,key,n,c)
    if pass_index:
        d=ImageDraw.Draw(im);txt(d,(1530,873),f'기본 속도 {pass_index}/3',29,MUTED)
    if legend and mode!='native':
        d=ImageDraw.Draw(im)
        for x,color,label in ((500,'#f18b81','현재 관절'),(830,'#75a7ed','이전 자세'),(1160,'#f2d787','이동 경로')):
            d.line((x,132,x+38,132),fill=color,width=5);txt(d,(x+53,112),label,30,WHITE)
    # Bottom 920..1079 is reserved for the unchanged final subtitle compositor.
    if caption:
        d=ImageDraw.Draw(im);bb=d.textbbox((0,0),caption,font=font(48));width=bb[2]-bb[0]+56
        d.rectangle((960-width/2,928,960+width/2,1024),fill='#f8f8f4')
        d.text((960,953),caption,font=font(48),anchor='mt',fill='#183e31')
    return im

def preview(ep,key,n,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);receipt=[]
    for mode in ('compare','stages'):
        im=frame(ep,key,n,mode,caption='같은 시간에서 달라진 자세를 확인해 보세요.',legend=mode=='compare')
        f=out/f'{ep}-{key}-{mode}.png';im.save(f);im.resize((375,211),Image.Resampling.LANCZOS).save(out/(f.stem+'-375.png'))
        receipt.append(dict(file=str(f),sha256=sha(f),mode=mode,sourceFrame=n))
    (out/f'{ep}-{key}.json').write_text(json.dumps({'source':input_receipt(ep,key),'contract':contract(ep,key),'samples':receipt,'actualCaptionFromMaster':False,'placeholderCaptionUsedForClearance':True,'humanReview':False},ensure_ascii=False,indent=2),'utf8')
    return receipt
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--episode',required=True);ap.add_argument('--key',required=True);ap.add_argument('--frame',type=int,default=50)
    ap.add_argument('--out',default=str(B/'local/contrast-v5/renderer-previews'));a=ap.parse_args();print(preview(a.episode,a.key,a.frame,a.out))
