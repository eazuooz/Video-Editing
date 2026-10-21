"""Preserve mesh/normal lesson mechanics and time; enlarge original diagrams."""
from pathlib import Path
import json,os,sys
from manim import *
R=Path(__file__).resolve().parents[3]
slug=os.environ['POLISH_SLUG']
assert slug in ['game-math-mesh-uv','game-math-normal-transform-uv']
T=json.loads((R/'projects'/slug/'production/timeline.json').read_text(encoding='utf8'))
lesson=json.loads((R/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
import mesh_uv as original
original.timing=lambda _slug,_data:T
base_diagram=original.diagram;base_text=original.Text
SCALES={}

def enlarged_diagram(mode,i):
 if mode not in SCALES:
  count=max(len(s['beats']) for s in lesson['scenes'] if s.get('mode')==mode)
  samples=[base_diagram(mode,j) for j in range(count)]
  # Every state of the comparison uses one scale, so changing a normal or
  # UV does not secretly change the apparent size of the object.
  SCALES[mode]=min(1.6,6.2/max(m.width for m in samples),3.2/max(m.height for m in samples))
 return base_diagram(mode,i).scale(SCALES[mode])

def legible_code(*args,**kwargs):
 if kwargs.get('font')=='Consolas':kwargs['font_size']=34
 return base_text(*args,**kwargs)

original.diagram=enlarged_diagram;original.Text=legible_code
for name,base in original.make_scenes(slug,__name__).items():
 globals()['Polish'+name.removeprefix('Scene')]=type('Polish'+name.removeprefix('Scene'),(base,),{'__module__':__name__})
