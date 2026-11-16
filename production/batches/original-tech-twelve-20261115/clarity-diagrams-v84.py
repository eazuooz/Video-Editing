"""Beginner comparisons: the displayed shapes use the same labelled inputs.

All diagrams are authored teaching models, never original engine telemetry.
"""
from pathlib import Path
import functools,importlib.util,math
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('prior_clarity_diagrams',H/'tech-diagrams-v5.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
base,lines,arrow,C=old.base,old.lines,old.arrow,old.C
g=base.__globals__;g['font']=functools.lru_cache(maxsize=80)(g['font'])
dot=g['dot']

def sand_mirrors(t):
 im,d=base('작은 면의 방향을 비교합니다','Normal & View (면의 방향과 시선) · 해설용 모형')
 view=math.sin(t*.35)*.8
 for i,a in enumerate([-.8,-.4,0,.4,.8]):
  x=130+i*180;y=540;brightness=max(0,math.cos(a-view))**20
  color=tuple(int(80+175*brightness)for _ in range(3));dx,dy=math.cos(a)*64,math.sin(a)*64
  d.line((x-dx,y-dy,x+dx,y+dy),fill=color,width=15)
  n=(-math.sin(a),-math.cos(a));arrow(d,(x,y),(x+n[0]*110,y+n[1]*110),C['relation'],5)
  lines(d,'밝음'if brightness>.3 else'어두움',(x,655),29,'title'if brightness>.3 else'muted')
 eye=(492+math.sin(view)*280,265);dot(d,eye,'changed',23);lines(d,'카메라',(eye[0],215),32,'changed')
 for i in range(5):d.line((130+i*180,540,*eye),fill='#614b36',width=2)
 lines(d,'작은 면은 그대로 · 시선만 이동',(492,780),38,'relation')
 lines(d,'밝기 예시는 N·V 기반의 시선 비교',(492,880),30,'muted')
 return im,dict(kind='authored surface-view comparison',viewAngle=view,normalAndViewShareCoordinates=True,originalJourneyBuffers=False)

def temporal_pixels(t):
 im,d=base('작은 칸에서 가는 선을 찾습니다','Pixel / Frame / Jitter (픽셀·프레임·지터)')
 phase=int(t*2)%4;shift=[(.2,.2),(.8,.2),(.2,.8),(.8,.8)][phase];result=[]
 for panel,x0 in enumerate([85,555]):
  lines(d,'한 위치만 검사'if panel==0 else'다른 위치도 모으기',(x0+170,255),33,'title')
  for y in range(10):
   for x in range(10):
    samples=[shift]if panel==0 else[(.2,.2),(.8,.2),(.2,.8),(.8,.8)]
    coverage=sum(abs((x+a)-(y+b)*.65-1.2)<.3 for a,b in samples)/len(samples)
    v=int(35+200*coverage);rect=(x0+x*34,325+y*34,x0+x*34+32,325+y*34+32);d.rectangle(rect,fill=(v,v,v),outline='#345050')
    if panel==0:d.ellipse((rect[0]+shift[0]*30-2,rect[1]+shift[1]*30-2,rect[0]+shift[0]*30+2,rect[1]+shift[1]*30+2),fill=C['changed'])
    result.append(coverage)
 lines(d,'색 칸 하나 = 픽셀',(492,745),38,'relation')
 lines(d,'주황 점 = 이번에 검사하는 위치',(492,825),34,'changed')
 lines(d,'선은 그대로 · 검사 위치만 바꾼 해설 모형',(492,930),29,'muted')
 return im,dict(kind='authored analytic thin-line sampling',phase=phase,samplePosition=shift,coverageSum=sum(result),notOriginalInsideBuffers=True)

def control_pieces(t):
 im,d=base('큰 조각과 작은 효과를 함께 봅니다','Fracture / Bonds / Debris (조각·연결·파편)')
 phase=min(1,max(0,(t-1.5)/3));pieces=[]
 for i in range(5):
  x=115+i*170;y=420
  if i in[2,3]:x+=phase*(i-1)*45;y+=phase*phase*270
  d.polygon([(x,y),(x+145,y+15),(x+140,y+85),(x-5,y+70)],fill='#99794c',outline=C['title'],width=4);pieces.append([x,y])
  if i<4 and (not phase or i not in[1,2,3]):d.line((x+145,y+38,x+170,y+38),fill=C['relation'],width=9)
 for i in range(32):
  a=i*2.4;x=492+math.cos(a)*phase*(75+i*3);y=485+phase*math.sin(a)*110+phase*phase*150
  r=3+i%4;d.ellipse((x-r,y-r,x+r,y+r),fill='#a99c87')
 arrow(d,(492,280),(492,390),C['changed'],9);lines(d,'같은 충격',(492,240),35,'changed')
 lines(d,'큰 조각 → 윤곽 변화',(492,800),36,'title');lines(d,'작은 파편·먼지 → 충격 위치',(492,872),34,'relation')
 return im,dict(kind='authored prepared-fragment and particle illustration',phase=phase,pieces=pieces,notOriginalPhysics=True)

def returnal_chain(t):
 im,d=base('앞의 이전 움직임을 뒤가 읽습니다','Previous-frame Parent Data (이전 프레임의 부모 정보)')
 frame=int(t*60);nodes=[]
 for i in range(22):
  q=(frame-i)/60;x=110+i*36;y=500+math.sin(q*4)*95;nodes.append((x,y))
 d.line(nodes,fill='#365e61',width=38)
 for i,p in enumerate(nodes):
  dot(d,p,'changed'if i==0 else'relation',13)
  if i in[0,6,12,21]:lines(d,'부모'if i==0 else'자식', (p[0],p[1]+70),27,'changed'if i==0 else'ink')
 lines(d,'각 점은 앞 점의 한 프레임 전 위치를 참조',(492,735),34,'relation')
 lines(d,'점들의 관계 → 부드럽게 휘는 줄',(492,830),37,'title')
 lines(d,'60Hz 해설용 규칙 예 · 원래 게임의 입자 값 아님',(492,930),27,'muted')
 return im,dict(kind='authored exact one-frame dependency chain',frame=frame,points=nodes,rule='child[i,t] = parent[i-1,t-1] + (36,0)',artisticModelNotReturnalSimulation=True)

def botw_motion_state(t):
 im,d=base('움직임과 상태 변화는 다릅니다','Physics / Chemistry (물리 / 화학)')
 x=160+min(1,t/5)*190
 d.rectangle((x,355,x+115,470),fill='#99794c',outline=C['title'],width=5)
 arrow(d,(90,410),(x-15,410),C['relation'],7);lines(d,'밀면 위치가 바뀜',(305,570),34,'relation')
 on=t>2;d.rectangle((655,355,770,470),fill='#99794c',outline=C['title'],width=5)
 if on:
  for i in range(6):
   xx=662+i*18;dy=30+25*math.sin(t*7+i);d.polygon([(xx,400),(xx+10,280-dy),(xx+22,410)],fill='#f39a4b')
 lines(d,'불이 닿으면 불붙음',(710,570),34,'changed')
 lines(d,'물리: 위치·속도',(275,740),37,'relation');lines(d,'화학: 상태의 관계',(725,740),37,'changed')
 lines(d,'같은 상자를 서로 다른 규칙으로 설명한 모형',(492,920),29,'muted')
 return im,dict(kind='authored motion-state comparison',boxPosition=x,woodState='burning'if on else'not-burning',noOriginalChemistryEngineExecuted=True)

def spider_anchors(t):
 im,d=base('위쪽 끝을 바꾸면 곡선도 바뀝니다','Attachment Point (거미줄 부착점) · 비교 모형')
 theta=.8*math.sin(t*.8);pts=[]
 for i,(x,y,length)in enumerate([(265,300,300),(730,410,300)]):
  point=(x+length*math.sin(theta),y+length*math.cos(theta));d.rectangle((x-40,y-45,x+40,y),fill='#415656');dot(d,(x,y),'title',15);d.line((x,y,*point),fill=C['ink'],width=6);dot(d,point,'changed',24);pts.append(point)
  lines(d,'높은 부착점'if i==0 else'낮은 부착점',(x,220),34,'title')
 d.line((70,825,914,825),fill=C['relation'],width=7);lines(d,'같은 줄 길이 · 같은 각도 · 부착점 높이만 변경',(492,920),29,'muted')
 return im,dict(kind='authored same-angle same-length anchor comparison',angle=theta,positions=pts,gameAnchorMeasured=False)

EXTRA={'sand-mirrors-easy':sand_mirrors,'temporal-pixels-easy':temporal_pixels,'control-pieces-easy':control_pieces,'returnal-chain-easy':returnal_chain,'botw-motion-state-easy':botw_motion_state,'spider-anchors-easy':spider_anchors}
DIAGRAMS=dict(old.DIAGRAMS,**EXTRA)
def render(key,t):
 im,e=DIAGRAMS[key](t);return im,dict(**e,diagramKey=key,localModelSeconds=t,notSpeechTimestamp=True,finalFilm=False)
