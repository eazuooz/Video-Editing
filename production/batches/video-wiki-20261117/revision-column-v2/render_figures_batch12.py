from render_figures import *
import numpy as np

def roles():
    fig,ax=canvas('보물상자 하나에서 만나는 서로 다른 문제','자체 협업 지도 · 실제 팀에서 직군이 반드시 이렇게 나뉜다는 조직도가 아님')
    for x,y,title,body,c in [(75,270,'기획','열 이유 · 조건 · 결과',BLUE),(700,270,'프로그래밍','상태 · 지급 · 저장',GREEN),(75,620,'2D 아트','아이콘 · 읽히는 화면',GOLD),(700,620,'3D·동작','형태 · 재질 · 열림 축',BLUE)]:node(ax,x,y,425,145,title+'\n'+body,c,size=24)
    text(ax,600,515,'한 번의 플레이 경험',27,ha='center')
    save(fig,'roles_chest','D04','자체 역할 지도. 상자의 규칙·상태·화면·입체 표현을 서로 다른 문제로 나눕니다. 실제 팀의 조직도나 완전한 직군 목록이 아니며 작은 팀에서는 역할이 겹칠 수 있습니다.')
    fig,ax=canvas('파일을 넘길 때 함께 맞출 연결 약속','자체 상자 통합 카드 · 연결 값이 같아야 개별 작업이 기능으로 만납니다')
    for y,title,body in [(280,'공간','단위 · 앞방향 · 원점 · 뚜껑 회전축'),(470,'시간','열기 시작 · 완료 · 중단의 의미'),(660,'상태','상자 ID · 보상 ID · 저장과 재접속')]:
        node(ax,75,y-55,300,110,title,BLUE,size=26);text(ax,420,y,body,24)
    text(ax,600,850,'실제 입력 → 열기 → 지급 → 저장 → 다시 읽기까지 확인',23,ha='center')
    save(fig,'roles_contract','D04','자체 통합 약속 카드. 공간·시간·상태 기준을 공유하고 실제 플레이 경로에서 함께 검수합니다. 개별 파일 완성만으로 통합 기능이 완료되었다고 판단하지 않습니다.')

def fov():
    fig,ax=canvas('세로 범위를 유지하며 양옆을 더 담는 비교','자체 창 모형 · 중앙 대상은 가로로 늘리지 않음 / 같은 화면 높이')
    # Equal displayed height. Wide frame grows sideways around the same center.
    ax.add_patch(Rectangle((110,290),980,420,fc='#f0f3ee',ec=GREEN,lw=4))
    ax.add_patch(Rectangle((227,290),746,420,fill=False,ec=BLUE,lw=4,ls='--'))
    ax.add_patch(Rectangle((550,455),100,120,fc=GOLD));text(ax,600,515,'차',26,ha='center')
    text(ax,600,235,'높이는 같게, 16:9 → 21:9',26,ha='center')
    text(ax,600,795,'파랑 점선: 기존 범위 / 초록: 양옆이 추가된 범위',24,ha='center')
    save(fig,'fov_aspect','D05','자체 화면 비율 도식. 세로 FOV와 화면 높이를 고정한 정책에서 가로 범위를 넓히는 관계를 보여 줍니다. 16:9와 21:9 틀은 같은 높이에 비례한 너비이며 중앙 차를 가로로 늘인 비교가 아닙니다.')
    fig,ax=canvas('같은 화면에 더 큰 각도 범위를 담는 별도 실험','자체 카메라 평면도 · 비율 변경과 FOV 변경을 같은 것으로 다루지 않기')
    p=(600,790)
    for angle,c,label,y in [(26,BLUE,'좁은 각도',390),(43,GREEN,'넓은 각도',255)]:
        for sign in [-1,1]:
            xx=600+sign*np.tan(np.radians(angle))*480;ax.plot([600,xx],[790,310],color=c,lw=4)
        text(ax,600,y,label,24,c,ha='center')
    ax.add_patch(Circle(p,18,fc=INK));text(ax,600,870,'같은 카메라 위치',24,ha='center')
    save(fig,'fov_angle','D05','자체 수평 시야 범위 비교. 카메라 위치를 유지하고 담는 방향 각도를 넓히는 관계를 보여 줍니다. 평면도의 부채꼴을 실제 원근 화면의 모든 왜곡이나 물체 크기 측정과 동일시하지 않습니다.')

def frames():
    fig,ax=canvas('경계 샘플 수와 경과한 간격 수를 구별하기','자체 시간 눈금 · 경계 번호 0~4는 점 5개지만 그 사이는 4칸')
    for i in range(4):
        x=220+i*195;ax.add_patch(Rectangle((x,510),195,120,fc=BLUE,alpha=.13,ec=BLUE,lw=2));text(ax,x+97,570,f'{i+1}칸째',24,BLUE,ha='center')
    for i in range(5):
        x=220+i*195;ax.add_patch(Circle((x,455),12,fc=INK));text(ax,x,375,str(i),26,ha='center')
    text(ax,600,760,'시간은 간격 수 ÷ 초당 눈금 수',27,ha='center')
    save(fig,'frame_boundaries','D09','자체 경계와 간격 비교. 0~4의 경계 샘플은 5개지만 0번에서 4번까지 지난 시간은 4칸입니다. 관찰 자료의 번호 기준과 시간 단위를 함께 적어 한 프레임씩 어긋나는 해석을 피합니다.')
    fig,ax=canvas('준비·활성·회복의 시간 경계를 정하기','자체 60Hz 시간표 · 12 + 3 + 15 = 30칸 = 0.5초')
    x=150;scale=30
    for count,label,c in [(12,'준비\n12칸',BLUE),(3,'활성\n3칸',RED),(15,'회복\n15칸',GOLD)]:
        ax.add_patch(Rectangle((x,340),count*scale,180,fc=c,alpha=.2,ec=c,lw=3));text(ax,x+count*scale/2,430,label,23,c,ha='center');x+=count*scale
    for frame in [0,12,15,30]:text(ax,150+frame*scale,610,str(frame),24,ha='center')
    text(ax,600,770,'활성은 12 이상 15 미만 · 모든 숫자는 자체 설계값',24,ha='center')
    save(fig,'frame_segments','D09','자체 연속 시간표. 시작 0, 준비 끝 12, 활성 끝 15, 회복 끝 30의 경계를 표시했습니다. 60Hz에서 총 30칸은 0.5초이며 실제 게임의 기술 수치를 추출한 것이 아닙니다.')

def praise():
    fig,ax=canvas('결과가 같아도 인정할 성공은 다를 수 있습니다','자체 방어·회피 시험장 · 어떤 사건을 인정하는지 실제 판정에 연결')
    for y,title,body,c in [(295,'방어 성공','실제 막기 사건 → 방어 응답',BLUE),(525,'회피 성공','정한 회피 조건 → 회피 응답',GREEN),(755,'그냥 빗나감','방어 성공으로 표시하지 않음',GOLD)]:
        node(ax,80,y-55,330,110,title,c,size=26);text(ax,450,y,body,24)
    save(fig,'praise_events','D11','자체 성공 사건 비교. 체력 감소가 없었다는 한 결과만으로 방어·회피·단순 빗나감을 같은 성취로 판정하지 않고 실제 사건과 응답을 연결합니다.')
    fig,ax=canvas('입력 수신·즉시 성과·나중 요약은 다른 응답입니다','자체 피드백 계층 · 모든 성과에 긴 축하 화면을 반복하지 않기')
    for y,title,body,c in [(285,'누른 순간','입력을 받음 · 방패 준비',BLUE),(520,'성공 확인','실제 막음 · 짧은 효과와 표시',GREEN),(755,'행동 뒤','누적 결과 · 필요한 상세 피드백',GOLD)]:
        node(ax,80,y-55,330,110,title,c,size=26);text(ax,450,y,body,24)
    save(fig,'praise_layers','D11','자체 피드백 시점 비교. 입력 수신은 성공 확정과 다르고, 즉시 결과와 나중 누적 요약은 다른 역할입니다. 중요한 다음 플레이 정보를 가리지 않는 강도와 시점을 선택합니다.')

if __name__=='__main__':
    roles();fov();frames();praise()
    (BASE/'figure-manifest-batch12.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
