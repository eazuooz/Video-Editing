"""Topic-specific conceptual diagrams, with an unchanged-clock example window."""
import math
from PIL import Image, ImageDraw, ImageFont
from prepare import HERE, WORK, read, save

BG='#080c0a'; WHITE='#f3f5ef'; YELLOW='#f2d787'; TEAL='#81cfc5'; RED='#f18b81'; GREEN='#a4d987'; MUTED='#abb9af'; LINE='#425247'
FONT='C:/Windows/Fonts/NotoSansKR-VF.ttf'
def font(size,weight=500):
    f=ImageFont.truetype(FONT,size)
    try:f.set_variation_by_axes([weight])
    except (ValueError,OSError):pass
    return f
def text(d,xy,s,size=38,fill=WHITE,weight=500,maxwidth=None,anchor=None):
    f=font(size,weight)
    while maxwidth and d.textlength(s,font=f)>maxwidth:
        size-=1;f=font(size,weight)
    d.text(xy,s,font=f,fill=fill,anchor=anchor)
def arrow(d,a,b,c=TEAL,width=6):
    d.line([a,b],fill=c,width=width)
    t=math.atan2(b[1]-a[1],b[0]-a[0]);L=19
    d.polygon([b,(b[0]-L*math.cos(t-.5),b[1]-L*math.sin(t-.5)),(b[0]-L*math.cos(t+.5),b[1]-L*math.sin(t+.5))],fill=c)
def label(d,x,y,s,c=TEAL,w=175):text(d,(x,y),s,36,c,maxwidth=w,anchor='mm')
def node(d,x,y,s,c=TEAL,w=190):
    d.line((x-w/2,y+36,x+w/2,y+36),fill=c,width=5)
    label(d,x,y,s,c,w)
def chain(d,labels,ys=515,colors=None):
    xs=[150+(i*(650/(len(labels)-1))) for i in range(len(labels))]
    for i,(x,s) in enumerate(zip(xs,labels)):
        node(d,x,ys,s,(colors or [TEAL]*len(labels))[i],min(180,700/len(labels)))
        if i:arrow(d,(xs[i-1]+85,ys),(x-85,ys),MUTED,4)
    return xs
def tracks(d,first,second):
    text(d,(65,421),first,30,MUTED)
    text(d,(65,577),second,30,MUTED)
    d.line((240,480,870,480),fill=TEAL,width=14)
    d.line((240,635,870,635),fill=GREEN,width=14)

def diagram(d,kind):
    if kind=='phases':
        chain(d,['대기','준비','타격','후속'],495,[TEAL,TEAL,RED,GREEN])
        text(d,(70,603),'동작의 단계 ≠ 판정의 유효 구간',34,MUTED,maxwidth=800)
        d.line((150,680,800,680),fill=LINE,width=12);d.line((520,680,610,680),fill=RED,width=12)
        label(d,560,735,'판정은 별도로 확인',RED,600)
    elif kind=='anticipation':
        chain(d,['첫 변화','힘 모으기','공격'],510,[TEAL,YELLOW,RED])
        arrow(d,(150,665),(800,665),MUTED)
        label(d,470,718,'변화를 읽고 → 다음 행동을 예상',WHITE,800)
    elif kind=='pose':
        node(d,195,455,'공격하는 팔',RED,240);node(d,735,455,'받치는 몸',TEAL,240)
        arrow(d,(245,520),(400,600),RED);arrow(d,(685,520),(530,600),TEAL)
        node(d,465,650,'힘이 읽히는 자세',YELLOW,520)
    elif kind=='follow':
        tracks(d,'동작','조작')
        d.line((460,480,870,480),fill=YELLOW,width=14)
        d.line((240,635,590,635),fill=LINE,width=14)
        label(d,480,530,'타격 뒤 몸의 정리',YELLOW,700)
        label(d,550,700,'다음 입력 시점은 따로 확인',GREEN,750)
    elif kind=='readability':
        chain(d,['실제 몸짓','정보 손실','동작 보완'],520,[TEAL,RED,GREEN])
        text(d,(70,655),'작게 보이면 미세한 변화가 사라집니다.',34,WHITE,maxwidth=800)
        text(d,(70,711),'실제 플레이 크기에서 다시 확인',32,MUTED,maxwidth=800)
    elif kind=='body':
        for x,y,s,c in [(170,470,'몸의 흐름',TEAL),(740,470,'팔·손의 윤곽',YELLOW),(465,700,'체중을 받치는 발',GREEN)]:
            node(d,x,y,s,c,280)
            arrow(d,(x,y+38 if y<600 else y-50),(465,570 if y<600 else 620),c,4)
        label(d,465,590,'하나의 포즈',WHITE,370)
    elif kind=='squash':
        for x,rx,ry,c in [(170,60,60,WHITE),(460,100,36,TEAL),(760,36,100,YELLOW)]:
            d.ellipse((x-rx,530-ry,x+rx,530+ry),outline=c,width=7)
        arrow(d,(260,530),(330,530),MUTED,4);arrow(d,(590,530),(670,530),MUTED,4)
        for x,s,c in [(170,'기본 형태',WHITE),(460,'눌림',TEAL),(760,'늘어남',YELLOW)]:label(d,x,675,s,c,260)
        text(d,(70,737),'형태 변화의 개념도',28,MUTED)
    elif kind=='reaction':
        chain(d,['접촉','몸의 반응','자세 회복'],515,[RED,YELLOW,GREEN])
        arrow(d,(100,680),(820,680),MUTED,4)
        label(d,465,735,'어디를 · 어느 방향으로 맞았는가',WHITE,810)
    elif kind=='timing':
        text(d,(65,415),'같은 시간 간격으로 본 위치',34,WHITE)
        for y,pts,c in [(520,[140,280,420,560,700,840],MUTED),(650,[140,180,225,300,500,840],TEAL)]:
            d.line((140,y,840,y),fill=LINE,width=3)
            for x in pts:d.ellipse((x-11,y-11,x+11,y+11),fill=c)
        text(d,(65,706),'사이의 간격을 바꾸면 속도감도 달라짐',32,TEAL,maxwidth=800)
    elif kind=='face':
        # These facial regions contribute together, rather than causing one another.
        for x,s,c in [(150,'눈썹',YELLOW),(475,'눈',TEAL),(800,'입',GREEN)]:node(d,x,475,s,c,180)
        for x in [150,475,800]:arrow(d,(x,540),(475,635),MUTED,4)
        node(d,475,680,'하나의 감정',WHITE,500)
    elif kind=='mirror':
        d.line((475,410,475,710),fill=LINE,width=3)
        for x,direction,c in [(230,1,TEAL),(720,-1,GREEN)]:
            d.ellipse((x-35,455,x+35,525),outline=c,width=6)
            d.line([(x,525),(x,630),(x+75*direction,650)],fill=c,width=7)
            arrow(d,(x,565),(x+100*direction,565),RED,6)
        label(d,230,725,'반전 전',TEAL,300);label(d,720,725,'반전 후',GREEN,300)
        text(d,(70,390),'화면 방향과 손·장비를 함께 확인',32,WHITE,maxwidth=810)
    elif kind=='blend':
        node(d,200,465,'동작 A',TEAL,260);node(d,730,465,'동작 B',GREEN,260)
        arrow(d,(230,530),(420,625),TEAL);arrow(d,(700,530),(510,625),GREEN)
        node(d,465,670,'재생 위치 + 섞는 비율',YELLOW,700)
    elif kind=='grip':
        d.ellipse((360,430,570,640),outline=YELLOW,width=7)
        for i in range(4):
            y=440+i*43
            d.arc((290,y,600,y+100),180,355,fill=TEAL,width=7)
        label(d,465,708,'물체의 형태 → 손가락 자세',WHITE,800)
        text(d,(70,390),'그립의 개념도',30,MUTED)
    elif kind=='detection':
        d.arc((80,450,840,740),185,350,fill=TEAL,width=9)
        d.rectangle((560,465,760,655),outline=RED,width=7)
        label(d,270,645,'보이는 무기 경로',TEAL,380)
        label(d,665,710,'판정 구간',RED,330)
        text(d,(65,390),'무기 경로와 판정 영역의 개념도',29,MUTED,maxwidth=810)
    elif kind=='rig':
        pts=[(130,660),(205,550),(260,460),(360,500)]
        d.line(pts,fill=TEAL,width=7)
        for x,y in pts:d.ellipse((x-12,y-12,x+12,y+12),fill=BG,outline=TEAL,width=4)
        d.arc((550,430,820,680),150,345,fill=GREEN,width=9)
        label(d,245,730,'관절의 회전',TEAL,350);label(d,690,730,'표면의 변형',GREEN,350)
        text(d,(65,390),'목표 형태에 필요한 방법을 선택',34,WHITE,maxwidth=800)
    elif kind=='axes':
        arrow(d,(250,650),(250,435),TEAL);arrow(d,(250,650),(480,650),YELLOW)
        label(d,295,420,'좌우',TEAL,220);label(d,485,702,'상하',YELLOW,220)
        for off,c in [(0,TEAL),(60,YELLOW)]:
            pts=[]
            for n in range(101):
                x=570+n*2.6;y=640-130*(.5-.5*math.cos(math.pi*min(1,max(0,(n*2.6-off)/200))))
                pts.append((x,y))
            d.line(pts,fill=c,width=6)
        text(d,(565,720),'축별로 다른 타이밍',31,WHITE,maxwidth=330)
    else:raise ValueError(kind)

def build(row):
    folder=WORK/row['id'];folder.mkdir(parents=True,exist_ok=True)
    image=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(image)
    text(d,(64,38),row['title'].split('|')[0].strip(),62,YELLOW,700,maxwidth=1770)
    text(d,(64,126),'개론 · '+row['term'],34,TEAL,500,maxwidth=1780)
    d.line((64,190,1856,190),fill=LINE,width=2)
    for i,line in enumerate(row['definition']):text(d,(64,225+i*65),line,42,WHITE,maxwidth=835)
    diagram(d,row['diagram'])
    text(d,(980,210),'앞의 장면과 연결해서 이해하기',28,MUTED)
    d.rectangle((976,254,1864,757),outline=LINE,width=2)
    text(d,(64,803),'이 순서로 살펴봅니다',28,MUTED)
    image.save(folder/'overview.png')
    overlay=Image.new('RGBA',(1920,1080),(0,0,0,0));od=ImageDraw.Draw(overlay)
    for i,s in enumerate(row['steps']):
        x=65+i*600
        text(od,(x,850),f'{i+1:02}',31,[TEAL,YELLOW,GREEN][i],700)
        text(od,(x+67,843),s,38,WHITE,maxwidth=495)
        if i<2:arrow(od,(x+535,871),(x+575,871),MUTED,3)
    overlay.save(folder/'roadmap.png')
    save(folder/'layout.json',dict(window=[980,258,880,495],captionCenter=[960,970],maxContentBottom=900,
         conceptualOnly=True,nativeVideoClock=True,roadmapFrame=row['roadmapFrame']))
    return image

def main():
    rows=read(HERE/'plan.json')['episodes'];WORK.mkdir(parents=True,exist_ok=True)
    for r in rows:build(r)
    print('16 independent concept diagrams and timed roadmaps ready.')
if __name__=='__main__':main()
