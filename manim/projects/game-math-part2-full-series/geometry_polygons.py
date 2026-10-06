"""Independent white2.5D centers, boundaries and verified ear partitions."""
from lesson import *

TRI=np.array([[0.,0.],[4.,0.],[0.,3.]])
L=np.array([[0.,0.],[4.,0.],[4.,1.],[1.,1.],[1.,4.],[0.,4.]])
EARS=[(0,1,2),(0,2,3),(0,3,4),(0,4,5)]
COLORS=[RED,GREEN,BLUE,GOLD]

def layered_polygon(v,C,scale=.8,color=BLUE,opacity=.22):
 points=[C+scale*np.r_[p,0.] for p in v]
 face=Polygon(*points,stroke_color=color,stroke_width=3,fill_color=color,fill_opacity=opacity)
 shadow=Polygon(*points,stroke_width=0,fill_color=RULE,fill_opacity=.35).shift(.07*RIGHT+.07*DOWN)
 return VGroup(shadow,face)

class TrianglePolygonScene(ThreeDScene):
 slug='';sid='';fixed=LectureScene.fixed;replace_fixed=LectureScene.replace_fixed
 def construct(self):
  self.camera.background_color=WHITE
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(x for x in data['scenes'] if x['id']==self.sid)
  slot=next(x for x in timing(self.slug,data)['scenes'] if x['id']==self.sid);mode=s['mode']
  title=fit(txt(s['title'],40),12.65).to_corner(UL,buff=.6)
  sub=fit(txt('게임수학 Part 2 / 기하 3편 · 중심의 목적 / 순서 있는 경계 / 영역 보존',20,MUTED),12.65).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.fixed(title,sub,Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1))
  full=mode=='overview';active=eq=note=None;special=None;legend=None;obj=[];labels=[]
  C=np.array([-5.2,-1.2,0.]);scale=.8
  pos=lambda p:C+scale*np.r_[p,0.]
  def equation(value,color=GOLD):
   nonlocal eq
   eq=self.replace_fixed(eq,fit(txt(value,26,color),11.8 if full else 5.9).move_to([0 if full else 3.15,-.55,0]))
  def foot(value,color=GREEN):
   nonlocal note
   note=self.replace_fixed(note,fit(txt(value,21,color),11.8 if full else 5.9).move_to([0 if full else 3.15,-2.13,0]))
  def contour(v,annotate=True):
   shape=layered_polygon(v,C,scale);self.fixed(shape)
   if annotate:
    for j,p in enumerate(v):
     d=Dot(pos(p),radius=.055,color=INK)
     direction=DOWN if p[1]==0 else UP if p[1]==max(v[:,1]) else RIGHT
     label=txt(f'v{j}',19,MUTED).next_to(d,direction,buff=.09)
     self.fixed(d,label);labels.append(VGroup(d,label))
   return shape
  def patch(indices,color=GREEN):return layered_polygon(L[list(indices)],C,scale,color,.25)
  if full:
   special=VGroup(*[card(v,width=3.8,size=27) for v in ['무게중심·내심·외심','경계·볼록성','삼각형 분할·검증']]).arrange(RIGHT,buff=.35).move_to([0,-.05,0]);self.fixed(special)
   self.fixed(VGroup(*[Arrow(special[j].get_right(),special[j+1].get_left(),buff=.04,color=MUTED) for j in range(2)]))
  elif mode in ['center-questions','centroid','incenter','circumcenter','polygon-practice']:
   if mode=='circumcenter':C=np.array([-5.2,.1,0.]);scale=.6
   else:C=np.array([-5.2,-.9,0.]);scale=.88
   triangle=contour(TRI);obj=[triangle]
   points=[np.array([4/3,1.]),np.array([1.,1.]),np.array([2.,1.5])]
   dots=VGroup(*[Dot(pos(p),radius=.075,color=c) for p,c in zip(points,[GREEN,GOLD,BLUE])])
   names=VGroup(*[txt(name,22,c).next_to(d,direction,buff=.1) for name,c,d,direction in zip(['G','I','O'],[GREEN,GOLD,BLUE],dots,[DOWN,LEFT,RIGHT])])
   if mode=='center-questions':obj.extend([dots,names])
   elif mode=='centroid':
    medians=VGroup(*[DashedLine(pos(TRI[j]),pos((TRI[(j+1)%3]+TRI[(j+2)%3])/2),color=GREEN,stroke_width=2) for j in range(3)])
    self.fixed(dots[0],names[0]);obj.extend([medians,dots[0],names[0]])
   elif mode=='incenter':
    self.fixed(dots[1],names[1]);circle=Circle(radius=scale,color=GOLD,stroke_width=3).move_to(pos(points[1]))
    feet=[np.array([1.,0.]),np.array([0.,1.]),np.array([1.6,1.8])]
    distances=VGroup(*[DashedLine(pos(points[1]),pos(p),color=GOLD,stroke_width=2) for p in feet])
    obj.extend([circle,distances])
   elif mode=='circumcenter':
    circle=Circle(radius=2.5*scale,color=BLUE,stroke_width=3).move_to(pos(points[2]))
    bisectors=VGroup(DashedLine(pos([2,-.6]),pos([2,3.9]),color=BLUE),DashedLine(pos([-.4,1.5]),pos([4.6,1.5]),color=BLUE))
    self.fixed(dots[2],names[2]);obj.extend([circle,bisectors,dots[2],names[2]])
   else:obj.extend([dots,names])
   legend=txt('논리 XY 좌표 / 면적·밀도 조건 명시',19,MUTED).move_to([-3.35,-2.13,0]);self.fixed(legend)
  elif mode in ['polygon-boundary','polygon-turns','concave-fan','ear-first','ear-sequence']:
   boundary=contour(L);obj=[boundary]
   if mode=='polygon-turns':
    arrows=VGroup(*[Arrow(pos(p),pos(q),buff=.12,color=RED if j==3 else GREEN,stroke_width=3) for j,(p,q) in enumerate(zip(L,np.roll(L,-1,axis=0)))])
    obj.append(arrows)
   if mode in ['ear-first','ear-sequence']:obj.append([])
   self.fixed(txt('반시계 경계 / 빈 영역은 오른쪽 위',19,MUTED).move_to([-3.35,-2.13,0]))
  elif mode=='convexity':
   hexagon=np.array([[math.cos(a),math.sin(a)] for a in np.arange(6)*TAU/6])*1.5+[2,2]
   shape=contour(hexagon,False);obj=[shape]
  elif mode=='convex-fan':
   v=np.array([[0,1],[1,0],[3,0],[4,1],[3,3],[1,3]],float);shape=contour(v);obj=[shape,v,[]]
  elif mode=='triangle-quality':
   thin=np.array([[0,0],[4,0],[3.9,.12]],float)
   good=np.array([[.8,1.3],[3.8,1.3],[2.3,3.6]],float)
   obj=[layered_polygon(thin,C,scale,RED,.25),layered_polygon(good,C,scale,GREEN,.25)];self.fixed(*obj)
   self.fixed(txt('긴 변·작은 높이',20,RED).move_to([-3.55,-1.65,0]),txt('같은 입력 조건 안에서 품질 비교',19,MUTED).move_to([-3.35,-2.13,0]))
  else:raise ValueError('Unimplemented independent polygon mode: '+mode)
  for i,beat in enumerate(s['beats']):
   ts=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   if ts>self.renderer.time+1/60:self.wait(ts-self.renderer.time,frozen_frame=True)
   active=self.replace_fixed(active,card(beat,width=12 if full else 6,size=25,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to([0 if full else 3.15,1.66,0]))
   if full:self.play(Indicate(special[max(0,min(i-1,2))],color=GREEN),run_time=.55)
   elif mode=='center-questions':
    if i<3:self.fixed(obj[1][i],obj[2][i]);self.play(FadeIn(obj[1][i]),FadeIn(obj[2][i]),run_time=.6)
    equation(['G=(4/3,1)','I=(1,1)','O=(2,1.5)','평균 / 변 / 꼭짓점','세 꼭짓점 (0,0),(4,0),(0,3)','세 점의 의미와 위치가 다름'][i])
   elif mode=='centroid':
    equation(['G=(v₀+v₁+v₂)/3','중선 위 2/3 지점','λ=(1/3,1/3,1/3)','일정 밀도 삼각형 판: 질량 중심','다각형 도심: ΣAᵢGᵢ/ΣAᵢ','좌표 평균 ≠ 비퇴화 판 보장'][i])
    if i==1:self.fixed(obj[1]);self.play(Create(obj[1]),run_time=.85)
    if i==4:foot('임의 다각형 꼭짓점 평균은 일반 도심이 아님',RED)
   elif mode=='incenter':
    equation(['I=Σaᵢvᵢ/P','반대편 길이 (5,3,4) / P=12','I=(1,1)','빗변 거리=|3+4-12|/5=1','r=2A/P=2×6/12=1','r=A/s=6/6=1'][i])
    if i==2:self.fixed(obj[1],obj[2]);self.play(Create(obj[1]),Create(obj[2]),run_time=.85)
    if i==5:foot('둘레 P / 반둘레 s=P/2 구분')
   elif mode=='circumcenter':
    equation(['두 변의 수직이등분선','O=(2,1.5)','R=2.5 / 세 꼭짓점 거리 동일','예각 내부·직각 빗변·둔각 외부','둔각 예제: O=(2,-1)','외적·면적≈0: 유일한 유한 원 거절'][i])
    if i==0:self.fixed(obj[2]);self.play(Create(obj[2]),run_time=.65)
    if i==2:self.fixed(obj[1]);self.play(Create(obj[1]),run_time=.8)
    if i==4:
     obtuse=np.array([[0.,0.],[4.,0.],[1.,1.]])
     self.remove(obj[2],legend,*[part for group in labels for part in group]);labels=[]
     new=layered_polygon(obtuse,C,scale)
     self.play(Transform(obj[0],new),obj[3].animate.move_to(pos([2,-1])),obj[4].animate.next_to(pos([2,-1]),RIGHT,buff=.15),Transform(obj[1],Circle(radius=math.sqrt(5)*scale,color=RED,stroke_width=3).move_to(pos([2,-1]))),run_time=1.0)
     self.fixed(txt('(0,0)  (4,0)  (1,1)',20,MUTED).move_to([-3.35,-2.13,0]));foot('외심이 바깥이어도 세 꼭짓점까지 같은 거리')
   elif mode=='polygon-boundary':
    equation(['마지막→처음까지 닫힌 순서','6점 L / 면적 7','오목 꼭짓점 v₃=(1,1)','finite / unique / nonzero edges','coplanar / simple boundary','오늘은 구멍 없는 단순 다각형'][i])
    if i==2:self.play(Indicate(labels[3],color=RED),run_time=.7)
    if i==5:foot('구멍·자기 교차를 이 예제에 넣지 않기')
   elif mode=='convexity':
    equation(['내부 두 점 → 선분 전체 내부','정육각형·삼각형: 볼록','L 내부 p=(.5,3.5), q=(3.5,.5)','선분 중간=(2,2): L 바깥','단순 평면 경계의 회전 부호','순서·교차 검증을 먼저 수행'][i])
    if i==1:
     segment=Line(pos([1,2]),pos([3,2]),color=GREEN,stroke_width=4);self.fixed(segment);obj.append(segment)
    if i==2:
     if len(obj)>1:self.remove(obj[1])
     self.play(Transform(obj[0],layered_polygon(L,C,scale)),run_time=.7)
     segment=Line(pos([.5,3.5]),pos([3.5,.5]),color=RED,stroke_width=4);dots=VGroup(Dot(pos([.5,3.5]),color=GREEN),Dot(pos([3.5,.5]),color=GREEN),Dot(pos([2,2]),color=RED));self.fixed(segment,dots);obj.append(segment);self.play(Create(segment),run_time=.75)
   elif mode=='polygon-turns':
    equation(['cross₂(eᵢ,eᵢ₊₁): turn sign','L 회전: +,+,−,+,+,+','0은 일직선 / 규칙 명시','Σθ=(n−2)·180°','n=6: 볼록·오목 모두 720°','acos clamp + 반사 내각 구분'][i])
    if i==0:self.fixed(obj[1]);self.play(Create(obj[1]),run_time=.8)
    if i==1:self.play(Indicate(labels[3],color=RED),run_time=.6)
    if i==4:foot('같은 각도 합이 볼록성을 보장하지 않음',RED)
   elif mode=='convex-fan':
    equation(['convex polygon: anchor v₀','(0,1,2), (0,2,3), …','n=6 → 4 triangles','볼록성: 대각선이 모두 내부','winding·원래 vertex indices','개수뿐 아니라 실제 덮기 검사'][i])
    if i in [1,2]:
     indices=[(0,j,j+1) for j in range(1,3 if i==1 else 5)]
     for item in obj[2]:self.remove(item)
     obj[2]=[layered_polygon(obj[1][list(k)],C,scale,c,.3) for k,c in zip(indices,COLORS)];self.fixed(*obj[2]);self.play(LaggedStart(*[FadeIn(x) for x in obj[2]],lag_ratio=.12),run_time=.8)
   elif mode=='concave-fan':
    equation(['오목 L / 임의 anchor v₂','외부 영역을 채우는 빨강 삼각형','signed areas: -4.5+1.5+8+2','합=7 / 절댓값 합=16','이 특정 L에서는 v₀ fan이 유효','일반 오목 입력에 fan을 적용하지 않기'][i])
    if i==0:
     items=[layered_polygon(L[list(k)],C,scale,c,.28) for k,c in zip([(2,3,4),(2,4,5),(2,5,0),(2,0,1)],COLORS)];obj.append(items);self.fixed(*items)
     items[0][1].set_fill(RED,opacity=.6);self.bring_to_front(items[0])
    if i==1:self.play(Indicate(obj[1][0],color=RED),run_time=.7)
    if i==4:
     for x in obj[1]:self.remove(x)
     items=[patch(k,c) for k,c in zip(EARS,COLORS)];obj[1]=items;self.fixed(*items);self.play(LaggedStart(*[FadeIn(x) for x in items],lag_ratio=.1),run_time=.85)
   elif mode=='ear-first':
    equation(['prev, current, next','convex + inside + other vertex test','ear (0,1,2), area=2','store triangle / remove v₁','0→2→3→4→5→0','indices 유지 / 연결 관계 갱신'][i])
    if i==2:
     ear=patch(EARS[0],GREEN);self.fixed(ear);obj[1].append(ear);self.play(FadeIn(ear),run_time=.6)
    if i==3:self.play(Transform(obj[0],layered_polygon(L[[0,2,3,4,5]],C,scale)),FadeOut(labels[1]),run_time=.8)
   elif mode=='ear-sequence':
    equation(['두 번째 (0,2,3): 1.5','세 번째 (0,3,4): 1.5','마지막 (0,4,5): 2','총 넓이 7 + 겹침·외부 없음','귀 없음: 실패를 기록하고 중단','구멍 연결은 별도 규칙·구현 필요'][i])
    if i==0:
     self.remove(labels[1]);first=patch(EARS[0],RED);second=patch(EARS[1],GREEN);self.fixed(first,second);obj[1].extend([first,second]);self.play(Transform(obj[0],layered_polygon(L[[0,3,4,5]],C,scale)),FadeOut(labels[2]),run_time=.8)
    if i==1:
     third=patch(EARS[2],BLUE);self.fixed(third);obj[1].append(third);self.play(Transform(obj[0],layered_polygon(L[[0,4,5]],C,scale)),FadeOut(labels[3]),run_time=.8)
    if i==2:
     fourth=patch(EARS[3],GOLD);self.fixed(fourth);obj[1].append(fourth);self.play(FadeIn(fourth),run_time=.6)
    if i==3:foot('2 + 1.5 + 1.5 + 2 = 7 / 같은 외곽선')
   elif mode=='triangle-quality':
    equation(['작은 넓이·각도 → 수치 민감성','여러 유효 귀 중 품질 선호','valid ear를 먼저 확인','대각선 선택에 따라 품질 달라짐','winding / indices / area / coverage','ε_length와 ε_area는 단위가 다름'][i])
    if i==1:self.play(Indicate(obj[1],color=GREEN),run_time=.7)
    if i==2:foot('각도만 좋고 바깥인 후보는 거절',RED)
   elif mode=='polygon-practice':
    equation(['세 중심을 직접 구분하세요','G=(4/3,1), I=(1,1), O=(2,1.5)','r=1 / R=2.5','L: 2+1.5+1.5+2=7','개수·면적 합 + 영역·경계 검사','다음: 렌더링 / 3D→화면 픽셀'][i])
    if i==1:self.fixed(obj[1],obj[2]);self.play(FadeIn(obj[1]),FadeIn(obj[2]),run_time=.7)
    if i==3:
     self.remove(*obj,legend,*[part for group in labels for part in group]);labels=[];C=np.array([-5.2,-1.2,0.]);scale=.8
     shape=contour(L);items=[patch(k,c) for k,c in zip(EARS,COLORS)];self.fixed(*items);obj=[shape,*items];self.play(LaggedStart(*[FadeIn(x) for x in items],lag_ratio=.12),run_time=.85)
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(TrianglePolygonScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
