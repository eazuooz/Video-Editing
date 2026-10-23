"""Purpose-matched centers, clearance and ordered boundaries; explicit planar models."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('polygon_style',Path(__file__).with_name('m03-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;FG=v.FG;YELLOW=v.YELLOW;GREEN=v.Y;BLUE=v.Z;RED=v.X;SECOND=v.SECOND
TITLES={'02':'한 타일의 가운데와 바깥선','QG01':'기준점과 전체 외곽은 다른 정보','05':'가운데 표시와 경계까지의 여유','QG02':'남은 벽과 빈 통로','08':'경계를 순서대로 연결하기','QG03':'높이 차이와 평면의 홈','11':'볼록한 조각 · 오목할 수 있는 전체','QB11':'목적을 정하고 기준을 선택','QG08':'빈 공간을 덮지 않는 경계'}
PHRASES={
'02':['한 타일의 가운데와 변 관찰','가운데 표시 / 안쪽에 원 넣기','바깥을 둘러싸는 원은 다른 조건','대칭적인 모양에서는 중심이 겹칠 수 있음','한 조각과 전체 영역은 구분','다음: 3·4·5 삼각형에서 비교'],
'QG01':['기준점 하나와 외곽선 전체','기준점 고정 · 폭만 변경'],
'05':['표시의 위치와 경계까지의 거리','중심을 고르는 목적이 다름','좌표 평균 G=(4/3,1)','G에서 세 변까지의 거리는 서로 다름','복잡한 윤곽을 한 삼각형으로 덮지 않기','내심 I=(1,1): 세 거리 모두1'],
'QG02':['벽 지우기 → 빈 부분 확인','통로는 벽에서 제외할 영역'],
'08':['돌출부와 들어간 홈','같은 점이라도 연결 순서가 중요','홈을 가로지르는 선은 빈 곳을 덮음','중복점·너무 짧은 변 확인','직접 정의한 입력 모형','다음: 여섯 점의 L자 경계'],
'QG03':['높이가 다르면 같은 평면으로 볼 수 없음','같은 높이의 L자도 오목할 수 있음'],
'11':['타일 하나와 연결 영역 구분','한 타일은 볼록 · 전체는 별도 검사','두 내부 점의 선분이 빈 곳을 통과','볼록한 조각의 합집합 ≠ 항상 볼록','구멍은 제외할 내부 경계도 필요','다음: 회전 부호와 내각의 합'],
'QB11':['한 점으로 위치를 표시 / 전체 경계로 범위 기록','평균인지 · 변에서 같은 거리인지 먼저 결정'],
'QG08':['두 점은 내부 · 연결선 일부는 외부','홈을 따라 경계를 기록해야 함']}

class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG;self.add(text(TITLES[self.sid],34,YELLOW).to_corner(UL,buff=.5),text('직접 정의한 평면 모형',19,SECOND).to_corner(UR,buff=.5))
  active=None;metric=None;model=VGroup();anchor=np.array([-4.9,-1.55,0]);scale=.95
  def pt(x,y):return anchor+scale*np.array([x,y,0])
  def note(s,color=GREEN):
   nonlocal metric
   if metric:self.remove(metric)
   metric=v.base.fit(text(s,27,color),5.7).move_to([3.3,-.05,0]);self.add(metric)
  def beat(s):
   nonlocal active
   if active:self.remove(active)
   active=v.base.fit(text(s,28),5.7).move_to([3.3,1.55,0]);self.add(active)
  def replace(m):
   nonlocal model
   self.remove(*model.get_family());model=m;self.add(model)
  def triangle():
   points=[pt(0,0),pt(4,0),pt(0,3)];m=VGroup(Polygon(*points,fill_color='#426F7C',fill_opacity=.35,stroke_color=GREEN,stroke_width=4))
   for i,p in enumerate(points):m.add(Dot(p,color=YELLOW),text('ABC'[i],24,YELLOW).next_to(p,DOWN if i<2 else LEFT,buff=.1))
   return m
  L=[(0,0),(4,0),(4,1),(1,1),(1,4),(0,4)]
  def lshape():return VGroup(Polygon(*[pt(x,y) for x,y in L],fill_color='#426F7C',fill_opacity=.35,stroke_color=GREEN,stroke_width=4),text('빈 영역',22,SECOND).move_to(pt(2.65,2.6)))
  def segment(m):
   a=pt(.5,3.5);b=pt(3.5,.5);m.add(Dot(a,color=BLUE,radius=.08),Dot(b,color=BLUE,radius=.08));line=Line(a,b,color=RED,stroke_width=5);self.play(Create(line),run_time=2);m.add(line)
  def hull(m):
   missing=Polygon(pt(4,1),pt(1,4),pt(1,1),fill_color=RED,fill_opacity=.24,stroke_width=0);chord=Line(pt(4,1),pt(1,4),color=RED,stroke_width=5);self.play(FadeIn(missing),Create(chord),run_time=1.7);m.add(missing,chord)
  def hexagon():
   center=pt(2,1.7);r=1.85;points=[center+r*np.array([np.cos(PI/6+k*PI/3),np.sin(PI/6+k*PI/3),0]) for k in range(6)]
   return VGroup(Polygon(*points,fill_color='#426F7C',fill_opacity=.35,stroke_color=GREEN,stroke_width=4),Dot(center,color=BLUE,radius=.08)),center,r
  def label(s,p,color=YELLOW):return text(s,24,color).next_to(p,UP,buff=.12)
  self.add(text('표식과 수치는 설명용 · 실제 게임 내부 구현의 측정값 아님',20,SECOND).move_to([-1.9,-2.65,0]))
  if self.sid in ['02','11']:
   model,center,r=hexagon();self.add(model)
  elif self.sid=='05':replace(triangle())
  elif self.sid in ['08','QG08','QB11']:replace(lshape())
  elif self.sid=='QG01':
   width=ValueTracker(2.4);center=pt(2,1.4)
   model=VGroup(always_redraw(lambda:Rectangle(width=width.get_value(),height=2,fill_opacity=.3,fill_color='#426F7C',stroke_color=GREEN,stroke_width=4).move_to(center)),Dot(center,color=BLUE,radius=.09),text('고정한 기준점',22,BLUE).next_to(center,DOWN,buff=.2));self.add(model)
  elif self.sid=='QG02':
   model=VGroup(Rectangle(width=4.3,height=2.7,fill_color='#426F7C',fill_opacity=.5,stroke_color=GREEN,stroke_width=4).move_to(pt(2,1.5)));self.add(model)
  elif self.sid=='QG03':
   model=VGroup(Polygon(pt(0,0),pt(3.7,0),pt(4.7,.7),pt(1,.7),fill_opacity=.3,fill_color='#426F7C',stroke_color=GREEN),Polygon(pt(.5,1.5),pt(3,1.5),pt(3.7,2),pt(1.2,2),fill_opacity=.3,fill_color='#426F7C',stroke_color=BLUE));self.add(model)
  starts=slot.get('lineStarts',[c['start'] for c in slot['cues']])
  for i,tm in enumerate(starts):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   beat(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)])
   if self.sid=='02':
    if i==0:note('가운데 한 점 / 여섯 개의 바깥 변',BLUE)
    if i==1:
     inner=Circle(radius=r*np.sqrt(3)/2,color=BLUE,stroke_width=3).move_to(center);self.play(Create(inner),run_time=1.2);model.add(inner);note('표시할 점 / 변까지 같은 거리',BLUE)
    if i==2:
     outer=Circle(radius=r,color=YELLOW,stroke_width=3).move_to(center);self.play(Create(outer),run_time=1.2);model.add(outer);note('변까지 같은 거리 / 꼭짓점까지 같은 거리',BLUE)
    if i==3:note('정육각형의 대칭 · 일반 삼각형은 다름',YELLOW)
    if i==4:note('한 타일 ≠ 연결된 전체 땅')
    if i==5:
     replace(triangle())
     for name,p,c in [('G',pt(4/3,1),BLUE),('I',pt(1,1),GREEN),('O',pt(2,1.5),YELLOW)]:model.add(Dot(p,color=c),label(name,p,c))
     note('같은 삼각형의 서로 다른 세 중심',YELLOW)
   elif self.sid=='QG01':
    if i==0:note('점 하나는 외곽을 기록하지 않음',BLUE)
    if i==1:self.play(width.animate.set_value(4.4),run_time=3);note('기준점 고정 / 폭2.4 →4.4',BLUE)
   elif self.sid=='05':
    if i==0:marker=Dot(pt(4/3,1),color=BLUE,radius=.08);model.add(marker,label('G',marker,BLUE));note('표시와 안전 여유는 다른 질문')
    if i==1:note('무엇을 같게 만들지 먼저 결정')
    if i==2:note('G=(4/3,1) : 꼭짓점 좌표 평균',BLUE)
    if i==3:
     G=np.array([4/3,1]);feet=[(0,1),(4/3,0),tuple(G+(12-np.dot([3,4],G))/25*np.array([3,4]))]
     for foot in feet:
      l=DashedLine(pt(*G),pt(*foot),color=BLUE,dash_length=.06);self.play(Create(l),run_time=.5);model.add(l)
     note('G에서의 거리: 4/3, 1, 4/5',BLUE)
    if i==4:note('현재 예제는 삼각형 판에 한정',YELLOW)
    if i==5:
     replace(triangle());I=pt(1,1);model.add(Dot(I,color=GREEN),label('I',I,GREEN));circle=Circle(radius=scale,color=GREEN,stroke_width=3).move_to(I);self.play(Create(circle),run_time=2);model.add(circle);note('I=(1,1), r=1',GREEN)
   elif self.sid=='QG02':
    if i==0:note('벽과 열린 공간을 각각 기록')
    if i==1:
     opening=Union(Rectangle(width=1.2,height=1.3).move_to(pt(2,.75)),Circle(radius=.6).move_to(pt(2,1.4)),fill_color=BG,fill_opacity=1,stroke_color=RED,stroke_width=4);self.play(FadeIn(opening),run_time=2);model.add(opening);note('빈 통로를 벽으로 채우면 안 됨',RED)
   elif self.sid=='08':
    if i==0:note('안으로 들어간 꼭짓점: (1,1)',BLUE)
    if i==1:
     path=VMobject().set_points_as_corners([pt(*p) for p in L+[L[0]]]).set_stroke(YELLOW,5);self.play(Create(path),run_time=3);model.add(path);note('마지막 점에서 처음으로 돌아오기')
    if i==2:hull(model);note('빨강: 지름길이 잘못 채운 부분',RED)
    if i==3:note('중복점 / 길이0 / 넓이0 먼저 검사',YELLOW)
    if i==4:note('게임 메시를 추출한 그림이 아님',SECOND)
    if i==5:replace(lshape());note('다음: 입력 순서와 빠진 영역 검사')
   elif self.sid=='QG03':
    if i==0:arrow=DoubleArrow(pt(.1,0),pt(.1,1.5),color=BLUE,buff=0,stroke_width=4);model.add(arrow);note('높이가 다른 두 표면',BLUE)
    if i==1:replace(lshape());segment(model);note('같은 평면 위 / 선분 일부는 바깥',RED)
   elif self.sid=='11':
    if i==0:note('한 타일의 볼록성과 전체 윤곽은 별개')
    if i==1:
     self.play(model.animate.scale(.56).shift(LEFT*.8),run_time=1);copy=model.copy().shift(RIGHT*1.78);model.add(copy);self.add(copy);note('볼록한 조각을 이어도 홈이 남을 수 있음')
    if i==2:replace(lshape());segment(model);note('같은 원리를 단순한 L자 모형으로 확인',BLUE)
    if i==3:note('안의 두 점을 잇는 선분 전체를 검사',RED)
    if i==4:
     outer=Rectangle(width=4,height=3,fill_color='#426F7C',fill_opacity=.35,stroke_color=GREEN,stroke_width=4).move_to(pt(2,1.5));inner=Rectangle(width=1.4,height=1.1,fill_color=BG,fill_opacity=1,stroke_color=RED,stroke_width=4).move_to(pt(2,1.5));replace(VGroup(outer,inner));note('초록: 바깥 경계 / 빨강: 제외할 내부 경계',YELLOW)
    if i==5:note('다음: 꺾이는 방향과 각도의 합')
   elif self.sid=='QB11':
    if i==0:model.add(Dot(pt(.5,.5),color=BLUE,radius=.09));note('점: 기준 위치 / 선: 남길 전체 경계',BLUE)
    if i==1:replace(triangle());note('평균·변까지 거리·꼭짓점까지 거리')
   elif self.sid=='QG08':
    if i==0:segment(model);note('두 내부 점만으로 볼록성을 보장 못 함',RED)
    if i==1:
     replace(lshape());trace=VMobject().set_points_as_corners([pt(*p) for p in L+[L[0]]]).set_stroke(YELLOW,5);self.play(Create(trace),run_time=3);model.add(trace);hull(model);note('노랑: 올바른 순서 / 빨강: 잘못된 지름길',YELLOW)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
