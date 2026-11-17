from render_figures import *
import numpy as np

def tracks():
    fig,ax=canvas('한 공격을 세 개의 시간표로 나누기','자체 설계: 60칸/초 · 전체 48칸 · 이동은 36부터 허용')
    x=lambda f:260+f*17
    for y,label in [(300,'동작 표현'),(510,'명중 검사'),(710,'이동 전환')]:
        text(ax,55,y,label,23);ax.plot([x(0),x(48)],[y,y],color=LIGHT,lw=4)
    for a,b,c,label in [(0,12,BLUE,'준비'),(12,16,RED,''),(16,48,GOLD,'후속 · 복귀')]:
        ax.add_patch(Rectangle((x(a),265),x(b)-x(a),70,fc=c,alpha=.2,ec=c,lw=2))
        if label:text(ax,(x(a)+x(b))/2,300,label,22,c,ha='center')
    ax.add_patch(Rectangle((x(12),475),x(16)-x(12),70,fc=RED,alpha=.7))
    text(ax,x(14),420,'12 이상 16 미만',22,RED,ha='center')
    ax.add_patch(Rectangle((x(36),675),x(48)-x(36),70,fc=GREEN,alpha=.3,ec=GREEN,lw=2))
    text(ax,x(42),795,'이동 가능',23,GREEN,ha='center')
    for f in [0,12,16,36,48]:
        ax.plot([x(f),x(f)],[835,853],color=INK,lw=2);text(ax,x(f),888,str(f),20,ha='center')
    text(ax,55,885,'시간 경계',20)
    save(fig,'attack_tracks','A03','자체 공격 시간표. 클립은 0~48칸, 판정은 12 이상 16 미만, 이동 전환은 36부터 허용합니다. 서로 다른 줄의 끝이 같지 않으며 숫자는 상용 게임의 실측이 아닙니다.')
    fig,ax=canvas('중단된 공격은 끝 이벤트를 기다릴 수 없습니다','공격 식별자·판정 상태·맞힌 대상 기록을 함께 관리하는 자체 모형')
    node(ax,90,235,390,125,'공격 진입\n새 공격 ID',BLUE,size=25)
    node(ax,710,235,390,125,'활성 구간\n중복 명중 확인',RED,'#fff0ec',25)
    arrow(ax,490,295,700,295)
    node(ax,90,620,390,130,'정상 종료',GREEN,size=25)
    node(ax,710,620,390,130,'피격 · 사망 등\n중간 상태 이탈',GOLD,size=25)
    arrow(ax,900,375,900,600,GOLD);arrow(ax,710,370,475,600,GREEN)
    text(ax,600,845,'두 경로 모두: 판정 해제 · 이전 공격의 임시 상태 정리',24,ha='center')
    save(fig,'attack_cleanup','A03','자체 중단 처리 모형. 정상 종료뿐 아니라 피격·사망 등으로 일찍 떠날 때도 이전 공격의 활성 판정과 임시 상태를 정리합니다. 중단 뒤 클립 끝 이벤트가 오기를 기다리지 않습니다.')

def anticipation():
    fig,ax=canvas('도착 시간은 같게, 변화의 배분만 다르게','세로축은 A→B의 정규화 진행도 · 힘이나 실제 관절 각도가 아님')
    X=lambda t:180+t*4550;Y=lambda u:770-u*470
    u=np.linspace(0,1,100)
    ax.plot(X(u*.2),Y(u),color=MUTED,lw=4,label='')
    ax.plot(X(u*.2),Y(1-(1-u)**3),color=BLUE,lw=5)
    arrow(ax,180,780,1120,780,INK,2);arrow(ax,180,780,180,240,INK,2)
    text(ax,70,295,'B · 1',21);text(ax,70,770,'A · 0',21)
    text(ax,180,840,'0초',22,ha='center');text(ax,1090,840,'0.2초',22,ha='center')
    text(ax,470,300,'초반에 더 많이 변화',24,BLUE);text(ax,690,660,'고르게 변화',24,MUTED)
    ax.add_patch(Circle((1090,300),9,fc=INK))
    save(fig,'anticipation_curves','A04','자체 진행도 비교. 두 모형은 0.2초에 같은 준비 자세 B에 도착합니다. 파란 곡선은 초반의 변화량이 크고 도착할수록 정리되며, 판정 시각이나 실제 관절별 값을 직접 표시한 그래프는 아닙니다.')
    fig,ax=canvas('반응이 늦어 보이면 입력부터 화면까지 나누어 보기','클립의 첫 자세를 고치는 것과 전환을 기다리는 시간을 고치는 것은 다름')
    for x,y,label,c in [(80,270,'입력 수신',BLUE),(690,270,'상태 조건 통과',GREEN),(80,590,'새 클립 재생',BLUE),(690,590,'블렌드 뒤 화면',GOLD)]:node(ax,x,y,420,125,label,c,size=25)
    arrow(ax,510,332,680,332)
    arrow(ax,890,410,290,575,INK)
    arrow(ax,510,652,680,652)
    text(ax,600,850,'기록할 것: 입력 시각 / 전환 시작 / 첫 눈에 띄는 변화',24,ha='center')
    save(fig,'anticipation_pipeline','A04','자체 원인 분해도. 입력 수신, 상태 전환 조건, 클립 재생, 화면에서의 블렌드 결과를 나눕니다. 모든 지연을 애니메이션 클립 길이 하나로 판단하지 않습니다.')

def pose():
    fig,ax=canvas('화면에서 겹쳐도 깊이가 다르면 지나칩니다','같은 무기 경로와 표적을 옆과 위에서 본 자체 투영 모형')
    text(ax,300,240,'옆에서 본 화면',27,ha='center');text(ax,900,240,'위에서 본 공간',27,ha='center')
    ax.plot([100,500],[500,500],color=BLUE,lw=6);ax.add_patch(Circle((360,500),45,fc=RED,alpha=.4))
    arrow(ax,160,500,450,500,BLUE,4);text(ax,300,660,'깊이를 납작하게 보면 겹침',22,ha='center')
    ax.add_patch(Circle((930,580),45,fc=RED,alpha=.4));arrow(ax,700,440,1090,440,BLUE,4)
    ax.plot([930,930],[460,535],color=MUTED,lw=2,ls='--');text(ax,900,660,'깊이 방향으로 떨어진 경로',22,ha='center')
    text(ax,350,410,'표적',21,RED,ha='center');text(ax,1030,580,'표적',21,RED)
    text(ax,600,835,'공간 경로를 확인한 뒤 카메라에서 읽히는 자세를 고릅니다.',24,ha='center')
    save(fig,'attack_projection','A05','자체 직교 투영 비교. 수평 파란 선은 무기 경로, 붉은 원은 표적입니다. 옆에서 깊이를 압축하면 겹쳐 보이지만 위에서는 서로 떨어져 있습니다. 실제 게임의 충돌 형상이나 궤적 실측이 아닙니다.')
    fig,ax=canvas('몸 안에 겹친 팔은 윤곽에서 사라질 수 있습니다','같은 카메라의 자체 인체 모형 · 동작의 세기나 생체 역학 측정이 아님')
    for x,opened,label in [(310,False,'몸통과 겹친 손·무기'),(900,True,'외곽으로 드러난 손·무기')]:
        ax.add_patch(Circle((x,335),48,fc=INK));ax.add_patch(Polygon([(x-60,400),(x+60,400),(x+45,610),(x-45,610)],fc=INK))
        ax.plot([x-25,x-65],[600,760],color=INK,lw=18);ax.plot([x+25,x+70],[600,760],color=INK,lw=18)
        if opened:
            ax.plot([x+40,x+130,x+170],[420,450,390],color=INK,lw=17)
            ax.plot([x+170,x+195],[390,260],color=BLUE,lw=9)
            ax.plot([x-40,x-110,x-135],[420,475,530],color=INK,lw=17)
        else:
            ax.plot([x+40,x-15,x+10],[420,460,515],color=INK,lw=17)
            ax.plot([x+10,x+15],[515,410],color=BLUE,lw=9)
            ax.plot([x-40,x+10],[420,500],color=INK,lw=17)
        text(ax,x,850,label,22,ha='center')
    save(fig,'attack_silhouette','A05','자체 실루엣 비교. 왼쪽 손과 무기는 몸통 영역에 겹치고, 오른쪽은 바깥 윤곽과 빈 공간으로 구분됩니다. 실제 동작의 강약을 측정한 것이 아니며 어떤 각도에서도 오른쪽 자세가 정답이라는 뜻은 아닙니다.')

def follow():
    fig,ax=canvas('판정 끝 · 조작 재개 · 클립 끝은 세 시각입니다','자체 망치 공격: 판정 0.3초 / 이동 전환 0.6초 / 클립 0.8초')
    x=lambda t:250+t*1060
    for y,label,t,c in [(310,'판정 가능',.3,RED),(510,'이동 제한',.6,GREEN),(710,'클립 재생',.8,BLUE)]:
        text(ax,55,y,label,24,c);ax.plot([x(0),x(.8)],[y,y],color=LIGHT,lw=4)
        ax.plot([x(0),x(t)],[y,y],color=c,lw=10);ax.add_patch(Circle((x(t),y),12,fc=c));text(ax,x(t),y-65,f'{t}초'+(' · 이동 허용' if t==.6 else ''),24,c,ha='center')
    save(fig,'follow_ends','A06','자체 시간 비교. 붉은 줄은 0.3초까지 판정이 가능했던 시간, 초록 줄은 이동을 제한했던 0.6초까지, 파란 줄은 0.8초짜리 원래 클립의 길이입니다. 수치는 원리 설명용입니다.')
    fig,ax=canvas('마무리를 끝까지 보거나 다음 입력으로 이어 가기','허용 시점 뒤의 두 경로를 나눈 자체 상태 모형')
    node(ax,70,420,320,140,'공격 마무리\n아직 몸을 정리 중',GOLD,size=23)
    node(ax,720,250,390,125,'새 입력 없음\n복귀를 끝까지 재생',BLUE,size=23)
    node(ax,720,620,390,125,'이동 요청 있음\n달리기로 전환',GREEN,size=23)
    arrow(ax,400,450,705,315,BLUE);arrow(ax,400,530,705,680,GREEN)
    text(ax,600,850,'전환 직전·직후의 발 / 중심 / 무기 위치를 함께 검수',24,ha='center')
    save(fig,'follow_branches','A06','자체 분기 모형. 이동을 허용한 뒤 입력이 없으면 원래 복귀를 끝까지 보고, 이동 요청이 있으면 남은 동작을 달리기로 전환합니다. 실제 전환에서는 접지와 자세의 연속성을 함께 검수해야 합니다.')

if __name__=='__main__':
    tracks();anticipation();pose();follow()
    (BASE/'figure-manifest-batch5.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
