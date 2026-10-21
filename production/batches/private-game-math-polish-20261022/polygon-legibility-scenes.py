"""Enlarge original numeric polygon labels/formulas; keep geometry and clock."""
import importlib.util,inspect,textwrap
from pathlib import Path
p=Path(__file__).with_name('polygon-scenes.py')
spec=importlib.util.spec_from_file_location('polygon_recovery',p);recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)
original=recovery.original
base_txt=original.txt;base_card=original.card

def readable_text(value,size=28,color=original.INK,font='Malgun Gothic'):
 # Preserve every string, anchor, diagram size and calculation. Only existing
 # undersized labels/footnotes/equations are enlarged within their old regions.
 size={19:26,20:25,21:26,22:28,26:32}.get(size,size)
 return base_txt(value,size,color,font)

def readable_card(value,width=6,size=29,color=original.BLUE):
 return base_card(value,width,max(28,size),color)

original.txt=readable_text;original.card=readable_card
original.timing=lambda _slug,_data:recovery.T
# Native QA found the old circumcircle crossing the subtitle, and enlarged
# top vertex labels touching its rule. Change only the diagram's screen mapping.
CONSTRUCT_SOURCE=textwrap.dedent(inspect.getsource(original.TrianglePolygonScene.construct))
needle="if mode=='circumcenter':C=np.array([-5.2,.1,0.]);scale=.6"
assert CONSTRUCT_SOURCE.count(needle)==1
CONSTRUCT_SOURCE=CONSTRUCT_SOURCE.replace(needle,"if mode=='circumcenter':C=np.array([-5.2,.1,0.]);scale=.48")
needle="C=np.array([-5.2,-1.2,0.]);scale=.8"
assert CONSTRUCT_SOURCE.count(needle)==2
replacement="C=np.array([-5.2,-1.45 if mode in ['polygon-boundary','polygon-turns','concave-fan','ear-first','ear-sequence','polygon-practice'] else -1.2,0.]);scale=.8"
CONSTRUCT_SOURCE=CONSTRUCT_SOURCE.replace(needle,replacement)
scope=dict(original.__dict__);exec(compile(CONSTRUCT_SOURCE,__file__,'exec'),scope)
original.TrianglePolygonScene.construct=scope['construct']
for slot in recovery.T['scenes']:
 if slot['classification']!='explanation' or not slot['id'].isdigit():continue
 sid=slot['id'];parent=getattr(recovery,'Polish'+sid)
 globals()['Polish'+sid]=type('Polish'+sid,(parent,),{'__module__':__name__})
