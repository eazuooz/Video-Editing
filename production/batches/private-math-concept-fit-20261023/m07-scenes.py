"""Fixed hinges and turntables make intermediate orientation directly visible.
Right-handed, column vectors, Z up. Values belong to our models, not the game.
"""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('part_style',Path(__file__).with_name('m06-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
q=v.q;text=v.text;BG=v.BG;FG=v.FG;YELLOW=v.YELLOW;RULE=v.RULE;X=v.X;Y=v.Y;Z=v.Z;base=v.base

def door(origin,scale=1):
 g=VGroup()
 g.add(Cube(side_length=1,fill_color='#5D8598',fill_opacity=1,stroke_color='#B5CCD2',stroke_width=.6).stretch(1.65,0).stretch(.12,1).stretch(2.4,2).shift([.825,0,0]))
 for zz in [-.6,.6]:
  g.add(Cube(side_length=1,fill_color='#739AAD',fill_opacity=1,stroke_color='#A1BCC8',stroke_width=.6).stretch(1.25,0).stretch(.05,1).stretch(.8,2).shift([.82,-.085,zz]))
 g.add(Sphere(radius=.09,resolution=(6,8),fill_color=YELLOW).shift([1.4,-.19,-.05]))
 g.add(Arrow3D(np.array([0,-.16,0]),np.array([1.95,-.16,0]),color=X,thickness=.022,height=.12,base_radius=.06))
 g.scale(scale,about_point=ORIGIN).shift(origin);return g

def hinge(origin,scale=1):
 return VGroup(Cylinder(radius=.055,height=2.65*scale,direction=OUT,resolution=(6,8),fill_color=YELLOW,checkerboard_colors=[YELLOW,YELLOW]).move_to(origin),DashedLine(origin,origin+2.4*scale*RIGHT,color=RULE))

def arc(origin,scale=1):
 ts=np.linspace(0,PI/2,40);points=[origin+np.array([1.4*scale*np.cos(t),1.4*scale*np.sin(t),-.05*scale]) for t in ts]
 return VMobject(stroke_color=Z,stroke_width=4).set_points_as_corners(points)

TITLES={'01':'두 자세 사이 · 경로와 속도','02':'닫힌 문과 열린 문 사이','IB03':'네 숫자를 섞으면 중간 자세가 될까?','IG01':'경첩은 고정 · 자세만 변경','05':'같은 끝 자세, 다른 회전 이력','IG10':'물체 크기와 저장값의 단위 길이','08':'순간 전환 / 중간 자세','IB09':'90° 회전을 네 구간으로','IG02':'같은 경로라도 도착 시각은 다르다','11':'열린 각도와 열리는 속도','IG07':'한 바퀴 더 돌아 같은 자세로','14':'물체의 앞쪽과 위쪽을 함께'}
PHRASES={
'01':['두 자세 사이의 중간 자세','문 열림 → 짧은 경로와 속도','다음 편: 같은 자세의 표현 변환','작은 각도 예제로 검산'],
'02':['닫힌 문 → 회전 → 열린 문','끝 자세가 맞아도 중간은 별개','고정된 경첩 / 호를 그리는 손잡이','게임의 내부 보간 함수는 미확인','이동과 경첩 회전을 구분','위치와 카메라는 고정'],
'IB03':['네 성분을 섞어도 단위 길이일까?'],
'IG01':['경첩 고정 · 0°에서90°로','빨간 문 방향 / 파란 손잡이 경로','t=0.5 → 우리 예제에서45°'],
'05':['자유롭게 회전하는 회전판','끝 자세로 경로 전체를 알 수 없음','입력 두 자세 사이에서 경로를 선택','위치 이동과 자세 보간은 별개','같은 끝 자세 / 다른 누적 회전량','다음: 단위 구면의 호'],
'IG10':['문이 돌아도 물체 크기는 그대로','네 성분 제곱의 합 = 1','단위 길이: 저장값의 조건','화면 선 길이·이동 거리와 구분'],
'08':['방문도 경첩을 중심으로 회전','순간 전환 / 연속 중간 자세','t로 중간 회전을 선택','가로 방향과 위쪽을 함께','정확한 각도는 우리 모형에서 정의','다음: 90°의1/4과1/2'],
'IB09':['고정된Z축 · 90°의 중간 자세'],
'IG02':['같은 두 문 · 중간 자세 비교','현재 자세 ≠ 도착 시각','같은 끝 자세라도 중간 속도는 다름'],
'11':['얼마나 열렸나 / 얼마나 빨리 열리나','각도는 한 순간 · 속도는 시간 변화','같은 시간 간격에서각도 차이 비교','각도° / 각속도°/s','카메라 고정 · 경첩 기준으로 비교','시간 함수가 달라지면속도도 변화'],
'IG07':['빨간 방향 표시를 관찰','현재 자세와 회전 이력은 별개','한 바퀴를 더 돌아 같은 앞 방향','끝 자세 하나에회전 수는 저장되지 않음'],
'14':['앞면 표시와 위쪽 축','앞 방향과 기울기가 전체 자세를 결정','목표 자세 ≠ 모든 중간 동작','우리 모형에서 직접 정의한 축·각도','앞은 같아도위쪽은 달라질 수 있음','편집 / 벡터 적용에맞는 표현 선택','다음: 표현 사이에같은 자세 전달']}

class Replacement(ThreeDScene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG;self.set_camera_orientation(phi=65*DEGREES,theta=-52*DEGREES,zoom=.85)
  self.add_fixed_in_frame_mobjects(text(TITLES[self.sid],36,YELLOW).to_corner(UL,buff=.5),text('우리 모형 · 오른손 / 열벡터 / Z 위',19,q.v.SECOND).to_corner(UR,buff=.5))
  paired=self.sid in ['05','08','IG02','11','IG07'];platform=self.sid in ['05','IG07','14']
  size=.68 if paired else 1.18
  origins=[q.pos(-5.15,-.1),q.pos(-2.05,-.1)] if paired else [q.pos(-4.1,-.1)]
  objs=[]
  for o in origins:
   if platform:
    self.add(Cylinder(radius=1.3*size,height=.15,direction=OUT,resolution=(6,16),fill_color='#263944',checkerboard_colors=['#263944','#263944']).move_to(o+1.0*size*IN))
    obj=v.rig(o,scale=size)
   else:
    self.add(hinge(o,size),arc(o,size));obj=door(o,size)
   objs.append(obj);self.add(obj)
  labels={'05':['+90°','+450°'],'08':['끝 자세로 즉시','중간 자세를 거쳐'],'IG02':['t = 시간 비율','t = 시간 비율²'],'11':['일정한 각속도','늘어나는 각속도'],'IG07':['+90°','+450°']}
  if paired:
   for x,label,c in zip([-4.7,-1.5],labels[self.sid],[Y,Z]):self.add_fixed_in_frame_mobjects(text(label,23,c).move_to([x,-2.05,0]))
  else:self.add_fixed_in_frame_mobjects(text('경첩: 고정 / 빨강: 문 방향 / 파랑: 경로' if not platform else 'X 앞 / Y 옆 / Z 위',22,q.v.SECOND).move_to([-3.0,-2.35,0]))
  active=None;metric=None
  def note(s):
   nonlocal metric
   if metric:self.remove(metric)
   metric=base.fit(text(s,27,Y),6.3).move_to([3,-.1,0]);self.add_fixed_in_frame_mobjects(metric)
  def turn(a=PI/2,idx=0,dt=1.6,axis=OUT):self.play(Rotate(objs[idx],a,axis=axis,about_point=origins[idx]),run_time=dt,rate_func=linear)
  def compare_speed(dt=3):
   self.play(Rotate(objs[0],PI/2,axis=OUT,about_point=origins[0],rate_func=linear),Rotate(objs[1],PI/2,axis=OUT,about_point=origins[1],rate_func=lambda t:t*t),run_time=dt)
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   if active:self.remove(active)
   active=base.fit(text(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)],29,FG),6.35).move_to([3,1.5,0]);self.add_fixed_in_frame_mobjects(active)
   if self.sid in ['01','02']:
    if i==0:turn()
    if self.sid=='02' and i==2:turn(-PI/4);note('경첩 위치는 그대로 · 문 각도만 변경')
   elif self.sid=='IB03':
    if i==0:turn(PI/4);note('물체 회전과 저장값 보간을 구분')
   elif self.sid=='IG01':
    if i==0:turn()
    if i==2:turn(-PI/4);note('t=0.5 · θ=45°')
   elif self.sid=='05':
    if i==0:
     self.play(Rotate(objs[0],PI/2,axis=OUT,about_point=origins[0]),Rotate(objs[1],5*PI/2,axis=OUT,about_point=origins[1]),run_time=3,rate_func=linear)
    if i==1:note('최종 두 자세는 같음 · 경로는 다름')
    if i==3:self.play(objs[0].animate.shift(.3*RIGHT),run_time=1.2);origins[0]+=.3*RIGHT;note('위치만 이동 · 자세 그대로')
   elif self.sid=='IG10':
    if i==0:turn()
    if i==1:note('||q||² = w² + x² + y² + z² = 1')
   elif self.sid=='08':
    if i==1:
     objs[0].rotate(PI/2,axis=OUT,about_point=origins[0]);turn(idx=1);note('같은 시작과 끝 · 다른 중간 과정')
    if i==3:
     for obj,o in zip(objs,origins):self.add(Arrow3D(o,o+1.8*size*OUT,color=Z,thickness=.022,height=.12,base_radius=.06))
   elif self.sid=='IB09':
    if i==0:turn(PI/8);note('t=0.25 → 22.5°')
   elif self.sid in ['IG02','11']:
    if (self.sid=='IG02' and i==0) or (self.sid=='11' and i==2):compare_speed()
    if self.sid=='11' and i==3:note('Δθ / Δ시간 · 각도와 각속도는 별개')
   elif self.sid=='IG07':
    if i==0:turn(idx=0)
    if i==2:turn(5*PI/2,idx=1,dt=2.5);note('같은 끝 자세 · 다른 누적 회전량')
   elif self.sid=='14':
    if i==1:turn(PI/4)
    if i==4:
     axis=rotation_matrix(PI/4,OUT)@RIGHT;turn(PI/3,axis=axis);note('앞 방향 유지 · 위쪽 방향 변화')
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
