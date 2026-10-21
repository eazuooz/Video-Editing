"""Static states of the unchanged original mesh lesson and its current captions."""
import importlib.util,os
from pathlib import Path
from manim import *
p=Path(__file__).with_name('mesh-polish-scenes.py')
spec=importlib.util.spec_from_file_location('mesh_polish',p);polish=importlib.util.module_from_spec(spec);spec.loader.exec_module(polish)
o=polish.original
class Preview(Scene):
 def construct(self):
  self.camera.background_color=WHITE
  s=next(x for x in polish.lesson['scenes'] if x['id']==os.environ['MESH_PREVIEW_SCENE']);i=int(os.environ['MESH_PREVIEW_STATE']);mode=s['mode']
  title=o.fit(o.txt(s['title'],38),12.5).to_corner(UL,buff=.58)
  sub=o.fit(o.txt('게임수학 Part 2 / 메시·법선·UV  ·  직접 정의한 데이터와 계산',20,o.MUTED),12.5).next_to(title,DOWN,aligned_edge=LEFT,buff=.13)
  self.add(title,sub,Line([-6.5,2.35,0],[6.5,2.35,0],color=o.RULE,stroke_width=1))
  target=o.diagram(mode,i);assert target.width<=6.3 and target.height<=3.3
  self.add(target.move_to([-3.05,-.35,0]),o.fit(o.txt(s['beats'][i],26,o.BLUE),5.9).move_to([3.3,-.28,0]))
  stage=o.fit(o.txt(f'{i+1}/{len(s["beats"])}  '+('형태를 보존한 원래 도식' if mode in ['interpolation','uv-mapping','repeat-order'] else '원래 예제 / 게임 내부 구현 추정 아님'),21,o.MUTED),12.2).move_to([0,-2.45,0]);self.add(stage)
  if mode=='accumulation':
   code=['sum[v] = 0','cross = edge1 × edge2','sum[index] += normalize(cross)','sum=(1,1,1)','n=normalize(sum)','if length(sum)==0: handle','policy: equal face weights'][i]
   self.add(o.fit(o.Text(code,font='Consolas',font_size=21,color=o.INK,t2c={'sum':o.BLUE,'index':'#7c3aad','normalize':o.GREEN,'cross':o.GOLD,'if':o.RED,'0':o.GOLD}),5.85).move_to([3.3,-1.1,0]))
