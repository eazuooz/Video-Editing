"""Figures with explicit time, space and state for four additional columns."""
from render_figures import *
import numpy as np

def timing():
    fig,ax=canvas('반복을 시작시키는 시계가 달라집니다','세로 표시: 발사 시점 / 첫 발은 모두 같은 틱 0에서 시작')
    xf=lambda t:260+t*2.35
    for base,title,series,col in [(260,'같은 간격 100틱',[[0,100,200,300]]*3,GREEN),(620,'매번 작은 차이 추가',[[0,100,199,301],[0,102,200,299],[0,98,199,300]],BLUE)]:
        text(ax,55,base-65,title,25,col)
        for j,times in enumerate(series):
            y=base+j*88;text(ax,80,y,chr(65+j)+' 병사',22)
            ax.plot([xf(0),xf(320)],[y,y],color=LIGHT,lw=2)
            for t in times:ax.plot([xf(t),xf(t)],[y-18,y+18],color=col,lw=4)
            text(ax,1090,y,str(times[-1]),20,col,ha='center')
    text(ax,260,900,'0',20,ha='center');text(ax,xf(100),900,'100',20,ha='center');text(ax,xf(200),900,'200',20,ha='center');text(ax,xf(300),900,'300틱',20,ha='center')
    save(fig,'fire_timing','S02','자체 발사 시각 비교. 위는 세 병사가 0·100·200·300틱에 함께 발사합니다. 아래는 A: 0·100·199·301, B: 0·102·200·299, C: 0·98·199·300틱인 예입니다. 오른쪽 숫자는 마지막 표시의 시각입니다. 실제 해병의 설정값이 아닙니다.')

def navigation():
    fig,ax=canvas('같은 경계라도 칸 크기에 따라 다르게 요약됩니다','예제 판정: 칸 중심이 다리 안에 있으면 통과 가능으로 저장')
    for x0,n,label in [(70,4,'큰 통행 칸'),(660,16,'작은 통행 칸')]:
        y0=290;size=450;cell=size/n
        ax.add_patch(Rectangle((x0,y0),size,size,fc='#e6f0f6',ec='none'))
        for j in range(n):
            for i in range(n):
                cx=(i+.5)*cell;cy=(j+.5)*cell
                ax.add_patch(Rectangle((x0+i*cell,y0+j*cell),cell,cell,fc=('#9bc6a4' if abs(cy-cx)<70 else 'none'),ec=LIGHT,lw=1))
        for d in [-70,70]:
            pts=[(x0+max(0,-d),y0+max(0,d)),(x0+min(size,size-d),y0+min(size,size+d))]
            ax.plot([p[0] for p in pts],[p[1] for p in pts],color=INK,lw=3)
        text(ax,x0+size/2,220,label,28,ha='center')
        text(ax,x0+size/2,800,f'{n} × {n} 칸',24,ha='center')
    text(ax,70,885,'검은 선: 실제 다리 경계 / 초록 칸: 통과 가능 / 하늘색: 강',23)
    save(fig,'navigation_resolution','S03','자체 통행 지도 모형. 같은 비스듬한 띠에 칸 중심 기준의 통과 판정을 적용했습니다. 작은 칸이 경계를 더 세밀하게 따르지만 칸 수는 늘어납니다. 이미지의 초록 칸은 특정 게임에서 추출한 데이터가 아닙니다.')
    fig,ax=canvas('중심점의 길과 몸이 지나갈 공간은 다릅니다','검은 벽 사이를 작은 유닛과 큰 유닛이 지나가는 자체 비교')
    for x0,r,label,col in [(70,38,'작은 몸: 여유 있음',GREEN),(660,92,'큰 몸: 벽과 겹침',RED)]:
        y0=255;w=450;h=560;left=x0+145;right=x0+305;center=x0+225
        ax.add_patch(Rectangle((x0,y0),145,h,fc=INK));ax.add_patch(Rectangle((right,y0),145,h,fc=INK))
        ax.add_patch(Rectangle((left,y0),r,h,fc='#d98978',alpha=.4));ax.add_patch(Rectangle((right-r,y0),r,h,fc='#d98978',alpha=.4))
        ax.add_patch(Circle((center,600),r,fc='#fffef9',ec=col,lw=4));arrow(ax,center,550-r,center,350,col,4)
        ax.add_patch(Circle((center,600),5,fc=col))
        text(ax,x0+225,890,label,25,col,ha='center')
    save(fig,'navigation_clearance','S03','자체 유닛 크기 비교. 붉은 띠는 벽에서 유닛 반지름만큼 확보해야 할 중심점의 여유입니다. 큰 유닛에서는 두 띠가 겹쳐 가능한 중심 경로가 사라집니다. 가운데 점의 경로가 보인다고 몸이 통과할 수 있는 것은 아닙니다.')

def worker():
    fig,ax=canvas('예외의 범위를 상태와 상대 종류로 나눕니다','이 글의 시제품 정책: 지형은 항상 유지하고 유닛 관계만 선택')
    cols=[70,420,765];width=[350,345,360]
    headers=['행동 상태','유닛과의 겹침','지형·건물과 겹침']
    for x,w,h in zip(cols,width,headers):node(ax,x,235,w,100,h,size=22)
    for j,(state,a,b) in enumerate([('일반 이동','막음','막음'),('채집·운반','허용','막음'),('정지·공격','막음','막음')]):
        y=335+j*130
        for x,w,val in zip(cols,width,[state,a,b]):
            col=GREEN if val=='허용' else INK
            node(ax,x,y,w,130,val,col,'#e6f3e9' if val=='허용' else '#fffef9',24)
    arrow(ax,160,810,380,810,GREEN);text(ax,420,810,'상태가 끝날 때 예외 해제와 겹침 분리도 처리',22)
    save(fig,'worker_rules','S04','자체 충돌 정책표. 채집·운반 상태에서 유닛끼리의 겹침만 허용하고 지형·건물 관계는 유지하는 예입니다. 전투용 회피·물리·통행 처리가 같은 설정이라고 단정하지 않습니다.')

def relative():
    fig,ax=canvas('월드 위치와 화면 위치를 나누어 봅니다','단순 2D: 화면 위치 = 물체 위치 - 카메라 위치 / 숫자는 처음 → 나중')
    for y,label,values in [(250,'① 캐릭터와 카메라가 함께 전진',[('캐릭터',5,8),('카메라',4,7),('화면 차이',1,1)]),(590,'② 캐릭터·카메라 고정, 배경만 이동',[('캐릭터',5,5),('카메라',4,4),('배경 표식',8,5)])]:
        text(ax,55,y-45,label,25)
        for j,(name,start,end) in enumerate(values):
            yy=y+j*80;text(ax,85,yy,name,22);text(ax,430,yy,str(start),25,BLUE,ha='center');arrow(ax,510,yy,685,yy,BLUE);text(ax,770,yy,str(end),25,BLUE,ha='center')
    text(ax,85,900,'전진감이 비슷해도, 충돌이 읽는 월드 상태는 다릅니다.',22)
    save(fig,'relative_motion','S06','자체 좌표 변화 표. 위는 캐릭터 5→8, 카메라 4→7로 움직여 화면 차이 1을 유지합니다. 아래는 둘을 고정한 채 배경 표식만 8→5로 이동시킵니다. 회전·원근·확대를 제외한 2D 모형입니다.')
    fig,ax=canvas('한 장면의 배경을 서로 다른 속도의 층으로 나누기','같은 시간 동안 원경보다 근경이 더 많이 이동하는 자체 예시')
    for j,(label,speed,colour) in enumerate([('원경 · 먼 산',100,MUTED),('중경 · 나무',230,GREEN),('근경 · 울타리',420,BLUE)]):
        y=280+j*220;text(ax,65,y-40,label,25,colour)
        ax.plot([95,1100],[y+70,y+70],color=LIGHT,lw=2)
        for k in [0,1,2]:
            x=520+k*180
            if j==0:ax.add_patch(Polygon([(x,y+65),(x+65,y-30),(x+130,y+65)],fc='#c9d9cf',ec=colour,lw=2))
            elif j==1:ax.plot([x+60,x+60],[y-15,y+65],color=colour,lw=5);ax.add_patch(Circle((x+60,y-15),35,fc='#c7dfbc',ec=colour,lw=2))
            else:ax.plot([x+60,x+60],[y-25,y+65],color=colour,lw=6);ax.plot([x,x+160],[y+10,y+10],color=colour,lw=4)
        arrow(ax,520,y+100,520-speed,y+100,colour,4)
    text(ax,65,905,'화살표 길이는 이동량의 비교입니다. 실제 거리·속도를 측정한 값은 아닙니다.',21)
    save(fig,'parallax_layers','S06','자체 층별 스크롤 도식. 같은 시간에 먼 산 100, 나무 230, 울타리 420의 설명용 화면 단위만큼 왼쪽으로 이동시킵니다. 층별 비율로 깊이 단서를 만드는 예시이며 특정 게임의 설정값이 아닙니다.')

if __name__=='__main__':
    timing();navigation();worker();relative()
    (BASE/'figure-manifest-batch2.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
