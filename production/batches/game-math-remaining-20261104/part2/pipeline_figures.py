"""Speech-timed teaching diagrams beside the preserved M23 Unity subject."""
import math

PURPOSES={
    "003":"같은 물체에 카메라 거리별로 다른 메시를 고르는 LOD",
    "011":"하나의 공통 변환 M을 삼각형의 세 정점에 적용",
    "012":"같은 정점 P에 저장된 위치, UV, 법선 N, 접선 T와 스키닝 가중치",
    "013":"같은 표면의 N과 T에서 B를 구하고 좌우성 h로 방향을 정하기",
    "015":"한 정점에 연결된 두 UV 주소와 뼈별 가중치 구분",
    "017":"정점 셰이더가 내보내는 클립 위치와 픽셀로 전달할 속성",
    "018":"같은 점이 모델·월드·카메라·클립 좌표를 차례로 얻는 과정",
}
TEACHING_SCENES=set(PURPOSES)
WHITE="EBF2F4";MUTED="909E9A";GOLD="83CEE9";TEAL="C2C773";GREEN="A6CA88";RED="9390EA"
DARK="233630"

class Diagram:
    def __init__(self,caption,stroke,reveal,cut,timeline):
        self.caption=caption;self.stroke=stroke;self.reveal=reveal
        self.lines=caption.ass_header()
        self.duration=cut["frames"]/60
        self.origin=cut["globalStartFrame"]/60
        self.cues=[c for c in timeline["ko"] if c["scene"]==cut["scene"]]
        self.area([(1000,258),(1840,258),(1840,731),(1000,731)],"000000",0,self.duration,1)
    def cue(self,words):
        matches=[c for c in self.cues if words in c["spoken"]]
        assert len(matches)==1,(words,len(matches))
        return max(0,min(self.duration,matches[0]["start"]-self.origin))
    def event(self,start,end,style,layer=4):
        if end>start:self.caption.event(self.lines,start,end,style,layer)
    def area(self,points,color,start,end,layer=3):
        path="m "+" ".join(map(str,points[0]))+" l "+" ".join(f"{x:.1f} {y:.1f}" for x,y in points[1:]+points[:1])
        self.event(start,end,r"{\an7\pos(0,0)\p1\bord0\shad0\1c&H"+color+"&}"+path,layer)
    def line(self,points,color,start,end,width=3,draw=.28):
        if end<=start:return
        stop=min(start+draw,end)
        count=max(1,math.ceil((stop-start)*24))
        tag=r"{\an7\pos(0,0)\p1\bord0\shad0\1c&H"+color+"&}"
        for i in range(count):
            part=self.reveal(points,(i+1)/count)
            self.event(start+(stop-start)*i/count,start+(stop-start)*(i+1)/count,tag+self.stroke(part,width),3)
        self.event(stop,end,tag+self.stroke(points,width),3)
    def label(self,x,y,text,start,end,color=WHITE,size=40):
        self.event(start,end,r"{\an5\pos("+f"{x},{y}"+r")\fs"+str(max(48,size))+r"\b1\bord3\shad0\1c&H"+color+"&}"+text,5)
    def dot(self,point,color,start,end,radius=9):
        x,y=point
        self.area([(x+radius*math.cos(i*math.tau/20),y+radius*math.sin(i*math.tau/20)) for i in range(20)],color,start,end,4)
    def arrow(self,a,b,color,start,end):
        self.line([a,b],color,start,end,3.5)
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);x,y=dx/length,dy/length
        self.area([b,(b[0]-17*x-8*y,b[1]-17*y+8*x),(b[0]-17*x+8*y,b[1]-17*y-8*x)],color,start+.24,end,4)

def patch(d,start,end):
    corners=[(1120,548),(1302,412),(1608,497),(1427,635)]
    d.area(corners,DARK,start,end,2)
    d.line(corners+[corners[0]],MUTED,start,end,2)
    p=(1364,524)
    for point in corners:d.line([point,p],MUTED,start,end,1.3)
    d.dot(p,GOLD,start,end)
    d.label(1390,573,"P",start,end,GOLD)
    return p

def bone_weights(d,start,end):
    a=(1200,536);b=(1465,420);p=(1570,565)
    d.line([a,b],MUTED,start,end,9)
    for point,label in [(a,"본 i"),(b,"본 j")]:
        d.dot(point,TEAL,start,end,14);d.label(point[0],point[1]-52,label,start,end,TEAL)
    d.dot(p,GOLD,start,end);d.label(1620,607,"정점 P",start,end,GOLD)
    d.arrow(a,p,TEAL,start+.12,end);d.arrow(b,p,GREEN,start+.15,end)
    d.label(1400,600,"가중치 wᵢ",start+.3,end,TEAL)
    d.label(1590,465,"wⱼ",start+.3,end,GREEN)

def vertex_attributes(d):
    e=d.duration;bone=d.cue("뼈로 움직이는");p=patch(d,0,bone)
    uv=d.cue("유브이는");normal=d.cue("법선은");color=d.cue("정점 색은");tangent=d.cue("접선 기저는")
    d.label(1250,600,"정점 위치",d.cue("위치는"),uv,GOLD,38)
    square=[(1660,420),(1770,420),(1770,530),(1660,530),(1660,420)]
    d.line(square,TEAL,uv,normal);d.dot((1720,470),TEAL,uv,normal)
    d.line([p,(1720,470)],TEAL,uv,normal,2)
    d.label(1716,575,"UV",uv,normal,TEAL)
    d.arrow(p,(1364,349),GREEN,normal,bone);d.label(1438,344,"N · 법선",normal,bone,GREEN)
    d.dot(p,RED,color,tangent,13);d.label(1602,615,"정점 색",color,tangent,RED)
    d.arrow(p,(1558,581),TEAL,tangent,bone);d.label(1635,594,"T · 접선",tangent,bone,TEAL)
    d.arrow(p,(1468,446),GOLD,tangent,bone);d.label(1534,423,"B",tangent,bone,GOLD)
    bone_weights(d,bone,e)

def tangent_frame(d):
    e=d.duration;p=patch(d,0,e)
    d.arrow(p,(1364,333),GREEN,0,e);d.label(1433,330,"N · 법선",.25,e,GREEN)
    t=d.cue("더하려면 접선과")
    d.arrow(p,(1550,581),TEAL,t,e);d.label(1635,597,"T · 접선",t+.25,e,TEAL)
    h=d.cue("외적에")
    d.arrow(p,(1464,449),GOLD,h,e);d.label(1558,417,"B  (h = +1)",h+.25,e,GOLD)
    d.arrow(p,(1264,599),RED,h+.25,e);d.label(1206,655,"B  (h = −1)",h+.48,e,RED)
    d.label(1460,696,"B = h (N × T)",h+.5,e)

def uv_sets(d):
    e=d.duration;bone=d.cue("스키닝 형식에는")
    p=(1204,532);d.dot(p,GOLD,0,bone);d.label(1204,586,"같은 정점 P",0,bone,GOLD)
    for x,y,color,label,start in [(1570,388,TEAL,"UV₀ · 표면 무늬",0),(1570,574,GREEN,"UV₁ · 라이트맵",d.cue("놓은 조명용"))]:
        box=[(x-52,y-52),(x+52,y-52),(x+52,y+52),(x-52,y+52)]
        d.area(box,DARK,start,bone);d.line(box+box[:1],color,start,bone,2)
        d.line([(x-50,y),(x+50,y)],color,start,bone,1);d.line([(x,y-50),(x,y+50)],color,start,bone,1)
        d.arrow(p,(x-58,y),color,start,bone);d.dot((x+16,y-10),color,start,bone,6)
        d.label(x,y+85,label,start,bone,color,38)
    bone_weights(d,bone,e)

def vertex_outputs(d):
    e=d.duration;p=(1190,500);d.dot(p,GOLD,0,e);d.label(1190,562,"정점 P",0,e,GOLD)
    for point,text,color,when in [((1470,370),"클립 위치 · p_clip",GOLD,d.cue("화면으로 보낼")),
                                 ((1470,579),"픽셀로 · UV, N",TEAL,d.cue("픽셀 셰이더가 사용할"))]:
        d.arrow(p,point,color,when,e);d.label(1620,point[1],text,when+.24,e,color,40)

def transforms(d):
    e=d.duration
    d.label(1658,278,"좌표계 해설 도형",0,e,MUTED,30)
    centers=[1120,1330,1535,1740];names=["모델","월드","카메라","클립"];symbols=["p_model","p_world","p_view","p_clip"]
    times=[0,d.cue("월드에 놓고"),d.cue("카메라 기준으로"),d.cue("투영에 사용할")]
    for i,(x,name,symbol,t) in enumerate(zip(centers,names,symbols,times)):
        d.line([(x-48,545),(x-48,430)],MUTED,t,e,2);d.line([(x-48,545),(x+64,545)],MUTED,t,e,2)
        dot=(x+10,474+12*(i%2));d.dot(dot,GOLD,t,e)
        d.label(x,363,name,t,e);d.label(x,605,symbol,t,e,GOLD,37)
        if i:
            d.arrow((x-142,480),(x-70,480),TEAL,t,e)
            d.label(x-104,428,["","M","V","P"][i],t+.2,e,TEAL,38)

def shared_state(d):
    e=d.duration;t=d.cue("같은 물체의")
    points=[(1190,617),(1420,507),(1680,608)]
    d.line(points+[points[0]],MUTED,0,e)
    for i,p in enumerate(points):
        d.dot(p,TEAL,0,e);d.label(p[0],p[1]+43,["P₀","P₁","P₂"][i],0,e,TEAL)
    root=(1420,388);d.label(root[0],326,"공통 변환 행렬 M",t,e,GOLD);d.dot(root,GOLD,t,e)
    for p in points:d.arrow(root,(p[0],p[1]-14),GOLD,t,e)

def lod(d):
    e=d.duration;t=d.cue("더 단순한 메시")
    for i,(x,at) in enumerate([(1203,d.cue("이어서 정점")),(1615,t)]):
        points=[(x-132,575),(x-60,446),(x+6,401),(x+133,575)]
        d.area(points,DARK,at,e);d.line(points+points[:1],TEAL,at,e)
        if i==0:
            mid=(x+2,510)
            for a in points:d.line([mid,a],TEAL,at,e,1.8)
            d.line([mid,(x+64,575)],TEAL,at,e,1.8)
        else:d.line([points[1],points[-1]],TEAL,at,e,1.8)
        d.label(x,633,"가까운 메시" if i==0 else "먼 메시",at,e,GOLD,39)

def render(file,cut,timeline,caption,stroke,reveal):
    draw=Diagram(caption,stroke,reveal,cut,timeline)
    builders={"003":lod,"011":shared_state,"012":vertex_attributes,"013":tangent_frame,
              "015":uv_sets,"017":vertex_outputs,"018":transforms}
    builders[cut["scene"]](draw)
    file.write_text("\n".join(draw.lines)+"\n",encoding="utf8")
