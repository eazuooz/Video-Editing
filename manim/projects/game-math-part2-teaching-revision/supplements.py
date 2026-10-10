"""Editable additive lecture geometry. Preview timing is never final narration QA."""
from pathlib import Path
import json,sys,os
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import txt,fit,basis,P,arrow,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD,PALE,rz,rx,ry
from quaternion import screen_point
BATCH=ROOT/'production/batches/game-math-part2-teaching-revision'
DATA=json.loads((BATCH/'quaternion-additive-draft.json').read_text(encoding='utf8'))
FRAMING=json.loads((BATCH/'quaternion-episode-framing.json').read_text(encoding='utf8'))
ITEMS=DATA['additions']+FRAMING['scenes']
CLARIFIED=json.loads((BATCH/'quaternion-clarified-additions-v3.json').read_text(encoding='utf8'))
for override in CLARIFIED['overrides']:
 for item in ITEMS:
  if item['id']==override['id']:item.update(override)
class Supplement(ThreeDScene):
 sid='N02'
 def construct(self):
  self.camera.background_color=WHITE
  s=next(x for x in ITEMS if x['id']==self.sid)
  timing=ROOT/'shared/output/game-math-part2-teaching-revision/supplement-timing.json'
  slot=json.loads(timing.read_text(encoding='utf8')).get(self.sid) if timing.exists() else None
  if os.environ.get('REVISION_FINAL_TIMING')=='1' and slot is None:raise RuntimeError('Current-hash measured alignment is required for final '+self.sid)
  starts=slot['lineStarts'] if slot else [i*2.4 for i in range(len(s['ko']))]
  total=slot['seconds'] if slot else len(s['ko'])*2.4+.5
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  self.add_fixed_in_frame_mobjects(fit(txt(s['title'],39),12).to_corner(UL,buff=.58),txt('게임수학 PART2 · 회전의 원리와 계산 / 오른손·Hamilton·wxyz',18,MUTED).move_to([0,2.68,0]))
  active=None;formula=None
  def fixed(m):self.add_fixed_in_frame_mobjects(m);return m
  def equation(text,color=GOLD):
   nonlocal formula
   if formula is not None:self.remove(formula)
   formula=fixed(fit(txt(text,29,color),6.1).move_to([3.2,.25,0]))
  O=screen_point(-3.1,-.3)
  mode=s['mode'];obj=None;v=None;axes=None
  planar=mode in ['imaginary','complex-turn','complex-trigonometry','normalization-example']
  if planar:
   # A visible plane with real top/edge faces: screen coordinates are a
   # presentation of the w/z or real/imaginary pair, never a world measurement.
   plane=Cube(side_length=1,fill_opacity=.7,fill_color=PALE,stroke_color=RULE,stroke_width=.6)
   plane.stretch(5.8,0);plane.stretch(4.7,1);plane.stretch(.07,2)
   self.set_camera_orientation(phi=20*DEGREES,theta=-90*DEGREES,zoom=.92)
   plane.move_to([-3,0,-.05]);self.add(plane)
   axes=Axes(x_range=[-3,3,1],y_range=[-2,3,1],x_length=5.4,y_length=4.5,axis_config={'color':MUTED,'stroke_width':1.6,'include_tip':True}).move_to([-3,0,.01]);self.add(axes)
   self.add_fixed_in_frame_mobjects(txt('w' if mode=='normalization-example' else '실수',22,RED).move_to([-.55,-.12,0]),txt('z 성분' if mode=='normalization-example' else '허수 계수',22,BLUE).move_to([-3,1.8,0]))
  else:
   obj=basis(np.eye(3),O,scale=1.7).scale(1.5,about_point=O);self.add(obj)
   self.add(VGroup(*[DashedLine(O-2.6*P[:,j],O+2.6*P[:,j],color=RULE,stroke_width=1) for j in range(3)]))
   fixed(VGroup(txt('x',22,RED),txt('y',22,GREEN),txt('z',22,BLUE)).arrange(RIGHT,buff=.7).move_to([-3.1,-2.25,0]))
  if mode=='complex-turn':
   v=Arrow(axes.c2p(0,0),axes.c2p(2,1),buff=0,color=RED,stroke_width=6);self.add(v)
   ghost=v.copy().set_opacity(.25);self.add(ghost)
  if mode=='complex-trigonometry':
   circle=Circle(radius=.9,color=BLUE,stroke_width=2).move_to(axes.c2p(0,0));self.add(circle)
   v=Arrow(axes.c2p(0,0),axes.c2p(1,0),buff=0,color=RED,stroke_width=6);self.add(v)
  if mode=='normalization-example':
   v=Arrow(axes.c2p(0,0),axes.c2p(1.5,2),buff=0,color=RED,stroke_width=6);self.add(v)
   fixed(txt('화살표 스케일 0.5 / w,z 성분 평면',18,MUTED).move_to([-3,-2.1,0]))
  if mode=='sandwich-prerequisite':
   v=arrow(O,O+1.35*P@np.array([1.,0,1]),GOLD,6);self.add(v)
  for i,beat in enumerate(s.get('beats',s['ko'])):
   if starts[i]>self.renderer.time:self.wait(starts[i]-self.renderer.time,frozen_frame=True)
   if active is not None:self.remove(active)
   # Keep teaching labels in the calculation column, above even a two-line
   # bottom-centred caption. The axis legend remains beside the geometry.
   active=fixed(fit(txt(beat.replace(' / ','\n'),25,INK),6.1).move_to([3.2,-1.8,0]))
   if mode=='imaginary':
    if i==0:equation('(-1)² = 1 / 1² = 1')
    elif i==1:
     equation('i² = -1',BLUE)
     self.play(Create(Arrow(axes.c2p(0,0),axes.c2p(0,1),buff=0,color=BLUE,stroke_width=5)),run_time=.7)
    elif i==2:equation('새 계산 규칙 → 방향 계산',GREEN)
    elif i==3:equation('a+bi ↔ (a,b)')
   elif mode=='complex-turn':
    if i==0:equation('2+i ↔ (2,1)')
    elif i==1:equation('(2+i)i = 2i - 1')
    elif i==2:
     equation('(2,1) → (-1,2) / √5 유지')
     self.play(Rotate(v,angle=PI/2,about_point=axes.c2p(0,0)),Create(Arc(radius=1.1,start_angle=np.arctan2(1,2),angle=PI/2,color=GREEN).move_arc_center_to(axes.c2p(0,0))),run_time=1.5)
    elif i==3:equation('(a,b) → (-b,a)')
    elif i==4:equation('평면 회전 → 3D의 축 선택',GREEN)
   elif mode=='complex-trigonometry':
    if i==0:equation('i: +90° / 다른 각도 θ는?')
    elif i==1:
     equation('단위원: (cos θ, sin θ)',BLUE)
     self.play(Rotate(v,PI/4,about_point=axes.c2p(0,0)),Create(Arc(radius=.55,start_angle=0,angle=PI/4,color=GREEN).move_arc_center_to(axes.c2p(0,0))),run_time=1)
    elif i==2:
     equation('cos 90° + i sin 90° = i')
     self.play(Rotate(v,PI/4,about_point=axes.c2p(0,0)),run_time=1)
    elif i==3:equation('평면: θ / 쿼터니언: 양쪽 연산',GREEN)
   elif mode=='axis-components':
    if i==0:equation('q = [숫자 하나, 벡터 세 성분]')
    elif i==1:equation('기호 i,j,k ≠ 네 번째 공간 방향')
    elif i==2:
     equation('z축: [w,0,0,z]',BLUE);self.play(Indicate(obj[1][2],color=GOLD),run_time=.7)
    elif i==3:equation('축 n + 각도 θ → q',GREEN)
   elif mode=='half-angle-bridge':
    if i==0:equation('θ=90° / θ/2=45°')
    elif i==1:equation('q [0,v] q⁻¹',BLUE)
    elif i==2:
     equation('전체 연산 → 실제 +z 90°',GREEN);self.play(Rotate(obj,PI/2,axis=P[:,2],about_point=O),run_time=1.5)
    elif i==3:equation('같은 v=(1,0,1)로 뒤에서 검산')
   elif mode=='normalization-example':
    if i==0:equation('√(3²+4²) = 5')
    elif i==1:
     equation('[3,0,0,4]÷5=[0.6,0,0,0.8]')
     self.play(Transform(v,Arrow(axes.c2p(0,0),axes.c2p(.3,.4),buff=0,color=GREEN,stroke_width=6)),run_time=1.3)
    elif i==2:equation('모든 성분 ÷ 같은 길이 / 축 비율 유지')
    elif i==3:equation('현재 자세의 길이 ≠ 이동 속도',BLUE)
   elif mode=='dot-cross':
    if i==0:equation('내적: 숫자 / 외적: 벡터')
    elif i==1:equation('(1,0,0)·(0,1,0)=0')
    elif i==2:
     equation('x×y=+z / y×x=-z',BLUE)
     plus=arrow(O,O+2.85*P[:,2],GOLD,7);self.play(Create(plus),run_time=.5)
     self.play(Transform(plus,arrow(O,O-2.85*P[:,2],GOLD,7)),run_time=.8)
    elif i==3:equation('순서 차이 → 회전 합성의 차이',GREEN)
   elif mode=='power-prerequisite':
    if i==0:equation('90°의 절반 = 45°')
    elif i==1:
     equation('Z45° × Z45° = Z90°',GREEN)
     self.play(Rotate(obj,PI/4,axis=P[:,2],about_point=O),run_time=.75)
     self.play(Rotate(obj,PI/4,axis=P[:,2],about_point=O),run_time=.75)
    elif i==2:equation('q → log: nθ/2 → exp: q')
    elif i==3:
     equation('반각 π/4 ÷ 2 = π/8 / 실제 45°')
     self.play(Rotate(obj,-PI/4,axis=P[:,2],about_point=O),run_time=1.2)
    elif i==4:equation('끝 자세와 중간 경로를 구분',BLUE)
   elif mode=='sandwich-prerequisite':
    if i==0:equation('v=(1,0,1) / +z 90°')
    elif i==1:equation('p=[0,1,0,1] / C=√2/2')
    elif i==2:equation('qp=[-C,C,C,C] / 스칼라 ≠ 0',RED)
    elif i==3:
     equation('qpq⁻¹=[0,0,1,1]',GREEN)
     self.play(Rotate(v,PI/2,axis=P[:,2],about_point=O),Rotate(obj,PI/2,axis=P[:,2],about_point=O),run_time=1.3)
    elif i==4:equation('v′=(0,1,1) / z 유지 / 길이 √2')
   elif mode=='episode-overview':
    equation('전체 지도 → 오늘: 만들기·되돌리기',BLUE)
    self.play(Rotate(obj,PI/2,axis=P[:,2],about_point=O),run_time=.9)
    self.play(Rotate(obj,-PI/2,axis=P[:,2],about_point=O),run_time=.9)
   elif mode=='first-conclusion':
    if i==0:equation('평면 회전 → 축 n + 각도 θ')
    elif i==1:
     equation('q · q⁻¹ = 1 / 원래 방향 복원',GREEN)
     self.play(Rotate(obj,PI/2,axis=P[:,2],about_point=O),run_time=.8)
     self.play(Rotate(obj,-PI/2,axis=P[:,2],about_point=O),run_time=.8)
    elif i==2:
     equation('다음 질문: X 뒤 Y = Y 뒤 X ?',BLUE)
     self.play(Rotate(obj,PI/2,axis=P[:,0],about_point=O),run_time=1)
   elif mode=='second-overview':
    if i==0:equation('역원 결과 → 두 회전의 합성',BLUE)
    elif i==1:
     equation('현재 a → Δ → 목표 b → 방향 v′')
     self.play(Rotate(obj,PI/2,axis=P[:,0],about_point=O),run_time=.8)
     self.play(Rotate(obj,PI/2,axis=P[:,1],about_point=O),run_time=.8)
    elif i==2:equation('먼저: 역회전 ≠ 경로 역주행',GREEN)
  if total>self.renderer.time:self.wait(total-self.renderer.time,frozen_frame=True)
for item in ITEMS:
 globals()[item['id']]=type(item['id'],(Supplement,),{'sid':item['id'],'__module__':__name__})
