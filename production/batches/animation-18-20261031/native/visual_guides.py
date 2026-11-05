"""Speech-matched visual evidence on the native test stage. Commercial footage never enters here."""
from pathlib import Path
import json,math,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from functools import lru_cache
@lru_cache(None)
def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size)
def read(path):
    return json.loads(path.read_text('utf-8-sig'))
MINT='#71CDB2';GOLD='#FFCA72';RED='#E67565';BLUE='#8ED4FF';WHITE='#F2F3E8';DARK='#172721'
def label(draw,x,y,text,size=26,colour=WHITE):
    draw.text((x,y),text,font=font(size),fill=colour,stroke_width=2,stroke_fill=DARK)
def panel(draw,x,y,w,h):
    draw.rounded_rectangle((x,y,x+w,y+h),radius=10,fill=DARK,outline='#435D50',width=2)
def dot(draw,p,r,color):
    x,y=p;draw.ellipse((x-r,y-r,x+r,y+r),outline=color,width=4)
def ease(x):
    x=float(np.clip(x,0,1));return x*x*(3-2*x)
def project(point,top=False,width=500):
    x,y,z=point
    if top:
        up=-math.sin(math.radians(88))*(y-35)+math.cos(math.radians(88))*(z-720)
    else:up=z-85
    return (round(960+x*1920/width),round(540-up*1920/width))
def joint(point,side,yaw=-73,width=500):
    a=math.radians(yaw);x,y,z=point
    return project([x*math.cos(a)-y*math.sin(a)+(-125,125)[side],x*math.sin(a)+y*math.cos(a),z],width=width)
def progressdraw(draw,frame,key,side):
    # The legs are the evidence. Place timing controls in the empty outer edge of each view.
    x=45+side*960
    panel(draw,x,280,300,180)
    if key=='guard':
        r=ease((frame-8)/30)*side;theta=(frame-8)*math.pi/65
        cx,cy=x+68,362;draw.ellipse((cx-47,cy-47,cx+47,cy+47),outline='#8C9C94',width=3)
        px=cx+round(43*r*math.cos(theta));py=cy-round(43*r*math.sin(theta))
        draw.line((cx,cy,px,py),fill=MINT,width=5);dot(draw,(px,py),6,WHITE);label(draw,x+128,341,f'기울기 {r:.2f}',25);return
    length=((1,14) if key=='blend' else (6,24))[side]
    w=ease((frame-18)/length)
    label(draw,x+12,293,'공격',24,GOLD);label(draw,x+12,339,'걷기',24,MINT)
    left=x+85;right=x+282;start=left+(right-left)*18/70
    finish=left+(right-left)*(18+length)/70
    draw.line((left,315,finish,315),fill=GOLD,width=9)
    draw.line((start,360,right,360),fill=MINT,width=9)
    px=left+round((right-left)*min(70,frame)/70);draw.line((px,300,px,374),fill=WHITE,width=3)
    label(draw,x+15,400,f'걷기 가중치  {w:.2f}',25)
def compose(ep,key,h,l,v,encoder):
    needed={'A10':('recoil','root'),'A11':('kick','returning'),'A12':('expression','mouth'),
            'A14':('blend','duration','guard','slope'),'A15':('scale','count'),
            'A16':('range','path','active'),'A17':('fkik','hint'),'A18':('head','curves','gaze','wrist')}
    if key not in needed.get(ep,()):return l/(key+'.mp4')
    motion=read(h/'motion-evidence.json') if ep in ('A10','A11','A14','A17') else {}
    collision=read(h/'collision-samples.json') if ep=='A16' else {}
    degrees=read(h/'degrees-by-frame.json') if ep=='A18' else {}
    directory=l/'frames'/key;frames=sorted(directory.glob('*.png'));assert len(frames)==120
    dst=v/(key+'-measured.mp4');size=(1920,1080)
    with (l/(key+'-guide-encode.log')).open('wb') as log:
        proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0','-an',*encoder,str(dst)],stdin=subprocess.PIPE,stderr=log)
        for n,frame in enumerate(frames):
            im=Image.open(frame).convert('RGB');draw=ImageDraw.Draw(im)
            if ep=='A10' and key=='recoil':
                if 10<=n<31:
                    # Show edges of the actual starting and arrival poses, faint enough to keep the current pose legible.
                    from scipy.ndimage import binary_erosion
                    pixels=np.asarray(im).copy()
                    for j,c in ((9,(223,171,106)),(31,(91,165,148))):
                        a=np.asarray(Image.open(frames[j]).convert('RGB')).astype(np.int16)
                        region=(a[:,:,0]-a[:,:,1]>19)&(a[:,:,1]>a[:,:,2]+8)&(a[:,:,0]>90)
                        edge=region^binary_erosion(region,iterations=3)
                        pixels[edge]=(.46*pixels[edge]+.54*np.array(c)).astype('uint8')
                    im=Image.fromarray(pixels);draw=ImageDraw.Draw(im);label(draw,67,735,'실제 시작·도착 자세의 윤곽',27)
            if ep=='A10' and key=='root':
                for side in range(2):
                    v0=ease((n-11)/6)*(1-ease((n-46)/30));base=joint((0,0,2),side)
                    advanced=joint((0,37*v0*side,2),side);dot(draw,base,13,GOLD);dot(draw,advanced,15,MINT)
                    if base!=advanced:draw.line([base,advanced],fill=MINT,width=5)
                    label(draw,advanced[0]-28,advanced[1]-58,'루트',23)
            if ep=='A11' and key=='kick':
                for i in range(2):
                    x=(56,1008)[i];panel(draw,x,262,230,134)
                    label(draw,x+14,268,'14 → 22 F',27);label(draw,x+14,308,f'현재 {n} F',23)
                    for j in range(9):
                        u=j/8;pos=u if not i else max(0,(u-.625)/.375)
                        px=x+18+round(194*pos);dot(draw,(px,371),5,GOLD if j==min(8,max(0,n-14)) else '#96A49C')
                    if 14<=n<=22:
                        p=joint(motion[key][i][n]['foot_r'],i,-65,505)
                        dot(draw,p,14,GOLD if not i else MINT)
            if ep=='A11' and key=='returning':
                for i in range(2):
                    trace=motion[key][i]
                    for lo,hi,color in ((11,26,GOLD),(30,57,MINT)):
                        pts=[joint(trace[k]['hand_r'],i,-65,505) for k in range(lo,min(n,hi)+1)]
                        if len(pts)>1:draw.line(pts,fill=color,width=6)
                    label(draw,95+950*i,718,'나갈 때',25,GOLD);label(draw,230+950*i,718,'돌아올 때',25,MINT)
            if ep=='A12' and 10<=n<30:
                # Retouch is a drawing over the observed target feature in the stationary left comparison, not a measured rig value.
                cx=960-23*1920/96;px=round(cx);s=1920/96
                if key=='mouth':
                    cy=round(540-(169-172)*s)
                    draw.arc((px-58,cy-9,px+58,cy+51),0,180,fill=GOLD,width=5)
                else:
                    for sign in (-1,1):
                        ex=round(cx+sign*3.1*s);ey=round(540-(176.7-172)*s)
                        draw.arc((ex-33,ey-21,ex+33,ey+15),185,355,fill=GOLD,width=5)
                label(draw,85,726,'수정 스케치',26,GOLD)
            if ep=='A14':
                for i in range(2):
                    if key=='slope':
                        pos=joint(motion[key][i][n]['foot_l'],i,-72);dot(draw,pos,16,MINT if i else GOLD)
                    else:progressdraw(draw,n,key,i)
            if ep=='A15' and key=='scale':
                # The wide study plays the identical authored hand pose at the same frame.
                with Image.open(l/'frames/count'/frame.name) as wide:
                    im.paste(wide.crop((960,0,1920,1080)),(960,0))
            if ep=='A15' and key=='count':
                # Four simultaneous instances of the same authored character image make the arithmetic visible.
                tile=im.crop((970,135,1900,875)).resize((325,259),Image.Resampling.LANCZOS)
                # Rebuild the entire right panel from an empty strip of the same stage.
                # Otherwise the full-sized actor's original feet remain beneath the four figures.
                strip=im.crop((908,0,960,1080))
                for x in range(960,1920,52):
                    im.paste(strip,(x,0))
                for j in range(4):
                    im.paste(tile,(1030+413*(j%2),170+259*(j//2)))
                panel(draw,72,707,765,75);label(draw,93,720,'10개 × 양손 × 1명  =  20개',29)
                panel(draw,1007,707,799,75);label(draw,1024,720,'10개 × 양손 × 4명  =  80개',29)
            if ep=='A16':
                if key=='path':
                    topfile=l/'frames/overhead'/frame.name
                    im.paste(Image.open(topfile).convert('RGB').crop((960,0,1920,1080)),(960,0));draw=ImageDraw.Draw(im)
                for i in range(2):
                    top=(key=='path' and i==1);track=collision['overhead' if top else key][i][n]
                    a,b,tar=[project(track[f],top) for f in ('start','end','target')]
                    radius=round(track['hurt']*1920/500)
                    dot(draw,tar,radius,MINT)
                    if track['enabled']:draw.line([a,b],fill=RED if track['hit'] else GOLD,width=max(3,round(track['radius']*2.2)))
                    x=80+i*950;panel(draw,x,703,729,70)
                    status='명중' if track['hit'] else '활성 · 미접촉' if track['enabled'] else '판정 꺼짐'
                    label(draw,x+16,716,f'{n} F    {status}',27,RED if track['hit'] else WHITE)
            if ep=='A17':
                # Project the wrist from this exact UE animation and camera, including actor yaw.
                for side in range(2):
                    wx,wy,wz=motion[key][side][n]['hand_r'];yaw=math.radians(-16)
                    px=960+(wx*math.cos(yaw)-wy*math.sin(yaw)+(-79,79)[side])*1920/370
                    py=540-(wz-105)*1920/370
                    dot(draw,(px,py),20,GOLD if side==0 and key=='fkik' else MINT)
                    label(draw,round(px)+25,round(py)-36,'손목',22)
            if ep=='A18' and key=='wrist':
                with Image.open(l/'frames/wristIsolated'/frame.name) as isolated:
                    im.paste(isolated.crop((960,0,1920,1080)),(960,0))
            if ep=='A18' and key in ('head','curves','gaze'):
                for i in range(2):
                    x=80+i*950;panel(draw,x,651,724,145)
                    yaw,nod,tilt,eye=degrees[key][i][n]
                    if key=='gaze':
                        label(draw,x+18,675,f'머리 {yaw:.0f}°   +   눈 {eye:.0f}°',30)
                        label(draw,x+18,735,f'최종 시선 방향  {yaw+eye:.0f}°',25,MINT)
                    else:
                        seq=degrees[key][i][:61]
                        for ix,col in ((0,GOLD),(1,MINT)):
                            pts=[(x+148+8*j,round(762-p[ix]*1.25)) for j,p in enumerate(seq)]
                            draw.line(pts,fill=col,width=4)
                        px=x+148+8*min(n,60);draw.line((px,675,px,774),fill=WHITE,width=3)
                        label(draw,x+14,659,'좌우 회전',24,GOLD);label(draw,x+14,708,'숙임',24,MINT)
            proc.stdin.write(im.tobytes())
        proc.stdin.close();assert proc.wait()==0
    return dst
