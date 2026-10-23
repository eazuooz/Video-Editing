from common import *
import shutil
P=R/'projects/game-math-normal-transform-uv';H=P/'production/concept-fit-v2';f=H/'render-progress.json';r=read(f);old=r['identity'];affected=['05','08','12'];backup=P/'production/local/concept-fit-v2/preflight-before-correction';backup.mkdir(exist_ok=True)
for sid in affected:
 row=r['scenes'].pop(sid);src=R/row['path'];dst=backup/f'Scene{sid}.mp4'
 if not dst.exists():shutil.copy2(src,dst)
 assert sha(dst)==row['sha256']
r['identity']=hashlib.sha256((sha(B/'m20-scenes.py')+sha(B/'m18-scenes.py')+sha(B/'m16-scenes.py')+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest();r.update(state='ready-to-resume',updatedAt=now());save(f,r)
save(H/'preflight-correction.json',dict(checkedAt=now(),oldIdentity=old,newIdentity=r['identity'],affected=affected,reason='The coplanar whole roof covered part of the separately sorted checker. Removed redundant whole roof faces while keeping the identical tiled surface. Draw visible attached windows over their front wall to avoid centre-sort occlusion. All audio/timing and unaffected math clips preserved.'))
print('M20 three model clips scheduled for corrected rerender')
