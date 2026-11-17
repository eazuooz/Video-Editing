from render_figures import *
import numpy as np

def brief():
    fig,ax=canvas('느낌을 사용 조건·자세·시간으로 함께 적기','자체 공격 의뢰 카드 · 수치는 상용 게임 실측이 아니라 협의용 설계값')
    rows=[('원하는 인상','무겁게 휘두르되 첫 입력 신호는 분명하게'),('사용 조건','지상 대기에서 시작 · 공격 중 방향 고정'),('시간 조건','48칸 클립 · 판정 12~16 · 이동 36부터'),('검수 조건','게임 카메라 · 피격 중단 · 전환 경계 입력')]
    for j,(label,body) in enumerate(rows):
        y=290+j*160;node(ax,65,y-45,255,90,label,BLUE,size=24);text(ax,355,y,body,22)
    save(fig,'animation_brief','A01','자체 의뢰 카드 예. 인상만 적지 않고 사용 상태·자세·시간·검수 조건을 함께 전달합니다. 판정 12~16은 본문에서 정한 12 이상 16 미만이며 초당 60칸의 설명용 시간표입니다.')
    fig,ax=canvas('큰 관계가 맞는지 먼저 보고 세부를 쌓기','자체 제작 순서 · 완성된 장식보다 실제 게임에서의 주요 동작을 먼저 검수')
    for y,title,body,c in [(285,'핵심 동작 초안','출발 · 타격 · 마무리 자세와 주요 시간',BLUE),(520,'게임 안의 관계','카메라 · 표적 경로 · 판정 · 다음 입력',GREEN),(755,'세부와 예외','손끝 · 장비 · 전환 · 피격 중단',GOLD)]:
        node(ax,100,y-60,1000,120,title+'\n'+body,c,size=24)
        if y<700:arrow(ax,600,y+75,600,y+155,c,3)
    save(fig,'animation_review','A01','자체 제작 검수 순서. 큰 자세와 시간, 실제 게임의 관계, 세부와 예외를 차례로 확인합니다. 이전 단계의 문제가 드러나면 되돌아가 수정할 수 있습니다.')

def scale():
    fig,ax=canvas('같은 비율의 손 이동도 화면에서는 더 작아집니다','자체 직교 투영 모형 · 화면 크기에 따른 단순 비례를 보기 위한 예')
    for x,scale,label in [(300,1,'키 200px → 변화 10px'),(900,.25,'키 50px → 변화 2.5px')]:
        y=700; height=420*scale
        ax.plot([x,x],[y,y-height],color=INK,lw=13*scale+3)
        ax.add_patch(Circle((x,y-height-40*scale),35*scale,fc=INK))
        ax.plot([x,x-70*scale],[y,y+80*scale],color=INK,lw=12*scale+2);ax.plot([x,x+70*scale],[y,y+80*scale],color=INK,lw=12*scale+2)
        ax.plot([x,x+120*scale],[y-height*.7,y-height*.7],color=BLUE,lw=8*scale+2)
        ax.add_patch(Circle((x+120*scale,y-height*.7),8*scale+3,fc=BLUE));ax.add_patch(Circle((x+145*scale,y-height*.7),8*scale+3,fill=False,ec=GOLD,lw=2))
        text(ax,x,870,label,23,ha='center')
    text(ax,830,330,'비례를 설명하는 확대 도식\n실제 픽셀 크기와 다름',21,MUTED,ha='center')
    save(fig,'exaggeration_scale','A02','자체 비례 설명. 키의 5%로 보이는 움직임은 키 200px일 때 10px, 키 50px일 때 2.5px입니다. 도식의 인체와 표시는 가독성을 위해 확대했으며 모든 원근 카메라의 측정 결과를 대신하지 않습니다.')
    fig,ax=canvas('목표를 넘었다가 정리되는 오버슈트 보기','자체 관절 각도 예 · 물리 시뮬레이션이나 실제 캐릭터 실측이 아님')
    t=np.array([0,.15,.35,.5,.65,1]);ang=np.array([0,20,42,32,37,36])
    X=lambda x:170+x*920;Y=lambda a:770-a*11
    ax.plot(X(t),Y(ang),color=BLUE,lw=5);ax.scatter(X(t),Y(ang),color=BLUE,s=55)
    ax.plot([170,1090],[Y(36),Y(36)],color=GOLD,lw=2,ls='--');text(ax,1100,Y(36)-45,'목표 36도',22,GOLD,ha='right')
    text(ax,X(.35),Y(42)-60,'42도까지 지나감',24,BLUE,ha='center')
    arrow(ax,170,790,1120,790,INK,2);arrow(ax,170,790,170,240,INK,2)
    text(ax,70,250,'각도',23);text(ax,1100,850,'시간',23,ha='right')
    save(fig,'overshoot','A02','자체 관절 각도 모형. 목표 36도를 지나 42도까지 간 뒤 32도·37도를 거쳐 정리되는 모습을 점과 선으로 표시했습니다. 모든 동작에 이런 튕김을 넣어야 한다는 기준이나 실제 물리 계산이 아닙니다.')

def info():
    fig,ax=canvas('기록된 동작과 최종 화면 사이의 변화 확인하기','자체 제작 검수 경로 · 단계마다 같은 의미가 남는지 봅니다')
    for x,y,title,body,c in [(80,270,'배우의 동작','작은 시선·몸 변화',BLUE),(700,270,'캐릭터 몸','머리·팔·옷 비례',GREEN),(80,620,'게임 카메라','크기·각도·재생 리듬',GOLD),(700,620,'실제 플레이 화면','배경·효과·UI와 겹침',BLUE)]:
        node(ax,x,y,420,145,title+'\n'+body,c,size=24)
    arrow(ax,515,342,685,342);arrow(ax,900,435,290,600,GREEN);arrow(ax,515,692,685,692)
    save(fig,'information_path','A07','자체 정보 검수 경로. 원본 기록, 캐릭터 비례, 카메라, 실제 화면의 가림을 각각 확인합니다. 어느 단계에서 의도한 단서가 약해졌는지 나누어 보는 자료입니다.')
    fig,ax=canvas('얼굴이 작다면 몸에도 같은 뜻의 단서를 남기기','자체 놀람 표현 모형 · 감정의 정답 포즈나 실제 심리 측정이 아님')
    for x,tilt,label in [(320,0,'얼굴 변화에만 의존'),(885,-45,'몸통·발·방향도 함께')]:
        ax.add_patch(Circle((x+tilt,360),48,fc='none',ec=INK,lw=5));ax.plot([x,x+tilt],[630,415],color=INK,lw=13)
        ax.plot([x,x-70],[630,780],color=INK,lw=13);ax.plot([x,x+85],[630,780],color=INK,lw=13)
        ax.plot([x+tilt,x+tilt+100],[465,430 if tilt else 510],color=INK,lw=10)
        ax.plot([x+tilt-18,x+tilt-4],[345,339],color=BLUE,lw=3);ax.plot([x+tilt+10,x+tilt+24],[339,345],color=BLUE,lw=3)
        text(ax,x,860,label,23,ha='center')
        if tilt:arrow(ax,x+tilt+60,360,1110,360,GOLD,3);text(ax,1090,290,'의식하는 대상',20,GOLD,ha='right')
    save(fig,'emotion_channels','A07','자체 정보 채널 비교. 오른쪽은 얼굴 외에 몸통 후퇴·팔·발·대상 방향에도 단서를 남긴 예입니다. 특정 감정의 유일한 포즈나 실제 사람의 정서를 판별하는 도구가 아닙니다.')

def pose():
    fig,ax=canvas('손이 닿는 위치와 몸 전체의 받침을 함께 보기','자체 상자 들기 포즈 도식 · 점선은 작화 도움선이며 질량 중심 계산이 아님')
    for x,shift,label in [(300,0,'손만 물체 쪽으로'),(850,55,'발·골반·가슴도 함께')]:
        hx=x+shift;ax.add_patch(Circle((hx,340),40,fc=INK))
        ax.plot([x,hx],[610,390],color=INK,lw=14)
        ax.plot([x,x-75],[610,780],color=INK,lw=14);ax.plot([x,x+95],[610,780],color=INK,lw=14)
        ax.add_patch(Rectangle((x+100,460),125,135,fc='#d7bb86',ec=INK,lw=3))
        ax.plot([hx,x+60,x+112],[435,520,590],color=BLUE,lw=8)
        ax.plot([hx,hx],[385,790],color=GOLD,lw=2,ls='--')
        ax.plot([x-100,x+120],[800,800],color=INK,lw=4)
        text(ax,x,870,label,23,ha='center')
    save(fig,'pose_support','A08','자체 포즈 관계 비교. 손·물체의 접촉과 발·골반·가슴의 배치를 함께 살펴봅니다. 점선은 형태를 비교하는 도움선이며 실제 인체의 질량 중심이나 안전한 운동 자세를 계산한 선이 아닙니다.')
    fig,ax=canvas('포즈는 큰 관계부터 세부로 확인합니다','자체 검수 우선순위 · 한 단계의 완성이 다음 단계 전체를 보장하지 않음')
    for y,title,body,c in [(290,'큰 덩어리','머리 · 가슴 · 골반 · 지지발',BLUE),(520,'접촉과 윤곽','물체를 잡은 손 · 팔의 사슬 · 빈 공간',GREEN),(750,'세부','손목 · 손끝 · 얼굴 · 옷과 장비',GOLD)]:
        node(ax,120,y-60,960,120,title+'\n'+body,c,size=24)
        if y<700:arrow(ax,600,y+75,600,y+150,c,3)
    save(fig,'pose_hierarchy','A08','자체 포즈 검수 순서. 전신의 큰 관계를 먼저 잡고 접촉·윤곽을 확인한 뒤 손끝과 표정 등 세부를 더합니다. 세부가 주요 관계를 가리면 이전 단계로 되돌아가 수정합니다.')

if __name__=='__main__':
    brief();scale();info();pose()
    (BASE/'figure-manifest-batch8.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
