from render_figures import *
import numpy as np

def head():
    fig,ax=canvas('좌우 방향은 도착하고 중간 숙임은 정리됩니다','자체 회전 시간표 · 두 그래프는 같은 시간축 / 세로 범위는 다름')
    u=np.linspace(0,1,101);X=lambda t:240+850*t
    yaw=60*(3*u*u-2*u*u*u);pitch=10*np.sin(np.pi*u)**2
    for base,values,maxv,c,label in [(420,yaw,60,BLUE,'좌우 회전'),(805,pitch,10,GOLD,'숙임')]:
        text(ax,65,base-110,label,24,c);ax.plot([240,1090],[base,base],color=LIGHT,lw=2)
        ax.plot(X(u),base-values/maxv*190,color=c,lw=5)
        text(ax,220,base,'0',20,ha='right');text(ax,220,base-190,f'{maxv}도',20,ha='right')
    text(ax,240,880,'시작',21,ha='center');text(ax,1090,880,'끝',21,ha='center')
    save(fig,'head_curves','A18','자체 회전 모형. 좌우 회전은 0에서 60도로, 숙임은 중간에 10도에 도달한 뒤 0도로 돌아옵니다. 같은 시간축을 쓰되 세로 범위가 다른 두 그래프이며 실제 게임에서 추출한 곡선이 아닙니다.')
    fig,ax=canvas('최종 시선은 눈·머리·몸통의 관계로 확인하기','자체 제어 분리도 · 실제 인체의 허용 각도나 고정 배분 비율을 정한 표가 아님')
    for y,title,body,c in [(295,'눈','어떤 대상을 보고 있는가',BLUE),(525,'머리','몸에 비해 어떤 방향인가',GREEN),(755,'몸통','월드에서 어느 쪽으로 향하는가',GOLD)]:
        node(ax,90,y-60,300,120,title,c,size=27);text(ax,445,y,body,24)
    save(fig,'gaze_layers','A18','자체 시선 검수 계층. 눈의 대상, 머리의 상대 방향, 몸통의 월드 방향을 나누어 봅니다. 각 시스템의 최종 합성과 부모 움직임을 확인해야 하며 고정된 인체 각도 비율을 처방하지 않습니다.')

def ticks():
    fig,ax=canvas('그림 선택과 게임 상태 갱신, 화면 표시를 나누기','자체 모형: 그림 24장/초 · 게임 상태와 화면은 60회/초로 가정')
    X=lambda t:250+t*3300
    for y,label,rate,c in [(310,'그림 교체',24,GOLD),(535,'위치·규칙',60,BLUE),(760,'화면 표시',60,GREEN)]:
        text(ax,60,y,label,24,c);ax.plot([X(0),X(.25)],[y,y],color=LIGHT,lw=2)
        for t in np.arange(0,.2501,1/rate):ax.plot([X(t),X(t)],[y-25,y+25],color=c,lw=3)
    text(ax,250,870,'0초',22,ha='center');text(ax,X(.25),870,'0.25초',22,ha='center')
    save(fig,'tick_tracks','S13','자체 갱신 모형. 0.25초 안에 서로 다른 주기의 그림 선택과 게임 갱신·화면 표시가 들어갑니다. 개별 눈금은 경계 시각이며 컵헤드의 내부 코드나 모든 이벤트 주기를 추출한 도표가 아닙니다.')
    fig,ax=canvas('같은 그림을 유지하는 동안에도 위치는 변할 수 있습니다','자체 샘플: t=k/60 · 그림 번호=floor(24t) · 속도=60px/초')
    xs=[85,350,665,970]
    for x,label in zip(xs,['표시 k','시간 ms','그림 번호','위치 px']):text(ax,x,235,label,24,weight='bold')
    for k in range(7):
        y=325+k*78; vals=[str(k),f'{k*1000/60:.1f}',str((k*24)//60),str(k)]
        ax.plot([65,1135],[y+36,y+36],color=LIGHT,lw=1)
        for x,s in zip(xs,vals):text(ax,x,y,s,25,BLUE if x==970 else (GOLD if x==665 else INK))
    save(fig,'tick_samples','S13','자체 샘플 표. 60회/초의 표시 시각에서 24장/초 그림을 고르면 같은 그림 번호가 반복되지만 60px/초로 이동하는 위치는 매번 달라집니다. 시간은 표시용으로 반올림했으며 특정 게임 로그가 아닙니다.')

def chunks():
    fig,ax=canvas('운동 상태 두 덩어리와 보이는 몸의 역할을 나누기','자체 두 점 생물 · 연결 길이는 제약 / 팔다리·꼬리는 그 위의 표현')
    ax.plot([360,690],[370,610],color=GOLD,lw=6)
    for x,y,r,label in [(360,370,95,'A'),(690,610,80,'B')]:
        ax.add_patch(Circle((x,y),r,fc='#c6ddd0',ec=GREEN,lw=4));ax.add_patch(Circle((x,y),10,fc=INK));text(ax,x+35,y-35,label,26,ha='center')
    text(ax,615,360,'거리 제약',25,GOLD,ha='center')
    ax.plot([330,260,205],[430,555,590],color=BLUE,lw=7);ax.plot([650,720,770],[665,765,780],color=BLUE,lw=7)
    ax.plot([750,850,930,1010],[625,690,670,730],color=BLUE,lw=7)
    text(ax,1000,820,'별도 외형·목표',23,BLUE,ha='right')
    save(fig,'body_chunks','S20','자체 두 덩어리 생물 모형. 두 중심의 거리와 충돌을 운동 상태로 두고 팔다리·꼬리를 별도 표현으로 이어 봅니다. 레인 월드 코드와 실제 형상을 복원한 이미지가 아닙니다.')
    fig,ax=canvas('운동을 먼저 검수하고 표현을 한 층씩 연결하기','자체 절차적 보행 설계 · 손발 목표에는 지지 상태의 기억이 필요할 수 있음')
    for x,y,label,c in [(70,270,'두 덩어리 운동\n힘 · 충돌 · 거리 제약',BLUE),(700,270,'몸 방향과 상태\n걷기 / 공중 등',GREEN),(70,620,'손발의 목표\n지지 유지 / 새 디딤',GOLD),(700,620,'몸과 외형 그리기\n실제 카메라에서 검수',BLUE)]:node(ax,x,y,430,145,label,c,size=23)
    arrow(ax,515,342,685,342);arrow(ax,920,435,285,600,GREEN);arrow(ax,515,692,685,692)
    save(fig,'body_layers','S20','자체 검수 계층. 운동 구조를 먼저 확인하고 상태·손발 목표·외형을 차례로 연결합니다. 현재 점 좌표만이 아니라 지지하는 발 등 필요한 상태를 기억하는 설계도 검토합니다.')

def inertial():
    fig,ax=canvas('두 클립 혼합과 새 클립에 보정하기는 출발점이 다릅니다','자체 단일 값 모형 · 실제 포즈 회전과 엔진의 감쇠 공식을 그대로 재현하지 않음')
    text(ax,65,235,'크로스페이드 모형',27,BLUE)
    node(ax,90,300,400,120,'이전 A(t) + 새 B(t)\n둘의 비중을 계속 변경',BLUE,size=24)
    arrow(ax,505,360,685,360,BLUE)
    node(ax,700,300,410,120,'혼합 결과',BLUE,size=25)
    text(ax,65,565,'관성화의 보정 관점',27,GREEN)
    node(ax,90,635,400,140,'직전 차이·움직임 저장\n새 동작 B(t) 평가',GREEN,size=24)
    arrow(ax,505,705,685,705,GREEN)
    node(ax,700,635,410,140,'B(t) + 줄어드는 보정',GREEN,size=24)
    save(fig,'inertial_pipeline','S30','자체 전환 계산 구분. 위는 두 원본을 계속 평가하며 섞는 단순 모형, 아래는 직전 차이·움직임을 기억해 새 동작에 보정하는 관점입니다. 엔진 구현이나 쿼터니언 포즈 계산 전체를 이 상자 한 개로 대체하지 않습니다.')
    fig,ax=canvas('0으로 줄어드는 것은 보정값입니다','자체 각도 모형: 새 동작은 10도 고정 / 직전은 30도 / 차이 20도')
    u=np.linspace(0,1,100);c=20*(1-3*u*u+2*u*u*u);b=np.ones_like(u)*10;y=b+c
    X=lambda t:175+t*900;Y=lambda v:790-v*16
    ax.plot(X(u),Y(y),color=BLUE,lw=5);ax.plot(X(u),Y(c),color=GOLD,lw=4,ls='--');ax.plot(X(u),Y(b),color=GREEN,lw=3)
    text(ax,490,275,'최종 각도: 30 → 10도',24,BLUE)
    text(ax,800,450,'보정: 20 → 0도',24,GOLD,ha='center')
    text(ax,300,690,'새 동작: 10도',23,GREEN)
    arrow(ax,175,810,1120,810,INK,2);text(ax,1100,865,'시간',22,ha='right')
    save(fig,'inertial_offset','S30','자체 단일 각도 보정 그림. 새 동작을 10도로 고정하고 보정 20도를 0으로 줄이면 최종 각도는 30도에서 10도로 갑니다. 이 감쇠 곡선은 설명용이며 직전 속도·가속도까지 맞추는 실제 관성화 구현 공식을 재현하지 않습니다.')

if __name__=='__main__':
    head();ticks();chunks();inertial()
    (BASE/'figure-manifest-batch11.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
