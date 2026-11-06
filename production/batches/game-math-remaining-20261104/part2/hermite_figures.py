"""Synchronized curve constructions for the introductory Hermite lecture."""
import math
from part2.force_figures import arrow, frames, progress

PURPOSES={
    "002":"매개변수로 원 한 바퀴의 위치를 골라 보기",
    "017":"두 직선을 같은 입력에서 다시 보간해 세 점을 잇기",
    "027":"고정된 양 끝의 도함수를 바꾸어 선로 모양 바꾸기",
    "032":"중간 지점에서 두 위치와 두 접선이 기여한 양",
}

def circle(d,art):
    e=d.duration;up=d.cue("첫 구간");left=d.cue("반 바퀴");sqrt=d.cue("루트 일")
    def xy(t):return 625+228*math.cos(t*math.tau),573-228*math.sin(t*math.tau)
    d.line([xy(i/96) for i in range(97)],art.MUTED,0,e,4)
    d.line([xy(i/96) for i in range(49)],art.GOLD,sqrt,e,6)
    d.label(1490,396,"x = cos(2πt)",0,e,art.GOLD)
    d.label(1490,494,"y = sin(2πt)",0,e,art.TEAL)
    d.label(1490,735,"√(1 − x²) ≥ 0",sqrt,e)
    for a,b in frames(e):
        t=.25*progress(a,up,.85)+.25*progress(a,left,.85)
        pt=xy(t);d.line([(625,573),pt],art.TEAL,a,b,3,0)
        d.dot(pt,art.TEAL,a,b,15)
        d.label(1480,619,f"t = {t:.2f}",a,b)
    d.label(950,587,"시작",0,e);d.label(625,288,"¼",up,e,art.TEAL);d.label(315,585,"½",left,e,art.TEAL)

def aitken(d,art):
    e=d.duration;link=d.cue("직선으로 연결");blend=d.cue("직선을 다시");middle=d.cue("가운데 점")
    def pos(x,y):return 290+x*350,780-(y-2)*230
    pts=[pos(x,y) for x,y in [(0,2),(1,3),(2,2)]]
    for i,pt in enumerate(pts):
        d.dot(pt,art.WHITE,0,e,11);d.label(pt[0],pt[1]+59,f"P{i}",0,e)
    d.line([pts[0],pts[1]],art.TEAL,link,e,5,.6);d.line([pts[1],pts[2]],art.RED,link,e,5,.6)
    d.line([pos(i/40,2+2*(i/40)-(i/40)**2) for i in range(81)],art.GOLD,blend,e,4,.6)
    d.label(1470,366,"앞 직선 · 뒤 직선",link,e)
    d.label(1470,503,"같은 입력에서 두 높이",blend,e)
    d.label(1470,650,"P₁에서는 둘 다 P₁",middle,e,art.GOLD)
    for a,b in frames(e):
        if a<blend:continue
        x=.7+.3*progress(a,middle,1.2)
        pa,pb=pos(x,2+x),pos(x,4-x)
        d.line([pa,pb],art.MUTED,a,b,2,0)
        d.dot(pa,art.TEAL,a,b,9);d.dot(pb,art.RED,a,b,9)
        d.dot(pos(x,2+2*x-x*x),art.GOLD,a,b,12)

def path(d,art,sid):
    e=d.duration
    def screen(x,y):return 285+345*x,737-235*y
    p0,p1=screen(0,0),screen(2,0)
    d.label(p0[0],811,"p₀",0,e,art.GOLD);d.label(p1[0],811,"p₁",0,e,art.GOLD)
    if sid=="027":
        change=d.cue("화살표를 돌리면");extend=d.cue("길게 늘리면")
        d.label(1530,402,"p₀, p₁ 고정",0,e);d.label(1505,526,"v₀, v₁ = 양 끝의 도함수",0,e,art.TEAL)
        d.label(1485,679,"시작 접선의 방향 변경",change,extend)
        d.label(1485,679,"시작 접선의 크기 변경",extend,e)
    else:
        mid=d.cue("위치 가중치");weights=d.cue("도함수 가중치");result=d.cue("더하면 일")
        d.label(1490,366,"p₀ = (0,0) · p₁ = (2,0)",0,e)
        d.label(1490,480,"v₀ = (0,3) · v₁ = (0,−3)",0,e,art.TEAL)
        d.label(1475,603,"위치 가중치  ½, ½",mid,e)
        d.label(1475,719,"접선 가중치  ⅛, −⅛",weights,e,art.TEAL)
    for a,b in frames(e):
        vx,vy=0,3
        if sid=="027":
            angle=.95*progress(a,change,1.5);m=2.1+1.05*progress(a,extend,1.4)
            vx,vy=m*math.sin(angle),m*math.cos(angle)
        def coord(t):
            s=t*t;cube=s*t
            return screen(2*(-2*cube+3*s)+(cube-2*s+t)*vx,(cube-2*s+t)*vy-3*(cube-s))
        d.line([coord(i/40) for i in range(41)],art.GOLD,a,b,4,0)
        d.dot(p0,art.WHITE,a,b,8);d.dot(p1,art.WHITE,a,b,8)
        arrow(d,p0,(p0[0]+vx*63,p0[1]-vy*63),art.TEAL,a,b)
        arrow(d,(p1[0],p1[1]-183),p1,art.TEAL,a,b)
        d.label(p0[0]+vx*63-63,p0[1]-vy*63,"v₀",a,b,art.TEAL)
        d.label(p1[0]+58,p1[1]-158,"v₁",a,b,art.TEAL)
        if sid=="032" and a>=mid:
            d.dot(coord(.5),art.TEAL,a,b,12)
            if a>=result:d.label(630,465,"p(½) = (1, 0.75)",a,b)

def draw_header(d,art,english,korean):
    d.area([(0,0),(1920,0),(1920,1080),(0,1080)],"000000",0,d.duration,2)
    for y,size,label in [(44,46,english),(105,53,korean)]:
        d.event(0,d.duration,rf'{{\an7\pos(80,{y})\fs{size}\b1\bord0\1c&H{art.GOLD}&}}'+label,5)
    d.event(0,d.duration,r'{\an9\pos(1828,65)\fs40\bord0\1c&HEBF2F4&}현재 화면 · 수학 모형',5)

def render(file,cut,timeline,caption,stroke,reveal,art):
    d=art.Diagram(caption,stroke,reveal,cut,timeline)
    if file.parent.parent.name=="render-v4":
        headers={
            "002":("Parametric Circle","원의 매개변수 표현"),
            "017":("Aitken Interpolation","에이트켄 보간"),
            "027":("Cubic Hermite Curve","삼차 에르미트 곡선"),
            "032":("Hermite Worked Example","에르미트 곡선의 중간점"),
        }
        draw_header(d,art,*headers[cut["scene"]])
    else:
        d.area([(0,226),(1920,226),(1920,1080),(0,1080)],"000000",0,d.duration,2)
    if cut["scene"]=="002":circle(d,art)
    elif cut["scene"]=="017":aitken(d,art)
    else:path(d,art,cut["scene"])
    file.write_text("\n".join(d.lines)+"\n",encoding="utf8")
