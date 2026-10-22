"""Preserve the closing summary and timing; use an outline that cannot hide text."""
from pathlib import Path
import json
from manim import *
ROOT=Path(__file__).resolve().parents[3]
class Summary(Scene):
 def construct(self):
  s=next(x for x in json.loads((ROOT/'projects/game-math-rotation-conversions-v2/production/concept-fit-v2/timeline.json').read_text(encoding='utf8'))['scenes'] if x['id']=='26')
  self.camera.background_color=WHITE
  def label(t,size=30,color='#292D31'):return Text(t,font='Malgun Gothic',font_size=size,color=color)
  self.add(label(s['title'],40).to_corner(UL,buff=.6))
  self.add(label('같은 규약 · 같은 입력 · 눈으로 확인한 결과',23,'#687078').move_to([0,2.4,0]))
  names=['부호·단위 길이 → 짧은 회전 경로','고정된 두 자세·선형 시간 → 일정 속도','같은 축·곱셈 약속 → 네 표현 변환','0°·180°·특이 자세 → 예외 처리','벡터를 돌리고 되돌려 → 왕복 검증']
  rows=VGroup(*[VGroup(Rectangle(width=12,height=.65,color='#D7DDE2',stroke_width=1),label(t,28,'#2D604B')) for t in names]).arrange(DOWN,buff=.16).move_to([0,.2,0]);self.add(rows)
  outline=None
  for i,t in enumerate(s['lineStarts']):
   if t>self.renderer.time:self.wait(t-self.renderer.time)
   if outline:self.remove(outline)
   targets=[0,1,2,4,4];outline=SurroundingRectangle(rows[targets[i]],color='#916B20',stroke_width=4,buff=.06);self.add(outline)
   if i==2:self.add(label('0°·180°·특이 자세도 함께 처리',23,'#916B20').move_to([0,-2.35,0]))
  if self.renderer.time<s['seconds']:self.wait(s['seconds']-self.renderer.time)
