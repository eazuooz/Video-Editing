import json,hashlib
from pathlib import Path
from candidate_boards import boards
P=Path(__file__).resolve().parent
ds=json.loads((P/'design-capture-progress.json').read_text(encoding='utf8'));rows=[dict(r,article=i) for i,r in ds.items() if r.get('path')];boards(rows,'design-fixed')
ss=json.loads((P/'shorts-capture-progress.json').read_text(encoding='utf8'));rows=[dict(r,article=i) for i,r in ss.items() if r.get('path')];boards(rows,'shorts-review',True)
owner=json.loads((P/'owner-player-frames.json').read_text(encoding='utf8'));s1=P/'evidence/S01-owner-frame.jpg'
owner.insert(0,dict(article='S01',file=str(s1),path=str(s1),seconds=29.634999,videoId='t5ALRM1xm7g',sourceUrl='https://www.youtube.com/watch?v=t5ALRM1xm7g',status='owner-player-capture-pending-visual-review'))
for r in owner:r['sha256']=hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()
(P/'owner-player-frames-reviewed-input.json').write_text(json.dumps(owner,ensure_ascii=False,indent=2)+'\n',encoding='utf8');boards(owner,'owner-review',True)
print(len(owner),'owner captures; other boards updated')
