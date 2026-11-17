from render_figures import *
import numpy as np
from matplotlib.patches import Arc, Ellipse

def mirror():
    fig,ax=canvas('180도 회전과 한 축 반사는 다른 변환입니다','자체 위쪽 시점의 방향 벡터 · x는 오른쪽 / z는 그림 위쪽')
    for cx,title,dx,dz,col in [(230,'원래 방향',110,75,BLUE),(600,'180도 회전',-110,-75,GREEN),(970,'x축 좌표 반전',-110,75,GOLD)]:
        arrow(ax,cx-130,510,cx+140,510,MUTED,1);arrow(ax,cx,650,cx,355,MUTED,1)
        arrow(ax,cx,510,cx+dx,510-dz,col,5);text(ax,cx,270,title,24,col,ha='center')
        text(ax,cx,760,'(x, z)' if cx==230 else ('(-x, -z)' if cx==600 else '(-x, z)'),24,col,ha='center')
    save(fig,'mirror_rotate','A13','자체 x-z 평면 방향 비교. 수직축 주위 180도 회전은 (x,z)를 (-x,-z)로, 한 축 반사는 (-x,z)로 바꿉니다. 두 변환이 다른 관계임을 보여 주는 수학 모형이며 특정 캐릭터의 구현을 측정한 그림이 아닙니다.')
    fig,ax=canvas('반전 전에 함께 확인할 약속을 나누어 적기','자체 점검표 · 모든 항목을 반드시 같은 방식으로 처리해야 한다는 뜻은 아님')
    for y,title,body in [(270,'몸과 손','어느 면과 어느 손을 보여 줄까'),(440,'소품과 무늬','장비 부착 · 글자 · 비대칭 배지'),(610,'게임 규칙','공격 방향 · 방어 면 · 판정 위치'),(780,'전환 경계','공격 중 방향 전환을 언제 허용할까')]:
        node(ax,70,y-50,300,100,title,BLUE,size=25);text(ax,415,y,body,24)
    save(fig,'mirror_policy','A13','자체 반전 정책 점검표. 몸·소품·문양·게임 규칙·전환 경계가 어떤 약속을 따를지 명시하고 최종 결과의 일치를 확인합니다.')

def grip():
    fig,ax=canvas('물체 두께가 달라지면 감싸는 손 모양도 달라집니다','자체 접촉 단면 모형 · 인체 관절의 정확한 구조를 재현한 해부학 도식이 아님')
    for x,r,label in [(315,45,'얇은 손잡이'),(890,105,'두꺼운 손잡이')]:
        ax.add_patch(Circle((x,510),r,fc='#d6c3a1',ec=INK,lw=3))
        ax.add_patch(Arc((x,510),2*(r+40),2*(r+40),theta1=70,theta2=290,ec=BLUE,lw=10))
        ax.add_patch(Arc((x,510),2*(r+15),2*(r+15),theta1=-50,theta2=50,ec=GREEN,lw=8))
        text(ax,x,285,label,26,ha='center');text(ax,x,760,'파랑: 감싸는 쪽\n초록: 맞서는 접촉',23,ha='center')
    save(fig,'grip_contact','A15','자체 물체 단면과 접촉 관계 모형. 얇고 두꺼운 손잡이에 다른 감싸는 형태가 필요할 수 있음을 보이며 파랑·초록 곡선은 손가락의 실제 개수나 해부학 궤적을 재현하지 않습니다.')
    fig,ax=canvas('필요한 가변성에 맞춰 손 제어 방식을 고르기','자체 설계 비교 · 아래로 갈수록 무조건 좋은 방식이라는 순위가 아님')
    for y,title,body,col in [(300,'미리 만든 포즈','정확히 다듬기 쉬움 / 물체별 조합 관리',BLUE),(530,'포즈·굽힘 혼합','중간값 가능 / 중간 접촉도 검사',GREEN),(760,'접촉 보정 추가','변화 대응 / 떨림·제약·계산 검수',GOLD)]:
        node(ax,65,y-60,340,120,title,col,size=24);text(ax,440,y,body,22)
    save(fig,'hand_controls','A15','자체 잡기 구현 비교. 포즈 제작, 중간값 혼합, 접촉 보정의 역할과 추가 검수를 나눕니다. 필요한 화면 크기와 물체 변화에 맞춰 섞어 사용할 수도 있습니다.')

def hit():
    fig,ax=canvas('공간에서의 겹침과 활성 시간이 함께 필요합니다','자체 직선 경로 · 빨간 구간만 판정이 켜진 시간으로 가정')
    ax.plot([120,1100],[465,465],color=LIGHT,lw=5);ax.plot([414,561],[465,465],color=RED,lw=12)
    for t,col in [(.2,MUTED),(.37,RED),(.6,MUTED)]:
        x=120+t*980;ax.add_patch(Circle((x,465),19,fc=col));text(ax,x,360,f't = {t}',23,col,ha='center')
    ax.add_patch(Rectangle((430,425),100,80,fill=False,ec=GREEN,lw=3));text(ax,480,610,'표적 영역',25,GREEN,ha='center')
    text(ax,600,770,'활성: 0.3 이상 0.45 미만',26,RED,ha='center')
    text(ax,600,850,'같은 경로라도 활성 구간을 바꾸면 결과가 달라집니다.',23,ha='center')
    save(fig,'hit_space_time','A16','자체 경로·시간 모형. t=0~1의 직선 이동에서 0.3 이상 0.45 미만만 판정을 활성화한다고 가정했습니다. 표적 겹침과 해당 시각의 유효성을 함께 확인하며 상용 게임 판정을 측정한 값이 아닙니다.')
    fig,ax=canvas('두 끝점만 보면 중간에 통과한 표적을 놓칠 수 있습니다','자체 직선 이동 모형 · 회전하는 긴 무기 전체의 검사를 대신하지 않음')
    for x,label,col in [(200,'이전 검사 위치',BLUE),(1000,'다음 검사 위치',BLUE)]:
        ax.add_patch(Circle((x,470),48,fill=False,ec=col,lw=4));text(ax,x,325,label,24,ha='center')
    ax.add_patch(Rectangle((565,415),70,110,fc='#e8a299',ec=RED,lw=3));text(ax,600,625,'중간의 작은 표적',25,RED,ha='center')
    arrow(ax,260,470,940,470,GOLD,4);text(ax,600,765,'실제 이동은 두 검사 위치 사이도 지납니다.',25,ha='center')
    text(ax,600,850,'부피·회전·샘플 간격에 맞는 검사 방법을 따로 설계',23,ha='center')
    save(fig,'hit_sampling','A16','자체 누락 예. 이전·다음 위치의 둥근 검사 영역은 가운데 표적과 겹치지 않지만 이동 중에는 표적을 통과합니다. 구간 검사 등을 고려할 수 있으며 이 직선 그림 하나로 회전 무기의 모든 궤적이 해결되지는 않습니다.')

def rig():
    fig,ax=canvas('고정 길이 사슬은 회전만으로 길어지지 않습니다','자체 두 구간 팔 · 각 길이 1 / 최대 끝점 거리 2 / 목표 거리 2.5')
    shoulder=(300,520);ax.add_patch(Circle(shoulder,220,fill=False,ec=LIGHT,lw=2,ls='--'))
    ax.plot([300,410,520],[520,520,520],color=BLUE,lw=8)
    for x in [300,410,520]:ax.add_patch(Circle((x,520),12,fc=BLUE))
    ax.add_patch(Circle((575,520),17,fc=RED));text(ax,575,620,'목표',24,RED,ha='center')
    text(ax,360,430,'1',24,BLUE,ha='center');text(ax,465,430,'1',24,BLUE,ha='center')
    text(ax,900,440,'회전만으로는 닿지 않음\n길이 · 어깨 이동 · 목표를\n바꾸면 조건이 달라짐',24,ha='center')
    text(ax,600,850,'관절 각도 제한이 있으면 실제 가능 범위는 더 좁을 수 있습니다.',22,ha='center')
    save(fig,'rig_reach','A17','자체 고정 길이 팔 모형. 두 구간 길이가 각각 1이면 끝점의 최대 거리는 2이므로 거리 2.5의 목표에는 회전만으로 닿지 않습니다. 회색 원은 길이만 고려한 최대 범위이며 관절 제약과 실제 모델은 별도입니다.')
    fig,ax=canvas('끝점과 중간 윤곽은 다른 제어입니다','자체 제어점 비교 · 뼈 수가 많을수록 항상 좋은 리그라는 기준은 아님')
    for y,title,xx,yy,col in [(365,'두 구간 사슬',[150,580,1050],[365,225,365],BLUE),(735,'여러 중간 제어점',[150,330,510,690,870,1050],[735,620,670,820,800,735],GREEN)]:
        text(ax,65,y-170,title,25,col)
        ax.plot(xx,yy,color=col,lw=6)
        for x,v in zip(xx,yy):ax.add_patch(Circle((x,v),12,fc=col))
        ax.plot([150,1050],[y,y],color=LIGHT,lw=1,ls='--')
    save(fig,'rig_shape','A17','자체 윤곽 제어 모형. 위는 중간점 하나의 두 구간 형태, 아래는 여러 중간점으로 다른 윤곽을 정한 예입니다. 각각의 시작·끝점 관계는 같지만 사슬 길이·제약은 동일하게 가정하지 않았으며 관절 개수 증가의 성능 효과를 측정한 그림은 아닙니다.')

if __name__=='__main__':
    mirror();grip();hit();rig()
    (BASE/'figure-manifest-batch10.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
