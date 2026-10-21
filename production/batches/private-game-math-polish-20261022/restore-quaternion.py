"""Render reusable explanation clips from the unchanged approved timing."""
from pathlib import Path
import json,os,subprocess,hashlib,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ident=sys.argv[1];q=read(B/'queue.json');entry=next(x for x in q['entries'] if x['id']==ident);slug=entry['slug'];assert ident in ['M05','M06']
P=R/'projects'/slug;O=P/'production/local/private-polish-v1';H=P/'production/private-polish-v1';O.mkdir(parents=True,exist_ok=True)
T=read(P/'production/timeline.json');save(O/'timing-map.json',{s['id']:s for s in T['scenes']})
env=dict(os.environ,PYTHONUTF8='1',POLISH_SLUG=slug,POLISH_TIMING_MAP=str(O/'timing-map.json'),QUATERNION_COMPARISON_TIMING=str(P/'production/timeline.json'),REVISION_FINAL_TIMING='1')
source=B/'quaternion-scenes.py';records=read(H/'explanation-restoration.json') if (H/'explanation-restoration.json').exists() else {'scenes':{}}
for slot in T['scenes']:
 if slot['classification']!='explanation':continue
 a=read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations'][q['authorization']['id']];assert a['status']=='active' and ident in a['ids'];assert sha(P/'production/timeline.json')==entry['originalTimelineSha256']
 sid=slot['id'];sig=sha(source)+sha(P/'production/timeline.json');path=O/f'manim/videos/quaternion-scenes/1080p60/Polish{sid}.mp4'
 if path.exists() and records['scenes'].get(sid,{}).get('signature')==sig:continue
 log=O/f'manim-{sid}.log'
 with log.open('w',encoding='utf8') as f:
  p=subprocess.run([R/'manim/.venv/Scripts/python.exe','-m','manim','--resolution','1920,1080','--fps','60','--disable_caching','--media_dir',O/'manim',source,'Polish'+sid],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(log.read_text(encoding='utf8',errors='replace')[-2500:])
 records['scenes'][sid]={'signature':sig,'path':path.relative_to(R).as_posix(),'sha256':sha(path),'originalSceneSeconds':slot['seconds'],'visualQa':'pending'};save(H/'explanation-restoration.json',records);print(ident,sid,'restored; visual review pending',flush=True)
