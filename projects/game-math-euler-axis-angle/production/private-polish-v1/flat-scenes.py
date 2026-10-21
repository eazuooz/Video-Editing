"""Restore unchanged original Manim logic; no new narration or lesson order."""
from pathlib import Path
import importlib.util,sys,inspect
R=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
import euler
retained={'01','13','16','24','25','26'}
globals().update({k:v for k,v in euler.make_scenes('game-math-euler-axis-angle',__name__).items() if v.sid in retained})
# The original rate labels state 720/1080 degrees per SECOND. Complete the
# corresponding two/three turns in one second, preserving the original scene
# duration and narration. Isolate this visual correction from upstream code.
fixed_source=inspect.getsource(euler.EulerScene).replace('run_time=2,rate_func=linear)','run_time=1,rate_func=linear)')
assert fixed_source!=inspect.getsource(euler.EulerScene)
fixed_ns=dict(euler.__dict__);exec(compile(fixed_source,__file__,'exec'),fixed_ns)
Scene24=type('Scene24',(fixed_ns['EulerScene'],),{'slug':'game-math-euler-axis-angle','sid':'24','__module__':__name__})
s=importlib.util.spec_from_file_location('original_brand',R/'manim/projects/game-math-polar-sample/scene.py')
b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
BrandIntro=type('BrandIntro',(b.BrandIntro,),{'__module__':__name__})
MemberOutro=type('MemberOutro',(b.MemberOutro,),{'__module__':__name__})
