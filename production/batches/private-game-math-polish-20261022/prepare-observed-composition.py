"""Apply observed UI clearance before the already reviewed screen-space guides."""
import sys
from polish_common import *
e=Episode(sys.argv[1]);e.authorized()
guide=read(e.H/'observed-guide-composition.json');preflight=read(e.H/'observed-guide-preflight.json')
assert guide['timelineSha256']==sha(e.P/'production/timeline.json')
assert preflight['status']=='passed-still-preflight'
assert preflight['assSha256']==guide['globalAssSha256']==sha(R/guide['globalAss'])
assert guide['planSha256']==sha(R/guide['plan'])
old=read(e.H/'observed-ui-clearance.json') if (e.H/'observed-ui-clearance.json').exists() else {}
folder=e.O/'ui-clearance';folder.mkdir(exist_ok=True);inputs={};receipts={}
vf='scale=1600:900:flags=lanczos,pad=1920:1080:160:0:black,setsar=1'
for sid in guide['captionClearanceScenes']:
 e.authorized();s=next(x for x in e.T['scenes'] if x['id']==sid)
 src=e.O/f'clips/{sid}.mp4';e.verify(src,s['frames']);dst=folder/f'{sid}.mp4'
 signature={'sourceSha256':sha(src),'vf':vf,'frames':s['frames']}
 if not (dst.exists() and old.get(sid,{}).get('source')==signature):
  e.ff(['-i',src,'-vf',vf,'-frames:v',s['frames'],'-an',*ENC,dst],f'observed-ui-clearance-{sid}.log')
 e.verify(dst,s['frames']);inputs[sid]={'path':rel(dst),'sha256':sha(dst),'reason':'Observed native controls preserved above fixed captions by aspect-preserving1600x900 inset; guide mapping already matches this transform'}
 receipts[sid]={'source':signature,**inputs[sid]}
save(e.H/'observed-ui-clearance.json',receipts)
save(e.H/'composition-polish.json',{**guide,'inputs':inputs,'internalVisualQa':'pending','changes':'Observed editorial region guides and native UI clearance only; original scene sequence, duration and recovered audio unchanged'})
print(e.id,'observed composition registered; final moving QA pending',flush=True)
