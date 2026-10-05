"""Repair only explicitly selected final scenes; retain timing and all raw voices."""
from pathlib import Path
import sys,importlib.util,json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[3]
slug=sys.argv[1];ids=sys.argv[2:]
assert ids and all(i.isdigit() for i in ids)
work=ROOT/'shared/output'/slug;base=ROOT/'projects'/slug
spec=importlib.util.spec_from_file_location('caption_tools',ROOT/'projects/game-math-polar-sample/production/build.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.BASE=base;b.WORK=work;b.MF=base/'project.json'
timeline=b.read(base/'production/timeline.json')
vdir=work/'manim/videos/scene/1080p60'
b.run([sys.executable,'-m','manim','-qh','--disable_caching','--media_dir',work/'manim',ROOT/f'manim/projects/{slug}/scene.py',*['Scene'+i for i in ids]],'visual-repair-manim.log')
for sid in ids:
 s=next(s for s in timeline['scenes'] if s['id']==sid)
 target=work/'clips'/f'{sid}.mp4'
 b.ff(['-i',vdir/f'Scene{sid}.mp4','-vf','fps=60,setsar=1,tpad=stop_mode=clone:stop_duration=0.05','-frames:v',str(s['frames']),*b.ENC,target],f'visual-repair-{sid}.log')
 import shutil
 shutil.copy2(target,ROOT/f'motion-canvas/src/projects/{slug}/assets/{sid}.mp4')
assert b.read(base/'production/timeline.json')==timeline
b.write(work/'visual-repair.json',{'scenes':ids,'reason':'Decimal matrix cells overlapped in final pixels; code emphasis also made paragraph-specific. All raw narration and measured timing preserved.','timelineUnchanged':True,'sourceSha256':b.sha(ROOT/'manim/projects/game-math-part2-full-series/lesson.py'),'humanListening':'pending'})
for stage in ['mix','burn','qa']:
 subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).parent/'build.py'),slug,stage],cwd=ROOT,check=True)
