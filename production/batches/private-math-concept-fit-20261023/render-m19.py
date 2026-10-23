"""Reuse unchanged lecture clips; rerender only altered game-dependent passages."""
from common import *
import shutil
P=R/'projects/game-math-mesh-uv';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';source=B/'m19-scenes.py'
T=read(H/'timeline.json');authorized('M19');assert not (R/'shared/output/GPU_HANDOFF.json').exists()
old={x['id']:x for x in read(P/'production/private-polish-v1/assembly.json')['scenes']};changed=set(read(B/'m19-narration-edits.json')['edits'])|set(read(B/'m19-narration-edits.json')['visualOnlyScenes'])
identity=hashlib.sha256((sha(source)+sha(B/'m18-scenes.py')+sha(B/'m16-scenes.py')+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest();rec=H/'render-progress.json'
d=read(rec) if rec.exists() else dict(identity=identity,scenes={},startedAt=now(),state='running');assert d['identity']==identity
env=dict(os.environ,MATH_RENDER_TIMING=str(H/'timeline.json'),PYTHONUTF8='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
for s in T['scenes']:
 sid=s['id'];authorized('M19')
 if sid in d['scenes']:
  assert sha(R/d['scenes'][sid]['path'])==d['scenes'][sid]['sha256'];continue
 if sid not in changed:
  r=old[sid];assert r['frames']==s['frames'] and sha(R/r['path'])==r['sha256'];d['scenes'][sid]=dict(path=r['path'],sha256=r['sha256'],frames=r['frames'],plannedFrames=s['frames'],origin='unchanged approved math clip');save(rec,d);continue
 assert shutil.disk_usage(R).free>15*2**30
 d.update(state='rendering',activeScene=sid,updatedAt=now());save(rec,d)
 dst=O/f'manim/videos/m19-scenes/1080p60/Scene{sid}.mp4';log=O/f'manim-{sid}.log'
 print('M19 replacement scene',sid,s['seconds'],flush=True)
 with log.open('w',encoding='utf8') as f:p=subprocess.run([str(R/'manim/.venv/Scripts/python.exe'),'-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',str(O/'manim'),str(source),'Scene'+sid],cwd=R,env=env,stdout=f,stderr=f)
 if p.returncode:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-2500:])
 video=next(x for x in probe(dst)['streams'] if x['codec_type']=='video');assert video['height']==1080 and video['r_frame_rate']=='60/1' and abs(int(video['nb_frames'])-s['frames'])<=2
 d['scenes'][sid]=dict(path=rel(dst),sha256=sha(dst),frames=int(video['nb_frames']),plannedFrames=s['frames'],origin='concept-matched own model',renderedAt=now());save(rec,d)
d.update(state='rendered-qa-pending',updatedAt=now(),activeScene=None);save(rec,d)
print('M19 scene rendering complete; composition and actual-file QA pending',flush=True)
