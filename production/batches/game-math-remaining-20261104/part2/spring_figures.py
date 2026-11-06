"""Compare one spring parameter at a time on a common position/time graph."""
import math

PURPOSES = {
    "009": "같은 기준에서 k, m, 진폭 중 하나만 바꾸면?",
    "012": "같은 용수철에서 감쇠만 높이면 다음 왕복은 어떻게 될까?",
}

def plot(d, art, reference, variant, start, end):
    def point(t, displacement):
        return 185 + 220*t, 597 - 93*displacement
    d.line([point(0,0),point(5,0)],art.MUTED,start,end,3,0)
    d.label(1256,803,"시간 t [s]",start,end)
    d.label(312,354,"위치 x(t)",start,end)
    for fn,color in [(reference,art.MUTED),(variant,art.TEAL)]:
        curve=[point(i/40, fn(i/40)) for i in range(201)]
        d.line(curve,color,start,end,4,.36)
    for i in range(math.ceil((end-start)*20)):
        a=start+i/20; b=min(a+.05,end)
        t=min(5,a-start)
        d.dot(point(t,variant(t)),art.TEAL,a,b,9)

def frequency(d,art):
    e=d.duration; k=d.cue("용수철 상수만"); m=d.cue("물체의 질량만"); amplitude=d.cue("더 멀리")
    reference=lambda t:math.cos(2*t)
    for a,b,omega,amp,label in [(0,k,2,1,"기준 용수철"),(k,m,4,1,"k만 4배 → f는 2배"),(m,amplitude,1,1,"m만 4배 → f는 ½배"),(amplitude,e,2,2,"진폭만 2배 → 같은 f")]:
        variant=lambda t:amp*math.cos(omega*t)
        plot(d,art,reference,variant,a,b)
        d.label(1530,395,"ω = √(k/m)",a,b,art.GOLD)
        d.label(1530,495,"f = ω / (2π)",a,b,art.GOLD)
        d.label(1510,635,label,a,b,art.TEAL)
        d.label(450,797,"회색은 기준 운동",a,b,art.MUTED)

def damping(d,art):
    end=d.duration; change=d.cue("감쇠만 키워")
    def position(t,zeta):
        omega=4; wd=omega*math.sqrt(1-zeta*zeta)
        return math.exp(-zeta*omega*t)*(math.cos(wd*t)+zeta*omega*math.sin(wd*t)/wd)
    reference=lambda t:position(t,.15)
    for a,b,zeta in [(0,change,.15),(change,end,.5)]:
        plot(d,art,reference,lambda t:position(t,zeta),a,b)
        d.label(1470,365,"ζ = c / (2mω₀)",a,b,art.GOLD)
        d.label(1470,481,"같은 m, k, 출발 위치",a,b)
        d.label(1480,643,f"감쇠비 ζ = {zeta:.2f}",a,b,art.TEAL)
        d.label(480,802,"회색: 작은 감쇠",a,b,art.MUTED)
        # Compare F_d at one explicitly fixed positive velocity. Arrow length is proportional to c.
        x,y=1450,786
        d.label(1480,725,"같은 v > 0에서 Fd",a,b)
        d.arrow((x+105,y),(x+105-450*zeta,y),art.TEAL,a,b)

def render(file,cut,timeline,caption,stroke,reveal,art):
    d=art.Diagram(caption,stroke,reveal,cut,timeline)
    bottom=912 if file.parent.parent.name=='render-v3' else 1080
    d.area([(0,178),(1920,178),(1920,bottom),(0,bottom)],"000000",0,d.duration,2)
    {"009":frequency,"012":damping}[cut["scene"]](d,art)
    file.write_text("\n".join(d.lines)+"\n",encoding="utf8")
