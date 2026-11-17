from render_figures import *
import numpy as np
from matplotlib.patches import Ellipse

def squash():
    fig,ax=canvas('높이를 줄이며 폭·깊이를 늘리는 자체 부피 모형','3D 축척의 곱을 1로 유지 · 그림은 정면 단면이며 깊이 값은 별도 표기')
    for x,sy,label in [(310,1,'기본'),(890,.5,'압축')]:
        sx=1/np.sqrt(sy);ax.add_patch(Ellipse((x,500),230*sx,230*sy,fc='#acd0d5',ec=BLUE,lw=4))
        text(ax,x,260,label,28,ha='center')
        text(ax,x,745,f'높이 {sy:.2f}\n폭·깊이 각각 {sx:.3f}',23,ha='center')
    text(ax,600,875,'폭 × 높이 × 깊이 = 1 · 2D 면적 보존과 구별',24,ha='center')
    save(fig,'squash_volume','A09','자체 3D 축척 모형의 정면 단면. 높이를 0.5배로 줄이고 폭·깊이를 각각 sqrt(2)배로 늘리면 세 축척의 곱이 1입니다. 그림의 정면 면적이 같다는 주장이 아니라 깊이까지 포함한 부피 배율 관계입니다.')
    fig,ax=canvas('전체 축척과 접촉을 고려한 목표 윤곽은 다릅니다','자체 압축 형태 비교 · 비슷한 폭·높이에서 아래쪽 표면을 다르게 배치')
    ax.plot([65,1140],[690,690],color=INK,lw=4)
    ax.add_patch(Ellipse((320,600),360,180,fc='#acd0d5',ec=BLUE,lw=4))
    pts=[(715,690),(755,570),(825,520),(920,515),(1020,560),(1075,690)]
    ax.add_patch(Polygon(pts,closed=True,fc='#b6d6c4',ec=GREEN,lw=4))
    text(ax,320,325,'전체를 같은 비율로 축척',25,BLUE,ha='center')
    text(ax,895,325,'부위별 목표 형태',25,GREEN,ha='center')
    text(ax,600,825,'기본형과 목표형 사이 값에서도 접촉·관통을 검수',24,ha='center')
    save(fig,'squash_contact','A09','자체 윤곽 비교. 왼쪽은 타원형 전체 축척, 오른쪽은 바닥 접촉 쪽을 평평하게 둔 별도 목표 형태 예입니다. 오른쪽은 설명용 다각형이며 실제 재질이나 물리적 압축을 계산한 결과가 아닙니다.')

def hit():
    fig,ax=canvas('몸의 자세 변화와 캐릭터 기준점 이동을 나누기','자체 디버그 모형 · 원·사각형은 설명용 충돌 표시이며 실제 게임 판정이 아님')
    for x,move,label in [(300,0,'기준점 유지 · 몸만 반응'),(860,100,'기준점도 오른쪽으로 이동')]:
        ax.add_patch(Rectangle((x-60,375),120,370,fill=False,ec=MUTED,lw=2,ls='--'))
        xx=x+move
        ax.add_patch(Rectangle((xx-60,375),120,370,fill=False,ec=GREEN,lw=3))
        ax.add_patch(Circle((xx+40,390),32,fc=INK));ax.plot([xx,xx+40],[640,435],color=INK,lw=12)
        ax.plot([xx,xx-45],[640,740],color=INK,lw=11);ax.plot([xx,xx+45],[640,740],color=INK,lw=11)
        ax.add_patch(Circle((xx,765),10,fc=GREEN));text(ax,x,850,label,22,ha='center')
        if move:arrow(ax,x,290,xx,290,GREEN,4)
    save(fig,'hit_root','A10','자체 위치·자세 분리도. 회색 점선은 이전 기준 영역, 초록은 현재 기준 영역입니다. 왼쪽은 같은 기준점에서 몸을 기울이고, 오른쪽은 기준점까지 이동합니다. 실제 상용 게임의 충돌 영역을 측정한 그림이 아닙니다.')
    fig,ax=canvas('피격 반응의 끝에서 현재 게임 상태를 다시 확인하기','자체 상태 모형 · 클립 끝만 보고 무조건 대기로 돌아가지 않기')
    node(ax,390,240,420,115,'피격 상태',RED,'#fff0ec',27)
    for x,y,label,c in [(70,570,'체력 없음\n사망',RED),(445,570,'공중 상태\n낙하 등으로 연결',BLUE),(820,570,'행동 복귀 가능\n현재 요청으로 연결',GREEN)]:
        node(ax,x,y,310,165,label,c,size=23);arrow(ax,600,375,x+155,550,c,3)
    text(ax,600,850,'추가 명중 · 벽 · 지면 이탈 · 중단 우선순위도 별도 검수',23,ha='center')
    save(fig,'hit_states','A10','자체 피격 복귀 상태도. 반응 후 사망·공중·행동 복귀 조건을 나누어 현재 상태에 맞게 이어 갑니다. 분기 우선순위와 추가 명중 처리 규칙은 프로젝트에 맞게 정해야 합니다.')

def interpolation():
    fig,ax=canvas('같은 시간 간격에 찍힌 점의 간격을 비교하기','자체 한 축 이동 · 시작과 끝, 종료 시각은 같고 중간 위치가 다릅니다')
    u=np.linspace(0,1,9)
    for y,label,values,c in [(375,'x = u · 일정한 이동',u,BLUE),(700,'x = u² · 뒤로 갈수록 빠르게',u*u,GREEN)]:
        text(ax,65,y-105,label,25,c);ax.plot([120,1100],[y,y],color=LIGHT,lw=3)
        for v in values:ax.add_patch(Circle((120+980*v,y),10,fc=c))
    text(ax,600,850,'점마다 같은 시간 차이 · 모인 구간은 위치 변화가 작음',24,ha='center')
    save(fig,'interpolation_spacing','A11','자체 한 축 보간 비교. 정규화 시간 0~1의 동일 간격 9개에서 위는 x=u, 아래는 x=u²로 위치를 구했습니다. 각 점 사이의 시간은 같고 위치 간격이 다르며 실제 캐릭터의 관절이나 카메라 실측이 아닙니다.')
    fig,ax=canvas('어느 시각에 어떤 값이 되어야 하는지 먼저 정하기','자체 단일 속성 시간표 · 손끝의 공간 궤적이나 힘을 직접 표시한 그래프가 아님')
    t=np.array([0,.18,.55,.72,1]);v=np.array([0,.4,.45,1,.2])
    X=lambda u:165+u*930;Y=lambda v:770-v*470
    ax.plot(X(t),Y(v),color=BLUE,lw=5);ax.scatter(X(t),Y(v),s=65,color=BLUE)
    for u,label in [(.18,'준비 형성'),(.55,'준비 유지'),(.72,'타격 시점')]:
        i=np.argmin(abs(t-u));ax.plot([X(u),X(u)],[Y(v[i]),790],color=LIGHT,lw=2,ls='--');text(ax,550 if u==.55 else X(u),470 if u==.55 else Y(v[i])-60,label,22,ha='center')
    arrow(ax,165,790,1120,790,INK,2);text(ax,1100,855,'시간',23,ha='right');text(ax,70,275,'값',23)
    save(fig,'interpolation_curve','A11','자체 단일 속성 예. 준비가 형성된 뒤 값 변화가 적은 시간을 두고 타격 시점으로 빠르게 이동한 뒤 복귀합니다. 점을 직선으로 이은 설명 모형이며 실제 클립의 보간 접선이나 무기 경로를 측정한 그래프는 아닙니다.')

def face(ax,x,y,mood='neutral',size=95,eyes=True,mouth=True):
    ax.add_patch(Circle((x,y),size,fill=False,ec=INK,lw=4))
    if eyes:
        for dx in [-35,35]:
            ax.add_patch(Ellipse((x+dx,y-20),18,24 if mood!='focus' else 14,fc=BLUE))
            if mood=='focus':ax.plot([x+dx-15,x+dx+15],[y-55,y-50],color=INK,lw=3)
    if mouth:
        xx=np.linspace(-35,35,20)
        yy=35+(12*(1-(xx/35)**2) if mood=='smile' else np.zeros_like(xx))
        ax.plot(x+xx,y+yy,color=GOLD,lw=4)

def faces():
    fig,ax=canvas('표정 프리셋보다 장면의 전후 관계를 먼저 만들기','자체 발견 장면의 세 시점 · 실제 사람의 감정을 판독하는 분류표가 아님')
    for x,mood,label,detail in [(230,'neutral','발견 전','주변을 보는 중'),(600,'focus','대상 확인','시선과 집중'),(970,'smile','발견 후','작은 만족')]:
        face(ax,x,490,mood);text(ax,x,285,label,28,ha='center');text(ax,x,730,detail,25,ha='center')
    arrow(ax,345,490,480,490,BLUE);arrow(ax,715,490,850,490,BLUE)
    save(fig,'face_beats','A12','자체 발견 장면의 관계도. 중립·대상 확인·작은 만족의 순서를 합의하기 위한 예이며 각 얼굴이 실제 사람의 고정된 감정 분류나 유일한 표현이라는 뜻은 아닙니다.')
    fig,ax=canvas('눈과 입을 따로 본 뒤 조합도 검수하기','자체 컨트롤 분리 모형 · 함께 쓸 때 표면과 인상이 어떻게 바뀌는지 확인')
    for x,eyes,mouth,label in [(230,True,False,'눈·시선만'),(600,False,True,'입·턱만'),(970,True,True,'둘을 함께')]:
        face(ax,x,490,'smile',eyes=eyes,mouth=mouth);text(ax,x,280,label,27,ha='center')
    text(ax,600,770,'극단값뿐 아니라 중간값·눈 감기·대사 조합도 검사',24,ha='center')
    save(fig,'face_combination','A12','자체 얼굴 컨트롤 분리도. 눈 쪽과 입 쪽의 역할을 따로 본 뒤 함께 적용한 결과를 검사합니다. 그림은 단순 선 모형이며 실제 모델의 표면 관통이나 표정 품질 검수를 대신하지 않습니다.')

if __name__=='__main__':
    squash();hit();interpolation();faces()
    (BASE/'figure-manifest-batch9.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
