from common import *
import shutil,runpy
P=R/'projects/game-math-rotation-conversions-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
authorized('M08');backup=O/'before-summary-contrast-fix';backup.mkdir(exist_ok=True)
for name in ['render-progress.json','composition.json','outputs.json','qa.json','caption-pixel-coverage.json']:
 if not (backup/name).exists():shutil.copy2(H/name,backup/name)
source=B/'m08-summary-repair.py';env=dict(os.environ,PYTHONUTF8='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
dst=O/'summary-repair/videos/m08-summary-repair/1080p60/Summary.mp4'
if not dst.exists():
 with (O/'summary-contrast-fix.log').open('w',encoding='utf8') as f:
  subprocess.run([str(R/'manim/.venv/Scripts/python.exe'),'-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',str(O/'summary-repair'),str(source),'Summary'],cwd=R,env=env,stdout=f,stderr=f,check=True)
v=next(x for x in probe(dst)['streams'] if x['codec_type']=='video');assert abs(int(v['nb_frames'])-1918)<=2
d=read(H/'render-progress.json');d['scenes']['26']=dict(path=rel(dst),sha256=sha(dst),frames=int(v['nb_frames']),plannedFrames=1918,origin='Same closing content and audio; outline emphasis replaces unreadable filled highlight',repairSource=rel(source));save(H/'render-progress.json',d)
source=B/'compose-m08.py';d=read(H/'composition.json');d['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(source)).encode()).hexdigest();d['scenes']=[x for x in d['scenes'] if x['id']!='26'];d['completed']=False;save(H/'composition.json',d)
save(H/'summary-contrast-repair.json',dict(at=now(),reason='Original summary highlight filled over low-contrast text; preserve all five narrated points and31.9667s timing, replace highlight with a labeled outline.',source=rel(B/'m08-summary-repair.py'),review='pending encoded inspection'))
runpy.run_path(str(source),run_name='__main__')
