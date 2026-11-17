from render_figures import *
import numpy as np

def crop():
    fig,ax=canvas('밭 한 칸의 상태가 입력과 시간에 따라 바뀝니다','자체 농사 고리 · 이번 예에서는 물을 준 뒤 다음 날 수확 가능')
    for x,y,l,c in [(65,260,'빈 땅',BLUE),(735,260,'씨앗 심음',GOLD),(735,650,'물 줌',GREEN),(65,650,'수확 가능',RED)]:node(ax,x,y,380,125,l,c,size=28)
    arrow(ax,465,320,715,320);text(ax,590,260,'씨앗 사용',21,ha='center');arrow(ax,925,405,925,630);text(ax,940,510,'물주기',20);arrow(ax,715,710,465,710);text(ax,590,775,'다음 날',21,ha='center');arrow(ax,255,630,255,405);text(ax,110,515,'수확',21)
    save(fig,'solo_crop_states','S47','자체 한 칸 농사 상태도. 빈 땅에 씨앗을 심고 물을 준 뒤 다음 날 수확하여 다시 빈 땅으로 돌아옵니다. 실제 Stardew Valley 성장 규칙을 복원한 그림이 아닙니다.')
    fig,ax=canvas('한 기능 안에도 여러 제작 역할이 연결됩니다','자체 물주기 작업 · 역할마다 만든 결과가 같은 상태를 가리켜야 함')
    for i,(a,b,c) in enumerate([('코드','물 준 상태 저장',BLUE),('그림','젖은 흙으로 구별',GREEN),('소리·안내','입력 결과 전달',GOLD),('검수','중복 사용·재열기 확인',RED)]):node(ax,70,220+i*175,320,115,a,c,size=26);text(ax,440,278+i*175,b,24)
    save(fig,'solo_roles','S47','자체 역할 연결. 코드만 완성하거나 모든 그림만 먼저 늘리기보다 한 기능에서 상태와 표현과 검수를 연결합니다.')

def remix():
    fig,ax=canvas('새 조건이 상자를 미는 순서를 바꾸는가','자체 5×5 실험 지도 · 정답 경로를 측정한 실제 게임 지도가 아님')
    n=5;sz=115;x0=310;y0=260
    for y in range(n):
        for x in range(n):ax.add_patch(Rectangle((x0+x*sz,y0+y*sz),sz,sz,fc='#edf2e8',ec=LIGHT,lw=2))
    for x,y,l,c in [(0,4,'S',BLUE),(2,2,'B',GOLD),(4,0,'G',RED),(4,4,'O',GREEN)]:node(ax,x0+x*sz+8,y0+y*sz+8,sz-16,sz-16,l,c,size=30)
    text(ax,90,350,'S 출발\nB 상자\nG 목표\nO 보충',23);text(ax,600,900,'이동할 때 산소 소모 → 보충 방문과 상자 경로를 함께 계획',22,ha='center')
    save(fig,'remix_map','S49','자체 규칙 실험용 배치. 상자 밀기에 산소 보충 지점을 더하고 경로와 행동 순서가 달라지는지 시험합니다. 완성 퍼즐의 해법이나 밸런스 결과는 아닙니다.')
    fig,ax=canvas('자원이 숫자 장식인지 실제 판단인지 비교하기','자체 두 조건 · 행동 순서와 바꾼 이유를 관찰')
    for y,l,b,c in [(280,'산소 없음','상자 경로와 막힘을 계획',BLUE),(540,'산소 있음','보충 시점 + 상자 경로를 계획',GREEN)]:node(ax,60,y,350,135,l,c,size=27);text(ax,460,y+65,b,23)
    text(ax,600,815,'항상 같은 길에 클릭만 추가된다면 새 판단은 약할 수 있음',23,ha='center');text(ax,600,890,'너무 넉넉함 / 도달 불가 / 의미 있는 선택을 구별',23,ha='center')
    save(fig,'remix_decisions','S49','자체 전후 질문. 산소 조건이 실제 경로와 순서를 바꾸는지, 단지 의무 행동만 늘리는지 비교합니다.')

def feedback():
    fig,ax=canvas('한 번의 플레이를 목표·입력·변화·결과로 보여 주기','자체 방 퍼즐 · 아래 판을 선택해 돌리면 높은 출구로 갈 수 있는 모형')
    for ox,label,rot in [(100,'회전 전',False),(680,'회전 후',True)]:
        ax.add_patch(Rectangle((ox,300),420,430,fc='#edf2e8',ec=INK,lw=2));ax.plot([ox+10,ox+410],[710,710],color=INK,lw=4);ax.add_patch(Circle((ox+65,680),22,fc=BLUE));ax.add_patch(Rectangle((ox+340,420),65,100,fc=GOLD))
        ax.plot([ox+180,ox+400] if not rot else [ox+180,ox+307.15],[710,710] if not rot else [710,530.73],color=GREEN,lw=20);text(ax,ox+210,815,label,26,ha='center')
    arrow(ax,545,520,650,520,BLUE,4);text(ax,600,235,'입력: 판 선택 → 회전',25,ha='center')
    save(fig,'feedback_scene','S52','자체 방의 전후 개념도. 회전하는 판과 높은 출구의 관계를 보여 주어 예상 입력과 목표를 질문합니다. 실제 충돌을 검증한 레벨 설계는 아닙니다.')
    fig,ax=canvas('관찰·가설·해결 제안을 서로 다른 자료로 남기기','자체 피드백 기록 · 제안을 곧바로 유일한 정답으로 확정하지 않음')
    for i,(a,b,c) in enumerate([('관찰','판이 회전하는 줄 몰랐음',BLUE),('원인 가설','회전 가능 신호가 약함',GOLD),('작은 변경','표식 또는 움직임 미리보기',GREEN),('재확인','처음 본 사람이 입력을 예상?',RED)]):
        y=210+i*175;node(ax,65,y,340,110,a,c,size=26);text(ax,450,y+55,b,23)
        if i<3:arrow(ax,235,y+115,235,y+165,c,2)
    save(fig,'feedback_record','S52','자체 피드백 처리. 실제 말과 원인 추정, 수정 후보, 다시 확인할 질문을 분리해 기록합니다.')

def iteration():
    fig,ax=canvas('입력 시점과 접지 상태를 같은 시간축에서 보기','자체 발판 끝 실패 예 · 위치가 아니라 시간 관계로 원인을 좁히기')
    for y,l in [(330,'접지 상태'),(600,'점프 입력')]:text(ax,65,y,l,24);ax.plot([330,1100],[y,y],color=LIGHT,lw=3)
    ax.plot([330,700],[330,330],color=GREEN,lw=12);ax.plot([700,1100],[330,330],color=RED,lw=6);ax.plot([700,700],[250,750],color=MUTED,ls='--',lw=2);text(ax,700,205,'발판을 벗어남',23,ha='center');ax.add_patch(Circle((790,600),18,fc=BLUE));text(ax,790,690,'늦은 입력',23,BLUE,ha='center');text(ax,600,850,'짧은 입력 여유를 허용할지 경험의 목표에 맞게 결정',23,ha='center')
    save(fig,'iteration_trace','S53','자체 시간 추적. 발판을 벗어난 뒤 들어온 입력이 왜 실행되지 않았는지 접지 상태와 비교합니다. 허용 시간은 실제 게임의 설정값을 뜻하지 않습니다.')
    fig,ax=canvas('수정의 효과와 새 문제를 버전별로 비교하기','자체 점프 개선 기록 · 이전 성공 장면도 다시 확인')
    cols=[60,420,780];w=340
    for x,l in zip(cols,['버전 1','버전 2','버전 3']):node(ax,x,250,w,90,l,BLUE,size=26)
    for x,l,c in [(60,'발판 끝\n늦은 입력 실패',RED),(420,'입력 여유 추가\n벽 접지 오류 발견',GOLD),(780,'바닥 판정 분리\n기존 여유 유지',GREEN)]:node(ax,x,420,w,230,l,c,size=24)
    text(ax,600,825,'변경 조건 · 통과 장면 · 남은 문제를 함께 기록',25,ha='center')
    save(fig,'iteration_versions','S53','자체 버전 비교. 입력 여유 개선과 벽의 접지 오류를 구별하고, 새 수정에서 이전의 좋은 동작도 유지되는지 확인합니다.')

def pong():
    fig,ax=canvas('움직이는 공을 시작·종료·재시작의 고리로 연결하기','자체 1인 패들 게임 · 성공과 실패에서 초기화할 자료를 정함')
    for x,y,l,c in [(70,250,'준비',BLUE),(720,250,'플레이 중',GREEN),(720,650,'성공 / 실패',RED),(70,650,'초기화',GOLD)]:node(ax,x,y,350,120,l,c,size=28)
    arrow(ax,440,310,700,310);text(ax,570,240,'시작 입력',21,ha='center');arrow(ax,895,390,895,630);text(ax,900,500,'목표 / 놓침',20);arrow(ax,700,710,440,710);text(ax,570,785,'재시작 입력',21,ha='center');arrow(ax,245,630,245,390);text(ax,85,500,'준비 완료',20)
    save(fig,'pong_states','S54','자체 작은 게임 상태도. 종료 시 이동·점수 갱신을 멈추고 재시작에서는 점수·공·속도·표시를 초기화합니다.')
    fig,ax=canvas('패들 중심만 화면 안에 있으면 충분하지 않습니다','자체 이동 경계 · 패들의 반폭까지 고려')
    ax.add_patch(Rectangle((180,280),840,440,fc='#edf2e8',ec=INK,lw=3))
    ax.add_patch(Rectangle((930,600),180,35,fc=RED));ax.add_patch(Circle((1020,618),9,fc=INK));text(ax,1020,790,'중심은 경계\n패들은 밖으로 나감',22,RED,ha='center')
    ax.add_patch(Rectangle((840,480),180,35,fc=GREEN));ax.add_patch(Circle((930,498),9,fc=INK));arrow(ax,930,440,1020,440,GREEN,3);text(ax,940,390,'남길 반폭',22,GREEN,ha='center')
    text(ax,600,885,'화면 크기와 패들 폭이 바뀌어도 같은 의도인지 확인',23,ha='center')
    save(fig,'pong_bounds','S54','자체 화면 경계 예. 빨간 패들의 중심이 오른쪽 경계에 있어도 절반은 화면 밖입니다. 반폭을 고려한 중심 범위를 정해야 합니다.')

def portfolio():
    fig,ax=canvas('물약 두 개를 추가할 때 실제로 들어갈 수 있는 수는?','자체 인벤토리 · 10칸, 같은 물약은 한 칸에 최대 5개, 빈칸 없음')
    for i in range(10):
        x=90+(i%5)*210;y=300+(i//5)*220
        node(ax,x,y,180,150,'물약 4/5' if i==0 else '다른 물건',GREEN if i==0 else MUTED,size=22)
    text(ax,600,230,'추가 요청: 물약 2개',26,BLUE,ha='center');text(ax,600,815,'기존 칸에는 1개만 가능 → 1개 반영, 1개 남음',25,GREEN,ha='center');text(ax,600,890,'부분 수용 정책을 선택한 자체 예 · 전체 거절 정책도 가능',22,ha='center')
    save(fig,'portfolio_inventory','S56','자체 경계 조건. 최대 5개 묶음에 4개가 있고 빈칸이 없는 상태에서 2개를 요청하면 부분 수용 정책에서는 1개만 추가됩니다.')
    fig,ax=canvas('결과 화면을 상태 변화와 연결해 증거로 남기기','자체 작업 기록 · 무엇을 생성했는가에서 무엇을 검수했는가까지')
    for i,(a,b,c) in enumerate([('문제','전체 개수만 보고 빈칸을 오판',RED),('결정','남은 수량을 돌려주는 부분 수용',BLUE),('변경','기존 묶음의 여유를 먼저 계산',GOLD),('증거','4 → 5 / 반영 1 / 남음 1',GREEN)]):node(ax,65,210+i*175,310,115,a,c,size=26);text(ax,420,268+i*175,b,23)
    save(fig,'portfolio_evidence','S56','자체 포트폴리오 기록. 문제·정책·코드 변경·상태 결과를 연결합니다. 도구 사용 목록만으로 설명되지 않는 판단과 검수의 근거입니다.')

if __name__=='__main__':
    crop();remix();feedback();iteration();pong();portfolio()
    (BASE/'figure-manifest-batch25.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
