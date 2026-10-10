"""Thirteen independent, narration-timed prerequisites and causal connections.

Same objects and coordinate axes persist within each worked example. White
palette belongs to this already-started lecture; all values are defined examples.
"""
from pathlib import Path
import sys,json,os
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import txt,fit,P,arrow,basis,rz,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD
from quaternion import screen_point
B=ROOT/'production/batches/game-math-part2-teaching-revision'
O=ROOT/'shared/output/game-math-part2-teaching-revision/lines'
draft=json.loads((B/'lines-bounds-flow-draft.json').read_text(encoding='utf8'))
CONTENT={s['id']:s for s in draft['additions'] if s['id'] not in draft['omitUnrecorded']}
CONTENT['LB06']=next(s for s in json.loads((ROOT/'projects/game-math-bounds-transform-v2/production/lesson.json').read_text(encoding='utf8'))['scenes'] if s['id']=='LB06')

class LinesAddition(ThreeDScene):
 sid='LF01'
 def construct(self):
  self.camera.background_color=WHITE
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  record=CONTENT[self.sid]
  slot=json.loads((O/'combined-addition-timing.json').read_text(encoding='utf8'))[self.sid]
  if os.environ.get('REVISION_FINAL_TIMING')=='1':
   slots=[]
   for slug in ['game-math-lines-circles-v2','game-math-bounds-transform-v2']:
    timeline_path=ROOT/f'projects/{slug}/production/timeline.json'
    if timeline_path.exists():slots.extend(s for s in json.loads(timeline_path.read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
   assert len(slots)==1 and slots[0]['voiceSha256']==slot['voiceSha256']
   slot=slots[0]
  total=slot['seconds'];starts=slot['lineStarts'];origin=screen_point(-3.2,-.15)
  self.add_fixed_in_frame_mobjects(fit(txt(record['title'],36),12.4).to_corner(UL,buff=.6),txt('정의한 계산 예시 / 같은 점·축·단위로 입력 → 결과를 연결',19,MUTED).move_to([0,2.67,0]))
  label=None;formula=None
  def fixed(text,where,color=INK,size=27):
   group=VGroup(*[fit(txt(r,size,color),6.05) for r in text.split(' / ')]).arrange(DOWN,aligned_edge=LEFT,buff=.17)
   if group.height>1.15:group.scale(1.15/group.height)
   group.move_to(where);self.add_fixed_in_frame_mobjects(group);return group
  def explain(text,color=INK):
   nonlocal label
   if label is not None:self.remove(label)
   label=fixed(text,[3.2,-1.75,0],color)
  def equation(text,color=GOLD):
   nonlocal formula
   if formula is not None:self.remove(formula)
   formula=fixed(text,[3.2,.35,0],color,29)
  def wait_to(t):
   if t>self.renderer.time:self.wait(t-self.renderer.time,frozen_frame=True)
  def at_line(i):wait_to(starts[i])
  def at_sentence(fragment):
   found=[c for c in slot.get('sentenceCues',[]) if fragment in c['text']]
   if len(found)!=1:raise RuntimeError(f'{self.sid}: one spoken sentence required: {fragment}')
   wait_to(found[0]['start'])
  def pt(x,y,z=0,scale=1):return origin+scale*P@np.array([x,y,z],dtype=float)
  def point(q,color=RED):return Dot3D(q,radius=.085,color=color,resolution=(8,8))
  def plane_axes(scale=2.4):
   axes=VGroup(arrow(pt(-scale,0),pt(scale,0),RED),arrow(pt(0,-scale),pt(0,scale),GREEN))
   face=Polygon(*[pt(x,y,-.035) for x,y in [(-scale,-scale),(scale,-scale),(scale,scale),(-scale,scale)]],fill_color=BLUE,fill_opacity=.045,stroke_color=RULE,stroke_width=1)
   self.add(face,axes);return VGroup(face,axes)
  def box(dim=(3,2,1.8),color=BLUE):
   cube=Cube(side_length=1,fill_color=color,fill_opacity=.11,stroke_color=color,stroke_width=2)
   for i,d in enumerate(dim):cube.stretch(d,i)
   return cube.apply_matrix(P).move_to(origin)
  def circle(radius=1.6):return ParametricFunction(lambda a:pt(radius*np.cos(a),radius*np.sin(a)),t_range=[0,TAU],color=BLUE,stroke_width=4)
  def caption(text):self.add_fixed_in_frame_mobjects(fit(txt(text,21,MUTED),5.4).move_to([-3.2,-2.22,0]))
  if self.sid in ['LF01','LF02','LF03']:
   obj=basis(np.eye(3),origin,scale=1.6);self.add(obj)
   a=pt(-2,0);b=pt(2,0);ends=VGroup(point(a,RED),point(b,GREEN));line=Line3D(a,b,color=GOLD,thickness=.025)
   if self.sid=='LF01':
    equation('앞 편: 물체의 자세를 계산함');explain('다음 질문 / 어디에서 어디로 연결할까?',GREEN)
    at_line(1);self.play(FadeOut(obj),Create(ends),Create(line),run_time=.85);equation('① 표현 선택 / ② 두 점 → 중간점 / ③ 세로선·같은 거리');caption('같은 연결선의 출발점과 끝점')
   elif self.sid=='LF02':
    self.remove(obj);self.add(ends,line);equation('두 점 → 점 생성 / 세로선도 표현 가능');explain('지금 얻은 연결선의 결과',GREEN)
    at_line(1);enclosure=box();self.play(Create(enclosure),run_time=.85);equation('다음 편 / 선이 닿을 대상의 크기는?');explain('구·상자로 대상의 범위를 감쌈');caption('연결선 → 대상이 차지하는 범위')
   else:
    self.remove(obj);self.add(ends,line);equation('앞 편: 선의 위치·범위를 정함');explain('대상의 크기도 있어야 / 닿을 범위를 검사',GREEN)
    at_line(1);sphere=Sphere(radius=1.7,resolution=(12,24),fill_color=BLUE,fill_opacity=.13,stroke_width=.4).move_to(origin);self.play(Create(sphere),run_time=.9)
    equation('① 구 / ② 축별 최소·최대 상자 / ③ 회전 뒤 경계 갱신');explain('같은 대상을 더 구체적으로 검사');caption('설명용 범위 / 게임 엔진 측정값 아님')
  elif self.sid=='LB01':
   a=pt(-2,0);b=pt(2,0);line=Line3D(a,b,color=GOLD,thickness=.025);self.add(point(a),point(b,GREEN),line)
   equation('같은 연결선 / 필요한 계산부터 정하기');explain('익숙한 원으로 세 질문을 비교',GREEN)
   at_line(1);self.play(FadeOut(line),Create(circle()),run_time=.8)
   q=point(pt(1.6,0),GOLD);inside=point(pt(.6,.7),GREEN);self.add(q,inside)
   self.play(MoveAlongPath(q,circle()),run_time=1.8,rate_func=linear)
   equation('저장: 중심·반지름 / 생성: 원 위의 점 / 검사: 주어진 점의 거리');explain('원에서 나눈 질문 / 같은 연결선에도 적용');caption('형태는 같아도 작업에 따라 식을 선택')
  elif self.sid=='LC04':
   plane_axes(2.1);self.add(circle());equation('원: 저장 / 점 생성 / 점 검사');explain('같은 모양을 다른 질문으로 계산',GREEN)
   at_sentence('이제 원 대신');self.play(Create(Line3D(pt(-2,0),pt(2,0),color=GOLD,thickness=.025)),run_time=.8);equation('이제 같은 질문을 선에 적용 / 먼저 연결점·방향 관찰');caption('원에서 구별한 목적 → 연결선의 표현')
  elif self.sid=='LP01':
   # Uniform drawing scale; coordinate labels retain the explicitly stated meters.
   shift=np.array([5,2.5,0.]);draw=lambda q:origin+.65*P@(np.array(q)-shift)
   a=draw([2,1,0]);b=draw([8,4,0]);mid=draw([5,2.5,0])
   self.add(point(a,RED),point(b,GREEN),Line3D(a,b,color=GOLD,thickness=.025));moving=point(a,GOLD);self.add(moving)
   equation('o=(2,1)m / 끝점=(8,4)m / δ=(6,3)m');explain('같은 두 점 / 티의 단위를 먼저 확인',GREEN)
   at_line(1);self.play(moving.animate.move_to(mid),run_time=1);equation('t=.5 (단위 없음) / o+.5δ=(5,2.5)m');explain('선분의 절반 비율',GREEN)
   at_line(2);unit=arrow(a,a+.65*P@np.array([6,3,0])/np.sqrt(45),BLUE,6);self.play(Create(unit),run_time=.7);equation('‖δ‖=√45m / 단위 방향 δ/√45');explain('길이1 방향 / 거리와 분리')
   at_sentence('여기에 거리인');self.play(moving.animate.move_to(a),run_time=.35);self.play(moving.animate.move_to(mid),run_time=1);equation('거리 s=√45/2 m / o+s(δ/√45)=(5,2.5)m');explain('같은 중간점 / 비율 t와 거리 s는 다른 입력',GREEN)
   at_line(3);caption('단위 없는 비율 / 미터로 재는 거리');explain('같은 결과 → 모든 방향의 선도 표현할까?',GREEN)
  elif self.sid=='LB02':
   # x=1 is a bisector of A/B, not their connecting line.
   # One uniform scale, centered at(1,2); the y-axis passes through A=(0,0).
   draw=lambda x,y:origin+.65*P@np.array([x-1,y-2,0.])
   face=Polygon(*[draw(x,y)-.025*P[:,2] for x,y in [(-.6,-.5),(2.6,-.5),(2.6,4.4),(-.6,4.4)]],fill_color=BLUE,fill_opacity=.045,stroke_color=RULE,stroke_width=1)
   self.add(face,arrow(draw(-.6,0),draw(2.6,0),RED),arrow(draw(0,-.5),draw(0,4.4),GREEN))
   a=draw(0,0);b=draw(2,0);q=draw(1,4)
   self.add(point(a,RED),point(b,GREEN),point(q,GOLD));links=VGroup(Line3D(a,q,color=RED,thickness=.018),Line3D(b,q,color=GREEN,thickness=.018));self.add(links)
   equation('A=(0,0), B=(2,0) / P=(x,y): 같은 거리?');explain('두 점을 잇는 것과 별개의 질문',GREEN)
   at_line(1);equation('AP²=x²+y² / BP²=(x−2)²+y²');self.play(Indicate(links),run_time=.7)
   at_line(2);self.play(Create(Line3D(draw(1,-.5),draw(1,4.4),color=BLUE,thickness=.025)),run_time=.8);equation('x²+y²=(x−2)²+y² / 4x=4 → x=1');explain('같은 거리인 점들의 세로선',BLUE)
   at_line(3);normal=arrow(draw(1,2),draw(3,2),GOLD,6);self.play(Create(normal),run_time=.7);equation('직각 방향 n=(2,0) / n·P=2x=2 → x=1');explain('법선·내적 / 방금 얻은 같은 세로선');caption('좌표 원점 A / P=(1,4) / 가운데 세로선 x=1')
  elif self.sid=='LP02':
   axes=VGroup(*[arrow(origin-2.1*P[:,j],origin+2.25*P[:,j],c) for j,c in enumerate([RED,GREEN,BLUE])]);sphere=Sphere(radius=1.55,resolution=(16,24),fill_color=BLUE,fill_opacity=.12,stroke_width=.4).move_to(origin);self.add(axes,sphere)
   q=point(origin,GOLD);self.add(q);equation('구: 중심에서 같은 거리 / 반지름 r=2');explain('2D 원의 거리 질문을 세 축으로',GREEN)
   at_line(1);self.play(q.animate.move_to(origin+1.55*P[:,0]),run_time=1);equation('차이(2,0,0) / 거리²=4=r² → 경계');explain('같은 중심을 기준으로 검사',BLUE)
   at_line(2);self.play(q.animate.move_to(origin+2.325*P[:,0]),run_time=1);equation('차이(3,0,0) / 거리²=9>4 → 바깥');explain('중심을 빼기 → 제곱합 → 같은 r² 비교',RED);caption('길이 단위는 동일 / 거리²는 제곱 단위')
  elif self.sid=='LC13':
   obj=box((3.7,.65,.65),GREEN);sphere=Sphere(radius=1.95,resolution=(12,24),fill_color=BLUE,fill_opacity=.08,stroke_width=.3).move_to(origin);self.add(obj,sphere)
   equation('긴 물체를 구로 감쌈 / 옆의 빈 공간도 포함');explain('구는 쉬운 범위 / 모양에 따라 여유가 큼',GREEN)
   at_line(1);self.play(FadeOut(sphere),Create(box((3.9,.85,.85))),run_time=1);equation('같은 물체 / x·y·z 최소·최대로 상자');explain('축별 퍼짐을 따로 저장');caption('보이는 모양 / 정의한 경계를 구분')
  elif self.sid=='LP03':
   # 1D line on a tilted plane preserves positions as labels are sorted.
   draw=lambda x:pt((x-4.5)*.75,0)
   self.add(Line3D(draw(1),draw(8),color=RULE,thickness=.012));dots=VGroup(*[point(draw(x),c) for x,c in [(2,RED),(4,GOLD),(7,GREEN)]]);self.add(dots)
   equation('한 축의 점: 2, 4, 7');explain('위치는 유지 / 가장 작은 값과 큰 값 찾기',GREEN)
   at_line(1);bound=Line3D(draw(2),draw(7),color=BLUE,thickness=.028);self.play(Create(bound),run_time=.8);equation('최소2 / 최대7 / 중심 c=(2+7)/2=4.5');self.add(point(draw(4.5),BLUE))
   at_sentence('중심은 둘의 평균');half=arrow(draw(4.5),draw(7),GOLD,6);self.play(Create(half),run_time=.7);equation('반크기 e=(7−2)/2=2.5 / c−e=2, c+e=7');explain('반크기는 중심에서 한쪽 끝까지',GREEN)
   at_line(2);self.play(FadeOut(dots),FadeOut(bound),FadeOut(half),Create(box()),run_time=.9);equation('3D에서는 축별로 같은 계산 / 최소·최대 각3개');explain('다음 다섯 점 코드 / 첫 점으로 초기화');caption('한 축 구간 → 세 축의 공간 범위')
  elif self.sid=='LB04':
   draw=lambda x,y:pt((x-3.5)*.65,y)
   one=Line3D(draw(1,.65),draw(4,.65),color=RED,thickness=.035);two=Line3D(draw(3,-.05),draw(6,-.05),color=GREEN,thickness=.035);self.add(one,two)
   equation('축별 최소·최대가 있음 / 두 구간이 겹치는가?');explain('한 축부터 동일한 숫자로 비교',GREEN)
   at_line(1);overlap=Line3D(draw(3,.3),draw(4,.3),color=BLUE,thickness=.05);self.play(Create(overlap),run_time=.8);equation('[1,4]∩[3,6] / 시작=max(1,3)=3 / 끝=min(4,6)=4');explain('시작≤끝 / 겹치는 구간[3,4]',BLUE)
   at_line(2);self.play(Transform(one,Line3D(draw(1,.65),draw(2,.65),color=RED,thickness=.035)),Transform(two,Line3D(draw(3,-.05),draw(5,-.05),color=GREEN,thickness=.035)),FadeOut(overlap),run_time=.8);equation('[1,2]와[3,5] / 시작3>끝2 → 겹침 없음');explain('3D는 x·y·z 검사를 모두 통과',RED)
   at_line(3);equation('경계 접촉도 겹침으로 정의 / 한 축이라도 실패 → 상자 분리');explain('상자가 겹쳐도 / 실제 모양 접촉은 별도 검사');caption('판정의 경계 포함 약속을 먼저 정함')
  elif self.sid=='LC18':
   # Start the next supplied example: the same side-two square remains in18.
   obj=box((2,2,.12),GREEN);bound=box((2,2,.14));self.add(obj,bound)
   equation('상자 겹침은 후보 / 실제 접촉은 별도 검사');explain('유효한 경계 / 물체 전체를 계속 감싸야 함',GREEN)
   at_line(1);self.play(Rotate(obj,PI/4,axis=P[:,2],about_point=origin),run_time=1);equation('같은 물체를 회전 / 옛 최소·최대로 충분한가?');explain('극값을 주는 꼭짓점이 바뀜',RED)
   updated=box((2*np.sqrt(2),2*np.sqrt(2),.14));self.play(Transform(bound,updated),run_time=.85);caption('다음 계산의 정사각형 / 같은 물체를 계속 사용')
  elif self.sid=='LB06':
   obj=box((2,2,.12),GREEN);bound=box((2*np.sqrt(2),2*np.sqrt(2),.14));self.add(obj,bound)
   self.play(Rotate(obj,PI/4,axis=P[:,2],about_point=origin),run_time=.75)
   equation('앞의 계산: 고정된 축 / 같은 정사각형을45° 회전');explain('정의한 예시 각도 / 게임 화면의 측정값 아님',GREEN)
   caption('물체의 회전과 카메라 이동을 구분 / 다음은 정지한 구조물')
  elif self.sid=='LB05':
   # Two separated rows are the same numeric axis before/after the affine map.
   draw=lambda x,y:pt((x+3)*.22,y)
   a=point(draw(3,.8),RED);b=point(draw(7,.8),GREEN);center=point(draw(5,.8),GOLD);line=Line3D(draw(3,.8),draw(7,.8),color=BLUE,thickness=.035);self.add(a,b,center,line)
   equation('입력[3,7] / 중심 c=5, 반크기 e=2');explain('위치의 방향 / 퍼진 크기는 구별',GREEN)
   at_line(1);equation('x′=−2x+1 / 같은 두 끝점에 적용');explain('중심5, 반크기2 / 삼부터 칠의 같은 구간')
   at_line(2);self.play(a.animate.move_to(draw(-5,-.5)),b.animate.move_to(draw(-13,-.5)),center.animate.move_to(draw(-9,-.5)),Transform(line,Line3D(draw(-13,-.5),draw(-5,-.5),color=BLUE,thickness=.035)),run_time=1.2);equation('3→−5, 7→−13 / 정렬[−13,−5] / c′=−9, e′=4');explain('e′=|−2|·2=4 / 반크기는 음수가 아님',GREEN);self.play(Indicate(line),run_time=.7)
   at_line(3);equation('세 축의 최대 퍼짐을 더함 / c′=Ac+t, e′=|A|e');explain('점들의 경계와 / 빈 공간을 포함한 상자 경계 구분');caption('색은 원래 끝점의 정체성을 유지')
  else:raise RuntimeError(self.sid)
  if self.renderer.time>total+.05:raise RuntimeError(f'{self.sid}: added motion exceeds its spoken slot')
  wait_to(total)

for ident in CONTENT:globals()[ident]=type(ident,(LinesAddition,),{'sid':ident,'__module__':__name__})
