from render_figures import *
import numpy as np

def palette():
    fig,ax=canvas('번호로 재질표를 읽고 칠한 칸의 번호만 바꾸기','자체 3×4 벽 · 3번 붉은 벽돌 / 9번 노란 벽돌이라는 가정')
    for row in range(3):
        for col in range(4):
            painted=(row,col) in [(1,1),(1,2)];x=80+col*100;y=320+row*100
            ax.add_patch(Rectangle((x,y),92,92,fc='#d8b237' if painted else '#a3573e',ec=INK,lw=2));text(ax,x+46,y+46,'9' if painted else '3',26,'white',ha='center')
    node(ax,750,300,350,120,'3 · 붉은 벽돌',RED,size=26);node(ax,750,600,350,120,'9 · 노란 벽돌',GOLD,size=26)
    arrow(ax,490,350,730,360,RED);arrow(ax,350,500,730,660,GOLD)
    text(ax,600,835,'모양·위치는 유지 / 참조하는 재질 항목이 바뀜',24,ha='center')
    save(fig,'palette_lookup','S12','자체 팔레트 조회. 같은 벽에서 두 칸의 참조만 3에서 9로 바꾸어 노란 재질을 사용합니다. 숫자는 예제용이며 실제 Teardown 파일의 고정 번호가 아닙니다.')
    fig,ax=canvas('작은 번호의 뒤에는 제한된 표의 자리가 있습니다','자체 12칸 팔레트 · 원본 3종 × 원본 포함 4변형 = 12칸')
    shades=[['#a3573e','#bd8050','#d0a34c','#d8b237'],['#536b79','#78827a','#a39b61','#c4b239'],['#477757','#728c55','#9eaa4b','#c6c13a']]
    for row in range(3):
        text(ax,85,345+row*185,f'재질 {row+1}',24)
        for col in range(4):
            x=300+col*205;y=280+row*185;ax.add_patch(Rectangle((x,y),165,130,fc=shades[row][col],ec=INK,lw=2));text(ax,x+82,y+65,'원본' if col==0 else f'변형 {col}',22,'white',ha='center')
    text(ax,600,900,'변형을 더 만들려면 자리·공유·저장 구조를 다시 선택',23,ha='center')
    save(fig,'palette_budget','S12','자체 팔레트 예산. 세 재질마다 원본과 세 변형을 두면 12칸을 모두 사용합니다. 실제 게임의 팔레트 크기가 아닌 작은 설명 모형입니다.')

def render():
    fig,ax=canvas('하나의 상태에서 서로 다른 두 표현을 그리기','자체 전투 · 피해·위치·행동 계산의 기준은 공통 상태')
    node(ax,340,230,520,150,'공통 상태\n위치 · 체력 · 행동 시작 시각',BLUE,size=25)
    node(ax,70,650,440,145,'스프라이트 표현\n방향·프레임 선택',GREEN,size=25);node(ax,690,650,440,145,'3D 모델 표현\n변환·클립 진행률',GOLD,size=25)
    arrow(ax,485,400,290,630,GREEN);arrow(ax,715,400,910,630,GOLD)
    save(fig,'dual_render_state','S15','자체 구조도. 논리 결과는 한 번 계산하고 두 표시가 같은 상태를 읽습니다. 실제 Diablo II: Resurrected 소스 구조를 추출한 도식은 아닙니다.')
    fig,ax=canvas('표시를 전환해도 행동의 시계를 처음으로 돌리지 않기','자체 공격 예 · 시작 0초에서 현재 0.4초까지 같은 진행 상태')
    for y,l,col in [(330,'논리 상태',BLUE),(520,'2D 표현',GREEN),(710,'3D 표현',GOLD)]:
        text(ax,70,y,l,25,col);ax.plot([310,1080],[y,y],color=LIGHT,lw=5);ax.add_patch(Circle((618,y),18,fc=col));text(ax,618,y+60,'0.4초',22,col,ha='center')
    ax.plot([618,618],[250,800],color=INK,ls='--',lw=2);text(ax,310,865,'0초 · 행동 시작',23);text(ax,980,865,'1초',23)
    save(fig,'render_timeline','S15','자체 행동 시각 대응. 세 줄 모두 같은 0.4초를 가리킵니다. 전환 후 새 애니메이션을 처음부터 재생하는 문제와 구별합니다. 실제 제품의 공격 길이 측정이 아닙니다.')

def sprite():
    fig,ax=canvas('캔버스를 잘라도 공통 기준점과 오프셋을 유지하기','자체 인형 · 부품 이미지의 중심을 맞추는 것과 같은 자세는 다름')
    for x,label,col in [(80,'몸통 그림',BLUE),(690,'무기 그림',GOLD)]:
        ax.add_patch(Rectangle((x,280),430,430,fc='#f1f5ef',ec=INK,lw=2));ax.plot([x+215,x+215],[300,690],color=LIGHT,ls='--');ax.plot([x+20,x+410],[650,650],color=LIGHT,ls='--');ax.add_patch(Circle((x+215,650),10,fc=RED));text(ax,x+215,760,label,25,col,ha='center')
    ax.add_patch(Rectangle((220,400),150,210,fc=BLUE));ax.plot([880,1030],[450,330],color=GOLD,lw=16);ax.add_patch(Circle((905,430),9,fc=GREEN,zorder=4));text(ax,600,870,'빨강 · 공통 발 기준 / 무기 위치는 손잡이 연결 좌표로 복원',21,ha='center')
    save(fig,'sprite_anchors','S16','자체 부품 좌표 모형. 같은 공통 기준점과 저장된 오프셋으로 부품의 위치를 복원합니다. 그림의 중앙을 단순히 일치시키는 방식과 구별합니다.')
    fig,ax=canvas('방향이 바뀌면 가리는 순서도 달라질 수 있습니다','자체 원형 몸통·막대 무기 모형 · 앞뒤 관계만 단순화')
    ax.add_patch(Circle((320,490),125,fc=BLUE));ax.plot([190,445],[530,375],color=GOLD,lw=22)
    ax.plot([775,1030],[530,375],color=GOLD,lw=22,zorder=1);ax.add_patch(Circle((900,490),125,fc=BLUE,zorder=2))
    text(ax,320,730,'앞을 볼 때\n무기가 몸통 앞',25,ha='center');text(ax,900,730,'뒤를 볼 때\n일부가 몸통 뒤',25,ha='center')
    save(fig,'sprite_order','S16','자체 가림 순서 비교. 같은 부품도 방향별 앞뒤 관계가 달라질 수 있습니다. 방향·행동별 정렬 자료가 필요한 이유를 단순 도형으로 보여 줍니다.')

def ranges():
    fig,ax=canvas('보이는 범위와 반응 범위와 공격 도달 범위를 나누기','자체 평면 모형 · 비율·거리는 실제 제품의 측정값이 아님')
    ax.add_patch(Rectangle((95,260),1020,480,fc='#f1f5ef',ec=BLUE,lw=3));ax.add_patch(Circle((460,500),200,fill=False,ec=GREEN,lw=3));ax.add_patch(Circle((460,500),300,fill=False,ec=GOLD,lw=3,ls='--'))
    ax.add_patch(Circle((460,500),17,fc=BLUE));ax.add_patch(Circle((710,500),21,fc=RED));arrow(ax,485,500,680,500,GOLD)
    text(ax,890,225,'사각형 · 카메라에 보임',23,BLUE,ha='center');text(ax,600,865,'초록 · 활성·반응 8 / 금색 · 공격 도달 12',22,ha='center');text(ax,900,620,'거리 10의 적\n공격은 닿지만\n활성 범위 밖',23,RED,ha='center')
    save(fig,'ranges_overlay','S18','자체 거리 가정. 플레이어로부터 10단위의 적이 화면과 공격 도달 범위 안이지만 8단위 활성 범위 밖에 있습니다. 실제 게임 AI가 원형 범위라는 주장은 아닙니다.')
    fig,ax=canvas('정상 조합만이 아니라 경계의 네 조합을 검수하기','자체 화면·활성 테스트 · 각 칸에서 피해·경고·이동의 의도와 실제를 비교')
    text(ax,490,250,'활성',26,GREEN,ha='center');text(ax,920,250,'비활성',26,GOLD,ha='center')
    for y,label in [(410,'화면 안'),(690,'화면 밖')]:
        text(ax,70,y,label,25,BLUE)
        for x,l,c in [(300,'반응·피해·갱신\n예상 결과 기록',GREEN),(730,'피해는 들어오는가\n들어오면 깨어나는가',GOLD)]:node(ax,x,y-100,390,200,l,c,size=23)
    save(fig,'range_matrix','S18','자체 경계 테스트 표. 화면 안팎과 활성 여부를 교차시켜 검사합니다. 모든 칸에 같은 정답을 강제하는 표가 아니라 프로젝트의 의도와 실제 처리의 일치를 확인하는 틀입니다.')

if __name__=='__main__':
    palette();render();sprite();ranges()
    (BASE/'figure-manifest-batch16.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
