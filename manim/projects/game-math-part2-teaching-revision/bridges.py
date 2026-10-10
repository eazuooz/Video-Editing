"""Causal bridges carry the previous mathematical state into the next question.

Original lecture scenes stay untouched. P is a proper 3D coordinate rotation;
these independent Cairo scenes are explanations, never actual-footage time.
"""
from pathlib import Path
import sys,json,os
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import txt,fit,basis,P,arrow,rz,rx,ry,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD
from quaternion import screen_point
B=ROOT/'production/batches/game-math-part2-teaching-revision'
D=json.loads((B/'quaternion-additive-draft.json').read_text(encoding='utf8'))
CONTENT={
 'B02':('같은 물체의 위치와 자세를 나누기','전체 질문: 네 숫자는 무엇을 저장할까?','위치 이동 → 방향 변화는 별도'),
 'B03':('평면의 방향 계산을3D로 넓히려면','(a,b) → (-b,a) / 길이 유지','공간에서는 축도 필요 → 네 성분'),
 'B04':('축과 각도를 어떤 숫자로 넣을까?','q=[w,x,y,z] / 세 공간 방향','+z축 90° → w와 z에 각도 정보'),
 'B05':('저장한 값과 눈에 보이는 자세 연결','수치 예제: +z 90° / 반각 45°','몸체에 붙은 방향들이 함께 회전'),
 'B06':('한 회전을 두 번 이어 붙이면?','축과 단위 길이를 정한 qz(90°)','같은 축 90° + 90° → 곱으로 합성'),
 'B07':('숫자의 부호가 바뀌어도 같은 자세?','Z360°의 저장값: [-1,0,0,0]','q와 -q / 수의 값과 회전 결과 구분'),
 'B08':('끝 자세가 같으면 과정도 같을까?','q와 -q: 같은 회전 결과','지나온 회전 이력은 별도 정보'),
 'B09':('회전을 하지 않는 연산의 값은?','끝 자세와 회전 과정을 구분','곱해도 입력이 그대로 남는 값'),
 'B10':('네 숫자의 길이를 왜 확인할까?','항등원 [1,0,0,0] / 길이1','같은 비율 [3,0,0,4] / 길이5'),
 'B11':('저장값의 길이와 이동 속도 구분','[0.6,0,0,0.8] / 길이1','위치는 움직여도 현재 자세의 길이는1'),
 'B12':('저장한 회전을 어떻게 되돌릴까?','속도와 현재 자세는 별도','계산 예시: +z 90° 뒤 -z 90°'),
 'B13':('단위가 아닌 값도 켤레로 되돌릴까?','단위 q: q q* = [1,0,0,0]','q=[2,0,0,0] / q q*=[4,0,0,0]'),
 'B14':('역원은 경로를 역주행하는 것일까?','일반 역원: 2 × 0.5 = 1','회전 입력 복원 / 이동 기록은 별도'),
 'B15':('두 회전의 결과를 하나로 저장하려면','한 번의 회전과 역원을 확인','고정 X90° 후 Y90° → qy qx'),
 'B16':('같은 두 회전의 순서만 바꾸면?','외적: x×y=+z / y×x=-z','+z 입력 / X→Y와 Y→X 결과 비교'),
 'B17':('몸이 돌면 몸에 붙은 기준도 돌까?','고정 축의 순서: 두 결과가 다름','월드 y는 고정 / 몸의 y는 함께 회전'),
 'B18':('현재에서 목표까지 무엇을 더할까?','월드 기준과 몸체 기준을 구분','같은 +z축: 현재30° → 목표90°'),
 'B19':('필요한 회전 차이는 얼마나 클까?','현재30° + 차이60° = 목표90°','네 성분의 내적 → 최소 끝 자세 각도'),
 'B20':('목표 위치와 목표 자세는 같은가?','최소 각도: 끝 자세 사이의 차이','남은 위치 거리 / 자세 차이를 따로'),
 'B21':('목표까지 한 번에 돌지 않으려면','목표 회전을 계산한 상태','먼저 같은 축의 회전량 일부 적용'),
 'B22':('저장값을 실제 방향에 적용하려면','Z90°의 절반 회전 Z45°를 확인','앞의 반각 검산: Z90° / v=(1,0,1)'),
 'B23':('계산 결과와 카메라 화면 연결','v=(1,0,1) → v′=(0,1,1)','몸체 방향 / 투영하는 카메라 구분'),
 'B24':('그림의 계산을 코드에서도 재현하려면','방향 v′=(0,1,1)를 직접 검산','wxyz · Hamilton · 오른손 · 열벡터'),
 'B25':('같은 입력을 직접 돌리고 되돌리기','코드의 성분 순서와 좌표 약속 확인','q=[c,0,0,c] / v=(1,0,1) / c=√2/2'),
 'B26':('첫 질문에 계산 결과로 답하기','q v q⁻¹ 뒤 q⁻¹ v′ q → 입력 복원','네 숫자: 자세 저장·합성·차이·벡터 회전')
}
class Bridge(ThreeDScene):
 sid='B02'
 def construct(self):
  self.camera.background_color=WHITE
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  title,prior,next_question=CONTENT[self.sid];O=screen_point(-3.1,-.3)
  timing=ROOT/'shared/output/game-math-part2-teaching-revision/bridge-timing.json'
  slot=json.loads(timing.read_text(encoding='utf8')).get(self.sid) if timing.exists() else None
  if os.environ.get('REVISION_FINAL_TIMING')=='1' and slot is None:raise RuntimeError('Current-hash measured alignment is required for final '+self.sid)
  total=slot['seconds'] if slot else 9.5;switch=slot.get('questionStart',total*.46) if slot else total*.46
  self.add_fixed_in_frame_mobjects(fit(txt(title,38),12.4).to_corner(UL,buff=.6),txt('앞의 결과 → 남은 질문 → 다음 계산 / 오른손·Hamilton·wxyz',19,MUTED).move_to([0,2.67,0]))
  def readable_label(content,color):
   lines=content.split(' / ')
   if len(lines)==1:return fit(txt(content,27,color),6.1).move_to([3.2,-1.8,0])
   group=VGroup(*[fit(txt(line,27,color),6.1) for line in lines]).arrange(DOWN,aligned_edge=LEFT,buff=.16)
   if group.height>.95:group.scale(.95/group.height)
   return group.move_to([3.2,-1.8,0])
  prior_label=readable_label(prior,GREEN);self.add_fixed_in_frame_mobjects(prior_label)
  formula=None
  def equation(text,color=GOLD):
   nonlocal formula
   if formula is not None:self.remove(formula)
   formula=fit(txt(text,28,color),6).move_to([3.2,.2,0]);self.add_fixed_in_frame_mobjects(formula)
  initial=np.eye(3)
  if self.sid in ['B05','B06','B12','B14','B20','B21','B25']:initial=rz(PI/2)
  if self.sid=='B08':initial=rz(PI/2)
  if self.sid=='B11':initial=rz(2*np.arccos(.6))
  if self.sid=='B17':initial=rx(PI/2)
  if self.sid in ['B18','B19']:initial=rz(PI/6)
  if self.sid=='B22':initial=rz(PI/4)
  if self.sid in ['B23','B24','B26']:initial=rz(PI/2)
  obj=basis(initial,O,scale=1.7).scale(1.5,about_point=O);self.add(obj)
  self.add(VGroup(*[DashedLine(O-2.6*P[:,j],O+2.6*P[:,j],color=RULE,stroke_width=1) for j in range(3)]))
  self.add_fixed_in_frame_mobjects(VGroup(txt('x',22,RED),txt('y',22,GREEN),txt('z',22,BLUE)).arrange(RIGHT,buff=.7).move_to([-3.1,-2.2,0]))
  if self.sid=='B02':equation('위치 p / 자세 q',BLUE)
  elif self.sid in ['B03','B04']:equation('q = [w, x, y, z]')
  elif self.sid=='B05':equation('q = [c,0,0,c] / c=√2/2')
  elif self.sid=='B06':equation('qz(90°) × qz(90°)')
  elif self.sid=='B07':equation('[-1,0,0,0] / 처음과 같은 자세')
  elif self.sid=='B08':equation('R(q) = R(-q)')
  elif self.sid=='B09':equation('? × q = q')
  elif self.sid=='B10':equation('[3,0,0,4] / √(9+16)=5')
  elif self.sid=='B11':equation('q=[0.6,0,0,0.8] / ||q||=1')
  elif self.sid=='B12':equation('q=[c,0,0,c] / 단위 q')
  elif self.sid=='B13':equation('단위 q: q q* = 1',GREEN)
  elif self.sid=='B14':equation('q⁻¹=q*/||q||²')
  elif self.sid in ['B15','B16']:equation('X90° 후 Y90° / qy qx')
  elif self.sid=='B17':equation('world: Δq / body: qΔ')
  elif self.sid in ['B18','B19']:equation('Z30° → Δ → Z90°')
  elif self.sid=='B20':equation('현재 자세 / 목표 자세')
  elif self.sid=='B21':equation('Z90° → Z45°')
  elif self.sid=='B22':equation('저장값 → 실제 방향 v',BLUE)
  elif self.sid in ['B23','B24']:equation('v′=(0,1,1) / z 성분 유지')
  elif self.sid=='B25':equation('같은 입력: v=(1,0,1)')
  elif self.sid=='B26':equation('v=(1,0,1) 복원',GREEN)
  vector=None
  if self.sid in ['B22','B25']:vector=arrow(O,O+1.35*P@np.array([1.,0,1]),GOLD,6);self.add(vector)
  if self.sid in ['B23','B24','B26']:vector=arrow(O,O+1.35*P@np.array([0.,1,1]),GOLD,6);self.add(vector)
  if switch>self.renderer.time:self.wait(switch-self.renderer.time,frozen_frame=True)
  self.remove(prior_label);question_label=readable_label(next_question,INK);self.add_fixed_in_frame_mobjects(question_label)
  if self.sid=='B02':
   self.play(obj.animate.shift(.8*P[:,0]),run_time=.7);self.play(Rotate(obj,PI/2,axis=P[:,2],about_point=O+.8*P[:,0]),run_time=.9)
  elif self.sid=='B03':self.play(Indicate(obj[1],color=GOLD),run_time=.7)
  elif self.sid=='B04':self.play(Indicate(obj[1][2],color=GOLD),run_time=.7);equation('n=(0,0,1) / θ=90°',BLUE)
  elif self.sid=='B05':self.play(Rotate(obj,-PI/2,axis=P[:,2],about_point=O),run_time=.6);self.play(Rotate(obj,PI/2,axis=P[:,2],about_point=O),run_time=.9)
  elif self.sid=='B06':self.play(Rotate(obj,PI/2,axis=P[:,2],about_point=O),run_time=1.1);equation('[0,0,0,1] / Z180°',GREEN)
  elif self.sid=='B07':equation('[1,0,0,0] / 같은 자세',BLUE)
  elif self.sid=='B08':self.play(Rotate(obj,2*PI,axis=P[:,2],about_point=O),run_time=1.6);equation('과정 360° 추가 / 끝 자세 유지',BLUE)
  elif self.sid=='B09':equation('[1,0,0,0] × q = q',GREEN);self.play(Indicate(obj),run_time=.7)
  elif self.sid=='B10':equation('[0.6,0,0,0.8] / 길이1',GREEN)
  elif self.sid=='B11':self.play(obj.animate.shift(P[:,0]),run_time=1.1)
  elif self.sid in ['B12','B14']:self.play(Rotate(obj,-PI/2,axis=P[:,2],about_point=O),run_time=1.2);equation('계산 예시: 원래 자세로 복원',GREEN)
  elif self.sid=='B13':equation('q=[2,0,0,0] / 2×2=4 ≠ 1',RED)
  elif self.sid=='B15':self.play(Rotate(obj,PI/2,axis=P[:,0],about_point=O),run_time=.7);self.play(Rotate(obj,PI/2,axis=P[:,1],about_point=O),run_time=.7)
  elif self.sid=='B16':
   left=arrow(O,O+2.55*P@np.array([0,-1.,0]),GREEN,6);right=arrow(O,O+2.55*P@np.array([1.,0,0]),RED,6)
   self.play(Create(left),Create(right),run_time=.8);equation('같은 +z 입력 → -y / +x',GREEN)
  elif self.sid=='B17':
   fixed=arrow(O,O+2.55*P[:,1],GREEN,5);self.play(Create(fixed),Indicate(obj[1][1],color=GOLD),run_time=.8);equation('고정 y / 몸체 y: 서로 다른 기준',GREEN)
  elif self.sid in ['B18','B19']:
   self.play(Rotate(obj,PI/3,axis=P[:,2],about_point=O),run_time=1.1);equation('Δ=Z60° / 재적용하면 목표90°',GREEN)
  elif self.sid=='B20':self.play(obj.animate.shift(.7*P[:,0]),run_time=.7);equation('위치 이동 ≠ 자세 회전',BLUE)
  elif self.sid=='B21':self.play(Rotate(obj,-PI/4,axis=P[:,2],about_point=O),run_time=1.1)
  elif self.sid=='B22':
   self.play(Rotate(obj,PI/4,axis=P[:,2],about_point=O),run_time=.8);equation('앞의 약속: +z90°를 벡터에 적용',GREEN)
  elif self.sid=='B23':self.play(Indicate(vector,color=GOLD),run_time=.7)
  elif self.sid=='B24':equation('입력·곱 순서·출력 규약을 확인',BLUE)
  elif self.sid=='B25':self.play(Indicate(vector),run_time=.7)
  elif self.sid=='B26':self.play(Rotate(vector,-PI/2,axis=P[:,2],about_point=O),Rotate(obj,-PI/2,axis=P[:,2],about_point=O),run_time=1.1)
  if total>self.renderer.time:self.wait(total-self.renderer.time,frozen_frame=True)
for item in D['bridges']:
 globals()[item['id']]=type(item['id'],(Bridge,),{'sid':item['id'],'__module__':__name__})
