from common import *
import shutil
P=R/'projects/game-math-mesh-uv';H=P/'production/concept-fit-v2';authorized('M19');f=H/'render-progress.json';r=read(f);old=r['identity'];affected=['06','07','10','11','15'];backup=P/'production/local/concept-fit-v2/preflight-before-correction';backup.mkdir(exist_ok=True)
for sid in affected:
 row=r['scenes'].pop(sid);src=R/row['path'];dst=backup/f'Scene{sid}.mp4'
 if not dst.exists():shutil.copy2(src,dst)
 assert sha(dst)==row['sha256']
r['identity']=hashlib.sha256((sha(B/'m19-scenes.py')+sha(B/'m18-scenes.py')+sha(B/'m16-scenes.py')+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest();r['state']='running';save(f,r)
save(H/'preflight-correction.json',dict(at=now(),oldIdentity=old,newIdentity=r['identity'],affected=affected,reason='Tower was occluded by a house; moved it to the foreground. Normal arrows enlarged and rear-facing guides hidden. Hexagonal prism now evaluates fixed-light Lambert values with face versus interpolated vertex directions, preserving identical positions.',preserved=['All audio and timing','Unchanged mathematical clips','Scene02']))
