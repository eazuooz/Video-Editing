"""Baseline-referenced recovery of the missing 18 polygon explanation scenes.

Original text/audio/cue times stay in the existing project files. White palette,
objects and worked examples are retained. The overly foreshortened supplementary
diagram is drawn in its logical XY plane to make distances and the notch legible.
Numeric scenes still execute the original geometry_polygons.py program.
"""
import os,sys,json
from pathlib import Path
import numpy as np
from manim import *
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
from lesson import txt,fit,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD,PALE
import geometry_polygons as original
# Direct native-frame inspection found the original header rule striking through
# its subtitle. Shift only that precise rule; original geometry/math stays intact.
_original_line=original.Line
def _header_safe_line(start,end,*args,**kwargs):
 if np.allclose(start,[-6.5,2.63,0]) and np.allclose(end,[6.5,2.63,0]):
  start=[-6.5,2.35,0];end=[6.5,2.35,0]
 return _original_line(start,end,*args,**kwargs)
original.Line=_header_safe_line
SLUG=os.environ['POLISH_SLUG']
T=json.loads((R/'projects'/SLUG/'production/timeline.json').read_text(encoding='utf8'))
LSS=json.loads((R/'projects'/SLUG/'production/lesson.json').read_text(encoding='utf8'))
TRI=original.TRI;L=original.L;EARS=original.EARS
C=np.array([-5.65,-1.45,0.]);S=.80
def p(v):return C+S*np.r_[np.array(v)[:2],0.]
def label(value,where,color=INK,size=25):return txt(value,size,color).move_to(where)
def face(v,color=BLUE,opacity=.13):
 return Polygon(*[p(x) for x in v],stroke_color=color,stroke_width=3.5,fill_color=color,fill_opacity=opacity)
def seg(a,b,color=GREEN,dash=False,width=5):
 return (DashedLine if dash else Line)(p(a),p(b),color=color,stroke_width=width)
def point(q,name='',color=GOLD,offset=UR):
 dot=Dot(p(q),radius=.065,color=color)
 return VGroup(dot,txt(name,25,color).next_to(dot,offset,buff=.09)) if name else dot
def boundary(v=L,names=True):
 base=VGroup(face(v))
 if names:
  for i,q in enumerate(v):
   direction=DOWN if q[1]==0 else UP if q[1]>=3 else RIGHT
   base.add(point(q,('ABC'[i] if len(v)==3 else str(i)),BLUE,direction))
 return base
def pieces():return VGroup(*[face(L[list(k)],c,.25) for k,c in zip(EARS,[GREEN,BLUE,GOLD,RED])])
def square():return boundary(np.array([[.6,.7],[3.4,.7],[3.4,3.5],[.6,3.5]]),False)
def center():return point([2,2.1],'',GOLD)
def textblock(value,x,y,color=GOLD,size=29,width=6.5):
 return fit(VGroup(*[txt(v,size,color) for v in value.split('\n')]).arrange(DOWN,aligned_edge=LEFT,buff=.16),width).move_to([x,y,0])

# Every state is keyed to an existing aligned sentence, never to a new voice.
# (sentence index, main panel, supporting panel, state key)
STATES={
 'QF01':[(0,'앞 편: p = .2A + .3B + .5C','삼각형 안의 주소','address'),(1,'남은 질문\n어떤 목적의 기준점인가?','찾은 위치 → 기준점 선택','address'),(2,'좌표를 평균할까?\n변·꼭짓점까지 거리를 같게 할까?','중심의 목적 → 경계 → 삼각형 분할','address')],
 'QF04':[(0,'다각형 전체 장\n두 편으로 이어 보기','','scope'),(1,'이번 편\n중심 선택 → 경계 검사','','scope-center'),(2,'다음 편\n유효한 경계 → 삼각형 분할','','scope-split')],
 'QB01':[(0,'세 점을 같은 비중으로','같은 비율 → 좌표 평균','mean'),(1,'p = ⅓A + ⅓B + ⅓C\nG = (4/3, 1)','A(0,0), B(4,0), C(0,3)','mean'),(2,'균일한 삼각형 판\n균형 위치와 연결','밀도가 일정하다는 조건','mean'),(3,'좌표 평균만 넣었음\n거리 조건은 아직 별개','평균 ≠ 변·꼭짓점까지 같은 거리','mean')],
 'QB02':[(0,'점에서 두 변으로\n수직선을 내려 거리 비교','수직 거리 · 꼭짓점 거리와 구분','perpendicular'),(1,'공통 빗변 + 같은 반각\n합동 → 수직 거리 같음','두 직각삼각형을 비교','bisector'),(2,'같은 점과 세 꼭짓점 연결','내심의 좌표는 다음 장면에서 계산','in-pieces'),(3,'세 부분의 높이 = r\n부분 넓이 = 반대편 변 × r / 2','같은 높이 → 넓이는 밑변에 비례','in-radii'),(4,'넓이 비율 = (5, 3, 4) / 12','앞 편의 넓이 가중치 → 변 길이 가중치','in-radii')],
 'QB03':[(0,'앞: 세 변까지 수직 거리 같음','변까지 거리 → 꼭짓점까지 거리','perpendicular'),(1,'이번: 세 꼭짓점까지 거리 같음','같은 삼각형 · 다른 질문','triangle'),(2,'중점의 양옆 길이 같음\n공통 높이 → 두 빗변 길이 같음','수직이등분선: 중점에서 직각','perp-bisector'),(3,'수직이등분선','이어서 두 수직이등분선의 교점을 계산','perp-bisector')],
 'QB04':[(0,'중심 한 점\n전체 모양은 아직 알 수 없음','남길 땅과 빈 공간을 경계로 구분','l-center'),(1,'0 → 1 → 2 → 3 → 4 → 5 → 0\n끝에서 처음으로 닫기','오른쪽 위 빈 영역은 제외','l-trace'),(2,'중심 선택의 결과 → 경계 보존','입력부터 차례대로 검증','l-trace')],
 'QB11':[(0,'도르프로만틱 · 타이니 글레이드\n배치할 위치와 전체 외곽','','scope-center'),(1,'시리어스 샘: 대상을 찾는 표시\n노이타: 땅과 빈 공간의 경계','','scope-center'),(2,'한 점 ≠ 전체 외곽','같은 기준점 · 서로 다른 모양','different'),(3,'가운데 점이 같아도\n모양은 서로 다름','한 점 ≠ 전체 외곽','different'),(4,'먼저 목적을 정함\n좌표 평균? 변까지 같은 거리?','','different'),(5,'관찰 사례와 공식\n내부 구현 주장은 구분','설명용 도형 · 게임 실측값 아님','different')],
 'QB05':[(0,'안의 두 점을 이은 선\n빈 부분을 지남 → 오목','같은 사실을 경계의 회전으로 계산','notch-cross'),(1,'경계를 돌며 회전 방향 비교','수학 좌표: x 오른쪽 · y 위쪽','l'),(2,'u = v₃ − v₂ = (−3, 0)\nv = v₄ − v₃ = (0, 3)','반시계 경계의 홈 · 다른 꼭짓점과 반대 회전','turn'),(3,'uₓvᵧ − uᵧvₓ\n(−3) × 3 − 0 × 0 = −9','부호는 방향 · 크기는 넓이 단위','turn')],
 'QF02':[(0,'중심의 목적을 구분\n유효한 경계·홈 확인','경계는 바깥을 정함','l'),(1,'안쪽 분할은 다음 문제','검사한 같은 경계와 홈을 유지','l'),(2,'다음 편\n빈 영역을 지키며 삼각형으로 나누기','다음 편에서도 같은 입력 유지','l')],
 'QF03':[(0,'앞 편: 중심의 목적 · 경계의 순서','같은 여섯 꼭짓점과 홈','l'),(1,'이번 질문\n땅을 겹침 없는 삼각형으로 나누기','','l'),(2,'① 볼록한 부채꼴과 실패\n② 귀를 하나씩 제거','같은 L자 · 점 번호 유지','l'),(3,'③ 영역·빈 공간·품질 검사','입력부터 결과까지 확인','l')],
 'QB06':[(0,'4조각이어도\n홈을 덮거나 겹칠 수 있음','같은 개수 ≠ 올바른 영역','wrong-fan'),(1,'부호 있는 넓이 합\n−4.5 + 1.5 + 8 + 2 = 7','합계가 같아도 위치는 다름','wrong-fan'),(2,'합계는 위치를 알려주지 않음\n원래 빈 홈은 계속 잘못 덮임','장부는 합계의 비유 · 공간 조건은 별도','wrong-fan')],
 'QB07':[(0,'전부 연결한 부채꼴은 실패\n작은 후보 하나부터 검사','같은 L자에서 방법 변경','l'),(1,'세 이웃 점 (0, 1, 2)\n가운데 1이 볼록 후보','아직 유효성을 모두 확인한 것은 아님','first-ear'),(2,'내부 대각선 검사\n다른 남은 꼭짓점 검사','볼록한 모서리만으로는 부족','first-ear-test'),(3,'모든 유효성 조건 통과 → 귀 저장','이어서 넓이 2인 귀 제거 · 원본 번호 보존','first-ear-test')],
 'QB08':[(0,'저장된 출력: (0, 1, 2)\n남은 경계는 별도로 유지','원본 점 번호는 그대로','first-ear'),(1,'이웃 갱신\n0 → 2 → 3 → 4 → 5 → 0','지운 것은 활성 연결 · 원본 번호 유지','next-link'),(2,'새 이웃으로 다음 귀 검사\n(0, 2, 3)','이어서 넓이 1.5 → 1.5 → 2','second-ear')],
 'QB12':[(0,'공장 게임의 목표\n도형 가공 → 목표 도형 납품','','scope'),(1,'벨트는 운반 경로','입력 도형 → 기계 → 출력 조각','cut-square'),(2,'기계에 들어가는 도형과\n밖으로 나오는 조각을 비교','설명용 도형 · 게임 내부 구현 아님','cut-square')],
 'QB14':[(0,'빈 공간 보존 → 순서 있는 연결','','l'),(1,'이동 경로와 영역의 외곽\n역할은 서로 다름','벨트는 이동 경로 · 다각형 경계가 아님','l'),(2,'연결됐어도\n홈을 가로질렀는지 검사','점의 순서 + 영역의 올바름','notch-cross')],
 'QB13':[(0,'셰이프즈 투: 목표 조각 만들기','','cut-square'),(1,'버리는 작업도 있음\n가공의 목적을 먼저 확인','','discard-square'),(2,'삼각형 분할\n모든 조각의 합집합 = 원래 영역','','pieces'),(3,'문 · 통로 · 땅의 홈\n빈 공간을 새로 채우지 않음','','pieces-notch'),(4,'게임이 달라도\n남길 영역과 빈 공간부터 확인','','pieces-notch'),(5,'모양과 조각은 설명용 예제','게임 내부 구현이나 실측값을 뜻하지 않음','pieces-notch')],
 'QB09':[(0,'먼저 영역을 올바르게 덮음\n그 뒤 조각 품질 개선','통로와 원래 경계 보존','pieces'),(1,'좌표 ×2 → 밑변 ×2 · 높이 ×2\n넓이 ×4','같은 형상 · 길이 단위와 넓이 단위²','scale'),(2,'길이 오차와 넓이 오차\n같은 기준을 쓰면 안 됨','ε_length와 ε_area · 서로 다른 단위','scale'),(3,'예시 h = .01, Δh = .001\n높이·넓이 변화 10%','가느다란 조각: 같은 오차의 영향 큼','thin'),(4,'유효한 후보 안에서 개선','통로와 원래 경계는 보존','thin')],
 'QB10':[(0,'균일한 판의 중심\n삼각형별 넓이로 가중 평균','분할한 조각의 역할 · 위치·속성 계산','centroids'),(1,'G = (2G₁ + 1.5G₂ + 1.5G₃ + 2G₄) / 7','넓이 가중 중심 = (19/14, 19/14)','weighted-centroid'),(2,'같은 조건·같은 경계·같은 조각\n마지막 두 문제로 확인','꼭짓점 평균 (5/3, 5/3)과 다름','weighted-centroid')],
}

def diagram(state):
 """Named layers make unchanged objects persistent across narration cues."""
 d={}
 if state in ['address','mean','perpendicular','bisector','in-pieces','in-radii','triangle','perp-bisector']:
  d['triangle']=boundary(TRI)
  if state=='address':d['point']=point(.2*TRI[0]+.3*TRI[1]+.5*TRI[2],'p')
  if state=='mean':
   g=TRI.mean(axis=0);d['point']=point(g,'G',GREEN);d['medians']=VGroup(*[seg(TRI[i],(TRI[(i+1)%3]+TRI[(i+2)%3])/2,GREEN,True,3) for i in range(3)])
  if state in ['perpendicular','bisector','in-pieces','in-radii']:
   q=np.array([1.,1.]);d['point']=point(q,'',GOLD)
   d['heights']=VGroup(seg(q,[1,0],GREEN),seg(q,[0,1],GREEN))
   d['right-angles']=VGroup(seg([1,.17],[.83,.17],GREEN,False,2),seg([.83,.17],[.83,0],GREEN,False,2),seg([.17,1],[.17,.83],GREEN,False,2),seg([.17,.83],[0,.83],GREEN,False,2))
   if state in ['bisector','in-pieces','in-radii']:d['bisector']=seg(TRI[0],q,GOLD)
   if state in ['in-pieces','in-radii']:
    d['triangle-parts']=VGroup(*[face([q,TRI[i],TRI[(i+1)%3]],col,.16) for i,col in enumerate([RED,GREEN,BLUE])])
    d['rays']=VGroup(*[seg(q,v,GOLD,False,3) for v in TRI])
   if state=='in-radii':
    d['third-height']=seg(q,[1.6,1.8],GREEN);d['r-labels']=VGroup(label('r',p([1.18,.4]),GREEN),label('r',p([.35,1.2]),GREEN),label('r',p([1.65,1.4]),GREEN))
  if state=='perp-bisector':
   mid=np.array([2.,0.]);q=np.array([2.,1.5]);d['bisector']=seg([2,-.4],[2,2.6],RED);d['equal-lengths']=VGroup(seg(TRI[0],q,BLUE),seg(TRI[1],q,BLUE));d['mid']=point(mid,'중점',RED,DOWN);d['point']=point(q,'',GOLD)
   d['half-labels']=VGroup(label('2',p([1,-.38]),RED),label('2',p([3,-.38]),RED));d['right-angle']=VGroup(seg([2.17,0],[2.17,.17],RED,False,2),seg([2.17,.17],[2,.17],RED,False,2))
 elif state in ['scope','scope-center','scope-split','different','cut-square','discard-square']:
  d['square']=square()
  if state in ['scope-center','different']:d['center']=center()
  if state=='scope-split':d['diagonal']=seg([.6,.7],[3.4,3.5],GREEN)
  if state=='different':
   d['square']=boundary(np.array([[.2,1.4],[3.8,1.4],[3.8,2.8],[.2,2.8]]),False).set_color(RED)
   d['old-outline']=square().set_opacity(.30)
  if state in ['cut-square','discard-square']:
   d.pop('square');a=np.array([[.45,.7],[1.85,.7],[1.85,3.5],[.45,3.5]]);b=a+[1.75,0]
   d['left-piece']=face(a,GREEN,.22);d['right-piece']=face(b,BLUE,.22)
   if state=='discard-square':d['right-piece'].set_opacity(.25);d['discard-label']=label('버릴 수 있음',p([2.9,.25]),MUTED,22)
 elif state=='scale':
  small=np.array([[.3,.3],[1.8,.3],[.3,1.3]]);big=np.array([[.3,.3],[3.3,.3],[.3,2.3]])
  d['big']=face(big,BLUE,.13);d['small']=face(small,GREEN,.26)
  d['dimensions']=VGroup(label('밑변 ×2',p([1.8,-.15]),BLUE,24),label('높이 ×2',p([.6,2.7]),BLUE,24),label('넓이 ×4',p([2.6,1.8]),GOLD,25))
 elif state=='thin':
  # Height is explicitly magnified x50, matching the approved baseline caveat.
  v=np.array([[.2,.8],[4,.8],[3.6,1.3]]);w=v.copy();w[2,1]+=.05
  d['thin']=face(v,GREEN,.2);d['perturbation']=face(w,RED,.12)
  d['note']=textblock('높이 방향 ×50 확대 도식\n정의한 수치 · 게임 실측값 아님',-3.7,-2.10,MUTED,21,5.2)
 else:
  d['l']=boundary()
  if state=='l-center':d['center']=point([19/14,19/14],'',GOLD)
  if state=='l-trace':d['outline']=VMobject(color=GREEN,stroke_width=6).set_points_as_corners([p(q) for q in [*L,L[0]]])
  if state in ['notch-cross','pieces-notch']:d['crossing']=seg([.5,3.5],[3.5,.5],RED,True)
  if state=='turn':
   d['incoming']=Arrow(p(L[2]),p(L[3]),buff=0,color=RED,stroke_width=6);d['outgoing']=Arrow(p(L[3]),p(L[4]),buff=0,color=GREEN,stroke_width=6)
   d['u-label']=label('u',p([2.7,.55]),RED);d['v-label']=label('v',p([1.45,2.7]),GREEN)
  if state=='wrong-fan':
   d['wrong-fan']=VGroup(*[face(L[list(k)],c,.20) for k,c in zip([(2,3,4),(2,4,5),(2,5,0),(2,0,1)],[RED,GOLD,BLUE,GREEN])]);d['bad-region']=face(L[[2,3,4]],RED,.32)
   d['notch-label']=label('원래 빈 홈',p([2.5,2.8]),RED,23)
  if state in ['first-ear','first-ear-test','next-link','second-ear']:
   d['first-ear']=face(L[[0,1,2]],GREEN,.28)
   if state in ['first-ear-test','next-link','second-ear']:d['new-edge']=seg(L[0],L[2],GREEN)
   if state=='first-ear-test':d['test-label']=label('내부 대각선',p([2.2,1.6]),GREEN,24)
   if state in ['next-link','second-ear']:d['active-boundary']=VMobject(color=GOLD,stroke_width=5).set_points_as_corners([p(q) for q in L[[0,2,3,4,5,0]]])
   if state=='second-ear':d['next-candidate']=face(L[[0,2,3]],GOLD,.26)
  if state in ['pieces','pieces-notch','centroids','weighted-centroid']:d['parts']=pieces()
  if state in ['centroids','weighted-centroid']:
   areas=[2,1.5,1.5,2];centers=[L[list(k)].mean(axis=0) for k in EARS]
   d['centroids']=VGroup(*[point(q,f'G{i+1}',col,LEFT if i>1 else DOWN) for i,(q,col) in enumerate(zip(centers,[GREEN,BLUE,GOLD,RED]))])
   if state=='weighted-centroid':d['whole-center']=point(np.average(centers,axis=0,weights=areas),'G',INK,UR)
 return d

class RecoveredAddition(Scene):
 sid=''
 def construct(self):
  self.camera.background_color=WHITE
  slot=next(s for s in T['scenes'] if s['id']==self.sid);source=next(s for s in LSS['scenes'] if s['id']==self.sid)
  title=fit(txt(source['title'],37),12.6).move_to([0,3.35,0],aligned_edge=LEFT).to_edge(LEFT,buff=.58)
  sub=txt('같은 입력 → 조건 선택 → 계산 → 결과 / 숫자는 정의한 예제',20,MUTED).move_to([0,2.75,0])
  self.add(title,sub,Line([-6.5,2.48,0],[6.5,2.48,0],color=RULE,stroke_width=1))
  layers={};main=note=None;previous=None
  for sentence,words,support,state in STATES[self.sid]:
   cue=slot['sentenceCues'][sentence];start=cue['start']
   if start>self.renderer.time+1/60:self.wait(start-self.renderer.time,frozen_frame=True)
   # Keep stable named geometry; reveal only changed properties.
   if state!=previous:
    fresh=diagram(state)
    remove=[key for key in layers if key not in fresh]
    if remove:self.play(*[FadeOut(layers[k]) for k in remove],run_time=.12)
    for k in remove:self.remove(layers.pop(k))
    additions=[]
    for key,mob in fresh.items():
     if key in layers:
      # Same layers are persistent except an explicitly changed shape.
      if key=='square' and state=='different':self.play(Transform(layers[key],mob),run_time=.4)
      continue
     layers[key]=mob;additions.append(mob)
    if additions:self.play(*[Create(m) for m in additions],run_time=.45)
    previous=state
   if main is not None:self.remove(main)
   if note is not None:self.remove(note)
   main=textblock(words,3.1,.95,RED if state=='wrong-fan' else GOLD,29,6.5)
   note=textblock(support,3.1,-1.15,GREEN if state not in ['wrong-fan','notch-cross'] else RED,25,6.5) if support else VGroup()
   self.add(main,note)
  if slot['seconds']>self.renderer.time+1/60:self.wait(slot['seconds']-self.renderer.time,frozen_frame=True)
  assert self.renderer.time<=slot['seconds']+2/60,(self.sid,self.renderer.time,slot['seconds'])

base=original.make_scenes('game-math-polygons-triangulation',__name__)
for slot in T['scenes']:
 if slot['classification']!='explanation':continue
 sid=slot['id']
 parent=base['Scene'+sid] if sid.isdigit() else RecoveredAddition
 globals()['Polish'+sid]=type('Polish'+sid,(parent,),{'sid':sid,'__module__':__name__})
