"""Editable symbol annotations for quantities that are not free direction vectors."""
import functools,math
import numpy as np
from PIL import Image,ImageDraw
from common import WORK,V6WORK,v6
from guides import STILLS,static,xy,unit,stroke,arrow,bracket,dot,NCLR,LCLR,RCLR,VCLR,PCLR
from layout import font
from review import grab
BG='#080b0e';WHITE='#f3f3e9';MINT='#9ee9cd';GOLD='#ffd277'
SCALARS={1:'재질 · 금속성',5:'C · 표면의 색',13:'정반사 색',31:'P · 광원 기여의 합',32:'C · 최종 표면색',43:'k · 이 픽셀의 재질색',45:'재질색 · 텍스처'}
def text(d,p,s,c=WHITE,size=34):
    d.text(tuple(p),s,font=font(size,True),fill=c,anchor='lm',stroke_width=2,stroke_fill=BG)
def leader(d,p,q,word,c):
    stroke(d,np.asarray(p),np.asarray(q),c,3);dot(d,p,6,c)
    text(d,(q[0]+7,q[1]),word,c,30)
@functools.lru_cache(None)
def inspected_point(i,s):
    c=v6.TABLE[i];f=V6WORK/'edit'/f'{i:03}-{s:03}.mp4'
    probes=[np.asarray(grab(f,c['frames']/60*u,960)) for u in [.16,.55,.86]]
    # Pick one interior patch that stays on the visible mesh in all samples; never infer a normal from color.
    y,x=np.mgrid[0:540,0:960]
    cx,cy=(339,340) if s==1 else (421,257) if s in (5,13,31,45) else (245,247)
    interior=(abs(x-cx)<76)&(abs(y-cy)<52)
    for im in probes:
        interior&=(im.mean(axis=2)>15)
    if not interior.any():raise RuntimeError(('Inspect material point',s))
    score=np.where(interior,-((x-cx)**2+(y-cy)**2),-1e9);iy,ix=np.unravel_index(np.argmax(score),score.shape)
    return np.array([ix*2,iy*2])
def static_mesh(canvas,s):
    d=ImageDraw.Draw(canvas);d.rectangle((0,174,962,917),fill=BG)
    # This is a static geometry diagram, so omit the unused linear-input meter.
    canvas.alpha_composite(Image.open(static(s)).convert('RGBA').crop((0,0,852,437)),(78,282))
    text(d,(98,223),'표면점 P에서 보는 기호',MINT,36)
    words={22:'들어온 빛과 퍼져 나가는 반사광',23:'표면에 도착하는 입사 방향 ω',41:'꼭짓점의 법선 → 픽셀의 법선 N',46:'N과 L 모두 같은 월드 공간',48:'P → Q가 L의 방향 · 두 점 사이가 d',54:'테두리는 빛을 받는 작은 면적 dA',57:'광원 Q와 표면점 P 사이의 거리 d',72:'같은 N 위에서 여러 입사 방향을 합산'}
    text(d,(92,824),words[s],WHITE,33)
    d.rectangle((1360,28,1900,141),fill='black');text(d,(1380,78),'자체 셰이더 · 기호 설명',WHITE,30)
def shell(canvas):
    d=ImageDraw.Draw(canvas);d.rectangle((0,174,962,917),fill=BG);text(d,(96,231),'한 광원의 출력이 퍼지는 면',MINT,38)
    q=np.array([428.,561.]);direction=unit([.82,-.57])
    for radius,color in [(122,'#7894a2'),(224,'#61c5d2')]:
        d.ellipse((*xy(q-radius),*xy(q+radius)),outline=color,width=4)
        point=q+direction*radius;dot(d,point,7,LCLR);rad=math.degrees(math.atan2(direction[1],direction[0]))
        d.arc((*xy(q-radius),*xy(q+radius)),rad-5,rad+5,fill=NCLR,width=9)
    target=q+direction*224;bracket(d,q,target,LCLR);dot(d,q,13,LCLR)
    text(d,q+[-130,37],'Q · 광원',GOLD);text(d,(q+target)/2+[0,23],'r',GOLD);text(d,target+[15,-12],'P · 받는 면',MINT)
    text(d,(105,841),'같은 출력 Φ · 더 넓은 구면에 나뉘어요.',WHITE,31)
def solid_angle(canvas):
    d=ImageDraw.Draw(canvas);d.rectangle((0,174,962,917),fill=BG);text(d,(96,228),'표면에서 광원 면이 보이는 범위',MINT,36)
    p=np.array([242.,680.]);q=np.array([691.,403.]);t=unit([.62,.78]);a=q-t*69;b=q+t*69
    d.polygon([xy(p),xy(a),xy(b)],fill='#253b39');stroke(d,p,a,'#75ada7',3);stroke(d,p,b,'#75ada7',3);stroke(d,a,b,NCLR,10)
    dot(d,p,9,PCLR);bracket(d,p,q,LCLR);text(d,(p+q)/2+[5,25],'r',GOLD)
    text(d,p+[-55,40],'P',WHITE);text(d,q+[60,53],'dAₛ',NCLR)
    n=np.array([-.78,.62]);qtip=q+85*n;stroke(d,q,qtip,NCLR,5);dot(d,qtip,4,NCLR);text(d,qtip+[-17,-26],'Nₛ',NCLR)
    toward_p=unit(p-q)
    emitter_arc=[q+63*unit((1-u)*n+u*toward_p) for u in np.linspace(0,1,22)]
    d.line(list(map(xy,emitter_arc)),fill=NCLR,width=4);text(d,q+[-132,70],'θₛ',NCLR,31)
    dirs=[unit(a-p),unit(b-p)]
    arc=[p+100*unit((1-u)*dirs[0]+u*dirs[1]) for u in np.linspace(0,1,32)];d.line(list(map(xy,arc)),fill=GOLD,width=5)
    text(d,p+[48,-76],'dω',GOLD)
    text(d,(95,845),'θₛ는 광원 면의 법선과 P를 향하는 방향 사이의 각',WHITE,29)
def projected(canvas):
    d=ImageDraw.Draw(canvas);d.rectangle((0,174,962,917),fill=BG);text(d,(96,227),'표면점을 광원 그림에 투영하기',MINT,38)
    q=np.array([170.,627.]);p=np.array([801.,395.]);plane=465;inter=q+(p-q)*(plane-q[0])/(p[0]-q[0])
    stroke(d,np.array([plane,320]),np.array([plane,709]),NCLR,6);stroke(d,q,p,LCLR,5);dot(d,p,9,PCLR);dot(d,inter,10,NCLR);dot(d,q,9,LCLR)
    text(d,q+[-54,40],'Q · 광원',GOLD);text(d,p+[-28,-39],'P',WHITE);text(d,inter+[14,27],'(u, v)',NCLR)
    bracket(d,q+[0,128],np.array([p[0],q[1]+128]),VCLR);text(d,(360,786),'깊이 z · 이 투영에서 w = z',VCLR,32)
def decorate(canvas,r,phase):
    s=r['sid'];d=ImageDraw.Draw(canvas)
    if s in STILLS:static_mesh(canvas,s)
    elif s in SCALARS:
        p=inspected_point(r['i'],s);d.ellipse((*xy(p-18),*xy(p+18)),outline=MINT,width=4)
        leader(d,p+[-12,14],p+[-140,82],SCALARS[s],MINT)
    elif s==53:shell(canvas)
    elif s==56:solid_angle(canvas)
    elif s in (62,65):projected(canvas)
    elif s==55:
        p=np.array([391.,384.]);toward=unit([384.,-62.]);perp=np.array([-toward[1],toward[0]])
        stroke(d,p-21*perp,p+21*perp,NCLR,5)
        for off in [-.13,.13]:stroke(d,p,p+150*unit(toward+off*perp),LCLR,3,True)
        text(d,(497,427),'dω · 방향 범위',GOLD,26)
        text(d,(152,515),'dA⊥ · 투영 면적',NCLR,27);stroke(d,np.array([335.,485.]),p-4*perp,NCLR,2)
    elif s==61:
        for j,(word,col) in enumerate([('G(u,v)',NCLR),('F(z)',VCLR),('a',GOLD)]):
            px=80+291*j+103;py=530;d.ellipse((px-9,py-9,px+9,py+9),outline=col,width=3);stroke(d,np.array([px,py+12]),np.array([px+22,py+48]),col,2)
            text(d,(px+27,py+53),word,col,23)
    elif s==64:
        for y,sym in [(411,'x'),(620,'u')]:
            d.polygon([(831,y),(809,y-10),(809,y+10)],fill=NCLR);text(d,(843,y),sym,NCLR,24)
        text(d,(490,497),'P',GOLD,30)
    elif s==15:
        stroke(d,np.array([275.,889.]),np.array([1445.,889.]),LCLR,3)
        d.polygon([(1459,889),(1437,882),(1437,896)],fill=LCLR);text(d,(553,871),'정반사 세기 kₛ',GOLD,24)
    elif s==73:
        # A basis weight is a scalar. Label its corresponding image instead of inventing a direction arrow.
        stroke(d,np.array([1370.,451.]),np.array([1440.,451.]),MINT,3,True)
