"""Six independent white 3D explanations for the additive four-game revision.

All numerical values belong to the explicitly defined model. Gameplay remains
a separate actual-footage scene; these models count only as explanation.
"""
from pathlib import Path
import json,os,sys,numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
sys.path.insert(0,str(Path(__file__).parent))
from lesson import txt,fit,INK,MUTED,RULE,RED,BLUE,GOLD
from quaternion import screen_point
from quaternion_four_game_v3 import plane,vec_arrow,comparison_object,TEAL
I=ROOT/'production/batches/game-math-part2-teaching-revision/cross-game-review-20261011/interpolation-four-game-v3'
CONTENT={s['id']:s for s in json.loads((I/'additions-draft.json').read_text(encoding='utf8'))['scenes']}

def block(dim,center,color):
 b=Cube(side_length=1,fill_color=color,fill_opacity=.82,stroke_color=RULE,stroke_width=.7)
 for i,size in enumerate(dim):b.stretch(size,i)
 return b.shift(center)

def map_object(kind,origin):
 if kind=='ski':return comparison_object('ski',origin)
 if kind=='aircraft':return plane(origin,scale=.8)
 if kind=='car':
  g=VGroup(block([2.25,1,.5],[0,0,0],GOLD),block([.9,.85,.48],[-.15,0,.45],BLUE))
  for x in [-.72,.72]:
   for y in [-.55,.55]:
    wheel=Cylinder(radius=.27,height=.14,resolution=(4,8),fill_color=INK,fill_opacity=.9,stroke_width=0)
    g.add(wheel.rotate(PI/2,axis=RIGHT).shift([x,y,-.19]))
 elif kind=='board':
  g=VGroup(block([2.6,.65,.13],[0,0,0],BLUE),block([.38,.48,.62],[0,0,.39],GOLD))
  for x in [-.75,.75]:g.add(block([.15,.82,.25],[x,0,-.2],INK))
 else:raise ValueError(kind)
 return g.scale(.82,about_point=ORIGIN).shift(origin)

class FourGameInterpolation(ThreeDScene):
 sid='IPF00'
 def construct(self):
  self.camera.background_color=WHITE
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  row=CONTENT[self.sid]
  preview=os.environ.get('INTERPOLATION_FOUR_GAME_PREVIEW')=='1'
  if preview:slot=dict(seconds=18,lineStarts=[0,6,12],sentenceCues=[])
  else:
   path=Path(os.environ.get('INTERPOLATION_FOUR_GAME_TIMING',str(I/'measured-new-scenes.json')))
   slot=next(s for s in json.loads(path.read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  title=fit(txt(row['title'],33),12.6).to_corner(UL,buff=.55)
  note=fit(txt('정의한 설명 모형 · 오른손 / 열벡터 / wxyz · 화면 각도를 게임 좌표로 실측한 것이 아님',17,MUTED),12.5).move_to([0,2.75,0])
  self.add_fixed_in_frame_mobjects(title,note);labels={}
  def label(key,value,where=(3.2,.1,0),color=INK,size=27,width=6.1):
   if key in labels:self.remove(labels[key])
   obj=VGroup(*[fit(txt(part,size,color),width) for part in value.split(' / ')]).arrange(DOWN,aligned_edge=LEFT,buff=.18).move_to(where)
   labels[key]=obj;self.add_fixed_in_frame_mobjects(obj)
  def wait_to(value):
   if value>self.renderer.time:self.wait(value-self.renderer.time,frozen_frame=True)
  def line(n):wait_to(slot['lineStarts'][n])
  def sentence(fragment):
   if preview:return
   cues=[c for c in slot['sentenceCues'] if fragment in c['text']]
   assert len(cues)==1,(self.sid,fragment,cues)
   wait_to(cues[0]['start'])
  def axes(origin,extent=2.6):
   self.add(*[DashedLine(origin-extent*np.eye(3)[j],origin+extent*np.eye(3)[j],color=RULE,stroke_width=1.1) for j in range(3)])
   for j,(name,color) in enumerate([('x',RED),('y',BLUE),('z',TEAL)]):
    self.add_fixed_orientation_mobjects(txt(name,24,color).move_to(origin+(extent+.17)*np.eye(3)[j]))
  origin=screen_point(-3.2,0)
  if self.sid in ['IPF00','RCF00']:
   kinds=['car','ski','board','aircraft'];names=['포르자 호라이즌 4','라이더스 리퍼블릭','스케이트 3','트레일메이커스']
   xs=[-4.9,-1.65,1.65,4.9]
   objects=[map_object(kind,screen_point(x,.1)) for kind,x in zip(kinds,xs)]
   self.add(*objects)
   self.add_fixed_in_frame_mobjects(*[fit(txt(name,21,BLUE),3).move_to([x,-1.5,0]) for x,name in zip(xs,names)])
   label('question','중간 자세와 시간의 빠르기' if self.sid=='IPF00' else '같은 자세를 다른 표현으로 기록',(0,-2.15,0),GOLD,29,12)
   self.play(*[Rotate(obj,PI/6,axis=OUT,about_point=obj.get_center()) for obj in objects],run_time=1.2)
  elif self.sid=='IPF11':
   axes(origin);obj=plane(origin,scale=1.45);self.add(obj)
   label('value','시작: z축 0° / 목표: z축 +90°',color=GOLD)
   sentence('시간 비율');self.play(Rotate(obj,PI/4,axis=OUT,about_point=origin),run_time=1.5)
   label('value','SLERP, t = 0.5 / 실제 중간 자세: +45°',color=BLUE)
   line(1);label('half','저장 반각: 22.5° / q = (cos22.5°, 0, 0, sin22.5°)',(3.2,-1.4,0),GOLD,25)
   line(2);label('value','앞과 날개를 함께 회전 / 길이 1, 내적 0 유지',color=BLUE)
   label('half','네 성분을 절반으로 줄이지 않음',(3.2,-1.85,0),RED,24)
  elif self.sid=='IPF12':
   left=screen_point(-3.2,.1);right=screen_point(3.2,.1)
   a=plane(left,scale=1.25);b=plane(right,scale=1.25);self.add(a,b)
   label('left','선형 시간: u = t',(-3.2,1.85,0),BLUE,27,5.8)
   label('right','제곱 시간: u = t²',(3.2,1.85,0),BLUE,27,5.8)
   label('base','두 모형 모두 z축 0° → 90° / 시작과 목표를 고정',(0,-2.05,0),GOLD,25,12)
   sentence('절반에서');self.play(Rotate(a,PI/4,axis=OUT,about_point=left),run_time=1.3)
   label('left-result','t = 0.5 → u = 0.5 → 45°',(-3.2,-1.45,0),RED,24,6)
   line(1);self.play(Rotate(b,PI/8,axis=OUT,about_point=right),run_time=1.3)
   label('right-result','t = 0.5 → u = 0.25 → 22.5°',(3.2,-1.45,0),RED,24,6)
   label('base','같은 자세 경로 / 다른 시간 진행 속도',(0,-2.05,0),GOLD,26,12)
  elif self.sid=='RCF11':
   axes(origin);obj=plane(origin,scale=1.4);self.add(obj)
   label('before','앞 x / 날개 y / 위 z',color=GOLD)
   sentence('구십 도로');self.play(Rotate(obj,PI/2,axis=OUT,about_point=origin),run_time=1.4)
   label('before','x → y = (0, 1, 0) / y → −x = (−1, 0, 0)',color=BLUE,size=26)
   line(1);label('below','z → z = (0, 0, 1) / 세 결과를 각 열에 놓음',(3.2,-1.8,0),TEAL,25)
   line(2);label('before','R = [[0, −1, 0], /       [1,   0, 0], /       [0,   0, 1]]',color=BLUE,size=27)
   label('below','q = (√2/2, 0, 0, √2/2) / 같은 세 축 결과',(3.2,-1.85,0),GOLD,24)
  elif self.sid=='RCF12':
   left=screen_point(-3.3,.05);right=screen_point(3.3,.05)
   def frame(where):
    g=VGroup(Cube(side_length=1.75,fill_color=GOLD,fill_opacity=.12,stroke_color=RULE,stroke_width=.8))
    g.add(vec_arrow(ORIGIN,[1,0,0],RED,1.9),vec_arrow(ORIGIN,[0,1,0],BLUE,1.9),vec_arrow(ORIGIN,[0,0,1],TEAL,1.9))
    # Distinct labeled directions expose handedness even for a symmetric cube.
    for point,color in [([1.2,.1,.2],RED),([.1,1.2,.2],BLUE),([.1,.2,1.2],TEAL)]:
     g.add(Sphere(radius=.15,resolution=(4,8),fill_color=color,fill_opacity=1,stroke_width=0).shift(point))
    return g.shift(where)
   a=frame(left);b=frame(right);self.add(a,b)
   label('left','엑스축만 뒤집기: 반사',(-3.3,1.9,0),RED,26,5.9)
   label('right','두 축 뒤집기: z축 반 바퀴',(3.3,1.9,0),BLUE,26,5.9)
   sentence('엑스축만');self.play(a.animate.apply_matrix(np.diag([-1,1,1]),about_point=left),run_time=1.3)
   line(1);self.play(Rotate(b,PI,axis=OUT,about_point=right),run_time=1.3)
   label('left-result','diag(−1, 1, 1) / det = −1',(-3.3,-1.5,0),RED,26,5.9)
   label('right-result','diag(−1, −1, 1) / det = +1',(3.3,-1.5,0),BLUE,26,5.9)
   label('rule','이 대각행렬에서는 대각 성분의 곱',(0,-2.05,0),MUTED,23,12)
   line(2);label('rule','길이·직각과 함께 det = +1 확인 / 쿼터니언 정규화로 반사를 고칠 수 없음',(0,-2.05,0),GOLD,24,12)
  else:raise ValueError(self.sid)
  assert self.renderer.time<=slot['seconds'],(self.sid,self.renderer.time,slot['seconds'])
  wait_to(slot['seconds'])

class IPF00(FourGameInterpolation):sid='IPF00'
class IPF11(FourGameInterpolation):sid='IPF11'
class IPF12(FourGameInterpolation):sid='IPF12'
class RCF00(FourGameInterpolation):sid='RCF00'
class RCF11(FourGameInterpolation):sid='RCF11'
class RCF12(FourGameInterpolation):sid='RCF12'
