from render_figures import *
import numpy as np

def person(ax,x,y,color=BLUE):
    ax.add_patch(Circle((x,y-80),22,fc=color));ax.plot([x,x],[y-55,y+15],color=color,lw=11)
    for dx in [-25,25]:ax.plot([x,x+dx],[y+10,y+55],color=color,lw=9)

def first():
    fig,ax=canvas('첫 행동과 그 결과가 같은 장면에서 연결되게','같은 방: 상자를 밀어 발판을 누르면 문이 열리는 자체 퍼즐')
    for j,(crate_x,player_x,opened,label) in enumerate([(330,210,False,'행동 전'),(650,530,True,'행동 후')]):
        y=390+j*365;text(ax,65,y-170,label,27)
        ax.plot([70,1130],[y+58,y+58],color=INK,lw=4)
        ax.add_patch(Rectangle((600,y+40),130,18,fc=GOLD))
        ax.add_patch(Rectangle((crate_x-45,y-40),90,90,fc='#e8c482',ec=INK,lw=3));person(ax,player_x,y)
        ax.plot([1000,1000],[y-125,y+58],color=INK,lw=5)
        if opened:ax.plot([1000,1110],[y-125,y-55],color=GREEN,lw=7)
        else:ax.add_patch(Rectangle((945,y-125),55,183,fc=INK))
        text(ax,985,y-170,'열린 문' if opened else '닫힌 문',23,GREEN if opened else INK,ha='center')
        text(ax,665,y+110,'발판',22,GOLD,ha='center')
        if j==0:arrow(ax,400,y-60,580,y-60,BLUE,4);text(ax,490,y-110,'밀기',24,BLUE,ha='center')
        else:arrow(ax,750,y+5,920,y-60,GREEN,3)
    save(fig,'first_action','D02','자체 퍼즐의 전후 상태. 상자·발판·문을 한 장면에서 보여 주며 상자를 밀어 위치를 바꾼 결과로 문 상태가 달라집니다. 특정 상용 게임의 레벨이나 실측 데이터가 아닙니다.')
    fig,ax=canvas('안내를 따라 한 번 하기와 스스로 다시 쓰기는 다릅니다','같은 행동을 다른 배치에서 사용할 수 있는지 관찰하는 자체 설계')
    for x0,label,detail in [(70,'첫 방','상자 하나로 관계 경험'),(675,'다음 방','두 상자에서 필요한 것 선택')]:
        text(ax,x0+225,240,label,28,ha='center');node(ax,x0,300,450,300,'',size=24)
        ax.add_patch(Rectangle((x0+160,430),70,70,fc='#e8c482',ec=INK,lw=3))
        if x0>100:ax.add_patch(Rectangle((x0+290,430),70,70,fc='#e8c482',ec=INK,lw=3))
        ax.add_patch(Rectangle((x0+160,540),100,15,fc=GOLD));text(ax,x0+225,660,detail,21,ha='center')
    arrow(ax,540,450,650,450,GREEN,4)
    text(ax,600,790,'입력은 아는데 장치를 못 읽는가?\n장치는 아는데 다음 길을 못 찾는가?',25,ha='center')
    save(fig,'first_learning','D02','자체 학습 관찰 모형. 처음 방에서 관계를 경험한 뒤 같은 조작을 다른 배치에서 스스로 쓰는지 봅니다. 안내 통과와 이해를 같은 것으로 간주하지 않고 실패한 관계를 나누어 관찰합니다.')

def input_figures():
    fig,ax=canvas('하나의 누름에는 사건 두 개와 유지 상태가 있습니다','새로 누름 / 누르는 중 / 놓음의 역할을 나눈 자체 신호도')
    xs=[100,340,340,850,850,1100];ys=[570,570,330,330,570,570]
    ax.plot(xs,ys,color=BLUE,lw=5)
    ax.add_patch(Rectangle((340,330),510,240,fc='#c8e4ed',alpha=.4))
    text(ax,595,430,'누른 상태 유지',29,BLUE,ha='center')
    arrow(ax,340,760,340,595,GREEN,4);text(ax,340,810,'누름 사건',25,GREEN,ha='center')
    arrow(ax,850,760,850,595,GOLD,4);text(ax,850,810,'뗌 사건',25,GOLD,ha='center')
    text(ax,100,280,'눌림',23);text(ax,100,630,'놓임',23);arrow(ax,100,890,1100,890,INK,2);text(ax,1100,920,'시간',19,ha='right')
    save(fig,'input_signal','D06','자체 입력 신호도. 파란 띠는 버튼을 누른 상태가 유지된 구간이고, 시작과 끝에는 서로 다른 사건이 한 번씩 발생합니다. 길게 누른 매 프레임을 새로운 누름으로 세지 않습니다.')
    fig,ax=canvas('예측해 맞추는 순간과 신호 뒤 반응은 다릅니다','같은 버튼이어도 주어진 정보와 허용되는 시점이 달라집니다')
    for y,label in [(350,'타이밍: 다가오는 순간을 예측'),(690,'반응: 신호가 나온 뒤에 누름')]:
        text(ax,65,y-110,label,25);arrow(ax,100,y,1100,y,INK,2)
    ax.add_patch(Rectangle((770,315),140,70,fc='#a8d8bd',ec=GREEN,lw=2));text(ax,840,445,'성공 구간',23,GREEN,ha='center')
    arrow(ax,470,270,470,320,BLUE,3);text(ax,300,285,'다가오는 대상',21,BLUE,ha='center')
    ax.add_patch(Rectangle((570,655),500,70,fc='#a8d8bd',ec=GREEN,lw=2));ax.plot([570,570],[610,760],color=GOLD,lw=4)
    text(ax,570,825,'신호 출현',23,GOLD,ha='center');text(ax,920,825,'신호 후 입력 허용',22,GREEN,ha='center')
    save(fig,'input_window','D06','자체 입력 판정 시간표. 위는 목표 구간을 미리 읽어 맞추는 모형, 아래는 신호가 나온 뒤 입력을 허용하는 모형입니다. 두 시간표의 위치와 폭은 설명용이며 특정 게임의 반응 시간 측정값이 아닙니다.')

def feedback():
    fig,ax=canvas('문은 둘 다 잠겼지만 알 수 있는 정보가 다릅니다','상태는 같게 두고 수신·거절 이유를 알려 주는 방식만 비교')
    for x0,label,notice in [(90,'응답 없음','왜 안 되지?'),(680,'응답 있음','열쇠가 필요합니다')]:
        ax.add_patch(Rectangle((x0+115,300),220,390,fc='#d7bf98',ec=INK,lw=4))
        ax.add_patch(Circle((x0+285,505),11,fc=INK));ax.add_patch(Circle((x0+225,425),14,fc=INK));ax.add_patch(Rectangle((x0+218,425),14,24,fc=INK))
        text(ax,x0+225,225,label,28,ha='center');text(ax,x0+225,780,notice,25,ha='center',color=GREEN if x0>100 else MUTED)
    text(ax,600,890,'입력 수신과 행동 성공을 같은 표시로 뭉개지 않습니다.',23,ha='center')
    save(fig,'feedback_door','D12','자체 잠긴 문 비교. 두 문 모두 열리지 않았습니다. 오른쪽은 입력을 알아보고 거절 이유를 전달해 플레이어가 다음 행동을 고를 수 있게 합니다. 성공과 실패를 바꾼 비교가 아닙니다.')
    fig,ax=canvas('저장 완료는 시간표가 아니라 실제 결과로 결정합니다','자체 상태 모형: 수신 → 처리 중 → 결과에 맞는 표시')
    node(ax,70,240,320,110,'요청 수신',size=26);arrow(ax,400,295,575,295)
    node(ax,590,240,450,110,'처리 중\n중복 시작 방지',size=24)
    arrow(ax,815,365,400,590,GREEN);arrow(ax,815,365,960,590,RED)
    node(ax,150,600,400,125,'성공 확인\n완료 표시',GREEN,size=25)
    node(ax,720,600,400,125,'실패 확인\n이유 · 재시도',RED,'#fff0ec',size=25)
    text(ax,605,830,'애니메이션 종료 ≠ 파일 저장 성공',27,ha='center')
    save(fig,'feedback_states','D12','자체 비동기 작업 상태도. 처리 중에는 같은 작업을 반복 시작하지 않으며, 실제 성공 또는 실패 결과를 받아 표시를 바꿉니다. 몇 초 기다렸다는 이유만으로 성공 처리하지 않습니다.')

def color_figures():
    fig,ax=canvas('색 하나가 사라져도 같은 의미를 확인할 수 있게','이 그림은 색각 시뮬레이션이 아니라 정보 채널을 비교한 자체 모형')
    for y,label,colors,shapes in [(300,'색만 다른 두 종류',[RED,GREEN],False),(545,'색의 구별을 일부러 없앰',[MUTED,MUTED],False),(790,'모양·문구도 함께 사용',[MUTED,MUTED],True)]:
        text(ax,65,y-65,label,24)
        for j,(x,c) in enumerate(zip([470,890],colors)):
            if shapes and j:ax.add_patch(Polygon([(x,y-48),(x-52,y+45),(x+52,y+45)],fc=c))
            else:ax.add_patch(Circle((x,y),50,fc=c))
            if shapes:text(ax,x,y+87,'A종 · 원' if j==0 else 'B종 · 삼각형',22,ha='center')
    save(fig,'color_channels','D25','자체 정보 채널 비교. 두 종류를 같은 회색으로 일부러 바꾸면 색만 쓰던 구분은 사라지지만 원·삼각형·이름을 추가한 구분은 남습니다. 실제 흑백 변환이나 특정 색각 조건을 정확히 재현한 그림은 아닙니다.')
    fig,ax=canvas('종류의 차이와 배경에서의 경계는 다른 질문입니다','물체·배경·위치를 유지하고 테두리만 바꾼 자체 비교')
    for x0,outlined,label in [(70,False,'비슷한 배경에 묻힌 윤곽'),(660,True,'같은 윤곽에 경계 보강')]:
        ax.add_patch(Rectangle((x0,300),450,400,fc='#234832'))
        for x,y in [(40,70),(300,25),(130,275)]:ax.add_patch(Rectangle((x0+x,300+y),110,90,fc='#284c39'))
        ax.add_patch(Circle((x0+225,500),72,fc='#28533b',ec='#f4ead1' if outlined else '#28533b',lw=6 if outlined else 0))
        text(ax,x0+225,795,label,22,ha='center')
    text(ax,600,890,'모든 물체에 같은 강조를 주면 우선순위는 다시 흐려질 수 있습니다.',22,ha='center')
    save(fig,'color_boundary','D25','자체 물체-배경 경계 비교. 두 화면은 같은 배경과 물체 색을 쓰며 오른쪽에만 테두리를 추가했습니다. 색상만 바꾸는 해결책과 경계를 보강하는 해결책을 나누어 봅니다.')

if __name__=='__main__':
    first();input_figures();feedback();color_figures()
    (BASE/'figure-manifest-batch4.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Rendered',len(manifest),'new figures')
