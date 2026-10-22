"""Only the revised observation passages. Unchanged approved Unity/math clips are reused."""
from pathlib import Path
import importlib.util,json,os
spec=importlib.util.spec_from_file_location('retained_math_style',Path(__file__).with_name('m03-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
from manim import *
import numpy as np
base=v.base;text=v.text;BG=v.BG;FG=v.FG;X=v.X;Y=v.Y;Z=v.Z;YELLOW=v.YELLOW;RULE=v.RULE
def pos(x,y):
 phi,theta=64*DEGREES,-48*DEGREES
 right=np.array([-np.sin(theta),np.cos(theta),0.]);up=np.array([-np.cos(phi)*np.cos(theta),-np.cos(phi)*np.sin(theta),np.sin(phi)])
 return (x*right+y*up)/.85
def rod(n,a):
 n=np.array(n,dtype=float);n/=np.linalg.norm(n);K=np.array([[0,-n[2],n[1]],[n[2],0,-n[0]],[-n[1],n[0],0]])
 return np.eye(3)*np.cos(a)+(1-np.cos(a))*np.outer(n,n)+np.sin(a)*K
TITLES={'01':'회전은 각도·축·순서를 함께 기록','02':'조립 물체의 회전을 나눠 보기','05':'물체 축과 고정축','08':'돌아간 앞쪽 주위의 비틀림','11':'화면의 수직 ≠ 짐벌락','14':'목표 방향과 회전 경로','17':'같은 끝 자세 · 서로 다른 경로','20':'이동 거리와 회전량은 다른 정보','23':'두 회전의 합성 ≠ 벡터의 합'}
PHRASES={
 '01':['같은 각도, 다른 순서','세 회전과 움직이는 축','짐벌락과 보간','축·각 / 회전벡터 / 두 문제'],
 '02':['고리의 열린 쪽을 따라가기','옆으로 돌리기 / 위아래 기울이기','앞쪽 주위로 비틀기','Heading · Pitch · Bank','화면 축 ≠ 물체 축','다음: 축과 회전 규약'],
 '05':['물체의 앞과 위를 정한다','물체에 붙인 축은 함께 회전','점선: 고정축 / 실선: 물체 축','카메라는 먼저 고정','이름만으로 축은 정해지지 않는다','앞 화살표 + 위 화살표','다음 회전의 기준축 비교','좌표계와 축을 함께 기록'],
 '08':['앞쪽을 돌린 뒤 그 앞쪽으로 비틀기','앞쪽 축도 월드에서 달라진다','고정축 / 이미 돌아간 물체 축','축과 순서가 결과를 정한다','우리 좌표계로 계산한 모형','다음: 같은 자세, 다른 세 각'],
 '11':['물체의 자세 고정 · 관찰 위치 변경','화면의 수직만으로 판단 불가','카메라와 회전 표현을 구분','인상과 축의 겹침은 다른 증거','정한 Euler 순서의 조건 검사','실제 관찰과 수학 모델을 연결'],
 '14':['타일을 돌려 주변과 맞추기','목표 방향 / 도는 경로','가까운 두 방향 사이의 두 경로','+340° 대신 −20°','게임 내부 구현 추정이 아닌 자체 계산','다음: 세 각을 따로 보간하면?'],
 '17':['같은 시작 · 같은 끝 · 다른 경로','끝 화면만으로 회전 이력은 모른다','자세 저장 / 경로 제어','중간 자세도 설계','한 축을 골라 한 번에 표현','다음: 축·각 표현'],
 '20':['붙인 고리를 들어 레일에 걸기','회전벡터 ≠ 이동 경로','방향: 회전축 / 길이: 회전각','화면의 화살표 ≠ 내부 회전벡터','위치 / 앞쪽 / 회전벡터','판과 고리의 접점을 기준점으로','회전량과 이동 거리는 다른 기록','다음: 같은 자세의 중복 표현'],
 '23':['회전을 순서대로 적용','자세와 그 사이의 변화','회전의 합성 / 벡터 성분의 합','기준축과 순서를 지정','정확한 합성 / 작은 각도 근사','다음: 회전량과 각속도']}
class Replacement(ThreeDScene):
 sid=''
 def construct(self):
  slot=next(x for x in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if x['id']==self.sid)
  self.camera.background_color=BG;self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  self.add_fixed_in_frame_mobjects(text(TITLES[self.sid],38,YELLOW).to_corner(UL,buff=.5),text('우리 구현 · 오른손 / 열벡터',20,v.SECOND).to_corner(UR,buff=.5))
  origin=pos(-3.35,-.2);objects=[];origins=[];notes=None;active=None
  if self.sid=='01':
   cards=VGroup(*[base.card(s,2.95,26,Z) for s in ['세 각과 축','회전 순서','짐벌락·보간','축·각과 실습']]).arrange(RIGHT,buff=.18).move_to([0,0,0]);self.add_fixed_in_frame_mobjects(cards)
  elif self.sid=='14':
   center=np.array([-3.4,0,0]);circle=Circle(radius=1.6,color=RULE).move_to(center);a=-170*DEGREES;b=170*DEGREES
   start=center+1.6*np.array([np.cos(a),np.sin(a),0]);end=center+1.6*np.array([np.cos(b),np.sin(b),0])
   hexagon=RegularPolygon(n=6,radius=.50,fill_color=Y,fill_opacity=.25,stroke_color=Y).move_to(center)
   self.add_fixed_in_frame_mobjects(circle,hexagon,Arrow(center,start,buff=0,color=Z),Arrow(center,end,buff=0,color=Y),text('−170°',24,Z).move_to([-5,-1.2,0]),text('+170°',24,Y).move_to([-5,1.2,0]))
  else:
   paired=self.sid in ['05','17','23'];origins=[pos(-4.6,-.25),pos(-1.55,-.25)] if paired else [origin]
   for o in origins:
    obj=v.rig(np.eye(3),o,'hook');obj.scale(.70 if paired else 1,about_point=o)
    world=VGroup(*[DashedLine(o-1.8*base.P[:,j],o+2.1*base.P[:,j],color=RULE,stroke_width=1.8) for j in range(3)])
    self.add(world,obj);objects.append(obj)
   if paired:
    labels={'05':['고정축 기준','물체 축 기준'],'17':['+90°','−270°'],'23':['X90° 후 Y90°','회전벡터 성분 합']}[self.sid]
    for px,label,color in zip([-4.6,-1.55],labels,[Y,Z]):self.add_fixed_in_frame_mobjects(base.fit(text(label,24,color),3).move_to([px,-2.1,0]))
   else:self.add_fixed_in_frame_mobjects(VGroup(text('X',27,X),text('Y ↑',27,Y),text('Z 앞',27,Z)).arrange(RIGHT,buff=.4).move_to([-3.3,-2.3,0]))
   if self.sid=='20':
    board=Cube(side_length=1,fill_color='#8D765D',fill_opacity=1,stroke_width=.6).stretch(2.3,0).stretch(.12,1).stretch(1.5,2);board.apply_matrix(base.P);board.shift(origin-base.P[:,1]);objects[0].add(board)
  orientations={id(obj):np.eye(3) for obj in objects}
  def rotation(obj,o,matrix):
   delta=matrix@orientations[id(obj)].T
   angle=float(np.arccos(np.clip((np.trace(delta)-1)/2,-1,1)))
   if angle<1e-8:axis=np.array([0.,1.,0.])
   elif abs(angle-PI)<1e-6:
    vals,vecs=np.linalg.eigh((delta+np.eye(3))/2);axis=vecs[:,np.argmax(vals)]
   else:axis=np.array([delta[2,1]-delta[1,2],delta[0,2]-delta[2,0],delta[1,0]-delta[0,1]])/(2*np.sin(angle))
   orientations[id(obj)]=matrix.copy()
   return Rotate(obj,angle=angle,axis=base.P@axis,about_point=o)
  def rotate(obj,o,matrix,duration=1):self.play(rotation(obj,o,matrix),run_time=duration)
  def note(label,color=Z):
   nonlocal notes
   if notes:self.remove(notes)
   notes=base.fit(text(label,26,color),6.3).move_to([3,-.4,0]);self.add_fixed_in_frame_mobjects(notes)
  events=[(t,'line',i) for i,t in enumerate(slot['lineStarts'])]
  if self.sid=='02':events.extend([(7.6,'game-turn',0),(11.1,'model-tilt',0)])
  if self.sid=='20':events.extend([(1.1,'lift',0),(4.1,'carry',0),(7.7,'lower',0)])
  for ts,kind,i in sorted(events,key=lambda e:e[0]):
   if ts>self.renderer.time:self.wait(ts-self.renderer.time)
   if kind=='game-turn':rotate(objects[0],origin,base.ry(PI/2),.7);continue
   if kind=='model-tilt':rotate(objects[0],origin,base.ry(PI/2)@base.rx(PI/6),1.2);continue
   if kind=='lift':self.play(objects[0].animate.shift(.6*base.P[:,1]),run_time=1.0);continue
   if kind=='carry':self.play(objects[0].animate.shift(.8*base.P[:,0]),run_time=1.3);continue
   if kind=='lower':self.play(objects[0].animate.shift(-.6*base.P[:,1]),run_time=1.0);continue
   if active:self.remove(active)
   active=base.fit(text(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)],29,FG),12 if self.sid=='01' else 6.5).move_to([0 if self.sid=='01' else 3,1.5,0]);self.add_fixed_in_frame_mobjects(active)
   if self.sid=='01':self.play(Indicate(cards[min(i,3)],color=YELLOW),run_time=.6)
   elif self.sid=='02':
    # Keep the actual game's single turn aligned; show the added tilt after the cut.
    if i==2:rotate(objects[0],origin,base.ry(PI/2)@base.rx(PI/6)@base.rz(PI/4),1.2)
    if i==3:note('R = Ry(h) Rx(p) Rz(b)')
   elif self.sid=='05':
    if i==0:
     self.play(*[rotation(obj,o,base.ry(PI/4)) for obj,o in zip(objects,origins)],run_time=1.2)
    if i==2:
     matrices=[base.rx(PI/4)@base.ry(PI/4),base.ry(PI/4)@base.rx(PI/4)]
     self.play(*[rotation(obj,o,m) for obj,o,m in zip(objects,origins,matrices)],run_time=1.4)
    if i==4:note('world X / body X',YELLOW)
    if i==6:note('Rx Ry ≠ Ry Rx',Y)
   elif self.sid=='08':
    if i==0:rotate(objects[0],origin,base.ry(PI/4),1.1)
    if i==1:rotate(objects[0],origin,base.ry(PI/4)@base.rz(PI/3),1.4)
    if i==2:note('body z = Ry(45°) (0,0,1)',Z)
   elif self.sid=='11':
    if i==0:self.move_camera(phi=22*DEGREES,theta=-48*DEGREES,run_time=2.1)
    if i==1:self.move_camera(phi=64*DEGREES,theta=-8*DEGREES,run_time=1.5)
    if i==4:note('검사 대상: 정한 회전 순서의 축',Y)
   elif self.sid=='14':
    if i==2:
     red=Arc(radius=1.8,start_angle=-170*DEGREES,angle=340*DEGREES,color=X,stroke_width=6).shift(center);green=Arc(radius=1.67,start_angle=-170*DEGREES,angle=-20*DEGREES,color=Y,stroke_width=7).shift(center)
     self.add_fixed_in_frame_mobjects(red,green);self.play(Create(red),Create(green),run_time=1.5);note('동일한 끝 방향 · 다른 회전량',Y)
    if i==3:note('wrap(+340°) = −20°',Y)
   elif self.sid=='17':
    if i==0:self.play(Rotate(objects[0],angle=PI/2,axis=base.P[:,1],about_point=origins[0]),Rotate(objects[1],angle=-3*PI/2,axis=base.P[:,1],about_point=origins[1]),run_time=2.5,rate_func=linear)
    if i==2:note('끝 자세는 같아도 경로는 다르다',Y)
   elif self.sid=='20':
    if i==1:note('이동 경로 ≠ 회전벡터',YELLOW)
    if i==2:
     axis=base.arrow(origin-1.5*base.P[:,1],origin+2.2*base.P[:,1],YELLOW,5);self.play(Create(axis),run_time=.7);note('e = θ n · 각도 단위 명시',Z)
    if i==5:
     point=Dot3D(origin+.8*base.P[:,0]-base.P[:,1],radius=.10,color=YELLOW);self.add(point);note('기준점의 위치 / 열린 방향',Y)
   elif self.sid=='23':
    if i==0:
     rotate(objects[0],origins[0],base.rx(PI/2),.8);rotate(objects[0],origins[0],base.ry(PI/2)@base.rx(PI/2),.8)
    if i==2:rotate(objects[1],origins[1],rod([1,1,0],PI/np.sqrt(2)),1.4);note('두 결과의 축 방향이 다르다',X)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
