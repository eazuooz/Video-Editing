"""One finite sequential set of original-code-based FHD60 explanation renders."""
from common import *
import sys,shutil
P=R/'projects/game-math-orientation-matrices';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';source=B/'m03-scenes.py'
T=read(H/'timeline.json');authorized('M03-original');assert not (R/'shared/output/GPU_HANDOFF.json').exists(),'Preserve active model job'
identity=hashlib.sha256((sha(source)+sha(R/'manim/projects/game-math-part2-full-series/lesson.py')+sha(H/'timeline.json')).encode()).hexdigest()
recpath=H/'render-progress.json';d=read(recpath) if recpath.exists() else dict(identity=identity,scenes={},startedAt=now(),state='running')
assert d['identity']==identity,'Different-source renders preserved; review before reuse'
env=dict(os.environ,MATH_RENDER_TIMING=str(H/'timeline.json'),PYTHONUTF8='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
selected=sys.argv[1:] or [s['id'] for s in T['scenes']]
for sid in selected:
 authorized('M03-original');slot=next(s for s in T['scenes'] if s['id']==sid);dst=O/f'manim/videos/m03-scenes/1080p60/Scene{sid}.mp4'
 if sid in d['scenes']:
  assert dst.exists() and sha(dst)==d['scenes'][sid]['sha256'];continue
 assert shutil.disk_usage(R).free>15*2**30,'Keep disk headroom; no source deletion'
 d.update(state='rendering',activeScene=sid,updatedAt=now());save(recpath,d)
 log=O/f'manim-{sid}.log'
 print('Rendering original lesson scene',sid,slot['seconds'],'seconds',flush=True)
 with log.open('w',encoding='utf8') as f:
  runargs=[str(R/'manim/.venv/Scripts/python.exe'),'-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',str(O/'manim'),str(source),'Scene'+sid]
  p=subprocess.run(runargs,env=env,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:
  d.update(state='failed',failedScene=sid,error=log.read_text(encoding='utf8',errors='replace')[-2500:]);save(recpath,d);raise RuntimeError(d['error'])
 v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
 actual=int(v['nb_frames']);assert abs(actual-slot['frames'])<=2,(sid,actual,slot['frames'])
 d['scenes'][sid]=dict(path=rel(dst),sha256=sha(dst),frames=actual,plannedFrames=slot['frames'],renderedAt=now(),visualQa='pending encoded moving/captioned review');save(recpath,d)
d.update(state='rendered-qa-pending' if len(d['scenes'])==24 else 'partial-rendered',activeScene=None,updatedAt=now());save(recpath,d)
print(len(d['scenes']),'FHD60 scenes rendered; assembly/QA pending',flush=True)
