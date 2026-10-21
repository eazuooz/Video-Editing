"""Finite60fps cell operations for the exact approved row-vector convention.

Root places each one-second phase at its spoken cue and retains endpoints.
No narration is paused for an animation and no source footage is time-warped.
"""
import os
from manim import *
config.frame_width=8;config.frame_height=7
WHITE='#f5f5f5';GOLD='#e8cf83';TEAL='#73c7c2';COLORS=['#ef5a63','#6cce8e','#66b9ed']
def label(s,size=42,color=WHITE):return Text(s,font='Noto Sans KR',font_size=size,color=color)
def cells(values):
 out=[]
 for i,row in enumerate(values):
  for j,v in enumerate(row):out.append(label(str(v),48,COLORS[i]).move_to([-1.6+j*1.6,1.2-i*1.1,0]))
 return out
R=[['0','0','−1'],['0','1','0'],['1','0','0']]
class MatrixAction(Scene):
 def construct(self):
  self.camera.background_color=BLACK
  self.add(label(os.environ.get('V8_MATH_TITLE',''),36,GOLD).move_to([0,2.9,0]))
  key=os.environ['V8_MATH_ACTION']
  if key=='rows':
   v=cells(R)
   for i in range(3):
    names=['물체 X축 → 첫째 행','물체 Y축 → 둘째 행','물체 Z축 → 셋째 행']
    q=label(names[i],36,COLORS[i]).move_to([0,-2.4,0]);self.add(q)
    self.play(*[FadeIn(x,shift=RIGHT*.25)for x in v[i*3:i*3+3]],run_time=1,rate_func=smooth);self.remove(q)
  elif key=='transpose':
   v=cells(R);self.add(*v)
   self.add(label('행 i, 열 j → 행 j, 열 i',36,TEAL).move_to([0,-2.4,0]))
   for i,j in [(0,1),(0,2),(1,2)]:
    a=v[i*3+j];b=v[j*3+i];pa,pb=a.get_center().copy(),b.get_center().copy()
    self.play(a.animate.move_to(pb),b.animate.move_to(pa),run_time=1,path_arc=PI/4)
  elif key=='weighted':
   terms=[('1 × (0, 0, −1)',COLORS[0]),('0 × (0, 1, 0)',COLORS[1]),('2 × (1, 0, 0)',COLORS[2])]
   for i,(s,col) in enumerate(terms):self.play(Write(label(s,40,col).move_to([0,1.7-i*1.1,0])),run_time=1)
   self.play(FadeIn(label('= (2, 0, −1)',48,TEAL).move_to([0,-2,0])),run_time=1)
  elif key=='dcm':
   vals=[[a+'·'+b+'′'for b in ['p','q','r']]for a in ['p','q','r']];v=cells(vals)
   for i in range(3):self.play(*[FadeIn(x)for x in v[i*3:i*3+3]],run_time=1)
   self.add(label('두 축은 같은 기준에서 읽는다',32,TEAL).move_to([0,-2.4,0]))
  elif key=='composition':
   a=label('A',54,COLORS[0]).move_to([-2.6,1.0,0]);b=label('B',54,COLORS[1]).move_to([0,1,0]);c=label('C',54,COLORS[2]).move_to([2.6,1,0]);self.add(a,b,c)
   self.play(GrowArrow(Arrow([-2.1,1,0],[-.5,1,0],color=WHITE,buff=0)),FadeIn(label('RAB',32).move_to([-1.3,1.7,0])),run_time=1)
   self.play(GrowArrow(Arrow([.5,1,0],[2.1,1,0],color=WHITE,buff=0)),FadeIn(label('RBC',32).move_to([1.3,1.7,0])),run_time=1)
   self.play(Write(label('RAC = RAB RBC',42,TEAL).move_to([0,-.8,0])),run_time=1)
   self.add(label('도착 B와 다음 출발 B가 일치',32).move_to([0,-2,0]))
  elif key=='storage':
   self.add(label('같은 225자세 / 초 · 32bit / 숫자',30).move_to([0,2,0]))
   self.play(FadeIn(label('행렬: 9 × 4B = 36B',38).move_to([0,.9,0])),run_time=1)
   self.play(Write(label('36B × 225 = 8,100B/초',40,TEAL).move_to([0,-.3,0])),run_time=1)
   self.play(FadeIn(label('한 프레임이 아니라 1초의 합',32,GOLD).move_to([0,-1.8,0])),run_time=1)
  else:raise ValueError(key)
  self.wait(1/60)
