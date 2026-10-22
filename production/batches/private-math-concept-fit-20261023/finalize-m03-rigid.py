"""One mathematical visual correction; preserve all other23 clips and speech."""
from common import *
import sys,shutil
H=R/'projects/game-math-orientation-matrices/production/concept-fit-v2'
authorized('M03-original'); archive=H/'qa-round3';archive.mkdir(exist_ok=True)
for name in ['composition.json','qa.json','outputs.json','render-progress.json']:
 if not (archive/name).exists():shutil.copy2(H/name,archive/name)
old=read(archive/'render-progress.json')
identity=hashlib.sha256((sha(B/'m03-scenes.py')+sha(R/'manim/projects/game-math-part2-full-series/lesson.py')+sha(H/'timeline.json')).encode()).hexdigest()
if not (H/'rigid-fix.json').exists():
 old['scenes'].pop('17');old.update(identity=identity,state='partial-rendered');save(H/'render-progress.json',old)
 save(H/'rigid-fix.json',dict(status='started',scope='Scene17 constant-length axes during rotation; use rigid rotations instead of linear point morphing',unchangedScenes=23,startedAt=now()))
subprocess.run([sys.executable,'-u',str(B/'render-m03.py'),'17'],cwd=R,check=True)
prev=read(archive/'composition.json');prev['scenes']=[r for r in prev['scenes'] if r['id']!='17'];prev['completed']=False
prev['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(B/'compose-m03.py')).encode()).hexdigest();save(H/'composition.json',prev)
for name in ['compose-m03.py','assemble-m03.py','qa-m03.py']:
 authorized('M03-original');subprocess.run([sys.executable,'-u','-X','utf8',str(B/name)],cwd=R,check=True)
d=read(H/'rigid-fix.json');d.update(status='encoded-targeted-review-pending',finishedAt=now());save(H/'rigid-fix.json',d)
