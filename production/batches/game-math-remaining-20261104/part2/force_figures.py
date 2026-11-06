"""Speech-timed attraction, Earth radius and static friction examples for M27."""
import math

PURPOSES = {
    "017": "두 물체 사이 거리가 두 배가 되면 서로 당기는 힘은 어떻게 변할까?",
    "019": "지구 중심에서 잰 거리와 물체가 받는 중력가속도",
    "025": "미는 힘과 함께 자라는 정지 마찰력",
}

def frames(duration):
    for frame in range(math.ceil(duration * 20)):
        start = frame / 20
        yield start, min(duration, start + .05)

def progress(time, start, seconds):
    u = max(0, min(1, (time-start)/seconds))
    return u*u*(3-2*u)

def arrow(d, start, end, color, a, b):
    dx, dy = end[0]-start[0], end[1]-start[1]
    length = math.hypot(dx, dy)
    if length < 3:
        return
    dx, dy = dx/length, dy/length
    tip = min(17, length*.35)
    x, y = end[0]-dx*tip, end[1]-dy*tip
    d.line([start, end], color, a, b, 5, 0)
    d.area([end, (x-dy*tip*.55,y+dx*tip*.55), (x+dy*tip*.55,y-dx*tip*.55)], color, a, b)

def attraction(d, art):
    end = d.duration
    move = d.cue("거리를 두 배")
    d.label(1450,370,"F = Gm₁m₂ / r²",0,end,art.GOLD)
    d.label(1450,685,"두 질량은 그대로",0,end,art.WHITE)
    for a,b in frames(end):
        radius = 1 + progress(a,move,1.8)
        x1, x2 = 690-170*radius, 690+170*radius
        d.dot((x1,510),art.GOLD,a,b,34); d.dot((x2,510),art.TEAL,a,b,34)
        d.label(x1,420,"A",a,b); d.label(x2,420,"B",a,b)
        arrow(d,(x1+33,510),(x1+33+112/radius**2,510),art.TEAL,a,b)
        arrow(d,(x2-33,510),(x2-33-112/radius**2,510),art.GOLD,a,b)
        d.line([(x1,625),(x2,625)],art.MUTED,a,b,3,0)
        d.label(690,690,f"거리 {radius:.1f}r₀",a,b)
        d.label(1450,505,f"인력  {1/radius**2:.2f} F₀",a,b,art.TEAL)

def earth(d, art):
    end = d.duration
    lift = d.cue("물체를 위로")
    centre = (490,645); radius = 168
    ring = [(centre[0]+radius*math.cos(i*math.tau/80),centre[1]+radius*math.sin(i*math.tau/80)) for i in range(81)]
    d.line(ring,art.TEAL,0,end,4)
    d.dot(centre,art.GOLD,0,end,7); d.label(445,695,"지구 중심",0,end)
    d.label(1460,365,"g(r) = GM / r²",0,end,art.GOLD)
    d.label(1460,710,"M은 지구 질량",0,end)
    for a,b in frames(end):
        scale=1+.8*progress(a,lift,2.2)
        y=centre[1]-radius*scale
        d.line([centre,(centre[0],y)],art.GOLD,a,b,4,0)
        d.dot((centre[0],y),art.TEAL,a,b,14)
        d.label(700,(centre[1]+y)/2,f"r = {scale:.1f}R",a,b,art.GOLD)
        arrow(d,(centre[0]+36,y),(centre[0]+36,y+108/scale**2),art.RED,a,b)
        d.label(1470,515,f"표면 중력의 {1/scale**2:.2f}배",a,b,art.TEAL)

def friction(d, art):
    end = d.duration
    push=d.cue("옆으로 조금"); limit=d.cue("밀기를 계속")
    d.line([(200,616),(1110,616)],art.MUTED,0,end,4)
    d.area([(540,490),(680,490),(660,612),(563,612)],art.GOLD,0,end)
    d.label(1430,355,"정지 마찰의 한도 μₛN",0,end,art.GOLD)
    d.label(1430,435,"이 예에서는 5 N",0,end)
    for a,b in frames(end):
        force=2*progress(a,push,1.2)+3*progress(a,limit,1.9)
        arrow(d,(680,520),(680+force*44,520),art.TEAL,a,b)
        arrow(d,(558,590),(558-force*44,590),art.RED,a,b)
        d.label(820,447,"미는 힘",a,b,art.TEAL)
        d.label(432,692,"정지 마찰",a,b,art.RED)
        d.label(1430,585,f"미는 힘  {force:.1f} N",a,b,art.TEAL)
        d.label(1430,685,f"정지 마찰  {force:.1f} N",a,b,art.RED)

def render(file,cut,timeline,caption,stroke,reveal,art):
    d=art.Diagram(caption,stroke,reveal,cut,timeline)
    d.area([(0,178),(1920,178),(1920,912),(0,912)],"000000",0,d.duration,2)
    {"017":attraction,"019":earth,"025":friction}[cut["scene"]](d,art)
    file.write_text("\n".join(d.lines)+"\n",encoding="utf8")
