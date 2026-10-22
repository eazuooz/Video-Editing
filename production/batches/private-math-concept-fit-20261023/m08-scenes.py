"""A fixed assembly part makes representation changes distinct from physical rotation."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('assembly_style',Path(__file__).with_name('m06-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
q=v.q;text=v.text;BG=v.BG;FG=v.FG;YELLOW=v.YELLOW;X=v.X;Y=v.Y;Z=v.Z;base=v.base
TITLES={'17':'같은 자세 · 다른 기록 형식','IG03':'부품에 붙은 축의 방향 성분','IG04':'입력 축을 구분하고 열을 읽기','20':'앞쪽과 위쪽이 함께 일치해야 같은 자세','IG11':'고정된 한 자세를 바꿔 적기','IG05':'표현 변환 / 실제 추가 회전','IG08':'고정된 물체를 다른 카메라에서 보기','23':'변환해도 세 축의 관계는 그대로','IG09':'한 방향만으로 알 수 없는 비틀림','IG06':'같은 입력끼리 결과 검산'}
PHRASES={
 '17':['선택한 부품과 주변 구조','화면 변화 ≠ 물체 자세 변화','위치·자세 고정 · 기록 형식만 변경','표현 변환은 추가 회전이 아님','숫자 모양보다 세 축의 결과 비교','같은 기준의 같은 자세'],
 'IG03':['빨간 X축의 방향 성분','고정 기준축 / 카메라 투영 구분','다음: 고정된 축 위 삼각형'],
 'IG04':['빨간 X축 / 파란 Z축','같은 행렬의 서로 다른 열','입력이 같을 때 결과를 비교'],
 '20':['앞쪽·위쪽을 함께 비교','위치와 속도는 별개','모형에서 정한 회전값','앞만 같고 위가 다르면 다른 자세','같은 입력으로 수학적 검산','다음: 반 바퀴 근처의 변환'],
 'IG11':['같은 물체의 두 축','한 순간 자세 고정','각도 / 쿼터니언 / 행렬','다음: 왕복 계산으로 확인'],
 'IG05':['부품 위치·자세 고정','행렬 → 쿼터니언 · 자세 그대로','이번에는 실제 추가 회전','표현 변환과 회전 적용을 구분'],
 'IG08':['물체 고정 · 카메라만 이동','화면 기울기 ≠ 3D 회전각','자세는 그대로 · 투영만 변화','검산에는 정의된 축·회전값 필요'],
 '23':['앞쪽·위쪽을 함께 기록','물체의 세 축 / 카메라 기준','축의 관계를 보존하는 변환','오른손 규칙과 축 방향 유지','정한 입력과 결과를 비교','다음: 축·각과 왕복 변환'],
 'IG09':['빨간 방향만으로 부족','파란 축의 비틀림을 함께 관찰','보이지 않는 정보는 추정하지 않음','같은 입력과 예외 규칙으로 검사'],
 'IG06':['같은 부품의 X축과 Z축','서로 다른 입력은 따로 비교','카메라·축을 고정한 검산','다음: 점을 선과 경계로 정의']}
class Replacement(ThreeDScene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG;self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  self.add_fixed_in_frame_mobjects(text(TITLES[self.sid],35,YELLOW).to_corner(UL,buff=.5),text('우리 모형 · 오른손 / 열벡터',20,q.v.SECOND).to_corner(UR,buff=.5))
  origin=q.pos(-3.35,-.15);obj=v.rig(origin,scale=1.2);R=rotation_matrix(PI/4 if self.sid in ['17','23','IG06'] else PI/2,OUT);obj.apply_matrix(R,about_point=origin)
  self.add(VGroup(*[DashedLine(origin-2*np.eye(3)[:,i],origin+2.7*np.eye(3)[:,i],color=v.RULE,stroke_width=1.4) for i in range(3)]),obj)
  self.add_fixed_in_frame_mobjects(VGroup(text('X 앞',25,X),text('Y 옆',25,Y),text('Z 위',25,Z)).arrange(RIGHT,buff=.25).move_to([-3.2,-2.35,0]))
  active=None;metric=None
  def note(s,color=Y):
   nonlocal metric
   if metric:self.remove(metric)
   metric=base.fit(text(s,28,color),6.2).move_to([3,-.1,0]);self.add_fixed_in_frame_mobjects(metric)
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   if active:self.remove(active)
   active=base.fit(text(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)],29,FG),6.25).move_to([3,1.5,0]);self.add_fixed_in_frame_mobjects(active)
   if self.sid=='17':
    if i==2:note('軸·각: Z, 45°'.replace('軸','축'))
    if i==3:note('q = (cos22.5°, 0, 0, sin22.5°)')
    if i==4:note('Rz(45°) · 세 축의 결과는 동일')
   elif self.sid=='IG03':
    if i==0:note('Rz(90°): X → (0, 1, 0)',X)
    if i==2:note('삼각형은 별도의 고정 2D 예제')
   elif self.sid=='IG04':
    if i==0:note('X → (0,1,0) / Z → (0,0,1)')
    if i==1:note('R[:,0] = X 결과 / R[:,2] = Z 결과')
    if i==2:note('R·X 와 q·X·q⁻¹ 를 비교',X)
   elif self.sid=='20':
    if i==0:note('Z축 90° · 앞 X→Y / 위 Z→Z')
    if i==2:note('q = (√2/2, 0, 0, √2/2)')
    if i==3:self.play(Rotate(obj,PI/4,axis=R@RIGHT,about_point=origin),run_time=1.8);note('앞은 유지 / 위는 변경 → 다른 자세',YELLOW)
    if i==4:self.play(Rotate(obj,-PI/4,axis=R@RIGHT,about_point=origin),run_time=1.8);note('원래 자세로 복원 · 입력 고정')
   elif self.sid=='IG11':
    if i==1:note('Z축 90° · 위치와 자세 고정')
    if i==2:note('각도 ↔ q ↔ R · 같은 축 결과')
   elif self.sid=='IG05':
    if i==0:note('현재 자세: Z축 90°')
    if i==1:note('R → q · 물체는 그대로')
    if i==2:self.play(Rotate(obj,PI/4,axis=OUT,about_point=origin),run_time=2);note('실제 +45° 적용 → 총135°',YELLOW)
   elif self.sid=='IG08':
    if i==0:self.move_camera(theta=-32*DEGREES,run_time=3);note('월드 자세 고정')
    if i==2:self.move_camera(theta=-60*DEGREES,run_time=3);note('카메라만 변화 · 투영 방향은 변화')
   elif self.sid=='23':
    if i==0:note('모형 입력: Z축 45°')
    if i==3:note('X × Y = Z · 오른손 정규직교 기저')
    if i==4:note('R·X 와 q·X·q⁻¹ · 같은 결과')
   elif self.sid=='IG09':
    if i==0:note('빨간 축 방향은 유지',X)
    if i==1:self.play(Rotate(obj,PI/3,axis=R@RIGHT,about_point=origin),run_time=2);note('빨간 축 주위 비틀림 → 파란 축 변화',Z)
   elif self.sid=='IG06':
    if i==0:note('Rz(45°) · 두 입력을 별도 검사')
    if i==1:note('X → (√2/2, √2/2, 0) / Z → Z')
    if i==2:note('R과 q에서 같은 입력의 결과 일치')
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
