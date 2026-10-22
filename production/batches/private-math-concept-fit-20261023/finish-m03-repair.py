from common import *
import sys
H=R/'projects/game-math-orientation-matrices/production/concept-fit-v2'
authorized('M03-original')
c=read(H/'composition.json');previous=read(H/'qa-round1/composition.json');repaired={'01','02','05','08','11'}
rows={x['id']:x for x in c['scenes']}
for row in previous['scenes']:
 if row['id'] not in repaired and row['id'] not in rows:
  assert sha(R/row['path'])==row['sha256'];rows[row['id']]=row
assert len(rows)==24
c.update(identity=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(B/'compose-m03.py')).encode()).hexdigest(),scenes=sorted(rows.values(),key=lambda x:x['id']),completed=True)
save(H/'composition.json',c)
for name in ['assemble-m03.py','qa-m03.py']:
 authorized('M03-original');subprocess.run([sys.executable,'-u','-X','utf8',str(B/name)],cwd=R,check=True)
d=read(H/'qa-correction.json');d.update(status='encoded-direct-review-pending',finishedAt=now());save(H/'qa-correction.json',d)
