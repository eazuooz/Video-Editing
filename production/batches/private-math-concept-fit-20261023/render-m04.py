"""Nine changed scenes; preserve the other17 approved Unity/Manim scene files."""
from common import *
import sys,shutil
P=R/'projects/game-math-euler-axis-angle';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';source=B/'m04-scenes.py'
T=read(H/'timeline.json');authorized('M04');assert not (R/'shared/output/GPU_HANDOFF.json').exists()
old={x['scene']:x for x in read(P/'production/private-polish-v1/assembly.json')['scenes']};changed=set(read(B/'m04-narration-edits.json')['edits'])
identity=hashlib.sha256((sha(source)+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest();rec=H/'render-progress.json'
d=read(rec) if rec.exists() else dict(identity=identity,scenes={},startedAt=now(),state='running')
assert d['identity']==identity
env=dict(os.environ,MATH_RENDER_TIMING=str(H/'timeline.json'),PYTHONUTF8='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
for s in T['scenes']:
 sid=s['id'];authorized('M04')
 if sid in d['scenes']:
  assert sha(R/d['scenes'][sid]['path'])==d['scenes'][sid]['sha256'];continue
 if sid not in changed:
  r=old[sid];assert r['frames']==s['frames'] and sha(R/r['file'])==r['sha256'];d['scenes'][sid]=dict(path=r['file'],sha256=r['sha256'],frames=r['frames'],plannedFrames=s['frames'],origin='unchanged approved Unity/Manim clip');save(rec,d);continue
 assert shutil.disk_usage(R).free>15*2**30
 d.update(state='rendering',activeScene=sid,updatedAt=now());save(rec,d)
 dst=O/f'manim/videos/m04-scenes/1080p60/Scene{sid}.mp4';log=O/f'manim-{sid}.log'
 print('M04 replacement scene',sid,s['seconds'],flush=True)
 with log.open('w',encoding='utf8') as f:
  p=subprocess.run([str(R/'manim/.venv/Scripts/python.exe'),'-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',str(O/'manim'),str(source),'Scene'+sid],cwd=R,env=env,stdout=f,stderr=f)
 if p.returncode:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-2500:])
 v=next(x for x in probe(dst)['streams'] if x['codec_type']=='video');assert v['height']==1080 and v['r_frame_rate']=='60/1' and abs(int(v['nb_frames'])-s['frames'])<=2
 d['scenes'][sid]=dict(path=rel(dst),sha256=sha(dst),frames=int(v['nb_frames']),plannedFrames=s['frames'],origin='revised concept-matched demonstration',renderedAt=now());save(rec,d)
d.update(state='rendered-qa-pending',updatedAt=now(),activeScene=None);save(rec,d)
print('M04:26 scenes ready,17 preserved without rerender; composition/QA pending',flush=True)
