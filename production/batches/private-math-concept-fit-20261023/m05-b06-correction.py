"""B06: show the narrated90-degree step twice, rather than generic illustration tilt."""
from pathlib import Path
import importlib.util,json,os
from manim import *
spec=importlib.util.spec_from_file_location('m05style',Path(__file__).with_name('m05-scenes.py'));q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
class CorrectB06(ThreeDScene):
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']=='B06')
  self.camera.background_color=q.BG;self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  o=q.pos(-3.35,-.15);obj=q.rig(o,'logs',.9)
  self.add(VGroup(*[DashedLine(o-1.7*q.np.eye(3)[:,j],o+2.1*q.np.eye(3)[:,j],color=q.RULE,stroke_width=1.4) for j in range(3)]),obj)
  self.add_fixed_in_frame_mobjects(q.text('같은 Z축으로 90°를 한 번 더',37,q.YELLOW).to_corner(UL,buff=.5),q.text('우리 모형 · 오른손 / 열벡터',20,q.v.SECOND).to_corner(UR,buff=.5),VGroup(q.text('X 앞',25,q.X),q.text('Y 옆',25,q.Y),q.text('Z 위',25,q.Z)).arrange(RIGHT,buff=.25).move_to([-3.2,-2.35,0]))
  a=q.text('첫 회전: +90°',29,q.FG).move_to([3,1.5,0]);self.add_fixed_in_frame_mobjects(a)
  self.play(Rotate(obj,PI/2,axis=OUT,about_point=o),run_time=1.2)
  self.wait(2.6);self.remove(a)
  b=q.text('같은 축으로 +90° 추가',29,q.FG).move_to([3,1.5,0]);self.add_fixed_in_frame_mobjects(b)
  self.play(Rotate(obj,PI/2,axis=OUT,about_point=o),run_time=1.2)
  self.add_fixed_in_frame_mobjects(q.text('90° + 90° = 180°',29,q.Y).move_to([3,-.1,0]))
  self.wait(slot['seconds']-self.renderer.time)
