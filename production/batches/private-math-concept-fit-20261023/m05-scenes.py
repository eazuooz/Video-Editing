"""Change only game-dependent passages; retain original quaternion mathematics.

Own illustrative coordinates: RH column vectors, +X front, +Y wing, +Z up.
No commercial game's internal pose, quaternion or velocity is inferred.
"""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('math_style',Path(__file__).with_name('m03-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;FG=v.FG;X=v.X;Y=v.Y;Z=v.Z;YELLOW=v.YELLOW;RULE=v.RULE;base=v.base
def pos(x,y):
 p,t=64*DEGREES,-48*DEGREES
 return (x*np.array([-np.sin(t),np.cos(t),0])+y*np.array([-np.cos(p)*np.cos(t),-np.cos(p)*np.sin(t),np.sin(p)]))/.85
def logs(origin,scale=1):
 g=VGroup()
 for y in [-.44,0,.44]:
  g.add(Cylinder(radius=.21,height=2.7,direction=RIGHT,resolution=(8,12),fill_color='#B58A5A',checkerboard_colors=['#B58A5A','#B58A5A'],fill_opacity=1,stroke_width=.4).shift([0,y,0]))
 for x in [-.7,.7]:
  g.add(Cube(side_length=1,fill_color='#536E77',fill_opacity=1,stroke_width=.5).stretch(.12,0).stretch(1.4,1).stretch(.16,2).shift([x,0,.2]))
 g.scale(scale);g.shift(origin);return g
def plane(origin,scale=1):
 # Convert the reused model's Z-front/Y-up to this lesson's X-front/Z-up.
 conv=np.array([[0,0,1],[1,0,0],[0,1,0]])
 g=v.aircraft(np.eye(3),ORIGIN,1);g.apply_matrix(conv@base.P.T);g.scale(scale);g.shift(origin);return g
def rig(origin,shape='logs',scale=1):
 obj=(plane if shape=='plane' else logs)(origin,scale)
 axes=VGroup(*[Arrow3D(origin,origin+2*scale*np.eye(3)[:,i],color=c,thickness=.022,height=.16,base_radius=.065) for i,c in enumerate([X,Y,Z])])
 return VGroup(obj,axes)
TITLES={'01':'네 숫자로 자세를 기록하고 되돌리기','QF00':'물체의 위치와 전체 자세','B02':'위치와 자세를 따로 기록','02':'통나무를 돌려 다리로 배치하기','GA06':'평면 회전에서 삼차원 회전축으로','GA01':'부품의 위치와 각 면의 방향','GA07':'반각 저장 ≠ 절반만 회전','QF10':'앞 방향은 같아도 자세는 다르다','B05':'물체에 붙은 방향은 함께 회전','05':'물체 전체의 자세를 기록','GA09':'같은 축의 회전을 두 번 적용','QF30':'주변 지도에 맞춰 타일 회전','QF31':'같은 회전은 직각을 보존','B06':'90°를 두 번 적용하면?','GA05':'같은 끝 자세 · 서로 다른 경로','08':'자세 한 개는 회전 이력이 아니다','GA04':'항등 회전과 위치 이동','GA02':'이동 속도와 자세값의 길이','11':'같은 자세 · 서로 다른 이동 속도','GA08':'위치는 그대로 · 기울기만 상쇄','QF20':'부품의 방향과 전체 자세','GA03':'역회전은 이동 경로 되감기가 아니다','GA10':'회전의 역원에서 합성으로'}
PHRASES={
 '01':['물체를 돌리고 배치한다','허수 → 네 성분 → 축과 반각','같은 자세의 두 부호','단위 길이 → 역원'],
 'QF00':['긴 방향과 위쪽을 함께 관찰'], 'B02':['위치와 자세는 별도 정보'],
 '02':['잡은 통나무의 끝을 관찰','위치 변화 / 긴 방향 변화','가까이 옮긴 뒤 방향 맞추기','화면 중심 ≠ 같은 자세','게임 내부 값이 아닌 관찰','정한 좌표계에서 세 축 회전'],
 'GA06':['평면: 하나의 각도','빨간 X축을 기준으로','삼차원: 축도 지정','단위 축의 세 성분'],
 'GA01':['부품을 복사해 배치','앞면과 옆면은 서로 다른 방향','카메라 움직임과 회전축 구분','축과 각도로 네 숫자 만들기'],
 'GA07':['저장식에는 θ/2','전체 작용은 θ = 90°','값과 물체의 자세를 연결'],
 'QF10':['앞: X / 위: Z','기수·날개·위쪽을 구분'],
 'B05':['같은 회전을 세 방향에 적용'],
 '05':['처음 자세 → 돌린 자세','세 축이 함께 회전','긴 방향 + 위쪽 방향','자세는 위치·속도와 별도','자체 모형의 축과 각도','방향 변화와 이동을 구분'],
 'GA09':['앞축과 위쪽 축을 같이 관찰','같은 축으로 한 번 더','90° + 90° = 180°'],
 'QF30':['선택 타일만 돌려 주변과 배치'],
 'QF31':['같은 회전은 두 방향의 직각 보존','모양이 달라도 회전 표현은 공통'],
 'B06':['정한 축에서 90°를 두 번 적용'],
 'GA05':['두 경로, 같은 끝 자세','앞축과 위쪽을 함께 관찰','끝 자세만으로 이력은 모른다','q와 −q는 같은 자세','다음: 추가 회전이 없다면?'],
 '08':['시간에 따라 변하는 세 축','끝 자세에는 과거 동작이 없다','자세와 경로를 구분','q와 −q: 같은 회전 작용','회전 횟수는 별도 기록','누적량은 별도 상태로 저장'],
 'GA04':['끝 자세 ≠ 과거 동작','모형과 기준축','빨강: X 앞','파랑: Z 위','이동해도 두 방향은 유지','항등 회전 ≠ 화면 정지','추가 회전 없이 같은 방향','입력 앞 방향','다음: 항등 쿼터니언'],
 'GA02':['속도와 축 방향을 비교','같은 자세, 다른 속도','속도 증가 ≠ ||q|| 증가','위치 차이 / 같은 자세'],
 '11':['같은 모형, 두 이동 속도','단위 회전값 ||q|| = 1','변화율과 현재 상태 구분','이동 중에도 축 방향 유지','모형의 계산값으로 확인','다음: 적용한 회전 되돌리기'],
 'GA08':['위치와 자세는 별도','옮긴 위치에서 기울기 상쇄','단위 회전의 켤레로 연결'],
 'QF20':['부품의 앞면과 옆면을 함께 관찰'],
 'GA03':['역원은 회전만 상쇄','옮긴 위치는 그대로 남는다','시간·거리 되감기가 아니다','다음: 일반 역원 검산'],
 'GA10':['방향 변화와 이동은 따로','다음: 두 회전의 곱']}
class Replacement(ThreeDScene):
 sid=''
 def construct(self):
  slot=next(x for x in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if x['id']==self.sid)
  self.camera.background_color=BG;self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  self.add_fixed_in_frame_mobjects(text(TITLES[self.sid],37,YELLOW).to_corner(UL,buff=.5),text('우리 모형 · 오른손 / 열벡터',20,v.SECOND).to_corner(UR,buff=.5))
  paired=self.sid in ['GA05','GA02','11'];origins=[pos(-4.65,-.15),pos(-1.55,-.15)] if paired else [pos(-3.35,-.15)]
  shape='plane' if self.sid in ['QF10','GA07','QF31'] else 'logs';size=.62 if paired else .9
  objects=[rig(o,shape,size) for o in origins]
  for o,obj in zip(origins,objects):
   self.add(VGroup(*[DashedLine(o-1.9*size*np.eye(3)[:,j],o+2.3*size*np.eye(3)[:,j],color=RULE,stroke_width=1.4) for j in range(3)]),obj)
  self.add_fixed_in_frame_mobjects(VGroup(text('X 앞',25,X),text('Y 날개',25,Y),text('Z 위',25,Z)).arrange(RIGHT,buff=.25).move_to([-3.2,-2.35,0]))
  if paired:
   for x,label,c in zip([-4.65,-1.55],['+90°','−270°'] if self.sid=='GA05' else ['1 단위/s','2 단위/s'],[Y,Z]):self.add_fixed_in_frame_mobjects(text(label,24,c).move_to([x,-1.9,0]))
  active=None;metric=None
  def note(s,color=Z):
   nonlocal metric
   if metric:self.remove(metric)
   metric=base.fit(text(s,27,color),6.4).move_to([3,-.1,0]);self.add_fixed_in_frame_mobjects(metric)
  def turn(angle,axis=OUT,duration=1.2,index=0):self.play(Rotate(objects[index],angle=angle,axis=axis,about_point=origins[index]),run_time=duration)
  def travel():
   # One common duration, same positive direction, twice the second displacement.
   self.play(objects[0].animate.shift(.45*RIGHT),objects[1].animate.shift(.9*RIGHT),run_time=2.0,rate_func=linear)
   origins[0]=origins[0]+.45*RIGHT;origins[1]=origins[1]+.9*RIGHT
  events=[(t,'line',i) for i,t in enumerate(slot['lineStarts'])]
  if self.sid=='02':events += [(1,'lift',0),(6,'carry',0),(13,'game-turn',0),(16,'place',0)]
  if self.sid=='GA01':events +=[(5,'copy-place',0)]
  if self.sid=='QF30':events +=[(5,'tile-turn',0)]
  for tm,kind,i in sorted(events,key=lambda x:x[0]):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   if kind=='lift':self.play(objects[0].animate.shift(.3*OUT),run_time=1);origins[0]+=.3*OUT;continue
   if kind in ['carry','copy-place']:self.play(objects[0].animate.shift(.7*RIGHT),run_time=1.3);origins[0]+=.7*RIGHT;continue
   if kind=='game-turn':turn(PI/2);continue
   if kind=='place':self.play(objects[0].animate.shift(-.3*OUT),run_time=1);origins[0]-=.3*OUT;continue
   if kind=='tile-turn':turn(PI/3);continue
   if active:self.remove(active)
   active=base.fit(text(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)],29,FG),6.4).move_to([3,1.5,0]);self.add_fixed_in_frame_mobjects(active)
   if self.sid in ['01','QF00','B02','GA06','B05','B06']:
    if i==0:turn(PI/6,RIGHT)
   elif self.sid=='GA07':
    if i==0:note('q = (cos 45°, 0, 0, sin 45°)')
    if i==1:turn(PI/2);note('q (0,v) q⁻¹ → 90°',Y)
   elif self.sid=='QF10':
    if i==0:turn(PI/3,RIGHT,2)
   elif self.sid=='05':
    if i==1:turn(PI/3)
    if i==2:turn(PI/6,RIGHT)
    if i==3:note('位置 p / 자세 q / 속도 v'.replace('位置','위치'),Y)
   elif self.sid=='GA09':
    if i in [0,1]:turn(PI/2)
    if i==2:note('같은 Z축: Rz(90°) Rz(90°)',Y)
   elif self.sid=='QF31':
    if i==0:turn(PI/2);note('Y · Z = 0 → (RY) · (RZ) = 0',Y)
   elif self.sid=='GA05':
    if i==0:self.play(Rotate(objects[0],angle=PI/2,axis=OUT,about_point=origins[0]),Rotate(objects[1],angle=-3*PI/2,axis=OUT,about_point=origins[1]),run_time=3,rate_func=linear)
    if i==3:note('R(q) = R(−q) · 경로는 별도',Y)
   elif self.sid=='08':
    if i==0:turn(2*PI,OUT,3);note('한 바퀴 뒤 같은 자세',Y)
    if i==5:note('자세 q + 별도 누적 각도',Y)
   elif self.sid=='GA04':
    if i==4:self.play(objects[0].animate.shift(.8*RIGHT),run_time=2);origins[0]+=.8*RIGHT
    if i==6:note('v → Ridentity v = v',Y)
   elif self.sid in ['GA02','11']:
    if i==0:travel()
    if i==2:note('q₁ = q₂ = (1,0,0,0) · ||q|| = 1',Y)
   elif self.sid in ['GA08','GA03','GA10']:
    if i==0:turn(PI/4);self.play(objects[0].animate.shift(.7*RIGHT),run_time=1);origins[0]+=.7*RIGHT
    if i==1:turn(-PI/4);note('기울기 복원 · 옮긴 위치 유지',Y)
   elif self.sid=='QF20':
    if i==0:turn(PI/2,UP,.9);turn(-PI/2,UP,.9)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})

class SceneN05(Scene):
 def construct(self):
  slot=next(x for x in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if x['id']=='N05')
  self.camera.background_color=BG
  self.add(text('정규화: 네 성분을 같은 길이로 나누기',37,YELLOW).to_corner(UL,buff=.5),text('우리 계산 · x = y = 0인 예',20,v.SECOND).to_corner(UR,buff=.5))
  axes=Axes(x_range=[0,4,1],y_range=[0,5,1],x_length=3.5,y_length=3.5,tips=False,axis_config={'color':RULE}).move_to([-3.4,-.1,0])
  labels=axes.get_axis_labels(text('w',25,X),text('z',25,Z));origin=axes.c2p(0,0)
  a=Arrow(origin,axes.c2p(3,4),buff=0,color=YELLOW);short=Arrow(origin,axes.c2p(.6,.8),buff=0,color=Y)
  self.add(axes,labels,a,text('네 숫자의 성분 평면 · 공간 회전축이 아님',21,v.SECOND).move_to([-3.4,-2.45,0]))
  math=None
  lines=[['q = (3, 0, 0, 4)','||q|| = √(3² + 4²) = 5'],['q / 5 = (0.6, 0, 0, 0.8)','0.6² + 0.8² = 0.36 + 0.64 = 1'],['모든 성분의 비율은 그대로','잘못 고른 축·순서는 고치지 못한다'],['이동 속도와 자세값의 길이는 별도','다음: 같은 자세를 두 속도로 이동']]
  for i,t in enumerate(slot['lineStarts']):
   if t>self.renderer.time:self.wait(t-self.renderer.time)
   if math:self.remove(math)
   math=VGroup(*[base.fit(text(s,29,Y if i==1 else FG),6.5) for s in lines[i]]).arrange(DOWN,aligned_edge=LEFT,buff=.55).move_to([3,.2,0]);self.add(math)
   if i==1:self.play(Create(short),a.animate.set_opacity(.3),run_time=1.2)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
