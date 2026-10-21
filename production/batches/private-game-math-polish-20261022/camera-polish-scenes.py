"""Retain original camera lesson geometry/clock; enlarge diagram guides only."""
from pathlib import Path
import os,sys,json
from manim import *
R=Path(__file__).resolve().parents[3]
slug='game-math-camera-frustum'
T=json.loads((R/'projects'/slug/'production/timeline.json').read_text(encoding='utf8'))
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
import camera_frustum as original
original.timing=lambda _slug,_data:T
base_edge=original.edge;base_label=original.label;base_diagram=original.diagram

def legible_edge(a,b,color=original.RULE,width=2,dashed=False):
 return base_edge(a,b,color,max(2.5,width*1.7),dashed)

def marked_label(p,value,color=original.INK,size=25,shift=(0,0,0)):
 obj=base_label(p,value,color,size,shift)
 obj.polish_label_value=value
 return obj

original.edge=legible_edge;original.label=marked_label

def legible_diagram(mode,i):
 obj=base_diagram(mode,i)
 mode=original.MODE_ALIASES.get(mode,mode)
 # Resize labels after the original common transform, keeping camera/model
 # positions and each FOV comparison at precisely the original shared scale.
 labels=[m for m in obj.get_family() if hasattr(m,'polish_label_value')]
 for m in labels:
  value=m.polish_label_value;anchor=m.get_center().copy()
  # Do not magnify overview thumbnails or every annotation indiscriminately:
  # they contain multiple separate models whose labels would collide.
  if mode in ['overview','summary']:continue
  target=0;shift=None
  if mode=='output' and value.startswith(('왼쪽 ','오른쪽 ')):
   # Keep the same words but put the pixel dimensions under the side name.
   ink=original.GREEN if value.startswith('왼쪽 ') else original.BLUE
   replacement=original.txt(value.replace(' ','\n',1),27,ink)
   replacement.scale(.53/max(replacement.height,.01)).move_to(anchor)
   replacement.add_background_rectangle(color=WHITE,opacity=.92,buff=.035)
   m.become(replacement);continue
  if value=='near':target=.32;shift=[-.48,.28,0]
  elif value=='far':target=.32;shift=[.65,-.28,0]
  elif value=='카메라':target=.26;shift=[-.12,-.16,0]
  elif mode=='planes' and value in ['0.5','6','12']:
   target=.32;shift={'0.5':[0,-.26,0],'6':[0,.32,0],'12':[.12,.42,0]}[value]
  elif mode in ['fov','zoom'] and value.startswith('폭 '):target=.29
  elif mode=='physical' and value.startswith('f='):target=.28;shift=[.25,-.30,0]
  elif mode=='physical' and value.startswith('센서 '):target=.28;shift=[-.10,.16,0]
  elif value.startswith('z='):target=.30
  elif value=='계산한 화면 크기':target=.27
  elif mode=='output':target=.27
  if target:m.scale(max(1,target/max(m.height,.01)))
  if shift:
   m.shift(shift)
   if value in ['near','far']:
    connector=Line(anchor,m.get_center(),color=original.GREEN if value=='near' else original.BLUE,stroke_width=2.4)
    obj.add_to_back(connector)
 return obj

original.diagram=legible_diagram
for name,base in original.make_scenes(slug,__name__).items():
 sid=name.removeprefix('Scene')
 globals()['Polish'+sid]=type('Polish'+sid,(base,),{'__module__':__name__})
