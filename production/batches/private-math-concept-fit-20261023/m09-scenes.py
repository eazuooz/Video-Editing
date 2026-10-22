"""Endpoint relationships and paths with explicit, authored 2D coordinates."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('math_style',Path(__file__).with_name('m03-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;FG=v.FG;YELLOW=v.YELLOW;GREEN=v.Y;BLUE=v.Z;RED=v.X;SECOND=v.SECOND
TITLES={'02':'연결에는 두 끝점이 필요하다','LG01':'배선의 모양 / 두 점을 잇는 선분','05':'방향은 같아도 길이는 달라진다','LG02':'연결용 선분 / 실제 이동 경로','LG03':'끝점이 달라도 비율의 규칙은 같다','08':'수직선에서도 쓸 수 있는 표현'}
PHRASES={
'02':['손에서 뻗는 밝은 연결','손 쪽 출발 / 반대쪽 끝','두 점을 정해야 선분이 결정','화면 픽셀 길이 ≠ 게임 속 거리','다음: 정한 좌표로 관계 계산','보이는 연결 ≠ 내부 물리 구현'],
'LG01':['케이블을 잇는 두 연결점','곡선 모양과 직선 연결을 구분','한 끝점 변경 → 차이 벡터 변경'],
'05':['출발점 A 고정 · B만 변경','차이 벡터: 방향 + 길이','같은 방향 · 다른 거리','방향만 쓰려면 길이로 나누기','연결용 선분 ≠ 실제 이동 경로','매개변수: 길이 비율인가, 거리인가?'],
'LG02':['출발점과 연결점','두 점의 관계를 나타내는 선분','움직인 점의 경로는 별도','게임 물리 재현이 아닌 설명 모형'],
'LG03':['새 끝점에 맞춰 차이 벡터 재계산','t=0: A / t=1: B','같은 비율로 새 점 계산','정한 좌표의 예제 · 게임 측정값 아님'],
'08':['B를 위로 · 같은 X 좌표','기울기 표현의 수직선 문제','Δx=0 · Δy/Δx 계산 불가','법선은 선의 방향과 직각','먼저 좌표계를 정의','다음: 같은 거리와 수직이등분선']}
class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG
  self.add(text(TITLES[self.sid],35,YELLOW).to_corner(UL,buff=.5),text('우리 모형 · 정한 2D 좌표',20,SECOND).to_corner(UR,buff=.5))
  origin=np.array([-5.2,-.65,0]);scale=.55
  def pos(xy):return origin+scale*np.array([xy[0],xy[1],0])
  self.add(VGroup(*[Line(pos([x,0]),pos([x,6]),color=v.RULE,stroke_width=.7) for x in range(7)],*[Line(pos([0,y]),pos([6,y]),color=v.RULE,stroke_width=.7) for y in range(7)]).set_opacity(.45))
  a=np.array([1.,1.]);b=np.array([5.,3.]);end=VectorizedPoint(pos(b));self.add(end)
  A=Dot(pos(a),radius=.10,color=GREEN);B=Dot(pos(b),radius=.10,color=BLUE)
  line=always_redraw(lambda:Line(A.get_center(),end.get_center(),color=GREEN,stroke_width=6));B.add_updater(lambda x:x.move_to(end.get_center()))
  la=text('A · 출발',26,GREEN).next_to(A,DOWN,buff=.18);lb=text('B · 끝점',26,BLUE);lb.add_updater(lambda x:x.next_to(B,UP,buff=.18))
  self.add(line,A,B,la,lb)
  self.add(text('기준점과 좌표는 직접 정한 예제',22,SECOND).move_to([-3.5,-1.55,0]))
  active=None;metric=None;curve=None;moving=None
  def note(s,color=GREEN):
   nonlocal metric
   if metric:self.remove(metric)
   metric=v.base.fit(text(s,29,color),6.15).move_to([3,-.1,0]);self.add(metric)
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   if active:self.remove(active)
   active=v.base.fit(text(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)],29),6.15).move_to([3,1.5,0]);self.add(active)
   if self.sid=='02':
    if i==1:note('A와 B를 나누어 확인')
    if i==2:note('A만으로는 B를 알 수 없음',YELLOW)
    if i==4:note('A=(1,1), B=(5,3) → B−A=(4,2)')
   elif self.sid=='LG01':
    if i==0:
     curve=CubicBezier(pos(a),pos(a)+[1,-1,0],pos(b)+[-1,-1,0],pos(b),color=BLUE,stroke_width=5);self.add(curve);note('파랑: 케이블 모양 / 초록: 선분')
    if i==1:note('끝점이 같아도 선의 모양은 다름',YELLOW)
    if i==2:
     if curve:self.play(FadeOut(curve),run_time=.25)
     self.play(end.animate.move_to(pos([4,5])),run_time=1.5);note('B=(4,5) → B−A=(3,4)')
   elif self.sid=='05':
    if i==0:self.play(end.animate.move_to(pos([3,2])),run_time=1.4);note('B−A=(2,1) · 길이 √5')
    if i==2:self.play(end.animate.move_to(pos([5,3])),run_time=1.8);note('B−A=(4,2) · 길이 2√5')
    if i==3:note('단위 방향: (2/√5, 1/√5)')
    if i==4:note('두 점의 관계와 물체의 궤적은 별개',YELLOW)
   elif self.sid=='LG02':
    if i==0:note('초록: A에서 B까지의 선분')
    if i==1:note('연결 관계는 이동 경로를 강제하지 않음',YELLOW)
    if i==2:
     curve=CubicBezier(pos(a),pos(a)+[.4,2.,0],pos(b)+[-.4,2.,0],pos(b),color=BLUE,stroke_width=5);moving=Dot(pos(a),radius=.11,color=YELLOW)
     self.play(Create(curve),FadeIn(moving),run_time=.6);self.play(MoveAlongPath(moving,curve),run_time=3.4,rate_func=linear);note('파랑: 움직인 점의 경로',BLUE)
    if i==3:note('다음: 선분 위의 점을 비율로 정하기')
   elif self.sid=='LG03':
    if i==0:self.play(end.animate.move_to(pos([4,5])),run_time=1.8);note('B=(4,5) · 새 차이 벡터 (3,4)')
    if i==1:note('P(t) = A + t(B−A)')
    if i==2:
     moving=Dot(A.get_center(),radius=.11,color=YELLOW);self.add(moving)
     self.play(moving.animate.move_to((A.get_center()+end.get_center())/2),run_time=1.4);note('t=0.5 → P=(2.5,3)')
     self.wait(.4);self.play(moving.animate.move_to(end.get_center()),run_time=1.4)
    if i==3:note('다음: Δx가 0인 수직선')
   elif self.sid=='08':
    if i==0:self.play(end.animate.move_to(pos([1,5])),run_time=2.5);note('A=(1,1), B=(1,5)')
    if i==2:note('Δx=0, Δy=4 → 4/0 정의 불가',RED)
    if i==3:
     center=(A.get_center()+end.get_center())/2
     self.play(GrowArrow(Arrow(center,center+[1.4,0,0],color=BLUE,buff=0,stroke_width=5)),run_time=1);note('법선 n=(1,0) · 수직선 x=1',BLUE)
    if i==4:note('화면 좌표와 게임 월드 좌표는 구분')
    if i==5:note('두 점에서 같은 거리 → 수직이등분선')
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
