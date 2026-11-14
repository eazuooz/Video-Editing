"""Pair real animation with explicit principle drawings, without driving a human rig."""
from functools import lru_cache
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance
import numpy as np

from prepare import BATCH, WORK, read
from native_visuals import BG, WHITE, YELLOW, TEAL, RED, GREEN, MUTED, text, paste, layout, legacy_crop, native_crop
import sources


@lru_cache(24)
def game_picture(key, frame):
    path=WORK/'game-banks'/key/f'{min(179,max(0,round(frame))):06d}.png'
    with Image.open(path) as im:
        result=im.convert('RGB')
        return ImageEnhance.Brightness(result).enhance(1.65) if key=='lune-face' else result


@lru_cache(None)
def a08_definition(key):
    return read(BATCH/'local/real-clips-v2/studies'/('A08-'+key+'.json'))


@lru_cache(None)
def a08_files(key):
    files=tuple(sorted((BATCH/'local/real-clips-v2/study-frames'/('A08-'+key)).glob('*.png')))
    assert len(files)>=180
    return files


def original_a08(key, n):
    source_key = 'edge' if key == 'edge' else 'flow'
    files=a08_files(source_key)
    with Image.open(files[min(179,max(0,round(n)))]) as im:
        return im.convert('RGB').crop((1215,20,1800,970))


def source_picture(ep,key,n,side=1,native_rate=False):
    if ep=='A08':
        return game_picture('ringfit',n) if key=='warrior' else original_a08(key,n)
    if ep=='A12':
        return game_picture('acnh-face' if key in ('eyes','distance') else 'lune-face',n)
    if ep=='A18':
        return native_crop('anim_OpeningValve_R',min(79,n if native_rate else n*79/179),1) if key=='wrist' else game_picture('luigi-face',n)
    if ep=='A17':
        return native_crop('anim_GrabValve_R',min(109,n if native_rate else n*109/179),1)
    if ep=='A14':
        if key=='guard':return native_crop('A_Guard_idle',n,0)
        full=sources.source('A01','walk')['definition']['frames']
        return legacy_crop('A01','walk',n%full,0)
    raise ValueError((ep,key))


def arrow(draw,a,b,color=YELLOW):
    draw.line([a,b],fill=color,width=7)
    angle=math.atan2(b[1]-a[1],b[0]-a[0]);r=18
    draw.polygon([b,(b[0]-r*math.cos(angle-.5),b[1]-r*math.sin(angle-.5)),
                     (b[0]-r*math.cos(angle+.5),b[1]-r*math.sin(angle+.5))],fill=color)


def chain(draw,points,color):
    draw.line(points,fill=color,width=10,joint='curve')
    for x,y in points:
        draw.ellipse((x-12,y-12,x+12,y+12),fill=BG,outline=color,width=5)


def arm_diagram(im,key,n):
    d=ImageDraw.Draw(im)
    u=np.clip(n/100,0,1)
    first_angle=math.radians(-25-35*u)
    second_angle=math.radians(70+20*u)
    elbow_delta=np.array([220*math.cos(first_angle),220*math.sin(first_angle)])
    end_delta=elbow_delta+np.array([240*math.cos(first_angle+second_angle),240*math.sin(first_angle+second_angle)])
    if key=='hint':
        end_delta=np.array([360.,-70.])
    for side,x in enumerate((90,1030)):
        shoulder=(x+80,700)
        target=tuple(np.array(shoulder)+end_delta)
        distance=float(np.linalg.norm(end_delta))
        direction=end_delta/distance
        along=(220**2-240**2+distance**2)/(2*distance)
        height=math.sqrt(max(0,220**2-along**2))
        pole=np.array([-direction[1],direction[0]])*(1 if key=='hint' and side else -1)
        elbow=tuple(np.array(shoulder)+direction*along+pole*height)
        if key=='fkik' and side==0:elbow=tuple(np.array(shoulder)+elbow_delta)
        chain(d,[shoulder,elbow,target],TEAL if not side else RED)
        if key=='hint':
            text(d,(x+90,550),'팔꿈치 방향',32,TEAL if not side else RED,650)
        else:
            text(d,(x+90,550),'관절 → 손' if not side else '손 목표 → 관절',35,TEAL if not side else RED,650)
        d.ellipse((target[0]-22,target[1]-22,target[0]+22,target[1]+22),outline=GREEN,width=5)
        text(d,(x+80,841),'어깨 → 팔꿈치 → 손 목표',31,MUTED,790)


def rotation_diagram(im,key,n):
    d=ImageDraw.Draw(im)
    u=np.clip(n/179,0,1)
    for side,cx in enumerate((1180,1610)):
        # These are the declared inputs of the principle drawing, not retail-game values.
        yaw_u=np.clip((u-.18)/.82,0,1) if key=='curves' and side else u
        yaw=math.radians((40 if key=='gaze' and side else 60)*yaw_u)
        pitch=math.radians(10*math.sin(math.pi*u)*(side if key!='curves' else 1)) if key in ('head','wrist','curves') else 0
        if key=='curves' and side:
            pitch=math.radians(10*math.sin(math.pi*min(1,u*1.6)))
        cy=530
        if key=='wrist':
            d.rounded_rectangle((cx-70,cy-80,cx+70,cy+90),radius=30,outline=WHITE,width=6)
            for finger in range(4):
                xx=cx-55+finger*36
                d.line((xx,cy-80,xx,cy-170+abs(finger-1)*15),fill=WHITE,width=8)
            d.line((cx+70,cy-25,cx+120,cy-90),fill=WHITE,width=8)
            d.line((cx-35,cy+90,cx-35,cy+170),fill=WHITE,width=7)
            d.line((cx+35,cy+90,cx+35,cy+170),fill=WHITE,width=7)
        else:
            roll=math.radians(10*math.sin(math.pi*u)) if key=='tilt' and side else 0
            points=[]
            for t in np.linspace(0,2*math.pi,120):
                xx,yy=115*math.cos(t),150*math.sin(t)
                points.append((cx+xx*math.cos(roll)-yy*math.sin(roll),cy+xx*math.sin(roll)+yy*math.cos(roll)))
            d.line(points,fill=WHITE,width=7,joint='curve')
        tip=(cx+140*math.sin(yaw),cy+95*math.sin(pitch))
        if key=='tilt' and side:
            dx,dy=tip[0]-cx,tip[1]-cy
            tip=(cx+dx*math.cos(roll)-dy*math.sin(roll),cy+dx*math.sin(roll)+dy*math.cos(roll))
        arrow(d,(cx,cy),tip,TEAL if not side else RED)
        d.line((cx-160,cy,cx+170,cy),fill='#67756c',width=3)
        d.line((cx,cy-185,cx,cy+190),fill='#67756c',width=3)
        label=('머리 60° · 눈 0°' if not side else '머리 40° · 눈 20°') if key=='gaze' else ('좌우 회전' if not side else '기울임도 함께')
        text(d,(cx-165,300),label,32,TEAL if not side else RED,350)
        if key=='gaze':
            eye=(cx+60*math.sin(yaw),cy-45)
            total=math.radians(60*u)
            arrow(d,eye,(eye[0]+120*math.sin(total),eye[1]-120*math.cos(total)),GREEN)
    if key=='curves':
        for side,cx in enumerate((1180,1610)):
            x0=cx-165;width=340
            for label,base_y,color,fn in (
                ('Yaw (좌우)',744,YELLOW,lambda t:60*(np.clip((t-.18)/.82,0,1) if side else t)),
                ('Pitch (숙임)',824,TEAL,lambda t:10*math.sin(math.pi*(min(1,t*1.6) if side else t)))):
                text(d,(x0,base_y-46),label,26,color,350)
                maximum=60 if label.startswith('Yaw') else 10
                pts=[(x0+i*width/60,base_y-34*fn(i/60)/maximum) for i in range(61)]
                d.line((x0,base_y,x0+width,base_y),fill='#52645a',width=3)
                d.line(pts,fill=color,width=5,joint='curve')
                cursor=x0+width*u
                d.line((cursor,base_y-40,cursor,base_y+4),fill=WHITE,width=3)
        text(d,(1010,871),'가로: 시간 · 세로: 회전값 (도식 설정)',27,MUTED,850)
    else:
        text(d,(1010,775),'축별 회전의 원리 도식',35,YELLOW,850)
        text(d,(1010,834),'도식 설정: 좌우 60° · 중간 변화 10°',30,MUTED,850)


def blend_diagram(im,key,n):
    d=ImageDraw.Draw(im)
    if key=='guard':
        c=(1430,510);r=180;u=np.clip(n/179,0,1)
        if u<1/3:
            angle=(u*3)*math.pi/2;amount=.75
        elif u<2/3:
            angle=math.pi/2;amount=.75-.60*math.sin((u-1/3)*3*math.pi)
        else:
            angle=(1-(u-2/3)*3)*math.pi/2;amount=.75
        d.ellipse((c[0]-r,c[1]-r,c[0]+r,c[1]+r),outline='#748279',width=5)
        for theta,name in ((0,'오른쪽'),(math.pi/2,'아래'),(math.pi,'왼쪽'),(3*math.pi/2,'위')):
            px,py=c[0]+r*math.cos(theta),c[1]+r*math.sin(theta)
            d.ellipse((px-11,py-11,px+11,py+11),fill=BG,outline=TEAL,width=4)
            text(d,(px-42,py-40),name,27,MUTED,130)
        target=(c[0]+r*amount*math.cos(angle),c[1]+r*amount*math.sin(angle))
        arrow(d,c,target,GREEN)
        for y,label,value,color in ((756,'기본 자세',1-amount,YELLOW),(823,'방향 자세',amount,TEAL)):
            text(d,(1080,y-22),label,31,color,220)
            d.line((1310,y,1810,y),fill='#41534a',width=13)
            d.line((1310,y,1310+500*value,y),fill=color,width=13)
    else:
        for side,x in enumerate((1090,1510)):
            ground=lambda xx: 735-(xx-x)*.27
            d.line((x-25,ground(x-25),x+350,ground(x+350)),fill=GREEN,width=9)
            hip=(x+130,455)
            feet=[(x+30,735 if side==0 else ground(x+30)),(x+275,735 if side==0 else ground(x+275))]
            for foot in feet:
                delta=np.array(foot)-np.array(hip)
                distance=float(np.linalg.norm(delta));direction=delta/distance
                along=(180**2-190**2+distance**2)/(2*distance)
                normal=np.array([-direction[1],direction[0]])
                knee=tuple(np.array(hip)+direction*along+normal*math.sqrt(max(0,180**2-along**2)))
                chain(d,[hip,knee,foot],TEAL if not side else RED)
            text(d,(x-15,806),'평지의 발 높이' if not side else '지면에 맞춘 목표',31,TEAL if not side else RED,395)
    text(d,(1100,228),'입력에 따른 자세 가중치' if key=='guard' else '지면에 맞추는 발 목표',39,YELLOW,750)


def draw_special(ep,key,n,mode,counter):
    im=layout(ep,key,mode,counter)
    d=ImageDraw.Draw(im)
    d.rectangle((50,110,1330,155),fill=BG)
    source_label = '실제 게임 · 동작 관찰' if ep in ('A12','A18') or key=='warrior' else '언리얼 · 설치된 애니메이션'
    text(d,(64,119),source_label,30,MUTED)
    if mode=='native':
        paste(im,source_picture(ep,key,n,native_rate=True),(180,188,1560,635))
        text(ImageDraw.Draw(im),(80,838),'동작 전체를 먼저 이어서 봅니다.',39)
        return im
    if ep=='A14' and key=='guard' and mode=='stages':
        text(d,(65,184),'기본 방어 동작',39,TEAL,880)
        paste(im,source_picture(ep,key,n),(65,245,850,520))
        text(d,(1020,204),'입력 → 방향 선택 → 혼합 비중',37,YELLOW,850)
        for j,(label,amount) in enumerate((('기본 자세',0),('방향 입력',.25),('방향 자세 강화',.75))):
            y=330+j*165
            text(d,(1040,y),label,36,(TEAL,YELLOW,GREEN)[j],730)
            d.line((1040,y+76,1800,y+76),fill='#41534a',width=18)
            if amount:d.line((1040,y+76,1040+760*amount,y+76),fill=TEAL,width=18)
            text(d,(1040,y+96),'기본 자세' if amount==0 else '기본 자세 + 방향 자세',27,MUTED,750)
        text(d,(80,842),'기본 동작을 바탕으로 입력에 따른 혼합 관계를 도식으로 봅니다.',36,WHITE)
        return im
    if ep in ('A14','A17','A18') and mode=='stages':
        for j,f in enumerate((0,60,120,179)):
            x=55+j*465
            text(d,(x,174),['처음','변화 시작','변화 중','다음 자세'][j],41,(TEAL,YELLOW,RED,GREEN)[j],425)
            paste(im,source_picture(ep,key,f),(x,236,425,520))
            d.line((x,792,x+425,792),fill=(TEAL,YELLOW,RED,GREEN)[j],width=7)
        text(d,(80,842),'움직임의 시작과 중간, 도달한 모습을 한 화면에서 확인하세요.',37,WHITE)
        return im
    if ep in ('A14','A17','A18'):
        if ep=='A17':
            text(d,(65,184),'완성된 잡기 동작',39,TEAL,850)
            paste(im,source_picture(ep,key,n),(555,174,810,300))
            arm_diagram(im,key,n)
            return im
        text(d,(65,184),'완성된 동작 관찰',39,TEAL,880)
        paste(im,source_picture(ep,key,n), (65,245,850,520))
        if ep=='A14':
            blend_diagram(im,key,n)
        else:
            rotation_diagram(im,key,n)
        return im
    if mode=='stages':
        samples=[0,60,120,179]
        for j,f in enumerate(samples):
            x=55+j*465
            text(d,(x,174),['시작 자세','변화 시작','주요 자세','다음 자세'][j],41,(TEAL,YELLOW,RED,GREEN)[j],425)
            paste(im,source_picture(ep,key,f),(x,236,425,540))
            d.line((x,805,x+425,805),fill=(TEAL,YELLOW,RED,GREEN)[j],width=7)
        return im
    for side,x in enumerate((55,985)):
        lab=['시작 자세','주요 자세'][side]
        if ep=='A12':
            lab=['전체 표정','수정 방향을 그린 그림' if key=='expression' else '관찰할 부위에 주목'][side]
        text(d,(x,174),lab,43,TEAL if not side else RED,875)
        sample=n if side else 0
        if ep=='A12':
            sample=n
        box=paste(im,source_picture(ep,key,sample),(x,239,875,535),.38 if ep=='A12' and key=='distance' and side else 1)
        bx,by,bw,bh=box
        if ep=='A12' and side and key in ('eyes','mouth','expression'):
            pen=ImageDraw.Draw(im)
            # Opaque neutral masks isolate an observed region; they do not deform a face.
            if key=='eyes':
                pen.rectangle((bx,by+bh*.56,bx+bw,by+bh),fill=BG)
            elif key=='mouth':
                pen.rectangle((bx,by,bx+bw,by+bh*.31),fill=BG)
            else:
                pen.rounded_rectangle((bx+bw*.18,by+bh*.10,bx+bw*.84,by+bh*.34),radius=16,outline=RED,width=6)
                for xx in (.35,.67):
                    arrow(pen,(bx+bw*xx,by+bh*.25),(bx+bw*xx,by+bh*.15),YELLOW)
                arrow(pen,(bx+bw*.54,by+bh*.42),(bx+bw*.54,by+bh*.54),YELLOW)
        if ep=='A08' and side:
            pen=ImageDraw.Draw(im)
            if key in ('stance','warrior'):
                pen.line((bx+bw*.14,by+bh*.92,bx+bw*.88,by+bh*.92),fill=GREEN,width=7)
            if key!='warrior':
                source_key='edge' if key=='edge' else 'flow'
                definition=a08_definition(source_key)
                pose=definition['motionEvidence'][1][min(179,max(0,round(sample)))]
                def point(name):
                    p=sources.projected(definition,pose[name],1)
                    return (bx+(p[0]-1215)*bw/585,by+(p[1]-20)*bh/950)
                if key in ('flow','overview'):
                    pen.line([point('head'),point('pelvis')],fill=YELLOW,width=7)
                if key=='edge':
                    for name,color in (('hand_r',RED),('hand_l',TEAL)):
                        px,py=point(name)
                        if bx<=px<=bx+bw and by<=py<=by+bh:
                            pen.ellipse((px-20,py-20,px+20,py+20),outline=color,width=6)
                if key=='stance':
                    for name in ('foot_r','foot_l'):
                        px,py=point(name)
                        if bx<=px<=bx+bw and by<=py<=by+bh:
                            pen.line((px-25,py+10,px+25,py+10),fill=GREEN,width=7)
    note='머리·몸통의 흐름, 팔 사이 빈 공간, 디딤발을 차례로 보세요.' if ep=='A08' else '눈썹·눈·입의 변화를 한 부분씩 나누어 확인하세요.'
    text(ImageDraw.Draw(im),(80,834),note,37)
    return im
