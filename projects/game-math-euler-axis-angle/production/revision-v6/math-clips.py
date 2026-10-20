"""Finite, transparent Manim diagrams; same Unity testbed is composited behind."""
from pathlib import Path
import json,os,math,re
import numpy as np
from manim import *
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
INK='#f5f5f5';MUTED='#b8b8b8';RULE='#6b7280';GOLD='#e8cf83';TEAL='#73c7c2';ORANGE='#f39a4b';RED='#ef8585';GREEN='#a4c6a0';PURPLE='#c6b7df';PANEL='#12181c'
def tx(s,size=42,color=INK,width=11.7,mono=False,t2c=None):
 m=Text(s,font='Consolas' if mono else 'Malgun Gothic',font_size=size,color=color,t2c=t2c or {})
 if m.width>width:m.scale_to_fit_width(width)
 return m
def rowgroup(rows,size=43,width=11.3):
 return VGroup(*[tx(t,size,TEAL if i==0 else INK,width=width) for i,t in enumerate(rows)]).arrange(DOWN,aligned_edge=LEFT,buff=.28)
class FiniteMathBeat(Scene):
 def construct(self):
  key=os.environ['V6_BEAT'];plan=json.loads((H/'screen-plan.json').read_text(encoding='utf8'));beat=next(b for s in plan['scenes'] for b in s['beats'] if b['id']==key);d=beat['demonstration'];assert d
  self.camera.background_opacity=0
  panel=RoundedRectangle(width=12.55,height=4.82,corner_radius=.06,stroke_width=1.2,stroke_color=RULE,fill_color=PANEL,fill_opacity=.86).move_to([0,.0,0]);self.add(panel)
  prompt=tx(d['prompt'],45,GOLD,width=11.8).move_to([-5.7,1.94,0],aligned_edge=LEFT);self.add(prompt)
  self.wait(.2)
  kind=d['kind'];rows=d['rows']
  if kind in ['rows','ranges','question','code']:
   if kind=='code':
    group=VGroup()
    for i,line in enumerate(rows):
     m=tx(line,40,INK,width=11.4,mono=True,t2c={'double':PURPLE,'if':PURPLE,'return':PURPLE,'std::remainder':TEAL,'wrapPiCanonical':TEAL,'tau':ORANGE,'pi':ORANGE})
     group.add(m)
    group.arrange(DOWN,aligned_edge=LEFT,buff=.28).move_to([-5.7,1.1,0],aligned_edge=UL)
   else:group=rowgroup(rows).move_to([-5.7,.88,0],aligned_edge=UL)
   for m in group:self.play(FadeIn(m,shift=.08*UP),run_time=.45);self.wait(1.35)
   if kind=='code':
    marker=SurroundingRectangle(group[0],color=GOLD,buff=.08,stroke_width=2);self.play(Create(marker),run_time=.35)
    for m in group[1:]:self.play(Transform(marker,SurroundingRectangle(m,color=GOLD,buff=.08,stroke_width=2)),run_time=.4);self.wait(.8)
    notes=VGroup(*[tx(t,30,MUTED,width=11.5) for t in d.get('notes',[])]).arrange(DOWN,aligned_edge=LEFT,buff=.12).move_to([-5.7,-1.35,0],aligned_edge=UL)
    for m in notes:self.play(FadeIn(m),run_time=.25);self.wait(.7)
   elif kind=='ranges':
    self.add(tx('해설용 대표 범위 · 끝점 포함 여부에 주의',29,MUTED).move_to([0,-1.83,0]))
   elif kind=='question':self.add(tx('지금은 답을 가리고 직접 생각해 보세요',31,MUTED).move_to([0,-1.65,0]))
  elif kind=='flow':
   boxes=VGroup();labels=VGroup()
   for i,s in enumerate(rows):
    x=-4.1+i*4.1;box=Rectangle(width=3.55,height=1.55,stroke_color=TEAL if i==1 else RULE,stroke_width=3,fill_color=PANEL,fill_opacity=.6).move_to([x,0,0]);lab=tx(s,39,width=3.05).move_to(box)
    self.play(FadeIn(box),FadeIn(lab),run_time=.4);boxes.add(box);labels.add(lab)
    if i:
     arrow=Arrow(boxes[i-1].get_right(),box.get_left(),buff=.08,color=GOLD,stroke_width=5,max_tip_length_to_length_ratio=.22);self.play(GrowArrow(arrow),run_time=.65)
     self.play(box.animate.set_stroke(GOLD,width=4),run_time=.25)
    self.wait(1.0)
  elif kind=='matrix':
   if key.startswith('v6-14'):
    inp=tx('[ x   y   z ]',50,TEAL).move_to([-3.8,.4,0]);self.add(inp)
    grid=VGroup(*[Square(side_length=.48,stroke_width=1.5,stroke_color=RULE) for _ in range(9)]).arrange_in_grid(rows=3,cols=3,buff=.06).move_to([-.5,.4,0]);self.play(Create(grid),run_time=.6)
    self.play(GrowArrow(Arrow(inp.get_right(),grid.get_left(),buff=.08,color=GOLD)),run_time=.6)
    self.add(tx('1 × 3',31,MUTED).next_to(inp,DOWN),tx('3 × 3',31,MUTED).next_to(grid,DOWN))
    for i,s in enumerate(rows):self.play(FadeIn(tx(s,39,width=6).move_to([3.4,1.0-i*.78,0])),run_time=.45);self.wait(1.2)
   else:
    square=Square(side_length=1.6,color=TEAL,stroke_width=5).move_to([-3.7,.1,0]);self.add(square)
    self.play(square.animate.stretch(1.8,0),run_time=1.6);self.add(tx('길이 변함 → 순수 회전 아님',30,ORANGE,width=4.4).move_to([-3.7,-1.2,0]))
    g=rowgroup(rows,size=38,width=7.0).move_to([2.4,.0,0]);
    for m in g:self.play(FadeIn(m),run_time=.4);self.wait(1.0)
  elif kind=='circle':
   c=np.array([-3.7,-.15,0]);rad=1.55;circle=Circle(radius=rad,color=RULE,stroke_width=3).move_to(c);self.add(circle)
   self.add(tx('+Z',29,MUTED).move_to(c+np.array([-.45,1.58,0])),tx('+X',29,MUTED).move_to(c+RIGHT*1.88),tx('+Y 쪽 → 원점',25,MUTED).move_to(c+DOWN*1.9))
   angle=d['startAngle'];delta=d['delta']*d.get('progress',1);a=(90-angle)*DEGREES
   needle=Arrow(c,c+rad*np.array([math.cos(a),math.sin(a),0]),buff=0,color=TEAL,stroke_width=6);self.add(needle)
   self.add(DashedVMobject(Line(c,needle.get_end(),color=TEAL,stroke_width=3),num_dashes=12),Dot(needle.get_end(),color=TEAL,radius=.06))
   target_angle=a-delta*DEGREES;target=Line(c,c+rad*np.array([math.cos(target_angle),math.sin(target_angle),0]),color=ORANGE,stroke_width=3);self.add(DashedVMobject(target,num_dashes=12))
   trace=Arc(radius=rad*1.06,start_angle=a,angle=-delta*DEGREES,color=GOLD,stroke_width=5).move_arc_center_to(c)
   duration=max(2.6,min(8,abs(delta)/90))
   self.play(Rotate(needle,angle=-delta*DEGREES,about_point=c),Create(trace),run_time=duration,rate_func=linear)
   g=rowgroup(rows,size=38,width=7.2).move_to([2.7,.2,0])
   for m in g:self.play(FadeIn(m),run_time=.4);self.wait(.9)
  elif kind in ['floor','quantize']:
   if kind=='floor':
    axis=NumberLine(x_range=[-1.4,.5,.5],length=9,include_numbers=False,color=RULE).move_to([0,.5,0]);self.add(axis)
    for val,label in [(-1,'−1'),(-.1,'−0.1'),(0,'0')]:self.add(tx(label,38,TEAL if val==-.1 else INK).next_to(axis.n2p(val),DOWN,buff=.22))
    dot=Dot(axis.n2p(-.1),color=TEAL,radius=.09);self.add(dot);self.play(dot.animate.move_to(axis.n2p(-1)),run_time=1.8)
    self.add(rowgroup(rows,size=40).move_to([0,-1.05,0]))
   else:
    axis=NumberLine(x_range=[19,22,1],length=9,include_numbers=False,color=RULE).move_to([0,.65,0]);self.add(axis)
    for val in [19,20,21,22]:self.add(tx(str(val)+'°',34).next_to(axis.n2p(val),DOWN,buff=.18))
    dot=Dot(axis.n2p(20.4),color=ORANGE,radius=.09);self.add(dot,tx('20.4°',36,ORANGE).next_to(dot,UP));self.play(dot.animate.move_to(axis.n2p(20)),run_time=1.6)
    self.add(rowgroup(rows,size=38).move_to([0,-1.1,0]))
  elif kind=='radian':
   c=np.array([-3.5,-.1,0]);radius=1.5;self.add(Circle(radius=radius,color=RULE).move_to(c));self.add(Line(c,c+RIGHT*radius,color=TEAL,stroke_width=5))
   theta=PI if d.get('halfTurn') else 1.0
   arc=Arc(radius=radius,start_angle=0,angle=theta,color=ORANGE,stroke_width=6).move_arc_center_to(c);ray=Line(c,c+radius*np.array([math.cos(theta),math.sin(theta),0]),color=TEAL,stroke_width=4)
   self.play(Create(arc),Create(ray),run_time=2.2);self.add(tx('r',37,TEAL).move_to(c+np.array([.8,-.3,0])))
   self.add(tx('s',37,ORANGE).move_to(c+np.array([radius*.9,radius*.75,0])))
   g=rowgroup(rows,size=41,width=6.4).move_to([2.7,.1,0])
   for m in g:self.play(FadeIn(m),run_time=.4);self.wait(1.2)
  elif kind=='progress':
   axis=NumberLine(x_range=[0,1,.25],length=9,color=RULE).move_to([0,.5,0]);self.add(axis);dot=Dot(axis.n2p(0),color=TEAL,radius=.1);self.add(dot)
   for value,label in zip([0,.5,1],rows):
    self.play(dot.animate.move_to(axis.n2p(value)),run_time=1.2);self.add(tx(label,38,ORANGE if value else TEAL).move_to(axis.n2p(value)+DOWN*.65));self.wait(.5)
  elif kind=='sine':
   axes=Axes(x_range=[0,90,30],y_range=[0,1,.5],x_length=5.2,y_length=2.6,axis_config={'color':RULE,'include_tip':False}).move_to([-3.2,-.0,0]);self.add(axes)
   curve=axes.plot(lambda a:math.sin(math.radians(a)),x_range=[0,90],color=TEAL);self.play(Create(curve),run_time=2)
   self.add(tx('θ: 0° → 90°',29,MUTED).next_to(axes,DOWN,buff=.12),tx('sin θ',29,MUTED).next_to(axes,UP,buff=.15))
   for a in [20,80]:self.add(Dot(axes.c2p(a,math.sin(a*DEGREES)),color=ORANGE))
   g=rowgroup(rows,size=36,width=6).move_to([3.2,.1,0]);
   for m in g:self.play(FadeIn(m),run_time=.4);self.wait(1)
  elif kind=='local':
   dots=VGroup(*[Dot(np.array([math.cos(a),math.sin(a),0])*1.55+LEFT*3.5,color=RULE,radius=.06) for a in np.linspace(0,TAU,32,endpoint=False)])
   self.add(dots);self.play(VGroup(*dots[:5]).animate.set_color(TEAL).scale(1.6),run_time=1.2)
   self.add(tx('표현 범위의 비유',27,MUTED).move_to([-3.5,-1.9,0]))
   g=rowgroup(rows,size=37,width=7).move_to([2.5,.2,0]);
   for m in g:self.play(FadeIn(m),run_time=.45);self.wait(1)
  else:raise ValueError(kind)
  self.wait(.4)
