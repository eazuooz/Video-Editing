from render_figures import *
import numpy as np

def leaves():
    fig,ax=canvas('접촉한 뒤 처리하기 전에 접근 경로를 바꿔 볼 수 있습니다','자체 경로 비교 · 상승 바람은 대부분의 진입을 줄이는 표현이며 완전 차단이 아님')
    for cx,label,on in [(315,'바람 없음',False),(880,'국소 상승 바람',True)]:
        ax.plot([cx-190,cx+190],[795,795],color=INK,lw=3)
        ax.add_patch(Polygon([(cx-65,790),(cx,660),(cx+65,790)],fc=GOLD))
        if on:
            ax.add_patch(Rectangle((cx-130,340),260,440,fc='#e3efe9',ec=GREEN,ls='--',alpha=.5))
            for dx in [-80,0,80]:arrow(ax,cx+dx,670,cx+dx,420,GREEN,2)
        pts=[(cx-160,260),(cx-100,390),(cx-55,535),(cx-20,670)] if not on else [(cx-160,260),(cx-100,390),(cx-55,535),(cx+5,550),(cx+90,400)]
        ax.plot(*zip(*pts),color=BLUE,lw=3)
        for x,y in pts:ax.add_patch(Polygon([(x-18,y),(x,y-9),(x+18,y),(x,y+9)],fc=BLUE))
        arrow(ax,*pts[-2],*pts[-1],BLUE,3);text(ax,cx,865,label,26,ha='center')
    save(fig,'leaf_paths','S31','자체 낙엽 경로 비교. 오른쪽의 연두 영역이 불 위의 상승 바람입니다. 파란 잎의 접근 경로를 바꾸는 개념도이며 실제 물리 계산을 측정한 궤적은 아닙니다.')
    fig,ax=canvas('영향 범위의 중앙과 경계를 다르게 설계하기','자체 바람 단면 · 중심에서 강하고 바깥에서는 0으로 줄이는 예')
    xs=np.linspace(150,1050,100);ys=760-460*np.maximum(0,1-abs(xs-600)/360)**2
    ax.plot(xs,ys,color=GREEN,lw=4);ax.plot([120,1100],[760,760],color=INK,lw=2)
    for x in [240,360,480,600,720,840,960]:
        strength=max(0,1-abs(x-600)/360)**2
        if strength:arrow(ax,x,755,x,760-460*strength,GREEN,3)
    text(ax,600,230,'상승 바람의 크기',25,GREEN,ha='center');text(ax,600,835,'중심에서의 가로 거리 →',24,ha='center');text(ax,210,695,'0',22);text(ax,980,695,'0',22)
    save(fig,'leaf_falloff','S31','자체 공간 영향도. 화살표가 길수록 상승 가속도를 크게 주는 모형입니다. 이 곡선이나 범위가 Ghost of Tsushima의 실제 설정이라는 뜻은 아닙니다.')

def director():
    fig,ax=canvas('등장을 조절하는 관리자와 이미 있는 적의 행동 나누기','자체 시스템 분리 · 생성 억제만으로 현재 교전이 사라지지는 않음')
    node(ax,70,240,300,150,'사건 관찰\n피해 · 교전',BLUE, size=25);node(ax,700,240,400,150,'페이싱 관리자\n상태와 강도',GREEN,size=25);arrow(ax,380,315,685,315)
    node(ax,700,560,400,150,'적 생성기\n새 무리 허용 / 억제',GOLD,size=25);arrow(ax,900,405,900,545,GREEN)
    node(ax,70,560,400,150,'현재 적의 행동\n추적 · 공격 · 퇴장',RED,size=25);arrow(ax,685,635,485,635,GOLD)
    text(ax,600,840,'관리자가 쉬어도 남은 적은 별도 규칙으로 행동할 수 있음',25,ha='center')
    save(fig,'director_layers','S35','자체 역할 분리도. 관찰 결과로 생성 흐름을 조절하더라도 이미 존재하는 적의 행동은 별도입니다. 적 생성기의 결과가 현재 적 집합으로 연결됩니다.')
    fig,ax=canvas('휴식 타이머 전에 현재 교전이 가라앉기를 기다리기','자체 시간 예시 · 임계값과 구간 길이는 원작 실측값이 아님')
    xs=[100,220,350,470,560,650,750,880,1050];ys=[750,650,350,310,400,600,750,785,680]
    for l,r,c in [(100,350,BLUE),(350,470,GOLD),(470,750,RED),(750,1050,GREEN)]:ax.axvspan(l,r,ymin=.20,ymax=.72,color=c,alpha=.10)
    ax.plot(xs,ys,color=INK,lw=4);ax.plot([100,1080],[805,805],color=INK,lw=2)
    for x,l,c in [(220,'고조',BLUE),(410,'정점 유지',GOLD),(610,'교전 소강 대기',RED),(900,'휴식',GREEN)]:text(ax,x,250,l,22,c,ha='center')
    text(ax,100,870,'시간 →',24);text(ax,95,365,'강도\n높음',19);text(ax,600,920,'기존 교전이 계속된 시간을 실제 휴식으로 착각하지 않기',22,ha='center')
    save(fig,'director_timeline','S35','자체 강도·상태 시간도. 빨간 구간은 새 위협을 줄이면서 기존 교전이 가라앉기를 기다리는 시간, 초록 구간은 이후 휴식입니다. 실제 L4D 플레이 기록이 아닙니다.')

def parallax():
    fig,ax=canvas('카메라가 오른쪽 100 이동하면 층은 얼마나 움직일까','자체 기준 · 화면 위치 s = x - k c')
    for y,k,label,c in [(300,.1,'먼 산',BLUE),(520,.5,'중간 숲',GREEN),(740,1,'가까운 길',GOLD)]:
        text(ax,60,y,label+'\nk = '+str(k),23,c);ax.plot([310,1100],[y,y],color=LIGHT,lw=2)
        ax.add_patch(Circle((1000,y),23,fill=False,ec=MUTED,lw=2));new=1000-5*k*100
        ax.add_patch(Circle((new,y),23,fc=c));arrow(ax,995,y,new+5,y,c,3)
        text(ax,500,y+65,'왼쪽 '+str(int(k*100))+' 이동',23,c)
    save(fig,'parallax_offsets','S45','자체 세 층 비교. 같은 카메라 이동 100에 대해 먼 산은 10, 숲은 50, 가까운 길은 100만큼 화면 왼쪽으로 이동합니다. 도형 이동도 같은 1:5:10 비율로 그렸습니다.')
    fig,ax=canvas('한 장의 끝을 다음 장의 시작과 이어 붙이기','자체 반복 배치 · 표시 폭 W가 반복 간격과 같아야 함')
    for x,c in [(140,BLUE),(600,GREEN)]:
        ax.add_patch(Rectangle((x,330),460,300,fc='#eaf2e8',ec=c,lw=3))
        ax.add_patch(Polygon([(x,580),(x+90,430),(x+190,570),(x+300,410),(x+460,580)],closed=False,fill=False,ec=c,lw=4))
        text(ax,x+230,695,'그림 한 장 · W',25,c,ha='center')
    ax.plot([600,600],[280,770],color=RED,ls='--',lw=2);text(ax,600,230,'오른쪽 끝 높이 = 다음 왼쪽 시작 높이',25,RED,ha='center');text(ax,600,850,'카메라 이동 · 확대 · 역방향에서도 빈 곳과 이음새 확인',23,ha='center')
    save(fig,'parallax_repeat','S45','자체 배경 반복 모형. 폭 W 간격으로 배치하고 양쪽 경계를 이어지게 만듭니다. 두 장으로 충분한지는 화면 폭과 확대 비율을 함께 검사해야 합니다.')

def terrain():
    fig,ax=canvas('언덕 하나가 보이는 정보의 순서를 바꿉니다','자체 옆면 단면 · 점선은 가려지는 시선, 실선은 열린 시선')
    ax.plot([90,1120],[785,785],color=INK,lw=3);ax.add_patch(Polygon([(300,785),(620,340),(930,785)],fc='#bed4b0',ec=GREEN,lw=3))
    ax.add_patch(Circle((180,640),18,fc=BLUE));ax.add_patch(Rectangle((1015,655),55,130,fc=GOLD));ax.plot([180,1040],[640,655],color=RED,ls='--',lw=3)
    ax.add_patch(Circle((620,285),18,fc=BLUE));arrow(ax,645,300,1030,635,BLUE,3)
    text(ax,165,850,'출발점',24,BLUE,ha='center');text(ax,620,215,'정상에서 새 정보 확인',25,BLUE,ha='center');text(ax,1025,850,'뒤쪽 대상',24,GOLD,ha='center')
    save(fig,'terrain_reveal','S50','자체 가림 단면. 낮은 출발점의 시선은 언덕을 통과해 대상이 가려지고, 정상에서는 대상이 드러납니다. 실제 젤다 지형이나 카메라 좌표를 복원한 그림은 아닙니다.')
    fig,ax=canvas('정상 경로와 우회 경로가 서로 다른 선택이 되려면','자체 평면 배치 · 길이·이동 비용·발견 지점을 함께 조정')
    ax.add_patch(Circle((600,500),195,fc='#e3ecd9',ec=GREEN,lw=3));text(ax,600,490,'언덕 H',28,GREEN,ha='center')
    ax.plot([160,600,1020],[770,500,260],color=BLUE,lw=4);ax.plot([160,300,760,1020],[770,870,830,260],color=GOLD,lw=4)
    for x,y,l,c in [(160,770,'S',INK),(1020,260,'T',RED),(860,510,'C',GREEN)]:ax.add_patch(Circle((x,y),30,fc=c));text(ax,x,y,l,22,'white',ha='center')
    text(ax,200,240,'파랑 · 정상에서 넓게 보기',24,BLUE);text(ax,200,300,'금색 · 완만하게 돌아가기',24,GOLD);text(ax,875,575,'보상',20,GREEN,ha='center')
    save(fig,'terrain_routes','S50','자체 경로 설계. 탑 T를 향하며 정상 또는 우회를 선택하고 중간 보상 C를 발견할 수 있습니다. 색 경로의 비용이 같거나 실제 최단거리라는 가정은 하지 않습니다.')

if __name__=='__main__':
    leaves();director();parallax();terrain()
    (BASE/'figure-manifest-batch22.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
