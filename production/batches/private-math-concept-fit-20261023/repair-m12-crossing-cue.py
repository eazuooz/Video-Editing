from common import *
P=R/'projects/game-math-triangle-addresses-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';source=B/'m12-scenes.py';authorized('M12')
for name in ['render-progress','composition','qa','outputs','caption-pixel-coverage']:
 p=H/(name+'-before-crossing-cue.json')
 if not p.exists():save(p,read(H/(name+'.json')))
T=read(H/'timeline.json');r=read(H/'render-progress.json');sid='PG04';s=next(x for x in T['scenes'] if x['id']==sid)
env=dict(os.environ,MATH_RENDER_TIMING=str(H/'timeline.json'),PYTHONUTF8='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
with (O/'manim-PG04-crossing-cue.log').open('w',encoding='utf8') as f:subprocess.run([str(R/'manim/.venv/Scripts/python.exe'),'-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',str(O/'manim'),str(source),'ScenePG04'],cwd=R,env=env,stdout=f,stderr=f,check=True)
dst=O/'manim/videos/m12-scenes/1080p60/ScenePG04.mp4';m=next(x for x in probe(dst)['streams'] if x['codec_type']=='video');assert abs(int(m['nb_frames'])-s['frames'])<=2
r['scenes'][sid].update(sha256=sha(dst),frames=int(m['nb_frames']),renderedAt=now());r['identity']=hashlib.sha256((sha(source)+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest();r['crossingCueRepair']=dict(scene=sid,reason='Reach outside position when narration says the point has crossed; start motion during preceding moving-point clause',audioUnchanged=True);save(H/'render-progress.json',r)
c=read(H/'composition.json');c['scenes']=[x for x in c['scenes'] if x['id']!=sid];c['completed']=False;c['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(B/'compose-m12.py')).encode()).hexdigest();save(H/'composition.json',c)
print('Single-scene timing repaired; wait for current full playback before replacing master')
