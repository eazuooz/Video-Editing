from render_figures import *
import numpy as np

def material():
    fig,ax=canvas('작은 상태 규칙을 하나씩 연결해 보기','자체 물질 모형 · 실제 Noita의 모든 물리·최적화를 재현한 것이 아님')
    for j,(lab,col) in enumerate([('낙하',GOLD),('옆 이동',BLUE),('이웃 반응',RED)]):
        bx=65+j*390;text(ax,bx+150,255,lab,26,col,ha='center')
        for r in range(4):
            for c in range(3):ax.add_patch(Rectangle((bx+c*100,330+r*100),95,95,fc='#f1f5ef',ec=LIGHT))
        if j==0:
            ax.add_patch(Rectangle((bx+100,330),95,95,fc=GOLD));arrow(ax,bx+148,410,bx+148,500,GOLD)
        elif j==1:
            ax.add_patch(Rectangle((bx+100,530),95,95,fc=BLUE));ax.add_patch(Rectangle((bx+100,630),95,95,fc=MUTED));arrow(ax,bx+190,577,bx+285,577,BLUE)
        else:
            ax.add_patch(Rectangle((bx,530),95,95,fc=RED));ax.add_patch(Rectangle((bx+100,530),95,95,fc=GOLD));arrow(ax,bx+95,577,bx+140,577,RED)
    text(ax,600,850,'먼저 이동만 검수 → 그다음 물질 간 반응 추가',24,ha='center')
    save(fig,'material_steps','S24','자체 격자 규칙. 낙하·옆 이동·이웃 반응을 별도 실험으로 나누어 원인을 읽습니다. 색은 물질 종류와 상태를 구별하기 위한 범례이며 실제 게임 데이터가 아닙니다.')
    fig,ax=canvas('한 틱에서 읽기·후보 충돌·확정을 나누기','자체 이중 상태 모형 · 같은 빈칸에 두 물질이 가려는 경우도 처리')
    for y,l,b,c in [(280,'이전 상태 읽기','틱 시작의 이웃·빈칸 확인',BLUE),(500,'후보·충돌 해결','같은 칸의 중복 예약 처리',GOLD),(720,'다음 상태 확정','소멸·복제·중복 이동 검사',GREEN)]:node(ax,65,y-65,365,130,l,c,size=25);text(ax,475,y,b,23)
    save(fig,'material_tick','S24','자체 틱 단계. 이전 상태와 다음 상태를 나누어도 이동 후보의 충돌은 따로 해결해야 합니다. 이중 버퍼만으로 모든 물질 보존이 자동 보장되는 것은 아닙니다.')

def gravity():
    fig,ax=canvas('같은 높이도 반지름에 대한 비율은 달라집니다','자체 비교 · 큰 행성 R=100과 작은 행성 R=1, 같은 h=1')
    for y,l,formula,c in [(330,'큰 행성','r = 100+1 = 101\ng/g0 = (100/101)², 약 0.98',BLUE),(650,'작은 행성','r = 1+1 = 2\ng/g0 = (1/2)² = 0.25',GREEN)]:
        node(ax,65,y-75,300,150,l,c,size=26);text(ax,435,y,formula,26,c)
    text(ax,600,870,'표면에서의 높이 h와 중심 거리 r=R+h를 구별',24,ha='center')
    save(fig,'gravity_radius','S26','자체 정규화 수치. 표면 중력은 같게 맞추고 같은 높이 1에서 중심 거리 비율을 비교합니다. 실제 천체나 Outer Wilds의 측정값이 아닙니다.')
    fig,ax=canvas('표면 값이 같아도 멀어질 때의 감쇠는 다를 수 있습니다','자체 함수 g/g0=(R/r)^q · q=1과 q=2를 비교하는 학습 모형')
    px=lambda r:160+(r-1)*300;py=lambda g:770-g*470
    ax.plot([160,1060],[770,770],color=INK,lw=2);ax.plot([160,160],[280,770],color=INK,lw=2)
    rr=np.linspace(1,4,200)
    ax.plot(px(rr),py(1/rr),color=GREEN,lw=4);ax.plot(px(rr),py(1/rr**2),color=BLUE,lw=4)
    for r in [1,2,3,4]:text(ax,px(r),815,str(r),22,ha='center')
    text(ax,90,300,'1',22);text(ax,85,770,'0',22);text(ax,600,890,'중심 거리 r/R →',24,ha='center');text(ax,780,430,'q=1 · 더 완만한 비교',23,GREEN);text(ax,780,690,'q=2 · 역제곱 모형',23,BLUE)
    save(fig,'gravity_falloff','S26','자체 감쇠 함수 비교. 표면 r/R=1에서 같은 값으로 시작합니다. q=1을 실제 제품의 모든 천체 공식이라고 주장하는 그래프가 아닙니다.')

def belts():
    fig,ax=canvas('함께 움직이면 내부 간격은 유지될 수 있습니다','자체 길이 20·물건 폭 2 · 물건을 오른쪽으로 1단위 이동')
    for y,positions,label,c in [(350,[2,6,10,14],'이전',BLUE),(660,[3,7,11,15],'이후',GREEN)]:
        text(ax,65,y-65,label,25,c);ax.plot([160,1060],[y+55,y+55],color=INK,lw=3)
        for p in positions:ax.add_patch(Rectangle((160+p*45,y-45),90,90,fc=c));text(ax,160+p*45+45,y,str(p),20,'white',ha='center')
        gap='끝 간격 2 / 내부 2·2·2 / 끝 간격 4' if label=='이전' else '끝 간격 3 / 내부 2·2·2 / 끝 간격 3'
        text(ax,600,y+110,gap,23,c,ha='center')
    save(fig,'belt_free','S27','자체 동일 상태의 두 표현. 각 숫자는 물건 왼쪽 끝 좌표이며 폭은 2입니다. 위치는 모두 1 증가하지만 내부 세 간격은 유지됩니다. 양 끝 간격과 폭의 합은 길이 20입니다.')
    fig,ax=canvas('앞이 막히면 줄일 수 있는 내부 간격을 찾아야 합니다','자체 오른쪽 끝 막힘 · 맨 앞 물건은 x=18에서 더 갈 수 없음')
    for y,positions,label,c in [(350,[2,6,10,18],'이전',BLUE),(660,[3,7,11,18],'이후',GREEN)]:
        ax.plot([160,1060],[y+55,y+55],color=INK,lw=3);ax.plot([1060,1060],[y-75,y+75],color=RED,lw=7);text(ax,65,y-70,label,25,c)
        for p in positions:ax.add_patch(Rectangle((160+p*45,y-45),90,90,fc=c));text(ax,160+p*45+45,y,str(p),20,'white',ha='center')
        text(ax,600,y+110,'끝 간격 2 / 내부 2·2·6 / 끝 0' if label=='이전' else '끝 간격 3 / 내부 2·2·5 / 끝 0',23,c,ha='center')
    save(fig,'belt_blocked','S27','자체 막힘 추적. 앞 물건은 18에 유지되고 뒤 세 물건만 1씩 이동해 앞쪽 내부 간격이 6에서 5로 줄어듭니다. 단순 자유 흐름과 수정할 자료가 달라집니다.')

def hitboxes():
    fig,ax=canvas('공격·피격·이동 충돌은 서로 다른 질문입니다','자체 판정 모형 · 영역 이름보다 실제 처리에 쓰이는 역할을 확인')
    for x,y,l,c in [(65,280,'파랑 · 이동 충돌\n벽·바닥을 통과하는가',BLUE),(65,650,'초록 · 피격 영역\n위험을 받아들이는가',GREEN),(690,460,'빨강 · 공격 영역\n지금 상대에 피해를 주는가',RED)]:node(ax,x,y,445,150,l,c,size=24)
    save(fig,'hitbox_roles','S28','자체 영역 역할. 세 영역의 질문과 사용 조건은 다릅니다. 코드에서 Hitbox가 범용 도형 클래스 이름일 수도 있으므로 공격이라는 의미를 이름만으로 단정하지 않습니다.')
    fig,ax=canvas('같은 너비와 위쪽 기준에서 높이가 2만큼 다릅니다','공개 Celeste 일반 상태 값의 도형화 · 모든 상태의 수치가 같지는 않음')
    for x,col,label,h in [(160,BLUE,'이동용 영역\n8×11',11),(740,GREEN,'피격 영역\n8×9',9)]:
        ax.add_patch(Rectangle((x,280),240,330,fc='none',ec=LIGHT,lw=3,ls='--'));ax.add_patch(Rectangle((x,280),240,h*30,fc=col,alpha=.85));text(ax,x+120,750,label,26,col,ha='center')
    arrow(ax,1040,550,1040,610,GOLD,2,style='<->');text(ax,1050,650,'아래쪽 2',22,GOLD,ha='center')
    save(fig,'hitbox_sizes','S28','공개 코드의 일반 상태 8×11과 8×9를 같은 상단 오프셋으로 그린 비교입니다. 실제 캐릭터 그림을 사용한 장면이나 모든 상태의 피격 규칙을 뜻하지 않습니다.')

if __name__=='__main__':
    material();gravity();belts();hitboxes()
    (BASE/'figure-manifest-batch19.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
