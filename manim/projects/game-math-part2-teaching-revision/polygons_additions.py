"""Independent narrated spatial additions; preserve the chapter's recorded white theme.

Logical coordinates are right-handed x/y with a proper rotation into Manim's
z-up drawing frame. Screen projection is presentation, never a game measure.
"""
from pathlib import Path
import sys,json,os
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import txt,fit,P,arrow,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD
from quaternion import screen_point
B=ROOT/'production/batches/game-math-part2-teaching-revision';O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons'
CONTENT={s['id']:s for s in json.loads((B/'polygons-flow-draft.json').read_text(encoding='utf8'))['additions']}
SLUGS=['game-math-polygon-centers-v2','game-math-polygon-partition-v2']
TEAL='#327d7d'

class PolygonAddition(ThreeDScene):
 sid='QF01'
 def construct(self):
  self.camera.background_color=WHITE
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  record=CONTENT[self.sid];slot=json.loads((O/'combined-addition-timing.json').read_text(encoding='utf8'))[self.sid]
  if os.environ.get('REVISION_FINAL_TIMING')=='1':
   found=[]
   for slug in SLUGS:
    path=ROOT/f'projects/{slug}/production/timeline.json'
    if path.exists():found.extend(s for s in json.loads(path.read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
   assert len(found)==1 and found[0]['voiceSha256']==slot['voiceSha256'];slot=found[0]
  total=slot['seconds'];starts=slot['lineStarts'];origin=screen_point(-3.25,.05)
  self.add_fixed_in_frame_mobjects(fit(txt(record['title'],35),12.4).to_corner(UL,buff=.6),
   txt('같은 입력 → 조건 선택 → 계산 → 결과 / 숫자는 정의한 예제',19,MUTED).move_to([0,2.67,0]))
  labels={};geometry_labels=[]
  def fixed(text,where,color=INK,size=27,width=6.0,height=1.45):
   g=VGroup(*[fit(txt(s,size,color),width) for s in text.split(' / ')]).arrange(DOWN,aligned_edge=LEFT,buff=.17)
   if g.height>height:g.scale(height/g.height)
   g.move_to(where);self.add_fixed_in_frame_mobjects(g);return g
  def replace(key,text,where,color=INK,size=27,width=6.,height=1.45):
   if key in labels:self.remove(labels[key])
   labels[key]=fixed(text,where,color,size,width,height)
  def equation(text,color=GOLD):replace('equation',text,[3.2,.5,0],color)
  def note(text,color=INK):replace('note',text,[3.2,-1.5,0],color,25,6.,1.15)
  def footer(text):replace('footer',text,[-3.25,-2.3,0],MUTED,20,5.8,.6)
  def wait_to(t):
   if t>self.renderer.time:self.wait(t-self.renderer.time,frozen_frame=True)
  def line(i):wait_to(starts[i])
  def sentence(fragment):
   matches=[c for c in slot.get('sentenceCues',[]) if fragment in c['text']]
   assert len(matches)==1,(self.sid,fragment,[c['text'] for c in matches]);wait_to(matches[0]['start'])
  def point(q,color=GOLD):return Dot3D(q,radius=.075,color=color,resolution=(8,8))
  def mapping(center=(2,2),scale=.8):
   return lambda q:origin+scale*P@np.array([q[0]-center[0],q[1]-center[1],q[2] if len(q)>2 else 0],float)
  def plate(coords,project,color=BLUE,opacity=.10,depth=.15):
   vertices=[project(q) for q in coords];down=-depth*P[:,2]
   lower=Polygon(*[v+down for v in vertices],fill_color=color,fill_opacity=.07,stroke_color=RULE,stroke_width=1.)
   sides=VGroup(*[Polygon(vertices[k],vertices[(k+1)%len(vertices)],vertices[(k+1)%len(vertices)]+down,vertices[k]+down,
    fill_color=color,fill_opacity=.16,stroke_color=RULE,stroke_width=.7) for k in range(len(vertices))])
   top=Polygon(*vertices,fill_color=color,fill_opacity=opacity,stroke_color=color,stroke_width=2.4)
   self.add(lower,sides,top);return VGroup(lower,sides,top),vertices
  def labels_at(coords,project,names=None):
   dots=VGroup(*[point(project(q),[RED,GREEN,BLUE,GOLD,TEAL,MUTED][k%6]) for k,q in enumerate(coords)])
   self.add(dots)
   geometry_labels.append(dots)
   for k,q in enumerate(coords):
    tag=txt(names[k] if names else str(k),19,INK).move_to(project(q)+screen_point(-.12,.18))
    self.add_fixed_orientation_mobjects(tag)
    geometry_labels.append(tag)
   return dots
  tri=np.array([[0.,0.],[4.,0.],[0.,3.]])
  lc=np.array([[0.,0.],[4.,0.],[4.,1.],[1.,1.],[1.,4.],[0.,4.]])
  project=mapping()
  def triangle():
   p=mapping((2,1.5),.9);shape,v=plate(tri,p);labels_at(tri,p,['A','B','C']);return shape,v,p
  def lshape(numbered=True):
   shape,v=plate(lc,project)
   if numbered:labels_at(lc,project)
   return shape,v
  def lparts():
   shape,v=lshape();ids=[(0,1,2),(0,2,3),(0,3,4),(0,4,5)];colors=[GREEN,BLUE,GOLD,TEAL]
   parts=VGroup(*[Polygon(*[v[k] for k in ind],fill_color=c,fill_opacity=.16,stroke_color=c,stroke_width=2.) for ind,c in zip(ids,colors)])
   self.add(parts);return shape,v,parts,ids
  if self.sid=='QF01':
   old=np.array([[0,0],[6,0],[0,4]],float);p=mapping((3,2),.65);shape,v=plate(old,p);labels_at(old,p,['A','B','C'])
   q=point(p([1.8,2]),GOLD);self.add(q)
   equation('앞 편: p=.2A+.3B+.5C / 삼각형 안의 주소');note('찾은 위치 → 기준점은 어디에?',GREEN)
   sentence('그런데 표시를');self.play(Indicate(q),run_time=.6);equation('남은 질문 / 어떤 목적의 기준점인가?')
   sentence('무엇을 같게');note('좌표를 평균할까? / 변·꼭짓점까지 거리를 같게 할까?');footer('중심의 목적 → 경계의 조건 → 삼각형 분할')
  elif self.sid=='QB01':
   shape,v,p=triangle();g=tri.mean(axis=0);q=point(p(g));self.add(q)
   rays=VGroup(*[Line3D(p(g),x,color=c,thickness=.022) for x,c in zip(v,[RED,GREEN,BLUE])])
   self.play(*[Create(r) for r in rays],run_time=.75);equation('p=⅓A+⅓B+⅓C / G=(4/3,1)');note('같은 비율 → 좌표 평균')
   sentence('균일한 종이');self.play(Indicate(shape,color=GREEN),run_time=.7);note('밀도가 일정한 삼각형 판 / 균형 위치와 연결',GREEN)
   sentence('모든 변까지');equation('좌표 평균만 넣었음 / 거리 조건은 아직 별개');footer('이제 명시한3-4-5 예제 / A(0,0), B(4,0), C(0,3)')
  elif self.sid=='QB02':
   shape,v,p=triangle();i=np.array([1.,1.]);ip=p(i);q=point(ip);self.add(q)
   feet=[p([1,0]),p([0,1])];perp=VGroup(*[Line3D(ip,f,color=TEAL,thickness=.027) for f in feet]);self.add(perp)
   equation('점에서 두 변으로 / 수직선을 내려 거리 비교');note('수직 거리 / 비스듬한 꼭짓점 거리가 아님')
   sentence('각을 반으로');bisect=arrow(v[0],ip,RED);self.play(Create(bisect),run_time=.7)
   right_parts=VGroup(*[Polygon(v[0],ip,f,fill_color=c,fill_opacity=.12,stroke_color=c,stroke_width=2.) for f,c in zip(feet,[BLUE,GREEN])])
   self.play(*[Create(t) for t in right_parts],run_time=.7);equation('공통 빗변 + 같은 반각 / 합동 → 수직 거리 같음')
   line(1);self.remove(right_parts);links=VGroup(*[Line3D(ip,x,color=GOLD,thickness=.02) for x in v]);self.play(*[Create(r) for r in links],run_time=.7)
   sentence('세 작은 삼각형은');regions=VGroup(*[Polygon(ip,v[(k+1)%3],v[(k+2)%3],fill_color=c,fill_opacity=.10,stroke_color=c,stroke_width=2) for k,c in enumerate([RED,GREEN,BLUE])])
   self.play(*[Create(r) for r in regions],run_time=.8);equation('세 부분의 높이=r / 부분 넓이=반대편 변×r/2')
   sentence('넓이는 밑변');equation('넓이 비율=(5r/2,3r/2,4r/2)/(12r/2) / =(5,3,4)/12');note('앞 편의 넓이 가중치 / 이번에는 반대편 변 길이로 구함',GREEN);footer('그림은 같은 거리 조건 / 이어서 내심 좌표와 반지름 계산')
  elif self.sid=='QB03':
   shape,v,p=triangle();i=point(p([1,1]),GREEN);self.add(i);equation('앞:세 변까지 수직 거리 같음');note('이번:세 꼭짓점까지 거리 같음',BLUE)
   sentence('두 점의 중간');mid=p([2,0]);m=point(mid,TEAL);self.add(m)
   bis=Line3D(p([2,-.2]),p([2,3.2]),color=RED,thickness=.022);self.play(Create(bis),run_time=.7)
   q=point(p([2,1.5]),BLUE);self.add(q);rays=VGroup(*[Line3D(q.get_center(),x,color=BLUE,thickness=.022) for x in v[:2]]);self.play(*[Create(r) for r in rays],run_time=.65)
   equation('중점의 양옆 길이 같음 / 공통 높이 → 두 빗변 길이 같음');note('수직이등분선 / 중점에서 직각으로 세운 선')
   sentence('이 선이');footer('이어서 두 변의 수직이등분선 교점 계산')
  elif self.sid=='QB04':
   shape,v=lshape();center=point(project([19/14,19/14]));self.add(center)
   equation('중심 한 점 / 전체 모양은 아직 알 수 없음');note('남길 땅과 빈 공간을 / 경계로 구분')
   sentence('경계점을 순서대로');walk=point(v[0],GOLD);self.add(walk)
   for k in range(6):self.play(Create(Line3D(v[k],v[(k+1)%6],color=RED,thickness=.023)),walk.animate.move_to(v[(k+1)%6]),run_time=.3)
   equation('0→1→2→3→4→5→0 / 끝에서 처음으로 닫기');footer('같은 L자 유지 / 오른쪽 위 빈 영역은 제외')
   sentence('이제 중심을');note('중심 선택의 결과 → 경계 보존 / 입력부터 차례대로 검증',GREEN)
  elif self.sid=='QB05':
   shape,v=lshape();inside1=project([.5,3.5]);inside2=project([3.5,.5]);bad=DashedLine(inside1,inside2,color=RED,stroke_width=3);self.add(bad)
   equation('안의 두 점을 잇는 선 / 빈 부분을 지남 → 오목');note('같은 사실을 / 경계의 회전으로 계산')
   sentence('경계를 돌며');self.play(FadeOut(bad),Create(arrow(v[2],v[3],RED)),Create(arrow(v[3],v[4],GREEN)),run_time=.7)
   equation('u=v₃−v₂=(-3,0) / v=v₄−v₃=(0,3)');note('반시계 경계의 홈 / 다른 꼭짓점과 반대 회전')
   sentence('두 방향의');curve=VMobject(color=GOLD,stroke_width=3).set_points_as_corners([project([1+.42*np.cos(t),1+.42*np.sin(t)]) for t in np.linspace(PI,PI/2,20)])
   self.play(Create(curve),run_time=.65);equation('uₓvᵧ−uᵧvₓ / (-3)×3−0×0=-9',RED);footer('x 오른쪽·y 위 / 부호는 방향, 크기는 넓이 단위')
  elif self.sid in ['QF02','QF03']:
   shape,v=lshape();equation('중심의 목적을 구분 / 유효한 경계·홈 확인');note('경계는 바깥을 정함 / 안쪽 분할은 다음 문제',GREEN)
   if self.sid=='QF02':
    sentence('경계는 땅의');self.play(Indicate(shape[-1]),run_time=.6);equation('다음 편 / 빈 영역을 지키며 삼각형으로 나누기');footer('검사한 경계와 홈 / 다음 편에서도 같은 입력 유지')
   else:
    sentence('이번에는');equation('이번 질문 / 땅을 겹침 없는 삼각형으로 나누기')
    line(1);equation('① 볼록한 부채꼴과 실패 / ② 귀를 하나씩 제거 / ③ 영역·빈 공간·품질 검사');note('같은 L자·점 번호 유지 / 입력부터 결과까지 확인');footer('여섯 꼭짓점의 L자 / 경계 순서와 빈 영역 계속 유지')
  elif self.sid=='QB06':
   shape,v=lshape();indices=[(2,3,4),(2,4,5),(2,5,0),(2,0,1)]
   parts=VGroup(*[Polygon(*[v[k] for k in ids],fill_color=RED if n==0 else BLUE,fill_opacity=.1,stroke_color=RED if n==0 else BLUE,stroke_width=2) for n,ids in enumerate(indices)])
   self.add(parts);equation('4조각이어도 / 홈을 덮거나 겹칠 수 있음',RED);note('같은 개수 ≠ 올바른 영역')
   sentence('더한 넓이에서');equation('부호 있는 합 / -4.5+1.5+8+2=7');self.play(Indicate(parts[0],color=RED),run_time=.7)
   sentence('합계가 같아도');note('합계는 위치를 알려주지 않음 / 원래 빈 홈은 계속 잘못 덮임',RED);footer('장부는 합계의 비유 / 공간을 덮는 조건까지 대신하지 않음')
  elif self.sid=='QB07':
   shape,v=lshape();ear=Polygon(v[0],v[1],v[2],fill_color=GREEN,fill_opacity=.12,stroke_color=GREEN,stroke_width=3)
   equation('전부 연결한 부채꼴은 실패 / 작은 후보 하나부터 검사');note('같은 L자에서 방법 변경')
   sentence('이번에는 이웃한');self.play(Create(ear),run_time=.7);equation('세 이웃 점(0,1,2) / 가운데1이 볼록 후보')
   sentence('볼록한 모서리여도');diagonal=Line3D(v[0],v[2],color=RED,thickness=.03);self.play(Create(diagonal),run_time=.7);equation('내부 대각선 검사 / 다른 남은 꼭짓점 검사');note('볼록한 모서리만으로는 부족',RED)
   sentence('안쪽에 놓이고');self.play(Indicate(ear,color=GREEN),run_time=.6);note('모든 유효성 조건 통과 → 귀 저장',GREEN);footer('이어서 넓이2인 귀 제거 / 저장된 점 번호는 보존')
  elif self.sid=='QB08':
   shape,v=lshape();ear=Polygon(v[0],v[1],v[2],fill_color=GREEN,fill_opacity=.18,stroke_color=GREEN,stroke_width=2.5)
   remaining=Polygon(*[v[k] for k in [0,2,3,4,5]],fill_color=BLUE,fill_opacity=.07,stroke_color=BLUE,stroke_width=2.5)
   self.add(ear,remaining);equation('저장된 출력:(0,1,2) / 남은 경계를 별도로 유지');note('원본 점 번호는 그대로')
   sentence('남은 경계에서는');edge=Line3D(v[0],v[2],color=RED,thickness=.03);self.play(Create(edge),run_time=.7);equation('이웃 갱신 / 0→2→3→4→5→0')
   sentence('삼각형을 하나');next_ear=Polygon(v[0],v[2],v[3],fill_color=GOLD,fill_opacity=.12,stroke_color=GOLD,stroke_width=3);self.play(Create(next_ear),run_time=.7);note('새 이웃으로 다음 귀 검사 / (0,2,3)',GREEN);footer('이어서 넓이1.5 → 1.5 → 2 / 합계와 실제 덮기 모두 검사')
  elif self.sid=='QB09':
   shape,v,parts,ids=lparts();equation('먼저 영역을 올바르게 덮음 / 그 뒤 조각 품질 개선');note('통로와 원래 경계 보존',GREEN)
   sentence('길이 단위를');self.play(FadeOut(shape),FadeOut(parts),run_time=.6)
   self.remove(*geometry_labels);geometry_labels.clear()
   # Independent unit comparison, not movement of the physical game surface.
   small=np.array([[0,0],[2,0],[0,1.5]],float);large=2*small;p=mapping((2,1.5),.85)
   a,_=plate(small,p,TEAL,.10);bb,_=plate(large,p,BLUE,.04);equation('좌표×2 → 밑변×2·높이×2 / 넓이×4');footer('같은 형상, 눈금 비교 / 길이 단위와 넓이 단위²를 구분')
   sentence('길이 오차와');note('길이 허용 오차와 넓이 허용 오차 / 단위·스케일을 따로 설정',RED)
   line(1);self.play(FadeOut(a),FadeOut(bb),run_time=.5)
   # Exact .01 height, deliberately enlarged in y only for readability.
   zoom=lambda q:origin+.75*P@np.array([q[0]-2,50*q[1]-.45,0.])
   thin,_=plate([[0,0],[4,0],[2,.01]],zoom,TEAL,.12)
   altered,_=plate([[0,0],[4,0],[2,.011]],zoom,RED,.04)
   equation('예시 h=.01, Δh=.001 / 높이·넓이 변화10%');note('가느다란 조각:같은 오차의 영향 큼 / 유효한 후보 안에서 개선')
   footer('높이 방향×50확대 도식 / 정의한 수치, 게임 실측값 아님')
  elif self.sid=='QB10':
   shape,v,parts,ids=lparts();centers=[lc[list(ind)].mean(axis=0) for ind in ids];areas=[2,1.5,1.5,2]
   dots=VGroup(*[point(project(g),c) for g,c in zip(centers,[GREEN,BLUE,GOLD,TEAL])]);self.add(dots)
   equation('균일한 판의 중심 / 삼각형별 넓이로 가중 평균');note('분할한 조각의 역할 / 위치·속성 계산의 바탕')
   sentence('넓이 이와');equation('G=(2G₁+1.5G₂+1.5G₃+2G₄)/7');g=np.sum(np.array(centers)*np.array(areas)[:,None],axis=0)/7
   center=point(project(g),RED);self.play(FadeIn(center),run_time=.6);footer('넓이 가중 중심=(19/14,19/14) / 꼭짓점 평균=(5/3,5/3)과 다름')
   sentence('분할한 이유가');note('같은 조건·같은 경계·같은 조각 / 마지막 두 문제로 확인',GREEN)
  else:raise RuntimeError(self.sid)
  assert self.renderer.time<=total+.05,(self.sid,self.renderer.time,total)
  wait_to(total)

for ident in CONTENT:globals()[ident]=type(ident,(PolygonAddition,),{'sid':ident,'__module__':__name__})
