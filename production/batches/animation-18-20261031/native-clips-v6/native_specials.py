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


def original_a08(key, n):
    source_key = 'edge' if key == 'edge' else 'flow'
    files=sorted((BATCH/'local/real-clips-v2/study-frames'/('A08-'+source_key)).glob('*.png'))
    assert len(files)>=180
    with Image.open(files[min(179,max(0,round(n)))]) as im:
        return im.convert('RGB').crop((1215,250,1770,940))


def source_picture(ep,key,n,side=1):
    if ep=='A08':
        return game_picture('ringfit',n) if key=='warrior' else original_a08(key,n)
    if ep=='A12':
        return game_picture('acnh-face' if key in ('eyes','distance') else 'lune-face',n)
    if ep=='A18':
        return native_crop('anim_OpeningValve_R',min(79,n*79/179),1) if key=='wrist' else game_picture('luigi-face',n)
    if ep=='A17':
        return native_crop('anim_GrabValve_R',min(109,n*109/179),1)
    if ep=='A14':
        return legacy_crop('A01','walk',min(119,n),0)
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
        pole=np.array([-direction[1],direction[0]])*(-1 if key=='hint' and side else 1)
        elbow=tuple(np.array(shoulder)+direction*along+pole*height)
        chain(d,[shoulder,elbow,target],TEAL if not side else RED)
        if key=='hint':
            text(d,(x+90,550),'팔꿈치 방향',32,TEAL if not side else RED,650)
        else:
            text(d,(x+90,550),'관절 → 손' if not side else '손 목표 → 관절',35,TEAL if not side else RED,650)
        d.ellipse((target[0]-22,target[1]-22,target[0]+22,target[1]+22),outline=GREEN,width=5)
        text(d,(x+80,841),'어깨 → 팔꿈치 → 손 목표',31,MUTED,790)


def rotation_diagram(im,key,n):
    d=ImageDraw.Draw(im)
    u=np.clip((n-9)/41,0,1)
    for side,cx in enumerate((1180,1610)):
        # These are the declared inputs of the principle drawing, not retail-game values.
        yaw=math.radians((40 if key=='gaze' and side else 60)*u)
        pitch=math.radians(10*math.sin(math.pi*u)*(side if key!='curves' else 1))
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
            d.ellipse((cx-115,cy-150,cx+115,cy+150),outline=WHITE,width=7)
        tip=(cx+140*math.sin(yaw),cy+95*math.sin(pitch))
        arrow(d,(cx,cy),tip,TEAL if not side else RED)
        d.line((cx-160,cy,cx+170,cy),fill='#67756c',width=3)
        d.line((cx,cy-185,cx,cy+190),fill='#67756c',width=3)
        label=('머리 60° · 눈 0°' if not side else '머리 40° · 눈 20°') if key=='gaze' else ('좌우 회전' if not side else '기울임도 함께')
        text(d,(cx-165,300),label,32,TEAL if not side else RED,350)
        if key=='gaze':
            eye=(cx+60*math.sin(yaw),cy-45)
            total=math.radians(60*u)
            arrow(d,eye,(eye[0]+120*math.sin(total),eye[1]-120*math.cos(total)),GREEN)
    text(d,(1010,775),'축별 회전의 원리 도식',35,YELLOW,850)
    text(d,(1010,834),'도식 설정: 좌우 60° · 중간 숙임 10°',30,MUTED,850)


def blend_diagram(im,key,n):
    d=ImageDraw.Draw(im)
    if key=='guard':
        c=(1430,530);r=190;u=np.clip(n/179,0,1)
        d.ellipse((c[0]-r,c[1]-r,c[0]+r,c[1]+r),outline='#748279',width=5)
        target=(c[0]+r*.8*math.cos(u*2*math.pi),c[1]+r*.8*math.sin(u*2*math.pi))
        arrow(d,c,target,GREEN)
        text(d,(1100,766),'방향 = 어느 자세를 섞을지',36,WHITE,750)
        text(d,(1100,827),'거리 = 얼마나 섞을지',36,WHITE,750)
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
    text(d,(1100,228),'입력·지면 관계 도식',39,YELLOW,750)


def draw_special(ep,key,n,mode,counter):
    im=layout(ep,key,mode,counter)
    d=ImageDraw.Draw(im)
    d.rectangle((50,110,1330,155),fill=BG)
    source_label = '실제 게임 · 동작 관찰' if ep in ('A12','A18') or key=='warrior' else '언리얼 · 설치된 애니메이션'
    text(d,(64,119),source_label,30,MUTED)
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
    if mode=='native':
        paste(im,source_picture(ep,key,n),(180,188,1560,635))
        text(ImageDraw.Draw(im),(80,838),'동작 전체를 먼저 이어서 봅니다.',39)
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
            lab=['전체 표정','관찰할 부위에 주목'][side]
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
                pen.rectangle((bx,by+bh*.69,bx+bw,by+bh),fill=BG)
            elif key=='mouth':
                pen.rectangle((bx,by,bx+bw,by+bh*.48),fill=BG)
            else:
                pen.rounded_rectangle((bx+bw*.15,by+bh*.14,bx+bw*.84,by+bh*.45),radius=16,outline=RED,width=6)
                for xx in (.35,.67):
                    arrow(pen,(bx+bw*xx,by+bh*.43),(bx+bw*xx,by+bh*.31),YELLOW)
                arrow(pen,(bx+bw*.54,by+bh*.81),(bx+bw*.54,by+bh*.93),YELLOW)
        if ep=='A08' and side:
            pen=ImageDraw.Draw(im)
            if key in ('stance','warrior'):
                pen.line((bx+bw*.14,by+bh*.92,bx+bw*.88,by+bh*.92),fill=GREEN,width=7)
            if key!='warrior':
                source_key='edge' if key=='edge' else 'flow'
                definition=read(BATCH/'local/real-clips-v2/studies'/('A08-'+source_key+'.json'))
                pose=definition['motionEvidence'][1][min(179,max(0,round(sample)))]
                def point(name):
                    p=sources.projected(definition,pose[name],1)
                    return (bx+(p[0]-1215)*bw/555,by+(p[1]-250)*bh/690)
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
