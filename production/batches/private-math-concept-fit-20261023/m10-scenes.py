"""Bounds of explicitly authored meshes; camera changes are not object changes."""
from pathlib import Path
import importlib.util,json,os,itertools
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('bounds_style',Path(__file__).with_name('m05-scenes.py'));q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
text=q.text;BG=q.BG;FG=q.FG;X=q.X;Y=q.Y;Z=q.Z;YELLOW=q.YELLOW;RULE=q.RULE

def solid(size,center,color):
 g=Cube(side_length=1,fill_color=color,fill_opacity=1,stroke_color='#9FB2BF',stroke_width=.35)
 for i,x in enumerate(size):g.stretch(x,i)
 return g.shift(center)
def ball(center,r,color):
 return Sphere(radius=r,resolution=(8,12),fill_color=color,fill_opacity=1,stroke_width=.2).move_to(center)
def limb(a,b,r=.12,color='#91ACBA'):
 a=np.array(a);b=np.array(b)
 return Cylinder(radius=r,height=np.linalg.norm(b-a),direction=b-a,resolution=(4,10),fill_color=color,checkerboard_colors=[color,color],fill_opacity=1,stroke_width=.25).move_to((a+b)/2)
def person():
 head=VGroup(ball([0,0,1.18],.36,'#DCC2A1'),ball([.34,-.13,1.24],.046,'#25353F'),ball([.34,.13,1.24],.046,'#25353F'),ball([.36,0,1.15],.08,'#DCC2A1'))
 torso=VGroup(solid([.48,.73,.85],[0,0,.36],'#52788C'),solid([.45,.62,.25],[0,0,-.18],'#3B5368'))
 arms=[]
 for s in [-1,1]:
  shoulder=np.array([0,s*.49,.67]);elbow=np.array([.03,s*.63,.12]);hand=np.array([.15,s*.68,-.42])
  arms.append(VGroup(ball(shoulder,.16,'#BCC6CE'),limb(shoulder,elbow),ball(elbow,.13,'#BCC6CE'),limb(elbow,hand),ball(hand,.14,'#DCC2A1')))
 legs=VGroup()
 for s in [-1,1]:
  hip=[0,s*.23,-.3];knee=[.05,s*.23,-.9];foot=[.03,s*.23,-1.48]
  legs.add(limb(hip,knee,.16),ball(knee,.145,'#BCC6CE'),limb(knee,foot,.13),solid([.5,.28,.18],[.15,s*.23,-1.55],'#293F52'))
 return VGroup(head,torso,*arms,legs)
def building():
 g=VGroup(solid([2.8,1.45,1.55],[0,0,.0],'#BFA77F'))
 z=.775;ridge=1.5
 for s,c in [(-1,'#547D91'),(1,'#365668')]:
  g.add(Polygon([-1.52,s*.85,z],[1.52,s*.85,z],[1.52,0,ridge],[-1.52,0,ridge],fill_color=c,fill_opacity=1,stroke_color='#9FB2BF',stroke_width=.6))
 for x in [-1.4,1.4]:g.add(Polygon([x,-.725,z],[x,.725,z],[x,0,ridge],fill_color='#D0BC97',fill_opacity=1,stroke_width=.4))
 g.add(solid([.48,.035,1.02],[.0,-.745,-.25],'#423D37'))
 for x in [-.9,.9]:
  g.add(solid([.42,.04,.48],[x,-.75,.12],'#233B4A'),solid([.045,.05,.5],[x,-.78,.12],'#D5C298'),solid([.45,.05,.04],[x,-.78,.12],'#D5C298'))
 g.add(solid([.28,.3,.8],[.8,.32,1.26],'#7A6C5E'))
 return g
def bridge():
 g=VGroup(solid([3.6,.95,.18],[0,0,.0],'#98754E'))
 for y in [-.55,.55]:
  g.add(solid([3.7,.08,.1],[0,y,.65],'#BFA078'))
  for x in [-1.6,-.8,0,.8,1.6]:g.add(solid([.09,.09,.8],[x,y,.3],'#BFA078'))
 return g
def wire_box(lo,hi,color=Z):
 pts={bits:np.where(bits,hi,lo) for bits in itertools.product([0,1],repeat=3)}
 return VGroup(*[Line(p,pts[tuple(1-b if j==i else b for j,b in enumerate(bits))],color=color,stroke_width=3) for bits,p in pts.items() for i in range(3) if bits[i]==0])
def bounds(obj,color=Z):
 points=obj.get_all_points();return wire_box(points.min(axis=0),points.max(axis=0),color)
def sphere_guide(center,r):
 return VGroup(*[Circle(radius=r,color=Y,stroke_width=3).rotate(PI/2,axis=axis).shift(center) for axis in [RIGHT,UP,OUT]])

TITLES={'10':'둥근 표면과 계산용 구','LG04':'머리와 팔다리는 다른 범위','13':'팔을 펼치면 경계도 달라집니다','LG05':'건물과 건물을 감싸는 상자','16':'경계 상자 겹침 ≠ 실제 접촉','LG06':'제자리 회전 / 카메라 이동','19':'건물은 고정 · 카메라만 이동','LG07':'높이를 바꾸고 경계 다시 계산','21':'무엇을 감쌀지 먼저 정하기'}
PHRASES={
'10':['둥근 머리와 계산용 구','중심에서 모든 방향으로 같은 반지름','근사 범위 ≠ 정확한 표면','중심에서의 거리와 반지름 비교','화면 크기 ≠ 실제 반지름','감쌀 부분과 근사 오차를 선택'],
'LG04':['둥근 머리 / 긴 팔다리','초록: 머리를 감싸는 계산용 구'],
'13':['팔을 펼치면 윤곽도 변화','상세 검사 전에 단순한 경계','머리: 구 / 몸 전체: 상자','물체 축 상자 / 월드 축 상자','동작에 따라 필요한 범위도 변화','다음: 점들의 축별 최소·최대'],
'LG05':['건물을 놓고 크기 변경','벽과 지붕을 함께 감싸기','지붕 위 빈 공간도 상자에 포함','모양과 경계 상자는 다름'],
'16':['두 모형을 각각 감싼 상자','상자는 겹쳐도 모형은 떨어져 있음','기울어진 모양의 바깥 빈 공간','빠른 후보 검사 ≠ 상세 충돌 검사','필요한 정확도와 계산 비용','다음: 2D 반례로 직접 확인'],
'LG06':['위치 고정 · 물체만 회전','초록: 물체 축 / 파랑: 월드 축','물체 정지 · 카메라만 이동'],
'19':['고정 건물을 다른 쪽에서 보기','화면의 윤곽은 투영에 따라 변화','고정 물체의 월드 경계는 그대로','물체 자체의 회전은 다른 경우','무엇이 움직였는지 구분','다음: 원근을 제외한 아핀 변환'],
'LG07':['건물 높이 변경','모형 자체가 변하므로 경계 재계산','표면의 점 ≠ 상자의 꼭짓점'],
'21':['고정된 다리 / 자세가 변하는 몸','상자부터 변환하면 빈 공간도 포함','실제 점부터 변환하면 다른 경계','한 자세 / 여러 자세 중 무엇을 감쌀까?','작으면 누락 · 크면 검사 후보 증가','다음: 두 방법의 수치 비교']}
class Replacement(ThreeDScene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG;self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  self.add_fixed_in_frame_mobjects(text(TITLES[self.sid],36,YELLOW).to_corner(UL,buff=.5),text('우리 모형 · 계산용 경계',20,q.v.SECOND).to_corner(UR,buff=.5))
  origin=q.pos(-3.3,.1);objs=[];guides=[];obb=None;head_guide=None
  if self.sid in ['10','LG04','13']:
   body=person().scale(1.0).shift(origin);objs=[body]
   head_guide=sphere_guide(origin+np.array([0,0,1.18]),.49)
   if self.sid in ['10','LG04']:self.add(head_guide)
  elif self.sid in ['LG05','19','LG07']:objs=[building().scale(.95).shift(origin)]
  elif self.sid=='16':
   for shift,c in [(np.array([-.35,.35,0]),'#A8C2CD'),(np.array([.35,-.35,0]),'#CDB181')]:
    obj=solid([3.5,.35,.42],[0,0,0],c).rotate(PI/4,axis=OUT).shift(origin+shift);objs.append(obj)
  elif self.sid=='LG06':objs=[bridge().shift(origin)]
  else:
   objs=[bridge().scale(.65).shift(q.pos(-4.8,-.1)),person().scale(.8).shift(q.pos(-1.6,-.1))]
  for obj in objs:self.add(obj)
  if self.sid not in ['10','LG04']:
   for obj in objs:
    guide=bounds(obj);guides.append(guide);self.add(guide)
  if self.sid=='LG06':obb=bounds(objs[0],Y);self.add(obb)
  self.add_fixed_in_frame_mobjects(text('X / Y : 수평 기준 · Z : 위',23,q.v.SECOND).move_to([-3.3,-2.35,0]))
  active=None;metric=None
  def note(s,color=Z):
   nonlocal metric
   if metric:self.remove(metric)
   metric=q.base.fit(text(s,28,color),6.25).move_to([3,-.05,0]);self.add_fixed_in_frame_mobjects(metric)
  def open_arms(body,center,scale,angle=65*DEGREES):
   updates=[UpdateFromFunc(g,lambda box,obj=obj:box.become(bounds(obj))) for obj,g in zip(objs,guides)]
   self.play(Rotate(body[2],angle=-angle,axis=RIGHT,about_point=center+scale*np.array([0,-.49,.67])),Rotate(body[3],angle=angle,axis=RIGHT,about_point=center+scale*np.array([0,.49,.67])),*updates,run_time=2)
  def update_bounds():return [UpdateFromFunc(g,lambda box,obj=obj:box.become(bounds(obj))) for obj,g in zip(objs,guides)]
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   if active:self.remove(active)
   active=q.base.fit(text(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)],29),6.25).move_to([3,1.5,0]);self.add_fixed_in_frame_mobjects(active)
   if self.sid=='10':
    if i==1:note('중심 c · 반지름 r',Y)
    if i==3:note('||p−c|| < r / = r / > r',Y)
    if i==4:note('투영된 픽셀 수와 월드 크기를 구분',YELLOW)
   elif self.sid=='LG04':
    if i==0:open_arms(objs[0],origin,1.0,40*DEGREES)
    if i==1:note('구는 머리만 감싸는 근사',Y)
   elif self.sid=='13':
    if i==0:open_arms(objs[0],origin,1.0)
    if i==2:self.add(head_guide);note('부분별 경계와 전체 경계는 다름',Y)
    if i==3:
     obb=bounds(objs[0],Y);self.add(obb);self.play(Rotate(objs[0],-PI/6,axis=OUT,about_point=origin),Rotate(obb,-PI/6,axis=OUT,about_point=origin),Rotate(head_guide,-PI/6,axis=OUT,about_point=origin),*update_bounds(),run_time=2);note('초록: 물체 축 / 파랑: 고정 월드 축')
    if i==5:note('min / max를 X, Y, Z별로 계산')
   elif self.sid=='LG05':
    if i==1:note('경계에는 지붕 밖 빈 공간도 포함')
    if i==2:note('상자의 꼭짓점이 표면 위일 필요 없음',YELLOW)
   elif self.sid=='16':
    if i==1:note('AABB는 겹침 · 실제 모형은 분리',YELLOW)
    if i==3:note('후보 필터 → 필요한 상세 검사')
   elif self.sid=='LG06':
    if i==0:self.play(Rotate(objs[0],PI/3,axis=OUT,about_point=origin),Rotate(obb,PI/3,axis=OUT,about_point=origin),*update_bounds(),run_time=3)
    if i==1:note('OBB는 함께 회전 · AABB는 축 고정')
    if i==2:self.move_camera(theta=-30*DEGREES,run_time=3);note('월드의 점과 경계는 그대로',Y)
   elif self.sid=='19':
    if i==0:self.move_camera(theta=-30*DEGREES,run_time=3)
    if i==1:self.move_camera(theta=-60*DEGREES,run_time=3)
    if i==2:note('월드 최소·최대 값은 동일',Y)
    if i==3:note('카메라 이동 ≠ 물체 회전',YELLOW)
   elif self.sid=='LG07':
    if i==1:self.play(objs[0].animate.stretch(1.4,2,about_point=origin+np.array([0,0,-.775*.95])),*update_bounds(),run_time=2);note('모형 점들의 높이 변화 → 경계 변화')
    if i==2:note('표면의 점 / 계산용 상자의 꼭짓점')
   elif self.sid=='21':
    if i==0:open_arms(objs[1],q.pos(-1.6,-.1),.8)
    if i==1:note('상자 → 변환 : 빈 공간까지 포함')
    if i==2:note('실제 점 → 변환 → 경계 재계산')
    if i==3:note('한 자세의 경계와 동작 전체 범위 구분',Y)
    if i==4:note('누락 위험과 검사 비용을 함께 판단',YELLOW)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
