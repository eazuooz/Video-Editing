"""Restore unchanged original Manim logic; no new narration or lesson order."""
from pathlib import Path
import importlib.util,sys
R=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
import euler
retained={'01','13','16','24','25','26'}
globals().update({k:v for k,v in euler.make_scenes('game-math-euler-axis-angle',__name__).items() if v.sid in retained})
s=importlib.util.spec_from_file_location('original_brand',R/'manim/projects/game-math-polar-sample/scene.py')
b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
BrandIntro=type('BrandIntro',(b.BrandIntro,),{'__module__':__name__})
MemberOutro=type('MemberOutro',(b.MemberOutro,),{'__module__':__name__})
