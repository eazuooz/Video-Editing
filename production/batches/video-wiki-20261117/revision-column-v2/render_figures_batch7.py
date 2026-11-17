from render_figures import *
import numpy as np

def analysis():
    fig,ax=canvas('본 사실과 이유에 대한 가설을 구별하기','자체 점프 분석 · 화면에서 확인한 것만으로 마음의 이유를 확정하지 않기')
    node(ax,75,265,465,240,'관찰한 사실\n발판 끝에서 멈춘 뒤\n점프하고 착지함',BLUE,size=25)
    node(ax,675,265,465,240,'이유에 대한 가설\n착지 공간이 좁아서\n조절에 집중했을까?',GOLD,size=25)
    arrow(ax,555,385,660,385,GOLD)
    node(ax,180,680,840,135,'다음 실험: 다른 조건은 유지하고 착지 너비만 변경',GREEN,size=24)
    arrow(ax,905,525,720,660,GREEN)
    save(fig,'analysis_observation','D07','자체 분석 예. 발판 앞에서 멈춘 사실과 멈춘 이유에 대한 해석을 나눕니다. 가설을 확인할 다음 실험에서 바꿀 조건 하나를 정하며, 관찰만으로 플레이어의 감정을 확정하지 않습니다.')
    fig,ax=canvas('기능 이름에서 옮길 판단을 골라내기','자체 설계 변형 · 같은 관계 일부를 가져와도 같은 게임이 되는 것은 아님')
    node(ax,180,235,840,120,'남길 판단: 정보를 보고 진입할 시점을 고르기',BLUE,size=25)
    for x,title,extra in [(65,'틈 건너기','공중 조절'),(435,'열리는 문 통과','통과 중 충돌'),(805,'순찰 피하기','발각 상태')]:
        node(ax,x,590,330,200,title+'\n추가 조건\n'+extra,GREEN,size=22)
        arrow(ax,600,375,x+165,580,GREEN)
    save(fig,'analysis_transfer','D07','자체 전이 실험도. 진입 시점을 고르는 판단을 점프·문·순찰에 각각 넣어 봅니다. 각 놀이에 새로 생기는 공중 제어·충돌·발각 조건도 기록해 같은 기능이나 같은 재미라고 단정하지 않습니다.')

def quest():
    fig,ax=canvas('길 두 개가 있을 때 선택할 근거도 함께 만들기','자체 나무 배달 퀘스트 · 거리는 설명용이며 실제 지도 실측이 아님')
    ax.plot([195,600,1005],[520,315,520],color=GOLD,lw=6)
    ax.plot([195,420,780,1005],[520,735,735,520],color=GREEN,lw=6)
    for x,l in [(195,'A 마을'),(1005,'B 벌목지')]:
        ax.add_patch(Circle((x,520),48,fc='#eef3ec',ec=INK,lw=3));text(ax,x,430,l,25,ha='center')
    text(ax,600,245,'짧지만 장애물 대응이 필요',25,GOLD,ha='center')
    text(ax,600,810,'멀지만 안전하게 이동',25,GREEN,ha='center')
    text(ax,600,520,'현재 자원·준비에 따라\n어느 길을 쓸지 판단',26,ha='center')
    save(fig,'quest_route','D08','자체 경로 비교. 마을과 벌목지를 잇는 두 길의 짧음·위험·안전 차이를 읽을 수 있게 합니다. 길이 두 개 있다는 사실만으로 의미 있는 선택이 보장되지는 않습니다.')
    fig,ax=canvas('전달 완료는 대사·재료·다리·보상과 연결됩니다','자체 상태 모형 · 표시를 다시 열 때마다 보상을 새로 주지 않기')
    node(ax,65,275,300,120,'미수락',BLUE,size=26);node(ax,450,275,300,120,'진행 중',GOLD,size=26);node(ax,835,275,300,120,'전달 완료',GREEN,size=26)
    arrow(ax,375,335,435,335);arrow(ax,760,335,820,335)
    text(ax,400,235,'수락',19,ha='center');text(ax,790,225,'조건 확인\n전달',19,ha='center')
    node(ax,240,620,720,180,'완료 전환에 맞춰 함께 처리\n재료 소비 · 다리 개방 · 보상 기록\n저장 후 다시 읽어도 상태 유지',GREEN,size=25)
    arrow(ax,980,415,735,600,GREEN)
    save(fig,'quest_state','D08','자체 퀘스트 상태와 연동 모형. 전달 완료 전환에 재료 소비·세계 변화·보상 기록을 연결합니다. 저장이 중간에 어긋나지 않는지, 완료 후 다시 열어도 중복 지급하지 않는지 실제 구현에서 검수해야 합니다.')

def reward():
    fig,ax=canvas('공통 기능과 개수에 따라 늘어나는 작업을 나누기','자체 초기 추정: 뷰어 3일 + 12개×0.5일 + 별도 검수 2일 = 11일')
    x=130;scale=85
    for days,label,c in [(3,'공통 뷰어\n3일',BLUE),(6,'개별 콘텐츠\n12 × 0.5 = 6일',GREEN),(2,'별도 검수\n2일',GOLD)]:
        w=days*scale;ax.add_patch(Rectangle((x,330),w,220,fc=c,alpha=.18,ec=c,lw=3));text(ax,x+w/2,440,label,24,c,ha='center');x+=w
    text(ax,600,665,'제작 일정의 정답이나 업계 단가가 아니라 가정입니다.',24,ha='center')
    text(ax,600,795,'첫 보상 하나를 끝까지 만들어 본 뒤 추정치를 고칩니다.',24,ha='center')
    save(fig,'reward_cost','D17','자체 작업 추정 모형. 공통 기능 3일, 개별 콘텐츠 12×0.5=6일, 별도 검수 2일을 가정한 총 11일입니다. 업계 평균이나 실제 프로젝트 일정이 아니며 첫 완성 경로를 통해 추정치를 갱신해야 합니다.')
    fig,ax=canvas('조건 달성과 지급 완료를 같은 표시로 뭉개지 않기','자체 보상 지급 구조 · UI는 저장된 결과를 읽어 보여 줍니다')
    node(ax,70,240,400,125,'조건 달성 확인',BLUE,size=26)
    node(ax,710,240,420,125,'보상 ID로\n기존 소유 확인',GOLD,size=25)
    arrow(ax,485,302,690,302)
    node(ax,70,625,400,125,'미소유일 때\n지급 · 소유 기록',GREEN,size=25)
    node(ax,710,625,420,125,'완료 화면\n상태를 읽어 표시',BLUE,size=25)
    arrow(ax,820,385,315,600,GREEN);arrow(ax,485,687,690,687,BLUE)
    text(ax,600,855,'이미 소유했다면 중복 지급하지 않고 결과를 표시',24,ha='center')
    save(fig,'reward_grant','D17','자체 지급 모형. 조건 달성, 소유 확인, 지급 기록, 화면 표시를 나눕니다. 소유 확인 후 기록의 저장 경계와 실패·재시도 처리는 프로젝트 구조에 맞게 검증해야 합니다.')

def pitch():
    fig,ax=canvas('되감기는 대상과 남는 상태를 같은 그림에 표시하기','자체 시간 퍼즐의 규칙 설명 · 완성된 게임이나 물리 검증 결과가 아님')
    for j,(y,boxx,label) in enumerate([(365,385,'상자를 오른쪽으로 옮긴 뒤'),(700,190,'상자만 이전 자리로 되감기')]):
        text(ax,65,y-130,label,26)
        ax.plot([90,1110],[y+40,y+40],color=INK,lw=3)
        ax.add_patch(Rectangle((boxx,y-45),90,85,fc='#dfc18b',ec=INK,lw=3))
        ax.add_patch(Circle((770,y-65),23,fc=GREEN));ax.plot([770,770],[y-40,y+15],color=GREEN,lw=12)
        ax.add_patch(Rectangle((1030,y-35),60,75,fc=BLUE))
        text(ax,790,y-82,'플레이어 유지',21,GREEN)
        text(ax,1060,y+88,'스위치 상태 유지',21,BLUE,ha='center')
    arrow(ax,420,620,250,620,GOLD,4);text(ax,335,515,'상자 기록만',21,GOLD,ha='center')
    save(fig,'pitch_scene','D18','자체 규칙도. 되감기 전후에 상자 위치만 이전 상태로 돌아가고 플레이어와 스위치 상태는 유지하도록 정한 아이디어입니다. 실제 플레이가 검증된 시연이나 퍼즐의 완성 해법을 나타내지 않습니다.')
    fig,ax=canvas('상대가 다시 설명한 플레이와 비교해서 고치기','자체 커뮤니케이션 절차 · 이해가 어긋난 관계에만 자료를 보충')
    for x,y,label,c in [(85,270,'한 장면 설명\n목표 · 행동 · 조건',BLUE),(695,270,'상대의 말로\n플레이를 다시 듣기',GREEN),(85,620,'어긋난 항목 찾기\n전체 재시도로 오해?',GOLD),(695,620,'그 관계의 그림 보충\n상자만 되감김',BLUE)]:node(ax,x,y,420,145,label,c,size=23)
    arrow(ax,520,342,680,342);arrow(ax,900,435,290,600,GREEN);arrow(ax,520,692,680,692)
    save(fig,'pitch_loop','D18','자체 피치 검수 절차. 상대가 되감기를 전체 재시도로 이해했다면 대상별 전후 상태를 보충하는 식으로 어긋난 관계를 고칩니다. 설명 길이만 늘리는 것으로 이해를 대신하지 않습니다.')

if __name__=='__main__':
    analysis();quest();reward();pitch()
    (BASE/'figure-manifest-batch7.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
