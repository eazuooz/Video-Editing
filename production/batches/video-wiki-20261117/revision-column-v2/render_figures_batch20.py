from render_figures import *
import numpy as np

def rim():
    fig,ax=canvas('표면 방향 N과 카메라를 향한 V의 관계로 가장자리 읽기','자체 직교 시점 단면 · 평행한 V를 가정해 정면과 옆면을 비교')
    ax.add_patch(Circle((760,530),190,fc='#e1ebe2',ec=INK,lw=3));node(ax,80,455,180,120,'카메라',BLUE,size=25)
    ax.add_patch(Circle((570,530),10,fc=INK));arrow(ax,570,530,420,530,GREEN);arrow(ax,570,555,350,555,BLUE)
    text(ax,360,650,'정면 · N과 V가 같음\nN·V=1 → 림 0',24,ha='center')
    ax.add_patch(Circle((760,340),10,fc=INK));arrow(ax,760,340,760,210,GREEN);arrow(ax,760,340,590,340,BLUE)
    text(ax,970,280,'옆면\nN·V=0\n림 1',24,ha='center');text(ax,600,870,'초록 N · 표면 바깥 / 파랑 V · 카메라 방향',24,ha='center')
    save(fig,'rim_vectors','S70','자체 직교 시점의 구 단면. 평행한 뷰 벡터를 사용해 정면의 내적 1과 옆면의 내적 0을 비교합니다. 원근 카메라의 모든 지점에서 V가 같다는 뜻은 아닙니다.')
    fig,ax=canvas('지수를 키우면 중간 면보다 가장자리에 강조가 모입니다','자체 r=(1−clamp(N·V,0,1))^p · p=1과 p=4 비교')
    x=np.linspace(0,1,200);px=lambda u:170+870*u;py=lambda u:770-470*u
    ax.plot([170,1040],[770,770],color=INK,lw=2);ax.plot([170,170],[280,770],color=INK,lw=2);ax.plot(px(x),py(1-x),color=BLUE,lw=4);ax.plot(px(x),py((1-x)**4),color=GOLD,lw=4)
    text(ax,170,820,'0 · 옆면',23,ha='center');text(ax,1040,820,'1 · 정면',23,ha='center');text(ax,600,900,'가로 N·V / 세로 림 비중 r',24,ha='center');text(ax,880,410,'p=1',26,BLUE);text(ax,880,600,'p=4',26,GOLD);text(ax,110,300,'1',23);text(ax,110,770,'0',23)
    save(fig,'rim_curve','S70','자체 림 함수 비교. 내적이 0인 가장자리는 두 함수 모두 1이지만 중간 영역에서는 지수 4가 더 작습니다. 정확한 물리 프레넬 반사율 계산 그래프가 아닙니다.')

def bloom():
    fig,ax=canvas('원본·추출·퍼짐·합성은 다른 자료입니다','자체 회색 점 · 임계값 T=2, 합성 강도 k=1의 학습 예')
    rows=[('원본 C',[0,0,4,0,0],BLUE),('추출 B',[0,0,2,0,0],GOLD),('퍼짐 G',[0,.5,1,.5,0],GREEN),('합성 C+G',[0,.5,5,.5,0],BLUE)]
    for j,(label,vals,col) in enumerate(rows):
        y=260+j*175;text(ax,65,y+45,label,24,col)
        for i,v in enumerate(vals):
            x=380+i*140;ax.add_patch(Rectangle((x,y),130,95,fc='#e5eacb' if v else '#19352c',ec=col,lw=2));text(ax,x+65,y+48,str(v),25,INK if v else 'white',ha='center')
    save(fig,'bloom_stages','S71','자체 숫자 버퍼. 원본 중심 4에서 임계값 2를 뺀 2를 추출하고 1/4·1/2·1/4 필터로 0.5·1·0.5를 만듭니다. 강도 1로 더하면 중심 5, 이웃 0.5입니다. 색은 HDR 표시의 정확한 광도 재현이 아닙니다.')
    fig,ax=canvas('번짐의 폭과 원본 밝기는 따로 볼 수 있습니다','자체 같은 버퍼의 선 그래프 · 필터 입력과 퍼진 결과를 비교')
    px=lambda u:180+205*u;py=lambda u:780-220*u
    vals=[0,0,2,0,0];blur=[0,.5,1,.5,0]
    ax.plot([180,1000],[780,780],color=INK,lw=2);ax.plot(px(np.arange(5)),py(np.array(vals)),color=GOLD,lw=4,marker='o');ax.plot(px(np.arange(5)),py(np.array(blur)),color=GREEN,lw=4,marker='o')
    text(ax,800,300,'금색 · 추출한 밝기',24,GOLD,ha='center');text(ax,800,400,'초록 · 이웃으로 퍼진 값',24,GREEN,ha='center');text(ax,600,880,'중심 밝기가 주변 위치로 나뉨 / 아직 원본과 합치기 전',23,ha='center')
    for v in [0,1,2]:text(ax,120,py(v),str(v),22)
    save(fig,'bloom_profile','S71','자체 5픽셀 필터 추적. [0,0,2,0,0]에서 [0,0.5,1,0.5,0]으로 변합니다. 번짐 결과와 최종 합성 화면을 구별합니다.')

def ibl():
    fig,ax=canvas('환경을 방향으로 찾아 읽는 자료로 생각하기','자체 큐브맵 펼침 · 면 배치와 축은 실제 API에서 정한 규약을 따라야 함')
    faces=[(480,230,'+Y · 위',BLUE),(260,450,'−X',GREEN),(480,450,'+Z',GOLD),(700,450,'+X',BLUE),(920,450,'−Z',GREEN),(480,670,'−Y · 아래',GOLD)]
    for x,y,l,c in faces:node(ax,x,y,205,190,l,c,size=24)
    ax.add_patch(Rectangle((755,470),70,45,fc='#fff6ba',ec=GOLD,lw=2));text(ax,130,510,'환경의\n밝은 창',24,ha='center');text(ax,600,910,'배경 표시 색과 조명용 HDR 자료의 의미도 구별',23,ha='center')
    save(fig,'ibl_environment','S74','자체 방향 환경 자료. 여섯 면을 한눈에 보기 위한 펼침이며 면의 실제 저장 순서·축 규약을 대신하지 않습니다. 밝은 창은 환경의 방향별 빛을 생각하기 위한 자체 예입니다.')
    fig,ax=canvas('여러 방향에서 받는 빛과 시선에 보이는 반사를 구별하기','자체 단면 · 법선 N은 위쪽, 반사 방향은 표면에서 환경을 향함')
    for x in [300,900]:ax.plot([x-190,x+190],[650,650],color=INK,lw=3);ax.add_patch(Circle((x,650),9,fc=INK))
    for sx,sy in [(110,350),(490,350)]:arrow(ax,sx,sy,300,630,GOLD,3)
    arrow(ax,300,650,300,280,GREEN);text(ax,300,230,'N',26,GREEN,ha='center')
    arrow(ax,900,650,900,300,GREEN);arrow(ax,900,650,1080,380,BLUE);arrow(ax,900,650,720,380,GOLD)
    text(ax,300,770,'확산 · 반구 여러 방향을\n법선에 대한 기여로 더함',24,ha='center');text(ax,900,770,'반사 · N과 V로\n환경 조회 방향 R을 정함',24,ha='center');text(ax,900,250,'N',26,GREEN,ha='center');text(ax,1110,350,'V',26,BLUE);text(ax,680,350,'R',26,GOLD)
    save(fig,'ibl_diffuse_specular','S74','자체 입력·반사 방향 구분. 왼쪽은 여러 입사 방향을 합하는 생각, 오른쪽은 법선·뷰 벡터에 따른 거울 반사 조회 방향입니다. 실제 환경 적분이나 재질의 모든 BRDF를 재현한 그림은 아닙니다.')

def skin():
    fig,ax=canvas('같은 정점도 뼈마다 다른 비중으로 연결될 수 있습니다','자체 두 뼈 가중치 · 각 막대는 한 정점의 합계 1인 영향 비율')
    for i,w0 in enumerate([1,.75,.5,.25,0]):
        x=140+i*205;h=360
        ax.add_patch(Rectangle((x,350),110,h*w0,fc=BLUE));ax.add_patch(Rectangle((x,350+h*w0),110,h*(1-w0),fc=GREEN));text(ax,x+55,790,f'정점 {i+1}\n{w0} / {1-w0}',22,ha='center')
    text(ax,600,260,'파랑 · 뼈 0 / 초록 · 뼈 1',25,ha='center');text(ax,600,900,'가중치와 기준 자세의 변환을 함께 사용해 표면 위치 계산',23,ha='center')
    save(fig,'skinning_weights','S75','자체 정점별 가중치. 각 정점의 두 영향이 1로 합쳐집니다. 막대는 가중치 자료이며 실제 팔의 변형 결과나 수업 캐릭터의 가중치를 측정한 그림은 아닙니다.')
    fig,ax=canvas('표면을 움직이는 자료와 환경을 읽는 자료는 다릅니다','자체 자료 흐름 · 움직임 처리 뒤의 위치·법선으로 색 계산에 연결')
    node(ax,65,250,430,145,'뼈 변환 + 정점 가중치\n표면 위치·방향 변화',BLUE,size=24);node(ax,705,250,430,145,'법선 N + 뷰 V\n반사 방향 R 계산',GREEN,size=24);node(ax,705,650,430,145,'방향 R로 큐브맵 조회\n재질 반응에 반영',GOLD,size=24)
    arrow(ax,510,322,690,322,BLUE);arrow(ax,920,410,920,630,GREEN);text(ax,300,665,'가려짐·변형 오류와\n환경 조회 오류를\n따로 검사',25,ha='center')
    save(fig,'skinning_environment','S75','자체 역할 연결도. 스키닝은 표면 자료를 바꾸고 환경 반사는 방향으로 환경 자료를 읽습니다. 같은 최종 화면에 들어가도 서로 다른 입력과 실패 원인을 가집니다.')

if __name__=='__main__':
    rim();bloom();ibl();skin()
    (BASE/'figure-manifest-batch20.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
