from common import *
P=R/'projects/game-math-quaternion-foundations-v3';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';authorized('M05')
r=read(H/'render-progress.json');assert r['state']=='rendered-qa-pending','Preserve current running render; repair after its safe completion'
source=B/'m05-b06-correction.py';dst=O/'manim/videos/m05-b06-correction/1080p60/CorrectB06.mp4';receipt=H/'b06-correction.json'
if not receipt.exists():
 env=dict(os.environ,MATH_RENDER_TIMING=str(H/'timeline.json'),PYTHONUTF8='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
 with (O/'manim-B06-correction.log').open('w',encoding='utf8') as f:
  subprocess.run([R/'manim/.venv/Scripts/python.exe','-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',O/'manim',source,'CorrectB06'],cwd=R,env=env,stdout=f,stderr=f,check=True)
 v=next(s for s in probe(dst)['streams'] if s['codec_type']=='video');assert abs(int(v['nb_frames'])-r['scenes']['B06']['plannedFrames'])<=2
 save(receipt,dict(before=r['scenes']['B06'],path=rel(dst),sha256=sha(dst),frames=int(v['nb_frames']),sourceSha256=sha(source),reason='Actual90-degree step applied twice, synchronized to the question. Generic30-degree tilt was an insufficient demonstration.',actualVisualReview='pending',recordedAt=now()))
fix=read(receipt);assert sha(dst)==fix['sha256'] and sha(source)==fix['sourceSha256']
r['scenes']['B06']=dict(path=fix['path'],sha256=fix['sha256'],frames=fix['frames'],plannedFrames=fix['before']['plannedFrames'],origin='concept-matched own model',correction=rel(receipt));save(H/'render-progress.json',r)
print('B06 corrected; full composition QA still required')
