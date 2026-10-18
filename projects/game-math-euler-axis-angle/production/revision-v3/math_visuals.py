"""Editable mathematical diagrams; exact scene/line timing is supplied after ASR."""
from pathlib import Path
import os,json,math
import numpy as np
from manim import *
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle'
INK='#202020';MUTED='#555b63';RULE='#b8bec5';RED='#b7443f';GREEN='#52704c';BLUE='#2f5faa';GOLD='#9a6b10'
def text(s,size=40,color=INK):return Text(s,font='Malgun Gothic',font_size=size,color=color)
def fit(m,w):
 if m.width>w:m.scale(w/m.width)
 return m
class MathScene(Scene):
 sid='01'
 def construct(self):
  self.camera.background_color=WHITE
  data=json.loads((P/'production/revision-v3/lesson.json').read_text(encoding='utf8'));s=next(v for v in data['scenes'] if v['id']==self.sid)
  timing=os.environ.get('MATH_RENDER_TIMING');slots=json.loads(Path(timing).read_text(encoding='utf8'))['scenes'] if timing else []
  slot=next((v for v in slots if v['id']==self.sid),{'seconds':len(s['ko'])*2.5+1,'lineStarts':[i*2.5 for i in range(len(s['ko']))]})
  def wait_until(t):
   # Cairo's frozen hold uses int(duration / frame_dt). Pass an integer
   # frame budget with a tiny sub-frame margin so float subtraction cannot
   # turn, for example, 452 frames into 451. No encoded-frame repair is used.
   target=round(t*60);remaining=target-round(self.renderer.time*60)
   if remaining<0:raise ValueError(f'{self.sid}: visual action exceeded cue frame {target}.')
   if remaining:self.wait((remaining+1e-6)/60,frozen_frame=True)
   if round(self.renderer.time*60)!=target:raise ValueError(f'{self.sid}: hold missed cue frame {target}.')
  self.add(fit(text(s['title'],46,GOLD),12.65).move_to([-6.35,3.35,0],aligned_edge=LEFT),fit(text('게임수학 · 오일러 각과 축–각',26,MUTED),12).move_to([-6.35,2.82,0],aligned_edge=LEFT))
  self.add(Line([-6.35,2.52,0],[6.35,2.52,0],stroke_width=1.5,color=RULE))
  note=None;focus=None;special=[]
  code_block=None;clock_group=None;angle_labels=None
  problem_heading=None;problem_prompt=None
  def replace(m,pos=None):
   nonlocal note
   if note:self.remove(note)
   note=m.move_to(pos or [3.1,0,0]);self.add(note)
  def formula(lines,size=42,color=INK,width=6.1):return VGroup(*[fit(text(v,size,color),width) for v in lines]).arrange(DOWN,aligned_edge=LEFT,buff=.32)
  def progress_circle(center,color):
   circle=Circle(radius=1.50,color=RULE).move_to(center)
   a=Arrow(center,center+1.35*RIGHT,buff=0,color=color,stroke_width=6)
   return VGroup(circle,a)
  if self.sid=='01':
   # Concrete same-start arrows make the overview a visual relationship.
   for j,(label,col) in enumerate([('방향과 비틀림',BLUE),('세 축과 순서',GREEN),('한 축과 회전각',GOLD)]):
    x=-4.3+j*4.3;self.add(Circle(radius=.52,color=col,stroke_width=4).move_to([x,.35,0]),Arrow([x,.35,0],[x+.7,1.05,0],buff=0,color=col,stroke_width=5),fit(text(label,38,col),3.8).move_to([x,-.7,0]))
    if j<2:self.add(Arrow([x+.85,.35,0],[x+3.4,.35,0],buff=.05,color=MUTED,stroke_width=3))
  elif self.sid=='13':
   center=np.array([-3.55,-.1,0]);self.add(Circle(radius=1.7,color=RULE).move_to(center));needle=Arrow(center,center+1.55*RIGHT,buff=0,color=BLUE,stroke_width=6);self.add(needle)
  elif self.sid=='15':
   # Full-width code first, then large excerpts beside the relevant speech.
   # The former 7-unit code column shrank every line on a phone.
   code=s['code']
  elif self.sid=='24':
   centers=[np.array([-3.25,.15,0]),np.array([3.25,.15,0])]
   faces=[progress_circle(centers[0],BLUE),progress_circle(centers[1],GREEN)]
   special=[face[1] for face in faces]
   rate_labels=[fit(text(label,37,col),6).move_to([centers[j][0],2.0,0]) for j,(label,col) in enumerate([('720°/s = 4π rad/s',BLUE),('1080°/s = 6π rad/s',GREEN)])]
   clock_group=VGroup(*faces,*rate_labels);self.add(clock_group)
  elif self.sid=='25':
   problem_heading=text('문제 1',42,GOLD).move_to([-5.5,1.8,0])
   problem_prompt=text('+170°  →  −170°',54,BLUE).move_to([0,.9,0])
   self.add(problem_heading,problem_prompt)
  elif self.sid=='26':
   self.add(formula(['① 축과 적용 순서','② 표현의 특이점과 물체의 회전','③ 단위 · 중복 표현 · 합성'],46,width=11.6).move_to([0,.25,0]))
  for i,beat in enumerate(s['beats']):
   at=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   wait_until(at)
   if focus:self.remove(focus)
   # Keep the worst-case two-line caption box (top y=897px) unobstructed.
   focus=fit(text(beat,34,GREEN),12.4).move_to([0,-2.25,0]);self.add(focus)
   if self.sid=='13':
    examples=[['t = 0 → 시작','t = 0.5 → 중간','t = 1 → 끝'],['720° ≡ 0°','45° − 720° = −675°'],['45° − 0° = +45°'],['170° − (−170°) = +340°'],['340° − 360° = −20°'],['180° = π rad','360° = 2π rad'],['Δ = wrapPi(end − start)','angle(t) = start + t Δ'],['−170° + 0.5 × (−20°)','= −180° ≡ +180°']]
    replace(formula(examples[min(i,len(examples)-1)],38),[3.1,.1,0])
    if i in [1,2,3,4]:
     self.remove(needle);a=(-170 if i>=3 else 0)*DEGREES;needle=Arrow(center,center+1.55*np.array([np.cos(a),np.sin(a),0]),buff=0,color=BLUE,stroke_width=6);self.add(needle)
     delta=[-675,45,340,-20][i-1]*DEGREES
     self.play(Rotate(needle,angle=delta,about_point=center),run_time=1.15,rate_func=linear)
   elif self.sid=='15':
    if code_block is not None:self.remove(code_block)
    if note is not None:self.remove(note);note=None
    rows=[[0,1,2,3,4,5,6],[1,2,3],[4,5,6],[4],[7,8],[]][min(i,5)]
    if rows:
     code_block=VGroup(*[Text(code[row],font='Consolas',font_size=40 if i==0 else 42,color=INK) for row in rows]).arrange(DOWN,aligned_edge=LEFT,buff=.10 if i==0 else .15)
     fit(code_block,12.3);code_block.move_to([0,.2 if i==0 else 1.15,0]);self.add(code_block)
     active_row=[0,2,0,0,0][min(i,4)]
     box=SurroundingRectangle(code_block[active_row],color=GREEN,buff=.07,stroke_width=3);self.add(box)
    else:code_block=None;box=None
    if i==1:replace(formula(['w = remainder(angle, 2π)','입력과 결과의 단위: rad'],40,width=11.8),[0,-1.05,0])
    elif i==2:replace(formula(['−π rad → +π rad','−π < result ≤ π'],42,width=11.8),[0,-1.05,0])
    elif i==3:
     cases=VGroup(formula(['angle = −π rad','참 → w = +π rad'],38,width=5.7),formula(['angle = π/2 rad','거짓 → w = π/2 rad'],38,width=5.7)).arrange(RIGHT,buff=.8)
     replace(cases,[0,-.65,0])
    elif i==4:replace(formula(['Δ = wrapPi(end − start)','angle(t) = start + t × Δ'],42,width=11.8),[0,-.85,0])
    elif i>=5:replace(formula(['입력 · 출력: 라디안(rad)','도와 라디안을 혼용하지 않기','한 축의 wrap ≠ 최단 삼차원 경로'],44,width=11.8),[0,.1,0])
    if box is not None:self.wait(.35);self.remove(box)
   elif self.sid=='24':
    if i==1:
     replace(formula(['t: 0.00 →','0.25 s'],32,GOLD,width=3.0),[0,0,0])
     self.play(*[Rotate(a,angle=turns*TAU*.25,about_point=c) for a,c,turns in zip(special,centers,[2,3])],run_time=.25,rate_func=linear)
     angle_labels=VGroup(text('180°',34,BLUE).move_to([-3.25,-1.7,0]),text('270°',34,GREEN).move_to([3.25,-1.7,0]));self.add(angle_labels)
     replace(formula(['t = 0.25 s','비교용 정지'],32,GOLD,width=3.0),[0,0,0]);self.wait(.8)
    if i==2:
     if angle_labels is not None:self.remove(angle_labels)
     replace(formula(['t: 0.25 →','1.00 s'],32,GOLD,width=3.0),[0,0,0])
     self.play(*[Rotate(a,angle=turns*TAU*.75,about_point=c) for a,c,turns in zip(special,centers,[2,3])],run_time=.75,rate_func=linear)
     angle_labels=VGroup(text('720° · 2회전',34,BLUE).move_to([-3.25,-1.7,0]),text('1080° · 3회전',34,GREEN).move_to([3.25,-1.7,0]));self.add(angle_labels)
     replace(formula(['t = 1.00 s','끝 자세 같음'],32,GOLD,width=3.0),[0,0,0])
    if i==4:
     self.remove(clock_group)
     if angle_labels is not None:self.remove(angle_labels);angle_labels=None
     replace(formula(['body +z  →  world +x','ω_world = R ω_body','Ry(90°) (0,0,1) = (1,0,0)'],38,width=11),[0,.1,0])
    if i==6:replace(formula(['자세 R','회전량 e [rad]','각속도 ω [rad/s]'],44,width=11),[0,.1,0])
   elif self.sid=='25':
    if i==3:
     problem_heading.become(text('문제 2',42,GOLD).move_to([-5.5,1.8,0]))
     problem_prompt.become(text('회전벡터 → 축·각',48,BLUE).move_to([0,.9,0]))
    if i==5:self.remove(problem_prompt)
    examples=[['start = +170°','end = −170°'],['Δdeg = −340° + 360° = +20°'],['170° + 0.5 × 20° = 180°','wrapPi(−17π/9) = +π/9 rad'],['e = (0, π/2, 0) rad'],['θ = ||e|| = π/2 rad = 90°','n = e/||e|| = (0,1,0)'],['다른 축의 회전 합성: 행렬 곱','벡터의 성분합과 구분']]
    replace(formula(examples[min(i,5)],43,width=11.5),[0,-.45,0])
  wait_until(slot['frames']/60 if 'frames' in slot else slot['seconds'])
for sid in ['01','13','15','24','25','26']:
 globals()['Scene'+sid]=type('Scene'+sid,(MathScene,),{'sid':sid,'__module__':__name__})
