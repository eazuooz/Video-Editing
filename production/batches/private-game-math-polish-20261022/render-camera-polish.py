"""Render only the inspected M16 visual wrapper on the unchanged lesson clock."""
from polish_common import *

e=Episode('M16');e.authorized()
preview=read(e.H/'camera-legibility-preflight.json')
assert preview['status']=='passed-still-preflight'
assert preview['timelineSha256']==sha(e.P/'production/timeline.json')
for path,digest in preview['sourceCode'].items():assert sha(R/path)==digest
source=B/'camera-polish-scenes.py'
signature=hashlib.sha256(json.dumps(preview['sourceCode'],sort_keys=True).encode()).hexdigest()+preview['timelineSha256']
out=e.O/'camera-polish';out.mkdir(exist_ok=True);(out/'clips').mkdir(exist_ok=True)
record=e.H/'camera-legibility-render.json'
data=read(record) if record.exists() else {'scenes':{}}
data.update(sourceCode=preview['sourceCode'],timelineSha256=preview['timelineSha256'],visualQa='pending-final-moving-review')
env=dict(os.environ,PYTHONUTF8='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
for slot in e.T['scenes']:
 if slot['classification']!='explanation':continue
 e.authorized();sid=slot['id'];dst=out/f'clips/{sid}.mp4'
 old=data['scenes'].get(sid,{})
 if old.get('signature')==signature and dst.exists() and sha(dst)==old['sha256']:
  e.verify(dst,slot['frames']);continue
 raw=out/f'manim/videos/camera-polish-scenes/1080p60/Polish{sid}.mp4'
 e.run([R/'manim/.venv/Scripts/python.exe','-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',out/'manim',source,'Polish'+sid],f'camera-polish-manim-{sid}.log',env=env)
 v=video(raw);assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
 difference=slot['frames']-int(v['nb_frames']);assert abs(difference)<=4,(sid,difference)
 e.ff(['-i',raw,'-vf','fps=60,tpad=stop_mode=clone:stop_duration=0.1,setsar=1','-frames:v',slot['frames'],'-an',*ENC,dst],f'camera-polish-normalize-{sid}.log')
 e.verify(dst,slot['frames'])
 data['scenes'][sid]={'signature':signature,'path':rel(dst),'sha256':sha(dst),'rawPath':rel(raw),'rawSha256':sha(raw),'frames':slot['frames'],'roundingFrameAdjustment':difference,'reason':'Original geometry/state transform, words and timing retained; thicker guide strokes and selected readable labels'}
 save(record,data);print('M16',sid,'visual wrapper rendered; final QA pending',flush=True)
