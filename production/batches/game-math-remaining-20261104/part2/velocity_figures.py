"""Unit diagrams and a computed Taylor comparison for the M24 narration."""
import math

PURPOSES={
    "008":"프레임 사이 이동량을 구할 때 단위가 어떻게 약분될까?",
    "009":"끝점이 같은 트랙을 미터와 피트로 각각 재기",
    "010":"같은 차의 속도를 길이와 시간 단위만 바꾸어 표시",
    "037":"사인 곡선에 몇 항의 근사 다항식이 얼마나 가까워질까?",
}

def displacement(d,art):
    e=d.duration;x0,x1=1150,1725;y=515
    d.line([(x0,y),(x1,y)],art.MUTED,0,e,4)
    for pos,label in [(x0,"x(t)"),(x1,"x(t + Δt)")]:
        d.dot((pos,y),art.TEAL,0,e);d.label(pos,y+64,label,0,e,art.TEAL)
    go=d.cue("속도에 경과시간");d.arrow((x0,y-48),(x1,y-48),art.GOLD,go,e)
    d.label(1435,394,"Δx = v Δt",go+.25,e,art.GOLD)
    d.label(1440,665,"(m/s) × s = m",d.cue("단위가 사라지고"),e)
    d.label(1435,751,"밀리초 ÷ 1000 → 초",d.cue("들어온다면 먼저"),e,art.TEAL)

def rulers(d,art):
    e=d.duration;left,right=1130,1738;width=right-left
    d.label(1434,306,"같은 트랙의 시작과 끝",0,e)
    for y,unit,step,when in [(423,"m",.5,0),(585,"ft",.3048,d.cue("피트 눈금"))]:
        d.line([(left,y),(right,y)],art.TEAL,when,e,4)
        for i in range(1+math.floor(2/step)):
            x=left+width*i*step/2;d.line([(x,y),(x,y+32)],art.GOLD,when,e,3)
        d.label(left-63,y+2,unit,when,e,art.GOLD)
    t=d.cue("실제 트랙의 양 끝")
    for x in (left,right):d.line([(x,380),(x,650)],art.MUTED,t,e,2)
    d.label(1434,744,"1 ft = 0.3048 m",d.cue("같은 길이를"),e)

def speed_units(d,art):
    e=d.duration;start=(1118,510);finish=(1740,510)
    d.line([start,finish],art.MUTED,0,e,3)
    d.label(1430,342,"같은 속도로 달리는 차",0,e)
    for i in range(math.ceil(e*16)):
        lo=i/16;hi=min(e,(i+1)/16);px=start[0]+(finish[0]-start[0])*lo/e
        d.dot((px,510),art.TEAL,lo,hi,11)
    steps=[("km/h",0),("m/h",d.cue("길이 쪽에서는")),("ft/h",d.cue("미터를 피트로")),("ft/s",d.cue("초를 써서"))]
    for i,(unit,t) in enumerate(steps):
        x=1100+i*209;d.label(x,660,unit,t,e,art.GOLD if i==3 else art.WHITE)
        if i:d.arrow((x-134,660),(x-76,660),art.TEAL,t,e)

def sine_series(d,art):
    e=d.duration;right=2.5
    # This comparison has its own displayed input. Hide the separate native
    # derivative experiment's readout rather than attaching its x to our curves.
    d.area([(70,775),(992,775),(992,916),(70,916)],"000000",0,e,2)
    def to_screen(x,y):return (1100+258*x,618-174*y)
    def polynomial(x,n):
        return sum((-1)**i*x**(2*i+1)/math.factorial(2*i+1) for i in range((n+1)//2))
    xs=[right*i/80 for i in range(81)]
    d.line([to_screen(0,0),to_screen(2.65,0)],art.MUTED,0,e,2)
    d.line([to_screen(0,-.25),to_screen(0,1.28)],art.MUTED,0,e,2)
    d.label(1090,662,"0",0,e,art.MUTED)
    d.label(1706,662,"x (rad)",0,e,art.MUTED)
    d.line([to_screen(x,math.sin(x)) for x in xs],art.TEAL,0,e,4,.55)
    d.label(1255,324,"sin(x)",0,e,art.TEAL)
    start=d.cue("얼마나 가까운지");far=d.cue("같은 항을 두고");add=d.cue("같은 입력에 항을");last=d.cue("이 범위에서는 다음 항")
    for n,a,b in [(3,start,add),(5,add,last),(7,last,e)]:
        d.line([to_screen(x,polynomial(x,n)) for x in xs],art.GOLD,a,b,3,.45)
        d.label(1600,324,f"{n}차 근사",a,b,art.GOLD)
    far_end=d.cue("옮기면 두 선")
    for i in range(math.ceil((e-start)*16)):
        a=start+i/16;b=min(e,a+1/16)
        x=.3+(right-.3)*max(0,min(1,(a-far)/max(.2,far_end-far)))
        n=3 if a<add else 5 if a<last else 7
        first=to_screen(x,math.sin(x));second=to_screen(x,polynomial(x,n))
        d.line([first,second],art.RED,a,b,3,0)
        d.dot(first,art.TEAL,a,b,7);d.dot(second,art.GOLD,a,b,5)
    d.label(1385,728,"같은 x에서 두 곡선의 높이 차",start,e)

def render(file,cut,timeline,caption,stroke,reveal,art):
    d=art.Diagram(caption,stroke,reveal,cut,timeline);e=d.duration
    d.area([(995,192),(1882,192),(1882,897),(995,897)],"000000",0,e,1)
    {"008":displacement,"009":rulers,"010":speed_units,"037":sine_series}[cut["scene"]](d,art)
    file.write_text("\n".join(d.lines)+"\n",encoding="utf8")
