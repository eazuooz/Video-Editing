from render_figures import *
import numpy as np

def asset():
    fig,ax=canvas('높이만 바꾸는 요청에도 기준이 필요합니다','자체 의자 단면 · 폭과 좌판 두께는 유지하고 다리 높이만 변경')
    for x,h,label,c in [(280,270,'변경 전 · 0.45m',BLUE),(830,300,'변경 후 · 0.50m',GREEN)]:
        ground=780;seat=ground-h
        ax.add_patch(Rectangle((x-100,seat-30),200,30,fc=c));ax.add_patch(Rectangle((x-95,seat),25,h,fc=c));ax.add_patch(Rectangle((x+70,seat),25,h,fc=c));ax.add_patch(Rectangle((x-100,seat-180),25,150,fc=c))
        ax.plot([x-180,x+180],[ground,ground],color=INK,lw=2);text(ax,x,855,label,23,c,ha='center');ax.add_patch(Circle((x,ground),8,fc=RED));text(ax,x,920,'바닥 피벗 유지',20,RED,ha='center')
    text(ax,600,240,'같은 좌판 폭 · 같은 두께 · 다른 다리 길이',25,ha='center');arrow(ax,470,600,640,600)
    save(fig,'asset_contract','S36','자체 의자 편집 계약. 바닥 피벗·폭·좌판 두께는 유지하고 다리 높이를 바꾸는 예입니다. 그림의 높이도 270:300으로 같은 비율을 사용했습니다.')
    fig,ax=canvas('편집 응답과 엔진에서의 합격을 구별합니다','자체 소품 검수 · 다음 단계에서 읽을 자료와 기준을 남기기')
    stages=[('대상·치수','어느 복사본을 바꾸는가',BLUE),('형태·피벗','여러 시점과 바닥 기준',GREEN),('저장·내보내기','다시 열어도 같은가',GOLD),('엔진 가져오기','단위·재질·충돌 확인',RED)]
    for i,(l,b,c) in enumerate(stages):
        y=200+i*175;node(ax,75,y,360,110,l,c,size=25);text(ax,490,y+55,b,24)
        if i<3:arrow(ax,255,y+115,255,y+165,c,2)
    save(fig,'asset_validation','S36','자체 단계별 검수도. 편집 호출이 성공해도 저장·재열기·엔진 가져오기에서 기대 조건이 유지되는지 확인합니다.')

def pixels():
    fig,ax=canvas('진행 방향과 그림의 방향이 같은 신호를 주는가','자체 8×8 실루엣 · 오른쪽 코와 뒤쪽 가방으로 앞뒤를 구분')
    grid=np.zeros((8,8));grid[1:4,3:5]=1;grid[2,5]=1;grid[4:6,3:5]=1;grid[4:6,2]=1;grid[6,2:6]=1
    for j,(pattern,label) in enumerate([(grid,'오른쪽을 향한 윤곽'),(np.fliplr(grid),'왼쪽을 향한 윤곽')]):
        x0=110+j*565
        for y in range(8):
            for x in range(8):ax.add_patch(Rectangle((x0+x*48,280+y*48),48,48,fc=BLUE if pattern[y,x] else '#edf2e8',ec=LIGHT,lw=.7))
        text(ax,x0+192,735,label,24,ha='center')
        if j==0:arrow(ax,x0+90,830,x0+310,830,GREEN,5)
        else:arrow(ax,x0+310,830,x0+90,830,GREEN,5)
    save(fig,'pixel_direction','S37','자체 픽셀 실루엣. 얼굴의 돌출과 등쪽 가방이 진행 방향과 함께 읽히도록 만든 예입니다. 영상 속 캐릭터 원본을 추출한 스프라이트가 아닙니다.')
    fig,ax=canvas('프레임마다 같은 바닥 기준점을 유지하기','자체 두 프레임 · 투명 영역의 경계와 발의 기준점은 다른 자료')
    for x,dy,l,c in [(260,0,'기준 맞음',GREEN),(860,-70,'몸 전체가 떠서 튐',RED)]:
        ax.add_patch(Rectangle((x-150,300),300,400,fc='none',ec=LIGHT,lw=3));ax.plot([x-200,x+200],[700,700],color=INK,lw=3)
        ax.add_patch(Rectangle((x-55,400+dy),110,150,fc=BLUE));ax.add_patch(Circle((x,355+dy),50,fc=BLUE));ax.plot([x-30,x-65,x-110],[550+dy,625+dy,700+dy],color=BLUE,lw=15);ax.plot([x+30,x+70,x+110],[550+dy,620+dy,660+dy],color=BLUE,lw=15)
        ax.add_patch(Circle((x,700),12,fc=c));text(ax,x,800,l,24,c,ha='center')
    text(ax,600,900,'캐릭터 동작의 변화와 캔버스 안 위치 오차를 나누어 확인',23,ha='center')
    save(fig,'pixel_anchor','S37','자체 기준점 비교. 왼쪽은 지지 발과 바닥선이 맞고 오른쪽은 같은 자세 전체를 위로 옮겨 의도하지 않은 뜀을 만든 경우입니다. 실제 걷기 프레임 데이터가 아닌 확대 설명 모형입니다.')

def benchmark():
    fig,ax=canvas('비교 전에 시작 조건과 합격 조건을 같이 고정하기','자체 건널목 과제 · 같은 지시문만으로 작업량이 같아지지는 않음')
    for y,l,r,c in [(250,'시작 상태','엔진 · 자산 · 참고 그림',BLUE),(450,'허용 작업','재시도 · 사람 수정 · 외부 자료',GOLD),(650,'합격 조건','구조 · 동작 · 재열기',GREEN),(850,'기록 단위','첫 결과 / 합격까지 전체 시간',RED)]:node(ax,60,y-60,320,120,l,c,size=25);text(ax,440,y,r,24)
    save(fig,'benchmark_contract','S38','자체 비교 계약. 시작 프로젝트, 허용 작업과 종료 조건을 함께 기록해야 시간과 비용을 같은 의미로 읽을 수 있습니다.')
    fig,ax=canvas('첫 결과가 빠른 것과 합격이 빠른 것은 다를 수 있습니다','자체 가상 시간 예 · 실제 영상 속 모델을 측정한 자료가 아님')
    for y,l,initial,fix,c in [(360,'A',3,7,BLUE),(640,'B',6,2,GREEN)]:
        text(ax,85,y+50,l,30,c);start=200;scale=80
        ax.add_patch(Rectangle((start,y),initial*scale,100,fc=c));ax.add_patch(Rectangle((start+initial*scale,y),fix*scale,100,fc=GOLD));text(ax,start+initial*scale/2,y+50,str(initial)+'분',24,'white',ha='center');text(ax,start+initial*scale+fix*scale/2,y+50,'추가 '+str(fix)+'분',24,'white',ha='center');text(ax,start+(initial+fix)*scale+15,y+50,str(initial+fix)+'분',23)
    text(ax,200,245,'색 · 첫 실행물 / 금색 · 합격까지 추가 작업',23);text(ax,600,850,'A는 첫 결과 3분, 최종 10분 / B는 첫 결과 6분, 최종 8분',23,ha='center')
    save(fig,'benchmark_time','S38','자체 시간 예시. A 3+7=10분, B 6+2=8분입니다. 첫 결과와 전체 합격 시간을 나누면 서로 다른 결론이 나올 수 있음을 보여 줍니다.')

def prototype():
    fig,ax=canvas('한 질문을 시험하는 데 필요한 범위부터 만들기','자체 점프 시제품 · 조작 질문과 관계없는 기능은 다음 단계로')
    ax.add_patch(Circle((385,520),255,fc='#e4efdf',ec=GREEN,lw=3));text(ax,385,380,'이번 질문',28,GREEN,ha='center');text(ax,385,505,'짧게 / 길게 눌러\n틈을 넘는가',28,ha='center');text(ax,385,670,'이동 · 점프 · 재시작',22,ha='center')
    for y,l in [(310,'상점'),(510,'대규모 맵'),(710,'장비 제작')]:node(ax,790,y,300,100,l,MUTED,size=26)
    text(ax,600,880,'작은 범위도 반복해서 시험할 수 있어야 시제품으로 유용함',23,ha='center')
    save(fig,'prototype_scope','S39','자체 범위 결정. 이번 질문인 점프 조작을 확인할 최소 기능을 만들고, 관련 없는 큰 기능은 별도 후보로 남깁니다.')
    fig,ax=canvas('캐릭터 위치만 돌려놓아도 재시작이 끝날까','자체 실패 후 초기화 예 · 어떤 상태를 되돌릴지 미리 정하기')
    for i,(l,a,b) in enumerate([('위치','낭떠러지','출발점'),('속도','아래로 낙하','0'),('코인','이번 시도 3개','이번 시도 0개'),('상태','실패 처리 중','플레이 중')]):
        y=260+i*170;text(ax,65,y+45,l,23);node(ax,260,y,320,90,a,RED,size=23);arrow(ax,595,y+45,690,y+45);node(ax,710,y,380,90,b,GREEN,size=23)
    save(fig,'restart_state','S39','자체 재시작 계약. 이번 시도에서 모은 코인을 초기화하는 예입니다. 게임마다 보존할 자료는 다를 수 있으므로 위치와 나머지 상태를 따로 정합니다.')

def automation():
    fig,ax=canvas('문이 열리는 중의 입력도 규칙에 포함됩니다','자체 상태도 · 열쇠는 소모하지 않고 재입력은 무시하는 예')
    for x,y,l,c in [(70,250,'잠김',RED),(720,250,'닫힘',BLUE),(720,650,'열리는 중',GOLD),(70,650,'열림',GREEN)]:node(ax,x,y,330,110,l,c,size=27)
    arrow(ax,420,305,700,305);text(ax,560,245,'열쇠 확인·잠금 해제',20,ha='center');arrow(ax,885,380,885,630);text(ax,900,505,'상호작용',21);arrow(ax,700,705,420,705);text(ax,560,760,'애니메이션 완료',21,ha='center')
    text(ax,600,900,'열리는 중 재입력 → 상태 유지 / 중복 애니메이션 없음',23,ha='center')
    save(fig,'door_states','S41','자체 문 상태도. 잠금 해제·열기 시작·완료를 나누고 열리는 중의 재입력은 무시합니다. 코드 이름보다 실제 상태 전환을 공유하기 위한 그림입니다.')
    fig,ax=canvas('함수 존재가 아니라 행동 결과로 검사합니다','자체 문 검수표 · 시작 상태와 입력을 함께 기록')
    cols=[65,410,760];width=[330,330,370]
    for x,w,l in zip(cols,width,['시작 상태','입력','기대 결과']):node(ax,x,230,w,90,l,BLUE,size=24)
    rows=[('잠김·열쇠 없음','상호작용','변화 없음'),('닫힘·해제됨','상호작용','한 번 열기 시작'),('열리는 중','빠른 연타','중복 실행 없음'),('열림','다시 입력','규칙대로 유지')]
    for j,row in enumerate(rows):
        for x,w,l in zip(cols,width,row):node(ax,x,350+j*130,w,105,l,INK,size=21)
    save(fig,'automation_evidence','S41','자체 행동 검사표. 함수 이름이나 파일 생성 여부가 아니라 상태별 입력에서 관찰할 결과를 확인합니다.')

def sheet():
    fig,ax=canvas('입력값과 계산 결과의 연결을 남기기','자체 판매표 · 수량 × 개당 가격 = 매출, 단위는 골드')
    x=[70,350,590,850];w=[260,220,240,280];headers=['아이템','수량·개','가격·골드/개','매출·골드'];rows=[['물약','3','10','30'],['폭탄','2','25','50']]
    for xx,ww,l in zip(x,w,headers):node(ax,xx,270,ww,100,l,BLUE,size=22)
    for i,row in enumerate(rows):
        for j,(xx,ww,l) in enumerate(zip(x,w,row)):node(ax,xx,390+i*130,ww,100,l,GREEN if j==3 else BLUE,size=27)
    arrow(ax,480,700,970,700,GREEN,3);text(ax,600,660,'입력 참조 → 행별 곱셈 → 매출 합계',23,ha='center');node(ax,820,760,310,100,'합계 80골드',GREEN,size=25)
    save(fig,'sheet_lineage','S42','자체 판매 계산. 3×10=30, 2×25=50, 합계 80골드입니다. 파랑은 입력, 초록은 계산 결과이며 본문과 같은 값을 사용했습니다.')
    fig,ax=canvas('숫자처럼 보이는 텍스트가 합계에서 빠질 수 있습니다','자체 범위 합계 예 · 계산 성공과 입력 유효성은 별도 검사')
    for y,l,c in [(280,'D2 · 숫자 30',GREEN),(450,'D3 · 텍스트 "50"',RED)]:node(ax,100,y,540,110,l,c,size=28)
    node(ax,775,365,340,140,'SUM 결과\n30',GOLD,size=28);arrow(ax,655,335,760,405,GREEN,3);ax.plot([655,735],[505,505],color=RED,lw=3);text(ax,700,550,'합산 제외',19,RED,ha='center')
    text(ax,600,730,'기대 합계 80과 다름 → 자료형·누락 여부를 확인',25,RED,ha='center');text(ax,600,845,'표시 서식만 바꾸는 것과 실제 숫자 변환도 구별하기',23,ha='center')
    save(fig,'sheet_missing','S42','자체 SUM 범위 예. 숫자 30과 텍스트 "50"이 있는 범위에서 텍스트가 제외되어 30만 합산되는 상황입니다. 실제 값 80을 기대한다면 자료형 검사가 필요합니다.')

if __name__=='__main__':
    asset();pixels();benchmark();prototype();automation();sheet()
    (BASE/'figure-manifest-batch23.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
