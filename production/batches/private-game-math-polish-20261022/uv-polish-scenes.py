"""Enlarge the existing dark UV lesson, preserving its corrected UV artwork."""
from pathlib import Path
import json,sys
from manim import *
R=Path(__file__).resolve().parents[3]
slug='game-math-normal-transform-uv'
T=json.loads((R/'projects'/slug/'production/timeline.json').read_text(encoding='utf8'))
lesson=json.loads((R/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
import normal_transform_uv as original
original.timing=lambda _slug,_data:T
base_diagram=original.diagram;base_text=original.txt
SCALES={}

def enlarged_diagram(mode,i):
 if mode not in SCALES:
  count=max(len(s['beats']) for s in lesson['scenes'] if s.get('mode')==mode)
  samples=[base_diagram(mode,j) for j in range(count)]
  SCALES[mode]=min(1.6,6.2/max(m.width for m in samples),3.2/max(m.height for m in samples))
 return base_diagram(mode,i).scale(SCALES[mode])

def readable_text(s,size=28,color=original.INK,font='Malgun Gothic'):
 if size==26 and color==original.BLUE:
  # Preserve the exact equation words and separators; line breaks only.
  lines=s.replace(' / ',' /\n').splitlines()
  lines=[line.replace(' → ',' →\n',1) if len(line)>34 and ' → ' in line else line for line in lines]
  return Text('\n'.join(lines),font=font,font_size=31,color=color,line_spacing=1.15)
 return base_text(s,size,color,font)

original.txt=readable_text
original.diagram=enlarged_diagram
for name,base in original.make_scenes(slug,__name__).items():
 globals()['Polish'+name.removeprefix('Scene')]=type('Polish'+name.removeprefix('Scene'),(base,),{'__module__':__name__})
