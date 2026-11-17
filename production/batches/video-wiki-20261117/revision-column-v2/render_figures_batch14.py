from render_figures import *

def camera():
    fig,ax=canvas('화면을 움직이는 원인부터 나누어 봅니다','자체 청소 게임 · 기본 시점과 추가 연출을 따로 조절')
    for y,l,b,c in [(280,'직접 시점 조작','다음 구역을 찾아 바라보기',BLUE),(500,'도구 조준','작은 얼룩을 따라 목표 옮기기',GREEN),(720,'추가 카메라 연출','걷기·반동·충격의 흔들림',GOLD)]:
        node(ax,65,y-65,380,130,l,c,size=25);text(ax,495,y,b,23)
    save(fig,'camera_layers','D15','자체 카메라 원인 분류. 시점 이동·도구 조준·추가 연출을 나눠 같은 화면 움직임의 목적을 검사합니다. 모든 움직임을 하나의 강도로 줄이지 않습니다.')
    fig,ax=canvas('조준점이 움직여도 배경 기준점은 유지할 수 있습니다','자체 조준 분리 모형 · 두 화면의 카메라와 기둥은 같은 위치')
    for x,aim,label in [(70,220,'가까운 얼룩 A'),(660,1030,'가까운 얼룩 B')]:
        ax.add_patch(Rectangle((x,270),470,430,fc='#edf1e8',ec=INK,lw=2));ax.add_patch(Rectangle((x+95,290),50,390,fc='#b7c7b8'))
        ax.add_patch(Circle((aim,475),25,fill=False,ec=BLUE,lw=4));ax.plot([aim-40,aim+40],[475,475],color=BLUE,lw=2);ax.plot([aim,aim],[435,515],color=BLUE,lw=2)
        text(ax,x+235,760,label,24,ha='center')
    text(ax,600,845,'기둥의 상대 위치는 유지 · 조준 대상만 변경',24,GREEN,ha='center')
    save(fig,'aim_camera','D15','자체 화면 비교. 카메라를 고정한 채 다른 얼룩을 가리키므로 같은 기둥이 두 화면의 같은 상대 위치에 남습니다. 실제 게임이나 개인별 멀미 실험 결과는 아닙니다.')

def loadout():
    fig,ax=canvas('같은 두 도구도 상황이 달라야 선택할 이유가 보입니다','자체 물감 도구 모형 · 실제 장비의 수치·성능을 측정한 그림이 아님')
    for x,label,col in [(85,'좁고 긴 도구',BLUE),(675,'넓고 짧은 도구',GREEN)]:
        node(ax,x,245,440,100,label,col,size=25)
    ax.add_patch(Rectangle((170,470),300,35,fc=BLUE));ax.add_patch(Rectangle((760,420),140,170,fc=GREEN))
    text(ax,320,690,'먼 작은 표적\n도달할 수 있는가',26,BLUE,ha='center');text(ax,895,690,'가까운 넓은 벽\n빠르게 덮는가',26,GREEN,ha='center')
    save(fig,'loadout_tradeoff','D21','자체 도구 비교. 길고 좁은 도달 범위와 짧고 넓은 범위가 서로 다른 과제에서 이점을 갖도록 설정한 가설입니다. 실제 게임의 장비나 계산된 최적 성능을 뜻하지 않습니다.')
    fig,ax=canvas('선택과 시험 사이의 왕복을 짧게 만들기','자체 선택 화면 흐름 · 확정 전 선택은 원래 조합을 덮어쓰지 않음')
    for x,y,l,c in [(80,270,'후보 고르기',BLUE),(700,270,'같은 표적에 사용',GREEN),(700,630,'이전 조합과 비교',GOLD),(80,630,'적용 또는 복구',BLUE)]:node(ax,x,y,420,130,l,c,size=25)
    arrow(ax,515,335,685,335);arrow(ax,910,415,910,610);arrow(ax,685,695,515,695);arrow(ax,290,615,290,415)
    save(fig,'loadout_loop','D21','자체 장비 시험 순환. 고른 결과를 같은 조건에서 써 보고 적용하거나 원래 조합으로 돌아옵니다. 도구 변경·안내·저장이 같은 선택을 참조하는지도 확인합니다.')

def remix():
    fig,ax=canvas('채굴 기능의 수보다 이동 판단의 변화를 확인하기','자체 생존 맵 · 안전한 우회와 위험을 감수한 직선 경로의 비교')
    ax.plot([150,150,1040,1040],[650,320,320,650],color=GREEN,lw=5);ax.plot([150,1040],[650,650],color=GOLD,lw=5)
    ax.add_patch(Rectangle((545,550),110,200,fc='#c6b58b',ec=INK,lw=3));text(ax,600,780,'파낼 벽',24,ha='center')
    text(ax,600,250,'우회 · 더 긴 이동',25,GREEN,ha='center');text(ax,600,465,'직선 · 파는 동안 접근하는 적',25,GOLD,ha='center')
    ax.add_patch(Circle((150,650),22,fc=BLUE));ax.add_patch(Circle((1040,650),22,fc=GREEN))
    save(fig,'remix_choices','D22','자체 새 규칙 가설. 채굴이 단순한 추가 버튼을 넘어 이동 경로·위험 판단을 바꾸는지 시험합니다. 어느 쪽이 항상 유리하다면 선택 구조를 다시 점검합니다.')
    fig,ax=canvas('같은 조작에 다른 역할을 연결할 수도 있습니다','자체 코스 공유 구조 · 편집 버튼만으로 공유 경험이 완성되지는 않음')
    for y,l,b,c in [(285,'달리는 사람','이 도전을 어떻게 통과할까',BLUE),(505,'만드는 사람','어떤 도전을 건네줄까',GREEN),(725,'공유하는 사람','누가 찾고 어떻게 비교할까',GOLD)]:
        node(ax,65,y-65,345,130,l,c,size=25);text(ax,460,y,b,24)
    save(fig,'remix_roles','D22','자체 역할 변화도. 이동 규칙을 재사용해도 도전을 통과·제작·공유할 때 필요한 판단이 달라집니다. 각 경로를 실제로 이어 붙여 새 경험 가설을 검증합니다.')

def ai():
    fig,ax=canvas('세계에 있는 정보와 상대가 관측한 정보를 구별하기','자체 경비병 · 벽 뒤의 실제 좌표를 곧바로 추적 자료로 쓰지 않기')
    ax.add_patch(Circle((180,510),40,fc=BLUE));text(ax,180,625,'경비병',25,BLUE,ha='center')
    ax.add_patch(Rectangle((620,300),55,430,fc=MUTED));ax.add_patch(Circle((920,510),40,fc=GREEN));text(ax,920,625,'플레이어',25,GREEN,ha='center')
    arrow(ax,235,510,595,510,GOLD);text(ax,420,420,'벽이 시야를 차단',23,GOLD,ha='center')
    ax.add_patch(Circle((440,720),25,fill=False,ec=BLUE,lw=3));text(ax,440,805,'마지막으로 본 위치 → 여기부터 확인',23,BLUE,ha='center')
    save(fig,'ai_information','D26','자체 정보 제한 모형. 현재 보이지 않는 실제 위치와 마지막 관측 위치는 별도 자료입니다. 경비병은 마지막 지점을 확인한 뒤 수색하도록 설계할 수 있습니다.')
    fig,ax=canvas('공격의 약속과 빈틈을 시간 위에 드러내기','자체 적 공격 모형 · 모든 순간 최선 행동으로 바꾸지 않는 제약')
    for x,w,l,col in [(100,340,'준비',GOLD),(440,220,'공격',RED),(660,440,'회복',BLUE)]:
        ax.add_patch(Rectangle((x,400),w,140,fc=col));text(ax,x+w/2,470,l,27,'white',ha='center')
    text(ax,270,650,'단서를 보고\n피할 방향 판단',24,GOLD,ha='center');text(ax,850,650,'반격할 틈\n행동 제약 확인',24,BLUE,ha='center');arrow(ax,110,790,1090,790,INK);text(ax,600,850,'시간 →',23,ha='center')
    save(fig,'ai_commitment','D26','자체 공격 상태 예. 준비 신호와 공격·회복의 제약이 대응 기회를 만듭니다. 구간 폭은 개념 설명용이며 특정 게임의 프레임 측정값이 아닙니다.')

if __name__=='__main__':
    camera();loadout();remix();ai()
    (BASE/'figure-manifest-batch14.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
