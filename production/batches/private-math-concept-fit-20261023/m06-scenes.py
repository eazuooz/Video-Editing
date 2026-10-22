"""M06: observed assembly, then defined-coordinate rotation calculations.

Reuse the prior lecture's mathematical renderer and coordinate convention:
right-handed, column vectors, X front, Y side, Z up. No measured game pose.
"""
from pathlib import Path
import importlib.util, json, os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('quaternion_style',Path(__file__).with_name('m05-scenes.py'))
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
text=q.text;BG=q.BG;FG=q.FG;X=q.X;Y=q.Y;Z=q.Z;YELLOW=q.YELLOW;RULE=q.RULE;base=q.base

def part(origin,scale=1):
 g=VGroup()
 # A recognizable assembly module: twin tubes, housing, rails and connector.
 for y in [-.39,.39]:
  g.add(Cylinder(radius=.27,height=1.85,direction=RIGHT,resolution=(8,12),fill_color='#607D91',checkerboard_colors=['#607D91','#607D91'],fill_opacity=1,stroke_width=.5).shift([.15,y,0]))
  g.add(Cylinder(radius=.19,height=.12,direction=RIGHT,resolution=(6,12),fill_color='#202C36',checkerboard_colors=['#202C36','#202C36'],fill_opacity=1,stroke_width=.5).shift([1.13,y,0]))
 for x in [-.7,.65]:
  g.add(Cube(side_length=1,fill_color='#A4B3BD',fill_opacity=1,stroke_width=.5).stretch(.13,0).stretch(1.4,1).stretch(.18,2).shift([x,0,-.3]))
 g.add(Cube(side_length=1,fill_color='#D5B459',fill_opacity=1,stroke_width=.7).stretch(.35,0).stretch(.65,1).stretch(.48,2).shift([-.9,0,.2]))
 g.scale(scale);g.shift(origin);return g

def rig(origin,shape='part',scale=1):
 obj=(q.plane if shape=='plane' else part)(origin,scale)
 axes=VGroup(*[Arrow3D(origin,origin+2.05*scale*np.eye(3)[:,i],color=c,thickness=.022,height=.16,base_radius=.065) for i,c in enumerate([X,Y,Z])])
 return VGroup(obj,axes)

TITLES={'F03':'회전을 이어 붙이고 목표 자세에 도달하기','QC00':'부품의 방향과 계산 결과','B14':'역원: 회전만 상쇄하기','14':'회전과 이동을 나누어 되돌리기','GB06':'두 회전을 더할까, 곱할까?','GB01':'월드의 고정 축 / 물체에 붙은 축','QC10':'위치는 고정 · 회전 순서만 변경','17':'같은 두 회전 · 다른 결과','GB02':'현재 A에서 목표 B까지','QC20':'부품의 앞면을 목표 방향으로','GB03':'최소 자세 차이 ≠ 동작 전체','B20':'목표 위치와 목표 자세','20':'놓을 자리와 놓을 자세를 따로 정하기','GB04':'같은 축에서 회전량 절반','GB05':'방향 벡터를 물체에 붙여 읽기','QC30':'부품에 붙은 방향을 계산','QC31':'회전은 방향을 바꾸고 길이는 보존','B23':'물체의 방향과 카메라 기준','23':'물체는 고정 · 카메라만 이동','GB07':'두 자세 사이의 중간 자세'}
PHRASES={
 'F03':['역원에서 합성으로','순서 → 목표 자세 → 벡터 검산','위치와 자세를 분리'],
 'QC00':['현재 방향 → 회전 → 결과 방향'],
 'B14':['회전만 되돌리고 위치는 유지'],
 '14':['두 둥근 면과 긴 몸체를 관찰','위치와 방향을 각각 맞추기','정확한 축·각도는 우리 모형에서 정의','역회전 ≠ 경로 역주행','옮긴 위치에서 기울기만 복원','다음: 회전 순서와 기준 공간'],
 'GB06':['앞: X / 위: Z','기울기와 앞 방향을 같이 변경','내적·외적 → 해밀턴 곱'],
 'GB01':['돌아간 물체 축과 고정 기준선','월드 X / 현재 몸체 X 비교','월드: 왼쪽 곱 / 몸체: 오른쪽 곱','현재에서 목표까지'],
 'QC10':['기수와 날개를 함께 관찰','카메라·위치는 고정, 순서만 변경'],
 '17':['동일한 부품 두 개','첫 회전이 몸체의 다음 축도 회전','첫 번째 → 두 번째 회전','고정 축과 몸체 축을 구분','우리 모형에서 정한 축과 순서','앞면과 위쪽을 함께 비교'],
 'GB02':['자세와 위치는 별개','현재 A / 목표 B','D A = B → D = B A⁻¹'],
 'QC20':['현재 방향에서 목표 방향으로'],
 'GB03':['최소 각도는 끝 자세의 차이','회전 이력은 별도 기록','끝 자세와 누적 각도를 구분','+90° / +450° → 같은 끝 자세','다음: 회전량 절반'],
 'B20':['남은 거리와 자세 차이를 별도 계산'],
 '20':['목표 위치 / 목표 자세','목표 자세가 달라지면 필요한 회전도 변화','위치 거리와 회전 차이는 다른 값','정확한 각도는 정의된 회전 데이터로','최소 각도 ≠ 지나온 경로의 길이','앞면과 위쪽을 함께 관찰','다른 경로도 같은 끝 자세에 도달','회전 연산은 충돌·이동 경로를 되감지 않음','다음: 일부 회전량 적용'],
 'GB04':['같은 축에서 회전량 조절','90°와 45° 비교','성분 전체에 0.5를 곱하지 않는다','qᵗ = exp(t log q)'],
 'GB05':['앞 방향과 위 방향을 함께','월드 계산과 카메라 화면 구분'],
 'QC30':['계산한 방향을 물체에 붙여 읽기'],
 'QC31':['Z축으로 90° 회전','√2 → √2 · 길이 보존'],
 'B23':['X 성분은 Y로, Z 성분은 유지','물체에 붙은 방향 관찰','카메라 기준과 분리'],
 '23':['물체의 위치·자세는 그대로','카메라만 이동 → 화면 모습은 변화','보기 좋은 화면과 자세 계산은 별개','앞쪽·위쪽 방향을 회전값으로 계산','우리 모형에서 직접 정의한 값','성분 순서·단위 길이를 연습문제로'],
 'GB07':['두 끝 자세 사이','중간 자세는 어떻게 만들까?']}

class Replacement(ThreeDScene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG;self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  self.add_fixed_in_frame_mobjects(text(TITLES[self.sid],37,YELLOW).to_corner(UL,buff=.5),text('우리 모형 · 오른손 / 열벡터',20,q.v.SECOND).to_corner(UR,buff=.5))
  paired=self.sid in ['GB01','QC10','17','GB03','GB04','GB07']
  origins=[q.pos(-4.65,-.15),q.pos(-1.55,-.15)] if paired else [q.pos(-3.35,-.15)]
  size=.72 if paired else 1.22;shape='plane' if self.sid=='QC10' else 'part'
  objs=[rig(o,shape,size) for o in origins];rot=[np.eye(3) for o in origins]
  for o,obj in zip(origins,objs):
   self.add(VGroup(*[DashedLine(o-1.9*size*np.eye(3)[:,j],o+2.3*size*np.eye(3)[:,j],color=RULE,stroke_width=1.4) for j in range(3)]),obj)
  self.add_fixed_in_frame_mobjects(VGroup(text('X 앞',25,X),text('Y 옆',25,Y),text('Z 위',25,Z)).arrange(RIGHT,buff=.25).move_to([-3.2,-2.35,0]))
  active=None;metric=None;vector=None
  def note(s,color=Z):
   nonlocal metric
   if metric:self.remove(metric)
   metric=base.fit(text(s,27,color),6.35).move_to([3,-.1,0]);self.add_fixed_in_frame_mobjects(metric)
  def turn(angle,axis=OUT,duration=1.25,index=0,body=False):
   world_axis=rot[index]@axis if body else axis
   self.play(Rotate(objs[index],angle=angle,axis=world_axis,about_point=origins[index]),run_time=duration)
   rot[index]=rotation_matrix(angle,world_axis)@rot[index]
  def order_compare():
   # Intrinsic/body axes: Z then X gives Rz Rx; X then Z gives Rx Rz.
   turn(PI/2,OUT,index=0,body=True);turn(PI/2,RIGHT,index=1,body=True)
   note('첫 회전: 왼쪽 Z / 오른쪽 X',Y)
   turn(PI/2,RIGHT,index=0,body=True);turn(PI/2,OUT,index=1,body=True)
   note('몸체축: Rz Rx ≠ Rx Rz',Y)
  if paired:
   names={'GB01':['월드 X로 추가','몸체 X로 추가'],'QC10':['몸체 Z → X','몸체 X → Z'],'17':['몸체 Z → X','몸체 X → Z'],'GB03':['+90° 경로','+450° 경로'],'GB04':['90°','45°'],'GB07':['시작 자세','목표 자세']}[self.sid]
   for x,label,c in zip([-4.65,-1.55],names,[Y,Z]):self.add_fixed_in_frame_mobjects(text(label,23,c).move_to([x,-1.9,0]))
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   if active:self.remove(active)
   active=base.fit(text(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)],29,FG),6.35).move_to([3,1.5,0]);self.add_fixed_in_frame_mobjects(active)
   if self.sid in ['F03','QC00','B14']:
    if i==0:turn(PI/4,RIGHT)
    if self.sid=='F03' and i==2:turn(-PI/4,RIGHT)
   elif self.sid=='14':
    if i==0:turn(PI/4,RIGHT)
    if i==1:self.play(objs[0].animate.shift(.7*RIGHT),run_time=1.3);origins[0]+=.7*RIGHT
    if i==3:turn(-PI/4,RIGHT);note('회전 상쇄 · 옮긴 위치 유지',Y)
   elif self.sid=='GB06':
    if i==1:turn(PI/4,RIGHT);turn(PI/2,OUT);note('월드 X → Z : qZ qX',Y)
   elif self.sid=='GB01':
    if i==0:
     turn(PI/2,OUT,index=0);turn(PI/2,OUT,index=1)
    if i==1:
     turn(PI/4,RIGHT,index=0);turn(PI/4,RIGHT,index=1,body=True)
    if i==2:note('qX q현재 / q현재 qX',Y)
   elif self.sid=='QC10' and i==1:order_compare()
   elif self.sid=='17':
    if i==1:
     turn(PI/2,OUT,index=0,body=True);turn(PI/2,RIGHT,index=1,body=True)
    if i==2:
     turn(PI/2,RIGHT,index=0,body=True);turn(PI/2,OUT,index=1,body=True);note('Rz Rx ≠ Rx Rz',Y)
   elif self.sid in ['GB02','B20','20']:
    if i==0:note('현재 pA, A / 목표 pB, B',Y)
    if self.sid=='GB02' and i==2:turn(PI/2);note('월드 추가 회전 D = B A⁻¹',Y)
    if self.sid=='20' and i==1:turn(PI/2);note('정한 목표 B: Z축 +90°',Y)
    if self.sid=='20' and i==2:self.play(objs[0].animate.shift(.65*RIGHT),run_time=1.3);origins[0]+=.65*RIGHT;note('위치만 이동 · 자세 B 유지',Y)
    if self.sid=='20' and i==6:turn(TAU,OUT,3);note('한 바퀴를 더 돌아도 같은 B',Y)
   elif self.sid=='QC20' and i==0:turn(PI/2,OUT,1.5)
   elif self.sid=='GB03':
    if i==1:turn(TAU,OUT,2.3)
    if i==3:
     self.play(Rotate(objs[0],angle=PI/2,axis=OUT,about_point=origins[0]),Rotate(objs[1],angle=5*PI/2,axis=OUT,about_point=origins[1]),run_time=3,rate_func=linear);note('같은 끝 자세 · 이력은 별도',Y)
   elif self.sid=='GB04':
    if i==1:turn(PI/2,index=0);turn(PI/4,index=1);note('θ = 90° / θ/2 = 45°',Y)
    if i==2:note('0.5q는 단위 쿼터니언이 아님',Y)
   elif self.sid in ['GB05','QC30']:
    if i==0:turn(PI/2);note('앞 X → Y / 위 Z → Z',Y)
   elif self.sid=='QC31':
    if i==0:
     vector=Arrow3D(origins[0],origins[0]+1.5*np.array([1,0,1]),color=YELLOW,thickness=.032,height=.17,base_radius=.07);self.add(vector)
     self.play(Rotate(vector,PI/2,axis=OUT,about_point=origins[0]),Rotate(objs[0],PI/2,axis=OUT,about_point=origins[0]),run_time=2);note('(1, 0, 1) → (0, 1, 1)',Y)
    if i==1:note('√(1² + 1²) = √2 · 그대로',Y)
   elif self.sid=='B23':
    if i==0:turn(PI/2);note('X → Y / Z → Z',Y)
   elif self.sid=='23':
    if i==0:self.move_camera(theta=-32*DEGREES,run_time=3)
    if i==1:self.move_camera(theta=-60*DEGREES,run_time=3);note('월드 자세 일정 / 카메라만 변화',Y)
   elif self.sid=='GB07':
    if i==0:turn(PI/2,index=1)
    if i==1:turn(PI/4,index=0);note('0° → 45° → 90°',Y)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
