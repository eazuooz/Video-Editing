from render_figures import *
import numpy as np

def practice():
    fig,ax=canvas('체력 0의 양쪽을 시험하면 조건의 뜻이 보입니다','자체 피해 계산 · 이후 체력 = max(0, 이전 체력 - 피해)')
    xs=[60,335,610,885];ws=[260,260,260,260]
    for x,w,l in zip(xs,ws,['이전 체력','피해','이후 체력','실패 여부']):node(ax,x,260,w,100,l,BLUE,size=23)
    for j,row in enumerate([['1','1','0','참'],['1','2','0','참'],['2','1','1','거짓']]):
        for i,(x,w,l) in enumerate(zip(xs,ws,row)):node(ax,x,400+j*150,w,110,l,RED if i==3 and l=='참' else GREEN,size=28)
    save(fig,'practice_boundaries','S68','자체 경계 입력 표. 피해를 뺀 뒤 0으로 제한하고 체력이 0 이하인지 판단합니다. 본문 함수의 반환값과 같은 결과입니다.')
    fig,ax=canvas('같은 경계 생각을 회복과 다른 자원에 옮겨 보기','자체 회복 · 체력 9에서 3 회복, 최대는 10')
    x=lambda v:120+80*v
    ax.plot([x(0),x(12)],[500,500],color=INK,lw=3)
    for v in [0,9,10,12]:ax.plot([x(v),x(v)],[480,520],color=INK,lw=2);text(ax,x(v),565,str(v),24,ha='center')
    ax.add_patch(Circle((x(9),500),17,fc=BLUE));ax.add_patch(Circle((x(12),500),17,fc=RED));arrow(ax,x(9),390,x(12),390,BLUE,4);text(ax,x(10),310,'9 + 3 = 12',27,ha='center');arrow(ax,x(12),690,x(10),690,GREEN,4);text(ax,x(10),770,'최대 10으로 제한',25,GREEN,ha='center');text(ax,600,880,'체력·탄약의 숫자 구조가 비슷해도 0의 게임 의미는 다를 수 있음',22,ha='center')
    save(fig,'practice_transfer','S68','자체 회복 경계. 산술 결과 12와 최대 체력 10을 구별하고 위 경계를 적용합니다. 피해의 아래 경계와 구조를 비교하는 연습입니다.')

def learning():
    fig,ax=canvas('만들 장면에서 필요한 질문을 거꾸로 찾기','자체 벽 반사 장면 · 각 실험을 통과한 뒤 다음 질문으로')
    for i,(a,b,c) in enumerate([('위치에 놓기','좌표는 어디에 저장?',BLUE),('시간에 따라 이동','속도 × 지난 시간은 얼마?',GREEN),('벽에 닿음 확인','중심 + 반지름이 경계를 넘었나?',GOLD),('방향 바꾸기','세로 벽 → 가로 속도 부호 반전',RED)]):
        y=215+i*175;node(ax,65,y,330,110,a,c,size=24);text(ax,435,y+55,b,22)
        if i<3:arrow(ax,230,y+115,230,y+165,c,2)
    save(fig,'learning_dependencies','S69','자체 의존 관계. 위치 표시, 시간 이동, 경계 검사, 속도 변경을 작은 실험으로 나누면 지금 필요한 개념과 다음에 배울 개념이 드러납니다.')
    fig,ax=canvas('세로 벽에서는 가로 성분의 부호를 바꿀 수 있습니다','자체 축에 평행한 벽 · 경사진 벽에 그대로 적용하는 일반 공식은 아님')
    ax.plot([900,900],[220,820],color=INK,lw=8);ax.add_patch(Circle((875,500),25,fc=GOLD));arrow(ax,425,800,865,507,BLUE,5);arrow(ax,865,493,425,200,GREEN,5)
    text(ax,280,750,'들어옴\nvx = +3, vy = +2',24,BLUE);text(ax,260,310,'나감\nvx = -3, vy = +2',24,GREEN);text(ax,970,510,'세로 벽',24,ha='center');text(ax,600,900,'위쪽을 +y로 정함 · 같은 크기의 위쪽 성분은 유지',23,ha='center')
    save(fig,'learning_reflection','S69','자체 반사 벡터. 오른쪽 위로 향하는 (3,2)가 세로 벽에서 왼쪽 위 (-3,2)로 바뀝니다. 두 화살표 기울기도 3:2 성분 비율로 그렸습니다.')

def tutorial():
    fig,ax=canvas('첫 방에서 가르칠 행동과 보이는 결과를 연결하기','자체 금속 상자 방 · 선택해 옮긴 뒤 출구까지 통로가 생김')
    for x,label,moved in [(80,'행동 전',False),(680,'행동 후',True)]:
        ax.add_patch(Rectangle((x,290),440,450,fc='#edf2e8',ec=INK,lw=3));ax.add_patch(Circle((x+75,650),25,fc=BLUE));ax.add_patch(Rectangle((x+350,550),70,100,fc=GOLD));ax.add_patch(Rectangle((x+200,400 if moved else 590),90,90,fc=GREEN));arrow(ax,x+110,650,x+340,650,BLUE,3) if moved else None;text(ax,x+220,815,label,26,ha='center')
    arrow(ax,545,510,650,510,GREEN,4);text(ax,600,235,'초록 상자를 위쪽 공간으로 옮김',25,GREEN,ha='center')
    save(fig,'tutorial_room_contract','DL01','자체 첫 방 설계. 행동 전에는 금속 상자가 출구 앞 경로를 막고, 옮긴 뒤에는 주인공과 출구의 연결이 보입니다. 게임 원본 레벨의 복원도가 아닙니다.')
    fig,ax=canvas('대기 시간만 보지 않고 행동 단계에 맞게 도움 주기','자체 힌트 상태 · 한 번 배운 뒤에는 불필요한 설명을 줄임')
    for y,l,b,c in [(220,'아직 발견 못 함','재질·대비로 조작 대상 강조',BLUE),(420,'대상 가까이 접근','선택 입력 표시',GREEN),(620,'선택했지만 이동 못 함','짧은 이동 예 또는 추가 안내',GOLD),(820,'혼자 다음 장애물 해결','학습 기록 · 같은 안내 축소',RED)]:node(ax,65,y-55,390,110,l,c,size=23);text(ax,500,y,b,22)
    save(fig,'tutorial_hint_states','DL01','자체 단계별 도움. 발견·선택·이동·재사용의 어느 연결이 끊겼는지에 따라 도움을 바꾸며, 정지 시간이 길다는 이유만으로 정답을 즉시 제시하지 않습니다.')

def jump():
    fig,ax=canvas('같은 높이 2m도 최고점까지의 시간은 다를 수 있습니다','자체 일정 중력 분석식 · 파랑 T=0.4초, 초록 T=0.8초')
    t1=np.linspace(0,.8,100);h1=10*t1-.5*25*t1*t1;t2=np.linspace(0,1.6,100);h2=5*t2-.5*6.25*t2*t2
    X=lambda t:150+t*580;Y=lambda h:780-h*220
    ax.plot(X(t1),Y(h1),color=BLUE,lw=4);ax.plot(X(t2),Y(h2),color=GREEN,lw=4);ax.plot([150,1100],[780,780],color=INK,lw=2);ax.plot([150,150],[260,780],color=INK,lw=2);ax.plot([150,1100],[340,340],color=MUTED,ls='--',lw=1.5)
    for t in [0,.4,.8,1.6]:text(ax,X(t),830,str(t),22,ha='center')
    text(ax,85,340,'2m',24);text(ax,1050,900,'시간·초',22,ha='center');text(ax,350,230,'빠르게 올라감',23,BLUE);text(ax,720,280,'천천히 올라감',23,GREEN)
    save(fig,'jump_height_time','DL02','자체 분석 곡선. 높이 2m, 최고점 시간 0.4초에는 v0=10·g=25, 시간 0.8초에는 v0=5·g=6.25입니다. 같은 높이에서 착지하는 총 시간은 각각 0.8초와 1.6초입니다.')
    fig,ax=canvas('같은 0.3초 유지라도 이륙 시점이 다릅니다','자체 두 입력 방식 · 누르기와 해제를 같은 시간축에 표시')
    for y,l,flight,c in [(330,'충전 뒤 출발',.3,BLUE),(640,'즉시 출발',0,GREEN)]:
        text(ax,65,y-95,l,26,c);ax.plot([300,1100],[y,y],color=LIGHT,lw=3);ax.plot([300,600],[y,y],color=GOLD,lw=13);ax.add_patch(Circle((300+1000*flight,y),17,fc=c));text(ax,300+1000*flight,y+80,'이륙',24,c,ha='center')
    for x,l in [(300,'누름 · 0초'),(600,'뗌 · 0.3초')]:ax.plot([x,x],[240,740],color=MUTED,ls='--',lw=1.5);text(ax,x,850,l,23,ha='center')
    text(ax,950,540,'금색 · 버튼 유지',23,GOLD,ha='center')
    save(fig,'jump_input_timing','DL02','자체 입력 시간 비교. 금색 유지 구간 0~0.3초가 같아도 충전형은 해제 때 이륙하고 즉시형은 누를 때 이륙합니다. 게임별 세부 구현을 같다고 가정하지 않습니다.')

def frames():
    fig,ax=canvas('같은 네 간격의 합 64ms라도 기다림은 다릅니다','자체 시간도 · 집계 빈도 4 / 0.064 = 62.5회/초로 동일')
    for y,label,values in [(340,'A',[16,16,16,16]),(650,'B',[8,8,8,40])]:
        text(ax,65,y+50,label,30);x=180
        for i,v in enumerate(values):
            w=v*14;ax.add_patch(Rectangle((x,y),w,110,fc=RED if v==40 else [BLUE,GREEN,BLUE,GREEN][i],ec='white',lw=2));text(ax,x+w/2,y+55,str(v)+'ms',22,'white',ha='center');x+=w
    text(ax,600,865,'B의 긴 40ms 간격은 평균 빈도만 보면 드러나지 않음',24,ha='center')
    save(fig,'frame_pacing_equal_average','D01','자체 네 간격 비교. A 16×4=64ms, B 8+8+8+40=64ms로 같은 집계 빈도지만 B에는 긴 대기가 있습니다. 실제 게임 성능 그래프가 아닙니다.')
    fig,ax=canvas('한 입력 사건에서 반응까지 시간을 추적하기','자체 가상 시간 · 실제 장치 측정이나 모든 단계의 단순 직렬화를 뜻하지 않음')
    points=[(0,'버튼 누름'),(8,'입력 확인'),(12,'상태 반영'),(20,'화면 준비'),(25,'반응 표시')];X=lambda t:100+40*t
    ax.plot([100,1100],[500,500],color=INK,lw=3)
    for i,(t,l) in enumerate(points):
        x=X(t);ax.add_patch(Circle((x,500),12,fc=BLUE));text(ax,x,570,str(t)+'ms',22,ha='center');text(ax,x,330 if i%2==0 else 400,l,22,ha='center')
    arrow(ax,100,740,1100,740,GREEN,4);text(ax,600,825,'이 사건의 입력 → 표시: 25ms',27,GREEN,ha='center')
    save(fig,'frame_input_path','D01','자체 입력 사건의 시점 예. 누름 0ms에서 반응 표시 25ms까지를 추적합니다. 표시 FPS에서 이 지연을 역산하거나 실제 CPU·GPU 처리 시간을 단순 합산한 측정값이 아닙니다.')

def rewards():
    fig,ax=canvas('추가된 칸이 다음 탐험의 선택을 바꾸는가','자체 3칸 → 5칸 가방 · 실제 Stardew Valley 가방 규격과 다른 설명 모형')
    colors=[BLUE,GREEN,GOLD,RED,'#7857a1']
    for y,n,l in [(340,3,'이전 · 3개만 보관'),(650,5,'이후 · 5개 보관')]:
        text(ax,65,y-80,l,26)
        for i in range(5):
            x=160+i*190;ax.add_patch(Rectangle((x,y),155,125,fc='#edf2e8' if i<n else 'white',ec=INK if i<n else LIGHT,lw=2,ls='-' if i<n else '--'));ax.add_patch(Circle((x+77,y+62),28,fc=colors[i],alpha=1 if i<n else .25))
    text(ax,600,875,'보상 뒤 곧바로 공간을 활용할 상황에서 차이를 확인',24,ha='center')
    save(fig,'reward_before_after','D03','자체 가방 활용 비교. 같은 다섯 물건 중 이전에는 셋만 가져가고 확장 뒤에는 다섯을 보관하는 예입니다. 실제 게임 UI나 숫자를 변경한 화면이 아닙니다.')
    fig,ax=canvas('두 번 안에 얻을 확률 75%도 보장은 아닙니다','자체 독립 시행 · 매번 50%로 한 개 획득, 한 개만 더 필요')
    for i,(a,b) in enumerate([(1,1),(1,0),(0,1),(0,0)]):
        y=280+i*160
        for x,v in [(330,a),(600,b)]:ax.add_patch(Circle((x,y),40,fc=GREEN if v else RED));text(ax,x,y,'성공' if v else '실패',19,'white',ha='center')
        arrow(ax,385,y,545,y,INK,2);text(ax,65,y,'25%',24);text(ax,760,y,'필요 재료 확보' if a or b else '여전히 부족',24,GREEN if a or b else RED)
    text(ax,330,190,'1회',23,ha='center');text(ax,600,190,'2회',23,ha='center');text(ax,600,925,'네 경우 중 세 경우 확보 · 마지막 경우는 남아 있음',22,ha='center')
    save(fig,'reward_uncertainty_paths','D03','자체 확률 경로. 독립 50% 두 번의 네 순서는 각각 25%이며 세 순서에서 한 개 이상 얻습니다. 실제 게임의 드롭률이나 보장 횟수가 아닙니다.')

if __name__=='__main__':
    practice();learning();tutorial();jump();frames();rewards()
    (BASE/'figure-manifest-batch26.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
