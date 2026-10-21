"""Render the reviewed visual-only mesh wrapper without overwriting baselines."""
import sys
from polish_common import *
e=Episode(sys.argv[1]);assert e.id in ['M19','M20'];e.authorized()
module='uv' if e.id=='M20' else 'mesh'
preview=read(e.H/'mesh-legibility-preflight.json')
assert preview['status']=='passed-still-preflight'
assert rel(B/f'{module}-polish-scenes.py') in preview['sourceCode'],'Preflight must use the original episode module'
assert preview['timelineSha256']==sha(e.P/'production/timeline.json')
for path,digest in preview['sourceCode'].items():assert sha(R/path)==digest
signature=hashlib.sha256(json.dumps(preview['sourceCode'],sort_keys=True).encode()).hexdigest()+preview['timelineSha256']
out=e.O/'mesh-polish';out.mkdir(exist_ok=True);(out/'clips').mkdir(exist_ok=True)
record=e.H/'mesh-legibility-render.json';data=read(record) if record.exists() else {'scenes':{}}
data.update(sourceCode=preview['sourceCode'],timelineSha256=preview['timelineSha256'],visualQa='pending-final-moving-review')
env=dict(os.environ,PYTHONUTF8='1',POLISH_SLUG=e.slug,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1')
for slot in e.T['scenes']:
 if slot['classification']!='explanation':continue
 e.authorized();sid=slot['id'];dst=out/f'clips/{sid}.mp4';old=data['scenes'].get(sid,{})
 if old.get('signature')==signature and dst.exists() and sha(dst)==old['sha256']:
  e.verify(dst,slot['frames']);continue
 raw=out/f'manim/videos/{module}-polish-scenes/1080p60/Polish{sid}.mp4'
 e.run([R/'manim/.venv/Scripts/python.exe','-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',out/'manim',B/f'{module}-polish-scenes.py','Polish'+sid],f'mesh-polish-manim-{sid}.log',env=env)
 v=video(raw);assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
 difference=slot['frames']-int(v['nb_frames']);assert abs(difference)<=4,(sid,difference)
 e.ff(['-i',raw,'-vf','fps=60,tpad=stop_mode=clone:stop_duration=0.1,setsar=1','-frames:v',slot['frames'],'-an',*ENC,dst],f'mesh-polish-normalize-{sid}.log');e.verify(dst,slot['frames'])
 data['scenes'][sid]={'signature':signature,'path':rel(dst),'sha256':sha(dst),'rawPath':rel(raw),'rawSha256':sha(raw),'frames':slot['frames'],'roundingFrameAdjustment':difference,'reason':'Same model and original state/clock; common enlargement per comparison mode, semantic code colors retained at larger size'}
 save(record,data);print(e.id,sid,'mesh visual wrapper rendered; final QA pending',flush=True)
