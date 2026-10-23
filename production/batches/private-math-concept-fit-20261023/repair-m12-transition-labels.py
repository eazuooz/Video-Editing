"""CPU-only delta repair; retain previous masters and unchanged current scene hashes."""
from common import *
P=R/'projects/game-math-triangle-addresses-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';source=B/'m12-scenes.py';authorized('M12')
T=read(H/'timeline.json');r=read(H/'render-progress.json');changes=['PG04','14','PG06']
backup=H/'render-progress-before-transition-labels.json'
if not backup.exists():save(backup,r)
env=dict(os.environ,MATH_RENDER_TIMING=str(H/'timeline.json'),PYTHONUTF8='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
for sid in changes:
 s=next(s for s in T['scenes'] if s['id']==sid);dst=O/f'manim/videos/m12-scenes/1080p60/Scene{sid}.mp4';log=O/f'manim-label-fix-{sid}.log';print('Correct transition labels',sid,flush=True)
 with log.open('w',encoding='utf8') as f:subprocess.run([str(R/'manim/.venv/Scripts/python.exe'),'-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',str(O/'manim'),str(source),'Scene'+sid],cwd=R,env=env,stdout=f,stderr=f,check=True)
 m=next(v for v in probe(dst)['streams'] if v['codec_type']=='video');assert abs(int(m['nb_frames'])-s['frames'])<=2
 r['scenes'][sid].update(sha256=sha(dst),frames=int(m['nb_frames']),renderedAt=now())
r['identity']=hashlib.sha256((sha(source)+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest();r['deltaRepair']=dict(scenes=changes,reason='Remove stale negative/fixed weights during point animation; distinguish checking both conditions from passing both.',unchangedScenesPreserved=True);save(H/'render-progress.json',r)
comp=read(H/'composition.json');save(H/'composition-before-transition-labels.json',comp);comp['scenes']=[s for s in comp['scenes'] if s['id'] not in changes];comp['completed']=False;comp['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(B/'compose-m12.py')).encode()).hexdigest();save(H/'composition.json',comp)
for name in ['qa','outputs','caption-pixel-coverage']:
 if (H/(name+'.json')).exists():save(H/(name+'-before-transition-labels.json'),read(H/(name+'.json')))
print('Three label corrections rendered; composition and new outputs pending',flush=True)
