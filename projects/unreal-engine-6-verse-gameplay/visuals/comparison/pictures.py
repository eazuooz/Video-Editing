"""Five additional scenes. The costs below reproduce the one dated worked case."""
from stage import Stage, BG, INK, MUTED, GOLD, TEAL, GREEN, RED, ORANGE, PANEL, FIELD, LINE, DIM, clamp, ease
from scenes import node

TITLES=[
 ('이래도 언리얼을 선택할까?', '같은 문 · 서로 다른 팀 조건'),
 ('Godot은 상용 게임에도 무료', 'Godot 4.7.2 실행 값 · 동작 도식'),
 ('Unity는 팀과 좌석을 본다', 'Unity C# 구현 예 · 2026.11.05 기준'),
 ('같은 게임의 엔진 비용', '2026.11.05 현행 조건 · 미국 달러'),
 ('우리 팀에 남는 선택', '제작 조건 비교')]

def floorplan(g,x,y,scale=1,rooms=6):
    g.p.save();g.p.translate(x,y);g.p.scale(scale,scale)
    shapes=[(0,0,81,65),(80,0,95,65),(175,0,71,65),(0,65,112,79),(112,65,63,79),(175,65,71,79)]
    for j,(a,b,w,h) in enumerate(shapes[:rooms]):
        g.rect(a,b,w,h,FIELD,TEAL,3)
        g.line([(a+w*.36,b+h),(a+w*.59,b+h)],FIELD,5)
        g.line([(a+w*.37,b+h),(a+w*.37,b+h-w*.22)],GOLD,3)
    g.p.restore()

def thirteen(g,i,p,t):
    if i<2:
        g.lab(72,1)
        g.tag(125,298,'방금 만든 문')
        g.text(1164,373,'도구를 바꿔도',46,MUTED,True)
        g.text(1161,469,'목표는 같다',63,GOLD,True)
        g.text(1165,611,'입력  →  열쇠 확인  →  열기',31,TEAL,True,maxw=601)
        return
    g.tag(99,286,'엔진을 고를 때 함께 보는 것')
    if i<4:
        for j,(x,title,sub) in enumerate([(265,'Unreal Engine 5','액터 · 블루프린트'),(855,'Godot','노드 · 시그널'),(1446,'Unity','게임 오브젝트 · 컴포넌트')]):
            g.door(x,736,.96,72*ease(p*2.2) if i==2 else 72)
            g.text(x+72,349,title,51,[GOLD,TEAL,GREEN][j],True,True,'center')
            g.text(x+80,788,sub,31,INK,True,align='center')
        return
    if i==5:
        g.picture('road-1.jpg',103,369,838,432)
        g.tag(1022,354,'포트나이트 안에 배포한다면',GOLD)
        g.bank(1029,455,[('UEFN에서 제작','게임이 실행될 환경에서 작업'),('바로 플레이 테스트','플레이어가 볼 결과 확인')],1,746,143)
        return
    floorplan(g,118,430,2.35,6 if i==4 else 1)
    g.tag(954,363,'이미 만든 게임' if i==4 else '이제 만드는 첫 방',GOLD)
    g.bank(961,472,[('지도 · 캐릭터','다시 만들어야 하는 양'),('조명 · 애니메이션','팀이 이미 다룰 수 있는 도구'),('다른 후보','Godot과 Unity의 제작 방식')],1 if i==4 else 2,810,118)

def device_tree(g,x,y):
    g.tag(x,y,'Door.tscn')
    names=[('Door','Node3D'),('Hinge','Node3D'),('Leaf','Node3D'),('Switch','Button')]
    for j,(name,role) in enumerate(names):
        row=y+76+j*70
        inset=[0,60,119,60][j]
        if j:
            g.line([(x+inset-26,row-16),(x+inset-26,row+19),(x+inset-5,row+19)],LINE,3)
        g.text(x+inset,row,name,37,TEAL,True,True)
        g.text(x+322,row+1,role,29,MUTED,False,True)

def fourteen(g,i,p,t):
    if i<2:
        device_tree(g,102,299)
        g.line([(635,297),(635,831)],LINE,2)
        g.tag(705,298,'Switch의 pressed 시그널')
        g.text(710,386,'$Switch.pressed.connect(_on_switch_pressed)',40,TEAL,True,True,maxw=1036)
        g.text(710,472,'if has_key:',42,GOLD,True,True)
        g.text(710,545,'$Hinge.rotation.y = deg_to_rad(90.0)',37,INK,False,True,maxw=1060)
        g.arrow(735,684,1022,684,TEAL,ease(p*3) if i==1 else .3)
        g.text(1043,636,'열쇠 없음   0°',34,MUTED,True)
        g.text(1043,705,'열쇠 있음  90°',42,GREEN,True)
        g.text(705,801,'실제 신호 호출 두 번으로 확인한 경첩 회전',30,MUTED)
        return
    g.tag(103,290,'MIT 라이선스')
    g.text(100,376,'Godot',63,TEAL,True,True)
    g.text(99,466,'$0',141,GOLD,True,True)
    g.text(109,663,'엔진 사용료',45,INK,True)
    g.line([(761,321),(761,828)],LINE,2)
    items=[('개발자 좌석','1명 또는 여러 명  ·  좌석료 $0'),('게임 매출','게임이 팔려도 엔진 로열티 $0'),('소스 공개 · 수정 가능','배포할 때 저작권·라이선스 안내를 포함')]
    focus=0 if i<=3 else 1 if i==4 else 2
    g.bank(868,353,items,focus,906,137)

def fifteen(g,i,p,t):
    if i<2:
        g.tag(102,292,'Door 게임 오브젝트')
        g.door(214,733,1.1,74*ease(p*2) if i==0 else 74)
        g.text(111,784,'Transform  +  DoorSwitch',32,TEAL,True,True)
        g.line([(765,298),(765,831)],LINE,2);g.tag(827,297,'DoorSwitch.cs  /  C# 컴포넌트')
        g.text(827,399,'public void PressSwitch()',39,TEAL,True,True)
        g.text(827,481,'if (hasKey)',43,GOLD,True,True)
        g.text(863,557,'hinge.localRotation =',38,INK,False,True)
        g.text(888,620,'Quaternion.Euler(0f, 90f, 0f);',35,INK,False,True,maxw=859)
        if i==1:g.text(828,776,'기존 팀의 C# 코드 · 에셋을 재사용',34,GREEN,True)
        return
    g.tag(101,288,'자체 게임 팀 · 최근 12개월')
    for k in range(12):
        x=114+k*65
        g.rect(x,410,48,37,TEAL if k<round(12*ease(p*2)) or i>2 else LINE)
    g.text(108,492,'매출 + 투자금',53,INK,True)
    g.text(108,617,'$200,000',79,GOLD,True,True)
    g.text(110,733,'Personal 이용 기준',36,MUTED)
    g.line([(956,315),(956,832)],LINE,2)
    g.tag(1021,324,'미국 요금 · 연간 선결제')
    node(g,1024,419,732,125,'Personal   $0',TEAL,'합계 $200,000 이하')
    node(g,1024,607,732,125,'Pro   $2,310',GOLD,'기준 초과 시  ·  한 좌석 / 1년')
    if i>=3:g.rect(1017,412 if i==3 else 600,746,139,None,TEAL if i==3 else GOLD,4,6)

def sixteen(g,i,p,t):
    g.tag(101,286,'두 명  ·  Steam 단독 판매  ·  첫 분기 누적 총매출 $1,200,000')
    x,y=115,396;cols=[(0,'Godot',TEAL),(4620,'Unity Pro',GREEN),(10000,'Unreal Engine',GOLD)]
    for j,(value,name,color) in enumerate(cols):
        yy=y+132*j;step=[2,3,5][j];visible=i>=step
        g.text(x,yy,name,45,color if visible else MUTED,True,True,maxw=423)
        g.line([(573,yy+43),(1434,yy+43)],LINE,2)
        if visible:
            length=850*value/10000*(ease(p*2.5) if i==step else 1)
            if value:g.rect(574,yy+24,max(1,length),38,color)
            else:g.circle(575,yy+43,9,None,color,4)
            g.text(1803,yy-4,f'\u0024{value:,}',55,color,True,True,'right')
        else:g.text(1803,yy,'—',41,DIM,True,align='right')
        notes=['좌석료·로열티 $0','$2,310 × 2좌석 × 1년','($1,200,000 − $1,000,000) × 5%']
        if visible:g.text(117,yy+60,notes[j],29,MUTED,False,True,maxw=1290)
        elif j==2 and i==4:g.text(117,yy+60,'제품 누적 총매출 중 첫 $1,000,000 제외',31,MUTED)
    g.line([(105,798),(1812,798)],LINE,2)
    g.text(106,818,'표준 게임 조건  ·  세금·스토어 수수료·인건비 및 별도 감면·계약 제외',30,MUTED,maxw=1700)

def seventeen(g,i,p,t):
    if i<3:
        g.tag(98,289,'각 팀이 이미 가진 것')
        rows=[('Unreal Engine','이미 만든 맵과 캐릭터','UE5로 완성할 때 보존할 작업량'),
              ('Unity','C# 경험과 에셋','팀이 다시 쓸 수 있는 코드와 도구'),
              ('Godot','비용 구조와 수정 자유','상용 엔진 사용료·로열티 $0 · MIT')]
        for j,(name,focus,detail) in enumerate(rows):
            yy=380+j*143;col=[GOLD,GREEN,TEAL][j]
            g.text(105,yy,name,49,col,True,True)
            g.text(642,yy,focus,43,INK,True)
            g.text(646,yy+59,detail,31,MUTED)
            g.line([(103,yy+122),(1805,yy+122)],LINE,2)
            if (i==1 and j==min(1,int(p*2))) or (i==2 and j==2):
                g.line([(104,yy+109),(104+420*ease(p*2),yy+109)],col,4)
        return
    g.tag(105,295,'두 후보에 같은 과제를 주기')
    for j,(x,label) in enumerate([(257,'후보 A'),(1212,'후보 B')]):
        g.text(x+85,365,label,41,GOLD if j==0 else TEAL,True,align='center')
        g.door(x,745,1.05,74*ease(p*2.25) if i==3 else 74)
    g.text(885,448,'첫 방',58,GOLD,True,align='center')
    g.text(887,542,'수정하고',38,INK,True,align='center')
    g.text(887,608,'목표 기기에서 실행',35,INK,True,align='center')
    g.text(936,802,'같은 입력  ·  열쇠 확인  ·  문 열기',36,TEAL,True,align='center')

DRAW=[thirteen,fourteen,fifteen,sixteen,seventeen]
MOTION={13:{2:1/2.2},14:{1:1/3},15:{0:.5,2:.5},16:{2:.4,3:.4,5:.4},17:{1:1,2:.5,3:1/2.25}}
def comparison(painter,index,beat,progress,t):
    index-=12
    stage=Stage(painter);stage.rect(0,0,1920,1080,BG)
    stage.header(*TITLES[index],index)
    DRAW[index](stage,beat,progress,t)
