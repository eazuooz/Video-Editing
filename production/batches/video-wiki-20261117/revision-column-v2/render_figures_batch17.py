from render_figures import *
import numpy as np

def movement():
    fig,ax=canvas('목적지 명령과 방향 명령은 우회 책임이 다릅니다','자체 장애물 장면 · 같은 위치에서 오른쪽 목표를 향하는 경우')
    for x in [70,670]:
        ax.add_patch(Rectangle((x,270),460,440,fc='#f1f5ef',ec=INK,lw=2));ax.add_patch(Rectangle((x+200,360),55,350,fc=MUTED));ax.add_patch(Circle((x+75,570),20,fc=BLUE));ax.add_patch(Circle((x+380,570),20,fc=GOLD))
    ax.plot([145,145,450,450],[570,320,320,570],color=GREEN,lw=4);arrow(ax,450,500,450,545,GREEN)
    arrow(ax,765,570,860,570,RED);text(ax,300,785,'목적지까지 경로 탐색\n게임이 우회로 선택',24,GREEN,ha='center');text(ax,900,785,'현재 오른쪽으로 입력\n막힌 뒤 방향은 직접 변경',24,RED,ha='center')
    save(fig,'destination_direction','S14','자체 명령 비교. 왼쪽은 통과 가능한 위쪽 경로를 계산하고, 오른쪽은 현재 방향으로 가다 벽에 막힙니다. 모든 컨트롤러 게임이 같은 정책을 사용한다는 뜻은 아닙니다.')
    fig,ax=canvas('중앙의 작은 입력과 적용할 속도 크기를 분리하기','자체 데드존 d=0.2 · 장치별 권장값이나 실제 측정값이 아님')
    x=lambda v:150+900*v;y=lambda v:760-480*v
    ax.plot([x(0),x(1)],[y(0),y(0)],color=INK,lw=2);ax.plot([x(0),x(0)],[y(0),y(1)],color=INK,lw=2)
    ax.plot([x(0),x(.2),x(1)],[y(0),y(0),y(1)],color=BLUE,lw=5);ax.plot([x(.6),x(.6)],[y(0),y(.5)],color=GOLD,ls='--');ax.add_patch(Circle((x(.6),y(.5)),10,fc=GOLD))
    for v in [0,.2,.6,1]:text(ax,x(v),y(0)+40,str(v),21,ha='center')
    text(ax,540,865,'입력 크기 m →',24,ha='center');text(ax,80,450,'적용\n크기',23,ha='center');text(ax,850,650,'(0.6−0.2) / 0.8 = 0.5',22,GOLD,ha='center')
    for v in [0,.5,1]:text(ax,115,y(v),str(v),20,ha='center')
    save(fig,'stick_deadzone','S14','자체 입력 함수. 입력 0.2 이하는 0, 그 밖은 남은 구간을 0~1로 대응시킵니다. 입력 0.6이 적용 크기 0.5가 되는 예입니다.')

def grass():
    fig,ax=canvas('중심에서 멀어질수록 영향이 약해집니다','자체 선형 영향 w=max(0,1−d/r) · r은 0보다 큰 반경')
    x=lambda v:150+850*v;y=lambda v:760-470*v
    ax.plot([x(0),x(1.1)],[760,760],color=INK,lw=2);ax.plot([150,150],[280,760],color=INK,lw=2);ax.plot([150,x(1),x(1.1)],[y(1),760,760],color=GREEN,lw=5)
    for v,label in [(0,'중심 · 0'),(.5,'r/2'),(1,'반경 · r')]:text(ax,x(v),810,label,22,ha='center')
    for v in [0,.5,1]:ax.add_patch(Circle((x(v),y(1-v)),9,fc=GREEN))
    text(ax,70,300,'1',23,ha='center');text(ax,70,760,'0',23,ha='center');text(ax,600,885,'거리 d → / 중심 1, 반경 끝 0',25,ha='center')
    save(fig,'grass_falloff','S17','자체 영향 함수. 중심은 1, 반경의 절반은 0.5, 반경 끝과 바깥은 0입니다. 실제 게임의 식생 셰이더 코드를 추출한 그래프가 아닙니다.')
    fig,ax=canvas('뿌리와 끝에 다른 가중치를 주어 바닥을 유지하기','자체 정점 변위 · 단순 위치 이동이며 완전한 물리 굽힘 모형은 아님')
    ax.plot([80,1120],[740,740],color=INK,lw=3);ax.add_patch(Circle((600,685),26,fc=GOLD))
    for root,sgn in [(340,-1),(860,1)]:
        ax.plot([root,root],[740,380],color=LIGHT,lw=10,ls='--');ax.plot([root,root+sgn*35,root+sgn*140],[740,560,380],color=GREEN,lw=10);ax.add_patch(Circle((root,740),10,fc=BLUE));arrow(ax,root,330,root+sgn*140,330,GREEN)
    text(ax,600,250,'중심에서 바깥으로',25,GREEN,ha='center');text(ax,600,820,'뿌리 h=0 · 끝 h=1 / 거리에 따른 w도 함께 적용',23,ha='center')
    save(fig,'grass_bend','S17','자체 풀 변위 단면. 뿌리는 고정하고 끝에 더 큰 변위를 줍니다. 회색은 변형 전, 초록은 변형 후이며 물리적으로 정확한 줄기 곡률을 계산한 그림은 아닙니다.')

def dither():
    ranks=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])
    fig,ax=canvas('같은 밝기를 위치별 임계값과 비교합니다','자체 4×4 순서 무늬 · T=(순서+0.5)/16, L>T이면 밝은 색')
    for row in range(4):
        for col in range(4):
            x=85+col*105;y=295+row*105;ax.add_patch(Rectangle((x,y),100,100,fc='#f1f5ef',ec=INK));text(ax,x+50,y+50,str(ranks[row,col]),25,ha='center')
    node(ax,700,340,420,170,'밝기 L=0.25\n임계값 T와 비교',BLUE,size=25);arrow(ax,540,500,680,425,BLUE);text(ax,910,650,'순서 0·1·2·3인\n네 칸만 밝아짐',25,GREEN,ha='center')
    save(fig,'dither_threshold','S19','자체 4×4 임계값 예. 순서에 0.5를 더해 16으로 나눈 값과 밝기를 비교합니다. L=0.25에서는 네 칸이 밝아지며 실제 게임의 최종 무늬를 복제한 자료가 아닙니다.')
    fig,ax=canvas('선택한 색은 두 개이고 밝은 점의 비율이 다릅니다','자체 같은 무늬 · 4/16, 8/16, 12/16을 확대해 비교')
    for j,L in enumerate([.25,.5,.75]):
        for row in range(4):
            for col in range(4):
                bright=L>(ranks[row,col]+.5)/16;x=75+j*385+col*70;y=350+row*70
                ax.add_patch(Rectangle((x,y),70,70,fc='#fffef9' if bright else '#19352c',ec='#65746d',lw=.7))
        text(ax,215+j*385,740,f'L={L}\n밝은 칸 {int(L*16)}/16',25,ha='center')
    save(fig,'dither_density','S19','자체 두 색 밀도 예. 각 4×4 칸에서 밝은 칸은 4·8·12개입니다. 점 비율과 사람이 느끼는 밝기가 항상 수치 그대로 같다는 의미는 아닙니다.')

def mesh():
    fig,ax=canvas('정점의 부호를 읽어 경계 양쪽을 분류하기','자체 평면 절단 단면 · 왼쪽 한 정점, 오른쪽 두 정점인 삼각형')
    verts=[(200,700),(1000,700),(800,300)];ax.add_patch(Polygon(verts,fc='#edf1e8',ec=INK,lw=3));ax.plot([600,600],[230,810],color=GOLD,lw=4,ls='--')
    for (x,y),lab,c in zip(verts,['A · 음수','B · 양수','C · 양수'],[BLUE,GREEN,GREEN]):ax.add_patch(Circle((x,y),12,fc=c));text(ax,x,y-45,lab,25,c,ha='center')
    text(ax,600,870,'평면 경계 · 부호가 바뀌는 두 모서리에 교차점 필요',23,ha='center')
    save(fig,'mesh_classify','S21','자체 삼각형 분류. 한 정점은 경계 왼쪽, 두 정점은 오른쪽에 있습니다. 두 모서리에서 부호가 바뀌므로 교차점을 만들어 조각을 구성해야 합니다.')
    fig,ax=canvas('교차점으로 새 조각을 만들고 삼각형으로 나누기','자체 같은 삼각형 · 왼쪽 삼각형 하나, 오른쪽 사각형을 두 삼각형으로')
    ax.add_patch(Polygon([(200,700),(600,700),(600,433.333)],fc='#c8dbec',ec=BLUE,lw=3))
    ax.add_patch(Polygon([(600,433.333),(800,300),(1000,700),(600,700)],fc='#dce9da',ec=GREEN,lw=3));ax.plot([600,1000],[433.333,700],color=GREEN,lw=2)
    for x,y,lab in [(600,433.333,'P'),(600,700,'Q')]:ax.add_patch(Circle((x,y),12,fc=GOLD));text(ax,x-32,y-20,lab,25,GOLD,ha='center')
    text(ax,350,805,'왼쪽 결과',25,BLUE,ha='center');text(ax,830,805,'오른쪽 결과',25,GREEN,ha='center');text(ax,600,900,'위치뿐 아니라 UV 등 속성도 교차 비율로 대응',23,ha='center')
    save(fig,'mesh_split','S21','자체 절단 결과. 같은 경계의 교차점 P·Q를 공유하고 왼쪽 한 삼각형과 오른쪽 두 삼각형을 구성합니다. 닫힌 입체의 단면 마감까지 처리한 예는 아닙니다.')

if __name__=='__main__':
    movement();grass();dither();mesh()
    (BASE/'figure-manifest-batch17.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
