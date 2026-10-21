"""Render reviewed original numeric polygon scenes with legibility-only changes."""
import sys
from polish_common import *
e=Episode(sys.argv[1]);assert e.id in ['M13','M14'];e.authorized()
preview=read(e.H/'polygon-legibility-preflight.json')
assert preview['status']=='passed-still-preflight'
assert preview['timelineSha256']==sha(e.P/'production/timeline.json')
for path,digest in preview['sourceCode'].items():assert sha(R/path)==digest
signature=hashlib.sha256(json.dumps(preview['sourceCode'],sort_keys=True).encode()).hexdigest()+preview['timelineSha256']
out=e.O/'polygon-legibility';out.mkdir(exist_ok=True);(out/'clips').mkdir(exist_ok=True)
record=e.H/'polygon-legibility-render.json';data=read(record) if record.exists() else {'scenes':{}}
data.update(sourceCode=preview['sourceCode'],timelineSha256=preview['timelineSha256'],visualQa='pending-final-moving-review')
env=dict(os.environ,PYTHONUTF8='1',POLISH_SLUG=e.slug,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
for slot in e.T['scenes']:
 if slot['classification']!='explanation' or not slot['id'].isdigit():continue
 e.authorized();sid=slot['id'];dst=out/f'clips/{sid}.mp4';old=data['scenes'].get(sid,{})
 if old.get('signature')==signature and dst.exists() and sha(dst)==old['sha256']:
  e.verify(dst,slot['frames']);continue
 raw=out/f'manim/videos/polygon-legibility-scenes/1080p60/Polish{sid}.mp4'
 e.run([R/'manim/.venv/Scripts/python.exe','-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',out/'manim',B/'polygon-legibility-scenes.py','Polish'+sid],f'polygon-legibility-manim-{sid}.log',env=env)
 v=video(raw);assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
 difference=slot['frames']-int(v['nb_frames']);assert abs(difference)<=4,(sid,difference)
 e.ff(['-i',raw,'-vf','fps=60,tpad=stop_mode=clone:stop_duration=0.1,setsar=1','-frames:v',slot['frames'],'-an',*ENC,dst],f'polygon-legibility-normalize-{sid}.log');e.verify(dst,slot['frames'])
 data['scenes'][sid]={'signature':signature,'path':rel(dst),'sha256':sha(dst),'rawPath':rel(raw),'rawSha256':sha(raw),'frames':slot['frames'],'roundingFrameAdjustment':difference,'reason':'Original logical geometry, vertex indices, worked values and clock; larger labels/formulas and header-safe screen mapping'}
 save(record,data);print(e.id,sid,'polygon legibility rendered; final QA pending',flush=True)
