"""Finite triangle, barycentric invariance, depth and attributes, using explicit coordinates."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('triangle_style',Path(__file__).with_name('m03-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;FG=v.FG;YELLOW=v.YELLOW;GREEN=v.Y;BLUE=v.Z;RED=v.X;SECOND=v.SECOND
TITLES={'11':'세 꼭짓점 사이에서 위치 찾기','PG04':'같은 평면 위여도 판 밖일 수 있음','14':'삼각형과 점을 함께 옮기기','17':'같은 화면 위치 · 다른 깊이','PG06':'평면 거리와 내부 여부는 별도 검사','19':'너무 가느다란 기준 삼각형','PG07':'위치와 그 자리의 속성','21':'표면의 위치를 찾고 값을 계산'}
PHRASES={
'11':['지붕의 모서리에서 출발','세 점 A, B, C 사이에서 P 이동','삼각형을 기준으로 정한 위치','세 기준점은 같은 화면에서 비교','세 점을 연결한 그림 ≠ 전체 지형','다음: 넓이에서 세 비율로'],
'PG04':['초록: 유한한 판 / 파랑: 기준 평면','같은 평면 위 · 삼각형 밖','안쪽으로 복귀 → 세 부분 넓이'],
'14':['모든 점에 같은 이동 적용','같은 가중치 · 달라지는 공간 위치','꼭짓점에서는 1 / 반대편 변에서는 0','화면 거리와 공간의 비율은 구분','직접 정한 좌표로 계산','다음: 음수 가중치의 바깥 위치'],
'17':['정면에서는 두 점이 겹침','화면 위치는 같아도 깊이는 다름','투영 위치만으로 표면 포함 판정 불가','평면 거리 → 내부 가중치 검사','평면 위여도 유한한 경계 밖 가능','다음: 같은 x, y · 다른 z'],
'PG06':['초록: 면 위 / 파랑: 면에서 떨어진 점','거리 조건과 내부 조건을 모두 검사'],
'19':['한 꼭짓점을 움직여 삼각형을 가늘게','작은 입력 차이 → 큰 가중치 차이','분모인 전체 넓이를 먼저 확인','좌표와 기준 삼각형은 한 쌍','세 점의 삼각형은 복잡한 지형과 다름','다음: 복잡한 경계를 나누는 방법'],
'PG07':['위치 고정 · 꼭짓점 색만 변경','꼭짓점 색 고정 · 위치 변경','직접 정의한 선형 RGB 예제'],
'21':['건물 표면의 색과 밝기 관찰','표면의 위치 → 그 자리의 속성','같은 비율로 꼭짓점의 값을 보간','실제 색은 재질·조명 등도 관여','물체 좌표와 화면 좌표를 구분','마지막: 거리·가중치·속성 함께 확인']}

class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG
  self.add(text(TITLES[self.sid],34,YELLOW).to_corner(UL,buff=.5),text('직접 정의한 모형 · XY면, Z 깊이',19,SECOND).to_corner(UR,buff=.5))
  az=ValueTracker(0);tx=ValueTracker(0);ty=ValueTracker(0);height=ValueTracker(4);wx=ValueTracker(.3);wy=ValueTracker(.5);depth=ValueTracker(0);palette=ValueTracker(0)
  anchor=np.array([-4.85,-1.25,0]);scale=.68
  def verts():return np.array([[0,0,0],[6,0,0],[0,height.get_value(),0]],dtype=float)
  def localpoint():return wx.get_value()*verts()[1]+wy.get_value()*verts()[2]+np.array([0,0,depth.get_value()])
  def project(p):
   x,y,z=np.array(p)+[tx.get_value(),ty.get_value(),0];a=az.get_value();return anchor+scale*np.array([x*np.cos(a)+z*np.sin(a),y-.1*z*np.sin(a),0])
  panel=always_redraw(lambda:Polygon(*[project(p) for p in verts()],fill_color='#426F7C',fill_opacity=.36,stroke_color=GREEN,stroke_width=4));self.add(panel)
  def vertexcolour(k):
   if self.sid not in ['PG07','21']:return YELLOW
   c=np.eye(3)[k];p=palette.get_value();rgb=(1-p)*c+p*np.roll(c,1)
   srgb=np.where(rgb<=.0031308,12.92*rgb,1.055*rgb**(1/2.4)-.055)
   return rgb_to_color(srgb)
  for k in range(3):
   self.add(always_redraw(lambda k=k:Dot(project(verts()[k]),radius=.08 if self.sid in ['PG07','21'] else .065,color=vertexcolour(k))),always_redraw(lambda k=k:text('ABC'[k],24,YELLOW).next_to(project(verts()[k]),DOWN if k<2 else LEFT,buff=.13)))
  point=always_redraw(lambda:Dot(project(localpoint()),radius=.09,color=YELLOW));self.add(point)
  self.add(always_redraw(lambda:text('P',23,YELLOW).next_to(point,UP,buff=.12)))
  weightbox=always_redraw(lambda:text(f'w = ({1-wx.get_value()-wy.get_value():.2f}, {wx.get_value():.2f}, {wy.get_value():.2f})',25,BLUE).move_to([-3,-2.1,0]));self.add(weightbox)
  self.add(text('수치와 도형은 우리 예제 · 게임 내부 측정값 아님',20,SECOND).move_to([-2,-2.65,0]))
  active=None;metric=None;extras=[]
  def note(s,color=GREEN):
   nonlocal metric
   if metric:self.remove(metric)
   metric=v.base.fit(text(s,27,color),5.8).move_to([3.3,-.05,0]);self.add(metric)
  def beat(s):
   nonlocal active
   if active:self.remove(active)
   active=v.base.fit(text(s,28),5.8).move_to([3.3,1.55,0]);self.add(active)
  def planegrid():
   grid=VGroup(*[Line(project([-1,y,0]),project([7,y,0]),color=BLUE,stroke_width=1.2,stroke_opacity=.4) for y in [-.6,1,2,3,4.6]],*[Line(project([x,-.6,0]),project([x,4.6,0]),color=BLUE,stroke_width=1.2,stroke_opacity=.4) for x in [-1,1,3,5,7]])
   self.add(grid);self.bring_to_front(panel,point);return grid
  def depthpair():
   self.remove(point);fixed=always_redraw(lambda:Dot(project([1.8,2,0]),radius=.11,color=GREEN));floating=always_redraw(lambda:Circle(radius=.13,stroke_width=4,color=BLUE).move_to(project([1.8,2,3])));line=always_redraw(lambda:DashedLine(project([1.8,2,0]),project([1.8,2,3]),dash_length=.08,color=BLUE) if abs(az.get_value())>.02 else VGroup());self.add(fixed,floating,line);return [fixed,floating,line]
  def attrcolour():
   w=np.array([1-wx.get_value()-wy.get_value(),wx.get_value(),wy.get_value()]);p=palette.get_value();rgb=(1-p)*w+p*w[[2,0,1]];rgb=np.clip(rgb,0,1);srgb=np.where(rgb<=.0031308,12.92*rgb,1.055*rgb**(1/2.4)-.055);return rgb_to_color(srgb)
  for i,tm in enumerate(slot['lineStarts']):
   if self.sid=='PG04' and i==1:tm=max(0,tm-2.5)
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   beat(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)])
   if self.sid=='11':
    if i==0:note('A, B, C : 우리가 고른 기준점')
    if i==1:self.play(wx.animate.set_value(.10),wy.animate.set_value(.10),run_time=2);self.play(wx.animate.set_value(.65),wy.animate.set_value(.15),run_time=2);note('P가 가까워지는 꼭짓점 확인')
    if i==2:note('P = wA·A + wB·B + wC·C',BLUE)
    if i==3:self.play(az.animate.set_value(.55),run_time=2);note('같은 대상·같은 시각의 좌표 비교')
    if i==4:note('세 점으로 채운 면과 실제 모양은 별개',YELLOW)
    if i==5:note('넓이 → 가중치 → 안과 밖')
   elif self.sid=='PG04':
    if i==0:extras.append(planegrid());note('z=0 : 무한한 기준 평면',BLUE)
    if i==1:
     beat('같은 평면 위에서 경계를 넘어 이동')
     self.play(wx.animate.set_value(.70),wy.animate.set_value(.50),run_time=2.5)
     beat('같은 평면 위 · 삼각형 밖');note('wA = −0.20 : A 반대편 바깥',RED)
    if i==2:
     note('안쪽으로 이동 · 가중치도 함께 변경',BLUE)
     self.play(wx.animate.set_value(.30),run_time=2)
     for p in verts():self.play(Create(Line(project(localpoint()),project(p),color=YELLOW,stroke_width=3)),run_time=.4)
     note('세 부분의 넓이로 위치를 표현',YELLOW)
   elif self.sid=='14':
    if i==0:self.play(tx.animate.set_value(.8),ty.animate.set_value(.45),run_time=3);note('A, B, C, P 모두 같은 이동')
    if i==1:self.play(az.animate.set_value(.55),run_time=2.5);note('w=(0.20, 0.30, 0.50) 그대로',BLUE)
    if i==2:note('P 이동 · 아래 가중치의 변화 확인',BLUE);self.play(wx.animate.set_value(0),wy.animate.set_value(0),run_time=1.8);self.play(wx.animate.set_value(.5),wy.animate.set_value(.5),run_time=1.8);note('A: (1,0,0) / BC 위: wA=0',BLUE)
    if i==3:note('원근 화면의 거리로3D 비율 추정 금지',YELLOW)
    if i==4:note('모형 좌표를 직접 정해 검산')
    if i==5:self.play(wx.animate.set_value(.7),run_time=2);note('다음: wA<0인 점도 계산',RED)
   elif self.sid=='17':
    if i==0:extras=depthpair();self.play(az.animate.set_value(.65),run_time=2.5);note('Z가 다르면 실제 두 점은 떨어짐',BLUE)
    if i==1:self.play(az.animate.set_value(0),run_time=2);note('정면 투영: 같은 x, y')
    if i==2:self.play(az.animate.set_value(.65),run_time=2);note('투영만으로 평면 위 여부 판단 불가',YELLOW)
    if i==3:note('① 평면 거리 ② 삼각형 가중치',BLUE)
    if i==4:
     for o in extras:self.remove(o)
     self.add(point);depth.set_value(0);self.play(wx.animate.set_value(.7),run_time=2);note('z=0이어도 wA<0이면 바깥',RED)
    if i==5:note('다음: (1.8,2,0)과(1.8,2,7)')
   elif self.sid=='PG06':
    if i==0:extras=depthpair();note('정면 투영은 같음 · 원래 점은 다름',BLUE)
    if i==1:self.play(az.animate.set_value(.65),run_time=3);note('면에서 떨어짐 → 표면 내부 판정 실패',RED)
   elif self.sid=='19':
    if i==0:self.play(height.animate.set_value(.22),run_time=3);note('높이 감소 → 전체 넓이 감소',YELLOW)
    if i==1:
     note('같은 Δy=0.05 : ΔwC=Δy/h',BLUE)
     self.play(wy.animate.set_value(.5+.05/.22),run_time=2)
    if i==2:note('분모가 작음 · 오차가 증폭될 수 있음',RED)
    if i==3:self.play(height.animate.set_value(4),run_time=2.5);note('같은 w라도 C가 바뀌면 P도 변경')
    if i==4:note('오목한 부분·구멍은 별도 경계 정보',YELLOW)
    if i==5:note('한 삼각형 → 복잡한 다각형 분할')
   elif self.sid in ['PG07','21']:
    if i==0:
     swatch=always_redraw(lambda:Square(side_length=.7,stroke_color=FG,stroke_width=2,fill_opacity=1,fill_color=attrcolour()).move_to([3.3,-1.3,0]));self.add(swatch)
     note('선형 RGB = wA·CA + wB·CB + wC·CC',BLUE)
     if self.sid=='PG07':self.play(palette.animate.set_value(1),run_time=3)
    if self.sid=='PG07':
     if i==1:self.play(wx.animate.set_value(.7),wy.animate.set_value(.15),run_time=3);note('점 이동 → 가중치 변경 → 색 변경')
     if i==2:note('표시용 색 변환과 실제 게임 구현은 별개',YELLOW)
    else:
     if i==1:note('먼저 위치를 찾고 그 자리의 속성 계산')
     if i==2:self.play(wx.animate.set_value(.6),wy.animate.set_value(.2),run_time=3);note('위치와 색에 같은 가중치 적용',BLUE)
     if i==3:note('영상의 최종 색만으로 내부 구현 확정 불가',YELLOW)
     if i==4:self.play(az.animate.set_value(.5),run_time=2);note('카메라를 바꿔도 모형의 w는 유지')
     if i==5:note('유효성 → 평면 거리 → 가중치 → 속성')
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
