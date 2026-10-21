"""Finite, resumable source restoration. Visual polish/QA remain separate."""
import sys,os,traceback
from polish_common import *
results={};supported={'M07','M08','M09','M10','M11','M12','M15','M16','M17','M18','M19','M20'}
for ident in sys.argv[1:]:
 try:
  assert ident in supported;e=Episode(ident);e.authorized();save(e.O/'timing-map.json',{s['id']:s for s in e.T['scenes']})
  env=dict(os.environ,PYTHONUTF8='1',POLISH_SLUG=e.slug,POLISH_TIMING_MAP=str(e.O/'timing-map.json'),MATH_RENDER_TIMING=str(e.P/'production/timeline.json'),REVISION_FINAL_TIMING='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
  source=B/'lesson-scenes.py';record_path=e.H/'explanation-restoration.json';records=read(record_path) if record_path.exists() else {'scenes':{}}
  files=[source,B/'quaternion-scenes.py',*sorted((R/'manim/projects/game-math-part2-full-series').glob('*.py')),*sorted((R/'manim/projects/game-math-part2-teaching-revision').glob('*additions.py'))]
  provenance={rel(p):sha(p) for p in files};signature=hashlib.sha256(json.dumps(provenance,sort_keys=True).encode()).hexdigest()+sha(e.P/'production/timeline.json')
  for slot in e.T['scenes']:
   if slot['classification']!='explanation':continue
   e.authorized();sid=slot['id'];dst=e.O/f'manim/videos/lesson-scenes/1080p60/Polish{sid}.mp4'
   if dst.exists() and records['scenes'].get(sid,{}).get('signature')==signature:continue
   e.run([R/'manim/.venv/Scripts/python.exe','-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',e.O/'manim',source,'Polish'+sid],f'manim-{sid}.log',env=env)
   v=video(dst);assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
   records['scenes'][sid]={'signature':signature,'path':rel(dst),'sha256':sha(dst),'originalSceneSeconds':slot['seconds'],'visualQa':'pending'};records['sourceCode']=provenance;save(record_path,records);print(ident,sid,'restored; visual review pending',flush=True)
  results[ident]={'status':'explanation-code-restored','visualQa':'pending'}
 except Exception as error:
  results[ident]={'status':'needs-restoration-repair','error':str(error)[-2500:]};print(ident,'restoration needs repair:',str(error)[-600:],flush=True)
 save(B/'lesson-restoration-status.json',results)
