"""Independent, narrated, spatial additions; original explanation scenes are exact.

White is the preserved palette of this already-started lecture. Mathematical
values below are explicit worked examples, never recovered game-engine data.
"""
from pathlib import Path
import sys,json,os
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import txt,fit,basis,P,arrow,rz,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD
from quaternion import screen_point
B=ROOT/'production/batches/game-math-part2-teaching-revision'
O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'
flow=json.loads((B/'interpolation-flow-insertions.json').read_text(encoding='utf8'))
draft=json.loads((B/'interpolation-additive-draft.json').read_text(encoding='utf8'))
CONTENT={s['id']:s for s in flow['scenes']+draft['additions'] if s['id']!='IB16'}
CONTENT.update({s['id']:s for s in json.loads((B/'interpolation-worked-checks-v3.json').read_text(encoding='utf8'))['scenes']})
LABELS={
 'IF01':['현재 자세 → 목표 자세','사이의 자세는 어떻게 만들까?'],
 'IB03':['관찰: 연속으로 방향이 바뀜','끝값 네 숫자를 섞어도 될까?'],
 'IB07':['단위 호 위의 중간값','끝점이 거의 같으면 분모는?'],
 'IB09':['실제 카메라도 함께 움직임','계산 예시: 축·카메라 고정'],
 'IB12':['중간 자세 q(t)를 계산함','실제 시간 → t의 증가량'],
 'IB13':['경로와 시간 조건을 정함','한 바퀴의 기록도 남을까?'],
 'IB19':['각도에서 만든 같은 세 축','이번 입력은 쿼터니언'],
 'IB24':['같은 자세의 표현 변환','0°와180°에서 남는 정보는?'],
 'IB25':['예외 조건까지 처리함','45° 중간 자세·왕복 검산'],
 'IF02':['경로·단위 길이·시간·이력','같은 자세 → 다음 작업'],
 'IF03':['앞 편의 같은 중간 자세','규약 → 변환 → 같은 방향 검산']
}
class InterpolationAddition(ThreeDScene):
 sid='IF01'
 def construct(self):
  self.camera.background_color=WHITE
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  record=CONTENT[self.sid]
  timing=O/'combined-addition-timing.json';slot=json.loads(timing.read_text(encoding='utf8')).get(self.sid) if timing.exists() else None
  if os.environ.get('REVISION_FINAL_TIMING')=='1':
   measured=[]
   for slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']:
    timeline=ROOT/f'projects/{slug}/production/timeline.json'
    if timeline.exists():measured.extend(s for s in json.loads(timeline.read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
   if len(measured)!=1:raise RuntimeError('One measured episode slot required for '+self.sid)
   assert slot and measured[0]['voiceSha256']==slot['voiceSha256']
   slot=measured[0]
  if os.environ.get('REVISION_FINAL_TIMING')=='1' and slot is None:raise RuntimeError('Measured current-hash timing required for '+self.sid)
  total=slot['seconds'] if slot else 15.
  line_starts=slot['lineStarts'] if slot else [0.,4.,8.,11.]
  O3=screen_point(-3.1,-.3)
  self.add_fixed_in_frame_mobjects(fit(txt(record['title'],36),12.4).to_corner(UL,buff=.6),txt('같은 물체·같은 축을 이어서 계산 / 오른손·열벡터·Hamilton·wxyz',19,MUTED).move_to([0,2.67,0]))
  initial=PI/4 if self.sid in ['IP03','IF02','IF03','IB12','IB13','IB25'] else 0.
  obj=basis(rz(initial),O3,scale=1.7).scale(1.5,about_point=O3);self.add(obj)
  self.add(VGroup(*[DashedLine(O3-2.6*P[:,j],O3+2.6*P[:,j],color=RULE,stroke_width=1) for j in range(3)]))
  self.add_fixed_in_frame_mobjects(VGroup(txt('x',22,RED),txt('y',22,GREEN),txt('z',22,BLUE)).arrange(RIGHT,buff=.7).move_to([-3.1,-2.2,0]))
  label=None;formula=None;extra=[]
  def fixed(content,where,color=INK,size=27):
   rows=content.split(' / ');group=VGroup(*[fit(txt(r,size,color),6.1) for r in rows]).arrange(DOWN,aligned_edge=LEFT,buff=.17)
   if group.height>1.10:group.scale(1.10/group.height)
   group.move_to(where);self.add_fixed_in_frame_mobjects(group);return group
  def explain(content,color=INK):
   nonlocal label
   if label is not None:self.remove(label)
   label=fixed(content,[3.2,-1.75,0],color)
  def equation(content,color=GOLD):
   nonlocal formula
   if formula is not None:self.remove(formula)
   formula=fixed(content,[3.2,.35,0],color,29)
  def wait_to(t):
   if t>self.renderer.time:self.wait(t-self.renderer.time,frozen_frame=True)
  def at_line(index):wait_to(line_starts[index] if index<len(line_starts) else total*.65)
  def at_sentence(fragment):
   matches=[c for c in slot.get('sentenceCues',[]) if fragment in c['text']] if slot else []
   if len(matches)!=1:raise RuntimeError(f'{self.sid}: one current spoken sentence required: {fragment}')
   wait_to(matches[0]['start'])
  if self.sid.startswith('IB') or self.sid in ['IF01','IF02','IF03']:
   prior,question=LABELS[self.sid];explain(prior,GREEN)
   if self.sid=='IB07':equation('sin(α) → 0 / 두 단위 끝점이 가까워짐')
   elif self.sid=='IB12':equation('q(t) / t = f(실제 시간)')
   elif self.sid=='IB13':equation('현재 자세 / 추가 회전 이력은 별도')
   elif self.sid in ['IB19','IF02','IF03']:equation('같은 자세 / 각도 ↔ q ↔ R')
   elif self.sid=='IB24':equation('축·각 / 0°와180°')
   elif self.sid=='IB25':equation('t=.5 / 물체의 회전45°')
   elif self.sid=='IB03':equation('끝값 → ? → 끝값')
   else:equation('시작 q₀ / 목표 q₁')
   switch=slot.get('questionStart',total*.42) if slot else total*.42
   if self.sid in ['IF02','IF03']:switch=line_starts[1] if len(line_starts)>1 else switch
   wait_to(switch);explain(question)
   if self.sid=='IB13':
    self.play(Rotate(obj,2*PI,axis=P[:,2],about_point=O3),run_time=min(2.5,max(.6,total-self.renderer.time-.5)),rate_func=linear);equation('끝 방향은 같음 / 이력에는360° 추가',GREEN)
   elif self.sid=='IB12':
    ticks=VGroup(*[Line([-5.4+i*.85,1.8,0],[-5.4+i*.85,1.95,0],color=INK) for i in range(5)])
    self.add_fixed_in_frame_mobjects(ticks,txt('같은 시간 간격 → 같은 Δt인지 확인',19,MUTED).move_to([-3.7,2.18,0]));self.play(Indicate(obj[1],color=GOLD),run_time=.65)
   elif self.sid=='IB07':
    self.play(Rotate(obj,2*DEGREES,axis=P[:,2],about_point=O3),run_time=.7);equation('거의 같은 자세 / 정규화 선형 보간 분기',GREEN)
   elif self.sid=='IB03':
    self.play(Rotate(obj,PI/2,axis=P[:,2],about_point=O3),run_time=.9);equation('직접 원소 혼합 / 회전 구조 검사')
   elif self.sid=='IB25':
    v=arrow(O3,O3+2.1*P@np.array([1.,0,0]),GOLD,6);self.add(v)
    self.play(Rotate(v,PI/4,axis=P[:,2],about_point=O3),run_time=.9);equation('v′=(√2/2,√2/2,0)',GREEN)
   elif self.sid in ['IF01','IB09']:
    self.play(Rotate(obj,PI/4,axis=P[:,2],about_point=O3),run_time=1.0);equation('예시:0° → 45° → 90°',GREEN)
   else:self.play(Indicate(obj[1],color=GOLD),run_time=.7)
  elif self.sid=='IP01':
   equation('Δᵗ / 지수는 t, t²가 아님');explain('Δ는 앞 편에서 구한 회전 차이',GREEN)
   at_line(1);self.play(Rotate(obj,PI/4,axis=P[:,2],about_point=O3),run_time=1.2);equation('Δ=Z90°, t=.5 / Δᵗ=Z45°',GREEN)
   at_line(2);explain('같은 축 유지 / 중간 자세를 단위 호 위에')
  elif self.sid=='IP02':
   # This embedded circle is a 2D section, not the entire quaternion S³.
   center=O3;radius=2.0
   plane=Polygon(*[center+P@np.array([x,y,-.08]) for x,y in [(-2.3,-2.3),(2.3,-2.3),(2.3,2.3),(-2.3,2.3)]],stroke_color=RULE,fill_color=BLUE,fill_opacity=.07)
   circle=ParametricFunction(lambda a:center+P@np.array([radius*np.cos(a),radius*np.sin(a),0]),t_range=[0,TAU],color=RULE)
   self.remove(obj);self.add(plane);self.play(Create(circle),run_time=.8);equation('단위 원: 방향·각도를 읽는 예시')
   at_line(1)
   x=arrow(center,center+radius*P@np.array([1.,0,0]),RED,6);y=arrow(center,center+radius*P@np.array([np.sqrt(3)/2,.5,0]),GREEN,6)
   self.play(Create(x),Create(y),run_time=.8);equation('(1,0)·(√3/2,1/2) / = √3/2');explain('같은 자리 곱하기 → 합하기',GREEN)
   at_line(2);arc=ParametricFunction(lambda a:center+P@np.array([.85*np.cos(a),.85*np.sin(a),0]),t_range=[0,PI/6],color=GOLD,stroke_width=7)
   self.play(Create(arc),run_time=.7);equation('acos(√3/2)=30°',GREEN)
   at_line(3);equation('d=w₀w₁+x₀x₁+y₀y₁+z₀z₁ / α=acos(d)');explain('원은 네 성분 공간의 단면 / α와 물체 회전각을 구분')
  elif self.sid=='IP03':
   equation('같은 자세 / 동일한 세 몸체 축');explain('작업의 입력·출력이 다릅니다',GREEN)
   at_line(1);equation('각도 편집 → q로 보간·저장 / R로 많은 방향 벡터 변환');self.play(Indicate(obj[1][0],color=RED),run_time=.7)
  elif self.sid=='IP04':
   # Scale drawing coordinates uniformly; numerical labels are explicit units.
   a=O3;b=a+2.25*P[:,0];c=b+3.0*P[:,1]
   tri=VGroup(Line(a,b,color=RED,stroke_width=7),Line(b,c,color=GREEN,stroke_width=7),Line(a,c,color=GOLD,stroke_width=7))
   corner=VGroup(Line(b-.22*P[:,0],b-.22*P[:,0]+.22*P[:,1],color=INK),Line(b-.22*P[:,0]+.22*P[:,1],b+.22*P[:,1],color=INK))
   dimension3=txt('3',25,RED).move_to((a+b)/2-.28*P[:,1]);dimension4=txt('4',25,GREEN).move_to((b+c)/2+.28*P[:,0]);dimension5=txt('5',25,GOLD).move_to((a+c)/2-.28*P[:,0])
   self.remove(obj);self.play(Create(tri),run_time=.8);equation('hypot(가로,세로)=빗변 길이');explain('같은 직각삼각형의 세 변을 연결',GREEN)
   self.add(corner)
   at_sentence('가로 길이는 삼');equation('가로3 / 세로? / 빗변?')
   self.add_fixed_orientation_mobjects(dimension3)
   self.play(Indicate(tri[0],color=RED),run_time=.5)
   at_sentence('세로 길이는 사');equation('가로3 / 세로4 / 빗변?')
   self.add_fixed_orientation_mobjects(dimension4)
   self.play(Indicate(tri[1],color=GREEN),run_time=.5)
   at_sentence('삼의 제곱인 구');equation('3²+4²=9+16=25');explain('같은 입력3·4의 제곱합',GREEN)
   at_sentence('그 제곱근은 오');equation('hypot(3,4)=√25=5');explain('제곱합25 → 길이5',GREEN)
   self.add_fixed_orientation_mobjects(dimension5)
   self.play(Indicate(tri[2],color=GOLD),run_time=.5)
   at_line(1);self.remove(tri,corner,dimension3,dimension4,dimension5)
   direction=arrow(O3,O3+1.7*P@np.array([1.,1.,0]),GOLD,7);self.play(Create(direction),run_time=.7)
   equation('atan2(y,x) / atan2(1,1)=45°');explain('두 값의 부호 → 사분면도 읽기')
   at_line(2);self.remove(direction);self.add(obj);equation('특이 자세: 방향 정보가 겹침');explain('원래 각도가 하나로 정해지지 않음 / 별도 대표값 약속')
  elif self.sid=='IP05':
   equation('trace(R)=R₀₀+R₁₁+R₂₂');explain('왼쪽 위 → 오른쪽 아래 / 대각선 세 수의 합',GREEN)
   at_line(1);self.play(Rotate(obj,PI,axis=P[:,2],about_point=O3),run_time=1.2)
   equation('Z180°: -1 + -1 + 1 = -1 / 쿼터니언 w=0');explain('w로 계속 나눌 수 없습니다',RED)
   at_line(2);equation('큰 성분 z 선택 → q / 다시 R로 같은 회전 검산',GREEN);self.play(Indicate(obj[1][2],color=BLUE),run_time=.7)
  elif self.sid=='IP07':
   equation('계산 예시: z축0°→90° / 전체 시간1초');explain('경로와 시간 조건을 같은 예시로 비교',GREEN)
   at_line(1);equation('0.5초÷1초=.5 / t=.5 → 45°')
   target=basis(rz(PI/4),O3,scale=1.7).scale(1.5,about_point=O3)
   self.play(Transform(obj,target),run_time=1.0);explain('선형 시간 / 절반 시간에 절반 회전',GREEN)
   at_line(2);equation('t=(.5)²=.25 / 90°×.25=22.5°')
   target=basis(rz(PI/8),O3,scale=1.7).scale(1.5,about_point=O3)
   self.play(Transform(obj,target),run_time=1.0);explain('시간 함수만 바꿈 / 같은 순간에 덜 진행',GOLD)
   at_line(3);equation('1초: 두 방법 모두 t=1 / 같은 끝 자세90°')
   target=basis(rz(PI/2),O3,scale=1.7).scale(1.5,about_point=O3)
   self.play(Transform(obj,target),run_time=1.0);explain('같은 시작·끝·호 / 다른 시간 진행',GREEN)
  elif self.sid=='IP08':
   self.remove(obj);v=arrow(O3,O3+2.1*P@np.array([1.,0,0]),GOLD,7);self.add(v)
   equation('입력 v=(1,0,0) / 같은 RH·열벡터·z축');explain('방금 얻은45° 자세를 벡터로 검사',GREEN)
   at_line(1);equation('q=(cos22.5°,0,0,sin22.5°) / 물체의 회전45°');explain('저장할 반각 / 물체가 도는 각도 구분')
   at_line(2)
   result=arrow(O3,O3+2.1*P@np.array([np.sqrt(.5),np.sqrt(.5),0]),GREEN,7)
   self.play(Transform(v,result),run_time=1.1);equation('같은45° 회전 / v′=(?, ?, ?)')
   at_sentence('첫 번째 성분');equation('v′=(√2/2, ?, ?)')
   at_sentence('두 번째 성분');equation('v′=(√2/2, √2/2, ?)')
   at_sentence('세 번째 성분');equation('v′=(√2/2, √2/2, 0)')
   at_sentence('오른쪽과 위쪽 성분');equation('v′=(√2/2,√2/2,0) / 길이 √(1/2+1/2)=1');explain('방향은 바뀜 / 길이는 보존',GREEN)
   at_line(3)
   original=arrow(O3,O3+2.1*P@np.array([1.,0,0]),GOLD,7)
   self.play(Transform(v,original),run_time=1.1);equation('Rz(-45°)Rz(45°)v=v / 결과(1,0,0)');explain('같은 자세의 작용·역회전 검산 / 정의한 계산 예시',GREEN)
  elif self.sid=='IP06':
   equation('위치·자세 변환 / 무엇을 움직이고 어디까지 닿을까?');explain('변환의 대상을 먼저 정의',GREEN)
   at_line(1)
   a=O3-1.6*P[:,0];b=O3+1.6*P[:,0]
   points=VGroup(Dot3D(a,color=RED,radius=.09),Dot3D(b,color=GREEN,radius=.09));line=Line3D(a,b,color=GOLD,thickness=.025)
   self.play(Create(points),Create(line),run_time=.9)
   box=Cube(side_length=3,fill_opacity=.035,stroke_color=BLUE,stroke_width=2).apply_matrix(P).move_to(O3)
   self.play(Create(box),run_time=.9);equation('점 → 줄·광선 → 구·상자 경계');explain('그 뒤 회전·이동 후의 범위 검사')
  else:raise RuntimeError(self.sid)
  if self.renderer.time>total+.05:raise RuntimeError(f'{self.sid}: narration timing cannot fit the animated explanation')
  wait_to(total)
for ident in CONTENT:
 globals()[ident]=type(ident,(InterpolationAddition,),{'sid':ident,'__module__':__name__})
