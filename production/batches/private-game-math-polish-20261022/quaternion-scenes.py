"""Original teaching actions/timing; isolated model legibility improvements."""
from pathlib import Path
import os,sys,json,types
from manim import *
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
slug=os.environ['POLISH_SLUG'];P=R/'projects'/slug
T=json.loads((P/'production/timeline.json').read_text(encoding='utf8'))
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
import lesson,quaternion

def aircraft(rotation,origin,scale=1.2):
 # +Z nose, +Y up in the lesson's logical coordinates; P is a proper rotation.
 fuselage=Sphere(radius=1,resolution=(8,12),fill_color='#d6a629',fill_opacity=1,stroke_width=0).scale([.15,.16,.86])
 canopy=Sphere(radius=1,resolution=(6,10),fill_color='#35475d',fill_opacity=1,stroke_width=0).scale([.11,.10,.25]).shift([0,.13,.24])
 wings=Polygon([-.95,0,-.12],[-.95,0,.05],[-.14,0,.31],[.14,0,.31],[.95,0,.05],[.95,0,-.12],fill_color='#e2e7ec',fill_opacity=1,stroke_color='#5d6774',stroke_width=1.2)
 tail=Polygon([-.38,.02,-.69],[0,.02,-.49],[.38,.02,-.69],[0,.02,-.79],fill_color='#52704c',fill_opacity=1,stroke_color='#3d5340',stroke_width=1)
 fin=Polygon([0,.03,-.78],[0,.36,-.70],[0,.03,-.45],fill_color='#d6a629',fill_opacity=1,stroke_color='#8a6b21',stroke_width=1)
 g=VGroup(fuselage,wings,tail,fin,canopy);g.apply_matrix(lesson.P@rotation);g.scale(scale,about_point=ORIGIN);g.shift(origin);return g

lesson.body=aircraft
quaternion.timing=lambda _slug,_data:T
def load_local(name,filename,old):
 p=R/'manim/projects/game-math-part2-teaching-revision'/filename
 s=p.read_text(encoding='utf8').replace(old,"Path(os.environ['POLISH_TIMING_MAP'])")
 module=types.ModuleType(name);module.__file__=str(p);sys.modules[name]=module;exec(compile(s,str(p),'exec'),module.__dict__);return module
supp=load_local('polish_supplements','supplements.py',"ROOT/'shared/output/game-math-part2-teaching-revision/supplement-timing.json'")
bridge=load_local('polish_bridges','bridges.py',"ROOT/'shared/output/game-math-part2-teaching-revision/bridge-timing.json'")
sys.path.insert(0,str(R/'manim/projects/game-math-part2-teaching-revision'))
import quaternion_four_game_v3 as cross
for slot in T['scenes']:
 if slot['classification']!='explanation':continue
 sid=slot['id']
 if sid.isdigit():base=quaternion.QuaternionScene;attrs={'slug':'game-math-quaternion-operations','sid':sid}
 elif sid.startswith('B'):base=bridge.Bridge;attrs={'sid':sid}
 elif sid.startswith(('QF','QC')):base=cross.CrossGameQuaternion;attrs={'sid':sid}
 else:base=supp.Supplement;attrs={'sid':sid}
 globals()['Polish'+sid]=type('Polish'+sid,(base,),{**attrs,'__module__':__name__})
