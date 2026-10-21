"""Restore existing lesson programs against the existing episode clock."""
from pathlib import Path
import ast,importlib,os,sys,json,types
from manim import *
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
slug=os.environ['POLISH_SLUG'];T=json.loads((R/'projects'/slug/'production/timeline.json').read_text(encoding='utf8'))
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
import lesson
mapping={
 'game-math-interpolation-paths-v2':('interpolation','game-math-rotation-interpolation','interpolation_additions','InterpolationAddition'),
 'game-math-rotation-conversions-v2':('interpolation','game-math-rotation-interpolation','interpolation_additions','InterpolationAddition'),
 'game-math-lines-circles-v2':('geometry','game-math-lines-bounds','lines_additions','LinesAddition'),
 'game-math-bounds-transform-v2':('geometry','game-math-lines-bounds','lines_additions','LinesAddition'),
 'game-math-plane-distances-v2':('geometry_planes','game-math-planes-barycentric','planes_additions','PlaneAddition'),
 'game-math-triangle-addresses-v2':('geometry_planes','game-math-planes-barycentric','planes_additions','PlaneAddition'),
}
if slug in mapping:modname,base_slug,addition,cls=mapping[slug]
else:modname=slug.removeprefix('game-math-').replace('-','_');base_slug=slug;addition=None
# The rotation lessons use the same axis conventions with a recognizable plane.
if modname=='interpolation':
 tree=ast.parse((B/'quaternion-scenes.py').read_text(encoding='utf8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='aircraft')
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(B/'quaternion-scenes.py'),'exec'),globals());lesson.body=aircraft
main=importlib.import_module(modname);classes=main.make_scenes(base_slug,__name__)
if addition:
 path=R/'manim/projects/game-math-part2-teaching-revision'/(addition+'.py');source=path.read_text(encoding='utf8')
 source=source.replace("O/'combined-addition-timing.json'","Path(os.environ['POLISH_TIMING_MAP'])")
 extra=types.ModuleType('polish_'+addition);extra.__file__=str(path);sys.modules[extra.__name__]=extra;exec(compile(source,str(path),'exec'),extra.__dict__)
for slot in T['scenes']:
 if slot['classification']!='explanation':continue
 sid=slot['id'];base=classes['Scene'+sid] if sid.isdigit() else getattr(extra,cls)
 globals()['Polish'+sid]=type('Polish'+sid,(base,),{'sid':sid,'__module__':__name__})
