"""Render editable, authored explanatory vector figures and native PNG previews."""
from pathlib import Path
import json, math, hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon
from matplotlib import font_manager as fm

BASE=Path(__file__).resolve().parent
OUT=BASE.parent/'evidence/column-v2'
OUT.mkdir(parents=True,exist_ok=True)
FONT=fm.FontProperties(fname='C:/Windows/Fonts/malgun.ttf')
plt.rcParams['svg.fonttype']='path'
INK='#19352c'; BLUE='#176eaa'; GREEN='#247e65'; RED='#bf4538'; GOLD='#b88117'; MUTED='#65746d'; LIGHT='#d9e2dc'
manifest=[]

def canvas(title,sub=''):
    fig=plt.figure(figsize=(12,10),dpi=100,facecolor='#fffef9')
    ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1200);ax.set_ylim(1000,0);ax.axis('off')
    heading=text(ax,55,62,title,29,weight='bold')
    fig.canvas.draw()
    width=heading.get_window_extent(fig.canvas.get_renderer()).width
    if width>1090:heading.set_fontsize(29*1090/width)
    if sub:text(ax,55,114,sub,19,color=MUTED)
    ax.plot([55,1145],[150,150],color=GOLD,lw=3)
    text(ax,55,966,'얌얌코딩 · 이 글을 위한 설명 모형 / 실제 게임의 내부 측정값이 아닙니다.',15,color=MUTED)
    return fig,ax

def text(ax,x,y,s,size=23,color=INK,weight='normal',ha='left',va='center'):
    return ax.text(x,y,s.replace('−','-').replace('₀','0'),fontsize=size,color=color,fontproperties=FONT,weight=weight,ha=ha,va=va,linespacing=1.5)

def arrow(ax,x1,y1,x2,y2,color=BLUE,lw=3,style='-|>'):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle=style,mutation_scale=23,color=color,lw=lw))

def node(ax,x,y,w,h,label,color=INK,fill='#f1f5ef',size=22):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=fill,edgecolor=color,lw=2))
    text(ax,x+w/2,y+h/2,label,size,color,ha='center')

def save(fig,key,article,caption):
    for ext in ['svg','png']:
        fig.savefig(OUT/f'{key}.{ext}',dpi=100,facecolor=fig.get_facecolor())
    plt.close(fig)
    manifest.append(dict(key='diagram_'+key,article=article,path=str((OUT/f'{key}.png').resolve()),
                         vector=str((OUT/f'{key}.svg').resolve()),caption=caption,
                         sha256=hashlib.sha256((OUT/f'{key}.png').read_bytes()).hexdigest(),
                         author='얌얌코딩',kind='authored-explanatory-model',dimensions=[1200,1000]))

def replay():
    fig,ax=canvas('명령은 같아도 바뀌는 상태는 다릅니다','왼쪽: 위치 변화 / 오른쪽: 같은 틱의 상태 기록')
    for j,(label,x,e,hp) in enumerate([('시작',0,2,3),('틱 1 · 이동',1,2,3),('틱 2 · 이동',2,2,3),('틱 3 · 사격',2,1,2)]):
        y=240+j*172;text(ax,55,y-45,label,22)
        for k in range(4):ax.add_patch(Rectangle((235+k*105,y-30),105,65,fc='none',ec=LIGHT,lw=1.5))
        if j:ax.add_patch(Circle((287.5+([0,0,1,2][j])*105,y+2),19,fill=False,ec=MUTED,lw=2))
        ax.add_patch(Circle((287.5+x*105,y+2),19,color=BLUE))
        if j in [1,2]:arrow(ax,287.5+(x-1)*105,y-3,287.5+x*105-24,y-3)
        if j==3:arrow(ax,287.5+x*105+30,y,695,y,RED);text(ax,660,y-38,'명중',19,RED)
        text(ax,790,y,f'x = {x}칸\n에너지 {e} · 체력 {hp}',22)
    save(fig,'replay_trace','S01','자체 상태 추적도. 틱 1·2에서는 병사 위치만, 틱 3에서는 에너지와 표적 체력만 바뀝니다. 회색 윤곽은 직전 위치입니다. 본문 표·의사코드와 같은 값을 사용했습니다.')
    fig,ax=canvas('되감기는 이전 저장점에서 다시 시작하기','스냅샷을 읽고 목적지까지의 명령만 순서대로 실행합니다')
    x=lambda t:100+t*82
    y=365;ax.plot([x(0),x(12)],[y,y],color=INK,lw=3)
    for t in range(13):
        ax.plot([x(t),x(t)],[y-12,y+12],color=INK,lw=2);text(ax,x(t),y+50,str(t),18,ha='center')
    for t in [0,4,8,12]:ax.add_patch(Rectangle((x(t)-20,y-25),40,50,fc=GOLD,ec=INK,lw=2))
    text(ax,x(8),y-85,'선택한 저장점',23,GOLD,ha='center')
    text(ax,x(10),y+125,'목적지: 틱 10',23,BLUE,ha='center')
    arrow(ax,x(8),y-135,x(10),y-135,BLUE,5)
    text(ax,(x(8)+x(10))/2,y-185,'명령 9, 10 재실행',20,BLUE,ha='center')
    node(ax,110,610,970,155,'저장 공간 ↑  ←  스냅샷을 더 자주 저장  →  탐색 계산 ↓',size=24)
    text(ax,110,830,'틱 0부터 매번 계산할 수도 있지만,\n긴 기록을 자주 탐색한다면 중간 상태가 유용합니다.',24)
    save(fig,'replay_seek','S01','자체 탐색 설계도. 주황 표시는 저장된 상태, 파란 구간은 틱 8 스냅샷을 읽은 뒤 재실행할 명령 9·10입니다. 이 저장 간격은 특정 게임의 구현을 뜻하지 않습니다.')

def blend():
    fig,ax=canvas('같은 50% 비율보다 먼저 맞춰야 할 발 디딤','정규화 시간 0~1: 서로 다른 길이의 한 주기를 비교하는 기준')
    xs=lambda u:300+760*u
    for section,base,offset,color in [('발 디딤이 맞음',245,0,GREEN),('달리기만 반 주기 어긋남',605,.5,RED)]:
        text(ax,55,base-55,section,24,color)
        for name,y,phase in [('걷기',base,0),('달리기',base+110,offset)]:
            text(ax,65,y,name,24);ax.plot([xs(0),xs(1)],[y,y],color=LIGHT,lw=5)
            for u,label in [(0,'왼발'),(.5,'오른발'),(1,'왼발')]:
                actual=(u+phase)%1 if u<1 else 1
                lab=('오른발' if label=='왼발' else '왼발') if phase else label
                ax.add_patch(Circle((xs(u),y),12,color=color));text(ax,xs(u),y+37,lab,18,color,ha='center')
        for u in [0,.5,1]:ax.plot([xs(u),xs(u)],[base-15,base+125],color=color,ls='--',lw=1.5)
    text(ax,300,875,'0',22,ha='center');text(ax,680,875,'0.5',22,ha='center');text(ax,1060,875,'1',22,ha='center')
    save(fig,'blend_phase','A14','자체 발 접지 시간표. 위는 두 클립이 같은 정규화 시점에 같은 발을 디딥니다. 아래는 달리기만 반 주기 어긋나 서로 다른 지지 자세를 섞는 경우입니다. 클립 길이와 가중치는 이 정렬과 다른 변수입니다.')
    fig,ax=canvas('발 미끄러짐: 세 가지 원인을 따로 보기','어디가 어긋났는지에 따라 바꿀 조건도 달라집니다')
    for y,title,clue,fix in [(245,'① 시간표의 불일치','걷기: 왼발 접지 / 달리기: 오른발 접지','확인: 접지 사건의 정규화 시점'),(480,'② 이동량의 불일치','몸은 빠르게 전진 / 발 동작은 느린 걷기','확인: 실제 이동 속도와 보행 리듬'),(715,'③ 지면과 발 목표의 불일치','원본은 평지 / 실제 바닥은 경사','확인: 지면 높이·발 목표·골반 보정')]:
        text(ax,70,y,title,27,weight='bold');text(ax,70,y+62,clue,23);arrow(ax,100,y+123,225,y+123,GREEN)
        text(ax,255,y+123,fix,23,GREEN)
    save(fig,'blend_causes','A14','자체 진단도. 위상, 이동 속도, 지면 조건은 서로 다른 문제입니다. 발 디딤을 먼저 맞춘 뒤 이동을 켜고, 마지막으로 경사와 IK를 추가하면 문제를 만든 조건을 분리할 수 있습니다.')

def outline():
    fig,ax=canvas('계층은 시간 순서가 아니라 설명의 포함 관계','포획이라는 기능의 어디에서 답을 찾을지 정합니다')
    node(ax,70,410,220,105,'포획 기능',size=26)
    labels=[('사용 조건','대상 · 도구 · 보관 칸'),('처리 순서','검사 · 예약 · 소모 · 판정'),('결과','성공 저장 · 실패 후 턴'),('취소·예외','거절 비용 · 중복 입력')]
    for j,(label,detail) in enumerate(labels):
        y=205+j*172;node(ax,390,y,240,85,label,size=25)
        ax.plot([290,335,335,390],[462,462,y+42,y+42],color=GREEN,lw=2.5)
        arrow(ax,650,y+42,710,y+42,GREEN);text(ax,735,y+42,detail,20)
    text(ax,70,915,'같은 종류의 질문을 묶고, 상세 조건은 그 아래에 둡니다.',22)
    save(fig,'outline_tree','D16','자체 아웃라인 구조. 가지는 처리 순서나 중요도 순위를 뜻하지 않습니다. 포획 기능의 조건·순서·결과·예외를 찾을 위치를 보여 줍니다.')
    fig,ax=canvas('같은 ‘실패’라도 비용을 쓰기 전과 후는 다릅니다','아웃라인에 적은 규칙을 실행 경로로 확인합니다')
    node(ax,100,200,350,95,'포획 입력');arrow(ax,275,298,275,365)
    node(ax,100,370,350,100,'사용 조건 검사')
    arrow(ax,450,420,685,420,RED);node(ax,690,370,400,100,'거절: 비용 없음',RED,'#fff0ec')
    text(ax,550,382,'불충족',21,RED,ha='center')
    arrow(ax,275,470,275,535,GREEN);text(ax,320,503,'충족',20,GREEN)
    node(ax,100,540,350,110,'칸 예약 · 입력 잠금\n도구 소모',size=22)
    arrow(ax,275,650,275,720);node(ax,100,725,350,95,'성공 여부 판정')
    arrow(ax,450,770,685,650,GREEN);node(ax,690,590,400,110,'성공: 저장\n결과 표시 · 전투 종료',GREEN,size=22)
    arrow(ax,450,770,685,825,RED);node(ax,690,775,400,110,'실패: 예약 해제\n도구 소모됨 · 상대 턴',RED,'#fff0ec',size=22)
    save(fig,'capture_flow','D16','자체 포획 규칙의 흐름. 시작 조건에서 거절되면 비용을 쓰지 않습니다. 도구를 소모한 뒤의 실패는 다른 결과입니다. 이 차이를 문장·UI·QA 사례에서 같은 이름으로 연결해야 합니다.')

def normals():
    fig,ax=canvas('평평한 면에서도 조명용 방향은 달라질 수 있습니다','실선: 실제 표면의 단면 / 화살표: 빛 계산에 사용할 법선')
    import numpy as np
    for j,(label,geom) in enumerate([('① 평면 + 같은 법선',False),('② 실제로 굽은 표면',True),('③ 평면 + 바뀐 법선',False)]):
        y=300+j*245;text(ax,55,y-95,label,25)
        xs=np.linspace(180,1060,200);ys=y+22*np.sin((xs-180)/880*4*np.pi) if geom else np.ones_like(xs)*y
        ax.plot(xs,ys,color=INK,lw=4)
        for k,x in enumerate(np.linspace(220,1020,11)):
            a=0 if j==0 else math.atan((22*4*math.pi/880)*np.cos((x-180)/880*4*np.pi))
            yy=y+22*np.sin((x-180)/880*4*np.pi) if geom else y
            arrow(ax,x,yy,x+math.sin(a)*73,yy-math.cos(a)*73,BLUE)
    save(fig,'normal_surface','S34','자체 표면 단면도. 둘째 줄은 기하 자체를 바꾸고, 셋째 줄은 평면을 유지한 채 조명용 법선만 바꿉니다. 노멀 맵의 화살표는 힘이나 표면 변위를 뜻하지 않습니다.')
    fig,ax=canvas('표면의 좌표계도 표면과 함께 돌아갑니다','T: 텍스처 가로 / N: 표면 바깥 / B: 여기서는 화면 안쪽')
    import numpy as np
    for x,y,angle,label in [(320,500,0,'평평한 표면'),(880,500,35,'기울어진 표면')]:
        a=math.radians(angle);T=np.array([math.cos(a),-math.sin(a)]);N=np.array([-math.sin(a),-math.cos(a)]);o=np.array([x,y])
        p=o-T*170;q=o+T*170;ax.plot([p[0],q[0]],[p[1],q[1]],color=INK,lw=5)
        for v,s,c in [(T,'T',GREEN),(N,'N',MUTED)]:
            e=o+v*150;arrow(ax,*o,*e,c);text(ax,e[0]+15,e[1]-15,s,25,c)
        vv=T*.42+N*.91;e=o+vv*180;arrow(ax,*o,*e,BLUE,4);text(ax,e[0]+10,e[1]-25,'n',28,BLUE)
        ax.add_patch(Circle(tuple(o),12,fill=False,ec=INK,lw=2));text(ax,x,y,'×',17,ha='center')
        text(ax,x,y+160,label,25,ha='center')
    node(ax,125,775,950,100,'같은 국소 방향  →  T·B·N으로 변환  →  같은 공간의 빛과 비교',size=23)
    save(fig,'normal_tbn','S34','자체 좌표계 단면도. 두 면의 T·N과 파란 국소 법선 n이 함께 돌아갑니다. B는 두 경우 모두 화면 안쪽입니다. 광원 방향과 비교하기 전에 좌표계를 맞춰야 한다는 뜻이며 실제 게임의 추출 데이터가 아닙니다.')

if __name__=='__main__':
    replay();blend();outline();normals()
    (BASE/'figure-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'figures')
