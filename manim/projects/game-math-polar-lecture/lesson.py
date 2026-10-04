"""Original Manim mathematical diagrams; all count as explanation time.

Coordinate conventions are visible. Card shadows and animated comparisons use
the channel's white research presentation style. No game prototypes are built.
"""
from pathlib import Path
import json,math,os
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
INK='#202020';MUTED='#737373';LINE='#cbd0d6';BLUE='#2f5faa';GREEN='#52704c';RED='#c43b3b';LIGHT='#dfeaf5'
GEO='#8795a6'
def txt(s,size=30,color=INK):return Text(s,font='Malgun Gothic',font_size=size,color=color)
def box(s,color=BLUE):
 face=Rectangle(width=6.0,height=1.08,stroke_color=LINE,stroke_width=1,fill_color=WHITE,fill_opacity=1)
 shadow=face.copy().set_stroke(width=0).set_fill(LIGHT,opacity=.85).shift(.09*RIGHT+.09*DOWN)
 words=txt(s,30,color);words.scale(min(1,5.55/max(words.width,.01)))
 return VGroup(shadow,face,words)
def timeline(slug,data):
 if os.environ.get('POLAR_RENDER_TIMING'):
  return json.loads(Path(os.environ['POLAR_RENDER_TIMING']).read_text(encoding='utf8'))
 if os.environ.get('POLAR_PREVIEW')=='1':
  return {'scenes':[{'id':s['id'],'seconds':len(s['ko'])*2+3,'voiceSeconds':len(s['ko'])*2,'lineStarts':[i*2 for i in range(len(s['ko']))],'cues':[{'start':i*2,'text':v} for i,v in enumerate(s['ko'])]} for s in data['scenes']]}
 return json.loads((ROOT/f'projects/{slug}/production/timeline.json').read_text(encoding='utf8'))
class Diagram(Scene):
 slug='';sid=''
 def construct(self):
  self.camera.background_color=WHITE
  d=json.loads((ROOT/('production/batches/game-math-polar-lecture/'+('lesson-data.json' if self.slug.endswith('2d') else 'part2-data.json'))).read_text(encoding='utf8'))[self.slug]
  s=next(s for s in d['scenes'] if s['id']==self.sid);p=timeline(self.slug,d);slot=next(s for s in p['scenes'] if s['id']==self.sid)
  title=txt(s['title'],40);title.scale(min(1,12.5/max(title.width,.01)));title.to_corner(UL,buff=.65)
  sub=txt(f'게임수학 Part 2 / 극좌표계 {d["part"]}편  ·  {self.sid}',21,MUTED).next_to(title,DOWN,aligned_edge=LEFT,buff=.16)
  self.add(title,sub,Line([-6.45,2.65,0],[6.45,2.65,0],color=LINE,stroke_width=1))
  mode=s['mode'];o=np.array([-3.55,-.05,0]);unit=.35
  axes=Axes(x_range=[-6,6,2],y_range=[-6,6,2],x_length=4.2,y_length=4.2,axis_config={'color':LINE,'stroke_width':1.8,'tip_width':.1,'tip_height':.1}).move_to(o)
  o=axes.c2p(0,0);point=axes.c2p(4,3)
  labels=VGroup(txt('+x',20,MUTED).next_to(axes.x_axis.get_end(),RIGHT,buff=.08),txt('+y',20,MUTED).next_to(axes.y_axis.get_end(),UP,buff=.08))
  graph=VGroup(axes,labels,Dot(o,color=INK,radius=.05));self.add(graph)
  angle=ValueTracker(math.atan2(3,4));radius=ValueTracker(5);cx=ValueTracker(0)
  def at():return o+np.array([cx.get_value(),0,0])+unit*radius.get_value()*np.array([math.cos(angle.get_value()),math.sin(angle.get_value()),0])
  dot=always_redraw(lambda:Dot(at(),radius=.09,color=BLUE));ray=always_redraw(lambda:Line(o+[cx.get_value(),0,0],at(),color=BLUE,stroke_width=4))
  circle=Circle(radius=1.75,color=LINE,stroke_width=2).move_to(o)
  if mode in ['overview','units','aliases','canonical','orbit','turn']:self.add(circle)
  if mode=='overview':
   self.remove(graph);self.add(Circle(radius=1.7,color=BLUE,stroke_width=2).move_to(o))
  if mode in ['aliases','canonical']:angle.set_value((30 if mode=='aliases' else 210)*DEGREES);radius.set_value(3)
  if mode=='turn':angle.set_value(179*DEGREES)
  if mode=='units':angle.set_value(0)
  if mode=='practice':angle.set_value(225*DEGREES);radius.set_value(2)
  self.add(dot,ray)
  if mode=='turn':
   target=o+unit*5*np.array([np.cos(181*DEGREES),np.sin(181*DEGREES),0])
   self.add(Dot(target,color=RED,radius=.08),txt('179° / -179°',23,RED).move_to([-3.55,-2.35,0]))
  if mode=='forward':
   unit=.18;radius.set_value(10);angle.set_value(30*DEGREES)
   h=Line(o,o+[unit*10*math.cos(PI/6),0,0],color=RED,stroke_width=4);v=Line(h.get_end(),at(),color=GREEN,stroke_width=4)
   self.add(h,v,txt('x ≈ 8.660',23,RED).next_to(h,DOWN,buff=.15),txt('y = 5',23,GREEN).next_to(v,RIGHT,buff=.15),txt('r = 10',24,BLUE).move_to((o+at())/2+[-.3,.3,0]))
  if mode=='inverse':
   other=Dot(axes.c2p(-4,-3),color=RED,radius=.09);self.add(other,Line(o,other.get_center(),color=RED,stroke_width=3),txt('(4,3)',23,BLUE).next_to(dot,UP),txt('(-4,-3)',23,RED).next_to(other,DOWN))
  if mode=='vectors':
   self.remove(dot,ray);a=axes.c2p(2,0);ab=axes.c2p(2,2)
   self.add(Arrow(o,a,buff=0,color=BLUE,stroke_width=4),Arrow(a,ab,buff=0,color=GREEN,stroke_width=4));self.play(Create(DashedLine(o,ab,color=RED,stroke_width=3)),run_time=.8)
  card=None;history=VGroup()
  # Lines and their word-aligned boundaries, rather than cue splitting, drive beats.
  origins=[]
  for line in s['ko']:
   normalized=''.join(c for c in line if c.isalnum());matches=[]
   for cue in slot['cues']:
    cue_text=''.join(c for c in cue['text'] if c.isalnum())
    if cue_text and (normalized.startswith(cue_text[:min(6,len(cue_text))]) or cue_text[:8] in normalized[:16]):matches.append(cue['start'])
   origins.append(min(matches) if matches else None)
  # Align tool also records an explicit line->cue map when available.
  beat_times=slot.get('lineStarts',origins)
  for i,beat in enumerate(s['beats']):
   t=beat_times[i] if i<len(beat_times) and beat_times[i] is not None else i*slot['voiceSeconds']/max(1,len(s['beats']))
   if t-self.renderer.time>1/60:self.wait(t-self.renderer.time,frozen_frame=True)
   new=box(beat,GREEN if i==len(s['beats'])-1 else BLUE).move_to([3.0,.8,0])
   if card:self.play(ReplacementTransform(card,new),run_time=.4)
   else:self.play(FadeIn(new,shift=.12*UP),run_time=.5)
   card=new
   small=txt(beat,21,MUTED);small.scale(min(1,5.55/max(small.width,.01)));small.move_to([3.0,-.18-i*.34,0]);self.play(FadeIn(small),run_time=.2);history.add(small)
   if mode=='overview' and i in [1,2]:self.play(angle.animate.set_value((i+1)*PI/6),run_time=.65)
   if mode=='locate' and i==1:self.play(angle.animate.set_value(PI/6),run_time=.65)
   if mode=='locate' and i==2:self.play(angle.animate.set_value(math.atan2(3,4)),run_time=.65)
   if mode=='locate' and i==3:self.play(angle.animate.set_value(math.atan2(3,4)),run_time=.65)
   if mode=='locate' and i==4:self.play(angle.animate.increment_value(TAU),run_time=2,rate_func=linear)
   if mode=='units' and i in [0,1,2]:self.play(angle.animate.set_value([TAU,1,PI/2][i]),run_time=1.4)
   if mode in ['aliases','canonical']:self.play(Indicate(dot,color=GREEN,scale_factor=1.6),run_time=.65)
   if mode=='aliases' and i==2:self.play(radius.animate.set_value(-3),run_time=.7)
   if mode=='aliases' and i==3:radius.set_value(3);angle.set_value(-150*DEGREES)
   if mode=='aliases' and i==4:self.play(radius.animate.set_value(0),run_time=.7)
   if mode=='orbit':
    if i in [1,2,3]:self.play(angle.animate.increment_value(PI/2),run_time=1.2,rate_func=linear)
    if i==4:self.play(cx.animate.set_value(.6),circle.animate.shift(.6*RIGHT),run_time=1)
   if mode=='turn' and i==1:self.play(angle.animate.set_value(-179*DEGREES),run_time=2,rate_func=linear)
   if mode=='turn' and i==2:
    angle.set_value(179*DEGREES);self.play(angle.animate.set_value(181*DEGREES),run_time=1.2)
   if mode=='turn' and i==3:self.play(angle.animate.set_value(180.5*DEGREES),run_time=.8)
   if mode=='practice' and i==2:self.play(angle.animate.set_value(math.atan2(4,-3)),radius.animate.set_value(5),run_time=.7)
  remain=slot['seconds']-self.renderer.time
  if remain>1/60:self.wait(remain,frozen_frame=True)
class SpaceDiagram(ThreeDScene):
 slug='';sid=''
 def construct(self):
  self.camera.background_color=WHITE
  d=json.loads((ROOT/'production/batches/game-math-polar-lecture/part2-data.json').read_text(encoding='utf8'))[self.slug]
  script=next(s for s in d['scenes'] if s['id']==self.sid);plan=timeline(self.slug,d);slot=next(s for s in plan['scenes'] if s['id']==self.sid)
  mode=script['mode'];math_axes=mode in ['cylinder','cylinderconvert','mathsphere']
  title=txt(script['title'],40);title.scale(min(1,12.5/max(title.width,.01)));title.to_corner(UL,buff=.65)
  convention='수학: z ↑ / θ: +x에서 반시계' if math_axes else '책의 게임 약속: +x 오른쪽, +y 위, +z 앞 / +p 아래'
  subtitle=txt(convention,21,MUTED).next_to(title,DOWN,aligned_edge=LEFT,buff=.16)
  self.add_fixed_in_frame_mobjects(title,subtitle,Line([-6.45,2.65,0],[6.45,2.65,0],color=LINE,stroke_width=1))
  self.set_camera_orientation(phi=65*DEGREES,theta=-45*DEGREES,zoom=.87)
  origin=np.array([-2.5,-2.5,-.25]);scale=.64
  axes=ThreeDAxes(x_range=[-3,3,1],y_range=[-3,3,1],z_range=[-3,3,1],x_length=3.84,y_length=3.84,z_length=3.84,axis_config={'color':GEO,'stroke_width':1.5,'include_ticks':False}).shift(origin)
  self.add(axes)
  label=txt('z ↑' if math_axes else 'y ↑',23,GREEN).move_to([-3.4,2.13,0]);self.add_fixed_in_frame_mobjects(label)
  r=ValueTracker(2);h=ValueTracker(PI/3);pitch=ValueTracker(-PI/6);height=ValueTracker(1.5)
  if mode in ['cylinder','cylinderconvert']:h.set_value(PI/6)
  if mode=='mathsphere':pitch.set_value(PI/3)
  if mode in ['gameconvention','gameforward','practice3d']:h.set_value(0);pitch.set_value(0)
  if mode=='aliases3d':h.set_value(PI/2);pitch.set_value(PI/4)
  if mode=='canonical3d':h.set_value(PI/3);pitch.set_value(PI/4)
  def endpoint():
   rr,hh,pp=r.get_value(),h.get_value(),pitch.get_value()
   if mode in ['cylinder','cylinderconvert']:v=np.array([rr*np.cos(hh),rr*np.sin(hh),height.get_value()])
   elif mode=='mathsphere':v=np.array([rr*np.sin(pp)*np.cos(hh),rr*np.sin(pp)*np.sin(hh),rr*np.cos(pp)])
   else:
    # Permute book y-up into Manim's physical z-up for drawing only.
    x=rr*np.cos(pp)*np.sin(hh);y=-rr*np.sin(pp);z=rr*np.cos(pp)*np.cos(hh);v=np.array([x,z,y])
   return origin+scale*v
  dot=always_redraw(lambda:Dot3D(endpoint(),radius=.10,color=BLUE,resolution=(4,4)))
  ray=always_redraw(lambda:Line(origin,endpoint(),color=BLUE,stroke_width=4))
  self.add(dot,ray,Dot3D(origin,radius=.06,color=INK,resolution=(4,4)))
  # Curves are genuine 3D geometry; no pre-rendered flat sphere illustration.
  equator=Circle(radius=2*scale,color=GEO,stroke_width=2).move_to(origin)
  meridian=Circle(radius=2*scale,color=GEO,stroke_width=1.6).rotate(PI/2,axis=RIGHT).move_to(origin)
  self.add(equator)
  if mode in ['cylinder','cylinderconvert']:
   top=equator.copy().shift(1.5*scale*OUT).set_color(GREEN)
   self.add(top,*[Line(origin+scale*np.array([2*np.cos(a),2*np.sin(a),0]),origin+scale*np.array([2*np.cos(a),2*np.sin(a),1.5]),color=GEO,stroke_width=1) for a in np.linspace(0,TAU,12,endpoint=False)])
   projected=always_redraw(lambda:Line(origin+scale*np.array([2*np.cos(h.get_value()),2*np.sin(h.get_value()),0]),endpoint(),color=GREEN,stroke_width=3));self.add(projected)
  else:
   self.add(meridian,meridian.copy().rotate(PI/2,axis=OUT,about_point=origin))
  if mode=='mathsphere':
   qlabel=txt('q = hypot(x,y)  ·  r = hypot(x,y,z)',22,MUTED).move_to([-3.4,-2.15,0]);self.add_fixed_in_frame_mobjects(qlabel)
  if mode=='inverse3d':
   end=endpoint();horizontal=np.array([end[0],end[1],origin[2]])
   self.add(Line(origin,horizontal,color=RED,stroke_width=4),Line(horizontal,end,color=GREEN,stroke_width=3))
   qlabel=txt('q: 수평 길이 / y: 높이',23,MUTED).move_to([-3.4,-2.1,0]);self.add_fixed_in_frame_mobjects(qlabel)
  if mode=='vectors3d':
   self.remove(dot,ray,equator,meridian)
   aa=origin+scale*np.array([1,0,0]);sum_point=origin+scale*np.array([1,0,2])
   self.play(Create(Line(origin,aa,color=BLUE,stroke_width=4)),Create(Line(aa,sum_point,color=GREEN,stroke_width=4)),Create(Line(origin,sum_point,color=RED,stroke_width=3)),run_time=.8)
   vectorlabel=txt('(1,0,0) + (0,2,0) = (1,2,0)',23,MUTED).move_to([-3.4,-1.85,0]);self.add_fixed_in_frame_mobjects(vectorlabel)
  card=None
  for i,beat in enumerate(script['beats']):
   ts=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   if ts-self.renderer.time>1/60:self.wait(ts-self.renderer.time,frozen_frame=True)
   new=box(beat,GREEN if i==len(script['beats'])-1 else BLUE).move_to([3.0,.8,0]);self.add_fixed_in_frame_mobjects(new)
   if card:self.play(FadeOut(card),FadeIn(new,shift=.1*UP),run_time=.4);self.remove(card)
   else:self.play(FadeIn(new,shift=.1*UP),run_time=.5)
   card=new
   detail=txt(beat,21,MUTED);detail.scale(min(1,5.55/max(detail.width,.01)));detail.move_to([3.0,-.2-i*.34,0]);self.add_fixed_in_frame_mobjects(detail);self.play(FadeIn(detail),run_time=.2)
   if mode=='cylinder':
    if i==1:self.play(height.animate.set_value(0),run_time=.7);self.play(height.animate.set_value(1.5),run_time=.9)
    if i==2:self.play(height.animate.set_value(2.0),run_time=.8)
    if i==3:self.play(h.animate.increment_value(TAU),run_time=2,rate_func=linear)
   elif mode=='cylinderconvert':
    if i==1:self.play(h.animate.set_value(0),height.animate.set_value(1.2),run_time=.8)
   elif mode=='mathsphere':
    if i==2:
     self.play(pitch.animate.set_value(0),run_time=.6);self.play(pitch.animate.set_value(PI/2),run_time=.6);self.play(pitch.animate.set_value(PI),run_time=.6)
    if i==3:self.play(pitch.animate.set_value(PI/3),run_time=.7)
   elif mode=='gameconvention':
    if i==1:self.play(h.animate.set_value(PI/2),run_time=1)
    if i==2:self.play(pitch.animate.set_value(PI/4),run_time=.8);self.play(pitch.animate.set_value(-PI/4),run_time=.8)
   elif mode=='gameforward':
    if i==1:self.play(pitch.animate.set_value(PI/6),run_time=.8)
    if i==3:self.play(h.animate.set_value(0),pitch.animate.set_value(0),run_time=.8)
    if i==4:self.play(h.animate.set_value(PI/2),run_time=.8)
   elif mode=='aliases3d':self.play(Indicate(dot,color=GREEN,scale_factor=1.5),run_time=.65)
   elif mode=='canonical3d':
    if i==2:self.play(pitch.animate.set_value(-PI/2),run_time=.8)
    if i==3:self.play(h.animate.increment_value(PI),run_time=.9)
   elif mode=='camera':
    if i==0:
     center=Dot3D(origin,radius=.08,color=GREEN,resolution=(4,4));self.add(center)
    if i==3:
     view=Arrow(endpoint(),origin,buff=.08,color=GREEN,stroke_width=5);self.play(GrowArrow(view),ray.animate.set_opacity(.25),run_time=1)
   elif mode=='vectors3d' and i==2:
    safe=txt('1.0000001 → clamp → 1',25,GREEN).move_to([-3.4,-2.35,0]);self.add_fixed_in_frame_mobjects(safe);self.play(FadeIn(safe),run_time=.6)
   elif mode=='practice3d':
    if i==1:self.play(h.animate.set_value(PI/2),run_time=.8)
    if i==2:self.play(h.animate.set_value(0),pitch.animate.set_value(-PI/2),run_time=.8)
    if i==3:self.play(h.animate.increment_value(PI),run_time=.8)
  remain=slot['seconds']-self.renderer.time
  if remain>1/60:self.wait(remain,frozen_frame=True)
def make_scenes(slug,module):
 d=json.loads((ROOT/('production/batches/game-math-polar-lecture/'+('lesson-data.json' if slug.endswith('2d') else 'part2-data.json'))).read_text(encoding='utf8'))[slug]
 return {'Scene'+s['id']:type('Scene'+s['id'],(Diagram if d['part']==1 or s['mode']=='overview' else SpaceDiagram,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in d['scenes'] if s['kind']=='explanation'}
