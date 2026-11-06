"""Animate the weighted centre and head-to-tail construction on the narrated clock."""
import math

PURPOSES={
    "009":"추 하나만 무거워지면 질량중심이 어디로 갈까?",
    "016":"서쪽과 북서쪽으로 달리는 두 차의 속도",
    "017":"두 운동량의 끝과 시작을 이어 합벡터 구하기",
}

def centre(d,art):
    e=d.duration;change=d.cue("질량만 늘려")
    x0,x1,y=285,1065,555
    d.line([(x0,y),(x1,y)],art.MUTED,0,e,4)
    d.dot((x0,y),art.TEAL,0,e,31)
    d.label(x0,429,"1 kg",0,e)
    d.label(x0,757,"x = 0",0,e); d.label(x1,757,"x = 4 m",0,e)
    d.label(1510,405,"c = Σ(mᵢxᵢ) / Σmᵢ",0,e,art.GOLD)
    for i in range(math.ceil(e*20)):
        a=i/20;b=min(e,a+.05);u=min(1,max(0,(a-change)/2))
        m=1+2*u*u*(3-2*u);c=4*m/(1+m);px=x0+(x1-x0)*c/4
        d.dot((x1,y),art.RED,a,b,31*math.sqrt(m))
        d.label(x1,429,f"{m:.1f} kg",a,b)
        d.line([(px,y-9),(px,y+64)],art.GOLD,a,b,5,0)
        d.label(px,y+111,"중심",a,b,art.GOLD)
        d.label(1510,575,f"질량중심 {c:.2f} m",a,b,art.GOLD)

def vectors(d,art,sid):
    e=d.duration;o=(870,659);west=(602,659)
    nw=(715,504);total=(447,504)
    d.line([(320,659),(1100,659)],art.MUTED,0,e,2)
    d.line([(870,800),(870,320)],art.MUTED,0,e,2)
    d.label(1090,735,"동 +x",0,e);d.label(952,327,"북 +y",0,e)
    if sid=="016":
        show=d.cue("첫 차는 서쪽")
        d.label(1550,393,"두 차가 오는 방향",0,e,art.GOLD)
        d.arrow(o,(736,659),art.TEAL,show,e);d.label(685,727,"v₁ 서쪽",show,e,art.TEAL)
        d.arrow(o,nw,art.RED,show+.35,e);d.label(645,423,"v₂ 북서쪽",show+.35,e,art.RED)
        d.label(1550,580,"붙은 뒤 속도는?",d.cue("충돌 뒤 붙는다면"),e)
    else:
        join=d.cue("끝과 시작");add=d.cue("세로 성분");final=d.cue("전체 질량")
        d.label(1540,380,"pᵢ = mᵢvᵢ",0,e)
        d.label(1540,285,"예시 m₁ = 2m₂",0,e)
        d.arrow(o,west,art.TEAL,0,e);d.label(737,750,"p₁",0,e,art.TEAL)
        d.arrow(o,nw,art.RED,0,join);d.label(650,437,"p₂",0,join,art.RED)
        d.arrow(west,total,art.RED,join,e);d.label(440,580,"p₂",join,e,art.RED)
        d.arrow(o,total,art.GOLD,add,e);d.label(540,416,"합 P",add,e,art.GOLD)
        d.label(1540,525,"P = p₁ + p₂",join,e,art.GOLD)
        d.label(1540,685,"v = P / (m₁ + m₂)",final,e,art.TEAL)

def render(file,cut,timeline,caption,stroke,reveal,art):
    d=art.Diagram(caption,stroke,reveal,cut,timeline)
    d.area([(0,178),(1920,178),(1920,1080),(0,1080)],"000000",0,d.duration,2)
    if cut["scene"]=="009":
        centre(d,art)
    else:
        vectors(d,art,cut["scene"])
    file.write_text("\n".join(d.lines)+"\n",encoding="utf8")
