"""Preserve visible Space Engineers instructions above fixed caption band."""
import sys
from polish_common import *
e=Episode(sys.argv[1]);e.authorized();assert e.id in ['M05','M06']
sid={'M05':'QF20','M06':'QC20'}[e.id];s=next(x for x in e.T['scenes'] if x['id']==sid)
src=e.O/f'clips/{sid}.mp4';folder=e.O/'ui-clearance';folder.mkdir(exist_ok=True);dst=folder/f'{sid}.mp4'
record=e.H/'ui-clearance.json';old=read(record) if record.exists() else {}
vf='scale=1600:900:flags=lanczos,pad=1920:1080:160:0:black,setsar=1'
sig={'sourceSha256':sha(src),'vf':vf,'frames':s['frames']}
if not (dst.exists() and old.get('source')==sig):
 e.ff(['-i',src,'-vf',vf,'-frames:v',s['frames'],'-an',*ENC,dst],f'ui-clearance-{sid}.log')
e.verify(dst,s['frames'])
save(record,{'source':sig,'inputs':{sid:{'path':rel(dst),'sha256':sha(dst),'reason':'Aspect-preserving1600x900 inset reserves bottom180px for unchanged captions; game object and native controls/guide labels transform together'}},'preflight':'Exact filter sampled at spoken cue and caption band; final encoded review pending'})
