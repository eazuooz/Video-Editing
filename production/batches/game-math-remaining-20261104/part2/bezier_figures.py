"""Build coefficients, midpoint weights and a subinterval on the same cubic."""
from part2.force_figures import frames
from part2.hermite_figures import draw_header

PURPOSES={
    "007":"각 다항식 계수가 어느 제어점에서 오는지",
    "013":"곡선 가운데에 기여하는 네 가중치",
    "024":"두 표식 사이만 이동하는 새 진행도",
}
PTS=[(220,735),(425,350),(835,350),(1040,735)]

def point(t):
    weights=[(1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3]
    return tuple(sum(w*p[axis] for w,p in zip(weights,PTS)) for axis in range(2))

def control_polygon(d,art,end):
    d.line(PTS,art.MUTED,0,end,3)
    d.line([point(i/80) for i in range(81)],art.TEAL,0,end,5)
    for i,(x,y) in enumerate(PTS):
        d.dot((x,y),art.WHITE,0,end,10)
        d.label(x,y-53 if i in (1,2) else y+68,"b"+"₀₁₂₃"[i],0,end)

def coefficients(d,art):
    e=d.duration;control_polygon(d,art,e)
    steps=[(0,"c₀ = b₀",[1,0,0,0]),(d.cue("비 일에서"),"c₁ = 3(b₁ − b₀)",[-3,3,0,0]),
           (d.cue("다음 계수는"),"c₂ = 3b₀ − 6b₁ + 3b₂",[3,-6,3,0]),
           (d.cue("마지막 계수"),"c₃ = −b₀ + 3b₁ − 3b₂ + b₃",[-1,3,-3,1])]
    for i,(a,formula,weights) in enumerate(steps):
        b=steps[i+1][0] if i+1<len(steps) else e
        d.label(1450,460,formula,a,b,art.GOLD)
        d.label(1450,646,"제어점에 곱하는 값",a,b)
        for j,((x,y),w) in enumerate(zip(PTS,weights)):
            if w:
                d.dot((x,y),art.GOLD if w>0 else art.RED,a,b,13)
                d.label(x,y+55 if j in (1,2) else y-55,f"{w:+d}",a,b,art.GOLD if w>0 else art.RED)

def weights(d,art):
    e=d.duration;control_polygon(d,art,e);mid=d.cue("한가운데")
    d.label(1470,363,"p(t) = Σ Bᵢ(t)bᵢ",0,e,art.GOLD)
    d.label(1470,485,"가중치 합 = 1",0,e)
    d.dot(point(.5),art.GOLD,mid,e,14)
    d.label(630,550,"p(½)",mid,e,art.GOLD)
    d.label(1470,630,"t = ½",mid,e,art.TEAL)
    for j,((x,y),label) in enumerate(zip(PTS,["⅛","⅜","⅜","⅛"])):
        d.label(x,y+58 if j in (1,2) else y-63,label,mid,e,art.TEAL)

def interval(d,art):
    e=d.duration;a,b=.25,.75
    d.line([point(i/100) for i in range(101)],art.MUTED,0,e,4)
    mark=d.cue("표식을 놓고");go=d.cue("새 진행도를")
    d.line([point(a+(b-a)*i/80) for i in range(81)],art.TEAL,mark,e,6,.4)
    for t,label in [(a,"a"),(b,"b")]:
        x,y=point(t);d.dot((x,y),art.WHITE,mark,e,10);d.label(x,y-55,label,mark,e)
    d.label(1480,395,"t = a + (b − a)u",0,e,art.GOLD)
    d.label(1480,505,"예시 [a, b] = [¼, ¾]",mark,e)
    for start,stop in frames(e):
        if start<go:continue
        u=min(1,(start-go)/max(1,(e-go)*.72));t=a+(b-a)*u
        d.dot(point(t),art.GOLD,start,stop,14)
        d.label(1465,655,f"u = {u:.2f}   t = {t:.2f}",start,stop,art.TEAL)

def render(file,cut,timeline,caption,stroke,reveal,art):
    d=art.Diagram(caption,stroke,reveal,cut,timeline)
    titles={"007":("Cubic Bézier Coefficients","삼차 베지에 계수"),"013":("Bernstein Basis","베른슈타인 기저"),"024":("Subinterval","부분 구간")}
    draw_header(d,art,*titles[cut["scene"]])
    {"007":coefficients,"013":weights,"024":interval}[cut["scene"]](d,art)
    file.write_text("\n".join(d.lines)+"\n",encoding="utf8")
