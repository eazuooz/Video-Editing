from render_figures import *
import numpy as np

def ink():
    fig,ax=canvas('벽의 위치를 그림의 같은 비율 주소로 연결하기','자체 벽: 가로 4m · 세로 2m / 맞은 점: 오른쪽 1m · 위 1m')
    for x,y,w,h,label in [(95,350,440,300,'벽 위 위치'),(725,350,350,300,'저장 그림 주소')]:
        ax.add_patch(Rectangle((x,y),w,h,fc='#eef3ec',ec=INK,lw=3));text(ax,x+w/2,260,label,27,ha='center')
        ax.plot([x+w*.25,x+w*.25],[y+h,y+h*.5],color=BLUE,lw=2,ls='--');ax.plot([x,x+w*.25],[y+h*.5,y+h*.5],color=BLUE,lw=2,ls='--')
        ax.add_patch(Circle((x+w*.25,y+h*.5),12,fc=BLUE))
    arrow(ax,550,500,705,500,BLUE,4)
    text(ax,310,730,'(1m, 1m)',25,BLUE,ha='center');text(ax,900,730,'UV = (0.25, 0.5)',25,BLUE,ha='center')
    text(ax,600,850,'카메라가 움직여도 벽에 붙인 주소는 유지됩니다.',25,ha='center')
    save(fig,'ink_address','S10','자체 평면 벽의 주소 계산. 가로 4m·세로 2m인 벽 전체가 그림 전체에 대응할 때 오른쪽 1m·위 1m의 점은 UV (0.25,0.5)입니다. 세로축을 위로 잡은 설명용 약속이며 카메라 좌표를 사용하지 않습니다.')
    fig,ax=canvas('공간에서 붙은 면도 저장 그림에서는 떨어질 수 있습니다','자체 아틀라스: 이웃 관계를 알고 두 영역으로 자국을 전달해야 함')
    for x,label in [(130,'면 A의 저장 영역'),(750,'면 B의 저장 영역')]:
        ax.add_patch(Rectangle((x,340),320,320,fc='#eef3ec',ec=INK,lw=3));text(ax,x+160,270,label,24,ha='center')
    # Separate atlas regions, each receives its part of the same stamp.
    ax.add_patch(plt.matplotlib.patches.Wedge((450,500),90,90,270,fc=BLUE,alpha=.6))
    ax.add_patch(plt.matplotlib.patches.Wedge((750,500),90,-90,90,fc=BLUE,alpha=.6))
    arrow(ax,470,500,725,500,GOLD,4);text(ax,600,420,'공간 이웃으로 전달',22,GOLD,ha='center')
    text(ax,600,800,'그림에서 바로 옆인 픽셀 ≠ 실제 공간에서 이웃한 면',25,ha='center')
    save(fig,'ink_seam','S10','자체 저장 영역 비교. 공간에서 만나는 두 면 A·B의 가장자리가 아틀라스에서는 떨어져 있다고 가정했습니다. 한 자국의 양쪽을 각각의 주소 영역에 기록해야 하며 저장 그림의 빈 공간을 칠하는 것으로 연결되지 않습니다.')

def ink_material():
    fig,ax=canvas('재질 한 장에서 플레이 정보 세 가지를 나누어 보기','자체 검사 과제: 팀 경계 / 지형의 꺾임 / 작은 이동 흔적')
    for y,c,title,body in [(270,BLUE,'팀 경계','어디까지 내 영역인가'),(490,GOLD,'지형 굴곡','벽과 바닥이 어디서 꺾이는가'),(710,GREEN,'작은 흔적','움직이는 대상을 어디서 놓치는가')]:
        node(ax,75,y-55,300,110,title,c,size=27);arrow(ax,390,y,520,y,c,3);text(ax,550,y,body,26)
    save(fig,'ink_tasks','S11','자체 가독성 과제도. 같은 잉크 화면도 영역, 공간, 움직임의 세 정보를 전달합니다. 한 재질 값이 세 과제를 모두 개선한다고 가정하지 않고 각각 평가합니다.')
    fig,ax=canvas('한 번에 한 조건만 바꾸어 같은 과제를 비교하기','조명 · 카메라 · 지형은 우선 고정한 자체 재질 실험')
    headers=['실험','바꾸는 값','확인하는 과제']
    xs=[80,390,740]
    for x,s in zip(xs,headers):text(ax,x,250,s,25,weight='bold')
    for y,a,b,c in [(395,'기준','변경 없음','경계 · 굴곡 · 흔적'),(555,'비교 A','광택 강도만','같은 세 과제'),(715,'비교 B','거칠기만','같은 세 과제')]:
        ax.plot([65,1135],[y+75,y+75],color=LIGHT,lw=2)
        for x,s in zip(xs,[a,b,c]):text(ax,x,y,s,23)
    text(ax,600,865,'기준 비교 다음에는 다른 조명·카메라·색 조합에서도 검사',23,ha='center')
    save(fig,'material_test','S11','자체 통제 비교표. 기준 장면에서 광택 강도와 거칠기를 각각 바꿔 같은 과제를 수행합니다. 실제 셰이더의 매개변수 이름과 작용은 확인해야 하며 특정 계수가 정답이라는 표가 아닙니다.')

def interior():
    fig,ax=canvas('같은 창문 점이라도 시선에 따라 먼저 닿는 벽이 다릅니다','자체 가상 방의 위쪽 시점 · 아래가 창문 / 안쪽이 깊이 방향')
    ax.plot([250,250,950,950],[720,260,260,720],color=INK,lw=5)
    ax.plot([250,510],[720,720],color=INK,lw=5);ax.plot([690,950],[720,720],color=INK,lw=5)
    text(ax,600,215,'뒷벽',24,ha='center');text(ax,1010,480,'옆벽',24)
    ax.add_patch(Circle((600,720),11,fc=GOLD));text(ax,570,770,'P',24,GOLD)
    for cam,end,c in [((600,900),(600,260),BLUE),((290,900),(950,517),GREEN)]:
        ax.add_patch(Circle(cam,17,fc=c));arrow(ax,*cam,*end,c,4)
    text(ax,600,880,'시선 A',21,BLUE,ha='left');text(ax,220,850,'시선 B',21,GREEN,ha='center')
    text(ax,725,780,'창문',22,GOLD)
    save(fig,'interior_rays','S22','자체 가상 방의 평면도. 시선 A는 창문 점 P를 지나 뒷벽을 먼저 만나고, 다른 카메라 위치의 시선 B는 같은 P를 지나 오른쪽 벽을 먼저 만납니다. 실제 렌더링에서는 이 관계를 픽셀별 3차원 광선으로 계산합니다.')
    fig,ax=canvas('가상 공간의 교차점이 창문 픽셀의 색이 되기까지','자체 구현 순서 · 먼저 면을 고르고 그 면의 두 축으로 주소를 만듭니다')
    for x,y,label,c in [(85,275,'카메라 → 창문 점\n광선 만들기',BLUE),(695,275,'방 좌표로 맞춤\n첫 유효 교차 선택',GREEN),(85,620,'만난 면 결정\n뒷벽 / 옆벽 / 천장 등',GOLD),(695,620,'해당 면의 2D 주소\n텍스처 색 읽기',BLUE)]:node(ax,x,y,420,135,label,c,size=23)
    arrow(ax,520,342,680,342);arrow(ax,900,430,295,600,GREEN);arrow(ax,520,687,680,687)
    text(ax,600,865,'실제로 그리는 창문 표면과 계산 속 가상 방을 구별합니다.',24,ha='center')
    save(fig,'interior_lookup','S22','자체 데이터 흐름도. 방 좌표의 광선 교차로 면을 결정하고 그 면의 무늬를 읽습니다. 가상 방 계산을 했다는 사실이 실제 내부 메시·충돌·탐험 공간을 만들었다는 뜻은 아닙니다.')

def flow():
    fig,ax=canvas('바위 주변의 흐름을 표면 위 화살표로 보기','자체 제작 벡터장 · 유체 압력·질량을 푼 시뮬레이션이 아님')
    for yy in range(290,790,85):
        for xx in range(120,1100,95):
            dx=(xx-600)/220;dy=(yy-530)/170;r2=dx*dx+dy*dy
            if r2<1:continue
            # Tangential deflection in a finite illustrative field.
            vy=.85*dy*np.exp(-((xx-520)/250)**2-((abs(yy-530)-150)/210)**2)
            vx=1-.3*np.exp(-r2)
            arrow(ax,xx-24,yy-vy*26,xx+24,yy+vy*26,BLUE,2)
    ax.add_patch(plt.matplotlib.patches.Ellipse((600,530),250,190,fc='#b8beb6',ec=INK,lw=3));text(ax,600,530,'바위',27,ha='center')
    text(ax,600,860,'물체를 옮겼다면 지도도 갱신하거나 별도 보정해야 합니다.',24,ha='center')
    save(fig,'flow_field','S25','자체 흐름 지도 예시. 화살표는 작가가 만든 표면 방향 데이터이며 바위 주변에서 위아래로 갈라집니다. 바위 모델의 위치 변화만으로 이 정적 벡터장이 자동 갱신되는 것은 아닙니다.')
    fig,ax=canvas('재시작 순간에는 그 레이어를 보이지 않게 하기','자체 두 레이어 모형 · 비중 합은 1 / 위상은 반 주기 차이')
    t=np.linspace(0,2,401);a=1-np.abs(2*(t%1)-1);b=1-a
    X=lambda t:150+t*480;Y=lambda w:640-w*320
    ax.plot(X(t),Y(a),color=BLUE,lw=4);ax.plot(X(t),Y(b),color=GREEN,lw=4)
    for q in [0,.5,1,1.5,2]:
        ax.plot([X(q),X(q)],[275,680],color=LIGHT,lw=1.5,ls='--');text(ax,X(q),745,str(q),20,ha='center')
    text(ax,65,320,'1',23);text(ax,65,640,'0',23);text(ax,150,245,'보이는 비중',23)
    text(ax,600,825,'파랑 A: 정수 시점 재시작 / 초록 B: 반 정수 시점 재시작',22,ha='center')
    text(ax,600,885,'각 재시작 때 해당 비중이 0이 되는지 확인합니다.',23,ha='center')
    save(fig,'flow_phases','S25','자체 두 레이어 가중치 모형. A는 정수 시점에, B는 반 정수 시점에 재시작하며 그 순간 각각 비중이 0입니다. 그래프는 왜곡량이 아니라 혼합 비중을 표시하고, 공간 반복·맥동까지 모두 해결되었다고 가정하지 않습니다.')

if __name__=='__main__':
    ink();ink_material();interior();flow()
    (BASE/'figure-manifest-batch6.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
