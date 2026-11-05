"""Twelve editable scenes. Times are read from the project narration timeline."""
from math import sin, pi
from stage import Stage, BG, INK, MUTED, GOLD, TEAL, GREEN, RED, ORANGE, PANEL, FIELD, LINE, DIM, ease, clamp

HEADERS=[
 ('문을 여는 규칙은 어디에 적을까?', '동작 설명 모형'),
 ('도쿄에서 교체를 예고한 세 가지', '2026.11.03 발표 내용 도식'),
 ('버튼에서 문까지, 선을 따라가면', 'UE5 예제 이미지 · 동작 설명도'),
 ('캐릭터가 물려받은 기능', 'UE 5.8 클래스 선언 · 공식 문서 이미지'),
 ('문 전체를 옮길까, 문짝만 돌릴까?', 'Scene Graph 구조 설명 모형'),
 ('문 백 개가 같은 규칙을 쓴다면', '프리팹 구조 설명도'),
 ('6월 로드맵과 11월 발표', '에픽 로드맵 · 두 발표의 계획 비교'),
 ('에픽이 전환을 선택한 이유', '발표 내용 도식 · 에픽 내부 관찰'),
 ('규칙 작성과 도구 사용', '에디터 작업 예시'),
 ('옮긴 뒤에도 같은 문일까?', '변환 계획 · 두 조건 검증 모형'),
 ('5.9 프리뷰와 6 얼리 액세스', '발표 시점 기준 일정'),
 ('같은 입력, 같은 결과', '동작 설명 모형')]

def label_block(g,x,y,number,title,detail,active):
    col=GOLD if active else TEAL
    g.text(x,y,number,29,col,True,True)
    g.text(x+75,y-5,title,40,INK,True)
    g.text(x+75,y+48,detail,31,MUTED)

def diagram_wire(g, a,b,col,progress=1):
    x1,y1=a;x2,y2=b;p=clamp(progress)
    elbow=(x1+x2)/2
    pts=[(x1,y1),(elbow,y1),(elbow,y2),(x2,y2)]
    lengths=[abs(elbow-x1),abs(y2-y1),abs(x2-elbow)]
    dist=sum(lengths)*p;out=[pts[0]]
    for k,length in enumerate(lengths):
        if dist>length:
            out.append(pts[k+1]);dist-=length
        elif length:
            frac=dist/length
            out.append((pts[k][0]+(pts[k+1][0]-pts[k][0])*frac,pts[k][1]+(pts[k+1][1]-pts[k][1])*frac));break
    if len(out)>1:g.line(out,col,5)
    g.circle(*out[-1],7,col)

def node(g,x,y,w,h,text,col,detail=None):
    g.rect(x,y,w,h,PANEL,LINE,2,6)
    g.rect(x,y,7,h,col)
    g.text(x+24,y+(10 if detail else (h-48)/2),text,38,INK,True,maxw=w-48)
    if detail:g.text(x+25,y+62,detail,28,col,maxw=w-46)

def frame1(g,i,p,t):
    opened=0 if i==0 else 74*ease(p*2.8) if i==1 else 74
    press=ease(p*2.8) if i==0 else 1
    g.lab(opened,press)
    g.tag(126,298,'스위치와 문')
    if i<2:
        g.bank(1155,315,[('입력','플레이어가 버튼을 누른다'),('조건','열쇠를 가지고 있는가?'),('결과','문이 열린다')],0 if i==0 else 2,640,122)
    else:
        g.tag(1148,300,'블루프린트의 실행선' if i<4 else 'UE6에서 규칙의 자리',TEAL)
        reveal=ease(p*1.8) if i==2 else 1-ease(p*1.5) if i==3 else 0
        for j,(label,col) in enumerate([('스위치 입력',TEAL),('열쇠 확인',GOLD),('문 열기',GREEN)]):
            y=371+j*134
            node(g,1172,y,540,80,label,col)
            if j<2 and reveal>0:g.arrow(1240,y+83,1240,y+130,TEAL,clamp(reveal*2-j),5)
        if i>=4:g.text(1172,785,'Verse  /  Scene Graph',38,GOLD,True,True)

def frame2(g,i,p,t):
    g.tag(98,291,'UE6 얼리 액세스부터 교체 예정',ORANGE)
    rows=[('Actors','레벨에 배치하는 기본 단위'),('Blueprints','노드를 연결하는 시각적 스크립팅'),('C++ Gameplay Framework','게임의 행동을 구성하는 클래스들')]
    for j,(title,sub) in enumerate(rows):
        ypos=371+j*139; col=GOLD if j==2 and i>=2 else INK
        g.text(105,ypos,title,45,col,True,True,maxw=850);g.text(107,ypos+59,sub,30,MUTED)
        g.line([(105,ypos+111),(945,ypos+111)],LINE,2)
    g.line([(990,291),(990,823)],LINE,2)
    g.tag(1045,293,'C++가 쓰이는 두 층')
    node(g,1050,382,706,130,'게임플레이',''+GOLD,'버튼 입력 → 조건 확인 → 문 열기')
    node(g,1050,573,706,130,'엔진 기반',TEAL,'빛 그리기 · 물리 충돌 계산')
    if i>=3:
        y=570 if i==3 else 377
        g.rect(1042,y,722,142,None,TEAL if i==3 else GOLD,4,7)
        g.text(1050,751,'엔진 기반은 C++ 사용' if i==3 else '게임플레이 작성 방식 전환',34,TEAL if i==3 else GOLD,True)
    elif i==1:
        row=min(2,int(p*3))
        y=371+row*139
        g.line([(106,y+100),(106+min(1,(p*3-row)*2)*797,y+100)],GOLD,4)

def frame3(g,i,p,t):
    if i<3:
        g.tag(99,286,'언리얼 설치본의 블루프린트 예제')
        g.picture('ClassBlueprint.png',96,343,876,472)
        g.bank(1050,365,[('문 액터','레벨에 배치하는 사물'),('겉모양','눈에 보이는 문짝과 문틀'),('충돌 범위','상호작용을 감지하는 영역')],0 if i<=1 else 2,710,128)
        return
    g.tag(98,281,'공식 예제 이미지')
    g.picture('DoorOpenShut.png',100,344,780,351)
    g.text(165,727,'닫힌 문',35,MUTED,True)
    g.text(615,727,'열린 문',35,GOLD,True)
    g.tag(949,281,'열쇠를 확인하는 조건 예시')
    node(g,950,420,257,105,'버튼 입력',TEAL)
    node(g,1310,420,390,105,'열쇠가 있나?',GOLD)
    diagram_wire(g,(1207,475),(1310,475),TEAL,ease(p*4) if i==3 else 1)
    g.arrow(1465,535,1465,607,GOLD,ease(p*3))
    g.line([(1465,603),(1280,603),(1280,645)],GREEN,4)
    g.line([(1465,603),(1630,603),(1630,645)],RED,4)
    g.text(1280,662,'있음 → 열기',35,GREEN,True,align='center')
    g.text(1630,662,'없음 → 닫힘',35,RED,True,align='center')
    if i>=4:
        g.text(952,757,'실행선과 분기',30,TEAL,True)
        g.picture('BP_Overview.png',1243,729,488,112)

def frame4(g,i,p,t):
    g.tag(97,289,'클래스 상속')
    rows=[('Actor','레벨에 배치'),('Pawn','플레이어·AI가 조종'),('Character','걷기·점프')]
    focus=0 if i<1 else 1 if i<3 else 2
    for j,(n,role) in enumerate(rows):
        x=104+j*56;y=363+j*133
        node(g,x,y,707-j*54,98,n,GOLD if j==focus else TEAL,role)
        if j<2:g.arrow(x+34,y+99,x+34,y+130,TEAL)
    g.tag(930,286,'엔진 5의 실제 선언')
    g.text(930,365,'Pawn.h   43',29,DIM,True,True)
    g.text(930,416,'class APawn : public AActor,',40,TEAL,True,True,maxw=835)
    g.text(930,470,'    public INavAgentInterface',35,MUTED,False,True,maxw=830)
    g.line([(928,549),(1804,549)],LINE,2)
    g.text(930,581,'Character.h   338',29,DIM,True,True)
    g.text(930,637,'class ACharacter : public APawn',39,GOLD,True,True,maxw=850)
    if i in (1,2,3):
        y=692 if i==3 else 469
        g.line([(930,y),(930+650*ease(p*2),y)],TEAL if i<3 else GOLD,4)
    if i>=4:
        g.picture('original-1-0.png',941,713,250,145)
        g.text(1220,750,'Gameplay Framework',38,INK,True,True,maxw=570)
        g.text(1220,805,'게임에 쓸 기본 역할을 제공',29,MUTED)

def frame5(g,i,p,t):
    shift=63*ease(min(p*2,1)) if i>=5 else 0
    angle=(69*ease((p-.47)*3) if i>=5 else 21*ease(p*2) if i==4 else 0)
    g.lab(angle,0,False,False,shift,34*ease(p*3) if i==3 else 0, i>=4)
    g.tag(125,298,'문 엔티티 / 설명 모형')
    if i==3:g.text(140,754,'겉모양 + 감지 + 규칙',32,TEAL,True)
    if i>=4:g.text(140,754,'주황색 축 = 경첩',32,ORANGE,True)
    g.tag(1140,300,'Scene Graph')
    node(g,1143,386,581,98,'부모 · 문 엔티티',GOLD)
    g.line([(1195,485),(1195,558),(1232,558)],TEAL,5)
    node(g,1233,505,530,110,'자식 · 문짝',TEAL,'경첩을 중심으로 회전')
    g.line([(1163,681),(1756,681)],LINE,2)
    if i>=4:
        g.text(1143,711,'부모 이동 → 문 전체',38,GOLD,True)
        g.text(1143,777,'자식 회전 → 문짝만',38,TEAL,True)
    else:
        g.text(1143,713,'컴포넌트',37,GOLD,True)
        g.text(1143,772,'모양   /   상호작용   /   규칙',32,INK,maxw=660)

def doors_array(g,x,y,cell,cols,rows,filled,alert=-1):
    for n in range(cols*rows):
        xx=x+(n%cols)*cell;yy=y+(n//cols)*cell
        col=RED if n==alert else TEAL if n<filled else LINE
        g.rect(xx+2,yy+1,cell*.60,cell*.82,FIELD,col,2.2)
        g.line([(xx+4,yy+cell*.82),(xx+cell*.57,yy+cell*.82)],col,2)
        g.circle(xx+cell*.44,yy+cell*.47,2.5,col)

def frame6(g,i,p,t):
    g.tag(97,285,'Verse로 작성하는 동작')
    g.key(146,414,1.65,GOLD)
    g.text(106,493,'열쇠가 있다면',53,INK,True)
    g.text(106,571,'문을 연다',64,GOLD,True)
    g.line([(105,694),(792,694)],LINE,2)
    g.text(106,729,'한 규칙을 원형에 저장',35,TEAL,True)
    if i<3:
        g.tag(961,285,'프리팹 인스턴스')
        filled=1 if i==0 else int(1+99*ease(p*2.4)) if i==1 else 100
        doors_array(g,971,362,45,10,10,filled)
        g.text(1482,430,str(filled),90,GOLD,True,True)
        g.text(1486,555,'개의 문',40,MUTED)
        if i>=2:g.text(1468,702,'같은 규칙',37,TEAL,True)
    else:
        g.picture('original-0-0.png',954,330,460,455)
        g.text(1440,405,'UEFN',54,TEAL,True,True)
        g.text(1440,490,'Verse',45,INK,True,True)
        g.text(1440,553,'Scene Graph',39,INK,True,True)
        g.text(1440,668,'현재 시험 가능',31,GOLD,True)

def frame7(g,i,p,t):
    g.picture('road-1.jpg',97,303,776,437)
    g.text(101,757,'The road to Unreal Engine 6',36,MUTED,True,True,maxw=770)
    g.tag(944,290,'에픽의 전환 계획')
    rows=[('2026.06','UE6 초기에 기존 체계 포함','이후 단계적으로 정리'),
          ('2026.11','얼리 액세스부터 제거','Actors · Blueprints · C++ Gameplay Framework')]
    for j,(date,title,sub) in enumerate(rows):
        y=378+j*231;active=(j==0 and i<2) or (j==1 and i>=2);col=GOLD if active else DIM
        g.circle(964,y+21,10,col)
        if j==0:g.line([(964,y+42),(964,y+209)],LINE,4)
        g.text(1003,y,date,33,col,True,True)
        g.text(1003,y+61,title,43,INK if active else MUTED,True,maxw=779)
        g.text(1003,y+130,sub,30,col,maxw=784)
    if i>=2:g.arrow(964,423,964,573,GOLD,ease(p*2.6) if i==2 else 1,5)

def frame8(g,i,p,t):
    if i<2:
        g.tag(97,286,'프로젝트 사이의 이식성')
        for j,(x,title) in enumerate([(263,'프로젝트 A'),(1190,'프로젝트 B')]):
            g.door(x,726,.92,21 if j else 0)
            g.text(x+60,773,title,39,TEAL if j else GOLD,True,align='center')
        g.arrow(621,536,1090,536,TEAL,ease(p*2.6) if i==1 else .4)
        g.text(851,450,'동작 · 콘텐츠',40,INK,True,align='center')
        return
    g.tag(100,288,'에픽 내부 생산성 관찰')
    g.text(103,385,'1.5–4×',109,GOLD,True,True)
    g.text(108,545,'프로그래밍',38,INK,True)
    g.text(108,607,'오류 추적',38,INK,True)
    g.text(108,669,'레벨 설계',38,INK,True)
    x=762;w=1000;y=638
    for n in range(5):
        xx=x+w*n/4;g.line([(xx,y-223),(xx,y+21)],LINE,2)
        g.text(xx,y+40,f'{n}×',30,MUTED,True,True,align='center')
    g.line([(x,y),(x+w,y)],MUTED,3)
    g.rect(x,y-69,w/4,44,TEAL);g.text(x,y-117,'기존 작업량 기준 1×',29,TEAL,True)
    frac=ease(p*3) if i==3 else (0 if i==2 else 1)
    start=x+w*1.5/4;end=start+w*2.5/4*frac
    g.line([(start,y-184),(end,y-184)],GOLD,10)
    for xx in [start,end]:g.line([(xx,y-200),(xx,y-169)],GOLD,5)
    g.text(start,y-252,'보고된 범위',31,GOLD,True)
    g.text(x,759,'동일 기준 대비 배수',32,MUTED)

def frame9(g,i,p,t):
    g.tag(101,292,'100개의 문에서 규칙 검색')
    count=int(100*ease(p)) if i==0 else 100
    doors_array(g,109,376,43,10,10,count,64 if count>64 else -1)
    if count>64:
        g.line([(318,652),(513,652),(595,582)],RED,3)
        g.text(580,511,'누락 1개',39,RED,True)
        g.text(580,573,'설명용 사례',26,MUTED)
    g.tag(889,292,'일을 나누는 방법')
    g.bank(902,375,[('개발자','게임 안에서 따를 열쇠 규칙'),('MCP','AI 도구 ↔ 에디터 기능 연결'),('Python','반복 검사를 스크립트로 실행')],0 if i<2 else 1 if i==2 else 2,885,132)
    g.text(927,798,'결과는 개발자가 확인',33,GREEN,True)

def frame10(g,i,p,t):
    if i<4:
        g.tag(99,294,'기존 자산의 이동')
        node(g,105,416,465,138,'Blueprints',TEAL,'기존 노드와 C++ 게임 코드')
        g.arrow(607,489,1268,489,GOLD,ease(p*2) if i==1 else 1)
        g.text(934,391,'AI 보조 변환 계획',37,GOLD,True,align='center')
        node(g,1291,416,463,138,'Verse',GREEN,'새 게임플레이 코드')
        g.line([(102,659),(1784,659)],LINE,2)
        msg=['블루프린트로 만든 기존 동작','에픽이 예고한 이전 지원','제공 방식은 아직 미정','포트나이트도 운영 중 코드 이전'][i]
        g.text(104,713,msg,44,INK,True)
        return
    g.tag(97,289,'이전 전후의 동작 검사')
    q=ease(p*2) if i==5 else 1 if i>=6 else 0
    for j,(x,a,title,col) in enumerate([(308,0,'열쇠 없음',RED),(1189,72*q,'열쇠 있음',GREEN)]):
        g.text(x-86,375,title,44,col,True);g.door(x,729,1,a)
        if j:g.key(x+222,468,.65,GOLD)
        g.text(x+14,776,'문이 닫혀 있다' if j==0 else '문이 열린다',36,INK,True)
    g.line([(927,365),(927,832)],LINE,2)

def frame11(g,i,p,t):
    g.tag(97,288,'2026–2027 발표 일정')
    g.line([(195,475),(1665,475)],LINE,5)
    for j,(x,version,date,color) in enumerate([(280,'UE 5.9','2026년 11월',TEAL),(1310,'UE 6','2027년 말 목표',GOLD)]):
        g.circle(x,475,15,color)
        g.text(x,362,version,72,color,True,True,align='center')
        g.text(x,517,date,40,INK,True,align='center')
    g.text(120,626,'11월 3일 발표의 다음 주',34,TEAL,True)
    g.text(120,682,'프리뷰 공개 예정',42,INK,True)
    if i>=2:g.text(120,752,'웹 타깃 · AI · 렌더링 · 애니메이션',33,MUTED,maxw=820)
    g.text(1090,626,'얼리 액세스',42,GOLD,True)
    if i>=3:
        g.text(1090,695,'정식판은 그 후 12–18개월',33,INK)
        g.text(1090,751,'6월 로드맵의 당시 예상',29,MUTED)
    if i<3:g.line([(145,478),(279,478)],TEAL,6)
    else:g.line([(287,475),(287+(1310-287)*ease(p*2.5),475)],GOLD,5)

def frame12(g,i,p,t):
    opening=72*(ease(p*2.4) if i==3 else .85 if i==0 else 0)
    press=ease(p*2.3) if i==0 else 1
    g.lab(opening,press)
    g.tag(125,298,'다시, 처음의 문')
    g.tag(1150,301,'작은 동작 하나로 비교')
    g.bank(1161,390,[('입력','스위치를 누른다'),('상태','열쇠가 있는지 확인한다'),('결과','문짝이 경첩을 따라 열린다')], i if i<3 else 2,635,125)
    g.text(1198,786,'UE5  →  UEFN · Verse',32,TEAL,True,maxw=580)

SCENES=[frame1,frame2,frame3,frame4,frame5,frame6,frame7,frame8,frame9,frame10,frame11,frame12]
def draw(painter,index,beat,progress,t):
    stage=Stage(painter);stage.rect(0,0,1920,1080,BG)
    title,kind=HEADERS[index];stage.header(title,kind,index)
    SCENES[index](stage,beat,progress,t)
