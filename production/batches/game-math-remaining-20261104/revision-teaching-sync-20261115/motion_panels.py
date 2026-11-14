"""One input controls every plotted quantity in a narrated worked example."""
import math
from boards import GOLD,TEAL,MUTED,WHITE,RED,cue


def line(b,points,a,z,color=MUTED,width=3):
    for p,q in zip(points,points[1:]):
        dx,dy=q[0]-p[0],q[1]-p[1];length=math.hypot(dx,dy)
        if not length:continue
        nx,ny=-dy/length*width/2,dx/length*width/2
        b.polygon([(p[0]+nx,p[1]+ny),(q[0]+nx,q[1]+ny),(q[0]-nx,q[1]-ny),(p[0]-nx,p[1]-ny)],a,z,color,3)


def dot(b,x,y,a,z,color=TEAL,r=7):
    b.polygon([(x+r*math.cos(math.tau*i/20),y+r*math.sin(math.tau*i/20)) for i in range(20)],a,z,color,4)


def arrow(b,p,q,a,z,color=TEAL,width=4):
    length=math.dist(p,q)
    if length<1:return
    line(b,[p,q],a,z,color,width)
    ux,uy=(q[0]-p[0])/length,(q[1]-p[1])/length
    b.polygon([q,(q[0]-18*ux-8*uy,q[1]-18*uy+8*ux),(q[0]-18*ux+8*uy,q[1]-18*uy-8*ux)],a,z,color,4)


def plots(b,scene,functions,tmax,states,footer):
    a,z=scene["start"],scene["end"]
    b.rectangle(995,178,888,738,a,z)
    count=len(functions);height=530/count
    for row,(label,fn,low,high,color) in enumerate(functions):
        top=248+row*height;bottom=top+height-53
        def xy(t,value):return 1135+610*t/tmax,bottom-(bottom-top-25)*(value-low)/(high-low)
        b.text(1128,top-31,label,a,z,color,43)
        line(b,[(1135,top+22),(1135,bottom),(1750,bottom)],a,z,MUTED,2)
        b.text(1055,top+6,f"{high:g}",a,z,MUTED,36)
        b.text(1055,bottom-30,f"{low:g}",a,z,MUTED,36)
        line(b,[xy(tmax*i/120,fn(tmax*i/120)) for i in range(121)],a,z,color,4)
        b.text(1125,bottom+3,"0",a,z,MUTED,36)
        b.text(1675,bottom+3,f"{tmax:g}",a,z,MUTED,36)
        for when,finish,t in states:
            px,py=xy(t,fn(t))
            line(b,[(px,top+22),(px,bottom)],when,finish,MUTED,2)
            dot(b,px,py,when,finish,color)
    for when,finish,t in states:
        b.text(1115,813,f"현재 대입한 시간 t = {t:.4g}",when,finish,TEAL,44,width=750)
    b.text(1115,865,footer,a,z,WHITE,42,width=750)


def derivative_value(b,s):
    at=cue(s,"구체적인")
    plots(b,s,[("위치 x(t) [fur]",lambda t:-t*t+6*t-1,-1,9,GOLD),
        ("속도 v(t) [fur/min]",lambda t:-2*t+6,-2,6,TEAL)],3.5,
        [(at,s["end"],2.5)],"같은 2.5 min → x = 7.75, v = 1")


def instantaneous_and_interval(b,game):
    # The Forza speedometer increases. Do not put the later rabbit's decreasing
    # velocity curve next to it and invite a false numerical comparison.
    a=game['start'];z=a+game['duration'];left,right=1120,1750
    b.rectangle(995,178,888,738,a,z)
    b.text(1060,219,"같은 주행을 두 관점으로 보기",a,z,GOLD,44,width=800)
    b.text(1080,320,"순간 속력: 바로 지금의 빠르기",a,z,TEAL,44,width=790)
    b.text(1080,395,"게임 계기판에서 현재 값을 봅니다",a,z,WHITE,42,width=790)
    b.text(1080,540,"구간 평균: 그동안의 움직임을 요약",a,z,GOLD,42,width=790)
    b.text(1080,810,"시간 띠만 표시 · 게임의 수치를 계산한 그래프 아님",a,z,WHITE,40,width=790)
    line(b,[(left,690),(right,690)],a,z,MUTED,4)
    for i in range(math.ceil((z-a)*20)):
        lo=a+i/20;hi=min(z,lo+.05);u=(lo-a)/(z-a);x=left+(right-left)*u
        line(b,[(left,690),(x,690)],lo,hi,GOLD,13)
        dot(b,x,690,lo,hi,TEAL,11)
        b.text(max(left,min(right-90,x-35)),730,"지금",lo,hi,TEAL,40)


def defined_circular_inputs(b,s):
    # Omega is taught in scene006. Earlier helper readouts must use the r and s
    # that have actually been introduced, rather than an unexplained omega.
    a,z=s['start'],s['end']
    if s['scene']=='001':b.rectangle(995,178,888,50,a,z)
    b.rectangle(995,795,888,123,a,z)
    b.text(1090,813,"r: 원의 반지름 · s: 속력",a,z,WHITE,43,width=780)
    b.text(1090,865,"속도 방향은 원의 접선",a,z,TEAL,42,width=780)


def throw_times(b,s):
    peak=79.25/32;back=2*peak
    a=cue(s,"값을 영으로 놓으면");z=cue(s,"출발 순간 0초");last=cue(s,"약 4.953초")
    plots(b,s,[("위치 y(t) [ft] · 아래쪽 +",lambda t:-79.25*t+16*t*t,-105,15,GOLD),
        ("속도 v(t) [ft/s]",lambda t:-79.25+32*t,-90,90,TEAL),
        ("가속도 a(t) [ft/s²]",lambda t:32,0,36,RED)],5.2,
        [(a,z,peak),(z,last,0),(last,s["end"],back)],"정점: v = 0 · 같은 높이 복귀: y = 0")


def designed_acceleration(b,s):
    a,z=s["start"],s["end"];remaining=cue(s,"초기 속도로 갈 6");result=cue(s,"계산하면 2")
    b.rectangle(995,178,888,738,a,z)
    b.text(1090,220,"3초 뒤 목표 위치를 먼저 표시",a,z,GOLD,44,width=780)
    left,right=1120,1770;top,bottom=345,730
    def xy(t,x):return left+(right-left)*t/3,bottom-(bottom-top)*x/15
    line(b,[(left,top),(left,bottom),(right,bottom)],a,z,MUTED,3)
    b.text(left-66,top-25,"15 m",a,z,GOLD,40)
    b.text(right-60,bottom+20,"3 s",a,z,GOLD,40)
    line(b,[xy(0,0),xy(3,6)],a,z,TEAL,4)
    b.text(1170,755,"v₀t = 2 × 3 = 6 m",a,z,TEAL,44)
    dot(b,*xy(3,15),a,z,GOLD,9)
    arrow(b,xy(3,6),xy(3,15),remaining,z,GOLD)
    b.text(1310,477,"남은 9 m",remaining,z,GOLD,44)
    line(b,[xy(3*i/100,2*(3*i/100)+(3*i/100)**2) for i in range(101)],result,z,GOLD,4)
    b.text(1100,840,"a = 2 m/s² → x(3) = 15 m",result,z,WHITE,44)


def power_area(b,s):
    a,z=s["start"],s["end"];at=cue(s,"전력이 두 초")
    b.rectangle(995,178,888,738,a,z)
    b.text(1090,231,"일정한 전력 × 사용 시간",a,z,GOLD,46)
    line(b,[(1120,340),(1120,720),(1760,720)],a,z,MUTED,3)
    b.text(1010,305,"100 W",at,z,TEAL,42)
    b.text(1670,746,"2 s",at,z,GOLD,44)
    b.rectangle(1120,355,640,365,at,z,"233630")
    line(b,[(1120,355),(1760,355)],at,z,TEAL,5)
    b.equation(1200,510,r"E=100\times2=200\ \mathrm{J}",at,z,GOLD,width=530,size=52)
    b.text(1090,840,"이 넓이가 같은 구간의 사용 에너지",at,z,WHITE,43,width=780)


def kart_acceleration(b,s,game):
    a=s["start"];z=cue(s,"지표 부근의 중력");go=game["start"]+5.2;stop=game["start"]+game["duration"]
    b.rectangle(995,178,888,738,a,z)
    b.text(1080,219,"같은 시간마다 같은 속도 변화",a,z,GOLD,44,width=790)
    b.equation(1120,289,r"a=\frac{\Delta v}{\Delta t}",a,z,TEAL,size=54)
    left,right=1140,1750;top,bottom=430,660
    line(b,[(left,top),(left,bottom),(right,bottom)],a,z,MUTED,3)
    line(b,[(left,bottom),(right,top)],a,z,TEAL,4)
    b.text(1050,406,"속도",a,z,TEAL,42);b.text(1630,678,"시간",a,z,WHITE,42)
    for j in range(4):
        x=left+(right-left)*j/3;y=bottom-(bottom-top)*j/3
        line(b,[(x,y),(x,bottom)],a,z,MUTED,2)
    for i in range(math.ceil((z-a)*20)):
        lo=a+i/20;hi=min(z,lo+.05)
        u=max(0,min(1,(lo-go)/(stop-go)))
        dot(b,left+(right-left)*u,bottom-(bottom-top)*u,lo,hi,TEAL)
        # Same model parameter, same v=a*t, not a guessed game speed.
        arrow(b,(1135,790),(1135+470*u,790),lo,hi,TEAL,7)
        b.text(1660,765,"v",lo,hi,TEAL,48)
    arrow(b,(1135,861),(1340,861),a,z,RED,6)
    b.text(1380,832,"일정한 a",a,z,RED,44)


def carriage_displacements(b,s):
    # Keep the original moving carriage until the spoken sixteen-second result.
    # At that exact clause, bind the pictured displacements to the same interval.
    a=cue(s,"십육 초 동안");z=s["end"]
    vc=5-75*1.25/1075;vp=vc+1.25;t=16
    b.rectangle(56,178,886,738,a,z)
    b.text(75,219,"같은 16초 동안 이동한 거리",a,z,GOLD,46,width=840)
    b.text(75,288,"각자의 출발점에서 잰 변위 · 지면 기준",a,z,WHITE,42,width=840)
    for row,(label,v,color) in enumerate((("객차",vc,GOLD),("사람",vp,TEAL))):
        y=485+row*205;left=130;right=left+700*(v*t)/100
        b.text(75,y-110,label,a,z,color,44)
        line(b,[(left,y),(830,y)],a,z,MUTED,3)
        arrow(b,(left,y),(right,y),a,z,color,8)
        b.text(75,y+23,f"{v:.4f} m/s × 16 s = {v*t:.1f} m",a,z,color,42,width=840)
    b.text(75,840,"두 경우 모두 상대 변위에 80 m를 더한 결과",a,z,WHITE,42,width=840)


def last_speed_rectangle(b,s):
    a=cue(s,"마지막 속도에");parts=cue(s,"작은 조각으로");z=s["end"]
    b.rectangle(995,178,888,738,a,z)
    b.text(1070,219,"같은 구간 T = 2.4 s를 비교",a,z,GOLD,44,width=800)
    left,right=1135,1760;top,bottom=355,715
    def xy(t,v):return left+(right-left)*t/2.4,bottom-(bottom-top)*v/76.8
    b.rectangle(left,top,right-left,bottom-top,a,parts,"292039")
    line(b,[(left,top),(left,bottom),(right,bottom)],a,z,MUTED,3)
    line(b,[xy(0,0),xy(2.4,76.8)],a,z,TEAL,5)
    line(b,[(left,top),(right,top)],a,parts,RED,5)
    b.text(1010,302,"76.8 ft/s",a,z,TEAL,40)
    b.text(1630,746,"2.4 s",a,z,GOLD,44)
    b.text(1080,810,"처음부터 마지막 속도라면: 직사각형 184.32 ft",a,parts,WHITE,42,width=790)
    for i in range(6):
        x0,y0=xy(i*.4,32*i*.4);x1,_=xy((i+1)*.4,0)
        if i:b.rectangle(x0,y0,x1-x0,bottom-y0,parts,z,"233630")
        line(b,[(x0,bottom),(x0,y0),(x1,y0),(x1,bottom)],parts,z,TEAL,3)
    b.text(1080,810,"각 조각: 그때의 속도 × 짧은 시간 폭",parts,z,WHITE,42,width=790)


def apply(board,episode,games):
    lookup={s["scene"]:s for s in episode["scenes"]}
    if episode["id"]=="M24":
        derivative_value(board,lookup["019"])
        instantaneous_and_interval(board,next(g for g in games if g['scene']=='015'))
    if episode["id"]=="M25":
        throw_times(board,lookup["014"])
        designed_acceleration(board,lookup["015"])
        power_area(board,lookup["028"])
        kart_acceleration(board,lookup["002"],next(g for g in games if g["scene"]=="002"))
        last_speed_rectangle(board,lookup["006"])
    if episode["id"]=="M30":carriage_displacements(board,lookup["053"])
    if episode["id"]=="M26":
        for sid in ('001','005'):defined_circular_inputs(board,lookup[sid])
