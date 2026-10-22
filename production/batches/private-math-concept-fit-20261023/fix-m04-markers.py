from common import *
import sys,shutil
H=R/'projects/game-math-euler-axis-angle/production/concept-fit-v2';authorized('M04')
archive=H/'qa-round1';archive.mkdir(exist_ok=True)
for n in ['composition.json','outputs.json','qa.json','caption-pixel-coverage.json']:
 if not (archive/n).exists():shutil.copy2(H/n,archive/n)
receipt=H/'marker-repair.json'
if not receipt.exists():
 c=read(H/'composition.json');c['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(B/'compose-m04.py')).encode()).hexdigest();c['scenes']=[s for s in c['scenes'] if s['id'] not in ['02','14','20']];c['completed']=False;save(H/'composition.json',c)
 save(receipt,dict(status='repairing',reason='Direct viewing of all10 sheets/112 encoded frames found ASS negative drawing-coordinate bbox offset. Use nonnegative circle geometry and explicit top-left anchor.',changedScenes=['02','14','20'],unchangedScenes=23,audioUnchanged=True,startedAt=now()))
for script,args in [('compose-m04.py',[]),('assemble-m04.py',[]),('qa-m04.py',[]),('caption-pixel-coverage.py',['game-math-euler-axis-angle'])]:
 authorized('M04');subprocess.run([sys.executable,'-u',str(B/script),*args],cwd=R,check=True)
d=read(receipt);d.update(status='encoded-direct-review-pending',finishedAt=now());save(receipt,d)
