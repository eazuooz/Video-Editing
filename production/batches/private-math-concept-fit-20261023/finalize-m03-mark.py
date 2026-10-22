"""Remove an observed drifting circle; reuse all23 unaffected composites and audio."""
from common import *
import sys, shutil
H=R/'projects/game-math-orientation-matrices/production/concept-fit-v2'
authorized('M03-original')
archive=H/'qa-round2'; archive.mkdir(exist_ok=True)
for name in ['composition.json','qa.json','outputs.json']:
    dst=archive/name
    if not dst.exists(): shutil.copy2(H/name,dst)
old=read(archive/'composition.json')
identity=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(B/'compose-m03.py')).encode()).hexdigest()
if not (H/'mark-fix.json').exists():
    kept=[x for x in old['scenes'] if x['id']!='02']
    for row in kept: assert sha(R/row['path'])==row['sha256']
    save(H/'composition.json',dict(identity=identity,scenes=kept,completed=False))
    save(H/'mark-fix.json',dict(status='started',scope='02 screen circle only; first3s, then native selection highlight',unchangedComposites=23,audioUnchanged=True,startedAt=now()))
for script in ['compose-m03.py','assemble-m03.py','qa-m03.py']:
    authorized('M03-original')
    subprocess.run([sys.executable,'-u','-X','utf8',str(B/script)],cwd=R,check=True)
d=read(H/'mark-fix.json'); d.update(status='encoded-targeted-review-pending',finishedAt=now());save(H/'mark-fix.json',d)
