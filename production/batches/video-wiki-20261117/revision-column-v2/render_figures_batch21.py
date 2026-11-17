from render_figures import *
import numpy as np

def scene():
    fig,ax=canvas('편집 시점에서 본 전체와 게임 카메라의 범위는 다릅니다','자체 평면 배치 · 초록 구는 시야 안, 금색 구는 시야 밖인 단순 모형')
    ax.add_patch(Rectangle((65,260),630,520,fc='#f1f5ef',ec=INK));ax.add_patch(Polygon([(160,540),(650,340),(650,740)],fc='#dce9da',ec=BLUE,lw=2));node(ax,85,500,120,80,'카메라',BLUE,size=18)
    ax.add_patch(Circle((500,540),30,fc=GREEN));ax.add_patch(Circle((550,300),30,fc=GOLD))
    ax.add_patch(Rectangle((780,360),350,340,fc='#f1f5ef',ec=BLUE,lw=3));ax.add_patch(Circle((955,530),50,fc=GREEN));text(ax,370,855,'Scene View · 배치 관찰',25,ha='center');text(ax,955,785,'Game View\n카메라 결과',25,ha='center')
    save(fig,'scene_game_camera','S67','자체 장면·카메라 비교. 장면 전체를 보는 편집 시점에는 두 구가 있어도 게임 카메라의 단순 시야에는 한 구만 포함됩니다. 실제 Unity UI의 측정 캡처가 아닙니다.')
    fig,ax=canvas('같아 보이지 않을 때 비교할 조건을 나누기','자체 검수 순서 · 카메라만 맞추어도 조명·표시 옵션이 다를 수 있음')
    for y,l,b,c in [(280,'위치·자세','같은 대상을 같은 방향에서 보는가',BLUE),(500,'투영·비율','시야각·직교 범위·가로세로 조건',GREEN),(720,'표시·조명','편집용 모드·노출·후처리 조건',GOLD)]:node(ax,65,y-65,350,130,l,c,size=25);text(ax,460,y,b,23)
    save(fig,'view_conditions','S67','자체 비교 조건. 위치와 방향, 투영과 화면 비율, 조명과 표시 조건을 나누어 차이가 생긴 층을 좁힙니다. 편집기의 진단 표시가 최종 제품에 자동 반영되지는 않습니다.')

def distortion():
    fig,ax=canvas('주소는 오른쪽으로 읽어도 보이는 무늬는 왼쪽에 나타납니다','자체 5칸 · 출력 x가 입력 x+1을 읽고, 가장자리는 고정한다고 가정')
    for row,y,feature,label in [(0,300,3,'원본'),(1,650,2,'출력')]:
        text(ax,65,y+60,label,25,BLUE)
        for i in range(5):
            x=300+i*165;ax.add_patch(Rectangle((x,y),155,120,fc=RED if i==feature else '#e2e8dd',ec=INK));text(ax,x+77,y+60,str(i),25,'white' if i==feature else INK,ha='center')
    arrow(ax,300+2*165+77,625,300+3*165+77,435,BLUE,4);text(ax,450,510,'출력 2가\n입력 3을 읽음',24,BLUE,ha='center');text(ax,600,875,'빨간 특징은 3번 위치 → 2번 위치로 보임',24,RED,ha='center')
    save(fig,'distortion_mapping','S72','자체 주소 추적. 출력 2가 입력 3의 빨간색을 읽으므로 빨간 무늬는 왼쪽으로 한 칸 이동해 보입니다. 조회 주소 이동과 특징의 겉보기 이동은 반대일 수 있습니다.')
    fig,ax=canvas('영향 영역과 변위 크기를 따로 확인하기','자체 고정 방향 변위 · 원 경계에서 마스크를 0으로 줄이는 모형')
    for x in range(140,1100,120):ax.plot([x,x],[260,790],color=LIGHT,lw=2)
    for y in range(280,800,100):ax.plot([100,1100],[y,y],color=LIGHT,lw=2)
    ax.add_patch(Circle((600,520),200,fill=False,ec=GOLD,lw=4))
    for x,y,w in [(600,520,1),(500,520,.5),(700,520,.5),(600,420,.5),(600,620,.5)]:arrow(ax,x-40*w,y,x+40*w,y,BLUE,3)
    text(ax,600,875,'파랑 · 샘플 주소의 방향과 크기 / 금색 · 영향 경계',23,ha='center')
    save(fig,'distortion_mask','S72','자체 마스크·변위 디버그. 중앙의 샘플 주소 변위가 크고 경계에서 0이 되도록 줄입니다. 화살표는 실제 물체의 세계 이동을 뜻하지 않습니다.')

def compare():
    fig,ax=canvas('고정 조건과 의도적으로 바꿀 조건을 먼저 적기','자체 블룸 비교 · 실행하지 않은 수치를 성능 측정 결과처럼 쓰지 않음')
    for y,l,b,c in [(280,'공통 조건','장면·카메라·최종 해상도·노출',BLUE),(500,'비교할 차이','중간 버퍼·필터·합성 경로',GOLD),(720,'기록할 결과','단계별 이미지·GPU 시간·실패 장면',GREEN)]:node(ax,65,y-65,350,130,l,c,size=25);text(ax,460,y,b,23)
    save(fig,'bloom_comparison_contract','S73','자체 비교 계약. 고정한 조건과 의도한 구현 차이를 구별하고 단계별 품질과 실제 시간을 함께 기록합니다. 이 표 자체가 특정 구현의 우월성을 측정한 자료는 아닙니다.')
    fig,ax=canvas('큰 밝은 면 하나로 모든 손실을 찾을 수는 없습니다','자체 스트레스 장면 · 크기·위치·움직임을 나누어 비교')
    ax.add_patch(Rectangle((75,290),1050,430,fc=INK));ax.add_patch(Rectangle((160,370),230,270,fc='#f7efb0'));ax.add_patch(Circle((650,495),8,fc='#fffef9'));ax.plot([850,1040],[550,400],color='#fffef9',lw=2)
    for x,l in [(275,'큰 밝은 면'),(650,'작은 점 광원'),(945,'얇은 밝은 선')]:text(ax,x,795,l,24,ha='center')
    text(ax,600,895,'이후 화면 가장자리로 옮기고 천천히 움직여 안정성 확인',23,ha='center')
    save(fig,'bloom_test_targets','S73','자체 검수 대상. 큰 창·작은 점·얇은 선을 구별해 중간 해상도와 필터에서 어떤 정보가 사라지는지 봅니다. 실제 두 구현의 비교 결과나 성능 측정 이미지는 아닙니다.')

if __name__=='__main__':
    scene();distortion();compare()
    (BASE/'figure-manifest-batch21.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
