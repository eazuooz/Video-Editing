from render_figures import *
import numpy as np

def dialogue():
    fig,ax=canvas('세계의 사실과 각 인물이 아는 사실은 다를 수 있습니다','자체 항구 대화 모형 · 게시판을 읽음과 문지기에게 말함은 별도 사건')
    for y,title,body,c in [(280,'세계','통행에는 증표가 필요하다',BLUE),(500,'주인공','게시판을 읽어 규칙을 알았다',GREEN),(720,'문지기','주인공이 읽었다고 전한 뒤에 안다',GOLD)]:
        node(ax,70,y-55,300,110,title,c,size=26);text(ax,420,y,body,24)
    save(fig,'dialogue_knowledge','D13','자체 대화 정보 분리도. 세계 규칙의 존재, 주인공의 지식, 문지기에게 전달한 기록을 구별합니다. 문지기가 다른 경로로 이미 알도록 설정했다면 그 정보 경로도 별도로 정의해야 합니다.')
    fig,ax=canvas('대사·조건·선택 뒤 상태를 한 줄에서 함께 검토하기','자체 증표 전달 예 · 완료 표시를 다시 열어도 증표를 중복 소비하지 않기')
    for y,title,body,c in [(290,'대사·선택','증표를 드리겠습니다',BLUE),(510,'노출 조건','미전달 + 현재 증표에 접근 가능',GOLD),(730,'선택 뒤 변화','소유 이동 · 전달 완료 · 입장 허용',GREEN)]:
        node(ax,70,y-55,300,110,title,c,size=26);text(ax,420,y,body,24)
    save(fig,'dialogue_rules','D13','자체 대사 조건 카드. 현재 접근할 수 있는지와 이미 전달했는지 검사한 뒤 선택지를 내고, 선택하면 소유·전달·입장 상태를 함께 반영합니다. 실제 상용 대화 엔진의 내부 구조를 추출한 그림이 아닙니다.')

def spectators():
    fig,ax=canvas('참가자 ID 하나에 여러 화면 단서를 일치시키기','자체 관전 정보 모형 · 겹침·탈락·재진입·카메라 전환에서도 확인')
    node(ax,400,230,400,120,'선택한 참가자 ID',BLUE,size=26)
    for x,label,col in [(65,'몸의 표식\n번호·모자',BLUE),(435,'목록 강조\n이름·번호',GREEN),(805,'추적 카메라\n같은 대상',GOLD)]:
        node(ax,x,615,330,150,label,col,size=25);arrow(ax,600,370,x+165,595,col,3)
    save(fig,'spectator_identity','D14','자체 관전 대상 연결 모형. 몸의 표식·명단·추적 카메라가 같은 참가자 ID를 참조하는지 검사합니다. 표시를 많이 넣는 것과 올바른 대상을 일관되게 가리키는 일은 다릅니다.')
    fig,ax=canvas('누구를 보느냐와 무엇이 위험하냐를 함께 보여 주기','자체 장애물 경주 화면 · 실제 게임 장면이나 경기 결과가 아님')
    ax.add_patch(Rectangle((100,620),300,90,fc='#b9c8ba',ec=INK,lw=3));ax.add_patch(Rectangle((710,565),330,145,fc='#b9c8ba',ec=INK,lw=3))
    ax.add_patch(Circle((315,440),28,fc=BLUE));ax.plot([315,315],[470,570],color=BLUE,lw=13);ax.plot([315,280],[570,620],color=BLUE,lw=10);ax.plot([315,350],[570,620],color=BLUE,lw=10)
    arrow(ax,355,450,820,410,GOLD,4);text(ax,590,330,'다음 목표와 틈',26,GOLD,ha='center')
    text(ax,315,350,'참가자 2',25,BLUE,ha='center');text(ax,550,760,'실패 영역',25,RED,ha='center')
    save(fig,'spectator_context','D14','자체 관전 화면 모형. 참가자 2와 다음 발판·중간 틈을 같은 관계로 보여 주어 지금의 위험과 목표를 읽게 합니다. 점프의 실제 가능 거리나 물리 계산을 제시한 그림은 아닙니다.')

def sequel():
    fig,ax=canvas('파일이 있다는 사실과 재사용할 수 있다는 결과를 나누기','자체 속편 기반 점검 · 새 환경에서 작은 완성 경로를 실제로 실행')
    for y,title,body,c in [(280,'기반 코드','새 기기·입력·규칙에서 작동하는가',BLUE),(500,'제작 도구','새 코스 편집 → 빌드가 이어지는가',GREEN),(720,'검수 경험','당시 조건과 새 조건이 어떻게 다른가',GOLD)]:
        node(ax,70,y-55,300,110,title,c,size=26);text(ax,420,y,body,23)
    save(fig,'sequel_audit','D19','자체 재사용 점검. 코드 파일·편집기·이전 경험이 존재한다는 사실과 새 조건에서 사용할 수 있는지를 나눕니다. 작은 실제 통합 경로로 재사용 계획을 검증합니다.')
    fig,ax=canvas('기존 운전 행동이 새 조건에서 다른 선택을 만드는가','자체 속편 경로 모형 · 갈림길 수만 늘렸다고 새 가치가 생기지는 않음')
    ax.plot([155,570,1030],[550,330,550],color=GOLD,lw=6);ax.plot([155,420,800,1030],[550,760,760,550],color=GREEN,lw=6)
    for x in [155,1030]:ax.add_patch(Circle((x,550),20,fc=INK))
    text(ax,590,250,'짧지만 미끄러운 노면',25,GOLD,ha='center');text(ax,590,840,'길지만 안정적인 노면',25,GREEN,ha='center')
    text(ax,590,545,'현재 차·위치·위험을 보고\n제동과 경로를 다시 판단',25,ha='center')
    save(fig,'sequel_choice','D19','자체 새 플레이 가설. 기존 제동·가속을 짧고 미끄러운 길과 길고 안정적인 길에서 다르게 사용하는지 시험합니다. 그림은 검증된 출시 게임이나 실제 성능 비교 결과가 아닙니다.')

def inputs():
    fig,ax=canvas('입력 장치와 게임의 행동을 한 층 나누어 연결하기','자체 상호작용 모형 · 어떤 키인가와 지금 문을 열 수 있는가는 다른 질문')
    node(ax,65,240,350,120,'키보드 E',BLUE,size=26);node(ax,65,650,350,120,'패드 버튼',GREEN,size=26)
    node(ax,550,440,330,130,'Interact 행동',GOLD,size=26)
    arrow(ax,430,310,535,470,BLUE);arrow(ax,430,705,535,550,GREEN)
    arrow(ax,895,505,1095,505,INK,3);text(ax,1070,360,'게임 규칙\n조건 검사',23,ha='center')
    save(fig,'input_action','D20','자체 입력 추상화 모형. 서로 다른 장치 컨트롤을 같은 Interact 행동에 연결하고 게임 규칙은 행동 요청의 조건을 검사합니다. 물리 키 이름과 행동의 실행 가능 여부를 분리합니다.')
    fig,ax=canvas('재설정은 실행·안내·저장을 함께 갱신해야 합니다','자체 입력 재설정 흐름 · 취소·중복 처리·기본값 복구도 별도 검수')
    for x,y,label,col in [(75,270,'새 입력 대기\n취소 경로 유지',BLUE),(700,270,'중복·허용 입력 확인\n정책에 따라 적용',GOLD),(75,620,'행동 연결 변경\n실제 입력 실행',GREEN),(700,620,'안내 갱신 · 저장\n다시 불러와 확인',BLUE)]:node(ax,x,y,425,145,label,col,size=24)
    arrow(ax,515,342,685,342);arrow(ax,910,435,285,600,GOLD);arrow(ax,515,692,685,692)
    save(fig,'remap_flow','D20','자체 재설정 모형. 새 입력 수신과 허용 정책, 실행 연결, 안내·저장을 함께 확인합니다. 도구 API를 사용했다는 사실만으로 중복 충돌·취소·복구·표시가 모두 해결되는 것은 아닙니다.')

if __name__=='__main__':
    dialogue();spectators();sequel();inputs()
    (BASE/'figure-manifest-batch13.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
