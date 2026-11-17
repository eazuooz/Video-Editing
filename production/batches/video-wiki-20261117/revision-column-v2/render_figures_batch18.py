from render_figures import *

def portal():
    fig,ax=canvas('세계 위치를 입구 기준으로 읽고 출구 기준으로 옮기기','자체 축 규약 · p_out = B H (A 역변환) p_in, H는 반 바퀴 회전')
    for y,l,b,c in [(280,'A 역변환 · 입구 기준','세계 위치 → 입구의 상대 위치',BLUE),(500,'H · 축 대응','문 앞뒤의 연결 방향 맞추기',GOLD),(720,'B · 출구 기준','상대 위치 → 출구 쪽 세계 위치',GREEN)]:node(ax,65,y-65,365,130,l,c,size=24);text(ax,475,y,b,23)
    save(fig,'portal_frames','S23','자체 좌표 변환 분해. 입구 기준으로 읽기, 정한 앞뒤 규약에 맞춘 반 바퀴 대응, 출구 세계로 변환하기를 나눕니다. 포털 제작 축에 따라 중간 대응은 달라질 수 있습니다.')
    fig,ax=canvas('한 몸의 보이는 부분을 두 공간에 나눠 그립니다','자체 표시 모형 · 시각용 복사본이 피해·획득을 또 실행해서는 안 됨')
    for x,plane,l in [(70,350,'입구 표시'),(670,950,'출구 표시')]:
        ax.add_patch(Rectangle((x,270),460,440,fc='#f1f5ef',ec=INK));ax.add_patch(Rectangle((x+50,430),350,110,fc='none',ec=MUTED,lw=3,ls='--'));ax.plot([plane,plane],[300,680],color=GOLD,lw=4)
        if x==70:ax.add_patch(Rectangle((120,430),230,110,fc=BLUE))
        else:ax.add_patch(Rectangle((950,430),120,110,fc=GREEN))
        text(ax,x+230,775,l,26,ha='center')
    text(ax,600,870,'회색 · 전체 표시 후보 / 색칠한 부분만 각 경계에 남김',23,ha='center')
    save(fig,'portal_slices','S23','자체 클리핑 모형. 양쪽의 전체 표시 후보 중 서로 다른 경계 부분만 남깁니다. 실제로 두 캐릭터를 만들거나 양쪽 충돌을 완전히 해결한 그림은 아닙니다.')

def recursion():
    fig,ax=canvas('안쪽으로 같은 시점 변환을 반복하되 깊이를 제한하기','자체 재귀 모형 · 가장 깊은 곳에 유효한 대체 결과를 정해야 함')
    for x,y,w,h,n,col in [(100,260,1000,570,1,BLUE),(310,380,650,350,2,GREEN),(520,490,330,155,3,GOLD)]:
        ax.add_patch(Rectangle((x,y),w,h,fc='#f1f5ef',ec=col,lw=5));text(ax,x+25,y+38,f'깊이 {n}',24,col)
    text(ax,600,900,'보이는 깊이와 실제 계산 횟수의 상한을 따로 기록',23,ha='center')
    save(fig,'portal_depth','S29','자체 세 단계 그림. 포털 안의 포털을 더 깊은 시점으로 계산하는 의존 관계를 표현합니다. 실제 무한 재귀나 특정 출시 게임의 렌더러 구조를 재현한 그림이 아닙니다.')
    fig,ax=canvas('안쪽 결과를 준비한 뒤 바깥 그림에 포함하기','자체 렌더 텍스처 의존 순서 · 계산한 시점 목록과 그리기 순서 구별')
    for x,l,col in [(75,'깊이 3\n가장 안쪽',GOLD),(445,'깊이 2\n3의 결과 포함',GREEN),(815,'깊이 1\n2의 결과 포함',BLUE)]:node(ax,x,420,310,180,l,col,size=25)
    arrow(ax,395,510,435,510,GREEN);arrow(ax,765,510,805,510,BLUE);text(ax,600,760,'깊이 3 → 2 → 1 → 최종 화면',27,ha='center')
    save(fig,'portal_render_order','S29','자체 제한 깊이의 그리기 순서. 안쪽 결과를 만든 뒤 바깥에서 참조하도록 의존성을 정합니다. 모든 포털 구현이 동일한 텍스처 저장 방식을 사용한다는 뜻은 아닙니다.')

def perspective():
    fig,ax=canvas('크기와 거리를 같은 배율로 바꾸면 같은 각도로 보입니다','자체 원근 단면 · 카메라·물체 자세 고정, 1/2 = 3/6')
    ax.add_patch(Circle((140,500),18,fc=BLUE));text(ax,140,700,'카메라',24,BLUE,ha='center')
    for endy in [350,650]:ax.plot([140,740],[500,endy],color=MUTED,lw=2)
    ax.plot([340,340],[450,550],color=GREEN,lw=13);ax.plot([740,740],[350,650],color=GOLD,lw=13)
    arrow(ax,145,790,335,790,GREEN,2,style='<->');arrow(ax,145,865,735,865,GOLD,2,style='<->');text(ax,240,750,'거리 2',22,GREEN,ha='center');text(ax,440,830,'거리 6',22,GOLD,ha='center')
    text(ax,390,380,'높이 1',25,GREEN);text(ax,810,500,'높이 3\n같은 각도 범위',25,GOLD)
    save(fig,'perspective_ratio','S32','자체 유사 삼각형 모형. 카메라에서 2만큼 떨어진 높이 1과 6만큼 떨어진 높이 3은 같은 각도 범위를 차지합니다. 실제 게임의 물체 크기를 측정한 도식이 아닙니다.')
    fig,ax=canvas('중앙 광선이 비어 있어도 커진 물체의 모서리는 겹칠 수 있습니다','자체 배치 검사 · 후보 전체의 부피·표면과 환경 관계를 확인')
    ax.add_patch(Circle((120,540),20,fc=BLUE));ax.plot([140,1000],[540,540],color=BLUE,lw=3)
    ax.add_patch(Rectangle((650,340),290,400,fc='#e6d5aa',ec=GOLD,lw=3));ax.add_patch(Rectangle((850,250),180,200,fc=MUTED,ec=INK,lw=2))
    text(ax,795,800,'커진 상자 후보',25,GOLD,ha='center');text(ax,990,200,'기둥',24,ha='center');text(ax,370,625,'중앙선만 통과',23,BLUE,ha='center')
    save(fig,'perspective_collision','S32','자체 배치 실패. 중앙선은 통과해도 큰 상자 후보의 위 모서리는 기둥과 겹칩니다. 중심점 검사와 물체 전체 배치 검사는 서로 다른 문제입니다.')

def eras():
    fig,ax=canvas('두 지도의 기준점 차이를 더해 대응 위치로 옮기기','자체 두 층 · B−A=(0,10,0), 실제 제품의 층 간격이 아님')
    for y,label,c in [(310,'현재 · 원점 B',GREEN),(700,'과거 · 원점 A',BLUE)]:
        ax.plot([110,1090],[y,y],color=c,lw=4);ax.add_patch(Circle((420,y-35),22,fc=c));text(ax,110,y+65,label,25,c)
    arrow(ax,420,630,420,330,GOLD,4);text(ax,590,500,'같은 가로 위치\n높이만 +10',27,GOLD)
    save(fig,'era_mapping','S33','자체 두 시대 좌표 대응. 지도 크기·방향을 같게 두고 원점 차이만큼 옮기는 모형입니다. 실제 Titanfall 2의 간격이나 전체 구현을 재현한 자료가 아닙니다.')
    fig,ax=canvas('대응 좌표가 있어도 몸이 들어갈 공간이 있는지 확인하기','자체 전환 검사 · 점 하나가 비었는지보다 캐릭터 부피를 검사')
    for x,label in [(90,'출발 시대'),(690,'도착 시대')]:
        ax.add_patch(Rectangle((x,300),430,400,fc='#f1f5ef',ec=INK,lw=2));ax.add_patch(Rectangle((x+170,390),90,230,fc='none',ec=BLUE,lw=4));text(ax,x+215,775,label,25,ha='center')
    ax.add_patch(Rectangle((830,360),170,300,fc='#bf4538',alpha=.55));text(ax,600,870,'도착 후보와 벽이 겹침 → 전환 허용·보정 정책 필요',23,ha='center')
    save(fig,'era_occupancy','S33','자체 도착 검사. 같은 상대 좌표라도 다른 시대의 벽이 몸과 겹칠 수 있습니다. 전환을 막거나 안전 위치로 보정하는 정책과 안내를 함께 정해야 합니다.')

if __name__=='__main__':
    portal();recursion();perspective();eras()
    (BASE/'figure-manifest-batch18.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
