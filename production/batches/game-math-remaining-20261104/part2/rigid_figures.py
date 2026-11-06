"""Visualize the narrated door, joint freedoms and unequal collision responses."""
import math
from part2.force_figures import arrow, frames, progress

PURPOSES={
    "007":"문을 누르는 위치와 힘의 방향이 토크를 바꾼다",
    "012":"손잡이의 지렛팔과 추의 질량 반지름을 분리해서 비교",
    "027":"관절마다 허용하는 회전과 이동",
    "054":"반대인 충격량을 받은 두 물체의 서로 다른 속도 변화",
}

def door(d,art,sid):
    e=d.duration; hinge=(275,656); y=hinge[1]
    d.area([(275,y-22),(1050,y-22),(1050,y+22),(275,y+22)],art.DARK,0,e)
    d.line([(275,y-22),(1050,y-22),(1050,y+22),(275,y+22),(275,y-22)],art.MUTED,0,e,4)
    d.dot(hinge,art.GOLD,0,e,18);d.label(269,760,"경첩",0,e,art.GOLD)
    if sid=="007":
        far=d.cue("손잡이 가까이");parallel=d.cue("힘이 문을 따라");normal=d.cue("지렛팔에 직각")
        d.label(1480,399,"|τ| = rF sin θ",0,e,art.GOLD)
        d.label(1480,510,"같은 세기의 힘 F",0,e)
        for a,b in frames(e):
            x=520+431*progress(a,far,.85)
            theta=math.pi/2 + math.pi/2*(progress(a,parallel,.8)-progress(a,normal,.8))
            arrow(d,(x,y-28),(x+180*math.cos(theta),y-28-180*math.sin(theta)),art.RED,a,b)
            d.dot((x,y),art.TEAL,a,b,11); d.label(x,786,"미는 곳",a,b,art.TEAL)
            note="경첩 쪽으로 밀면 τ = 0" if parallel<=a<normal else "직각으로 밀면 |τ| = rF"
            d.label(1480,670,note,a,b)
    else:
        lift=d.cue("문에 붙인 추를")
        d.label(1460,379,"τ = r힘 F⊥",0,e,art.GOLD)
        d.label(1460,496,"I추 = m r추²",lift,e,art.TEAL)
        d.label(1460,630,"같은 τ에서 I가 크면",lift,e)
        d.label(1460,716,"각가속도 α가 작다",lift,e)
        d.dot((960,y),art.GOLD,0,e,12); d.label(961,779,"손잡이",0,e,art.GOLD)
        d.arrow((960,y-36),(960,y-205),art.RED,0,e)
        for a,b in frames(e):
            x=445+310*progress(a,lift,1.9)
            d.dot((x,y),art.TEAL,a,b,28);d.label(x,525,"추 m",a,b,art.TEAL)
            d.line([(hinge[0],y+56),(x,y+56)],art.TEAL,a,b,3,0)

def joint(d,art):
    e=d.duration
    switches=[0,d.cue("힌지는 축까지"),d.cue("프리즘 관절"),d.cue("축 회전도"),d.cue("유니버설 관절"),d.cue("어깨 같은"),e]
    titles=["볼 소켓 · 회전","힌지 · 한 축 회전","프리즘 · 한 축 이동","원통 · 이동과 축 회전","유니버설 · 직교하는 두 축","어깨 · 회전 범위 제한"]
    base=(670,589)
    for state,(a,b) in enumerate(zip(switches,switches[1:])):
        if b<=a:continue
        d.label(1460,460,titles[state],a,b,art.GOLD);d.label(1450,640,"허용된 움직임",a,b)
        if state in (2,3):d.line([(320,589),(1000,589)],art.MUTED,a,b,4)
        else:d.dot(base,art.GOLD,a,b,18)
        for lo,hi in frames(b-a):
            t=a+lo;end=a+hi;angle=lo*1.5
            if state in (2,3):
                x=665+206*math.sin(angle);w=56
                d.area([(x-w,554),(x+w,554),(x+w,624),(x-w,624)],art.TEAL,t,end)
                if state==3:
                    d.line([(x,589),(x+22*math.sin(angle),589-28*math.cos(angle))],art.GOLD,t,end,5,0)
            else:
                # Front view of the active rod. A second projected axis is visible for the universal joint.
                swing=.66*math.sin(angle)
                x=base[0]+245*math.cos(swing);y=base[1]-245*math.sin(swing)
                if state in (0,4,5):x=base[0]+(x-base[0])*(.70+.28*math.cos(.73*angle))
                d.line([base,(x,y)],art.TEAL,t,end,6,0);d.dot((x,y),art.TEAL,t,end,14)
        if state==4:
            d.line([(530,702),(735,488)],art.GOLD,a,b,3)
            d.line([(552,489),(740,686)],art.RED,a,b,3)
        if state==5:
            for sign in [-1,1]:d.line([base,(940,589+sign*175)],art.MUTED,a,b,2)

def collision(d,art):
    e=d.duration;hit=d.cue("충격량을 구합니다")
    d.label(1465,360,"마찰 없는 접촉",0,e,art.GOLD)
    d.label(1465,485,"예시 mA = 2mB",0,e)
    d.label(1465,645,"같은 |J|, 다른 |Δv|",hit,e,art.TEAL)
    scale=175
    for a,b in frames(e):
        if a<hit:
            dt=(a/hit-1)*1.4
            xa,xb=650+2*scale*dt,728-scale*dt;va,vb=2,-1
        else:
            dt=min((a-hit)*.16,1.1)
            xa,xb=650+.5*scale*dt,728+2*scale*dt;va,vb=.5,2
        y=635-47*dt
        for x,v,col,label in [(xa,va,art.TEAL,"A"),(xb,vb,art.RED,"B")]:
            d.dot((x,y),col,a,b,38);d.label(x,y+90,label,a,b,col)
            arrow(d,(x,y-55),(x+80*v,y-55-40),col,a,b)
    d.label(671,365,"속도 벡터 · 접선 성분은 유지",0,e)

def render(file,cut,timeline,caption,stroke,reveal,art):
    d=art.Diagram(caption,stroke,reveal,cut,timeline)
    d.area([(0,226),(1920,226),(1920,1080),(0,1080)],"000000",0,d.duration,2)
    sid=cut["scene"]
    if sid in ("007","012"):door(d,art,sid)
    elif sid=="027":joint(d,art)
    else:collision(d,art)
    file.write_text("\n".join(d.lines)+"\n",encoding="utf8")
