from render_figures import *
import numpy as np

def marketing():
    fig,ax=canvas('관심을 만든 장면과 다음 행동이 이어지는가','자체 회전 퍼즐 홍보 흐름 · 같은 경험의 약속을 유지')
    for y,l,r,c in [(230,'짧은 소개','막힌 길 → 방 회전 → 통로 열림',BLUE),(450,'도착 페이지','회전하는 이유와 실제 조작 확인',GREEN),(670,'체험판','같은 규칙을 직접 사용',GOLD)]:node(ax,70,y,300,120,l,c,size=25);text(ax,420,y+60,r,23);arrow(ax,220,y+125,220,y+205,c,2) if y<670 else None
    text(ax,600,900,'각 단계에서 처음 본 사람이 무엇을 이해했는지 확인',24,ha='center')
    save(fig,'marketing_path','S43','자체 홍보 연결도. 소개·페이지·체험판이 방 회전이라는 같은 경험을 설명해야 다음 단계의 이탈 이유도 구체적으로 조사할 수 있습니다.')
    fig,ax=canvas('서로 다른 단계의 비율을 구별해 읽기','자체 가상 기록 · 같은 기간과 집계 정의를 가정')
    for x,l,n,c in [(60,'노출','1,000',BLUE),(440,'방문','100',GREEN),(820,'실행','20',GOLD)]:node(ax,x,340,320,160,l+'\n'+n,c,size=28)
    arrow(ax,230,620,600,620,BLUE);text(ax,410,580,'100 / 1,000 = 10%',22,ha='center');arrow(ax,600,760,980,760,GREEN);text(ax,790,715,'20 / 100 = 20%',22,ha='center');text(ax,600,870,'비율이 다루는 질문도 다름 · 원인을 이 숫자만으로 확정하지 않음',22,ha='center')
    save(fig,'marketing_rates','S43','자체 유입 예. 노출에서 방문 10%, 방문에서 실행 20%는 분모가 다릅니다. 시장 평균이나 실제 채널 성과가 아닙니다.')

def pitch():
    fig,ax=canvas('만들 가치와 만들 능력에 서로 다른 근거 붙이기','자체 회전 퍼즐 제안 · 확인한 것과 아직 모르는 것 나누기')
    node(ax,70,250,500,120,'경험의 가치',BLUE,size=28);node(ax,630,250,500,120,'실행 가능성',GREEN,size=28)
    for x,ls,c in [(90,['공간 역할이 바뀌는 매력','처음 본 사람이 규칙 이해?','다른 방도 풀고 싶은가?'],BLUE),(650,['회전·충돌은 작동','레벨 제작 속도는 미확인','작은 버전으로 비용 확인'],GREEN)]:
        for j,l in enumerate(ls):text(ax,x,460+j*135,l,23,c)
    text(ax,600,880,'칭찬·구현 성공·일정 추정은 같은 종류의 증거가 아님',24,ha='center')
    save(fig,'pitch_evidence','S44','자체 피치 근거. 경험의 매력에 대한 가설과 제작 가능한 범위에 대한 증거를 분리합니다. 아직 측정하지 않은 레벨 제작 속도는 미확인으로 남깁니다.')
    fig,ax=canvas('요청할 도움을 다음 결과에 연결하기','자체 협업 제안 · 지원을 받으면 무엇을 검증할지 설명')
    for y,l,r,c in [(240,'현재','회전·충돌 시제품',BLUE),(450,'필요한 작업','환경 아트 + 레벨 검수',GOLD),(660,'다음 결과','방 5개 · 규칙 이해와 제작 속도 확인',GREEN)]:node(ax,65,y,300,110,l,c,size=26);text(ax,410,y+55,r,23);arrow(ax,215,y+115,215,y+195,c,2) if y<660 else None
    text(ax,600,875,'큰 약속보다 확인할 산출물과 남은 위험을 함께 제시',24,ha='center')
    save(fig,'pitch_next_step','S44','자체 협업 요청. 현재 작동하는 기능에서 다음 검증 결과까지 필요한 작업을 연결합니다. 기간이나 비용을 실제 측정한 계획표는 아닙니다.')

def hook():
    fig,ax=canvas('무기 모양보다 회수 시간이 만드는 선택을 보여 주기','자체 부메랑 액션 · 던진 무기가 돌아오기 전에는 다음 공격 불가')
    for y,l,length,c in [(350,'짧게 던지기',260,GREEN),(650,'멀리 던지기',700,BLUE)]:
        ax.add_patch(Circle((180,y),35,fc=INK));arrow(ax,230,y-35,230+length,y-35,c,4);arrow(ax,230+length,y+35,230,y+35,GOLD,4);text(ax,70,y-120,l,26,c)
        for x in [400,600,800]:ax.add_patch(Circle((x,y),18,fill=False,ec=RED,lw=2))
        text(ax,550,y+105,'빠른 회수 · 짧은 범위' if length==260 else '긴 범위 · 긴 무방비 시간',23,c,ha='center')
    save(fig,'hook_action','S46','자체 무기 회수 선택. 짧은 던지기와 긴 던지기의 공격 범위·회수 시간 차이가 판단을 만드는 모형입니다. 거리와 시간의 실제 측정 궤적은 아닙니다.')
    fig,ax=canvas('서로 다른 소개가 같은 경험을 약속하는가','자체 게임 훅 · 문장과 화면과 조작을 따로 시험한 뒤 연결')
    for x,y,l,b,c in [(70,290,'이야기','빛을 던진 동안\n어둠을 버팀',BLUE),(720,290,'화면','빛의 왕복 경로\n무방비 상태',GOLD),(390,690,'행동','던질 거리 선택\n돌아올 때까지 회피',GREEN)]:node(ax,x,y,410,160,l+'\n'+b,c,size=23)
    ax.plot([480,720],[370,370],color=INK,lw=2);ax.plot([275,590],[465,675],color=INK,lw=2);ax.plot([920,590],[465,675],color=INK,lw=2)
    save(fig,'hook_consistency','S46','자체 훅 연결. 이야기의 설정, 왕복하는 빛의 시각 신호, 던지고 피하는 행동이 같은 위험과 선택을 설명하는지 확인합니다. 세 항목을 채우는 성공 공식이 아닙니다.')

def validation():
    fig,ax=canvas('같은 칭찬도 서로 다른 게임을 상상한 결과일 수 있습니다','자체 길 회전 퍼즐 설명 · 선호보다 예상 행동부터 듣기')
    node(ax,340,210,520,110,'길을 돌려 배달하는 퍼즐',INK,size=27);node(ax,65,580,480,150,'기대 A\n시간에 쫓겨 빠르게 회전',BLUE,size=24);node(ax,655,580,480,150,'기대 B\n멈추고 경로를 계획',GOLD,size=24);arrow(ax,480,340,300,560,BLUE);arrow(ax,720,340,900,560,GOLD)
    text(ax,600,850,'무엇이 그런 기대를 만들었는지 자료의 신호를 다시 확인',23,ha='center')
    save(fig,'pitch_expectations','S48','자체 기대 차이. 같은 자료를 보고도 빠른 조작과 느린 계획이라는 서로 다른 플레이를 상상할 수 있습니다. 이해 질문으로 이 차이를 먼저 드러냅니다.')
    fig,ax=canvas('각 단계에서 답할 수 있는 질문이 다릅니다','자체 검증 사다리 · 앞 단계의 긍정 반응을 뒤 단계의 보장으로 쓰지 않기')
    for i,(l,b,c) in enumerate([('제안 자료','어떤 플레이를 기대하는가',BLUE),('작은 실행물','규칙·입력·선택이 작동하는가',GREEN),('짧은 체험','반복하고 다음 문제를 할 것인가',GOLD),('제품 판단','가격·환경·전체 경험이 맞는가',RED)]):
        y=210+i*175;node(ax,65,y,330,110,l,c,size=25);text(ax,450,y+55,b,23)
        if i<3:arrow(ax,230,y+115,230,y+165,c,2)
    save(fig,'validation_ladder','S48','자체 질문별 검증도. 자료 이해, 실제 조작, 반복 체험, 제품 선택은 다른 증거를 필요로 합니다. 앞 단계의 칭찬을 구매 확정값으로 취급하지 않습니다.')

def demo():
    fig,ax=canvas('짧은 체험에도 학습과 활용과 완결을 배치하기','자체 회전 퍼즐 체험판 · 시간 비율은 정해진 성공 공식이 아님')
    for x,l,ob,c in [(70,'① 규칙 배우기','통로 하나 열기',BLUE),(450,'② 예상해 보기','상자 낙하 활용',GOLD),(830,'③ 스스로 조합','마지막 방 도달',GREEN)]:
        ax.add_patch(Rectangle((x,300),300,300,fc='#edf2e8',ec=c,lw=3));ax.plot([x+50,x+50,x+220],[550,400,400],color=c,lw=10);ax.add_patch(Circle((x+50,550),15,fc=INK));ax.add_patch(Rectangle((x+205,370),30,30,fc=GOLD));text(ax,x+150,680,l,23,c,ha='center');text(ax,x+150,760,ob,23,ha='center')
    save(fig,'demo_arc','S51','자체 체험판의 세 역할. 같은 회전 규칙을 처음 배우고, 결과를 예상하고, 스스로 조합하는 작은 완결을 설계합니다. 실제 게임의 레벨 캡처는 아닙니다.')
    fig,ax=canvas('완료율 하나 대신 어디에서 멈췄는지 확인하기','자체 관찰 지점 · 개인정보는 목적에 필요한 범위만')
    labels=['실행','첫 입력','회전 성공','첫 방 완료','최종 완료','종료']
    for j,l in enumerate(labels):
        x=65+j*185;node(ax,x,360,165,110,l,BLUE,size=21)
        if j<5:arrow(ax,x+168,415,x+182,415,BLUE,2)
    text(ax,600,620,'입력 전 중단 → 환경·시작 안내 확인',25,ha='center');text(ax,600,730,'특정 방에서 중단 → 단서·조작·버그 구별',25,ha='center');text(ax,600,840,'완료해도 선호는 다를 수 있음 → 짧은 질문과 함께 보기',23,ha='center')
    save(fig,'demo_measure','S51','자체 체험 관찰 지점. 실행부터 완료까지의 중단 위치로 다음 조사의 범위를 좁힙니다. 중단 자체가 모두 실패이거나 재미없음이라는 뜻은 아닙니다.')

def mastery():
    fig,ax=canvas('실패가 다음 시도를 바꿀 정보를 주는가','자체 점프 학습 고리 · 성공 표시 이전의 이해가 중요')
    for x,y,l,c in [(70,240,'목표 이해',BLUE),(720,240,'점프 시도',GOLD),(720,650,'결과 관찰',RED),(70,650,'방법 수정',GREEN)]:node(ax,x,y,350,120,l,c,size=28)
    arrow(ax,440,300,700,300);arrow(ax,895,380,895,630);arrow(ax,700,710,440,710);arrow(ax,245,630,245,380)
    text(ax,600,505,'무엇이 달라져서\n이번에는 성공했는가?',26,ha='center')
    save(fig,'mastery_loop','S55','자체 달성감 검수 고리. 목표·시도·관찰·수정이 이어지는지를 보고 플레이어가 성공의 이유를 설명할 수 있는지 확인합니다.')
    fig,ax=canvas('도움의 범위에 따라 남는 판단도 다릅니다','자체 발판 예 · 접근성 목표와 의도한 경험에 맞게 선택')
    for y,w,l,c in [(310,110,'좁은 발판',BLUE),(555,260,'착지 허용 폭 확대',GREEN)]:
        ax.plot([90,420],[y+90,y+90],color=INK,lw=5);ax.plot([720,720+w],[y+90,y+90],color=c,lw=10)
        t=np.linspace(0,1,100);ax.plot(400+400*t,y+90-180*4*t*(1-t),color=c,lw=3);text(ax,900,y+145,l,23,c,ha='center')
    text(ax,600,840,'발판을 넓혀도 점프 선택은 직접 할 수 있음',25,ha='center');text(ax,600,900,'목표까지 자동 이동하는 도움은 다른 경험',23,ha='center')
    save(fig,'mastery_assistance','S55','자체 착지 보조 비교. 발판 폭을 늘려 실패 부담을 낮추면서 점프 선택은 플레이어에게 남길 수 있습니다. 도움과 달성감의 관계를 보편적인 심리 법칙으로 단정하지 않습니다.')

if __name__=='__main__':
    marketing();pitch();hook();validation();demo();mastery()
    (BASE/'figure-manifest-batch24.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
