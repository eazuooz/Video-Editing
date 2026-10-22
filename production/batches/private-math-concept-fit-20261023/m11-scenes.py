"""Finite surfaces, signed plane distance and ordered vertices in one explicit frame."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('plane_style',Path(__file__).with_name('m03-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;FG=v.FG;YELLOW=v.YELLOW;GREEN=v.Y;BLUE=v.Z;RED=v.X;SECOND=v.SECOND
TITLES={'02':'다리 표면과 그 위의 점','PG01':'표면을 따라가기 / 수직으로 움직이기','PG02':'표면이 기울면 법선도 함께 회전','05':'기준면의 위와 아래를 구분','08':'세 점과 둘레 순서','PG03':'판의 둘레를 순서대로 연결'}
PHRASES={
'02':['눈에 보이는 유한한 다리 표면','한 점과 표면의 관계','계산용 평면은 무한히 이어짐','표면까지의 거리 ≠ 판 위의 범위','같은 월드 좌표계로 비교','게임 내부 구현을 측정한 그림 아님'],
'PG01':['초록: 표면을 따라 이동 / 파랑: 법선','법선 방향으로 내려 가장 가까운 점'],
'PG02':['연결된 다리의 일부가 기울어짐','면과 법선은 항상 수직','같은 점 · 다른 표면 → 거리 변화'],
'05':['바닥 고정 · 점의 높이만 변경','부호로 위와 아래를 구분','물체 고정 · 보는 방향만 변경','수평면: 높이 차이 / 일반면: 법선 거리','평면만으로 끝과 구멍을 알 수 없음','다음: 평면 위의 가장 가까운 점'],
'08':['세 연결점을 먼저 확인','평면의 화면 투영과 실제3D 구분','둘레 순서를 뒤집으면 법선 반대','직접 정한 A, B, C의 예제','삼각형 안에서 점의 위치 변경','여러 점의 면 방향으로 연결'],
'PG03':['같은 판을 기울인 모습 · 가려진 변 구분','마지막 점에서 첫 점으로 연결']}

class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG
  self.add(text(TITLES[self.sid],35,YELLOW).to_corner(UL,buff=.5),text('우리 수학 모형 · Y 위',20,SECOND).to_corner(UR,buff=.5))
  anchor=np.array([-3.35,-.05,0]);zoom=.94;tilt=ValueTracker(0);view=ValueTracker(.32);px=ValueTracker(.2);py=ValueTracker(1.6);nz=ValueTracker(1)
  def rot(p):
   a=tilt.get_value();x,y,z=p;return np.array([np.cos(a)*x-np.sin(a)*y,np.sin(a)*x+np.cos(a)*y,z])
  def project(p):
   x,y,z=p;az=view.get_value();return anchor+zoom*np.array([np.cos(az)*x-np.sin(az)*z,y*.86-.26*(np.sin(az)*x+np.cos(az)*z),0])
  triangle=self.sid=='08';pent=self.sid=='PG03'
  if triangle or pent:nz.set_value(-1)  # Ordered XZ vertices define a downward normal.
  vertices=[[-1.8,0,-1.1],[1.6,0,-1.1],[.8,0,1.3]] if triangle else ([[-1.8,0,-1.1],[.8,0,-1.3],[1.9,0,.0],[.8,0,1.3],[-1.6,0,1.0]] if pent else [[-2.1,0,-1.1],[2.1,0,-1.1],[2.1,0,1.1],[-2.1,0,1.1]])
  panel=always_redraw(lambda:Polygon(*[project(rot(p)) for p in vertices],fill_color='#426F7C',fill_opacity=.40,stroke_color=GREEN,stroke_width=4))
  self.add(panel)
  normal=always_redraw(lambda:Arrow(project([0,0,0]),project(rot([0,1.7*nz.get_value(),0])),buff=0,color=BLUE,stroke_width=5))
  self.add(normal)
  point=always_redraw(lambda:Dot(project([px.get_value(),py.get_value(),0]),radius=.09,color=YELLOW));self.add(point)
  label=always_redraw(lambda:text('P',25,YELLOW).next_to(point,UP,buff=.12));self.add(label)
  def foot():
   p=np.array([px.get_value(),py.get_value(),0]);n=rot([0,1,0]);return p-n*np.dot(n,p)
  perpendicular=always_redraw(lambda:DashedLine(project(foot()),point.get_center(),color=BLUE,stroke_width=3,dash_length=.09) if np.linalg.norm(project(foot())-point.get_center())>.02 else VGroup())
  self.add(perpendicular)
  bottom=text('Y : 위 · 초록 : 표면 · 파랑 : 법선',22,SECOND).move_to([-3.3,-2.25,0]);self.add(bottom)
  active=None;metric=None;extra=[]
  def note(s,color=GREEN):
   nonlocal metric
   if metric:self.remove(metric)
   metric=v.base.fit(text(s,28,color),6.1).move_to([3,-.05,0]);self.add(metric)
  def beat(s):
   nonlocal active
   if active:self.remove(active)
   active=v.base.fit(text(s,29),6.1).move_to([3,1.5,0]);self.add(active)
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   beat(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)])
   if self.sid=='02':
    if i==1:self.play(py.animate.set_value(.45),run_time=2);note('점 P와 기준 표면')
    if i==2:
     guides=VGroup(*[DashedLine(project([-3.1,0,z]),project([3.1,0,z]),color=SECOND,stroke_width=1.8,dash_length=.13) for z in [-1,0,1]])
     self.play(Create(guides),run_time=1);note('표면의 연장: 계산용 무한 평면')
    if i==3:self.play(px.animate.set_value(2.7),py.animate.set_value(0),run_time=2);note('거리=0 · 유한한 판 바깥',YELLOW)
    if i==4:self.play(view.animate.set_value(.9),run_time=2.5);note('모형의 점과 면은 고정')
    if i==5:note('다음: 표면에 수직인 방향')
   elif self.sid=='PG01':
    if i==0:
     tangent=Arrow(project([-1.5,0,0]),project([1.5,0,0]),buff=0,color=GREEN,stroke_width=5);self.add(tangent);note('수평 이동: 법선 방향 거리 유지')
     self.play(px.animate.set_value(1.3),run_time=2);self.play(py.animate.set_value(.4),run_time=2);self.play(py.animate.set_value(1.6),run_time=2)
    if i==1:self.play(py.animate.set_value(0),run_time=2.4);note('파랑 방향으로 P를 표면에 투영',BLUE)
   elif self.sid=='PG02':
    if i==1:self.play(tilt.animate.set_value(.48),run_time=3);note('법선 n은 기울어진 면에 수직',BLUE)
    if i==2:
     note('P 고정 · 기울기 변경 → 수직 거리 변경');self.play(tilt.animate.set_value(-.30),run_time=3)
   elif self.sid=='05':
    if i==0:self.play(py.animate.set_value(-1.2),run_time=2);self.play(py.animate.set_value(1.2),run_time=2);note('위쪽 + / 아래쪽 −',BLUE)
    if i==1:self.play(py.animate.set_value(-.9),run_time=1.8);note('y−h < 0 : 기준면 아래',YELLOW)
    if i==2:self.play(view.animate.set_value(1.10),run_time=2.8);note('카메라 변화 · 점의 월드 높이 불변')
    if i==3:self.play(py.animate.set_value(1.3),tilt.animate.set_value(.40),run_time=2.5);note('n·X=d : (n·P−d) / ||n||',BLUE)
    if i==4:note('무한 평면의 거리와 유한 영역은 별개',YELLOW)
    if i==5:note('직접 정의한 면 → 가장 가까운 점')
   elif self.sid=='08':
    if i==0:
     point.clear_updaters();label.clear_updaters();self.remove(point,label,perpendicular)
     for k,p in enumerate(vertices):
      dot=always_redraw(lambda p=p:Dot(project(p),radius=.09,color=YELLOW));name=always_redraw(lambda k=k,p=p:text('ABC'[k],25,YELLOW).next_to(project(p),DOWN,buff=.14));self.add(dot,name);extra.extend([dot,name])
     note('세 점 A, B, C')
    if i==1:
     self.play(view.animate.set_value(1.02),run_time=2.5)
     note('화면에 보이는 형태는 투영 결과')
    if i==2:
     note('A→B→C / A→C→B',BLUE);self.play(nz.animate.set_value(1),run_time=1.6);self.play(nz.animate.set_value(-1),run_time=1.6)
    if i==3:note('이 삼각형은 직접 정의한 수학 예제')
    if i==4:
     p=Dot(project(np.mean(vertices,axis=0)),radius=.10,color=YELLOW);self.add(p)
     self.play(p.animate.move_to(project(.7*np.array(vertices[0])+.15*np.array(vertices[1])+.15*np.array(vertices[2]))),run_time=2);note('세 꼭짓점 사이의 위치를 숫자로 표현')
    if i==5:note('다음: 여러 꼭짓점의 면 방향')
   elif self.sid=='PG03':
    if i==0:
     point.clear_updaters();label.clear_updaters();self.remove(point,label,perpendicular)
     self.play(tilt.animate.set_value(-.22),view.animate.set_value(.72),run_time=3)
     # An opaque raised strip supplies a real, explicitly constructed occluder.
     strip=Polygon(*[project(p) for p in [[-.45,-.75,-1.6],[.45,-.75,-1.6],[.45,.8,-1.6],[-.45,.8,-1.6]]],fill_color='#253F4B',fill_opacity=1,stroke_color=SECOND,stroke_width=1.8)
     self.add(strip);extra=[strip]
     mask=strip.get_vertices()
     def inside(p):
      cross=[]
      for j in range(len(mask)):
       edge=mask[(j+1)%len(mask)]-mask[j];delta=p-mask[j]
       cross.append(edge[0]*delta[1]-edge[1]*delta[0])
      return min(cross)>=-1e-6 or max(cross)<=1e-6
     for j,a in enumerate(vertices):
      a=project(rot(a));b=project(rot(vertices[(j+1)%len(vertices)]));ts=[t for t in np.linspace(0,1,101) if inside(a+t*(b-a))]
      if len(ts)>1:
       hidden=DashedLine(a+min(ts)*(b-a),a+max(ts)*(b-a),color=YELLOW,stroke_width=3,dash_length=.075);self.add(hidden);extra.append(hidden)
     note('가림판 뒤의 변: 노란 점선',YELLOW)
    if i==1:
     for obj in extra:self.remove(obj)
     self.play(tilt.animate.set_value(0),view.animate.set_value(.32),run_time=1.2)
     for k,p in enumerate(vertices):
      a=project(p);b=project(vertices[(k+1)%len(vertices)])
      self.add(Dot(a,radius=.07,color=YELLOW),text(str(k),22,YELLOW).next_to(a,DOWN,buff=.1));self.play(Create(Arrow(a,b,buff=.10,color=YELLOW,stroke_width=4)),run_time=.4)
     note('0→1→2→3→4→0 · 순서를 보존',YELLOW)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
