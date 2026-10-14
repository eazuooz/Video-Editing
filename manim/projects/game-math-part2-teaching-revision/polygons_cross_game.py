"""Additive, narrated cross-game comparison scenes for the recorded white series.

All geometry is a defined illustrative shape, never measured engine geometry.
"""
from pathlib import Path
import json,sys
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import txt,fit,P,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD
from quaternion import screen_point
B=ROOT/'production/batches/game-math-part2-teaching-revision'
CONTENT={s['id']:s for s in json.loads((B/'cross-game-review-20261011/polygon-cross-game-content-v4.json').read_text(encoding='utf8'))['scenes']}
TEAL='#327d7d'

class CrossGamePolygon(ThreeDScene):
 sid='QF04'
 def construct(self):
  self.camera.background_color=WHITE
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  record=CONTENT[self.sid]
  timeline=json.loads((ROOT/f'projects/game-math-polygon-{record["episode"]}-v2/production/timeline.json').read_text(encoding='utf8'))
  slot=next(s for s in timeline['scenes'] if s['id']==self.sid)
  labels={}
  self.add_fixed_in_frame_mobjects(fit(txt(record['title'],34),12).to_corner(UL,buff=.6),txt('설명용 도형 · 게임 내부 구현이나 실측값을 뜻하지 않음',19,MUTED).move_to([0,2.65,0]))
  def label(key,text,where=(3.2,.2,0),color=INK,size=27,width=6):
   if key in labels:self.remove(labels[key])
   g=VGroup(*[fit(txt(t,size,color),width) for t in text.split(' / ')]).arrange(DOWN,aligned_edge=LEFT,buff=.18)
   g.move_to(where);labels[key]=g;self.add_fixed_in_frame_mobjects(g);return g
  def wait_to(t):
   if t>self.renderer.time:self.wait(t-self.renderer.time,frozen_frame=True)
  def line(i):wait_to(slot['lineStarts'][i])
  def sentence(fragment):
   matches=[c for c in slot['sentenceCues'] if fragment in c['text']];assert len(matches)==1,(self.sid,fragment);wait_to(matches[0]['start'])
  def project(x,y,center=(-3.2,0),scale=.8):return screen_point(*center)+P@np.array([x*scale,y*scale,0.])
  def plate(coords,color=BLUE,center=(-3.2,0),scale=.8):
   v=[project(x,y,center,scale) for x,y in coords];dz=-.16*P[:,2]
   bottom=Polygon(*[p+dz for p in v],fill_color=color,fill_opacity=.08,stroke_color=RULE,stroke_width=1)
   faces=VGroup(*[Polygon(v[i],v[(i+1)%len(v)],v[(i+1)%len(v)]+dz,v[i]+dz,fill_color=color,fill_opacity=.22,stroke_color=RULE,stroke_width=.8) for i in range(len(v))])
   top=Polygon(*v,fill_color=color,fill_opacity=.12,stroke_color=color,stroke_width=2.6)
   group=VGroup(bottom,faces,top);self.add(group);return group,v
  square=[[-1.5,-1.5],[1.5,-1.5],[1.5,1.5],[-1.5,1.5]]
  el=[[-2,-2],[2,-2],[2,-1],[-1,-1],[-1,2],[-2,2]]
  def animate_region(coords,color=TEAL,center=(-3.2,0),scale=.8):
   g,v=plate(coords,color,center,scale);self.play(Indicate(g,color=color),run_time=.6);return g,v
  if self.sid=='QF04':
   a,v=plate(square,BLUE,center=(-3.3,.25));point=Dot3D(project(0,0,(-3.3,.25)),radius=.08,color=GOLD);self.add(point)
   label('main','다각형 전체 장 / 두 편으로 이어 보기',color=GOLD)
   sentence('이번 편은');label('main','이번 편 / 중심 선택 → 경계 검사',color=BLUE);self.play(Indicate(point),run_time=.6)
   sentence('삼각형으로');self.play(FadeOut(point),run_time=.4)
   diagonal=Line3D(v[0],v[2],color=TEAL,thickness=.028);self.play(Create(diagonal),run_time=.65)
   label('main','다음 편 / 유효한 경계 → 삼각형 분할',color=TEAL)
  elif self.sid=='QB11':
   shape,v=plate(square,BLUE);point=Dot3D(project(0,0),radius=.09,color=GOLD);self.add(point)
   label('main','도르프로만틱 · 타이니 글레이드 / 배치할 위치와 전체 외곽',color=BLUE)
   sentence('반면 시리어스');label('main','시리어스 샘: 대상을 찾는 표시 / 노이타: 땅과 빈 공간의 경계',color=TEAL)
   line(1);self.play(FadeOut(shape),run_time=.4);shape,v=animate_region([[-2,-.8],[2,-.8],[2,.8],[-2,.8]],RED)
   label('main','같은 기준점 / 서로 다른 모양',color=RED);label('below','한 점 ≠ 전체 외곽',(3.2,-1.75,0),RED,25)
   sentence('좌표 평균인지');label('main','먼저 목적을 정함 / 좌표 평균? 변까지 같은 거리?',color=GOLD)
   sentence('게임 내부가');label('below','관찰 사례와 공식 / 내부 구현 주장은 구분',(3.2,-1.75,0),MUTED,22)
  elif self.sid=='QB12':
   incoming,v=plate(square,BLUE,scale=.65)
   label('main','공장 게임의 목표 / 도형 가공 → 목표 도형 납품',color=GOLD)
   sentence('벨트는');self.play(incoming.animate.shift(P[:,0]*.5),run_time=.7);label('below','벨트는 운반 경로',(3.2,-1.75,0),TEAL,25)
   sentence('이제 기계에');self.remove(incoming)
   l,_=plate([[-1.5,-1.5],[0,-1.5],[0,1.5],[-1.5,1.5]],GREEN,center=(-3.6,0),scale=.65)
   r,_=plate([[0,-1.5],[1.5,-1.5],[1.5,1.5],[0,1.5]],BLUE,center=(-2.9,0),scale=.65)
   self.play(l.animate.shift(-.15*P[:,0]),r.animate.shift(.15*P[:,0]),run_time=.8)
   label('main','입력 도형 → 기계의 동작 / 출력 조각을 순서대로 관찰',color=TEAL)
  elif self.sid=='QB13':
   shape,v=plate(square,BLUE);half=Polygon(v[0],(v[0]+v[1])/2,(v[2]+v[3])/2,v[3],fill_color=GOLD,fill_opacity=.25,stroke_color=GOLD,stroke_width=2)
   self.add(half);label('main','셰이프즈 투: 목표 조각 만들기',color=GOLD)
   sentence('불필요한 부분을');self.play(half.animate.shift(-P[:,0]*.55),run_time=.7);label('below','버리는 작업도 있음 / 가공의 목적을 먼저 확인',(3.2,-1.75,0),MUTED,23)
   sentence('반면 삼각형');self.remove(shape,half);shape,v=animate_region(el,TEAL)
   ids=[(0,1,2),(0,2,3),(0,3,4),(0,4,5)];parts=VGroup(*[Polygon(*[v[k] for k in ind],fill_color=c,fill_opacity=.13,stroke_color=c,stroke_width=2) for ind,c in zip(ids,[RED,GREEN,BLUE,GOLD])])
   self.play(*[Create(t) for t in parts],run_time=.8);label('main','삼각형 분할 / 모든 조각의 합집합 = 원래 영역',color=TEAL)
   line(1);label('below','문 · 통로 · 땅의 홈 / 빈 공간을 새로 채우지 않음',(3.2,-1.75,0),RED,25)
   segment=Line3D(v[2],v[4],color=RED,thickness=.03);self.play(Create(segment),run_time=.7)
   sentence('도르프로만틱의');self.play(FadeOut(segment),Indicate(parts),run_time=.65);label('main','게임이 달라도 / 남길 영역과 빈 공간부터 확인',color=TEAL)
  elif self.sid=='QB14':
   shape,v=plate(el,BLUE);path=VGroup(Line3D(v[0],v[1],color=RED,thickness=.035),Line3D(v[1],v[2],color=RED,thickness=.035));self.add(path)
   label('main','빈 공간 보존 → 순서 있는 연결',color=GOLD)
   sentence('벨트는');label('main','이동 경로와 영역의 외곽 / 역할은 서로 다름',color=BLUE)
   sentence('둘 다 점의');link=Line3D(v[2],v[4],color=RED,thickness=.03);self.play(Create(link),run_time=.7)
   label('below','연결됐어도 / 홈을 가로질렀는지 검사',(3.2,-1.75,0),RED,25)
  else:raise ValueError(self.sid)
  wait_to(slot['seconds'])

class QF04(CrossGamePolygon):sid='QF04'
class QB11(CrossGamePolygon):sid='QB11'
class QB12(CrossGamePolygon):sid='QB12'
class QB13(CrossGamePolygon):sid='QB13'
class QB14(CrossGamePolygon):sid='QB14'
