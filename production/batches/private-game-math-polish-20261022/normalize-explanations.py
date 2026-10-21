"""Preserve approved scene frame counts after native FHD rerender."""
import sys
from polish_common import *
e=Episode(sys.argv[1]);records=read(e.H/'explanation-restoration.json');out={'scenes':{}};target=e.H/'normalized-explanations.json'
if target.exists():out=read(target)
(e.O/'clips').mkdir(exist_ok=True)
for s in e.T['scenes']:
 if s['classification']!='explanation':continue
 e.authorized();sid=s['id'];record=records['scenes'][sid];src=R/record['path'];assert sha(src)==record['sha256'];dst=e.O/f'clips/{sid}.mp4';v=video(src)
 difference=s['frames']-int(v['nb_frames']);assert abs(difference)<=4,(sid,'Review original animation timing before trimming or extending',difference)
 if dst.exists() and out['scenes'].get(sid,{}).get('sourceSha256')==record['sha256']:e.verify(dst,s['frames']);continue
 e.ff(['-i',src,'-vf','fps=60,tpad=stop_mode=clone:stop_duration=0.1,setsar=1','-frames:v',s['frames'],'-an',*ENC,dst],f'normalize-{sid}.log');e.verify(dst,s['frames'])
 out['scenes'][sid]={'sourceSha256':record['sha256'],'path':rel(dst),'sha256':sha(dst),'frames':s['frames'],'roundingFrameAdjustment':difference,'visualReview':'pending'};save(target,out);print(e.id,sid,'normalized',flush=True)
