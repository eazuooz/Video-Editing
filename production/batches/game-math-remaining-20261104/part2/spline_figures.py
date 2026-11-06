"""Use the actual neighbouring controls and playback intervals to explain joins."""
import math
from part2.force_figures import arrow,frames,progress
from part2.hermite_figures import draw_header

HEADERS={
    "008":("Geometric and Parametric Continuity","같은 방향, 다른 속력"),
    "011":("First-Derivative Continuity","매듭에서 속도 잇기"),
    "019":("Uniform Catmull–Rom Tangent","이웃한 두 점으로 접선 정하기"),
    "028":("Lagrange Basis","세 시각에 대한 보간 기저"),
    "029":("Projectile Parabola","출발·정점·착지"),
    "030":("De Casteljau Evaluation","이웃 점에서 곡선점까지"),
    "040":("Midpoint Split","두 조각이 만나는 한 점"),
}
PURPOSES={s:ko for s,(_,ko) in HEADERS.items()}

def motion(d,art):
    e=d.duration;unequal=d.cue("길이만 다르면");corner=d.cue("양쪽 도함수를")
    for a,b,kind in [(0,unequal,0),(unequal,corner,1),(corner,e,2)]:
        if b<=a:continue
        knot=(680,583);start=(285,583);stop=(1075,583) if kind<2 else (680,301)
        d.line([start,knot,stop],art.MUTED,a,b,5,0); d.dot(knot,art.GOLD,a,b,13)
        d.label(660,692,"매듭",a,b,art.GOLD)
        step=55; rightstep=step*(2 if kind==1 else 1)
        if kind<2:
            for i in range(1,4):
                d.dot((680-i*step,583),art.TEAL,a,b,6);d.dot((680+i*rightstep,583),art.RED,a,b,6)
            d.label(1460,456,"같은 시간 간격의 점",a,b)
            d.label(1460,574,["양쪽 속력도 같다","오른쪽에서 더 빠르다"][kind],a,b,art.TEAL)
        else:
            d.label(1460,477,"매듭에서 v = 0",a,b,art.GOLD)
            d.label(1460,620,"멈춘 뒤 방향 변경",a,b)
        for lo,hi in frames(b-a):
            t=lo/(b-a)
            if kind<2:
                fraction=.5 if kind==0 else 2/3
                pt=(285+395*t/fraction,583) if t<fraction else (680+395*(t-fraction)/(1-fraction),583)
            else:
                pt=(680-395*(1-2*t)**2,583) if t<.5 else (680,583-282*(2*t-1)**2)
            d.dot(pt,art.WHITE,a+lo,a+hi,13)

def handles(d,art):
    e=d.duration;align=d.cue("손잡이로는")
    kx,ky=680,590;f=(440,ky);d.line([(255,ky),(1150,ky)],art.MUTED,0,e,3)
    d.dot((kx,ky),art.GOLD,0,e,14);d.label(kx,695,"매듭 k",0,e,art.GOLD)
    d.dot(f,art.TEAL,0,e,12);d.label(f[0],695,"f",0,e)
    d.label(1490,375,"같은 구간 시간",0,e)
    d.label(1490,507,"v⁻ = 3(k − f)",0,e,art.TEAL)
    d.label(1490,621,"v⁺ = 3(a − k)",0,e,art.RED)
    for lo,hi in frames(e):
        x=kx+116+124*progress(lo,align,1.1)
        d.dot((x,ky),art.RED,lo,hi,12);d.label(x,695,"a",lo,hi)
        arrow(d,(f[0],ky-45),(kx,ky-45),art.TEAL,lo,hi)
        arrow(d,(kx,ky-45),(x,ky-45),art.RED,lo,hi)

def tangent(d,art):
    e=d.duration;chord=d.cue("화살표를 그린");attach=d.cue("절반을")
    prev,mid,nxt=(245,705),(585,405),(1030,650)
    for pt,label in [(prev,"Pᵢ₋₁"),(mid,"Pᵢ"),(nxt,"Pᵢ₊₁")]:
        d.dot(pt,art.WHITE,0,e,11);d.label(pt[0],pt[1]+65,label,0,e)
    d.line([prev,mid,nxt],art.MUTED,0,e,2,0)
    d.arrow(prev,nxt,art.TEAL,chord,e)
    end=(mid[0]+(nxt[0]-prev[0])/2,mid[1]+(nxt[1]-prev[1])/2)
    d.arrow(mid,end,art.GOLD,attach,e)
    d.label(1510,450,"Tᵢ = (Pᵢ₊₁ − Pᵢ₋₁) / 2",attach,e,art.GOLD)
    d.label(1480,630,"균일한 매개변수 간격",0,e)

def basis(d,art):
    e=d.duration
    phases=[(d.cue("첫 번째 기저"),lambda t:(t-1)*(t-2)/2,"L₀ = (t−1)(t−2)/2",art.TEAL),
            (d.cue("가운데 함수"),lambda t:-t*(t-2),"L₁ = −t(t−2)",art.GOLD),
            (d.cue("마지막 함수를"),lambda t:t*(t-1)/2,"L₂ = t(t−1)/2",art.RED)]
    def xy(t,v):return 235+408*t,693-285*v
    d.line([xy(0,0),xy(2,0)],art.MUTED,0,e,3)
    for i in range(3):d.label(xy(i,0)[0],809,str(i)+"초",0,e)
    for i,(start,f,text,color) in enumerate(phases):
        d.line([xy(t/50,f(t/50)) for t in range(101)],color,start,e,4,.45)
        until=phases[i+1][0] if i<2 else e
        for j in range(3):d.dot(xy(j,f(j)),color,start,until,10)
        d.label(1470,441,text,start,until,color)
        d.label(1470,632,f"{i}초에서만 1",start,until)

def projectile(d,art):
    e=d.duration;apex=d.cue("원점에서 출발해");land=d.cue("다시 지면에 닿")
    replay=d.cue("시간은 초 단위");check=d.cue("그래서 일 초")
    def xy(t):return 245+443*t,743-342*t*(2-t)
    d.line([xy(i/60) for i in range(121)],art.MUTED,0,e,4)
    d.line([(195,743),(1176,743)],art.MUTED,0,e,2,0)
    for t,lab in [(0,"출발"),(1,"정점 h"),(2,"착지")]:
        x,y=xy(t);d.dot((x,y),art.GOLD,0,e);d.label(x,y-66 if t==1 else y+68,lab,0,e)
    d.label(1490,385,"t는 초 단위의 시간",0,e)
    d.label(1485,500,"y = h t (2 − t)",0,e,art.GOLD);d.label(1485,605,"z = d t / 2",0,e,art.TEAL)
    for lo,hi in frames(e):
        if lo<replay:
            u=progress(lo,apex,1)+progress(lo,land,1)
        else:
            u=progress(lo,replay,max(.3,check-replay))+progress(lo,check,min(1.5,max(.3,e-check-.15)))
        d.dot(xy(u),art.TEAL,lo,hi,15);d.label(1485,740,f"t = {u:.2f} s",lo,hi)

def casteljau(d,art,sid):
    e=d.duration
    # Original worked example in the Unity shot: (3,5), (6,1), (0,3), (5,5).
    pts=[(650,380),(1010,780),(290,580),(890,380)]
    def rows(t):
        levels=[pts]
        while len(levels[-1])>1:
            group=levels[-1]
            levels.append([((1-t)*a[0]+t*b[0],(1-t)*a[1]+t*b[1]) for a,b in zip(group,group[1:])])
        return levels
    def curve(t):return rows(t)[-1][0]
    line=[curve(i/96) for i in range(97)]
    d.line(pts,art.MUTED,0,e,2);d.line(line,art.WHITE,0,e,4)
    if sid=="030":
        one=d.cue("진행도 표시");two=d.cue("같은 일을")
        three=d.cue("마지막에 남은");move=d.cue("표시를 움직이면")
    else:
        one=0;two=d.cue("중점들을");three=d.cue("같은 자리에");move=e
        d.line(line[:49],art.TEAL,three,e,6);d.line(line[48:],art.RED,three,e,6)
    for lo,hi in frames(e):
        t=.5 if sid=="040" else .4+.4*progress(lo,move,2)
        levels=rows(t)
        for level,when,color in [(1,one,art.TEAL),(2,two,art.RED),(3,three,art.GOLD)]:
            if lo<when:continue
            points=levels[level]
            if len(points)>1:d.line(points,color,lo,hi,3,0)
            for pt in points:d.dot(pt,color,lo,hi,10)
        d.label(1490,446,f"보간 비율 t = {t:.2f}",lo,hi)
        if lo>=three:d.label(1490,609,"두 조각의 공통점" if sid=="040" else "곡선 위의 점 p(t)",lo,hi,art.GOLD)

def render(file,cut,timeline,caption,stroke,reveal,art):
    d=art.Diagram(caption,stroke,reveal,cut,timeline);sid=cut["scene"]
    draw_header(d,art,*HEADERS[sid])
    if sid in ("030","040"):casteljau(d,art,sid)
    else:{"008":motion,"011":handles,"019":tangent,"028":basis,"029":projectile}[sid](d,art)
    file.write_text("\n".join(d.lines)+"\n",encoding="utf8")
