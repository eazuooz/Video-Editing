"""Editable planar examples: preserve an L-shaped region while partitioning it."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('partition_style',Path(__file__).with_name('m03-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;YELLOW=v.YELLOW;GREEN=v.Y;BLUE=v.Z;RED=v.X;SECOND=v.SECOND
L=[(0,0),(4,0),(4,1),(1,1),(1,4),(0,4)]
EARS=[(0,1,2),(0,2,3),(0,3,4),(0,4,5)]
TITLES={'QG04':'땅과 비워 둘 영역','14':'홈을 가로지르는 대각선','QG05':'귀를 저장해도 빈 홈은 그대로','17':'같은 땅을 겹침 없이 덮기','QG06':'가공과 분할은 목적이 다릅니다','QB13':'남겨야 할 영역을 검사','QG09':'타일을 더하고 빼면 바뀌는 경계','19':'긴 변과 아주 가까운 꼭짓점','QG07':'이동 경로와 영역 경계','21':'한 조각에서 전체 경계로'}
PHRASES={
'QG04':['물로 바뀐 부분은 땅에서 제외','노랑: 삼각형으로 채우면 안 되는 홈'],
'14':['바깥으로 열린 빈 공간','임의의 점에서 연결하면 홈을 가로지를 수 있음','잘못 덮은 영역은 빨강','일부 삼각형은 서로 겹침','직접 정의한 실패 예제','다음: 시작점에 따른 차이'],
'QG05':['귀를 저장 / 남은 경계와 다시 합치기'],
'17':['초록: 땅 / 노랑: 빈 부분','원래 땅을 남기고 홈은 비워 두기','귀 하나를 떼면 이웃 관계도 갱신','겹침 없는 덮기와 같은 바깥 경계','실제 게임에서 추출한 지형이 아님','네 조각의 합집합이 원래 L자'],
'QG06':['사각형 자르기 → 조각 방향 바꾸기','목표 조각 가공 ≠ 삼각형 분할의 증거'],
'QB13':['가공은 일부를 버릴 수 있음 / 분할은 원래 영역 보존','비워 둘 곳을 채우면 다른 모양'],
'QG09':['타일 하나 추가 → 바깥선 변화','모형에서 추가한 타일 제거'],
'19':['긴 변 가까이에 점 하나','길고 가느다란 삼각형','유효할 수 있지만 오차에 민감','길이 오차와 넓이 오차 구분','단순화로 통로를 지우지 않기','유효성 먼저 · 품질은 그다음'],
'QG07':['벨트는 물건이 지나는 경로','경계를 줄여도 필요한 틈은 보존'],
'21':['한 타일과 전체 땅 구분','중심의 목적 → 경계 → 홈과 구멍','분할해도 원래 영역을 유지','다음: 세 중심과 네 삼각형 확인']}

class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG
  self.add(v.base.fit(text(TITLES[self.sid],34,YELLOW),11).to_corner(UL,buff=.5),text('직접 정의한 설명 모형',19,SECOND).to_corner(UR,buff=.5))
  anchor=np.array([-4.9,-1.6,0]);sc=.93;model=VGroup();active=None;metric=None
  def p(x,y):return anchor+sc*np.array([x,y,0])
  def beat(s):
   nonlocal active
   if active:self.remove(active)
   active=v.base.fit(text(s,27),5.7).move_to([3.3,1.6,0]);self.add(active)
  def note(s,c=GREEN):
   nonlocal metric
   if metric:self.remove(metric)
   metric=v.base.fit(text(s,26,c),5.7).move_to([3.3,.05,0]);self.add(metric)
  def replace(m):
   nonlocal model
   self.remove(*model.get_family());model=m;self.add(model)
  def poly(points,c=GREEN,opacity=.35):return Polygon(*[p(*z) for z in points],fill_color=c,fill_opacity=opacity,stroke_color=c,stroke_width=4)
  def notch():return VGroup(DashedVMobject(poly([(1,1),(4,1),(4,4),(1,4)],YELLOW,0),num_dashes=36),text('비워 둘 홈',22,YELLOW).move_to(p(2.55,2.6)))
  def land(numbers=False):
   m=VGroup(poly(L),notch())
   if numbers:
    for j,z in enumerate(L):m.add(Dot(p(*z),radius=.055,color=YELLOW),text(str(j),21,YELLOW).next_to(p(*z),LEFT if j in [0,3,4,5] else RIGHT,buff=.1))
   return m
  def ear(j,c=BLUE):return poly([L[k] for k in EARS[j]],c,.55)
  def triangles():return VGroup(*[ear(j,[BLUE,GREEN,YELLOW,'#BCA7DE'][j]) for j in range(4)],notch())
  def trace():return VMobject().set_points_as_corners([p(*z) for z in L+[L[0]]]).set_stroke(YELLOW,5)
  def narrow():
   pts=[(0,0),(4,0),(4,4),(2.15,4),(2.15,1),(1.85,1),(1.85,4),(0,4)]
   return VGroup(poly(pts),text('남겨야 할 틈',22,YELLOW).move_to(p(2,4.6)),Arrow(p(2,4.25),p(2,2.5),color=YELLOW,buff=.08,stroke_width=3))
  def hexat(x,y,c=GREEN):
   points=[(x+.88*np.cos(PI/6+k*PI/3),y+.88*np.sin(PI/6+k*PI/3)) for k in range(6)]
   return poly(points,c,.4)
  self.add(text('표식·좌표는 설명용 · 게임 내부 측정값 아님',20,SECOND).move_to([-2,-2.68,0]))
  if self.sid in ['QG04','14','QG05','17','QB13']:replace(land(self.sid in ['14','17']))
  elif self.sid=='QG06':replace(VGroup(poly([(0,0),(3,0),(3,3),(0,3)])))
  elif self.sid in ['QG09','21']:replace(VGroup(hexat(1,1.5),hexat(2.524,1.5),hexat(1.762,2.82)))
  elif self.sid=='19':replace(VGroup(Line(p(0,0),p(4,0),color=GREEN,stroke_width=4),Dot(p(0,0),color=YELLOW),Dot(p(4,0),color=YELLOW)))
  elif self.sid=='QG07':replace(VGroup(VMobject().set_points_as_corners([p(0,0),p(1.5,0),p(1.5,2),p(4,2)]).set_stroke(BLUE,9),Arrow(p(2.5,2),p(3.7,2),color=YELLOW,buff=0)))
  starts=slot.get('lineStarts',[c['start'] for c in slot['cues']])
  for i,tm in enumerate(starts):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   beat(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)])
   if self.sid=='QG04':
    if i==0:note('남은 땅 / 물이 차지한 부분',BLUE)
    if i==1:
     outline=trace();self.play(Create(outline),run_time=2);model.add(outline);note('홈은 원래부터 영역 밖',YELLOW)
   elif self.sid=='14':
    if i==0:note('시작점 후보 (4,1)',BLUE)
    if i==1:
     bad=Line(p(4,1),p(1,4),color=RED,stroke_width=5);self.play(Create(bad),run_time=2);model.add(bad);note('이 대각선은 원래 땅 밖을 통과',RED)
    if i==2:
     wrong=poly([(4,1),(1,1),(1,4)],RED,.4);self.play(FadeIn(wrong),run_time=1);model.add(wrong);note('빨강: 원래 없던 영역을 덮음',RED)
    if i==3:
     a=poly([(4,1),(1,4),(0,4)],BLUE,.35);b=poly([(4,1),(0,4),(0,0)],YELLOW,.25);self.play(FadeIn(a),FadeIn(b),run_time=1.5);model.add(a,b);note('개수만 세면 겹침을 놓칠 수 있음',RED)
    if i==4:note('게임 오류를 관측한 화면이 아님',SECOND)
    if i==5:replace(land(True));note('같은 입력에서 시작점만 비교',BLUE)
   elif self.sid=='QG05':
    if i==0:
     replace(VGroup(poly([L[k] for k in [0,2,3,4,5]]),notch()));piece=ear(0);model.add(piece);self.add(piece);note('저장한 귀 + 남은 영역 = 원래 L자',BLUE);self.play(piece.animate.shift(DOWN*.5+RIGHT*.65),run_time=2);self.wait(1);self.play(piece.animate.shift(UP*.5+LEFT*.65),run_time=2)
   elif self.sid=='17':
    if i==0:note('원래 넓이 7 · 빈 부분 제외',YELLOW)
    if i==1:
     replace(triangles());note('4개 조각 · 내부 겹침 없음')
    if i==2:
     replace(land(True));a=ear(0);self.add(a);model.add(a);self.play(a.animate.set_fill(opacity=.1),run_time=1);line=Line(p(0,0),p(4,1),color=BLUE,stroke_width=5);self.play(Create(line),run_time=1);model.add(line);note('첫 귀 0·1·2 저장 → 새 이웃 0·2',BLUE)
    if i==3:replace(triangles());note('합집합이 원래 경계와 같아야 함')
    if i==4:note('조건을 확인하기 위해 정의한 예제',SECOND)
    if i==5:note('2 + 1.5 + 1.5 + 2 = 7',YELLOW)
   elif self.sid=='QG06':
    if i==0:
     note('입력 도형 / 잘린 조각',BLUE);cut=DashedLine(p(1.5,0),p(1.5,3),color=YELLOW,dash_length=.12);self.play(Create(cut),run_time=1);model.add(cut);self.wait(.7);left=poly([(0,0),(1.5,0),(1.5,3),(0,3)],GREEN,.5);right=poly([(1.5,0),(3,0),(3,3),(1.5,3)],BLUE,.5);replace(VGroup(left,right));self.play(left.animate.shift(LEFT*.25),right.animate.shift(RIGHT*.45),run_time=1.2);self.play(Rotate(right,angle=PI/2),run_time=1.5)
    if i==1:note('방향·남은 모양을 확인하는 가공',YELLOW)
   elif self.sid=='QB13':
    if i==0:replace(triangles());note('모든 조각을 합치면 원래 영역')
    if i==1:
     fill=poly([(1,1),(4,1),(4,4),(1,4)],RED,.3);self.play(FadeIn(fill),run_time=1.5);model.add(fill);note('빨강을 채우면 원래 영역이 달라짐',RED)
   elif self.sid=='QG09':
    if i==0:
     added=hexat(3.286,2.82,BLUE);self.play(FadeIn(added),run_time=1.5);model.add(added);note('파랑: 이번에 추가한 타일',BLUE)
    if i==1:self.play(FadeOut(added),run_time=2);model.remove(added);note('제외한 타일만큼 전체 경계도 복원',BLUE)
   elif self.sid=='19':
    if i==0:
     dot=Dot(p(.2,.17),color=BLUE,radius=.07);model.add(dot);self.play(FadeIn(dot),run_time=1);note('가까운 두 점 + 멀리 있는 한 점',BLUE)
    if i==1:
     slim=poly([(0,0),(4,0),(.2,.17)],BLUE,.5);self.play(Create(slim),run_time=2);model.add(slim);note('긴 변 / 작은 높이',BLUE)
    if i==2:note('가느다람 자체가 곧 오류는 아님',YELLOW)
    if i==3:note('길이 [단위] / 넓이 [단위²] 구분',YELLOW)
    if i==4:replace(narrow());note('점을 지워도 빈 틈은 남아야 함',YELLOW)
    if i==5:note('경계 보존 확인 후 모양 개선')
   elif self.sid=='QG07':
    if i==0:note('선의 연결 순서 ≠ 땅을 덮는 영역',BLUE)
    if i==1:
     replace(narrow());bridge=Line(p(1.85,4),p(2.15,4),color=RED,stroke_width=6);self.play(Create(bridge),run_time=1);model.add(bridge);note('빨강처럼 틈을 막으면 모양이 달라짐',RED)
   elif self.sid=='21':
    if i==0:note('한 조각의 모양 / 합쳐진 바깥 윤곽',BLUE)
    if i==1:replace(land());note('경계를 따라 빈 영역부터 구분',YELLOW)
    if i==2:replace(triangles());note('조각을 합쳐 원래 L자 복원')
    if i==3:note('세 중심 · 네 조각 · 넓이7 확인',YELLOW)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)

for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
