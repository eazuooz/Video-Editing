from common import *
import shutil
P=R/'projects/game-math-camera-frustum';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';authorized('M16')
for name in ['render-progress','composition','outputs','qa','caption-pixel-coverage']:
 dst=H/f'{name}-before-pane-repair.json'
 if not dst.exists():shutil.copy2(H/f'{name}.json',dst)
r=read(H/'render-progress.json');r['identity']=hashlib.sha256((sha(B/'m16-scenes.py')+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest()
env=dict(os.environ,MATH_RENDER_TIMING=str(H/'timeline.json'),PYTHONUTF8='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
with (O/'manim-16-pane-repair.log').open('w',encoding='utf8') as f:
 subprocess.run([str(R/'manim/.venv/Scripts/python.exe'),'-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',str(O/'manim'),str(B/'m16-scenes.py'),'Scene16'],cwd=R,env=env,stdout=f,stderr=f,check=True)
dst=O/'manim/videos/m16-scenes/1080p60/Scene16.mp4';r['scenes']['16']['sha256']=sha(dst);r['scenes']['16']['renderedAt']=now();save(H/'render-progress.json',r)
c=read(H/'composition.json');c['scenes']=[s for s in c['scenes'] if s['id']!='16'];c['completed']=False;c['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(B/'compose-m16.py')).encode()).hexdigest();save(H/'composition.json',c)
save(H/'pane-repair.json',dict(scene='16',reason='Always-redraw model retained left pixels during a frozen Wait while new prose moved left. Force immediate model update when changing pane.',frameTime=708.337,mathNarrationTimingUnchanged=True,otherCompositeCount=21))
run(['C:/Python/python.exe','-X','utf8',B/'compose-m16.py'])
print('M16 scene16 repaired; wait for parent playback before replacing complete master')
