"""Finite prerequisite diagrams, explicitly projected illustrations."""
from pathlib import Path
import importlib.util,json,os,math
import numpy as np
from manim import *
H=Path(__file__).parent
spec=importlib.util.spec_from_file_location('math_base',H/'math-clips.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
tx=base.tx;rowgroup=base.rowgroup
INK=base.INK;MUTED=base.MUTED;RULE=base.RULE;GOLD=base.GOLD;TEAL=base.TEAL;ORANGE=base.ORANGE;PANEL=base.PANEL
class FinitePrerequisite(Scene):
 def construct(self):
  key=os.environ['V6_BEAT'];plan=json.loads((H/'screen-plan.json').read_text(encoding='utf8'));d=next(b['demonstration'] for s in plan['scenes'] for b in s['beats'] if b['id']==key)
  self.camera.background_opacity=0
  self.add(RoundedRectangle(width=12.55,height=4.82,corner_radius=.06,stroke_width=1.2,stroke_color=RULE,fill_color=PANEL,fill_opacity=.86))
  self.add(tx(d['prompt'],45,GOLD,width=11.8).move_to([-5.7,1.94,0],aligned_edge=LEFT));self.wait(.2)
  k=d['kind'];rows=d['rows']
  if k=='unitaxis':
   origin=np.array([-4.6,-1.05,0]);vec=(RIGHT+2*UP+2*np.array([-.65,-.35,0]))*1.4
   for direction,label,color in [(RIGHT,'X',base.RED),(UP,'Y',base.GREEN),(np.array([-.65,-.35,0]),'Z','#6ca5e8')]:
    ar=Arrow(origin,origin+direction*1.15,buff=0,color=color,stroke_width=3);self.add(ar,tx(label,28,color).next_to(ar.get_end(),direction,buff=.06))
   ghost=DashedLine(origin,origin+vec,color=MUTED,stroke_width=3);arrow=Arrow(origin,origin+vec,buff=0,color=TEAL,stroke_width=7);self.play(Create(ghost),GrowArrow(arrow),run_time=.9);self.wait(1)
   self.play(Transform(arrow,Arrow(origin,origin+vec/3,buff=0,color=ORANGE,stroke_width=7,max_tip_length_to_length_ratio=.35)),run_time=1.8)
   self.add(tx('방향 유지 / 길이만 1',27,MUTED,width=4).move_to([-3.3,-1.9,0]))
   g=rowgroup(rows,35,6.7).move_to([-.6,.0,0],aligned_edge=LEFT)
   for t in g:self.play(FadeIn(t),run_time=.4);self.wait(1.15)
  elif k=='camera':
   c=np.array([-3.6,-.25,0]);self.add(Circle(radius=1.4,color=RULE).move_to(c),tx('위에서 본 수직 Y축',28,MUTED,width=4.3).move_to(c+DOWN*1.8))
   ray=Arrow(c,c+UP*1.3,buff=0,color=TEAL,stroke_width=6);wedge=Polygon(c,c+np.array([-.5,1.3,0]),c+np.array([.5,1.3,0]),color=TEAL,fill_opacity=.16,stroke_width=2);self.add(wedge,ray)
   self.play(Rotate(VGroup(wedge,ray),-PI/3,about_point=c),run_time=2);self.add(Dot(c,color=GOLD),tx('Y',30,GOLD).next_to(c,LEFT))
   g=rowgroup(rows,36,6.6).move_to([-.6,.0,0],aligned_edge=LEFT)
   for t in g:self.play(FadeIn(t),run_time=.4);self.wait(1.1)
  elif k=='norm':
   c=np.array([-4.8,-1.05,0]);x=Arrow(c,c+RIGHT*1.8,buff=0,color=base.RED,stroke_width=5);y=Arrow(c,c+UP*1.8,buff=0,color=base.GREEN,stroke_width=5);self.play(GrowArrow(x),GrowArrow(y),run_time=.9)
   self.add(DashedLine(x.get_end(),x.get_end()+UP*1.8,color=RULE),DashedLine(y.get_end(),y.get_end()+RIGHT*1.8,color=RULE));v=Arrow(c,c+np.array([1.8,1.8,0]),buff=0,color=TEAL,stroke_width=6);self.play(GrowArrow(v),run_time=.8)
   self.add(tx('벡터 성분의 합',28,MUTED,width=4).move_to([-3.8,-1.65,0]))
   g=rowgroup(rows,33,6.9).move_to([-.9,.1,0],aligned_edge=LEFT)
   for t in g:self.play(FadeIn(t),run_time=.4);self.wait(1.3)
  elif k=='velocity':
   c=np.array([-3.7,-.3,0]);outer=Circle(radius=1.5,color=RULE,stroke_width=3).move_to(c);inner=RoundedRectangle(width=1.75,height=1.2,corner_radius=.1,stroke_color=INK,fill_color=PANEL,fill_opacity=.6).move_to(c);self.add(outer,inner,tx('같은 물체',30).move_to(c))
   a=Arrow(c+LEFT*.8+UP*.75,c+UP*1.4+RIGHT*.5,buff=0,color=TEAL,stroke_width=5);b=Arrow(c+RIGHT*.8+DOWN*.75,c+RIGHT*1.5+UP*.3,buff=0,color=ORANGE,stroke_width=5);self.play(GrowArrow(a),run_time=.7)
   label=tx('ω1',28,TEAL).move_to(c+LEFT*1.9+UP*.85);self.add(label,Line(label.get_right()+RIGHT*.06,a.get_start(),color=TEAL,stroke_width=1.5));self.play(GrowArrow(b),run_time=.7);self.add(tx('ω2',28,ORANGE).next_to(b.get_end(),RIGHT,buff=.08))
   self.add(tx('공통 기준틀로 표현',28,MUTED,width=4.8).move_to(c+DOWN*1.85))
   g=rowgroup(rows,36,6.6).move_to([-.6,.0,0],aligned_edge=LEFT)
   for t in g:self.play(FadeIn(t),run_time=.4);self.wait(1.4)
  self.wait(.2)
