from render_figures import *
import numpy as np

def rope():
    fig,ax=canvas('점의 위치와 이웃 사이의 길이를 함께 관리하기','위: 점 사슬 / 아래: 같은 질량인 두 점의 거리 보정 예제')
    pts=np.array([[120,270],[300,350],[480,405],[660,405],[840,350],[1020,270]])
    ax.plot(pts[:,0],pts[:,1],color=GOLD,lw=5)
    for j,p in enumerate(pts):ax.add_patch(Circle(tuple(p),14,fc=INK if j in [0,5] else BLUE));text(ax,p[0],p[1]+45,str(j),19,ha='center')
    arrow(ax,570,330,570,460,RED);text(ax,610,500,'중력',21,RED)
    text(ax,80,590,'보정 전',24);text(ax,80,780,'보정 후',24)
    for y,ls,rs,label in [(590,400,700,'현재 거리 300'),(780,450,650,'목표 길이 200')]:
        ax.plot([ls,rs],[y,y],color=GOLD,lw=4)
        for x in [ls,rs]:ax.add_patch(Circle((x,y),15,fc=BLUE))
        text(ax,850,y,label,23)
    arrow(ax,400,640,450,730,GREEN);arrow(ax,700,640,650,730,GREEN)
    text(ax,600,890,'같은 질량의 두 점이 각각 절반을 보정합니다.',22,ha='center')
    save(fig,'rope_chain','S05','자체 점 사슬과 거리 제약 모형. 아래는 두 점의 거리를 300에서 목표 200으로 맞추며 각각 50씩 안쪽으로 보정한 예입니다. 수치는 그림의 설명 단위이며 실제 게임의 로프 설정값이 아닙니다.')
    fig,ax=canvas('양끝만 맞추면 그 사이가 기둥을 지날 수 있습니다','빨간 점선: 허용할 수 없는 직선 / 초록 선: 장애물 밖의 경로')
    ax.add_patch(Rectangle((420,375),280,290,fc='#dedacf',ec=INK,lw=3));text(ax,560,530,'기둥',29,ha='center')
    A=np.array([140,570]);B=np.array([1060,570]);ax.plot([A[0],B[0]],[A[1],B[1]],color=RED,ls='--',lw=4)
    safe=np.array([A,[407,355],[713,355],B]);ax.plot(safe[:,0],safe[:,1],color=GREEN,lw=4)
    for p in safe:ax.add_patch(Circle(tuple(p),12,fc=GREEN))
    text(ax,140,630,'고정점 A',23,ha='center');text(ax,1060,630,'고정점 B',23,ha='center')
    text(ax,560,290,'꺾임점을 기억하고, 직접 연결이 안전해지면 풀어 줍니다.',22,ha='center')
    text(ax,80,830,'흔들리는 모습의 계산과, 반드시 지킬 통과 경로는 역할이 다릅니다.',22)
    save(fig,'rope_path','S05','자체 장애물 회피 모형. 양끝은 모두 장애물 밖이지만 직선은 기둥을 관통합니다. 꺾임점 두 개를 가진 초록 경로는 장애물 밖에 유지됩니다. 복잡한 3D 로프의 전체 제품 알고리즘이 아니라 역할을 나눈 설명입니다.')

def water():
    fig,ax=canvas('배 안쪽에 겹친 외부 수면만 숨깁니다','같은 선체와 같은 수면에서 마스크 적용만 바꾼 단면 모형')
    for offset,label,masked in [(0,'마스크 없음',False),(360,'마스크 적용',True)]:
        text(ax,55,210+offset,label,25)
        hull=np.array([[240,275],[340,540],[860,540],[960,275]])+[0,offset]
        ax.plot(hull[:,0],hull[:,1],color=INK,lw=6)
        y=365+offset
        if masked:
            ax.add_patch(Polygon(hull,fc='#e9c278',alpha=.17,ec=GOLD,lw=2,ls='--'))
            xl=240+90/265*100;xr=960-90/265*100
            ax.plot([55,xl],[y,y],color=BLUE,lw=6);ax.plot([xr,1145],[y,y],color=BLUE,lw=6)
            text(ax,600,y+30,'외부 바다를 숨길 내부 영역',22,GOLD,ha='center')
        else:ax.plot([55,1145],[y,y],color=BLUE,lw=6);text(ax,600,y+40,'선실 안까지 수면이 통과',22,RED,ha='center')
    save(fig,'water_cutaway','S07','자체 선체 단면. 위는 외부 바다 면을 그대로 그린 경우, 아래는 주황 영역 안의 바다 조각만 숨긴 경우입니다. 바다 전체 높이나 선체 위치를 바꾸어 비교한 것이 아닙니다.')
    fig,ax=canvas('같은 시선에서도 들어가기 전·안쪽·나온 뒤가 다릅니다','하나의 닫힌 볼록 마스크를 카메라 밖에서 보는 단순 예제')
    ax.add_patch(Rectangle((430,310),370,320,fc='#f1d9a2',ec=GOLD,lw=3));text(ax,615,275,'숨길 공간',25,GOLD,ha='center')
    arrow(ax,100,470,1120,470,INK,3);text(ax,100,540,'카메라',23,ha='center')
    for x,label,col in [(270,'바깥: 유지',BLUE),(615,'안쪽: 숨김',RED),(990,'바깥: 유지',BLUE)]:
        ax.add_patch(Circle((x,470),15,fc=col));text(ax,x,730,label,23,col,ha='center')
        ax.plot([x,x],[490,680],color=col,ls='--',lw=1.5)
    text(ax,430,590,'d_in',23,GOLD,ha='center');text(ax,800,590,'d_out',23,GOLD,ha='center')
    text(ax,615,845,'수면 후보 깊이가 두 경계 사이에 있을 때 숨깁니다.',24,ha='center')
    save(fig,'water_depth','S07','자체 깊이 구간 모형. 카메라에서 같은 시선을 따라 서로 다른 깊이의 수면 후보를 시험한 그림입니다. d_in과 d_out 사이의 후보만 내부이며, 이 단순 조건은 카메라가 밖에 있는 한 볼록 영역을 가정합니다.')

def foot(ax,x,y,scale=1,color=BLUE):
    shape=np.array([[0,-18],[12,-15],[19,-3],[18,15],[12,27],[10,46],[-7,49],[-14,40],[-11,22],[-17,4],[-12,-12]])
    ax.add_patch(Polygon(shape*scale+[x,y],closed=True,fc=color))

def snow():
    fig,ax=canvas('바닥 위 위치를 텍스처의 주소와 연결합니다','같은 접촉을 공간상의 자리와 그림의 칸으로 표현한 자체 모형')
    for x0,label in [(90,'눈 구역을 위에서 보기'),(690,'눌림 기록 텍스처')]:
        y0=310;size=390;n=10;cell=size/n
        for j in range(n):
            for i in range(n):ax.add_patch(Rectangle((x0+i*cell,y0+j*cell),cell,cell,fc='#f1f5ef',ec=LIGHT,lw=1))
        foot(ax,x0+5.5*cell,y0+4*cell,1.7,BLUE)
        text(ax,x0+size/2,235,label,24,ha='center')
        arrow(ax,x0,y0+size+45,x0+size,y0+size+45,GREEN);text(ax,x0+size/2,y0+size+95,'가로 위치 → u 주소',22,GREEN,ha='center')
    arrow(ax,510,500,660,500,GREEN,4)
    text(ax,90,890,'카메라가 움직여도 같은 바닥 위치는 같은 텍셀을 가리켜야 합니다.',22)
    save(fig,'snow_mapping','S08','자체 바닥-텍스처 대응도. 같은 발 접촉을 바닥의 위치와 텍스처 칸에 대응시켰습니다. 색은 기록 위치를 알아보기 위한 표시이며 압력이나 높이를 실측한 값이 아닙니다.')
    fig,ax=canvas('현재 접촉이 사라져도 이전 기록은 남습니다','예제 정책: 각 텍셀에서 이전 눌림과 새 접촉 중 큰 값을 유지')
    for x0,label,feet in [(55,'이전 기록\nD_old',[(.3,.3)]),(450,'현재 접촉\nM',[(.65,.6)]),(845,'새 기록\nD_new',[(.3,.3),(.65,.6)])]:
        size=300;y0=370
        for j in range(10):
            for i in range(10):ax.add_patch(Rectangle((x0+i*30,y0+j*30),30,30,fc='#f1f5ef',ec=LIGHT,lw=1))
        for u,v in feet:foot(ax,x0+u*size,y0+v*size,1.6,BLUE)
        text(ax,x0+150,290,label,22,ha='center')
    text(ax,403,530,'와',25,ha='center');text(ax,800,530,'→',32,ha='center')
    text(ax,600,805,'새 발자국이 찍혀도 먼저 남긴 발자국을 지우지 않습니다.',24,ha='center')
    save(fig,'snow_memory','S08','자체 축적 과정. 이전 기록의 발자국과 이번 접촉을 텍셀별 max 정책으로 합쳐 두 흔적을 남깁니다. 첫 번째 자국은 현재 접촉에서 사라졌지만 새 기록에는 계속 보존됩니다.')

def clip_polygon(poly,n,d):
    result=[]
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        sa=np.dot(n,a)-d;sb=np.dot(n,b)-d
        if sa<=0:result.append(a)
        if (sa<=0)!=(sb<=0):result.append(a+(b-a)*sa/(sa-sb))
    return np.array(result)

def liquid():
    fig,ax=canvas('병에 붙은 기준과 월드의 수평 기준은 다릅니다','주황: 같은 병의 자세 / 파랑: 선택한 기준면 아래의 영역')
    angle=math.radians(-28);R=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    local=np.array([[-40,-210],[40,-210],[40,-135],[100,-75],[100,200],[-100,200],[-100,-75],[-40,-135]])
    for x,world,label in [(320,False,'병 기준으로 자르기'),(880,True,'월드 수평으로 자르기')]:
        center=np.array([x,500]);poly=local@R.T+center;n=np.array([0.,-1.]) if world else R@np.array([0.,-1.]);d=np.dot(n,center)
        fill=clip_polygon(poly,n,d);ax.add_patch(Polygon(fill,fc='#8bc9e8',ec='none'))
        closed=np.vstack([poly,poly[0]]);ax.plot(closed[:,0],closed[:,1],color=GOLD,lw=4)
        tangent=np.array([-n[1],n[0]]);a=center-tangent*175;b=center+tangent*175
        ax.plot([a[0],b[0]],[a[1],b[1]],color=BLUE,lw=3,ls='--')
        text(ax,x,820,label,25,ha='center')
    save(fig,'liquid_spaces','S09','자체 병 단면을 두 기준면으로 자른 결과. 두 병의 자세는 같지만 왼쪽 기준면은 병과 함께 돌아가고 오른쪽은 월드 수평을 유지합니다. 채운 부피를 보존하는 유체 해석 모형은 아닙니다.')
    fig,ax=canvas('평면의 어느 쪽인지 내적의 부호로 구분합니다','같은 좌표계의 기준점 p₀, 위쪽 단위 법선 n, 검사점 p를 사용')
    y=540;ax.plot([90,1110],[y,y],color=BLUE,lw=4);text(ax,1050,590,'수면',23,BLUE)
    origin=np.array([380,y]);ax.add_patch(Circle(tuple(origin),9,fc=INK));text(ax,340,600,'p₀',27)
    arrow(ax,*origin,380,280,GREEN,4);text(ax,335,300,'n',28,GREEN)
    for p,label,col in [(np.array([850,330]),'s > 0 · 수면 위',RED),(np.array([850,760]),'s < 0 · 수면 아래',BLUE)]:
        arrow(ax,*origin,*p,MUTED,2);ax.add_patch(Circle(tuple(p),12,fc=col));text(ax,p[0],p[1]-55,label,23,col,ha='center')
    text(ax,600,880,'s = dot(n, p - p0) · 양수는 위쪽, 음수는 아래쪽',23,ha='center')
    save(fig,'liquid_plane','S09','자체 평면 부호 모형. 화살표 n은 수면 위쪽을 정하는 단위 법선이고, 회색 선은 기준점에서 각 검사점으로 향하는 벡터입니다. 양수인 위쪽을 버리고 음수인 아래쪽을 남기는 예입니다.')

if __name__=='__main__':
    rope();water();snow();liquid()
    (BASE/'figure-manifest-batch3.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
